"""Offline payment-evidence boundaries, using real signatures and synthetic data.

These tests inspect bindings and attributed observations. They neither contact a
payment provider nor establish an adapter's durable replay/recovery behaviour.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


HERE = Path(__file__).resolve().parents[1]


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# Avoid sharing the generic ``fixtures`` module with another experiment's tests.
evidence = _module("payment_evidence", HERE / "payment_evidence.py")
fixtures = _module("payment_boundary_test_fixtures", HERE / "fixtures.py")


class PaymentEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.reset()

    def reset(self, case="authorized"):
        self.bundle, self.trust, self.identities, self.at = fixtures.make_fixture(case)

    def verify(self, **overrides):
        return evidence.verify_bundle(
            self.bundle, self.trust, identities=self.identities,
            evaluation_time=overrides.pop("evaluation_time", self.at), **overrides)

    def verdict(self, name):
        return self.verify()["claims"][name]["verdict"]

    def update(self, name, **changes):
        body = copy.deepcopy(self.bundle["evidence"][name]["payload"])
        body.update(changes)
        fixtures.resign(self.bundle, name, body)

    def refresh(self):
        fixtures.refresh_bindings(self.bundle)

    def reapprove(self, *, policy_updates=None, operation_updates=None):
        """Issue a new fully synthetic approval chain, only for test controls.

        This explicitly signs NEW statements so policy and semantic assertions
        can be tested after all hash bindings match. It is not evidence repair.
        """
        if policy_updates:
            self.update("policy", **policy_updates)
        op = self.bundle["operation"]
        op.update(operation_updates or {})
        op["policy_digest"] = evidence.digest(self.bundle["evidence"]["policy"])
        request = evidence.synthetic_request_bytes(op)
        op["payload_digest"] = evidence.bytes_digest(request)
        op_ref = evidence.digest(op)
        for name in ("maker_approval", "checker_approval"):
            self.update(name, operation_digest=op_ref, policy_digest=op["policy_digest"])
        self.update("final_status", operation_digest=op_ref, policy_digest=op["policy_digest"],
                    configuration_digest=op["configuration_digest"],
                    recovery_epoch=op["recovery_epoch"], credential_id=op["credential_id"])
        self.update("dispatch", operation_digest=op_ref, policy_digest=op["policy_digest"],
                    actual_operation=copy.deepcopy(op), request_hex=request.hex())
        self.update("provider_receipt", operation_digest=op_ref,
                    payload_digest=op["payload_digest"], api_audience=op["api_audience"])
        for name in ("control", "collector"):
            self.update(name, operation_digest=op_ref,
                        configuration_digest=op["configuration_digest"],
                        recovery_epoch=op["recovery_epoch"])
        self.refresh()

    def test_healthy_evidence_has_four_bounded_claims_and_no_live_admission(self):
        report = self.verify()
        self.assertEqual(set(report["claims"]), {
            "integrity", "authorization", "execution_match", "control_state"})
        self.assertTrue(all(c["verdict"] == "VALID" for c in report["claims"].values()))
        self.assertIs(report["read_only"], True)
        self.assertIs(report["automatic_retry"], False)
        self.assertNotIn("admission", report)
        self.assertEqual(report["outcome"]["status"], "settled")
        self.assertIs(report["outcome"]["settlement_confirmed"], True)

    def test_verification_is_deterministic_and_preserves_all_caller_inputs(self):
        before = copy.deepcopy((self.bundle, self.trust, self.identities))
        first = evidence.canonical_json(self.verify())
        self.assertEqual(first, evidence.canonical_json(self.verify()))
        self.assertEqual(before, (self.bundle, self.trust, self.identities))

    def test_missing_entire_evidence_is_unknown_and_not_settled(self):
        self.bundle["evidence"] = {}
        report = self.verify()
        self.assertTrue(all(c["verdict"] == "INDETERMINATE" for c in report["claims"].values()))
        self.assertIs(report["outcome"]["settlement_confirmed"], False)

    def test_bundle_cannot_choose_its_own_trust(self):
        self.trust = {}
        report = self.verify()
        self.assertTrue(all(c["verdict"] == "INDETERMINATE" for c in report["claims"].values()))
        self.assertIs(report["outcome"]["settlement_confirmed"], False)
        self.bundle["trusted_keys"] = {"attacker": "00" * 32}
        self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_expected_labels_cannot_make_evidence_pass(self):
        self.bundle["expected_verdict"] = "VALID"
        self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_valid_two_signatures_do_not_establish_two_people(self):
        self.reset("same_person")
        maker = self.bundle["evidence"]["maker_approval"]["key_id"]
        checker = self.bundle["evidence"]["checker_approval"]["key_id"]
        self.assertNotEqual(self.trust["approver"][maker], self.trust["approver"][checker])
        self.assertEqual(self.identities[self.trust["approver"][maker].hex()]["person_id"],
                         self.identities[self.trust["approver"][checker].hex()]["person_id"])
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")
        self.assertEqual(self.verdict("execution_match"), "VALID")

    def test_missing_identity_is_unknown_not_proof_of_same_person(self):
        self.identities = {}
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_identity_role_and_scope_are_checked_outside_the_bundle(self):
        for field, value in (("roles", ["checker"]), ("tenant", "another-tenant"),
                             ("environment", "another-environment")):
            with self.subTest(field=field):
                self.reset()
                maker_id = self.bundle["evidence"]["maker_approval"]["key_id"]
                public = self.trust["approver"][maker_id].hex()
                self.identities[public][field] = value
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_signing_key_aliases_cannot_create_a_second_person(self):
        key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        public = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.identities[public.hex()] = {
            "person_id": "one-person-with-two-key-aliases", "roles": ["maker", "checker"],
            "tenant": self.bundle["operation"]["tenant"],
            "environment": self.bundle["operation"]["environment"],
            "valid_from": self.at - 7200, "valid_until": self.at + 7200,
        }
        for name in ("maker_approval", "checker_approval"):
            alias = "alias-for-" + name
            self.trust["approver"][alias] = public
            self.bundle["evidence"][name] = evidence.sign_envelope(
                self.bundle["evidence"][name]["payload"], alias, key)
        self.refresh()
        report = self.verify()
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["authorization"]["verdict"], "INVALID")
        self.assertIn("approvals:same_person", report["claims"]["authorization"]["reasons"])

    def test_each_missing_approval_is_unknown(self):
        for name in ("maker_approval", "checker_approval"):
            with self.subTest(name=name):
                self.reset()
                del self.bundle["evidence"][name]
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_changed_dispatched_operation_can_have_valid_signatures(self):
        for case in ("changed_beneficiary", "changed_amount", "changed_currency",
                     "changed_tenant", "changed_environment"):
            with self.subTest(case=case):
                self.reset(case)
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("authorization"), "INVALID")
                self.assertEqual(self.verdict("execution_match"), "INVALID")

    def test_unchanged_renewed_synthetic_chain_remains_a_healthy_control(self):
        self.reapprove()
        self.assertTrue(all(c["verdict"] == "VALID" for c in self.verify()["claims"].values()))

    def test_amount_limit_is_checked_after_all_authorities_bind_the_same_operation(self):
        amount = int(self.bundle["operation"]["amount_minor"])
        self.reapprove(policy_updates={"max_amount_minor": str(amount - 1)})
        report = self.verify()
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["authorization"]["verdict"], "INVALID")
        self.assertIn("policy:amount_exceeded", report["claims"]["authorization"]["reasons"])
        self.assertEqual(report["claims"]["execution_match"]["verdict"], "VALID")

    def test_exact_operation_fields_are_covered_by_existing_approval(self):
        substitutions = {
            "operation_id": "other-operation", "tenant": "other-tenant",
            "environment": "other-environment", "api_audience": "other-api",
            "principal_id": "other-principal", "credential_id": "other-credential",
            "workload_id": "other-workload", "source_account": "other-source",
            "beneficiary": "other-beneficiary", "idempotency_domain": "other-domain",
            "idempotency_key": "other-idempotency", "configuration_digest": "sha256:" + "ab" * 32,
            "recovery_epoch": 99, "amount_minor": "1", "currency": "JPY",
            "minor_unit_scale": 7, "nonce": "999",
        }
        for field, value in substitutions.items():
            with self.subTest(field=field):
                self.reset()
                self.assertNotEqual(self.bundle["operation"][field], value)
                actual = copy.deepcopy(self.bundle["operation"])
                actual[field] = value
                self.update("dispatch", actual_operation=actual)
                fixtures.refresh_bindings(self.bundle, refresh_request=True)
                report = self.verify()
                self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
                self.assertEqual(report["claims"]["authorization"]["verdict"], "INVALID")
                self.assertEqual(report["claims"]["execution_match"]["verdict"], "INVALID")

    def test_wrong_request_bytes_are_detected_despite_new_execution_signature(self):
        self.update("dispatch", request_hex=b'{"unexpected":"payload"}'.hex())
        self.refresh()
        report = self.verify()
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["authorization"]["verdict"], "INVALID")
        self.assertEqual(report["claims"]["execution_match"]["verdict"], "INVALID")

    def test_matching_byte_digest_does_not_excuse_wrong_synthetic_payload_semantics(self):
        actual = copy.deepcopy(self.bundle["operation"])
        raw = evidence.load_json(evidence.synthetic_request_bytes(actual))
        raw["operation"]["beneficiary"] = "different-wire-beneficiary"
        request = evidence.canonical_json(raw)
        actual["payload_digest"] = evidence.bytes_digest(request)
        self.update("dispatch", actual_operation=actual, request_hex=request.hex())
        self.refresh()
        report = self.verify()
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertIn("dispatch:request_semantics_mismatch",
                      report["claims"]["execution_match"]["reasons"])
        self.assertEqual(report["claims"]["execution_match"]["verdict"], "INVALID")

    def test_revocation_contradicts_authorization_even_with_matching_execution(self):
        self.reset("revoked")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_missing_and_stale_status_remain_unknown(self):
        for case in ("missing_status", "stale_status"):
            with self.subTest(case=case):
                self.reset(case)
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_historical_authorization_is_evaluated_at_dispatch_not_review_time(self):
        report = self.verify(evaluation_time=self.at + 86400)
        self.assertEqual(report["claims"]["authorization"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["control_state"]["verdict"], "VALID")

    def test_identity_must_cover_approval_issuance_as_well_as_dispatch(self):
        dispatched = self.bundle["evidence"]["dispatch"]["payload"]["dispatched_at"]
        for name in ("maker_approval", "checker_approval"):
            with self.subTest(name=name):
                self.reset()
                env = self.bundle["evidence"][name]
                self.assertLess(env["payload"]["issued_at"], dispatched - 1)
                public = self.trust["approver"][env["key_id"]].hex()
                self.identities[public]["valid_from"] = dispatched - 1
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_expired_approval_at_dispatch_is_invalid(self):
        dispatched = self.bundle["evidence"]["dispatch"]["payload"]["dispatched_at"]
        self.update("checker_approval", expires_at=dispatched)
        self.refresh()
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_status_observed_before_approval_cannot_be_its_final_check(self):
        issued = min(self.bundle["evidence"][name]["payload"]["issued_at"]
                     for name in ("maker_approval", "checker_approval"))
        self.update("final_status", checked_at=issued - 1)
        self.refresh()
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_future_observations_do_not_establish_an_outcome_at_the_review_horizon(self):
        self.update("provider_receipt", observed_at=self.at + 1)
        self.refresh()
        report = self.verify()
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["execution_match"]["verdict"], "INDETERMINATE")
        self.assertIs(report["outcome"]["settlement_confirmed"], False)

    def test_future_revocation_does_not_establish_historical_contradiction_until_available(self):
        dispatched = self.bundle["evidence"]["dispatch"]["payload"]["dispatched_at"]
        self.update("final_status", state="revoked", revoked_at=dispatched - 1,
                    checked_at=self.at + 10)
        self.refresh()
        before = self.verify()
        self.assertEqual(before["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(before["claims"]["authorization"]["verdict"], "INDETERMINATE")
        self.assertIn("final_status", {item["record"] for item in before["excluded_after_horizon"]})
        after = self.verify(evaluation_time=self.at + 11)
        self.assertEqual(after["claims"]["authorization"]["verdict"], "INVALID")

    def test_future_control_and_recovery_contradictions_are_not_used_before_horizon(self):
        for name in ("control", "collector"):
            with self.subTest(name=name):
                self.reset()
                if name == "control":
                    routes = copy.deepcopy(self.bundle["evidence"][name]["payload"]["routes"])
                    routes["cloud_management"] = "bypassed"
                    self.update(name, routes=routes, observed_at=self.at + 10)
                else:
                    old_epoch = self.bundle["operation"]["recovery_epoch"] - 1
                    self.update(name, recovery_epoch=old_epoch, checkpoint_at=self.at + 10)
                self.refresh()
                before = self.verify()
                self.assertEqual(before["claims"]["integrity"]["verdict"], "VALID")
                self.assertEqual(before["claims"]["control_state"]["verdict"], "INDETERMINATE")
                self.assertIn(name, {item["record"] for item in before["excluded_after_horizon"]})
                after = self.verify(evaluation_time=self.at + 11)
                self.assertEqual(after["claims"]["control_state"]["verdict"], "INVALID")

    def test_observed_bypass_and_missing_coverage_are_different(self):
        self.reset("bypass")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("control_state"), "INVALID")
        self.reset("missing_route")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("control_state"), "INDETERMINATE")

    def test_ambiguous_acknowledgment_never_authorizes_a_retry(self):
        for case in ("lost_ack", "http_only"):
            with self.subTest(case=case):
                self.reset(case)
                first = self.verify()
                self.assertEqual(first["claims"]["execution_match"]["verdict"], "INDETERMINATE")
                self.assertEqual(first, self.verify())
                self.assertIs(first["automatic_retry"], False)
                self.assertIs(first["read_only"], True)
                self.assertIs(first["outcome"]["settlement_confirmed"], False)

    def test_assessment_does_not_use_network_subprocess_clock_or_report_writes(self):
        self.reset("lost_ack")
        with mock.patch("socket.socket", side_effect=AssertionError("network attempted")), \
             mock.patch("subprocess.Popen", side_effect=AssertionError("subprocess attempted")), \
             mock.patch("time.time", side_effect=AssertionError("implicit clock read")), \
             mock.patch.object(Path, "write_bytes", side_effect=AssertionError("file write")), \
             mock.patch.object(Path, "write_text", side_effect=AssertionError("file write")):
            self.assertEqual(self.verdict("execution_match"), "INDETERMINATE")

    def test_altered_replay_is_a_binding_failure_not_duplicate_suppression(self):
        self.reset("altered_replay")
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("execution_match"), "INVALID")
        self.assertIs(self.verify()["automatic_retry"], False)

    def test_authentic_receipt_for_other_operation_does_not_establish_settlement(self):
        self.reset("wrong_receipt")
        report = self.verify()
        self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
        self.assertEqual(report["claims"]["execution_match"]["verdict"], "INVALID")
        self.assertEqual(report["outcome"]["status"], "unknown")
        self.assertIs(report["outcome"]["settlement_confirmed"], False)

    def test_provider_receipt_binds_payload_audience_provider_dispatch_and_time(self):
        dispatched = self.bundle["evidence"]["dispatch"]["payload"]["dispatched_at"]
        for field, value in (("payload_digest", "sha256:" + "ab" * 32),
                             ("api_audience", "different-audience"),
                             ("provider_id", "different-provider"),
                             ("dispatch_digest", "sha256:" + "cd" * 32),
                             ("observed_at", dispatched - 1)):
            with self.subTest(field=field):
                self.reset()
                self.update("provider_receipt", **{field: value})
                report = self.verify()
                self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
                self.assertEqual(report["claims"]["execution_match"]["verdict"], "INVALID")
                self.assertIs(report["outcome"]["settlement_confirmed"], False)

    def test_provider_acceptance_and_pending_are_not_settlement(self):
        for status in ("accepted", "pending"):
            with self.subTest(status=status):
                self.reset(status)
                report = self.verify()
                self.assertEqual(report["claims"]["execution_match"]["verdict"], "INDETERMINATE")
                self.assertEqual(report["outcome"]["status"], status)
                self.assertIs(report["outcome"]["settlement_confirmed"], False)

    def test_matching_failure_or_reversal_is_not_a_successful_payment(self):
        for status in ("failed", "reversed"):
            with self.subTest(status=status):
                self.reset(status)
                report = self.verify()
                self.assertEqual(report["claims"]["execution_match"]["verdict"], "VALID")
                self.assertEqual(report["outcome"]["status"], status)
                self.assertIs(report["outcome"]["settlement_confirmed"], False)

    def test_collector_gap_is_unknown_and_epoch_or_checkpoint_mismatch_invalid(self):
        for case, expected in (("collector_gap", "INDETERMINATE"),
                               ("old_epoch", "INVALID"),
                               ("checkpoint_mismatch", "INVALID")):
            with self.subTest(case=case):
                self.reset(case)
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("control_state"), expected)

    def test_collector_must_bind_records_that_existed_before_the_checkpoint(self):
        dispatched = self.bundle["evidence"]["dispatch"]["payload"]["dispatched_at"]
        self.update("collector", checkpoint_at=dispatched - 1)
        self.assertEqual(self.verdict("integrity"), "VALID")
        self.assertEqual(self.verdict("control_state"), "INVALID")

    def test_control_epoch_configuration_and_route_scope_are_checked(self):
        for field, value in (("configuration_digest", "sha256:" + "ee" * 32),
                             ("recovery_epoch", 999)):
            with self.subTest(field=field):
                self.reset()
                self.update("control", **{field: value})
                self.refresh()
                self.assertEqual(self.verdict("integrity"), "VALID")
                self.assertEqual(self.verdict("control_state"), "INVALID")
        self.reset()
        routes = copy.deepcopy(self.bundle["evidence"]["control"]["payload"]["routes"])
        routes["unknown-extra-path"] = "blocked"
        self.update("control", routes=routes)
        self.refresh()
        self.assertEqual(self.verdict("control_state"), "INDETERMINATE")

    def test_control_for_intended_runtime_cannot_validate_changed_actual_runtime(self):
        for field, value in (("configuration_digest", "sha256:" + "dd" * 32),
                             ("recovery_epoch", 999)):
            with self.subTest(field=field):
                self.reset()
                actual = copy.deepcopy(self.bundle["operation"])
                actual[field] = value
                self.update("dispatch", actual_operation=actual)
                fixtures.refresh_bindings(self.bundle, refresh_request=True)
                report = self.verify()
                self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
                self.assertEqual(report["claims"]["control_state"]["verdict"], "INVALID")
                self.assertIn("control:actual_" + field + "_scope_mismatch",
                              report["claims"]["control_state"]["reasons"])

    def test_each_dispatch_ref_binds_the_exact_supplied_signed_record(self):
        for field in ("policy_digest", "final_status_digest", "control_digest"):
            with self.subTest(field=field):
                self.reset()
                self.update("dispatch", **{field: "sha256:" + "ab" * 32})
                report = self.verify()
                self.assertEqual(report["claims"]["integrity"]["verdict"], "VALID")
                self.assertEqual(report["claims"]["execution_match"]["verdict"], "INVALID")
        for name in ("maker_approval", "checker_approval"):
            with self.subTest(name=name):
                self.reset()
                refs = copy.deepcopy(self.bundle["evidence"]["dispatch"]["payload"]["approval_digests"])
                refs[name] = "sha256:" + "ab" * 32
                self.update("dispatch", approval_digests=refs)
                self.assertEqual(self.verdict("authorization"), "INVALID")

    def test_record_from_another_run_or_kind_is_not_reusable(self):
        for field, value in (("run_id", "other-run"), ("kind", "checker_approval")):
            with self.subTest(field=field):
                self.reset()
                self.update("maker_approval", **{field: value})
                report = self.verify()
                self.assertEqual(report["claims"]["integrity"]["verdict"], "INVALID")
                self.assertEqual(report["claims"]["authorization"]["verdict"], "INDETERMINATE")

    def test_key_identifier_is_signed_even_when_alias_has_same_public_key(self):
        env = self.bundle["evidence"]["maker_approval"]
        original = self.trust["approver"][env["key_id"]]
        self.trust["approver"]["alias"] = original
        env["key_id"] = "alias"
        self.assertEqual(self.verdict("integrity"), "INVALID")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_each_envelope_signature_is_actually_verified(self):
        for name in tuple(self.bundle["evidence"]):
            with self.subTest(name=name):
                self.reset()
                env = self.bundle["evidence"][name]
                old = env["signature"]
                env["signature"] = ("0" if old[0] != "0" else "1") + old[1:]
                self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_unverified_claim_does_not_establish_revocation(self):
        self.reset("revoked")
        env = self.bundle["evidence"]["final_status"]
        old = env["signature"]
        env["signature"] = ("0" if old[0] != "0" else "1") + old[1:]
        self.assertEqual(self.verdict("integrity"), "INVALID")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_verified_revocation_is_not_erased_by_missing_receipt(self):
        self.reset("revoked")
        del self.bundle["evidence"]["provider_receipt"]
        self.assertEqual(self.verdict("authorization"), "INVALID")
        self.assertEqual(self.verdict("execution_match"), "INDETERMINATE")

    def test_signature_encoding_is_checked_before_unknown_trust(self):
        self.bundle["evidence"]["maker_approval"].update(key_id="untrusted", signature=42)
        self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_key_trusted_for_policy_cannot_sign_a_business_approval(self):
        # A valid signature with an unrelated caller-trusted role is still not
        # a trusted approval. This fresh public test key is not a fixture key.
        key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        public = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        self.trust["policy_authority"]["policy-only-test-key"] = public
        original = self.bundle["evidence"]["maker_approval"]["payload"]
        self.bundle["evidence"]["maker_approval"] = evidence.sign_envelope(
            original, "policy-only-test-key", key)
        self.assertEqual(self.verdict("integrity"), "INDETERMINATE")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_wallet_signature_domain_is_not_accepted_as_payment_evidence(self):
        key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
        public = key.public_key().public_bytes(
            serialization.Encoding.Raw, serialization.PublicFormat.Raw)
        env = self.bundle["evidence"]["maker_approval"]
        self.trust["approver"][env["key_id"]] = public
        signed = {"key_id": env["key_id"], "payload": env["payload"]}
        env["signature"] = key.sign(
            b"VSO experimental wallet evidence v0\x00" + evidence.canonical_json(signed)).hex()
        self.assertEqual(self.verdict("integrity"), "INVALID")
        self.assertEqual(self.verdict("authorization"), "INDETERMINATE")

    def test_envelope_cannot_inject_a_public_key_or_signature_valid_flag(self):
        for field, value in (("public_key", "00" * 32), ("signature_valid", True)):
            with self.subTest(field=field):
                self.reset()
                self.bundle["evidence"]["maker_approval"][field] = value
                self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_unrecognized_signed_evidence_fields_fail_closed(self):
        for name in tuple(self.bundle["evidence"]):
            with self.subTest(name=name):
                self.reset()
                self.update(name, unexpected=True)
                report = self.verify()
                self.assertFalse(all(c["verdict"] == "VALID" for c in report["claims"].values()))

    def test_malformed_signed_fields_cannot_crash_or_produce_overall_validity(self):
        # Mutate one field at a time and sign the malformed statement afresh;
        # a signature must never substitute for schema validation.
        original = copy.deepcopy(self.bundle)
        for name, env in original["evidence"].items():
            for field, value in env["payload"].items():
                with self.subTest(name=name, field=field):
                    self.reset()
                    self.update(name, **{field: [] if type(value) is dict else {}})
                    report = self.verify()
                    self.assertFalse(all(c["verdict"] == "VALID"
                                         for c in report["claims"].values()))

    def test_claim_references_resolve_to_exact_signed_envelopes(self):
        refs = {evidence.digest(env) for env in self.bundle["evidence"].values()}
        report = self.verify()
        for name, claim in report["claims"].items():
            with self.subTest(name=name):
                self.assertTrue(claim["evidence_refs"])
                self.assertTrue(set(claim["evidence_refs"]).issubset(refs))
                self.assertTrue(claim["reasons"])

    def test_unknown_operation_field_cannot_be_excluded_from_binding(self):
        self.bundle["operation"]["unreviewed_destination"] = "hidden-beneficiary"
        self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_amount_unit_and_epoch_types_cannot_exploit_boolean_or_float_coercion(self):
        for field, value in (("amount_minor", 100), ("amount_minor", "1.0"),
                             ("amount_minor", "01"), ("amount_minor", "-1"),
                             ("amount_minor", "9" * 79), ("minor_unit_scale", True),
                             ("recovery_epoch", True), ("valid_from", True),
                             ("operation_id", "x" * 257)):
            with self.subTest(field=field, value=value):
                self.reset()
                self.bundle["operation"][field] = value
                self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_boolean_signed_timestamp_is_not_an_integer_timestamp(self):
        for name, field in (("maker_approval", "issued_at"), ("final_status", "checked_at"),
                             ("dispatch", "dispatched_at"), ("provider_receipt", "observed_at"),
                             ("collector", "checkpoint_at")):
            with self.subTest(name=name, field=field):
                self.reset()
                self.update(name, **{field: True})
                self.assertEqual(self.verdict("integrity"), "INVALID")

    def test_caller_time_and_freshness_limit_are_explicit_strict_integers(self):
        for at in (True, -1, 1.0, "100"):
            with self.subTest(at=at), self.assertRaises(ValueError):
                self.verify(evaluation_time=at)
        for age in (True, 0, -1, 1.0, "300"):
            with self.subTest(age=age), self.assertRaises(ValueError):
                self.verify(max_snapshot_age=age)

    def test_parser_rejects_ambiguous_or_noncanonical_values(self):
        for raw in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}',
                    '{"a":1.0}', '{"a":9007199254740992}'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                evidence.load_json(raw)
        for value in ({"text": "e\u0301"}, {"float": 1.5}, {1: "nonstring key"}):
            with self.subTest(value=value), self.assertRaises(ValueError):
                evidence.canonical_json(value)

    def test_deep_untrusted_input_returns_failure_without_recursion_crash(self):
        nested = {}
        for _ in range(1200):
            nested = {"child": nested}
        self.bundle["extra"] = nested
        self.assertEqual(self.verdict("integrity"), "INVALID")
        with self.assertRaises(ValueError):
            evidence.load_json("[" * 1200 + "0" + "]" * 1200)

    def test_cli_requires_external_trust_and_identity_and_creates_no_files(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            bundle_path = base / "bundle.json"
            trust_path = base / "trust.json"
            identities_path = base / "identities.json"
            bundle_path.write_bytes(evidence.canonical_json(self.bundle))
            trust_path.write_bytes(evidence.canonical_json({
                role: {key: public.hex() for key, public in keys.items()}
                for role, keys in self.trust.items()}))
            identities_path.write_bytes(evidence.canonical_json(self.identities))
            command = [sys.executable, str(HERE / "payment_evidence.py"),
                       "--bundle", str(bundle_path), "--trust", str(trust_path),
                       "--identities", str(identities_path), "--at", str(self.at)]
            env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            first = subprocess.run(command, capture_output=True, env=env, check=False)
            second = subprocess.run(command, capture_output=True, env=env, check=False)
            self.assertEqual(first.returncode, 0, first.stderr.decode())
            self.assertEqual(first.stdout, second.stdout)
            self.assertIs(json.loads(first.stdout)["read_only"], True)
            self.assertEqual(sorted(path.name for path in base.iterdir()),
                             ["bundle.json", "identities.json", "trust.json"])
            identities_path.write_text("{}", encoding="utf-8")
            incomplete = subprocess.run(command, capture_output=True, env=env, check=False)
            self.assertEqual(incomplete.returncode, 2, incomplete.stderr.decode())
            self.assertEqual(json.loads(incomplete.stdout)["claims"]["authorization"]["verdict"],
                             "INDETERMINATE")


if __name__ == "__main__":
    unittest.main()
