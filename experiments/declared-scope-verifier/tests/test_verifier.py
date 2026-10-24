import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scope_verifier.crypto import (InputError, canonical, digest, hex_bytes, inclusion,
                                   leaf_hash, merkle_root, strict_json)
from scope_verifier.fixtures import (EVALUATION_TIME, base, disposition, private_key,
                                    refresh_manifest, resign, signed)
from scope_verifier.verifier import aggregate, verify


class CryptoVectors(unittest.TestCase):
    def test_jcs_rfc8785_numbers_and_property_order(self):
        obj = {"z": [1e30, 4.50, 2e-3, 1e-27], "a": "€\n"}
        self.assertEqual(canonical(obj), b'{"a":"\xe2\x82\xac\\n","z":[1e+30,4.5,0.002,1e-27]}')

    def test_jcs_utf16_order_differs_from_unicode_codepoint_order(self):
        self.assertEqual(canonical({"\ue000": 2, "😀": 1}), '{"😀":1,"\ue000":2}'.encode())

    def test_jcs_unsafe_integer_and_nonfinite_rejected(self):
        for value in (2**60, float("nan"), float("inf")):
            with self.subTest(value=value), self.assertRaises(InputError):
                canonical(value)

    def test_duplicate_json_members_and_nan_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.json"
            for raw in ('{"a":1,"a":2}', '{"x":NaN}', '{"x":Infinity}'):
                path.write_text(raw)
                with self.subTest(raw=raw), self.assertRaises(InputError):
                    strict_json(path)

    def test_rfc6962_three_leaf_tree_independent_manual_vector(self):
        # Explicit RFC 6962 tree shape: H(01 || H(01 || L0 || L1) || L2).
        h = lambda b: hashlib.sha256(b).digest()
        a, b, c = [h(b"\x00" + raw) for raw in (b'"a"', b'"b"', b'"c"')]
        ab = h(b"\x01" + a + b)
        root = h(b"\x01" + ab + c)
        self.assertEqual(merkle_root([a, b, c]), root)
        self.assertTrue(inclusion(a, 0, 3, [b.hex(), c.hex()], root.hex()))
        self.assertTrue(inclusion(b, 1, 3, [a.hex(), c.hex()], root.hex()))
        self.assertTrue(inclusion(c, 2, 3, [ab.hex()], root.hex()))
        self.assertFalse(inclusion(c, 2, 3, [ab.hex(), ab.hex()], root.hex()))
        self.assertFalse(inclusion(a, 0, 3, [b.hex()], root.hex()))
        self.assertFalse(inclusion(c, 1, 3, [ab.hex()], root.hex()))

    def test_merkle_empty_and_singleton(self):
        self.assertEqual(merkle_root([]), hashlib.sha256(b"").digest())
        leaf = leaf_hash({"x": 1})
        self.assertTrue(inclusion(leaf, 0, 1, [], leaf.hex()))
        self.assertFalse(inclusion(leaf, 1, 1, [], leaf.hex()))
        self.assertFalse(inclusion(leaf, 0, 0, [], leaf.hex()))

    def test_boolean_and_negative_merkle_indices_rejected(self):
        for index in (True, -1):
            with self.subTest(index=index), self.assertRaises(InputError):
                inclusion(b"a" * 32, index, 1, [], "00" * 32)

    def test_failure_precedes_unknown_without_losing_unknown_items(self):
        checks = [{"result": s} for s in ("verified", "failed", "indeterminate")]
        self.assertEqual(aggregate(checks), "failed")
        self.assertEqual(checks[-1]["result"], "indeterminate")


class EvidenceRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original = base(count=3)

    def setUp(self):
        self.p, self.trust = copy.deepcopy(self.original)

    def run_verifier(self, mode="experimental-scope", at=EVALUATION_TIME, simulate=True):
        return verify(self.p, self.trust, mode, at, simulate)

    def outcome(self, integrity, scope):
        result = self.run_verifier()
        self.assertEqual(result["integrity"]["result"], integrity)
        self.assertEqual(result["scope_fulfillment"]["result"], scope)
        self.assertIsNone(result["overall_pass"])
        return result

    def reapprove(self):
        # Explicit out-of-band approval used only to exercise a changed test policy.
        x = self.p["experimental"]
        x["scope"] = resign(x["scope"])
        sd = digest(x["scope"])
        self.trust["scope_digest"] = sd
        for name in ("inventory", "closure", "manifest"):
            if x.get(name):
                x[name]["body"]["scope_digest"] = sd
                x[name] = resign(x[name])
        if x.get("scope_receipt"):
            x["scope_receipt"]["body"]["target_digest"] = sd
            x["scope_receipt"] = resign(x["scope_receipt"])

    def test_complete_small_package(self):
        self.outcome("verified", "met")

    def test_current_mode_does_not_parse_or_require_extension(self):
        self.p["experimental"] = "deliberately-not-an-extension"
        result = self.run_verifier("vap-v1.2")
        self.assertIsNone(result["scope_fulfillment"])
        self.assertEqual(result["proposal_status"], "not_applied")
        self.assertEqual(result["integrity"]["result"], "verified")

    def test_extension_mode_requires_sidecars(self):
        del self.p["experimental"]
        self.outcome("verified", "indeterminate")

    def test_no_synthetic_opt_in_never_verifies_external_time(self):
        result = self.run_verifier(simulate=False)
        self.assertEqual(result["integrity"]["result"], "indeterminate")
        self.assertEqual(result["scope_fulfillment"]["result"], "indeterminate")

    def test_removed_record_preserves_original_anchor(self):
        original_anchor = copy.deepcopy(self.p["anchor"])
        self.p["events"].pop()
        disposition(self.p, "record-0002", "unaccounted")
        refresh_manifest(self.p)
        result = self.outcome("verified", "not_met")
        self.assertEqual(self.p["anchor"], original_anchor)
        self.assertEqual(next(c["result"] for c in result["v1_2_requirements"] if c["check"] == "INT-008"), "failed")

    def test_input_signature_valid_flag_cannot_bypass_crypto(self):
        self.p["events"][0]["signed"]["body"]["payload"]["value"] = 1
        self.p["signature_valid"] = True
        refresh_manifest(self.p)
        self.outcome("failed", "indeterminate")

    def test_failed_crypto_retains_missing_proof_unknown(self):
        self.p["events"][0]["signed"]["signature"] = "00" * 64
        self.p["experimental"]["scope_receipt"] = None
        refresh_manifest(self.p)
        result = self.outcome("failed", "indeterminate")
        self.assertIn("indeterminate", [c["result"] for c in result["integrity"]["checks"]])

    def test_key_embedded_in_package_is_not_trusted(self):
        event = self.p["events"][0]["signed"]
        self.p["events"][0]["signed"] = signed(event["body"], "attacker")
        self.p["keys"] = {"attacker": {"public_key": private_key("attacker").public_key().public_bytes_raw().hex(), "roles": ["event"]}}
        refresh_manifest(self.p)
        result = self.run_verifier()
        self.assertEqual(result["integrity"]["result"], "indeterminate")
        self.assertEqual(result["scope_fulfillment"]["result"], "indeterminate")

    def test_unsupported_algorithm_is_unknown(self):
        self.p["events"][0]["signed"]["algorithm"] = "FutureAlgorithm"
        refresh_manifest(self.p)
        self.outcome("indeterminate", "indeterminate")

    def test_missing_signature_is_unknown(self):
        del self.p["events"][0]["signed"]["signature"]
        refresh_manifest(self.p)
        self.outcome("indeterminate", "indeterminate")

    def test_invalid_merkle_proof_is_failure(self):
        self.p["events"][0]["path"][0] = "00" * 32
        refresh_manifest(self.p)
        self.outcome("failed", "indeterminate")

    def test_anchor_count_tampering_is_failure(self):
        self.p["anchor"]["body"]["batch"]["event_count"] = 2
        self.outcome("failed", "indeterminate")

    def test_missing_anchor_receipt_does_not_pass_int006(self):
        self.p["anchor_receipt"] = None
        result = self.outcome("indeterminate", "indeterminate")
        self.assertEqual(next(c["result"] for c in result["v1_2_requirements"] if c["check"] == "INT-006"), "indeterminate")

    def test_future_receipt_is_not_available_at_evaluation_time(self):
        self.p["anchor_receipt"]["body"]["accepted_at"] = EVALUATION_TIME + 100
        self.p["anchor_receipt"] = resign(self.p["anchor_receipt"])
        self.outcome("indeterminate", "indeterminate")

    def test_cross_exercise_inventory_is_rejected(self):
        x = self.p["experimental"]
        x["inventory"]["body"]["evaluation_id"] = "another-evaluation"
        x["inventory"] = resign(x["inventory"])
        self.outcome("failed", "indeterminate")

    def test_changed_inventory_cannot_rewrite_prior_fixed_commitment(self):
        x = self.p["experimental"]
        x["inventory"]["body"]["obligations"].pop()
        x["inventory"] = resign(x["inventory"])
        self.outcome("failed", "indeterminate")

    def test_manifest_cannot_reference_different_delivery(self):
        x = self.p["experimental"]
        x["manifest"]["body"]["delivery_digest"] = "00" * 32
        x["manifest"] = resign(x["manifest"])
        self.outcome("failed", "indeterminate")

    def test_manifest_included_flag_cannot_conceal_missing_record(self):
        self.p["events"].pop()
        refresh_manifest(self.p)
        result = self.outcome("verified", "not_met")
        self.assertEqual(result["scope_fulfillment"]["violations"][0]["code"], "missing_delivery")

    def test_signed_withheld_claim_is_not_accepted_when_payload_is_present(self):
        disposition(self.p, "record-0002", "withheld")
        refresh_manifest(self.p)
        result = self.outcome("verified", "indeterminate")
        self.assertFalse(result["scope_fulfillment"]["violations"])

    def test_duplicate_expected_obligation_is_rejected(self):
        x = self.p["experimental"]
        x["inventory"]["body"]["obligations"].append(copy.deepcopy(x["inventory"]["body"]["obligations"][0]))
        x["inventory"] = resign(x["inventory"])
        with self.assertRaises(InputError):
            self.run_verifier()

    def test_hidden_commitment_cannot_be_relabelled_as_other_event(self):
        self.p, self.trust = base(commitment=True, count=3)
        self.p["events"].pop()
        disposition(self.p, "record-0002", "withheld")
        wrong = self.p["events"][0]
        self.p["commitment_proofs"] = [{**self.p["batch_index"][0], "event_id": "record-0002", "index": 0, "path": wrong["path"]}]
        refresh_manifest(self.p)
        self.outcome("failed", "indeterminate")

    def test_hidden_commitment_must_match_required_source(self):
        self.p, self.trust = base(commitment=True, count=3)
        removed = self.p["events"].pop()
        disposition(self.p, "record-0002", "withheld")
        self.p["commitment_proofs"] = [{**self.p["batch_index"][-1], "index": 2, "path": removed["path"]}]
        x = self.p["experimental"]
        obligations = x["inventory"]["body"]["obligations"]
        obligations[-1]["source_id"] = "producer"
        x["scope"]["body"]["expected_digest"] = digest(obligations)
        x["closure"]["body"]["expected_digest"] = digest(obligations)
        self.reapprove()
        refresh_manifest(self.p)
        result = self.outcome("verified", "not_met")
        self.assertEqual(result["scope_fulfillment"]["violations"][0]["code"], "commitment_type_mismatch")

    def test_closure_must_bind_same_expected_set(self):
        x = self.p["experimental"]
        x["closure"]["body"]["expected_digest"] = "00" * 32
        x["closure"] = resign(x["closure"])
        self.outcome("failed", "indeterminate")

    def test_unapproved_retrospective_narrowing_rejected(self):
        x = self.p["experimental"]
        x["scope"]["body"]["revision"] = "2"
        x["scope"]["body"]["previous_revision"] = self.trust["scope_digest"]
        x["scope"]["body"]["expected_digest"] = digest(x["inventory"]["body"]["obligations"][:1])
        x["scope"] = resign(x["scope"])
        self.outcome("failed", "indeterminate")

    def test_reapproved_amendment_still_not_supported_as_new_success(self):
        self.p["experimental"]["scope"]["body"]["revision"] = "2"
        self.reapprove()
        self.outcome("verified", "indeterminate")

    def test_derived_inventory_reproduced_from_source_records(self):
        self.p, self.trust = base(derived=True, count=3)
        self.outcome("verified", "met")

    def test_derived_inventory_requires_source_records(self):
        self.p, self.trust = base(derived=True, count=3)
        del self.p["experimental"]["source_records"]
        self.outcome("verified", "indeterminate")

    def test_derived_source_tamper_is_detected(self):
        self.p, self.trust = base(derived=True, count=3)
        self.p["experimental"]["source_records"][0]["obligation"]["id"] = "forged"
        self.outcome("failed", "indeterminate")

    def test_unsupported_derivation_never_met(self):
        self.p["experimental"]["scope"]["body"]["derivation_rule"] = "new-unknown-rule"
        self.reapprove()
        self.outcome("verified", "indeterminate")

    def test_late_receipt_alone_does_not_prove_violation(self):
        x = self.p["experimental"]
        x["scope_receipt"]["body"]["accepted_at"] = 2000000060
        x["scope_receipt"] = resign(x["scope_receipt"])
        self.outcome("verified", "indeterminate")

    def test_receipt_uncertainty_spanning_cutoff_is_unknown(self):
        x = self.p["experimental"]
        x["scope_receipt"]["body"]["accepted_at"] = 2000000050
        x["scope_receipt"] = resign(x["scope_receipt"])
        self.outcome("verified", "indeterminate")

    def test_receipt_latest_bound_equal_cutoff_is_accepted(self):
        x = self.p["experimental"]
        x["scope_receipt"]["body"]["accepted_at"] = 2000000049
        x["scope_receipt"] = resign(x["scope_receipt"])
        self.outcome("verified", "met")

    def test_deadline_pending_does_not_become_missing_delivery_failure(self):
        self.p["events"].pop()
        disposition(self.p, "record-0002", "unaccounted")
        refresh_manifest(self.p)
        result = self.run_verifier(at=2000000280)
        self.assertEqual(result["scope_fulfillment"]["result"], "indeterminate")

    def test_known_violation_survives_unknown_full_expected_inventory(self):
        x = self.p["experimental"]
        x["scope"]["body"]["individually_required"] = [copy.deepcopy(x["inventory"]["body"]["obligations"][-1])]
        self.reapprove()
        x["inventory"] = x["closure"] = None
        self.p["events"].pop()
        disposition(self.p, "record-0002", "withheld")
        refresh_manifest(self.p)
        result = self.outcome("verified", "not_met")
        self.assertIsNone(result["scope_fulfillment"]["expected_distinct_obligations"])
        self.assertTrue(result["scope_fulfillment"]["unresolved"])

    def test_independent_withholding_violation_survives_corrupt_other_event(self):
        self.p["events"][0]["signed"]["signature"] = "00" * 64
        self.p["events"].pop()
        disposition(self.p, "record-0002", "withheld")
        refresh_manifest(self.p)
        result = self.outcome("failed", "not_met")
        self.assertIn("trust", result["scope_fulfillment"]["violations"][0]["evidence"])

    def test_notification_stages_are_not_interchangeable(self):
        self.p, self.trust = base(notification=True, count=3)
        x = self.p["experimental"]
        obligations = x["inventory"]["body"]["obligations"]
        obligations[-1]["notification"]["stage"] = "human_acknowledged"
        x["scope"]["body"]["expected_digest"] = digest(obligations)
        x["closure"]["body"]["expected_digest"] = digest(obligations)
        self.reapprove()
        self.outcome("verified", "not_met")

    def test_empty_explicit_inventory_has_only_narrow_empty_set_result(self):
        self.p, self.trust = base(count=0)
        result = self.outcome("verified", "met")
        self.assertEqual(result["scope_fulfillment"]["expected_distinct_obligations"], 0)

    def test_string_false_cannot_assert_closure(self):
        x = self.p["experimental"]
        x["closure"]["body"]["closed"] = "false"
        x["closure"] = resign(x["closure"])
        with self.assertRaises(InputError):
            self.run_verifier()

    def test_duplicate_manifest_entries_rejected(self):
        x = self.p["experimental"]
        x["manifest"]["body"]["entries"].append(copy.deepcopy(x["manifest"]["body"]["entries"][0]))
        x["manifest"] = resign(x["manifest"])
        with self.assertRaises(InputError):
            self.run_verifier()

    def test_policy_cannot_be_replaced_by_submitter(self):
        self.p["policy"]["id"] = "less-demanding"
        self.outcome("failed", "indeterminate")

    def test_unsupported_mode_rejected(self):
        with self.assertRaises(InputError):
            self.run_verifier("automatic")


if __name__ == "__main__":
    unittest.main()
