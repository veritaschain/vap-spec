"""Independent verification of bounded, inert, portable synthetic custody JSON.

Public fixture keys are deliberate test data. A valid pack establishes only its
signed declared prefix under external pins; its internal checkpoint is not a
separately retained witness and cannot prove latestness or completeness.
"""
from __future__ import annotations

import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collector_support import SENSITIVE_SENTINEL, tree_snapshot
from pack_support import (
    BINARY_ORIGINAL, CHUNK_BYTES, Harness, MAX_PACK_BYTES, PUBLIC_TEST_KEY,
    PUBLIC_TEST_SEED, PYTHON, ROOT, artifact_bytes, canonical, chunks,
    collected_pack, digest, export, pack_module, private_json, private_write,
    resign, resign_chain, standalone_verify, verify_signature,
)

pack = pack_module()


class PackTestCase(unittest.TestCase):
    def harness(self, **options):
        h = Harness(**options)
        self.addCleanup(h.close)
        return h

    def verify(self, h, package, **options):
        return pack.verify_pack(package, trusted_public_key=PUBLIC_TEST_KEY,
                                expected_store_id=h.manifest["payload"]["store_id"], **options)

    def assert_boundaries(self, report, *, external=False):
        self.assertEqual("supported", report["content_integrity"])
        self.assertEqual("matched_exported_tip", report["internal_checkpoint_status"])
        self.assertEqual("matched_prefix" if external else "not_provided", report["external_checkpoint_status"])
        self.assertEqual("consistent_with_retained_checkpoint_only" if external else "not_assessed",
                         report["rollback_assessment"])
        self.assertEqual("unresolved", report["completeness"])
        self.assertEqual("unresolved", report["latestness"])
        self.assertFalse(report["independent_custody"])
        self.assertEqual("not_established", report["azure_origin"])
        self.assertEqual("not_assessed", report["authority"])
        self.assertNotIn(SENSITIVE_SENTINEL, json.dumps(report))
        for field in ("safe", "pass", "prevented", "raw", "artifacts", "receipts", "public_key"):
            self.assertNotIn(field, report)

    def assert_all_signatures(self, package):
        for envelope in [package["manifest"], package["checkpoint"], *package["receipts"]]:
            verify_signature(envelope)


