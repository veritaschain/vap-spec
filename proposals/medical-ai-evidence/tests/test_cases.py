"""Synthetic application-level checks; no patient data or external services."""

import copy
import hashlib
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).parent
sys.path.insert(0, str(ROOT.parent))
from synthetic_assessment import assess


def commitment(text):
    return "sha256:" + hashlib.sha256(text.encode()).hexdigest()


class SyntheticCases(unittest.TestCase):
    def test_nine_catalogue_cases(self):
        cases = json.loads((ROOT / "cases.json").read_text())
        self.assertEqual(len(cases), 9)
        self.assertEqual(len({case["id"] for case in cases}), 9)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertNotIn("expect", case)
                result = assess(case["evidence"])
                for dimension, expected in case["expected"].items():
                    self.assertEqual(result[dimension], expected)

    def test_empty_evidence_never_becomes_a_positive_result(self):
        self.assertEqual(set(assess({}).values()), {"UNKNOWN"})

    def test_nonobject_input_is_rejected(self):
        for evidence in (None, [], "passed", True):
            with self.subTest(evidence=evidence), self.assertRaises(TypeError):
                assess(evidence)

    def test_expectations_and_scenario_names_cannot_select_a_result(self):
        evidence = {"check_status": "not_run", "provider_filter_state": None}
        original = copy.deepcopy(evidence)
        result = assess(evidence)
        self.assertEqual(evidence, original)
        for label in ("NOT_RUN", "PASSED", "PROVIDER_STATE_UNOBSERVABLE"):
            with self.subTest(label=label):
                self.assertEqual(assess({**evidence, "expect": label,
                                         "expected_result": label, "id": label}), result)
        self.assertEqual(result["check_execution"], "NOT_RUN")
        self.assertEqual(result["provider_state"], "UNKNOWN")

    def test_missing_or_malformed_digests_are_unknown(self):
        valid = commitment("synthetic observation")
        for bad in (None, "", "sha256:a", "sha256:" + "z" * 64, [], 1):
            for first, second in ((bad, valid), (valid, bad), (bad, bad)):
                with self.subTest(first=first, second=second):
                    result = assess({"draft_digest": first, "display_digest": second,
                                     "original_digest": first, "translated_digest": second,
                                     "replay_digest": second, "parent_ref": "source-1"})
                    for dimension in ("display", "translation", "replay"):
                        self.assertEqual(result[dimension], "UNKNOWN")

    def test_equal_digests_do_not_report_divergence(self):
        value = commitment("same synthetic bytes")
        result = assess({"draft_digest": value, "display_digest": value,
                         "original_digest": value, "translated_digest": value,
                         "replay_digest": value, "parent_ref": "source-1"})
        for dimension in ("display", "translation", "replay"):
            self.assertEqual(result[dimension], "SAME_COMMITMENT")

    def test_translation_requires_a_declared_parent(self):
        for parent in (None, "", " ", []):
            with self.subTest(parent=parent):
                result = assess({"original_digest": commitment("original"),
                                 "translated_digest": commitment("translation"),
                                 "parent_ref": parent})
                self.assertEqual(result["translation"], "UNKNOWN")

    def test_invalid_counts_or_unbound_manifest_do_not_pass(self):
        for count in (None, True, -1, "4", 4.0, []):
            with self.subTest(count=count):
                self.assertEqual(assess({"anchored_count": count, "submitted_count": 4,
                                         "manifest_bound": True})["submitted_batch"], "UNKNOWN")
                self.assertEqual(assess({"anchored_count": 5, "submitted_count": count,
                                         "manifest_bound": True})["submitted_batch"], "UNKNOWN")
        for binding in (None, False, "true", 1):
            with self.subTest(binding=binding):
                self.assertEqual(assess({"anchored_count": 5, "submitted_count": 4,
                                         "manifest_bound": binding})["submitted_batch"], "UNKNOWN")

    def test_count_comparison_keeps_conflicts_distinct(self):
        for submitted, expected in ((4, "INCOMPLETE_SUBMISSION"), (5, "COUNTS_MATCH"),
                                    (6, "COUNT_CONFLICT")):
            with self.subTest(submitted=submitted):
                self.assertEqual(assess({"anchored_count": 5, "submitted_count": submitted,
                                         "manifest_bound": True})["submitted_batch"], expected)

    def test_unknown_or_timed_out_checks_never_pass(self):
        for status in (None, "timeout", "unknown", "guessed-passed", [], True):
            with self.subTest(status=status):
                result = assess({"check_status": status, "provider_filter_state": status})
                self.assertEqual(result["check_execution"], "UNKNOWN")
                self.assertEqual(result["provider_state"], "UNKNOWN")

    def test_patient_field_list_distinguishes_missing_from_unknown(self):
        self.assertEqual(assess({"patient_fields": []})["patient_context"], "MISSING")
        self.assertEqual(assess({"patient_fields": ["renal_function"]})["patient_context"], "PRESENT")
        for fields in (None, "renal_function", [None], [""], [" "]):
            with self.subTest(fields=fields):
                self.assertEqual(assess({"patient_fields": fields})["patient_context"], "UNKNOWN")

    def test_multiple_dimensions_remain_separate(self):
        result = assess({"check_status": "passed", "collector_coverage": "partial",
                         "draft_digest": commitment("with warning"),
                         "display_digest": commitment("without warning")})
        self.assertEqual(result["check_execution"], "REPORTED_PASSED")
        self.assertEqual(result["collection"], "UNOBSERVED")
        self.assertEqual(result["display"], "DIVERGENCE")
        self.assertEqual(result["provider_state"], "UNKNOWN")


if __name__ == "__main__":
    unittest.main()

