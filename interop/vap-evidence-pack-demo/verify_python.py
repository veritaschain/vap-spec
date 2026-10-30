#!/usr/bin/env python3
"""Verifier for vap-interop-demo/0.2.0, an experimental synthetic-data contract.

This is not a VAP profile-conformance or production-identity verifier. Trust and
the expected scope must be supplied separately by the caller.
"""

import argparse
import base64
import binascii
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

CONTRACT_ID = "vap-interop-demo/0.2.0"
CANONICALIZATION = "DEMO-ASCII-SAFEINT-JSON-v1"
MAX_SAFE_INTEGER = 9007199254740991
MAX_FILE_BYTES = 2 * 1024 * 1024
EVENT_TYPES = ["AI_DECISION_ATTEMPT", "AI_DECISION_OUTCOME"]
CHECKS = [
    "contract-and-shape", "pinned-scope", "event-signatures",
    "sequence-and-scope", "rfc6962-root", "role-receipts",
    "attempt-outcome-bijection",
]


class VerificationError(ValueError):
    """Input does not satisfy the experimental contract."""


def _require(condition, message):
    if not condition:
        raise VerificationError(message)


def _subset(value, depth=0):
    _require(depth <= 16, "JSON nesting exceeds 16")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        _require(abs(value) <= MAX_SAFE_INTEGER, "integer exceeds the safe range")
    elif type(value) is str:
        _require(len(value) <= 1024 and all(32 <= ord(c) <= 126 for c in value),
                 "strings must be printable ASCII, at most 1024 characters")
    elif type(value) is list:
        for item in value:
            _subset(item, depth + 1)
    elif type(value) is dict:
        for key, item in value.items():
            _require(type(key) is str, "object key must be a string")
            _subset(key, depth + 1)
            _subset(item, depth + 1)
    else:
        raise VerificationError("unsupported JSON value type")


def canonical(value):
    """Canonical bytes of the restricted ASCII/safe-integer demo subset."""
    _subset(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("ascii")


def _integer(token):
    _require(token != "-0", "negative zero is not permitted")
    # Avoid conversion of arbitrarily long integers before the range check.
    _require(len(token.lstrip("-")) <= 16, "integer exceeds the safe range")
    value = int(token)
    _require(abs(value) <= MAX_SAFE_INTEGER, "integer exceeds the safe range")
    return value


def _not_integer(_token):
    raise VerificationError("only integer number tokens are permitted")


def _object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate object key")
        result[key] = value
    return result


def strict_loads(text):
    """Parse raw JSON without duplicate keys, floats or lossy number coercion."""
    _require(type(text) is str, "JSON input must be text")
    try:
        _require(len(text.encode("utf-8")) <= MAX_FILE_BYTES,
                 "JSON input exceeds 2 MiB")
        value = json.loads(text, object_pairs_hook=_object, parse_int=_integer,
                           parse_float=_not_integer, parse_constant=_not_integer)
        _subset(value)
        return value
    except (json.JSONDecodeError, UnicodeError, RecursionError) as exc:
        raise VerificationError("invalid JSON encoding or syntax") from exc


def load_json(path):
    """Read at most 2 MiB of strict UTF-8. OSError is an operational error."""
    with Path(path).open("rb") as stream:
        raw = stream.read(MAX_FILE_BYTES + 1)
    _require(len(raw) <= MAX_FILE_BYTES, "JSON input exceeds 2 MiB")
    try:
        return strict_loads(raw.decode("utf-8", errors="strict"))
    except UnicodeError as exc:
        raise VerificationError("input is not valid UTF-8") from exc


def _shape(value, fields, label):
    _require(type(value) is dict and set(value) == set(fields.split()),
             label + " has missing or unknown fields")


def _string(value, label):
    _require(type(value) is str and 0 < len(value) <= 1024
             and all(32 <= ord(c) <= 126 for c in value), label + " must be nonempty ASCII")


def _count(value, low, high, label):
    _require(type(value) is int and low <= value <= high, label + " is out of range")


def _hex(value, label):
    _require(type(value) is str and re.fullmatch(r"[0-9a-f]{64}", value) is not None,
             label + " must be a lowercase SHA-256 digest")


def _base64(value, size, label):
    _require(type(value) is str, label + " must be base64 text")
    try:
        raw = base64.b64decode(value, validate=True)
    except (ValueError, binascii.Error) as exc:
        raise VerificationError(label + " is not canonical base64") from exc
    _require(len(raw) == size and base64.b64encode(raw).decode("ascii") == value,
             label + " has the wrong length or noncanonical base64")
    return raw


def _timestamp(value, label):
    _require(type(value) is str and re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value) is not None,
        label + " must be a UTC timestamp with seconds")
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise VerificationError(label + " is not a real calendar timestamp") from exc


