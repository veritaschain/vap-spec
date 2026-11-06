"""Offline synthetic payment evidence assessment, never payment execution.

Small restricted-JSON and envelope helpers follow the repository's wallet
evidence experiment, with a separate schema, signing domain and trust contract.
This is not RFC 8785, a bank adapter, VAP conformance or an admission control.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any, Callable

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey,
)


BUNDLE_SCHEMA = "experimental-payment-evidence-bundle-v0"
RESULT_SCHEMA = "experimental-payment-evidence-result-v0"
ADAPTER = "synthetic-payment-request-v0"
SIGNING_DOMAIN = b"VSO experimental payment evidence v0\x00"
CLAIMS = ("integrity", "authorization", "execution_match", "control_state")
ROLES = {
    "policy": "policy_authority",
    "maker_approval": "approver",
    "checker_approval": "approver",
    "final_status": "status_authority",
    "dispatch": "execution_observer",
    "provider_receipt": "payment_provider",
    "control": "control_observer",
    "collector": "collector",
}
APPROVALS = ("maker_approval", "checker_approval")
REQUIRED_ROUTES = {
    "payment_gate": "gated",
    "test_to_production": "blocked",
    "cloud_management": "blocked",
    "deployment": "blocked",
}
HASH = re.compile(r"sha256:[0-9a-f]{64}\Z")
DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)\Z")
MAX_INTEGER = 9007199254740991


def _json_value(value: Any, depth: int = 0) -> None:
    if depth > 32:
        raise ValueError("json_nesting_limit")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > MAX_INTEGER:
            raise ValueError("unsafe_json_integer")
        return
    if type(value) is str:
        if len(value) > 65536:
            raise ValueError("json_string_limit")
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non_nfc_string")
        value.encode("utf-8", errors="strict")
        return
    if type(value) is list:
        if len(value) > 256:
            raise ValueError("json_array_limit")
        for item in value:
            _json_value(item, depth + 1)
        return
    if type(value) is dict:
        if len(value) > 256:
            raise ValueError("json_object_limit")
        for key, item in value.items():
            if type(key) is not str:
                raise ValueError("non_string_json_key")
            _json_value(key, depth + 1)
            _json_value(item, depth + 1)
        return
    raise ValueError("unsupported_json_type")


def canonical_json(value: Any) -> bytes:
    """Restricted, bounded canonical JSON; deliberately not an RFC 8785 claim."""
    _json_value(value)
    result = json.dumps(value, ensure_ascii=False, sort_keys=True,
                        separators=(",", ":"), allow_nan=False).encode("utf-8")
    if len(result) > 1048576:
        raise ValueError("json_document_limit")
    return result


def _unique_pairs(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate_json_key")
        result[key] = value
    return result


def _no_float(_: str) -> None:
    raise ValueError("non_integer_json_number")


def load_json(raw: str | bytes) -> Any:
    if type(raw) not in (str, bytes) or len(raw) > 1048576:
        raise ValueError("json_input_type_or_size")
    try:
        value = json.loads(raw, object_pairs_hook=_unique_pairs,
                           parse_float=_no_float, parse_constant=_no_float)
        canonical_json(value)
    except RecursionError as exc:
        raise ValueError("json_nesting_limit") from exc
    return value


def bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest(value: Any) -> str:
    return bytes_digest(canonical_json(value))


def sign_envelope(payload: dict, key_id: str,
                  private_key: Ed25519PrivateKey) -> dict:
    """Evidence-only helper. Fixtures use public test seeds, not payment keys."""
    signed = {"key_id": key_id, "payload": load_json(canonical_json(payload))}
    return {**signed, "signature": private_key.sign(
        SIGNING_DOMAIN + canonical_json(signed)).hex()}


def _text(value: Any) -> bool:
    return type(value) is str and 0 < len(value) <= 256


def _integer(value: Any) -> bool:
    return type(value) is int and 0 <= value <= MAX_INTEGER


def _hash(value: Any) -> bool:
    return type(value) is str and HASH.fullmatch(value) is not None


def _decimal(value: Any) -> bool:
    return type(value) is str and len(value) <= 78 and DECIMAL.fullmatch(value) is not None


def _texts(value: Any) -> bool:
    return (type(value) is list and len(value) <= 64 and all(_text(x) for x in value)
            and len(value) == len(set(value)))


def _hash_map(value: Any) -> bool:
    return (type(value) is dict and all(_text(k) and _hash(v)
                                      for k, v in value.items()))


def _approval_refs(value: Any) -> bool:
    return _hash_map(value) and set(value) == set(APPROVALS)


def _request_hex(value: Any) -> bool:
    return (type(value) is str and 0 < len(value) <= 65536
            and re.fullmatch(r"(?:[0-9a-f]{2})+", value) is not None)


def _routes(value: Any) -> bool:
    return (type(value) is dict and all(_text(k) and type(v) is str and
            v in ("gated", "blocked", "bypassed", "unobserved")
            for k, v in value.items()))


OPERATION_SCHEMA: dict[str, Callable[[Any], bool]] = {
    **{field: _text for field in (
        "operation_id", "tenant", "environment", "api_audience", "principal_id",
        "credential_id", "workload_id", "source_account", "beneficiary",
        "idempotency_domain", "idempotency_key")},
    "adapter": lambda x: x == ADAPTER,
    "configuration_digest": _hash,
    "policy_digest": _hash,
    "payload_digest": _hash,
    "recovery_epoch": _integer,
    "action": lambda x: x == "transfer",
    "amount_minor": lambda x: _decimal(x) and int(x) > 0,
    "currency": lambda x: type(x) is str and re.fullmatch(r"[A-Z]{3}", x) is not None,
    "minor_unit_scale": lambda x: type(x) is int and 0 <= x <= 9,
    "nonce": _decimal,
    "valid_from": _integer,
    "valid_until": _integer,
}


def _shape(value: Any, schema: dict[str, Callable[[Any], bool]]) -> bool:
    return (type(value) is dict and set(value) == set(schema)
            and all(check(value[name]) for name, check in schema.items()))


def validate_operation(operation: Any) -> None:
    if not _shape(operation, OPERATION_SCHEMA):
        raise ValueError("operation_shape")


def synthetic_request_bytes(operation: dict) -> bytes:
    """Only this synthetic encoding is supported, not any bank's wire protocol."""
    validate_operation(operation)
    return canonical_json({"adapter": ADAPTER, "operation": {
        key: value for key, value in operation.items() if key != "payload_digest"}})


