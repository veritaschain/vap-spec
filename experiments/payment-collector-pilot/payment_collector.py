"""Separate-process loopback custody pilot; same operator and user identity.

A signed ACK concerns exact retained bytes, not their truth, completeness or
independent observation. Historical ACKs do not establish present retention.
The raw provider/bearer remains outside this wrapper's enforcement boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import http.client
import importlib.util
import json
import re
import secrets
import socket
import sqlite3
import stat
import sys
import time
import unicodedata
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode, urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def _dependency(name: str, directory: str, file: str) -> Any:
    path = Path(__file__).resolve().parents[1] / directory / file
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError("local_payment_dependency_unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


runtime = _dependency("_vso_collector_payment_runtime", "payment-runtime-pilot", "payment_runtime.py")
authorization = _dependency("_vso_collector_payment_authorization", "payment-authorization-pilot", "authorization_gate.py")
DEFAULT_COLLECTOR_ID = "synthetic-payment-collector-v0"
PACKAGE_SCHEMA = "synthetic-payment-collection-package-v0"
ACK_SCHEMA = "synthetic-payment-collection-ack-v0"
READBACK_SCHEMA = "synthetic-payment-collection-readback-v0"
OBSERVATION_SCHEMA = "synthetic-payment-custody-observation-v0"
STORE_SCHEMA = "synthetic-payment-custody-store-v0"
SIGNING_DOMAIN = b"VSO synthetic payment custody v0\x00"
MAX_EVIDENCE_BYTES = 65536
MAX_MESSAGE_BYTES = 524288
KINDS = {"admission_record": "admission", "provider_receipt": "outcome"}
PACKAGE_FIELDS = {"schema", "request_bytes", "request_digest", "context_digest", "kind", "phase",
                  "evidence_bytes", "evidence_digest", "evidence_length"}
BINDING_FIELDS = ("request_digest", "context_digest", "kind", "phase", "evidence_digest", "evidence_length")
Hook = Callable[[str, dict], None]


def _value(value: Any, depth: int = 0) -> None:
    if depth > 20:
        raise ValueError("collector_json_depth")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > runtime.MAX_INTEGER:
            raise ValueError("collector_json_integer")
        return
    if type(value) is str:
        if len(value) > MAX_MESSAGE_BYTES or unicodedata.normalize("NFC", value) != value:
            raise ValueError("collector_json_string")
        value.encode("utf-8", errors="strict")
        return
    if type(value) is list and len(value) <= 256:
        for item in value:
            _value(item, depth + 1)
        return
    if type(value) is dict and len(value) <= 128:
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("collector_json_key")
            _value(key, depth + 1)
            _value(item, depth + 1)
        return
    raise ValueError("collector_json_type_or_size")


def canonical_json(value: Any) -> bytes:
    _value(value)
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                     allow_nan=False).encode("utf-8")
    if len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError("collector_message_size_limit")
    return raw


def load_json(raw: bytes | str) -> Any:
    if type(raw) not in (bytes, str) or len(raw) > MAX_MESSAGE_BYTES:
        raise ValueError("collector_input_size_or_type")
    try:
        value = json.loads(raw, object_pairs_hook=runtime._pairs,
                           parse_float=runtime._no_float, parse_constant=runtime._no_float)
        canonical_json(value)
        return value
    except RecursionError as exc:
        raise ValueError("collector_json_depth") from exc


def bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return bytes_digest(canonical_json(value))


def _hex(value: Any, *, maximum: int = MAX_EVIDENCE_BYTES) -> bytes:
    if (type(value) is not str or not 0 < len(value) <= maximum * 2
            or re.fullmatch(r"(?:[0-9a-f]{2})+", value) is None):
        raise ValueError("collector_hex_shape_or_size")
    return bytes.fromhex(value)


def make_package(request: dict, kind: str, evidence_bytes: bytes) -> bytes:
    raw = runtime.request_bytes(request)
    if kind not in KINDS or type(evidence_bytes) is not bytes or not 0 < len(evidence_bytes) <= MAX_EVIDENCE_BYTES:
        raise ValueError("original_evidence_kind_or_size")
    context = {field: request[field] for field in runtime.CONTEXT_FIELDS}
    packed = canonical_json({"schema": PACKAGE_SCHEMA, "request_bytes": raw.hex(),
        "request_digest": bytes_digest(raw), "context_digest": digest(context), "kind": kind,
        "phase": KINDS[kind], "evidence_bytes": evidence_bytes.hex(),
        "evidence_digest": bytes_digest(evidence_bytes), "evidence_length": len(evidence_bytes)})
    validate_package(packed, context)
    return packed


def validate_package(raw: bytes, context: dict) -> dict:
    package = load_json(raw)
    if (type(package) is not dict or set(package) != PACKAGE_FIELDS or package["schema"] != PACKAGE_SCHEMA
            or canonical_json(package) != raw or type(package["kind"]) is not str or package["kind"] not in KINDS
            or package["phase"] != KINDS[package["kind"]]
            or not runtime._hash(package["request_digest"]) or not runtime._hash(package["context_digest"])
            or not runtime._hash(package["evidence_digest"]) or not runtime._integer(package["evidence_length"])):
        raise ValueError("collection_package_shape")
    request_bytes = _hex(package["request_bytes"])
    request = runtime.load_json(request_bytes)
    if (runtime.request_bytes(request) != request_bytes
            or any(request[field] != context[field] for field in runtime.CONTEXT_FIELDS)
            or package["request_digest"] != bytes_digest(request_bytes)
            or package["context_digest"] != digest(context)):
        raise ValueError("collection_request_context_binding")
    evidence = _hex(package["evidence_bytes"])
    if len(evidence) != package["evidence_length"] or bytes_digest(evidence) != package["evidence_digest"]:
        raise ValueError("collection_original_bytes_binding")
    body = runtime.load_json(evidence)
    if package["kind"] == "admission_record":
        if (type(body) is not dict or body.get("schema") != authorization.PROOF_SCHEMA
                or body.get("request_bytes") != request_bytes.hex()):
            raise ValueError("admission_record_request_binding")
    else:
        payload = body.get("payload") if type(body) is dict else None
        if (type(payload) is not dict or payload.get("schema") != runtime.RECEIPT_SCHEMA
                or payload.get("request_digest") != bytes_digest(request_bytes)
                or runtime.request_bytes(payload.get("request")) != request_bytes):
            raise ValueError("provider_receipt_request_binding")
    # The collector checks package correspondence, not embedded authority truth.
    return package


def _binding(package: dict, raw: bytes) -> dict:
    return {"package_digest": bytes_digest(raw), **{field: package[field] for field in BINDING_FIELDS}}


def sign_statement(payload: dict, private_key: bytes) -> bytes:
    signed = canonical_json(payload)
    signature = Ed25519PrivateKey.from_private_bytes(private_key).sign(SIGNING_DOMAIN + signed)
    return canonical_json({"payload": payload, "signature": signature.hex()})


def _verify_statement(raw: bytes, public_key: bytes) -> dict:
    if type(public_key) is not bytes or len(public_key) != 32:
        raise ValueError("collector_pinned_public_key_shape")
    body = load_json(raw)
    if (type(body) is not dict or set(body) != {"payload", "signature"}
            or canonical_json(body) != raw or type(body["payload"]) is not dict
            or type(body["signature"]) is not str or re.fullmatch(r"[0-9a-f]{128}", body["signature"]) is None):
        raise ValueError("collector_signed_envelope_shape")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            bytes.fromhex(body["signature"]), SIGNING_DOMAIN + canonical_json(body["payload"]))
    except InvalidSignature as exc:
        raise ValueError("collector_signature_invalid") from exc
    return body["payload"]


def verify_ack(ack_bytes: bytes, package_bytes: bytes, public_key: bytes, *,
               collector_id: str = DEFAULT_COLLECTOR_ID, recovery_epoch: int = 1) -> dict:
    package = load_json(package_bytes)
    payload = _verify_statement(ack_bytes, public_key)
    fields = {"schema", "collector_id", "storage_epoch", "recorded_at_ms", "package_digest", *BINDING_FIELDS}
    if (set(payload) != fields or payload["schema"] != ACK_SCHEMA or payload["collector_id"] != collector_id
            or not runtime._integer(payload["storage_epoch"]) or payload["storage_epoch"] > recovery_epoch
            or not runtime._integer(payload["recorded_at_ms"])
            or any(payload[field] != value for field, value in _binding(package, package_bytes).items())):
        raise ValueError("collector_ack_binding_or_epoch")
    return payload


def verify_readback(response_bytes: bytes, package_bytes: bytes, public_key: bytes, *, nonce: str,
                    collector_id: str = DEFAULT_COLLECTOR_ID, recovery_epoch: int = 1,
                    historical: bool = False) -> dict:
    package = load_json(package_bytes)
    response = load_json(response_bytes)
    if type(response) is not dict or set(response) != {"readback_bytes", "ack_bytes", "package_bytes"}:
        raise ValueError("collector_readback_response_shape")
    readback_bytes = _hex(response["readback_bytes"])
    observed = _verify_statement(readback_bytes, public_key)
    fields = {"schema", "collector_id", "recovery_epoch", "nonce", "observed_at_ms", "state",
              "package_digest", "context_digest", "ack_digest"}
    if (set(observed) != fields or observed["schema"] != READBACK_SCHEMA
            or observed["collector_id"] != collector_id or observed["nonce"] != nonce
            or re.fullmatch(r"[0-9a-f]{32}", nonce) is None
            or not runtime._integer(observed["recovery_epoch"])
            or (observed["recovery_epoch"] > recovery_epoch if historical else observed["recovery_epoch"] != recovery_epoch)
            or observed["package_digest"] != bytes_digest(package_bytes)
            or observed["context_digest"] != package["context_digest"]
            or not runtime._integer(observed["observed_at_ms"])):
        raise ValueError("collector_readback_binding_or_fresh_challenge")
    if observed["state"] == "MISSING":
        if response["ack_bytes"] is not None or response["package_bytes"] is not None or observed["ack_digest"] is not None:
            raise ValueError("collector_missing_readback_shape")
        return {"state": "MISSING", "readback_bytes": readback_bytes, "ack_bytes": None,
                "response_bytes": response_bytes, "nonce": nonce}
    if observed["state"] != "PRESENT":
        raise ValueError("collector_readback_state")
    ack = _hex(response["ack_bytes"])
    original = _hex(response["package_bytes"], maximum=MAX_MESSAGE_BYTES)
    if original != package_bytes or observed["ack_digest"] != bytes_digest(ack):
        raise ValueError("collector_readback_original_bytes_mismatch")
    verify_ack(ack, original, public_key, collector_id=collector_id,
               recovery_epoch=observed["recovery_epoch"])
    return {"state": "PRESENT", "readback_bytes": readback_bytes, "ack_bytes": ack,
            "response_bytes": response_bytes, "nonce": nonce}


@dataclass
class CollectorConfig:
    db_path: str | Path
    context: dict
    private_key: bytes
    credential: str
    collector_id: str = DEFAULT_COLLECTOR_ID
    recovery_epoch: int = 1
    sqlite_timeout: float = 0.2
    fault_hook: Hook | None = None
    drop_ack_after_commit: bool = False


def _store_identity(config: CollectorConfig) -> dict:
    return {"schema": STORE_SCHEMA, "context": config.context, "collector_id": config.collector_id,
            "public_key": runtime._public(config.private_key).hex()}


def _initialize(config: CollectorConfig) -> None:
    config.context = runtime.validate_context(config.context)
    runtime._credential(config.credential)
    runtime._public(config.private_key)
    config.sqlite_timeout = runtime._timeout(config.sqlite_timeout)
    if (not runtime._text(config.collector_id) or not runtime._integer(config.recovery_epoch)
            or type(config.drop_ack_after_commit) is not bool
            or config.fault_hook is not None and not callable(config.fault_hook)):
        raise ValueError("collector_configuration_shape")
    Path(config.db_path).parent.mkdir(parents=True, exist_ok=True)
    connection = runtime._connect(config.db_path, config.sqlite_timeout, initialize=True)
    try:
        connection.execute("BEGIN IMMEDIATE")
        identity = _store_identity(config)
        runtime._meta(connection, identity, config.recovery_epoch, digest(identity))
        connection.execute("""CREATE TABLE IF NOT EXISTS collection_records (
            package_digest TEXT PRIMARY KEY, request_digest TEXT NOT NULL, kind TEXT NOT NULL,
            package_bytes BLOB NOT NULL, ack_bytes BLOB NOT NULL,
            UNIQUE(request_digest,kind))""")
        connection.execute("CREATE TABLE IF NOT EXISTS metrics (name TEXT PRIMARY KEY, value INTEGER NOT NULL)")
        for name in ("collect_attempts", "query_attempts"):
            connection.execute("INSERT OR IGNORE INTO metrics VALUES (?,0)", (name,))
        for action in ("UPDATE", "DELETE"):
            connection.execute(f"""CREATE TRIGGER IF NOT EXISTS immutable_collection_{action.lower()}
                BEFORE {action} ON collection_records BEGIN
                SELECT RAISE(ABORT,'original_collection_retained'); END""")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def _count(config: CollectorConfig, name: str) -> None:
    connection = runtime._connect(config.db_path, config.sqlite_timeout)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE metrics SET value=value+1 WHERE name=?", (name,))
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def _collect(config: CollectorConfig, raw: bytes) -> tuple[bytes, bool, dict]:
    package = validate_package(raw, config.context)
    connection = runtime._connect(config.db_path, config.sqlite_timeout)
    try:
        connection.execute("BEGIN IMMEDIATE")
        old = connection.execute("SELECT * FROM collection_records WHERE request_digest=? AND kind=?",
                                 (package["request_digest"], package["kind"])).fetchone()
        if old is not None:
            if bytes(old["package_bytes"]) != raw:
                raise ValueError("original_collection_conflict")
            connection.commit()
            return bytes(old["ack_bytes"]), False, package
        runtime._current_generation(connection, config.recovery_epoch, digest(_store_identity(config)))
        ack = sign_statement({"schema": ACK_SCHEMA, "collector_id": config.collector_id,
            "storage_epoch": config.recovery_epoch, "recorded_at_ms": time.time_ns() // 1000000,
            **_binding(package, raw)}, config.private_key)
        connection.execute("INSERT INTO collection_records VALUES (?,?,?,?,?)", (
            bytes_digest(raw), package["request_digest"], package["kind"], raw, ack))
        connection.commit()
        return ack, True, package
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def _readback(config: CollectorConfig, package_digest: str, nonce: str) -> bytes:
    connection = runtime._readonly(config.db_path)
    try:
        connection.execute("BEGIN")
        # A stale still-running process cannot assert that its old epoch is the
        # current storage epoch after another process advanced the same store.
        runtime._current_generation(connection, config.recovery_epoch, digest(_store_identity(config)))
        row = connection.execute("SELECT * FROM collection_records WHERE package_digest=?", (package_digest,)).fetchone()
        ack = bytes(row["ack_bytes"]) if row is not None else None
        package = bytes(row["package_bytes"]) if row is not None else None
        signed = sign_statement({"schema": READBACK_SCHEMA, "collector_id": config.collector_id,
            "recovery_epoch": config.recovery_epoch, "nonce": nonce,
            "observed_at_ms": time.time_ns() // 1000000, "state": "PRESENT" if row is not None else "MISSING",
            "package_digest": package_digest, "context_digest": digest(config.context),
            "ack_digest": bytes_digest(ack) if ack is not None else None}, config.private_key)
        connection.commit()
        return canonical_json({"readback_bytes": signed.hex(), "ack_bytes": ack.hex() if ack else None,
                               "package_bytes": package.hex() if package else None})
    finally:
        connection.close()


def collector_snapshot(db_path: str | Path) -> dict:
    connection = runtime._readonly(db_path)
    try:
        connection.execute("BEGIN")
        metrics = {row["name"]: row["value"] for row in connection.execute("SELECT * FROM metrics")}
        rows = connection.execute("SELECT package_digest,kind FROM collection_records ORDER BY package_digest").fetchall()
        return {**metrics, "collection_posts": metrics["collect_attempts"], "readback_queries": metrics["query_attempts"],
                "records": len(rows), "kind_counts": {kind: sum(row["kind"] == kind for row in rows) for kind in KINDS},
                "record_digests": [row["package_digest"] for row in rows]}
    finally:
        connection.close()


def serve_collector(config: CollectorConfig, *, ready: Callable[[str], None] | None = None) -> None:
    _initialize(config)

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _authorized(self) -> bool:
            value = self.headers.get("Authorization", "")
            return (value.isascii() and len(self.headers.get_all("Authorization", [])) == 1
                    and hmac.compare_digest(value, "Bearer " + config.credential))

        def _send(self, status: int, raw: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _drop(self) -> None:
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()

        def do_POST(self) -> None:
            if self.path != "/collections":
                self._send(404, canonical_json({"error": "unsupported_path"}))
                return
            try:
                self.connection.settimeout(5)
                _count(config, "collect_attempts")
                if not self._authorized():
                    self._send(401, canonical_json({"error": "ephemeral_credential_required"}))
                    return
                length = self.headers.get("Content-Length", "")
                if (re.fullmatch(r"[0-9]+", length) is None or not 0 < int(length) <= MAX_MESSAGE_BYTES
                        or len(self.headers.get_all("Content-Length", [])) != 1
                        or self.headers.get("Transfer-Encoding") is not None):
                    raise ValueError("collection_body_length")
                raw = self.rfile.read(int(length))
                if len(raw) != int(length):
                    raise ValueError("collection_incomplete_body")
                ack, created, package = _collect(config, raw)
                if created:
                    if config.fault_hook is not None:
                        config.fault_hook("after_commit", {"kind": package["kind"],
                            "request_digest": package["request_digest"], "package_digest": bytes_digest(raw)})
                    if config.drop_ack_after_commit:
                        self._drop()
                        return
                self._send(200, ack)
            except (ValueError, TypeError, UnicodeError) as exc:
                status = 409 if str(exc) == "original_collection_conflict" else 400
                self._send(status, canonical_json({"error": "collection_rejected"}))
            except Exception:
                self._drop()

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            if parsed.path != "/collections" or parsed.fragment:
                self._send(404, canonical_json({"error": "unsupported_path"}))
                return
            try:
                _count(config, "query_attempts")
                if not self._authorized():
                    self._send(401, canonical_json({"error": "ephemeral_credential_required"}))
                    return
                query = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True, max_num_fields=2)
                if (set(query) != {"package_digest", "nonce"} or any(len(items) != 1 for items in query.values())
                        or not runtime._hash(query["package_digest"][0])
                        or re.fullmatch(r"[0-9a-f]{32}", query["nonce"][0]) is None):
                    raise ValueError("collection_query_shape")
                self._send(200, _readback(config, query["package_digest"][0], query["nonce"][0]))
            except (ValueError, TypeError, UnicodeError):
                self._send(400, canonical_json({"error": "readback_rejected"}))
            except (sqlite3.Error, OSError):
                self._drop()

    class Server(ThreadingHTTPServer):
        daemon_threads = True
        allow_reuse_address = False

    server = Server(("127.0.0.1", 0), Handler)
    endpoint = "http://127.0.0.1:" + str(server.server_address[1])
    try:
        if ready is None:
            print(json.dumps({"event": "ready", "endpoint": endpoint}), flush=True)
        else:
            ready(endpoint)
        server.serve_forever(poll_interval=0.1)
    finally:
        server.server_close()


class CollectorClient:
    def __init__(self, endpoint: str, context: dict, public_key: bytes, credential: str, *,
                 collector_id: str = DEFAULT_COLLECTOR_ID, recovery_epoch: int = 1, timeout: float = 2.0) -> None:
        self.host, self.port = runtime._endpoint(endpoint)
        self.context = runtime.validate_context(context)
        if type(public_key) is not bytes or len(public_key) != 32:
            raise ValueError("collector_public_key_shape")
        Ed25519PublicKey.from_public_bytes(public_key)
        if not runtime._text(collector_id) or not runtime._integer(recovery_epoch):
            raise ValueError("collector_identity_epoch_shape")
        self.public_key, self.collector_id, self.recovery_epoch = public_key, collector_id, recovery_epoch
        self.credential, self.timeout = runtime._credential(credential), runtime._timeout(timeout)

    def _http(self, method: str, path: str, body: bytes | None = None) -> tuple[int, bytes]:
        connection = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
        try:
            headers = {"Authorization": "Bearer " + self.credential, "Accept": "application/json"}
            if body is not None:
                headers["Content-Type"] = "application/json"
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read(MAX_MESSAGE_BYTES + 1)
            if len(raw) > MAX_MESSAGE_BYTES:
                raise ValueError("collector_response_size_limit")
            return response.status, raw
        finally:
            connection.close()

    def readback(self, package_bytes: bytes) -> dict:
        validate_package(package_bytes, self.context)
        nonce = secrets.token_hex(16)
        status, raw = self._http("GET", "/collections?" + urlencode({
            "package_digest": bytes_digest(package_bytes), "nonce": nonce}))
        if status != 200:
            raise ValueError("collector_readback_unavailable")
        return verify_readback(raw, package_bytes, self.public_key, nonce=nonce,
            collector_id=self.collector_id, recovery_epoch=self.recovery_epoch)

    def collect_and_check(self, package_bytes: bytes) -> dict:
        validate_package(package_bytes, self.context)
        status, ack = self._http("POST", "/collections", package_bytes)
        if status != 200:
            raise ValueError("collector_ack_unavailable")
        verify_ack(ack, package_bytes, self.public_key, collector_id=self.collector_id,
                   recovery_epoch=self.recovery_epoch)
        observation = self.readback(package_bytes)
        if observation["state"] != "PRESENT" or observation["ack_bytes"] != ack:
            raise ValueError("collector_original_ack_not_read_back")
        return {**observation, "package_bytes": package_bytes}


class CollectedAdapter:
    """Custody prerequisite for only the first wrapper-owned payment attempt."""

    def __init__(self, authorized_adapter: Any, collector_client: CollectorClient, *,
                 fault_hook: Hook | None = None) -> None:
        self._authorized = authorized_adapter
        self._native = authorized_adapter._adapter
        self._collector = collector_client
        if self._native.context != collector_client.context:
            raise ValueError("collector_payment_context_mismatch")
        if fault_hook is not None and not callable(fault_hook):
            raise ValueError("trusted_custody_hook_type")
        self._fault_hook = fault_hook
        self._initialize_local()

    def _identity(self) -> dict:
        return {"collector_id": self._collector.collector_id, "public_key": self._collector.public_key.hex(),
                "context": self._collector.context}

    def _initialize_local(self) -> None:
        connection = runtime._connect(self._native.journal_path, self._native.sqlite_timeout)
        try:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute("CREATE TABLE IF NOT EXISTS custody_metadata (key TEXT PRIMARY KEY,value TEXT NOT NULL)")
            expected = canonical_json(self._identity()).decode()
            old = connection.execute("SELECT value FROM custody_metadata WHERE key='identity'").fetchone()
            if old is None:
                connection.execute("INSERT INTO custody_metadata VALUES ('identity',?)", (expected,))
                connection.execute("INSERT INTO custody_metadata VALUES ('epoch',?)", (str(self._collector.recovery_epoch),))
            else:
                epoch = int(connection.execute("SELECT value FROM custody_metadata WHERE key='epoch'").fetchone()[0])
                if old["value"] != expected or self._collector.recovery_epoch < epoch:
                    raise ValueError("persisted_custody_pin_or_epoch_mismatch")
                connection.execute("UPDATE custody_metadata SET value=? WHERE key='epoch'", (str(self._collector.recovery_epoch),))
            connection.execute("""CREATE TABLE IF NOT EXISTS custody_observations (
                observation_digest TEXT PRIMARY KEY, request_digest TEXT NOT NULL,
                kind TEXT NOT NULL, stage TEXT NOT NULL, record_bytes BLOB NOT NULL,
                FOREIGN KEY(request_digest) REFERENCES dispatches(request_digest))""")
            connection.execute("""CREATE TABLE IF NOT EXISTS custody_prerequisites (
                request_digest TEXT PRIMARY KEY, observation_digest TEXT NOT NULL,
                FOREIGN KEY(request_digest) REFERENCES dispatches(request_digest),
                FOREIGN KEY(observation_digest) REFERENCES custody_observations(observation_digest))""")
            for table in ("custody_observations", "custody_prerequisites"):
                for action in ("UPDATE", "DELETE"):
                    connection.execute(f"""CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action.lower()}
                        BEFORE {action} ON {table} BEGIN SELECT RAISE(ABORT,'custody_history_retained'); END""")
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _originals(self, request: dict) -> dict[str, bytes]:
        packages = {}
        proof = self._authorized.read_authorization(request)
        if proof["status"] == "FOUND":
            packages["admission_record"] = make_package(request, "admission_record", proof["record_bytes"])
        financial = self._native.read_status(request)
        if financial["state"] in runtime.TERMINAL and financial["receipt_bytes"] is not None:
            packages["provider_receipt"] = make_package(request, "provider_receipt", financial["receipt_bytes"])
        return packages

    def _persist(self, request: dict, package_bytes: bytes, observation: dict, stage: str) -> None:
        package = validate_package(package_bytes, self._collector.context)
        if stage not in ("PRE_DISPATCH", "POST_EFFECT", "HISTORICAL_RECOVERY"):
            raise ValueError("custody_stage")
        # Retain the original signed components, without repeating the large
        # unsigned HTTP container. They reconstruct its exact verification input.
        record = canonical_json({"schema": OBSERVATION_SCHEMA, "request_digest": package["request_digest"],
            "kind": package["kind"], "stage": stage, "package_bytes": package_bytes.hex(),
            "ack_bytes": observation["ack_bytes"].hex(), "readback_bytes": observation["readback_bytes"].hex(),
            "nonce": observation["nonce"], "collector_epoch": self._collector.recovery_epoch,
            "collector_identity_digest": digest(self._identity()), "recorded_at_ms": time.time_ns() // 1000000})
        connection = runtime._connect(self._native.journal_path, self._native.sqlite_timeout)
        try:
            connection.execute("BEGIN IMMEDIATE")
            epoch = connection.execute("SELECT value FROM custody_metadata WHERE key='epoch'").fetchone()
            if epoch is None or int(epoch["value"]) != self._collector.recovery_epoch:
                raise ValueError("stale_custody_writer_epoch")
            claim = runtime._find(connection, "dispatches", self._native.scope, request, runtime.request_bytes(request))
            if claim is None or (stage == "PRE_DISPATCH" and claim["state"] != "CLAIMED"):
                raise ValueError("original_claim_not_eligible_for_custody")
            connection.execute("INSERT INTO custody_observations VALUES (?,?,?,?,?)", (
                bytes_digest(record), package["request_digest"], package["kind"], stage, record))
            if stage == "PRE_DISPATCH":
                if package["kind"] != "admission_record":
                    raise ValueError("pre_dispatch_admission_record_required")
                # This marker can only be written by the initial owner's code
                # path. Recovery inserts observations but cannot create it.
                connection.execute("INSERT INTO custody_prerequisites VALUES (?,?)", (
                    package["request_digest"], bytes_digest(record)))
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _collect_and_persist(self, request: dict, package_bytes: bytes, stage: str) -> None:
        package = validate_package(package_bytes, self._collector.context)
        observation = self._collector.collect_and_check(package_bytes)
        details = {"request_digest": package["request_digest"], "kind": package["kind"], "stage": stage}
        if self._fault_hook is not None:
            self._fault_hook("after_verified_collection", details)
        self._persist(request, package_bytes, observation, stage)
        if stage == "PRE_DISPATCH" and self._fault_hook is not None:
            self._fault_hook("after_pre_dispatch_persisted", details)

    @staticmethod
    def _empty_custody() -> dict:
        return {"state": "UNKNOWN", "basis": "historical_local_observations_only",
                "present_retention": "NOT_CHECKED", "pre_dispatch": {"state": "UNKNOWN"},
                "admission_record": {"state": "UNKNOWN"}, "provider_receipt": {"state": "UNKNOWN"},
                "observations": [], "unverifiable_observations": 0}

    def _verified_local(self, row: sqlite3.Row, expected: dict[str, bytes], request_digest: str) -> dict:
        record_bytes = bytes(row["record_bytes"])
        record = load_json(record_bytes)
        fields = {"schema", "request_digest", "kind", "stage", "package_bytes", "ack_bytes", "readback_bytes",
                  "nonce", "collector_epoch", "collector_identity_digest", "recorded_at_ms"}
        if (type(record) is not dict or set(record) != fields or record["schema"] != OBSERVATION_SCHEMA
                or canonical_json(record) != record_bytes or bytes_digest(record_bytes) != row["observation_digest"]
                or record["request_digest"] != request_digest or row["request_digest"] != request_digest
                or record["kind"] != row["kind"] or record["stage"] != row["stage"]
                or record["stage"] not in ("PRE_DISPATCH", "POST_EFFECT", "HISTORICAL_RECOVERY")
                or not runtime._integer(record["collector_epoch"]) or record["collector_epoch"] > self._collector.recovery_epoch
                or record["collector_identity_digest"] != digest(self._identity())
                or not runtime._integer(record["recorded_at_ms"])):
            raise ValueError("local_custody_record_shape_or_pin")
        package_bytes = _hex(record["package_bytes"], maximum=MAX_MESSAGE_BYTES)
        if expected.get(record["kind"]) != package_bytes:
            raise ValueError("local_custody_original_evidence_mismatch")
        response = canonical_json({name: record[name] for name in ("readback_bytes", "ack_bytes", "package_bytes")})
        checked = verify_readback(response, package_bytes, self._collector.public_key, nonce=record["nonce"],
            collector_id=self._collector.collector_id, recovery_epoch=record["collector_epoch"])
        if checked["state"] != "PRESENT":
            raise ValueError("local_custody_present_observation_required")
        return {"observation_digest": row["observation_digest"], "stage": record["stage"], "kind": record["kind"],
                "package_digest": bytes_digest(package_bytes), "package_bytes": package_bytes,
                "ack_bytes": checked["ack_bytes"], "readback_bytes": checked["readback_bytes"],
                "nonce": record["nonce"], "collector_epoch": record["collector_epoch"], "record_bytes": record_bytes}

    def read_custody(self, request: dict) -> dict:
        result = self._empty_custody()
        try:
            snapshot, raw = self._native._prepare(request)
            expected = self._originals(snapshot)
            connection = runtime._readonly(self._native.journal_path)
            try:
                connection.execute("BEGIN")
                marker = connection.execute("SELECT observation_digest FROM custody_prerequisites WHERE request_digest=?",
                                            (bytes_digest(raw),)).fetchone()
                if marker is None:
                    result["pre_dispatch"] = {"state": "NOT_RECORDED"}
                rows = connection.execute("SELECT * FROM custody_observations WHERE request_digest=? ORDER BY rowid DESC LIMIT 128",
                                          (bytes_digest(raw),)).fetchall()
                if marker and all(row["observation_digest"] != marker[0] for row in rows):
                    original = connection.execute("SELECT * FROM custody_observations WHERE observation_digest=?", (marker[0],)).fetchone()
                    if original is not None:
                        rows.append(original)
                if marker:
                    result["pre_dispatch"] = {"state": "UNKNOWN"}
                for row in rows:
                    try:
                        observed = self._verified_local(row, expected, bytes_digest(raw))
                    except (ValueError, TypeError, UnicodeError, KeyError):
                        result["unverifiable_observations"] += 1
                        continue
                    result["observations"].append(observed)
                    kind = observed["kind"]
                    if result[kind]["state"] != "ACKNOWLEDGED":
                        result[kind] = {"state": "ACKNOWLEDGED", "observation_digest": observed["observation_digest"],
                                        "package_digest": observed["package_digest"], "stage": observed["stage"]}
                    if (marker and observed["observation_digest"] == marker[0]
                            and kind == "admission_record" and observed["stage"] == "PRE_DISPATCH"):
                        result["pre_dispatch"] = {"state": "VERIFIED_PREREQUISITE", "observation_digest": marker[0],
                            "proves_payment_post_occurred": False}
                if all(result[kind]["state"] == "ACKNOWLEDGED" for kind in KINDS):
                    result["state"] = "ACKNOWLEDGED"
                return result
            finally:
                connection.close()
        except (sqlite3.Error, OSError, ValueError, TypeError, UnicodeError):
            return result

    def _attach(self, financial: dict, snapshot: dict) -> dict:
        if financial.get("request_digest") != bytes_digest(runtime.request_bytes(snapshot)):
            return {**financial, "custody": self._empty_custody()}
        return {**financial, "custody": self.read_custody(snapshot)}

    def _rejected(self) -> dict:
        # Never re-read a mutable failed input through a different submission
        # path: that could bypass this wrapper's required collection hooks.
        financial = self._native._result("REJECTED", None, "request_schema_or_scope_rejected")
        return {**financial, "mock_admission": self._authorized._unavailable_admission(
            None, "native_request_unusable"), "custody": self._empty_custody()}

    def submit(self, request: dict, evidence: Any = None) -> dict:
        try:
            snapshot, raw = self._native._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            return self._rejected()

        def before(native_request: dict, native_raw: bytes) -> None:
            if native_raw != raw:
                raise ValueError("custody_request_snapshot_mismatch")
            proof = self._authorized.read_authorization(snapshot)
            if proof["status"] != "FOUND" or proof["request_digest"] != bytes_digest(raw):
                raise ValueError("original_authorization_record_unavailable")
            self._collect_and_persist(snapshot, make_package(snapshot, "admission_record", proof["record_bytes"]), "PRE_DISPATCH")

        def after(native_request: dict, native_raw: bytes, receipt: bytes) -> None:
            if native_raw != raw:
                raise ValueError("custody_outcome_snapshot_mismatch")
            runtime.verify_receipt(receipt, raw, self._native.provider_public_key, self._native.provider_id)
            self._collect_and_persist(snapshot, make_package(snapshot, "provider_receipt", receipt), "POST_EFFECT")

        result = self._authorized._submit_prepared(snapshot, raw, evidence,
            before_dispatch=before, after_terminal_receipt=after)
        return self._attach(result, snapshot)

    def read_status(self, request: dict) -> dict:
        try:
            snapshot, _ = self._native._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            return self._rejected()
        return self._attach(self._authorized.read_status(snapshot), snapshot)

    def reconcile(self, request: dict) -> dict:
        """Financial reconciliation only; this never submits collector evidence."""
        try:
            snapshot, _ = self._native._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            return self._rejected()
        return self._attach(self._authorized.reconcile(snapshot), snapshot)

    def recover_evidence(self, request: dict) -> dict:
        """Historical evidence collection only, never financial GET/POST or rearm."""
        try:
            snapshot, _ = self._native._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            return self._rejected()
        failures = []
        for kind, package in self._originals(snapshot).items():
            try:
                self._collect_and_persist(snapshot, package, "HISTORICAL_RECOVERY")
            except Exception:
                failures.append(kind)
        result = self._attach(self._authorized.read_status(snapshot), snapshot)
        return {**result, "evidence_recovery": {"historical_only": True, "unresolved_kinds": failures,
                                                "payment_rearmed": False}}

    def check_custody(self, request: dict) -> dict:
        """Fresh challenged collector GETs; no collection/payment writes."""
        result = {"present_retention": "UNKNOWN", "observations": {}}
        try:
            snapshot, _ = self._native._prepare(request)
            for kind, package in self._originals(snapshot).items():
                try:
                    observed = self._collector.readback(package)
                    result["observations"][kind] = {**observed, "package_bytes": package}
                except Exception:
                    result["observations"][kind] = {"state": "UNKNOWN"}
            if set(result["observations"]) == set(KINDS) and all(
                    item["state"] == "PRESENT" for item in result["observations"].values()):
                result["present_retention"] = "PRESENT_AT_CHALLENGED_READBACKS"
        except (ValueError, TypeError, UnicodeError, sqlite3.Error, OSError):
            pass
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    collector = commands.add_parser("collector")
    collector.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    try:
        if stat.S_IMODE(args.config.stat().st_mode) & 0o077:
            raise ValueError("collector_config_must_be_owner_private")
        config = load_json(args.config.read_bytes())
        required = {"db_path", "context", "private_key_hex", "credential"}
        optional = {"collector_id", "recovery_epoch", "sqlite_timeout", "drop_ack_after_commit"}
        if type(config) is not dict or not required <= set(config) or set(config) - required - optional:
            raise ValueError("collector_config_fields")
        private_hex = config.pop("private_key_hex")
        private = _hex(private_hex, maximum=32)
        if len(private) != 32:
            raise ValueError("collector_private_key_shape")
        serve_collector(CollectorConfig(private_key=private, **config))
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, TypeError, sqlite3.Error):
        parser.error("local collector configuration or store could not be opened")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