def _digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _without(value, *keys):
    return {key: item for key, item in value.items() if key not in keys}


def merkle_root(events):
    """RFC 6962 MTH over canonical full signed events, without odd-leaf padding."""
    def tree(leaves):
        if not leaves:
            return hashlib.sha256(b"").digest()
        if len(leaves) == 1:
            return hashlib.sha256(b"\x00" + canonical(leaves[0])).digest()
        split = 1 << ((len(leaves) - 1).bit_length() - 1)
        return hashlib.sha256(b"\x01" + tree(leaves[:split]) + tree(leaves[split:])).digest()
    return tree(events).hex()


def _signature(value, public_key, label):
    signature = _base64(value["signature"], 64, label + " signature")
    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature, canonical(_without(value, "signature")))
    except (InvalidSignature, ValueError) as exc:
        raise VerificationError(label + " signature is invalid") from exc


def _validate_shape(pack, trust):
    _subset(pack)
    _subset(trust)
    _shape(pack, "contract_id canonicalization hash_algorithm signature_algorithm scope "
           "scope_commitment events merkle producer_manifest observer_receipt demo_anchor_receipt", "pack")
    _require(pack["contract_id"] == CONTRACT_ID, "unsupported contract_id")
    _require(pack["canonicalization"] == CANONICALIZATION, "unsupported canonicalization")
    _require(pack["hash_algorithm"] == "SHA-256", "unsupported hash algorithm")
    _require(pack["signature_algorithm"] == "Ed25519", "unsupported signature algorithm")
    scope = pack["scope"]
    _shape(scope, "chain_id batch_id policy_id window_start window_end in_scope_event_types "
           "expected_attempt_count completeness_rule", "scope")
    for key in ("chain_id", "batch_id", "policy_id"):
        _string(scope[key], "scope." + key)
    start = _timestamp(scope["window_start"], "scope.window_start")
    end = _timestamp(scope["window_end"], "scope.window_end")
    _require(start <= end, "scope window is reversed")
    _require(scope["in_scope_event_types"] == EVENT_TYPES, "unsupported in-scope event types")
    _require(scope["completeness_rule"] == "ATTEMPT_OUTCOME_BIJECTION", "unsupported completeness rule")
    _count(scope["expected_attempt_count"], 1, 64, "expected_attempt_count")
    _hex(pack["scope_commitment"], "scope_commitment")
    _require(type(pack["events"]) is list and 2 <= len(pack["events"]) <= 128,
             "events must contain between 2 and 128 items")
    for event in pack["events"]:
        _shape(event, "contract_id chain_id event_id sequence_no event_type timestamp issuer_id "
               "key_id policy_id model_id provenance payload_hash signature", "event")
        _require(event["contract_id"] == CONTRACT_ID, "unsupported event contract")
        _require(event["event_type"] in EVENT_TYPES, "unsupported event type")
        for key in ("chain_id", "event_id", "issuer_id", "key_id", "policy_id", "model_id"):
            _string(event[key], "event." + key)
        _count(event["sequence_no"], 1, 128, "sequence_no")
        _timestamp(event["timestamp"], "event.timestamp")
        _hex(event["payload_hash"], "payload_hash")
        _base64(event["signature"], 64, "event signature")
        provenance = event["provenance"]
        common = "attempt_id actor action "
        is_attempt = event["event_type"] == EVENT_TYPES[0]
        _shape(provenance, common + ("input_hash context" if is_attempt else
               "outcome reason_code human_review_required"), "provenance")
        for key in ("attempt_id", "actor", "action"):
            _string(provenance[key], "provenance." + key)
        if is_attempt:
            _hex(provenance["input_hash"], "input_hash")
            _shape(provenance["context"], "jurisdiction", "context")
            _string(provenance["context"]["jurisdiction"], "jurisdiction")
        else:
            _require(provenance["outcome"] in ("APPROVED", "DENIED_AUTOMATION"), "unsupported outcome")
            _string(provenance["reason_code"], "reason_code")
            _require(type(provenance["human_review_required"]) is bool,
                     "human_review_required must be boolean")
    _shape(pack["merkle"], "algorithm root", "merkle")
    _require(pack["merkle"]["algorithm"] == "RFC6962-SHA256", "unsupported Merkle algorithm")
    _hex(pack["merkle"]["root"], "merkle.root")
    for field in ("producer_manifest", "observer_receipt", "demo_anchor_receipt"):
        record = pack[field]
        _shape(record, "record_type key_id merkle_root scope_commitment event_count issued_at signature", field)
        _string(record["record_type"], "record_type")
        _string(record["key_id"], "record.key_id")
        _hex(record["merkle_root"], "record.merkle_root")
        _hex(record["scope_commitment"], "record.scope_commitment")
        _count(record["event_count"], 1, 128, "record.event_count")
        _timestamp(record["issued_at"], "record.issued_at")
        _base64(record["signature"], 64, "record signature")
    _shape(trust, "contract_id trust_version scope_commitment roles", "trust")
    _require(trust["contract_id"] == CONTRACT_ID and trust["trust_version"] == "demo-trust/1",
             "unsupported trust contract")
    _hex(trust["scope_commitment"], "trust.scope_commitment")
    _shape(trust["roles"], "producer observer anchor", "trust.roles")
    role_keys, role_ids = {}, set()
    for role, config in trust["roles"].items():
        _shape(config, "key_id public_key", "trust role")
        _string(config["key_id"], "trust.key_id")
        raw = _base64(config["public_key"], 32, "public_key")
        _require(config["key_id"] not in role_ids and raw not in role_keys.values(),
                 "roles require distinct key IDs and public keys")
        role_ids.add(config["key_id"])
        role_keys[role] = raw
    return start, end, role_keys


