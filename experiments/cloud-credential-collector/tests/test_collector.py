"""Independent native-filesystem/process tests for the bounded local collector.

All data and signing seeds are PUBLIC synthetic fixtures. Separate processes
share one local operator; they do not establish independent custody. The tests
distinguish an externally witnessed checkpoint from a merely self-consistent
chain, including the otherwise indistinguishable coherent-prefix rollback.
"""
from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import sqlite3
import stat
import subprocess
import sys
import tempfile
import time
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collector_support import (
    COLLECTOR_ID, CUSTODY_DOMAIN, Harness, KEY_ID, KEYVAULT_ADAPTER, PUBLIC_TEST_KEY,
    PUBLIC_TEST_SEED, PYTHON, ROOT, SENSITIVE_SENTINEL, SIGNIN_ADAPTER, TENANT, VAULT,
    canonical, context, digest, load_collector, private_json, private_write, raw_record,
    tree_snapshot,
)

collector = load_collector()


class CollectorTestCase(unittest.TestCase):
    def harness(self, **options):
        result = Harness(**options)
        self.addCleanup(result.close)
        return result

    def assert_signature(self, envelope):
        self.assertEqual(KEY_ID, envelope["key_id"])
        signed = {key: envelope[key] for key in ("key_id", "payload")}
        Ed25519PublicKey.from_public_bytes(PUBLIC_TEST_KEY).verify(
            bytes.fromhex(envelope["signature"]), CUSTODY_DOMAIN + canonical(signed))

    def assert_boundaries(self, audit):
        self.assertEqual("unresolved", audit["completeness"])
        self.assertFalse(audit["independent_custody"])
        for misleading in ("safe", "pass", "prevented", "rollback_impossible", "azure_verified"):
            self.assertNotIn(misleading, audit)

    def assert_barrier(self, worker, stage):
        observed = worker.event()
        self.assertEqual("barrier", observed["event"])
        self.assertEqual(stage, observed["stage"])
        self.assertNotIn(SENSITIVE_SENTINEL, json.dumps(observed))
        self.assertEqual(-signal.SIGKILL, worker.kill())


