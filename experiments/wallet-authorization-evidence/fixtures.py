"""Deterministic synthetic evidence fixtures. ALL signing seeds are PUBLIC TEST DATA.

Never import these keys into a service, wallet, trust store or production system.
The signatures authenticate deliberately synthetic statements, not real facts.
"""
from __future__ import annotations

import copy
import hashlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from wallet_evidence import (BUNDLE_SCHEMA, ROLES, ZERO_ADDRESS, bytes_digest,
                             canonical_json, digest, sign_envelope)


DEFAULT_AT = 1804723200
WALLET = "0x" + "11" * 20
DESTINATION = "0x" + "22" * 20
ALTERNATE_DESTINATION = "0x" + "33" * 20
DELEGATE = "0x" + "44" * 20
CASES = ("authorized", "approval_mismatch", "missing_approval", "stop_with_delegation",
         "clear_observed", "deployment_bypass", "unknown_controller", "credential_revoked")


def fixture_key(role: str) -> Ed25519PrivateKey:
    if role not in ROLES.values():
        raise ValueError("unknown_fixture_role")
    seed = hashlib.sha256(("PUBLIC SYNTHETIC TEST SEED ONLY / " + role).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def fixture_trust() -> dict:
    return {role: {"synthetic-" + role: fixture_key(role).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)} for role in ROLES.values()}


def resign(bundle: dict, evidence_name: str, payload: dict) -> None:
    """Mutate one fixture envelope with a PUBLIC test key; does not repair bindings."""
    role = ROLES[evidence_name]
    bundle["evidence"][evidence_name] = sign_envelope(payload, "synthetic-" + role, fixture_key(role))


def fixture_signing_bytes(operation: dict) -> bytes:
    """Synthetic intent bytes, explicitly NOT an Ethereum transaction encoding."""
    return canonical_json({"domain": "synthetic-wallet-intent-v0", "operation": {
        key: value for key, value in operation.items() if key != "signing_payload_digest"}})


def rebind_fixture(bundle: dict, *, operation_updates: dict | None = None,
                   policy_updates: dict | None = None, execution_updates: dict | None = None,
                   chain_updates: dict | None = None) -> None:
    """Rebuild a FULL synthetic approval chain after intentionally changing a fixture.

    This helper creates new authority statements, not evidence of an existing
    approval. It must NEVER be used to 'repair' evidence from an incident.
    A supplied execution_updates['signing_payload'] is hex and is bound exactly.
    """
    evidence = bundle["evidence"]
    p = copy.deepcopy(evidence["policy"]["payload"])
    p.update(policy_updates or {})
    bundle["operation"].update(operation_updates or {})
    op = bundle["operation"]
    op["policy_digest"] = digest(p)
    payload = (execution_updates or {}).get("signing_payload")
    if payload is None:
        payload = "0x" + fixture_signing_bytes(op).hex()
    op["signing_payload_digest"] = bytes_digest(bytes.fromhex(payload[2:]))
    a = copy.deepcopy(evidence["approval"]["payload"])
    a.update(operation_digest=digest(op), policy_digest=digest(p),
             actor_id=op["actor_id"], credential_id=op["credential_id"])
    r = copy.deepcopy(evidence["final_revocation"]["payload"])
    r.update(operation_digest=digest(op), policy_digest=digest(p), approval_digest=digest(a))
    control = copy.deepcopy(evidence["control_observation"]["payload"])
    control.update(operation_digest=digest(op), workload_id=op["workload_id"],
                   deployment_digest=op["deployment_digest"])
    e = copy.deepcopy(evidence["execution"]["payload"])
    e.update(operation_digest=digest(op), policy_digest=digest(p), approval_digest=digest(a),
             revocation_digest=digest(r), control_digest=digest(control),
             actual_operation=copy.deepcopy(op), signing_payload=payload)
    # Model execution observations independently of requested operation. The
    # helper must not copy stale operation digests into actual_operation.
    execution_fields = dict(execution_updates or {})
    actual_updates = execution_fields.pop("actual_operation_updates", {})
    e["actual_operation"].update(actual_updates)
    e.update(execution_fields)
    b = copy.deepcopy(evidence["chain_observation"]["payload"])
    b.update(operation_digest=digest(op), execution_digest=digest(e),
             chain_id=op["chain_id"], wallet=op["wallet"])
    b.update(chain_updates or {})
    for name, body in (("policy", p), ("approval", a), ("final_revocation", r),
                       ("control_observation", control), ("execution", e), ("chain_observation", b)):
        resign(bundle, name, body)


def _rebind_downstream(bundle: dict) -> None:
    """Keep the original approval statement while changing other synthetic evidence."""
    ev = bundle["evidence"]
    r = copy.deepcopy(ev["final_revocation"]["payload"])
    r["approval_digest"] = digest(ev["approval"]["payload"])
    resign(bundle, "final_revocation", r)
    e = copy.deepcopy(ev["execution"]["payload"])
    e.update(approval_digest=digest(ev["approval"]["payload"]), revocation_digest=digest(r),
             control_digest=digest(ev["control_observation"]["payload"]))
    resign(bundle, "execution", e)
    b = copy.deepcopy(ev["chain_observation"]["payload"])
    b["execution_digest"] = digest(e)
    resign(bundle, "chain_observation", b)