POLICY_SCHEMA = {
    **{field: _text for field in (
        "policy_id", "version", "tenant", "environment", "api_audience",
        "provider_id", "principal_id", "credential_id", "workload_id")},
    "adapter": lambda x: x == ADAPTER,
    "configuration_digest": _hash,
    "recovery_epoch": _integer,
    "allowed_sources": _texts,
    "allowed_beneficiaries": _texts,
    "currency": OPERATION_SCHEMA["currency"],
    "minor_unit_scale": OPERATION_SCHEMA["minor_unit_scale"],
    "max_amount_minor": _decimal,
    "required_routes": _texts,
    "valid_from": _integer,
    "valid_until": _integer,
}
APPROVAL_SCHEMA = {
    "approval_id": _text, "operation_digest": _hash, "policy_digest": _hash,
    "issued_at": _integer, "expires_at": _integer,
}
STATUS_SCHEMA = {
    "operation_digest": _hash, "policy_digest": _hash,
    "approval_digests": _approval_refs, "configuration_digest": _hash,
    "recovery_epoch": _integer, "credential_id": _text,
    "checked_at": _integer, "valid_until": _integer,
    "state": lambda x: type(x) is str and x in ("active", "revoked", "unknown"),
    "revoked_at": lambda x: x is None or _integer(x),
}
DISPATCH_SCHEMA = {
    "operation_digest": _hash, "policy_digest": _hash,
    "approval_digests": _approval_refs, "final_status_digest": _hash,
    "control_digest": _hash,
    "actual_operation": lambda x: _shape(x, OPERATION_SCHEMA),
    "request_hex": _request_hex, "dispatched_at": _integer,
    "http_status": lambda x: x is None or type(x) is int and 100 <= x <= 599,
}
RECEIPT_SCHEMA = {
    "provider_id": _text, "api_audience": _text,
    "operation_digest": _hash, "payload_digest": _hash,
    "dispatch_digest": _hash, "observed_at": _integer,
    "status": lambda x: type(x) is str and x in (
        "accepted", "pending", "settled", "failed", "reversed", "unknown"),
}
CONTROL_SCHEMA = {
    "operation_digest": _hash, "configuration_digest": _hash,
    "recovery_epoch": _integer, "observed_at": _integer,
    "observation_boundary": _text, "routes": _routes,
}
COLLECTOR_SCHEMA = {
    "operation_digest": _hash, "configuration_digest": _hash,
    "recovery_epoch": _integer, "checkpoint_id": _text,
    "checkpoint_at": _integer, "retained": _hash_map, "gaps": _texts,
}
SCHEMAS = {
    "policy": POLICY_SCHEMA, "maker_approval": APPROVAL_SCHEMA,
    "checker_approval": APPROVAL_SCHEMA, "final_status": STATUS_SCHEMA,
    "dispatch": DISPATCH_SCHEMA, "provider_receipt": RECEIPT_SCHEMA,
    "control": CONTROL_SCHEMA, "collector": COLLECTOR_SCHEMA,
}
IDENTITY_SCHEMA = {
    "person_id": _text, "roles": _texts, "tenant": _text, "environment": _text,
    "valid_from": _integer, "valid_until": _integer,
}


