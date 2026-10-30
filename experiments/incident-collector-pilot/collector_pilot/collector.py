"""A restartable local metadata collector with measured HTTP exchanges.

The directory and host are controller-owned. SQLite FULL is the declared local
durability assumption, not tamper-proof storage or a physical power-loss test.
Fault modes are constructor-only controls and never accepted in HTTP content.
"""

import multiprocessing
import os
import socket
import sqlite3
import stat
import uuid
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from upload_pilot.receiver import _BoundedHeaderReader
from upload_pilot.transport import checked_headers, content_length

from .protocol import (
    MAX_CONTROL, InputError, _exact, _hex, _text, canonical, decode_json, digest,
    public_key, sign_control, timestamp, utc_now, validate_endpoint, validate_intent,
    validate_query, verify_control, verify_receipt,
)


MODES = {"normal", "drop_before_commit", "drop_after_commit", "wrong_receipt", "wrong_status_nonce"}
IDENTITY_FIELDS = {
    "format", "collector_id", "gateway_public", "gateway_key_id",
    "collector_public", "collector_key_id", "endpoint",
}
ROW_SELECT = "SELECT collection_id,request_id,request_sha256,intent_json,receipt_json FROM collections"


class _DropConnection(Exception):
    """An explicit synthetic pre-commit rollback, followed by response loss."""


def _checked_path(path, *, directory=False):
    try:
        info = path.lstat()
    except FileNotFoundError:
        return False
    correct = stat.S_ISDIR(info.st_mode) if directory else stat.S_ISREG(info.st_mode)
    if not correct or info.st_uid != os.getuid():
        raise InputError("Collector storage must be an owned regular path")
    return True


def _storage_paths(path):
    # This detects ordinary replacement/symlink mistakes. It does not claim to
    # isolate this controller from a malicious process with the same user ID.
    _checked_path(path.parent, directory=True)
    for candidate in (path, Path(str(path) + "-wal"), Path(str(path) + "-shm")):
        _checked_path(candidate)


def _connect(path, *, readonly=False):
    _storage_paths(path)
    if readonly:
        return sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=2.0, isolation_level=None)
    connection = sqlite3.connect(str(path), timeout=2.0, isolation_level=None)
    try:
        mode = connection.execute("PRAGMA journal_mode=WAL").fetchone()[0]
        connection.execute("PRAGMA synchronous=FULL")
        synchronous = connection.execute("PRAGMA synchronous").fetchone()[0]
        connection.execute("PRAGMA busy_timeout=2000")
        if str(mode).lower() != "wal" or synchronous != 2:
            raise InputError("Required collector SQLite WAL/FULL configuration is unavailable")
        return connection
    except BaseException:
        connection.close()
        raise


def _identity(connection):
    if connection.execute("PRAGMA user_version").fetchone()[0] != 1:
        raise InputError("Unsupported collector database version")
    columns = {
        "metadata": [("id", "INTEGER"), ("identity_json", "TEXT")],
        "stats": [("name", "TEXT"), ("value", "INTEGER")],
        "collections": [("collection_id", "TEXT"), ("request_id", "TEXT"),
                        ("request_sha256", "TEXT"), ("intent_json", "TEXT"), ("receipt_json", "TEXT")],
    }
    tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if tables != columns.keys():
        raise InputError("Unexpected collector database tables")
    for table, expected in columns.items():
        info = connection.execute("PRAGMA table_info(" + table + ")").fetchall()
        if [(row[1], row[2]) for row in info] != expected or info[0][5] != 1:
            raise InputError("Unexpected collector database layout")
    rows = connection.execute("SELECT id,identity_json FROM metadata").fetchall()
    if len(rows) != 1 or rows[0][0] != 1:
        raise InputError("Collector database identity is unavailable")
    identity = _exact(decode_json(rows[0][1]), IDENTITY_FIELDS)
    if identity["format"] != "collector-pilot-store/0.1":
        raise InputError("Unsupported collector identity format")
    for key in ("collector_id", "gateway_key_id", "collector_key_id"):
        _text(identity[key])
    for key in ("gateway_public", "collector_public"):
        _hex(identity[key])
    validate_endpoint(identity["endpoint"])
    stats = connection.execute("SELECT name,value FROM stats").fetchall()
    if ({row[0] for row in stats} != {"collect_calls", "status_calls"}
            or any(type(row[1]) is not int or row[1] < 0 for row in stats)):
        raise InputError("Invalid collector counters")
    return identity


