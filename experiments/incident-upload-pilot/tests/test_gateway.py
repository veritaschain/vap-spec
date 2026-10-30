"""Deterministic gateway/journal tests: transport is fake and sockets are blocked."""

import hashlib
import socket
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

from upload_pilot.gateway import Gateway
from upload_pilot.harness import SYNTHETIC_BYTES, make_case, make_keys
from upload_pilot.journal import Journal
from upload_pilot.protocol import canonical, digest, sign_control, sign_record, timestamp, utc_now


ENDPOINT = "http://127.0.0.1:31337/upload"


class FakeTransport:
    def __init__(self, endpoint, receiver, *, probe=None, complete=True, clock=utc_now):
        self._endpoint, self.receiver = endpoint, receiver
        self.probe, self.complete, self.clock = probe, complete, clock
        self.payloads, self.envelopes, self._lock = [], [], threading.Lock()

    @property
    def endpoint(self):
        return self._endpoint

    def send(self, payload, dispatch_envelope):
        self.assert_bytes(payload)
        with self._lock:
            self.payloads.append(payload)
            self.envelopes.append(deepcopy(dispatch_envelope))
        attempted = self.clock()
        if self.probe is not None:
            self.probe(payload, dispatch_envelope)
        if not self.complete:
            return {"attempted": True, "body_send_completed": False, "attempted_at": attempted,
                    "dispatched_at": None, "status": None, "receipt": None, "error": "synthetic-partial-send"}
        received = self.clock()
        intent = dispatch_envelope["body"]
        receipt = sign_control({
            "kind": "upload_receipt", "request_id": intent["request_id"],
            "subject_sha256": intent["subject_sha256"],
            "payload_sha256": hashlib.sha256(payload).hexdigest(), "byte_length": len(payload),
            "received_at": received, "receipt_id": "synthetic-fake-receipt",
        }, self.receiver["secret"], self.receiver["key_id"])
        return {"attempted": True, "body_send_completed": True, "attempted_at": attempted,
                "dispatched_at": self.clock(), "status": 200, "receipt": receipt, "error": None}

    @staticmethod
    def assert_bytes(payload):
        if type(payload) is not bytes:
            raise AssertionError("Transport received mutable or transformed input")


class FailingCommitJournal(Journal):
    def _commit(self, connection):
        raise OSError("synthetic failure before SQLite commit")


class CommitThenFailJournal(Journal):
    def _commit(self, connection):
        super()._commit(connection)
        raise OSError("synthetic failure after SQLite commit")


class FailingFinishJournal(Journal):
    def finish(self, request_id, state, details):
        raise OSError("synthetic failure before result persistence")


class FinishThenFailJournal(Journal):
    def finish(self, request_id, state, details):
        super().finish(request_id, state, details)
        raise OSError("synthetic failure after result persistence")


class GatewayTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="upload-pilot-gateway-test-")
        self.addCleanup(self.directory.cleanup)
        self.path = Path(self.directory.name) / "journal.sqlite"
        self.socket_guard = patch.object(socket, "socket", side_effect=AssertionError("Unit tests must not open sockets"))
        self.socket_guard.start()
        self.addCleanup(self.socket_guard.stop)

    def setup_case(self, *, payload=SYNTHETIC_BYTES, journal_class=Journal, **kwargs):
        package, trust, config, receiver = make_case(payload, ENDPOINT, **kwargs)
        journal = journal_class(self.path)
        transport = FakeTransport(ENDPOINT, receiver)
        return package, trust, config, receiver, journal, transport

    def test_full_committed_intent_exists_at_transport_boundary(self):
        package, trust, config, receiver, journal, transport = self.setup_case()
        original_records = canonical(package["records"])

        def probe(payload, envelope):
            row = journal.get(package["target"]["subject"]["request_id"])
            self.assertEqual(row["state"], "dispatch_intent")
            self.assertIsNone(row["details"])
            snapshot = row["snapshot"]
            self.assertEqual(snapshot["payload_sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(snapshot["byte_length"], len(payload))
            self.assertEqual(snapshot["dispatch_intent"], envelope)
            self.assertNotIn("transfer.dispatch", [r["body"]["kind"] for r in snapshot["evidence"]["records"]])
            policy = snapshot["evidence"]["records"][0]["body"]["data"]
            self.assertIs(policy["require_collector"], False)
            self.assertEqual(snapshot["preflight_assessment"]["assessments"]["transfer_authorization"], "ALLOW")
            with journal._connect() as connection:
                self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0], "wal")
                self.assertEqual(connection.execute("PRAGMA synchronous").fetchone()[0], 2)

        transport.probe = probe
        result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["state"], "RECEIPT_CONFIRMED")
        self.assertEqual(result["postflight_assessment"]["assessments"]["remote_outcome"], "UNKNOWN")
        self.assertEqual(transport.payloads, [SYNTHETIC_BYTES])
        self.assertEqual(canonical(package["records"]), original_records)
        dispatches = [r for r in result["evidence"]["records"] if r["body"]["kind"] == "transfer.dispatch"]
        self.assertEqual(len(dispatches), 1)
        self.assertEqual(dispatches[0]["body"]["data"]["dispatched_at"], result["transport_observation"]["dispatched_at"])
        self.assertEqual(result["evidence"]["target"]["operation_at"], result["preflight_evidence"]["target"]["operation_at"])
        public = canonical(result).decode()
        self.assertNotIn(config.gateway_secret, public)
        self.assertNotIn(receiver["secret"], public)

    def test_snapshot_remains_immutable_after_caller_mutates_bytearray(self):
        original = bytearray(SYNTHETIC_BYTES)
        package, trust, config, _, journal, transport = self.setup_case(payload=original)

        def mutate():
            original[:] = b"changed after capture"
            config.route["tenant_id"] = "caller-mutated-tenant"

        gateway = Gateway(config, journal, transport)
        result = gateway.execute(package, trust, original, after_snapshot=mutate)
        self.assertEqual(result["state"], "RECEIPT_CONFIRMED")
        self.assertEqual(transport.payloads, [SYNTHETIC_BYTES])
        self.assertEqual(result["payload_sha256"], hashlib.sha256(SYNTHETIC_BYTES).hexdigest())
        self.assertEqual(result["evidence"]["target"]["subject"]["tenant_id"], "tenant-enterprise-a")

    def test_changed_payload_does_not_refresh_old_signed_permit(self):
        package, trust, config, _, journal, transport = self.setup_case()
        original_records = canonical(package["records"])
        result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES + b"changed")
        self.assertEqual(result["state"], "BLOCKED_WITHOUT_ATTEMPT")
        self.assertEqual(result["preflight_assessment"]["assessments"]["binding_assessment"], "PAYLOAD_MISMATCH")
        self.assertEqual(transport.payloads, [])
        self.assertEqual(canonical(result["preflight_evidence"]["records"]), original_records)
        self.assertIsNone(journal.get(package["target"]["subject"]["request_id"]))

    def test_commit_failure_never_reaches_transport_even_when_commit_may_have_completed(self):
        for index, journal_class in enumerate((FailingCommitJournal, CommitThenFailJournal)):
            with self.subTest(journal_class=journal_class.__name__):
                self.path = Path(self.directory.name) / ("commit-" + str(index) + ".sqlite")
                package, trust, config, _, journal, transport = self.setup_case(journal_class=journal_class)
                result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES)
                self.assertEqual(result["state"], "BLOCKED_WITHOUT_ATTEMPT")
                self.assertFalse(result["attempted"])
                self.assertEqual(transport.payloads, [])
                if journal_class is CommitThenFailJournal:
                    replay = Gateway(config, Journal(self.path), transport).execute(package, trust, SYNTHETIC_BYTES)
                    self.assertEqual(replay["state"], "REPLAY_NO_SEND")
                    self.assertIsNone(replay["receipt"])

    def test_result_persistence_failure_is_unknown_and_restart_never_resends(self):
        for index, journal_class in enumerate((FailingFinishJournal, FinishThenFailJournal)):
            with self.subTest(journal_class=journal_class.__name__):
                self.path = Path(self.directory.name) / ("finish-" + str(index) + ".sqlite")
                package, trust, config, _, journal, transport = self.setup_case(journal_class=journal_class)
                result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES)
                self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
                self.assertTrue(result["attempted"])
                self.assertIsNone(result["receipt"])
                replay = Gateway(config, Journal(self.path), transport).execute(package, trust, SYNTHETIC_BYTES)
                self.assertEqual(replay["state"], "REPLAY_NO_SEND")
                self.assertFalse(replay["attempted"])
                self.assertIsNone(replay["receipt"])
                self.assertEqual(len(transport.payloads), 1)

    def test_malformed_post_commit_claim_acknowledgements_never_allow_send(self):
        mutations = {
            "absent": lambda row: None,
            "empty": lambda row: {},
            "other_request": lambda row: {**row, "request_id": "other-request"},
            "other_fingerprint": lambda row: {**row, "fingerprint": "0" * 64},
            "terminal_state": lambda row: {**row, "state": "receipt_confirmed"},
            "other_snapshot": lambda row: {**row, "snapshot": {"unrelated": True}},
            "unexpected_details": lambda row: {**row, "details": {"unrelated": True}},
        }
        for label, mutation in mutations.items():
            with self.subTest(acknowledgement=label):
                self.path = Path(self.directory.name) / (label + ".sqlite")

                class MalformedAcknowledgementJournal(Journal):
                    def claim(self, request_id, fingerprint, snapshot):
                        return mutation(super().claim(request_id, fingerprint, snapshot))

                package, trust, config, _, journal, transport = self.setup_case(journal_class=MalformedAcknowledgementJournal)
                result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES)
                self.assertEqual(result["state"], "BLOCKED_WITHOUT_ATTEMPT")
                self.assertEqual(result["reason"], "JOURNAL_CLAIM_ACKNOWLEDGEMENT_NOT_ESTABLISHED")
                self.assertEqual(transport.payloads, [])
                replay = Gateway(config, Journal(self.path), transport).execute(package, trust, SYNTHETIC_BYTES)
                self.assertEqual(replay["state"], "REPLAY_NO_SEND")
                self.assertEqual(transport.payloads, [])

    def test_malformed_result_acknowledgement_cannot_promote_receipt(self):
        class MalformedResultAcknowledgementJournal(Journal):
            def finish(self, request_id, state, details):
                super().finish(request_id, state, details)
                return {"state": state}

        package, trust, config, _, journal, transport = self.setup_case(journal_class=MalformedResultAcknowledgementJournal)
        result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertEqual(result["reason"], "JOURNAL_RESULT_PERSISTENCE_FAILED")
        self.assertIsNone(result["receipt"])
        replay = Gateway(config, Journal(self.path), transport).execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(replay["state"], "REPLAY_NO_SEND")
        self.assertIsNone(replay["receipt"])
        self.assertEqual(len(transport.payloads), 1)

    def test_expiration_after_commit_is_blocked_by_final_assessment(self):
        package, trust, config, _, journal, transport = self.setup_case(expires_in=3)
        current = [package["as_of"]]
        permit_until = package["records"][1]["body"]["data"]["valid_until"]

        def advance():
            current[0] = (timestamp(permit_until) + timedelta(seconds=1)).isoformat().replace("+00:00", "Z")

        result = Gateway(config, journal, transport, clock=lambda: current[0]).execute(
            package, trust, SYNTHETIC_BYTES, before_send=advance)
        self.assertEqual(result["preflight_assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        self.assertNotEqual(result["final_gate_assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        self.assertEqual(result["state"], "BLOCKED_WITHOUT_ATTEMPT")
        self.assertEqual(result["journal_state"], "blocked_after_intent")
        self.assertEqual(transport.payloads, [])
        self.assertNotIn("transfer.dispatch", [r["body"]["kind"] for r in result["evidence"]["records"]])

    def test_concurrent_calls_have_one_transport_attempt(self):
        package, trust, config, _, journal, transport = self.setup_case()
        entered, release = threading.Event(), threading.Event()

        def hold(payload, intent):
            entered.set()
            if not release.wait(5):
                raise AssertionError("Controlled transport release timed out")

        transport.probe = hold
        gateway = Gateway(config, journal, transport)
        with ThreadPoolExecutor(max_workers=6) as executor:
            first = executor.submit(gateway.execute, package, trust, SYNTHETIC_BYTES)
            self.assertTrue(entered.wait(5))
            repeated = [executor.submit(gateway.execute, package, trust, SYNTHETIC_BYTES) for _ in range(5)]
            try:
                replays = [future.result(timeout=5) for future in repeated]
            finally:
                release.set()
            initial = first.result(timeout=5)
        self.assertEqual(initial["state"], "RECEIPT_CONFIRMED")
        self.assertTrue(all(r["state"] == "REPLAY_NO_SEND" and not r["attempted"] for r in replays))
        self.assertEqual(len(transport.payloads), 1)

    def test_interrupted_after_claim_survives_restart_without_send(self):
        package, trust, config, _, journal, transport = self.setup_case()

        def interrupted():
            raise KeyboardInterrupt("trusted test interruption")

        with self.assertRaises(KeyboardInterrupt):
            Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES, before_send=interrupted)
        row = journal.get(package["target"]["subject"]["request_id"])
        self.assertEqual(row["state"], "dispatch_intent")
        replay = Gateway(config, Journal(self.path), transport).execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(replay["state"], "REPLAY_NO_SEND")
        self.assertEqual(transport.payloads, [])

    def test_same_request_id_different_validly_authorized_action_conflicts(self):
        keys = make_keys()
        package, trust, config, receiver, journal, transport = self.setup_case(keys=keys)
        gateway = Gateway(config, journal, transport)
        self.assertEqual(gateway.execute(package, trust, SYNTHETIC_BYTES)["state"], "RECEIPT_CONFIRMED")
        other_payload = b"another synthetic payload"
        other, other_trust, other_config, _ = make_case(other_payload, ENDPOINT, keys=keys)
        request_id = package["target"]["subject"]["request_id"]
        other["target"]["subject"]["request_id"] = request_id
        for index, envelope in enumerate(other["records"]):
            body = deepcopy(envelope["body"])
            body["binding"]["request_id"] = request_id
            role = "policy" if body["kind"] == "transfer.policy" else "gateway"
            other["records"][index] = sign_record(body, keys[role]["secret"], keys[role]["key_id"])
        other_trust["target_sha256"] = digest(other["target"])
        result = Gateway(other_config, journal, transport).execute(other, other_trust, other_payload)
        self.assertEqual(result["preflight_assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        self.assertEqual(result["state"], "REQUEST_ID_CONFLICT")
        self.assertFalse(result["attempted"])
        self.assertEqual(len(transport.payloads), 1)

    def test_partial_send_and_transport_exception_do_not_manufacture_dispatch(self):
        package, trust, config, _, journal, transport = self.setup_case()
        transport.complete = False
        result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertTrue(result["attempted"])
        self.assertNotIn("transfer.dispatch", [r["body"]["kind"] for r in result["evidence"]["records"]])
        self.path = Path(self.directory.name) / "exception.sqlite"
        package, trust, config, _, journal, transport = self.setup_case()

        def explode(payload, intent):
            raise OSError("trusted test exception containing " + config.gateway_secret)

        transport.probe = explode
        result = Gateway(config, journal, transport).execute(package, trust, SYNTHETIC_BYTES)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertEqual(result["reason"], "TRANSPORT_EXCEPTION")
        self.assertNotIn(config.gateway_secret, canonical(result).decode())
        self.assertNotIn("transfer.dispatch", [r["body"]["kind"] for r in result["evidence"]["records"]])


if __name__ == "__main__":
    unittest.main()
