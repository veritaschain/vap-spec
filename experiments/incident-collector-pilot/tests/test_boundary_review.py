"""Independent boundary checks with real crypto/SQLite and diagnostic RPC doubles.

These tests do not establish HTTP or collector-process execution.  The separate
required process tests and finite suite own that claim.  No diagnostic capture
created here is published as a measured network scenario.
"""

import hashlib
import json
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import sqlite3
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from collector_pilot.exports import check_case, derive_actual
from collector_pilot.gateway import CollectorGateway
from collector_pilot.harness import COLLECTOR_ID, SYNTHETIC_BYTES, make_case, make_keys
from collector_pilot.protocol import (
    InputError, canonical, digest, sign_control, sign_record, timestamp, utc_now,
    validate_intent, validate_query, verify_control,
)
from incident_assessor.assess import assess
from upload_pilot.journal import Journal
from upload_pilot.protocol import sign_control as sign_upload_control


def _iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


class DiagnosticClock:
    """A deterministic diagnostic timeline; never an actual network measurement."""

    def __init__(self):
        self.value = timestamp(utc_now()) + timedelta(seconds=1)

    def __call__(self):
        self.value += timedelta(milliseconds=1)
        return _iso(self.value)


class DiagnosticCollector:
    endpoint = "http://127.0.0.1:52101"

    def __init__(self, keys, clock, mode="normal"):
        self.keys, self.clock, self.mode = keys, clock, mode
        self.collect_calls = self.status_calls = 0
        self.intent = self.receipt = None

    def _signed(self, body):
        key = self.keys["collector"]
        return sign_control(body, key["secret"], key["key_id"])

    def collect(self, envelope):
        self.collect_calls += 1
        started = self.clock()
        key = self.keys["gateway"]
        body = validate_intent(verify_control(envelope, key["public"], key["key_id"], "collection_intent"))
        self.intent = deepcopy(envelope)
        receipt = {
            "kind": "collection_receipt", "collector_id": body["collector_id"],
            "collection_id": body["collection_id"], "request_id": body["request_id"],
            "request_sha256": digest(envelope), "recorded_at": self.clock(),
            "receipt_id": "diagnostic-stable-receipt", "storage": "sqlite-wal-full",
        }
        self.receipt = self._signed(receipt)
        response = deepcopy(self.receipt)
        if self.mode == "bad_receipt_signature":
            response["signature"] = "00" * 64
        elif self.mode == "wrong_intent_receipt":
            receipt["request_sha256"] = "00" * 32
            response = self._signed(receipt)
        elif self.mode == "wrong_collector_key":
            wrong = self.keys["receiver"]
            response = sign_control(receipt, wrong["secret"], self.keys["collector"]["key_id"])
        completed = self.clock()
        if self.mode == "future_receipt":
            receipt["recorded_at"] = _iso(timestamp(completed) + timedelta(microseconds=500))
            response = self._signed(receipt)
        return {
            "attempted": True, "attempted_at": started, "completed_at": completed,
            "status": None if self.mode == "lost_ack" else 200,
            "response": None if self.mode == "lost_ack" else response,
            "error": "diagnostic response loss" if self.mode == "lost_ack" else None,
        }

    def status(self, envelope):
        self.status_calls += 1
        started = self.clock()
        key = self.keys["gateway"]
        query = validate_query(verify_control(envelope, key["public"], key["key_id"], "collection_query"))
        body = {
            "kind": "collection_status", "collector_id": query["collector_id"],
            "collection_id": query["collection_id"], "request_id": query["request_id"],
            "request_sha256": query["request_sha256"], "query_sha256": digest(envelope),
            "nonce": query["nonce"], "status": "FOUND", "receipt": deepcopy(self.receipt),
            "checked_at": self.clock(),
        }
        if self.mode == "replayed_nonce":
            old_query = deepcopy(query)
            old_query["nonce"] = ("1" if query["nonce"][0] == "0" else "0") + query["nonce"][1:]
            old_envelope = sign_control(old_query, key["secret"], key["key_id"])
            body["nonce"], body["query_sha256"] = old_query["nonce"], digest(old_envelope)
        elif self.mode == "substituted_nested_receipt":
            nested = deepcopy(self.receipt["body"])
            nested["request_sha256"] = "00" * 32
            body["receipt"] = self._signed(nested)
        completed = self.clock()
        if self.mode == "future_status":
            body["checked_at"] = _iso(timestamp(completed) + timedelta(microseconds=500))
        response = self._signed(body)
        if self.mode == "bad_status_signature":
            response["signature"] = "00" * 64
        return {"attempted": True, "attempted_at": started, "completed_at": completed,
                "status": 200, "response": response, "error": None}


