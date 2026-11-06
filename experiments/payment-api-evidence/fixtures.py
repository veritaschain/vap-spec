"""Synthetic statements only. Every signing seed in this module is PUBLIC TEST DATA.

No bank, school, customer, production credential, payment or collection outage is
represented. Fixture signatures do not establish independently observed facts.
"""
from __future__ import annotations

import copy
import hashlib

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from payment_evidence import (
    ADAPTER, APPROVALS, BUNDLE_SCHEMA, REQUIRED_ROUTES, ROLES, bytes_digest,
    canonical_json, digest, sign_envelope, synthetic_request_bytes,
)


DEFAULT_AT = 1793923200
CASES = {
    "authorized": "PAY-01",
    "same_person": "PAY-02", "missing_identity": "PAY-02",
    "changed_beneficiary": "PAY-03", "changed_amount": "PAY-03",
    "changed_currency": "PAY-03", "changed_tenant": "PAY-03",
    "changed_environment": "PAY-03",
    "revoked": "PAY-04", "missing_status": "PAY-04", "stale_status": "PAY-04",
    "bypass": "PAY-05", "missing_route": "PAY-05",
    "lost_ack": "PAY-06", "altered_replay": "PAY-06",
    "http_only": "PAY-07", "wrong_receipt": "PAY-07",
    "pending": "PAY-07", "accepted": "PAY-07", "failed": "PAY-07", "reversed": "PAY-07",
    "collector_gap": "PAY-08", "old_epoch": "PAY-08", "checkpoint_mismatch": "PAY-08",
}


