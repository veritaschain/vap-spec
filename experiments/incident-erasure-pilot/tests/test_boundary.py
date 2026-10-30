"""Adversarial boundary checks using actual, owned synthetic filesystem objects.

These checks review the adapter's declared local scope; they are not independent
provider verification, secure-media erasure tests, or VAP conformance tests.
"""

from copy import deepcopy
from datetime import timedelta
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from erasure_pilot.adapter import validate_pins, validate_task, verify_bundle
from erasure_pilot.harness import execute, make_case, make_task
from erasure_pilot.protocol import (
    EXCLUSIONS, LOCATION, InputError, canonical, decode_json, digest,
    object_name, sign_message, sign_record, timestamp, utc_now,
)


def iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)

    def case(self, name="store"):
        return make_case(self.root / name)

    def verify(self, captured, bundle=None):
        return verify_bundle(
            captured["bundle"] if bundle is None else bundle,
            captured["pins"], captured["expected_task_sha256"],
        )

    def resign_message(self, case, body, role):
        key = case["keys"][role]
        return sign_message(body, key["secret"], key["key_id"])

    def resign_request(self, case, task):
        key = case["keys"]["requester"]
        task["request"] = sign_record(task["request"]["body"], key["secret"], key["key_id"])
        authorization = deepcopy(task["authorization"]["body"])
        authorization["request_sha256"] = digest(task["request"])
        task["authorization"] = self.resign_message(case, authorization, "requester")

    def test_measured_unlink_preserves_unknown_scope_and_exports_no_secrets(self):
        case = self.case()
        captured = execute(case)
        result = captured["bundle"]["provider_result"]
        assessed = self.verify(captured)
        self.assertEqual(result["state"], "LOCAL_UNLINK_CONFIRMED")
        self.assertIs(result["attempted"], True)
        self.assertEqual(case["provider"].inspect(case["manifest"])["state"], "ABSENT")
        self.assertEqual(assessed["local_observation"], "REMOVAL_OBSERVED_SAME_CONTROLLER")
        core = assessed["assessor_report"]["assessments"]
        self.assertEqual(core["deletion_evidence"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE")
        self.assertEqual(core["independent_verification"], "NOT_ESTABLISHED")
        for field in ("provider_completion", "target_completion", "outside_scope_outcome", "excluded_scope_outcome"):
            self.assertEqual(core[field], "UNKNOWN")
        self.assertEqual(assessed["unknown_domains"], {name: "UNKNOWN" for name in EXCLUSIONS})
        self.assertEqual(result["attestation"]["body"]["data"]["locations"], [LOCATION])
        exported = canonical(captured)
        for key in case["keys"].values():
            self.assertNotIn(key["secret"].encode("ascii"), exported)
        self.assertNotIn(b"SYNTHETIC LOCAL OBJECT;", exported)
        self.assertNotIn(b'"kind":"erasure.review"', exported)

    def test_caller_mutation_after_snapshot_cannot_redirect_deletion(self):
        case = self.case()
        original = deepcopy(case["task"])
        other = case["provider"].create("object-other", "version-other", b"OTHER SYNTHETIC OBJECT")
        replacement = make_task(other, case["keys"], case["pins"])
        before = case["observer"].observe(original, "before")

        def mutate_caller():
            case["task"].clear()
            case["task"].update(deepcopy(replacement))

        result = case["provider"].delete(case["task"], before_unlink=mutate_caller)
        self.assertEqual(result["state"], "LOCAL_UNLINK_CONFIRMED")
        self.assertEqual(case["provider"].inspect(original["manifest"])["state"], "ABSENT")
        self.assertEqual(case["provider"].inspect(other)["state"], "PRESENT")
        self.assertEqual(result["receipt"]["body"]["task_sha256"], digest(original))
        after = case["observer"].observe(original, "after", previous=before,
                                          completion=result["attestation"])
        bundle = {"format": "incident-erasure-bundle/0.1", "task": original,
                  "as_of": utc_now(), "provider_result": result,
                  "before": before, "after": after}
        assessed = verify_bundle(bundle, case["pins"], digest(original))
        self.assertEqual(assessed["local_observation"], "REMOVAL_OBSERVED_SAME_CONTROLLER")
        with self.assertRaises(InputError):
            verify_bundle(bundle, case["pins"], digest(case["task"]))

    def test_namespace_replacement_never_produces_scoped_completion(self):
        for phase, state, attempted in (
            ("before_unlink", "BLOCKED", False),
            ("after_unlink", "OUTCOME_UNKNOWN", True),
        ):
            with self.subTest(phase=phase):
                case = self.case(phase)
                namespace = case["provider"].namespace_root
                moved = namespace.with_name("moved-namespace")
                name = object_name(case["manifest"])

                def replace_namespace():
                    namespace.rename(moved)
                    namespace.mkdir(mode=0o700)
                    (namespace / name).write_bytes(b"REPLACEMENT NAMESPACE OBJECT")

                result = case["provider"].delete(case["task"], **{phase: replace_namespace})
                self.assertEqual(result["state"], state)
                self.assertIs(result["attempted"], attempted)
                self.assertIsNone(result["attestation"])
                self.assertIsNone(result["receipt"])
                self.assertEqual((namespace / name).read_bytes(), b"REPLACEMENT NAMESPACE OBJECT")
                self.assertEqual((moved / name).exists(), not attempted)

    def test_signed_request_still_requires_exact_identity_scope_and_types(self):
        case = self.case()
        mutations = {
            "wrong tenant": lambda task: task["request"]["body"]["binding"].update(tenant_id="another-tenant"),
            "wrong object": lambda task: task["request"]["body"]["binding"].update(object_ids=["another-object"]),
            "wrong manifest digest": lambda task: task["request"]["body"]["binding"].update(payload_sha256="0" * 64),
            "wrong stage": lambda task: task["request"]["body"]["binding"].update(stage="transfer"),
            "unsupported scope": lambda task: task["request"]["body"]["data"].update(requested_locations=["all-provider-data"]),
            "missing active namespace": lambda task: task["request"]["body"]["data"].update(requested_locations=[EXCLUSIONS[0]]),
            "duplicate scope": lambda task: task["request"]["body"]["data"].update(requested_locations=[LOCATION, LOCATION]),
            "boolean object length": lambda task: task["manifest"].update(byte_length=True),
            "caller path": lambda task: task["manifest"].update(object_id="../outside"),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                task = deepcopy(case["task"])
                mutate(task)
                self.resign_request(case, task)
                with self.assertRaises(InputError):
                    validate_task(task, case["pins"], utc_now())
                with self.assertRaises(InputError):
                    case["provider"].delete(task)
                self.assertEqual(case["provider"].inspect(case["manifest"])["state"], "PRESENT")

    def test_controller_metadata_cannot_widen_roles_or_invent_independence(self):
        case = self.case()
        role_cases = (
            ("requester", "roles", ["responder", "provider"]),
            ("provider", "roles", ["reviewer"]),
            ("observer", "organization", "supposed-independent-reviewer"),
            ("requester", "roles", "responder"),
        )
        for role, field, value in role_cases:
            with self.subTest(role=role, field=field, value=value):
                pins = deepcopy(case["pins"])
                pins["keys"][pins[role + "_key_id"]][field] = value
                with self.assertRaises(InputError):
                    validate_pins(pins)
        pins = deepcopy(case["pins"])
        pins["tenant_id"] = "another-tenant"
        with self.assertRaises(InputError):
            validate_task(case["task"], pins, utc_now())

    def test_missing_observations_do_not_invent_prior_presence_or_removal(self):
        case = self.case()
        captured = execute(case)
        for before, after, expected in (
            (False, True, "ABSENCE_ONLY"),
            (True, False, "NOT_ESTABLISHED"),
            (False, False, "NOT_OBSERVED"),
        ):
            with self.subTest(before=before, after=after):
                bundle = deepcopy(captured["bundle"])
                if not before:
                    bundle["before"] = None
                if not after:
                    bundle["after"] = None
                assessed = self.verify(captured, bundle)
                self.assertEqual(assessed["local_observation"], expected)
                self.assertEqual(assessed["assessor_report"]["assessments"]["target_completion"], "UNKNOWN")

    def test_authentic_receipt_cannot_change_target_measurement_or_chronology(self):
        case = self.case()
        captured = execute(case)
        request_at = timestamp(case["task"]["request"]["body"]["recorded_at"])
        after_cutoff = iso(timestamp(captured["bundle"]["as_of"]) + timedelta(seconds=1))
        mutations = {
            "another task": lambda body: body.update(task_sha256="0" * 64),
            "another manifest": lambda body: body.update(manifest_sha256="0" * 64),
            "another request": lambda body: body.update(request_id="another-request"),
            "wrong prior digest": lambda body: body["before"].update(sha256="0" * 64),
            "boolean prior length": lambda body: body["before"].update(byte_length=True),
            "present completion": lambda body: body.update(after="PRESENT"),
            "before request": lambda body: body.update(unlinked_at=iso(request_at - timedelta(seconds=1))),
            "beyond cutoff": lambda body: body.update(observed_at=after_cutoff),
            "unsupported claim": lambda body: body.update(universal_deletion=True),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                bundle = deepcopy(captured["bundle"])
                body = bundle["provider_result"]["receipt"]["body"]
                mutate(body)
                bundle["provider_result"]["receipt"] = self.resign_message(case, body, "provider")
                with self.assertRaises(InputError):
                    self.verify(captured, bundle)

    def test_authentic_observation_requires_exact_chain_scope_and_time(self):
        case = self.case()
        captured = execute(case)
        before_completion = iso(timestamp(captured["bundle"]["provider_result"]["attestation"]["body"]["data"]["completed_at"]) - timedelta(seconds=1))
        mutations = {
            "another task": lambda body: body.update(task_sha256="0" * 64),
            "another tenant": lambda body: body.update(tenant_id="another-tenant"),
            "another version": lambda body: body.update(version_id="another-version"),
            "wrong predecessor": lambda body: body.update(previous_sha256="0" * 64),
            "wrong completion": lambda body: body.update(completion_sha256="0" * 64),
            "wrong phase": lambda body: body.update(phase="before"),
            "observation before completion": lambda body: body.update(window_start=before_completion, window_end=before_completion),
            "absence with size": lambda body: body["measurement"].update(byte_length=1),
            "unsupported claim": lambda body: body.update(independent_verification=True),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                bundle = deepcopy(captured["bundle"])
                body = bundle["after"]["body"]
                mutate(body)
                bundle["after"] = self.resign_message(case, body, "observer")
                with self.assertRaises(InputError):
                    self.verify(captured, bundle)

    def test_report_cannot_hide_attempts_or_relabel_incomplete_terminal_state(self):
        case = self.case()
        captured = execute(case)
        mutations = {
            "denied attempt": lambda result: result.update(attempted=False),
            "string attempt": lambda result: result.update(attempted="true"),
            "uncommitted result": lambda result: result.update(journal_state="deletion_intent"),
            "unknown with completion": lambda result: result.update(state="OUTCOME_UNKNOWN", journal_state="OUTCOME_UNKNOWN"),
            "acknowledgement relabel": lambda result: result.update(state="ACKNOWLEDGED_ONLY", journal_state="ACKNOWLEDGED_ONLY", attempted=False),
            "replay reuses completion": lambda result: result.update(state="REPLAY_NO_ACTION", attempted=False),
            "missing attestation": lambda result: result.update(attestation=None),
            "missing receipt": lambda result: result.update(receipt=None),
        }
        for label, mutate in mutations.items():
            with self.subTest(label=label):
                bundle = deepcopy(captured["bundle"])
                mutate(bundle["provider_result"])
                with self.assertRaises(InputError):
                    self.verify(captured, bundle)

    def test_later_present_observation_keeps_claim_but_withholds_corroboration(self):
        case = self.case()
        captured = execute(case)
        # A trusted local owner can recreate the path after the recorded unlink.
        # This is an actual contradictory current observation, not a signature fault.
        path = case["provider"].namespace_root / object_name(case["manifest"])
        path.write_bytes(b"RECREATED SYNTHETIC CONTENT")
        bundle = deepcopy(captured["bundle"])
        bundle["after"] = case["observer"].observe(
            bundle["task"], "after", previous=bundle["before"],
            completion=bundle["provider_result"]["attestation"],
        )
        bundle["as_of"] = utc_now()
        assessed = self.verify(captured, bundle)
        self.assertEqual(assessed["local_observation"], "PRESENT_AT_OBSERVATION")
        self.assertEqual(assessed["assessor_report"]["assessments"]["deletion_evidence"],
                         "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE")
        self.assertEqual(bundle["after"]["body"]["measurement"]["state"], "PRESENT")

    def test_later_cutoff_preserves_original_request_time_without_new_action(self):
        case = self.case()
        captured = execute(case)
        bundle = deepcopy(captured["bundle"])
        bundle["as_of"] = iso(timestamp(bundle["task"]["authorization"]["body"]["valid_until"]) + timedelta(seconds=1))
        assessed = self.verify(captured, bundle)
        self.assertEqual(assessed["local_observation"], "REMOVAL_OBSERVED_SAME_CONTROLLER")
        self.assertEqual(bundle["task"], captured["bundle"]["task"])
        self.assertEqual(case["provider"].get(bundle["task"]["request"]["body"]["binding"]["request_id"])["state"],
                         "LOCAL_UNLINK_CONFIRMED")
        for raw in (b'{"duplicate":1,"duplicate":2}', b'{"value":NaN}', '"\ud800"'):
            with self.subTest(raw=repr(raw)):
                with self.assertRaises(InputError):
                    decode_json(raw)


if __name__ == "__main__":
    unittest.main()