class PortableOriginalsAndTrust(PackTestCase):
    def test_complete_prefix_preserves_raw_bytes_and_legitimate_shared_hash_deduplication(self):
        h = self.harness()
        path, package, report = collected_pack(h)
        self.assert_all_signatures(package)
        self.assertEqual(3, report["receipt_count"])
        self.assertEqual(2, report["artifact_count"])
        self.assertEqual([1, 2, 3], [receipt["payload"]["sequence"] for receipt in package["receipts"]])
        originals = {item["artifact_sha256"]: artifact_bytes(item) for item in package["artifacts"]}
        self.assertEqual({digest(h.raw): h.raw, digest(BINARY_ORIGINAL): BINARY_ORIGINAL}, originals)
        self.assertEqual(len(h.raw) + len(BINARY_ORIGINAL), report["total_artifact_bytes"])
        self.assertEqual(sorted(originals), [item["artifact_sha256"] for item in package["artifacts"]])
        for receipt in package["receipts"]:
            p = receipt["payload"]
            self.assertEqual(len(originals[p["artifact_sha256"]]), p["artifact_size"])
        self.assertEqual(digest(path.read_bytes()), report["package_sha256"])
        self.assert_boundaries(report)

    def test_real_process_verifies_after_store_source_and_private_seed_are_removed(self):
        h = self.harness()
        h.collect("text-original")
        binary = private_write(h.root / "binary.raw", BINARY_ORIGINAL)
        h.collect("binary-original", path=binary)
        seed_file = private_write(h.root / "export-private-test-seed.bin", PUBLIC_TEST_SEED)
        public_file = private_write(h.root / "external-public-key.bin", PUBLIC_TEST_KEY)
        target = h.root / "portable.json"
        expected_id = h.manifest["payload"]["store_id"]
        pack.export_pack(h.store, target, trusted_public_key=public_file.read_bytes(),
                         private_key=seed_file.read_bytes(), expected_store_id=expected_id)
        shutil.rmtree(h.store)
        h.input.unlink()
        binary.unlink()
        seed_file.unlink()
        self.assertFalse(h.store.exists())
        self.assertFalse(seed_file.exists())
        result = standalone_verify(target, public_file, expected_id)
        self.assertEqual(0, result.returncode, result.stderr)
        observed = json.loads(result.stdout)
        self.assertEqual([], observed["store_modules_loaded"])
        self.assertEqual(2, observed["verification"]["receipt_count"])
        self.assert_boundaries(observed["verification"])
        for sensitive in (SENSITIVE_SENTINEL, PUBLIC_TEST_SEED.hex(), base64.b64encode(BINARY_ORIGINAL).decode()):
            self.assertNotIn(sensitive, result.stdout + result.stderr)

    def test_empty_binary_and_maximum_size_originals_have_exact_chunk_framing(self):
        for raw in (b"", b"\xff", bytes(range(256)) * 256):
            with self.subTest(size=len(raw)):
                h = self.harness(raw=raw)
                h.collect()
                _, package, report = export(h)
                item = package["artifacts"][0]
                self.assertEqual(raw, artifact_bytes(item))
                self.assertEqual(chunks(raw), item["base64_chunks"])
                self.assertEqual((len(raw) + CHUNK_BYTES - 1) // CHUNK_BYTES, len(item["base64_chunks"]))
                self.assertEqual(len(raw), item["artifact_size"])
                self.assertEqual(len(raw), report["total_artifact_bytes"])

    def test_wrong_external_public_key_cannot_be_replaced_by_pack_contents(self):
        h = self.harness()
        _, package, _ = collected_pack(h)
        wrong_public = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"OTHER PUBLIC PACK KEY").digest()).public_key().public_bytes_raw()
        with self.assertRaises(pack.PackError):
            pack.verify_pack(package, trusted_public_key=wrong_public,
                             expected_store_id=h.manifest["payload"]["store_id"])
        for field in ("public_key", "trusted_keys"):
            altered = copy.deepcopy(package)
            altered[field] = PUBLIC_TEST_KEY.hex()
            with self.subTest(field=field):
                with self.assertRaises(pack.PackError):
                    self.verify(h, altered)

    def test_expected_store_id_is_required_external_input_not_bootstrapped_from_manifest(self):
        h = self.harness()
        _, package, _ = collected_pack(h)
        with self.assertRaises(TypeError):
            pack.verify_pack(package, trusted_public_key=PUBLIC_TEST_KEY)
        for invalid in (None, "", "not-a-store-id", "0" * 32):
            with self.subTest(expected_id=invalid):
                with self.assertRaises(pack.PackError):
                    pack.verify_pack(package, trusted_public_key=PUBLIC_TEST_KEY, expected_store_id=invalid)

    def test_same_key_other_store_snapshot_is_rejected_under_original_expected_id(self):
        first, second = self.harness(), self.harness()
        _, first_package, _ = collected_pack(first)
        _, second_package, _ = collected_pack(second)
        self.assertNotEqual(first_package["manifest"]["payload"]["store_id"],
                            second_package["manifest"]["payload"]["store_id"])
        self.assert_all_signatures(second_package)
        self.assert_boundaries(self.verify(second, second_package))
        with self.assertRaises(pack.PackError):
            self.verify(first, second_package)


