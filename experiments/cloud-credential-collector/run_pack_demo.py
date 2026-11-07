#!/usr/bin/env python3
"""Execute a private, portable custody-pack demo with public synthetic material.

The exporting parent creates actual stores/files. Separate verifying processes
receive only the inert JSON pack, external public pin, expected store ID and an
optional separately retained checkpoint. They reject collector/SQLite imports.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
from collector_support import SENSITIVE_SENTINEL
from pack_support import (
    BINARY_ORIGINAL, Harness, PUBLIC_TEST_KEY, PUBLIC_TEST_SEED,
    artifact_bytes, chunks, digest, pack_module, private_json, private_write,
    standalone_verify, verify_signature,
)


def require(condition, code):
    if not condition:
        raise RuntimeError("synthetic pack demo expectation mismatch: " + code)


def verified_process(path, public_pin, expected_id, *, external_checkpoint=None):
    process = standalone_verify(path, public_pin, expected_id, external_checkpoint_path=external_checkpoint)
    require(process.returncode == 0, "portable_verification_completed")
    result = json.loads(process.stdout)
    require(result["store_modules_loaded"] == [], "no_collector_or_sqlite_dependency")
    require(SENSITIVE_SENTINEL not in process.stdout + process.stderr, "no_raw_marker_output")
    return result


def rejected_process(path, public_pin, expected_id, *, external_checkpoint=None):
    process = standalone_verify(path, public_pin, expected_id, external_checkpoint_path=external_checkpoint)
    require(process.returncode == 2, "invalid_pack_rejected")
    observed = json.loads(process.stderr)
    require(observed["error_type"] == "PackError", "rejection_is_pack_verification_not_process_failure")
    require(SENSITIVE_SENTINEL not in process.stdout + process.stderr, "no_rejected_original_echo")
    return {"exit_code": process.returncode, "error_type": observed["error_type"]}


def run_demo():
    pack = pack_module()
    scenarios = []
    with Harness() as h:
        expected_id = h.manifest["payload"]["store_id"]
        public_pin = private_write(h.root / "external-public-pin.bin", PUBLIC_TEST_KEY)
        private_seed = private_write(h.root / "export-private-test-seed.bin", PUBLIC_TEST_SEED)
        h.collect("text-original")
        old_witness = private_json(h.root / "separately-retained-old-checkpoint.json", h.checkpoint())
        old_path = h.root / "old-prefix-pack.json"
        pack.export_pack(h.store, old_path, trusted_public_key=public_pin.read_bytes(),
                         private_key=private_seed.read_bytes(), expected_store_id=expected_id)
        binary = private_write(h.root / "arbitrary-binary-source.raw", BINARY_ORIGINAL)
        h.collect("binary-original", path=binary)
        h.collect("same-binary-distinct-request", path=binary)
        current_path = h.root / "full-prefix-pack.json"
        exported = pack.export_pack(h.store, current_path, trusted_public_key=public_pin.read_bytes(),
                                    private_key=private_seed.read_bytes(), expected_store_id=expected_id)
        later_witness = private_json(h.root / "separately-retained-later-checkpoint.json", h.checkpoint())
        package = json.loads(current_path.read_text(encoding="utf-8"))
        originals = {item["artifact_sha256"]: artifact_bytes(item) for item in package["artifacts"]}
        exact = originals == {digest(h.raw): h.raw, digest(BINARY_ORIGINAL): BINARY_ORIGINAL}
        require(exact, "exact_text_and_non_utf8_originals")
        for envelope in [package["manifest"], package["checkpoint"], *package["receipts"]]:
            verify_signature(envelope)
        require(exported["receipt_count"] == 3 and exported["artifact_count"] == 2, "full_prefix_and_shared_hash_dedup")
        scenarios.append({"scenario": "full_committed_prefix_export", "receipt_count": exported["receipt_count"],
                          "artifact_count": exported["artifact_count"],
                          "total_artifact_bytes": exported["total_artifact_bytes"],
                          "original_bytes_preserved": exact,
                          "custody_signatures_verified_with_external_pin": True})

        foreign_path = h.root / "other-store-same-key-pack.json"
        with Harness(raw=b"synthetic other-store original") as other:
            other.collect("other-store-request")
            foreign = pack.export_pack(other.store, foreign_path, trusted_public_key=PUBLIC_TEST_KEY,
                                       private_key=PUBLIC_TEST_SEED,
                                       expected_store_id=other.manifest["payload"]["store_id"])
            require(foreign["store_id"] != expected_id, "distinct_expected_store_identity")

        # Only portable packs, the public pin and retained checkpoints remain.
        shutil.rmtree(h.store)
        h.input.unlink()
        binary.unlink()
        private_seed.unlink()
        require(not h.store.exists() and not private_seed.exists(), "original_store_and_seed_unavailable")
        portable = verified_process(current_path, public_pin, expected_id)
        report = portable["verification"]
        require(report["internal_checkpoint_status"] == "matched_exported_tip", "exact_internal_tip")
        require(report["rollback_assessment"] == "not_assessed", "internal_tip_is_not_external_witness")
        scenarios.append({"scenario": "separate_process_without_original_store_or_private_seed",
                          "original_store_available": h.store.exists(), "private_seed_file_available": private_seed.exists(),
                          "store_modules_loaded": portable["store_modules_loaded"],
                          "verification": report})

        changed = copy.deepcopy(package)
        first = changed["artifacts"][0]
        raw = artifact_bytes(first)
        first["base64_chunks"] = chunks(bytes([raw[0] ^ 1]) + raw[1:])
        corrupt_path = private_json(h.root / "modified-original-pack.json", changed)
        tamper = rejected_process(corrupt_path, public_pin, expected_id)
        scenarios.append({"scenario": "changed_original_bytes", **tamper})

        swap = rejected_process(foreign_path, public_pin, expected_id)
        scenarios.append({"scenario": "same_key_other_store_swap", **swap})

        without = verified_process(old_path, public_pin, expected_id)["verification"]
        with_old = verified_process(old_path, public_pin, expected_id, external_checkpoint=old_witness)["verification"]
        extended = verified_process(current_path, public_pin, expected_id, external_checkpoint=old_witness)["verification"]
        newer_rejection = rejected_process(old_path, public_pin, expected_id, external_checkpoint=later_witness)
        require(without["rollback_assessment"] == "not_assessed", "old_prefix_without_witness_not_assessed")
        require(with_old["external_checkpoint_status"] == extended["external_checkpoint_status"] == "matched_prefix",
                "old_witness_matches_only_its_retained_prefix")
        require(with_old["latestness"] == extended["latestness"] == "unresolved", "matching_prefix_does_not_prove_latestness")
        scenarios.append({"scenario": "older_pack_and_external_checkpoint_scope",
                          "older_pack_receipts": without["receipt_count"],
                          "without_external_checkpoint": without["rollback_assessment"],
                          "older_pack_with_old_witness": with_old["external_checkpoint_status"],
                          "extended_pack_with_old_witness": extended["external_checkpoint_status"],
                          "matching_prefix_latestness": extended["latestness"],
                          "later_witness_rejection": newer_rejection})
    return {"schema": "experimental-cloud-custody-pack-demo-v0", "synthetic": True,
            "public_test_keys": True, "same_local_operator": True, "live_cloud_calls": 0,
            "independent_custody_established": False, "scenario_count": len(scenarios), "scenarios": scenarios}


def main():
    try:
        result = run_demo()
    except Exception as exc:
        print(json.dumps({"schema": "experimental-cloud-custody-pack-demo-error-v0", "synthetic": True,
                          "error_type": type(exc).__name__}), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
