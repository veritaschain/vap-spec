"""One-shot removal from a trusted local namespace; never universal erasure."""

import os
import sqlite3
import stat
from contextlib import closing, contextmanager
from copy import deepcopy
from pathlib import Path

from .adapter import validate_pins, validate_task
from .protocol import (
    EXCLUSIONS, LOCATION, MAX_OBJECT, InputError, canonical, capture, decode_json, digest,
    digest_hex, exact_keys, identifier, object_name, public_key, sha256_bytes,
    sign_message, sign_record, timestamp, utc_now,
)


INTENT = "deletion_intent"
TERMINAL = {"LOCAL_UNLINK_CONFIRMED", "ACKNOWLEDGED_ONLY", "BLOCKED", "OUTCOME_UNKNOWN"}
RESULT_STATES = TERMINAL | {"REPLAY_NO_ACTION", "REQUEST_ID_CONFLICT"}
RESULT_FIELDS = {"state", "attempted", "acknowledgement", "attestation", "receipt", "journal_state", "reason"}
MANIFEST_FIELDS = {"provider_id", "tenant_id", "object_id", "version_id", "sha256", "byte_length", "location"}


class ProviderError(RuntimeError):
    """The controller cannot establish the requested local storage fact."""


def _historical_context(task, pins):
    try:
        at = task["request"]["body"]["data"]["requested_at"]
    except (KeyError, TypeError) as exc:
        raise InputError("Task lacks its original request time") from exc
    return validate_task(task, pins, at)


def _validate_result(result):
    exact_keys(result, RESULT_FIELDS)
    if type(result["state"]) is not str or result["state"] not in RESULT_STATES:
        raise InputError("Unsupported provider result state")
    if type(result["attempted"]) is not bool or type(result["reason"]) is not str or not result["reason"]:
        raise InputError("Malformed provider attempt or reason")
    if type(result["journal_state"]) is not str or result["journal_state"] not in TERMINAL | {INTENT, "NOT_CLAIMED", "UNAVAILABLE"}:
        raise InputError("Unsupported provider journal state")
    for field in ("acknowledgement", "attestation", "receipt"):
        if result[field] is not None and type(result[field]) is not dict:
            raise InputError("Malformed provider evidence envelope")
    if result["state"] == "LOCAL_UNLINK_CONFIRMED":
        if not result["attempted"] or any(result[field] is None for field in ("acknowledgement", "attestation", "receipt")):
            raise InputError("Confirmed local unlink lacks its measured evidence")
    elif result["attestation"] is not None or result["receipt"] is not None:
        raise InputError("An unconfirmed result cannot assert completion")
    if result["state"] in {"BLOCKED", "ACKNOWLEDGED_ONLY", "REPLAY_NO_ACTION", "REQUEST_ID_CONFLICT"} and result["attempted"]:
        raise InputError("Provider state is inconsistent with an unlink attempt")
    if result["state"] == "ACKNOWLEDGED_ONLY" and result["acknowledgement"] is None:
        raise InputError("Acknowledgement-only state lacks its acknowledgement")
    if result["state"] in {"REPLAY_NO_ACTION", "REQUEST_ID_CONFLICT"} and result["acknowledgement"] is not None:
        raise InputError("Replays cannot issue fresh acknowledgements")