class ReceiptAndArtifactContradictions(PackTestCase):
    def test_signed_manifest_receipt_and_checkpoint_metadata_tamper_is_detected(self):
        h = self.harness()
        _, original, _ = collected_pack(h)
        for target in ("manifest", "receipt", "checkpoint"):
            with self.subTest(target=target):
                package = copy.deepcopy(original)
                envelope = package["receipts"][0] if target == "receipt" else package[target]
                envelope["payload"]["collector_id"] = "altered-synthetic-collector"
                with self.assertRaises(pack.PackError):
                    self.verify(h, package)

    def test_receipt_signature_corruption_is_detected(self):
        h = self.harness()
        _, package, _ = collected_pack(h)
        signature = package["receipts"][0]["signature"]
        package["receipts"][0]["signature"] = ("00" if signature[:2] != "00" else "01") + signature[2:]
        with self.assertRaises(pack.PackError):
            self.verify(h, package)

    def test_fresh_signatures_do_not_hide_duplicate_request_gap_store_or_time_conflicts(self):
        h = self.harness()
        _, original, _ = collected_pack(h)
        for mutation in ("duplicate-request", "sequence-gap", "foreign-store", "time-pair"):
            with self.subTest(mutation=mutation):
                package = copy.deepcopy(original)
                body = package["receipts"][1]["payload"]
                if mutation == "duplicate-request":
                    body["request_id"] = package["receipts"][0]["payload"]["request_id"]
                elif mutation == "sequence-gap":
                    body["sequence"] = 4
                elif mutation == "foreign-store":
                    body["store_id"] = "0" * 32
                else:
                    body["received_time"] -= 1
                resign_chain(package)
                self.assert_all_signatures(package)
                with self.assertRaises(pack.PackError):
                    self.verify(h, package)

    def test_missing_extra_duplicate_and_reordered_receipts_are_not_silently_reindexed(self):
        h = self.harness()
        _, original, _ = collected_pack(h)
        for mutation in ("missing-middle", "missing-tip", "duplicate", "extra", "reordered"):
            with self.subTest(mutation=mutation):
                package = copy.deepcopy(original)
                if mutation == "missing-middle":
                    package["receipts"].pop(1)
                elif mutation == "missing-tip":
                    package["receipts"].pop()
                elif mutation == "duplicate":
                    package["receipts"].insert(1, copy.deepcopy(package["receipts"][0]))
                elif mutation == "extra":
                    extra = copy.deepcopy(package["receipts"][-1])
                    extra["payload"].update(sequence=4, request_id="extra-request",
                                             previous_receipt_sha256=digest(canonical(package["receipts"][-1])))
                    package["receipts"].append(resign(extra))
                else:
                    package["receipts"][0], package["receipts"][1] = package["receipts"][1], package["receipts"][0]
                self.assert_all_signatures(package)
                with self.assertRaises(pack.PackError):
                    self.verify(h, package)

    def test_exact_artifact_set_rejects_missing_extra_duplicate_and_reordered_entries(self):
        h = self.harness()
        _, original, _ = collected_pack(h)
        for mutation in ("missing", "extra", "duplicate", "reordered"):
            with self.subTest(mutation=mutation):
                package = copy.deepcopy(original)
                if mutation == "missing":
                    package["artifacts"].pop()
                elif mutation == "extra":
                    raw = b"unreferenced synthetic original"
                    package["artifacts"].append({"artifact_sha256": digest(raw), "artifact_size": len(raw),
                                                  "base64_chunks": chunks(raw)})
                    package["artifacts"].sort(key=lambda item: item["artifact_sha256"])
                elif mutation == "duplicate":
                    package["artifacts"].append(copy.deepcopy(package["artifacts"][0]))
                    package["artifacts"].sort(key=lambda item: item["artifact_sha256"])
                else:
                    package["artifacts"].reverse()
                with self.assertRaises(pack.PackError):
                    self.verify(h, package)

    def test_raw_content_hash_size_and_receipt_binding_are_checked_independently(self):
        h = self.harness()
        _, original, _ = collected_pack(h)
        for mutation in ("raw-bytes", "artifact-size", "artifact-hash", "signed-receipt-size"):
            with self.subTest(mutation=mutation):
                package = copy.deepcopy(original)
                if mutation == "raw-bytes":
                    item = package["artifacts"][0]
                    original_raw = artifact_bytes(item)
                    item["base64_chunks"] = chunks(bytes([original_raw[0] ^ 1]) + original_raw[1:])
                elif mutation == "artifact-size":
                    package["artifacts"][0]["artifact_size"] += 1
                elif mutation == "artifact-hash":
                    package["artifacts"][0]["artifact_sha256"] = "sha256:" + "0" * 64
                    package["artifacts"].sort(key=lambda item: item["artifact_sha256"])
                else:
                    package["receipts"][0]["payload"]["artifact_size"] += 1
                    resign_chain(package)
                    self.assert_all_signatures(package)
                with self.assertRaises(pack.PackError):
                    self.verify(h, package)

    def test_noncanonical_base64_pad_bits_and_alternate_spellings_are_rejected(self):
        h = self.harness(raw=b"\xff")
        h.collect()
        _, original, _ = export(h)
        self.assertEqual(b"\xff", base64.b64decode("/x==", validate=True))
        self.assertNotEqual("/x==", base64.b64encode(b"\xff").decode())
        for encoded in ("/x==", "/w===", "/w", "/w==\n", "_w=="):
            with self.subTest(encoded=encoded):
                package = copy.deepcopy(original)
                package["artifacts"][0]["base64_chunks"] = [encoded]
                with self.assertRaises(pack.PackError):
                    self.verify(h, package)

    def test_chunk_boundaries_are_canonical_even_when_concatenated_original_is_unchanged(self):
        raw = b"x" * (CHUNK_BYTES + 1)
        h = self.harness(raw=raw)
        h.collect()
        _, original, _ = export(h)
        invalid = [
            [base64.b64encode(raw).decode()],
            [base64.b64encode(raw[:100]).decode(), base64.b64encode(raw[100:]).decode()],
            [*chunks(raw), ""],
        ]
        for changed_chunks in invalid:
            with self.subTest(chunk_lengths=[len(chunk) for chunk in changed_chunks]):
                self.assertEqual(raw, b"".join(base64.b64decode(chunk, validate=True) for chunk in changed_chunks))
                package = copy.deepcopy(original)
                package["artifacts"][0]["base64_chunks"] = changed_chunks
                with self.assertRaises(pack.PackError):
                    self.verify(h, package)
        empty = self.harness(raw=b"")
        empty.collect()
        _, empty_package, _ = export(empty)
        empty_package["artifacts"][0]["base64_chunks"] = [""]
        with self.assertRaises(pack.PackError):
            self.verify(empty, empty_package)