class DiagnosticTransport:
    endpoint = "http://127.0.0.1:52100/upload"

    def __init__(self, keys, clock):
        self.keys, self.clock = keys, clock
        self.calls = 0
        self.payloads = []

    def send(self, payload, intent):
        self.calls += 1
        self.payloads.append(bytes(payload))
        started = self.clock()
        body = intent["body"]
        receipt = {"kind": "upload_receipt", "request_id": body["request_id"],
                   "subject_sha256": body["subject_sha256"],
                   "payload_sha256": hashlib.sha256(payload).hexdigest(), "byte_length": len(payload),
                   "received_at": self.clock(), "receipt_id": "diagnostic-receiver-receipt"}
        key = self.keys["receiver"]
        return {"attempted": True, "body_send_completed": True, "attempted_at": started,
                "dispatched_at": self.clock(), "status": 200,
                "receipt": sign_upload_control(receipt, key["secret"], key["key_id"]), "error": None}


class CommittedLostAck(Journal):
    def claim(self, *args, **kwargs):
        super().claim(*args, **kwargs)
        raise OSError("diagnostic loss after actual SQLite commit")


class CommittedMalformedAck(Journal):
    def claim(self, *args, **kwargs):
        row = super().claim(*args, **kwargs)
        row["fingerprint"] = "00" * 32
        return row