class Checks:
    def __init__(self) -> None:
        self.invalid: list[str] = []
        self.unknown: list[str] = []
        self.refs: list[str] = []

    def require(self, condition: bool, reason: str) -> None:
        if not condition:
            self.invalid.append(reason)

    def available(self, condition: bool, reason: str) -> None:
        if not condition:
            self.unknown.append(reason)

    def result(self, success: str) -> dict:
        verdict = "INVALID" if self.invalid else "INDETERMINATE" if self.unknown else "VALID"
        return {"verdict": verdict, "reasons": sorted(set(self.invalid + self.unknown or [success])),
                "evidence_refs": sorted(set(self.refs))}


def _trust(trusted_keys: Any) -> dict:
    if type(trusted_keys) is not dict or set(trusted_keys) - set(ROLES.values()):
        raise ValueError("caller_trust_roles")
    result = {}
    for role, keys in trusted_keys.items():
        if type(keys) is not dict:
            raise ValueError("caller_trust_keys")
        result[role] = {}
        for key_id, public in keys.items():
            if not _text(key_id) or type(public) is not bytes or len(public) != 32:
                raise ValueError("caller_trust_key_shape")
            Ed25519PublicKey.from_public_bytes(public)
            result[role][key_id] = public
    return result


def _identities(identities: Any) -> dict:
    if type(identities) is not dict:
        raise ValueError("caller_identity_mapping")
    result = load_json(canonical_json(identities))
    for public_hex, body in result.items():
        if (re.fullmatch(r"[0-9a-f]{64}", public_hex) is None
                or not _shape(body, IDENTITY_SCHEMA)
                or body["valid_from"] >= body["valid_until"]):
            raise ValueError("caller_identity_shape")
    return result