class CheckpointScope(PackTestCase):
    def test_internal_checkpoint_must_match_exact_exported_tip_not_an_older_prefix(self):
        h = self.harness()
        h.collect("first")
        older = h.checkpoint()
        h.collect("second")
        _, package, _ = export(h)
        self.assert_all_signatures(package)
        package["checkpoint"] = older
        self.assert_all_signatures(package)
        with self.assertRaises(pack.PackError):
            self.verify(h, package)

    def test_internal_checkpoint_is_not_an_external_witness(self):
        h = self.harness()
        _, package, _ = collected_pack(h)
        report = self.verify(h, package)
        self.assert_boundaries(report)
        # Caller explicitly supplying the same value is reported only as a
        # matched retained prefix; no latestness or independent-origin inference.
        with_external = self.verify(h, package, external_checkpoint=copy.deepcopy(package["checkpoint"]))
        self.assert_boundaries(with_external, external=True)

    def test_old_pack_absent_old_and_later_external_checkpoints_remain_distinct(self):
        h = self.harness()
        h.collect("first")
        older_checkpoint = h.checkpoint()
        _, old_package, _ = export(h, h.root / "old-pack.json")
        h.collect("second")
        later_checkpoint = h.checkpoint()
        _, current_package, _ = export(h, h.root / "current-pack.json")
        retained = private_json(h.root / "retained-later-checkpoint.json", later_checkpoint)
        self.assert_boundaries(self.verify(h, old_package))
        self.assert_boundaries(self.verify(h, old_package, external_checkpoint=older_checkpoint), external=True)
        self.assert_boundaries(self.verify(h, current_package, external_checkpoint=older_checkpoint), external=True)
        self.assert_boundaries(self.verify(h, current_package, external_checkpoint=later_checkpoint), external=True)
        with self.assertRaises(pack.PackError):
            self.verify(h, old_package, external_checkpoint=json.loads(retained.read_text()))

    def test_foreign_or_modified_external_checkpoint_cannot_anchor_a_pack(self):
        h, other = self.harness(), self.harness()
        _, package, _ = collected_pack(h)
        other.collect()
        modified = h.checkpoint()
        modified["payload"]["receipt_sha256"] = "sha256:" + "0" * 64
        for checkpoint in (other.checkpoint(), modified):
            with self.subTest(store_id=checkpoint["payload"]["store_id"]):
                with self.assertRaises(pack.PackError):
                    self.verify(h, package, external_checkpoint=checkpoint)


