"""Bounded, owned control messages for the synthetic collector experiment.

These signatures attest to this controller's statements, not independent truth.
No control message contains the payload that the separate upload receiver sees.
"""

import json
import re
from copy import deepcopy

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from upload_pilot.protocol import (
    InputError, canonical, digest, public_key, sign_record, timestamp, utc_now,
)


DOMAIN = b"collector-pilot-control/0.1\0"
MAX_CONTROL = 64 * 1024
MAX_PAYLOAD = 1024 * 1024
MAX_STRING = 256
ENVELOPE_FIELDS = {"algorithm", "key_id", "body", "signature"}
INTENT_FIELDS = {
    "kind", "collector_id", "collection_id", "request_id", "evaluation_id",
    "subject_sha256", "payload_sha256", "byte_length", "policy_sha256",
    "decision_sha256", "created_at",
}
RECEIPT_FIELDS = {
    "kind", "collector_id", "collection_id", "request_id", "request_sha256",
    "recorded_at", "receipt_id", "storage",
}
QUERY_FIELDS = {
    "kind", "collector_id", "collection_id", "request_id", "request_sha256", "nonce", "created_at",
}
STATUS_FIELDS = {
    "kind", "collector_id", "collection_id", "request_id", "request_sha256",
    "query_sha256", "nonce", "status", "receipt", "checked_at",
}


def _exact(value, fields):
    if type(value) is not dict or value.keys() != set(fields):
        raise InputError("Unexpected control object fields")
    return value


def _text(value):
    if type(value) is not str or not value.strip() or len(value) > MAX_STRING:
        raise InputError("Expected a bounded nonempty control string")
    return value


def _hex(value, length=32):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{%d}" % (length * 2), value):
        raise InputError("Invalid lowercase hexadecimal control value")
    return value


def _bounded(value, depth=0):
    if depth > 32:
        raise InputError("Control JSON is too deeply nested")
    if type(value) is dict:
        if len(value) > 1024 or any(type(key) is not str for key in value):
            raise InputError("Invalid control JSON object")
        for item in value.values():
            _bounded(item, depth + 1)
    elif type(value) is list:
        if len(value) > 1024:
            raise InputError("Control JSON array is too large")
        for item in value:
            _bounded(item, depth + 1)
    elif value is not None and type(value) not in {str, int, bool}:
        # Reject integral floats before JCS can normalize 1.0 into integer 1.
        raise InputError("Control JSON permits no floats or non-JSON values")


def decode_json(raw, *, max_bytes=MAX_CONTROL):
    if type(raw) is str:
        try:
            raw = raw.encode("utf-8")
        except UnicodeError as exc:
            raise InputError("Invalid control JSON encoding") from exc
    if type(raw) is not bytes or len(raw) > max_bytes:
        raise InputError("Invalid or oversized control JSON")

    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InputError("Duplicate control JSON key")
            result[key] = value
        return result

    def unsupported(_):
        raise InputError("Control JSON permits no floats or non-finite values")

    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs,
                           parse_float=unsupported, parse_constant=unsupported)
        _bounded(value)
        canonical(value)
        return value
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError("Invalid control JSON") from exc


def capture(value):
    """Take an owned, bounded snapshot without normalizing invalid scalar types."""
    try:
        owned = deepcopy(value)
        _bounded(owned)
        raw = canonical(owned)
        return decode_json(raw)
    except (TypeError, ValueError, RecursionError, RuntimeError) as exc:
        raise InputError("Invalid control value") from exc


def validate_endpoint(endpoint):
    _text(endpoint)
    match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})", endpoint)
    if match is None or not 1 <= int(match.group(1)) <= 65535:
        raise InputError("Only a literal loopback collector endpoint is supported")
    return endpoint


def collection_id(collector_id, request_id):
    _text(collector_id)
    _text(request_id)
    return digest({"collector_id": collector_id, "request_id": request_id})


def _identity(body):
    _text(body["collector_id"])
    _text(body["request_id"])
    _hex(body["collection_id"])
    if body["collection_id"] != collection_id(body["collector_id"], body["request_id"]):
        raise InputError("Collection identity does not match its request")


