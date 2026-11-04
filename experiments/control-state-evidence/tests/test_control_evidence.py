"""Synthetic verifier/policy unit tests; these are NOT OS/network test results."""
import copy
import json
from pathlib import Path
import sys
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from control_evidence import ARTIFACTS, CASES, artifact, canonical, digest, preflight, read_json, seal, verify


def fixture():
    summary = {'execution_complete': True, 'execution_error': None,
               'cases': [{'case': c, 'observed': {}} for c in CASES]}
    summary['cases'][14]['observed'] = {'attempt': {'connected': True, 'http_status': 200},
                                      'backend_counts': {'effects': 1, 'requests': 1}}
    values = {name: {} for name in ARTIFACTS}
    values['summary.json'] = summary
    values['cleanup.json'] = {'returncode': 0}
    return {'run_id': 'synthetic-run', 'source_commit_before': 'test', 'source_commit_after': 'test',
            'source_digest_before': 'test-digest', 'source_digest_after': 'test-digest',
            'artifacts': {name: artifact(json.dumps(value)) for name, value in values.items()},
            'observations': [{'seq': 1, 'run_id': 'synthetic-run', 'monotonic_ns': 1},
                             {'seq': 2, 'run_id': 'synthetic-run', 'monotonic_ns': 2}]}


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.key = Ed25519PrivateKey.generate()
        self.public = self.key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.payload = fixture()

    def check(self, payload=None):
        return verify(seal(payload or self.payload, self.key), self.public, 'synthetic-run')

    def edit_summary(self, edit):
        summary = read_json(self.payload['artifacts']['summary.json']['text'])
        edit(summary)
        self.payload['artifacts']['summary.json'] = artifact(json.dumps(summary))

    def test_signed_negative_control_is_not_safe(self):
        report = self.check()
        self.assertEqual(report['integrity'], 'VERIFIED')
        self.assertEqual(report['isolation'], 'VIOLATED_IN_NEGATIVE_CONTROL')
        self.assertEqual(report['action'], 'BYPASS_EFFECT_OBSERVED')
        self.assertEqual(report['overall_safety'], 'NOT_ASSESSED')
        self.assertEqual(report['external_anchor'], 'NOT_ESTABLISHED')

    def test_wrong_trusted_key(self):
        other = Ed25519PrivateKey.generate().public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
        self.assertEqual(verify(seal(self.payload, self.key), other, 'synthetic-run')['integrity'], 'INVALID')

    def test_run_replay(self):
        self.assertEqual(verify(seal(self.payload, self.key), self.public, 'another-run')['integrity'], 'INVALID')

    def test_unsigned_edit_rejected(self):
        env = seal(self.payload, self.key)
        env['payload']['observations'][0]['monotonic_ns'] = 0
        self.assertEqual(verify(env, self.public, 'synthetic-run')['integrity'], 'INVALID')

    def test_removed_artifact_rejected(self):
        del self.payload['artifacts']['runtime.json']
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_wrong_raw_artifact_hash_rejected_even_when_resigned(self):
        self.payload['artifacts']['runtime.json']['text'] = '{"other":true}'
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_changed_source_commit_rejected(self):
        self.payload['source_commit_after'] = 'changed'
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_changed_observer_code_rejected(self):
        self.payload['source_digest_after'] = 'changed'
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_removed_observation_leaves_sequence_gap(self):
        self.payload['observations'].pop(0)
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_duplicate_sequence_rejected(self):
        self.payload['observations'][1]['seq'] = 1
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_event_run_mismatch(self):
        self.payload['observations'][1]['run_id'] = 'other'
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_decreasing_clock_rejected(self):
        self.payload['observations'][1]['monotonic_ns'] = 0
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_missing_observations_rejected(self):
        self.payload['observations'] = []
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_signed_incomplete_case_inventory_remains_unknown(self):
        self.edit_summary(lambda summary: summary['cases'].pop())
        report = self.check()
        self.assertEqual(report['integrity'], 'VERIFIED')
        self.assertEqual(report['case_inventory'], 'NOT_ESTABLISHED')

    def test_duplicate_case_inventory_unknown(self):
        self.edit_summary(lambda summary: summary['cases'].append(summary['cases'][0]))
        self.assertEqual(self.check()['case_inventory'], 'NOT_ESTABLISHED')

    def test_execution_error_cannot_count_as_complete(self):
        self.edit_summary(lambda summary: summary.update(execution_error='cleanup failed'))
        self.assertEqual(self.check()['case_inventory'], 'NOT_ESTABLISHED')

    def test_cleanup_failure_cannot_count_as_complete(self):
        self.payload['artifacts']['cleanup.json'] = artifact('{"returncode":1}')
        self.assertEqual(self.check()['case_inventory'], 'NOT_ESTABLISHED')

    def test_no_bypass_is_not_universal_isolation(self):
        self.edit_summary(lambda summary: summary['cases'][14].update(observed={}))
        self.assertEqual(self.check()['isolation'], 'NOT_ESTABLISHED')

    def test_expectations_matched_flag_is_not_evidence(self):
        self.edit_summary(lambda summary: summary.update(all_expectations_matched=True, cases=[]))
        report = self.check()
        self.assertEqual(report['case_inventory'], 'NOT_ESTABLISHED')
        self.assertEqual(report['isolation'], 'NOT_ESTABLISHED')

    def test_attacker_supplied_key_field_not_accepted(self):
        env = seal(self.payload, self.key)
        env['trusted_key'] = self.public.hex()
        self.assertEqual(verify(env, self.public, 'synthetic-run')['integrity'], 'INVALID')

    def test_invalid_signature_encoding(self):
        env = seal(self.payload, self.key); env['signature'] = 'not hex'
        self.assertEqual(verify(env, self.public, 'synthetic-run')['integrity'], 'INVALID')

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError): read_json('{"a":1,"a":2}')

    def test_float_canonicalization_rejected(self):
        with self.assertRaises(ValueError): canonical({'time': 0.5})

    def test_nan_json_rejected(self):
        with self.assertRaises(ValueError): read_json('{"a":NaN}')

    def test_malformed_signed_artifact_is_rejected(self):
        self.payload['artifacts']['summary.json'] = artifact('[]')
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_malformed_signed_cases_are_rejected(self):
        self.edit_summary(lambda summary: summary.update(cases='invalid'))
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_malformed_signed_network_result_is_rejected(self):
        self.edit_summary(lambda summary: summary['cases'][14].update(observed={'attempt': []}))
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_deterministic_encoding(self):
        self.assertEqual(digest({'b':2,'a':1}), digest({'a':1,'b':2}))


