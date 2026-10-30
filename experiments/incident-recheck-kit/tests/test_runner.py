"""Process-boundary tests and one real offline recheck of the fixed CI captures."""

from copy import deepcopy
from importlib import metadata
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from incident_recheck import runner, worker
from incident_recheck.archive import build_archive
from incident_recheck.layout import (PILOTS, REPO_ROOT, SNAPSHOT_ROOT, KitError,
                                     collect_payload, json_bytes)


def worker_result(pilot="upload"):
    return {
        "format": "incident-recheck-worker/0.1", "pilot": pilot,
        "verified_exports": PILOTS[pilot]["count"], "actions_reexecuted": False,
        "source_sha256": PILOTS[pilot]["source_sha256"], "dependencies": deepcopy(worker.DEPENDENCIES),
        "guard": "PYTHON_AUDIT_EVENTS",
    }


class RunnerTests(unittest.TestCase):
    def run_protocol_child(self, output, *, stderr=b"", exit_code=0, environment=None):
        """Exercise pipe/JSON handling with a diagnostic child, not a verifier."""
        real_popen = subprocess.Popen
        calls, children = [], []
        code = "import os; os.write(1, " + repr(output) + "); os.write(2, " + repr(stderr) + "); raise SystemExit(" + repr(exit_code) + ")"

        def start(command, **kwargs):
            calls.append((command, kwargs))
            process = real_popen([sys.executable, "-I", "-B", "-c", code], **kwargs)
            children.append(process)
            return process

        with patch.object(runner, "_validate_worker_tree"), \
                patch.object(runner.subprocess, "Popen", side_effect=start), \
                patch.dict(os.environ, environment or {}):
            result = runner.run_worker(REPO_ROOT, SNAPSHOT_ROOT, "upload")
        for process in children:
            self.assertIsNotNone(process.poll())
            self.assertTrue(process.stdout.closed)
            self.assertTrue(process.stderr.closed)
        return result, calls

    def test_fixed_invocation_is_isolated_and_ignores_python_environment_paths(self):
        result, calls = self.run_protocol_child(json_bytes(worker_result()), environment={
            "PYTHONPATH": "/not-a-verifier-source", "PYTHONHOME": "/not-a-python-runtime",
        })
        self.assertEqual(result, worker_result())
        self.assertEqual(len(calls), 1)
        command, options = calls[0]
        self.assertEqual(command, [sys.executable, "-I", "-B", str(REPO_ROOT / runner.WORKER_PATH),
                                   str(REPO_ROOT), str(SNAPSHOT_ROOT), "upload"])
        self.assertNotIn("PYTHONPATH", options["env"])
        self.assertNotIn("PYTHONHOME", options["env"])
        self.assertIs(options["close_fds"], True)
        self.assertEqual(options["stdin"], subprocess.DEVNULL)
        self.assertNotIn("shell", options)

    def test_success_looking_or_malformed_zero_exit_worker_output_is_rejected(self):
        mutations = [
            {"actions_reexecuted": True}, {"actions_reexecuted": 0}, {"verified_exports": True},
            {"verified_exports": 18}, {"pilot": "erasure"}, {"source_sha256": "0" * 64},
            {"dependencies": {}}, {"guard": "NOT_INSTALLED"}, {"extra": "ignored?"},
        ]
        raw_cases = [b"success\n", b'"verified 53 cases"\n', b"[]\n", b"", b'{"pilot":"upload","pilot":"upload"}\n']
        for mutation in mutations:
            result = worker_result()
            result.update(mutation)
            raw_cases.append(json_bytes(result))
        missing = worker_result()
        del missing["actions_reexecuted"]
        raw_cases.append(json_bytes(missing))
        raw_cases.append(json_bytes(worker_result()) + b"extra trailing output")
        for raw in raw_cases:
            with self.subTest(raw=raw[:100]), self.assertRaises(KitError):
                self.run_protocol_child(raw)

    def test_nonzero_exit_and_unexpected_stderr_cannot_return_success(self):
        for exit_code in (0, 2):
            with self.subTest(exit_code=exit_code), self.assertRaises(KitError):
                self.run_protocol_child(json_bytes(worker_result()), stderr=b"diagnostic from child\n", exit_code=exit_code)

    def test_incremental_limits_terminate_and_reap_both_output_streams(self):
        real_popen = subprocess.Popen
        for descriptor in (1, 2):
            children = []

            def start(command, **kwargs):
                process = real_popen(command, **kwargs)
                children.append(process)
                return process

            code = f"import os,time; os.write({descriptor}, b'x' * {runner.OUTPUT_LIMIT + 1}); time.sleep(10)"
            with self.subTest(descriptor=descriptor), patch.object(runner.subprocess, "Popen", side_effect=start):
                with self.assertRaisesRegex(KitError, "limit"):
                    runner._capture_child([sys.executable, "-I", "-B", "-c", code], cwd=REPO_ROOT, timeout=2)
            self.assertEqual(len(children), 1)
            self.assertIsNotNone(children[0].poll())
            self.assertTrue(children[0].stdout.closed)
            self.assertTrue(children[0].stderr.closed)

    def test_timeout_reaps_children_even_when_they_close_their_output_pipes(self):
        real_popen = subprocess.Popen
        for close_output in (False, True):
            children = []

            def start(command, **kwargs):
                process = real_popen(command, **kwargs)
                children.append(process)
                return process

            code = "import os,time; " + ("os.close(1); os.close(2); " if close_output else "") + "time.sleep(10)"
            with self.subTest(close_output=close_output), patch.object(runner.subprocess, "Popen", side_effect=start):
                with self.assertRaisesRegex(KitError, "time limit"):
                    runner._capture_child([sys.executable, "-I", "-B", "-c", code], cwd=REPO_ROOT, timeout=0.1)
            self.assertEqual(len(children), 1)
            self.assertIsNotNone(children[0].poll())
            self.assertTrue(children[0].stdout.closed)
            self.assertTrue(children[0].stderr.closed)

    def test_invalid_pilot_and_timeout_are_rejected_before_source_or_process_access(self):
        with patch.object(runner, "_validate_worker_tree") as sources, patch.object(runner, "_capture_child") as start:
            for pilot in ("run-suite", "upload;run", "untrusted.module", None, 1):
                with self.subTest(pilot=pilot), self.assertRaises(KitError):
                    runner.run_worker(REPO_ROOT, SNAPSHOT_ROOT, pilot)
            for timeout in (True, 0, -1, 31, 10 ** 1000, float("nan"), float("inf"), "1"):
                with self.subTest(timeout=timeout), self.assertRaises(KitError):
                    runner.run_worker(REPO_ROOT, SNAPSHOT_ROOT, "upload", timeout=timeout)
            sources.assert_not_called()
            start.assert_not_called()

    def test_dependency_mismatch_missing_metadata_and_loaded_version_fail_clearly(self):
        for problem in ("wrong-distribution", "missing-distribution", "wrong-module"):
            def version(name):
                if name == "pycparser" and problem == "wrong-distribution":
                    return "3.11"
                if name == "rfc8785" and problem == "missing-distribution":
                    raise metadata.PackageNotFoundError(name)
                return worker.DEPENDENCIES[name]

            def module(name):
                return SimpleNamespace(__version__="0.0.0" if problem == "wrong-module" else worker.DEPENDENCIES[name])

            with self.subTest(problem=problem), \
                    patch.object(worker.metadata, "version", side_effect=version), \
                    patch.object(worker.importlib, "import_module", side_effect=module) as imports:
                with self.assertRaisesRegex(ValueError, "dependency|version"):
                    worker._dependency_versions()
                if problem != "wrong-module":
                    imports.assert_not_called()

    def test_real_offline_recheck_verifies_all_53_and_removes_private_staging(self):
        with tempfile.TemporaryDirectory(prefix="kit-runner-test-") as directory:
            archive = Path(directory) / "fixed.zip"
            built = build_archive(archive, collect_payload())
            created = []
            real_temporary_directory = tempfile.TemporaryDirectory

            def temporary(*args, **kwargs):
                result = real_temporary_directory(*args, **kwargs)
                created.append(Path(result.name))
                return result

            with patch.object(runner, "TemporaryDirectory", side_effect=temporary):
                report = runner.recheck_archive(archive, built["archive_sha256"])
            self.assertEqual(report["verified_exports"], 53)
            self.assertEqual([item["pilot"] for item in report["pilots"]], ["upload", "publication", "erasure"])
            self.assertEqual([item["verified_exports"] for item in report["pilots"]], [17, 18, 18])
            self.assertIs(report["actions_reexecuted"], False)
            self.assertEqual(report["independent_reproduction"], "NOT_ESTABLISHED")
            self.assertEqual(report["source_binding"], "MATCHED_TRUSTED_CHECKOUT")
            for item in report["pilots"]:
                self.assertEqual(item, worker_result(item["pilot"]))
            self.assertEqual(len(created), 1)
            self.assertFalse(created[0].exists())

    def test_failed_worker_never_yields_partial_success_and_staging_is_removed(self):
        with tempfile.TemporaryDirectory(prefix="kit-runner-failure-") as directory:
            archive = Path(directory) / "fixed.zip"
            built = build_archive(archive, collect_payload())
            created = []
            real_temporary_directory = tempfile.TemporaryDirectory

            def temporary(*args, **kwargs):
                result = real_temporary_directory(*args, **kwargs)
                created.append(Path(result.name))
                return result

            with patch.object(runner, "TemporaryDirectory", side_effect=temporary), \
                    patch.object(runner, "run_worker", side_effect=[worker_result("upload"), KitError("worker failed")]) as run:
                with self.assertRaisesRegex(KitError, "worker failed"):
                    runner.recheck_archive(archive, built["archive_sha256"])
                self.assertEqual(run.call_count, 2)
            self.assertEqual(len(created), 1)
            self.assertFalse(created[0].exists())


if __name__ == "__main__":
    unittest.main()