def make_fixture(case: str = "authorized", *, at: int = DEFAULT_AT) -> tuple[dict, dict, int]:
    if case not in CASES:
        raise ValueError("unknown_fixture_case")
    run_id = "synthetic-wallet-run-001"
    deployment = digest({"synthetic_image": "wallet-observer-test-image-v0"})
    p = {"kind": "policy", "run_id": run_id, "policy_id": "synthetic-policy-001", "version": "1",
         "actor_id": "synthetic-developer-001", "credential_id": "synthetic-credential-001",
         "allowed_chains": ["31337"], "allowed_wallets": [WALLET],
         "allowed_actions": ["transfer", "delegate", "clear_delegation"],
         "allowed_assets": ["native"], "allowed_destinations": [DESTINATION, ALTERNATE_DESTINATION],
         "allowed_delegation_targets": [DELEGATE, ZERO_ADDRESS], "max_amount": "1000000",
         "workload_id": "synthetic-wallet-worker", "deployment_digest": deployment,
         "valid_from": at - 600, "valid_until": at + 600, "required_finality": "observed_block",
         "required_routes": ["approved_gate", "direct_signer", "deployment_signer"]}
    clear = case in ("clear_observed", "stop_with_delegation")
    op = {"operation_id": "synthetic-operation-001", "actor_id": p["actor_id"],
          "credential_id": p["credential_id"], "workload_id": p["workload_id"],
          "deployment_digest": deployment, "chain_id": "31337", "wallet": WALLET,
          "action": "clear_delegation" if clear else "delegate", "asset": "native", "amount": "0",
          "destination": DESTINATION, "calldata": "0x", "delegation_target": ZERO_ADDRESS if clear else DELEGATE,
          "nonce": "7", "signing_payload_digest": "sha256:" + "00" * 32, "policy_digest": digest(p)}
    signing_payload = "0x" + fixture_signing_bytes(op).hex()
    op["signing_payload_digest"] = bytes_digest(bytes.fromhex(signing_payload[2:]))
    a = {"kind": "approval", "run_id": run_id, "approval_id": "synthetic-approval-001",
         "approver_id": "synthetic-approver-001", "actor_id": op["actor_id"],
         "credential_id": op["credential_id"], "operation_digest": digest(op),
         "policy_digest": digest(p), "issued_at": at - 30, "expires_at": at + 120}
    r = {"kind": "final_revocation", "run_id": run_id, "snapshot_id": "synthetic-snapshot-001",
         "operation_digest": digest(op), "policy_digest": digest(p), "approval_digest": digest(a),
         "checked_at": at - 3, "valid_until": at + 30, "revoked_credentials": [], "revoked_approvals": []}
    control = {"kind": "control_observation", "run_id": run_id, "operation_digest": digest(op),
               "workload_id": op["workload_id"], "deployment_digest": deployment, "observed_at": at - 3,
               "observation_boundary": "synthetic named routes; privileged controller outside trust",
               "routes": {"approved_gate": "recorded", "direct_signer": "blocked", "deployment_signer": "blocked"}}
    e = {"kind": "execution", "run_id": run_id, "operation_digest": digest(op),
         "policy_digest": digest(p), "approval_digest": digest(a), "revocation_digest": digest(r),
         "control_digest": digest(control), "actual_operation": copy.deepcopy(op),
         "signing_payload": signing_payload, "state": "included", "observed_at": at - 2}
    b = {"kind": "chain_observation", "run_id": run_id, "operation_digest": digest(op),
         "execution_digest": digest(e), "chain_id": op["chain_id"], "wallet": op["wallet"],
         "observed_at": at - 1, "block_number": "100", "block_hash": "0x" + "aa" * 32,
         "transaction_hash": "0x" + "bb" * 32, "transaction_block_number": "100",
         "transaction_block_hash": "0x" + "aa" * 32, "receipt_status": "success",
         "delegation_code": "0x" if clear else "0xef0100" + DELEGATE[2:], "finality": "observed_block"}
    bundle = {"schema": BUNDLE_SCHEMA, "synthetic": True, "run_id": run_id, "operation": op, "evidence": {}}
    for name, body in (("policy", p), ("approval", a), ("final_revocation", r),
                       ("control_observation", control), ("execution", e), ("chain_observation", b)):
        resign(bundle, name, body)
    if case == "approval_mismatch":
        a["operation_digest"] = digest({"different_synthetic_intent": True})
        resign(bundle, "approval", a)
        _rebind_downstream(bundle)
    elif case == "missing_approval":
        del bundle["evidence"]["approval"]
    elif case == "stop_with_delegation":
        e["state"] = "offchain_stopped"
        resign(bundle, "execution", e)
        b.update(execution_digest=digest(e), receipt_status="missing", transaction_hash=None,
                 transaction_block_number=None, transaction_block_hash=None,
                 delegation_code="0xef0100" + DELEGATE[2:])
        resign(bundle, "chain_observation", b)
    elif case == "deployment_bypass":
        control["routes"]["deployment_signer"] = "reachable"
        resign(bundle, "control_observation", control)
        _rebind_downstream(bundle)
    elif case == "unknown_controller":
        control["routes"]["deployment_signer"] = "unobserved"
        resign(bundle, "control_observation", control)
        _rebind_downstream(bundle)
    elif case == "credential_revoked":
        r["revoked_credentials"] = [op["credential_id"]]
        resign(bundle, "final_revocation", r)
        _rebind_downstream(bundle)
    return bundle, fixture_trust(), at
