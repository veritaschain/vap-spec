"""Offline security-boundary tests with real Ed25519 signatures and synthetic data."""
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fixtures import (ALTERNATE_DESTINATION, DELEGATE, fixture_key, make_fixture,
                      rebind_fixture, resign, _rebind_downstream)
from wallet_evidence import (CLAIMS, ZERO_ADDRESS, admission_decision, canonical_json,
                             digest, load_json, sign_envelope, verify_bundle)


class WalletEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.bundle, self.trust, self.at = make_fixture()

    def verify(self):
        return verify_bundle(self.bundle, self.trust, evaluation_time=self.at)

    def verdict(self, claim):
        return self.verify()["claims"][claim]["verdict"]

    def update(self, name, **changes):
        payload = copy.deepcopy(self.bundle["evidence"][name]["payload"])
        payload.update(changes)
        resign(self.bundle, name, payload)

    def bind_chain_to_execution(self):
        self.update("chain_observation", execution_digest=digest(self.bundle["evidence"]["execution"]["payload"]))

    def test_deterministic_valid_evidence_and_independent_claims(self):
        first = self.verify()
        self.assertEqual(first["admission"], "ALLOW")
        self.assertEqual(set(first["claims"]), set(CLAIMS))
        self.assertTrue(all(v["verdict"] == "VALID" for v in first["claims"].values()))
        self.assertEqual(canonical_json(first), canonical_json(self.verify()))
        self.assertEqual(self.bundle, make_fixture()[0])

    def test_valid_signature_is_not_authorization(self):
        self.bundle, self.trust, self.at = make_fixture("approval_mismatch")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")
        self.assertEqual(self.verdict("execution_match"), "VALID")
        self.assertEqual(self.verify()["admission"], "DENY")

    def test_missing_approval_is_unknown_not_proof_of_no_approval(self):
        self.bundle, self.trust, self.at = make_fixture("missing_approval")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")
        self.assertEqual(self.verify()["admission"], "DENY")

    def test_missing_entire_evidence_set_never_means_valid(self):
        self.bundle["evidence"] = {}
        report = self.verify()
        self.assertTrue(all(x["verdict"] == "INDETERMINATE" for x in report["claims"].values()))

    def test_each_missing_required_authorization_record_is_unknown(self):
        for name in ("policy", "approval", "final_revocation", "control_observation"):
            with self.subTest(name=name):
                self.setUp()
                del self.bundle["evidence"][name]
                self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_unsigned_mutation_is_detected_by_ed25519(self):
        self.bundle["evidence"]["approval"]["payload"]["approver_id"] = "attacker"
        self.assertEqual(self.verdict("integrity"), "INVALID")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_key_id_is_inside_signature_domain(self):
        env = self.bundle["evidence"]["approval"]
        original = self.trust["approval_authority"][env["key_id"]]
        self.trust["approval_authority"]["alias"] = original
        env["key_id"] = "alias"
        self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_bundle_cannot_supply_trust_anchor(self):
        self.trust = {}
        self.assertEqual(self.verdict("integrity"), "INDETERMINATE")
        self.assertEqual(self.verify()["admission"], "DENY")
        self.bundle["evidence"]["approval"]["public_key"] = "00" * 32
        self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_invalid_signature_encoding_is_rejected_even_for_unknown_key(self):
        self.bundle["evidence"]["approval"].update(key_id="unknown-key", signature=123)
        self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_trusted_key_for_wrong_role_is_not_approval_authority(self):
        a = self.bundle["evidence"]["approval"]["payload"]
        self.bundle["evidence"]["approval"] = sign_envelope(a, "synthetic-policy_authority", fixture_key("policy_authority"))
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_chain_observer_must_use_independent_pinned_key(self):
        key_id = "synthetic-execution_observer"
        key = self.trust["execution_observer"][key_id]
        self.trust["chain_observer"] = {key_id: key}
        body = self.bundle["evidence"]["chain_observation"]["payload"]
        self.bundle["evidence"]["chain_observation"] = sign_envelope(body, key_id, fixture_key("execution_observer"))
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("delegation_state"), "INDETERMINATE")

    def test_exact_approved_operation_rejects_each_validly_shaped_substitution(self):
        changes = {"operation_id": "other-operation", "actor_id": "other-actor", "credential_id": "other-credential",
                   "workload_id": "other-workload", "deployment_digest": "sha256:" + "ab" * 32,
                   "chain_id": "31338", "wallet": "0x" + "55" * 20, "asset": "0x" + "66" * 20,
                   "amount": "1", "destination": ALTERNATE_DESTINATION, "calldata": "0xab",
                   "delegation_target": "0x" + "77" * 20, "nonce": "8",
                   "signing_payload_digest": "sha256:" + "cd" * 32, "policy_digest": "sha256:" + "ef" * 32}
        for field, value in changes.items():
            with self.subTest(field=field):
                self.setUp()
                self.bundle["operation"][field] = value
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("authorization"), "INVALID")
        self.setUp()
        self.bundle["operation"].update(action="clear_delegation", delegation_target=ZERO_ADDRESS)
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_signed_actual_execution_change_does_not_change_approval(self):
        actual = copy.deepcopy(self.bundle["operation"])
        actual["destination"] = ALTERNATE_DESTINATION
        self.update("execution", actual_operation=actual)
        self.bind_chain_to_execution()
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "VALID")
        self.assertEqual(self.verdict("execution_match"), "INVALID")

    def test_exact_signing_bytes_mismatch_is_detected(self):
        self.update("execution", signing_payload="0x010203")
        self.bind_chain_to_execution()
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("execution_match"), "INVALID")

    def test_policy_is_checked_even_after_all_digests_are_rebound(self):
        rebind_fixture(self.bundle, operation_updates={"amount": "1000001"})
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_policy_version_change_requires_new_exact_approval(self):
        self.update("policy", version="2")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_revoked_credential_is_verified_contradiction(self):
        self.bundle, self.trust, self.at = make_fixture("credential_revoked")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_revoked_approval_is_verified_contradiction(self):
        approval_id = self.bundle["evidence"]["approval"]["payload"]["approval_id"]
        self.update("final_revocation", revoked_approvals=[approval_id])
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_stale_or_future_revocation_is_unknown(self):
        for checked_at, valid_until in ((self.at - 301, self.at + 30), (self.at + 1, self.at + 30),
                                       (self.at - 30, self.at - 1)):
            with self.subTest(checked_at=checked_at, valid_until=valid_until):
                self.setUp()
                self.update("approval", issued_at=self.at - 400)
                self.update("final_revocation", checked_at=checked_at, valid_until=valid_until)
                _rebind_downstream(self.bundle)
                self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_execution_must_bind_final_revocation_and_control(self):
        for field in ("revocation_digest", "control_digest", "approval_digest"):
            with self.subTest(field=field):
                self.setUp()
                self.update("execution", **{field: "sha256:" + "aa" * 32})
                self.assertEqual(self.verdict("execution_match"), "INVALID")

    def test_execution_outside_snapshot_window_is_not_accepted(self):
        self.update("execution", observed_at=self.at - 10)
        self.assertEqual(self.verdict("execution_match"), "INVALID")

    def test_final_snapshot_cannot_precede_the_approval_it_claims_to_check(self):
        self.update("approval", issued_at=self.at - 2)
        _rebind_downstream(self.bundle)
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")
        self.assertEqual(self.verify()["admission"], "DENY")

    def test_control_observation_after_execution_cannot_prove_preexecution_control(self):
        self.update("control_observation", observed_at=self.at)
        _rebind_downstream(self.bundle)
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("execution_match"), "INVALID")
        self.assertEqual(self.verify()["admission"], "DENY")

    def test_old_control_observation_is_unknown_at_execution_time(self):
        self.update("control_observation", observed_at=self.at - 303)
        _rebind_downstream(self.bundle)
        self.assertEqual(self.verdict("execution_match"), "INDETERMINATE")

    def test_offchain_stop_does_not_clear_persistent_delegation(self):
        self.bundle, self.trust, self.at = make_fixture("stop_with_delegation")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("execution_match"), "INDETERMINATE")
        self.assertEqual(self.verdict("delegation_state"), "INVALID")

    def test_successful_receipt_does_not_establish_cleared_code(self):
        self.bundle, self.trust, self.at = make_fixture("clear_observed")
        self.update("chain_observation", receipt_status="success", delegation_code="0xef0100" + DELEGATE[2:])
        self.assertEqual(self.verdict("delegation_state"), "INVALID")

    def test_outer_revert_does_not_undo_observed_delegation_or_clear(self):
        for case in ("authorized", "clear_observed"):
            with self.subTest(case=case):
                self.bundle, self.trust, self.at = make_fixture(case)
                self.update("chain_observation", receipt_status="reverted")
                self.assertEqual(self.verdict("delegation_state"), "VALID")

    def test_receipt_without_independent_chain_observation_is_unknown(self):
        del self.bundle["evidence"]["chain_observation"]
        self.assertEqual(self.verdict("execution_match"), "VALID")
        self.assertEqual(self.verdict("delegation_state"), "INDETERMINATE")

    def test_observation_is_bound_to_chain_wallet_run_block_and_execution(self):
        for field, value in (("chain_id", "1"), ("wallet", "0x" + "55" * 20), ("run_id", "other-run"),
                             ("block_hash", "0x" + "cc" * 32), ("block_number", "99"),
                             ("execution_digest", "sha256:" + "dd" * 32)):
            with self.subTest(field=field):
                self.setUp()
                self.update("chain_observation", **{field: value})
                self.assertEqual(self.verdict("delegation_state"), "INVALID")

    def test_finality_requirement_not_assumed_from_receipt(self):
        rebind_fixture(self.bundle, policy_updates={"required_finality": "finalized"})
        self.assertEqual(self.verdict("delegation_state"), "INDETERMINATE")
        self.update("chain_observation", finality="finalized")
        self.assertEqual(self.verdict("delegation_state"), "VALID")

    def test_later_state_block_without_ancestry_proof_is_unknown(self):
        self.update("chain_observation", block_number="101", block_hash="0x" + "cc" * 32)
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("delegation_state"), "INDETERMINATE")
        self.assertEqual(self.verify()["admission"], "DENY")

    def test_unknown_outcome_has_no_resend_or_signing_path(self):
        self.update("execution", state="unknown")
        self.bind_chain_to_execution()
        self.assertEqual(self.verdict("execution_match"), "INDETERMINATE")
        self.assertEqual(self.verify()["admission"], "DENY")
        self.assertIn("no_automatic_resigning_rebroadcast_or_retry_on_unknown_outcome", self.verify()["limitations"])

    def test_signed_bypass_observation_is_control_failure_not_integrity_failure(self):
        self.bundle, self.trust, self.at = make_fixture("deployment_bypass")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_unobserved_controller_route_is_unknown_not_blocked(self):
        self.bundle, self.trust, self.at = make_fixture("unknown_controller")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")
        self.update("control_observation", routes={"approved_gate": "recorded", "direct_signer": "blocked"})
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_replayed_signed_record_from_other_run_is_rejected(self):
        self.update("approval", run_id="synthetic-other-run")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_boolean_timestamp_cannot_pass_as_integer(self):
        self.update("final_revocation", checked_at=True)
        self.assertEqual(self.verdict("authorization"), "INVALID")
        with self.assertRaises(ValueError):
            verify_bundle(self.bundle, self.trust, evaluation_time=True)

    def test_parser_rejects_ambiguous_json_representations(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":1.0}', '{"a":9007199254740992}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                load_json(raw)
        with self.assertRaises(ValueError):
            canonical_json({"a": "e\u0301"})
        with self.assertRaises(ValueError):
            canonical_json({"a": 1.5})

    def test_deep_untrusted_input_fails_closed_without_recursion_error(self):
        nested = {}
        for _ in range(1200):
            nested = {"child": nested}
        self.bundle["extra"] = nested
        self.assertEqual(self.verdict("integrity"), "INVALID")
        with self.assertRaises(ValueError):
            load_json("[" * 1200 + "0" + "]" * 1200)

    def test_invalid_signed_shapes_produce_verdicts_not_crashes(self):
        for name, field, value in (("policy", "max_amount", {}), ("policy", "required_routes", [{}]),
                                   ("approval", "issued_at", []), ("final_revocation", "revoked_credentials", [{}]),
                                   ("control_observation", "routes", None), ("execution", "actual_operation", []),
                                   ("chain_observation", "transaction_block_number", {})):
            with self.subTest(name=name, field=field):
                self.setUp()
                self.update(name, **{field: value})
                self.assertEqual(self.verify()["admission"], "DENY")

    def test_missing_and_explicit_null_evidence_have_same_unknown_meaning(self):
        del self.bundle["evidence"]["approval"]
        absent = self.verify()
        self.bundle["evidence"]["approval"] = None
        self.assertEqual(absent, self.verify())

    def test_caller_bundle_is_not_mutated_by_verifier(self):
        before = copy.deepcopy(self.bundle)
        self.verify()
        self.assertEqual(before, self.bundle)

    def test_admission_helper_is_not_a_live_authorizer(self):
        self.assertEqual(admission_decision({}), "DENY")
        self.bundle, self.trust, self.at = make_fixture("missing_approval")
        self.assertEqual(admission_decision(self.verify()), "DENY")

    def test_read_only_cli_is_deterministic_and_uses_external_trust(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            bundle_path, trust_path = base / "bundle.json", base / "trust.json"
            bundle_path.write_bytes(canonical_json(self.bundle))
            trust_path.write_bytes(canonical_json({role: {key: pub.hex() for key, pub in keys.items()}
                                                   for role, keys in self.trust.items()}))
            command = [sys.executable, str(Path(__file__).resolve().parents[1] / "wallet_evidence.py"),
                       "--bundle", str(bundle_path), "--trust", str(trust_path), "--at", str(self.at)]
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            first = subprocess.run(command, capture_output=True, check=False, env=env)
            second = subprocess.run(command, capture_output=True, check=False, env=env)
            self.assertEqual(first.returncode, 0, first.stderr.decode())
            self.assertEqual(first.stdout, second.stdout)
            self.assertEqual(json.loads(first.stdout)["admission"], "ALLOW")
            self.assertEqual(sorted(path.name for path in base.iterdir()), ["bundle.json", "trust.json"])
            trust_path.write_text("{}")
            denied = subprocess.run(command, capture_output=True, check=False, env=env)
            self.assertEqual(denied.returncode, 2)
            self.assertEqual(json.loads(denied.stdout)["claims"]["authorization"]["verdict"], "INDETERMINATE")


if __name__ == "__main__":
    unittest.main()