class LocalProvider:
    """Controller-owned local files and a WAL/FULL one-shot deletion journal.

    Fault seams, reserved for trusted tests:
      _claim(request_id, fingerprint, snapshot) -> row plus claim_status
      _finish(request_id, state, result) -> row

    Row fields are request_id, fingerprint, state, snapshot and result. The
    snapshot is the complete public signed task, never the object plaintext.
    Directory ownership is an assumption; these checks are not OS isolation.
    """

    def __init__(self, root, pins, secret, clock=utc_now):
        if os.name != "posix" or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise InputError("This experiment requires POSIX no-follow and directory operations")
        self._pins = validate_pins(capture(pins))
        self.provider_id, self.tenant_id, self.location = (self._pins[field] for field in ("provider_id", "tenant_id", "location"))
        self.key_id = self._pins["provider_key_id"]
        self.public_key = public_key(secret)
        if self.public_key != self._pins["keys"][self.key_id]["public_key"] or not callable(clock):
            raise InputError("Provider signing key or clock does not match controller configuration")
        self._secret, self.clock = secret, clock
        self.root = Path(root)
        self.namespace_root, self.journal_path = self.root / "namespace", self.root / "journal.sqlite3"
        if self.root.is_symlink():
            raise InputError("Provider root must not be a symlink")
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.namespace_root.mkdir(mode=0o700, exist_ok=True)
        self._identities = {}
        for path in (self.root, self.namespace_root):
            info = path.lstat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o077:
                raise InputError("Provider directories must be real and accessible only to their owner")
            self._identities[path] = (info.st_dev, info.st_ino)
        with closing(self._connect()) as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise ProviderError("Unsupported deletion journal version")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS erasure_journal ("
                "request_id TEXT PRIMARY KEY NOT NULL, fingerprint TEXT NOT NULL, "
                "state TEXT NOT NULL CHECK(state IN ('deletion_intent','LOCAL_UNLINK_CONFIRMED',"
                "'ACKNOWLEDGED_ONLY','BLOCKED','OUTCOME_UNKNOWN')), snapshot_json TEXT NOT NULL, result_json TEXT)"
            )
            columns = connection.execute("PRAGMA table_info(erasure_journal)").fetchall()
            if [(row[1], row[2]) for row in columns] != [
                ("request_id", "TEXT"), ("fingerprint", "TEXT"), ("state", "TEXT"),
                ("snapshot_json", "TEXT"), ("result_json", "TEXT"),
            ] or columns[0][5] != 1:
                raise ProviderError("Unsupported deletion journal layout")
            if version == 0:
                connection.execute("PRAGMA user_version=1")

    @contextmanager
    def _directory(self, path):
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            info = os.fstat(descriptor)
            if (info.st_dev, info.st_ino) != self._identities[path]:
                raise ProviderError("A controller directory was replaced")
            yield descriptor
        finally:
            os.close(descriptor)

    def _connect(self):
        if self.journal_path.is_symlink():
            raise ProviderError("Deletion journal cannot be a symlink")
        with self._directory(self.root):
            connection = sqlite3.connect(self.journal_path, timeout=5.0, isolation_level=None)
        try:
            mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("PRAGMA busy_timeout=5000")
            if str(mode).lower() != "wal" or connection.execute("PRAGMA synchronous").fetchone()[0] != 2:
                raise ProviderError("SQLite WAL/FULL prerequisites are unavailable")
            return connection
        except BaseException:
            connection.close()
            raise

    def _check_namespace(self, directory_fd):
        # An open directory may survive a rename; LOCATION still names the
        # controller-configured path, so check that path at each action boundary.
        for path in (self.root, self.namespace_root):
            current = path.lstat()
            if not stat.S_ISDIR(current.st_mode) or (current.st_dev, current.st_ino) != self._identities[path]:
                raise ProviderError("The configured provider namespace was replaced")
        opened = os.fstat(directory_fd)
        if (opened.st_dev, opened.st_ino) != self._identities[self.namespace_root]:
            raise ProviderError("The open namespace differs from the configured namespace")

    def _manifest(self, manifest):
        exact_keys(manifest, MANIFEST_FIELDS)
        for field in ("provider_id", "tenant_id", "object_id", "version_id"):
            identifier(manifest[field])
        digest_hex(manifest["sha256"])
        if type(manifest["byte_length"]) is not int or not 1 <= manifest["byte_length"] <= MAX_OBJECT:
            raise InputError("Object manifest length is outside the supported bound")
        if any(manifest[field] != getattr(self, field) for field in ("provider_id", "tenant_id", "location")):
            raise InputError("Object manifest does not match the pinned provider namespace")
        return object_name(manifest)

    @staticmethod
    def _file_state(info):
        return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)

    @staticmethod
    def _measure(directory_fd, name):
        try:
            descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
        except FileNotFoundError:
            return {"state": "ABSENT", "sha256": None, "byte_length": None}, None
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or not 1 <= before.st_size <= MAX_OBJECT:
                raise ProviderError("Object is not a bounded nonempty regular file")
            chunks, total = [], 0
            while True:
                chunk = os.read(descriptor, min(65536, MAX_OBJECT + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > MAX_OBJECT:
                    raise ProviderError("Object exceeds the supported byte limit")
            after = os.fstat(descriptor)
            for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns"):
                if getattr(before, field) != getattr(after, field):
                    raise ProviderError("Object changed while it was being measured")
            current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            identity = LocalProvider._file_state(before)
            if not stat.S_ISREG(current.st_mode) or LocalProvider._file_state(current) != identity:
                raise ProviderError("Object path no longer names the measured regular file")
            return {"state": "PRESENT", "sha256": sha256_bytes(b"".join(chunks)), "byte_length": total}, identity
        finally:
            os.close(descriptor)

    def create(self, object_id, version_id, content):
        identifier(object_id)
        identifier(version_id)
        if type(content) is not bytes or not 1 <= len(content) <= MAX_OBJECT:
            raise InputError("Creation requires immutable nonempty synthetic bytes within the size limit")
        manifest = {"provider_id": self.provider_id, "tenant_id": self.tenant_id,
                    "object_id": object_id, "version_id": version_id, "sha256": sha256_bytes(content),
                    "byte_length": len(content), "location": self.location}
        name = self._manifest(manifest)
        with self._directory(self.namespace_root) as directory_fd:
            self._check_namespace(directory_fd)
            descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=directory_fd)
            try:
                remaining = memoryview(content)
                while remaining:
                    written = os.write(descriptor, remaining)
                    if written <= 0:
                        raise ProviderError("Object creation made no write progress")
                    remaining = remaining[written:]
                os.fchmod(descriptor, 0o400)
                os.fsync(descriptor)
                info = os.fstat(descriptor)
                identity = self._file_state(info)
            finally:
                os.close(descriptor)
            os.fsync(directory_fd)
            measured, measured_identity = self._measure(directory_fd, name)
            self._check_namespace(directory_fd)
            if measured_identity != identity or measured != self._expected(manifest):
                raise ProviderError("Created object could not be confirmed by measured readback")
        return manifest

    def inspect(self, manifest):
        owned = capture(manifest)
        name = self._manifest(owned)
        with self._directory(self.namespace_root) as directory_fd:
            measurement, _ = self._measure(directory_fd, name)
            self._check_namespace(directory_fd)
        return measurement

    @staticmethod
    def _expected(manifest):
        return {"state": "PRESENT", "sha256": manifest["sha256"], "byte_length": manifest["byte_length"]}

    def _validate_row(self, row, *, claim=False):
        fields = {"request_id", "fingerprint", "state", "snapshot", "result"}
        if claim:
            fields.add("claim_status")
        exact_keys(row, fields)
        context = _historical_context(row["snapshot"], self._pins)
        if row["request_id"] != context["request_id"] or row["fingerprint"] != context["task_sha256"]:
            raise InputError("Journal row does not bind its original signed task")
        if type(row["state"]) is not str or row["state"] not in TERMINAL | {INTENT}:
            raise InputError("Unsupported persisted deletion state")
        if row["state"] == INTENT:
            if row["result"] is not None:
                raise InputError("An unfinished intent cannot contain a terminal result")
        else:
            _validate_result(row["result"])
            if row["result"]["state"] != row["state"] or row["result"]["journal_state"] != row["state"]:
                raise InputError("Persisted terminal state and result disagree")
        if claim and row["claim_status"] not in ("CLAIMED", "REPLAY", "CONFLICT"):
            raise InputError("Unsupported deletion claim acknowledgement")

    def _decode_row(self, row):
        if row is None:
            return None
        request_id, fingerprint, state_value, snapshot_json, result_json = row
        result = {"request_id": request_id, "fingerprint": fingerprint, "state": state_value,
                  "snapshot": decode_json(snapshot_json), "result": None if result_json is None else decode_json(result_json)}
        self._validate_row(result)
        return result

    def get(self, request_id):
        identifier(request_id)
        with closing(self._connect()) as connection:
            return self._decode_row(connection.execute(
                "SELECT request_id,fingerprint,state,snapshot_json,result_json FROM erasure_journal WHERE request_id=?",
                (request_id,),
            ).fetchone())

    def _claim(self, request_id, fingerprint, snapshot):
        """Commit one task intent; return its exact row with CLAIMED/REPLAY/CONFLICT."""
        context = _historical_context(snapshot, self._pins)
        if request_id != context["request_id"] or fingerprint != context["task_sha256"]:
            raise InputError("Claim does not bind the signed task")
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json FROM erasure_journal WHERE request_id=?",
                    (request_id,),
                ).fetchone())
                if row is not None:
                    connection.rollback()
                    row["claim_status"] = "REPLAY" if row["fingerprint"] == fingerprint else "CONFLICT"
                    return row
                connection.execute(
                    "INSERT INTO erasure_journal(request_id,fingerprint,state,snapshot_json,result_json) VALUES(?,?,?, ?,NULL)",
                    (request_id, fingerprint, INTENT, canonical(snapshot).decode()),
                )
                connection.commit()
                row = self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json FROM erasure_journal WHERE request_id=?",
                    (request_id,),
                ).fetchone())
                if row is None:
                    raise ProviderError("Committed deletion intent is unreadable")
                row["claim_status"] = "CLAIMED"
                return row
            except BaseException:
                connection.rollback()
                raise

    def _finish(self, request_id, state, result):
        """Commit one terminal result, returning the exact persisted bound row."""
        identifier(request_id)
        _validate_result(result)
        if state not in TERMINAL or result["state"] != state or result["journal_state"] != state:
            raise InputError("Terminal deletion result is inconsistent")
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json FROM erasure_journal WHERE request_id=?",
                    (request_id,),
                ).fetchone())
                if row is None or row["state"] != INTENT:
                    raise ProviderError("Only a claimed intent can receive a terminal deletion result")
                connection.execute(
                    "UPDATE erasure_journal SET state=?,result_json=? WHERE request_id=? AND state=?",
                    (state, canonical(result).decode(), request_id, INTENT),
                )
                connection.commit()
                return self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json FROM erasure_journal WHERE request_id=?",
                    (request_id,),
                ).fetchone())
            except BaseException:
                connection.rollback()
                raise

    def _current_state(self, request_id):
        try:
            row = self.get(request_id)
            return "NOT_CLAIMED" if row is None else row["state"]
        except Exception:
            return "UNAVAILABLE"

    @staticmethod
    def _replay(result, row, fingerprint):
        matches = row["fingerprint"] == fingerprint
        result["state"] = "REPLAY_NO_ACTION" if matches else "REQUEST_ID_CONFLICT"
        result["journal_state"] = row["state"]
        result["reason"] = "REQUEST_ALREADY_CLAIMED_NO_EVIDENCE_REASSERTED" if matches else "REQUEST_ID_BINDS_DIFFERENT_TASK"
        return result

    def _replay_if_claimed(self, result, context):
        try:
            row = self.get(context["request_id"])
            if row is None:
                return None
            self._validate_row(row)
            if row["request_id"] != context["request_id"]:
                raise ProviderError("Journal lookup returned another request")
            return self._replay(result, row, context["task_sha256"])
        except Exception:
            result["reason"], result["journal_state"] = "JOURNAL_UNAVAILABLE_BEFORE_CLAIM", "UNAVAILABLE"
            return result

    def _persist(self, result, context):
        state = result["state"]
        result["journal_state"] = state
        try:
            row = self._finish(context["request_id"], state, deepcopy(result))
            self._validate_row(row)
            if (row["request_id"] != context["request_id"] or row["fingerprint"] != context["task_sha256"]
                    or row["state"] != state or digest(row["snapshot"]) != context["task_sha256"]
                    or digest(row["result"]) != digest(result)):
                raise ProviderError("Terminal acknowledgement does not bind the owned deletion result")
        except Exception:
            result["state"], result["reason"] = "OUTCOME_UNKNOWN", "RESULT_PERSISTENCE_NOT_ESTABLISHED"
            result["attestation"], result["receipt"] = None, None
            result["journal_state"] = self._current_state(context["request_id"])
        return result

    def _time(self, earliest):
        value = self.clock()
        at = timestamp(value)
        key = self._pins["keys"][self.key_id]
        if at < timestamp(earliest) or not timestamp(key["not_before"]) <= at < timestamp(key["not_after"]):
            raise InputError("Provider event time or signing-key validity is inapplicable")
        return value

    def _record(self, context, kind, event_at, data):
        prefix = "ack" if kind == "erasure.acknowledgement" else "completion"
        record_id = prefix + "-" + context["task_sha256"][:48]
        if record_id == context["request_record_id"]:
            record_id += "-p"
        return sign_record({
            "record_id": record_id, "evaluation_id": context["evaluation_id"], "kind": kind,
            "issuer": self._pins["keys"][self.key_id]["issuer"], "recorded_at": event_at,
            "binding": deepcopy(context["subject"]), "data": data,
        }, self._secret, self.key_id)

    def delete(self, task, *, before_unlink=None, after_unlink=None, acknowledge_only=False):
        # Capture caller-controlled objects before any hook, I/O or asynchronous work.
        owned = capture(task)
        context = _historical_context(owned, self._pins)
        if type(acknowledge_only) is not bool or any(hook is not None and not callable(hook) for hook in (before_unlink, after_unlink)):
            raise InputError("Deletion fault hooks and acknowledgement-only flag are invalid")
        name = self._manifest(context["manifest"])
        result = {"state": "BLOCKED", "attempted": False, "acknowledgement": None, "attestation": None,
                  "receipt": None, "journal_state": "NOT_CLAIMED", "reason": "NOT_PREPARED"}
        prior = self._replay_if_claimed(result, context)
        if prior is not None:
            return prior
        try:
            proposed_at = self._time(context["operation_at"])
            validate_task(owned, self._pins, proposed_at)
        except Exception:
            result["reason"] = "AUTHORIZATION_NOT_CURRENT"
            return result
        try:
            with self._directory(self.namespace_root) as directory_fd:
                try:
                    measurement, identity = self._measure(directory_fd, name)
                    if measurement != self._expected(context["manifest"]):
                        result["reason"] = "REQUESTED_OBJECT_NOT_PRESENT_AS_BOUND"
                        # Another caller may have claimed and removed the object
                        # after our first lookup. Resolve that row, never resume it.
                        prior = self._replay_if_claimed(result, context)
                        return result if prior is None else prior
                except Exception:
                    result["reason"] = "REQUESTED_OBJECT_NOT_SAFELY_ESTABLISHED"
                    prior = self._replay_if_claimed(result, context)
                    return result if prior is None else prior
                try:
                    row = self._claim(context["request_id"], context["task_sha256"], deepcopy(owned))
                    self._validate_row(row, claim=True)
                    if row["request_id"] != context["request_id"]:
                        raise ProviderError("Claim acknowledgement is for another request")
                    matches = row["fingerprint"] == context["task_sha256"] and digest(row["snapshot"]) == context["task_sha256"]
                    if row["claim_status"] == "CLAIMED":
                        if not matches or row["state"] != INTENT or row["result"] is not None:
                            raise ProviderError("Claim acknowledgement does not match the owned deletion intent")
                    elif row["claim_status"] != ("REPLAY" if matches else "CONFLICT"):
                        raise ProviderError("Claim disposition contradicts the acknowledged task")
                    else:
                        return self._replay(result, row, context["task_sha256"])
                except Exception:
                    result["reason"] = "INTENT_ACKNOWLEDGEMENT_NOT_ESTABLISHED"
                    result["journal_state"] = self._current_state(context["request_id"])
                    return result
                result["journal_state"] = INTENT
                try:
                    acknowledged_at = self._time(proposed_at)
                    result["acknowledgement"] = self._record(context, "erasure.acknowledgement", acknowledged_at, {
                        "request_record_id": context["request_record_id"], "acknowledged_at": acknowledged_at, "queue_state": "received",
                    })
                except Exception:
                    result["state"], result["reason"] = "OUTCOME_UNKNOWN", "ACKNOWLEDGEMENT_NOT_ESTABLISHED"
                    return self._persist(result, context)
                if acknowledge_only:
                    result["state"], result["reason"] = "ACKNOWLEDGED_ONLY", "REQUEST_RECEIVED_WITHOUT_DELETION"
                    return self._persist(result, context)
                try:
                    if before_unlink is not None:
                        before_unlink()
                except Exception:
                    result["state"], result["reason"] = "OUTCOME_UNKNOWN", "BEFORE_UNLINK_CALLBACK_FAILED"
                    return self._persist(result, context)
                try:
                    final_at = self._time(acknowledged_at)
                    validate_task(owned, self._pins, final_at)
                    measured, final_identity = self._measure(directory_fd, name)
                    if measured != self._expected(context["manifest"]) or final_identity != identity:
                        raise ProviderError("Final target differs from the originally measured object")
                    unlinked_at = self._time(final_at)
                    validate_task(owned, self._pins, unlinked_at)
                    current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                    # Detect ordinary replacement/in-place changes across the
                    # authorization recheck. stat+unlink is still non-atomic;
                    # this is not protection against a malicious same-UID writer.
                    if not stat.S_ISREG(current.st_mode) or self._file_state(current) != final_identity:
                        raise ProviderError("Object identity changed immediately before unlink")
                    self._check_namespace(directory_fd)
                except Exception:
                    result["reason"] = "FINAL_AUTHORIZATION_OR_OBJECT_NOT_ESTABLISHED"
                    return self._persist(result, context)
                result["attempted"] = True
                try:
                    os.unlink(name, dir_fd=directory_fd)
                    if after_unlink is not None:
                        after_unlink()
                    os.fsync(directory_fd)
                    absence, _ = self._measure(directory_fd, name)
                    if absence != {"state": "ABSENT", "sha256": None, "byte_length": None}:
                        raise ProviderError("The exact namespace entry is present after unlink")
                    self._check_namespace(directory_fd)
                    observed_at = self._time(unlinked_at)
                    result["receipt"] = sign_message({
                        "kind": "local_unlink_receipt", "task_sha256": context["task_sha256"],
                        "request_id": context["request_id"], "manifest_sha256": context["manifest_sha256"],
                        "before": {"sha256": measurement["sha256"], "byte_length": measurement["byte_length"]},
                        "unlinked_at": unlinked_at, "observed_at": observed_at, "after": "ABSENT",
                    }, self._secret, self.key_id)
                    result["attestation"] = self._record(context, "erasure.provider_attestation", observed_at, {
                        "request_record_id": context["request_record_id"], "completed_at": observed_at,
                        "locations": [LOCATION], "exclusions": list(EXCLUSIONS),
                    })
                except Exception:
                    result["state"], result["reason"] = "OUTCOME_UNKNOWN", "UNLINK_OR_SCOPED_COMPLETION_NOT_ESTABLISHED"
                    result["attestation"], result["receipt"] = None, None
                    return self._persist(result, context)
                result["state"], result["reason"] = "LOCAL_UNLINK_CONFIRMED", "EXACT_NAMESPACE_ENTRY_REMOVAL_CONFIRMED"
                return self._persist(result, context)
        except Exception:
            result["state"] = "OUTCOME_UNKNOWN" if result["attempted"] or result["journal_state"] == INTENT else "BLOCKED"
            result["reason"] = "CONTROLLER_STORAGE_UNAVAILABLE"
            result["attestation"], result["receipt"] = None, None
            result["journal_state"] = self._current_state(context["request_id"])
            return result
