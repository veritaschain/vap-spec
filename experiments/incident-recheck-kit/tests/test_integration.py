"""The public CLI and portable source/evidence topology must work end to end."""

from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

from incident_recheck.archive import build_archive, inspect_archive
from incident_recheck.layout import ROOT, REPO_ROOT, KitError, collect_payload, strict_json


class IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = collect_payload()

    def command(self, args, cwd=ROOT):
        completed = subprocess.run([sys.executable, "-B", "-m", "incident_recheck", *args],
                                   cwd=cwd, capture_output=True, timeout=45, check=False)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode(errors="replace"))
        self.assertEqual(completed.stderr, b"")
        return strict_json(completed.stdout)

    def test_json_rejects_overflow_nonfinite_duplicate_and_invalid_unicode(self):
        for raw in (b'{"value":1e999}', b'{"value":-1e999}', b'{"value":NaN}',
                    b'{"value":Infinity}', b'{"value":1,"value":2}', b'"\\ud800"'):
            with self.subTest(raw=raw), self.assertRaises(KitError):
                strict_json(raw)

    def test_cli_build_inspect_and_verify_agree(self):
        with TemporaryDirectory() as temporary:
            archive = Path(temporary) / "kit.zip"
            built = self.command(["build", "--output", str(archive)])
            common = ["--archive", str(archive), "--expected-sha256", built["archive_sha256"]]
            inspected = self.command(["inspect", *common])
            verified = self.command(["verify", *common])
            self.assertEqual(verified, built["report"])
            self.assertEqual(verified["verified_exports"], 53)
            self.assertIs(verified["actions_reexecuted"], False)
            self.assertEqual(inspected["file_count"], len(self.payload))
            self.assertEqual(inspected["source_binding"], "NOT_CHECKED")
            self.assertIs(inspected["exports_rechecked"], False)

    def test_cli_failure_emits_no_success_report_and_does_not_overwrite(self):
        with TemporaryDirectory() as temporary:
            archive = Path(temporary) / "kit.zip"
            build_archive(archive, self.payload)
            original = archive.read_bytes()
            for args in (["inspect", "--archive", str(archive), "--expected-sha256", "0" * 64],
                         ["build", "--output", str(archive)]):
                result = subprocess.run([sys.executable, "-B", "-m", "incident_recheck", *args],
                                        cwd=ROOT, capture_output=True, timeout=45, check=False)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, b"")
                self.assertIn(b"Incident recheck failed:", result.stderr)
                self.assertEqual(archive.read_bytes(), original)

    def test_standalone_payload_rechecks_and_rebuilds_identical_bytes(self):
        with TemporaryDirectory() as temporary:
            base = Path(temporary)
            archive = base / "original.zip"
            measurement = build_archive(archive, self.payload)
            # Test-only staging occurs after trusted inspection. Production has
            # no caller-selected extraction command or extractall operation.
            inspected = inspect_archive(archive, measurement["archive_sha256"])
            standalone = base / "standalone"
            for relative, raw in inspected["files"].items():
                path = standalone / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(raw)
            script = r'''
import os, pathlib, runpy, sys
source, original, action, archive, digest, output = sys.argv[1:]
source = pathlib.Path(source).resolve()
original = pathlib.Path(original).resolve()
def refuse_original(event, args):
    if event not in {"open", "os.listdir", "os.scandir"} or not args:
        return
    path = args[0]
    if isinstance(path, (str, bytes, os.PathLike)):
        resolved = pathlib.Path(os.fsdecode(path)).absolute()
        if resolved == original or original in resolved.parents:
            raise RuntimeError("Standalone command accessed original checkout")
sys.addaudithook(refuse_original)
sys.path.insert(0, str(source / "experiments/incident-recheck-kit"))
from incident_recheck import layout
assert layout.REPO_ROOT == source
assert layout.SNAPSHOT_ROOT == source.parent / "evidence"
sys.argv = ["incident_recheck", action]
if action == "verify":
    sys.argv += ["--archive", archive, "--expected-sha256", digest]
else:
    sys.argv += ["--output", output]
runpy.run_module("incident_recheck", run_name="__main__")
'''
            rebuilt = base / "rebuilt.zip"
            reports = {}
            for action in ("verify", "build"):
                result = subprocess.run(
                    [sys.executable, "-I", "-B", "-c", script, str(standalone / "source"),
                     str(REPO_ROOT), action, str(archive), measurement["archive_sha256"], str(rebuilt)],
                    cwd=standalone, capture_output=True, timeout=45, check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
                self.assertEqual(result.stderr, b"")
                reports[action] = strict_json(result.stdout)
            self.assertEqual(reports["verify"]["verified_exports"], 53)
            self.assertEqual(reports["build"]["report"], reports["verify"])
            self.assertEqual(rebuilt.read_bytes(), archive.read_bytes())


if __name__ == "__main__":
    unittest.main()
