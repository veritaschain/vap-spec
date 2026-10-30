"""Adversarial checks for the separate retention-evidence application contract."""

from copy import deepcopy
from pathlib import Path
import json
import sys
import unittest

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_ROOT))

from fixture_support import FreshFixture, REQUESTED_AT, STATEMENT_AT, DEADLINE, NOW, BEFORE_DEADLINE, AFTER_DEADLINE
from retention_adapter import InputError, assess
from incident_assessor.assess import assess as assess_erasure


class RetentionAdapterTests(unittest.TestCase):
    def run_fixture(self, fixture, *, as_of=None):
        package, trust = fixture.inputs(as_of=as_of)
        return assess(package, trust, allow_synthetic=True)

    def assert_unknown_universal_outcome(self, report):
        self.assertEqual(report["universal_deletion"], "NOT_ESTABLISHED")
        self.assertEqual(report["legal_compliance"], "NOT_ASSESSED")
        self.assertEqual(report["erasure_report"]["assessments"]["target_completion"], "UNKNOWN")
        self.assertEqual(report["erasure_report"]["assessments"]["outside_scope_outcome"], "UNKNOWN")

    def check_for(self, report, record):
        matches = [row for row in report["record_checks"] if row["record_id"] == record["body"]["record_id"]]
        self.assertEqual(len(matches), 1)
        return matches[0]

    def test_clock_alone_changes_deadline_state_but_never_deletion_evidence(self):
        fixture = FreshFixture()
        fixture.statement()
        snapshots = []
        for cutoff, expected in ((BEFORE_DEADLINE, "BEFORE_DECLARED_DEADLINE"),
                                 (DEADLINE, "AT_DECLARED_DEADLINE"),
                                 (AFTER_DEADLINE, "AFTER_DECLARED_DEADLINE")):
            with self.subTest(cutoff=cutoff):
                report = self.run_fixture(fixture, as_of=cutoff)
                self.assertEqual(report["statements"][0]["deadline_state"], expected)
                self.assertEqual(report["erasure_report"]["assessments"]["deletion_evidence"], "REQUEST_ONLY")
                self.assert_unknown_universal_outcome(report)
                snapshots.append(report["erasure_report"]["assessments"])
                if cutoff == BEFORE_DEADLINE:
                    self.assertNotIn("COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF", report["follow_up_reasons"])
                else:
                    self.assertIn("COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF", report["follow_up_reasons"])
        self.assertEqual(snapshots[0], snapshots[1])
        self.assertEqual(snapshots[1], snapshots[2])

    def test_future_planned_deadline_is_not_a_future_record(self):
        fixture = FreshFixture(as_of=BEFORE_DEADLINE)
        statement = fixture.statement()
        report = self.run_fixture(fixture)
        self.assertEqual(len(report["statements"]), 1)
        self.assertEqual(report["statements"][0]["deadline_state"], "BEFORE_DECLARED_DEADLINE")
        self.assertEqual(self.check_for(report, statement)["signature"], "VERIFIED")
        self.assert_unknown_universal_outcome(report)

    def test_equivalent_timezone_instants_have_the_same_boundary_result(self):
        fixture = FreshFixture()
        statement = fixture.statement()
        original = self.run_fixture(fixture, as_of=DEADLINE)
        statement["body"]["data"]["schedule"]["deadline"] = "2026-10-31T09:00:00+09:00"
        fixture.resign(statement)
        alternate = self.run_fixture(fixture, as_of="2026-10-30T20:00:00-04:00")
        self.assertEqual(original["statements"][0]["deadline_state"], "AT_DECLARED_DEADLINE")
        self.assertEqual(alternate["statements"][0]["deadline_state"], "AT_DECLARED_DEADLINE")
        self.assertEqual(original["erasure_report"]["assessments"], alternate["erasure_report"]["assessments"])

    def test_unknown_start_or_calculation_rule_remains_unknown_after_time_passes(self):
        fixture = FreshFixture()
        fixture.statement(schedule={"kind": "unknown", "reason": "Thirty days stated; triggering deletion time is unavailable."})
        for cutoff in (BEFORE_DEADLINE, NOW, "2026-12-01T00:00:00Z"):
            with self.subTest(cutoff=cutoff):
                report = self.run_fixture(fixture, as_of=cutoff)
                self.assertEqual(report["statements"][0]["deadline_state"], "UNKNOWN")
                self.assertIn("UNKNOWN_DEADLINE", report["follow_up_reasons"])
                self.assert_unknown_universal_outcome(report)

    def test_training_and_processing_claims_do_not_answer_deletion_questions(self):
        for use in ("reported-disabled", "reported-enabled", "not-reported"):
            with self.subTest(training=use):
                fixture = FreshFixture()
                fixture.statement(training_use=use, processing_locations=[],
                                  schedule={"kind": "unknown", "reason": "No retention conditions supplied."})
                report = self.run_fixture(fixture)
                self.assertEqual(report["statements"][0]["training_use"], use)
                self.assertEqual(report["statements"][0]["processing_locations"], [])
                self.assertEqual(report["erasure_report"]["assessments"]["deletion_evidence"], "REQUEST_ONLY")
                self.assert_unknown_universal_outcome(report)

    def test_provider_claim_is_attributed_without_independent_completion(self):
        fixture = FreshFixture()
        fixture.statement()
        fixture.attestation()
        report = self.run_fixture(fixture)
        self.assertEqual(report["erasure_report"]["assessments"]["deletion_evidence"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE")
        self.assertEqual(report["erasure_report"]["assessments"]["independent_verification"], "NOT_ESTABLISHED")
        self.assert_unknown_universal_outcome(report)

    def test_existing_scoped_review_report_is_preserved_exactly(self):
        fixture = FreshFixture()
        fixture.attestation()
        fixture.review()
        fixture.statement()
        package, trust = fixture.inputs()
        expected = assess_erasure(package["erasure"], trust["erasure_trust"], allow_synthetic=True)
        report = assess(package, trust, allow_synthetic=True)
        self.assertEqual(report["erasure_report"], expected)
        self.assertEqual(expected["assessments"]["deletion_evidence"], "INDEPENDENTLY_REVIEWED_WITHIN_DECLARED_SCOPE")
        self.assert_unknown_universal_outcome(report)

    def test_future_statement_and_presence_cannot_enter_current_assessment(self):
        fixture = FreshFixture()
        statement = fixture.statement(recorded_at="2026-11-01T00:00:00Z")
        presence = fixture.presence(observed_at="2026-11-01T00:00:00Z", recorded_at="2026-11-01T01:00:00Z")
        earlier = self.run_fixture(fixture)
        self.assertEqual(earlier["statements"], [])
        self.assertEqual(earlier["presence_reports"], [])
        self.assertEqual(self.check_for(earlier, statement)["signature"], "VERIFIED")
        self.assertEqual(self.check_for(earlier, presence)["signature"], "VERIFIED")
        later = self.run_fixture(fixture, as_of="2026-11-01T02:00:00Z")
        self.assertEqual(len(later["statements"]), 1)
        self.assertEqual(len(later["presence_reports"]), 1)
        self.assertEqual(earlier["statements"], [])
        self.assert_unknown_universal_outcome(later)

    def test_every_target_field_binds_signed_statements(self):
        replacements = {
            "request_id": "different-request", "provider_id": "different-provider",
            "tenant_id": "different-tenant", "account_id": "different-account",
            "object_ids": ["different-version"], "payload_sha256": "f" * 64,
        }
        for field, value in replacements.items():
            with self.subTest(field=field):
                fixture = FreshFixture()
                statement = fixture.statement()
                statement["body"]["binding"][field] = value
                fixture.resign(statement)
                report = self.run_fixture(fixture)
                self.assertEqual(report["statements"], [])
                self.assertEqual(self.check_for(report, statement)["signature"], "VERIFIED")

    def test_wrong_request_reference_and_missing_request_do_not_apply(self):
        for mode in ("wrong-reference", "no-request", "invalid-request-signature", "before-request"):
            with self.subTest(mode=mode):
                fixture = FreshFixture(add_request=mode != "no-request")
                kwargs = {"request_record_id": "missing-request"} if mode == "wrong-reference" else {}
                if mode == "before-request":
                    kwargs["recorded_at"] = "2026-09-30T23:59:59Z"
                fixture.statement(**kwargs)
                if mode == "invalid-request-signature":
                    fixture.package["erasure"]["records"][0]["signature"] = "00" * 64
                report = self.run_fixture(fixture)
                self.assertEqual(report["statements"], [])
                self.assert_unknown_universal_outcome(report)

    def test_forged_signature_and_legacy_domain_signature_are_unusable(self):
        for mode in ("tampered-body", "wrong-domain"):
            with self.subTest(mode=mode):
                fixture = FreshFixture()
                statement = fixture.statement()
                if mode == "tampered-body":
                    statement["body"]["data"]["training_use"] = "reported-enabled"
                else:
                    fixture.resign(statement, legacy=True)
                report = self.run_fixture(fixture)
                self.assertEqual(report["statements"], [])
                self.assertEqual(self.check_for(report, statement)["signature"], "FAILED")

    def test_identity_role_and_key_trust_are_separate_from_signature(self):
        for mode in ("wrong-issuer", "wrong-role", "untrusted-key", "expired-key"):
            with self.subTest(mode=mode):
                fixture = FreshFixture()
                statement = fixture.statement()
                key = fixture.trust["erasure_trust"]["keys"]["provider-fresh-key"]
                if mode == "wrong-issuer":
                    statement["body"]["issuer"] = "another-issuer"
                    fixture.resign(statement)
                elif mode == "wrong-role":
                    key["roles"] = ["collector"]
                elif mode == "untrusted-key":
                    del fixture.trust["erasure_trust"]["keys"]["provider-fresh-key"]
                else:
                    key["not_after"] = STATEMENT_AT
                report = self.run_fixture(fixture)
                self.assertEqual(report["statements"], [])
                if mode != "untrusted-key":
                    self.assertEqual(self.check_for(report, statement)["signature"], "VERIFIED")

    def test_separate_evaluator_cutoff_target_and_evaluation_pins_are_enforced(self):
        for part in ("as_of", "target", "evaluation_id", "workflow"):
            with self.subTest(part=part):
                fixture = FreshFixture()
                fixture.statement()
                package, trust = fixture.inputs()
                if part == "as_of":
                    package["erasure"]["as_of"] = "2026-11-01T12:00:00Z"
                elif part == "target":
                    package["erasure"]["target"]["subject"]["tenant_id"] = "substituted-target"
                elif part == "evaluation_id":
                    package["erasure"]["evaluation_id"] = "substituted-evaluation"
                else:
                    package["erasure"]["workflow"] = "transfer"
                with self.assertRaises(InputError):
                    assess(package, trust, allow_synthetic=True)

    def test_each_exception_is_retained_without_inferring_disappearance(self):
        exceptions = [
            {"location": "active", "reason": "Synthetic bounded retention claim", "until": "2026-10-30T00:00:00Z"},
            {"location": "provider-log", "reason": "Synthetic exception with no reported end", "until": None},
        ]
        fixture = FreshFixture()
        fixture.statement(exceptions=exceptions)
        report = self.run_fixture(fixture)
        returned = report["statements"][0]["exceptions"]
        self.assertEqual([{k: v for k, v in item.items() if k != "boundary_state"} for item in returned], exceptions)
        self.assertEqual([item["boundary_state"] for item in returned], ["AFTER_DECLARED_DEADLINE", "UNKNOWN"])
        self.assertIn("REPORTED_RETENTION_EXCEPTION", report["follow_up_reasons"])
        self.assert_unknown_universal_outcome(report)

    def test_completion_evidence_must_cover_the_statement_locations_and_request(self):
        for mode in ("partial-location-claim", "other-request-record", "matching-scope"):
            with self.subTest(mode=mode):
                fixture = FreshFixture()
                if mode == "other-request-record":
                    fixture.add_legacy("erasure.request", {
                        "requested_at": REQUESTED_AT,
                        "requested_locations": ["active", "provider-log", "backup"],
                    }, role="responder", record_id="another-request-record")
                    fixture.statement(locations=["active"], request_record_id="another-request-record")
                else:
                    fixture.statement(locations=["active"] if mode == "matching-scope" else ["active", "provider-log"])
                fixture.attestation()
                report = self.run_fixture(fixture)
                self.assertEqual(report["erasure_report"]["assessments"]["deletion_evidence"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE")
                if mode == "matching-scope":
                    self.assertNotIn("COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF", report["follow_up_reasons"])
                else:
                    self.assertIn("COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF", report["follow_up_reasons"])
                self.assert_unknown_universal_outcome(report)

    def test_multiple_statements_are_preserved_not_replaced_by_the_latest(self):
        fixture = FreshFixture()
        fixture.statement(record_id="z-first", deadline="2026-10-30T00:00:00Z")
        fixture.statement(record_id="a-second", recorded_at="2026-10-02T00:00:00Z", deadline="2026-11-30T00:00:00Z")
        report = self.run_fixture(fixture)
        self.assertEqual([r["record_id"] for r in report["statements"]], ["a-second", "z-first"])
        self.assertEqual({r["deadline_state"] for r in report["statements"]}, {"BEFORE_DECLARED_DEADLINE", "AFTER_DECLARED_DEADLINE"})
        self.assertIn("MULTIPLE_STATEMENTS_REQUIRE_REVIEW", report["follow_up_reasons"])
        self.assert_unknown_universal_outcome(report)

    def test_presence_at_or_after_deadline_requires_review_not_universal_failure(self):
        for observed in (BEFORE_DEADLINE, DEADLINE, AFTER_DEADLINE):
            with self.subTest(observed=observed):
                fixture = FreshFixture()
                fixture.statement()
                fixture.presence(observed_at=observed)
                report = self.run_fixture(fixture)
                self.assertEqual(len(report["presence_reports"]), 1)
                if observed == BEFORE_DEADLINE:
                    self.assertNotIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])
                else:
                    self.assertIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])
                self.assert_unknown_universal_outcome(report)

    def test_later_presence_does_not_rewrite_prior_scoped_erasure_assessment(self):
        fixture = FreshFixture()
        fixture.statement()
        fixture.attestation()
        fixture.review()
        baseline = self.run_fixture(fixture)
        fixture.presence(observed_at="2026-10-31T02:00:00Z", recorded_at="2026-10-31T03:00:00Z")
        report = self.run_fixture(fixture)
        self.assertEqual(report["erasure_report"], baseline["erasure_report"])
        self.assertIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])
        self.assert_unknown_universal_outcome(report)

    def test_presence_before_or_outside_declared_scope_is_not_deadline_contradiction(self):
        fixture = FreshFixture()
        fixture.statement(locations=["active"])
        fixture.presence(location="backup")
        report = self.run_fixture(fixture)
        self.assertEqual(len(report["presence_reports"]), 1)
        self.assertNotIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])
        self.assert_unknown_universal_outcome(report)

    def test_prior_presence_is_context_not_post_deletion_counterevidence(self):
        fixture = FreshFixture()
        fixture.statement()
        fixture.attestation()
        fixture.presence(observed_at="2026-09-30T23:59:59Z")
        report = self.run_fixture(fixture)
        self.assertEqual(len(report["presence_reports"]), 1)
        self.assertNotIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])
        self.assertNotIn("PRESENCE_REPORTED_AT_OR_AFTER_COMPLETION_CLAIM", report["follow_up_reasons"])
        self.assert_unknown_universal_outcome(report)

    def test_deadline_before_request_does_not_turn_prior_presence_into_post_request_evidence(self):
        fixture = FreshFixture()
        fixture.statement(deadline="2026-09-29T00:00:00Z")
        fixture.presence(observed_at="2026-09-30T23:59:59Z")
        report = self.run_fixture(fixture)
        self.assertEqual(report["statements"][0]["deadline_state"], "AFTER_DECLARED_DEADLINE")
        self.assertEqual(len(report["presence_reports"]), 1)
        self.assertNotIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])
        self.assert_unknown_universal_outcome(report)

    def test_presence_for_another_request_record_does_not_flag_this_statement(self):
        fixture = FreshFixture()
        fixture.add_legacy("erasure.request", {
            "requested_at": REQUESTED_AT,
            "requested_locations": ["active", "provider-log", "backup"],
        }, role="responder", record_id="another-request-record")
        fixture.statement()
        fixture.presence(request_record_id="another-request-record")
        report = self.run_fixture(fixture)
        self.assertEqual(len(report["presence_reports"]), 1)
        self.assertNotIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])
        self.assert_unknown_universal_outcome(report)

    def test_unrelated_or_forged_presence_cannot_add_deadline_findings(self):
        for mode in ("wrong-account", "wrong-version", "wrong-request", "forged", "observation-after-recording"):
            with self.subTest(mode=mode):
                fixture = FreshFixture()
                fixture.statement()
                presence = fixture.presence()
                if mode == "wrong-account":
                    presence["body"]["binding"]["account_id"] = "another-account"
                elif mode == "wrong-version":
                    presence["body"]["binding"]["object_ids"] = ["object-synthetic-v2"]
                elif mode == "wrong-request":
                    presence["body"]["data"]["request_record_id"] = "another-request"
                elif mode == "observation-after-recording":
                    presence["body"]["data"]["observed_at"] = "2026-10-31T04:00:00Z"
                if mode != "forged":
                    fixture.resign(presence, "collector")
                else:
                    presence["body"]["data"]["location"] = "provider-log"
                report = self.run_fixture(fixture)
                self.assertEqual(report["presence_reports"], [])
                self.assertNotIn("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE", report["follow_up_reasons"])

    def test_record_order_does_not_change_applied_claims_or_follow_up(self):
        fixture = FreshFixture()
        fixture.statement(record_id="z-statement")
        fixture.statement(record_id="a-statement", deadline="2026-11-30T00:00:00Z")
        fixture.presence(record_id="z-presence")
        fixture.presence(record_id="a-presence", location="provider-log")
        baseline = self.run_fixture(fixture)
        fixture.package["retention_records"].reverse()
        reverse = self.run_fixture(fixture)
        for key in ("statements", "presence_reports", "follow_up_reasons", "universal_deletion", "erasure_report"):
            self.assertEqual(baseline[key], reverse[key], key)
        self.assertEqual(reverse["follow_up_reasons"], sorted(set(reverse["follow_up_reasons"])))
        self.assertEqual([r["record_id"] for r in reverse["presence_reports"]], ["a-presence", "z-presence"])

    def test_missing_requested_location_does_not_broaden_scope(self):
        for kind in ("statement", "presence"):
            with self.subTest(kind=kind):
                fixture = FreshFixture()
                if kind == "statement":
                    fixture.statement(locations=["unrequested-storage"])
                else:
                    fixture.presence(location="unrequested-storage")
                report = self.run_fixture(fixture)
                self.assertEqual(report["statements"] if kind == "statement" else report["presence_reports"], [])

    def test_duplicate_record_ids_across_old_and_new_evidence_are_rejected(self):
        for mode in ("new-new", "old-new"):
            with self.subTest(mode=mode):
                fixture = FreshFixture()
                statement = fixture.statement(record_id=fixture.request_id if mode == "old-new" else "repeated-id")
                if mode == "new-new":
                    fixture.package["retention_records"].append(deepcopy(statement))
                with self.assertRaises(InputError):
                    self.run_fixture(fixture)

    def test_malformed_or_unsupported_supplied_material_is_not_silent_unknown(self):
        mutations = {
            "unknown-kind": lambda r: r["body"].update(kind="retention.unlearning"),
            "unknown-data-field": lambda r: r["body"]["data"].update(deleted=True),
            "boolean-training": lambda r: r["body"]["data"].update(training_use=False),
            "empty-locations": lambda r: r["body"]["data"].update(locations=[]),
            "duplicate-locations": lambda r: r["body"]["data"].update(locations=["active", "active"]),
            "bad-digest": lambda r: r["body"]["data"].update(terms_sha256="g" * 64),
            "timezone-free": lambda r: r["body"]["data"].update(schedule={"kind": "stated-deadline", "deadline": "2026-10-31T00:00:00"}),
            "unknown-empty-reason": lambda r: r["body"]["data"].update(schedule={"kind": "unknown", "reason": ""}),
            "deadline-and-unknown": lambda r: r["body"]["data"].update(schedule={"kind": "unknown", "reason": "unestablished", "deadline": DEADLINE}),
            "malformed-exception": lambda r: r["body"]["data"].update(exceptions=[{"location": "active", "reason": "hold", "until": False}]),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                fixture = FreshFixture()
                record = fixture.statement()
                mutate(record)
                fixture.resign(record)
                with self.assertRaises(InputError):
                    self.run_fixture(fixture)

    def test_missing_binding_identity_fields_and_unrecognized_wrappers_are_rejected(self):
        for field in ("account_id", "payload_sha256"):
            with self.subTest(field=field):
                fixture = FreshFixture()
                del fixture.package["erasure"]["target"]["subject"][field]
                for record in fixture.package["erasure"]["records"]:
                    del record["body"]["binding"][field]
                    fixture.resign(record, "responder", legacy=True)
                with self.assertRaises(InputError):
                    self.run_fixture(fixture)
        fixture = FreshFixture()
        package, trust = fixture.inputs()
        package["retention_completed"] = True
        with self.assertRaises(InputError):
            assess(package, trust, allow_synthetic=True)

    def test_synthetic_mode_requires_explicit_opt_in_and_real_boolean(self):
        fixture = FreshFixture()
        fixture.statement()
        package, trust = fixture.inputs()
        with self.assertRaises(InputError):
            assess(package, trust)
        for flag in (1, "true", None):
            with self.subTest(flag_type=type(flag).__name__):
                with self.assertRaises(InputError):
                    assess(package, trust, allow_synthetic=flag)

    def test_inputs_are_unchanged_and_only_public_fixture_material_is_returned(self):
        fixture = FreshFixture()
        fixture.statement()
        package, trust = fixture.inputs()
        before = deepcopy((package, trust))
        report = assess(package, trust, allow_synthetic=True)
        self.assertEqual((package, trust), before)
        public = json.dumps({"package": package, "trust": trust, "report": report}, sort_keys=True)
        private_seeds = [key.private_bytes_raw().hex() for key in fixture._private_keys.values()]
        self.assertFalse(any(seed in public for seed in private_seeds), "Public artifacts must omit every private signing seed")
        other = FreshFixture()
        self.assertNotEqual(trust["erasure_trust"]["keys"]["provider-fresh-key"]["public_key"],
                            other.trust["erasure_trust"]["keys"]["provider-fresh-key"]["public_key"])


if __name__ == "__main__":
    unittest.main()
