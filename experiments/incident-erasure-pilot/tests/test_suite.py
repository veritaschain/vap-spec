from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from erasure_pilot.protocol import InputError, decode_json, sha256_bytes
from erasure_pilot.suite import run_suite, verify_case, verify_exports, write_json


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        cls.root = Path(cls.temp.name) / "export"
        cls.summary = run_suite(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def tearDown(self):
        write_json(self.root / "summary.json", self.summary)

    def test_actual_scenarios_and_read_only_recheck(self):
        self.assertEqual(self.summary["total"], 18)
        self.assertEqual(self.summary["matched"], 18)
        result = verify_exports(self.root)
        self.assertEqual(result["verified_exports"], 18)
        self.assertIs(result["filesystem_actions_reexecuted"], False)

    def test_summary_cannot_promote_scope_or_hide_failed_counts(self):
        for name, value in (("universal_erasure", "ESTABLISHED"), ("independent_reproduction", "ESTABLISHED"),
                            ("raw_object_content_exported", True), ("matched", 17), ("total", True)):
            with self.subTest(name=name):
                changed = deepcopy(self.summary)
                changed[name] = value
                write_json(self.root / "summary.json", changed)
                with self.assertRaises(InputError):
                    verify_exports(self.root)

    def test_rehashed_case_cannot_forge_assessment(self):
        path = self.root / "cases/LE-01.json"
        raw = path.read_bytes()
        changed = decode_json(raw)
        changed["records"][0]["assessment"]["unknown_domains"]["backups"] = "DELETED"
        try:
            write_json(path, changed)
            summary = deepcopy(self.summary)
            summary["results"][0]["export_sha256"] = sha256_bytes(path.read_bytes())
            write_json(self.root / "summary.json", summary)
            with self.assertRaises(InputError):
                verify_exports(self.root)
        finally:
            path.write_bytes(raw)

    def test_retained_read_controls_cannot_be_relabelled_or_rebound(self):
        path = self.root / "cases/LE-12.json"
        raw = path.read_bytes()
        changed = decode_json(raw)
        changed["retained_controls"][0]["body"]["state"] = "DELETED"
        try:
            write_json(path, changed)
            summary = deepcopy(self.summary)
            summary["results"][11]["export_sha256"] = sha256_bytes(path.read_bytes())
            write_json(self.root / "summary.json", summary)
            with self.assertRaises(InputError):
                verify_exports(self.root)
        finally:
            path.write_bytes(raw)

    def test_retained_read_must_precede_case_completion_cutoff(self):
        data = decode_json((self.root / "cases/LE-12.json").read_bytes())
        data["case_as_of"] = data["records"][0]["bundle"]["as_of"]
        with self.assertRaises(InputError):
            verify_case(data)


if __name__ == "__main__":
    unittest.main()
