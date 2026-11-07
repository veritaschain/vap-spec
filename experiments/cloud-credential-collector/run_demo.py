#!/usr/bin/env python3
"""Run actual local disk/process exercises using only public synthetic material.

Temporary stores, raw exports and test jobs stay owner-private and are removed
when the demo exits. The summary contains measured distinctions, not a global
safety, prevention, independent-custody or conformance verdict.
"""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import signal
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
from collector_support import (
    CUSTODY_DOMAIN, Harness, PUBLIC_TEST_KEY, SENSITIVE_SENTINEL, canonical, digest,
    load_collector, private_json, private_write, tree_snapshot,
)
from integration_support import bridge_scenario


def require(condition, code):
    # Deliberately not a Python assert: demo checks also execute under python -O.
    if not condition:
        raise RuntimeError("synthetic demo expectation mismatch: " + code)


def verified_receipt(receipt):
    signed = {name: receipt[name] for name in ("key_id", "payload")}
    Ed25519PublicKey.from_public_bytes(PUBLIC_TEST_KEY).verify(
        bytes.fromhex(receipt["signature"]), CUSTODY_DOMAIN + canonical(signed))


def collect_restart_and_bridge():
    with Harness() as h:
        receipt = h.collect()
        verified_receipt(receipt)
        require(receipt["payload"]["artifact_sha256"] == digest(h.raw), "original_byte_commitment")
        require(h.blob_path().read_bytes() == h.raw, "stored_original_bytes")
        restarted = h.job("receipt").result()
        repeated = h.job("collect").result()
        require(receipt == restarted == repeated, "original_receipt_after_restart_and_retry")
        retry_audit = h.audit()
        require(retry_audit["record_count"] == 1, "restart_did_not_duplicate")
        result = bridge_scenario(h)
        resource = result["native_envelopes"]["resource"]["payload"]
        require(resource["body"]["raw"].encode("utf-8") == h.raw, "bridge_exact_bytes")
        require(resource["received_time"] == receipt["payload"]["received_time"], "bridge_actual_receipt")
        require(resource["available_time"] is None, "unknown_availability_preserved")
        claims = {name: claim["status"] for name, claim in result["report"]["claims"].items()}
        require(claims["operation"] == "supported", "retrospective_read_supported")
        require(claims["timing"] == "contradicted", "post_action_collection_remains_late")
        for name in ("external_exfiltration", "global_containment", "ai_orchestration"):
            require(claims[name] == "unresolved", name + "_boundary")
        require(SENSITIVE_SENTINEL not in json.dumps(result["report"]), "minimized_derived_report")
        return [
            {"scenario": "capture_restart_and_idempotent_retry", "record_count_after_retry": retry_audit["record_count"],
             "original_bytes_preserved": resource["body"]["raw"].encode("utf-8") == h.raw,
             "original_receipt_recovered": receipt == restarted == repeated,
             "received_time_ns": receipt["payload"]["received_time_ns"],
             "bridge_received_time": resource["received_time"],
             "signature_verified_with_external_public_key": True},
            {"scenario": "existing_verifier_native_bridge", "claims": claims,
             "source_availability": "unknown", "caller_policy_and_context": "synthetic",
             "private_raw_envelope_and_separate_derived_report": True},
        ]


def concurrent_idempotency():
    with Harness() as h:
        workers = [h.job(start_barrier=True), h.job(start_barrier=True)]
        for worker in workers:
            require(worker.event()["event"] == "ready", "concurrent_process_ready")
        for worker in workers:
            worker.release()
        receipts = [worker.result() for worker in workers]
        audit = h.audit()
        require(receipts[0] == receipts[1], "concurrent_same_receipt")
        require(audit["record_count"] == 1, "one_concurrent_commit")
        return {"scenario": "two_process_same_request", "processes": len(workers),
                "committed_records": audit["record_count"], "same_receipt": receipts[0] == receipts[1]}