def _initialize(path, expected):
    existed = path.exists()
    with closing(_connect(path)) as connection:
        if existed:
            if _identity(connection) != expected:
                raise InputError("Persisted collector identity or endpoint differs")
            return
        os.chmod(path, 0o600)
        connection.execute("BEGIN IMMEDIATE")
        try:
            connection.execute("CREATE TABLE metadata (id INTEGER PRIMARY KEY CHECK(id=1), identity_json TEXT NOT NULL)")
            connection.execute("CREATE TABLE stats (name TEXT PRIMARY KEY NOT NULL, value INTEGER NOT NULL CHECK(value>=0))")
            connection.execute("CREATE TABLE collections (collection_id TEXT PRIMARY KEY NOT NULL, request_id TEXT UNIQUE NOT NULL, request_sha256 TEXT NOT NULL, intent_json TEXT NOT NULL, receipt_json TEXT NOT NULL)")
            connection.execute("INSERT INTO metadata VALUES (1,?)", (canonical(expected).decode("utf-8"),))
            connection.executemany("INSERT INTO stats VALUES (?,0)", [("collect_calls",), ("status_calls",)])
            connection.execute("PRAGMA user_version=1")
            connection.commit()
            if _identity(connection) != expected:
                raise InputError("Committed collector identity is not readable")
        except BaseException:
            connection.rollback()
            raise


def _row(row, identity):
    if row is None:
        return None
    collection, request, request_digest, intent_json, receipt_json = row
    _hex(collection)
    _text(request)
    _hex(request_digest)
    intent, receipt = decode_json(intent_json), decode_json(receipt_json)
    body = validate_intent(verify_control(intent, identity["gateway_public"],
                                          identity["gateway_key_id"], "collection_intent"))
    if (body["collector_id"] != identity["collector_id"] or body["collection_id"] != collection
            or body["request_id"] != request or digest(intent) != request_digest):
        raise InputError("Stored collector row does not bind its signed intent")
    verify_receipt(receipt, intent, identity["collector_public"], identity["collector_key_id"], utc_now())
    return {"collection_id": collection, "request_id": request, "request_sha256": request_digest,
            "intent": intent, "receipt": receipt}


def _find(connection, body, identity):
    rows = connection.execute(ROW_SELECT + " WHERE collection_id=? OR request_id=?",
                              (body["collection_id"], body["request_id"])).fetchall()
    if len(rows) > 1:
        raise InputError("COLLECTION_CONFLICT")
    return _row(rows[0], identity) if rows else None


