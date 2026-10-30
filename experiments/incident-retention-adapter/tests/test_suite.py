"""Recheck persisted evidence independently of its stored success claims."""

from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
import unittest

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_ROOT))

from retention_adapter import InputError, assess
from suite import run_suite, verify_exports


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, value):
    path.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")


class RetentionExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.original = Path(cls.temp.name) / "original"
        cls.summary = run_suite(cls.original)

    @contextmanager
    def copy_export(self):
        with TemporaryDirectory() as temporary:
            output = Path(temporary) / "export"
            shutil.copytree(self.original, output)
            yield output

    def rewrite_case_with_matching_hash(self, output, case_id, capture):
        """Give tampering a consistent inventory, so hashes alone cannot catch it."""
        case_path = output / "cases" / (case_id + ".json")
        write_json(case_path, capture)
        summary_path = output / "summary.json"
        summary = read_json(summary_path)
        summary["cases"][case_id]["sha256"] = hashlib.sha256(case_path.read_bytes()).hexdigest()
        write_json(summary_path, summary)

    def test_export_roundtrip_rechecks_all_cases_without_writing(self):
        before = {path.relative_to(self.original): path.read_bytes()
                  for path in self.original.rglob("*.json")}
        result = verify_exports(self.original)
        after = {path.relative_to(self.original): path.read_bytes()
                 for path in self.original.rglob("*.json")}
        self.assertEqual(self.summary["case_count"], 16)
        self.assertEqual(self.summary["passed"], 16)
        self.assertEqual(self.summary["failed"], 0)
        self.assertEqual(result["rechecked"], 16)
        self.assertIs(result["source_manifest_matches"], True)
        self.assertTrue(result["cross_case_checks"])
        for value in result["cross_case_checks"].values():
            self.assertIs(value, True)
        self.assertEqual(before, after)

    def test_rehashed_report_cannot_assert_universal_deletion(self):
        with self.copy_export() as output:
            capture = read_json(output / "cases/RT-03.json")
            capture["report"]["universal_deletion"] = "ESTABLISHED"
            self.rewrite_case_with_matching_hash(output, "RT-03", capture)
            with self.assertRaises(InputError):
                verify_exports(output)

    def test_rehashed_signature_forgery_fails_even_with_a_recomputed_report(self):
        with self.copy_export() as output:
            capture = read_json(output / "cases/RT-03.json")
            record = capture["input"]["retention_records"][0]
            signature = record["signature"]
            record["signature"] = ("0" if signature[0] != "0" else "1") + signature[1:]
            capture["report"] = assess(capture["input"], capture["trust"], allow_synthetic=True)
            self.assertEqual(capture["report"]["record_checks"][0]["signature"], "FAILED")
            self.assertEqual(capture["report"]["statements"], [])
            capture["differences"] = []
            self.rewrite_case_with_matching_hash(output, "RT-03", capture)
            with self.assertRaises(InputError):
                verify_exports(output)

    def test_missing_case_cannot_be_hidden_by_shrinking_the_inventory(self):
        for shrink_inventory in (False, True):
            with self.subTest(shrink_inventory=shrink_inventory), self.copy_export() as output:
                (output / "cases/RT-16.json").unlink()
                if shrink_inventory:
                    summary = read_json(output / "summary.json")
                    del summary["cases"]["RT-16"]
                    summary["case_count"] = summary["passed"] = 15
                    write_json(output / "summary.json", summary)
                with self.assertRaises(InputError):
                    verify_exports(output)

    def test_changed_source_manifest_cannot_reuse_a_previous_success(self):
        with self.copy_export() as output:
            summary = read_json(output / "summary.json")
            source = next(iter(summary["source_manifest"]))
            original_hash = summary["source_manifest"][source]
            summary["source_manifest"][source] = ("0" if original_hash[0] != "0" else "1") + original_hash[1:]
            write_json(output / "summary.json", summary)
            with self.assertRaises(InputError):
                verify_exports(output)

    def test_capture_symlinks_are_rejected_even_when_contents_and_hashes_match(self):
        for location in ("root", "summary.json", "cases", "cases/RT-01.json"):
            with self.subTest(location=location), self.copy_export() as output:
                if location == "root":
                    alias = output.parent / "alias"
                    alias.symlink_to(output, target_is_directory=True)
                    candidate = alias
                else:
                    path = output / location
                    is_directory = path.is_dir()
                    target = output.parent / "original-target"
                    path.rename(target)
                    path.symlink_to(target, target_is_directory=is_directory)
                    candidate = output
                with self.assertRaises(InputError):
                    verify_exports(candidate)

    def test_inventory_paths_cannot_escape_or_alias_the_fixed_case_path(self):
        for path in ("../RT-01.json", "cases/../cases/RT-01.json", "/tmp/RT-01.json"):
            with self.subTest(path=path), self.copy_export() as output:
                summary = read_json(output / "summary.json")
                summary["cases"]["RT-01"]["path"] = path
                write_json(output / "summary.json", summary)
                with self.assertRaises(InputError):
                    verify_exports(output)

    def test_json_types_cannot_substitute_equal_python_values(self):
        mutations = ("report_boolean", "expected_integer", "case_boolean", "cross_case_boolean",
                     "summary_integer", "cases_mapping")
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.copy_export() as output:
                if mutation in ("report_boolean", "expected_integer"):
                    capture = read_json(output / "cases/RT-01.json")
                    if mutation == "report_boolean":
                        self.assertIs(capture["report"]["synthetic"], True)
                        capture["report"]["synthetic"] = 1
                    else:
                        self.assertEqual(capture["expected"]["presence_count"], 0)
                        capture["expected"]["presence_count"] = False
                    self.rewrite_case_with_matching_hash(output, "RT-01", capture)
                else:
                    summary = read_json(output / "summary.json")
                    if mutation == "case_boolean":
                        summary["cases"]["RT-01"]["matches_expectations"] = 1
                    elif mutation == "cross_case_boolean":
                        first = next(iter(summary["cross_case_checks"]))
                        summary["cross_case_checks"][first] = 1
                    elif mutation == "summary_integer":
                        summary["failed"] = False
                    else:
                        summary["cases"] = list(summary["cases"])
                    write_json(output / "summary.json", summary)
                with self.assertRaises(InputError):
                    verify_exports(output)


if __name__ == "__main__":
    unittest.main()
