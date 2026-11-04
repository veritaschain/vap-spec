"""Offline, synthetic wallet evidence experiment; not a wallet or production gate.

Trust anchors and the evaluation time come from the caller, never the bundle.
Ed25519 signs evidence only. No private wallet key, RPC, network or transaction
submission is used. See README.md for the precise scope of every verdict.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey,
)


BUNDLE_SCHEMA = "experimental-wallet-authorization-bundle-v0"
RESULT_SCHEMA = "experimental-wallet-authorization-evidence-v0"
SIGNING_DOMAIN = b"VSO experimental wallet evidence v0\x00"
ROLES = {
    "policy": "policy_authority",
    "approval": "approval_authority",
    "final_revocation": "revocation_authority",
    "control_observation": "control_observer",
    "execution": "execution_observer",
    "chain_observation": "chain_observer",
}
CLAIMS = ("integrity", "authorization", "execution_match", "delegation_state")
HEX = re.compile(r"0x(?:[0-9a-f]{2})*\Z")
ADDRESS = re.compile(r"0x[0-9a-f]{40}\Z")
HASH = re.compile(r"sha256:[0-9a-f]{64}\Z")
BLOCK_HASH = re.compile(r"0x[0-9a-f]{64}\Z")
DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)\Z")
ZERO_ADDRESS = "0x" + "00" * 20
OPERATION_FIELDS = {
    "operation_id", "actor_id", "credential_id", "workload_id",
    "deployment_digest", "chain_id", "wallet", "action", "asset", "amount",
    "destination", "calldata", "delegation_target", "nonce",
    "signing_payload_digest", "policy_digest",
}


def _json_value(value: Any, depth: int = 0) -> None:
    """Restricted JSON domain, deliberately not a claim of RFC 8785 support."""
    if depth > 64:
        raise ValueError("json_nesting_limit")
    if value is None or type(value) is bool:
        return
    if type(value) is int:
        if abs(value) > 9007199254740991:
            raise ValueError("unsafe_json_integer_use_decimal_string")
        return
    if type(value) is str:
        if unicodedata.normalize("NFC", value) != value:
            raise ValueError("non_nfc_string")
        value.encode("utf-8", errors="strict")
        return
    if type(value) is list:
        for child in value:
            _json_value(child, depth + 1)
        return
    if type(value) is dict:
        for key, child in value.items():
            if type(key) is not str:
                raise ValueError("non_string_json_key")
            _json_value(key, depth + 1)
            _json_value(child, depth + 1)
        return
    raise ValueError("unsupported_json_type")


def canonical_json(value: Any) -> bytes:
    _json_value(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


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
    try:
        value = json.loads(raw, object_pairs_hook=_unique_pairs,
                           parse_float=_no_float, parse_constant=_no_float)
    except RecursionError as exc:
        raise ValueError("json_nesting_limit") from exc
    canonical_json(value)
    return value


def digest(value: Any) -> str:
    return bytes_digest(canonical_json(value))


def bytes_digest(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def sign_envelope(payload: dict, key_id: str,
                  private_key: Ed25519PrivateKey) -> dict:
    """Test helper: signs an evidence statement, never a blockchain transaction."""
    signed = {"key_id": key_id, "payload": load_json(canonical_json(payload))}
    return {**signed, "signature": private_key.sign(
        SIGNING_DOMAIN + canonical_json(signed)).hex()}


def _exact(value: Any, fields: set[str]) -> bool:
    return type(value) is dict and set(value) == fields


def _text(value: Any) -> bool:
    return type(value) is str and bool(value) and len(value) <= 4096


def _match(pattern: re.Pattern, value: Any) -> bool:
    return type(value) is str and pattern.fullmatch(value) is not None


def _integer(value: Any) -> bool:
    return type(value) is int and 0 <= value <= 9007199254740991


def _texts(value: Any) -> bool:
    return type(value) is list and all(_text(x) for x in value) and len(value) == len(set(value))


def validate_operation(operation: dict) -> None:
    if not _exact(operation, OPERATION_FIELDS):
        raise ValueError("operation_fields")
    for field in ("operation_id", "actor_id", "credential_id", "workload_id"):
        if not _text(operation[field]):
            raise ValueError("operation_identity_shape")
    for field in ("deployment_digest", "signing_payload_digest", "policy_digest"):
        if not _match(HASH, operation[field]):
            raise ValueError("operation_digest_shape")
    for field in ("chain_id", "amount", "nonce"):
        if not _match(DECIMAL, operation[field]) or len(operation[field]) > 78:
            raise ValueError("operation_decimal_shape")
    if operation["chain_id"] == "0":
        raise ValueError("chain_id_zero_not_supported")
    for field in ("wallet", "destination"):
        if not _match(ADDRESS, operation[field]):
            raise ValueError("operation_address_shape")
    if operation["asset"] != "native" and not _match(ADDRESS, operation["asset"]):
        raise ValueError("operation_asset_shape")
    if not _match(HEX, operation["calldata"]):
        raise ValueError("operation_calldata_shape")
    action, target = operation["action"], operation["delegation_target"]
    if action not in ("transfer", "delegate", "clear_delegation"):
        raise ValueError("operation_action")
    if action == "transfer" and target is not None:
        raise ValueError("transfer_cannot_assert_delegation_transition")
    if action == "delegate" and (not _match(ADDRESS, target) or target == ZERO_ADDRESS):
        raise ValueError("delegate_target")
    if action == "clear_delegation" and target != ZERO_ADDRESS:
        raise ValueError("clear_delegation_target")


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
        reasons = self.invalid + self.unknown or [success]
        return {"verdict": verdict, "evidence_refs": sorted(set(self.refs)),
                "reasons": sorted(set(reasons))}


def _trust(trusted_keys: dict) -> dict:
    if type(trusted_keys) is not dict or set(trusted_keys) - set(ROLES.values()):
        raise ValueError("caller_trust_roles")
    copied = {}
    for role, keys in trusted_keys.items():
        if type(keys) is not dict:
            raise ValueError("caller_trust_keys")
        copied[role] = {}
        for key_id, public in keys.items():
            if not _text(key_id) or type(public) is not bytes or len(public) != 32:
                raise ValueError("caller_trust_key_shape")
            Ed25519PublicKey.from_public_bytes(public)
            copied[role][key_id] = public
    return copied


def _record(name: str, evidence: dict, trust: dict, integrity: Checks) -> tuple[dict | None, bytes | None]:
    env = evidence.get(name)
    if env is None:
        return None, None
    ref = digest(env)
    integrity.refs.append(ref)
    if not _exact(env, {"key_id", "payload", "signature"}) or not _text(env.get("key_id")) or type(env.get("payload")) is not dict:
        integrity.invalid.append(name + ":envelope_shape")
        return None, None
    signature = env["signature"]
    if type(signature) is not str or re.fullmatch(r"[0-9a-f]{128}", signature) is None:
        integrity.invalid.append(name + ":signature_encoding")
        return None, None
    public = trust.get(ROLES[name], {}).get(env["key_id"])
    if public is None:
        integrity.unknown.append(name + ":no_caller_trusted_role_key")
        return None, None
    try:
        Ed25519PublicKey.from_public_bytes(public).verify(bytes.fromhex(signature),
            SIGNING_DOMAIN + canonical_json({"key_id": env["key_id"], "payload": env["payload"]}))
    except InvalidSignature:
        integrity.invalid.append(name + ":signature_invalid")
        return None, None
    return env["payload"], public


def _body(records: dict, name: str, fields: set[str], run_id: str,
          checks: Checks, evidence: dict) -> dict | None:
    body = records[name]
    if body is None:
        checks.unknown.append(name + ":missing_or_unverifiable")
        return None
    checks.refs.append(digest(evidence[name]))
    if not _exact(body, fields | {"kind", "run_id"}):
        checks.invalid.append(name + ":signed_payload_schema")
        return None
    checks.require(body["kind"] == name, name + ":kind_mismatch")
    checks.require(body["run_id"] == run_id, name + ":run_mismatch")
    return body


POLICY_FIELDS = {
    "policy_id", "version", "actor_id", "credential_id", "allowed_chains",
    "allowed_wallets", "allowed_actions", "allowed_assets", "allowed_destinations",
    "allowed_delegation_targets", "max_amount", "workload_id", "deployment_digest",
    "valid_from", "valid_until", "required_finality", "required_routes",
}
APPROVAL_FIELDS = {"approval_id", "approver_id", "actor_id", "credential_id",
                   "operation_digest", "policy_digest", "issued_at", "expires_at"}
REVOCATION_FIELDS = {"snapshot_id", "operation_digest", "policy_digest", "approval_digest",
                     "checked_at", "valid_until", "revoked_credentials", "revoked_approvals"}
CONTROL_FIELDS = {"operation_digest", "workload_id", "deployment_digest", "observed_at",
                   "observation_boundary", "routes"}
EXECUTION_FIELDS = {"operation_digest", "policy_digest", "approval_digest", "revocation_digest",
                     "control_digest", "actual_operation", "signing_payload", "state", "observed_at"}
CHAIN_FIELDS = {"operation_digest", "execution_digest", "chain_id", "wallet", "observed_at",
                 "block_number", "block_hash", "transaction_hash", "transaction_block_number",
                 "transaction_block_hash", "receipt_status", "delegation_code", "finality"}


def _window(body: dict, start: str, end: str, at: int, checks: Checks, label: str) -> None:
    valid = _integer(body[start]) and _integer(body[end]) and body[start] < body[end]
    checks.require(valid, label + ":time_shape")
    if valid:
        checks.require(body[start] <= at < body[end], label + ":outside_validity_window")


def _fresh(body: dict, start: str, at: int, max_age: int, checks: Checks, label: str) -> None:
    checks.require(_integer(body[start]), label + ":time_shape")
    if _integer(body[start]):
        checks.available(body[start] <= at and at - body[start] <= max_age,
                         label + ":freshness_not_established")


def _authorization(records: dict, evidence: dict, op: dict, run_id: str,
                   at: int, max_age: int) -> tuple[dict, dict]:
    c = Checks()
    p = _body(records, "policy", POLICY_FIELDS, run_id, c, evidence)
    a = _body(records, "approval", APPROVAL_FIELDS, run_id, c, evidence)
    r = _body(records, "final_revocation", REVOCATION_FIELDS, run_id, c, evidence)
    control = _body(records, "control_observation", CONTROL_FIELDS, run_id, c, evidence)
    op_digest = digest(op)
    if p is not None:
        c.require(op["policy_digest"] == digest(p), "policy:digest_mismatch")
        for field in ("policy_id", "version", "actor_id", "credential_id", "workload_id"):
            c.require(_text(p[field]), "policy:identity_shape")
        for field in ("actor_id", "credential_id", "workload_id", "deployment_digest"):
            c.require(p[field] == op[field], "policy:" + field + "_mismatch")
        for field, allowed in (("chain_id", "allowed_chains"), ("wallet", "allowed_wallets"),
                               ("action", "allowed_actions"), ("asset", "allowed_assets"),
                               ("destination", "allowed_destinations")):
            c.require(_texts(p[allowed]) and op[field] in p[allowed], "policy:" + field + "_not_allowed")
        c.require(_texts(p["allowed_delegation_targets"]), "policy:delegation_target_list_shape")
        if op["delegation_target"] is not None:
            c.require(type(p["allowed_delegation_targets"]) is list and
                      op["delegation_target"] in p["allowed_delegation_targets"], "policy:delegation_target_not_allowed")
        amount_valid = _match(DECIMAL, p["max_amount"]) and len(p["max_amount"]) <= 78
        c.require(amount_valid, "policy:max_amount_shape")
        if amount_valid:
            c.require(int(op["amount"]) <= int(p["max_amount"]), "policy:amount_exceeded")
        c.require(p["required_finality"] in ("observed_block", "finalized"), "policy:finality_shape")
        c.require(_texts(p["required_routes"]) and set(p["required_routes"]) ==
                  {"approved_gate", "direct_signer", "deployment_signer"}, "policy:route_scope_shape")
        _window(p, "valid_from", "valid_until", at, c, "policy")
    if a is not None:
        for field in ("approval_id", "approver_id"):
            c.require(_text(a[field]), "approval:identity_shape")
        for field in ("actor_id", "credential_id"):
            c.require(a[field] == op[field], "approval:" + field + "_mismatch")
        c.require(a["operation_digest"] == op_digest, "approval:operation_digest_mismatch")
        c.require(a["policy_digest"] == op["policy_digest"], "approval:policy_digest_mismatch")
        _window(a, "issued_at", "expires_at", at, c, "approval")
    if r is not None:
        c.require(_text(r["snapshot_id"]), "revocation:snapshot_id_shape")
        c.require(r["operation_digest"] == op_digest, "revocation:operation_digest_mismatch")
        c.require(r["policy_digest"] == op["policy_digest"], "revocation:policy_digest_mismatch")
        if a is not None:
            c.require(r["approval_digest"] == digest(a), "revocation:approval_digest_mismatch")
            if _integer(r["checked_at"]) and _integer(a["issued_at"]):
                c.require(r["checked_at"] >= a["issued_at"], "revocation:snapshot_precedes_approval")
        _fresh(r, "checked_at", at, max_age, c, "revocation")
        time_shape = _integer(r["valid_until"]) and _integer(r["checked_at"]) and r["checked_at"] < r["valid_until"]
        c.require(time_shape, "revocation:time_shape")
        if time_shape:
            c.available(at < r["valid_until"], "revocation:expired_snapshot")
        for field in ("revoked_credentials", "revoked_approvals"):
            c.require(_texts(r[field]), "revocation:list_shape")
        if type(r["revoked_credentials"]) is list:
            c.require(op["credential_id"] not in r["revoked_credentials"], "revocation:credential_revoked")
        if a is not None and type(r["revoked_approvals"]) is list:
            c.require(a["approval_id"] not in r["revoked_approvals"], "revocation:approval_revoked")
    if control is not None:
        c.require(control["operation_digest"] == op_digest, "control:operation_digest_mismatch")
        for field in ("workload_id", "deployment_digest"):
            c.require(control[field] == op[field], "control:" + field + "_mismatch")
        c.require(_text(control["observation_boundary"]), "control:boundary_missing")
        _fresh(control, "observed_at", at, max_age, c, "control")
        routes = control["routes"]
        expected = {"approved_gate": "recorded", "direct_signer": "blocked", "deployment_signer": "blocked"}
        if type(routes) is not dict or set(routes) != set(expected):
            c.unknown.append("control:route_coverage_incomplete")
        else:
            for route, required in expected.items():
                status = routes[route]
                if status == "unobserved":
                    c.unknown.append("control:" + route + "_unobserved")
                else:
                    c.require(status == required, "control:" + route + "_violated")
    return c.result("exact_intent_authorized_at_caller_time_with_scoped_control_evidence"), {
        "policy": p, "approval": a, "final_revocation": r, "control_observation": control}


def _execution(records: dict, evidence: dict, op: dict, run_id: str,
               at: int, max_age: int, bodies: dict) -> tuple[dict, dict | None]:
    c = Checks()
    e = _body(records, "execution", EXECUTION_FIELDS, run_id, c, evidence)
    if e is None:
        return c.result("execution_matches"), None
    c.require(e["operation_digest"] == digest(op), "execution:operation_digest_mismatch")
    c.require(e["policy_digest"] == op["policy_digest"], "execution:policy_digest_mismatch")
    for body_name, field in (("approval", "approval_digest"), ("final_revocation", "revocation_digest"),
                              ("control_observation", "control_digest")):
        body = bodies[body_name]
        c.available(body is not None, "execution:" + body_name + "_unverifiable")
        if body is not None:
            c.require(e[field] == digest(body), "execution:" + field + "_mismatch")
    try:
        validate_operation(e["actual_operation"])
        c.require(digest(e["actual_operation"]) == digest(op), "execution:actual_operation_mismatch")
    except (ValueError, TypeError):
        c.invalid.append("execution:actual_operation_shape")
    valid_payload = _match(HEX, e["signing_payload"])
    c.require(valid_payload, "execution:signing_payload_shape")
    if valid_payload:
        c.require(bytes_digest(bytes.fromhex(e["signing_payload"][2:])) == op["signing_payload_digest"],
                  "execution:signing_payload_digest_mismatch")
    c.require(e["state"] in ("signed", "broadcast", "included", "offchain_stopped", "unknown", "not_observed"),
              "execution:state_shape")
    c.available(e["state"] in ("signed", "broadcast", "included"), "execution:signing_not_observed")
    c.require(_integer(e["observed_at"]), "execution:time_shape")
    if _integer(e["observed_at"]):
        c.available(e["observed_at"] <= at, "execution:future_observation")
        r = bodies["final_revocation"]
        if r is not None and _integer(r["checked_at"]) and _integer(r["valid_until"]):
            c.require(r["checked_at"] <= e["observed_at"] < r["valid_until"],
                      "execution:outside_final_revocation_window")
            c.available(e["observed_at"] - r["checked_at"] <= max_age,
                        "execution:revocation_freshness_not_established")
        control = bodies["control_observation"]
        if control is not None and _integer(control["observed_at"]):
            c.require(control["observed_at"] <= e["observed_at"],
                      "execution:control_observation_follows_execution")
            c.available(e["observed_at"] - control["observed_at"] <= max_age,
                        "execution:control_freshness_not_established")
        for name, start, end in (("policy", "valid_from", "valid_until"), ("approval", "issued_at", "expires_at")):
            if bodies[name] is not None:
                _window(bodies[name], start, end, e["observed_at"], c, "execution:" + name)
    return c.result("signed_observer_binds_exact_declared_operation_and_exact_payload_bytes"), e


def _chain(records: dict, evidence: dict, op: dict, run_id: str, at: int,
           policy: dict | None, execution: dict | None, public: bytes | None, trust: dict) -> dict:
    c = Checks()
    b = _body(records, "chain_observation", CHAIN_FIELDS, run_id, c, evidence)
    if b is None:
        return c.result("delegation_state_matches")
    other_keys = {key for role, keys in trust.items() if role != "chain_observer" for key in keys.values()}
    c.available(public is not None and public not in other_keys, "chain:independent_observer_key_not_established")
    c.require(b["operation_digest"] == digest(op), "chain:operation_digest_mismatch")
    c.require(b["chain_id"] == op["chain_id"], "chain:chain_id_mismatch")
    c.require(b["wallet"] == op["wallet"], "chain:wallet_mismatch")
    c.require(_integer(b["observed_at"]), "chain:observation_time_shape")
    if _integer(b["observed_at"]):
        c.available(b["observed_at"] <= at, "chain:future_observation")
        if execution is not None and _integer(execution["observed_at"]):
            c.require(b["observed_at"] >= execution["observed_at"], "chain:observation_precedes_execution")
    c.available(execution is not None, "chain:execution_binding_unavailable")
    if execution is not None:
        c.require(b["execution_digest"] == digest(execution), "chain:execution_digest_mismatch")
        c.available(execution["state"] in ("broadcast", "included"), "chain:submission_not_observed")
    context = _match(DECIMAL, b["block_number"]) and len(b["block_number"]) <= 78 and _match(BLOCK_HASH, b["block_hash"])
    c.require(context, "chain:block_context_shape")
    c.require(b["receipt_status"] in ("success", "reverted", "missing"), "chain:receipt_status_shape")
    c.require(b["finality"] in ("observed_block", "finalized", "unknown"), "chain:finality_shape")
    c.require(_match(HEX, b["delegation_code"]), "chain:code_shape")
    if policy is None:
        c.unknown.append("chain:required_finality_unavailable")
    else:
        sufficient = b["finality"] == "finalized" or (
            b["finality"] == "observed_block" and policy["required_finality"] == "observed_block")
        c.available(sufficient, "chain:required_finality_not_observed")
    tx_fields = (b["transaction_hash"], b["transaction_block_number"], b["transaction_block_hash"])
    if all(x is None for x in tx_fields):
        c.unknown.append("chain:transaction_inclusion_unobserved")
    else:
        inclusion = (_match(BLOCK_HASH, tx_fields[0]) and _match(DECIMAL, tx_fields[1]) and
                     len(tx_fields[1]) <= 78 and _match(BLOCK_HASH, tx_fields[2]))
        c.require(inclusion, "chain:transaction_context_shape")
        if context and inclusion:
            c.require(int(b["block_number"]) >= int(tx_fields[1]), "chain:state_block_precedes_inclusion")
            if b["block_number"] == tx_fields[1]:
                c.require(b["block_hash"] == tx_fields[2], "chain:inclusion_block_hash_mismatch")
            elif int(b["block_number"]) > int(tx_fields[1]):
                c.unknown.append("chain:later_block_ancestry_not_proven_in_v0")
    # EIP-7702 authorization processing can persist despite a later execution
    # revert. A receipt's success bit is not the delegation-state proposition.
    # State is established only by the separately observed code at this block.
    if op["action"] == "transfer":
        c.unknown.append("chain:operation_does_not_request_delegation_transition")
    elif _match(HEX, b["delegation_code"]):
        expected = "0x" if op["action"] == "clear_delegation" else "0xef0100" + op["delegation_target"][2:]
        c.require(b["delegation_code"] == expected, "chain:requested_delegation_state_contradicted")
    return c.result("requested_delegation_code_observed_at_bound_block_and_required_finality")


def admission_decision(report: dict) -> str:
    """Illustrative evidence acceptance, ONLY for an independently verified report.

    This function is not an authorizer or execution control. A caller can forge a
    dict. It must call verify_bundle with its own trust/time first. ALLOW means
    that this experimental report has four VALID claims; it executes nothing.
    """
    if report.get("schema") != RESULT_SCHEMA or report.get("synthetic") is not True:
        return "DENY"
    claims = report.get("claims", {})
    if type(claims) is not dict or set(claims) != set(CLAIMS):
        return "DENY"
    return "ALLOW" if all(type(claims[name]) is dict and claims[name].get("verdict") == "VALID"
                          for name in CLAIMS) else "DENY"


def verify_bundle(bundle: dict, trusted_keys: dict, *, evaluation_time: int,
                  max_snapshot_age: int = 300) -> dict:
    """Verify offline at caller-supplied time; neither trust nor time is inferred."""
    trust = _trust(trusted_keys)
    if not _integer(evaluation_time) or not _integer(max_snapshot_age) or max_snapshot_age == 0:
        raise ValueError("caller_evaluation_time_or_max_age")
    result = {"schema": RESULT_SCHEMA, "synthetic": True, "evaluation_time": evaluation_time,
              "claims": {}, "limitations": [
                  "synthetic_experiment_not_DAP_adoption_or_VAP_conformance",
                  "no_network_no_transaction_signing_or_submission_no_live_enforcement",
                  "trust_keys_and_time_are_external_caller_inputs",
                  "valid_integrity_does_not_prove_evidence_completeness_or_authorization",
                  "control_observations_cover_named_routes_and_observation_time_only",
                  "privileged_deployment_controller_is_outside_the_trust_boundary",
                  "no_atomic_check_to_execution_binding_or_continuous_revocation_guarantee",
                  "payload_digest_binds_exact_bytes_not_universal_Ethereum_semantic_decoding",
                  "chain_state_is_an_observer_statement_at_a_block_not_current_or_global_truth",
                  "v0_requires_same_state_and_inclusion_block_no_ancestry_or_reorg_proof",
                  "no_automatic_resigning_rebroadcast_or_retry_on_unknown_outcome",
              ]}
    try:
        bundle = load_json(canonical_json(bundle))  # Own immutable snapshot of caller data.
        if not _exact(bundle, {"schema", "synthetic", "run_id", "operation", "evidence"}):
            raise ValueError("bundle_fields")
        if bundle["schema"] != BUNDLE_SCHEMA or bundle["synthetic"] is not True or not _text(bundle["run_id"]):
            raise ValueError("bundle_schema_or_scope")
        if type(bundle["evidence"]) is not dict or set(bundle["evidence"]) - set(ROLES):
            raise ValueError("evidence_fields")
        validate_operation(bundle["operation"])
    except (ValueError, TypeError, UnicodeError) as exc:
        result["claims"] = {name: {"verdict": "INVALID" if name == "integrity" else "INDETERMINATE",
                                   "evidence_refs": [], "reasons": ["bundle_unusable:" + str(exc)]}
                            for name in CLAIMS}
        result["admission"] = "DENY"
        return result
    result["run_id"] = bundle["run_id"]
    result["operation_digest"] = digest(bundle["operation"])
    evidence, op, run_id = bundle["evidence"], bundle["operation"], bundle["run_id"]
    integrity = Checks()
    records, keys = {}, {}
    for name in ROLES:
        records[name], keys[name] = _record(name, evidence, trust, integrity)
    integrity.available(bool(integrity.refs), "no_supplied_signed_evidence")
    result["claims"]["integrity"] = integrity.result("all_supplied_evidence_signatures_verified_completeness_not_established")
    auth, bodies = _authorization(records, evidence, op, run_id, evaluation_time, max_snapshot_age)
    result["claims"]["authorization"] = auth
    executed, execution = _execution(records, evidence, op, run_id, evaluation_time, max_snapshot_age, bodies)
    result["claims"]["execution_match"] = executed
    result["claims"]["delegation_state"] = _chain(records, evidence, op, run_id, evaluation_time,
        bodies["policy"], execution, keys["chain_observation"], trust)
    result["admission"] = admission_decision(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--trust", required=True, type=Path)
    parser.add_argument("--at", required=True, type=int)
    parser.add_argument("--max-snapshot-age", default=300, type=int)
    args = parser.parse_args()
    try:
        bundle = load_json(args.bundle.read_bytes())
        raw_trust = load_json(args.trust.read_bytes())
        trust = {role: {key_id: bytes.fromhex(public) for key_id, public in keys.items()}
                 for role, keys in raw_trust.items()}
        report = verify_bundle(bundle, trust, evaluation_time=args.at, max_snapshot_age=args.max_snapshot_age)
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        parser.error(str(exc))
    print(canonical_json(report).decode("utf-8"))
    return 0 if report["admission"] == "ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
