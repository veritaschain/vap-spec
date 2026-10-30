"""Gateway diagnostics over real SQLite and explicit, non-network test doubles."""

import hashlib
import sqlite3
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from uuid import uuid4

from collector_pilot.gateway import CollectorGateway
from collector_pilot.harness import COLLECTOR_ID, SYNTHETIC_BYTES, make_case, make_keys
from collector_pilot.protocol import (
    InputError, canonical, capture, digest, sign_control, sign_record, timestamp,
    validate_intent, validate_query, verify_control,
)
from incident_assessor.assess import assess
from upload_pilot.journal import Journal
from upload_pilot.protocol import (
    MAX_PAYLOAD, sign_control as sign_upload_control,
    verify_control as verify_upload_control,
)


def iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


class DiagnosticClock:
    def __init__(self, start):
        self.value = timestamp(start) + timedelta(milliseconds=10)
        self.lock = threading.Lock()

    def __call__(self):
        with self.lock:
            self.value += timedelta(milliseconds=1)
            return iso(self.value)

    def advance(self, seconds):
        with self.lock:
            self.value += timedelta(seconds=seconds)


class CollectorDouble:
    """Signed in-memory responses; never evidence that an HTTP collector ran."""
    endpoint = "http://127.0.0.1:43112"

    def __init__(self, keys, clock, mode="normal"):
        self.keys, self.clock, self.mode = keys, clock, mode
        self.collect_calls = self.status_calls = 0
        self.rows = {}

    def _sign(self, body):
        return sign_control(body, self.keys["collector"]["secret"], self.keys["collector"]["key_id"])

    def collect(self, value):
        self.collect_calls += 1
        started = self.clock()
        value = capture(value)
        body = validate_intent(verify_control(value, self.keys["gateway"]["public"],
                                             self.keys["gateway"]["key_id"], "collection_intent"))
        if self.mode == "unavailable":
            return {"attempted": True, "attempted_at": started, "completed_at": self.clock(),
                    "status": None, "response": None, "error": "DIAGNOSTIC_UNAVAILABLE"}
        receipt = self._sign({
            "kind": "collection_receipt", "collector_id": body["collector_id"],
            "collection_id": body["collection_id"], "request_id": body["request_id"],
            "request_sha256": digest(value), "recorded_at": self.clock(),
            "receipt_id": "diagnostic-" + uuid4().hex, "storage": "sqlite-wal-full",
        })
        self.rows[body["collection_id"]] = {"intent": value, "receipt": receipt}
        lost = self.mode == "drop_after_commit"
        return {"attempted": True, "attempted_at": started, "completed_at": self.clock(),
                "status": None if lost else 200, "response": None if lost else deepcopy(receipt),
                "error": "DIAGNOSTIC_RESPONSE_LOST" if lost else None}

    def status(self, value):
        self.status_calls += 1
        started = self.clock()
        value = capture(value)
        body = validate_query(verify_control(value, self.keys["gateway"]["public"],
                                            self.keys["gateway"]["key_id"], "collection_query"))
        if self.mode == "status_unavailable":
            return {"attempted": True, "attempted_at": started, "completed_at": self.clock(),
                    "status": None, "response": None, "error": "DIAGNOSTIC_UNAVAILABLE"}
        row = None if self.mode == "not_found" else self.rows.get(body["collection_id"])
        response = self._sign({
            "kind": "collection_status", "collector_id": body["collector_id"],
            "collection_id": body["collection_id"], "request_id": body["request_id"],
            "request_sha256": body["request_sha256"], "query_sha256": digest(value),
            "nonce": body["nonce"], "status": "FOUND" if row else "NOT_FOUND",
            "receipt": deepcopy(row["receipt"]) if row else None, "checked_at": self.clock(),
        })
        return {"attempted": True, "attempted_at": started, "completed_at": self.clock(),
                "status": 200, "response": response, "error": None}


class TransportDouble:
    """An explicit diagnostic transport; no socket or receiver process is used."""
    endpoint = "http://127.0.0.1:43111/upload"

    def __init__(self, keys, clock):
        self.keys, self.clock = keys, clock
        self.calls = []
        self.raise_on_send = False

    def send(self, payload, envelope):
        self.calls.append(bytes(payload))
        if self.raise_on_send:
            raise OSError("diagnostic send failure")
        body = verify_upload_control(envelope, self.keys["gateway"]["public"],
                                     self.keys["gateway"]["key_id"], "dispatch_intent")
        started, dispatched, received = self.clock(), self.clock(), self.clock()
        receipt = sign_upload_control({
            "kind": "upload_receipt", "request_id": body["request_id"],
            "subject_sha256": body["subject_sha256"], "payload_sha256": hashlib.sha256(payload).hexdigest(),
            "byte_length": len(payload), "received_at": received, "receipt_id": "diagnostic-receiver",
        }, self.keys["receiver"]["secret"], self.keys["receiver"]["key_id"])
        return {"attempted": True, "body_send_completed": True, "attempted_at": started,
                "dispatched_at": dispatched, "status": 200, "receipt": receipt, "error": None}


