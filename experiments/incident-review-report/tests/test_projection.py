"""Projection checks over real owned bytes from the frozen 53-case archive."""

import unittest
from copy import deepcopy

from incident_review.common import json_bytes, resolve_pointer, sha256, strict_json
from incident_review.projection import NOTE_TEXT, _Sources, _frame, project
from test_support import capture_fixture


def nodes(value):
    yield value
    if type(value) is dict:
        for child in value.values():
            yield from nodes(child)
    elif type(value) is list:
        for child in value:
            yield from nodes(child)


def section_values(row, key, operation_index=None):
    sections = [section for section in row["sections"]
                if section["key"] == key and section["operation_index"] == operation_index]
    if len(sections) != 1:
        raise AssertionError("Expected exactly one matching projection section")
    return {fact["name"]: fact["value"] for fact in sections[0]["facts"]}


class ProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.capture = capture_fixture()
        cls.files = cls.capture["files"]
        cls.report = project(cls.files, cls.capture["recheck"], cls.capture["identity"])
        cls.rows = {row["case_id"]: row for row in cls.report["cases"]}
        cls.sources = {file: strict_json(raw) for file, raw in cls.files.items() if file.startswith("evidence/")}

    def original(self, cid):
        pilot = {"UL": "upload", "LP": "publication", "LE": "erasure"}[cid[:2]]
        return self.sources["evidence/" + pilot + "/cases/" + cid + ".json"]

    def frame(self, cid, index, phase):
        frames = [frame for frame in self.rows[cid]["frames"]
                  if frame["operation_index"] == index and frame["phase"] == phase]
        self.assertEqual(len(frames), 1)
        return frames[0]

    def assert_reference(self, source):
        self.assertEqual(set(source), {"file", "sha256", "pointer"})
        self.assertIn(source["file"], self.sources)
        self.assertEqual(source["sha256"], sha256(self.files[source["file"]]))
        self.assertNotIn("*", source["pointer"])
        return resolve_pointer(self.sources[source["file"]], source["pointer"])

    def test_exact_case_inventory_shape_counts_and_scope(self):
        self.assertEqual(set(self.report), {"format", "snapshot_id", "reporter", "input", "recheck", "scope", "counts", "pilots", "cases"})
        expected = [prefix + "-" + str(number).zfill(2) for prefix, count in (("UL", 17), ("LP", 18), ("LE", 18))
                    for number in range(1, count + 1)]
        self.assertEqual([row["case_id"] for row in self.report["cases"]], expected)
        self.assertEqual(self.report["counts"], {"saved_cases_rechecked": 53, "scenario_expectations_matched": 53,
                                                "per_pilot": {"upload": 17, "publication": 18, "erasure": 18}})
        self.assertEqual(self.report["scope"], {
            "actions_reexecuted": False, "observation_truth": "NOT_ESTABLISHED",
            "independent_reproduction": "NOT_ESTABLISHED", "human_review": "NOT_PERFORMED",
            "conformance": "NOT_ASSESSED", "legal_compliance": "NOT_ASSESSED",
            "dependency_scope": "PINNED_VERSIONS_NOT_HERMETIC",
        })
        self.assertEqual(self.report["recheck"], self.capture["recheck"])
        self.assertEqual(self.report["reporter"], self.capture["identity"])
        for row in self.report["cases"]:
            self.assertEqual(set(row), {"pilot", "case_id", "capture_source", "title", "expectation", "sections", "frames", "notes"})
            self.assertEqual(set(row["expectation"]), {"matched", "expected", "actual", "differences"})
            self.assertIs(row["expectation"]["matched"]["value"], True)
            for section in row["sections"]:
                self.assertEqual(set(section), {"key", "operation_index", "facts"})
            for frame in row["frames"]:
                self.assertEqual(set(frame), {"operation_index", "phase", "availability", "absence_reason", "source",
                                             "evidence_integrity", "assessments", "findings"})

    def test_every_fact_and_reference_resolves_to_its_exact_owned_source(self):
        facts, references = 0, 0
        for item in nodes(self.report):
            if type(item) is not dict:
                continue
            if set(item) == {"name", "value", "source"}:
                facts += 1
                original = self.assert_reference(item["source"])
                # Canonical presentation bytes retain bool/int distinctions.
                self.assertEqual(json_bytes(item["value"]), json_bytes(original))
            elif set(item) == {"file", "sha256", "pointer"}:
                references += 1
                self.assert_reference(item)
        self.assertGreater(facts, 1000)
        self.assertGreater(references, facts)

    def test_all_original_core_frames_and_complete_dimensions_are_preserved(self):
        recorded = absent = total = 0
        for row in self.report["cases"]:
            source = self.original(row["case_id"])
            expected = []
            if row["pilot"] == "upload":
                for index, record in enumerate(source["reports"]):
                    expected.extend((index, phase, record[field]) for phase, field in
                                    (("preflight", "preflight_assessment"), ("final_gate", "final_gate_assessment"),
                                     ("postflight", "postflight_assessment")))
            elif row["pilot"] == "publication":
                for index, record in enumerate(source["records"]):
                    for phase in ("preflight", "final_gate"):
                        container = record["report"][phase]
                        core = None if container is None or container["assessor_frame"] is None else container["assessor_frame"]["report"]
                        expected.append((index, phase, core))
            else:
                expected = [(index, "erasure", record["assessment"]["assessor_report"])
                            for index, record in enumerate(source["records"])]
            self.assertEqual(len(row["frames"]), len(expected))
            for projected, (index, phase, core) in zip(row["frames"], expected):
                total += 1
                self.assertEqual((projected["operation_index"], projected["phase"]), (index, phase))
                if core is None:
                    absent += 1
                    self.assertEqual(projected["availability"], "FRAME_NOT_RECORDED")
                else:
                    recorded += 1
                    self.assertEqual(projected["availability"], "RECORDED")
                    self.assertIsNone(projected["absence_reason"])
                    for name in ("evidence_integrity", "assessments", "findings"):
                        self.assertEqual(projected[name]["value"], core[name])
        self.assertEqual((total, recorded, absent), (129, 100, 29))

    def test_null_and_missing_frames_never_invent_unknown_assessments(self):
        for row in self.report["cases"]:
            for frame in row["frames"]:
                if frame["availability"] == "FRAME_NOT_RECORDED":
                    self.assertEqual(frame["absence_reason"], "NULL_CONTAINER")
                    self.assertIsNone(self.assert_reference(frame["source"]))
                    for name in ("evidence_integrity", "assessments", "findings"):
                        self.assertIsNone(frame[name])
        self.assertEqual(self.frame("LP-03", 0, "preflight")["source"]["pointer"],
                         "/records/0/report/preflight/assessor_frame")
        self.assertEqual(self.frame("UL-02", 0, "final_gate")["source"]["pointer"], "/reports/0/final_gate_assessment")
        # Exercise only the absence-location helper, not a bypass of the public
        # recheck gate: a missing field must cite its existing parent container.
        file = "evidence/publication/cases/LP-03.json"
        document = deepcopy(self.sources[file])
        del document["records"][0]["report"]["preflight"]["assessor_frame"]
        owned = {file: json_bytes(document)}
        frame = _frame(_Sources(owned), file, ["records", 0, "report", "preflight", "assessor_frame", "report"], 0, "preflight")
        self.assertEqual(frame["availability"], "FRAME_NOT_RECORDED")
        self.assertEqual(frame["absence_reason"], "MISSING_FIELD")
        self.assertEqual(frame["source"]["pointer"], "/records/0/report/preflight")
        self.assertEqual(frame["source"]["sha256"], sha256(owned[file]))
        self.assertIsNone(frame["assessments"])

    def test_final_authorization_and_postflight_are_not_conflated(self):
        values = [self.frame("UL-10", 0, phase)["assessments"]["value"]["transfer_authorization"]
                  for phase in ("preflight", "final_gate", "postflight")]
        self.assertEqual(values, ["ALLOW", "REVIEW", "ALLOW"])
        self.assertFalse(section_values(self.rows["UL-10"], "operation", 0)["attempted"])
        initial = section_values(self.rows["LP-08"], "authorization_preflight", 0)
        final = section_values(self.rows["LP-08"], "authorization_final_gate", 0)
        self.assertTrue(initial["authorized_local_export"])
        self.assertFalse(final["authorized_local_export"])
        self.assertEqual(self.frame("LP-08", 0, "final_gate")["assessments"]["value"]["approval_applicability"], "NOT_ESTABLISHED")

    def test_concurrent_cases_keep_original_operation_assessment_pairs(self):
        raw = self.original("LE-11")
        self.assertTrue(raw["sort_states"])
        self.assertEqual(raw["actual"]["local_observations"][0], "ABSENCE_ONLY")
        for index, record in enumerate(raw["records"]):
            operation = section_values(self.rows["LE-11"], "operation", index)
            self.assertEqual(operation["state"], record["bundle"]["provider_result"]["state"])
            self.assertEqual(operation["local_observation"], record["assessment"]["local_observation"])
            self.assertEqual(self.frame("LE-11", index, "erasure")["assessments"]["value"],
                             record["assessment"]["assessor_report"]["assessments"])
        self.assertEqual(section_values(self.rows["LE-11"], "operation", 0)["local_observation"], "REMOVAL_OBSERVED_SAME_CONTROLLER")
        raw = self.original("LP-15")
        self.assertNotEqual(raw["actual"]["states"][0], raw["records"][0]["report"]["state"])
        self.assertEqual(section_values(self.rows["LP-15"], "operation", 0)["state"], "REPLAY_NO_PUBLICATION")
        self.assertEqual(section_values(self.rows["LP-15"], "operation", 1)["state"], "LOCAL_OUTPUT_CONFIRMED")

    def test_bypass_notes_preserve_observed_effects_despite_controlled_blocks(self):
        upload = section_values(self.rows["UL-14"], "actual")
        self.assertEqual((upload["gateway_attempts"], upload["accepted_count"], upload["controller_direct_status"]), (0, 1, 200))
        self.assertIs(upload["all_route_prevention_established"], False)
        self.assertEqual(section_values(self.rows["UL-14"], "operation", 0)["state"], "BLOCKED_WITHOUT_ATTEMPT")
        publication = section_values(self.rows["LP-16"], "actual")
        self.assertEqual((publication["publication_attempts"], publication["visible_count"]), (0, 1))
        self.assertIs(publication["outside_gate_write_observed"], True)
        self.assertIs(publication["all_route_prevention_established"], False)
        self.assertIsNone(section_values(self.rows["LP-16"], "operation", 0)["publication"])
        self.assertIn("UPLOAD_OUTSIDE_ROUTE_BYPASS", {note["code"] for note in self.rows["UL-14"]["notes"]})
        self.assertIn("PUBLICATION_OUTSIDE_GATE_WRITE", {note["code"] for note in self.rows["LP-16"]["notes"]})

    def test_retained_read_later_presence_and_absence_only_remain_distinct(self):
        for cid, mechanism in (("LE-12", "excluded-copy"), ("LE-13", "open-handle")):
            control = section_values(self.rows[cid], "retained_control")
            self.assertEqual(control["retained_controls[0].mechanism"], mechanism)
            self.assertEqual(control["retained_controls[0].state"], "READABLE")
            operation = section_values(self.rows[cid], "operation", 0)
            self.assertEqual(operation["state"], "LOCAL_UNLINK_CONFIRMED")
            self.assertEqual(operation["local_observation"], "REMOVAL_OBSERVED_SAME_CONTROLLER")
            self.assertEqual(set(section_values(self.rows[cid], "unknown_domains", 0).values()), {"UNKNOWN"})
        self.assertEqual(section_values(self.rows["LE-14"], "operation", 0)["local_observation"], "ABSENCE_ONLY")
        self.assertIsNone(section_values(self.rows["LE-14"], "namespace_before", 0)["before"])
        self.assertEqual(section_values(self.rows["LE-15"], "operation", 0)["state"], "LOCAL_UNLINK_CONFIRMED")
        self.assertEqual(section_values(self.rows["LE-15"], "namespace_after", 0)["measurement"]["state"], "PRESENT")
        self.assertEqual(section_values(self.rows["LE-18"], "operation", 0)["local_observation"], "NOT_OBSERVED")
        for phase in ("before", "after"):
            self.assertIsNone(section_values(self.rows["LE-18"], "namespace_" + phase, 0)[phase])

    def test_unknown_dimensions_and_original_disclosure_extras_are_retained(self):
        for row in self.report["cases"]:
            for frame in row["frames"]:
                if frame["availability"] != "RECORDED":
                    continue
                values = frame["assessments"]["value"]
                if row["pilot"] == "upload":
                    self.assertEqual(values["remote_outcome"], "UNKNOWN")
                    self.assertEqual(values["coverage"], "INCOMPLETE")
                elif row["pilot"] == "publication":
                    self.assertIn(values["publication_action"], {"REVIEW", "BLOCK"})
                    self.assertEqual(values["delivery_status"], "UNCONFIRMED")
                    self.assertEqual(values["acceptance_status"], "UNKNOWN")
                else:
                    for name in ("provider_completion", "target_completion", "excluded_scope_outcome", "outside_scope_outcome"):
                        self.assertEqual(values[name], "UNKNOWN")
                    self.assertEqual(values["independent_verification"], "NOT_ESTABLISHED")
        for cid, activities in (("LP-09", []), ("LP-10", ["generation"])):
            extra = section_values(self.rows[cid], "additional_observations")
            self.assertEqual(extra, {"core_ai_involvement": "UNKNOWN", "core_activity_completeness": "UNKNOWN", "declared_activities": activities})
            self.assertEqual(extra["declared_activities"], self.rows[cid]["expectation"]["actual"]["value"]["declared_activities"])
        self.assertIsNone(section_values(self.rows["LE-03"], "operation", 0)["provider_result"])
        for cid in ("LE-04", "LE-05"):
            self.assertEqual(section_values(self.rows[cid], "operation", 0)["state"], "LOCAL_UNLINK_CONFIRMED")
            self.assertEqual(section_values(self.rows[cid], "probe")["probes[0].outcome"], "REJECTED")

    def test_notes_have_fixed_bilingual_text_and_required_control_references(self):
        required = {
            "UL-14": "UPLOAD_OUTSIDE_ROUTE_BYPASS", "UL-10": "UPLOAD_FINAL_GATE_DIFFERS",
            "UL-07": "UPLOAD_UNKNOWN_WITH_RECEIVER_OBSERVATION", "UL-08": "UPLOAD_UNKNOWN_WITH_RECEIVER_OBSERVATION",
            "UL-16": "UPLOAD_UNKNOWN_WITH_RECEIVER_OBSERVATION", "LP-16": "PUBLICATION_OUTSIDE_GATE_WRITE",
            "LP-09": "PUBLICATION_UNKNOWN_ORIGIN", "LP-10": "PUBLICATION_UNKNOWN_ORIGIN",
            "LP-14": "PUBLICATION_UNKNOWN_WITH_VISIBLE_FILE", "LE-12": "ERASURE_READABLE_RETAINED_DATA",
            "LE-13": "ERASURE_READABLE_RETAINED_DATA", "LE-14": "ERASURE_AFTER_ONLY_ABSENCE",
            "LE-15": "ERASURE_LATER_PRESENCE", "LE-18": "ERASURE_NO_OBSERVER",
        }
        for cid, code in required.items():
            self.assertIn(code, {note["code"] for note in self.rows[cid]["notes"]})
        for row in self.report["cases"]:
            for note in row["notes"]:
                self.assertEqual(set(note), {"code", "sources"})
                self.assertIn(note["code"], NOTE_TEXT)
                self.assertEqual(set(NOTE_TEXT[note["code"]]), {"en", "ja"})
                self.assertTrue(all(NOTE_TEXT[note["code"]].values()))
                self.assertTrue(note["sources"])
                for source in note["sources"]:
                    self.assert_reference(source)

    def test_raw_digest_conventions_and_article_signature_exclusion(self):
        for pilot, cid in (("upload", "UL-01"), ("publication", "LP-01"), ("erasure", "LE-01")):
            summary = self.sources["evidence/" + pilot + "/summary.json"]
            source = self.rows[cid]["capture_source"]
            self.assertEqual(source["sha256"], sha256(self.files[source["file"]]))
            if pilot == "upload":
                self.assertNotEqual(source["sha256"], summary["results"][0]["export_sha256"])
            else:
                self.assertEqual(source["sha256"], summary["results"][0]["export_sha256"])
        strings = {node for node in nodes(self.report) if type(node) is str}
        for row in self.report["cases"]:
            if row["pilot"] == "publication":
                for record in self.original(row["case_id"])["records"]:
                    self.assertNotIn(record["candidate"]["html"], strings)
        for node in nodes(self.report):
            if type(node) is dict:
                self.assertFalse({"algorithm", "key_id", "body", "signature"}.issubset(node))
                if set(node) == {"name", "value", "source"}:
                    self.assertNotIn("/candidate/html", node["source"]["pointer"])
                    self.assertNotIn("/candidate/source", node["source"]["pointer"])
                    self.assertNotIn("/signature", node["source"]["pointer"])

    def test_projection_is_deterministic_and_does_not_mutate_inputs(self):
        original = json_bytes(self.report)
        repeated = project(dict(reversed(list(self.files.items()))), self.capture["recheck"], self.capture["identity"])
        self.assertEqual(json_bytes(repeated), original)
        self.assertLess(len(original), 2 * 1024 * 1024)
        repeated["recheck"]["pilots"][0]["verified_exports"] = -1
        repeated["reporter"]["source_manifest"].clear()
        self.assertEqual(self.capture["recheck"]["pilots"][0]["verified_exports"], 17)
        self.assertTrue(self.capture["identity"]["source_manifest"])
        self.assertEqual(json_bytes(project(self.files, self.capture["recheck"], self.capture["identity"])), original)


if __name__ == "__main__":
    unittest.main()