def process_failure(stage):
    with Harness() as h:
        worker = h.job(barrier=stage)
        event = worker.event()
        require(event["event"] == "barrier" and event["stage"] == stage, "crash_boundary_reached")
        exit_code = worker.kill()
        require(exit_code == -signal.SIGKILL, "actual_process_death")
        before_retry = h.audit()
        committed_before_retry = 1 if stage == "after_commit" else 0
        require(before_retry["record_count"] == committed_before_retry, "durable_commit_boundary")
        original = h.job("receipt").result() if committed_before_retry else None
        recovered = h.job("collect").result()
        repeated = h.job("collect").result()
        require(recovered == repeated, "recovery_idempotent")
        if original is not None:
            require(recovered == original, "lost_response_original_receipt")
        after_retry = h.audit()
        require(after_retry["record_count"] == 1, "recovery_one_commit")
        return {"scenario": "sigkill_" + stage, "signal": "SIGKILL", "child_exit_code": exit_code,
                "records_before_retry": before_retry["record_count"],
                "records_after_retry": after_retry["record_count"],
                "retry_returns_original_committed_receipt": original == recovered if original is not None else None,
                "repeat_is_idempotent": recovered == repeated}


def corruption_without_repair():
    collector = load_collector()
    with Harness() as h:
        h.collect()
        h.blob_path().write_bytes(b"deliberately altered synthetic committed original")
        before = tree_snapshot(h.store)
        rejected = []
        for operation, action in (("audit", h.audit), ("retry", h.collect)):
            try:
                action()
            except collector.CollectorError:
                rejected.append(operation)
        require(rejected == ["audit", "retry"], "committed_corruption_rejected")
        unchanged = before == tree_snapshot(h.store)
        require(unchanged, "no_automatic_repair")
        return {"scenario": "committed_original_tamper", "rejected_operations": rejected,
                "store_unchanged_after_rejection": unchanged}


def retained_checkpoint_boundary():
    collector = load_collector()
    with Harness() as h:
        h.collect()
        prefix_checkpoint = h.checkpoint()
        old_prefix = h.root / "copied-old-prefix"
        shutil.copytree(h.store, old_prefix)
        alternate = private_write(h.root / "second-source.raw", h.raw + b" ")
        h.collect("request-2", path=alternate)
        later_checkpoint = h.checkpoint()
        retained = private_json(h.root / "retained-later-checkpoint.json", later_checkpoint)
        extended = h.audit(checkpoint=prefix_checkpoint)
        require(extended["record_count"] == 2 and extended["checkpoint_status"] == "matched",
                "valid_prefix_extension")
        with collector.Collector(old_prefix, trusted_public_key=PUBLIC_TEST_KEY) as old:
            without = old.audit()
            with_old = old.audit(checkpoint=prefix_checkpoint)
            rejected = False
            try:
                old.audit(checkpoint=json.loads(retained.read_text(encoding="utf-8")))
            except collector.CollectorError:
                rejected = True
        require(without["record_count"] == 1 and without["checkpoint_status"] == "not_provided",
                "coherent_prefix_is_not_rollback_assessed")
        require(with_old["checkpoint_status"] == "matched", "old_checkpoint_cannot_witness_lost_suffix")
        require(rejected, "later_external_checkpoint_detects_truncation")
        return {"scenario": "copied_coherent_prefix_and_retained_checkpoint",
                "live_store_records": extended["record_count"], "copied_prefix_records": without["record_count"],
                "without_checkpoint": without["checkpoint_status"],
                "rollback_assessment_without_checkpoint": without["rollback_assessment"],
                "with_old_prefix_checkpoint": with_old["checkpoint_status"],
                "extended_store_accepts_old_checkpoint": extended["checkpoint_status"],
                "retained_later_checkpoint_rejects_truncation": rejected,
                "completeness": without["completeness"]}


def run_demo():
    scenarios = collect_restart_and_bridge()
    scenarios.append(concurrent_idempotency())
    scenarios.append(process_failure("before_commit"))
    scenarios.append(process_failure("after_commit"))
    scenarios.append(corruption_without_repair())
    scenarios.append(retained_checkpoint_boundary())
    return {"schema": "experimental-cloud-collector-demo-results-v0", "synthetic": True,
            "public_test_keys": True, "same_local_operator": True, "live_cloud_calls": 0,
            "independent_custody_established": False, "prevention_established": False,
            "scenario_count": len(scenarios), "scenarios": scenarios}


def main():
    try:
        report = run_demo()
    except Exception as exc:
        # No private records, keys, paths or arbitrary exception messages.
        print(json.dumps({"schema": "experimental-cloud-collector-demo-error-v0", "synthetic": True,
                          "error_type": type(exc).__name__}), file=sys.stderr)
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
