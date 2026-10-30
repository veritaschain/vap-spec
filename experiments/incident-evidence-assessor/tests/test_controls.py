"""Positive controls and the remaining identified evidence-boundary regressions."""

from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_ROOT))

from incident_assessor.assess import assess
from fixture_publication_response import information_response, publication_ready
from fixture_support import BEFORE, NOW, add, sign
from fixture_transfer_erasure import approved_transfer, scoped_erasure_review


def evaluate(package, trust):
    return assess(package, trust, allow_synthetic=True)


def replace_signed(package, record, role):
    replacement = sign(copy.deepcopy(record["body"]), role)
    package["records"][package["records"].index(record)] = replacement
    return replacement


class PositiveControlsAndRegressions(unittest.TestCase):
    def test_positive_controls_support_only_the_documented_dimensions(self):
        controls = (
            (approved_transfer, {
                "transfer_authorization": "ALLOW",
                "proposed_transfer_authorization": "ALLOW",
                "collector_health": "AVAILABLE_WITH_DURABLE_ACKNOWLEDGEMENT",
                "remote_outcome": "UNKNOWN",
            }),
            (scoped_erasure_review, {
                "deletion_evidence": "INDEPENDENTLY_REVIEWED_WITHIN_DECLARED_SCOPE",
                "review_result": "SUPPORTED_WITHIN_REVIEW_METHOD_AND_LIMITATIONS",
                "outside_scope_outcome": "UNKNOWN",
                "target_completion": "UNKNOWN",
            }),
            (publication_ready, {
                "publication_action": "REVIEW",
                "ai_involvement": "OBSERVED_UNDER_GIVEN_ASSUMPTIONS",
                "policy_applicability": "BOUND_AND_EFFECTIVE_UNDER_GIVEN_ASSUMPTIONS",
                "approval_applicability": "BOUND_APPROVAL_RECORDED",
                "disclosure_assessment": "REQUIRES_CONTENT_REVIEW",
                "delivery_status": "RECIPIENT_ASSERTED_RECEIPT",
                "acceptance_status": "RECIPIENT_ASSERTED_ACCEPTANCE",
                "activity_completeness": "UNKNOWN",
            }),
            (information_response, {
                "request_delivery": "RECEIPT_ESTABLISHED_UNDER_GIVEN_ASSUMPTIONS",
                "response_status": "COMPLETE_RESPONSE_RECORDED_BY_CUTOFF",
                "requested_facts": "UNKNOWN",
            }),
        )
        for factory, dimensions in controls:
            with self.subTest(control=factory.__name__):
                report = evaluate(*factory())
                for name, expected in dimensions.items():
                    self.assertEqual(report["assessments"].get(name), expected, name)
                self.assertEqual(report["evidence_integrity"], "VERIFIED_UNDER_EVALUATOR_TRUST")
                self.assertEqual(report["full_vap_conformance"], "NOT_ASSESSED")
                self.assertEqual(report["full_cap_conformance"], "NOT_ASSESSED")
                self.assertEqual(report["legal_compliance"], "NOT_ASSESSED")

    def test_authentic_transfer_policy_for_another_stage_cannot_allow(self):
        package, trust = approved_transfer()
        policy = next(
            record for record in package["records"]
            if record["body"]["kind"] == "transfer.policy"
        )
        policy["body"]["binding"]["stage"] = "unrelated-stage"
        policy = replace_signed(package, policy, "policy")
        report = evaluate(package, trust)
        check = next(
            item for item in report["evidence_checks"]
            if item["record_id"] == policy["body"]["record_id"]
        )
        self.assertEqual(check["signature"], "VERIFIED")
        self.assertIn("stage", check["binding_differences"])
        self.assertEqual(report["assessments"]["transfer_authorization"], "REVIEW")
        self.assertEqual(report["assessments"]["policy_binding"], "EXPIRED_OR_UNRESOLVED")

    def test_inconclusive_review_prevents_unqualified_promotion_in_either_order(self):
        package, trust = scoped_erasure_review()
        review = next(
            record for record in package["records"]
            if record["body"]["kind"] == "erasure.review"
        )
        second = copy.deepcopy(review["body"])
        second["record_id"] = "additional-inconclusive-review"
        second["data"]["conclusion"] = "inconclusive"
        package["records"].append(sign(second, "reviewer"))
        outcomes = []
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                candidate = copy.deepcopy(package)
                if reverse:
                    candidate["records"].reverse()
                report = evaluate(candidate, trust)
                result = report["assessments"]
                outcomes.append(result)
                self.assertEqual(report["evidence_integrity"], "VERIFIED_UNDER_EVALUATOR_TRUST")
                self.assertEqual(result["deletion_evidence"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE")
                self.assertEqual(result["independent_verification"], "NOT_ESTABLISHED")
                self.assertEqual(result["review_result"], "INCONCLUSIVE_OR_CONFLICTING_REVIEWS")
        self.assertEqual(outcomes[0], outcomes[1])

    def test_future_or_conflicting_coverage_cannot_establish_non_observation(self):
        package, trust = approved_transfer()
        decision = next(
            record for record in package["records"]
            if record["body"]["kind"] == "transfer.decision"
        )
        decision["body"]["data"]["decision"] = "deny"
        replace_signed(package, decision, "gateway")
        coverage = add(
            package, "transfer.coverage",
            {
                "window_start": BEFORE,
                "window_end": NOW,
                "covered_routes": [package["target"]["subject"]["route_id"]],
                "complete": True,
                "dispatch_observed": False,
            },
            role="collector", recorded_at=NOW, record_id="complete-route-coverage",
        )
        baseline = evaluate(package, trust)
        self.assertEqual(baseline["assessments"]["transfer_observation"], "NOT_OBSERVED")

        for mutation in ("future-window", "incomplete-conflict"):
            with self.subTest(mutation=mutation):
                candidate = copy.deepcopy(package)
                altered = next(
                    record for record in candidate["records"]
                    if record["body"]["record_id"] == coverage["body"]["record_id"]
                )
                if mutation == "future-window":
                    altered["body"]["data"]["window_end"] = "2026-10-30T13:00:00Z"
                    replace_signed(candidate, altered, "collector")
                else:
                    second = copy.deepcopy(altered["body"])
                    second["record_id"] = "conflicting-incomplete-route-coverage"
                    second["data"]["complete"] = False
                    candidate["records"].append(sign(second, "collector"))
                report = evaluate(candidate, trust)
                self.assertEqual(report["evidence_integrity"], "VERIFIED_UNDER_EVALUATOR_TRUST")
                self.assertEqual(report["assessments"]["transfer_authorization"], "DENY")
                self.assertEqual(report["assessments"]["coverage"], "INCOMPLETE")
                self.assertEqual(report["assessments"]["transfer_observation"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()
