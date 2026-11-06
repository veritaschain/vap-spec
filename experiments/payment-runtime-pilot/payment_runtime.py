"""Local synthetic payment runtime pilot, after caller business authorization.

No real payment API, funds, account, business authorization check or production
gate is implemented. The provider is a separate loopback HTTP process. SQLite
stores this pilot's effects and dispatch claims; replacing/rolling back a store
is outside the guarantee. A result never authorizes an automatic write retry.
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import http.client
import json
import math
import re
import socket
import sqlite3
import stat
import time
import unicodedata
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Callable
from urllib.parse import parse_qs, urlencode, urlsplit

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


REQUEST_SCHEMA = "synthetic-loopback-payment-request-v0"
RECEIPT_SCHEMA = "synthetic-loopback-payment-receipt-v0"
JOURNAL_SCHEMA = "synthetic-payment-dispatch-journal-v0"
PROVIDER_SCHEMA = "synthetic-loopback-payment-store-v0"
SIGNING_DOMAIN = b"VSO local payment runtime receipt v0\x00"
DEFAULT_PROVIDER_ID = "synthetic-loopback-provider-v0"
MAX_BODY = 65536
MAX_INTEGER = 9007199254740991
SCOPE_FIELDS = ("tenant", "environment", "api_audience", "idempotency_domain")
CONTEXT_FIELDS = {*SCOPE_FIELDS, "currency", "minor_unit_scale"}
REQUEST_FIELDS = {"schema", *CONTEXT_FIELDS, "operation_id", "idempotency_key",
                  "configuration_digest", "recovery_epoch", "source_account",
                  "beneficiary", "amount_minor"}
TERMINAL = {"SETTLED", "FAILED"}
Hook = Callable[[str, dict], None]


def _json_value(value: Any, depth: int = 0) -> None:
    if depth > 16:
        raise ValueError("json_nesting_limit")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_INTEGER:
            raise ValueError("json_integer_limit")
        return
    if type(value) is str:
        if len(value) > MAX_BODY or unicodedata.normalize("NFC", value) != value:
            raise ValueError("json_string_limit_or_normalization")
        value.encode("utf-8", errors="strict")
        return
    if type(value) is list and len(value) <= 128:
        for child in value:
            _json_value(child, depth + 1)
        return
    if type(value) is dict and len(value) <= 128:
        for key, child in value.items():
            if type(key) is not str:
                raise ValueError("json_key_type")
            _json_value(key, depth + 1)
            _json_value(child, depth + 1)
        return
    raise ValueError("json_value_type_or_size")


def canonical_json(value: Any) -> bytes:
    """Bounded JSON subset, not an RFC 8785 implementation."""
    _json_value(value)
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                     allow_nan=False).encode("utf-8")
    if len(raw) > MAX_BODY:
        raise ValueError("json_document_limit")
    return raw


def _pairs(items: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _no_float(_: str) -> None:
    raise ValueError("noninteger_json_number")


def load_json(raw: str | bytes) -> Any:
    if type(raw) not in (str, bytes) or len(raw) > MAX_BODY:
        raise ValueError("json_input_size_or_type")
    try:
        value = json.loads(raw, object_pairs_hook=_pairs,
                           parse_float=_no_float, parse_constant=_no_float)
        canonical_json(value)
        return value
    except RecursionError as exc:
        raise ValueError("json_nesting_limit") from exc


def bytes_digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def digest(value: Any) -> str:
    return bytes_digest(canonical_json(value))


def _text(value: Any) -> bool:
    return (type(value) is str and 0 < len(value) <= 128
            and all(ord(character) >= 32 for character in value))


def _decimal(value: Any) -> bool:
    return (type(value) is str and len(value) <= 78
            and re.fullmatch(r"0|[1-9][0-9]*", value) is not None)


def _integer(value: Any) -> bool:
    return type(value) is int and 0 <= value <= MAX_INTEGER


def _hash(value: Any) -> bool:
    return type(value) is str and re.fullmatch(r"sha256:[0-9a-f]{64}", value) is not None


def validate_context(context: Any) -> dict:
    snapshot = load_json(canonical_json(context))
    if (type(snapshot) is not dict or set(snapshot) != CONTEXT_FIELDS
            or not all(_text(snapshot[key]) for key in SCOPE_FIELDS)
            or type(snapshot["currency"]) is not str
            or re.fullmatch(r"[A-Z]{3}", snapshot["currency"]) is None
            or type(snapshot["minor_unit_scale"]) is not int
            or not 0 <= snapshot["minor_unit_scale"] <= 9):
        raise ValueError("context_shape")
    return snapshot


def request_bytes(request: Any) -> bytes:
    raw = canonical_json(request)
    item = load_json(raw)
    if type(item) is not dict or set(item) != REQUEST_FIELDS or item["schema"] != REQUEST_SCHEMA:
        raise ValueError("request_schema")
    validate_context({name: item[name] for name in CONTEXT_FIELDS})
    if (not all(_text(item[name]) for name in ("operation_id", "idempotency_key", "source_account", "beneficiary"))
            or item["source_account"] == item["beneficiary"]
            or not _hash(item["configuration_digest"]) or not _integer(item["recovery_epoch"])
            or not _decimal(item["amount_minor"]) or int(item["amount_minor"]) == 0):
        raise ValueError("request_fields")
    return raw


def make_request(context: dict, *, operation_id: str, idempotency_key: str,
                 configuration_digest: str, recovery_epoch: int, source_account: str,
                 beneficiary: str, amount_minor: str) -> dict:
    result = {"schema": REQUEST_SCHEMA, **validate_context(context), "operation_id": operation_id,
              "idempotency_key": idempotency_key, "configuration_digest": configuration_digest,
              "recovery_epoch": recovery_epoch, "source_account": source_account,
              "beneficiary": beneficiary, "amount_minor": amount_minor}
    request_bytes(result)
    return result


def _scope(context: dict) -> str:
    return digest({field: context[field] for field in SCOPE_FIELDS})


def _check_scope(request: dict, context: dict) -> None:
    if any(request[field] != context[field] for field in SCOPE_FIELDS):
        raise ValueError("request_scope_mismatch")


def _check_generation(request: dict, context: dict, epoch: int, configuration: str) -> None:
    if (request["currency"] != context["currency"]
            or request["minor_unit_scale"] != context["minor_unit_scale"]
            or request["recovery_epoch"] != epoch
            or request["configuration_digest"] != configuration):
        raise ValueError("request_currency_unit_or_generation_mismatch")


def _credential(value: Any) -> str:
    if (type(value) is not str or not 24 <= len(value) <= 256
            or re.fullmatch(r"[A-Za-z0-9_-]+", value) is None):
        raise ValueError("ephemeral_credential_shape")
    return value


def _timeout(value: Any) -> float:
    if type(value) not in (int, float) or not math.isfinite(value) or not 0 < value <= 30:
        raise ValueError("timeout_range")
    return float(value)


def _generation(epoch: Any, configuration: Any) -> None:
    if not _integer(epoch) or not _hash(configuration):
        raise ValueError("generation_shape")


def _public(private: bytes) -> bytes:
    if type(private) is not bytes or len(private) != 32:
        raise ValueError("provider_private_key_shape")
    return Ed25519PrivateKey.from_private_bytes(private).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def _endpoint(endpoint: str) -> tuple[str, int]:
    """Literal loopback only, no DNS, proxies, credentials, redirects or path."""
    if type(endpoint) is not str or re.fullmatch(r"http://127\.0\.0\.1:[1-9][0-9]{0,4}", endpoint) is None:
        raise ValueError("literal_loopback_endpoint_required")
    port = int(endpoint.rsplit(":", 1)[1])
    if not 1 <= port <= 65535:
        raise ValueError("loopback_port_range")
    return "127.0.0.1", port


def _connect(path: str | Path, timeout: float, *, initialize: bool = False) -> sqlite3.Connection:
    connection = sqlite3.connect(str(path), timeout=timeout, isolation_level=None)
    try:
        connection.row_factory = sqlite3.Row
        mode = connection.execute("PRAGMA journal_mode=WAL" if initialize else "PRAGMA journal_mode").fetchone()[0]
        if str(mode).lower() != "wal":
            raise ValueError("wal_journal_required")
        connection.execute("PRAGMA synchronous=FULL")
        if connection.execute("PRAGMA synchronous").fetchone()[0] != 2:
            raise ValueError("full_synchronous_required")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection
    except BaseException:
        connection.close()
        raise


def _readonly(path: str | Path) -> sqlite3.Connection:
    # URI encoding is performed by Path.as_uri; mode=ro prevents creating a new
    # empty store while looking at a missing original journal/provider file.
    uri = Path(path).resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(uri, uri=True, isolation_level=None)
    connection.row_factory = sqlite3.Row
    return connection


def _meta(connection: sqlite3.Connection, expected: dict, epoch: int, configuration: str) -> None:
    connection.execute("CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    row = connection.execute("SELECT value FROM metadata WHERE key='identity'").fetchone()
    encoded = canonical_json(expected).decode("utf-8")
    if row is None:
        connection.execute("INSERT INTO metadata VALUES ('identity', ?)", (encoded,))
        connection.execute("INSERT INTO metadata VALUES ('generation', ?)",
                           (canonical_json({"recovery_epoch": epoch, "configuration_digest": configuration}).decode(),))
        return
    if row["value"] != encoded:
        raise ValueError("persisted_store_identity_mismatch")
    generation = connection.execute("SELECT value FROM metadata WHERE key='generation'").fetchone()
    if generation is None:
        raise ValueError("persisted_generation_missing")
    previous = load_json(generation["value"])
    if (epoch < previous["recovery_epoch"] or
            epoch == previous["recovery_epoch"] and configuration != previous["configuration_digest"]):
        raise ValueError("persisted_generation_rollback_or_redefinition")
    if epoch > previous["recovery_epoch"]:
        connection.execute("UPDATE metadata SET value=? WHERE key='generation'",
                           (canonical_json({"recovery_epoch": epoch, "configuration_digest": configuration}).decode(),))


def _current_generation(connection: sqlite3.Connection, epoch: int, configuration: str) -> None:
    # This fences new local claims/effects in their transaction. It does not
    # atomically revoke an already claimed in-flight request across services.
    row = connection.execute("SELECT value FROM metadata WHERE key='generation'").fetchone()
    current = load_json(row["value"]) if row else None
    if current != {"recovery_epoch": epoch, "configuration_digest": configuration}:
        raise ValueError("stale_runtime_generation")


def _find(connection: sqlite3.Connection, table: str, scope: str, request: dict,
          raw: bytes) -> sqlite3.Row | None:
    if table not in ("payments", "dispatches"):
        raise ValueError("internal_table_name")
    rows = connection.execute(
        f"SELECT * FROM {table} WHERE scope=? AND (operation_id=? OR idempotency_key=?)",
        (scope, request["operation_id"], request["idempotency_key"])).fetchall()
    if not rows:
        return None
    if (len(rows) != 1 or rows[0]["operation_id"] != request["operation_id"]
            or rows[0]["idempotency_key"] != request["idempotency_key"]
            or bytes(rows[0]["request_bytes"]) != raw):
        raise ValueError("immutable_request_identity_conflict")
    return rows[0]


@dataclass
class ProviderConfig:
    db_path: str | Path
    context: dict
    private_key: bytes
    credential: str
    configuration_digest: str
    recovery_epoch: int
    initial_balances: dict[str, str]
    provider_id: str = DEFAULT_PROVIDER_ID
    sqlite_timeout: float = 0.2
    fault_hook: Hook | None = None
    drop_after_commit: bool = False


def _signed_receipt(config: ProviderConfig, request: dict, raw: bytes,
                    status: str, failure_reason: str | None) -> bytes:
    # Called in the actual payment transaction after the local effect decision.
    # It is stored in that transaction and only exposed after COMMIT succeeds.
    request_digest = bytes_digest(raw)
    payload = {"schema": RECEIPT_SCHEMA, "provider_id": config.provider_id,
               "request_digest": request_digest, "request": request,
               "status": status, "failure_reason": failure_reason,
               "effect_id": request_digest if status == "settled" else None,
               "recorded_at_ms": time.time_ns() // 1000000}
    signature = Ed25519PrivateKey.from_private_bytes(config.private_key).sign(
        SIGNING_DOMAIN + canonical_json(payload))
    return canonical_json({"payload": payload, "signature": signature.hex()})


def verify_receipt(raw_receipt: bytes, raw_request: bytes, provider_public_key: bytes,
                   provider_id: str = DEFAULT_PROVIDER_ID) -> dict:
    """Verify exact original native receipt bytes against one immutable request."""
    if type(provider_public_key) is not bytes or len(provider_public_key) != 32:
        raise ValueError("provider_public_key_shape")
    envelope = load_json(raw_receipt)
    if (type(envelope) is not dict or set(envelope) != {"payload", "signature"}
            or canonical_json(envelope) != raw_receipt
            or type(envelope["signature"]) is not str
            or re.fullmatch(r"[0-9a-f]{128}", envelope["signature"]) is None):
        raise ValueError("native_receipt_envelope")
    payload = envelope["payload"]
    if (type(payload) is not dict or set(payload) != {"schema", "provider_id", "request_digest", "request",
            "status", "failure_reason", "effect_id", "recorded_at_ms"}
            or payload["schema"] != RECEIPT_SCHEMA or payload["provider_id"] != provider_id
            or not _integer(payload["recorded_at_ms"])):
        raise ValueError("native_receipt_payload")
    try:
        Ed25519PublicKey.from_public_bytes(provider_public_key).verify(
            bytes.fromhex(envelope["signature"]), SIGNING_DOMAIN + canonical_json(payload))
    except InvalidSignature as exc:
        raise ValueError("native_receipt_signature") from exc
    if (payload["request_digest"] != bytes_digest(raw_request)
            or request_bytes(payload["request"]) != raw_request):
        raise ValueError("native_receipt_request_mismatch")
    if payload["status"] == "settled":
        if payload["effect_id"] != payload["request_digest"] or payload["failure_reason"] is not None:
            raise ValueError("native_receipt_settlement_shape")
    elif payload["status"] == "failed":
        if payload["effect_id"] is not None or payload["failure_reason"] not in (
                "insufficient_funds", "unknown_account", "balance_limit"):
            raise ValueError("native_receipt_failure_shape")
    else:
        raise ValueError("native_receipt_nonterminal_status")
    return payload


def _initialize_provider(config: ProviderConfig) -> None:
    config.context = validate_context(config.context)
    _generation(config.recovery_epoch, config.configuration_digest)
    _credential(config.credential)
    config.sqlite_timeout = _timeout(config.sqlite_timeout)
    public = _public(config.private_key)
    if (not _text(config.provider_id) or type(config.drop_after_commit) is not bool
            or config.fault_hook is not None and not callable(config.fault_hook)):
        raise ValueError("provider_configuration_shape")
    balances = load_json(canonical_json(config.initial_balances))
    if (type(balances) is not dict or not balances
            or not all(_text(account) and _decimal(amount) for account, amount in balances.items())):
        raise ValueError("initial_balances_shape")
    config.initial_balances = balances
    path = Path(config.db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = _connect(path, config.sqlite_timeout, initialize=True)
    try:
        connection.execute("BEGIN IMMEDIATE")
        _meta(connection, {"schema": PROVIDER_SCHEMA, "context": config.context,
              "provider_id": config.provider_id, "provider_public_key": public.hex(),
              "initial_balances": balances}, config.recovery_epoch, config.configuration_digest)
        connection.execute("CREATE TABLE IF NOT EXISTS balances (account TEXT PRIMARY KEY, amount_minor TEXT NOT NULL)")
        connection.execute("""CREATE TABLE IF NOT EXISTS payments (
            request_digest TEXT PRIMARY KEY, scope TEXT NOT NULL,
            operation_id TEXT NOT NULL, idempotency_key TEXT NOT NULL,
            request_bytes BLOB NOT NULL, status TEXT NOT NULL CHECK(status IN ('settled','failed')),
            receipt_bytes BLOB NOT NULL,
            UNIQUE(scope, operation_id), UNIQUE(scope, idempotency_key))""")
        connection.execute("""CREATE TABLE IF NOT EXISTS effects (
            request_digest TEXT PRIMARY KEY, source_account TEXT NOT NULL,
            beneficiary TEXT NOT NULL, amount_minor TEXT NOT NULL,
            FOREIGN KEY(request_digest) REFERENCES payments(request_digest)
              DEFERRABLE INITIALLY DEFERRED)""")
        connection.execute("CREATE TABLE IF NOT EXISTS metrics (name TEXT PRIMARY KEY, value INTEGER NOT NULL)")
        for name in ("post_attempts", "lookup_attempts"):
            connection.execute("INSERT OR IGNORE INTO metrics VALUES (?, 0)", (name,))
        # Existing balances are never re-seeded after a provider restart.
        for account, amount in balances.items():
            connection.execute("INSERT OR IGNORE INTO balances VALUES (?, ?)", (account, amount))
        for table in ("payments", "effects"):
            for action in ("UPDATE", "DELETE"):
                connection.execute(f"""CREATE TRIGGER IF NOT EXISTS immutable_{table}_{action.lower()}
                    BEFORE {action} ON {table} BEGIN
                    SELECT RAISE(ABORT, 'immutable_payment_record'); END""")
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def _metric(config: ProviderConfig, name: str) -> None:
    connection = _connect(config.db_path, config.sqlite_timeout)
    try:
        connection.execute("BEGIN IMMEDIATE")
        connection.execute("UPDATE metrics SET value=value+1 WHERE name=?", (name,))
        connection.commit()
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def _apply_payment(config: ProviderConfig, request: dict, raw: bytes) -> tuple[bytes, bool]:
    connection = _connect(config.db_path, config.sqlite_timeout)
    try:
        connection.execute("BEGIN IMMEDIATE")
        existing = _find(connection, "payments", _scope(config.context), request, raw)
        if existing is not None:
            connection.commit()
            return bytes(existing["receipt_bytes"]), False
        _current_generation(connection, config.recovery_epoch, config.configuration_digest)
        _check_generation(request, config.context, config.recovery_epoch, config.configuration_digest)
        balances = {row["account"]: int(row["amount_minor"]) for row in connection.execute(
            "SELECT account,amount_minor FROM balances WHERE account IN (?,?)",
            (request["source_account"], request["beneficiary"]))}
        amount = int(request["amount_minor"])
        failure = None
        if len(balances) != 2:
            failure = "unknown_account"
        elif balances[request["source_account"]] < amount:
            failure = "insufficient_funds"
        elif len(str(balances[request["beneficiary"]] + amount)) > 78:
            failure = "balance_limit"
        status = "failed" if failure else "settled"
        request_digest = bytes_digest(raw)
        if failure is None:
            connection.execute("UPDATE balances SET amount_minor=? WHERE account=?",
                               (str(balances[request["source_account"]] - amount), request["source_account"]))
            connection.execute("UPDATE balances SET amount_minor=? WHERE account=?",
                               (str(balances[request["beneficiary"]] + amount), request["beneficiary"]))
            connection.execute("INSERT INTO effects VALUES (?,?,?,?)",
                               (request_digest, request["source_account"], request["beneficiary"], request["amount_minor"]))
        receipt = _signed_receipt(config, request, raw, status, failure)
        connection.execute("INSERT INTO payments VALUES (?,?,?,?,?,?,?)", (
            request_digest, _scope(config.context), request["operation_id"], request["idempotency_key"],
            raw, status, receipt))
        connection.commit()
        return receipt, True
    except BaseException:
        connection.rollback()
        raise
    finally:
        connection.close()


def _lookup_payment(config: ProviderConfig, query: dict[str, list[str]]) -> tuple[int, bytes]:
    required = {"operation_id", "idempotency_key", "request_digest"}
    if (set(query) != required or any(len(values) != 1 for values in query.values())
            or not _text(query["operation_id"][0]) or not _text(query["idempotency_key"][0])
            or not _hash(query["request_digest"][0])):
        return 400, canonical_json({"error": "lookup_query_shape"})
    connection = _readonly(config.db_path)
    try:
        rows = connection.execute(
            "SELECT * FROM payments WHERE scope=? AND (operation_id=? OR idempotency_key=?)",
            (_scope(config.context), query["operation_id"][0], query["idempotency_key"][0])).fetchall()
        if not rows:
            return 404, canonical_json({"error": "not_observed_in_this_store"})
        if (len(rows) != 1 or rows[0]["operation_id"] != query["operation_id"][0]
                or rows[0]["idempotency_key"] != query["idempotency_key"][0]
                or rows[0]["request_digest"] != query["request_digest"][0]):
            return 409, canonical_json({"error": "immutable_request_identity_conflict"})
        return 200, bytes(rows[0]["receipt_bytes"])
    finally:
        connection.close()


def provider_snapshot(db_path: str | Path) -> dict:
    """Harness-only read-only SQL inspection, not independent collection."""
    connection = _readonly(db_path)
    try:
        connection.execute("BEGIN")
        metrics = {row["name"]: row["value"] for row in connection.execute("SELECT name,value FROM metrics")}
        result = {"post_attempts": metrics["post_attempts"], "lookup_attempts": metrics["lookup_attempts"],
                  "payments": connection.execute("SELECT count(*) FROM payments").fetchone()[0],
                  "effects": connection.execute("SELECT count(*) FROM effects").fetchone()[0],
                  "settled_payments": connection.execute("SELECT count(*) FROM payments WHERE status='settled'").fetchone()[0],
                  "failed_payments": connection.execute("SELECT count(*) FROM payments WHERE status='failed'").fetchone()[0],
                  "balances": {row["account"]: row["amount_minor"] for row in connection.execute(
                      "SELECT account,amount_minor FROM balances ORDER BY account")}}
        connection.commit()
        return result
    finally:
        connection.close()


def serve_provider(config: ProviderConfig, *, ready: Callable[[str], None] | None = None) -> None:
    """Block in the real local HTTP provider. Faults belong to its trusted harness."""
    _initialize_provider(config)

    class Handler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, format: str, *args: Any) -> None:
            # No request headers, credentials, paths or request bodies in logs.
            return

        def _respond(self, status: int, raw: bytes) -> None:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _authorized(self) -> bool:
            supplied = self.headers.get("Authorization", "")
            if not supplied.isascii() or len(self.headers.get_all("Authorization", [])) != 1:
                return False
            return hmac.compare_digest(supplied, "Bearer " + config.credential)

        def _drop(self) -> None:
            self.close_connection = True
            try:
                self.connection.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self.connection.close()

        def do_POST(self) -> None:
            if self.path != "/payments":
                self._respond(404, canonical_json({"error": "unsupported_path"}))
                return
            try:
                self.connection.settimeout(5)
                _metric(config, "post_attempts")
                if not self._authorized():
                    self._respond(401, canonical_json({"error": "ephemeral_credential_required"}))
                    return
                length = self.headers.get("Content-Length", "")
                if (re.fullmatch(r"[0-9]+", length) is None or not 0 < int(length) <= MAX_BODY
                        or self.headers.get("Transfer-Encoding") is not None
                        or len(self.headers.get_all("Content-Length", [])) != 1):
                    self._respond(400, canonical_json({"error": "body_length_or_transfer_encoding"}))
                    return
                raw = self.rfile.read(int(length))
                if len(raw) != int(length):
                    self._respond(400, canonical_json({"error": "incomplete_request_body"}))
                    return
                request = load_json(raw)
                if request_bytes(request) != raw:
                    raise ValueError("noncanonical_request_bytes")
                _check_scope(request, config.context)
                receipt, created = _apply_payment(config, request, raw)
                if created:
                    if config.fault_hook is not None:
                        config.fault_hook("after_commit", {"request_digest": bytes_digest(raw)})
                    if config.drop_after_commit:
                        self._drop()
                        return
                self._respond(200, receipt)
            except ValueError as exc:
                status = 409 if str(exc) == "immutable_request_identity_conflict" else 400
                self._respond(status, canonical_json({"error": "identity_conflict" if status == 409 else "request_rejected"}))
            except (sqlite3.Error, OSError, http.client.HTTPException):
                self._drop()
            except Exception:
                # Trusted crash/fault hook failures also retain a committed
                # provider row, without returning an invented success response.
                self._drop()

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            if parsed.path != "/payments" or parsed.fragment:
                self._respond(404, canonical_json({"error": "unsupported_path"}))
                return
            try:
                _metric(config, "lookup_attempts")
                if not self._authorized():
                    self._respond(401, canonical_json({"error": "ephemeral_credential_required"}))
                    return
                query = parse_qs(parsed.query, keep_blank_values=True, strict_parsing=True,
                                 max_num_fields=3)
                status, raw = _lookup_payment(config, query)
                self._respond(status, raw)
            except (ValueError, UnicodeError):
                self._respond(400, canonical_json({"error": "lookup_query_shape"}))
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


class Adapter:
    """One durable dispatch claim, one POST opportunity, read-only reconciliation.

    The caller is responsible for business approval before calling submit. This
    primitive does not invoke the separate retrospective evidence assessor.
    Hooks are trusted harness callbacks; they are never request fields.
    """

    def __init__(self, journal_path: str | Path, endpoint: str, context: dict,
                 provider_public_key: bytes, credential: str, configuration_digest: str,
                 recovery_epoch: int, *, provider_id: str = DEFAULT_PROVIDER_ID,
                 timeout: float = 2.0, sqlite_timeout: float = 0.2,
                 fault_hook: Hook | None = None) -> None:
        self.host, self.port = _endpoint(endpoint)
        self.endpoint = endpoint
        self.context = validate_context(context)
        self.scope = _scope(self.context)
        if type(provider_public_key) is not bytes or len(provider_public_key) != 32:
            raise ValueError("provider_public_key_shape")
        Ed25519PublicKey.from_public_bytes(provider_public_key)
        self.provider_public_key = provider_public_key
        self.credential = _credential(credential)
        _generation(recovery_epoch, configuration_digest)
        if not _text(provider_id) or fault_hook is not None and not callable(fault_hook):
            raise ValueError("adapter_configuration_shape")
        self.provider_id = provider_id
        self.configuration_digest = configuration_digest
        self.recovery_epoch = recovery_epoch
        self.timeout = _timeout(timeout)
        self.sqlite_timeout = _timeout(sqlite_timeout)
        self.fault_hook = fault_hook
        self.journal_path = Path(journal_path)
        self._initialize_journal()

    def _initialize_journal(self) -> None:
        self.journal_path.parent.mkdir(parents=True, exist_ok=True)
        connection = _connect(self.journal_path, self.sqlite_timeout, initialize=True)
        try:
            connection.execute("BEGIN IMMEDIATE")
            _meta(connection, {"schema": JOURNAL_SCHEMA, "context": self.context,
                  "provider_id": self.provider_id, "provider_public_key": self.provider_public_key.hex()},
                  self.recovery_epoch, self.configuration_digest)
            connection.execute("""CREATE TABLE IF NOT EXISTS dispatches (
                request_digest TEXT PRIMARY KEY, scope TEXT NOT NULL,
                operation_id TEXT NOT NULL, idempotency_key TEXT NOT NULL,
                request_bytes BLOB NOT NULL,
                state TEXT NOT NULL CHECK(state IN ('CLAIMED','SETTLED','FAILED')),
                receipt_bytes BLOB,
                claimed_at_ms INTEGER NOT NULL,
                observed_at_ms INTEGER,
                UNIQUE(scope, operation_id), UNIQUE(scope, idempotency_key),
                CHECK((state='CLAIMED' AND receipt_bytes IS NULL AND observed_at_ms IS NULL)
                   OR (state IN ('SETTLED','FAILED') AND receipt_bytes IS NOT NULL AND observed_at_ms IS NOT NULL)))""")
            connection.execute("""CREATE TRIGGER IF NOT EXISTS immutable_dispatch_identity
                BEFORE UPDATE ON dispatches WHEN
                NEW.request_digest != OLD.request_digest OR NEW.scope != OLD.scope OR
                NEW.operation_id != OLD.operation_id OR NEW.idempotency_key != OLD.idempotency_key OR
                NEW.request_bytes != OLD.request_bytes OR NEW.claimed_at_ms != OLD.claimed_at_ms
                BEGIN SELECT RAISE(ABORT, 'immutable_dispatch_identity'); END""")
            connection.execute("""CREATE TRIGGER IF NOT EXISTS monotone_dispatch_terminal
                BEFORE UPDATE ON dispatches WHEN OLD.state IN ('SETTLED','FAILED') AND
                (NEW.state != OLD.state OR NEW.receipt_bytes != OLD.receipt_bytes OR NEW.observed_at_ms != OLD.observed_at_ms)
                BEGIN SELECT RAISE(ABORT, 'immutable_terminal_receipt'); END""")
            connection.execute("""CREATE TRIGGER IF NOT EXISTS retained_dispatch_claim
                BEFORE DELETE ON dispatches BEGIN SELECT RAISE(ABORT, 'dispatch_claim_retained'); END""")
            connection.commit()
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    @staticmethod
    def _result(state: str, request_digest: str | None, reason: str,
                receipt: bytes | None = None, **extra: Any) -> dict:
        return {"state": state, "request_digest": request_digest, "reason": reason,
                "receipt_bytes": receipt, "synthetic": True,
                "business_authorization_verified": False, "automatic_retry": False,
                "production_gate": False, **extra}

    def _prepare(self, request: Any) -> tuple[dict, bytes]:
        raw = request_bytes(request)
        snapshot = load_json(raw)
        _check_scope(snapshot, self.context)
        return snapshot, raw

    def _from_row(self, row: sqlite3.Row) -> dict:
        if row["state"] in TERMINAL and row["receipt_bytes"] is not None:
            receipt = bytes(row["receipt_bytes"])
            try:
                payload = verify_receipt(receipt, bytes(row["request_bytes"]),
                                         self.provider_public_key, self.provider_id)
                if payload["status"].upper() != row["state"]:
                    raise ValueError("stored_state_receipt_mismatch")
                return self._result(row["state"], row["request_digest"], "stored_verified_native_receipt", receipt)
            except (ValueError, TypeError, UnicodeError):
                return self._result("UNKNOWN", row["request_digest"], "stored_receipt_unverifiable_claim_retained")
        return self._result("UNKNOWN", row["request_digest"], "durable_claim_outcome_unresolved")

    def _claim(self, request: dict, raw: bytes) -> tuple[sqlite3.Row, bool]:
        connection = _connect(self.journal_path, self.sqlite_timeout)
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = _find(connection, "dispatches", self.scope, request, raw)
            if existing is not None:
                connection.commit()
                return existing, False
            _current_generation(connection, self.recovery_epoch, self.configuration_digest)
            _check_generation(request, self.context, self.recovery_epoch, self.configuration_digest)
            connection.execute("""INSERT INTO dispatches
                (request_digest,scope,operation_id,idempotency_key,request_bytes,state,receipt_bytes,claimed_at_ms,observed_at_ms)
                VALUES (?,?,?,?,?,'CLAIMED',NULL,?,NULL)""", (
                bytes_digest(raw), self.scope, request["operation_id"], request["idempotency_key"],
                raw, time.time_ns() // 1000000))
            row = connection.execute("SELECT * FROM dispatches WHERE request_digest=?", (bytes_digest(raw),)).fetchone()
            connection.commit()
            return row, True
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _read(self, request: dict, raw: bytes) -> sqlite3.Row | None:
        connection = _readonly(self.journal_path)
        try:
            return _find(connection, "dispatches", self.scope, request, raw)
        finally:
            connection.close()

    def _http(self, method: str, path: str, body: bytes | None = None) -> tuple[int, bytes]:
        # http.client neither consults proxy environment variables nor follows
        # redirects. Host/port passed here came from the literal-loopback check.
        connection = http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)
        try:
            headers = {"Authorization": "Bearer " + self.credential, "Accept": "application/json"}
            if body is not None:
                headers["Content-Type"] = "application/json"
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read(MAX_BODY + 1)
            if len(raw) > MAX_BODY:
                raise ValueError("provider_response_size_limit")
            return response.status, raw
        finally:
            connection.close()

    def _store_receipt(self, request: dict, raw: bytes, receipt: bytes) -> sqlite3.Row:
        payload = verify_receipt(receipt, raw, self.provider_public_key, self.provider_id)
        connection = _connect(self.journal_path, self.sqlite_timeout)
        try:
            connection.execute("BEGIN IMMEDIATE")
            existing = _find(connection, "dispatches", self.scope, request, raw)
            if existing is None:
                raise ValueError("original_dispatch_claim_missing")
            if existing["state"] in TERMINAL:
                if bytes(existing["receipt_bytes"]) != receipt:
                    raise ValueError("conflicting_terminal_receipt")
                connection.commit()
                return existing
            connection.execute("""UPDATE dispatches SET state=?,receipt_bytes=?,observed_at_ms=?
                WHERE request_digest=? AND state='CLAIMED'""", (
                payload["status"].upper(), receipt, time.time_ns() // 1000000, bytes_digest(raw)))
            row = connection.execute("SELECT * FROM dispatches WHERE request_digest=?", (bytes_digest(raw),)).fetchone()
            connection.commit()
            return row
        except BaseException:
            connection.rollback()
            raise
        finally:
            connection.close()

    def _retain_unknown(self, request: dict, raw: bytes, reason: str) -> dict:
        # Never write UNKNOWN over another worker's confirmed receipt. A failed
        # observation cannot invalidate a previously authenticated observation.
        try:
            row = self._read(request, raw)
            if row is not None:
                stored = self._from_row(row)
                if stored["state"] in TERMINAL:
                    return {**stored, "observation_warning": reason}
        except (sqlite3.Error, ValueError, OSError):
            pass
        return self._result("UNKNOWN", bytes_digest(raw), reason)

    def submit(self, request: dict) -> dict:
        """Claim once before at most one POST; an existing claim never sends."""
        try:
            request, raw = self._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            return self._result("REJECTED", None, "request_schema_or_scope_rejected")
        try:
            row, created = self._claim(request, raw)
        except ValueError as exc:
            state = "CONFLICT" if str(exc) == "immutable_request_identity_conflict" else "REJECTED"
            return self._result(state, bytes_digest(raw), str(exc))
        except (sqlite3.Error, OSError):
            return self._result("JOURNAL_UNAVAILABLE", bytes_digest(raw), "durable_claim_not_confirmed_no_post")
        if not created:
            return self._from_row(row)
        try:
            if self.fault_hook is not None:
                self.fault_hook("after_claim", {"request_digest": bytes_digest(raw)})
            status, receipt = self._http("POST", "/payments", raw)
            if status != 200:
                return self._retain_unknown(request, raw, "provider_http_" + str(status) + "_claim_retained")
            payload = verify_receipt(receipt, raw, self.provider_public_key, self.provider_id)
            if self.fault_hook is not None:
                self.fault_hook("after_response", {"request_digest": bytes_digest(raw), "status": payload["status"]})
            return self._from_row(self._store_receipt(request, raw, receipt))
        except Exception:
            # Includes transport, receipt verification, SQLite writes and the
            # explicitly trusted harness hooks. Process death simply leaves the
            # already committed CLAIMED row for the next process to inspect.
            return self._retain_unknown(request, raw, "post_claim_outcome_unresolved")

    def read_status(self, request: dict) -> dict:
        """Read the original claim/receipt without network access or a write."""
        try:
            request, raw = self._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            return self._result("REJECTED", None, "request_schema_or_scope_rejected")
        try:
            row = self._read(request, raw)
            return (self._from_row(row) if row is not None else
                    self._result("UNKNOWN", bytes_digest(raw), "no_durable_claim_in_this_store"))
        except ValueError as exc:
            state = "CONFLICT" if str(exc) == "immutable_request_identity_conflict" else "UNKNOWN"
            return self._result(state, bytes_digest(raw), str(exc))
        except (sqlite3.Error, OSError):
            return self._result("UNKNOWN", bytes_digest(raw), "journal_unreadable")

    def reconcile(self, request: dict) -> dict:
        """Only GET; a missing lookup is UNKNOWN and never clears/resends a claim."""
        try:
            request, raw = self._prepare(request)
        except (ValueError, TypeError, UnicodeError):
            return self._result("REJECTED", None, "request_schema_or_scope_rejected")
        try:
            row = self._read(request, raw)
            if row is None:
                return self._result("UNKNOWN", bytes_digest(raw), "no_durable_claim_in_this_store")
            cached = self._from_row(row)
            if cached["state"] in TERMINAL:
                return cached
        except ValueError as exc:
            state = "CONFLICT" if str(exc) == "immutable_request_identity_conflict" else "UNKNOWN"
            return self._result(state, bytes_digest(raw), str(exc))
        except (sqlite3.Error, OSError):
            return self._result("UNKNOWN", bytes_digest(raw), "journal_unreadable_no_lookup")
        try:
            query = urlencode({"operation_id": request["operation_id"],
                               "idempotency_key": request["idempotency_key"],
                               "request_digest": bytes_digest(raw)})
            status, receipt = self._http("GET", "/payments?" + query)
            if status != 200:
                return self._retain_unknown(request, raw, "read_only_lookup_http_" + str(status))
            payload = verify_receipt(receipt, raw, self.provider_public_key, self.provider_id)
            if self.fault_hook is not None:
                self.fault_hook("after_response", {"request_digest": bytes_digest(raw), "status": payload["status"]})
            return self._from_row(self._store_receipt(request, raw, receipt))
        except Exception:
            return self._retain_unknown(request, raw, "read_only_reconciliation_unresolved")

    def snapshot(self) -> dict:
        """Harness-only view of retained local claims, without credentials/keys."""
        connection = _readonly(self.journal_path)
        try:
            rows = connection.execute("SELECT * FROM dispatches ORDER BY request_digest").fetchall()
            return {"claims": len(rows), "records": [{
                "request_digest": row["request_digest"], "operation_id": row["operation_id"],
                "idempotency_key": row["idempotency_key"], "state": row["state"],
                "receipt_digest": bytes_digest(bytes(row["receipt_bytes"])) if row["receipt_bytes"] is not None else None,
            } for row in rows]}
        finally:
            connection.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    provider = commands.add_parser("provider", help="Run local synthetic provider from a private harness config")
    provider.add_argument("--config", required=True, type=Path)
    args = parser.parse_args()
    try:
        if stat.S_IMODE(args.config.stat().st_mode) & 0o077:
            raise ValueError("provider_config_must_be_owner_private")
        raw = load_json(args.config.read_bytes())
        required = {"db_path", "context", "private_key_hex", "credential", "configuration_digest",
                    "recovery_epoch", "initial_balances"}
        optional = {"provider_id", "sqlite_timeout", "drop_after_commit"}
        if type(raw) is not dict or not required <= set(raw) or set(raw) - required - optional:
            raise ValueError("provider_config_fields")
        private_hex = raw.pop("private_key_hex")
        if type(private_hex) is not str or re.fullmatch(r"[0-9a-f]{64}", private_hex) is None:
            raise ValueError("provider_config_private_key_shape")
        serve_provider(ProviderConfig(private_key=bytes.fromhex(private_hex), **raw))
    except KeyboardInterrupt:
        return 0
    except (OSError, ValueError, TypeError, sqlite3.Error):
        # Do not print repr(config), headers, tokens or private key material.
        parser.error("local provider configuration or store could not be opened")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