def _record(name: str, evidence: dict, trust: dict, run_id: str,
            integrity: Checks) -> tuple[dict | None, bytes | None]:
    if name not in evidence:
        return None, None
    env = evidence[name]
    integrity.refs.append(digest(env))
    if (type(env) is not dict or set(env) != {"key_id", "payload", "signature"}
            or not _text(env.get("key_id")) or type(env.get("payload")) is not dict
            or type(env.get("signature")) is not str
            or re.fullmatch(r"[0-9a-f]{128}", env["signature"]) is None):
        integrity.invalid.append(name + ":envelope_shape")
        return None, None
    public = trust.get(ROLES[name], {}).get(env["key_id"])
    if public is None:
        integrity.unknown.append(name + ":no_caller_trusted_role_key")
        return None, None
    try:
        Ed25519PublicKey.from_public_bytes(public).verify(
            bytes.fromhex(env["signature"]), SIGNING_DOMAIN + canonical_json({
                "key_id": env["key_id"], "payload": env["payload"]}))
    except InvalidSignature:
        integrity.invalid.append(name + ":signature_invalid")
        return None, None
    body = env["payload"]
    schema = {**SCHEMAS[name], "kind": lambda x: x == name,
              "run_id": lambda x: x == run_id}
    if not _shape(body, schema):
        integrity.invalid.append(name + ":signed_payload_shape_or_context")
        return None, None
    return body, public


def _need(name: str, records: dict, evidence: dict, checks: Checks) -> dict | None:
    body = records[name]
    checks.available(body is not None, name + ":missing_or_unverifiable")
    if name in evidence:
        checks.refs.append(digest(evidence[name]))
    return body


def _bind(value: str, name: str, records: dict, evidence: dict,
          checks: Checks, label: str) -> None:
    checks.available(records[name] is not None, label + ":referent_unverifiable")
    if name in evidence:
        checks.refs.append(digest(evidence[name]))
    else:
        checks.unknown.append(label + ":referent_not_supplied")
    # A corrupted/untrusted replacement is not an authenticated contradiction
    # about the actual payment. Integrity reports its own failure separately.
    if records[name] is not None:
        checks.require(value == digest(evidence[name]), label + ":digest_mismatch")


def _window(start: int, end: int, at: int, checks: Checks, label: str) -> None:
    checks.require(start < end, label + ":invalid_window")
    checks.require(start <= at < end, label + ":outside_validity_window")


def _fresh(observed: int, at: int, max_age: int, checks: Checks, label: str) -> None:
    checks.available(observed <= at and at - observed <= max_age,
                     label + ":freshness_not_established")


def _dispatch_payload(dispatch: dict, operation: dict, checks: Checks) -> None:
    actual = dispatch["actual_operation"]
    checks.require(dispatch["operation_digest"] == digest(operation),
                   "dispatch:approved_operation_digest_mismatch")
    checks.require(actual == operation, "dispatch:actual_operation_mismatch")
    request = bytes.fromhex(dispatch["request_hex"])
    checks.require(bytes_digest(request) == actual["payload_digest"],
                   "dispatch:actual_payload_digest_mismatch")
    checks.require(bytes_digest(request) == operation["payload_digest"],
                   "dispatch:approved_payload_digest_mismatch")
    try:
        decoded = load_json(request)
        checks.require(canonical_json(decoded) == request, "dispatch:noncanonical_request")
        expected = load_json(synthetic_request_bytes(actual))
        checks.require(decoded == expected, "dispatch:request_semantics_mismatch")
    except (ValueError, TypeError, UnicodeError):
        checks.invalid.append("dispatch:request_encoding_invalid")