class JSONLimitsAndPublication(PackTestCase):
    def test_duplicate_json_keys_are_rejected_at_top_and_nested_receipt_levels(self):
        h = self.harness()
        _, package, _ = collected_pack(h)
        encoded = canonical(package).decode()
        duplicated = [
            '{"schema":"experimental-cloud-custody-pack-v0",' + encoded[1:],
            encoded.replace('"request_id":', '"request_id":"duplicate-key","request_id":', 1),
        ]
        for document in duplicated:
            with self.subTest(length=len(document)):
                json.loads(document)  # Valid ordinary JSON; strict duplicate-key rejection is required.
                with self.assertRaises(pack.PackError):
                    self.verify(h, document)

    def test_one_mib_input_boundary_counts_original_serialized_bytes(self):
        h = self.harness()
        _, package, _ = collected_pack(h)
        encoded = canonical(package)
        at_limit = encoded + b" " * (MAX_PACK_BYTES - len(encoded))
        self.assertEqual(MAX_PACK_BYTES, len(at_limit))
        self.assert_boundaries(self.verify(h, at_limit))
        with self.assertRaises(pack.PackError):
            self.verify(h, at_limit + b" ")

    def test_receipt_limit_accepts_256_validly_signed_records_and_rejects_257(self):
        h = self.harness(raw=b"bounded synthetic original")
        h.collect()
        _, package, _ = export(h)
        first = package["receipts"][0]
        package["receipts"] = []
        for index in range(256):
            record = copy.deepcopy(first)
            record["payload"].update(sequence=index + 1, request_id="synthetic-request-%d" % index)
            package["receipts"].append(record)
        resign_chain(package)
        self.assert_all_signatures(package)
        self.assertEqual(256, self.verify(h, package)["receipt_count"])
        extra = copy.deepcopy(package["receipts"][-1])
        extra["payload"].update(sequence=257, request_id="synthetic-request-256")
        package["receipts"].append(extra)
        resign_chain(package)
        with self.assertRaises(pack.PackError):
            self.verify(h, package)

    def test_oversize_export_rejects_the_full_snapshot_without_output_or_truncation(self):
        h = self.harness(raw=b"unused source")
        for index in range(13):
            source = private_write(h.root / ("large-%d.raw" % index), bytes([index]) * 65_536)
            h.collect("large-request-%d" % index, path=source)
        before = tree_snapshot(h.store)
        output = h.root / "oversize-pack.json"
        with self.assertRaises(pack.PackError):
            export(h, output)
        self.assertFalse(output.exists())
        self.assertEqual(before, tree_snapshot(h.store))
        self.assertEqual(13, h.audit()["record_count"])

    def test_private_output_no_overwrite_and_managed_store_exclusion(self):
        h = self.harness()
        h.collect()
        previous = os.umask(0)
        try:
            output, _, _ = export(h)
        finally:
            os.umask(previous)
        self.assertEqual(0o600, stat.S_IMODE(output.stat().st_mode))
        original = output.read_bytes()
        link = h.root / "pack-link.json"
        link.symlink_to(output)
        for target in (output, link, h.store / "new-pack.json"):
            with self.subTest(target=target.name):
                with self.assertRaises(pack.PackError):
                    export(h, target)
        self.assertEqual(original, output.read_bytes())
        self.assertFalse((h.store / "new-pack.json").exists())

    def test_export_checks_all_committed_originals_before_publishing(self):
        h = self.harness()
        h.collect("first")
        h.collect("second")
        h.blob_path().unlink()
        before = tree_snapshot(h.store)
        target = h.root / "missing-original-pack.json"
        with self.assertRaises(pack.PackError):
            export(h, target)
        self.assertFalse(target.exists())
        self.assertEqual(before, tree_snapshot(h.store))

    def test_pack_remains_inert_and_does_not_extract_supplied_paths(self):
        h = self.harness(raw=b"../../synthetic-path-is-only-original-content")
        h.collect()
        _, package, _ = export(h)
        before = tree_snapshot(h.root)
        self.assert_boundaries(self.verify(h, package))
        altered = copy.deepcopy(package)
        altered["artifacts"][0]["path"] = "../../synthetic-must-not-be-created.txt"
        with self.assertRaises(pack.PackError):
            self.verify(h, altered)
        self.assertEqual(before, tree_snapshot(h.root))

    def test_export_holds_the_same_cross_process_lock_through_snapshot_and_publication(self):
        h = self.harness()
        h.collect()
        stages = []
        probe = r'''
import fcntl
import os
import sys
fd = os.open(sys.argv[1], os.O_RDWR | os.O_NOFOLLOW)
try:
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("held")
    else:
        print("unlocked")
finally:
    os.close(fd)
'''
        def hook(stage, metadata):
            if stage in ("snapshot_locked", "before_publish", "after_publish"):
                process = subprocess.run([*PYTHON, "-c", probe, str(h.store / "store.lock")],
                                         capture_output=True, text=True, timeout=10, check=False)
                self.assertEqual(0, process.returncode, process.stderr)
                self.assertEqual("held", process.stdout.strip(), stage)
                stages.append(stage)
        export(h, hook=hook)
        self.assertEqual(["snapshot_locked", "before_publish", "after_publish"], stages)