def _count(path, identity, name):
    with closing(_connect(path)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            if _identity(connection) != identity:
                raise InputError("Collector persistence identity changed")
            connection.execute("UPDATE stats SET value=value+1 WHERE name=?", (name,))
            connection.commit()
        except BaseException:
            connection.rollback()
            raise


def _accept(path, identity, intent, body, secret, *, drop_before_commit=False):
    request_digest = digest(intent)
    with closing(_connect(path)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        try:
            if _identity(connection) != identity:
                raise InputError("Collector persistence identity changed")
            existing = _find(connection, body, identity)
            if existing is not None:
                if (existing["collection_id"] != body["collection_id"]
                        or existing["request_id"] != body["request_id"]
                        or existing["request_sha256"] != request_digest):
                    raise InputError("COLLECTION_CONFLICT")
                connection.rollback()
                return existing["receipt"]
            receipt = sign_control({
                "kind": "collection_receipt", "collector_id": body["collector_id"],
                "collection_id": body["collection_id"], "request_id": body["request_id"],
                "request_sha256": request_digest, "recorded_at": utc_now(),
                "receipt_id": "receipt-" + uuid.uuid4().hex, "storage": "sqlite-wal-full",
            }, secret, identity["collector_key_id"])
            connection.execute("INSERT INTO collections VALUES (?,?,?,?,?)", (
                body["collection_id"], body["request_id"], request_digest,
                canonical(intent).decode("utf-8"), canonical(receipt).decode("utf-8"),
            ))
            if drop_before_commit:
                connection.rollback()
                raise _DropConnection()
            connection.commit()
            persisted = _find(connection, body, identity)
            if (persisted is None or persisted["request_sha256"] != request_digest
                    or persisted["intent"] != intent or persisted["receipt"] != receipt):
                raise InputError("Committed collector record is not readable")
            return persisted["receipt"]
        except BaseException:
            connection.rollback()
            raise


def _lookup(path, identity, query, body, secret, *, wrong_nonce=False):
    # Request counters change separately. This lookup never creates or updates
    # a collection row and cannot authorize/resume the separate payload call.
    with closing(_connect(path, readonly=True)) as connection:
        connection.execute("BEGIN")
        if _identity(connection) != identity:
            raise InputError("Collector persistence identity changed")
        existing = _find(connection, body, identity)
        if existing is not None and (existing["collection_id"] != body["collection_id"]
                                     or existing["request_id"] != body["request_id"]
                                     or existing["request_sha256"] != body["request_sha256"]):
            raise InputError("COLLECTION_CONFLICT")
        connection.commit()
    nonce = body["nonce"]
    if wrong_nonce:
        nonce = ("1" if nonce[0] == "0" else "0") + nonce[1:]
    return sign_control({
        "kind": "collection_status", "collector_id": body["collector_id"],
        "collection_id": body["collection_id"], "request_id": body["request_id"],
        "request_sha256": body["request_sha256"], "query_sha256": digest(query),
        "nonce": nonce, "status": "FOUND" if existing is not None else "NOT_FOUND",
        "receipt": None if existing is None else existing["receipt"], "checked_at": utc_now(),
    }, secret, identity["collector_key_id"])


class _Server(HTTPServer):
    allow_reuse_address = True  # Same fixed port after owned process shutdown.

    def handle_error(self, request, client_address):
        # No request bodies, authorization, keys or uncontrolled tracebacks.
        pass


class _Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def setup(self):
        self.request.settimeout(2.0)
        super().setup()

    def log_message(self, format, *args):
        pass

    def parse_request(self):
        original = self.rfile
        self.rfile = _BoundedHeaderReader(original)
        try:
            return super().parse_request()
        finally:
            self.rfile = original

    def _reply(self, status, value):
        raw = canonical(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(raw)
        self.wfile.flush()
        self.close_connection = True

    def send_error(self, code, message=None, explain=None):
        self._reply(code, {"error": "INVALID_HTTP_REQUEST"})

    def handle_expect_100(self):
        self._reply(417, {"error": "EXPECT_CONTINUE_UNSUPPORTED"})
        return False

    def _unsupported(self):
        self._reply(405, {"error": "POST_REQUIRED"})

    do_GET = _unsupported
    do_PUT = _unsupported
    do_DELETE = _unsupported
    do_PATCH = _unsupported
    do_HEAD = _unsupported
    do_OPTIONS = _unsupported

    def _drop(self):
        try:
            self.connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        self.connection.close()

    def do_POST(self):
        self.close_connection = True
        try:
            if self.path not in {"/collect", "/status"}:
                self._reply(404, {"error": "FIXED_PATH_REQUIRED"})
                return
            counter = "collect_calls" if self.path == "/collect" else "status_calls"
            _count(self.server.db_path, self.server.identity, counter)
            headers = checked_headers(list(self.headers.items()))
            length = content_length(headers, MAX_CONTROL)
            if (headers.get("content-type") != "application/json" or "expect" in headers
                    or headers.get("host") != "127.0.0.1:" + str(self.server.server_address[1])):
                raise InputError("Unsupported collector HTTP framing")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise InputError("Incomplete collector request")
            value = decode_json(raw)
            kind = "collection_intent" if self.path == "/collect" else "collection_query"
            body = verify_control(value, self.server.identity["gateway_public"],
                                  self.server.identity["gateway_key_id"], kind)
            body = validate_intent(body) if self.path == "/collect" else validate_query(body)
            if (body["collector_id"] != self.server.identity["collector_id"]
                    or timestamp(body["created_at"]) > timestamp(utc_now())):
                raise InputError("Collector request identity or time is inapplicable")
            if self.path == "/collect":
                response = _accept(self.server.db_path, self.server.identity, value, body,
                                   self.server.collector_secret,
                                   drop_before_commit=self.server.mode == "drop_before_commit")
                if self.server.mode == "drop_after_commit":
                    self._drop()
                    return
                if self.server.mode == "wrong_receipt":
                    altered = dict(response["body"])
                    old = altered["request_sha256"]
                    altered["request_sha256"] = ("1" if old[0] == "0" else "0") + old[1:]
                    response = sign_control(altered, self.server.collector_secret,
                                            self.server.identity["collector_key_id"])
            else:
                response = _lookup(self.server.db_path, self.server.identity, value, body,
                                   self.server.collector_secret,
                                   wrong_nonce=self.server.mode == "wrong_status_nonce")
            self._reply(200, response)
        except _DropConnection:
            self._drop()
        except InputError as exc:
            conflict = str(exc) == "COLLECTION_CONFLICT"
            self._reply(409 if conflict else 400,
                        {"error": "COLLECTION_CONFLICT" if conflict else "INVALID_REQUEST"})
        except (OSError, sqlite3.Error, ValueError):
            # Committed rows may exist even when no usable response is delivered.
            # The client retains uncertainty and performs no automatic retry.
            self.close_connection = True


def _serve(path, expected, secret, port, mode, ready, stop):
    server = None
    try:
        server = _Server(("127.0.0.1", port), _Handler)
        identity = dict(expected)
        identity["endpoint"] = "http://127.0.0.1:" + str(server.server_address[1])
        _initialize(path, identity)
        server.db_path, server.identity = path, identity
        server.collector_secret, server.mode = secret, mode
        server.timeout = 0.1
        ready.send({"endpoint": identity["endpoint"]})
        ready.close()
        while not stop.is_set():
            server.handle_request()
    except BaseException as exc:
        try:
            ready.send({"error": type(exc).__name__})
        except (OSError, EOFError):
            pass
    finally:
        ready.close()
        if server is not None:
            server.server_close()


class CollectorProcess:
    def __init__(self, directory, *, collector_id, gateway_public, gateway_key_id,
                 collector_secret, collector_key_id, port=0, mode="normal"):
        if mode not in MODES:
            raise InputError("Unsupported trusted collector mode")
        if type(port) is not int or not 0 <= port <= 65535:
            raise InputError("Invalid requested collector port")
        self.directory = Path(directory).absolute()
        self._db_path = self.directory / "collector.sqlite3"
        self._base_identity = {
            "format": "collector-pilot-store/0.1", "collector_id": _text(collector_id),
            "gateway_public": _hex(gateway_public), "gateway_key_id": _text(gateway_key_id),
            "collector_public": public_key(_hex(collector_secret)), "collector_key_id": _text(collector_key_id),
        }
        self._collector_secret = collector_secret
        self._requested_port, self._mode = port, mode
        self._process, self._stop, self._endpoint, self._pid = None, None, None, None
        self.cleanup_result = {"child_stopped": True, "forced_termination": False}

    @property
    def endpoint(self):
        if self._endpoint is None:
            raise InputError("Collector has not started")
        return self._endpoint

    @property
    def pid(self):
        return self._pid

    def _start(self, mode):
        if mode not in MODES or self._process is not None:
            raise InputError("Collector mode is invalid or process is already owned")
        if not _checked_path(self.directory, directory=True):
            self.directory.mkdir(parents=True, mode=0o700, exist_ok=False)
        _storage_paths(self._db_path)
        port = self._requested_port
        expected = dict(self._base_identity)
        if self._db_path.exists():
            with closing(_connect(self._db_path, readonly=True)) as connection:
                stored = _identity(connection)
            if any(stored[key] != value for key, value in expected.items()):
                raise InputError("Persisted collector identity or key differs")
            old_port = urlsplit(stored["endpoint"]).port
            if port not in {0, old_port} or (self._endpoint is not None and self._endpoint != stored["endpoint"]):
                raise InputError("Persisted collector endpoint differs")
            port = old_port
            expected["endpoint"] = stored["endpoint"]
        context = multiprocessing.get_context("spawn")
        parent_ready, child_ready = context.Pipe(duplex=False)
        self._stop = context.Event()
        self._process = context.Process(target=_serve,
            args=(self._db_path, expected, self._collector_secret, port, mode, child_ready, self._stop),
            daemon=True)
        try:
            self._process.start()
            self._pid = self._process.pid
            child_ready.close()
            if not parent_ready.poll(8.0):
                raise InputError("Local collector did not become ready")
            message = parent_ready.recv()
            if type(message) is not dict or set(message) != {"endpoint"}:
                raise InputError("Local collector startup failed")
            endpoint = validate_endpoint(message["endpoint"])
            if "endpoint" in expected and endpoint != expected["endpoint"]:
                raise InputError("Restarted collector endpoint differs")
            self._endpoint = endpoint
            self._mode = mode
            self.cleanup_result = {"child_stopped": False, "forced_termination": False}
            return self
        except BaseException:
            self.stop()
            raise
        finally:
            parent_ready.close()
            child_ready.close()

    def __enter__(self):
        return self._start(self._mode)

    def stop(self):
        if self._process is None:
            return
        forced = False
        if self._stop is not None:
            self._stop.set()
        if self._process.pid is not None:
            self._process.join(3.0)
            if self._process.is_alive():
                forced = True
                self._process.terminate()
                self._process.join(3.0)
            if self._process.is_alive():
                self._process.kill()
                self._process.join(3.0)
        stopped = self._process.pid is None or not self._process.is_alive()
        self.cleanup_result = {"child_stopped": stopped, "forced_termination": forced}
        if not stopped:
            raise RuntimeError("Owned collector child did not stop")
        self._process.close()
        self._process = None

    def restart(self, mode="normal"):
        if self._endpoint is None:
            raise InputError("Collector restart requires a prior successful start")
        self.stop()
        return self._start(mode)

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        return False

    def snapshot(self):
        if self._endpoint is None or not self._db_path.exists():
            raise InputError("Collector persistence is not available")
        with closing(_connect(self._db_path, readonly=True)) as connection:
            connection.execute("BEGIN")
            identity = _identity(connection)
            if identity != {**self._base_identity, "endpoint": self._endpoint}:
                raise InputError("Persisted collector identity changed")
            counters = dict(connection.execute("SELECT name,value FROM stats").fetchall())
            rows = [_row(row, identity) for row in connection.execute(ROW_SELECT + " ORDER BY collection_id")]
            connection.commit()
        return {"collect_calls": counters["collect_calls"], "status_calls": counters["status_calls"],
                "accepted_count": len(rows), "rows": rows}