def _authorization(records: dict, keys: dict, evidence: dict, op: dict,
                   identities: dict, at: int, max_age: int) -> dict:
    c = Checks()
    d = _need("dispatch", records, evidence, c)
    if d is None:
        return c.result("actual_dispatch_authorization_supported")
    dispatched = d["dispatched_at"]
    c.available(dispatched <= at, "dispatch:after_evaluation_horizon")
    _dispatch_payload(d, op, c)
    actual = d["actual_operation"]
    _window(actual["valid_from"], actual["valid_until"], dispatched, c, "operation")
    c.require(bytes_digest(synthetic_request_bytes(op)) == op["payload_digest"],
              "operation:declared_payload_digest_mismatch")
    p = _need("policy", records, evidence, c)
    _bind(op["policy_digest"], "policy", records, evidence, c, "operation:policy")
    _bind(d["policy_digest"], "policy", records, evidence, c, "dispatch:policy")
    if p is not None:
        for field in ("tenant", "environment", "api_audience", "adapter", "principal_id",
                      "credential_id", "workload_id", "configuration_digest", "recovery_epoch",
                      "currency", "minor_unit_scale"):
            c.require(p[field] == actual[field], "policy:" + field + "_mismatch")
        c.require(actual["source_account"] in p["allowed_sources"], "policy:source_not_allowed")
        c.require(actual["beneficiary"] in p["allowed_beneficiaries"], "policy:beneficiary_not_allowed")
        c.require(int(actual["amount_minor"]) <= int(p["max_amount_minor"]), "policy:amount_exceeded")
        c.require(set(p["required_routes"]) == set(REQUIRED_ROUTES), "policy:required_route_scope_mismatch")
        _window(p["valid_from"], p["valid_until"], dispatched, c, "policy")
    approvals = {}
    persons = []
    for name, role in zip(APPROVALS, ("maker", "checker")):
        approval = _need(name, records, evidence, c)
        approvals[name] = approval
        _bind(d["approval_digests"][name], name, records, evidence, c, "dispatch:" + name)
        if approval is None:
            continue
        c.require(approval["operation_digest"] == digest(op), name + ":operation_digest_mismatch")
        c.require(approval["policy_digest"] == op["policy_digest"], name + ":policy_digest_mismatch")
        _window(approval["issued_at"], approval["expires_at"], dispatched, c, name)
        identity = identities.get(keys[name].hex())
        c.available(identity is not None, name + ":identity_mapping_missing")
        if identity is not None:
            persons.append(identity["person_id"])
            c.require(role in identity["roles"], name + ":ineligible_role")
            for field in ("tenant", "environment"):
                c.require(identity[field] == actual[field], name + ":identity_" + field + "_mismatch")
            _window(identity["valid_from"], identity["valid_until"], approval["issued_at"],
                    c, name + ":identity_at_issuance")
            _window(identity["valid_from"], identity["valid_until"], dispatched, c, name + ":identity")
    if len(persons) == 2:
        c.require(persons[0] != persons[1], "approvals:same_person")
    if all(approvals.values()):
        c.require(approvals[APPROVALS[0]]["approval_id"] != approvals[APPROVALS[1]]["approval_id"],
                  "approvals:duplicate_approval_id")
    status = _need("final_status", records, evidence, c)
    _bind(d["final_status_digest"], "final_status", records, evidence, c, "dispatch:final_status")
    if status is not None:
        c.require(status["operation_digest"] == digest(op), "final_status:operation_digest_mismatch")
        c.require(status["policy_digest"] == op["policy_digest"], "final_status:policy_digest_mismatch")
        for field in ("credential_id", "configuration_digest", "recovery_epoch"):
            c.require(status[field] == actual[field], "final_status:" + field + "_mismatch")
        for name in APPROVALS:
            _bind(status["approval_digests"][name], name, records, evidence, c, "final_status:" + name)
            if approvals[name] is not None:
                c.require(approvals[name]["issued_at"] <= status["checked_at"],
                          "final_status:precedes_" + name)
        c.require(status["checked_at"] < status["valid_until"], "final_status:invalid_window")
        _fresh(status["checked_at"], dispatched, max_age, c, "final_status")
        c.available(status["checked_at"] <= at, "final_status:after_evaluation_horizon")
        c.available(dispatched < status["valid_until"], "final_status:expired_snapshot")
        if status["state"] == "revoked":
            revoked = status["revoked_at"]
            c.require(revoked is not None, "final_status:revocation_time_missing")
            if revoked is not None:
                c.require(revoked <= status["checked_at"], "final_status:revocation_after_observation")
                c.require(revoked > dispatched, "final_status:revoked_before_dispatch")
                c.available(revoked <= dispatched, "final_status:historical_active_state_unknown")
        else:
            c.require(status["revoked_at"] is None, "final_status:unexpected_revocation_time")
            c.available(status["state"] == "active", "final_status:status_unknown")
    return c.result("authenticated_actual_dispatch_has_exact_scoped_approvals_at_dispatch_time")


