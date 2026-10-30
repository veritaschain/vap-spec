"""Independent control-boundary tests; transport doubles do not establish HTTP IO.

The required live HTTP suite separately measures actual loopback receiver behavior.
Fresh synthetic keys here exercise real signature verification without opening a
socket or importing the offline assessor's public deterministic fixture keys.
"""

import hashlib
import sqlite3
import tempfile
import unittest
from copy import deepcopy
from datetime import timedelta
from pathlib import Path

from upload_pilot.gateway import Gateway
from upload_pilot.harness import make_case, make_keys
from upload_pilot.journal import Journal
from upload_pilot.protocol import (
    InputError, canonical, decode_json, digest, public_key, sign_control,
    sign_record, timestamp, validate_endpoint, verify_control,
)


ENDPOINT = "http://127.0.0.1:50000/upload"


def iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


class ReceiptDouble:
    """A trusted transport unit-test double, explicitly not a network observer."""

    def __init__(self, config, receiver, clock, *, completed=True, mutation=None,
                 signer=None):
        self.endpoint = config.endpoint
        self.config, self.receiver, self.clock = config, receiver, clock
        self.completed, self.mutation, self.signer = completed, mutation, signer
        self.calls = []

    def send(self, payload, dispatch_envelope):
        self.calls.append((payload, deepcopy(dispatch_envelope)))
        started = self.clock()
        dispatch = verify_control(
            dispatch_envelope, public_key(self.config.gateway_secret),
            self.config.gateway_key_id, "dispatch_intent",
        )
        if not self.completed:
            return {"attempted": True, "body_send_completed": False,
                    "attempted_at": started, "dispatched_at": None,
                    "status": None, "receipt": None, "error": "unit_transport_failure"}
        body = {"kind": "upload_receipt", "request_id": dispatch["request_id"],
                "subject_sha256": dispatch["subject_sha256"],
                "payload_sha256": hashlib.sha256(payload).hexdigest(),
                "byte_length": len(payload), "received_at": self.clock(),
                "receipt_id": "unit-receipt"}
        if self.mutation:
            self.mutation(body)
        key = self.receiver if self.signer is None else self.signer
        receipt = sign_control(body, key["secret"], self.receiver["key_id"])
        return {"attempted": True, "body_send_completed": True,
                "attempted_at": started, "dispatched_at": self.clock(),
                "status": 200, "receipt": receipt, "error": None}


