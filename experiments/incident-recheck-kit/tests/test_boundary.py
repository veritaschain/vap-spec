"""Independent cross-layer checks for the fixed portable recheck envelope.

Narrow ZIP grammar tests belong to test_archive; worker transport and exact
result-schema tests belong to test_runner. These tests exercise the trust
boundary between a structurally valid archive and its executable source.
"""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from incident_recheck import runner
from incident_recheck.archive import build_archive, inspect_archive
from incident_recheck.layout import (
    KIT_PREFIX, PILOTS, SNAPSHOT_ID, KitError, collect_payload, json_bytes,
    sha256, strict_json,
)


class BoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original_payload = collect_payload()

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.work = Path(self.directory.name)

    def archive(self, payload=None, name="kit.zip"):
        path = self.work / name
        report = build_archive(path, self.original_payload if payload is None else payload)
        return path, report["archive_sha256"]

    def assert_rejected_before_worker(self, payload, name):
        path, expected = self.archive(payload, name)
        # Give the attacker a consistent ZIP, manifest and external hash. The
        # separate trusted source/capture binding must still refuse the content.
        inspected = inspect_archive(path, expected)
        self.assertEqual(inspected["files"], payload)
        with patch.object(runner, "run_worker") as worker, patch.object(runner, "TemporaryDirectory") as staging:
            with self.assertRaises(KitError):
                runner.recheck_archive(path, expected)
            worker.assert_not_called()
            staging.assert_not_called()

    def test_rewritten_verifier_and_internal_source_hash_never_execute(self):
        payload = dict(self.original_payload)
        lock_name = "source/" + KIT_PREFIX + "source-lock.json"
        lock = strict_json(payload[lock_name])
        relative = next(name for name in lock["files"] if name.endswith("/incident_assessor/assess.py"))
        source_name = "source/" + relative
        marker = self.work / "verifier-executed.txt"
        injected = (
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('untrusted verifier executed')\n"
        ).encode("utf-8")
        payload[source_name] = payload[source_name] + b"\n" + injected
        lock["files"][relative] = sha256(payload[source_name])
        payload[lock_name] = json_bytes(lock)
        self.assert_rejected_before_worker(payload, "rewritten-source.zip")
        self.assertFalse(marker.exists())

    def test_rewritten_packaged_worker_never_runs_even_with_valid_manifest(self):
        payload = dict(self.original_payload)
        name = "source/" + KIT_PREFIX + "incident_recheck/worker.py"
        marker = self.work / "worker-executed.txt"
        payload[name] = (
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('untrusted worker executed')\n"
            "print('{\"verified_exports\":53,\"actions_reexecuted\":false}')\n"
        ).encode("utf-8")
        self.assert_rejected_before_worker(payload, "rewritten-worker.zip")
        self.assertFalse(marker.exists())

    def test_original_capture_bytes_cannot_be_reserialized_and_relabelled(self):
        name = "evidence/upload/cases/UL-01.json"
        original = self.original_payload[name]
        changed = original + b" \n"
        # The existing upload case digest is over parsed JCS, so these values
        # remain identical. The kit's original-byte commitment must distinguish.
        self.assertEqual(strict_json(original), strict_json(changed))
        self.assertNotEqual(sha256(original), sha256(changed))
        for rewrite_provenance in (False, True):
            with self.subTest(rewrite_provenance=rewrite_provenance):
                payload = dict(self.original_payload)
                payload[name] = changed
                if rewrite_provenance:
                    provenance = strict_json(payload["evidence/provenance.json"])
                    provenance["pilots"]["upload"]["files"]["cases/UL-01.json"] = {
                        "sha256": sha256(changed), "byte_length": len(changed),
                    }
                    payload["evidence/provenance.json"] = json_bytes(provenance)
                self.assert_rejected_before_worker(payload, f"changed-capture-{rewrite_provenance}.zip")

    def test_rewritten_capture_provenance_and_lock_do_not_create_a_new_origin(self):
        payload = dict(self.original_payload)
        provenance = strict_json(payload["evidence/provenance.json"])
        original_run = provenance["pilots"]["upload"]["workflow_run_id"]
        provenance["pilots"]["upload"]["workflow_run_id"] = original_run + 1
        provenance["pilots"]["upload"]["workflow_run_url"] = (
            f"https://github.com/veritaschain/vap-spec/actions/runs/{original_run + 1}"
        )
        payload["evidence/provenance.json"] = json_bytes(provenance)
        lock_name = "source/" + KIT_PREFIX + "source-lock.json"
        lock = strict_json(payload[lock_name])
        lock["provenance_sha256"] = sha256(payload["evidence/provenance.json"])
        payload[lock_name] = json_bytes(lock)
        self.assert_rejected_before_worker(payload, "rewritten-origin.zip")

    def test_complete_recheck_ignores_hostile_pythonpath_and_keeps_limited_claims(self):
        path, expected = self.archive()
        poison = self.work / "pythonpath"
        poison.mkdir()
        marker = self.work / "pythonpath-executed.txt"
        injected = (
            "from pathlib import Path\n"
            f"Path({str(marker)!r}).write_text('untrusted Python path executed')\n"
            "raise RuntimeError('Untrusted path must not enter a recheck worker')\n"
        )
        for name in ("sitecustomize.py", "rfc8785.py", "cryptography.py"):
            (poison / name).write_text(injected, encoding="utf-8")
        with patch.dict(os.environ, {"PYTHONPATH": str(poison), "PYTHONSTARTUP": str(poison / "sitecustomize.py")}):
            result = runner.recheck_archive(path, expected)
        self.assertFalse(marker.exists())
        self.assertEqual(result["format"], "incident-recheck-report/0.1")
        self.assertEqual(result["snapshot_id"], SNAPSHOT_ID)
        self.assertEqual(result["verified_exports"], 53)
        self.assertIs(result["actions_reexecuted"], False)
        self.assertEqual(result["independent_reproduction"], "NOT_ESTABLISHED")
        self.assertEqual(result["conformance"], "NOT_ASSESSED")
        self.assertEqual(result["dependency_scope"], "PINNED_VERSIONS_NOT_HERMETIC")
        self.assertEqual([item["pilot"] for item in result["pilots"]], list(PILOTS))
        self.assertEqual([item["verified_exports"] for item in result["pilots"]], [17, 18, 18])
        for item in result["pilots"]:
            self.assertIs(item["actions_reexecuted"], False)
            self.assertEqual(item["guard"], "PYTHON_AUDIT_EVENTS")
            self.assertEqual(item["source_sha256"], PILOTS[item["pilot"]]["source_sha256"])

    def test_audit_guard_denies_representative_actions_and_retains_denials(self):
        victim = self.work / "existing.txt"
        victim.write_text("UNCHANGED SYNTHETIC CONTENT", encoding="utf-8")
        marker = self.work / "created.txt"
        renamed = self.work / "renamed.txt"
        new_directory = self.work / "created-directory"
        mode = victim.stat().st_mode
        script = "\n".join((
            "import json, os, pathlib, socket, subprocess, sys",
            f"sys.path.insert(0, {str(ROOT)!r})",
            "from incident_recheck.worker import install_audit_guard",
            f"victim = pathlib.Path({str(victim)!r})",
            f"marker = pathlib.Path({str(marker)!r})",
            f"renamed = pathlib.Path({str(renamed)!r})",
            f"new_directory = pathlib.Path({str(new_directory)!r})",
            "events = install_audit_guard()",
            "actions = {",
            " 'write': lambda: marker.open('w'),",
            " 'open_update': lambda: victim.open('r+'),",
            " 'os_open': lambda: os.open(marker, os.O_WRONLY | os.O_CREAT, 0o600),",
            " 'unlink': lambda: victim.unlink(),",
            " 'rename': lambda: victim.rename(renamed),",
            " 'mkdir': lambda: new_directory.mkdir(),",
            " 'chmod': lambda: victim.chmod(0o400),",
            " 'socket': lambda: socket.socket(),",
            " 'process': lambda: subprocess.run([sys.executable, '-c', 'raise SystemExit(0)'], check=True),",
            "}",
            "denied = []",
            "for label, action in actions.items():",
            " try:",
            "  value = action()",
            " except PermissionError:",
            "  denied.append(label)",
            " else:",
            "  if hasattr(value, 'close'): value.close()",
            "  if type(value) is int: os.close(value)",
            "print(json.dumps({'denied': denied, 'event_count': len(events), 'readback': victim.read_text()}))",
        ))
        result = subprocess.run([sys.executable, "-I", "-B", "-c", script],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(set(data["denied"]), {
            "write", "open_update", "os_open", "unlink", "rename", "mkdir", "chmod", "socket", "process",
        })
        self.assertGreaterEqual(data["event_count"], len(data["denied"]))
        self.assertEqual(data["readback"], "UNCHANGED SYNTHETIC CONTENT")
        self.assertEqual(victim.read_text(), "UNCHANGED SYNTHETIC CONTENT")
        self.assertEqual(victim.stat().st_mode, mode)
        self.assertFalse(marker.exists())
        self.assertFalse(renamed.exists())
        self.assertFalse(new_directory.exists())


if __name__ == "__main__":
    unittest.main()