def validate_intent(body):
    body = _exact(capture(body), INTENT_FIELDS)
    if body["kind"] != "collection_intent":
        raise InputError("Expected a collection intent")
    _identity(body)
    _text(body["evaluation_id"])
    for name in ("subject_sha256", "payload_sha256", "policy_sha256", "decision_sha256"):
        _hex(body[name])
    if type(body["byte_length"]) is not int or not 0 <= body["byte_length"] <= MAX_PAYLOAD:
        raise InputError("Invalid payload length in collection intent")
    timestamp(body["created_at"])
    return body


def validate_query(body):
    body = _exact(capture(body), QUERY_FIELDS)
    if body["kind"] != "collection_query":
        raise InputError("Expected a collection query")
    _identity(body)
    _hex(body["request_sha256"])
    _hex(body["nonce"])
    timestamp(body["created_at"])
    return body


def _envelope(value, kind):
    envelope = _exact(capture(value), ENVELOPE_FIELDS)
    if envelope["algorithm"] != "Ed25519":
        raise InputError("Unexpected control signature algorithm")
    _text(envelope["key_id"])
    _hex(envelope["signature"], 64)
    if type(envelope["body"]) is not dict or envelope["body"].get("kind") != kind:
        raise InputError("Unexpected control record kind")
    return envelope


def sign_control(body, secret_hex, key_id):
    _hex(secret_hex)
    _text(key_id)
    if type(body) is not dict:
        raise InputError("A control body must be an object")
    envelope = {"algorithm": "Ed25519", "key_id": key_id, "body": capture(body)}
    envelope["signature"] = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret_hex)).sign(
        DOMAIN + canonical(envelope)).hex()
    return envelope


def verify_control(envelope, public_hex, key_id, kind):
    envelope = _envelope(envelope, kind)
    _hex(public_hex)
    _text(key_id)
    if envelope["key_id"] != key_id:
        raise InputError("Unexpected control signing key")
    unsigned = {name: envelope[name] for name in ("algorithm", "key_id", "body")}
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex)).verify(
            bytes.fromhex(envelope["signature"]), DOMAIN + canonical(unsigned))
    except InvalidSignature as exc:
        raise InputError("Invalid collector control signature") from exc
    return deepcopy(envelope["body"])


def verify_receipt(envelope, intent, public_key, key_id, at):
    intent = _envelope(intent, "collection_intent")
    original = validate_intent(intent["body"])
    body = _exact(verify_control(envelope, public_key, key_id, "collection_receipt"), RECEIPT_FIELDS)
    _identity(body)
    _hex(body["request_sha256"])
    _text(body["receipt_id"])
    if body["storage"] != "sqlite-wal-full":
        raise InputError("Unexpected collector storage claim")
    if (any(body[name] != original[name] for name in ("collector_id", "collection_id", "request_id"))
            or body["request_sha256"] != digest(intent)):
        raise InputError("Collector receipt does not bind this intent")
    if not timestamp(original["created_at"]) <= timestamp(body["recorded_at"]) <= timestamp(at):
        raise InputError("Collector receipt chronology is invalid")
    return deepcopy(body)


def verify_status(envelope, query, intent, public_key, key_id, at):
    intent = _envelope(intent, "collection_intent")
    original = validate_intent(intent["body"])
    query = _envelope(query, "collection_query")
    requested = validate_query(query["body"])
    if (any(requested[name] != original[name] for name in ("collector_id", "collection_id", "request_id"))
            or requested["request_sha256"] != digest(intent)
            or timestamp(requested["created_at"]) < timestamp(original["created_at"])):
        raise InputError("Collector query does not bind this intent")
    body = _exact(verify_control(envelope, public_key, key_id, "collection_status"), STATUS_FIELDS)
    _identity(body)
    for name in ("request_sha256", "query_sha256", "nonce"):
        _hex(body[name])
    if (any(body[name] != requested[name] for name in
            ("collector_id", "collection_id", "request_id", "request_sha256", "nonce"))
            or body["query_sha256"] != digest(query)):
        raise InputError("Collector status does not bind this fresh query")
    if not timestamp(requested["created_at"]) <= timestamp(body["checked_at"]) <= timestamp(at):
        raise InputError("Collector status chronology is invalid")
    if body["status"] == "FOUND":
        verify_receipt(body["receipt"], intent, public_key, key_id, body["checked_at"])
    elif body["status"] == "NOT_FOUND":
        if body["receipt"] is not None:
            raise InputError("Missing collector record cannot carry a receipt")
    else:
        raise InputError("Unsupported collector status")
    return deepcopy(body)
