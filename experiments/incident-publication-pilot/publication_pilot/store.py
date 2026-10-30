"""Trusted-directory local publication; no overwrite, retry or external acceptance."""

import os
import re
import sqlite3
import stat
from contextlib import closing, contextmanager
from copy import deepcopy
from pathlib import Path
from uuid import uuid4

from .protocol import (
    InputError, MAX_HTML, canonical, decode_json, digest, identifier, public_key,
    sha256_bytes, sign_message, timestamp, utc_now,
)


STATES = {"publication_intent", "blocked_after_intent", "local_output_confirmed", "outcome_unknown"}
SAFE_NAME = re.compile(r"[0-9a-f]{64}\.html\Z")
SNAPSHOT_FIELDS = {"request_id", "fingerprint", "artifact_sha256", "disclosure_sha256",
                   "byte_length", "destination_id", "visible_name"}


class StoreError(RuntimeError):
    """The local store cannot establish the requested state or observation."""


def _exact(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise InputError("Unsupported local store object fields")


def _hex(value):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise InputError("Expected a lowercase SHA-256 hexadecimal digest")


def _safe_name(request_id):
    return sha256_bytes(identifier(request_id).encode("utf-8")) + ".html"


def _validate_snapshot(snapshot):
    _exact(snapshot, SNAPSHOT_FIELDS)
    identifier(snapshot["request_id"])
    identifier(snapshot["destination_id"])
    for field in ("fingerprint", "artifact_sha256", "disclosure_sha256"):
        _hex(snapshot[field])
    if type(snapshot["byte_length"]) is not int or not 0 <= snapshot["byte_length"] <= MAX_HTML:
        raise InputError("Invalid measured artifact length")
    if snapshot["visible_name"] != _safe_name(snapshot["request_id"]):
        raise InputError("Visible name does not bind the request identifier")


def _validate_row(row, *, claim=False):
    fields = {"request_id", "fingerprint", "state", "snapshot", "result"}
    if claim:
        fields.add("claim_status")
    _exact(row, fields)
    _validate_snapshot(row["snapshot"])
    if (row["request_id"] != row["snapshot"]["request_id"]
            or row["fingerprint"] != row["snapshot"]["fingerprint"]
            or type(row["state"]) is not str or row["state"] not in STATES):
        raise InputError("Persisted request binding or state is inconsistent")
    if row["result"] is not None and type(row["result"]) is not dict:
        raise InputError("Malformed persisted publication result")
    if claim and row["claim_status"] not in ("CLAIMED", "REPLAY", "CONFLICT"):
        raise InputError("Unsupported publication claim disposition")


class LocalPublisher:
    """One-shot publisher for a controller-owned root on one local filesystem.

    Fault seams (trusted harness only):
      _claim(request_id, fingerprint, snapshot) -> row plus claim_status
      _finish(request_id, state, result) -> row

    The caller gate owns policy and reviewer authorization. A before_link
    callback returning False blocks after the durable intent. Missing callbacks
    do not add authorization semantics to this lower-level storage component.
    """

    def __init__(self, root, destination_id, secret, key_id, clock=utc_now):
        if os.name != "posix" or not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise InputError("This experiment requires POSIX no-follow and directory operations")
        self.destination_id = identifier(destination_id)
        if type(key_id) is not str or not key_id.strip() or len(key_id) > 16384 or not callable(clock):
            raise InputError("Invalid publisher key identifier or clock")
        self._secret, self.key_id, self.clock = secret, key_id, clock
        self.public_key = public_key(secret)
        self.root = Path(root)
        self.private_root, self.visible_root = self.root / "private", self.root / "visible"
        self.journal_path = self.root / "journal.sqlite3"
        if self.root.is_symlink():
            raise InputError("Publisher root must not be a symlink")
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._identities = {}
        for path in (self.root, self.private_root, self.visible_root):
            if path != self.root:
                path.mkdir(mode=0o700, exist_ok=True)
            info = path.lstat()
            if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or info.st_mode & 0o022:
                raise InputError("Publisher directories must be owned, real and not writable by other users")
            if path == self.private_root and info.st_mode & 0o077:
                raise InputError("Private staging must be accessible only to its owner")
            self._identities[path] = (info.st_dev, info.st_ino)
        if self._identities[self.private_root][0] != self._identities[self.visible_root][0]:
            raise InputError("Private staging and visible output must share one filesystem")
        if self.journal_path.is_symlink():
            raise InputError("Publication journal must not be a symlink")
        with closing(self._connect()) as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in (0, 1):
                raise StoreError("Unsupported local publication journal version")
            connection.execute(
                "CREATE TABLE IF NOT EXISTS publication_journal ("
                "request_id TEXT PRIMARY KEY NOT NULL, fingerprint TEXT NOT NULL, "
                "state TEXT NOT NULL CHECK(state IN "
                "('publication_intent','blocked_after_intent','local_output_confirmed','outcome_unknown')), "
                "snapshot_json TEXT NOT NULL, result_json TEXT)"
            )
            columns = connection.execute("PRAGMA table_info(publication_journal)").fetchall()
            if [(r[1], r[2]) for r in columns] != [
                ("request_id", "TEXT"), ("fingerprint", "TEXT"), ("state", "TEXT"),
                ("snapshot_json", "TEXT"), ("result_json", "TEXT"),
            ] or columns[0][5] != 1:
                raise StoreError("Publication journal layout is unsupported")
            if version == 0:
                connection.execute("PRAGMA user_version=1")

    @contextmanager
    def _directory(self, path):
        # Directory ownership is a controller assumption, not an OS sandbox.
        descriptor = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            info = os.fstat(descriptor)
            if (info.st_dev, info.st_ino) != self._identities[path]:
                raise StoreError("A controller directory was replaced")
            yield descriptor
        finally:
            os.close(descriptor)

    def _connect(self):
        if self.journal_path.is_symlink():
            raise StoreError("Journal path became a symlink")
        connection = sqlite3.connect(self.journal_path, timeout=5.0, isolation_level=None)
        try:
            mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
            connection.execute("PRAGMA synchronous=FULL")
            connection.execute("PRAGMA busy_timeout=5000")
            if str(mode).lower() != "wal" or connection.execute("PRAGMA synchronous").fetchone()[0] != 2:
                raise StoreError("SQLite WAL/FULL prerequisites are unavailable")
            return connection
        except Exception:
            connection.close()
            raise

    @staticmethod
    def _decode_row(row):
        if row is None:
            return None
        request_id, fingerprint, state_value, snapshot_json, result_json = row
        result = {"request_id": request_id, "fingerprint": fingerprint, "state": state_value,
                  "snapshot": decode_json(snapshot_json),
                  "result": None if result_json is None else decode_json(result_json)}
        _validate_row(result)
        return result

    def get(self, request_id):
        identifier(request_id)
        with closing(self._connect()) as connection:
            return self._decode_row(connection.execute(
                "SELECT request_id,fingerprint,state,snapshot_json,result_json "
                "FROM publication_journal WHERE request_id=?", (request_id,)
            ).fetchone())

    def _claim(self, request_id, fingerprint, snapshot):
        """Atomically commit measured intent; returns row + CLAIMED/REPLAY/CONFLICT."""
        identifier(request_id)
        _hex(fingerprint)
        _validate_snapshot(snapshot)
        if snapshot["request_id"] != request_id or snapshot["fingerprint"] != fingerprint:
            raise InputError("Claim arguments do not bind their snapshot")
        serialized = canonical(snapshot).decode()
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json "
                    "FROM publication_journal WHERE request_id=?", (request_id,)
                ).fetchone())
                if row is not None:
                    connection.rollback()
                    matches = row["fingerprint"] == fingerprint and digest(row["snapshot"]) == digest(snapshot)
                    row["claim_status"] = "REPLAY" if matches else "CONFLICT"
                    return row
                connection.execute(
                    "INSERT INTO publication_journal(request_id,fingerprint,state,snapshot_json,result_json) "
                    "VALUES(?,?,'publication_intent',?,NULL)", (request_id, fingerprint, serialized),
                )
                connection.commit()
                row = self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json "
                    "FROM publication_journal WHERE request_id=?", (request_id,)
                ).fetchone())
                if row is None:
                    raise StoreError("Committed publication intent is unreadable")
                row["claim_status"] = "CLAIMED"
                return row
            except Exception:
                connection.rollback()
                raise

    def _finish(self, request_id, state, result):
        """Commit one terminal result; returns its fully bound persisted row."""
        identifier(request_id)
        if type(state) is not str or state not in STATES - {"publication_intent"} or type(result) is not dict:
            raise InputError("Unsupported terminal publication result")
        serialized = canonical(result).decode()
        with closing(self._connect()) as connection:
            connection.execute("BEGIN IMMEDIATE")
            try:
                row = self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json "
                    "FROM publication_journal WHERE request_id=?", (request_id,)
                ).fetchone())
                if row is None or row["state"] != "publication_intent":
                    raise StoreError("Only a claimed publication intent can receive a terminal result")
                connection.execute(
                    "UPDATE publication_journal SET state=?,result_json=? "
                    "WHERE request_id=? AND state='publication_intent'", (state, serialized, request_id),
                )
                connection.commit()
                return self._decode_row(connection.execute(
                    "SELECT request_id,fingerprint,state,snapshot_json,result_json "
                    "FROM publication_journal WHERE request_id=?", (request_id,)
                ).fetchone())
            except Exception:
                connection.rollback()
                raise

    @staticmethod
    def _read_artifact(directory_fd, name, expected_identity=None):
        if not SAFE_NAME.fullmatch(name):
            raise StoreError("Unexpected visible basename")
        descriptor = os.open(name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=directory_fd)
        try:
            before = os.fstat(descriptor)
            if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_HTML:
                raise StoreError("Visible artifact is not a bounded regular file")
            if expected_identity is not None and (before.st_dev, before.st_ino) != expected_identity:
                raise StoreError("Visible artifact is not the prepared file")
            chunks, total = [], 0
            while True:
                chunk = os.read(descriptor, min(65536, MAX_HTML + 1 - total))
                if not chunk:
                    break
                chunks.append(chunk)
                total += len(chunk)
                if total > MAX_HTML:
                    raise StoreError("Visible artifact exceeds the supported limit")
            after = os.fstat(descriptor)
            for field in ("st_dev", "st_ino", "st_size", "st_mtime_ns", "st_ctime_ns"):
                if getattr(before, field) != getattr(after, field):
                    raise StoreError("Visible artifact changed during readback")
            data = b"".join(chunks)
            return {"sha256": sha256_bytes(data), "byte_length": len(data)}
        finally:
            os.close(descriptor)

    def inspect(self):
        files = {}
        with self._directory(self.visible_root) as directory_fd:
            for name in sorted(os.listdir(directory_fd)):
                files[name] = self._read_artifact(directory_fd, name)
        return {"visible_count": len(files), "files": files}

    def _current_state(self, request_id):
        try:
            row = self.get(request_id)
            return "NOT_CLAIMED" if row is None else row["state"]
        except Exception:
            return "UNAVAILABLE"

    @staticmethod
    def _replay(result, row, snapshot):
        matches = row["fingerprint"] == snapshot["fingerprint"] and digest(row["snapshot"]) == digest(snapshot)
        result["state"] = "REPLAY_NO_PUBLICATION" if matches else "REQUEST_ID_CONFLICT"
        result["reason"] = "REQUEST_ALREADY_CLAIMED_NO_RECEIPT_REASSERTED" if matches else "REQUEST_ID_BINDS_DIFFERENT_ACTION"
        result["journal_state"] = row["state"]
        result["receipt"] = None
        return result

    def _persist(self, result, snapshot, state):
        result["journal_state"] = state
        try:
            row = self._finish(snapshot["request_id"], state, deepcopy(result))
            _validate_row(row)
            if (row["request_id"] != snapshot["request_id"] or row["state"] != state
                    or row["fingerprint"] != snapshot["fingerprint"]
                    or digest(row["snapshot"]) != digest(snapshot) or digest(row["result"]) != digest(result)):
                raise StoreError("Result acknowledgement does not match the owned publication")
        except Exception:
            result["state"] = "OUTCOME_UNKNOWN"
            result["reason"] = "PUBLICATION_RESULT_PERSISTENCE_NOT_ESTABLISHED"
            result["receipt"] = None
            result["journal_state"] = self._current_state(snapshot["request_id"])
        return result

    def publish(self, request_id, fingerprint, html_bytes, disclosure_sha256, *, before_link=None, after_link=None):
        identifier(request_id)
        _hex(fingerprint)
        _hex(disclosure_sha256)
        if type(html_bytes) is not bytes or len(html_bytes) > MAX_HTML:
            raise InputError("Publisher requires immutable bytes within the 1 MiB limit")
        for hook in (before_link, after_link):
            if hook is not None and not callable(hook):
                raise InputError("Fault hooks must be trusted callables")
        name = _safe_name(request_id)
        snapshot = {"request_id": request_id, "fingerprint": fingerprint,
                    "artifact_sha256": sha256_bytes(html_bytes), "disclosure_sha256": disclosure_sha256,
                    "byte_length": len(html_bytes), "destination_id": self.destination_id, "visible_name": name}
        result = {"state": "BLOCKED_WITHOUT_PUBLICATION", "attempted": False, "visible_name": name,
                  "receipt": None, "journal_state": "NOT_CLAIMED", "reason": "NOT_PREPARED"}
        try:
            existing = self.get(request_id)
            if existing is not None:
                _validate_row(existing)
                if existing["request_id"] != request_id:
                    raise StoreError("Journal returned another request")
                return self._replay(result, existing, snapshot)
        except Exception:
            result["reason"], result["journal_state"] = "JOURNAL_UNAVAILABLE_BEFORE_CLAIM", "UNAVAILABLE"
            return result

        stage_name = uuid4().hex + ".stage"
        stage_created = False
        try:
            with self._directory(self.private_root) as private_fd, self._directory(self.visible_root) as visible_fd:
                try:
                    stage_fd = os.open(stage_name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                       0o600, dir_fd=private_fd)
                    stage_created = True
                    try:
                        remaining = memoryview(html_bytes)
                        while remaining:
                            written = os.write(stage_fd, remaining)
                            if written <= 0:
                                raise StoreError("Private stage write made no progress")
                            remaining = remaining[written:]
                        os.fchmod(stage_fd, 0o444)
                        os.fsync(stage_fd)
                        info = os.fstat(stage_fd)
                        stage_identity = (info.st_dev, info.st_ino)
                    finally:
                        os.close(stage_fd)
                    os.fsync(private_fd)
                except Exception:
                    result["reason"] = "PRIVATE_STAGE_NOT_ESTABLISHED"
                    return result
                try:
                    row = self._claim(request_id, fingerprint, snapshot)
                    _validate_row(row, claim=True)
                    if row["request_id"] != request_id:
                        raise StoreError("Claim acknowledgement names another request")
                    matches = row["fingerprint"] == fingerprint and digest(row["snapshot"]) == digest(snapshot)
                    if row["claim_status"] == "CLAIMED":
                        if not matches or row["state"] != "publication_intent" or row["result"] is not None:
                            raise StoreError("Claim acknowledgement does not match the committed owned intent")
                    elif row["claim_status"] != ("REPLAY" if matches else "CONFLICT"):
                        raise StoreError("Claim acknowledgement disposition is inconsistent")
                    else:
                        return self._replay(result, row, snapshot)
                except Exception:
                    result["reason"] = "PUBLICATION_INTENT_ACKNOWLEDGEMENT_NOT_ESTABLISHED"
                    result["journal_state"] = self._current_state(request_id)
                    return result
                result["journal_state"] = "publication_intent"
                try:
                    permitted = before_link() if before_link is not None else True
                except Exception:
                    result["state"], result["reason"] = "OUTCOME_UNKNOWN", "BEFORE_LINK_CALLBACK_FAILED"
                    return self._persist(result, snapshot, "outcome_unknown")
                if permitted is False:
                    result["reason"] = "FINAL_GATE_BLOCKED_PUBLICATION"
                    return self._persist(result, snapshot, "blocked_after_intent")
                result["attempted"] = True
                try:
                    os.link(stage_name, name, src_dir_fd=private_fd, dst_dir_fd=visible_fd, follow_symlinks=False)
                except FileExistsError:
                    result["reason"] = "VISIBLE_NAME_ALREADY_EXISTS"
                    return self._persist(result, snapshot, "blocked_after_intent")
                except Exception:
                    result["state"], result["reason"] = "OUTCOME_UNKNOWN", "ATOMIC_PUBLICATION_OUTCOME_UNKNOWN"
                    return self._persist(result, snapshot, "outcome_unknown")
                try:
                    if after_link is not None:
                        after_link()
                    os.fsync(visible_fd)
                    actual = self._read_artifact(visible_fd, name, stage_identity)
                    if actual != {"sha256": snapshot["artifact_sha256"], "byte_length": snapshot["byte_length"]}:
                        raise StoreError("Visible readback differs from the measured artifact")
                    observed_at = self.clock()
                    timestamp(observed_at)
                    receipt = sign_message({"kind": "local_publication_receipt", **deepcopy(snapshot),
                                            "observed_at": observed_at}, self._secret, self.key_id)
                except Exception:
                    result["state"], result["reason"] = "OUTCOME_UNKNOWN", "VISIBLE_OUTPUT_READBACK_NOT_ESTABLISHED"
                    return self._persist(result, snapshot, "outcome_unknown")
                result["state"], result["reason"], result["receipt"] = (
                    "LOCAL_OUTPUT_CONFIRMED", "MEASURED_LOCAL_FILE_CONFIRMED", receipt)
                return self._persist(result, snapshot, "local_output_confirmed")
        except Exception:
            result["state"] = "OUTCOME_UNKNOWN" if result["attempted"] else "BLOCKED_WITHOUT_PUBLICATION"
            result["reason"] = "CONTROLLER_DIRECTORIES_UNAVAILABLE"
            result["receipt"] = None
            result["journal_state"] = self._current_state(request_id)
            return result
        finally:
            if stage_created:
                # Only remove our private random stage name. Never unlink visible output.
                try:
                    with self._directory(self.private_root) as cleanup_fd:
                        os.unlink(stage_name, dir_fd=cleanup_fd)
                        os.fsync(cleanup_fd)
                except Exception:
                    pass