class PreflightTests(unittest.TestCase):
    def setUp(self):
        self.paths = ['ipv4', 'ipv6', 'dns', 'proxy']
        self.obs = {'run_id': 'run', 'config_digest': 'config', 'measured_ns': 100,
                    'paths': {path: {'reachable': False, 'target_healthy': True} for path in self.paths}}

    def check(self, **kwargs):
        args = dict(run_id='run', config_digest='config', now_ns=110, max_age_ns=20, required_paths=self.paths)
        args.update(kwargs)
        return preflight(self.obs, **args)

    def test_only_measured_window_passes(self):
        self.assertEqual(self.check()['control_status'], 'MET_FOR_DECLARED_PATHS')
        self.assertEqual(self.check()['runtime_enforcement'], 'not_implemented')

    def test_configuration_flag_cannot_override_measurement(self):
        self.obs['isolation_enabled'] = True
        self.obs['paths']['ipv4']['reachable'] = True
        self.assertEqual(self.check()['control_status'], 'VIOLATED')

    def test_configuration_drift_invalidates_preflight(self):
        self.assertEqual(self.check(config_digest='changed')['reason'], 'configuration_changed')

    def test_stale_preflight(self):
        self.assertEqual(self.check(now_ns=121)['control_status'], 'NOT_ESTABLISHED')

    def test_future_preflight(self):
        self.assertEqual(self.check(now_ns=99)['control_status'], 'NOT_ESTABLISHED')

    def test_wrong_run(self):
        self.assertEqual(self.check(run_id='other')['reason'], 'run_mismatch')

    def test_missing_alternate_paths_never_pass(self):
        for path in self.paths:
            with self.subTest(path=path):
                saved = self.obs['paths'].pop(path)
                self.assertEqual(self.check()['control_status'], 'NOT_ESTABLISHED')
                self.obs['paths'][path] = saved

    def test_unknown_path_never_passes(self):
        self.obs['paths']['dns']['reachable'] = None
        self.assertEqual(self.check()['control_status'], 'NOT_ESTABLISHED')

    def test_unhealthy_endpoint_does_not_prove_isolation(self):
        self.obs['paths']['proxy']['target_healthy'] = False
        self.assertEqual(self.check()['control_status'], 'NOT_ESTABLISHED')

    def test_reachable_alternate_path_is_violation(self):
        for path in self.paths:
            with self.subTest(path=path):
                self.obs['paths'][path]['reachable'] = True
                self.assertEqual(self.check()['control_status'], 'VIOLATED')
                self.obs['paths'][path]['reachable'] = False

    def test_empty_scope_does_not_vacuously_pass(self):
        self.assertEqual(self.check(required_paths=[])['control_status'], 'NOT_ESTABLISHED')

    def test_duplicate_scope_rejected(self):
        self.assertEqual(self.check(required_paths=['ipv4','ipv4'])['control_status'], 'NOT_ESTABLISHED')

    def test_non_boolean_measurement_not_trusted(self):
        self.obs['paths']['ipv6']['reachable'] = 0
        self.assertEqual(self.check()['control_status'], 'NOT_ESTABLISHED')

    def test_invalid_path_scope_rejected(self):
        for scope in (None, 'ipv4', [[]], [None]):
            with self.subTest(scope=scope):
                self.assertEqual(self.check(required_paths=scope)['control_status'], 'NOT_ESTABLISHED')

    def test_invalid_clock_rejected(self):
        for value in (True, None, -1, 1.2):
            with self.subTest(value=value):
                self.assertEqual(self.check(now_ns=value)['control_status'], 'NOT_ESTABLISHED')


class OutputSafetyTests(unittest.TestCase):
    def test_existing_output_is_never_reused(self):
        import tempfile
        from run import run
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(FileExistsError): run(directory)

    def test_symlink_output_is_never_followed(self):
        import tempfile
        from run import run
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory) / 'link'
            link.symlink_to(directory, target_is_directory=True)
            with self.assertRaises(FileExistsError): run(link)


if __name__ == '__main__': unittest.main()