class BoundaryReviewTests(unittest.TestCase):
    def fixture(self, *, mode="normal", journal_type=Journal, payload=SYNTHETIC_BYTES):
        directory = Path(self.enterContext(tempfile.TemporaryDirectory()))
        keys = make_keys()
        package, trust, config, _ = make_case(payload, DiagnosticTransport.endpoint, keys=keys)
        clock = DiagnosticClock()
        journal = journal_type(directory / "journal.sqlite3")
        collector = DiagnosticCollector(keys, clock, mode)
        transport = DiagnosticTransport(keys, clock)
        gate = CollectorGateway(config, journal, transport, collector, collector_id=COLLECTOR_ID,
                                collector_public=keys["collector"]["public"],
                                collector_key_id=keys["collector"]["key_id"], clock=clock)
        return {"directory": directory, "keys": keys, "package": package, "trust": trust,
                "config": config, "clock": clock, "journal": journal, "collector": collector,
                "transport": transport, "gate": gate, "payload": payload}

    def execute(self, fixture, **kwargs):
        return fixture["gate"].execute(fixture["package"], fixture["trust"], fixture["payload"], **kwargs)

    def assert_no_payload(self, fixture, report):
        self.assertIs(report["attempted"], False)
        self.assertEqual(fixture["transport"].calls, 0)
        self.assertIsNone(report["payload_receipt"])
        self.assertNotEqual(report["state"], "RECEIPT_CONFIRMED")

    @staticmethod
    def resign(fixture, index):
        record = fixture["package"]["records"][index]
        role = "policy" if record["body"]["kind"] == "transfer.policy" else "gateway"
        key = fixture["keys"][role]
        fixture["package"]["records"][index] = sign_record(record["body"], key["secret"], key["key_id"])

    def diagnostic_case(self, fixture, report):
        """A protocol-test object, never an exported actual-network capture."""
        collector = fixture["collector"]
        intent = collector.intent
        receipt = report["payload_receipt"]
        receiver_row = {name: receipt["body"][name] for name in
                        ("request_id", "subject_sha256", "payload_sha256", "byte_length")}
        receiver_row["receipt"] = deepcopy(receipt)
        record = {
            "format": "collector-pilot-case/0.1", "case_id": "CP-01", "recorded_at": fixture["clock"](),
            "collector_id": COLLECTOR_ID, "collector_endpoint": collector.endpoint,
            "keys": {role: {key: value for key, value in values.items() if key != "secret"}
                     for role, values in fixture["keys"].items()},
            "payload_sha256": report["payload_sha256"], "byte_length": report["byte_length"],
            "reports": [deepcopy(report)], "reconciliations": [],
            "collector_snapshot": {"collect_calls": collector.collect_calls, "status_calls": collector.status_calls,
                                   "accepted_count": 1, "rows": [{
                                       "collection_id": intent["body"]["collection_id"],
                                       "request_id": intent["body"]["request_id"], "request_sha256": digest(intent),
                                       "intent": deepcopy(intent), "receipt": deepcopy(collector.receipt)}]},
            "receiver_snapshot": {"handler_calls": 1, "accepted_count": 1, "rows": [receiver_row]},
            "cleanup": {name: {"child_stopped": True, "forced_termination": False}
                        for name in ("collector", "receiver")},
        }
        record["actual"] = derive_actual(record)
        return record

    def test_provisional_review_does_not_substitute_for_current_required_policy_and_permit(self):
        for change in ("collector_optional", "expired_permit", "wrong_tenant", "wrong_role", "changed_payload"):
            with self.subTest(change=change):
                f = self.fixture()
                package, trust = f["package"], f["trust"]
                if change == "collector_optional":
                    package["records"][0]["body"]["data"]["require_collector"] = False
                    new_hash = digest(package["records"][0]["body"]["data"])
                    package["target"]["subject"]["policy_sha256"] = new_hash
                    for index in range(2):
                        package["records"][index]["body"]["binding"]["policy_sha256"] = new_hash
                        self.resign(f, index)
                    trust["target_sha256"] = digest(package["target"])
                elif change == "expired_permit":
                    package["records"][1]["body"]["data"]["valid_until"] = package["as_of"]
                    self.resign(f, 1)
                elif change == "wrong_tenant":
                    package["records"][1]["body"]["binding"]["tenant_id"] = "a-different-tenant"
                    self.resign(f, 1)
                elif change == "wrong_role":
                    trust["keys"][f["keys"]["gateway"]["key_id"]]["roles"] = ["collector"]
                else:
                    f["payload"] = SYNTHETIC_BYTES + b"not permitted"
                report = self.execute(f)
                self.assert_no_payload(f, report)
                self.assertEqual(report["journal_state"], "NOT_CLAIMED")
                self.assertEqual((f["collector"].collect_calls, f["collector"].status_calls), (0, 0))

    def test_usable_collector_response_requires_exact_signature_binding_nonce_and_time(self):
        modes = ("lost_ack", "bad_receipt_signature", "wrong_intent_receipt", "wrong_collector_key",
                 "future_receipt", "replayed_nonce", "substituted_nested_receipt",
                 "bad_status_signature", "future_status")
        for mode in modes:
            with self.subTest(mode=mode):
                f = self.fixture(mode=mode)
                report = self.execute(f)
                self.assert_no_payload(f, report)
                self.assertEqual(report["state"], "BLOCKED_WITHOUT_ATTEMPT")
                self.assertEqual(f["collector"].collect_calls, 1)
                self.assertNotEqual(report["collector_outcome"], "FRESH_READBACK_CONFIRMED")
                if report["final"] is not None:
                    self.assertNotEqual(report["final"]["assessment"]["assessments"]["transfer_authorization"], "ALLOW")

    def test_health_is_point_in_time_and_is_not_rewritten_to_the_later_dispatch(self):
        f = self.fixture()
        report = self.execute(f)
        self.assertEqual(report["state"], "RECEIPT_CONFIRMED")
        final, post = report["final"], report["postflight"]
        self.assertEqual(final["assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        self.assertEqual(post["assessment"]["assessments"]["observed_action_authorization"], "REVIEW")
        health = [r for r in final["evidence"]["records"] if r["body"]["kind"] == "transfer.collector_health"]
        self.assertEqual(len(health), 1)
        self.assertEqual(health, [r for r in post["evidence"]["records"] if r["body"]["kind"] == "transfer.collector_health"])
        observed = health[0]["body"]["data"]["checked_at"]
        self.assertEqual(observed, final["evidence"]["target"]["operation_at"])
        self.assertLessEqual(timestamp(report["status_exchange"]["completed_at"]), timestamp(observed))
        self.assertLess(timestamp(observed), timestamp(report["payload_transport"]["dispatched_at"]))
        self.assertEqual(report["collection_receipt"], report["collection_status"]["body"]["receipt"])
        self.assertEqual(f["transport"].payloads, [SYNTHETIC_BYTES])

    def test_committed_claim_with_lost_or_malformed_ack_blocks_and_remains_consumed(self):
        for journal_type in (CommittedLostAck, CommittedMalformedAck):
            with self.subTest(journal=journal_type.__name__):
                f = self.fixture(journal_type=journal_type)
                report = self.execute(f)
                self.assert_no_payload(f, report)
                self.assertEqual((f["collector"].collect_calls, f["collector"].status_calls), (0, 0))
                request = f["package"]["target"]["subject"]["request_id"]
                reopened = Journal(f["directory"] / "journal.sqlite3")
                saved = reopened.get(request)
                self.assertIsNotNone(saved)
                self.assertEqual(saved["state"], "dispatch_intent")
                replacement = CollectorGateway(f["config"], reopened, f["transport"], f["collector"],
                                               collector_id=COLLECTOR_ID,
                                               collector_public=f["keys"]["collector"]["public"],
                                               collector_key_id=f["keys"]["collector"]["key_id"], clock=f["clock"])
                replay = replacement.execute(f["package"], f["trust"], f["payload"])
                self.assertEqual(replay["state"], "REPLAY_NO_SEND")
                self.assert_no_payload(f, replay)
                self.assertEqual((f["collector"].collect_calls, f["collector"].status_calls), (0, 0))
                self.assertEqual(reopened.get(request), saved)

    def test_lost_collector_ack_reconciles_without_reauthorizing_or_resending(self):
        f = self.fixture(mode="lost_ack")
        report = self.execute(f)
        self.assert_no_payload(f, report)
        request = f["package"]["target"]["subject"]["request_id"]
        before = deepcopy(f["journal"].get(request))
        first = f["gate"].reconcile(request)
        second = f["gate"].reconcile(request)
        for result in (first, second):
            self.assertEqual(result["state"], "FOUND")
            self.assertIs(result["attempted"], False)
            self.assertIs(result["upload_resumed"], False)
            self.assertEqual(result["collection_receipt"], f["collector"].receipt)
        self.assertNotEqual(first["status_query"]["body"]["nonce"], second["status_query"]["body"]["nonce"])
        self.assertEqual(f["journal"].get(request), before)
        replay = self.execute(f)
        self.assertEqual(replay["state"], "REPLAY_NO_SEND")
        self.assert_no_payload(f, replay)
        self.assertEqual((f["collector"].collect_calls, f["collector"].status_calls), (1, 2))

    def test_corrupt_saved_intent_is_rejected_before_reconciliation_rpc(self):
        for change in ("fingerprint", "collector_pin", "intent_binding"):
            with self.subTest(change=change):
                f = self.fixture(mode="lost_ack")
                self.execute(f)
                request = f["package"]["target"]["subject"]["request_id"]
                row = f["journal"].get(request)
                if change == "fingerprint":
                    row["fingerprint"] = "00" * 32
                elif change == "collector_pin":
                    row["snapshot"]["pins"]["collector_public"] = f["keys"]["receiver"]["public"]
                else:
                    row["snapshot"]["collection_intent"]["body"]["payload_sha256"] = "00" * 32
                    key = f["keys"]["gateway"]
                    row["snapshot"]["collection_intent"] = sign_control(
                        row["snapshot"]["collection_intent"]["body"], key["secret"], key["key_id"])
                with sqlite3.connect(f["directory"] / "journal.sqlite3") as connection:
                    connection.execute("UPDATE request_journal SET fingerprint=?,snapshot_json=? WHERE request_id=?",
                                       (row["fingerprint"], json.dumps(row["snapshot"]), request))
                connection.close()
                result = f["gate"].reconcile(request)
                self.assertEqual(result["state"], "JOURNAL_UNAVAILABLE")
                self.assertIs(result["upload_resumed"], False)
                self.assertEqual((f["collector"].status_calls, f["transport"].calls), (0, 0))

    def test_caller_mutation_cannot_change_captured_bytes_authority_or_collector_intent(self):
        payload = bytearray(SYNTHETIC_BYTES)
        f = self.fixture(payload=payload)
        original_subject = deepcopy(f["package"]["target"]["subject"])
        def mutate():
            payload[:] = b"different caller buffer"
            f["package"]["target"]["subject"]["tenant_id"] = "unapproved-tenant"
            f["package"]["records"].clear()
            f["trust"]["keys"].clear()
            f["config"].route["purpose"] = "changed-caller-purpose"
        report = self.execute(f, before_final_check=mutate)
        self.assertEqual(report["state"], "RECEIPT_CONFIRMED")
        self.assertEqual(f["transport"].payloads, [SYNTHETIC_BYTES])
        self.assertEqual(report["admission"]["evidence"]["target"]["subject"], original_subject)
        self.assertEqual(report["collection_intent"]["body"]["subject_sha256"], digest(original_subject))
        public = canonical(report)
        self.assertNotIn(SYNTHETIC_BYTES, public)
        for key in f["keys"].values():
            self.assertNotIn(key["secret"].encode("ascii"), public)

    def test_offline_recheck_rejects_signed_future_response_or_rewritten_permit(self):
        f = self.fixture()
        baseline = self.diagnostic_case(f, self.execute(f))
        check_case(baseline)
        for change in ("future_status", "different_final_permit", "case_cutoff"):
            with self.subTest(change=change):
                case = deepcopy(baseline)
                report = case["reports"][0]
                if change == "future_status":
                    envelope = deepcopy(report["collection_status"])
                    envelope["body"]["checked_at"] = report["payload_transport"]["attempted_at"]
                    key = f["keys"]["collector"]
                    signed = sign_control(envelope["body"], key["secret"], key["key_id"])
                    report["collection_status"] = signed
                    report["status_exchange"]["response"] = deepcopy(signed)
                elif change == "different_final_permit":
                    for name in ("final", "postflight"):
                        frame = report[name]
                        record = next(r for r in frame["evidence"]["records"] if r["body"]["kind"] == "transfer.decision")
                        record["body"]["data"]["valid_until"] = _iso(timestamp(record["body"]["data"]["valid_until"]) + timedelta(seconds=1))
                        key = f["keys"]["gateway"]
                        signed = sign_record(record["body"], key["secret"], key["key_id"])
                        frame["evidence"]["records"] = [signed if r["body"]["kind"] == "transfer.decision" else r
                                                          for r in frame["evidence"]["records"]]
                        frame["assessment"] = assess(frame["evidence"], frame["trust"], allow_synthetic=True)
                else:
                    case["recorded_at"] = report["final"]["evidence"]["target"]["operation_at"]
                case["actual"] = derive_actual(case)
                with self.assertRaises(InputError):
                    check_case(case)


if __name__ == "__main__":
    unittest.main()