class BoundaryReviewTests(unittest.TestCase):
    def test_strict_messages_and_literal_endpoint(self):
        self.assertEqual(validate_endpoint(ENDPOINT), ENDPOINT)
        endpoints = (
            "http://127.0.0.1:65536/upload", "http://127.0.0.1:0/upload",
            "http://127.0.0.1:050000/upload", "http://localhost:50000/upload",
            "http://127.0.0.1:50000/upload?next=elsewhere",
            "http://127.0.0.1:50000/upload#fragment",
            "http://user@127.0.0.1:50000/upload", "http://[::1]:50000/upload",
            " http://127.0.0.1:50000/upload", "http://127.0.0.1:50000/up\tload",
            "http://127.0.0.1:50000/%75pload", "https://127.0.0.1:50000/upload",
        )
        for endpoint in endpoints:
            with self.subTest(endpoint=endpoint), self.assertRaises(InputError):
                validate_endpoint(endpoint)
        for raw in (b'{"x":1,"x":2}', b'{"outer":{"x":1,"x":2}}',
                    b'{"x":NaN}', b'{"x":Infinity}', b'"\xff"'):
            with self.subTest(raw=repr(raw)), self.assertRaises(InputError):
                decode_json(raw)
        with self.assertRaises(InputError):
            decode_json(b" " * (64 * 1024 + 1))

    def test_control_domain_identity_and_signed_body_are_bound(self):
        keys = make_keys()
        signer = keys["gateway"]
        body = {"kind": "dispatch_intent", "request_id": "unit-request"}
        valid = sign_control(body, signer["secret"], signer["key_id"])
        self.assertEqual(verify_control(valid, signer["public"], signer["key_id"],
                                        "dispatch_intent"), body)
        candidates = []
        changed = deepcopy(valid)
        changed["body"]["request_id"] = "other-request"
        candidates.append((changed, signer["public"], signer["key_id"], "dispatch_intent"))
        changed = deepcopy(valid)
        changed["trusted"] = True
        candidates.append((changed, signer["public"], signer["key_id"], "dispatch_intent"))
        candidates.extend((
            (valid, keys["receiver"]["public"], signer["key_id"], "dispatch_intent"),
            (valid, signer["public"], "other-key", "dispatch_intent"),
            (valid, signer["public"], signer["key_id"], "upload_receipt"),
            (sign_record(body, signer["secret"], signer["key_id"]), signer["public"],
             signer["key_id"], "dispatch_intent"),
        ))
        for index, candidate in enumerate(candidates):
            with self.subTest(index=index), self.assertRaises(InputError):
                verify_control(*candidate)

    def test_original_evaluator_pin_is_checked_before_reframing(self):
        changes = (
            lambda package, trust: package["target"]["subject"].update(purpose="other-purpose"),
            lambda package, trust: package["target"]["authorities"].update(gateway="other-issuer"),
            lambda package, trust: trust.update(target_sha256="0" * 64),
            lambda package, trust: trust.update(workflow="erasure"),
            lambda package, trust: trust.update(as_of=iso(timestamp(trust["as_of"]) + timedelta(seconds=1))),
        )
        for index, change in enumerate(changes):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                package, trust, config, receiver = make_case(b"synthetic", ENDPOINT)
                request_id = package["target"]["subject"]["request_id"]
                clock = lambda: package["as_of"]
                transport = ReceiptDouble(config, receiver, clock)
                journal = Journal(Path(directory) / "journal.sqlite3")
                gateway = Gateway(config, journal, transport, clock=clock)
                change(package, trust)
                try:
                    report = gateway.execute(package, trust, b"synthetic")
                except InputError:
                    pass
                else:
                    self.assertEqual(report["state"], "BLOCKED_WITHOUT_ATTEMPT")
                    self.assertFalse(report["attempted"])
                self.assertEqual(len(transport.calls), 0)
                self.assertIsNone(journal.get(request_id))

    def test_measured_payload_repin_does_not_refresh_permission(self):
        variants = (
            {"permit_payload": b"different approved bytes"},
            {"grant_changes": {"tenant_id": "another-tenant"}},
            {"grant_changes": {"endpoint": "http://127.0.0.1:50001/upload"}},
            {"decision": "deny"},
        )
        for index, options in enumerate(variants):
            with self.subTest(index=index), tempfile.TemporaryDirectory() as directory:
                payload = b"actual synthetic bytes\x00\xff\n"
                package, trust, config, receiver = make_case(payload, ENDPOINT, **options)
                original_records = deepcopy(package["records"])
                original_package, original_trust = deepcopy(package), deepcopy(trust)
                clock = lambda: package["as_of"]
                transport = ReceiptDouble(config, receiver, clock)
                journal = Journal(Path(directory) / "journal.sqlite3")
                report = Gateway(config, journal, transport, clock=clock).execute(package, trust, payload)
                self.assertEqual(report["state"], "BLOCKED_WITHOUT_ATTEMPT")
                self.assertFalse(report["attempted"])
                self.assertEqual(len(transport.calls), 0)
                self.assertEqual(report["payload_sha256"], hashlib.sha256(payload).hexdigest())
                self.assertEqual(report["evidence"]["records"], original_records)
                self.assertEqual(report["preflight_assessment"]["assessments"]["transfer_authorization"], "DENY")
                self.assertEqual(package, original_package)
                self.assertEqual(trust, original_trust)

    def test_real_gateway_clock_replaces_historical_operation_and_rechecks_expiry(self):
        for expire_before_admission in (True, False):
            with self.subTest(before_admission=expire_before_admission), tempfile.TemporaryDirectory() as directory:
                package, trust, config, receiver = make_case(b"synthetic", ENDPOINT)
                cutoff = package["records"][1]["body"]["data"]["valid_until"]
                expired_at = iso(timestamp(cutoff) + timedelta(seconds=1))
                now = [expired_at if expire_before_admission else package["as_of"]]
                clock = lambda: now[0]
                transport = ReceiptDouble(config, receiver, clock)
                journal = Journal(Path(directory) / "journal.sqlite3")
                gateway = Gateway(config, journal, transport, clock=clock)
                def advance():
                    now[0] = expired_at
                report = gateway.execute(package, trust, b"synthetic", before_send=advance)
                self.assertEqual(report["state"], "BLOCKED_WITHOUT_ATTEMPT")
                self.assertFalse(report["attempted"])
                self.assertEqual(len(transport.calls), 0)
                self.assertNotIn("transfer.dispatch", [r["body"]["kind"] for r in report["evidence"]["records"]])
                if expire_before_admission:
                    self.assertEqual(report["evidence"]["target"]["operation_at"], expired_at)
                    self.assertNotEqual(report["preflight_assessment"]["assessments"]["transfer_authorization"], "ALLOW")
                else:
                    self.assertEqual(report["preflight_assessment"]["assessments"]["transfer_authorization"], "ALLOW")
                    self.assertNotEqual(report["final_gate_assessment"]["assessments"]["transfer_authorization"], "ALLOW")

    def test_intent_and_failed_attempt_are_not_dispatch_observations(self):
        with tempfile.TemporaryDirectory() as directory:
            package, trust, config, receiver = make_case(b"synthetic", ENDPOINT)
            clock = lambda: package["as_of"]
            transport = ReceiptDouble(config, receiver, clock, completed=False)
            journal = Journal(Path(directory) / "journal.sqlite3")
            report = Gateway(config, journal, transport, clock=clock).execute(package, trust, b"synthetic")
            self.assertEqual(report["state"], "OUTCOME_UNKNOWN")
            self.assertTrue(report["attempted"])
            self.assertEqual(len(transport.calls), 1)
            self.assertNotIn("transfer.dispatch", [r["body"]["kind"] for r in report["evidence"]["records"]])
            self.assertEqual(report["postflight_assessment"]["assessments"]["transfer_observation"], "UNKNOWN")
            self.assertEqual(report["postflight_assessment"]["assessments"]["remote_outcome"], "UNKNOWN")

    def test_signed_receipt_needs_strict_fields_full_binding_and_chronology(self):
        def set_value(name, value):
            return lambda body: body.update({name: value})
        variants = (
            ("request", set_value("request_id", "different-request")),
            ("subject", set_value("subject_sha256", "0" * 64)),
            ("payload", set_value("payload_sha256", "0" * 64)),
            ("boolean-length", set_value("byte_length", True)),
            ("string-length", set_value("byte_length", "1")),
            ("missing-length", lambda body: body.pop("byte_length")),
            ("extra-success-flag", set_value("approved", True)),
            ("early-time", set_value("received_at", "2000-01-01T00:00:00Z")),
            ("future-time", set_value("received_at", "2100-01-01T00:00:00Z")),
            ("empty-receipt-id", set_value("receipt_id", "")),
            ("wrong-signer", None),
        )
        for name, mutation in variants:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as directory:
                package, trust, config, receiver = make_case(b"x", ENDPOINT)
                clock = lambda: package["as_of"]
                other_signer = make_keys()["receiver"] if name == "wrong-signer" else None
                transport = ReceiptDouble(config, receiver, clock, mutation=mutation, signer=other_signer)
                journal = Journal(Path(directory) / "journal.sqlite3")
                report = Gateway(config, journal, transport, clock=clock).execute(package, trust, b"x")
                self.assertEqual(report["state"], "OUTCOME_UNKNOWN")
                self.assertTrue(report["attempted"])
                self.assertEqual(len(transport.calls), 1)
                self.assertNotEqual(report["journal_state"], "receipt_confirmed")
                self.assertEqual(report["postflight_assessment"]["assessments"]["remote_outcome"], "UNKNOWN")

    def test_public_output_has_no_private_keys_or_payload_and_keeps_remote_unknown(self):
        with tempfile.TemporaryDirectory() as directory:
            keys = make_keys()
            payload = b"UNIQUE_SYNTHETIC_PLAINTEXT_NOT_FOR_THE_JOURNAL_9e78"
            package, trust, config, receiver = make_case(payload, ENDPOINT, keys=keys)
            clock = lambda: package["as_of"]
            transport = ReceiptDouble(config, receiver, clock)
            journal = Journal(Path(directory) / "journal.sqlite3")
            report = Gateway(config, journal, transport, clock=clock).execute(package, trust, payload)
            self.assertEqual(report["state"], "RECEIPT_CONFIRMED")
            self.assertEqual(report["postflight_assessment"]["assessments"]["remote_outcome"], "UNKNOWN")
            public_output = canonical(report)
            stored_output = canonical(journal.get(package["target"]["subject"]["request_id"]))
            for role, key in keys.items():
                with self.subTest(role=role):
                    self.assertFalse(key["secret"].encode() in public_output, "Private key escaped into public report")
                    self.assertFalse(key["secret"].encode() in stored_output, "Private key escaped into journal")
            self.assertFalse(config.gateway_secret in repr(config), "Config diagnostics expose a private key")
            self.assertFalse(payload in public_output, "Raw payload escaped into public report")
            self.assertFalse(payload in stored_output, "Raw payload escaped into journal")
            self.assertEqual(report["trust"]["target_sha256"], digest(report["evidence"]["target"]))

    def test_transplanted_or_corrupt_journal_details_never_reassert_a_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            keys = make_keys()
            path = Path(directory) / "journal.sqlite3"
            journal = Journal(path)
            completed = []
            for payload in (b"first synthetic request", b"second synthetic request"):
                package, trust, config, receiver = make_case(payload, ENDPOINT, keys=keys)
                at = package["as_of"]
                clock = lambda at=at: at
                transport = ReceiptDouble(config, receiver, clock)
                gateway = Gateway(config, journal, transport, clock=clock)
                report = gateway.execute(package, trust, payload)
                self.assertEqual(report["state"], "RECEIPT_CONFIRMED")
                completed.append((package, trust, payload, transport, gateway,
                                  journal.get(package["target"]["subject"]["request_id"])))
            package, trust, payload, transport, _, saved = completed[1]
            first_details = canonical(completed[0][5]["details"]).decode()
            original_snapshot = saved["snapshot"]
            damaged_snapshot = deepcopy(original_snapshot)
            damaged_snapshot["payload_sha256"] = "0" * 64
            variants = (
                ("other-request-receipt", original_snapshot, first_details, "REPLAY_NO_SEND"),
                ("inconsistent-binding", damaged_snapshot,
                 canonical(saved["details"]).decode(), "BLOCKED_WITHOUT_ATTEMPT"),
                ("malformed-details", original_snapshot, "{broken", "BLOCKED_WITHOUT_ATTEMPT"),
            )
            for name, snapshot, details, state in variants:
                with self.subTest(name=name):
                    with sqlite3.connect(path) as connection:
                        connection.execute(
                            "UPDATE request_journal SET snapshot_json=?,details_json=? WHERE request_id=?",
                            (canonical(snapshot).decode(), details, saved["request_id"]),
                        )
                    restarted = Gateway(config, Journal(path), transport, clock=lambda: package["as_of"])
                    replay = restarted.execute(package, trust, payload)
                    self.assertEqual(replay["state"], state)
                    self.assertFalse(replay["attempted"])
                    self.assertIsNone(replay["receipt"])
                    self.assertEqual(len(transport.calls), 1)

    def test_offline_recheck_rejects_missing_frames_and_receipt_contradictions(self):
        from incident_assessor.assess import assess
        from upload_pilot.suite import _check_export

        with tempfile.TemporaryDirectory() as directory:
            package, trust, config, receiver = make_case(b"x", ENDPOINT)
            clock = lambda: package["as_of"]
            transport = ReceiptDouble(config, receiver, clock)
            report = Gateway(config, Journal(Path(directory) / "journal.sqlite3"),
                             transport, clock=clock).execute(package, trust, b"x")
            self.assertEqual(report["state"], "RECEIPT_CONFIRMED")
            body = report["receipt"]["body"]
            row = {name: body[name] for name in ("request_id", "subject_sha256", "payload_sha256", "byte_length")}
            row["receipt"] = deepcopy(report["receipt"])
            case = {
                "format": "incident-upload-case/0.1", "case_id": "UL-01", "synthetic": True,
                "actual": {"states": ["RECEIPT_CONFIRMED"], "gateway_attempts": 1,
                           "handler_calls": 1, "accepted_count": 1, "received_bytes_match": True},
                "reports": [report],
                "receiver_snapshot": {"handler_calls": 1, "accepted_count": 1, "rows": [row]},
                "receiver_public": receiver["public"], "receiver_key_id": receiver["key_id"],
                "payload_sha256": report["payload_sha256"], "byte_length": 1,
                "cleanup": {"child_stopped": True, "forced_termination": False},
            }
            _check_export(case)
            mutations = []
            missing_reports = deepcopy(case)
            missing_reports["reports"] = []
            mutations.append(("missing-reports", missing_reports))
            for prefix in ("preflight", "postflight"):
                missing_frame = deepcopy(case)
                fields = (("preflight_evidence", "preflight_trust", "preflight_assessment")
                          if prefix == "preflight" else ("evidence", "trust", "postflight_assessment"))
                for field in fields:
                    missing_frame["reports"][0][field] = None
                mutations.append(("missing-" + prefix, missing_frame))
            inconsistent_attempts = deepcopy(case)
            inconsistent_attempts["reports"][0]["attempted"] = False
            mutations.append(("attempt-count", inconsistent_attempts))
            inconsistent_receiver = deepcopy(case)
            inconsistent_receiver["actual"]["handler_calls"] = 0
            mutations.append(("receiver-count", inconsistent_receiver))
            boolean_length = deepcopy(case)
            boolean_length["receiver_snapshot"]["rows"][0]["byte_length"] = True
            mutations.append(("boolean-row-length", boolean_length))
            unrelated_final = deepcopy(case)
            final = unrelated_final["reports"][0]
            final["final_gate_evidence"]["target"]["subject"]["purpose"] = "different-purpose"
            final["final_gate_trust"]["target_sha256"] = digest(final["final_gate_evidence"]["target"])
            final["final_gate_assessment"] = assess(
                final["final_gate_evidence"], final["final_gate_trust"], allow_synthetic=True)
            mutations.append(("unrelated-denied-final-frame", unrelated_final))
            for name, changes in (
                ("future-receipt", {"received_at": "2100-01-01T00:00:00Z"}),
                ("early-receipt", {"received_at": "2000-01-01T00:00:00Z"}),
                ("extra-receipt-field", {"approved": True}),
            ):
                invalid_receipt = deepcopy(case)
                changed = deepcopy(body)
                changed.update(changes)
                invalid_receipt["reports"][0]["receipt"] = sign_control(
                    changed, receiver["secret"], receiver["key_id"])
                mutations.append((name, invalid_receipt))
            for name, changed in mutations:
                with self.subTest(name=name), self.assertRaises(InputError):
                    _check_export(changed)


if __name__ == "__main__":
    unittest.main()
