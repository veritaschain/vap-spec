"""The documented CLI must deliver and rederive the real source-bound report."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
import zipfile

from incident_review.common import ROOT, sha256, strict_json
from incident_review.core import FROZEN_ARCHIVE, verify_toolchain
from test_support import capture_fixture


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = capture_fixture()

    def command(self, *arguments):
        return subprocess.run([sys.executable, "-B", "-m", "incident_review", *arguments],
                              cwd=ROOT, capture_output=True, timeout=90, check=False)

    def test_cli_build_and_exact_rederivation_preserve_frozen_inputs(self):
        original_sources = verify_toolchain()
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            kit, report = base / "kit.zip", base / "report.zip"
            kit.write_bytes(self.capture["archive_bytes"])
            built = self.command("build", "--archive", str(kit), "--expected-sha256", FROZEN_ARCHIVE,
                                 "--output", str(report))
            self.assertEqual(built.returncode, 0, built.stderr.decode(errors="replace"))
            self.assertEqual(built.stderr, b"")
            measurement = strict_json(built.stdout)
            self.assertEqual(measurement["saved_cases_rechecked"], 53)
            self.assertIs(measurement["actions_reexecuted"], False)
            self.assertEqual(measurement["human_review"], "NOT_PERFORMED")
            self.assertEqual(sha256(report.read_bytes()), measurement["report_sha256"])
            verified = self.command("verify", "--archive", str(kit), "--expected-sha256", FROZEN_ARCHIVE,
                                    "--report", str(report), "--expected-report-sha256", measurement["report_sha256"])
            self.assertEqual(verified.returncode, 0, verified.stderr.decode(errors="replace"))
            self.assertEqual(verified.stderr, b"")
            verification = strict_json(verified.stdout)
            self.assertEqual(verification["report_sha256"], measurement["report_sha256"])
            self.assertEqual(verification["saved_cases_rechecked"], 53)
            with zipfile.ZipFile(report) as bundle:
                self.assertEqual(set(bundle.namelist()), {"review.json", "review-en.md", "review-ja.md", "manifest.json"})
                model = strict_json(bundle.read("review.json"))
                self.assertEqual(len(model["cases"]), 53)
                self.assertEqual(model["input"]["archive_sha256"], FROZEN_ARCHIVE)
                self.assertEqual(model["scope"]["observation_truth"], "NOT_ESTABLISHED")
            self.assertEqual(kit.read_bytes(), self.capture["archive_bytes"])
        self.assertEqual(verify_toolchain(), original_sources)

    def test_cli_wrong_input_and_existing_destination_fail_without_success(self):
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            kit, destination = base / "kit.zip", base / "reserved.zip"
            kit.write_bytes(self.capture["archive_bytes"])
            destination.write_bytes(b"caller-owned-existing-file")
            for expected in ("0" * 64, FROZEN_ARCHIVE):
                result = self.command("build", "--archive", str(kit), "--expected-sha256", expected,
                                      "--output", str(destination))
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"Incident review failed:", result.stderr)
                self.assertEqual(destination.read_bytes(), b"caller-owned-existing-file")


if __name__ == "__main__":
    unittest.main()
