import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from change_evidence import assess, digest, observe, sign, text_hash
from run import (Fixture, Harness, NOW, expectations, file_hash, run_case, run_suite,
                 save, verify_case, verify_exports)


class PolicyBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.h = Harness()

    @classmethod
    def tearDownClass(cls):
        cls.h.close()

    def setUp(self):
        self.h.revoke([])
        self.f = Fixture(self.h, 'unit-case')

    def review(self):
        return assess(**self.f.args())

    def test_trusted_key_is_required(self):
        args = self.f.args()
        args['trusted_key'] = self.h.publics['agent']
        self.assertEqual(assess(**args)['record_integrity'], 'INVALID')

    def test_signature_cannot_hide_changed_patch(self):
        self.f.artifacts['patch.txt'] += 'replacement'
        self.assertEqual(self.review()['record_integrity'], 'INVALID')

    def test_resigned_patch_needs_matching_test_run(self):
        self.f.artifacts['patch.txt'] += 'replacement'
        self.f.reseal()
        report = self.review()
        self.assertEqual(report['record_integrity'], 'VERIFIED')
        self.assertEqual(report['test_evidence'], 'NOT_SATISFIED')
        self.assertEqual(report['admission'], 'DENY')

    def test_signed_failed_test_is_preserved_but_not_admitted(self):
        self.f.alter('test-run.json', lambda r: r['case_results'].update(smoke='failed'))
        report = self.review()
        self.assertEqual(report['record_integrity'], 'VERIFIED')
        self.assertEqual(report['admission'], 'DENY')

    def test_changed_target_snapshot_invalidates_evidence(self):
        self.f.context['baseline_sha256'] = text_hash('later baseline')
        self.assertEqual(self.review()['test_evidence'], 'NOT_SATISFIED')

    def test_future_test_is_not_fresh(self):
        self.f.alter('test-run.json', lambda r: r.update(finished_at=NOW + 1))
        self.assertEqual(self.review()['test_evidence'], 'NOT_SATISFIED')

    def test_bool_is_not_a_test_timestamp(self):
        self.f.alter('test-run.json', lambda r: r.update(finished_at=True))
        self.assertEqual(self.review()['test_evidence'], 'NOT_SATISFIED')

    def test_duplicate_result_keys_rejected_even_in_signed_artifact(self):
        original = self.f.artifacts['test-run.json'].strip()
        self.f.artifacts['test-run.json'] = original[:-1] + ',"finished_at":2000000140}\n'
        self.f.reseal()
        report = self.review()
        self.assertEqual(report['record_integrity'], 'VERIFIED')
        self.assertEqual(report['test_evidence'], 'NOT_SATISFIED')

    def test_valid_approval_for_other_manifest_is_insufficient(self):
        old = copy.deepcopy(self.f.request)
        self.f.body['change_id'] = 'another-change'
        self.f.reseal()
        self.f.request = old
        self.assertEqual(self.review()['authorization_binding'], 'INVALID')

    def test_conditions_cannot_be_removed_from_declared_policy(self):
        self.f.policy['required_conditions'] = []
        self.assertEqual(self.review()['admission'], 'DENY')

    def test_pending_condition_is_not_full_approval(self):
        self.f.alter('conditions.json', lambda r: r['conditions']['peer-review'].update(state='pending'))
        report = self.review()
        self.assertEqual(report['authorization_binding'], 'VERIFIED')
        self.assertEqual(report['approval_conditions'], 'NOT_SATISFIED')

    def test_new_artifacts_are_not_silently_ignored(self):
        self.f.artifacts['extra.txt'] = 'unscoped'
        self.f.reseal()
        self.assertEqual(self.review()['record_integrity'], 'INVALID')

    def test_observation_has_separate_binding_and_uncertainty(self):
        env = sign({'kind': 'change_observation', 'manifest_digest': digest(self.f.manifest),
                    'stage': 'health', 'outcome': 'unhealthy', 'evidence_text': 'Synthetic bad result'},
                   self.h.secrets['backend'], 'change-observer')
        key = self.h.publics['backend']
        self.assertEqual(observe(self.f.manifest, env, key, 'health'), 'ATTESTED_UNHEALTHY')
        self.assertEqual(observe(self.f.manifest, env, key, 'rollback'), 'INVALID')
        self.assertEqual(observe(self.f.manifest, None, key, 'rollback'), 'NOT_ESTABLISHED')
        env['body']['outcome'] = 'healthy'
        self.assertEqual(observe(self.f.manifest, env, key, 'health'), 'INVALID')


class NativeBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Retain only in-memory test keys after run_case closes the services;
        # replacement credentials below have real signatures and proof of possession.
        cls.h = Harness()
        with patch('run.Harness', return_value=cls.h):
            cls.original = run_case('normal')
        cls.expected = next(row for row in expectations() if row['case'] == 'normal')

    def setUp(self):
        self.artifact = copy.deepcopy(self.original)

    def test_different_valid_approval_cannot_replace_recorded_request(self):
        self.h.retoken(self.artifact['request'], 'approval', approver='another-synthetic-approver')
        with self.assertRaisesRegex(ValueError, 'gate_request_binding'):
            verify_case(self.artifact, self.expected)

    def test_different_valid_status_cannot_replace_recorded_snapshot(self):
        status = self.artifact['public_context']['revocations']['body']
        self.artifact['public_context']['revocations'] = sign(
            {**status, 'issued_at': NOW - 2}, self.h.secrets['authority'], 'authority')
        with self.assertRaisesRegex(ValueError, 'gate_authorization_snapshot_binding'):
            verify_case(self.artifact, self.expected)

    def test_alternative_valid_time_cannot_replace_recorded_check(self):
        self.artifact['public_context']['evaluation_time'] += 1
        self.artifact['context']['now'] += 1
        with self.assertRaisesRegex(ValueError, 'gate_authorization_snapshot_binding'):
            verify_case(self.artifact, self.expected)

    def test_primary_receipt_cannot_move_to_recovery_slot(self):
        self.artifact['recovered_evidence'] = self.artifact['gate_evidence']
        self.artifact['gate_evidence'] = None
        self.artifact['report']['reconciliation'] = {'state': 'confirmed_success'}
        with self.assertRaisesRegex(ValueError, 'gate_evidence_inventory'):
            verify_case(self.artifact, self.expected)

    def test_boolean_is_not_an_effect_count(self):
        self.artifact['harness_counts'] = {'effects': True, 'backend_requests': True}
        with self.assertRaisesRegex(ValueError, 'harness_effect_expectation'):
            verify_case(self.artifact, self.expected)


class ExportRecheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='change-evidence-tests-')
        cls.original = Path(cls.temp.name) / 'original'
        with redirect_stdout(io.StringIO()):
            run_suite(cls.original)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def setUp(self):
        self.target = Path(self.temp.name) / self._testMethodName
        shutil.copytree(self.original, self.target)

    def read(self, name):
        return json.loads((self.target / name).read_text())

    def recheck(self):
        with redirect_stdout(io.StringIO()):
            verify_exports(self.target, file_hash(self.target / 'summary.json'))

    def test_preserved_suite_rechecks_without_services(self):
        self.recheck()

    def test_wrong_external_summary_pin_rejected(self):
        with self.assertRaisesRegex(ValueError, 'summary_pin_mismatch'):
            verify_exports(self.target, '0' * 64)

    def test_missing_case_is_not_success_even_with_new_pin(self):
        summary = self.read('summary.json')
        summary['cases'].pop()
        save(self.target / 'summary.json', summary)
        with self.assertRaisesRegex(ValueError, 'incomplete_case_inventory'):
            self.recheck()

    def test_duplicate_case_is_rejected(self):
        summary = self.read('summary.json')
        summary['cases'][-1] = summary['cases'][0]
        save(self.target / 'summary.json', summary)
        with self.assertRaisesRegex(ValueError, 'invalid_case_inventory'):
            self.recheck()

    def test_empty_case_inventory_cannot_pass(self):
        summary = self.read('summary.json')
        summary.update(cases=[], scenario_expectations_matched=0)
        save(self.target / 'summary.json', summary)
        with self.assertRaisesRegex(ValueError, 'incomplete_case_inventory'):
            self.recheck()

    def test_tampered_case_fails_original_pin(self):
        artifact = self.read('normal.json')
        artifact['artifacts']['patch.txt'] += 'tampered'
        save(self.target / 'normal.json', artifact)
        with self.assertRaisesRegex(ValueError, 'case_pin_mismatch'):
            self.recheck()

    def test_rehashed_tampering_still_fails_signature_recheck(self):
        artifact = self.read('normal.json')
        artifact['artifacts']['patch.txt'] += 'tampered'
        save(self.target / 'normal.json', artifact)
        summary = self.read('summary.json')
        summary['cases'][0]['sha256'] = file_hash(self.target / 'normal.json')
        save(self.target / 'summary.json', summary)
        with self.assertRaisesRegex(ValueError, 'offline_assessment_mismatch'):
            self.recheck()

    def test_missing_native_receipt_evidence_fails(self):
        artifact = self.read('normal.json')
        artifact['gate_evidence'] = None
        save(self.target / 'normal.json', artifact)
        summary = self.read('summary.json')
        summary['cases'][0]['sha256'] = file_hash(self.target / 'normal.json')
        save(self.target / 'summary.json', summary)
        with self.assertRaisesRegex(ValueError, 'gate_evidence_inventory'):
            self.recheck()


if __name__ == '__main__':
    unittest.main()