class PackCLI(PackTestCase):
    def command(self, h, operation, *args):
        public_file = h.root / "public-key.bin"
        private_file = h.root / "private-test-seed.bin"
        if not public_file.exists():
            private_write(public_file, PUBLIC_TEST_KEY)
        if operation == "export" and not private_file.exists():
            private_write(private_file, PUBLIC_TEST_SEED)
        command = [*PYTHON, str(ROOT / "custody_pack.py"), operation,
                   "--public-key-file", str(public_file),
                   "--expected-store-id", h.manifest["payload"]["store_id"]]
        if operation == "export":
            command.extend(("--store", str(h.store), "--private-key-file", str(private_file)))
        command.extend(map(str, args))
        return subprocess.run(command, capture_output=True, text=True, timeout=20, check=False)

    def test_cli_export_and_store_free_verify_emit_only_metadata(self):
        h = self.harness()
        h.collect()
        target = h.root / "cli-pack.json"
        exported = self.command(h, "export", "--out", target)
        self.assertEqual(0, exported.returncode, exported.stderr)
        self.assert_boundaries(json.loads(exported.stdout))
        shutil.rmtree(h.store)
        (h.root / "private-test-seed.bin").unlink()
        verified = self.command(h, "verify", "--pack", target)
        self.assertEqual(0, verified.returncode, verified.stderr)
        self.assert_boundaries(json.loads(verified.stdout))
        for result in (exported, verified):
            for sensitive in (SENSITIVE_SENTINEL, PUBLIC_TEST_SEED.hex(), base64.b64encode(h.raw).decode()):
                self.assertNotIn(sensitive, result.stdout + result.stderr)
            self.assertNotIn('"base64_chunks"', result.stdout)
        self.assertEqual(0o600, stat.S_IMODE(target.stat().st_mode))

    def test_cli_rejection_does_not_echo_raw_sensitive_input_or_overwrite_output(self):
        h = self.harness()
        h.collect()
        existing = private_write(h.root / "existing.json", b"unchanged output")
        rejected_export = self.command(h, "export", "--out", existing)
        self.assertEqual(2, rejected_export.returncode)
        self.assertEqual(b"unchanged output", existing.read_bytes())
        invalid = private_write(h.root / "invalid-pack.json", (
            '{"private":"' + SENSITIVE_SENTINEL + '","private":2}').encode())
        rejected_verify = self.command(h, "verify", "--pack", invalid)
        self.assertEqual(2, rejected_verify.returncode)
        for result in (rejected_export, rejected_verify):
            self.assertNotIn(SENSITIVE_SENTINEL, result.stdout + result.stderr)
            self.assertNotIn(PUBLIC_TEST_SEED.hex(), result.stdout + result.stderr)

    def test_pack_demo_executes_portable_processes_and_reports_only_bounded_results(self):
        process = subprocess.run([*PYTHON, str(ROOT / "run_pack_demo.py")], capture_output=True,
                                 text=True, timeout=30, check=False)
        self.assertEqual(0, process.returncode, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(5, report["scenario_count"])
        self.assertEqual(report["scenario_count"], len(report["scenarios"]))
        self.assertFalse(report["independent_custody_established"])
        self.assertEqual(0, report["live_cloud_calls"])
        scenarios = {item["scenario"]: item for item in report["scenarios"]}
        portable = scenarios["separate_process_without_original_store_or_private_seed"]
        self.assertFalse(portable["original_store_available"])
        self.assertFalse(portable["private_seed_file_available"])
        self.assertEqual([], portable["store_modules_loaded"])
        self.assert_boundaries(portable["verification"])
        checkpoint = scenarios["older_pack_and_external_checkpoint_scope"]
        self.assertEqual("not_assessed", checkpoint["without_external_checkpoint"])
        self.assertEqual("unresolved", checkpoint["matching_prefix_latestness"])
        self.assertEqual(2, checkpoint["later_witness_rejection"]["exit_code"])
        for sensitive in (SENSITIVE_SENTINEL, PUBLIC_TEST_SEED.hex(), base64.b64encode(BINARY_ORIGINAL).decode()):
            self.assertNotIn(sensitive, process.stdout + process.stderr)
        for misleading in ("safe", "pass", "prevented", "conformant"):
            self.assertNotIn(misleading, report)


if __name__ == "__main__":
    unittest.main()
