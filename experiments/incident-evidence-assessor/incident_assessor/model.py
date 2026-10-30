"""Strict parsing for this experiment's small, versioned input contract."""

import json
import re
from datetime import datetime
from pathlib import Path

import rfc8785

MAX_BYTES = 8 * 1024 * 1024
MAX_ITEMS = 10000
MAX_DEPTH = 64
ROLES = {"policy", "gateway", "collector", "provider", "author", "reviewer", "responder", "recipient"}
WORKFLOWS = {"transfer", "erasure", "publication", "incident_response", "cross_party"}
SUBJECT_FIELDS = {
    "request_id", "actor_id", "provider_id", "endpoint", "tenant_id", "account_id",
    "purpose", "payload_sha256", "artifact_id", "revision_id", "object_ids",
    "policy_id", "policy_version", "policy_sha256", "stage", "route_id", "disclosure_sha256",
}


class InputError(ValueError):
    """Malformed or unsupported input; not a finding about external conduct."""


def exact_keys(value, required, optional=()):
    if type(value) is not dict:
        raise InputError("Expected an object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    if missing or extra:
        raise InputError("Object fields differ: missing=" + repr(sorted(missing)) + "; unknown=" + repr(sorted(extra)))
    return value


def text(value):
    if type(value) is not str or not value.strip() or len(value) > 16384:
        raise InputError("Expected a nonempty string of at most 16384 characters")
    return value


def boolean(value):
    if type(value) is not bool:
        raise InputError("Expected a JSON boolean, not a string or number")
    return value


def strings(value):
    if type(value) is not list or len(value) > MAX_ITEMS:
        raise InputError("Expected a bounded string array")
    for item in value:
        text(item)
    if len(set(value)) != len(value):
        raise InputError("Duplicate string array item")
    return value


def enum(value, choices):
    text(value)
    if value not in choices:
        raise InputError("Unsupported enum value: " + value)
    return value


def digest_hex(value, length=32):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{%d}" % (2 * length), value):
        raise InputError("Expected lowercase hexadecimal of length " + str(2 * length))
    return value


def timestamp(value):
    text(value)
    pattern = r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d{1,6})?(?:Z|[+-]\d\d:\d\d)"
    if not re.fullmatch(pattern, value):
        raise InputError("Expected ISO 8601 seconds with a timezone; precision at most microseconds")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise InputError("Invalid timestamp") from exc
    if parsed.tzinfo is None:
        raise InputError("Timezone required")
    return parsed


def interval(start, end):
    left, right = timestamp(start), timestamp(end)
    if left >= right:
        raise InputError("Time interval must be nonempty and increasing")
    return left, right


def bounded_json(value, depth=0):
    if depth > MAX_DEPTH:
        raise InputError("JSON nesting exceeds 64 levels")
    if type(value) is dict:
        if len(value) > MAX_ITEMS or any(type(k) is not str for k in value):
            raise InputError("Object is too large or has a non-string key")
        for item in value.values():
            bounded_json(item, depth + 1)
    elif type(value) is list:
        if len(value) > MAX_ITEMS:
            raise InputError("Array exceeds 10000 items")
        for item in value:
            bounded_json(item, depth + 1)
    elif value is not None and type(value) not in {str, int, float, bool}:
        raise InputError("Unsupported JSON value")


def canonical(value):
    bounded_json(value)
    try:
        return rfc8785.dumps(value)
    except (ValueError, TypeError, OverflowError, UnicodeError, RecursionError) as exc:
        raise InputError("Value is outside the supported JCS data model") from exc


def strict_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InputError("Duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(value):
        raise InputError("Non-finite JSON constant: " + value)

    with Path(path).open("rb") as handle:
        raw = handle.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise InputError("Input exceeds 8 MiB")
    try:
        result = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        canonical(result)
        return result
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise InputError("Invalid JSON input") from exc


def subject(value, field_names=None):
    exact_keys(value, {"request_id"}, SUBJECT_FIELDS - {"request_id"})
    if field_names is not None and value.keys() != field_names:
        raise InputError("Record binding must use the target subject field names")
    for name, item in value.items():
        if name == "object_ids":
            strings(item)
            if not item:
                raise InputError("Object identifiers cannot be empty when supplied")
        elif name.endswith("_sha256"):
            digest_hex(item)
        else:
            text(item)
    return value


def validate_package(package, modules):
    canonical(package)
    exact_keys(package, {"format", "evaluation_id", "workflow", "as_of", "target", "records"})
    enum(package["format"], {"incident-evidence-input/0.1"})
    text(package["evaluation_id"])
    enum(package["workflow"], WORKFLOWS)
    timestamp(package["as_of"])
    target = exact_keys(package["target"], {"subject", "operation_at", "coverage_requested", "authorities"})
    subject(target["subject"])
    timestamp(target["operation_at"])
    enum(target["coverage_requested"], {"managed_route", "broader_activity"})
    exact_keys(target["authorities"], (), ROLES)
    for issuer in target["authorities"].values():
        text(issuer)
    records = package["records"]
    if type(records) is not list or len(records) > MAX_ITEMS:
        raise InputError("Expected at most 10000 signed records")
    record_ids = set()
    for record in records:
        exact_keys(record, {"algorithm", "key_id", "body", "signature"})
        enum(record["algorithm"], {"Ed25519"})
        text(record["key_id"])
        digest_hex(record["signature"], 64)
        body = exact_keys(record["body"], {"record_id", "evaluation_id", "kind", "issuer", "recorded_at", "binding", "data"})
        for key in ("record_id", "evaluation_id", "kind", "issuer"):
            text(body[key])
        if body["record_id"] in record_ids:
            raise InputError("Duplicate record identifier")
        record_ids.add(body["record_id"])
        timestamp(body["recorded_at"])
        subject(body["binding"], target["subject"].keys())
        if body["kind"] not in modules:
            raise InputError("Unsupported record kind: " + body["kind"])
        modules[body["kind"]].validate_data(body["kind"], body["data"])


def validate_trust(trust):
    canonical(trust)
    exact_keys(trust, {"format", "evaluation_id", "workflow", "as_of", "target_sha256", "mode", "keys"})
    enum(trust["format"], {"incident-evidence-trust/0.1"})
    text(trust["evaluation_id"])
    enum(trust["workflow"], WORKFLOWS)
    timestamp(trust["as_of"])
    digest_hex(trust["target_sha256"])
    enum(trust["mode"], {"synthetic-test-only", "explicit-evaluator"})
    if type(trust["keys"]) is not dict or len(trust["keys"]) > MAX_ITEMS:
        raise InputError("Expected a bounded trust key mapping")
    public_identities, organizations = {}, {}
    for key_id, key in trust["keys"].items():
        text(key_id)
        exact_keys(key, {"public_key", "issuer", "organization", "roles", "not_before", "not_after"})
        digest_hex(key["public_key"])
        text(key["issuer"])
        text(key["organization"])
        strings(key["roles"])
        for role in key["roles"]:
            enum(role, ROLES)
        interval(key["not_before"], key["not_after"])
        identity = (key["issuer"], key["organization"])
        if key["public_key"] in public_identities and public_identities[key["public_key"]] != identity:
            raise InputError("One public key cannot establish different trusted identities")
        if key["issuer"] in organizations and organizations[key["issuer"]] != key["organization"]:
            raise InputError("An issuer has conflicting trusted organizations")
        public_identities[key["public_key"]] = identity
        organizations[key["issuer"]] = key["organization"]
