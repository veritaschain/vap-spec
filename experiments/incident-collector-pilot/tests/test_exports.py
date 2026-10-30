"""Offline recheck boundaries exercised against two actual local HTTP captures.

Adversarial variants are test-only modifications, never exported as observations.
Only the early file/source guards use deliberately incomplete envelope fixtures;
they are not substitutes for the separately required complete 18-case suite.
"""

import hashlib
import json
import platform
import sys
import tempfile
import unittest
from copy import deepcopy
from importlib.metadata import version
from pathlib import Path
from unittest.mock import patch

from collector_pilot import ROOT, VERSION
from collector_pilot.exports import (
    check_case, derive_actual, read_json, scope, source_manifest, verify_exports,
)
from collector_pilot.harness import make_keys
from collector_pilot.protocol import (
    InputError, canonical, digest, sign_control, sign_record, utc_now,
    verify_control, verify_receipt, verify_status,
)
from collector_pilot.suite import run_case
from incident_assessor.assess import assess
from upload_pilot.protocol import sign_control as sign_upload_control


def _bytes(value):
    return json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8") + b"\n"


def _refresh(frame):
    frame["trust"]["target_sha256"] = digest(frame["evidence"]["target"])
    frame["assessment"] = assess(frame["evidence"], frame["trust"], allow_synthetic=True)


class ExportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = Path(cls.enterClassContext(tempfile.TemporaryDirectory(prefix="collector-export-tests-")))
        cls.keys = make_keys()
        cls.captures = {}
        # Fresh test-owned keys permit semantically targeted, validly signed
        # mutations. The unmodified observations still come from real processes.
        with patch("collector_pilot.suite.make_keys", return_value=deepcopy(cls.keys)):
            for case_id in ("CP-01", "CP-04"):
                cls.captures[case_id] = run_case(case_id, cls.directory / case_id)
        cls.catalogue = read_json(ROOT / "acceptance.json")["cases"]

    def capture(self, case_id="CP-01"):
        # JSON round-trip also breaks any in-memory aliasing among saved frames.
        return json.loads(_bytes(self.captures[case_id]))

    def sign(self, body, role, *, record=False, upload=False):
        key = self.keys[role]
        function = sign_record if record else sign_upload_control if upload else sign_control
        return function(body, key["secret"], key["key_id"])

    def test_real_positive_capture_and_lost_ack_reconciliation_are_both_accepted(self):
        expected = {case["id"]: case["expected"] for case in self.catalogue}
        for case_id in ("CP-01", "CP-04"):
            with self.subTest(case=case_id):
                captured = self.capture(case_id)
                before = canonical(captured)
                check_case(captured)
                self.assertEqual(canonical(captured), before)
                for name, value in expected[case_id].items():
                    self.assertEqual(captured["actual"][name], value)
        confirmed = self.captures["CP-01"]["reports"][0]
        self.assertEqual(confirmed["final"]["assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        self.assertEqual(confirmed["postflight"]["assessment"]["assessments"]["observed_action_authorization"], "REVIEW")
        lost = self.captures["CP-04"]
        self.assertIsNone(lost["reports"][0]["collection_receipt"])
        self.assertEqual(lost["collector_snapshot"]["accepted_count"], 1)
        self.assertEqual(lost["reconciliations"][0]["state"], "FOUND")
        self.assertIs(lost["reconciliations"][0]["upload_resumed"], False)
        self.assertEqual(lost["actual"]["payload_attempts"], 0)

    def test_positive_health_cannot_be_removed_changed_or_moved_with_recomputed_assessments(self):
        for mutation in ("missing", "unavailable", "stale"):
            with self.subTest(mutation=mutation):
                case = self.capture()
                report = case["reports"][0]
                for name in ("final", "postflight"):
                    frame = report[name]
                    updated = []
                    for record in frame["evidence"]["records"]:
                        if record["body"]["kind"] != "transfer.collector_health":
                            updated.append(record)
                            continue
                        if mutation == "missing":
                            continue
                        body = deepcopy(record["body"])
                        if mutation == "unavailable":
                            body["data"].update(available=False, durable_acknowledged=False)
                        else:
                            body["data"]["checked_at"] = report["admission"]["evidence"]["target"]["operation_at"]
                        updated.append(self.sign(body, "gateway", record=True))
                    frame["evidence"]["records"] = updated
                    _refresh(frame)
                    self.assertEqual(frame["assessment"]["evidence_integrity"], "VERIFIED_UNDER_EVALUATOR_TRUST")
                case["actual"] = derive_actual(case)
                with self.assertRaisesRegex(InputError, "final authorization|Health was backdated"):
                    check_case(case)

    def _collector_optional_variant(self):
        """Rebind all downstream evidence so failure is not a stale signature."""
        case = self.capture()
        report = case["reports"][0]
        policy = next(record for record in report["admission"]["evidence"]["records"]
                      if record["body"]["kind"] == "transfer.policy")
        optional = {**policy["body"]["data"], "require_collector": False}
        new_policy_digest = digest(optional)
        for name in ("admission", "final", "postflight"):
            frame = report[name]
            frame["evidence"]["target"]["subject"]["policy_sha256"] = new_policy_digest
            records = []
            for record in frame["evidence"]["records"]:
                body = deepcopy(record["body"])
                body["binding"]["policy_sha256"] = new_policy_digest
                role = "policy" if body["kind"] == "transfer.policy" else "gateway"
                if role == "policy":
                    body["data"] = deepcopy(optional)
                records.append(self.sign(body, role, record=True))
            frame["evidence"]["records"] = records
            _refresh(frame)
        subject = report["admission"]["evidence"]["target"]["subject"]
        permit = next(record for record in report["admission"]["evidence"]["records"]
                      if record["body"]["kind"] == "transfer.decision")
        body = deepcopy(report["collection_intent"]["body"])
        body.update(subject_sha256=digest(subject), policy_sha256=new_policy_digest, decision_sha256=digest(permit))
        report["collection_intent"] = self.sign(body, "gateway")
        request_digest = digest(report["collection_intent"])
        body = {**report["collection_receipt"]["body"], "request_sha256": request_digest}
        report["collection_receipt"] = self.sign(body, "collector")
        report["collection_exchange"]["response"] = deepcopy(report["collection_receipt"])
        body = {**report["status_query"]["body"], "request_sha256": request_digest}
        report["status_query"] = self.sign(body, "gateway")
        body = {**report["collection_status"]["body"], "request_sha256": request_digest,
                "query_sha256": digest(report["status_query"]), "receipt": deepcopy(report["collection_receipt"])}
        report["collection_status"] = self.sign(body, "collector")
        report["status_exchange"]["response"] = deepcopy(report["collection_status"])
        row = case["collector_snapshot"]["rows"][0]
        row.update(request_sha256=request_digest, intent=deepcopy(report["collection_intent"]),
                   receipt=deepcopy(report["collection_receipt"]))
        body = {**report["dispatch_intent"]["body"], "subject_sha256": digest(subject)}
        report["dispatch_intent"] = self.sign(body, "gateway", upload=True)
        body = {**report["payload_receipt"]["body"], "subject_sha256": digest(subject)}
        report["payload_receipt"] = self.sign(body, "receiver", upload=True)
        report["payload_transport"]["receipt"] = deepcopy(report["payload_receipt"])
        case["receiver_snapshot"]["rows"][0].update(
            subject_sha256=digest(subject), receipt=deepcopy(report["payload_receipt"]))
        case["actual"] = derive_actual(case)
        return case

    def test_validly_resigned_optional_collector_policy_cannot_pass_the_required_prerequisite(self):
        case = self._collector_optional_variant()
        report = case["reports"][0]
        for name in ("admission", "final", "postflight"):
            self.assertEqual(report[name]["assessment"]["evidence_integrity"], "VERIFIED_UNDER_EVALUATOR_TRUST")
        # Under the generic assessor this optional policy allows the action.
        # This dedicated pilot must still refuse its stronger prerequisite claim.
        self.assertEqual(report["admission"]["assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        self.assertEqual(report["final"]["assessment"]["assessments"]["transfer_authorization"], "ALLOW")
        gateway, collector = self.keys["gateway"], self.keys["collector"]
        verify_control(report["collection_intent"], gateway["public"], gateway["key_id"], "collection_intent")
        verify_receipt(report["collection_receipt"], report["collection_intent"], collector["public"],
                       collector["key_id"], report["collection_exchange"]["completed_at"])
        verify_status(report["collection_status"], report["status_query"], report["collection_intent"],
                      collector["public"], collector["key_id"], report["status_exchange"]["completed_at"])
        with self.assertRaisesRegex(InputError, "policy|collector|authorization"):
            check_case(case)

    def guard_fixture(self):
        """A deliberately incomplete envelope for guards before case inspection.

        Only CP-01/04 contain observations. Other case placeholders must never
        pass a full recheck; tests assert the specific earlier guard that fails.
        """
        root = Path(self.enterContext(tempfile.TemporaryDirectory(prefix="collector-export-guards-")))
        public = root / "public"
        (public / "cases").mkdir(parents=True)
        results = []
        for item in self.catalogue:
            original = self.captures.get(item["id"])
            raw = _bytes(original) if original is not None else b"{}\n"
            (public / "cases" / (item["id"] + ".json")).write_bytes(raw)
            results.append({
                "case_id": item["id"], "title": item["title"], "expected": deepcopy(item["expected"]),
                "actual": deepcopy(original["actual"]) if original is not None else {},
                "matched": True, "differences": {}, "file_sha256": hashlib.sha256(raw).hexdigest(),
            })
        sources = source_manifest()
        summary = {
            "format": "collector-pilot-summary/0.1", "implementation_version": VERSION,
            "recorded_at": utc_now(), "scope": scope(), "source_sha256": digest(sources),
            "source_files": sources,
            "toolchain": {"python": sys.version, "platform": platform.platform(),
                          "dependencies": {name: version(name) for name in ("cryptography", "rfc8785", "cffi", "pycparser")}},
            "total": len(self.catalogue), "matched": len(self.catalogue), "results": results,
        }
        return public, summary

    @staticmethod
    def save_summary(public, summary):
        raw = _bytes(summary)
        (public / "summary.json").write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def test_external_summary_digest_is_checked_against_original_raw_bytes(self):
        public, summary = self.guard_fixture()
        original_hash = self.save_summary(public, summary)
        path = public / "summary.json"
        path.write_bytes(path.read_bytes() + b"\n")  # Same JSON, different externally pinned bytes.
        with self.assertRaisesRegex(InputError, "externally supplied expected bytes"):
            verify_exports(public, expected_summary_sha256=original_hash)

    def test_changed_source_inventory_is_rejected_even_with_updated_self_hashes(self):
        for mutation in ("removed", "changed", "added"):
            with self.subTest(mutation=mutation):
                public, summary = self.guard_fixture()
                source = "experiments/incident-evidence-assessor/incident_assessor/transfer.py"
                self.assertIn(source, summary["source_files"])
                if mutation == "removed":
                    del summary["source_files"][source]
                elif mutation == "changed":
                    summary["source_files"][source] = "0" * 64
                else:
                    summary["source_files"]["experiments/incident-collector-pilot/collector_pilot/injected.py"] = "0" * 64
                summary["source_sha256"] = digest(summary["source_files"])
                externally_supplied = self.save_summary(public, summary)
                with self.assertRaisesRegex(InputError, "trusted implementation checkout"):
                    verify_exports(public, expected_summary_sha256=externally_supplied)

    def test_fixed_expectations_cannot_be_replaced_by_rehashed_summary_claims(self):
        public, summary = self.guard_fixture()
        self.assertEqual(summary["results"][0]["case_id"], "CP-01")
        summary["results"][0]["expected"]["collector_rows"] = 0
        changed_hash = self.save_summary(public, summary)
        with self.assertRaisesRegex(InputError, "fixed local catalogue"):
            verify_exports(public, expected_summary_sha256=changed_hash)

    def test_public_file_inventory_rejects_extra_or_missing_members_before_case_checks(self):
        for mutation in ("extra_root", "extra_case", "missing_case"):
            with self.subTest(mutation=mutation):
                public, summary = self.guard_fixture()
                expected_hash = self.save_summary(public, summary)
                if mutation == "extra_root":
                    (public / "unlisted.json").write_bytes(b"{}\n")
                elif mutation == "extra_case":
                    (public / "cases" / "CP-99.json").write_bytes(b"{}\n")
                else:
                    (public / "cases" / "CP-18.json").unlink()
                with self.assertRaisesRegex(InputError, "export inventory|unexpected case file"):
                    verify_exports(public, expected_summary_sha256=expected_hash)


if __name__ == "__main__":
    unittest.main()
