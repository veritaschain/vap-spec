"""A separate, bounded loopback receiver with actual persisted receipt counters.

Trusted fault modes are local harness controls, not HTTP-selectable features.
This synthetic receiver is not a production upload service or policy engine.
"""

import base64
import binascii
import hashlib
import http.client
import multiprocessing
import re
import socket
import sqlite3
import uuid
from contextlib import closing
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .protocol import MAX_PAYLOAD, InputError, canonical, decode_json, digest, sign_control, timestamp, utc_now, verify_control
from .transport import MAX_AUTH_BYTES, MAX_AUTH_HEADER, MAX_HEADER_BYTES, MAX_HEADER_COUNT, checked_headers, content_length

MODES = {"normal", "drop_after_commit", "wrong_receipt", "redirect", "unauthenticated"}
DISPATCH_FIELDS = {"kind", "request_id", "subject_sha256", "payload_sha256", "byte_length", "created_at"}


def _hex(value):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise InputError("Expected a 32-byte lowercase hexadecimal value")


def _text(value):
    if type(value) is not str or not value.strip():
        raise InputError("Expected a nonempty string")


def _decode_header(value):
    if type(value) is not str or not value or len(value) > MAX_AUTH_HEADER:
        raise InputError("Missing or oversized dispatch authorization")
    try:
        encoded = value.encode("ascii")
        raw = base64.b64decode(encoded, validate=True)
    except (UnicodeError, binascii.Error, ValueError) as exc:
        raise InputError("Invalid authorization encoding") from exc
    if len(raw) > MAX_AUTH_BYTES or base64.b64encode(raw) != encoded:
        raise InputError("Noncanonical or oversized authorization encoding")
    envelope = decode_json(raw, max_bytes=MAX_AUTH_BYTES)
    if raw != canonical(envelope):
        raise InputError("Authorization must contain canonical JSON")
    return envelope


def _validate_dispatch(value, payload, gateway_public, gateway_key_id, received_at):
    envelope = _decode_header(value)
    body = verify_control(envelope, gateway_public, gateway_key_id, "dispatch_intent")
    if set(body) != DISPATCH_FIELDS:
        raise InputError("Unexpected dispatch fields")
    _text(body["request_id"])
    _hex(body["subject_sha256"])
    _hex(body["payload_sha256"])
    if type(body["byte_length"]) is not int or not 0 <= body["byte_length"] <= MAX_PAYLOAD:
        raise InputError("Invalid dispatch byte length")
    if type(payload) is not bytes or len(payload) > MAX_PAYLOAD:
        raise InputError("Invalid measured payload")
    if body["byte_length"] != len(payload) or body["payload_sha256"] != hashlib.sha256(payload).hexdigest():
        raise InputError("Measured body does not match dispatch authorization")
    if timestamp(body["created_at"]) > timestamp(received_at):
        raise InputError("Dispatch authorization is dated after receipt")
    return body


def _connect(path):
    connection = sqlite3.connect(str(path), timeout=2.0)
    connection.execute("PRAGMA synchronous=FULL")
    return connection


def _initialize(path):
    with closing(_connect(path)) as connection:
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("CREATE TABLE stats (name TEXT PRIMARY KEY, value INTEGER NOT NULL)")
        connection.execute("INSERT INTO stats VALUES ('handler_calls', 0)")
        connection.execute("CREATE TABLE uploads (request_id TEXT PRIMARY KEY, subject_sha256 TEXT NOT NULL, payload_sha256 TEXT NOT NULL, byte_length INTEGER NOT NULL, receipt TEXT NOT NULL)")
        connection.commit()


def _count_handler(path):
    with closing(_connect(path)) as connection:
        connection.execute("UPDATE stats SET value=value+1 WHERE name='handler_calls'")
        connection.commit()