def verify_pack(pack, trust):
    """Return completed check names or raise VerificationError. No network I/O."""
    start, end, role_keys = _validate_shape(pack, trust)
    scope, events, roles = pack["scope"], pack["events"], trust["roles"]
    commitment = _digest(scope)
    _require(pack["scope_commitment"] == commitment == trust["scope_commitment"],
             "scope does not match the caller's pinned commitment")
    for event in events:
        _require(event["key_id"] == roles["producer"]["key_id"], "event is not signed by the producer role")
        _require(event["payload_hash"] == _digest(_without(event, "payload_hash", "signature")),
                 "event payload hash mismatch")
        _signature(event, role_keys["producer"], "event")
    seen_ids, previous_time = set(), start
    for sequence, event in enumerate(events, 1):
        _require(event["sequence_no"] == sequence, "sequence is not contiguous in array order")
        _require(event["event_id"] not in seen_ids, "duplicate event ID")
        seen_ids.add(event["event_id"])
        _require(event["chain_id"] == scope["chain_id"] and event["policy_id"] == scope["policy_id"],
                 "event chain or policy differs from scope")
        time = _timestamp(event["timestamp"], "event.timestamp")
        _require(start <= time <= end and time >= previous_time,
                 "event timestamp is outside the window or decreases")
        previous_time = time
    root = merkle_root(events)
    _require(pack["merkle"]["root"] == root, "Merkle root mismatch")
    for field, role, kind in (
        ("producer_manifest", "producer", "PRODUCER_MANIFEST"),
        ("observer_receipt", "observer", "OBSERVER_RECEIPT"),
        ("demo_anchor_receipt", "anchor", "DEMO_ANCHOR_RECEIPT"),
    ):
        record = pack[field]
        _require(record["record_type"] == kind and record["key_id"] == roles[role]["key_id"],
                 field + " has the wrong record type or role")
        _require(record["merkle_root"] == root and record["scope_commitment"] == commitment
                 and record["event_count"] == len(events), field + " binding mismatch")
        _require(_timestamp(record["issued_at"], field + ".issued_at") >= end,
                 field + " predates the end of the scope")
        _signature(record, role_keys[role], field)
    pairs = {}
    for event in events:
        attempt_id = event["provenance"]["attempt_id"]
        pair = pairs.setdefault(attempt_id, {})
        kind = event["event_type"]
        _require(kind not in pair, "duplicate attempt or outcome for an attempt ID")
        if kind == EVENT_TYPES[1]:
            _require(EVENT_TYPES[0] in pair, "outcome appears before its attempt")
        pair[kind] = event["sequence_no"]
    _require(len(pairs) == scope["expected_attempt_count"]
             and all(set(pair) == set(EVENT_TYPES) for pair in pairs.values()),
             "attempt/outcome bijection does not match the pinned expected count")
    return list(CHECKS)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("pack", type=Path)
    parser.add_argument("--trust", required=True, type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    checks, error, verdict, exit_code = [], None, "PASS", 0
    try:
        checks = verify_pack(load_json(args.pack), load_json(args.trust))
    except VerificationError as exc:
        error, verdict, exit_code = str(exc), "FAIL", 1
    except OSError as exc:
        error, verdict, exit_code = str(exc), "ERROR", 2
    if args.as_json:
        print(json.dumps({"contract_id": CONTRACT_ID, "verdict": verdict,
                          "checks": checks, "error": error}, separators=(",", ":")))
    elif exit_code == 0:
        print("PASS (experimental demo only): " + ", ".join(checks))
    else:
        print(verdict + ": " + error)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