def fixture_key(name: str) -> Ed25519PrivateKey:
    if name not in ROLES:
        raise ValueError("unknown_fixture_record")
    seed = hashlib.sha256(("PUBLIC SYNTHETIC PAYMENT EVIDENCE TEST SEED / " + name).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def fixture_key_id(name: str) -> str:
    if name not in ROLES:
        raise ValueError("unknown_fixture_record")
    return "public-synthetic-payment-" + name


def fixture_public(name: str) -> bytes:
    return fixture_key(name).public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def fixture_trust() -> dict:
    trust = {}
    for name, role in ROLES.items():
        trust.setdefault(role, {})[fixture_key_id(name)] = fixture_public(name)
    return trust


def fixture_identities(at: int = DEFAULT_AT) -> dict:
    return {fixture_public(name).hex(): {
        "person_id": "synthetic-person-" + role, "roles": [role],
        "tenant": "synthetic-tenant-A", "environment": "synthetic-production",
        "valid_from": at - 7200, "valid_until": at + 7200,
    } for name, role in zip(APPROVALS, ("maker", "checker"))}


def resign(bundle: dict, evidence_name: str, payload: dict) -> None:
    """Re-sign a synthetic statement only; do not repair any other reference."""
    bundle["evidence"][evidence_name] = sign_envelope(
        payload, fixture_key_id(evidence_name), fixture_key(evidence_name))


def refresh_bindings(bundle: dict, *, refresh_request: bool = False) -> None:
    """Rebuild downstream refs in a synthetic test, never 'repair' real evidence.

    The operation, policy and maker/checker approvals are NEVER modified here.
    Final status keeps all its assertions except refs to supplied approvals.
    Dispatch keeps its operation digest and actual operation; only its refs to
    policy/approvals/status/control are refreshed. With refresh_request=True,
    dispatch.actual_operation.payload_digest and request_hex are also regenerated
    using the declared actual operation; the approved operation stays unchanged.
    A receipt keeps its asserted operation/payload/outcome, changing only its
    dispatch ref. Collector retains its scope/epoch/gaps/time and receives exact
    refs to all other supplied envelopes. No missing record is manufactured.
    """
    evidence = bundle["evidence"]
    if "final_status" in evidence:
        body = copy.deepcopy(evidence["final_status"]["payload"])
        for name in APPROVALS:
            if name in evidence:
                body["approval_digests"][name] = digest(evidence[name])
        resign(bundle, "final_status", body)
    if "dispatch" in evidence:
        body = copy.deepcopy(evidence["dispatch"]["payload"])
        for field, name in (("policy_digest", "policy"), ("final_status_digest", "final_status"),
                            ("control_digest", "control")):
            if name in evidence:
                body[field] = digest(evidence[name])
        for name in APPROVALS:
            if name in evidence:
                body["approval_digests"][name] = digest(evidence[name])
        if refresh_request:
            request = synthetic_request_bytes(body["actual_operation"])
            body["actual_operation"]["payload_digest"] = bytes_digest(request)
            body["request_hex"] = request.hex()
        resign(bundle, "dispatch", body)
    if "provider_receipt" in evidence and "dispatch" in evidence:
        body = copy.deepcopy(evidence["provider_receipt"]["payload"])
        body["dispatch_digest"] = digest(evidence["dispatch"])
        resign(bundle, "provider_receipt", body)
    if "collector" in evidence:
        body = copy.deepcopy(evidence["collector"]["payload"])
        body["retained"] = {name: digest(env) for name, env in evidence.items() if name != "collector"}
        resign(bundle, "collector", body)


def make_fixture(case: str = "authorized", *, at: int = DEFAULT_AT) -> tuple[dict, dict, dict, int]:
    if case not in CASES:
        raise ValueError("unknown_fixture_case")
    if type(at) is not int or at < 7200:
        raise ValueError("fixture_time")
    run_id = "synthetic-payment-run-001"
    configuration = digest({"image": "synthetic-payment-worker-v0", "configuration": "fixture-A"})
    bundle = {"schema": BUNDLE_SCHEMA, "synthetic": True, "run_id": run_id,
              "operation": {}, "evidence": {}}
    common = {"run_id": run_id}
    policy = {
        **common, "kind": "policy", "policy_id": "synthetic-payment-policy", "version": "1",
        "tenant": "synthetic-tenant-A", "environment": "synthetic-production",
        "api_audience": "synthetic-payment-api", "provider_id": "synthetic-provider-A",
        "adapter": ADAPTER, "principal_id": "synthetic-agent-A", "credential_id": "synthetic-credential-A",
        "workload_id": "synthetic-workload-A", "configuration_digest": configuration,
        "recovery_epoch": 7, "allowed_sources": ["synthetic-source-A"],
        "allowed_beneficiaries": ["synthetic-beneficiary-A"], "currency": "USD", "minor_unit_scale": 2,
        "max_amount_minor": "1000000", "required_routes": list(REQUIRED_ROUTES),
        "valid_from": at - 3600, "valid_until": at + 3600,
    }
    resign(bundle, "policy", policy)
    operation = {
        "operation_id": "synthetic-operation-A", "tenant": policy["tenant"],
        "environment": policy["environment"], "api_audience": policy["api_audience"],
        "adapter": ADAPTER, "principal_id": policy["principal_id"], "credential_id": policy["credential_id"],
        "workload_id": policy["workload_id"], "configuration_digest": configuration,
        "recovery_epoch": policy["recovery_epoch"], "source_account": "synthetic-source-A",
        "beneficiary": "synthetic-beneficiary-A", "action": "transfer", "amount_minor": "12500",
        "currency": "USD", "minor_unit_scale": 2, "nonce": "23",
        "idempotency_domain": "synthetic-tenant-A:synthetic-payment-api:synthetic-production",
        "idempotency_key": "synthetic-idempotency-A", "policy_digest": digest(bundle["evidence"]["policy"]),
        "payload_digest": "sha256:" + "00" * 32, "valid_from": at - 1800, "valid_until": at + 600,
    }
    request = synthetic_request_bytes(operation)
    operation["payload_digest"] = bytes_digest(request)
    bundle["operation"] = operation
    operation_ref = digest(operation)
    for name in APPROVALS:
        resign(bundle, name, {
            **common, "kind": name, "approval_id": "synthetic-" + name,
            "operation_digest": operation_ref, "policy_digest": operation["policy_digest"],
            "issued_at": at - 900, "expires_at": at + 600,
        })
    evidence = bundle["evidence"]
    approval_refs = {name: digest(evidence[name]) for name in APPROVALS}
    resign(bundle, "final_status", {
        **common, "kind": "final_status", "operation_digest": operation_ref,
        "policy_digest": operation["policy_digest"], "approval_digests": approval_refs,
        "configuration_digest": configuration, "recovery_epoch": operation["recovery_epoch"],
        "credential_id": operation["credential_id"], "checked_at": at - 12, "valid_until": at + 60,
        "state": "active", "revoked_at": None,
    })
    resign(bundle, "control", {
        **common, "kind": "control", "operation_digest": operation_ref,
        "configuration_digest": configuration, "recovery_epoch": operation["recovery_epoch"],
        "observed_at": at - 13, "observation_boundary": "synthetic named routes at one recorded time",
        "routes": dict(REQUIRED_ROUTES),
    })
    resign(bundle, "dispatch", {
        **common, "kind": "dispatch", "operation_digest": operation_ref,
        "policy_digest": operation["policy_digest"], "approval_digests": approval_refs,
        "final_status_digest": digest(evidence["final_status"]), "control_digest": digest(evidence["control"]),
        "actual_operation": copy.deepcopy(operation), "request_hex": request.hex(),
        "dispatched_at": at - 10, "http_status": 200,
    })
    resign(bundle, "provider_receipt", {
        **common, "kind": "provider_receipt", "provider_id": policy["provider_id"],
        "api_audience": policy["api_audience"], "operation_digest": operation_ref,
        "payload_digest": operation["payload_digest"], "dispatch_digest": digest(evidence["dispatch"]),
        "observed_at": at - 5, "status": "settled",
    })
    resign(bundle, "collector", {
        **common, "kind": "collector", "operation_digest": operation_ref,
        "configuration_digest": configuration, "recovery_epoch": operation["recovery_epoch"],
        "checkpoint_id": "synthetic-checkpoint-A", "checkpoint_at": at - 1,
        "retained": {name: digest(env) for name, env in evidence.items()}, "gaps": [],
    })
    identities = fixture_identities(at)

    if case == "same_person":
        identities[fixture_public("checker_approval").hex()]["person_id"] = identities[
            fixture_public("maker_approval").hex()]["person_id"]
    elif case == "missing_identity":
        del identities[fixture_public("checker_approval").hex()]
    elif case.startswith("changed_") or case == "altered_replay":
        change = {
            "changed_beneficiary": ("beneficiary", "synthetic-beneficiary-B"),
            "changed_amount": ("amount_minor", "12501"),
            "changed_currency": ("currency", "EUR"),
            "changed_tenant": ("tenant", "synthetic-tenant-B"),
            "changed_environment": ("environment", "synthetic-test"),
            "altered_replay": ("amount_minor", "25000"),
        }[case]
        body = copy.deepcopy(evidence["dispatch"]["payload"])
        body["actual_operation"][change[0]] = change[1]
        resign(bundle, "dispatch", body)
        refresh_bindings(bundle, refresh_request=True)
        # A newly signed provider assertion faithfully describes this changed
        # actual request, while the original approvals remain untouched.
        receipt = copy.deepcopy(evidence["provider_receipt"]["payload"])
        actual = evidence["dispatch"]["payload"]["actual_operation"]
        receipt.update(operation_digest=digest(actual), payload_digest=actual["payload_digest"])
        resign(bundle, "provider_receipt", receipt)
    elif case in ("revoked", "stale_status"):
        body = copy.deepcopy(evidence["final_status"]["payload"])
        if case == "revoked":
            body.update(state="revoked", revoked_at=at - 20)
        else:
            body.update(checked_at=at - 600)
        resign(bundle, "final_status", body)
    elif case == "missing_status":
        del evidence["final_status"]
    elif case in ("bypass", "missing_route"):
        body = copy.deepcopy(evidence["control"]["payload"])
        if case == "bypass":
            body["routes"]["cloud_management"] = "bypassed"
        else:
            del body["routes"]["deployment"]
        resign(bundle, "control", body)
    elif case in ("lost_ack", "http_only"):
        del evidence["provider_receipt"]
        if case == "lost_ack":
            body = copy.deepcopy(evidence["dispatch"]["payload"])
            body["http_status"] = None
            resign(bundle, "dispatch", body)
    elif case == "wrong_receipt":
        body = copy.deepcopy(evidence["provider_receipt"]["payload"])
        body["operation_digest"] = digest({"operation": "synthetic-other-operation"})
        resign(bundle, "provider_receipt", body)
    elif case in ("pending", "accepted", "failed", "reversed"):
        body = copy.deepcopy(evidence["provider_receipt"]["payload"])
        body["status"] = case
        resign(bundle, "provider_receipt", body)
    elif case == "collector_gap":
        body = copy.deepcopy(evidence["collector"]["payload"])
        body["gaps"] = ["synthetic declared outage before checkpoint; unobserved actions unknown"]
        resign(bundle, "collector", body)
    elif case == "old_epoch":
        body = copy.deepcopy(evidence["collector"]["payload"])
        body["recovery_epoch"] -= 1
        resign(bundle, "collector", body)
    refresh_bindings(bundle)
    if case == "checkpoint_mismatch":
        body = copy.deepcopy(evidence["collector"]["payload"])
        body["retained"]["dispatch"] = digest({"dispatch": "synthetic-other-record"})
        resign(bundle, "collector", body)
    return bundle, fixture_trust(), identities, at


if __name__ == "__main__":
    # stdout only; this is a convenience view of synthetic semantics, not a
    # test runner, a durable evidence capture or payment processing.
    from payment_evidence import verify_bundle

    summaries = []
    for case, candidate in CASES.items():
        bundle, trust, identities, at = make_fixture(case)
        report = verify_bundle(bundle, trust, identities=identities, evaluation_time=at)
        summaries.append({"case": case, "candidate": candidate,
                          "claims": {name: result["verdict"] for name, result in report["claims"].items()},
                          "outcome": report["outcome"]})
    print(canonical_json({"synthetic": True, "evidence_semantics_only": True,
                          "cases": summaries}).decode("utf-8"))