def _accept(path, dispatch, payload, received_at, receiver_secret, receiver_key_id):
    """Commit one measured row, or return the identical prior receipt."""
    measured_digest, measured_length = hashlib.sha256(payload).hexdigest(), len(payload)
    with closing(_connect(path)) as connection:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute("SELECT subject_sha256,payload_sha256,byte_length,receipt FROM uploads WHERE request_id=?", (dispatch["request_id"],)).fetchone()
        if row is not None:
            if row[:3] != (dispatch["subject_sha256"], measured_digest, measured_length):
                connection.rollback()
                raise InputError("REQUEST_ID_CONFLICT")
            receipt = decode_json(row[3])
            connection.commit()
            return receipt
        body = {
            "kind": "upload_receipt", "request_id": dispatch["request_id"],
            "subject_sha256": dispatch["subject_sha256"], "payload_sha256": measured_digest,
            "byte_length": measured_length, "received_at": received_at,
            "receipt_id": "receipt-" + uuid.uuid4().hex,
        }
        receipt = sign_control(body, receiver_secret, receiver_key_id)
        connection.execute("INSERT INTO uploads VALUES (?,?,?,?,?)", (body["request_id"], body["subject_sha256"],
                           measured_digest, measured_length, canonical(receipt).decode("utf-8")))
        connection.commit()
        return receipt


class _ReceiverServer(HTTPServer):
    allow_reuse_address = False

    def handle_error(self, request, client_address):
        # Do not log request bodies or authorization headers through a traceback.
        # Parent-side results/counters remain the evidence of this local run.
        pass