class BeforeCommitFailure(Journal):
    def _commit(self, connection):
        raise OSError("diagnostic failure before commit")


class FinishFailure(Journal):
    def finish(self, request_id, state, details):
        raise OSError("diagnostic result-write failure")


class ClaimBarrier:
    def __init__(self, inner, barrier):
        self.inner, self.barrier = inner, barrier

    def get(self, request_id):
        return self.inner.get(request_id)

    def claim(self, *args):
        self.barrier.wait(timeout=5)
        return self.inner.claim(*args)

    def finish(self, *args):
        return self.inner.finish(*args)


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.keys = make_keys()

    def setup_case(self, *, payload=SYNTHETIC_BYTES, mode="normal", journal_type=Journal, **kwargs):
        package, trust, config, _ = make_case(payload, TransportDouble.endpoint, keys=self.keys, **kwargs)
        clock = DiagnosticClock(package["as_of"])
        collector, transport = CollectorDouble(self.keys, clock, mode), TransportDouble(self.keys, clock)
        path = Path(self.directory.name) / (uuid4().hex + ".sqlite")
        journal = journal_type(path)
        gateway = CollectorGateway(config, journal, transport, collector, collector_id=COLLECTOR_ID,
                                   collector_public=self.keys["collector"]["public"],
                                   collector_key_id=self.keys["collector"]["key_id"], clock=clock)
        return package, trust, config, clock, collector, transport, journal, gateway

    @staticmethod
    def request_id(package):
        return package["target"]["subject"]["request_id"]

    def no_rpcs(self, collector, transport):
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), (0, 0, 0))

    def test_success_preserves_reproducible_frames_and_separate_diagnostic_evidence(self):
        package, trust, _, _, collector, transport, journal, gateway = self.setup_case()
        result = gateway.execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["state"], "RECEIPT_CONFIRMED")
        self.assertEqual(result["collector_outcome"], "FRESH_READBACK_CONFIRMED")
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), (1, 1, 1))
        self.assertEqual(transport.calls, [SYNTHETIC_BYTES])
        self.assertEqual(result["payload_sha256"], hashlib.sha256(SYNTHETIC_BYTES).hexdigest())
        self.assertEqual(result["byte_length"], len(SYNTHETIC_BYTES))
        self.assertEqual(result["admission"]["assessment"]["assessments"]["transfer_authorization"], "REVIEW")
        self.assertEqual(result["final"]["assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        self.assertEqual(result["postflight"]["assessment"]["assessments"]["observed_action_authorization"], "REVIEW")
        for phase in ("admission", "final", "postflight"):
            frame = result[phase]
            self.assertEqual(frame["assessment"], assess(frame["evidence"], frame["trust"], allow_synthetic=True))
        self.assertIsNotNone(result["collection_receipt"])
        self.assertIsNotNone(result["payload_receipt"])
        saved = journal.get(self.request_id(package))
        self.assertEqual(saved["state"], "receipt_confirmed")
        self.assertEqual(saved["details"], result)
        self.assertNotIn(SYNTHETIC_BYTES, canonical(saved))
        for role in self.keys.values():
            self.assertNotIn(role["secret"].encode(), canonical(result))

    def test_generic_review_denial_and_wrong_measured_bytes_never_collect(self):
        for mutation in ("deny", "missing_permit", "wrong_payload", "wrong_tenant"):
            with self.subTest(mutation=mutation):
                kwargs = {"decision": "deny"} if mutation == "deny" else {}
                if mutation == "wrong_tenant":
                    kwargs["grant_changes"] = {"tenant_id": "other-tenant"}
                package, trust, _, _, collector, transport, journal, gateway = self.setup_case(**kwargs)
                if mutation == "missing_permit":
                    package["records"] = [item for item in package["records"] if item["body"]["kind"] != "transfer.decision"]
                actual = b"different measured bytes" if mutation == "wrong_payload" else SYNTHETIC_BYTES
                result = gateway.execute(package, trust, actual)
                self.assertEqual(result["state"], "BLOCKED_WITHOUT_ATTEMPT")
                self.assertEqual(result["reason"], "POLICY_OR_PERMIT_NOT_AUTHORIZED")
                self.no_rpcs(collector, transport)
                self.assertIsNone(journal.get(self.request_id(package)))

    def test_initial_observation_records_and_payload_limits_are_rejected(self):
        package, trust, _, _, collector, transport, journal, gateway = self.setup_case()
        body = {"record_id": "untrusted-input-observation", "kind": "transfer.collector_health",
                "evaluation_id": package["evaluation_id"], "issuer": self.keys["gateway"]["issuer"],
                "recorded_at": package["as_of"], "binding": deepcopy(package["target"]["subject"]),
                "data": {"checked_at": package["as_of"], "available": True, "durable_acknowledged": True}}
        extra = deepcopy(package)
        extra["records"].append(sign_record(body, self.keys["gateway"]["secret"], self.keys["gateway"]["key_id"]))
        with self.assertRaises(InputError):
            gateway.execute(extra, trust, SYNTHETIC_BYTES)
        for payload in ("text", b"x" * (MAX_PAYLOAD + 1)):
            with self.subTest(payload_type=type(payload).__name__), self.assertRaises(InputError):
                gateway.execute(package, trust, payload)
        self.no_rpcs(collector, transport)
        self.assertIsNone(journal.get(self.request_id(package)))

    def test_changed_configured_endpoint_blocks_before_claim(self):
        package, trust, _, _, collector, transport, journal, gateway = self.setup_case()
        collector.endpoint = "http://127.0.0.1:43113"
        result = gateway.execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["reason"], "CONFIGURED_ENDPOINT_CHANGED")
        self.no_rpcs(collector, transport)
        self.assertIsNone(journal.get(self.request_id(package)))

    def test_lost_ack_readback_does_not_resume_or_change_prior_result(self):
        package, trust, _, _, collector, transport, journal, gateway = self.setup_case(mode="drop_after_commit")
        result = gateway.execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["state"], "BLOCKED_WITHOUT_ATTEMPT")
        self.assertEqual(result["final"]["assessment"]["assessments"]["transfer_authorization"], "DENY")
        self.assertEqual(len(collector.rows), 1)
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), (1, 0, 0))
        before = journal.get(self.request_id(package))
        collector.mode = "normal"
        reconciled = gateway.reconcile(self.request_id(package))
        self.assertEqual(reconciled["state"], "FOUND")
        self.assertFalse(reconciled["attempted"])
        self.assertFalse(reconciled["upload_resumed"])
        self.assertEqual(journal.get(self.request_id(package)), before)
        self.assertEqual(result["state"], "BLOCKED_WITHOUT_ATTEMPT")
        replay = gateway.execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(replay["state"], "REPLAY_NO_SEND")
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), (1, 1, 0))

    def test_unavailable_and_authenticated_not_found_checks_block_scope(self):
        for mode, expected_calls, available in (("unavailable", (1, 0, 0), False),
                                                ("status_unavailable", (1, 1, 0), False),
                                                ("not_found", (1, 1, 0), True)):
            with self.subTest(mode=mode):
                package, trust, _, _, collector, transport, _, gateway = self.setup_case(mode=mode)
                result = gateway.execute(package, trust, SYNTHETIC_BYTES)
                self.assertFalse(result["attempted"])
                self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), expected_calls)
                self.assertEqual(result["final"]["assessment"]["assessments"]["application_route_action"], "BLOCK")
                health = [item for item in result["final"]["evidence"]["records"]
                          if item["body"]["kind"] == "transfer.collector_health"]
                self.assertEqual(len(health), 1)
                self.assertIs(health[0]["body"]["data"]["available"], available)
                self.assertFalse(health[0]["body"]["data"]["durable_acknowledged"])

    def test_expiry_and_regressed_clock_after_collection_never_send(self):
        for change in ("expiry", "regression"):
            with self.subTest(change=change):
                package, trust, _, clock, collector, transport, journal, gateway = self.setup_case()
                result = gateway.execute(package, trust, SYNTHETIC_BYTES,
                                         before_final_check=lambda: clock.advance(200 if change == "expiry" else -200))
                self.assertFalse(result["attempted"])
                self.assertEqual(transport.calls, [])
                self.assertEqual(collector.collect_calls, 1)
                self.assertEqual(journal.get(self.request_id(package))["state"], "blocked_after_intent")
                if change == "expiry":
                    self.assertEqual(result["reason"], "FINAL_ASSESSOR_RECHECK_DID_NOT_ALLOW")
                    self.assertEqual(result["collector_outcome"], "FRESH_READBACK_CONFIRMED")
                else:
                    self.assertEqual(collector.status_calls, 0)
                    self.assertEqual(result["reason"], "COLLECTOR_READBACK_NOT_ESTABLISHED")

    def test_precommit_failure_does_not_claim_durable_consumption(self):
        package, trust, config, clock, collector, transport, journal, gateway = self.setup_case(journal_type=BeforeCommitFailure)
        result = gateway.execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["reason"], "JOURNAL_INTENT_COMMIT_NOT_ESTABLISHED")
        self.assertEqual(result["journal_state"], "NOT_CLAIMED")
        self.assertIsNone(journal.get(self.request_id(package)))
        self.no_rpcs(collector, transport)
        explicitly_retried = CollectorGateway(config, Journal(journal.path), transport, collector,
                                             collector_id=COLLECTOR_ID,
                                             collector_public=self.keys["collector"]["public"],
                                             collector_key_id=self.keys["collector"]["key_id"], clock=clock)
        self.assertEqual(explicitly_retried.execute(package, trust, SYNTHETIC_BYTES)["state"], "RECEIPT_CONFIRMED")

    def test_result_persistence_failure_and_restart_do_not_duplicate_upload(self):
        package, trust, config, clock, collector, transport, journal, gateway = self.setup_case(journal_type=FinishFailure)
        result = gateway.execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertEqual(result["reason"], "JOURNAL_RESULT_PERSISTENCE_FAILED")
        self.assertTrue(result["attempted"])
        self.assertIsNotNone(result["payload_transport"])
        self.assertIsNone(result["payload_receipt"])
        self.assertEqual(journal.get(self.request_id(package))["state"], "dispatch_intent")
        restarted = CollectorGateway(config, Journal(journal.path), transport, collector,
                                     collector_id=COLLECTOR_ID,
                                     collector_public=self.keys["collector"]["public"],
                                     collector_key_id=self.keys["collector"]["key_id"], clock=clock)
        self.assertEqual(restarted.execute(package, trust, SYNTHETIC_BYTES)["state"], "REPLAY_NO_SEND")
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), (1, 1, 1))

    def test_same_request_different_payload_is_conflict_without_rpcs(self):
        package, trust, _, _, collector, transport, _, gateway = self.setup_case()
        self.assertEqual(gateway.execute(package, trust, SYNTHETIC_BYTES)["state"], "RECEIPT_CONFIRMED")
        conflict = gateway.execute(package, trust, b"new bytes under the same request ID")
        self.assertEqual(conflict["state"], "REQUEST_ID_CONFLICT")
        self.assertFalse(conflict["attempted"])
        self.assertIsNone(conflict["payload_receipt"])
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), (1, 1, 1))

    def test_concurrent_claims_allow_one_diagnostic_upload_only(self):
        package, trust, config, clock, collector, transport, journal, _ = self.setup_case()
        shared = ClaimBarrier(journal, threading.Barrier(2))
        gateways = [CollectorGateway(config, shared, transport, collector, collector_id=COLLECTOR_ID,
                                     collector_public=self.keys["collector"]["public"],
                                     collector_key_id=self.keys["collector"]["key_id"], clock=clock) for _ in range(2)]
        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(gateway.execute, package, trust, SYNTHETIC_BYTES) for gateway in gateways]
            results = [future.result(timeout=10) for future in futures]
        self.assertEqual(sorted(item["state"] for item in results), ["RECEIPT_CONFIRMED", "REPLAY_NO_SEND"])
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), (1, 1, 1))

    def test_reconcile_missing_or_corrupt_owned_snapshot_performs_no_rpcs(self):
        package, trust, _, _, collector, transport, journal, gateway = self.setup_case(mode="unavailable")
        self.assertEqual(gateway.reconcile("missing-request")["state"], "REQUEST_NOT_FOUND")
        self.no_rpcs(collector, transport)
        gateway.execute(package, trust, SYNTHETIC_BYTES)
        calls = (collector.collect_calls, collector.status_calls, len(transport.calls))
        row = journal.get(self.request_id(package))
        row["snapshot"]["pins"]["collector_public"] = "00" * 32
        with closing(sqlite3.connect(journal.path)) as connection:
            connection.execute("UPDATE request_journal SET snapshot_json=? WHERE request_id=?",
                               (canonical(row["snapshot"]).decode(), self.request_id(package)))
            connection.commit()
        result = gateway.reconcile(self.request_id(package))
        self.assertEqual(result["state"], "JOURNAL_UNAVAILABLE")
        self.assertFalse(result["attempted"])
        self.assertEqual((collector.collect_calls, collector.status_calls, len(transport.calls)), calls)


if __name__ == "__main__":
    unittest.main()
