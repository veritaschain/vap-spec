"""Exercise the command boundary with real JSON files and subprocesses."""

import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT_ROOT))

from fixture_support import FreshFixture
from retention_adapter import assess


class RetentionCliTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.directory = Path(temporary.name)
        fixture = FreshFixture()
        fixture.statement()
        self.package, self.trust = fixture.inputs()
        self.input_path = self.directory / "input.json"
        self.trust_path = self.directory / "trust.json"
        self.input_path.write_text(json.dumps(self.package), encoding="utf-8")
        self.trust_path.write_text(json.dumps(self.trust), encoding="utf-8")

    def command(self, *arguments):
        return subprocess.run([sys.executable, *arguments], cwd=EXPERIMENT_ROOT, text=True,
                              capture_output=True, timeout=30, check=False)

    def assess_cli(self, *arguments):
        return self.command("-m", "retention_adapter", "assess", "--input", str(self.input_path),
                            "--trust", str(self.trust_path), *arguments)

    def test_synthetic_keys_require_opt_in_before_producing_a_report(self):
        output = self.directory / "blocked-report.json"
        blocked = self.assess_cli("--output", str(output))
        self.assertEqual(blocked.returncode, 2, blocked.stderr)
        self.assertIn("--allow-synthetic", blocked.stderr)
        self.assertEqual(blocked.stdout, "")
        self.assertFalse(output.exists())

        allowed = self.assess_cli("--allow-synthetic")
        self.assertEqual(allowed.returncode, 0, allowed.stderr)
        self.assertEqual(allowed.stderr, "")
        report = json.loads(allowed.stdout)
        self.assertIs(report["synthetic"], True)
        self.assertEqual(report, assess(self.package, self.trust, allow_synthetic=True))

    def test_output_matches_api_and_existing_files_or_symlinks_are_preserved(self):
        output = self.directory / "report.json"
        result = self.assess_cli("--allow-synthetic", "--output", str(output))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertEqual(json.loads(output.read_text(encoding="utf-8")),
                         assess(self.package, self.trust, allow_synthetic=True))

        original_bytes = output.read_bytes()
        alias = self.directory / "report-alias.json"
        alias.symlink_to(output)
        for destination in (output, alias):
            with self.subTest(destination=destination.name):
                rejected = self.assess_cli("--allow-synthetic", "--output", str(destination))
                self.assertEqual(rejected.returncode, 2, rejected.stderr)
                self.assertEqual(rejected.stdout, "")
                self.assertEqual(output.read_bytes(), original_bytes)
                self.assertTrue(alias.is_symlink())

    def test_duplicate_json_keys_are_rejected_in_both_input_and_trust(self):
        for path, value in ((self.input_path, self.package), (self.trust_path, self.trust)):
            with self.subTest(file=path.name):
                original = path.read_text(encoding="utf-8")
                duplicate = '{"format":' + json.dumps(value["format"]) + "," + original[1:]
                path.write_text(duplicate, encoding="utf-8")
                output = self.directory / (path.stem + "-rejected-report.json")
                try:
                    result = self.assess_cli("--allow-synthetic", "--output", str(output))
                finally:
                    path.write_text(original, encoding="utf-8")
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn("Duplicate JSON key", result.stderr)
                self.assertEqual(result.stdout, "")
                self.assertFalse(output.exists())

    def test_suite_cli_runs_verifies_and_refuses_to_overwrite_its_capture(self):
        output = self.directory / "capture"
        run = self.command("suite.py", "run", "--output", str(output))
        self.assertEqual(run.returncode, 0, run.stderr)
        measured = json.loads(run.stdout)
        self.assertEqual((measured["case_count"], measured["passed"], measured["failed"]), (16, 16, 0))
        original_bytes = {path.relative_to(output): path.read_bytes() for path in output.rglob("*.json")}

        verify = self.command("suite.py", "verify", str(output))
        self.assertEqual(verify.returncode, 0, verify.stderr)
        self.assertEqual(json.loads(verify.stdout)["rechecked"], 16)

        rerun = self.command("suite.py", "run", "--output", str(output))
        self.assertEqual(rerun.returncode, 2, rerun.stderr)
        self.assertIn("must be new", rerun.stderr)
        self.assertEqual(rerun.stdout, "")
        self.assertEqual(original_bytes,
                         {path.relative_to(output): path.read_bytes() for path in output.rglob("*.json")})


if __name__ == "__main__":
    unittest.main()
