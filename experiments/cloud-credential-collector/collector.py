"""Private local file custody and a restricted native-evidence export bridge.

Linux-only, same-host/operator pilot. No Azure API, network, credential discovery,
provider-origin proof or independent custody. Trust keys are always caller inputs.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import ctypes
import errno
import fcntl
import hashlib
import importlib.util
import os
from pathlib import Path
import re
import secrets
import sqlite3
import stat
import sys
import time
from typing import Any, Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def _evidence_module():
    path = Path(__file__).resolve().parents[1] / "cloud-credential-evidence" / "cloud_evidence.py"
    spec = importlib.util.spec_from_file_location("_vso_local_cloud_custody_evidence", path)
    if spec is None or spec.loader is None:
        raise ImportError("local_evidence_dependency_missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


evidence = _evidence_module()
canonical_json = evidence.canonical_json
load_json = evidence.load_json
digest = evidence.digest
bytes_digest = evidence.bytes_digest
CONTEXT_SCHEMA = "experimental-cloud-custody-source-context-v0"
STORE_SCHEMA = "experimental-cloud-custody-store-v0"
RECEIPT_SCHEMA = "experimental-cloud-custody-receipt-v0"
CHECKPOINT_SCHEMA = "experimental-cloud-custody-checkpoint-v0"
AUDIT_SCHEMA = "experimental-cloud-custody-audit-v0"
SIGNING_DOMAIN = b"VSO experimental cloud custody v0\x00"
MAX_ARTIFACT_BYTES = 65536
MAX_METADATA_BYTES = 65536
MAX_CONTEXT_BYTES = 16384
MAX_RECORDS = 1024
MAX_DIRECTORY_ENTRIES = 2048
MAX_DATABASE_BYTES = 64 * 1024 * 1024
NANOSECONDS = 1000000000
DATABASE_NAME = "index.sqlite3"
LOCK_NAME = "store.lock"
BLOB_DIRECTORY = "blobs"
STAGING_DIRECTORY = "staging"
APPLICATION_ID = 0x56434350
HASH_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
HEX_KEY = re.compile(r"[0-9a-f]{64}\Z")
NANO_RE = re.compile(r"(?:0|[1-9][0-9]{0,21})\Z")
Hook = Callable[[str, dict], None]

METADATA_SQL = "CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
RECEIPTS_SQL = """CREATE TABLE receipts (
    sequence INTEGER PRIMARY KEY CHECK(sequence >= 1),
    request_id TEXT NOT NULL UNIQUE,
    artifact_sha256 TEXT NOT NULL,
    artifact_size INTEGER NOT NULL,
    context_json TEXT NOT NULL,
    received_time_ns TEXT NOT NULL,
    received_time INTEGER NOT NULL,
    previous_receipt_sha256 TEXT,
    receipt_sha256 TEXT NOT NULL UNIQUE,
    receipt_json TEXT NOT NULL
)"""


class CollectorError(ValueError):
    """Stable, data-free failure code. Never contains original evidence or a path."""


def _text(value: Any, maximum: int = 4096) -> bool:
    return type(value) is str and 0 < len(value) <= maximum


def _integer(value: Any) -> bool:
    return type(value) is int and 0 <= value <= evidence.MAX_INTEGER


def _hash(value: Any) -> bool:
    return type(value) is str and HASH_RE.fullmatch(value) is not None


def _snapshot(value: Any) -> Any:
    try:
        return load_json(canonical_json(value))
    except (ValueError, TypeError, RecursionError) as exc:
        raise CollectorError("invalid_metadata_json") from exc


def _context(value: Any) -> dict:
    value = _snapshot(value)
    if (type(value) is not dict or set(value) != {"schema", "adapter", "issuer", "tenant_id", "resource_id"}
            or value["schema"] != CONTEXT_SCHEMA or any(not _text(value[k]) for k in (
                "adapter", "issuer", "tenant_id", "resource_id"))
            or len(canonical_json(value)) > MAX_CONTEXT_BYTES):
        raise CollectorError("invalid_source_context")
    return value


def _clock(clock_ns: Callable[[], int] | None) -> tuple[str, int]:
    value = (clock_ns or time.time_ns)()
    if type(value) is not int or value < 0 or NANO_RE.fullmatch(str(value)) is None:
        raise CollectorError("invalid_capture_clock")
    rounded = (value + NANOSECONDS - 1) // NANOSECONDS
    if not _integer(rounded):
        raise CollectorError("invalid_capture_clock")
    return str(value), rounded


def _time_pair(nanoseconds: Any, seconds: Any) -> bool:
    return (type(nanoseconds) is str and NANO_RE.fullmatch(nanoseconds) is not None
            and _integer(seconds) and seconds == (int(nanoseconds) + NANOSECONDS - 1) // NANOSECONDS)


def _keys(public_key: bytes, private_key: bytes | None) -> tuple[Ed25519PublicKey, Ed25519PrivateKey | None]:
    if type(public_key) is not bytes or len(public_key) != 32:
        raise CollectorError("invalid_trusted_public_key")
    public = Ed25519PublicKey.from_public_bytes(public_key)
    private = None
    if private_key is not None:
        if type(private_key) is not bytes or len(private_key) != 32:
            raise CollectorError("invalid_private_key")
        private = Ed25519PrivateKey.from_private_bytes(private_key)
        actual = private.public_key().public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        if actual != public_key:
            raise CollectorError("private_and_trusted_key_mismatch")
    return public, private


def _sign(payload: dict, key_id: str, private: Ed25519PrivateKey) -> dict:
    signed = {"key_id": key_id, "payload": _snapshot(payload)}
    return {**signed, "signature": private.sign(SIGNING_DOMAIN + canonical_json(signed)).hex()}


def _verify(envelope: Any, public: Ed25519PublicKey) -> dict:
    if (type(envelope) is not dict or set(envelope) != {"key_id", "payload", "signature"}
            or not _text(envelope["key_id"], 256) or type(envelope["payload"]) is not dict
            or type(envelope["signature"]) is not str
            or re.fullmatch(r"[0-9a-f]{128}", envelope["signature"]) is None):
        raise CollectorError("invalid_custody_envelope")
    try:
        public.verify(bytes.fromhex(envelope["signature"]), SIGNING_DOMAIN + canonical_json(
            {"key_id": envelope["key_id"], "payload": envelope["payload"]}))
    except (InvalidSignature, ValueError) as exc:
        raise CollectorError("custody_signature_mismatch") from exc
    return envelope["payload"]


def _components(path: str | Path) -> tuple[bool, tuple[str, ...]]:
    if not isinstance(path, (str, Path)):
        raise CollectorError("invalid_path")
    value = os.fspath(path)
    if not value or "\x00" in value or ".." in value.split("/"):
        raise CollectorError("unsafe_path")
    parsed = Path(value)
    parts = tuple(part for part in parsed.parts if part not in ("/", "."))
    if not parts:
        raise CollectorError("unsafe_path")
    return parsed.is_absolute(), parts


def _directory(path: str | Path, *, create_leaf: bool = False) -> int:
    absolute, parts = _components(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC
    fd = os.open("/" if absolute else ".", flags)
    try:
        for index, part in enumerate(parts):
            if create_leaf and index == len(parts) - 1:
                try:
                    os.mkdir(part, 0o700, dir_fd=fd)
                    os.fsync(fd)
                except FileExistsError:
                    pass
            next_fd = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = next_fd
        return fd
    except OSError as exc:
        os.close(fd)
        raise CollectorError("unsafe_or_missing_directory") from exc


def _parent(path: str | Path) -> tuple[int, str]:
    absolute, parts = _components(path)
    if len(parts) == 1:
        return os.open("/" if absolute else ".", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC), parts[0]
    parent = Path("/" if absolute else ".").joinpath(*parts[:-1])
    return _directory(parent), parts[-1]


def _private_directory(fd: int) -> None:
    info = os.fstat(fd)
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o700:
        raise CollectorError("unsafe_store_directory")


def _regular(fd: int, *, private: bool, maximum: int) -> os.stat_result:
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise CollectorError("nonregular_or_linked_file")
    if info.st_size < 0 or info.st_size > maximum:
        raise CollectorError("file_size_limit")
    if private and (info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o600):
        raise CollectorError("unsafe_private_file")
    return info


def _read_fd(fd: int, *, private: bool, maximum: int) -> bytes:
    before = _regular(fd, private=private, maximum=maximum)
    data = bytearray()
    while len(data) <= maximum:
        chunk = os.read(fd, min(65536, maximum + 1 - len(data)))
        if not chunk:
            break
        data.extend(chunk)
    after = _regular(fd, private=private, maximum=maximum)
    facts = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
    if len(data) > maximum or len(data) != before.st_size or facts(before) != facts(after):
        raise CollectorError("file_changed_during_read")
    return bytes(data)


def _read_at(directory_fd: int, name: str, *, private: bool = True, maximum: int = MAX_ARTIFACT_BYTES) -> bytes:
    try:
        fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=directory_fd)
    except OSError as exc:
        raise CollectorError("unsafe_or_missing_file") from exc
    try:
        return _read_fd(fd, private=private, maximum=maximum)
    finally:
        os.close(fd)


def _read_path(path: str | Path, *, private: bool = False, maximum: int = MAX_ARTIFACT_BYTES) -> bytes:
    fd, name = _parent(path)
    try:
        return _read_at(fd, name, private=private, maximum=maximum)
    finally:
        os.close(fd)


def _write_all(fd: int, raw: bytes) -> None:
    view = memoryview(raw)
    while view:
        written = os.write(fd, view)
        if written <= 0:
            raise CollectorError("short_file_write")
        view = view[written:]
    os.fsync(fd)


_libc = ctypes.CDLL(None, use_errno=True)
_renameat2 = getattr(_libc, "renameat2", None)
if _renameat2 is not None:
    _renameat2.argtypes = (ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint)
    _renameat2.restype = ctypes.c_int


def _publish(source_fd: int, source: str, target_fd: int, target: str) -> None:
    if _renameat2 is None:
        raise CollectorError("atomic_no_replace_unavailable")
    if _renameat2(source_fd, os.fsencode(source), target_fd, os.fsencode(target), 1) != 0:
        code = ctypes.get_errno()
        if code == errno.EEXIST:
            raise FileExistsError("target_exists")
        raise CollectorError("atomic_publication_failed")
    os.fsync(target_fd)
    if target_fd != source_fd:
        os.fsync(source_fd)


def _names(fd: int) -> list[str]:
    result = []
    with os.scandir(fd) as entries:
        for entry in entries:
            result.append(entry.name)
            if len(result) > MAX_DIRECTORY_ENTRIES:
                raise CollectorError("directory_entry_limit")
    return sorted(result)


def _open_private(directory_fd: int, name: str, *, create: bool = False, maximum: int) -> int:
    flags = os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC
    if create:
        flags |= os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(name, flags, 0o600, dir_fd=directory_fd)
    except OSError as exc:
        raise CollectorError("unsafe_or_missing_private_file") from exc
    try:
        if create:
            os.fchmod(fd, 0o600)
        _regular(fd, private=True, maximum=maximum)
        return fd
    except BaseException:
        os.close(fd)
        raise


def _entry_matches(directory_fd: int, name: str, fd: int) -> None:
    try:
        entry = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
    except OSError as exc:
        raise CollectorError("store_entry_replaced") from exc
    actual = os.fstat(fd)
    if (entry.st_dev, entry.st_ino) != (actual.st_dev, actual.st_ino):
        raise CollectorError("store_entry_replaced")


def _manifest(envelope: dict, public: Ed25519PublicKey) -> dict:
    payload = _verify(envelope, public)
    fields = {"schema", "store_id", "collector_id", "created_time_ns", "created_time"}
    if (set(payload) != fields or payload["schema"] != STORE_SCHEMA
            or type(payload["store_id"]) is not str or re.fullmatch(r"[0-9a-f]{32}", payload["store_id"]) is None
            or not _text(payload["collector_id"], 256)
            or not _time_pair(payload["created_time_ns"], payload["created_time"])):
        raise CollectorError("invalid_store_manifest")
    return payload


def _receipt(envelope: dict, public: Ed25519PublicKey, manifest: dict) -> dict:
    payload = _verify(envelope, public)
    fields = {"schema", "store_id", "collector_id", "request_id", "sequence", "previous_receipt_sha256",
              "artifact_sha256", "artifact_size", "context", "received_time_ns", "received_time"}
    if (set(payload) != fields or payload["schema"] != RECEIPT_SCHEMA
            or not _text(payload["request_id"], 256) or not _integer(payload["sequence"])
            or not 1 <= payload["sequence"] <= MAX_RECORDS
            or not _hash(payload["artifact_sha256"]) or not _integer(payload["artifact_size"])
            or payload["artifact_size"] > MAX_ARTIFACT_BYTES
            or payload["previous_receipt_sha256"] is not None and not _hash(payload["previous_receipt_sha256"])
            or not _time_pair(payload["received_time_ns"], payload["received_time"])):
        raise CollectorError("invalid_custody_receipt")
    if (envelope["key_id"] != manifest["key_id"]
            or any(payload[k] != manifest["payload"][k] for k in ("store_id", "collector_id"))):
        raise CollectorError("receipt_store_binding_mismatch")
    _context(payload["context"])
    return payload


def _json_text(value: Any, code: str) -> dict:
    if type(value) is not str or len(value.encode("utf-8")) > MAX_METADATA_BYTES:
        raise CollectorError(code)
    try:
        result = load_json(value)
        if canonical_json(result).decode("utf-8") != value:
            raise CollectorError(code)
        return result
    except (ValueError, TypeError) as exc:
        raise CollectorError(code) from exc


def _configure(connection: sqlite3.Connection, *, creating: bool = False) -> None:
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA trusted_schema=OFF")
    connection.enable_load_extension(False)
    if hasattr(connection, "setconfig") and hasattr(sqlite3, "SQLITE_DBCONFIG_DEFENSIVE"):
        connection.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE, True)
    connection.execute("PRAGMA busy_timeout=5000")
    if creating:
        connection.execute("PRAGMA journal_mode=DELETE")
    elif connection.execute("PRAGMA journal_mode").fetchone()[0] != "delete":
        raise CollectorError("unsupported_database_journal")
    connection.execute("PRAGMA synchronous=FULL")


def _schema(connection: sqlite3.Connection) -> None:
    if (connection.execute("PRAGMA application_id").fetchone()[0] != APPLICATION_ID
            or connection.execute("PRAGMA user_version").fetchone()[0] != 1):
        raise CollectorError("database_header_mismatch")
    objects = connection.execute("SELECT type,name,sql FROM sqlite_schema ORDER BY name").fetchall()
    tables = {row["name"]: row["sql"] for row in objects if row["type"] == "table"}
    expected = {"metadata": METADATA_SQL, "receipts": RECEIPTS_SQL}
    squash = lambda value: " ".join(value.split()) if type(value) is str else None
    if set(tables) != set(expected) or any(squash(tables[k]) != squash(v) for k, v in expected.items()):
        raise CollectorError("database_schema_mismatch")
    permitted_indexes = {"sqlite_autoindex_metadata_1", "sqlite_autoindex_receipts_1", "sqlite_autoindex_receipts_2"}
    if any(row["type"] != "table" and not (
            row["type"] == "index" and row["name"] in permitted_indexes and row["sql"] is None) for row in objects):
        raise CollectorError("unexpected_database_object")
    if [row[0] for row in connection.execute("PRAGMA quick_check")] != ["ok"]:
        raise CollectorError("database_integrity_failure")


def _load_manifest(connection: sqlite3.Connection, public: Ed25519PublicKey) -> dict:
    rows = connection.execute("SELECT key,value FROM metadata LIMIT 2").fetchall()
    if len(rows) != 1 or rows[0]["key"] != "manifest":
        raise CollectorError("manifest_index_mismatch")
    envelope = _json_text(rows[0]["value"], "invalid_manifest_encoding")
    _manifest(envelope, public)
    return envelope


def initialize_store(path, *, collector_id, key_id, private_key, trusted_public_key, clock_ns=None):
    """Create an owner-only local store with a signed manifest; no trust is stored."""
    public, private = _keys(trusted_public_key, private_key)
    if private is None or not _text(collector_id, 256) or not _text(key_id, 256):
        raise CollectorError("invalid_store_identity")
    _snapshot({"collector_id": collector_id, "key_id": key_id})
    root = _directory(path, create_leaf=True)
    lock = None
    try:
        _private_directory(root)
        entries = _names(root)
        required = {LOCK_NAME, DATABASE_NAME, BLOB_DIRECTORY, STAGING_DIRECTORY}
        if set(entries) - (required | {DATABASE_NAME + "-journal"}):
            raise CollectorError("unexpected_store_entry")
        fresh = not entries
        if not fresh and not required <= set(entries):
            # A partial old layout is evidence of damage or incomplete creation,
            # never permission to replace identity, index, lock or directories.
            raise CollectorError("incomplete_existing_store")
        lock = _open_private(root, LOCK_NAME, create=fresh, maximum=0)
        fcntl.flock(lock, fcntl.LOCK_EX)
        _entry_matches(root, LOCK_NAME, lock)
        if not fresh:
            # Repeated initialization verifies existing custody instead of replacing it.
            fcntl.flock(lock, fcntl.LOCK_UN)
            with Collector(path, trusted_public_key=trusted_public_key, private_key=private_key) as store:
                store.audit()
                manifest = store.manifest
                if manifest["key_id"] != key_id or manifest["payload"]["collector_id"] != collector_id:
                    raise CollectorError("existing_store_identity_mismatch")
                return _snapshot(manifest)
        if set(_names(root)) != {LOCK_NAME}:
            raise CollectorError("store_changed_during_initialization")
        for name in (BLOB_DIRECTORY, STAGING_DIRECTORY):
            os.mkdir(name, 0o700, dir_fd=root)
            fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=root)
            try:
                _private_directory(fd)
            finally:
                os.close(fd)
        dbfd = _open_private(root, DATABASE_NAME, create=True, maximum=MAX_DATABASE_BYTES)
        connection = None
        try:
            connection = sqlite3.connect(f"file:/proc/self/fd/{root}/{DATABASE_NAME}?mode=rw", uri=True,
                                         isolation_level=None, timeout=5)
            _configure(connection, creating=True)
            ns, seconds = _clock(clock_ns)
            manifest = _sign({"schema": STORE_SCHEMA, "store_id": secrets.token_hex(16),
                              "collector_id": collector_id, "created_time_ns": ns,
                              "created_time": seconds}, key_id, private)
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(METADATA_SQL)
            connection.execute(RECEIPTS_SQL)
            connection.execute(f"PRAGMA application_id={APPLICATION_ID}")
            connection.execute("PRAGMA user_version=1")
            connection.execute("INSERT INTO metadata(key,value) VALUES (?,?)",
                               ("manifest", canonical_json(manifest).decode("utf-8")))
            connection.commit()
            _entry_matches(root, DATABASE_NAME, dbfd)
            os.fsync(dbfd)
            os.fsync(root)
            return _snapshot(manifest)
        except sqlite3.Error as exc:
            raise CollectorError("database_initialization_failed") from exc
        finally:
            if connection is not None:
                connection.close()
            os.close(dbfd)
    except OSError as exc:
        raise CollectorError("store_initialization_io_failure") from exc
    finally:
        if lock is not None:
            fcntl.flock(lock, fcntl.LOCK_UN)
            os.close(lock)
        os.close(root)


class Collector:
    """Serialized local custody; injected clocks/hooks are API-only test facilities."""

    def __init__(self, path, *, trusted_public_key, private_key=None, clock_ns=None, hook=None):
        self.public, self.private = _keys(trusted_public_key, private_key)
        self.path, self.clock_ns, self.hook = path, clock_ns, hook
        self.root = self.lock = self.blobs = self.staging = None
        self.manifest = None
        try:
            self.root = _directory(path)
            _private_directory(self.root)
            self.lock = _open_private(self.root, LOCK_NAME, maximum=0)
            for field, name in (("blobs", BLOB_DIRECTORY), ("staging", STAGING_DIRECTORY)):
                fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=self.root)
                setattr(self, field, fd)
                _private_directory(fd)
            with self._locked(), self._connection() as connection:
                self.manifest = _load_manifest(connection, self.public)
        except BaseException:
            self.close()
            raise

    def close(self):
        for field in ("staging", "blobs", "lock", "root"):
            fd = getattr(self, field, None)
            if fd is not None:
                os.close(fd)
                setattr(self, field, None)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    @contextmanager
    def _locked(self):
        if self.lock is None:
            raise CollectorError("store_closed")
        fcntl.flock(self.lock, fcntl.LOCK_EX)
        try:
            _private_directory(self.root)
            anchor = _directory(self.path)
            try:
                a, b = os.fstat(anchor), os.fstat(self.root)
                if (a.st_dev, a.st_ino) != (b.st_dev, b.st_ino):
                    raise CollectorError("store_path_replaced")
            finally:
                os.close(anchor)
            permitted = {LOCK_NAME, DATABASE_NAME, DATABASE_NAME + "-journal", BLOB_DIRECTORY, STAGING_DIRECTORY}
            entries = set(_names(self.root))
            if not {LOCK_NAME, DATABASE_NAME, BLOB_DIRECTORY, STAGING_DIRECTORY} <= entries or entries - permitted:
                raise CollectorError("unexpected_store_layout")
            _entry_matches(self.root, LOCK_NAME, self.lock)
            _regular(self.lock, private=True, maximum=0)
            for name, fd in ((BLOB_DIRECTORY, self.blobs), (STAGING_DIRECTORY, self.staging)):
                _entry_matches(self.root, name, fd)
                _private_directory(fd)
            journal = DATABASE_NAME + "-journal"
            if journal in entries:
                _read_at(self.root, journal, maximum=MAX_DATABASE_BYTES)
            yield
        except OSError as exc:
            raise CollectorError("store_io_failure") from exc
        finally:
            fcntl.flock(self.lock, fcntl.LOCK_UN)

    @contextmanager
    def _connection(self):
        dbfd = _open_private(self.root, DATABASE_NAME, maximum=MAX_DATABASE_BYTES)
        connection = None
        try:
            connection = sqlite3.connect(f"file:/proc/self/fd/{self.root}/{DATABASE_NAME}?mode=rw", uri=True,
                                         isolation_level=None, timeout=5)
            _configure(connection)
            _entry_matches(self.root, DATABASE_NAME, dbfd)
            _schema(connection)
            yield connection
            _entry_matches(self.root, DATABASE_NAME, dbfd)
            _regular(dbfd, private=True, maximum=MAX_DATABASE_BYTES)
        except sqlite3.Error as exc:
            raise CollectorError("database_operation_failed") from exc
        finally:
            if connection is not None:
                connection.close()
            os.close(dbfd)

    def _audit(self, connection, checkpoint=None):
        manifest = _load_manifest(connection, self.public)
        if manifest != self.manifest:
            raise CollectorError("store_manifest_changed")
        rows = connection.execute("SELECT * FROM receipts ORDER BY sequence").fetchmany(MAX_RECORDS + 1)
        if len(rows) > MAX_RECORDS:
            raise CollectorError("store_record_limit")
        receipts, by_request, blob_bytes = [], {}, {}
        previous = None
        previous_ns = int(manifest["payload"]["created_time_ns"])
        for sequence, row in enumerate(rows, 1):
            receipt = _json_text(row["receipt_json"], "invalid_receipt_encoding")
            payload = _receipt(receipt, self.public, manifest)
            if (payload["sequence"] != sequence or payload["previous_receipt_sha256"] != previous
                    or int(payload["received_time_ns"]) < previous_ns):
                raise CollectorError("receipt_chain_or_time_mismatch")
            reference = digest(receipt)
            expected = {"sequence": sequence, "request_id": payload["request_id"],
                        "artifact_sha256": payload["artifact_sha256"], "artifact_size": payload["artifact_size"],
                        "context_json": canonical_json(payload["context"]).decode("utf-8"),
                        "received_time_ns": payload["received_time_ns"], "received_time": payload["received_time"],
                        "previous_receipt_sha256": previous, "receipt_sha256": reference,
                        "receipt_json": canonical_json(receipt).decode("utf-8")}
            if any(row[key] != value or type(row[key]) is not type(value) for key, value in expected.items()):
                raise CollectorError("receipt_index_mismatch")
            if payload["request_id"] in by_request:
                raise CollectorError("duplicate_request_index")
            artifact = payload["artifact_sha256"]
            if artifact not in blob_bytes:
                blob_bytes[artifact] = _read_at(self.blobs, artifact[7:] + ".bin")
            raw = blob_bytes[artifact]
            if bytes_digest(raw) != artifact or len(raw) != payload["artifact_size"]:
                raise CollectorError("committed_artifact_mismatch")
            receipts.append(receipt)
            by_request[payload["request_id"]] = receipt
            previous, previous_ns = reference, int(payload["received_time_ns"])
        orphan_count = 0
        for name in _names(self.blobs):
            if re.fullmatch(r"[0-9a-f]{64}\.bin", name) is None:
                raise CollectorError("unexpected_blob_name")
            artifact = "sha256:" + name[:-4]
            if artifact not in blob_bytes:
                raw = _read_at(self.blobs, name)
                if bytes_digest(raw) != artifact:
                    raise CollectorError("uncommitted_artifact_mismatch")
                orphan_count += 1
        staging_names = _names(self.staging)
        for name in staging_names:
            if re.fullmatch(r"[0-9a-f]{32}\.part", name) is None:
                raise CollectorError("unexpected_staging_name")
            _read_at(self.staging, name)
        checkpoint_status = "not_provided"
        if checkpoint is not None:
            checkpoint = _snapshot(checkpoint)
            payload = _verify(checkpoint, self.public)
            fields = {"schema", "store_id", "collector_id", "sequence", "receipt_sha256", "issued_time_ns", "issued_time"}
            if (set(payload) != fields or payload["schema"] != CHECKPOINT_SCHEMA
                    or not _integer(payload["sequence"]) or payload["sequence"] > MAX_RECORDS
                    or not _time_pair(payload["issued_time_ns"], payload["issued_time"])
                    or checkpoint["key_id"] != manifest["key_id"]
                    or any(payload[k] != manifest["payload"][k] for k in ("store_id", "collector_id"))):
                raise CollectorError("invalid_external_checkpoint")
            sequence = payload["sequence"]
            if sequence > len(receipts):
                raise CollectorError("checkpoint_prefix_missing")
            expected = digest(receipts[sequence - 1]) if sequence else None
            witness_ns = int(receipts[sequence - 1]["payload"]["received_time_ns"]) if sequence else int(
                manifest["payload"]["created_time_ns"])
            if payload["receipt_sha256"] != expected or int(payload["issued_time_ns"]) < witness_ns:
                raise CollectorError("checkpoint_prefix_mismatch")
            checkpoint_status = "matched"
        summary = {"schema": AUDIT_SCHEMA, "store_id": manifest["payload"]["store_id"],
                   "record_count": len(receipts), "head_sequence": len(receipts), "head_receipt_sha256": previous,
                   "local_integrity": "supported", "checkpoint_status": checkpoint_status,
                   "rollback_assessment": ("not_assessed" if checkpoint is None
                                           else "consistent_with_retained_checkpoint_only"),
                   "completeness": "unresolved", "orphan_blob_count": orphan_count,
                   "staging_file_count": len(staging_names), "independent_custody": False}
        return summary, receipts, by_request, blob_bytes

    def collect_file(self, input_path, *, request_id, context):
        if self.private is None:
            raise CollectorError("signing_key_required")
        if not _text(request_id, 256):
            raise CollectorError("invalid_request_id")
        request_id = _snapshot(request_id)
        context = _context(context)
        raw = _read_path(input_path)
        artifact = bytes_digest(raw)
        with self._locked(), self._connection() as connection:
            summary, receipts, by_request, _ = self._audit(connection)
            if request_id in by_request:
                original = by_request[request_id]
                payload = original["payload"]
                if (payload["artifact_sha256"] != artifact or payload["artifact_size"] != len(raw)
                        or payload["context"] != context):
                    raise CollectorError("conflicting_request_retry")
                # Full audit above re-read the retained original, not just its index.
                retained = _read_at(self.blobs, artifact[7:] + ".bin")
                if retained != raw:
                    raise CollectorError("committed_artifact_mismatch")
                return _snapshot(original)
            if len(receipts) >= MAX_RECORDS:
                raise CollectorError("store_record_limit")
            metadata = {"request_id": request_id, "sequence": len(receipts) + 1,
                        "artifact_sha256": artifact, "artifact_size": len(raw)}
            stage_name = secrets.token_hex(16) + ".part"
            fd = _open_private(self.staging, stage_name, create=True, maximum=MAX_ARTIFACT_BYTES)
            try:
                _write_all(fd, raw)
            finally:
                os.close(fd)
            os.fsync(self.staging)
            self._hook("after_staging_fsync", metadata)
            blob_name = artifact[7:] + ".bin"
            try:
                _publish(self.staging, stage_name, self.blobs, blob_name)
            except FileExistsError:
                # A known content-addressed orphan is adoptable only by exact bytes.
                # No existing original, indexed or unindexed, is ever overwritten.
                retained = _read_at(self.blobs, blob_name)
                if retained != raw or bytes_digest(retained) != artifact:
                    raise CollectorError("existing_artifact_conflict")
                os.unlink(stage_name, dir_fd=self.staging)
                os.fsync(self.staging)
            self._hook("after_blob_publish", metadata)
            ns, seconds = _clock(self.clock_ns)
            previous_ns = int(receipts[-1]["payload"]["received_time_ns"]) if receipts else int(
                self.manifest["payload"]["created_time_ns"])
            if int(ns) < previous_ns:
                raise CollectorError("capture_clock_regressed")
            payload = {"schema": RECEIPT_SCHEMA, "store_id": self.manifest["payload"]["store_id"],
                       "collector_id": self.manifest["payload"]["collector_id"], "request_id": request_id,
                       "sequence": metadata["sequence"], "previous_receipt_sha256": summary["head_receipt_sha256"],
                       "artifact_sha256": artifact, "artifact_size": len(raw), "context": context,
                       "received_time_ns": ns, "received_time": seconds}
            receipt = _sign(payload, self.manifest["key_id"], self.private)
            try:
                connection.execute("BEGIN IMMEDIATE")
                current, _, _, _ = self._audit(connection)
                if current["head_sequence"] != summary["head_sequence"] or current["head_receipt_sha256"] != summary[
                        "head_receipt_sha256"]:
                    raise CollectorError("store_changed_during_capture")
                connection.execute("""INSERT INTO receipts
                    (sequence,request_id,artifact_sha256,artifact_size,context_json,received_time_ns,
                     received_time,previous_receipt_sha256,receipt_sha256,receipt_json)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",
                    (payload["sequence"], request_id, artifact, len(raw), canonical_json(context).decode("utf-8"),
                     ns, seconds, payload["previous_receipt_sha256"], digest(receipt),
                     canonical_json(receipt).decode("utf-8")))
                self._hook("before_commit", metadata)
                connection.commit()
                os.fsync(self.root)
            except BaseException:
                if connection.in_transaction:
                    connection.rollback()
                raise
            self._hook("after_commit", metadata)
            return _snapshot(receipt)

    def get_receipt(self, request_id):
        if not _text(request_id, 256):
            raise CollectorError("invalid_request_id")
        with self._locked(), self._connection() as connection:
            _, _, by_request, _ = self._audit(connection)
            if request_id not in by_request:
                raise CollectorError("request_not_collected")
            return _snapshot(by_request[request_id])

    def audit(self, *, checkpoint=None):
        checkpoint = _snapshot(checkpoint) if checkpoint is not None else None
        with self._locked(), self._connection() as connection:
            summary, _, _, _ = self._audit(connection, checkpoint)
            return summary

    def checkpoint(self):
        if self.private is None:
            raise CollectorError("signing_key_required")
        with self._locked(), self._connection() as connection:
            summary, receipts, _, _ = self._audit(connection)
            ns, seconds = _clock(self.clock_ns)
            previous_ns = int(receipts[-1]["payload"]["received_time_ns"]) if receipts else int(
                self.manifest["payload"]["created_time_ns"])
            if int(ns) < previous_ns:
                raise CollectorError("capture_clock_regressed")
            return _sign({"schema": CHECKPOINT_SCHEMA, "store_id": summary["store_id"],
                          "collector_id": self.manifest["payload"]["collector_id"],
                          "sequence": summary["head_sequence"], "receipt_sha256": summary["head_receipt_sha256"],
                          "issued_time_ns": ns, "issued_time": seconds}, self.manifest["key_id"], self.private)

    def export_native(self, request_id, output_path, *, checkpoint=None):
        if self.private is None:
            raise CollectorError("signing_key_required")
        if not _text(request_id, 256):
            raise CollectorError("invalid_request_id")
        checkpoint = _snapshot(checkpoint) if checkpoint is not None else None
        with self._locked(), self._connection() as connection:
            _, _, by_request, blobs = self._audit(connection, checkpoint)
            if request_id not in by_request:
                raise CollectorError("request_not_collected")
            receipt = by_request[request_id]
            payload = receipt["payload"]
            context = payload["context"]
            raw = blobs[payload["artifact_sha256"]]
            try:
                text = raw.decode("utf-8", errors="strict")
                normalized = evidence.normalize_record(context["adapter"], text)
            except (ValueError, TypeError) as exc:
                raise CollectorError("unsupported_native_mapping") from exc
            if text.encode("utf-8") != raw or normalized["source_kind_conflict"]:
                raise CollectorError("unsupported_native_mapping")
            for field in ("tenant_id", "resource_id"):
                if normalized[field] is not None and normalized[field] != context[field]:
                    raise CollectorError("native_source_context_conflict")
            record_id = "custody:" + digest(receipt)
            native = {"schema": evidence.RECORD_SCHEMA, "record_id": record_id,
                      "issuer": context["issuer"], "role": "collector", "tenant_id": context["tenant_id"],
                      "resource_id": context["resource_id"], "event_time": None, "available_time": None,
                      "received_time": payload["received_time"], "kind": "native",
                      "body": {"adapter": context["adapter"], "raw": text,
                               "raw_sha256": payload["artifact_sha256"], "claimed_normalized": None}}
            envelope = evidence.sign_envelope(native, self.manifest["key_id"], self.private)
            self._write_output(output_path, canonical_json(envelope) + b"\n")
            return {"record_id": record_id, "artifact_sha256": payload["artifact_sha256"],
                    "custody_receipt_sha256": digest(receipt), "native_envelope_sha256": digest(envelope),
                    "received_time": payload["received_time"]}

    def _hook(self, name: str, metadata: dict) -> None:
        if self.hook is not None:
            self.hook(name, _snapshot(metadata))

    def _outside_store(self, parent_fd: int) -> None:
        target = os.fstat(self.root)
        current = os.dup(parent_fd)
        try:
            for _ in range(256):
                info = os.fstat(current)
                if (info.st_dev, info.st_ino) == (target.st_dev, target.st_ino):
                    raise CollectorError("output_must_be_outside_store")
                parent = os.open("..", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=current)
                above = os.fstat(parent)
                if (above.st_dev, above.st_ino) == (info.st_dev, info.st_ino):
                    os.close(parent)
                    return
                os.close(current)
                current = parent
            raise CollectorError("output_ancestor_limit")
        finally:
            os.close(current)

    def _write_output(self, path, raw: bytes) -> None:
        parent, name = _parent(path)
        stage_name = ".cloud-custody-export-" + secrets.token_hex(16) + ".part"
        created = False
        try:
            self._outside_store(parent)
            fd = _open_private(parent, stage_name, create=True, maximum=evidence.MAX_DOCUMENT)
            created = True
            try:
                _write_all(fd, raw)
            finally:
                os.close(fd)
            try:
                _publish(parent, stage_name, parent, name)
            except FileExistsError as exc:
                raise CollectorError("output_already_exists") from exc
            created = False
        except OSError as exc:
            raise CollectorError("output_io_failure") from exc
        finally:
            if created:
                os.unlink(stage_name, dir_fd=parent)
                os.fsync(parent)
            os.close(parent)


