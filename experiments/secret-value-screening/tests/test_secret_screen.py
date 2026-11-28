"""Regressions for the secret-value screening experiment (synthetic input only)."""

import json
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))

import secret_screen as ss  # noqa: E402

CASES = HERE / "cases.json"


class SuiteTests(unittest.TestCase):
    def test_every_case_matches_its_expected_result(self):
        summary = ss.run_suite(CASES)
        mismatches = [r for r in summary["results"] if not r["match"]]
        self.assertEqual(mismatches, [])
        self.assertEqual(summary["cases"], 14)

    def test_known_limit_case_is_declared(self):
        summary = ss.run_suite(CASES)
        self.assertEqual(summary["known_limit_cases"], ["S11-hash-of-low-entropy-secret"])

    def test_stored_cases_hold_no_secret_shaped_literal(self):
        raw = CASES.read_text(encoding="utf-8")
        for name, pattern in ss.VALUE_PATTERNS:
            self.assertIsNone(pattern.search(raw), name)

    def test_every_placeholder_in_cases_is_defined(self):
        raw = CASES.read_text(encoding="utf-8")
        table = ss.synthetic_values()
        import re

        for placeholder in set(re.findall(r"\{\{[A-Z0-9_]+\}\}", raw)):
            self.assertIn(placeholder, table)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.table = ss.synthetic_values()

    def test_report_never_carries_the_matched_text(self):
        for case in ss.load_cases(CASES):
            if "event" not in case:
                continue
            event = ss.materialize(case["event"], self.table)
            report = json.dumps(ss.screen(event, tuple(case.get("not_assessed", ()))))
            for placeholder, value in self.table.items():
                if placeholder in ("{{SHA256_DIGEST}}", "{{BASE64_SIGNATURE}}", "{{SHA256_OF_LOW_ENTROPY}}"):
                    continue
                self.assertNotIn(value, report, case["id"])
                self.assertNotIn(value.split()[-1], report, case["id"])

    def test_no_match_states_its_limit(self):
        report = ss.screen({"header": {"event_type": "X"}})
        self.assertEqual(report["result"], ss.NOT_MATCHED)
        self.assertIn("not evidence", report["limit"])
        self.assertTrue(report["complete_coverage"])

    def test_not_assessed_is_reported_and_lowers_coverage(self):
        event = {"provenance": {"context": {"protected": {"c": self.table["{{BEARER}}"]}}}}
        report = ss.screen(event, ("/provenance/context/protected",))
        self.assertEqual(report["result"], ss.NOT_MATCHED)
        self.assertEqual(report["not_assessed"], ["/provenance/context/protected"])
        self.assertFalse(report["complete_coverage"])

    def test_not_assessed_pointer_that_matches_nothing_is_listed(self):
        report = ss.screen({"header": {"event_type": "X"}}, ("/provenance/missing",))
        self.assertEqual(report["not_assessed_but_absent"], ["/provenance/missing"])

    def test_pointer_prefix_does_not_cover_a_sibling(self):
        event = {"provenance": {"context": {"protected": "x", "protected2": self.table["{{BEARER}}"]}}}
        report = ss.screen(event, ("/provenance/context/protected",))
        self.assertEqual(report["result"], ss.FOUND)
        self.assertEqual(report["findings"][0]["pointer"], "/provenance/context/protected2")

    def test_pointer_escaping(self):
        event = {"a/b": {"c~d": self.table["{{JWT}}"]}}
        report = ss.screen(event)
        self.assertEqual(report["findings"][0]["pointer"], "/a~1b/c~0d")

    def test_non_string_and_empty_values_are_ignored(self):
        event = {"domain_payload": {"api_key": "", "password": None, "secret": 12345, "token": True}}
        self.assertEqual(ss.screen(event)["result"], ss.NOT_MATCHED)


class InputTests(unittest.TestCase):
    def test_byte_order_mark_is_rejected(self):
        self.assertEqual(ss.screen_text("﻿{}")["result"], ss.REJECTED)

    def test_duplicate_member_names_are_rejected(self):
        self.assertEqual(ss.screen_text('{"a": 1, "a": 2}')["result"], ss.REJECTED)

    def test_nested_duplicate_member_names_are_rejected(self):
        self.assertEqual(ss.screen_text('{"a": {"b": 1, "b": 2}}')["result"], ss.REJECTED)

    def test_non_object_top_level_is_rejected(self):
        self.assertEqual(ss.screen_text("[1, 2]")["result"], ss.REJECTED)

    def test_malformed_json_is_rejected(self):
        self.assertEqual(ss.screen_text("{")["result"], ss.REJECTED)


class CliTests(unittest.TestCase):
    def test_run_suite_exit_code(self):
        import contextlib
        import io

        with contextlib.redirect_stdout(io.StringIO()) as out:
            code = ss.main(["run-suite", "--cases", str(CASES)])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())["matched"], 14)


if __name__ == "__main__":
    unittest.main()
