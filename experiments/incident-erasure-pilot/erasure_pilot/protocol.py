"""Strict, domain-separated messages; original assessor record signatures."""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import re

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from incident_assessor.evidence import digest, signing_bytes
from incident_assessor.model import InputError, bounded_json, canonical, digest_hex, exact_keys, text, timestamp

DOMAIN = b"erasure-pilot-control/0.1\0"
MAX_OBJECT = 1024 * 1024
MAX_JSON = 4 * 1024 * 1024
LOCATION = "active-object-namespace"
EXCLUSIONS = ["backups", "replicas", "downstream-copies", "training-derivatives",
              "open-handles-and-memory", "storage-media"]


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def sha256_bytes(value):
    if type(value) is not bytes:
        raise InputError("Hash input must be owned bytes")
    return hashlib.sha256(value).hexdigest()


def identifier(value):
    if type(value) is not str or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,63}", value):
        raise InputError("Unsupported bounded identifier")
    return value


def decode_json(raw):
    if type(raw) is str:
        try:
            raw = raw.encode("utf-8")
        except UnicodeError as exc:
            raise InputError("Invalid JSON encoding") from exc
    if type(raw) is not bytes or len(raw) > MAX_JSON:
        raise InputError("Invalid or oversized JSON message")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InputError("Duplicate JSON key")
            result[key] = value
        return result
    def constant(value):
        raise InputError("Non-finite JSON constant")
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant, parse_float=constant)
        canonical(result)
        return result
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError("Invalid JSON message") from exc


def capture(value):
    """Own strict JSON without allowing JCS to normalize invalid numeric types."""
    bounded_json(value)
    def reject_floats(item):
        if type(item) is float:
            raise InputError("This bounded protocol has no floating-point fields")
        if type(item) is dict:
            for child in item.values():
                reject_floats(child)
        elif type(item) is list:
            for child in item:
                reject_floats(child)
    reject_floats(value)
    return decode_json(canonical(value))


def public_key(secret):
    digest_hex(secret)
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret)).public_key().public_bytes_raw().hex()


def _sign(body, secret, key_id, *, record=False):
    digest_hex(secret)
    text(key_id)
    envelope = {"algorithm": "Ed25519", "key_id": key_id, "body": deepcopy(body)}
    message = signing_bytes(envelope) if record else DOMAIN + canonical(envelope)
    envelope["signature"] = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret)).sign(message).hex()
    return envelope


def sign_message(body, secret, key_id):
    return _sign(body, secret, key_id)


def sign_record(body, secret, key_id):
    return _sign(body, secret, key_id, record=True)


def _verify(envelope, public, key_id, kind, *, record=False):
    exact_keys(envelope, {"algorithm", "key_id", "body", "signature"})
    if envelope["algorithm"] != "Ed25519" or envelope["key_id"] != key_id:
        raise InputError("Unexpected signature algorithm or key")
    if type(envelope["body"]) is not dict or envelope["body"].get("kind") != kind:
        raise InputError("Unexpected record kind")
    digest_hex(public)
    digest_hex(envelope["signature"], 64)
    unsigned = {key: envelope[key] for key in ("algorithm", "key_id", "body")}
    message = signing_bytes(unsigned) if record else DOMAIN + canonical(unsigned)
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public)).verify(bytes.fromhex(envelope["signature"]), message)
    except InvalidSignature as exc:
        raise InputError("Invalid signature") from exc
    return deepcopy(envelope["body"])


def verify_message(envelope, public, key_id, kind):
    return _verify(envelope, public, key_id, kind)


def verify_record(envelope, public, key_id, kind):
    return _verify(envelope, public, key_id, kind, record=True)


def object_name(manifest):
    fields = ("provider_id", "tenant_id", "object_id", "version_id")
    for field in fields:
        identifier(manifest[field])
    return digest({field: manifest[field] for field in fields}) + ".bin"
