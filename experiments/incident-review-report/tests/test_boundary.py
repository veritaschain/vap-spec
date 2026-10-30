"""Independent checks of the report's verification and publication boundary.

Malformed-result injections below are diagnostic test doubles. The original
capture fixture and the forged-bundle rederivation use the unchanged kit's
actual three workers; no upload, publication or erasure action is repeated.
"""

from copy import deepcopy
from io import BytesIO
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from types import ModuleType
import unittest
from unittest.mock import Mock, patch
import zipfile

from incident_review import core
from incident_review.common import ReviewError, json_bytes, sha256, strict_json
from test_support import capture_fixture


class ReportBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = TemporaryDirectory(prefix="review-boundary-fixture-")
        cls.addClassCleanup(cls.temporary.cleanup)
        cls.root = Path(cls.temporary.name)
        cls.captured = capture_fixture()
        cls.lock = core.verify_toolchain()
        cls.archive = cls.root / "original-kit.zip"
        cls.archive.write_bytes(cls.captured["archive_bytes"])
        cls.report = core.generate_report(cls.archive, cls.lock["archive_sha256"])

    def setUp(self):
        temporary = TemporaryDirectory(prefix="review-boundary-")
        self.addCleanup(temporary.cleanup)
        self.work = Path(temporary.name)

    def diagnostic_kit(self, result):
        inspected = Mock(return_value=deepcopy(self.captured["inspected"]))
        if isinstance(result, Exception):
            checked = Mock(side_effect=result)
        else:
            checked = Mock(return_value=result)
        return inspected, checked, deepcopy(self.lock)

    def test_unsuccessful_or_malformed_recheck_cannot_project_or_publish(self):
        from incident_review import delivery, projection

        good = self.captured["recheck"]
        examples = [("failed verifier", ValueError("deliberate verifier refusal")),
                    ("missing result", None)]

        def changed(name, mutate):
            value = deepcopy(good)
            mutate(value)
            examples.append((name, value))

        changed("incomplete total", lambda x: x.update(verified_exports=52))
        changed("float total", lambda x: x.update(verified_exports=53.0))
        changed("integer false flag", lambda x: x.update(actions_reexecuted=0))
        changed("unbound source", lambda x: x.update(source_binding="NOT_CHECKED"))
        changed("other archive", lambda x: x.update(archive_sha256="0" * 64))
        changed("other manifest", lambda x: x.update(manifest_sha256="0" * 64))
        changed("claimed independence", lambda x: x.update(independent_reproduction="ESTABLISHED"))
        changed("claimed conformance", lambda x: x.update(conformance="CONFORMANT"))
        changed("missing worker", lambda x: x["pilots"].pop())
        changed("reordered workers", lambda x: x["pilots"].reverse())
        changed("float worker count", lambda x: x["pilots"][0].update(verified_exports=17.0))
        changed("string worker flag", lambda x: x["pilots"][0].update(actions_reexecuted="false"))
        changed("different worker source", lambda x: x["pilots"][0].update(source_sha256="0" * 64))
        changed("missing guard", lambda x: x["pilots"][0].pop("guard"))
        changed("different dependency", lambda x: x["pilots"][0]["dependencies"].update(rfc8785="0.0.0"))
        changed("extra success assertion", lambda x: x.update(security_verified=True))

        for index, (name, value) in enumerate(examples):
            with self.subTest(name=name):
                destination = self.work / f"refused-{index}.zip"
                with patch.object(core, "_load_kit", return_value=self.diagnostic_kit(value)), \
                        patch.object(projection, "project") as project, \
                        patch.object(delivery, "publish_bundle") as publish:
                    with self.assertRaises(ReviewError):
                        core.build_report(self.archive, self.lock["archive_sha256"], destination)
                    project.assert_not_called()
                    publish.assert_not_called()
                self.assertFalse(destination.exists())

    def test_changed_locked_source_is_rejected_before_kit_import(self):
        checkout = self.work / "checkout"
        for relative in self.lock["files"]:
            destination = checkout / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes((core.REPO_ROOT / relative).read_bytes())

        sentinel = self.work / "untrusted-import-executed"
        poisoned = checkout / "experiments/incident-recheck-kit/incident_recheck/__init__.py"
        poisoned.write_bytes(poisoned.read_bytes() + (
            "\nfrom pathlib import Path as _BoundaryPath\n"
            f"_BoundaryPath({str(sentinel)!r}).write_text('executed')\n"
        ).encode("utf-8"))

        script = """
import json
from pathlib import Path
import sys
sys.path.insert(0, sys.argv[1])
from incident_review import core
from incident_review.common import ReviewError
core.REPO_ROOT = Path(sys.argv[2])
try:
    core.generate_report(Path(sys.argv[3]), sys.argv[4])
except ReviewError:
    print(json.dumps({"refused": True, "kit_imported": any(
        name == "incident_recheck" or name.startswith("incident_recheck.")
        for name in sys.modules)}))
else:
    raise SystemExit("changed frozen source unexpectedly accepted")
"""
        completed = subprocess.run(
            [sys.executable, "-I", "-B", "-c", script, str(core.ROOT),
             str(checkout), str(self.archive), self.lock["archive_sha256"]],
            capture_output=True, check=False, timeout=30,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr.decode("utf-8", "replace"))
        self.assertEqual(completed.stderr, b"")
        self.assertEqual(json.loads(completed.stdout), {"refused": True, "kit_imported": False})
        self.assertFalse(sentinel.exists())

    def test_foreign_cached_kit_modules_are_not_reused(self):
        package = ModuleType("incident_recheck")
        package.__file__ = str(self.work / "foreign/incident_recheck/__init__.py")
        package.__path__ = [str(self.work / "foreign/incident_recheck")]
        archive = ModuleType("incident_recheck.archive")
        archive.__file__ = str(self.work / "foreign/incident_recheck/archive.py")
        archive.inspect_archive = Mock(side_effect=AssertionError("foreign inspect executed"))
        runner = ModuleType("incident_recheck.runner")
        runner.__file__ = str(self.work / "foreign/incident_recheck/runner.py")
        runner.recheck_archive = Mock(side_effect=AssertionError("foreign recheck executed"))

        with patch.dict(sys.modules, {"incident_recheck": package,
                                     "incident_recheck.archive": archive,
                                     "incident_recheck.runner": runner}):
            with self.assertRaises(ReviewError):
                core._load_kit()
        archive.inspect_archive.assert_not_called()
        runner.recheck_archive.assert_not_called()

    def test_projection_cannot_promote_scope_substitute_a_fact_or_drop_a_case(self):
        from incident_review import delivery, projection

        def change_fact(report):
            row = next(row for row in report["cases"] if row["case_id"] == "UL-07")
            for section in row["sections"]:
                for fact in section["facts"]:
                    if fact["source"]["pointer"] == "/actual/states":
                        fact["value"] = ["SECURITY_CONFIRMED"]
                        return
            self.fail("The original unknown-state fact is missing from the reviewed projection")

        changes = [
            ("promoted guarantee", lambda x: x["scope"].update(legal_compliance="COMPLIANT")),
            ("invented observed state", change_fact),
            ("dropped capture", lambda x: x["cases"].pop()),
        ]
        for index, (name, mutate) in enumerate(changes):
            with self.subTest(name=name):
                report = deepcopy(self.report)
                mutate(report)
                destination = self.work / f"projection-{index}.zip"
                with patch.object(core, "_load_kit", return_value=self.diagnostic_kit(deepcopy(self.captured["recheck"]))), \
                        patch.object(projection, "project", return_value=report), \
                        patch.object(delivery, "publish_bundle") as publish:
                    with self.assertRaises(ReviewError):
                        core.build_report(self.archive, self.lock["archive_sha256"], destination)
                    publish.assert_not_called()
                self.assertFalse(destination.exists())

    def test_rewritten_report_and_its_self_hashes_fail_actual_rederivation(self):
        from incident_review import delivery

        original = delivery.bundle_bytes(self.report)
        with zipfile.ZipFile(BytesIO(original)) as source:
            infos = source.infolist()
            members = {info.filename: source.read(info) for info in infos}
        report = strict_json(members["review.json"])
        report["scope"]["legal_compliance"] = "COMPLIANT"
        report["scope"]["human_review"] = "PERFORMED"
        members["review.json"] = json_bytes(report)
        members["review-en.md"] += b"\nSecurity and universal erasure confirmed.\n"
        members["review-ja.md"] += "\n安全性と完全消去を確認しました。\n".encode("utf-8")
        manifest = strict_json(members["manifest.json"])
        for entry in manifest["entries"]:
            entry["sha256"] = sha256(members[entry["path"]])
            entry["byte_length"] = len(members[entry["path"]])
        members["manifest.json"] = json_bytes(manifest)
        output = BytesIO()
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED) as destination:
            for info in infos:
                destination.writestr(info, members[info.filename])
        forged = output.getvalue()
        path = self.work / "rewritten-report.zip"
        path.write_bytes(forged)

        # The supplied candidate digest and every rewritten internal member hash
        # are self-consistent. Only rederivation from the frozen source is trusted.
        self.assertEqual(delivery.read_bundle(path, sha256(forged)), forged)
        with zipfile.ZipFile(BytesIO(forged)) as candidate:
            for entry in strict_json(candidate.read("manifest.json"))["entries"]:
                raw = candidate.read(entry["path"])
                self.assertEqual(entry["sha256"], sha256(raw))
                self.assertEqual(entry["byte_length"], len(raw))
        with self.assertRaises(ReviewError):
            core.verify_report(self.archive, self.lock["archive_sha256"], path, sha256(forged))

    def test_wrong_external_report_digest_fails_before_rederivation(self):
        from incident_review import delivery

        path = self.work / "otherwise-valid-report.zip"
        path.write_bytes(delivery.bundle_bytes(self.report))
        with patch.object(core, "generate_report") as generate:
            with self.assertRaises(ReviewError):
                core.verify_report(self.archive, self.lock["archive_sha256"], path, "0" * 64)
            generate.assert_not_called()

    def test_source_drift_before_publication_exposes_no_report(self):
        from incident_review import delivery

        drifted = deepcopy(self.report["reporter"])
        drifted["source_sha256"] = "0" * 64
        destination = self.work / "source-drift.zip"
        with patch.object(core, "generate_report", return_value=deepcopy(self.report)), \
                patch.object(core, "source_identity", return_value=drifted), \
                patch.object(delivery, "publish_bundle") as publish:
            with self.assertRaises(ReviewError):
                core.build_report(self.archive, self.lock["archive_sha256"], destination)
            publish.assert_not_called()
        self.assertFalse(destination.exists())

    def test_complete_real_report_keeps_counts_separate_from_operational_outcomes(self):
        self.assertEqual(self.report["counts"], {
            "saved_cases_rechecked": 53,
            "scenario_expectations_matched": 53,
            "per_pilot": {"upload": 17, "publication": 18, "erasure": 18},
        })
        self.assertEqual(self.report["scope"], {
            "actions_reexecuted": False,
            "observation_truth": "NOT_ESTABLISHED",
            "independent_reproduction": "NOT_ESTABLISHED",
            "human_review": "NOT_PERFORMED",
            "conformance": "NOT_ASSESSED",
            "legal_compliance": "NOT_ASSESSED",
            "dependency_scope": "PINNED_VERSIONS_NOT_HERMETIC",
        })
        self.assertTrue(all(row["expectation"]["matched"]["value"] is True
                            for row in self.report["cases"]))
        row = next(row for row in self.report["cases"] if row["case_id"] == "UL-07")
        states = [fact["value"] for section in row["sections"] for fact in section["facts"]
                  if fact["source"]["pointer"] == "/actual/states"]
        self.assertEqual(len(states), 1)
        self.assertIn("OUTCOME_UNKNOWN", states[0])


if __name__ == "__main__":
    unittest.main()
