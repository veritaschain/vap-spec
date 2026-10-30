"""Independent publication boundaries, using real local files and fresh test keys.

Reviewer and assistance operations are synthetic. These tests establish neither
real human inspection nor AI origin, external publication, or complete history.
"""

import tempfile
import unittest
from copy import deepcopy
from datetime import timedelta
from pathlib import Path

from publication_pilot.editor import Editor, verify_snapshot
from publication_pilot.gate import Gate, GateConfig, verify_report
from publication_pilot.harness import approve, iso, make_case, make_keys, prepare_candidate
from publication_pilot.protocol import canonical, digest, sha256_bytes, sign_message, sign_record, timestamp, utc_now, InputError
from publication_pilot.store import LocalPublisher


def publisher(directory, case, *, key=None, destination=None, clock=utc_now):
    key = case["keys"]["publisher"] if key is None else key
    return LocalPublisher(Path(directory) / "publication", destination or case["config"].route["provider_id"],
                          key["secret"], key["key_id"], clock=clock)


class BoundaryTests(unittest.TestCase):
    def assert_blocked(self, case, directory):
        store = publisher(directory, case)
        report = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], store)
        self.assertEqual(report["state"], "BLOCKED_WITHOUT_PUBLICATION")
        self.assertFalse(report["attempted"])
        self.assertEqual(store.inspect()["visible_count"], 0)
        return report

    def test_exact_local_output_keeps_core_review_and_does_not_export_secrets(self):
        with tempfile.TemporaryDirectory() as directory:
            case = make_case()
            store = publisher(directory, case)
            report = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], store)
            self.assertEqual(report["state"], "LOCAL_OUTPUT_CONFIRMED")
            self.assertTrue(report["attempted"])
            name = report["receipt"]["body"]["visible_name"]
            actual = (store.visible_root / name).read_bytes()
            self.assertEqual(actual, case["candidate"]["html"].encode("utf-8"))
            self.assertEqual(sha256_bytes(actual), report["receipt"]["body"]["artifact_sha256"])
            self.assertEqual(len(actual), report["receipt"]["body"]["byte_length"])
            self.assertIn(b"&lt;script&gt;", actual)
            self.assertNotIn(b"<script>", actual)
            self.assertTrue(verify_report(case["candidate"], case["trust"], case["approval"], report, case["config"]))
            for frame in (report["preflight"], report["final_gate"]):
                assessments = frame["assessor_frame"]["report"]["assessments"]
                self.assertEqual(assessments["publication_action"], "REVIEW")
                self.assertEqual(assessments["activity_completeness"], "UNKNOWN")
                self.assertEqual(assessments["disclosure_assessment"], "REQUIRES_CONTENT_REVIEW")
                self.assertEqual(assessments["acceptance_status"], "UNKNOWN")
                kinds = {r["body"]["kind"] for r in frame["assessor_frame"]["evidence"]["records"]}
                self.assertFalse({"publication_dispatch", "publication_receipt"} & kinds)
            public = canonical({"candidate": case["candidate"], "trust": case["trust"],
                                "approval": case["approval"], "config": case["config"].export(), "report": report})
            for role, key in case["keys"].items():
                with self.subTest(role=role):
                    self.assertFalse(key["secret"].encode() in public, "Private key escaped into a public export")

    def test_changed_artifact_stale_approval_and_removed_disclosure_do_not_publish(self):
        for variant in ("changed-html", "new-revision-old-approval", "omitted-session-disclosure"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                case = make_case()
                if variant == "changed-html":
                    case["candidate"]["html"] += "<!-- unapproved change -->"
                elif variant == "new-revision-old-approval":
                    subject = case["candidate"]["evidence"]["target"]["subject"]
                    evaluation_id = case["candidate"]["evidence"]["evaluation_id"]
                    case["editor"].set_block("paragraph-1", "A different final paragraph", activity="manual_edit")
                    candidate, trust, config = prepare_candidate(
                        case["editor"], case["keys"], request_id=subject["request_id"],
                        evaluation_id=evaluation_id, policy=case["policy"])
                    case.update(candidate=candidate, trust=trust, config=config)
                else:
                    candidate, trust, config = prepare_candidate(
                        case["editor"], case["keys"], policy=case["policy"], disclosure_activities=[])
                    case.update(candidate=candidate, trust=trust, config=config,
                                approval=approve(candidate, case["keys"]))
                self.assert_blocked(case, directory)

    def test_controller_pins_key_metadata_policy_and_publisher_identity(self):
        for variant in ("role", "key-validity", "issuer", "policy-version", "publisher-key", "publisher-id"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                case = make_case()
                reviewer = case["keys"]["reviewer"]["key_id"]
                if variant == "role":
                    case["trust"]["keys"][reviewer]["roles"].append("policy")
                elif variant == "key-validity":
                    case["trust"]["keys"][reviewer]["not_after"] = "2100-01-01T00:00:00Z"
                elif variant == "issuer":
                    case["trust"]["keys"][reviewer]["issuer"] = "substituted-reviewer"
                elif variant == "policy-version":
                    values = case["config"].export()
                    values["policy_version"] = "other-version"
                    case["config"] = GateConfig(**values)
                if variant.startswith("publisher-"):
                    other_key = make_keys()["publisher"] if variant == "publisher-key" else None
                    destination = "another-venue" if variant == "publisher-id" else None
                    store = publisher(directory, case, key=other_key, destination=destination)
                    report = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], store)
                    self.assertEqual(report["state"], "BLOCKED_WITHOUT_PUBLICATION")
                    self.assertFalse(report["attempted"])
                    self.assertEqual(store.inspect()["visible_count"], 0)
                else:
                    self.assert_blocked(case, directory)

    def test_reviewer_signature_and_assessor_approval_must_agree(self):
        for variant in ("wrong-signer", "different-until", "different-target", "wrong-policy"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                case = make_case()
                reviewer = case["keys"]["reviewer"]
                approval = case["approval"]
                if variant == "wrong-signer":
                    approval["release"] = sign_message(approval["release"]["body"],
                                                        case["keys"]["author"]["secret"], reviewer["key_id"])
                elif variant in {"different-until", "different-target"}:
                    body = deepcopy(approval["evidence"]["body"])
                    if variant == "different-until":
                        body["data"]["valid_until"] = iso(timestamp(body["data"]["valid_until"]) + timedelta(seconds=1))
                    else:
                        body["binding"]["tenant_id"] = "another-tenant"
                    approval["evidence"] = sign_record(body, reviewer["secret"], reviewer["key_id"])
                else:
                    body = deepcopy(approval["release"]["body"])
                    body["policy_sha256"] = "0" * 64
                    approval["release"] = sign_message(body, reviewer["secret"], reviewer["key_id"])
                self.assert_blocked(case, directory)

    def test_prohibited_recorded_activity_survives_replacement_of_exact_output(self):
        with tempfile.TemporaryDirectory() as directory:
            case = make_case(prohibited=("generation",))
            case["editor"].set_block("paragraph-1", "Manually replaced local text; earlier activity remains recorded.",
                                     activity="manual_edit")
            candidate, trust, config = prepare_candidate(case["editor"], case["keys"], policy=case["policy"])
            case.update(candidate=candidate, trust=trust, config=config,
                        approval=approve(candidate, case["keys"]))
            collector = case["keys"]["collector"]
            view = verify_snapshot(candidate["source"], collector["public"], collector["key_id"])
            self.assertEqual(view["adopted"], [])
            self.assertIn("generation", view["observed_activities"])
            report = self.assert_blocked(case, directory)
            assessed = report["preflight"]["assessor_frame"]["report"]["assessments"]
            self.assertEqual(assessed["ai_involvement"], "UNKNOWN")
            self.assertEqual(assessed["publication_action"], "REVIEW")
            self.assertIn("prohibited", report["reason"])

    def test_current_time_expiry_and_collector_signing_interval_are_enforced(self):
        for variant in ("final-approval-expiry", "source-before-key-validity"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as directory:
                if variant == "source-before-key-validity":
                    keys = make_keys()
                    collector = keys["collector"]
                    old = iso(timestamp(collector["not_before"]) - timedelta(seconds=1))
                    editor = Editor("old-source", collector["secret"], collector["key_id"], clock=lambda: old)
                    editor.set_block("paragraph-1", "Synthetic source signed outside its configured key interval.")
                    candidate, trust, config = prepare_candidate(editor, keys)
                    case = {"candidate": candidate, "trust": trust, "config": config,
                            "approval": approve(candidate, keys), "keys": keys}
                    self.assert_blocked(case, directory)
                else:
                    case = make_case()
                    now = [utc_now()]
                    def clock():
                        return now[0]
                    def expire():
                        now[0] = iso(timestamp(case["approval"]["release"]["body"]["valid_until"]) + timedelta(seconds=1))
                    store = publisher(directory, case, clock=clock)
                    report = Gate(case["config"], clock=clock).release(
                        case["candidate"], case["trust"], case["approval"], store, before_publish=expire)
                    self.assertTrue(report["preflight"]["authorized_local_export"])
                    self.assertFalse(report["final_gate"]["authorized_local_export"])
                    self.assertEqual(report["state"], "BLOCKED_WITHOUT_PUBLICATION")
                    self.assertFalse(report["attempted"])
                    self.assertEqual(store.inspect()["visible_count"], 0)

    def test_postpublication_clock_failure_preserves_known_attempt(self):
        with tempfile.TemporaryDirectory() as directory:
            case = make_case()
            store = publisher(directory, case)
            calls = []
            def clock():
                calls.append(None)
                if len(calls) == 3:
                    raise OSError("injected postpublication clock failure")
                return utc_now()
            report = Gate(case["config"], clock=clock).release(
                case["candidate"], case["trust"], case["approval"], store)
            self.assertEqual(store.inspect()["visible_count"], 1)
            self.assertEqual(report["state"], "OUTCOME_UNKNOWN")
            self.assertTrue(report["attempted"])
            self.assertIsNone(report["receipt"])
            self.assertTrue(report["publication"]["attempted"])

    def test_validly_signed_receipts_cannot_change_scope_types_or_time(self):
        with tempfile.TemporaryDirectory() as directory:
            case = make_case()
            store = publisher(directory, case)
            report = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], store)
            self.assertEqual(report["state"], "LOCAL_OUTPUT_CONFIRMED")
            changes = (("request_id", "another-request"), ("fingerprint", "0" * 64),
                       ("artifact_sha256", "0" * 64), ("disclosure_sha256", "0" * 64),
                       ("destination_id", "another-venue"), ("byte_length", True),
                       ("visible_name", "0" * 64 + ".html"),
                       ("observed_at", "2000-01-01T00:00:00Z"),
                       ("observed_at", "2100-01-01T00:00:00Z"), ("approved", True))
            key = case["keys"]["publisher"]
            for field, value in changes:
                with self.subTest(field=field, value=value):
                    changed = deepcopy(report)
                    body = deepcopy(changed["receipt"]["body"])
                    body[field] = value
                    envelope = sign_message(body, key["secret"], key["key_id"])
                    changed["receipt"] = deepcopy(envelope)
                    changed["publication"]["receipt"] = deepcopy(envelope)
                    with self.assertRaises(InputError):
                        verify_report(case["candidate"], case["trust"], case["approval"], changed, case["config"])

    def test_saved_report_cannot_hide_or_invent_publication_observations(self):
        with tempfile.TemporaryDirectory() as directory:
            case = make_case()
            store = publisher(directory, case)
            report = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], store)
            self.assertEqual(report["state"], "LOCAL_OUTPUT_CONFIRMED")
            self.assertTrue(verify_report(case["candidate"], case["trust"], case["approval"], report, case["config"]))
            variants = []
            hidden = deepcopy(report)
            hidden.update(state="BLOCKED_WITHOUT_PUBLICATION", attempted=False, receipt=None, final_gate=None)
            variants.append(("hidden-attempt", hidden))
            false_attempt = deepcopy(report)
            false_attempt["publication"]["attempted"] = False
            variants.append(("inner-attempt", false_attempt))
            uncommitted = deepcopy(report)
            uncommitted["publication"]["journal_state"] = "publication_intent"
            variants.append(("uncommitted-result", uncommitted))
            wrong_name = deepcopy(report)
            wrong_name["publication"]["visible_name"] = "0" * 64 + ".html"
            variants.append(("inconsistent-name", wrong_name))
            missing = deepcopy(report)
            missing["preflight"] = None
            variants.append(("missing-preflight", missing))
            denied_final = deepcopy(report)
            later = iso(timestamp(case["approval"]["release"]["body"]["valid_until"]) + timedelta(seconds=1))
            denied_final["final_gate"] = Gate(case["config"]).check(
                case["candidate"], case["trust"], case["approval"], at=later)
            denied_final["post_at"] = later
            variants.append(("recomputed-denied-final", denied_final))
            for name, changed in variants:
                with self.subTest(name=name), self.assertRaises(InputError):
                    verify_report(case["candidate"], case["trust"], case["approval"], changed, case["config"])

    def test_import_only_and_missing_approval_do_not_become_origin_claims(self):
        with tempfile.TemporaryDirectory() as directory:
            case = make_case(activity=None)
            store = publisher(directory, case)
            report = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], store)
            self.assertEqual(report["state"], "LOCAL_OUTPUT_CONFIRMED")
            assessments = report["preflight"]["assessor_frame"]["report"]["assessments"]
            self.assertEqual(assessments["ai_involvement"], "UNKNOWN")
            self.assertEqual(assessments["activity_completeness"], "UNKNOWN")
            self.assertEqual(assessments["publication_action"], "REVIEW")
        for options in ({"include_approval": False}, {"interpretation": "unresolved"}):
            with self.subTest(options=options), tempfile.TemporaryDirectory() as directory:
                self.assert_blocked(make_case(**options), directory)


if __name__ == "__main__":
    unittest.main()
