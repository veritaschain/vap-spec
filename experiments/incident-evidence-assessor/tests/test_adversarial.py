"""Independent negative tests for the experimental offline assessor.

These tests mutate authenticated synthetic inputs. They do not read the prose
catalogue or infer expected decisions from case identifiers at runtime.
"""

from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_ROOT))

from incident_assessor.assess import assess
from incident_assessor.evidence import digest
from fixture_publication_response import build as build_publication
from fixture_support import add, finish, sign
from fixture_transfer_erasure import approved_transfer, build as build_transfer
from incident_assessor.model import InputError, strict_json


def _boolean_paths(value, prefix=()):
    if type(value) is bool:
        yield prefix
    elif isinstance(value, dict):
        for key, item in value.items():
            yield from _boolean_paths(item, prefix + (key,))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _boolean_paths(item, prefix + (index,))


def _replace_path(value, path, replacement):
    for key in path[:-1]:
        value = value[key]
    value[path[-1]] = replacement


class AdversarialTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixtures = {**build_transfer(), **build_publication()}

    def pair(self, case_id):
        return copy.deepcopy(self.fixtures[case_id])

    def run_assessor(self, package, trust):
        return assess(package, trust, allow_synthetic=True)

    @staticmethod
    def role_record(package, trust, role):
        return next(
            record
            for record in package["records"]
            if role in trust["keys"][record["key_id"]]["roles"]
        )

    @staticmethod
    def resign(package, trust, record):
        role = trust["keys"][record["key_id"]]["roles"][0]
        replacement = sign(copy.deepcopy(record["body"]), role)
        package["records"][package["records"].index(record)] = replacement
        return replacement

    @staticmethod
    def check_for(report, record):
        return next(
            check
            for check in report["evidence_checks"]
            if check["record_id"] == record["body"]["record_id"]
        )

    def assert_no_provider_attestation(self, report):
        self.assertNotEqual(
            report["assessments"].get("deletion_evidence"),
            "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE",
        )

    def test_strict_json_rejects_ambiguous_keys_and_numbers(self):
        samples = (
            '{"value":1,"value":2}',
            '{"outer":{"value":1,"value":2}}',
            '{"value":NaN}',
            '{"value":Infinity}',
            '{"value":-Infinity}',
            '{"value":9007199254740992}',
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for raw in samples:
                with self.subTest(raw=raw):
                    path.write_text(raw, encoding="utf-8")
                    with self.assertRaises(InputError):
                        strict_json(path)

    def test_types_booleans_and_unknown_fields_are_not_coerced(self):
        for malformed in (False, 1, None, "2026-10-30T12:00:00"):
            with self.subTest(as_of=malformed):
                package, trust = self.pair("UP-01")
                package["as_of"] = malformed
                with self.assertRaises(InputError):
                    self.run_assessor(package, trust)

        checked = 0
        for case_id in ("UP-01", "UP-08", "PB-01"):
            source, _ = self.pair(case_id)
            paths = list(_boolean_paths(source))
            for path in paths[:2]:
                for malformed in ("false", 0, 1, None):
                    with self.subTest(case=case_id, path=path, value=malformed):
                        package, trust = self.pair(case_id)
                        _replace_path(package, path, malformed)
                        with self.assertRaises(InputError):
                            self.run_assessor(package, trust)
                        checked += 1
        self.assertGreater(checked, 0, "Fixtures must exercise typed booleans")

        package, trust = self.pair("ER-03")
        package["records"][0]["body"]["trusted"] = True
        with self.assertRaises(InputError):
            self.run_assessor(package, trust)

        package, trust = self.pair("ER-03")
        package["target"]["subject"] = {"request_id": "request-only"}
        for record in list(package["records"]):
            record["body"]["binding"] = {"request_id": "request-only"}
            self.resign(package, trust, record)
        finish(package, trust)
        with self.assertRaises(InputError):
            self.run_assessor(package, trust)

    def test_duplicate_ids_and_binding_set_members_are_rejected(self):
        package, trust = self.pair("UP-05")
        package["records"].append(copy.deepcopy(package["records"][0]))
        with self.assertRaises(InputError):
            self.run_assessor(package, trust)

        package, trust = self.pair("ER-03")
        record = self.role_record(package, trust, "provider")
        objects = record["body"]["binding"]["object_ids"]
        objects.append(objects[0])
        self.resign(package, trust, record)
        with self.assertRaises(InputError):
            self.run_assessor(package, trust)

    def test_synthetic_trust_requires_explicit_opt_in(self):
        package, trust = self.pair("ER-03")
        with self.assertRaises(InputError):
            assess(package, trust)
        report = self.run_assessor(package, trust)
        self.assertEqual(
            report["assessments"]["deletion_evidence"],
            "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE",
        )

    def test_tampered_signed_binding_is_not_authenticated(self):
        package, trust = self.pair("ER-03")
        record = self.role_record(package, trust, "provider")
        record["body"]["binding"]["tenant_id"] = "substituted-tenant"
        report = self.run_assessor(package, trust)
        self.assertEqual(self.check_for(report, record)["signature"], "FAILED")
        self.assert_no_provider_attestation(report)

    def test_signature_identity_role_and_key_are_separate(self):
        for mutation in ("unknown-key", "wrong-public-key", "wrong-issuer", "wrong-role"):
            with self.subTest(mutation=mutation):
                package, trust = self.pair("ER-03")
                record = self.role_record(package, trust, "provider")
                key = trust["keys"][record["key_id"]]
                if mutation == "unknown-key":
                    record["key_id"] = "unregistered-key"
                elif mutation == "wrong-public-key":
                    other_id = next(
                        key_id for key_id, candidate in trust["keys"].items()
                        if "author" in candidate["roles"]
                    )
                    other = trust["keys"].pop(other_id)
                    key["public_key"] = other["public_key"]
                elif mutation == "wrong-issuer":
                    record["body"]["issuer"] = "unexpected-provider"
                    record = self.resign(package, trust, record)
                else:
                    key["roles"] = ["author"]
                report = self.run_assessor(package, trust)
                check = self.check_for(report, record)
                self.assertEqual(check["eligibility"], "INELIGIBLE")
                if mutation == "wrong-issuer":
                    self.assertEqual(check["signature"], "VERIFIED")
                    self.assertEqual(check["identity"], "MISMATCH")
                elif mutation == "wrong-role":
                    self.assertEqual(check["signature"], "VERIFIED")
                    self.assertEqual(check["role"], "UNAUTHORIZED")
                self.assert_no_provider_attestation(report)

    def test_evaluator_context_pin_prevents_target_time_or_workflow_substitution(self):
        for part in ("subject", "authorities", "as_of", "workflow"):
            with self.subTest(part=part):
                package, trust = self.pair("ER-03")
                if part == "subject":
                    package["target"]["subject"]["tenant_id"] = "substituted-tenant"
                elif part == "authorities":
                    package["target"]["authorities"]["provider"] = "unexpected-provider"
                elif part == "as_of":
                    package["as_of"] = "2026-10-31T12:00:00Z"
                else:
                    package["workflow"] = "cross_party"
                with self.assertRaises(InputError):
                    self.run_assessor(package, trust)

    def test_future_and_expired_key_records_cannot_support_claim(self):
        for mutation in ("future-record", "expired-key"):
            with self.subTest(mutation=mutation):
                package, trust = self.pair("ER-03")
                record = self.role_record(package, trust, "provider")
                if mutation == "future-record":
                    record["body"]["recorded_at"] = "2026-10-30T12:00:01Z"
                    record = self.resign(package, trust, record)
                    expected_time = "FUTURE_RECORD"
                else:
                    trust["keys"][record["key_id"]]["not_after"] = "2026-10-30T10:00:00Z"
                    expected_time = "OUTSIDE_KEY_VALIDITY"
                report = self.run_assessor(package, trust)
                check = self.check_for(report, record)
                self.assertEqual(check["signature"], "VERIFIED")
                self.assertEqual(check["time"], expected_time)
                self.assert_no_provider_attestation(report)

        package, trust = approved_transfer()
        decision = next(
            record for record in package["records"]
            if record["body"]["kind"] == "transfer.decision"
        )
        decision["body"]["data"]["valid_until"] = "2026-10-30T11:15:00Z"
        self.resign(package, trust, decision)
        add(
            package, "transfer.collector_health",
            {"checked_at": "2026-10-30T11:30:00Z", "available": True, "durable_acknowledged": True},
            role="gateway", recorded_at="2026-10-30T11:30:00Z",
        )
        add(
            package, "transfer.dispatch", {"dispatched_at": "2026-10-30T11:30:00Z"},
            role="gateway", recorded_at="2026-10-30T11:30:00Z",
        )
        expired_at_dispatch = self.run_assessor(package, trust)["assessments"]
        self.assertEqual(expired_at_dispatch["proposed_transfer_authorization"], "ALLOW")
        self.assertEqual(expired_at_dispatch["observed_action_authorization"], "REVIEW")
        self.assertEqual(expired_at_dispatch["transfer_authorization"], "REVIEW")

        package, trust = self.pair("PB-07")
        receipt = add(
            package,
            "publication_receipt",
            {"received_at": "2026-10-30T10:00:00Z", "status": "accepted"},
            role="recipient",
            recorded_at="2026-10-30T10:00:00Z",
        )
        before_submission = self.run_assessor(package, trust)
        self.assertEqual(self.check_for(before_submission, receipt)["signature"], "VERIFIED")
        self.assertEqual(before_submission["assessments"]["delivery_status"], "UNCONFIRMED")
        self.assertEqual(before_submission["assessments"]["acceptance_status"], "UNKNOWN")
        receipt["body"]["data"]["received_at"] = "2026-10-30T11:05:00Z"
        receipt["body"]["recorded_at"] = "2026-10-30T11:05:00Z"
        self.resign(package, trust, receipt)
        after_submission = self.run_assessor(package, trust)
        self.assertEqual(after_submission["assessments"]["delivery_status"], "RECIPIENT_ASSERTED_RECEIPT")

    def test_authentic_receipt_for_other_binding_does_not_apply(self):
        substitutions = {
            "request_id": "another-request",
            "tenant_id": "another-tenant",
            "payload_sha256": "f" * 64,
            "policy_version": "another-version",
            "object_ids": ["another-object"],
        }
        for field, value in substitutions.items():
            with self.subTest(field=field):
                package, trust = self.pair("ER-03")
                record = self.role_record(package, trust, "provider")
                self.assertNotEqual(record["body"]["binding"][field], value)
                record["body"]["binding"][field] = value
                record = self.resign(package, trust, record)
                report = self.run_assessor(package, trust)
                check = self.check_for(report, record)
                self.assertEqual(check["signature"], "VERIFIED")
                self.assertIn(field, check["binding_differences"])
                self.assert_no_provider_attestation(report)

    def test_second_key_in_provider_organization_is_not_independent(self):
        package, trust = self.pair("ER-05")
        baseline = self.run_assessor(package, trust)
        self.assertEqual(
            baseline["assessments"]["deletion_evidence"],
            "INDEPENDENTLY_REVIEWED_WITHIN_DECLARED_SCOPE",
        )
        provider_organization = next(
            key["organization"] for key in trust["keys"].values()
            if "provider" in key["roles"]
        )
        reviewer = self.role_record(package, trust, "reviewer")
        trust["keys"][reviewer["key_id"]]["organization"] = provider_organization
        report = self.run_assessor(package, trust)
        self.assertEqual(self.check_for(report, reviewer)["signature"], "VERIFIED")
        self.assertNotEqual(
            report["assessments"].get("deletion_evidence"),
            "INDEPENDENTLY_REVIEWED_WITHIN_DECLARED_SCOPE",
        )

    def test_known_contradiction_survives_missing_or_bad_extra_evidence(self):
        package, trust = self.pair("UP-05")
        package["records"] = [
            record for record in package["records"]
            if record["body"]["kind"] != "transfer.coverage"
        ]
        bad = copy.deepcopy(package["records"][0])
        bad["body"]["record_id"] = "untrusted-extra-record"
        package["records"].append(bad)
        report = self.run_assessor(package, trust)
        self.assertEqual(self.check_for(report, bad)["signature"], "FAILED")
        self.assertEqual(report["assessments"]["control_assessment"], "VIOLATION")

        package, trust = approved_transfer()
        baseline = self.run_assessor(package, trust)
        self.assertEqual(baseline["assessments"]["transfer_authorization"], "ALLOW")
        health = next(
            record for record in package["records"]
            if record["body"]["kind"] == "transfer.collector_health"
        )
        health["body"]["data"]["available"] = False
        health["body"]["data"]["durable_acknowledged"] = False
        self.resign(package, trust, health)
        add(
            package, "transfer.egress",
            {"observed_at": package["target"]["operation_at"]},
            role="collector",
            recorded_at=package["target"]["operation_at"],
        )
        actual = self.run_assessor(package, trust)
        self.assertEqual(actual["assessments"]["transfer_authorization"], "DENY")
        self.assertEqual(actual["assessments"]["control_assessment"], "VIOLATION")

    def test_absent_evidence_does_not_establish_completion_or_authorship(self):
        for case_id in ("ER-03", "PB-02", "XR-01"):
            with self.subTest(case=case_id):
                package, trust = self.pair(case_id)
                package["records"] = []
                report = self.run_assessor(package, trust)
                self.assertEqual(report["evidence_checks"], [])
                result = report["assessments"]
                if case_id == "ER-03":
                    self.assert_no_provider_attestation(report)
                elif case_id == "PB-02":
                    self.assertEqual(result["ai_involvement"], "UNKNOWN")
                else:
                    self.assertEqual(result["xref_assessment"], "NOT_ESTABLISHED")
                    self.assertNotEqual(
                        result.get("receipt_attribution"),
                        "ESTABLISHED_UNDER_GIVEN_ASSUMPTIONS",
                    )

    def test_publication_policy_expiry_is_evaluated_after_hash_binding(self):
        package, trust = self.pair("PB-01")
        baseline = self.run_assessor(package, trust)
        self.assertEqual(baseline["assessments"]["publication_action"], "BLOCK")
        policy = next(
            record for record in package["records"]
            if record["body"]["kind"] == "publication_policy"
        )
        policy["body"]["data"]["effective_until"] = "2026-10-30T10:00:00Z"
        new_digest = digest(policy["body"]["data"])
        package["target"]["subject"]["policy_sha256"] = new_digest
        for record in list(package["records"]):
            record["body"]["binding"]["policy_sha256"] = new_digest
            self.resign(package, trust, record)
        finish(package, trust)
        report = self.run_assessor(package, trust)
        self.assertTrue(all(c["signature"] == "VERIFIED" for c in report["evidence_checks"]))
        self.assertEqual(report["assessments"]["publication_action"], "REVIEW")

    def test_runtime_is_catalogue_independent_and_ids_are_opaque(self):
        package, trust = self.pair("UP-05")
        baseline = self.run_assessor(package, trust)["assessments"]
        package["evaluation_id"] = "opaque-evaluation-with-no-case-label"
        trust["evaluation_id"] = package["evaluation_id"]
        for record in list(package["records"]):
            record["body"]["evaluation_id"] = package["evaluation_id"]
            self.resign(package, trust, record)
        finish(package, trust)
        with mock.patch("builtins.open", side_effect=AssertionError("Runtime file read")), \
             mock.patch.object(Path, "read_text", side_effect=AssertionError("Runtime file read")), \
             mock.patch.object(Path, "open", side_effect=AssertionError("Runtime file read")):
            actual = self.run_assessor(package, trust)["assessments"]
        self.assertEqual(actual, baseline)

    def test_late_information_response_does_not_rewrite_cutoff_observation(self):
        package, trust = self.pair("IR-01")
        request = next(
            record for record in package["records"]
            if record["body"]["kind"] == "info_request"
        )
        request["body"]["data"]["observation_cutoff"] = "2026-10-30T11:30:00Z"
        request = self.resign(package, trust, request)
        response = add(
            package,
            "info_response",
            {
                "responded_at": "2026-10-30T11:40:00Z",
                "request_record_id": request["body"]["record_id"],
                "status": "complete",
                "answers": [
                    {"question": question, "answer": "Synthetic provider statement"}
                    for question in request["body"]["data"]["questions"]
                ],
            },
            role="recipient",
            recorded_at="2026-10-30T11:40:00Z",
        )
        finish(package, trust)
        late = self.run_assessor(package, trust)
        self.assertEqual(self.check_for(late, response)["eligibility"], "ELIGIBLE")
        self.assertEqual(
            late["assessments"]["response_status"],
            "NO_RESPONSE_OBSERVED_BY_CUTOFF",
        )
        response["body"]["data"]["responded_at"] = "2026-10-30T11:20:00Z"
        response["body"]["recorded_at"] = "2026-10-30T11:20:00Z"
        self.resign(package, trust, response)
        timely = self.run_assessor(package, trust)
        self.assertNotEqual(
            timely["assessments"]["response_status"],
            "NO_RESPONSE_OBSERVED_BY_CUTOFF",
        )


if __name__ == "__main__":
    unittest.main()
