"""Native subprocess custody tests for synthetic payment evidence.

Both services are actual loopback HTTP/SQLite processes. Receive-boundary reply
faults, where used, alter bytes only after the genuine server exchange; they
test verifier behavior, not an independently demonstrated network compromise.
The collector is a separate process under the same test operator/user identity.
"""
from __future__ import annotations

import copy
from contextlib import closing
import json
from pathlib import Path
import signal
import sqlite3
import sys
from unittest import mock
import unittest
from urllib.parse import parse_qs, urlsplit


sys.path.insert(0, str(Path(__file__).resolve().parent))
from collector_support import Harness, authorization, collector, direct_http, runtime


class PaymentCollectorTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def rows(self):
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            return {"claims": db.execute("SELECT count(*) FROM dispatches").fetchone()[0],
                    "proofs": db.execute("SELECT count(*) FROM authorization_proofs").fetchone()[0]}

    def assert_no_payment(self):
        counts = self.h.counts()
        self.assertEqual(counts["post_attempts"], 0)
        self.assertEqual(counts["effects"], 0)
        self.assertEqual(counts["payments"], 0)

    def assert_one_effect(self):
        counts = self.h.counts()
        self.assertEqual(counts["post_attempts"], 1)
        self.assertEqual(counts["effects"], 1)
        self.assertEqual(counts["payments"], 1)
        self.assertEqual(counts["balances"]["source-A"], "98750")
        self.assertEqual(counts["balances"]["beneficiary-A"], "1250")
        self.assertEqual(self.rows(), {"claims": 1, "proofs": 1})

    def assert_original_claim(self):
        self.assertEqual(self.rows(), {"claims": 1, "proofs": 1})
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            self.assertEqual(db.execute("SELECT request_bytes,state FROM dispatches").fetchone(),
                             (runtime.request_bytes(self.h.request), "CLAIMED"))

    def assert_repeats_are_local(self, adapter, *, expected_state="UNKNOWN"):
        payment_before = self.h.counts()
        collector_before = self.h.collector_counts()
        for owner in (adapter, self.h.collected()):
            result = owner.submit(self.h.request, self.h.evidence)
            self.assertEqual(result["state"], expected_state)
            self.assertIs(result["automatic_retry"], False)
        self.assertEqual(self.h.counts(), payment_before)
        self.assertEqual(self.h.collector_counts(), collector_before)

    def assert_original_observations(self, custody, originals, *, harness=None, request=None):
        h = self.h if harness is None else harness
        request = h.request if request is None else request
        public_key = h.collector_key.public_key()
        self.assertEqual(custody["present_retention"], "NOT_CHECKED")
        for kind, evidence in originals.items():
            matching = [item for item in custody["observations"] if item["kind"] == kind]
            self.assertTrue(matching, "missing original signed custody components for " + kind)
            self.assertEqual(custody[kind]["state"], "ACKNOWLEDGED")
            expected_package = collector.make_package(request, kind, evidence)
            for observed in matching:
                self.assertEqual(observed["package_bytes"], expected_package)
                package = collector.load_json(observed["package_bytes"])
                self.assertEqual(bytes.fromhex(package["evidence_bytes"]), evidence)
                self.assertEqual(bytes.fromhex(package["request_bytes"]), runtime.request_bytes(request))
                ack = collector.load_json(observed["ack_bytes"])
                # Verify the exported cryptographic bytes directly, in addition
                # to testing the public verifier's acceptance/rejection paths.
                public_key.verify(bytes.fromhex(ack["signature"]),
                    collector.SIGNING_DOMAIN + collector.canonical_json(ack["payload"]))
                self.assertEqual(ack["payload"]["package_digest"], collector.bytes_digest(expected_package))
                self.assertEqual(ack["payload"]["evidence_digest"], collector.bytes_digest(evidence))
                self.assertEqual(ack["payload"]["request_digest"], runtime.bytes_digest(runtime.request_bytes(request)))
                self.assertEqual(ack["payload"]["kind"], kind)
                readback = collector.load_json(observed["readback_bytes"])
                public_key.verify(bytes.fromhex(readback["signature"]),
                    collector.SIGNING_DOMAIN + collector.canonical_json(readback["payload"]))
                self.assertEqual(readback["payload"]["nonce"], observed["nonce"])
                self.assertEqual(readback["payload"]["state"], "PRESENT")
                self.assertEqual(readback["payload"]["ack_digest"], collector.bytes_digest(observed["ack_bytes"]))

    def test_original_admission_is_collected_before_only_payment_and_receipt_after(self):
        gate = self.h.gate()
        adapter = self.h.collected(gate=gate)
        worker = self.h.collected_worker(barrier="after_pre_dispatch_persisted")
        event = worker.event()
        self.assertEqual((event["event"], event["stage"]), ("barrier", "after_pre_dispatch_persisted"))
        proof = gate.read_authorization(self.h.request)
        self.assertEqual(proof["status"], "FOUND")
        admission = collector.make_package(self.h.request, "admission_record", proof["record_bytes"])
        before = self.h.collector_counts()
        self.assertEqual(before["collection_posts"], 1)
        self.assertEqual(before["readback_queries"], 1)
        self.assertEqual(before["records"], 1)
        self.assertEqual(before["record_digests"], [collector.bytes_digest(admission)])
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
        self.assertEqual(self.h.collector_counts(), before)
        self.assert_original_claim()
        self.assert_no_payment()
        worker.release()
        result = worker.result()
        self.assertEqual(result["state"], "SETTLED")
        self.assertEqual(result["mock_admission"]["verdict"], "AUTHORIZED")
        self.assertIs(result["business_authorization_verified"], False)
        self.assertIs(result["automatic_retry"], False)
        receipt = collector.make_package(self.h.request, "provider_receipt", result["receipt_bytes"])
        after = self.h.collector_counts()
        self.assertEqual(after["collection_posts"], 2)
        self.assertEqual(after["readback_queries"], 2)
        self.assertEqual(after["records"], 2)
        self.assertEqual(set(after["record_digests"]), {
            collector.bytes_digest(admission), collector.bytes_digest(receipt)})
        self.assert_original_observations(result["custody"], {
            "admission_record": proof["record_bytes"], "provider_receipt": result["receipt_bytes"]})
        self.assert_one_effect()
        self.assert_repeats_are_local(adapter, expected_state="SETTLED")
        self.assertEqual(adapter.read_status(self.h.request)["receipt_bytes"], result["receipt_bytes"])
        self.assertEqual(adapter.reconcile(self.h.request)["receipt_bytes"], result["receipt_bytes"])
        self.assertEqual(self.h.collector_counts(), after)
        self.assertEqual(self.h.counts()["lookup_attempts"], 0)
        for secret in (self.h.credential, self.h.collector_credential,
                       self.h.collector_key.private_bytes_raw().hex()):
            self.assertNotIn(secret.encode(), admission)
            self.assertNotIn(secret.encode().hex().encode(), admission)

    def test_missing_authorization_never_contacts_collector_or_payment_provider(self):
        adapter = self.h.collected()
        result = adapter.submit(self.h.request, {})
        self.assertEqual(result["state"], "REJECTED")
        self.assertEqual(result["mock_admission"]["verdict"], "UNKNOWN")
        self.assertEqual(self.rows(), {"claims": 0, "proofs": 0})
        self.assert_no_payment()
        self.assertEqual(self.h.collector_counts()["collection_posts"], 0)
        self.assertEqual(self.h.collector_counts()["readback_queries"], 0)
        self.assertEqual(self.h.collector_counts()["records"], 0)

    def test_unavailable_collector_consumes_claim_and_recovery_never_sends_payment(self):
        adapter = self.h.collected()
        self.h.stop_collector()
        result = adapter.submit(self.h.request, self.h.evidence)
        self.assertEqual(result["state"], "UNKNOWN")
        self.assert_original_claim()
        self.assert_no_payment()
        self.assertEqual(self.h.collector_counts()["records"], 0)
        self.assert_repeats_are_local(adapter)
        self.h.start_collector()
        recovered = self.h.collected()
        recovered.recover_evidence(self.h.request)
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertGreater(self.h.collector_counts()["readback_queries"], 0)
        self.assertEqual(recovered.read_custody(self.h.request)["pre_dispatch"]["state"], "NOT_RECORDED")
        self.assert_repeats_are_local(recovered)
        self.assert_no_payment()
        self.assertEqual(self.h.counts()["lookup_attempts"], 0)

    def test_committed_admission_ack_loss_cannot_rearm_initial_payment(self):
        self.h.stop_collector()
        self.h.collector_config["drop_ack_after_commit"] = True
        self.h.start_collector()
        adapter = self.h.collected()
        result = adapter.submit(self.h.request, self.h.evidence)
        self.assertEqual(result["state"], "UNKNOWN")
        self.assert_original_claim()
        self.assert_no_payment()
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertEqual(self.h.collector_counts()["collection_posts"], 1)
        self.assert_repeats_are_local(adapter)
        adapter.recover_evidence(self.h.request)
        self.assertGreater(self.h.collector_counts()["readback_queries"], 0)
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "NOT_RECORDED")
        self.assertEqual(adapter.reconcile(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(self.h.counts()["lookup_attempts"], 1)
        self.assert_no_payment()

    def test_sigkill_after_claim_before_collection_retains_consumption(self):
        adapter = self.h.collected()
        worker = self.h.collected_worker(barrier="after_claim")
        event = worker.event()
        self.assertEqual((event["event"], event["stage"]), ("barrier", "after_claim"))
        self.assert_original_claim()
        self.assertEqual(self.h.collector_counts()["collection_posts"], 0)
        self.assertEqual(worker.kill(), -signal.SIGKILL)
        self.assert_repeats_are_local(adapter)
        adapter.recover_evidence(self.h.request)
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "NOT_RECORDED")
        self.assert_no_payment()

    def test_collector_sigkill_after_commit_recovers_same_record_without_payment(self):
        self.h.stop_collector()
        server = self.h.start_collector(barrier="after_commit", kind="admission_record")
        worker = self.h.collected_worker()
        event = server.event()
        self.assertEqual((event["event"], event["kind"]), ("barrier", "admission_record"))
        before = self.h.collector_counts()
        self.assertEqual(before["records"], 1)
        self.assert_no_payment()
        self.assertEqual(server.kill(), -signal.SIGKILL)
        self.assertEqual(worker.result()["state"], "UNKNOWN")
        self.h.stop_collector()
        self.h.start_collector()
        recovered = self.h.collected()
        recovered.recover_evidence(self.h.request)
        after = self.h.collector_counts()
        self.assertEqual(after["records"], 1)
        self.assertEqual(after["record_digests"], before["record_digests"])
        self.assertGreater(after["readback_queries"], before["readback_queries"])
        self.assertEqual(recovered.read_custody(self.h.request)["pre_dispatch"]["state"], "NOT_RECORDED")
        self.assert_repeats_are_local(recovered)
        self.assert_no_payment()

    def test_sigkill_after_pre_dispatch_persistence_never_resumes_payment_send(self):
        adapter = self.h.collected()
        worker = self.h.collected_worker(barrier="after_pre_dispatch_persisted")
        event = worker.event()
        self.assertEqual((event["event"], event["stage"]), ("barrier", "after_pre_dispatch_persisted"))
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertGreater(self.h.collector_counts()["readback_queries"], 0)
        self.assert_no_payment()
        self.assertEqual(worker.kill(), -signal.SIGKILL)
        self.assert_repeats_are_local(adapter)
        adapter.recover_evidence(self.h.request)
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
        self.assert_original_claim()
        self.assert_no_payment()

    def test_real_collector_database_lock_prevents_payment_but_keeps_claim(self):
        adapter = self.h.collected()
        with closing(sqlite3.connect(self.h.collector_path, timeout=0.1)) as locked:
            locked.execute("BEGIN IMMEDIATE")
            result = adapter.submit(self.h.request, self.h.evidence)
            self.assertEqual(result["state"], "UNKNOWN")
            self.assert_original_claim()
            self.assert_no_payment()
            self.assertEqual(self.h.collector_counts()["records"], 0)
            locked.rollback()
        adapter.recover_evidence(self.h.request)
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "NOT_RECORDED")
        self.assert_repeats_are_local(adapter)
        self.assert_no_payment()

    def test_real_ack_verified_then_local_journal_lock_cannot_authorize_payment(self):
        adapter = self.h.collected()
        worker = self.h.collected_worker(barrier="after_verified_collection", kind="admission_record")
        event = worker.event()
        self.assertEqual((event["event"], event["kind"]), ("barrier", "admission_record"))
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertGreater(self.h.collector_counts()["readback_queries"], 0)
        self.assert_no_payment()
        # The actual collector commit and signed readback have completed. Hold
        # the real local writer lock while the client attempts to persist them.
        with closing(sqlite3.connect(self.h.journal_path, timeout=0.1)) as locked:
            locked.execute("BEGIN IMMEDIATE")
            worker.release()
            self.assertEqual(worker.result()["state"], "UNKNOWN")
            locked.rollback()
        self.assert_original_claim()
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "NOT_RECORDED")
        self.assert_repeats_are_local(adapter)
        adapter.recover_evidence(self.h.request)
        self.assert_no_payment()

    def test_wrong_collector_pin_rejects_genuine_signed_ack_before_payment(self):
        wrong = self.h.key.public_key().public_bytes_raw().hex()
        self.assertNotEqual(wrong, self.h.collector_key.public_key().public_bytes_raw().hex())
        adapter = self.h.collected(client=self.h.client(public_key_hex=wrong))
        result = adapter.submit(self.h.request, self.h.evidence)
        self.assertEqual(result["state"], "UNKNOWN")
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assertEqual(self.h.collector_counts()["collection_posts"], 1)
        self.assert_original_claim()
        self.assert_no_payment()
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "NOT_RECORDED")

    def test_financial_terminal_outcome_survives_actual_post_effect_collector_outage(self):
        for expected_state in ("SETTLED", "FAILED"):
            with self.subTest(expected_state=expected_state), Harness() as h:
                if expected_state == "FAILED":
                    h.request["amount_minor"] = "100001"
                    h.policy["max_amount_minor"] = "200000"
                    h.evidence = h.make_evidence(h.request)
                worker = h.collected_worker(barrier="after_response")
                event = worker.event()
                self.assertEqual((event["event"], event["stage"]), ("barrier", "after_response"))
                self.assertEqual(h.counts()["post_attempts"], 1)
                self.assertEqual(h.counts()["effects"], int(expected_state == "SETTLED"))
                self.assertEqual(h.collector_counts()["records"], 1)
                h.stop_collector()
                worker.release()
                result = worker.result()
                self.assertEqual(result["state"], expected_state)
                self.assertEqual(runtime.load_json(result["receipt_bytes"])["payload"]["status"], expected_state.lower())
                self.assertEqual(result["custody"]["admission_record"]["state"], "ACKNOWLEDGED")
                self.assertEqual(result["custody"]["provider_receipt"]["state"], "UNKNOWN")
                self.assertEqual(result["custody"]["state"], "UNKNOWN")
                self.assertEqual(result["custody"]["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
                before = h.counts()
                adapter = h.collected()
                self.assertEqual(adapter.read_status(h.request)["state"], expected_state)
                self.assertEqual(adapter.reconcile(h.request)["state"], expected_state)
                self.assertEqual(adapter.check_custody(h.request)["present_retention"], "UNKNOWN")
                self.assertEqual(h.counts(), before)
                h.start_collector()
                adapter = h.collected()
                recovered = adapter.recover_evidence(h.request)
                self.assertEqual(recovered["state"], expected_state)
                self.assertEqual(recovered["receipt_bytes"], result["receipt_bytes"])
                self.assertEqual(recovered["custody"]["state"], "ACKNOWLEDGED")
                self.assertEqual(recovered["evidence_recovery"], {
                    "historical_only": True, "unresolved_kinds": [], "payment_rearmed": False})
                self.assertEqual(h.counts(), before)
                self.assertEqual(h.collector_counts()["records"], 2)
                proof = h.gate().read_authorization(h.request)
                self.assert_original_observations(recovered["custody"], {
                    "admission_record": proof["record_bytes"], "provider_receipt": result["receipt_bytes"]}, harness=h)

    def test_collector_sigkill_after_receipt_commit_keeps_financial_result_and_stable_ack(self):
        self.h.stop_collector()
        server = self.h.start_collector(barrier="after_commit", kind="provider_receipt")
        worker = self.h.collected_worker()
        event = server.event()
        self.assertEqual((event["event"], event["kind"]), ("barrier", "provider_receipt"))
        self.assert_one_effect()
        self.assertEqual(self.h.collector_counts()["records"], 2)
        with closing(sqlite3.connect(self.h.collector_path)) as db:
            original_package, original_ack = db.execute(
                "SELECT package_bytes,ack_bytes FROM collection_records WHERE kind='provider_receipt'").fetchone()
        self.assertEqual(server.kill(), -signal.SIGKILL)
        result = worker.result()
        self.assertEqual(result["state"], "SETTLED")
        self.assertEqual(result["custody"]["provider_receipt"]["state"], "UNKNOWN")
        self.assertEqual(original_package, collector.make_package(self.h.request, "provider_receipt", result["receipt_bytes"]))
        self.h.stop_collector()
        self.h.start_collector()
        recovered = self.h.collected().recover_evidence(self.h.request)
        self.assertEqual(recovered["state"], "SETTLED")
        self.assertEqual(recovered["receipt_bytes"], result["receipt_bytes"])
        self.assertEqual(recovered["custody"]["provider_receipt"]["state"], "ACKNOWLEDGED")
        receipts = [item for item in recovered["custody"]["observations"] if item["kind"] == "provider_receipt"]
        self.assertEqual(len(receipts), 1)
        self.assertEqual(receipts[0]["ack_bytes"], original_ack)
        self.assertEqual(receipts[0]["package_bytes"], original_package)
        self.assertEqual(self.h.collector_counts()["records"], 2)
        self.assertEqual(self.h.counts()["lookup_attempts"], 0)
        self.assert_one_effect()

    def test_provider_ack_loss_requires_native_get_then_evidence_only_receipt_recovery(self):
        self.h.stop_provider()
        self.h.provider_config["drop_after_commit"] = True
        self.h.start_provider()
        adapter = self.h.collected()
        first = adapter.submit(self.h.request, self.h.evidence)
        self.assertEqual(first["state"], "UNKNOWN")
        self.assertEqual(first["custody"]["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
        self.assertEqual(first["custody"]["provider_receipt"]["state"], "UNKNOWN")
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assert_one_effect()
        before_native = self.h.counts()
        recovered_evidence = adapter.recover_evidence(self.h.request)
        self.assertEqual(recovered_evidence["state"], "UNKNOWN")
        self.assertEqual(self.h.counts(), before_native)
        self.assertEqual(self.h.collector_counts()["records"], 1)
        before_collector = self.h.collector_counts()
        reconciled = adapter.reconcile(self.h.request)
        self.assertEqual(reconciled["state"], "SETTLED")
        self.assertEqual(self.h.counts()["lookup_attempts"], 1)
        self.assertEqual(self.h.collector_counts(), before_collector)
        self.assertEqual(reconciled["custody"]["provider_receipt"]["state"], "UNKNOWN")
        with closing(sqlite3.connect(self.h.provider_path)) as db:
            original_receipt = db.execute("SELECT receipt_bytes FROM payments").fetchone()[0]
        self.assertEqual(reconciled["receipt_bytes"], original_receipt)
        before_native = self.h.counts()
        final = adapter.recover_evidence(self.h.request)
        self.assertEqual(final["state"], "SETTLED")
        self.assertEqual(final["receipt_bytes"], original_receipt)
        self.assertEqual(final["custody"]["state"], "ACKNOWLEDGED")
        self.assertEqual(self.h.counts(), before_native)
        self.assertEqual(self.h.collector_counts()["records"], 2)
        self.assert_repeats_are_local(adapter, expected_state="SETTLED")
        self.assert_one_effect()

    def test_fresh_missing_readback_does_not_turn_historical_ack_into_present_retention(self):
        adapter = self.h.collected()
        settled = adapter.submit(self.h.request, self.h.evidence)
        self.assertEqual(settled["state"], "SETTLED")
        historical = adapter.read_custody(self.h.request)
        self.assertEqual(historical["state"], "ACKNOWLEDGED")
        self.assertEqual(historical["present_retention"], "NOT_CHECKED")
        native_before = self.h.counts()
        collector_before = self.h.collector_counts()
        current = adapter.check_custody(self.h.request)
        self.assertEqual(current["present_retention"], "PRESENT_AT_CHALLENGED_READBACKS")
        self.assertEqual({kind: item["state"] for kind, item in current["observations"].items()},
                         {"admission_record": "PRESENT", "provider_receipt": "PRESENT"})
        self.assertEqual(self.h.collector_counts()["collection_posts"], collector_before["collection_posts"])
        self.assertEqual(self.h.collector_counts()["readback_queries"], collector_before["readback_queries"] + 2)
        self.assertEqual(adapter.read_custody(self.h.request), historical)

        # Controlled empty-store substitution under the same ephemeral signing
        # key demonstrates fresh MISSING versus historical ACK. It makes no
        # claim that this prototype resists an operator rolling storage back.
        self.h.stop_collector()
        self.h.collector_path = self.h.root / "controlled-empty-collector.sqlite"
        self.h.collector_config["db_path"] = str(self.h.collector_path)
        self.h.start_collector()
        adapter = self.h.collected()
        self.assertEqual(adapter.read_custody(self.h.request), historical)
        missing = adapter.check_custody(self.h.request)
        self.assertEqual(missing["present_retention"], "UNKNOWN")
        self.assertEqual({kind: item["state"] for kind, item in missing["observations"].items()},
                         {"admission_record": "MISSING", "provider_receipt": "MISSING"})
        for item in missing["observations"].values():
            statement = collector.load_json(item["readback_bytes"])
            self.h.collector_key.public_key().verify(bytes.fromhex(statement["signature"]),
                collector.SIGNING_DOMAIN + collector.canonical_json(statement["payload"]))
            self.assertEqual(statement["payload"]["nonce"], item["nonce"])
            self.assertIsNone(item["ack_bytes"])
        self.assertEqual(self.h.collector_counts()["records"], 0)
        self.assertEqual(self.h.collector_counts()["collection_posts"], 0)
        self.assertEqual(self.h.collector_counts()["readback_queries"], 2)
        self.assertEqual(self.h.counts(), native_before)
        cached = adapter.read_status(self.h.request)
        self.assertEqual(cached["state"], "SETTLED")
        self.assertEqual(cached["receipt_bytes"], settled["receipt_bytes"])
        self.assertEqual(cached["custody"], historical)

    def test_current_collector_epoch_fences_old_process_but_preserves_original_ack(self):
        old_client = self.h.client()
        old_adapter = self.h.collected(client=old_client)
        settled = old_adapter.submit(self.h.request, self.h.evidence)
        historical = old_adapter.read_custody(self.h.request)
        old_acks = {item["kind"]: item["ack_bytes"] for item in historical["observations"]}
        old_server = self.h.collector_process
        # Keep the old server alive. Advancing this same store through a second
        # real server must fence stale present-retention assertions.
        self.h.collector_config["recovery_epoch"] = 2
        self.h.start_collector()
        self.assertIsNone(old_server.proc.poll())
        current = self.h.collected(client=self.h.client(recovery_epoch=2))
        self.assertEqual(current.read_custody(self.h.request), historical)
        stale = old_adapter.check_custody(self.h.request)
        self.assertEqual(stale["present_retention"], "UNKNOWN")
        self.assertEqual({item["state"] for item in stale["observations"].values()}, {"UNKNOWN"})
        fresh = current.check_custody(self.h.request)
        self.assertEqual(fresh["present_retention"], "PRESENT_AT_CHALLENGED_READBACKS")
        for kind, observed in fresh["observations"].items():
            self.assertEqual(observed["ack_bytes"], old_acks[kind])
            self.assertEqual(collector.load_json(observed["ack_bytes"])["payload"]["storage_epoch"], 1)
            self.assertEqual(collector.load_json(observed["readback_bytes"])["payload"]["recovery_epoch"], 2)
        recovered = current.recover_evidence(self.h.request)
        self.assertEqual(recovered["state"], "SETTLED")
        self.assertEqual(recovered["receipt_bytes"], settled["receipt_bytes"])
        self.assertEqual(recovered["custody"]["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
        for observed in recovered["custody"]["observations"]:
            self.assertEqual(observed["ack_bytes"], old_acks[observed["kind"]])
        self.assertEqual({item["collector_epoch"] for item in recovered["custody"]["observations"]}, {1, 2})
        with self.assertRaisesRegex(ValueError, "persisted_custody_pin_or_epoch_mismatch"):
            self.h.collected(client=self.h.client(recovery_epoch=1))
        before_collector = self.h.collector_counts()
        self.assertEqual(old_adapter.submit(self.h.request, self.h.evidence)["state"], "SETTLED")
        self.assertEqual(current.submit(self.h.request, self.h.evidence)["state"], "SETTLED")
        self.assertEqual(self.h.collector_counts(), before_collector)
        self.assertEqual(self.h.collector_counts()["records"], 2)
        self.assert_one_effect()

    def test_reconciliation_and_evidence_recovery_own_request_across_real_http_calls(self):
        self.h.stop_provider()
        self.h.provider_config["drop_after_commit"] = True
        self.h.start_provider()
        native = self.h.adapter()
        gate = self.h.gate(native=native)
        client = self.h.client()
        adapter = self.h.collected(gate=gate, client=client)
        original = copy.deepcopy(self.h.request)
        other = self.h.next_request("other", amount_minor="500")
        self.assertEqual(adapter.submit(original, self.h.evidence)["state"], "UNKNOWN")
        self.assertEqual(adapter.submit(other, self.h.make_evidence(other, suffix="other"))["state"], "UNKNOWN")
        proof = gate.read_authorization(original)
        other_proof = gate.read_authorization(other)
        self.assertNotEqual(proof["record_digest"], other_proof["record_digest"])
        self.assertEqual(adapter.reconcile(other)["state"], "SETTLED")
        self.assertEqual(adapter.recover_evidence(other)["custody"]["state"], "ACKNOWLEDGED")
        caller = copy.deepcopy(original)
        native_http = native._http

        def mutate_after_real_payment_get(method, path, body=None):
            response = native_http(method, path, body)
            self.assertEqual(method, "GET")
            caller.clear()
            caller.update(other)
            return response

        before_collector = self.h.collector_counts()
        with mock.patch.object(native, "_http", side_effect=mutate_after_real_payment_get):
            reconciled = adapter.reconcile(caller)
        self.assertEqual(caller, other)
        self.assertEqual(reconciled["request_digest"], proof["request_digest"])
        self.assertEqual(reconciled["mock_admission"]["proof_digest"], proof["record_digest"])
        self.assertEqual(reconciled["custody"]["provider_receipt"]["state"], "UNKNOWN")
        self.assertEqual(self.h.collector_counts(), before_collector)
        self.assert_original_observations(reconciled["custody"], {"admission_record": proof["record_bytes"]}, request=original)
        runtime.verify_receipt(reconciled["receipt_bytes"], runtime.request_bytes(original),
                               self.h.key.public_key().public_bytes_raw())

        caller.clear()
        caller.update(original)
        collector_http = client._http
        actual_posts = []

        def mutate_after_real_collection_post(method, path, body=None):
            response = collector_http(method, path, body)
            if method == "POST":
                actual_posts.append(body)
                caller.clear()
                caller.update(other)
            return response

        before_native = self.h.counts()
        with mock.patch.object(client, "_http", side_effect=mutate_after_real_collection_post):
            recovered = adapter.recover_evidence(caller)
        self.assertEqual(len(actual_posts), 2)
        for package in actual_posts:
            self.assertEqual(collector.load_json(package)["request_digest"], proof["request_digest"])
        self.assertEqual(recovered["request_digest"], proof["request_digest"])
        self.assertEqual(recovered["mock_admission"]["proof_digest"], proof["record_digest"])
        self.assertEqual(recovered["receipt_bytes"], reconciled["receipt_bytes"])
        self.assert_original_observations(recovered["custody"], {
            "admission_record": proof["record_bytes"], "provider_receipt": reconciled["receipt_bytes"]}, request=original)
        self.assertEqual(self.h.counts(), before_native)

        caller.clear()
        caller.update(original)
        native_read = native.read_status

        def mutate_after_local_read(request):
            result = native_read(request)
            caller.clear()
            caller.update(other)
            return result

        with mock.patch.object(native, "read_status", side_effect=mutate_after_local_read):
            cached = adapter.read_status(caller)
        self.assertEqual(cached["request_digest"], proof["request_digest"])
        self.assertEqual(cached["custody"], recovered["custody"])
        self.assertEqual(self.h.counts()["post_attempts"], 2)
        self.assertEqual(self.h.counts()["effects"], 2)
        self.assertEqual(self.h.collector_counts()["records"], 4)

    def test_unreadable_or_tampered_local_custody_never_asserts_verified_pre_dispatch(self):
        adapter = self.h.collected()
        settled = adapter.submit(self.h.request, self.h.evidence)
        self.assertEqual(settled["custody"]["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
        before_collector = self.h.collector_counts()
        before_native = self.h.counts()
        saved_path = self.h.root / "temporarily-unavailable-journal.sqlite"
        self.h.journal_path.rename(saved_path)
        try:
            unreadable = adapter.read_custody(self.h.request)
            self.assertEqual(unreadable["state"], "UNKNOWN")
            self.assertEqual(unreadable["pre_dispatch"]["state"], "UNKNOWN")
            self.assertEqual(unreadable["present_retention"], "NOT_CHECKED")
            self.assertEqual(adapter.read_status(self.h.request)["custody"]["pre_dispatch"]["state"], "UNKNOWN")
        finally:
            saved_path.rename(self.h.journal_path)
        self.assertEqual(adapter.read_custody(self.h.request)["pre_dispatch"]["state"], "VERIFIED_PREREQUISITE")
        self.assertEqual(self.h.collector_counts(), before_collector)
        self.assertEqual(self.h.counts(), before_native)

        # Trusted corruption injection removes local SQL guards and recomputes
        # the unsigned outer digest/marker. This checks re-verification of the
        # original signed components, not malicious-administrator resistance.
        original = next(item for item in settled["custody"]["observations"] if item["stage"] == "PRE_DISPATCH")
        record = collector.load_json(original["record_bytes"])
        ack = collector.load_json(bytes.fromhex(record["ack_bytes"]))
        ack["signature"] = ("00" if ack["signature"][:2] != "00" else "01") + ack["signature"][2:]
        record["ack_bytes"] = collector.canonical_json(ack).hex()
        changed_record = collector.canonical_json(record)
        changed_digest = collector.bytes_digest(changed_record)
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            db.execute("DROP TRIGGER immutable_custody_observations_update")
            db.execute("DROP TRIGGER immutable_custody_prerequisites_update")
            db.execute("UPDATE custody_observations SET record_bytes=?,observation_digest=? WHERE observation_digest=?",
                       (changed_record, changed_digest, original["observation_digest"]))
            db.execute("UPDATE custody_prerequisites SET observation_digest=? WHERE request_digest=?",
                       (changed_digest, runtime.bytes_digest(runtime.request_bytes(self.h.request))))
            db.commit()
        cached = adapter.read_status(self.h.request)
        self.assertEqual(cached["state"], "SETTLED")
        self.assertEqual(cached["receipt_bytes"], settled["receipt_bytes"])
        self.assertEqual(cached["custody"]["pre_dispatch"]["state"], "UNKNOWN")
        self.assertEqual(cached["custody"]["admission_record"]["state"], "UNKNOWN")
        self.assertEqual(cached["custody"]["unverifiable_observations"], 1)
        self.assert_repeats_are_local(adapter, expected_state="SETTLED")
        recovered = adapter.recover_evidence(self.h.request)
        self.assertEqual(recovered["custody"]["state"], "ACKNOWLEDGED")
        self.assertEqual(recovered["custody"]["pre_dispatch"]["state"], "UNKNOWN")
        self.assertEqual(recovered["state"], "SETTLED")
        self.assert_one_effect()

    def test_real_collection_replay_keeps_original_bytes_ack_and_conflict_after_restart(self):
        gate = self.h.gate()
        adapter = self.h.collected(gate=gate)
        self.assertEqual(adapter.submit(self.h.request, self.h.evidence)["state"], "SETTLED")
        proof = gate.read_authorization(self.h.request)
        package = collector.make_package(self.h.request, "admission_record", proof["record_bytes"])
        with closing(sqlite3.connect(self.h.collector_path)) as db:
            original_package, original_ack = db.execute(
                "SELECT package_bytes,ack_bytes FROM collection_records WHERE package_digest=?",
                (collector.bytes_digest(package),)).fetchone()
        self.assertEqual(original_package, package)
        collector.verify_ack(original_ack, package, self.h.collector_key.public_key().public_bytes_raw())
        for restarted in (False, True):
            if restarted:
                self.h.stop_collector()
                self.h.start_collector()
            status, ack = direct_http(self.h.collector_endpoint, "POST", "/collections",
                                      raw=package, credential=self.h.collector_credential)
            self.assertEqual(status, 200)
            self.assertEqual(ack, original_ack)
            changed = authorization.load_json(proof["record_bytes"])
            changed["decision"]["reasons"] = ["changed-after-original-custody"]
            conflict = collector.make_package(self.h.request, "admission_record", authorization.canonical_json(changed))
            status, _ = direct_http(self.h.collector_endpoint, "POST", "/collections",
                                    raw=conflict, credential=self.h.collector_credential)
            self.assertEqual(status, 409)
            with closing(sqlite3.connect(self.h.collector_path)) as db:
                self.assertEqual(db.execute(
                    "SELECT package_bytes,ack_bytes FROM collection_records WHERE package_digest=?",
                    (collector.bytes_digest(package),)).fetchone(), (original_package, original_ack))
        self.assertEqual(self.h.collector_counts()["records"], 2)
        self.assertEqual(self.h.collector_counts()["collection_posts"], 6)
        self.assert_one_effect()

    def test_collector_rejects_malformed_or_mismatched_original_packages_over_http(self):
        gate = self.h.gate()
        self.assertEqual(self.h.collected(gate=gate).submit(self.h.request, self.h.evidence)["state"], "SETTLED")
        proof = gate.read_authorization(self.h.request)
        package = collector.make_package(self.h.request, "admission_record", proof["record_bytes"])
        body = collector.load_json(package)
        changed = [
            {**body, "request_digest": "sha256:" + "00" * 32},
            {**body, "context_digest": "sha256:" + "00" * 32},
            {**body, "kind": "provider_receipt", "phase": "outcome"},
            {**body, "kind": ["admission_record"]},
            {**body, "phase": "outcome"},
            {**body, "evidence_digest": "sha256:" + "00" * 32},
            {**body, "evidence_length": True},
            {**body, "evidence_length": float(body["evidence_length"])},
            {**body, "evidence_bytes": "00" * (collector.MAX_EVIDENCE_BYTES + 1)},
            {**body, "unrecognized": "field"},
        ]
        raw_inputs = [json.dumps(item, separators=(",", ":")).encode() for item in changed]
        raw_inputs += [b" " + package, package[:-1] + b',"kind":"admission_record"}', b"[]"]
        before = self.h.collector_counts()
        for raw in raw_inputs:
            with self.subTest(raw_length=len(raw)):
                status, _ = direct_http(self.h.collector_endpoint, "POST", "/collections",
                                        raw=raw, credential=self.h.collector_credential)
                self.assertEqual(status, 400)
                self.assertEqual(self.h.collector_counts()["records"], before["records"])
        status, ack = direct_http(self.h.collector_endpoint, "POST", "/collections",
                                  raw=package, credential=self.h.collector_credential)
        self.assertEqual(status, 200)
        collector.verify_ack(ack, package, self.h.collector_key.public_key().public_bytes_raw())
        self.assertEqual(self.h.collector_counts()["collection_posts"], before["collection_posts"] + len(raw_inputs) + 1)
        self.assert_one_effect()

    def test_controlled_ack_reply_faults_after_real_commit_never_allow_payment(self):
        # Every input below is obtained from a real native collection POST and
        # verified first. Only the received bytes are then changed in this
        # trusted harness; this is not an independent network-attack claim.
        client = self.h.client()
        adapter = self.h.collected(client=client)
        genuine_http = client._http
        faults = ("signature", "signature_domain", "request_digest", "context_digest", "kind", "phase",
                  "package_digest", "evidence_length", "collector_id", "storage_epoch")
        for index, fault in enumerate(faults, 1):
            with self.subTest(fault=fault):
                request = self.h.next_request("ack-fault-" + str(index))
                observed = []

                def fault_after_real_exchange(method, path, body=None):
                    status, raw = genuine_http(method, path, body)
                    if method != "POST" or status != 200:
                        return status, raw
                    collector.verify_ack(raw, body, self.h.collector_key.public_key().public_bytes_raw())
                    observed.append(raw)
                    envelope = collector.load_json(raw)
                    if fault == "signature":
                        envelope["signature"] = ("00" if envelope["signature"][:2] != "00" else "01") + envelope["signature"][2:]
                        return status, collector.canonical_json(envelope)
                    if fault == "signature_domain":
                        envelope["signature"] = self.h.collector_key.sign(
                            b"wrong-test-domain\x00" + collector.canonical_json(envelope["payload"])).hex()
                        return status, collector.canonical_json(envelope)
                    replacements = {"request_digest": "sha256:" + "00" * 32,
                        "context_digest": "sha256:" + "00" * 32, "kind": "provider_receipt", "phase": "outcome",
                        "package_digest": "sha256:" + "00" * 32,
                        "evidence_length": envelope["payload"]["evidence_length"] + 1,
                        "collector_id": "other-collector", "storage_epoch": 2}
                    envelope["payload"][fault] = replacements[fault]
                    return status, collector.sign_statement(envelope["payload"], self.h.collector_key.private_bytes_raw())

                with mock.patch.object(client, "_http", side_effect=fault_after_real_exchange):
                    result = adapter.submit(request, self.h.make_evidence(request, suffix=str(index)))
                self.assertEqual(len(observed), 1)
                self.assertEqual(result["state"], "UNKNOWN")
                self.assertEqual(result["mock_admission"]["verdict"], "AUTHORIZED")
                self.assertEqual(adapter.read_custody(request)["pre_dispatch"]["state"], "NOT_RECORDED")
                self.assertEqual(self.h.collector_counts()["records"], index)
                self.assertEqual(self.h.collector_counts()["collection_posts"], index)
                self.assertEqual(self.h.collector_counts()["readback_queries"], 0)
                self.assert_no_payment()
                self.assertEqual(adapter.submit(request, self.h.make_evidence(request))["state"], "UNKNOWN")
                self.assertEqual(self.h.collector_counts()["collection_posts"], index)

    def test_signed_matching_ack_without_valid_fresh_readback_cannot_allow_payment(self):
        # POST and GET both reach the actual collector. The authentic matching
        # ACK is retained; these faults affect only its subsequent signed
        # challenge/readback response at the controlled receive boundary.
        client = self.h.client()
        adapter = self.h.collected(client=client)
        genuine_http = client._http
        faults = ("nonce", "state", "recovery_epoch", "ack_digest", "original_package")
        for index, fault in enumerate(faults, 1):
            with self.subTest(fault=fault):
                request = self.h.next_request("readback-fault-" + str(index))
                actual = {}

                def fault_after_real_exchange(method, path, body=None):
                    status, raw = genuine_http(method, path, body)
                    if status != 200:
                        return status, raw
                    if method == "POST":
                        collector.verify_ack(raw, body, self.h.collector_key.public_key().public_bytes_raw())
                        actual["package"] = body
                        actual["ack"] = raw
                        return status, raw
                    nonce = parse_qs(urlsplit(path).query)["nonce"][0]
                    checked = collector.verify_readback(raw, actual["package"],
                        self.h.collector_key.public_key().public_bytes_raw(), nonce=nonce)
                    self.assertEqual(checked["ack_bytes"], actual["ack"])
                    actual["readback"] = raw
                    response = collector.load_json(raw)
                    signed = collector.load_json(bytes.fromhex(response["readback_bytes"]))["payload"]
                    if fault == "original_package":
                        response["package_bytes"] = (actual["package"] + b" ").hex()
                    else:
                        changes = {"nonce": ("00" if nonce[:2] != "00" else "01") + nonce[2:],
                                   "state": "MISSING", "recovery_epoch": 2,
                                   "ack_digest": "sha256:" + "00" * 32}
                        signed[fault] = changes[fault]
                        response["readback_bytes"] = collector.sign_statement(
                            signed, self.h.collector_key.private_bytes_raw()).hex()
                    return status, collector.canonical_json(response)

                with mock.patch.object(client, "_http", side_effect=fault_after_real_exchange):
                    result = adapter.submit(request, self.h.make_evidence(request, suffix=str(index)))
                self.assertEqual(set(actual), {"package", "ack", "readback"})
                self.assertEqual(result["state"], "UNKNOWN")
                self.assertEqual(adapter.read_custody(request)["pre_dispatch"]["state"], "NOT_RECORDED")
                self.assertEqual(self.h.collector_counts()["records"], index)
                self.assertEqual(self.h.collector_counts()["collection_posts"], index)
                self.assertEqual(self.h.collector_counts()["readback_queries"], index)
                self.assert_no_payment()

    def test_legacy_raw_and_authorized_claims_cannot_gain_pre_dispatch_coverage(self):
        for legacy_kind in ("raw", "authorized"):
            with self.subTest(legacy_kind=legacy_kind), Harness() as h:
                gate = h.gate()
                original = (gate.submit(h.request, h.evidence) if legacy_kind == "authorized"
                            else h.adapter().submit(h.request))
                self.assertEqual(original["state"], "SETTLED")
                adapter = h.collected(gate=gate)
                self.assertEqual(adapter.submit(h.request, h.evidence)["state"], "SETTLED")
                self.assertEqual(h.collector_counts()["records"], 0)
                adapter.recover_evidence(h.request)
                self.assertEqual(adapter.read_custody(h.request)["pre_dispatch"]["state"], "NOT_RECORDED")
                self.assertEqual(adapter.read_status(h.request)["receipt_bytes"], original["receipt_bytes"])
                self.assertEqual(h.counts()["post_attempts"], 1)
                self.assertEqual(h.counts()["effects"], 1)
                self.assertEqual(h.collector_counts()["records"], 2 if legacy_kind == "authorized" else 1)

    def test_reads_and_recovery_of_unsubmitted_request_never_create_a_claim(self):
        adapter = self.h.collected()
        for action in ("read_status", "read_custody", "check_custody", "reconcile", "recover_evidence"):
            with self.subTest(action=action):
                getattr(adapter, action)(self.h.request)
                self.assertEqual(self.rows(), {"claims": 0, "proofs": 0})
                self.assertEqual(self.h.collector_counts()["records"], 0)
                self.assertEqual(self.h.collector_counts()["collection_posts"], 0)
                self.assertEqual(self.h.collector_counts()["readback_queries"], 0)
                self.assertEqual(self.h.counts()["lookup_attempts"], 0)
                self.assert_no_payment()

    def test_rejected_owned_snapshot_is_terminal_even_if_caller_becomes_valid(self):
        native = self.h.adapter()
        adapter = self.h.collected(gate=self.h.gate(native=native))
        original_prepare = native._prepare
        for action in ("submit", "read_status", "reconcile"):
            with self.subTest(action=action):
                caller = {**self.h.request, "amount_minor": False}
                prepare_calls = []

                def reject_then_mutate(value):
                    prepare_calls.append(copy.deepcopy(value))
                    if len(prepare_calls) == 1:
                        # Deterministically reproduce a caller mutation after
                        # the wrapper's failed snapshot. Retrying preparation
                        # through the raw authorization path used to omit the
                        # collector prerequisite completely.
                        caller.clear()
                        caller.update(self.h.request)
                        raise ValueError("controlled_rejected_snapshot")
                    return original_prepare(value)

                with mock.patch.object(native, "_prepare", side_effect=reject_then_mutate):
                    result = (adapter.submit(caller, self.h.evidence) if action == "submit"
                              else getattr(adapter, action)(caller))
                self.assertEqual(len(prepare_calls), 1)
                self.assertEqual(caller, self.h.request)
                self.assertEqual(result["state"], "REJECTED")
                self.assertEqual(self.rows(), {"claims": 0, "proofs": 0})
                self.assertEqual(self.h.collector_counts()["collection_posts"], 0)
                self.assertEqual(self.h.collector_counts()["readback_queries"], 0)
                self.assertEqual(self.h.counts()["lookup_attempts"], 0)
                self.assert_no_payment()

    def test_concurrent_initialized_clients_have_one_pre_path_and_original_proof(self):
        gate = self.h.gate()
        self.h.collected(gate=gate)
        alternate = self.h.make_evidence(self.h.request, suffix="second-client")
        options = {"barrier": "after_pre_dispatch_persisted", "start_barrier": True,
                   "config_changes": {"sqlite_timeout": 2.0}}
        a = self.h.collected_worker(evidence=self.h.evidence, **options)
        ready_a = a.event()
        self.assertEqual((ready_a["event"], ready_a["stage"]), ("ready", "initialized"))
        b = self.h.collected_worker(evidence=alternate, **options)
        ready_b = b.event()
        self.assertEqual((ready_b["event"], ready_b["stage"]), ("ready", "initialized"))
        self.assertEqual(self.rows(), {"claims": 0, "proofs": 0})
        self.assertEqual(self.h.collector_counts()["records"], 0)
        a.release()
        b.release()
        observed = [(a, a.event(), self.h.evidence), (b, b.event(), alternate)]
        winners = [(p, event, evidence) for p, event, evidence in observed if event["event"] == "barrier"]
        followers = [(p, event) for p, event, _ in observed if event["event"] == "result"]
        self.assertEqual(len(winners), 1)
        self.assertEqual(len(followers), 1)
        self.assertEqual(winners[0][1]["stage"], "after_pre_dispatch_persisted")
        self.assertEqual(followers[0][1]["result"]["state"], "UNKNOWN")
        self.assertEqual(followers[0][1]["result"]["reason"], "durable_claim_outcome_unresolved")
        proof = gate.read_authorization(self.h.request)
        packed = authorization.load_json(proof["record_bytes"])
        self.assertEqual(packed["evidence"], {name: raw.hex() for name, raw in winners[0][2].items()})
        self.assert_original_claim()
        self.assertEqual(self.h.collector_counts()["collection_posts"], 1)
        self.assertEqual(self.h.collector_counts()["records"], 1)
        self.assert_no_payment()
        winners[0][0].release()
        self.assertEqual(winners[0][0].result()["state"], "SETTLED")
        self.assertEqual(followers[0][0].proc.wait(timeout=5), 0)
        self.assertEqual(self.h.collector_counts()["collection_posts"], 2)
        self.assertEqual(self.h.collector_counts()["records"], 2)
        self.assert_one_effect()


if __name__ == "__main__":
    unittest.main()
