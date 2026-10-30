"""Pure verifier checks using signed synthetic statements, not storage execution."""

from copy import deepcopy
import secrets
import unittest
from unittest.mock import patch

from erasure_pilot import adapter
from erasure_pilot.protocol import (EXCLUSIONS, LOCATION, MAX_OBJECT, InputError,
                                    canonical, digest, public_key, sha256_bytes,
                                    sign_message, sign_record)

REQUEST_AT = "2026-10-30T10:00:00Z"
BEFORE_START = "2026-10-30T10:00:01Z"
BEFORE_END = "2026-10-30T10:00:02Z"
ACK_AT = "2026-10-30T10:00:03Z"
UNLINK_AT = "2026-10-30T10:00:04Z"
COMPLETE_AT = "2026-10-30T10:00:05Z"
AFTER_START = "2026-10-30T10:00:06Z"
AFTER_END = "2026-10-30T10:00:07Z"
EXPIRES = "2026-10-30T10:00:10Z"
CUTOFF = "2026-10-30T12:00:00Z"


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.secrets = {role: secrets.token_hex(32) for role in ("requester", "provider", "observer")}
        self.pins = {
            "provider_id": "provider-local", "tenant_id": "tenant-synthetic", "location": LOCATION,
            "requester_key_id": "requester-key", "provider_key_id": "provider-key", "observer_key_id": "observer-key",
            "keys": {
                role + "-key": {
                    "public_key": public_key(self.secrets[role]), "issuer": role + "-local",
                    "organization": "single-local-controller", "roles": [core_role],
                    "not_before": "2026-10-30T00:00:00Z", "not_after": "2026-10-31T00:00:00Z",
                }
                for role, core_role in (("requester", "responder"), ("provider", "provider"), ("observer", "reviewer"))
            },
        }
        content = b"synthetic object bytes"
        manifest = {
            "provider_id": self.pins["provider_id"], "tenant_id": self.pins["tenant_id"],
            "object_id": "object-synthetic", "version_id": "version-one",
            "sha256": sha256_bytes(content), "byte_length": len(content), "location": LOCATION,
        }
        subject = {
            "request_id": "request-one", "provider_id": manifest["provider_id"], "tenant_id": manifest["tenant_id"],
            "object_ids": [manifest["object_id"]], "payload_sha256": digest(manifest), "stage": "erasure",
        }
        request = self.record("requester", "request-record", "erasure.request", REQUEST_AT, subject, {
            "requested_at": REQUEST_AT, "requested_locations": [LOCATION, *EXCLUSIONS],
        })
        authorization = self.message("requester", {
            "kind": "deletion_authorization", "request_sha256": digest(request), "manifest_sha256": digest(manifest),
            "authorized_at": REQUEST_AT, "valid_until": EXPIRES,
        })
        task = {"format": "incident-erasure-task/0.1", "manifest": manifest, "request": request, "authorization": authorization}
        ack = self.record("provider", "ack-record", "erasure.acknowledgement", ACK_AT, subject, {
            "request_record_id": "request-record", "acknowledged_at": ACK_AT, "queue_state": "received",
        })
        attestation = self.record("provider", "attestation-record", "erasure.provider_attestation", COMPLETE_AT, subject, {
            "request_record_id": "request-record", "completed_at": COMPLETE_AT,
            "locations": [LOCATION], "exclusions": list(EXCLUSIONS),
        })
        receipt = self.message("provider", {
            "kind": "local_unlink_receipt", "task_sha256": digest(task), "request_id": "request-one",
            "manifest_sha256": digest(manifest), "before": {key: manifest[key] for key in ("sha256", "byte_length")},
            "unlinked_at": UNLINK_AT, "observed_at": COMPLETE_AT, "after": "ABSENT",
        })
        observation = {
            "kind": "local_namespace_observation", "task_sha256": digest(task), "manifest_sha256": digest(manifest),
            **{key: manifest[key] for key in ("provider_id", "tenant_id", "location", "object_id", "version_id")},
        }
        before = self.message("observer", {
            **observation, "phase": "before", "previous_sha256": None, "completion_sha256": None,
            "window_start": BEFORE_START, "window_end": BEFORE_END,
            "measurement": {"state": "PRESENT", **{key: manifest[key] for key in ("sha256", "byte_length")}},
        })
        after = self.message("observer", {
            **observation, "phase": "after", "previous_sha256": digest(before), "completion_sha256": digest(attestation),
            "window_start": AFTER_START, "window_end": AFTER_END,
            "measurement": {"state": "ABSENT", "sha256": None, "byte_length": None},
        })
        result = {
            "state": "LOCAL_UNLINK_CONFIRMED", "attempted": True, "acknowledgement": ack,
            "attestation": attestation, "receipt": receipt, "journal_state": "LOCAL_UNLINK_CONFIRMED",
            "reason": "synthetic-signed-statements",
        }
        self.bundle = {
            "format": "incident-erasure-bundle/0.1", "task": task, "as_of": CUTOFF,
            "provider_result": result, "before": before, "after": after,
        }

    def message(self, role, body):
        return sign_message(body, self.secrets[role], role + "-key")

    def record(self, role, record_id, kind, recorded_at, subject, data):
        return sign_record({
            "record_id": record_id, "evaluation_id": "evaluation-one", "kind": kind,
            "issuer": role + "-local", "recorded_at": recorded_at, "binding": deepcopy(subject), "data": data,
        }, self.secrets[role], role + "-key")

    def verify(self, bundle=None, pins=None):
        value = self.bundle if bundle is None else bundle
        return adapter.verify_bundle(value, self.pins if pins is None else pins, digest(self.bundle["task"]))

    def resign_message(self, envelope, role):
        return self.message(role, envelope["body"])

    def resign_record(self, envelope, role):
        return sign_record(envelope["body"], self.secrets[role], role + "-key")

    def test_scoped_positive_retains_original_core_records_and_unknown_dimensions(self):
        original = deepcopy(self.bundle)
        with patch.object(adapter, "assess", wraps=adapter.assess) as inner:
            report = self.verify()
        self.assertEqual(report["local_observation"], "REMOVAL_OBSERVED_SAME_CONTROLLER")
        self.assertEqual(set(report), {"format", "task_sha256", "assessor_report", "local_observation", "unknown_domains", "limitations"})
        package = inner.call_args.args[0]
        expected_records = [self.bundle["task"]["request"], self.bundle["provider_result"]["acknowledgement"],
                            self.bundle["provider_result"]["attestation"]]
        self.assertEqual(canonical(package["records"]), canonical(expected_records))
        self.assertFalse(any(r["body"]["kind"] == "erasure.review" for r in package["records"]))
        dimensions = report["assessor_report"]["assessments"]
        self.assertEqual(dimensions["deletion_evidence"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE")
        self.assertEqual(dimensions["independent_verification"], "NOT_ESTABLISHED")
        for name in ("provider_completion", "target_completion", "excluded_scope_outcome", "outside_scope_outcome"):
            self.assertEqual(dimensions[name], "UNKNOWN")
        self.assertEqual(report["unknown_domains"], {name: "UNKNOWN" for name in EXCLUSIONS})
        self.assertEqual(self.bundle, original)

    def test_request_acknowledgement_and_absence_are_distinct(self):
        request_only = deepcopy(self.bundle)
        request_only.update(provider_result=None, before=None, after=None)
        report = self.verify(request_only)
        self.assertEqual(report["local_observation"], "NOT_OBSERVED")
        self.assertEqual(report["assessor_report"]["assessments"]["deletion_evidence"], "REQUEST_ONLY")
        ack_only = deepcopy(request_only)
        ack_only["provider_result"] = {
            "state": "ACKNOWLEDGED_ONLY", "attempted": False,
            "acknowledgement": self.bundle["provider_result"]["acknowledgement"],
            "attestation": None, "receipt": None, "journal_state": "ACKNOWLEDGED_ONLY", "reason": "received-only",
        }
        report = self.verify(ack_only)
        self.assertEqual(report["assessor_report"]["assessments"]["deletion_evidence"], "ACKNOWLEDGED")
        for omitted in ("before", "provider_result"):
            with self.subTest(missing=omitted):
                bundle = deepcopy(self.bundle)
                bundle[omitted] = None
                self.assertEqual(self.verify(bundle)["local_observation"], "ABSENCE_ONLY")
        before_only = deepcopy(self.bundle)
        before_only["after"] = None
        self.assertEqual(self.verify(before_only)["local_observation"], "NOT_ESTABLISHED")

    def test_present_after_and_nonmatching_before_never_promote_removal(self):
        for before_measurement in (
            {"state": "ABSENT", "sha256": None, "byte_length": None},
            {"state": "PRESENT", "sha256": "0" * 64, "byte_length": 1},
        ):
            with self.subTest(before=before_measurement):
                bundle = deepcopy(self.bundle)
                bundle["before"]["body"]["measurement"] = before_measurement
                bundle["before"] = self.resign_message(bundle["before"], "observer")
                bundle["after"]["body"]["previous_sha256"] = digest(bundle["before"])
                bundle["after"] = self.resign_message(bundle["after"], "observer")
                self.assertEqual(self.verify(bundle)["local_observation"], "ABSENCE_ONLY")
        bundle = deepcopy(self.bundle)
        bundle["after"]["body"]["measurement"] = deepcopy(bundle["before"]["body"]["measurement"])
        bundle["after"] = self.resign_message(bundle["after"], "observer")
        report = self.verify(bundle)
        self.assertEqual(report["local_observation"], "PRESENT_AT_OBSERVATION")
        self.assertEqual(report["assessor_report"]["assessments"]["deletion_evidence"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE")

    def test_unlinked_observations_are_not_a_complete_chain(self):
        for field in ("previous_sha256", "completion_sha256"):
            with self.subTest(field=field):
                bundle = deepcopy(self.bundle)
                bundle["after"]["body"][field] = None
                bundle["after"] = self.resign_message(bundle["after"], "observer")
                self.assertEqual(self.verify(bundle)["local_observation"], "ABSENCE_ONLY")
                bundle["after"]["body"][field] = "0" * 64
                bundle["after"] = self.resign_message(bundle["after"], "observer")
                with self.assertRaises(InputError):
                    self.verify(bundle)

    def test_historical_recheck_survives_expiry_but_late_unlink_does_not(self):
        self.verify()  # Cutoff is much later than authorization expiry.
        with self.assertRaises(InputError):
            adapter.validate_task(self.bundle["task"], self.pins, EXPIRES)
        bundle = deepcopy(self.bundle)
        bundle["provider_result"]["receipt"]["body"].update(unlinked_at=EXPIRES, observed_at="2026-10-30T10:00:11Z")
        bundle["provider_result"]["receipt"] = self.resign_message(bundle["provider_result"]["receipt"], "provider")
        attestation = bundle["provider_result"]["attestation"]
        attestation["body"]["recorded_at"] = "2026-10-30T10:00:11Z"
        attestation["body"]["data"]["completed_at"] = "2026-10-30T10:00:11Z"
        bundle["provider_result"]["attestation"] = self.resign_record(attestation, "provider")
        bundle.update(before=None, after=None)
        with self.assertRaises(InputError):
            self.verify(bundle)
        # Completion after expiry is valid when the actual unlink preceded it.
        bundle["provider_result"]["receipt"]["body"]["unlinked_at"] = UNLINK_AT
        bundle["provider_result"]["receipt"] = self.resign_message(bundle["provider_result"]["receipt"], "provider")
        self.verify(bundle)

    def test_scope_manifest_and_separately_pinned_task_cannot_be_substituted(self):
        for field, value in (("tenant_id", "tenant-other"), ("version_id", "version-other"),
                             ("sha256", "0" * 64), ("byte_length", True), ("byte_length", MAX_OBJECT + 1)):
            with self.subTest(field=field, value=value):
                task = deepcopy(self.bundle["task"])
                task["manifest"][field] = value
                with self.assertRaises(InputError):
                    adapter.validate_task(task, self.pins, REQUEST_AT)
        task = deepcopy(self.bundle["task"])
        task["request"]["body"]["data"]["requested_locations"].append("arbitrary-unpinned-location")
        task["request"] = self.resign_record(task["request"], "requester")
        task["authorization"]["body"]["request_sha256"] = digest(task["request"])
        task["authorization"] = self.resign_message(task["authorization"], "requester")
        with self.assertRaises(InputError):
            adapter.validate_task(task, self.pins, REQUEST_AT)
        with self.assertRaises(InputError):
            adapter.verify_bundle(self.bundle, self.pins, "0" * 64)

    def test_pins_enforce_roles_distinct_keys_and_one_honest_organization(self):
        for mutation in ("role", "organization", "duplicate-key", "extra-key", "expired", "issuer"):
            with self.subTest(mutation=mutation):
                pins = deepcopy(self.pins)
                if mutation == "role":
                    pins["keys"]["observer-key"]["roles"] = ["provider"]
                elif mutation == "organization":
                    pins["keys"]["observer-key"]["organization"] = "claimed-independent-party"
                elif mutation == "duplicate-key":
                    pins["keys"]["provider-key"]["public_key"] = pins["keys"]["requester-key"]["public_key"]
                elif mutation == "extra-key":
                    pins["keys"]["extra"] = deepcopy(pins["keys"]["provider-key"])
                elif mutation == "expired":
                    pins["keys"]["provider-key"]["not_after"] = ACK_AT
                else:
                    pins["keys"]["provider-key"]["issuer"] = "other-provider"
                with self.assertRaises(InputError):
                    self.verify(pins=pins)
        returned = adapter.validate_pins(self.pins)
        returned["keys"]["provider-key"]["roles"].append("reviewer")
        self.assertEqual(self.pins["keys"]["provider-key"]["roles"], ["provider"])

    def test_authenticated_but_mismatched_provider_records_are_rejected(self):
        for field in ("binding", "evaluation_id", "request_record_id", "scope", "record_id"):
            with self.subTest(field=field):
                bundle = deepcopy(self.bundle)
                record = bundle["provider_result"]["attestation"]
                if field == "binding":
                    record["body"]["binding"]["tenant_id"] = "tenant-other"
                elif field == "evaluation_id":
                    record["body"]["evaluation_id"] = "evaluation-other"
                elif field == "request_record_id":
                    record["body"]["data"][field] = "request-other"
                elif field == "scope":
                    record["body"]["data"]["exclusions"] = []
                else:
                    record["body"]["record_id"] = "request-record"
                bundle["provider_result"]["attestation"] = self.resign_record(record, "provider")
                bundle["after"]["body"]["completion_sha256"] = digest(bundle["provider_result"]["attestation"])
                bundle["after"] = self.resign_message(bundle["after"], "observer")
                with self.assertRaises(InputError):
                    self.verify(bundle)

    def test_validly_signed_receipt_and_observation_inconsistencies_are_rejected(self):
        receipt_changes = (
            ("request_id", "request-other"), ("task_sha256", "0" * 64),
            ("before", {"sha256": "0" * 64, "byte_length": 1}),
            ("unlinked_at", BEFORE_END), ("observed_at", UNLINK_AT), ("after", "PRESENT"),
        )
        for field, value in receipt_changes:
            with self.subTest(receipt=field):
                bundle = deepcopy(self.bundle)
                receipt = bundle["provider_result"]["receipt"]
                receipt["body"][field] = value
                bundle["provider_result"]["receipt"] = self.resign_message(receipt, "provider")
                with self.assertRaises(InputError):
                    self.verify(bundle)
        for field, value in (("object_id", "object-other"), ("window_start", UNLINK_AT),
                             ("window_end", "2026-10-30T13:00:00Z"), ("phase", "before"),
                             ("measurement", {"state": "ABSENT", "sha256": "0" * 64, "byte_length": None})):
            with self.subTest(observation=field):
                bundle = deepcopy(self.bundle)
                bundle["after"]["body"][field] = value
                bundle["after"] = self.resign_message(bundle["after"], "observer")
                with self.assertRaises(InputError):
                    self.verify(bundle)

    def test_result_matrix_cannot_promote_unconfirmed_or_replayed_actions(self):
        for mutation in ("attempted-string", "not-attempted", "wrong-journal", "unknown-with-completion", "missing-receipt"):
            with self.subTest(mutation=mutation):
                bundle = deepcopy(self.bundle)
                result = bundle["provider_result"]
                if mutation == "attempted-string":
                    result["attempted"] = "true"
                elif mutation == "not-attempted":
                    result["attempted"] = False
                elif mutation == "wrong-journal":
                    result["journal_state"] = "deletion_intent"
                elif mutation == "unknown-with-completion":
                    result["state"] = "OUTCOME_UNKNOWN"
                else:
                    result["receipt"] = None
                with self.assertRaises(InputError):
                    self.verify(bundle)
        for state in ("BLOCKED", "OUTCOME_UNKNOWN", "REPLAY_NO_ACTION", "REQUEST_ID_CONFLICT"):
            with self.subTest(state=state):
                bundle = deepcopy(self.bundle)
                bundle["provider_result"] = {
                    "state": state, "attempted": state == "OUTCOME_UNKNOWN", "acknowledgement": None,
                    "attestation": None, "receipt": None, "journal_state": "deletion_intent", "reason": "no-completion",
                }
                self.assertEqual(self.verify(bundle)["local_observation"], "ABSENCE_ONLY")

    def test_invalid_supplied_signatures_are_errors_not_missing_evidence(self):
        for where in ("before", "after", "acknowledgement", "attestation", "receipt"):
            with self.subTest(where=where):
                bundle = deepcopy(self.bundle)
                envelope = bundle[where] if where in {"before", "after"} else bundle["provider_result"][where]
                envelope["signature"] = "0" * 128
                with self.assertRaises(InputError):
                    self.verify(bundle)

    def test_jcs_normalization_cannot_turn_float_lengths_into_integer_inputs(self):
        task = deepcopy(self.bundle["task"])
        task["manifest"]["byte_length"] = float(task["manifest"]["byte_length"])
        # The digest/signatures would be unchanged by JCS normalization, but the
        # supplied JSON value still violates the required actual integer type.
        self.assertEqual(digest(task), digest(self.bundle["task"]))
        with self.assertRaises(InputError):
            adapter.validate_task(task, self.pins, REQUEST_AT)
        bundle = deepcopy(self.bundle)
        bundle["task"] = task
        with self.assertRaises(InputError):
            self.verify(bundle)
        bundle = deepcopy(self.bundle)
        before = bundle["provider_result"]["receipt"]["body"]["before"]
        before["byte_length"] = float(before["byte_length"])
        with self.assertRaises(InputError):
            self.verify(bundle)

    def test_zero_duration_reads_and_pure_verification(self):
        bundle = deepcopy(self.bundle)
        bundle["after"]["body"]["window_end"] = bundle["after"]["body"]["window_start"]
        bundle["after"] = self.resign_message(bundle["after"], "observer")
        with patch("builtins.open", side_effect=AssertionError("Verifier must not read files")), \
                patch("os.open", side_effect=AssertionError("Verifier must not open descriptors")), \
                patch("os.unlink", side_effect=AssertionError("Verifier must not delete")):
            self.assertEqual(self.verify(bundle)["local_observation"], "REMOVAL_OBSERVED_SAME_CONTROLLER")


if __name__ == "__main__":
    unittest.main()
