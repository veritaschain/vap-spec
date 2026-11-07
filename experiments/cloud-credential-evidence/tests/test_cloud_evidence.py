"""Adversarial checks for the limited CE proposal, using public synthetic keys.

Expected distinctions are declared here and in fixtures.py, independently of the
verifier. Semantic mutations are freshly signed and all dependent commitments
are recomputed. Passing these checks is neither live-cloud validation nor a
prevention, conformance, independent-custody or universal-completeness result.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

EXPERIMENT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXPERIMENT))
import cloud_evidence as core
import fixtures as f


def evaluate(case, *, bundle=None):
    return core.verify_bundle(f.seal_bundle(case) if bundle is None else bundle,
                              copy.deepcopy(case["trust"]), scope=copy.deepcopy(case["scope"]),
                              evaluation_time=case["evaluation_time"])


def move_resource(case, seconds, *, raw_time=None):
    f.payload(case, "resource-1").update(event_time=seconds, available_time=seconds + 1,
                                        received_time=seconds + 2)
    f.change_native(case, "resource-1", lambda raw: raw.update(
        time=f.iso(seconds) if raw_time is None else raw_time))


class EvidenceCase(unittest.TestCase):
    def assert_status(self, report, claim, expected):
        self.assertEqual(expected, report["claims"][claim]["status"],
                         (claim, report["claims"][claim]))

    def record(self, report, record_id):
        return next(record for record in report["records"] if record["record_id"] == record_id)

    def assert_all_signatures(self, report):
        self.assertTrue(report["records"])
        for record in report["records"]:
            self.assertEqual("supported", record["signature_status"], record["record_id"])

    def assert_boundaries(self, report):
        for name in ("external_exfiltration", "global_containment", "ai_orchestration"):
            self.assert_status(report, name, "unresolved")
        for misleading in ("safe", "pass", "prevented", "conformant", "overall_success"):
            self.assertNotIn(misleading, report)


class RepresentativeCases(EvidenceCase):
    def test_ten_proposal_distinctions_execute_with_actual_results(self):
        results = f.run_cases(core.verify_bundle)
        self.assertEqual(["CE-%02d" % n for n in range(1, 11)],
                         [item["case_id"] for item in results["results"]])
        self.assertEqual(10, results["acceptance_cases_executed"])
        self.assertEqual(0, results["expectation_mismatch_count"],
                         [(item["case_id"], item["expectation_mismatches"])
                          for item in results["results"] if item["expectation_mismatches"]])
        for item in results["results"]:
            self.assert_boundaries(item["actual_report"])

    def test_positive_control_supports_only_declared_claims(self):
        case = f.positive_case()
        report = evaluate(case)
        for name in case["expected"]:
            self.assert_status(report, name, "supported")
        self.assert_all_signatures(report)
        self.assert_boundaries(report)
        # Resource and binding receipts occur after action; retrospective support
        # must not impose their arrival on the selected pre-action prerequisites.
        self.assertGreater(self.record(report, "resource-1")["received_time"], case["scope"]["action_time"])
        self.assertEqual(2, len(report["timing_observations"]))

    def test_fixture_signatures_and_original_byte_commitments_are_independent(self):
        case = f.positive_case()
        for envelope in f.seal_bundle(case)["records"]:
            key = Ed25519PublicKey.from_public_bytes(bytes.fromhex(
                case["trust"]["keys"][envelope["key_id"]]["public_key"]))
            signed = {key: envelope[key] for key in ("key_id", "payload")}
            key.verify(bytes.fromhex(envelope["signature"]), f.SIGNING_DOMAIN + f.canonical(signed))
            body = envelope["payload"]["body"]
            if envelope["payload"]["kind"] == "native":
                self.assertEqual(f.bytes_hash(body["raw"].encode("utf-8")), body["raw_sha256"])
                self.assertNotEqual(f.canonical(json.loads(body["raw"])), body["raw"].encode("utf-8"))


class IntegrityAndTrust(EvidenceCase):
    def test_raw_whitespace_tamper_is_detected_after_valid_resigning(self):
        case = f.positive_case()
        body = f.payload(case, "resource-1")["body"]
        body["raw"] += " "  # Same JSON value, different original bytes; digest intentionally stale.
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "integrity", "contradicted")
        self.assertEqual("contradicted", self.record(report, "resource-1")["commitment_status"])

    def test_raw_semantic_tamper_does_not_use_stale_commitment(self):
        case = f.positive_case()
        f.change_native(case, "resource-1", lambda raw: raw.update(operationName="VaultGet"),
                        refresh_commitment=False)
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "integrity", "contradicted")
        self.assertNotEqual("supported", report["claims"]["operation"]["status"])

    def test_claimed_normalized_mapping_cannot_override_original(self):
        case = f.positive_case()
        f.payload(case, "resource-1")["body"]["claimed_normalized"] = {"operation": "SecretGet"}
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assertEqual("contradicted", self.record(report, "resource-1")["commitment_status"])
        self.assert_status(report, "integrity", "contradicted")

    def test_signature_bit_flip_is_a_contradiction(self):
        case = f.positive_case()
        bundle = f.seal_bundle(case)
        signature = bundle["records"][0]["signature"]
        bundle["records"][0]["signature"] = ("00" if signature[:2] != "00" else "01") + signature[2:]
        report = evaluate(case, bundle=bundle)
        self.assert_status(report, "integrity", "contradicted")
        self.assertEqual("contradicted", self.record(report, "signin-1")["signature_status"])

    def test_wrong_public_key_and_unknown_key_have_distinct_results(self):
        for known, expected in ((True, "contradicted"), (False, "unresolved")):
            with self.subTest(known=known):
                case = f.positive_case()
                key_id = f.KEY_IDS["policy_authority"]
                if known:
                    case["trust"]["keys"][key_id]["public_key"] = f.public_key("collector")
                else:
                    del case["trust"]["keys"][key_id]
                report = evaluate(case)
                self.assertEqual(expected, self.record(report, "permission-1")["signature_status"])
                self.assert_status(report, "authority", "unresolved")

    def test_each_trust_scope_dimension_is_required_despite_valid_signature(self):
        for field, replacement in (("issuer", "different-issuer"), ("role", "collector"),
                                   ("tenant_id", f.TENANT_B), ("resource_id", f.VAULT_B)):
            with self.subTest(field=field):
                case = f.positive_case()
                case["trust"]["keys"][f.KEY_IDS["policy_authority"]]["grants"][0][field] = replacement
                report = evaluate(case)
                self.assert_all_signatures(report)
                self.assert_status(report, "provenance", "unresolved")
                self.assert_status(report, "authority", "unresolved")

    def test_key_grant_is_checked_at_asserted_receipt(self):
        case = f.positive_case()
        case["trust"]["keys"][f.KEY_IDS["policy_authority"]]["grants"][0]["valid_until"] = f.BASE + 15
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assertEqual("unresolved", self.record(report, "permission-1")["authority_status"])
        self.assert_status(report, "authority", "unresolved")

    def test_record_role_cannot_be_promoted_by_a_matching_grant(self):
        case = f.positive_case()
        p = f.payload(case, "permission-1")
        p["role"] = "collector"
        case["trust"]["keys"][f.KEY_IDS["policy_authority"]]["grants"][0]["role"] = "collector"
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assertEqual("contradicted", self.record(report, "permission-1")["authority_status"])
        self.assert_status(report, "provenance", "contradicted")


class IdentityAndBindings(EvidenceCase):
    def test_workspace_id_does_not_replace_missing_identity_tenant(self):
        case = f.positive_case()
        def change(raw):
            raw.pop("AADTenantId")
            raw["TenantId"] = f.TENANT_A
        f.change_native(case, "signin-1", change)
        report = evaluate(case)
        native = self.record(report, "signin-1")["normalized"]
        self.assertIsNone(native["tenant_id"])
        self.assertEqual(f.TENANT_A, native["workspace_id"])
        self.assert_status(report, "authentication", "unresolved")
        self.assert_status(report, "association", "unresolved")

    def test_same_app_id_does_not_merge_tenant_local_principals(self):
        case = f.acceptance_cases()[2]
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "association", "contradicted")
        native = self.record(report, "signin-1")["normalized"]
        self.assertEqual(f.APP_ID, native["app_id"])
        self.assertEqual(f.TENANT_B, native["tenant_id"])
        self.assertEqual(f.PRINCIPAL_B, native["principal_id"])

    def test_each_signin_target_mapping_dimension_is_bound(self):
        for field in ("ResourceIdentity", "ResourceOwnerTenantId", "ResourceServicePrincipalId"):
            with self.subTest(field=field):
                case = f.positive_case()
                f.change_native(case, "signin-1", lambda raw: raw.update({field: "synthetic-graph-target"}))
                report = evaluate(case)
                self.assert_all_signatures(report)
                self.assert_status(report, "association", "contradicted")
                self.assert_status(report, "authentication", "supported")

    def test_missing_signin_target_mapping_or_native_field_stays_unknown(self):
        for source in ("configuration", "ResourceIdentity", "ResourceOwnerTenantId", "ResourceServicePrincipalId"):
            with self.subTest(source=source):
                case = f.positive_case()
                if source == "configuration":
                    case["scope"]["sign_in_resource"] = None
                else:
                    f.change_native(case, "signin-1", lambda raw: raw.pop(source))
                self.assert_status(evaluate(case), "association", "unresolved")

    def test_bound_native_app_id_mismatch_is_not_hidden_by_matching_principal(self):
        case = f.positive_case()
        f.change_native(case, "resource-1", lambda raw: raw["identity"]["claim"].update(appid="synthetic-other-app"))
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "association", "contradicted")

    def test_missing_keyvault_tenant_or_object_is_not_invented(self):
        for field in ("tid", "oid"):
            with self.subTest(field=field):
                case = f.positive_case()
                f.change_native(case, "resource-1", lambda raw: raw["identity"]["claim"].pop(field))
                report = evaluate(case)
                self.assert_status(report, "association", "unresolved")
                self.assert_status(report, "operation", "unresolved")

    def test_documented_identity_alias_and_conflicting_aliases(self):
        alias = "http://schemas.microsoft.com/identity/claims/objectidentifier"
        case = f.positive_case()
        def replace(raw):
            claim = raw["identity"]["claim"]
            claim[alias] = claim.pop("oid")
        f.change_native(case, "resource-1", replace)
        self.assert_status(evaluate(case), "operation", "supported")
        f.change_native(case, "resource-1", lambda raw: raw["identity"]["claim"].update(oid=f.PRINCIPAL_B))
        report = evaluate(case)
        self.assert_status(report, "operation", "contradicted")
        self.assert_status(report, "provenance", "contradicted")

    def test_matching_correlation_and_ip_do_not_supply_missing_binding(self):
        case = f.positive_case()
        f.drop_record(case, "binding-1")
        report = evaluate(case)
        self.assert_status(report, "authentication", "supported")
        self.assert_status(report, "association", "unresolved")
        self.assert_status(report, "operation", "unresolved")

    def test_exact_secret_uri_is_separate_from_vault_arm_id(self):
        for uri, expected in ((f.OTHER_SECRET_URI, "contradicted"), (None, "unresolved")):
            with self.subTest(uri=uri):
                case = f.positive_case()
                def change(raw):
                    if uri is None:
                        raw["properties"].pop("requestUri")
                    else:
                        raw["properties"]["requestUri"] = uri
                f.change_native(case, "resource-1", change)
                report = evaluate(case)
                self.assert_status(report, "operation", expected)
                self.assertEqual(f.VAULT_A, self.record(report, "resource-1")["normalized"]["resource_id"])


class AuthorityAndNativeOperations(EvidenceCase):
    def test_explicit_denial_survives_missing_resource_and_collection_evidence(self):
        case = f.positive_case()
        f.payload(case, "permission-1")["body"]["decision"] = "deny"
        f.drop_record(case, "resource-1")
        f.drop_record(case, "collection-1")
        report = evaluate(case)
        self.assert_status(report, "authority", "contradicted")
        self.assert_status(report, "operation", "unresolved")
        self.assert_status(report, "coverage", "unresolved")

    def test_permission_subject_audience_action_and_exact_target_are_bound(self):
        for field, value in (("principal_id", f.PRINCIPAL_B), ("audience", "https://graph.invalid"),
                             ("action", "VaultGet"), ("request_uri", f.OTHER_SECRET_URI)):
            with self.subTest(field=field):
                case = f.positive_case()
                f.payload(case, "permission-1")["body"][field] = value
                report = evaluate(case)
                self.assert_all_signatures(report)
                self.assert_status(report, "authority", "contradicted")

    def test_permission_for_different_attempt_or_operation_is_not_reused(self):
        for field in ("attempt_id", "operation_id"):
            with self.subTest(field=field):
                case = f.positive_case()
                f.payload(case, "permission-1")["body"][field] = "another-synthetic-" + field
                self.assert_status(evaluate(case), "authority", "unresolved")

    def test_actual_operation_after_permission_expiry_is_not_backdated_to_checkpoint(self):
        case = f.positive_case()
        f.payload(case, "permission-1")["body"]["valid_until"] = f.BASE + 21
        move_resource(case, f.BASE + 22)
        f.payload(case, "binding-1").update(available_time=f.BASE + 24, received_time=f.BASE + 25)
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "operation", "supported")
        self.assert_status(report, "authority", "contradicted")

    def test_actual_operation_before_policy_decision_cannot_be_retroactively_allowed(self):
        case = f.positive_case()
        move_resource(case, f.BASE + 14)
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "authority", "contradicted")

    def test_unknown_native_operation_time_does_not_inherit_collector_time(self):
        case = f.positive_case()
        f.change_native(case, "resource-1", lambda raw: raw.pop("time"))
        report = evaluate(case)
        self.assertIsNone(self.record(report, "resource-1")["normalized"]["source_time"])
        self.assert_status(report, "operation", "unresolved")
        self.assert_status(report, "authority", "unresolved")

    def test_control_plane_metadata_200_is_not_secret_content(self):
        report = evaluate(f.acceptance_cases()[5])
        self.assert_all_signatures(report)
        self.assert_status(report, "operation", "contradicted")
        self.assert_status(report, "association", "contradicted")
        self.assert_boundaries(report)

    def test_supplied_method_and_api_plane_cannot_contradict_secret_get(self):
        for field, value in (("method", "POST"), ("method", "DELETE"), ("api_plane", "control")):
            with self.subTest(field=field, value=value):
                case = f.positive_case()
                f.payload(case, "binding-1")["body"][field] = value
                report = evaluate(case)
                self.assert_all_signatures(report)
                self.assert_status(report, "operation", "contradicted")

    def test_missing_method_is_not_filled_as_a_provider_native_field(self):
        case = f.positive_case()
        f.payload(case, "binding-1")["body"]["method"] = None
        report = evaluate(case)
        self.assertIsNone(report["attempts"][0]["request_context"]["method"])
        native = self.record(report, "resource-1")["normalized"]
        self.assertIsNone(native["method"])
        self.assertIsNone(native["api_plane"])

    def test_native_result_channels_cannot_hide_explicit_failure(self):
        for adapter, record_id in ((f.SIGNIN_ADAPTER, "signin-1"), (f.KEYVAULT_ADAPTER, "resource-1")):
            with self.subTest(adapter=adapter):
                case = f.positive_case()
                if adapter == f.SIGNIN_ADAPTER:
                    f.change_native(case, record_id, lambda raw: raw.update(ResultSignature="700016"))
                    claim = "authentication"
                else:
                    def change(raw):
                        raw["resultSignature"] = "Forbidden"
                        raw["properties"].pop("httpStatusCode")
                    f.change_native(case, record_id, change)
                    claim = "operation"
                report = evaluate(case)
                self.assert_all_signatures(report)
                self.assert_status(report, claim, "contradicted")
                self.assertTrue(self.record(report, record_id)["normalized"]["status_conflict"])

    def test_signin_numeric_result_type_is_not_documented_success(self):
        case = f.positive_case()
        f.change_native(case, "signin-1", lambda raw: raw.update(ResultType="0"))
        self.assert_status(evaluate(case), "authentication", "unresolved")

    def test_202_and_204_do_not_establish_secret_content_read(self):
        for status, label in ((202, "Accepted"), (204, "No Content")):
            with self.subTest(status=status):
                case = f.positive_case()
                def change(raw):
                    raw["resultSignature"] = label
                    raw["properties"]["httpStatusCode"] = status
                f.change_native(case, "resource-1", change)
                self.assert_status(evaluate(case), "operation", "unresolved")

    def test_unknown_native_http_vocabulary_does_not_assert_success(self):
        case = f.positive_case()
        def change(raw):
            raw["resultSignature"] = "synthetic-unrecognized-status"
            raw["properties"].pop("httpStatusCode")
        f.change_native(case, "resource-1", change)
        self.assert_status(evaluate(case), "operation", "unresolved")

    def test_http_result_signature_is_preserved_separately_from_crypto(self):
        report = evaluate(f.positive_case())
        record = self.record(report, "resource-1")
        self.assertEqual("OK", record["normalized"]["result_signature"])
        self.assertEqual(200, record["normalized"]["http_status"])
        self.assertEqual("supported", record["signature_status"])


class TimingCoverageAndHistory(EvidenceCase):
    def test_late_or_unknown_permission_availability_does_not_become_timely(self):
        for availability, receipt, expected in ((f.BASE + 35, f.BASE + 40, "contradicted"),
                                                (None, f.BASE + 16, "unresolved"),
                                                (None, f.BASE + 40, "contradicted")):
            with self.subTest(availability=availability):
                case = f.positive_case()
                f.payload(case, "permission-1").update(available_time=availability, received_time=receipt)
                report = evaluate(case)
                self.assert_status(report, "timing", expected)
                self.assert_status(report, "operation", "supported")

    def test_empty_prerequisite_set_does_not_prove_pre_action_availability(self):
        case = f.positive_case()
        case["scope"]["prerequisite_record_ids"] = []
        self.assert_status(evaluate(case), "timing", "unresolved")

    def test_outcome_record_cannot_be_declared_a_pre_action_prerequisite(self):
        case = f.positive_case()
        case["scope"]["prerequisite_record_ids"].append("resource-1")
        self.assert_status(evaluate(case), "timing", "contradicted")

    def test_non_prerequisite_impossible_clock_order_is_not_semantically_eligible(self):
        for updates in ({"available_time": f.BASE + 19},
                        {"available_time": f.BASE + 25, "received_time": f.BASE + 22},
                        {"event_time": f.BASE + 24, "available_time": f.BASE + 21}):
            with self.subTest(updates=updates):
                case = f.positive_case()
                f.payload(case, "resource-1").update(updates)
                report = evaluate(case)
                self.assert_status(report, "temporal_consistency", "contradicted")
                self.assertEqual("contradicted", self.record(report, "resource-1")["temporal_status"])
                self.assertFalse(self.record(report, "resource-1")["eligible"])
                self.assertNotEqual("supported", report["claims"]["operation"]["status"])

    def test_subsecond_native_timestamp_is_not_truncated_at_authorization_boundary(self):
        case = f.positive_case()
        f.payload(case, "permission-1")["body"]["valid_until"] = f.BASE + 20
        native_time = f.iso(f.BASE + 20).replace("Z", ".0000001Z")
        move_resource(case, f.BASE + 20, raw_time=native_time)
        report = evaluate(case)
        self.assertEqual(native_time, self.record(report, "resource-1")["normalized"]["source_time"])
        self.assert_status(report, "authority", "contradicted")

    def test_source_event_100ns_after_horizon_cannot_be_used(self):
        case = f.positive_case()
        case["evaluation_time"] = f.BASE + 100
        native_time = f.iso(f.BASE + 100).replace("Z", ".0000001Z")
        move_resource(case, f.BASE + 100, raw_time=native_time)
        # The claimed receipt is at the horizon; this is also an impossible
        # temporal order. Neither condition can be rounded into eligibility.
        f.payload(case, "resource-1").update(available_time=f.BASE + 100, received_time=f.BASE + 100)
        report = evaluate(case)
        self.assertFalse(self.record(report, "resource-1")["eligible"])
        self.assertNotEqual("supported", report["claims"]["operation"]["status"])

    def test_later_evaluation_can_admit_received_retrospective_evidence(self):
        case = f.positive_case()
        case["evaluation_time"] = f.BASE + 21
        early = evaluate(case)
        self.assert_status(early, "operation", "unresolved")
        self.assert_status(early, "coverage", "unresolved")
        case["evaluation_time"] = f.BASE + 100
        later = evaluate(case)
        self.assert_status(later, "operation", "supported")
        self.assert_status(later, "coverage", "supported")
        self.assert_boundaries(later)

    def test_binding_cannot_reference_an_envelope_received_after_its_own_receipt(self):
        case = f.positive_case()
        f.payload(case, "resource-1")["received_time"] = f.BASE + 80
        # Keep the later collection feasible so the binding chronology itself
        # supplies the association contradiction.
        f.payload(case, "collection-1")["received_time"] = f.BASE + 90
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "association", "contradicted")

    def test_collection_cannot_reference_an_envelope_received_after_collection_receipt(self):
        case = f.positive_case()
        f.payload(case, "resource-1")["received_time"] = f.BASE + 80
        f.payload(case, "binding-1")["received_time"] = f.BASE + 82
        # The association is now chronologically possible; collection receipt
        # remains 72 and cannot already commit to these exact later envelopes.
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "association", "supported")
        self.assert_status(report, "coverage", "contradicted")

    def test_delayed_reference_chain_supports_retrospective_claims_when_receipts_are_ordered(self):
        case = f.positive_case()
        f.payload(case, "resource-1")["received_time"] = f.BASE + 80
        f.payload(case, "binding-1")["received_time"] = f.BASE + 82
        f.payload(case, "collection-1")["received_time"] = f.BASE + 90
        # Keep source event/availability times unchanged: those times do not
        # assert publication of the complete retrospective signed wrappers.
        report = evaluate(case)
        self.assert_all_signatures(report)
        for claim in ("operation", "association", "coverage", "timing"):
            self.assert_status(report, claim, "supported")
        self.assert_boundaries(report)

    def test_closed_collection_cannot_claim_future_interval(self):
        for end in (f.BASE + 80, f.BASE + 120):
            with self.subTest(end=end):
                case = f.positive_case()
                case["scope"]["interval_end"] = end
                f.payload(case, "collection-1")["body"]["interval_end"] = end
                report = evaluate(case)
                self.assert_all_signatures(report)
                self.assert_status(report, "coverage", "contradicted")

    def test_incomplete_collection_and_rotation_leave_scoped_gaps(self):
        report = evaluate(f.acceptance_cases()[8])
        self.assert_status(report, "operation", "supported")
        self.assert_status(report, "coverage", "unresolved")
        self.assertEqual("rotate", report["controls"][0]["action"])
        self.assert_boundaries(report)

    def test_missing_token_identifier_is_preserved_and_cannot_prove_containment(self):
        case = f.acceptance_cases()[8]
        f.change_native(case, "signin-1", lambda raw: raw.pop("UniqueTokenIdentifier"))
        report = evaluate(case)
        self.assertIsNone(self.record(report, "signin-1")["normalized"]["token_id"])
        self.assert_status(report, "coverage", "unresolved")
        self.assert_status(report, "global_containment", "unresolved")

    def test_failed_attempt_and_altered_retry_are_both_preserved(self):
        report = evaluate(f.acceptance_cases()[7])
        attempts = {item["attempt_id"]: item for item in report["attempts"]}
        self.assertEqual({f.ATTEMPT_ID, "synthetic-attempt-2"}, set(attempts))
        self.assertEqual("POST", attempts[f.ATTEMPT_ID]["request_context"]["method"])
        self.assertEqual("7.3", attempts[f.ATTEMPT_ID]["request_context"]["api_version"])
        self.assertEqual("GET", attempts["synthetic-attempt-2"]["request_context"]["method"])
        self.assertEqual("7.4", attempts["synthetic-attempt-2"]["request_context"]["api_version"])
        self.assertNotEqual(attempts[f.ATTEMPT_ID]["resource_ref"], attempts["synthetic-attempt-2"]["resource_ref"])
        self.assertEqual("failure", self.record(report, "resource-failed")["normalized"]["result"])
        self.assertEqual("success", self.record(report, "resource-1")["normalized"]["result"])
        self.assert_status(report, "operation", "supported")

    def test_successful_retry_response_cannot_be_transplanted_to_original_request(self):
        case = f.acceptance_cases()[7]
        old = f.payload(case, "binding-failed")["body"]
        old["resource_ref"] = f.reference("resource-1")
        case["scope"].update(attempt_id=f.ATTEMPT_ID, request_uri=old["request_uri"])
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assert_status(report, "operation", "contradicted")
        self.assert_status(report, "association", "contradicted")

    def test_dated_source_revisions_preserve_both_assessments(self):
        report = evaluate(f.acceptance_cases()[9])
        history = report["assessment_history"]
        self.assertEqual(["uncertain", "agentic"], [item["assessment"] for item in history])
        self.assertLess(history[0]["updated_at"], history[1]["updated_at"])
        self.assertEqual(history[0]["record_ref"], history[1]["supersedes"])
        self.assertTrue(all(item["classification"] == "supplied_source_assessment_not_model_telemetry"
                            for item in history))
        self.assert_status(report, "assessment", "supported")
        self.assert_status(report, "ai_orchestration", "unresolved")

    def test_orphaned_revision_and_reversed_revision_dates_are_distinct(self):
        case = f.acceptance_cases()[9]
        f.payload(case, "assessment-v2")["body"]["supersedes"] = "sha256:" + "0" * 64
        self.assert_status(evaluate(case), "assessment", "unresolved")
        case = f.acceptance_cases()[9]
        f.payload(case, "assessment-v2")["body"]["updated_at"] = f.BASE + 29
        self.assert_status(evaluate(case), "assessment", "contradicted")

    def test_source_revision_cannot_commit_to_an_earlier_version_received_later(self):
        case = f.acceptance_cases()[9]
        f.payload(case, "assessment-v1")["received_time"] = f.BASE + 60
        # Source dates still increase (30 -> 50); exact signed-envelope receipt
        # chronology is a separate constraint (60 -> 52 is impossible).
        report = evaluate(case)
        self.assert_all_signatures(report)
        self.assertEqual(2, len(report["assessment_history"]))
        self.assert_status(report, "assessment", "contradicted")

    def test_agent_fields_and_raw_sensitive_sentinel_are_not_model_telemetry_or_output(self):
        case = f.positive_case()
        sentinel = "SYNTHETIC-DO-NOT-ECHO-SECRET-VALUE-523497"
        f.change_native(case, "signin-1", lambda raw: raw.update(
            Agent={"claimed_model": "unverified", "fixture_private_value": sentinel}, UserAgent=sentinel))
        f.change_native(case, "resource-1", lambda raw: raw.update(syntheticRetrievedContents=sentinel))
        report = evaluate(case)
        self.assert_status(report, "ai_orchestration", "unresolved")
        self.assertNotIn(sentinel, json.dumps(report))
        self.assertTrue(self.record(report, "signin-1")["normalized"]["agent_field_present"])


class ParsingAndCLI(EvidenceCase):
    def test_json_parser_rejects_ambiguous_or_unsupported_numeric_forms(self):
        for document in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}', '{"x":1.0}',
                         '{"x":-0}', '{"x":9007199254740992}'):
            with self.subTest(document=document):
                with self.assertRaises((ValueError, TypeError)):
                    core.load_json(document)

    def test_json_parser_rejects_noncanonical_unicode_and_excessive_nesting(self):
        for document in ('{"x":"e\\u0301"}', '{"x":"\\ud800"}', '[' * 40 + '0' + ']' * 40):
            with self.subTest(document=document[:50]):
                with self.assertRaises((ValueError, TypeError, UnicodeError)):
                    core.load_json(document)

    def test_boolean_timestamp_and_duplicate_declared_ids_are_rejected(self):
        for variant in ("scope", "trust", "declared_ids", "prerequisite_outside_scope"):
            with self.subTest(variant=variant):
                case = f.positive_case()
                if variant == "scope":
                    case["scope"]["action_time"] = True
                elif variant == "trust":
                    case["trust"]["keys"][f.KEY_IDS["collector"]]["grants"][0]["valid_from"] = False
                elif variant == "declared_ids":
                    case["scope"]["expected_record_ids"].append("signin-1")
                else:
                    case["scope"]["prerequisite_record_ids"].append("not-declared")
                with self.assertRaises((ValueError, TypeError)):
                    evaluate(case)

    def test_duplicate_supplied_record_ids_are_not_silently_overwritten(self):
        case = f.positive_case()
        bundle = f.seal_bundle(case)
        bundle["records"].append(copy.deepcopy(bundle["records"][0]))
        report = evaluate(case, bundle=bundle)
        self.assert_status(report, "integrity", "contradicted")
        duplicates = [item for item in report["records"] if item["record_id"] == "signin-1"]
        self.assertEqual(2, len(duplicates))
        self.assertTrue(all(not item["eligible"] for item in duplicates))

    def test_native_timestamp_precision_above_seven_digits_is_rejected(self):
        case = f.positive_case()
        f.change_native(case, "resource-1", lambda raw: raw.update(
            time=f.iso(f.BASE + 20).replace("Z", ".00000001Z")))
        with self.assertRaises(ValueError):
            evaluate(case)

    def run_cli(self, case, *, raw_bundle=None):
        with tempfile.TemporaryDirectory(prefix="synthetic-cloud-evidence-") as directory:
            paths = {}
            for name, value in (("bundle", f.seal_bundle(case)), ("trust", case["trust"]), ("scope", case["scope"])):
                path = Path(directory) / (name + ".json")
                path.write_text(raw_bundle if name == "bundle" and raw_bundle is not None else json.dumps(value),
                                encoding="utf-8")
                paths[name] = str(path)
            optimization = ["-O"] if sys.flags.optimize else []
            return subprocess.run([sys.executable, *optimization, str(EXPERIMENT / "cloud_evidence.py"),
                                   "--bundle", paths["bundle"], "--trust", paths["trust"],
                                   "--scope", paths["scope"], "--at", str(case["evaluation_time"])],
                                  capture_output=True, text=True, timeout=30, check=False)

    def test_cli_zero_means_report_produced_even_when_claim_is_contradicted(self):
        for denied in (False, True):
            with self.subTest(denied=denied):
                case = f.positive_case()
                if denied:
                    f.payload(case, "permission-1")["body"]["decision"] = "deny"
                process = self.run_cli(case)
                self.assertEqual(0, process.returncode, process.stderr)
                report = json.loads(process.stdout)
                self.assert_status(report, "authority", "contradicted" if denied else "supported")
                self.assert_boundaries(report)

    def test_cli_malformed_input_has_status_two_and_no_echo(self):
        sentinel = "SYNTHETIC-PRIVATE-INPUT-DO-NOT-ECHO-3278"
        process = self.run_cli(f.positive_case(), raw_bundle='{"x":"' + sentinel + '","x":2}')
        self.assertEqual(2, process.returncode)
        self.assertEqual("", process.stdout)
        self.assertNotIn(sentinel, process.stderr)

    def test_fixture_cli_executes_all_cases_and_reports_actual_claims(self):
        optimization = ["-O"] if sys.flags.optimize else []
        process = subprocess.run([sys.executable, *optimization, str(EXPERIMENT / "fixtures.py")],
                                 capture_output=True, text=True, timeout=30, check=False)
        self.assertEqual(0, process.returncode, process.stderr)
        report = json.loads(process.stdout)
        self.assertEqual(10, report["acceptance_cases_executed"])
        self.assertEqual(0, report["expectation_mismatch_count"])
        self.assertFalse(report["prevention_established"])
        self.assertFalse(report["independent_reproduction_established"])
        self.assertEqual(0, report["live_cloud_calls"])
        self.assertEqual("contradicted", report["results"][5]["actual_report"]["claims"]["operation"]["status"])


if __name__ == "__main__":
    unittest.main()