def _cli_metadata(path: Path, *, maximum: int = MAX_METADATA_BYTES) -> Any:
    try:
        return load_json(_read_path(path, maximum=maximum))
    except (ValueError, TypeError) as exc:
        raise CollectorError("invalid_metadata_input") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("init", "collect", "audit", "checkpoint", "export-native"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--store", required=True, type=Path)
        subparser.add_argument("--public-key-file", required=True, type=Path)
        if command != "audit":
            subparser.add_argument("--private-key-file", required=True, type=Path)
        if command == "init":
            subparser.add_argument("--collector-id", required=True)
            subparser.add_argument("--key-id", required=True)
        if command in ("collect", "export-native"):
            subparser.add_argument("--request-id", required=True)
        if command == "collect":
            subparser.add_argument("--input", required=True, type=Path)
            subparser.add_argument("--context", required=True, type=Path)
        if command in ("checkpoint", "export-native"):
            subparser.add_argument("--out", required=True, type=Path)
        if command in ("audit", "export-native"):
            subparser.add_argument("--checkpoint", type=Path)
    args = parser.parse_args(argv)
    try:
        public = _read_path(args.public_key_file, maximum=32)
        private_path = getattr(args, "private_key_file", None)
        private = _read_path(private_path, private=True, maximum=32) if private_path is not None else None
        if args.command == "init":
            manifest = initialize_store(args.store, collector_id=args.collector_id, key_id=args.key_id,
                                        private_key=private, trusted_public_key=public)
            result = {"store_id": manifest["payload"]["store_id"], "manifest_sha256": digest(manifest)}
        else:
            with Collector(args.store, trusted_public_key=public, private_key=private) as store:
                checkpoint_path = getattr(args, "checkpoint", None)
                checkpoint = _cli_metadata(checkpoint_path) if checkpoint_path is not None else None
                if args.command == "collect":
                    receipt = store.collect_file(args.input, request_id=args.request_id, context=_cli_metadata(args.context))
                    payload = receipt["payload"]
                    result = {"store_id": payload["store_id"], "sequence": payload["sequence"],
                              "artifact_sha256": payload["artifact_sha256"], "artifact_size": payload["artifact_size"],
                              "custody_receipt_sha256": digest(receipt), "received_time": payload["received_time"],
                              "received_time_ns": payload["received_time_ns"]}
                elif args.command == "audit":
                    result = store.audit(checkpoint=checkpoint)
                elif args.command == "checkpoint":
                    checkpoint = store.checkpoint()
                    store._write_output(args.out, canonical_json(checkpoint) + b"\n")
                    result = {"store_id": checkpoint["payload"]["store_id"],
                              "sequence": checkpoint["payload"]["sequence"], "checkpoint_sha256": digest(checkpoint)}
                else:
                    result = store.export_native(args.request_id, args.out, checkpoint=checkpoint)
        sys.stdout.buffer.write(canonical_json(result) + b"\n")
        return 0
    except CollectorError as exc:
        sys.stderr.write(canonical_json({"error": str(exc)}).decode("utf-8") + "\n")
        return 2
    except (ValueError, OSError, sqlite3.Error, TypeError, OverflowError):
        sys.stderr.write('{"error":"local_custody_operation_rejected"}\n')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