def _execution(records: dict, evidence: dict, op: dict, at: int) -> tuple[dict, dict]:
    c = Checks()
    outcome = {"status": "unknown", "reported_status": None,
               "settlement_confirmed": False, "evidence_ref": None}
    d = _need("dispatch", records, evidence, c)
    receipt = _need("provider_receipt", records, evidence, c)
    if receipt is not None:
        outcome["reported_status"] = receipt["status"]
        outcome["evidence_ref"] = digest(evidence["provider_receipt"])
    if d is None:
        return c.result("authenticated_execution_and_provider_outcome_match"), outcome
    _dispatch_payload(d, op, c)
    c.available(d["dispatched_at"] <= at, "dispatch:after_evaluation_horizon")
    _bind(op["policy_digest"], "policy", records, evidence, c, "operation:policy")
    _bind(d["policy_digest"], "policy", records, evidence, c, "dispatch:policy")
    for name in APPROVALS:
        _bind(d["approval_digests"][name], name, records, evidence, c, "dispatch:" + name)
    _bind(d["final_status_digest"], "final_status", records, evidence, c, "dispatch:final_status")
    _bind(d["control_digest"], "control", records, evidence, c, "dispatch:control")
    if receipt is not None:
        c.require(receipt["operation_digest"] == digest(op), "provider_receipt:operation_digest_mismatch")
        c.require(receipt["payload_digest"] == op["payload_digest"], "provider_receipt:payload_digest_mismatch")
        c.require(receipt["api_audience"] == op["api_audience"], "provider_receipt:audience_mismatch")
        _bind(receipt["dispatch_digest"], "dispatch", records, evidence, c, "provider_receipt:dispatch")
        policy = _need("policy", records, evidence, c)
        if policy is not None:
            c.require(receipt["provider_id"] == policy["provider_id"], "provider_receipt:provider_mismatch")
        c.require(d["dispatched_at"] <= receipt["observed_at"], "provider_receipt:precedes_dispatch")
        c.available(receipt["observed_at"] <= at, "provider_receipt:after_evaluation_horizon")
        # Receipt outcome and execution correspondence are not a business-success flag.
        if not c.invalid and not c.unknown:
            outcome["status"] = receipt["status"]
        c.available(receipt["status"] in ("settled", "failed", "reversed"),
                    "provider_receipt:terminal_outcome_not_established")
    result = c.result("authenticated_request_and_terminal_provider_outcome_match_exact_operation")
    outcome["settlement_confirmed"] = result["verdict"] == "VALID" and outcome["status"] == "settled"
    return result, outcome


