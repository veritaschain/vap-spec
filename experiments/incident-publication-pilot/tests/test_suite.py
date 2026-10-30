"""Integration regressions for stored observations and canonical replay."""

from copy import deepcopy
from pathlib import Path
import tempfile
import unittest

from publication_pilot.protocol import InputError
from publication_pilot.suite import run_case, verify_case, publisher_for, capture
from publication_pilot.harness import make_case
from publication_pilot.gate import Gate, verify_report


class SuiteTests(unittest.TestCase):
    def test_mutation_after_capture_cannot_replace_approved_output(self):
        case = make_case()
        original = capture(case)
        expected = case["candidate"]["html"].encode("utf-8")
        def mutate_caller_objects():
            case["candidate"]["html"] = "unapproved replacement"
            case["candidate"]["source"]["operations"] = []
            case["trust"]["keys"] = {}
            case["approval"]["release"]["body"]["decision"] = "deny"
        with tempfile.TemporaryDirectory() as directory:
            publisher = publisher_for(case, Path(directory) / "publisher")
            report = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], publisher,
                                                after_snapshot=mutate_caller_objects)
            self.assertEqual(report["state"], "LOCAL_OUTPUT_CONFIRMED")
            self.assertEqual(next(publisher.visible_root.iterdir()).read_bytes(), expected)
            self.assertTrue(verify_report(original["candidate"], original["trust"], original["approval"], report, case["config"]))

    def test_stale_approval_rechecks_across_dictionary_order(self):
        with tempfile.TemporaryDirectory() as directory:
            case = run_case("LP-02", Path(directory) / "publisher")
            self.assertEqual(case["actual"]["states"], ["BLOCKED_WITHOUT_PUBLICATION"])
            self.assertTrue(verify_case(case))

    def test_unknown_and_bypass_lengths_must_match_candidate_measurements(self):
        for case_id in ("LP-14", "LP-16"):
            with self.subTest(case_id=case_id), tempfile.TemporaryDirectory() as directory:
                case = run_case(case_id, Path(directory) / "publisher")
                self.assertTrue(verify_case(case))
                changed = deepcopy(case)
                next(iter(changed["visible"]["files"].values()))["byte_length"] += 1
                with self.assertRaises(InputError):
                    verify_case(changed)

    def test_changed_visible_observation_does_not_rewrite_confirmed_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            case = run_case("LP-01", Path(directory) / "publisher")
            self.assertTrue(verify_case(case))
            filename = next((Path(directory) / "publisher" / "visible").iterdir())
            filename.chmod(0o600)  # Trusted owner can alter its file; readonly mode is not OS isolation.
            filename.write_bytes(b"changed after the earlier observation")
            from publication_pilot.protocol import sha256_bytes
            changed = deepcopy(case)
            changed["visible"]["files"][filename.name] = {"sha256": sha256_bytes(filename.read_bytes()), "byte_length": filename.stat().st_size}
            with self.assertRaises(InputError):
                verify_case(changed)
            self.assertEqual(case["records"][0]["report"]["state"], "LOCAL_OUTPUT_CONFIRMED")


if __name__ == "__main__":
    unittest.main()
