"""Synthetic medical AI evidence checks; no patient data or external dependencies."""
import json, pathlib, unittest
ROOT=pathlib.Path(__file__).parent
def assess(c):
    evidence=c["evidence"]
    expectation=c["expect"]
    if expectation=="NOT_RUN": return "NOT_RUN" if evidence.get("check_status")=="not_run" else "MISMATCH"
    if expectation=="UNKNOWN_TIMEOUT": return "UNKNOWN" if evidence.get("check_status")=="timeout" else "MISMATCH"
    if expectation=="DISPLAY_DIVERGENCE": return "DIVERGENCE" if evidence.get("draft_digest")!=evidence.get("display_digest") else "MISMATCH"
    if expectation=="MISSING_CONTEXT": return "MISSING" if "renal_function" not in evidence.get("patient_fields",[]) else "MISMATCH"
    if expectation=="POST_ANCHOR_OMISSION": return "INCOMPLETE_SUBMISSION" if evidence.get("anchored_count",0)>evidence.get("submitted_count",0) and evidence.get("manifest_bound") else "MISMATCH"
    if expectation=="PRE_COLLECTION_GAP": return "UNOBSERVED" if evidence.get("collector_coverage")=="partial" else "MISMATCH"
    if expectation=="TRANSLATION_DERIVATION": return "DERIVATIVE" if evidence.get("original_digest")!=evidence.get("translated_digest") and evidence.get("parent_ref") else "MISMATCH"
    if expectation=="PROVIDER_STATE_UNOBSERVABLE": return "UNKNOWN" if evidence.get("provider_filter_state") is None else "MISMATCH"
    if expectation=="MODEL_REPLAY_DIVERGENCE": return "REPLAY_DIFFERS" if evidence.get("original_digest")!=evidence.get("replay_digest") else "MISMATCH"
    raise ValueError("Unknown expectation")
class SyntheticCases(unittest.TestCase):
    def test_all(self):
        cases=json.loads((ROOT/"cases.json").read_text())
        self.assertEqual(len(cases),9)
        for case in cases:
            with self.subTest(case=case["id"]):
                self.assertEqual(assess(case),case["expected_result"])
if __name__=="__main__": unittest.main()
