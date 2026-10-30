"""Strict local experiment messages; no fixture keys or network side effects."""

import json
import re
from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from incident_assessor.evidence import canonical, digest, signing_bytes
from incident_assessor.model import InputError, digest_hex, exact_keys, strict_json, text, timestamp

MAX_PAYLOAD = 1024 * 1024
MAX_CONTROL = 64 * 1024
DOMAIN = b"upload-pilot-control/0.1\0"
ROUTE_FIELDS = {"actor_id", "provider_id", "endpoint", "tenant_id", "account_id", "purpose", "route_id", "stage"}


def utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "Z")


def validate_endpoint(endpoint):
    text(endpoint)
    # Literal spelling is deliberate: no DNS, URL normalization, userinfo or alternate paths.
    match = re.fullmatch(r"http://127\.0\.0\.1:([1-9][0-9]{0,4})/upload", endpoint)
    if not match:
        raise InputError("Only the controller-pinned literal loopback /upload endpoint is supported")
    port = int(match.group(1))
    if not 1 <= port <= 65535:
        raise InputError("Invalid loopback port")
    return endpoint


def decode_json(raw, *, max_bytes=MAX_CONTROL):
    if type(raw) is str:
        raw = raw.encode("utf-8")
    if type(raw) is not bytes or len(raw) > max_bytes:
        raise InputError("Invalid or oversized JSON message")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InputError("Duplicate JSON key: " + key)
            result[key] = value
        return result
    def constant(value):
        raise InputError("Non-finite JSON constant")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        canonical(value)
        return value
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise InputError("Invalid JSON message") from exc


def public_key(secret_hex):
    digest_hex(secret_hex)
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret_hex)).public_key().public_bytes_raw().hex()


def _sign(body, secret_hex, key_id, research):
    digest_hex(secret_hex)
    text(key_id)
    envelope = {"algorithm": "Ed25519", "key_id": key_id, "body": deepcopy(body)}
    message = signing_bytes(envelope) if research else DOMAIN + canonical(envelope)
    envelope["signature"] = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(secret_hex)).sign(message).hex()
    return envelope


def sign_record(body, secret_hex, key_id):
    return _sign(body, secret_hex, key_id, True)


def sign_control(body, secret_hex, key_id):
    return _sign(body, secret_hex, key_id, False)


def verify_control(envelope, public_hex, key_id, kind):
    exact_keys(envelope, {"algorithm", "key_id", "body", "signature"})
    if envelope["algorithm"] != "Ed25519" or envelope["key_id"] != key_id:
        raise InputError("Unexpected control signature algorithm or key")
    if type(envelope["body"]) is not dict or envelope["body"].get("kind") != kind:
        raise InputError("Unexpected control record kind")
    digest_hex(public_hex)
    digest_hex(envelope["signature"], 64)
    unsigned = {key: envelope[key] for key in ("algorithm", "key_id", "body")}
    try:
        Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_hex)).verify(
            bytes.fromhex(envelope["signature"]), DOMAIN + canonical(unsigned))
    except InvalidSignature as exc:
        raise InputError("Invalid control signature") from exc
    return deepcopy(envelope["body"])


@dataclass(frozen=True)
class GateConfig:
    endpoint: str
    route: dict
    gateway_secret: str = field(repr=False)
    gateway_key_id: str
    gateway_issuer: str
    receiver_public: str
    receiver_key_id: str

    def __post_init__(self):
        validate_endpoint(self.endpoint)
        exact_keys(self.route, ROUTE_FIELDS)
        for value in self.route.values():
            text(value)
        if self.route["endpoint"] != self.endpoint or self.route["stage"] != "transfer":
            raise InputError("Configured route does not bind the controlled upload endpoint/stage")
        digest_hex(self.gateway_secret)
        digest_hex(self.receiver_public)
        for value in (self.gateway_key_id, self.gateway_issuer, self.receiver_key_id):
            text(value)
        object.__setattr__(self, "route", deepcopy(self.route))