class OriginalBytesAndTrust(CollectorTestCase):
    def test_signed_receipt_commits_exact_original_bytes_including_whitespace(self):
        h = self.harness()
        before = time.time_ns()
        receipt = h.collect()
        after = time.time_ns()
        self.assert_signature(receipt)
        p = receipt["payload"]
        self.assertEqual("experimental-cloud-custody-receipt-v0", p["schema"])
        self.assertEqual(digest(h.raw), p["artifact_sha256"])
        self.assertEqual(len(h.raw), p["artifact_size"])
        self.assertEqual(h.context, p["context"])
        self.assertEqual(1, p["sequence"])
        self.assertIsNone(p["previous_receipt_sha256"])
        self.assertLessEqual(before, int(p["received_time_ns"]))
        self.assertLessEqual(int(p["received_time_ns"]), after)
        self.assertEqual((int(p["received_time_ns"]) + 999_999_999) // 1_000_000_000, p["received_time"])
        self.assertEqual(h.raw, h.blob_path().read_bytes())
        self.assertNotEqual(digest(canonical(json.loads(h.raw))), p["artifact_sha256"])

    def test_manifest_checkpoint_and_receipts_use_the_external_pinned_key(self):
        h = self.harness()
        self.assert_signature(h.manifest)
        receipt = h.collect()
        checkpoint = h.checkpoint()
        self.assert_signature(receipt)
        self.assert_signature(checkpoint)
        self.assertEqual(digest(canonical(receipt)), checkpoint["payload"]["receipt_sha256"])
        wrong_key = Ed25519PrivateKey.from_private_bytes(hashlib.sha256(b"OTHER PUBLIC TEST KEY").digest()).public_key().public_bytes_raw()
        with self.assertRaises(collector.CollectorError):
            with collector.Collector(h.store, trusted_public_key=wrong_key) as store:
                store.audit()

    def test_initialization_rejects_a_private_key_not_matching_the_external_pin(self):
        h = self.harness(initialize=False)
        wrong_seed = hashlib.sha256(b"OTHER PUBLIC SYNTHETIC PRIVATE SEED").digest()
        with self.assertRaises(collector.CollectorError):
            collector.initialize_store(h.store, collector_id=COLLECTOR_ID, key_id=KEY_ID,
                                       private_key=wrong_seed, trusted_public_key=PUBLIC_TEST_KEY)

    def test_subsecond_receipt_rounds_up_without_backdating_the_bridge(self):
        h = self.harness()
        exact_ns = (time.time_ns() // 1_000_000_000 + 1) * 1_000_000_000 + 1
        receipt = h.collect(clock_ns=lambda: exact_ns)
        self.assertEqual(str(exact_ns), receipt["payload"]["received_time_ns"])
        self.assertEqual(exact_ns // 1_000_000_000 + 1, receipt["payload"]["received_time"])

    def test_intake_accepts_arbitrary_original_bytes_without_claiming_native_validity(self):
        for raw in (b"", b"not JSON\x00\xff\xfe", b'{"duplicate":1,"duplicate":2}'):
            with self.subTest(raw_digest=digest(raw)):
                h = self.harness(raw=raw)
                receipt = h.collect()
                self.assertEqual(digest(raw), receipt["payload"]["artifact_sha256"])
                self.assertEqual(1, h.audit()["record_count"])
                target = h.root / "native.json"
                with self.assertRaises(collector.CollectorError):
                    with h.open() as store:
                        store.export_native("request-1", target)
                self.assertFalse(target.exists())

    def test_oversize_original_is_rejected_without_a_committed_record(self):
        h = self.harness(raw=b"x" * 65_537)
        with self.assertRaises(collector.CollectorError):
            h.collect()
        self.assertEqual(0, h.audit()["record_count"])

    def test_unknown_adapter_is_preserved_at_intake_but_cannot_be_native_exported(self):
        h = self.harness(source_context=context("synthetic-unsupported-adapter"))
        receipt = h.collect()
        self.assertEqual("synthetic-unsupported-adapter", receipt["payload"]["context"]["adapter"])
        target = h.root / "native.json"
        with self.assertRaises(collector.CollectorError):
            with h.open() as store:
                store.export_native("request-1", target)
        self.assertFalse(target.exists())

    def test_caller_context_and_input_are_frozen_before_publication(self):
        h = self.harness()
        original_context = copy.deepcopy(h.context)
        original_raw = h.raw
        reached = []
        def hook(stage, metadata):
            if stage == "after_staging_fsync":
                reached.append(stage)
                h.context["issuer"] = "mutated-after-staging"
                h.input.write_bytes(b"source changed after staging")
        receipt = h.collect(hook=hook)
        self.assertEqual(["after_staging_fsync"], reached)
        self.assertEqual(original_context, receipt["payload"]["context"])
        self.assertEqual(digest(original_raw), receipt["payload"]["artifact_sha256"])
        self.assertEqual(original_raw, h.blob_path(original_raw).read_bytes())


class IdempotencyAndRealProcesses(CollectorTestCase):
    def test_restart_and_repeat_return_the_original_receipt_and_time(self):
        h = self.harness()
        receipt = h.collect()
        later = int(receipt["payload"]["received_time_ns"]) + 100_000_000_000
        repeated = h.collect(clock_ns=lambda: later)
        self.assertEqual(receipt, repeated)
        # A new interpreter reopens the actual SQLite/filesystem state.
        self.assertEqual(receipt, h.job("receipt").result())
        self.assertEqual(receipt, h.job("collect").result())
        self.assertEqual(1, h.audit()["record_count"])

    def test_same_id_with_changed_original_or_context_rejects_without_repair(self):
        h = self.harness()
        receipt = h.collect()
        before = tree_snapshot(h.store)
        alternate = private_write(h.root / "alternate.raw", h.raw + b" ")
        changed_context = {**h.context, "issuer": "different-source-context"}
        for path, source in ((alternate, h.context), (h.input, changed_context)):
            with self.subTest(path=path.name):
                with self.assertRaises(collector.CollectorError):
                    h.collect(path=path, source_context=source)
                self.assertEqual(before, tree_snapshot(h.store))
        with h.open(writable=False) as store:
            self.assertEqual(receipt, store.get_receipt("request-1"))

    def test_separate_concurrent_processes_commit_one_idempotent_request(self):
        h = self.harness()
        workers = [h.job(start_barrier=True), h.job(start_barrier=True)]
        for worker in workers:
            self.assertEqual("ready", worker.event()["event"])
        for worker in workers:
            worker.release()
        results = [worker.result() for worker in workers]
        self.assertEqual(results[0], results[1])
        self.assertEqual(1, h.audit()["record_count"])
        next_receipt = h.collect("request-2")
        self.assertEqual(2, next_receipt["payload"]["sequence"])
        self.assertEqual(digest(canonical(results[0])), next_receipt["payload"]["previous_receipt_sha256"])

    def test_concurrent_same_id_different_bytes_has_one_commit_and_one_conflict(self):
        h = self.harness()
        alternate = private_write(h.root / "alternate.raw", h.raw + b" ")
        workers = [h.job(start_barrier=True), h.job(path=alternate, start_barrier=True)]
        for worker in workers:
            self.assertEqual("ready", worker.event()["event"])
        for worker in workers:
            worker.release()
        events = [worker.event() for worker in workers]
        codes = [worker.proc.wait(timeout=10) for worker in workers]
        self.assertEqual([0, 2], sorted(codes))
        self.assertEqual(["error", "result"], sorted(event["event"] for event in events))
        self.assertEqual(1, h.audit()["record_count"])

    def test_sigkill_before_commit_leaves_no_receipt_and_retry_commits_once(self):
        h = self.harness()
        worker = h.job(barrier="before_commit")
        self.assert_barrier(worker, "before_commit")
        audit = h.audit()
        self.assertEqual(0, audit["record_count"])
        with h.open(writable=False) as store:
            with self.assertRaises(collector.CollectorError):
                store.get_receipt("request-1")
        receipt = h.job().result()
        self.assertEqual(1, receipt["payload"]["sequence"])
        self.assertEqual(receipt, h.job().result())
        self.assertEqual(1, h.audit()["record_count"])

    def test_sigkill_after_commit_before_response_recovers_identical_receipt(self):
        h = self.harness()
        worker = h.job(barrier="after_commit")
        self.assert_barrier(worker, "after_commit")
        self.assertEqual(1, h.audit()["record_count"])
        original = h.job("receipt").result()
        self.assertEqual(original, h.job().result())
        self.assertEqual(1, h.audit()["record_count"])

    def test_sigkill_at_staging_and_blob_publication_boundaries_keeps_commits_honest(self):
        for stage in ("after_staging_fsync", "after_blob_publish"):
            with self.subTest(stage=stage):
                h = self.harness()
                self.assert_barrier(h.job(barrier=stage), stage)
                audit = h.audit()
                self.assertEqual(0, audit["record_count"])
                if stage == "after_staging_fsync":
                    self.assertGreaterEqual(audit["staging_file_count"], 1)
                else:
                    self.assertGreaterEqual(audit["orphan_blob_count"], 1)
                receipt = h.job().result()
                self.assertEqual(digest(h.raw), receipt["payload"]["artifact_sha256"])
                self.assertEqual(1, h.audit()["record_count"])


class FilesystemAndExport(CollectorTestCase):
    def test_private_store_and_export_modes_do_not_depend_on_callers_umask(self):
        previous = os.umask(0)
        try:
            h = self.harness()
            h.collect()
            target = h.root / "native.json"
            with h.open() as store:
                store.export_native("request-1", target)
        finally:
            os.umask(previous)
        for path in [h.store, *h.store.rglob("*")]:
            mode = stat.S_IMODE(path.lstat().st_mode)
            self.assertEqual(0o700 if path.is_dir() else 0o600, mode, path.name)
        self.assertEqual(0o600, stat.S_IMODE(target.stat().st_mode))

    def test_native_export_preserves_stored_raw_and_receipt_after_source_deletion(self):
        h = self.harness()
        receipt = h.collect()
        h.input.unlink()
        target = h.root / "native.json"
        with h.open() as store:
            summary = store.export_native("request-1", target)
        envelope = json.loads(target.read_text(encoding="utf-8"))
        p = envelope["payload"]
        self.assertEqual(h.raw, p["body"]["raw"].encode("utf-8"))
        self.assertEqual(digest(h.raw), p["body"]["raw_sha256"])
        self.assertIsNone(p["body"]["claimed_normalized"])
        self.assertIsNone(p["event_time"])
        self.assertIsNone(p["available_time"])
        self.assertEqual(receipt["payload"]["received_time"], p["received_time"])
        self.assertEqual("custody:" + digest(canonical(receipt)), p["record_id"])
        self.assertEqual(digest(canonical(receipt)), summary["custody_receipt_sha256"])
        self.assertEqual(digest(canonical(envelope)), summary["native_envelope_sha256"])
        self.assertNotIn(SENSITIVE_SENTINEL, json.dumps(summary))
        Ed25519PublicKey.from_public_bytes(PUBLIC_TEST_KEY).verify(
            bytes.fromhex(envelope["signature"]), b"VSO experimental cloud evidence v0\x00" + canonical(
                {key: envelope[key] for key in ("key_id", "payload")}))

    def test_export_never_overwrites_existing_file_or_symlink_target(self):
        h = self.harness()
        h.collect()
        target = private_write(h.root / "existing.json", b"existing private output")
        link = h.root / "output-link.json"
        link.symlink_to(target)
        for output in (target, link):
            with self.subTest(output=output.name):
                with self.assertRaises(collector.CollectorError):
                    with h.open() as store:
                        store.export_native("request-1", output)
        self.assertEqual(b"existing private output", target.read_bytes())

    def test_input_symlink_hardlink_directory_and_fifo_are_rejected(self):
        for kind in ("symlink", "hardlink", "directory", "fifo"):
            with self.subTest(kind=kind):
                h = self.harness()
                path = h.root / ("bad-" + kind)
                if kind == "symlink":
                    path.symlink_to(h.input)
                elif kind == "hardlink":
                    os.link(h.input, path)
                elif kind == "directory":
                    path.mkdir(mode=0o700)
                else:
                    os.mkfifo(path, 0o600)
                with self.assertRaises(collector.CollectorError):
                    h.collect(path=path)
                self.assertEqual(0, h.audit()["record_count"])

    def test_input_ancestor_symlink_and_traversal_are_rejected(self):
        h = self.harness()
        real = h.root / "real-input-dir"
        real.mkdir(mode=0o700)
        nested = private_write(real / "source.raw", h.raw)
        link = h.root / "linked-input-dir"
        link.symlink_to(real, target_is_directory=True)
        for path in (link / nested.name, str(real) + "/../source.raw", str(h.input) + "\x00ignored"):
            with self.subTest(path=str(path)):
                with self.assertRaises(collector.CollectorError):
                    h.collect(path=path)
        self.assertEqual(0, h.audit()["record_count"])

    def test_store_symlink_ancestor_non_directory_and_traversal_are_rejected(self):
        h = self.harness()
        direct = h.root / "store-link"
        direct.symlink_to(h.store, target_is_directory=True)
        ancestor = h.root / "root-link"
        ancestor.symlink_to(h.root, target_is_directory=True)
        regular = private_write(h.root / "not-a-directory", b"x")
        for path in (direct, ancestor / "store", regular, str(h.store) + "/../store"):
            with self.subTest(path=str(path)):
                with self.assertRaises(collector.CollectorError):
                    with collector.Collector(path, trusted_public_key=PUBLIC_TEST_KEY) as store:
                        store.audit()

    def test_public_store_directory_mode_is_rejected(self):
        h = self.harness()
        h.store.chmod(0o755)
        with self.assertRaises(collector.CollectorError):
            h.audit()

    def test_public_private_artifact_modes_are_rejected_without_chmod_repair(self):
        for artifact in ("database", "blob", "lock"):
            with self.subTest(artifact=artifact):
                h = self.harness()
                h.collect()
                path = h.db_path() if artifact == "database" else (
                    h.blob_path() if artifact == "blob" else h.store / "store.lock")
                path.chmod(0o644)
                before = tree_snapshot(h.store)
                with self.assertRaises(collector.CollectorError):
                    h.audit()
                self.assertEqual(before, tree_snapshot(h.store))

    def test_lock_symlink_hardlink_and_fifo_are_rejected(self):
        for kind in ("symlink", "hardlink", "fifo"):
            with self.subTest(kind=kind):
                h = self.harness()
                lock = h.store / "store.lock"
                outside = private_write(h.root / "outside-lock", b"")
                lock.unlink()
                if kind == "symlink":
                    lock.symlink_to(outside)
                elif kind == "hardlink":
                    os.link(outside, lock)
                else:
                    os.mkfifo(lock, 0o600)
                with self.assertRaises(collector.CollectorError):
                    h.audit()

    def test_malformed_context_and_request_ids_cannot_create_receipts(self):
        h = self.harness()
        for request_id, source in (("", h.context), ("x" * 257, h.context), (True, h.context),
                                   ("request-1", {**h.context, "available_time": 1}),
                                   ("request-1", {**h.context, "tenant_id": None})):
            with self.subTest(request_id=str(request_id)[:30], source_keys=sorted(source)):
                with self.assertRaises(collector.CollectorError):
                    h.collect(request_id=request_id, source_context=source)
        self.assertEqual(0, h.audit()["record_count"])


class CorruptionAndCheckpoints(CollectorTestCase):
    def test_reinitialization_preserves_intact_identity_and_cannot_repair_missing_managed_state(self):
        def initialize(h):
            return collector.initialize_store(h.store, collector_id=COLLECTOR_ID, key_id=KEY_ID,
                                              private_key=PUBLIC_TEST_SEED, trusted_public_key=PUBLIC_TEST_KEY)
        intact = self.harness()
        original_receipt = intact.collect()
        original_tree = tree_snapshot(intact.store)
        self.assertEqual(intact.manifest, initialize(intact))
        self.assertEqual(original_tree, tree_snapshot(intact.store))
        with intact.open(writable=False) as store:
            self.assertEqual(original_receipt, store.get_receipt("request-1"))
        for missing in ("index.sqlite3", "blobs", "staging", "store.lock"):
            with self.subTest(missing=missing):
                h = self.harness()
                h.collect()
                target = h.store / missing
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                damaged_tree = tree_snapshot(h.store)
                with self.assertRaises(collector.CollectorError):
                    initialize(h)
                self.assertEqual(damaged_tree, tree_snapshot(h.store))

    def test_committed_raw_tamper_or_deletion_is_detected_without_auto_repair(self):
        for mutation in ("alter", "delete"):
            with self.subTest(mutation=mutation):
                h = self.harness()
                h.collect()
                blob = h.blob_path()
                if mutation == "alter":
                    blob.write_bytes(b"altered committed bytes")
                else:
                    blob.unlink()
                before = tree_snapshot(h.store)
                with self.assertRaises(collector.CollectorError):
                    h.audit()
                with self.assertRaises(collector.CollectorError):
                    h.collect()
                self.assertEqual(before, tree_snapshot(h.store))

    def test_raw_blob_symlink_and_hardlink_replacements_are_rejected(self):
        for mutation in ("symlink", "hardlink"):
            with self.subTest(mutation=mutation):
                h = self.harness()
                h.collect()
                blob = h.blob_path()
                outside = private_write(h.root / "outside-original.raw", h.raw)
                blob.unlink()
                if mutation == "symlink":
                    blob.symlink_to(outside)
                else:
                    os.link(outside, blob)
                with self.assertRaises(collector.CollectorError):
                    h.audit()
                self.assertEqual(h.raw, outside.read_bytes())

    def test_missing_or_non_sqlite_index_is_not_recreated(self):
        for mutation in ("delete", "alter"):
            with self.subTest(mutation=mutation):
                h = self.harness()
                h.collect()
                database = h.db_path()
                if mutation == "delete":
                    database.unlink()
                else:
                    database.write_bytes(b"not the original SQLite index")
                before = tree_snapshot(h.store)
                with self.assertRaises(collector.CollectorError):
                    h.audit()
                self.assertEqual(before, tree_snapshot(h.store))

    def test_database_symlink_hardlink_and_fifo_replacements_are_rejected(self):
        for mutation in ("symlink", "hardlink", "fifo"):
            with self.subTest(mutation=mutation):
                h = self.harness()
                h.collect()
                database = h.db_path()
                outside = h.root / "outside.sqlite"
                shutil.copy2(database, outside)
                database.unlink()
                if mutation == "symlink":
                    database.symlink_to(outside)
                elif mutation == "hardlink":
                    os.link(outside, database)
                else:
                    os.mkfifo(database, 0o600)
                with self.assertRaises(collector.CollectorError):
                    h.audit()

    def test_signed_receipt_or_manifest_corruption_is_detected_without_repair(self):
        for target in ("receipt", "manifest"):
            with self.subTest(target=target):
                h = self.harness()
                h.collect()
                with sqlite3.connect(h.db_path()) as database:
                    if target == "receipt":
                        envelope = json.loads(database.execute("SELECT receipt_json FROM receipts WHERE sequence=1").fetchone()[0])
                    else:
                        envelope = json.loads(database.execute("SELECT value FROM metadata WHERE key='manifest'").fetchone()[0])
                    signature = envelope["signature"]
                    envelope["signature"] = ("00" if signature[:2] != "00" else "01") + signature[2:]
                    if target == "receipt":
                        database.execute("UPDATE receipts SET receipt_json=? WHERE sequence=1", (canonical(envelope).decode(),))
                    else:
                        database.execute("UPDATE metadata SET value=? WHERE key='manifest'", (canonical(envelope).decode(),))
                before = tree_snapshot(h.store)
                with self.assertRaises(collector.CollectorError):
                    h.audit()
                with self.assertRaises(collector.CollectorError):
                    h.collect()
                self.assertEqual(before, tree_snapshot(h.store))

    def test_index_metadata_cannot_disagree_with_the_signed_receipt(self):
        mutations = {
            "artifact_sha256": "sha256:" + "0" * 64,
            "artifact_size": 1,
            "context_json": "{}",
            "received_time_ns": "1",
            "receipt_sha256": "sha256:" + "1" * 64,
        }
        for column, value in mutations.items():
            with self.subTest(column=column):
                h = self.harness()
                h.collect()
                with sqlite3.connect(h.db_path()) as database:
                    # Column names are the fixed test vector set above, never input.
                    database.execute("UPDATE receipts SET " + column + "=? WHERE sequence=1", (value,))
                before = tree_snapshot(h.store)
                with self.assertRaises(collector.CollectorError):
                    h.audit()
                self.assertEqual(before, tree_snapshot(h.store))

    def test_missing_referenced_receipt_is_detected_but_is_not_confused_with_coherent_prefix(self):
        h = self.harness()
        h.collect()
        h.collect("request-2")
        with sqlite3.connect(h.db_path()) as database:
            database.execute("DELETE FROM receipts WHERE sequence=1")
        before = tree_snapshot(h.store)
        with self.assertRaises(collector.CollectorError):
            h.audit()
        self.assertEqual(before, tree_snapshot(h.store))

    def test_missing_manifest_is_not_recreated_as_a_new_store(self):
        h = self.harness()
        h.collect()
        with sqlite3.connect(h.db_path()) as database:
            database.execute("DELETE FROM metadata WHERE key='manifest'")
        before = tree_snapshot(h.store)
        with self.assertRaises(collector.CollectorError):
            h.audit()
        self.assertEqual(before, tree_snapshot(h.store))

    def test_old_checkpoint_matches_a_valid_extension_without_proving_universal_completeness(self):
        h = self.harness()
        h.collect()
        old_checkpoint = h.checkpoint()
        h.collect("request-2")
        audit = h.audit(checkpoint=old_checkpoint)
        self.assertEqual("matched", audit["checkpoint_status"])
        self.assertEqual("consistent_with_retained_checkpoint_only", audit["rollback_assessment"])
        self.assertEqual(2, audit["record_count"])
        self.assertEqual(2, audit["head_sequence"])
        self.assert_boundaries(audit)

    def test_coherent_prefix_or_old_sqlite_is_not_rollback_assessed_without_a_checkpoint(self):
        for representation in ("whole-prefix", "sqlite-prefix"):
            with self.subTest(representation=representation):
                h = self.harness()
                h.collect()
                old_checkpoint = h.checkpoint()
                snapshot = h.root / "old-prefix"
                shutil.copytree(h.store, snapshot)
                database_relative = h.db_path().relative_to(h.store)
                alternate = private_write(h.root / "second-source.raw", h.raw + b" ")
                h.collect("request-2", path=alternate)
                later_checkpoint = h.checkpoint()
                witness = private_json(h.root / "separately-retained-later-checkpoint.json", later_checkpoint)
                # Both copies are actual closed SQLite/filesystem snapshots.
                if representation == "whole-prefix":
                    rolled_back = snapshot
                else:
                    rolled_back = h.root / "sqlite-rolled-back"
                    shutil.copytree(h.store, rolled_back)
                    shutil.copy2(snapshot / database_relative, rolled_back / database_relative)
                with collector.Collector(rolled_back, trusted_public_key=PUBLIC_TEST_KEY) as store:
                    audit = store.audit()
                    self.assertEqual(1, audit["record_count"])
                    self.assertEqual("supported", audit["local_integrity"])
                    self.assertEqual("not_provided", audit["checkpoint_status"])
                    self.assertEqual("not_assessed", audit["rollback_assessment"])
                    self.assert_boundaries(audit)
                    self.assertEqual("matched", store.audit(checkpoint=old_checkpoint)["checkpoint_status"])
                    with self.assertRaises(collector.CollectorError):
                        store.audit(checkpoint=json.loads(witness.read_text(encoding="utf-8")))

    def test_checkpoint_from_another_store_is_rejected_even_under_same_public_key(self):
        first = self.harness()
        second = self.harness()
        first.collect()
        second.collect()
        with self.assertRaises(collector.CollectorError):
            first.audit(checkpoint=second.checkpoint())


class ProductionCLI(CollectorTestCase):
    def run_cli(self, h, operation, *arguments):
        public_path = h.root / "public-test-key.bin"
        private_path = h.root / "public-synthetic-test-seed.bin"
        if not public_path.exists():
            private_write(public_path, PUBLIC_TEST_KEY)
            private_write(private_path, PUBLIC_TEST_SEED)
        command = [*PYTHON, str(ROOT / "collector.py"), operation, "--store", str(h.store),
                   "--public-key-file", str(public_path)]
        if operation != "audit":
            command.extend(("--private-key-file", str(private_path)))
        command.extend(map(str, arguments))
        return subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)

    def test_cli_collect_audit_checkpoint_and_export_print_only_metadata(self):
        h = self.harness(initialize=False)
        source = private_json(h.root / "source-context.json", h.context)
        commands = [
            ("init", ("--collector-id", COLLECTOR_ID, "--key-id", KEY_ID)),
            ("collect", ("--input", h.input, "--request-id", "request-1", "--context", source)),
            ("audit", ()),
            ("checkpoint", ("--out", h.root / "retained-checkpoint.json")),
            ("export-native", ("--request-id", "request-1", "--out", h.root / "native.json")),
        ]
        for operation, arguments in commands:
            with self.subTest(operation=operation):
                result = self.run_cli(h, operation, *arguments)
                self.assertEqual(0, result.returncode, result.stderr)
                summary = json.loads(result.stdout)
                self.assertIsInstance(summary, dict)
                for sensitive in (SENSITIVE_SENTINEL, PUBLIC_TEST_SEED.hex(), h.raw.decode("utf-8")):
                    self.assertNotIn(sensitive, result.stdout + result.stderr)
                self.assertNotIn('"raw"', result.stdout)
        self.assertEqual(0o600, stat.S_IMODE((h.root / "retained-checkpoint.json").stat().st_mode))
        self.assertEqual(0o600, stat.S_IMODE((h.root / "native.json").stat().st_mode))

    def test_cli_malformed_context_rejects_without_echoing_input(self):
        h = self.harness()
        malformed = private_write(h.root / "malformed-context.json", (
            '{"x":"' + SENSITIVE_SENTINEL + '","x":2}').encode())
        result = self.run_cli(h, "collect", "--input", h.input, "--request-id", "request-1", "--context", malformed)
        self.assertEqual(2, result.returncode)
        self.assertNotIn(SENSITIVE_SENTINEL, result.stdout + result.stderr)
        self.assertNotIn(PUBLIC_TEST_SEED.hex(), result.stdout + result.stderr)
        self.assertEqual(0, h.audit()["record_count"])

    def test_cli_checkpoint_and_native_export_do_not_overwrite_targets(self):
        h = self.harness()
        h.collect()
        for operation in ("checkpoint", "export-native"):
            with self.subTest(operation=operation):
                target = private_write(h.root / (operation + ".json"), b"preserved output")
                options = ("--request-id", "request-1") if operation == "export-native" else ()
                result = self.run_cli(h, operation, *options, "--out", target)
                self.assertEqual(2, result.returncode)
                self.assertEqual(b"preserved output", target.read_bytes())


class ExistingVerifierBridge(CollectorTestCase):
    def test_actual_post_action_collection_remains_late_while_retrospective_read_can_be_supported(self):
        from integration_support import bridge_scenario
        h = self.harness()
        h.collect()
        result = bridge_scenario(h)
        report = result["report"]
        for name in ("authentication", "authority", "operation", "association"):
            self.assertEqual("supported", report["claims"][name]["status"], report["claims"][name])
        self.assertEqual("contradicted", report["claims"]["timing"]["status"], report["claims"]["timing"])
        for name in ("external_exfiltration", "global_containment", "ai_orchestration"):
            self.assertEqual("unresolved", report["claims"][name]["status"])
        for kind, envelope in result["native_envelopes"].items():
            self.assertIsNone(envelope["payload"]["available_time"])
            self.assertEqual(result["receipts"][kind]["payload"]["received_time"], envelope["payload"]["received_time"])
            self.assertGreater(envelope["payload"]["received_time"], result["scope"]["action_time"])
        self.assertEqual(h.raw, result["native_envelopes"]["resource"]["payload"]["body"]["raw"].encode("utf-8"))
        native_id = result["native_envelopes"]["resource"]["payload"]["record_id"]
        observed = next(record for record in report["records"] if record["record_id"] == native_id)
        self.assertEqual("SecretGet", observed["normalized"]["operation"])
        self.assertEqual("success", observed["normalized"]["result"])
        self.assertIsNone(observed["normalized"]["method"])
        # The private native envelope contains raw evidence; the checker's
        # separate derived report omits the arbitrary sensitive marker/raw text.
        self.assertNotIn(SENSITIVE_SENTINEL, json.dumps(report))
        self.assertNotIn('"raw"', json.dumps(report))

    def test_demo_runs_real_scenarios_and_emits_a_bounded_summary(self):
        process = subprocess.run([*PYTHON, str(ROOT / "run_demo.py")], capture_output=True,
                                 text=True, timeout=45, check=False)
        self.assertEqual(0, process.returncode, process.stderr)
        result = json.loads(process.stdout)
        self.assertEqual(7, result["scenario_count"])
        self.assertEqual(result["scenario_count"], len(result["scenarios"]))
        self.assertTrue(result["synthetic"])
        self.assertTrue(result["public_test_keys"])
        self.assertEqual(0, result["live_cloud_calls"])
        self.assertFalse(result["independent_custody_established"])
        self.assertFalse(result["prevention_established"])
        scenarios = {item["scenario"]: item for item in result["scenarios"]}
        for stage in ("before_commit", "after_commit"):
            self.assertEqual(-signal.SIGKILL, scenarios["sigkill_" + stage]["child_exit_code"])
            self.assertEqual(1, scenarios["sigkill_" + stage]["records_after_retry"])
        checkpoint = scenarios["copied_coherent_prefix_and_retained_checkpoint"]
        self.assertEqual("not_provided", checkpoint["without_checkpoint"])
        self.assertEqual("matched", checkpoint["with_old_prefix_checkpoint"])
        self.assertTrue(checkpoint["retained_later_checkpoint_rejects_truncation"])
        for sensitive in (SENSITIVE_SENTINEL, PUBLIC_TEST_SEED.hex()):
            self.assertNotIn(sensitive, process.stdout + process.stderr)
        for misleading in ("safe", "pass", "prevented", "conformant"):
            self.assertNotIn(misleading, result)


if __name__ == "__main__":
    unittest.main()