class _BoundedHeaderReader:
    """Enforce the total header budget while the standard parser is reading."""
    def __init__(self, reader):
        self.reader, self.remaining, self.lines = reader, MAX_HEADER_BYTES, 0

    def readline(self, size=-1):
        budget = self.remaining + 1
        line = self.reader.readline(budget if size < 0 else min(size, budget))
        self.remaining -= len(line)
        if self.remaining < 0:
            raise http.client.LineTooLong("header block")
        if line not in {b"\r\n", b"\n", b""}:
            self.lines += 1
            if self.lines > MAX_HEADER_COUNT:
                raise http.client.HTTPException("Too many header lines")
        return line


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

    def handle_expect_100(self):
        _count_handler(self.server.db_path)
        self._reply(417, {"error": "EXPECT_CONTINUE_UNSUPPORTED"})
        return False

    def _reply(self, status, value, *, location=None):
        raw = canonical(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Connection", "close")
        if location is not None:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(raw)
        self.wfile.flush()
        self.close_connection = True

    def _unsupported(self):
        _count_handler(self.server.db_path)
        self._reply(405, {"error": "POST_REQUIRED"})

    do_GET = _unsupported
    do_PUT = _unsupported
    do_DELETE = _unsupported
    do_PATCH = _unsupported
    do_HEAD = _unsupported
    do_OPTIONS = _unsupported

    def do_POST(self):
        self.close_connection = True
        _count_handler(self.server.db_path)
        try:
            if self.path != "/upload":
                self._reply(404, {"error": "FIXED_PATH_REQUIRED"})
                return
            headers = checked_headers(list(self.headers.items()))
            length = content_length(headers, MAX_PAYLOAD)
            if headers.get("content-type") != "application/octet-stream":
                raise InputError("Raw octet-stream body required")
            if "expect" in headers:
                raise InputError("Expect/continue is not supported")
            payload = self.rfile.read(length)
            if len(payload) != length:
                raise InputError("Incomplete request body")
            received_at = utc_now()
            if self.server.mode == "unauthenticated":
                # Explicit negative control: no claim of gateway authorization.
                request_id = "unauthenticated-" + uuid.uuid4().hex
                dispatch = {"request_id": request_id,
                            "subject_sha256": digest({"negative_control": "unauthenticated", "request_id": request_id})}
            else:
                dispatch = _validate_dispatch(headers.get("x-pilot-authorization"), payload,
                                              self.server.gateway_public, self.server.gateway_key_id, received_at)
            if self.server.mode == "redirect":
                self._reply(307, {"error": "TRUSTED_REDIRECT_CONTROL"}, location="/not-upload")
                return
            receipt = _accept(self.server.db_path, dispatch, payload, received_at,
                              self.server.receiver_secret, self.server.receiver_key_id)
            if self.server.mode == "drop_after_commit":
                try:
                    self.connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
                self.connection.close()
                return
            if self.server.mode == "wrong_receipt":
                body = dict(receipt["body"])
                body["payload_sha256"] = "0" * 64 if body["payload_sha256"] != "0" * 64 else "1" * 64
                receipt = sign_control(body, self.server.receiver_secret, self.server.receiver_key_id)
            self._reply(200, receipt)
        except InputError as exc:
            status = 409 if str(exc) == "REQUEST_ID_CONFLICT" else 400
            self._reply(status, {"error": "REQUEST_ID_CONFLICT" if status == 409 else "INVALID_REQUEST"})
        except (OSError, ValueError, sqlite3.Error):
            # A response failure after commit remains a committed receiver row.
            # The transport reports uncertainty and never retries automatically.
            self.close_connection = True


def _serve(db_path, gateway_public, gateway_key_id, receiver_secret, receiver_key_id, mode, ready, stop):
    server = None
    try:
        _initialize(db_path)
        server = _ReceiverServer(("127.0.0.1", 0), _Handler)
        server.db_path = db_path
        server.gateway_public, server.gateway_key_id = gateway_public, gateway_key_id
        server.receiver_secret, server.receiver_key_id = receiver_secret, receiver_key_id
        server.mode = mode
        server.timeout = 0.1
        ready.send({"port": server.server_address[1]})
        ready.close()
        while not stop.is_set():
            server.handle_request()
    except BaseException as exc:
        try:
            ready.send({"error": type(exc).__name__})
            ready.close()
        except (OSError, EOFError):
            pass
    finally:
        if server is not None:
            server.server_close()


class ReceiverProcess:
    def __init__(self, directory, *, gateway_public, gateway_key_id, receiver_secret, receiver_key_id, mode="normal"):
        if mode not in MODES:
            raise InputError("Unsupported trusted receiver mode")
        _hex(gateway_public)
        _hex(receiver_secret)
        _text(gateway_key_id)
        _text(receiver_key_id)
        self.directory = Path(directory).absolute()
        self._db_path = self.directory / "receiver.sqlite3"
        self._arguments = (gateway_public, gateway_key_id, receiver_secret, receiver_key_id, mode)
        self._process, self._stop, self._endpoint = None, None, None
        self.cleanup_result = {"child_stopped": True, "forced_termination": False}

    @property
    def endpoint(self):
        if self._endpoint is None:
            raise InputError("Receiver has not started")
        return self._endpoint

    @property
    def pid(self):
        return None if self._process is None else self._process.pid

    def __enter__(self):
        if self._process is not None or self.directory.exists():
            raise InputError("Receiver requires a fresh, nonexistent output directory")
        self.directory.mkdir(parents=True, exist_ok=False)
        context = multiprocessing.get_context("spawn")
        parent_ready, child_ready = context.Pipe(duplex=False)
        self._stop = context.Event()
        self._process = context.Process(target=_serve, args=(self._db_path, *self._arguments, child_ready, self._stop), daemon=True)
        try:
            self._process.start()
            child_ready.close()
            if not parent_ready.poll(8.0):
                raise InputError("Local receiver did not become ready")
            message = parent_ready.recv()
            if "error" in message:
                raise InputError("Local receiver startup failed: " + message["error"])
            self._endpoint = "http://127.0.0.1:" + str(message["port"]) + "/upload"
            self.cleanup_result = {"child_stopped": False, "forced_termination": False}
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise
        finally:
            parent_ready.close()
            child_ready.close()

    def __exit__(self, exc_type, exc_value, traceback):
        forced = False
        if self._stop is not None:
            self._stop.set()
        if self._process is not None and self._process.pid is not None:
            self._process.join(3.0)
            if self._process.is_alive():
                forced = True
                self._process.terminate()
                self._process.join(3.0)
            if self._process.is_alive():
                self._process.kill()
                self._process.join(3.0)
        stopped = self._process is None or self._process.pid is None or not self._process.is_alive()
        self.cleanup_result = {"child_stopped": stopped, "forced_termination": forced}
        if not stopped:
            raise RuntimeError("Owned receiver child did not stop")
        return False

    def snapshot(self):
        if not self._db_path.is_file():
            raise InputError("Receiver persistence is not available")
        with closing(sqlite3.connect(self._db_path.as_uri() + "?mode=ro", uri=True, timeout=2.0)) as connection:
            calls = connection.execute("SELECT value FROM stats WHERE name='handler_calls'").fetchone()
            rows = connection.execute("SELECT request_id,subject_sha256,payload_sha256,byte_length,receipt FROM uploads ORDER BY request_id").fetchall()
        return {
            "handler_calls": calls[0], "accepted_count": len(rows),
            "rows": [{"request_id": r[0], "subject_sha256": r[1], "payload_sha256": r[2],
                      "byte_length": r[3], "receipt": decode_json(r[4])} for r in rows],
        }