def _control(records: dict, evidence: dict, op: dict, at: int, max_age: int) -> dict:
    c = Checks()
    control = _need("control", records, evidence, c)
    collector = _need("collector", records, evidence, c)
    dispatch = _need("dispatch", records, evidence, c)
    policy = _need("policy", records, evidence, c)
    if dispatch is not None:
        # Route observations for the intended runtime cannot silently certify an
        # actual dispatch from another tenant, identity, workload or recovery.
        for field in ("tenant", "environment", "api_audience", "adapter", "principal_id",
                      "credential_id", "workload_id", "configuration_digest", "recovery_epoch"):
            c.require(dispatch["actual_operation"][field] == op[field],
                      "control:actual_" + field + "_scope_mismatch")
    if policy is not None:
        _bind(op["policy_digest"], "policy", records, evidence, c, "control:policy")
        c.require(set(policy["required_routes"]) == set(REQUIRED_ROUTES), "policy:required_route_scope_mismatch")
    if control is not None:
        c.require(control["operation_digest"] == digest(op), "control:operation_digest_mismatch")
        for field in ("configuration_digest", "recovery_epoch"):
            c.require(control[field] == op[field], "control:" + field + "_mismatch")
        c.available(control["observed_at"] <= at, "control:after_evaluation_horizon")
        if dispatch is not None:
            _fresh(control["observed_at"], dispatch["dispatched_at"], max_age, c, "control")
            _bind(dispatch["control_digest"], "control", records, evidence, c, "dispatch:control")
            c.available(dispatch["dispatched_at"] <= at, "dispatch:after_evaluation_horizon")
        for route, expected in REQUIRED_ROUTES.items():
            state = control["routes"].get(route)
            if state is None or state == "unobserved":
                c.unknown.append("control:" + route + "_not_observed")
            else:
                c.require(state == expected, "control:" + route + "_violated")
        for extra in set(control["routes"]) - set(REQUIRED_ROUTES):
            c.unknown.append("control:additional_route_not_in_supported_scope:" + extra)
    if collector is not None:
        c.require(collector["operation_digest"] == digest(op), "collector:operation_digest_mismatch")
        for field in ("configuration_digest", "recovery_epoch"):
            c.require(collector[field] == op[field], "collector:" + field + "_mismatch")
        c.available(collector["checkpoint_at"] <= at, "collector:after_evaluation_horizon")
        c.available(not collector["gaps"], "collector:declared_collection_gap")
        retained = collector["retained"]
        for name in set(ROLES) - {"collector"}:
            c.available(name in retained, "collector:" + name + "_retention_not_asserted")
            c.available(records[name] is not None, "collector:" + name + "_evidence_unverifiable")
        for name, ref in retained.items():
            if name not in evidence or name == "collector":
                c.unknown.append("collector:retained_reference_not_supplied:" + name)
                continue
            c.refs.append(digest(evidence[name]))
            body = records.get(name)
            if body is not None:
                c.require(ref == digest(evidence[name]), "collector:" + name + "_digest_mismatch")
                time_field = {
                    "maker_approval": "issued_at", "checker_approval": "issued_at",
                    "final_status": "checked_at", "dispatch": "dispatched_at",
                    "provider_receipt": "observed_at", "control": "observed_at",
                }.get(name)
                if time_field:
                    c.require(body[time_field] <= collector["checkpoint_at"],
                              "collector:checkpoint_precedes_" + name)
    return c.result("named_routes_and_retained_supplied_records_match_at_declared_times_only")


