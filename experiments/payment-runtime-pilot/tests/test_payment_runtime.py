"""Actual loopback/SQLite behavior, including native process failure boundaries.

Upstream business authorization is a caller responsibility. These synthetic
tests do not establish production exactly-once delivery or collector independence.
"""
from __future__ import annotations

import copy
from contextlib import closing
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import signal
import sqlite3
import sys
import threading
import unittest
from unittest import mock

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from runtime_support import Harness, runtime


class RedirectProbe:
    """An actual controlled loopback redirect/proxy trap, with no external I/O."""
    def __init__(self, location):
        self.posts = 0
        self.gets = 0
        owner = self

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                self.rfile.read(int(self.headers.get("Content-Length", "0")))
                owner.posts += 1
                self.send_response(307)
                self.send_header("Location", location)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def do_GET(self):
                owner.gets += 1
                self.send_response(307)
                self.send_header("Location", location)
                self.send_header("Content-Length", "0")
                self.end_headers()

            def log_message(self, *_):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.daemon_threads = True
        self.endpoint = f"http://127.0.0.1:{self.server.server_address[1]}"
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def close(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)
        if self.thread.is_alive():
            raise AssertionError("controlled redirect probe failed to shut down")


class PaymentRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def request(self, **changes):
        h = self.h
        fields = {"operation_id": "operation-A", "idempotency_key": "idempotency-A",
                  "configuration_digest": h.configuration_digest, "recovery_epoch": h.recovery_epoch,
                  "source_account": "source-A", "beneficiary": "beneficiary-A", "amount_minor": "1250"}
        fields.update(changes)
        return runtime.make_request(h.context, **fields)

    def assert_one_effect(self):
        counts = self.h.counts()
        self.assertEqual(counts["post_attempts"], 1)
        self.assertEqual(counts["effects"], 1)
        self.assertEqual(counts["payments"], 1)
        self.assertEqual(int(counts["balances"]["source-A"]), 98750)
        self.assertEqual(int(counts["balances"]["beneficiary-A"]), 1250)
        self.assertEqual(int(counts["balances"]["beneficiary-B"]), 0)
        return counts

    def journal_states(self):
        with closing(sqlite3.connect(self.h.journal_path)) as db:
            return [row[0] for row in db.execute("SELECT state FROM dispatches")]

    def native_post(self, request):
        raw = runtime.request_bytes(request)
        port = int(self.h.endpoint.rsplit(":", 1)[1])
        connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
        try:
            connection.request("POST", "/payments", body=raw, headers={
                "Authorization": "Bearer " + self.h.credential,
                "Content-Type": "application/json", "Content-Length": str(len(raw))})
            response = connection.getresponse()
            return response.status, response.read()
        finally:
            connection.close()

    def test_healthy_dispatch_has_one_real_post_and_atomic_local_balance_effect(self):
        result = self.h.adapter().submit(self.h.request)
        self.assertEqual(result["state"], "SETTLED")
        self.assertIsInstance(result["receipt_bytes"], bytes)
        self.assertIs(result["business_authorization_verified"], False)
        self.assertIs(result["automatic_retry"], False)
        self.assert_one_effect()
        self.assertEqual(self.journal_states(), ["SETTLED"])

    def test_repeated_submit_after_adapter_restart_uses_original_receipt_without_post(self):
        first = self.h.adapter().submit(self.h.request)
        second = self.h.adapter().submit(copy.deepcopy(self.h.request))
        self.assertEqual(second["state"], "SETTLED")
        self.assertEqual(first["receipt_bytes"], second["receipt_bytes"])
        self.assert_one_effect()

    def test_verified_terminal_reconciliation_and_status_use_no_network(self):
        adapter = self.h.adapter()
        first = adapter.submit(self.h.request)
        with mock.patch.object(adapter, "_http", side_effect=AssertionError("unexpected network")) as network:
            reconciled = adapter.reconcile(self.h.request)
            local = adapter.read_status(self.h.request)
            network.assert_not_called()
        self.assertEqual(first["receipt_bytes"], reconciled["receipt_bytes"])
        self.assertEqual(first["receipt_bytes"], local["receipt_bytes"])
        self.assertEqual(reconciled["state"], "SETTLED")
        self.assertEqual(self.h.counts()["lookup_attempts"], 0)
        self.assert_one_effect()

    def test_provider_direct_replay_and_client_suppression_have_separate_counts(self):
        first = self.h.adapter().submit(self.h.request)
        status, replayed = self.native_post(self.h.request)
        self.assertEqual(status, 200)
        self.assertEqual(first["receipt_bytes"], replayed)
        counts = self.h.counts()
        self.assertEqual(counts["post_attempts"], 2)
        self.assertEqual(counts["payments"], 1)
        self.assertEqual(counts["effects"], 1)
        self.assertEqual(self.h.adapter().submit(self.h.request)["receipt_bytes"], replayed)
        self.assertEqual(self.h.counts()["post_attempts"], 2)
        self.assertEqual(len(self.journal_states()), 1)

    def test_provider_alias_conflicts_cannot_create_a_second_effect(self):
        self.h.adapter().submit(self.h.request)
        for changes in ({"idempotency_key": "other-key"}, {"operation_id": "other-operation"},
                        {"amount_minor": "9999"}, {"beneficiary": "beneficiary-B"}):
            with self.subTest(changes=changes):
                status, _ = self.native_post(self.request(**changes))
                self.assertEqual(status, 409)
                self.assertEqual(self.h.counts()["effects"], 1)
                self.assertEqual(self.h.counts()["payments"], 1)
        self.assertEqual(self.h.counts()["post_attempts"], 5)

    def test_real_receipt_corruption_wrong_scope_and_wrong_signer_are_rejected(self):
        settled = self.h.adapter().submit(self.h.request)
        original = runtime.load_json(settled["receipt_bytes"])
        raw_request = runtime.request_bytes(self.h.request)
        public = self.h.key.public_key().public_bytes_raw()
        runtime.verify_receipt(settled["receipt_bytes"], raw_request, public)
        corrupted = copy.deepcopy(original)
        signature = corrupted["signature"]
        corrupted["signature"] = ("0" if signature[0] != "0" else "1") + signature[1:]
        with self.assertRaises(ValueError):
            runtime.verify_receipt(runtime.canonical_json(corrupted), raw_request, public)
        for change in ("provider", "request", "digest"):
            with self.subTest(change=change):
                bad = copy.deepcopy(original)
                if change == "provider":
                    bad["payload"]["provider_id"] = "different-provider"
                elif change == "request":
                    bad["payload"]["request"]["tenant"] = "different-tenant"
                else:
                    bad["payload"]["request_digest"] = "sha256:" + "dd" * 32
                bad["signature"] = self.h.key.sign(
                    runtime.SIGNING_DOMAIN + runtime.canonical_json(bad["payload"])).hex()
                with self.assertRaises(ValueError):
                    runtime.verify_receipt(runtime.canonical_json(bad), raw_request, public)
        wrong_public = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
        with self.assertRaises(ValueError):
            runtime.verify_receipt(settled["receipt_bytes"], raw_request, wrong_public)
        self.assert_one_effect()

    def test_real_insufficient_funds_receipt_is_failed_without_balance_effect(self):
        request = self.request(amount_minor="100001")
        adapter = self.h.adapter()
        failed = adapter.submit(request)
        self.assertEqual(failed["state"], "FAILED")
        receipt = runtime.verify_receipt(failed["receipt_bytes"], runtime.request_bytes(request),
                                         self.h.key.public_key().public_bytes_raw())
        self.assertEqual(receipt["status"], "failed")
        self.assertEqual(receipt["failure_reason"], "insufficient_funds")
        self.assertIsNone(receipt["effect_id"])
        self.assertEqual(adapter.submit(request)["receipt_bytes"], failed["receipt_bytes"])
        self.assertEqual(adapter.reconcile(request)["state"], "FAILED")
        counts = self.h.counts()
        self.assertEqual(counts["post_attempts"], 1)
        self.assertEqual(counts["effects"], 0)
        self.assertEqual(counts["failed_payments"], 1)
        self.assertEqual(counts["settled_payments"], 0)
        self.assertEqual(counts["balances"], self.h.initial_balances)
        self.assertEqual(self.journal_states(), ["FAILED"])

    def test_wrong_pinned_provider_key_cannot_confirm_real_committed_response(self):
        wrong_public = Ed25519PrivateKey.generate().public_key().public_bytes_raw()
        adapter = self.h.adapter(provider_public_key_hex=wrong_public.hex())
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(adapter.reconcile(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assert_one_effect()
        self.assertEqual(self.journal_states(), ["CLAIMED"])

    def test_wrong_pinned_provider_identity_cannot_confirm_real_committed_response(self):
        adapter = self.h.adapter(provider_id="different-synthetic-provider")
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(adapter.reconcile(self.h.request)["state"], "UNKNOWN")
        self.assert_one_effect()
        self.assertEqual(self.journal_states(), ["CLAIMED"])

    def test_bad_native_response_keeps_claim_until_genuine_readonly_receipt_is_recovered(self):
        # Each POST really commits at the native provider. The trusted test
        # harness then corrupts/re-signs only the received bytes, so this tests
        # the adapter's confirmation boundary without faking provider effects.
        adapter = self.h.adapter()
        genuine_http = adapter._http
        for index, fault in enumerate(("corrupt", "wrong_scope", "wrong_provider", "pending", "http_only"), 1):
            with self.subTest(fault=fault):
                request = self.request(operation_id=f"fault-operation-{index}",
                                       idempotency_key=f"fault-idempotency-{index}")

                def faulty_response(method, path, body=None):
                    status, received = genuine_http(method, path, body)
                    self.assertEqual(method, "POST")
                    self.assertEqual(status, 200)
                    if fault == "http_only":
                        return status, b'{"ok":true}'
                    envelope = runtime.load_json(received)
                    if fault == "corrupt":
                        signature = envelope["signature"]
                        envelope["signature"] = ("0" if signature[0] != "0" else "1") + signature[1:]
                    else:
                        payload = envelope["payload"]
                        if fault == "wrong_scope":
                            payload["request"]["tenant"] = "different-tenant"
                        elif fault == "wrong_provider":
                            payload["provider_id"] = "different-provider"
                        else:
                            payload.update(status="pending", effect_id=None, failure_reason=None)
                        envelope["signature"] = self.h.key.sign(
                            runtime.SIGNING_DOMAIN + runtime.canonical_json(payload)).hex()
                    return status, runtime.canonical_json(envelope)

                with mock.patch.object(adapter, "_http", side_effect=faulty_response):
                    result = adapter.submit(request)
                self.assertEqual(result["state"], "UNKNOWN")
                self.assertEqual(adapter.submit(request)["state"], "UNKNOWN")
                self.assertEqual(self.h.counts()["post_attempts"], index)
                self.assertEqual(self.h.counts()["effects"], index)
                recovered = adapter.reconcile(request)
                self.assertEqual(recovered["state"], "SETTLED")
                self.assertEqual(adapter.submit(request)["receipt_bytes"], recovered["receipt_bytes"])
                self.assertEqual(self.h.counts()["post_attempts"], index)
                self.assertEqual(self.h.counts()["effects"], index)

    def test_two_concurrent_native_clients_share_one_durable_claim_and_post(self):
        # Every Adapter constructor performs write initialization. Complete each
        # before releasing concurrent claims; 2s is the bounded healthy-contention
        # budget, while dedicated lock-failure tests keep the short default.
        options = {"barrier": "after_claim", "start_barrier": True,
                   "config_changes": {"sqlite_timeout": 2.0}}
        a = self.h.worker(**options)
        ready_a = a.event()
        self.assertEqual((ready_a["event"], ready_a["stage"]), ("ready", "initialized"))
        b = self.h.worker(**options)
        ready_b = b.event()
        self.assertEqual((ready_b["event"], ready_b["stage"]), ("ready", "initialized"))
        self.assertEqual(self.journal_states(), [])
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        a.release()
        b.release()
        events = [(a, a.event()), (b, b.event())]
        claimed = [(p, e) for p, e in events if e.get("event") == "barrier"]
        already_claimed = [(p, e) for p, e in events if e.get("event") == "result"]
        self.assertEqual(len(claimed), 1)
        self.assertEqual(len(already_claimed), 1)
        self.assertEqual(claimed[0][1]["stage"], "after_claim")
        self.assertEqual(already_claimed[0][1]["result"]["state"], "UNKNOWN")
        self.assertEqual(already_claimed[0][1]["result"]["reason"], "durable_claim_outcome_unresolved")
        self.assertEqual(self.journal_states(), ["CLAIMED"])
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        claimed[0][0].release()
        self.assertEqual(claimed[0][0].result()["state"], "SETTLED")
        self.assertEqual(already_claimed[0][0].proc.wait(timeout=5), 0)
        self.assert_one_effect()

    def test_amount_beneficiary_or_alias_changes_cannot_reuse_a_consumed_request(self):
        first = self.h.adapter().submit(self.h.request)
        variants = (
            {"amount_minor": "1251"}, {"beneficiary": "beneficiary-B"},
            {"idempotency_key": "different-idempotency"}, {"operation_id": "different-operation"},
        )
        for changes in variants:
            with self.subTest(changes=changes):
                result = self.h.adapter().submit(self.request(**changes))
                self.assertEqual(result["state"], "CONFLICT")
                self.assert_one_effect()
        self.assertEqual(self.h.adapter().read_status(self.h.request)["receipt_bytes"],
                         first["receipt_bytes"])

    def test_epoch_and_configuration_rotation_do_not_reset_consumed_aliases(self):
        first = self.h.adapter().submit(self.h.request)
        configuration = "sha256:" + "cd" * 32
        adapter = self.h.adapter(configuration_digest=configuration, recovery_epoch=2)
        changed = self.request(configuration_digest=configuration, recovery_epoch=2)
        self.assertEqual(adapter.submit(changed)["state"], "CONFLICT")
        self.assertEqual(adapter.submit(self.h.request)["receipt_bytes"], first["receipt_bytes"])
        self.assert_one_effect()

    def test_changed_currency_or_unit_cannot_open_a_new_consumption_scope(self):
        self.h.adapter().submit(self.h.request)
        for field, value in (("currency", "EUR"), ("minor_unit_scale", 3)):
            with self.subTest(field=field):
                context = {**self.h.context, field: value}
                with self.assertRaises((ValueError, RuntimeError)):
                    self.h.adapter(context=context)
                self.assert_one_effect()

    def test_provider_commit_then_lost_ack_stays_unknown_until_readonly_reconciliation(self):
        self.h.stop_provider()
        self.h.provider_config["drop_after_commit"] = True
        self.h.start_provider()
        adapter = self.h.adapter()
        first = adapter.submit(self.h.request)
        self.assertEqual(first["state"], "UNKNOWN")
        self.assert_one_effect()
        self.assertEqual(self.h.adapter().submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(self.h.counts()["post_attempts"], 1)
        recovered = self.h.adapter().reconcile(self.h.request)
        self.assertEqual(recovered["state"], "SETTLED")
        self.assertEqual(self.h.counts()["lookup_attempts"], 1)
        self.assert_one_effect()
        self.assertEqual(self.h.adapter().submit(self.h.request)["receipt_bytes"],
                         recovered["receipt_bytes"])

    def test_sigkill_after_claim_before_post_never_becomes_permission_to_resend(self):
        worker = self.h.worker(barrier="after_claim")
        event = worker.event()
        self.assertEqual((event["event"], event["stage"]), ("barrier", "after_claim"))
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        self.assertEqual(worker.kill(), -signal.SIGKILL)
        adapter = self.h.adapter()
        self.assertEqual(adapter.read_status(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        # An actual absent lookup is still not evidence that a safe retry exists.
        self.assertEqual(adapter.reconcile(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        self.assertEqual(self.h.counts()["effects"], 0)
        self.assertEqual(self.h.counts()["lookup_attempts"], 1)
        self.assertEqual(self.journal_states(), ["CLAIMED"])

    def test_sigkill_after_real_response_before_local_store_recovers_original_receipt(self):
        worker = self.h.worker(barrier="after_response")
        event = worker.event()
        self.assertEqual((event["event"], event["stage"]), ("barrier", "after_response"))
        self.assert_one_effect()
        self.assertEqual(self.journal_states(), ["CLAIMED"])
        worker.kill()
        adapter = self.h.adapter()
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        recovered = adapter.reconcile(self.h.request)
        self.assertEqual(recovered["state"], "SETTLED")
        self.assertEqual(adapter.read_status(self.h.request)["receipt_bytes"], recovered["receipt_bytes"])
        self.assert_one_effect()

    def test_provider_sigkill_after_commit_recovers_with_same_db_and_stable_receipt(self):
        self.h.stop_provider()
        provider = self.h.start_provider(barrier="after_commit")
        worker = self.h.worker()
        event = provider.event()
        self.assertEqual((event["event"], event["stage"]), ("barrier", "after_commit"))
        self.assert_one_effect()
        provider.kill()
        provider.close()
        self.h.provider = None
        self.assertEqual(worker.result()["state"], "UNKNOWN")
        self.h.start_provider()
        adapter = self.h.adapter()
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        one = adapter.reconcile(self.h.request)
        two = adapter.reconcile(self.h.request)
        self.assertEqual(one["state"], "SETTLED")
        self.assertEqual(one["receipt_bytes"], two["receipt_bytes"])
        self.assert_one_effect()

    def test_real_journal_lock_before_claim_blocks_every_post(self):
        adapter = self.h.adapter()
        with closing(sqlite3.connect(self.h.journal_path, timeout=0.1)) as locked:
            locked.execute("BEGIN IMMEDIATE")
            result = adapter.submit(self.h.request)
            self.assertEqual(result["state"], "JOURNAL_UNAVAILABLE")
            self.assertEqual(self.h.counts()["post_attempts"], 0)
            self.assertEqual(self.h.counts()["effects"], 0)
            locked.rollback()
        self.assertEqual(self.journal_states(), [])

    def test_real_result_store_lock_keeps_the_claim_after_provider_effect(self):
        worker = self.h.worker(barrier="after_response")
        event = worker.event()
        self.assertEqual(event["stage"], "after_response")
        self.assert_one_effect()
        with closing(sqlite3.connect(self.h.journal_path, timeout=0.1)) as locked:
            locked.execute("BEGIN IMMEDIATE")
            worker.release()
            result = worker.result()
            self.assertEqual(result["state"], "UNKNOWN")
            locked.rollback()
        self.assertEqual(self.journal_states(), ["CLAIMED"])
        adapter = self.h.adapter()
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(adapter.reconcile(self.h.request)["state"], "SETTLED")
        self.assert_one_effect()

    def test_late_submitter_failure_cannot_downgrade_an_independently_reconciled_result(self):
        worker = self.h.worker(barrier="after_response")
        self.assertEqual(worker.event()["stage"], "after_response")
        adapter = self.h.adapter()
        reconciled = adapter.reconcile(self.h.request)
        self.assertEqual(reconciled["state"], "SETTLED")
        worker.release(raise_after=True)
        self.assertIn(worker.result()["state"], ("UNKNOWN", "SETTLED"))
        self.assertEqual(self.journal_states(), ["SETTLED"])
        self.assertEqual(adapter.read_status(self.h.request)["receipt_bytes"],
                         reconciled["receipt_bytes"])
        self.assert_one_effect()

    def test_stopped_provider_gives_no_effect_and_consumed_unknown_claim(self):
        adapter = self.h.adapter()
        self.h.stop_provider()
        result = adapter.submit(self.h.request)
        self.assertEqual(result["state"], "UNKNOWN")
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        self.assertEqual(self.h.counts()["effects"], 0)
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(self.journal_states(), ["CLAIMED"])

    def test_status_and_reconciliation_do_not_claim_or_reset_an_unsubmitted_request(self):
        adapter = self.h.adapter()
        before = self.h.counts()
        adapter.read_status(self.h.request)
        adapter.reconcile(self.h.request)
        after = self.h.counts()
        self.assertEqual(after["post_attempts"], before["post_attempts"])
        self.assertEqual(after["effects"], 0)
        self.assertEqual(self.journal_states(), [])

    def test_invalid_amount_units_and_request_shapes_never_reach_provider(self):
        adapter = self.h.adapter()
        for field, value in (("amount_minor", 1250), ("amount_minor", True),
                             ("amount_minor", 12.50), ("amount_minor", "01250"),
                             ("amount_minor", "1.25"), ("amount_minor", "-1"),
                             ("amount_minor", "0"), ("amount_minor", "9" * 79),
                             ("minor_unit_scale", True), ("recovery_epoch", True),
                             ("operation_id", "x" * 129)):
            with self.subTest(field=field, value=value):
                candidate = copy.deepcopy(self.h.request)
                candidate[field] = value
                self.assertEqual(adapter.submit(candidate)["state"], "REJECTED")
        candidate = copy.deepcopy(self.h.request)
        candidate["human_approved"] = True
        self.assertEqual(adapter.submit(candidate)["state"], "REJECTED")
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        self.assertEqual(self.journal_states(), [])

    def test_parser_does_not_accept_ambiguous_numeric_or_duplicate_json(self):
        for raw in (b'{"amount_minor":1,"amount_minor":2}', b'{"n":1.0}',
                    b'{"n":NaN}', b'{"n":9007199254740992}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                runtime.load_json(raw)
        with self.assertRaises(ValueError):
            runtime.canonical_json({"text": "e\u0301"})

    def test_nonliteral_loopback_targets_are_rejected_before_any_connection(self):
        endpoints = (
            "http://example.invalid:80", "http://169.254.169.254:80",
            "http://localhost:80", "http://2130706433:80", "http://127.0.0.1.evil.invalid:80",
            "http://user:password@127.0.0.1:80", "https://127.0.0.1:80",
            "http://127.0.0.1:80/payments", "http://127.0.0.1:80?x=y",
            "http://127.0.0.1:80#fragment", "http://127.0.0.1:0", "http://127.0.0.1:65536",
        )
        with mock.patch("socket.create_connection", side_effect=AssertionError("unexpected connection")):
            for endpoint in endpoints:
                with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                    self.h.adapter(endpoint=endpoint)
        self.assertEqual(self.h.counts()["post_attempts"], 0)

    def test_native_transport_ignores_environment_proxy_configuration(self):
        trap = RedirectProbe(self.h.endpoint + "/payments")
        self.addCleanup(trap.close)
        environment = {name: trap.endpoint for name in (
            "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "http_proxy", "https_proxy", "all_proxy")}
        environment.update(NO_PROXY="", no_proxy="")
        result = self.h.worker(env=environment).result()
        self.assertEqual(result["state"], "SETTLED")
        self.assertEqual((trap.posts, trap.gets), (0, 0))
        self.assert_one_effect()

    def test_redirect_is_not_followed_and_cannot_rearm_consumed_claim(self):
        trap = RedirectProbe(self.h.endpoint + "/payments")
        self.addCleanup(trap.close)
        adapter = self.h.adapter(endpoint=trap.endpoint)
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(trap.posts, 1)
        self.assertEqual(self.h.counts()["post_attempts"], 0)
        self.assertEqual(adapter.submit(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(trap.posts, 1)
        self.assertEqual(adapter.reconcile(self.h.request)["state"], "UNKNOWN")
        self.assertEqual(trap.gets, 1)
        self.assertEqual(self.h.counts()["lookup_attempts"], 0)
        self.assertEqual(self.journal_states(), ["CLAIMED"])


if __name__ == "__main__":
    unittest.main()
