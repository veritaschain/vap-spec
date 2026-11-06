"""Actual local mock admission and response-loss demo; no real funds or people.

Exports only selected public results, the original admission record and the
original provider receipt. All private material and stores are temporary.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
import secrets
import selectors
import subprocess
import sys
import tempfile

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

import authorization_gate as admission


runtime = admission.runtime


def public_key(key: Ed25519PrivateKey) -> bytes:
    return key.public_key().public_bytes(
        serialization.Encoding.Raw, serialization.PublicFormat.Raw)


def demo_authority(context: dict, configuration: str) -> tuple[admission.GateConfig, dict]:
    """All identities and keys belong to this single trusted demo controller."""
    at = admission.now_ms()
    keys = {name: Ed25519PrivateKey.generate() for name in admission.SLOTS}
    policy = {
        "schema": admission.POLICY_SCHEMA, "policy_id": "synthetic-demo-policy",
        "version": "1", "context": context, "principal_id": "synthetic-principal-A",
        "credential_id": "synthetic-credential-label-A",
        "configuration_digest": configuration, "recovery_epoch": 1,
        "allowed_sources": ["synthetic-source"],
        "allowed_beneficiaries": ["synthetic-beneficiary", "synthetic-other-beneficiary"],
        "max_amount_minor": "50000", "valid_from_ms": at - 600000,
        "valid_until_ms": at + 600000,
    }
    trust = {
        "approver": {name: public_key(keys[name]) for name in admission.APPROVALS},
        "status_authority": {"final_status": public_key(keys["final_status"])},
    }
    identities = {
        public_key(keys[name]).hex(): {
            "person_id": "synthetic-person-" + role, "roles": [role],
            **{field: context[field] for field in runtime.SCOPE_FIELDS},
            "valid_from_ms": at - 600000, "valid_until_ms": at + 600000,
        }
        for name, role in zip(admission.APPROVALS, ("maker", "checker"))
    }
    return admission.GateConfig(policy, trust, identities), keys


def demo_evidence(request: dict, config: admission.GateConfig, keys: dict,
                  *, state: str = "active", observed_at_ms: int | None = None) -> dict:
    at = admission.now_ms()
    observed = at if observed_at_ms is None else observed_at_ms
    policy_hash = admission.policy_digest(config.policy)
    request_hash = runtime.bytes_digest(runtime.request_bytes(request))
    evidence = {}
    for name in admission.APPROVALS:
        payload = {
            "schema": admission.APPROVAL_SCHEMA, "kind": name,
            "approval_id": "synthetic-demo-" + name,
            "request_digest": request_hash, "policy_digest": policy_hash,
            "issued_at_ms": min(at - 1000, observed - 1000),
            "expires_at_ms": at + 300000,
        }
        evidence[name] = admission.sign_evidence(payload, name, keys[name])
    payload = {
        "schema": admission.STATUS_SCHEMA, "kind": "final_status",
        "status_id": "synthetic-demo-status", "request_digest": request_hash,
        "policy_digest": policy_hash,
        "approval_digests": {name: runtime.bytes_digest(evidence[name]) for name in admission.APPROVALS},
        "principal_id": config.policy["principal_id"],
        "credential_id": config.policy["credential_id"],
        "configuration_digest": config.policy["configuration_digest"],
        "recovery_epoch": config.policy["recovery_epoch"],
        "observed_at_ms": observed, "valid_until_ms": at + 60000,
        "state": state, "revoked_at_ms": observed - 1 if state == "revoked" else None,
    }
    evidence["final_status"] = admission.sign_evidence(payload, "final_status", keys["final_status"])
    return evidence


def public_result(result: dict) -> dict:
    record = result["mock_admission"]
    return {
        "state": result["state"], "request_digest": result["request_digest"],
        "mock_admission": {key: record[key] for key in (
            "verdict", "reasons", "request_digest", "evaluated_at_ms", "admitted_at_ms",
            "proof_digest", "historical_original_decision") if key in record},
        "business_authorization_verified": result["business_authorization_verified"],
        "automatic_retry": result["automatic_retry"], "production_gate": result["production_gate"],
        "receipt_digest": runtime.bytes_digest(result["receipt_bytes"]) if result["receipt_bytes"] else None,
    }


def run_demo() -> tuple[dict, bytes, bytes]:
    with tempfile.TemporaryDirectory(prefix="synthetic-payment-authorization-") as directory:
        root = Path(directory)
        context = {
            "tenant": "synthetic-tenant-A", "environment": "synthetic-lab",
            "api_audience": "synthetic-loopback-api", "idempotency_domain": "synthetic-domain-A",
            "currency": "USD", "minor_unit_scale": 2,
        }
        configuration = runtime.digest({"synthetic_configuration": "authorization-demo-v0"})
        provider_key = Ed25519PrivateKey.generate()
        credential = secrets.token_urlsafe(32)
        provider_db = root / "provider.sqlite"
        provider_config = {
            "db_path": str(provider_db), "context": context,
            "private_key_hex": provider_key.private_bytes(
                serialization.Encoding.Raw, serialization.PrivateFormat.Raw,
                serialization.NoEncryption()).hex(),
            "credential": credential, "configuration_digest": configuration, "recovery_epoch": 1,
            "initial_balances": {"synthetic-source": "1000000", "synthetic-beneficiary": "0",
                                 "synthetic-other-beneficiary": "0"},
            "drop_after_commit": True,
        }
        config_path = root / "private-provider.json"
        descriptor = os.open(config_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(runtime.canonical_json(provider_config))
        command = [sys.executable] + (["-O"] if sys.flags.optimize else []) + [
            str(Path(runtime.__file__)), "provider", "--config", str(config_path)]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdout, selectors.EVENT_READ)
                if not selector.select(timeout=10):
                    raise RuntimeError("mock_provider_startup_timeout")
                line = process.stdout.readline()
            ready = json.loads(line) if line else {}
            if ready.get("event") != "ready":
                raise RuntimeError("mock_provider_startup_failed")
            config, keys = demo_authority(context, configuration)
            request = runtime.make_request(context, operation_id="synthetic-operation-A",
                idempotency_key="synthetic-idempotency-A", configuration_digest=configuration,
                recovery_epoch=1, source_account="synthetic-source",
                beneficiary="synthetic-beneficiary", amount_minor="12500")

            def gate_for(name: str, adopted: admission.GateConfig):
                adapter = runtime.Adapter(root / (name + ".sqlite"), ready["endpoint"], context,
                    public_key(provider_key), credential, configuration, 1)
                return adapter, admission.AuthorizedAdapter(adapter, adopted)

            same_person = copy.deepcopy(config)
            same_person.identities[public_key(keys["checker_approval"]).hex()]["person_id"] = (
                config.identities[public_key(keys["maker_approval"]).hex()]["person_id"])
            changed = {**request, "amount_minor": "13000"}
            missing_status = demo_evidence(request, config, keys)
            del missing_status["final_status"]
            cases = [
                ("same_person_two_keys", same_person, request, demo_evidence(request, config, keys), "DENIED"),
                ("changed_amount_with_original_approvals", config, changed, demo_evidence(request, config, keys), "DENIED"),
                ("signed_revoked_status", config, request, demo_evidence(request, config, keys, state="revoked"), "DENIED"),
                ("missing_status", config, request, missing_status, "UNKNOWN"),
                ("stale_signed_status", config, request, demo_evidence(request, config, keys,
                     observed_at_ms=admission.now_ms() - 90000), "UNKNOWN"),
            ]
            steps = []
            for name, adopted, actual_request, evidence, verdict in cases:
                adapter, gate = gate_for(name, adopted)
                result = gate.submit(actual_request, evidence)
                provider = runtime.provider_snapshot(provider_db)
                if (result["state"] != "REJECTED" or result["mock_admission"]["verdict"] != verdict
                        or adapter.snapshot()["claims"] != 0
                        or provider["post_attempts"] != 0 or provider["effects"] != 0):
                    raise RuntimeError("mock_admission_negative_control_failed:" + name)
                steps.append({"stage": name, "result": public_result(result), "provider": provider})

            adapter, gate = gate_for("authorized", config)
            first = gate.submit(request, demo_evidence(request, config, keys))
            original = gate.read_authorization(request)
            if original["status"] != "FOUND" or original["record_bytes"] is None:
                raise RuntimeError("original_admission_record_missing")
            steps.append({"stage": "authorized_provider_committed_response_lost",
                          "result": public_result(first), "provider": runtime.provider_snapshot(provider_db)})
            repeated = gate.submit(request, demo_evidence(request, config, keys, state="revoked"))
            steps.append({"stage": "repeat_with_later_revoked_statement_no_new_admission",
                          "result": public_result(repeated), "provider": runtime.provider_snapshot(provider_db)})
            reconciled = gate.reconcile(request)
            steps.append({"stage": "read_only_reconciliation", "result": public_result(reconciled),
                          "provider": runtime.provider_snapshot(provider_db)})
            stable = gate.submit(request)
            steps.append({"stage": "stored_historical_result_no_provider_call", "result": public_result(stable),
                          "provider": runtime.provider_snapshot(provider_db)})
            terminal = steps[-1]["provider"]
            valid = (
                first["state"] == repeated["state"] == "UNKNOWN"
                and reconciled["state"] == stable["state"] == "SETTLED"
                and all(value["mock_admission"]["verdict"] == "AUTHORIZED"
                        for value in (first, repeated, reconciled, stable))
                and all(step["provider"]["post_attempts"] == 1 and step["provider"]["effects"] == 1
                        for step in steps[-4:])
                and [step["provider"]["lookup_attempts"] for step in steps[-4:]] == [0, 0, 1, 1]
                and gate.read_authorization(request)["record_bytes"] == original["record_bytes"]
                and reconciled["receipt_bytes"] == stable["receipt_bytes"]
                and reconciled["receipt_bytes"] is not None
                and terminal["balances"] == {"synthetic-source": "987500", "synthetic-beneficiary": "12500",
                                             "synthetic-other-beneficiary": "0"}
            )
            if not valid:
                raise RuntimeError("mock_authorization_recovery_demo_failed")
            summary = {
                "schema": "synthetic-payment-authorization-demo-v0", "synthetic": True,
                "request": request, "provider_public_key_hex": public_key(provider_key).hex(),
                "key_provenance": "all_keys_and_identity_mappings_from_one_trusted_demo_controller",
                "business_authorization_verified": False, "production_gate": False, "automatic_retry": False,
                "admission_record_digest": runtime.bytes_digest(original["record_bytes"]),
                "provider_receipt_digest": runtime.bytes_digest(reconciled["receipt_bytes"]),
                "steps": steps,
                "limitations": [
                    "synthetic_identities_policy_and_local_mock_balances_only",
                    "supplied_signed_status_is_not_latest_authority_state",
                    "claim_time_admission_is_not_continuous_revocation_or_atomic_provider_enforcement",
                    "configured_principal_labels_do_not_authenticate_the_caller",
                    "direct_provider_or_raw_runtime_with_bearer_can_bypass_wrapper",
                    "historical_admission_record_is_not_a_separately_signed_gate_attestation",
                    "no_independent_collector_external_anchor_or_OS_isolation",
                    "no_storage_rollback_power_loss_VAP_conformance_or_production_readiness_claim",
                ],
            }
            return summary, original["record_bytes"], reconciled["receipt_bytes"]
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)
            process.stdout.close()
            process.stderr.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Directory for three explicitly public demo files")
    args = parser.parse_args()
    summary, record, receipt = run_demo()
    if args.output is not None:
        args.output.mkdir(parents=True, exist_ok=True)
        (args.output / "summary.json").write_bytes(runtime.canonical_json(summary) + b"\n")
        (args.output / "admission-record.json").write_bytes(record)
        (args.output / "provider-receipt.json").write_bytes(receipt)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