def verify_bundle(bundle: dict, trusted_keys: dict, *, identities: dict,
                  evaluation_time: int, max_snapshot_age: int = 300) -> dict:
    """Read-only retrospective assessment with caller-owned trust, identity and time.

    Repetition consumes no nonce and changes no state. A missing provider response
    stays unknown. No return value authorizes dispatch or retry of a payment.
    """
    trust = _trust(trusted_keys)
    identity_map = _identities(identities)
    if not _integer(evaluation_time) or not _integer(max_snapshot_age) or max_snapshot_age == 0:
        raise ValueError("caller_time_or_freshness_limit")
    result = {"schema": RESULT_SCHEMA, "synthetic": True, "read_only": True,
              "automatic_retry": False, "evaluation_time": evaluation_time,
              "claims": {}, "outcome": {"status": "unknown", "reported_status": None,
                  "settlement_confirmed": False, "evidence_ref": None},
              "limitations": [
                  "synthetic_evidence_semantics_only_not_bank_execution_or_VAP_conformance",
                  "caller_supplies_role_keys_person_mapping_and_evaluation_clock",
                  "signatures_do_not_establish_truth_independence_or_complete_collection",
                  "authorization_is_retrospective_at_authenticated_dispatch_time",
                  "no_live_enforcement_atomic_check_to_execution_or_continuous_revocation",
                  "only_the_named_synthetic_request_encoding_is_decoded",
                  "provider_outcomes_are_trusted_statements_not_independent_bank_observation",
                  "control_scope_is_named_routes_and_times_not_every_privileged_route",
                  "no_consumption_ledger_duplicate_suppression_or_automatic_write_retry",
                  "no_collector_outage_or_recovery_system_was_exercised",
                  "unobserved_actions_and_complete_eradication_remain_unknown",
              ]}
    try:
        bundle = load_json(canonical_json(bundle))
        if (type(bundle) is not dict or set(bundle) != {
                "schema", "synthetic", "run_id", "operation", "evidence"}
                or bundle["schema"] != BUNDLE_SCHEMA or bundle["synthetic"] is not True
                or not _text(bundle["run_id"])):
            raise ValueError("bundle_shape_or_scope")
        evidence = bundle["evidence"]
        if type(evidence) is not dict or set(evidence) - set(ROLES):
            raise ValueError("evidence_slots")
        validate_operation(bundle["operation"])
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        result["claims"] = {name: {"verdict": "INVALID" if name == "integrity" else "INDETERMINATE",
                                   "reasons": ["bundle_unusable:" + str(exc)], "evidence_refs": []}
                            for name in CLAIMS}
        return result
    op, run_id = bundle["operation"], bundle["run_id"]
    result["run_id"] = run_id
    result["operation_digest"] = digest(op)
    integrity = Checks()
    records, keys = {}, {}
    for name in ROLES:
        records[name], keys[name] = _record(name, evidence, trust, run_id, integrity)
    integrity.available(bool(evidence), "no_supplied_evidence")
    result["claims"]["integrity"] = integrity.result(
        "all_supplied_record_signatures_shapes_and_run_bindings_verify_not_completeness")
    # A future-dated statement may have a correct signature but cannot support a
    # retrospective proposition as of the caller's evaluation horizon.
    observed_fields = {
        "maker_approval": "issued_at", "checker_approval": "issued_at",
        "final_status": "checked_at", "dispatch": "dispatched_at",
        "provider_receipt": "observed_at", "control": "observed_at",
        "collector": "checkpoint_at",
    }
    result["excluded_after_horizon"] = []
    for name, field in observed_fields.items():
        if records[name] is not None and records[name][field] > evaluation_time:
            result["excluded_after_horizon"].append({
                "record": name, "evidence_ref": digest(evidence[name]),
                "recorded_time": records[name][field]})
            records[name] = None
    result["claims"]["authorization"] = _authorization(
        records, keys, evidence, op, identity_map, evaluation_time, max_snapshot_age)
    result["claims"]["execution_match"], result["outcome"] = _execution(
        records, evidence, op, evaluation_time)
    result["claims"]["control_state"] = _control(
        records, evidence, op, evaluation_time, max_snapshot_age)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--trust", required=True, type=Path)
    parser.add_argument("--identities", required=True, type=Path)
    parser.add_argument("--at", required=True, type=int)
    parser.add_argument("--max-snapshot-age", default=300, type=int)
    args = parser.parse_args()
    try:
        bundle = load_json(args.bundle.read_bytes())
        raw_trust = load_json(args.trust.read_bytes())
        trust = {role: {key_id: bytes.fromhex(public) for key_id, public in keys.items()}
                 for role, keys in raw_trust.items()}
        identities = load_json(args.identities.read_bytes())
        report = verify_bundle(bundle, trust, identities=identities,
                               evaluation_time=args.at, max_snapshot_age=args.max_snapshot_age)
    except (OSError, ValueError, TypeError, AttributeError, UnicodeError) as exc:
        parser.error(str(exc))
    print(canonical_json(report).decode("utf-8"))
    return 0 if all(x["verdict"] == "VALID" for x in report["claims"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
