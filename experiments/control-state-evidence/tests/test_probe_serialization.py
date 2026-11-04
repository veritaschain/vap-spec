"""Regression for finite runtime timings; synthetic data, not a network proof."""
import json
from pathlib import Path
import sys
import unittest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from control_evidence import (ARTIFACTS, CASES, artifact, canonical, probe_result_record,
                              read_json, seal, validate_probe_result, verify)


class ProbeSerializationTests(unittest.TestCase):
    def setUp(self):
        self.result = {'http_status': 200, 'result': {
            'state': 'confirmed_success', 'before_send_ms': 15.889545, 'total_ms': 27.080375}}
        self.details = probe_result_record('agent', ('execute', 'valid'), self.result)
        self.key = Ed25519PrivateKey.generate()
        self.public = self.key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)

    def payload(self):
        values = {name: {} for name in ARTIFACTS}
        values['summary.json'] = {'execution_complete': True, 'execution_error': None,
            'cases': [{'case': c, 'observed': {}} for c in CASES]}
        values['summary.json']['cases'][14]['observed'] = {
            'attempt': {'connected': True, 'http_status': 200},
            'backend_counts': {'effects': 1, 'requests': 1}}
        values['cleanup.json'] = {'returncode': 0}
        return {'run_id': 'synthetic', 'source_commit_before': 'test', 'source_commit_after': 'test',
                'source_digest_before': 'test', 'source_digest_after': 'test',
                'artifacts': {name: artifact(json.dumps(value)) for name, value in values.items()},
                'observations': [{'seq': 1, 'run_id': 'synthetic', 'monotonic_ns': 1,
                                  'kind': 'probe-result', 'details': self.details}]}

    def check(self):
        return verify(seal(self.payload(), self.key), self.public, 'synthetic')

    def test_original_shape_reproduces_float_rejection(self):
        with self.assertRaisesRegex(ValueError, 'floats'):
            canonical({'result': self.result})

    def test_timings_survive_encoding_and_signed_verification(self):
        decoded = validate_probe_result(self.details)
        self.assertEqual(decoded, self.result)
        for key in ('before_send_ms', 'total_ms'):
            self.assertEqual(decoded['result'][key].hex(), self.result['result'][key].hex())
        self.assertEqual(self.check()['integrity'], 'VERIFIED')

    def test_outer_canonical_contract_is_unchanged(self):
        canonical(self.details)
        with self.assertRaises(ValueError): canonical({'time': 1.25})

    def test_no_safety_promotion_after_successful_sealing(self):
        report = self.check()
        self.assertEqual(report['isolation'], 'VIOLATED_IN_NEGATIVE_CONTROL')
        self.assertEqual(report['action'], 'BYPASS_EFFECT_OBSERVED')
        self.assertEqual(report['external_anchor'], 'NOT_ESTABLISHED')
        self.assertEqual(report['overall_safety'], 'NOT_ASSESSED')

    def test_unsigned_inner_edit_rejected(self):
        envelope = seal(self.payload(), self.key)
        envelope['payload']['observations'][0]['details']['result_json'] = artifact('{}')
        self.assertEqual(verify(envelope, self.public, 'synthetic')['integrity'], 'INVALID')

    def test_resigned_wrong_inner_digest_rejected(self):
        self.details['result_json']['text'] = '{}'
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_resigned_invalid_json_rejected(self):
        self.details['result_json'] = artifact('{')
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_resigned_non_object_result_rejected(self):
        self.details['result_json'] = artifact('[]')
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_resigned_duplicate_keys_rejected(self):
        self.details['result_json'] = artifact('{"ok":true,"ok":false}')
        self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_nonfinite_values_not_serialized(self):
        for number in (float('nan'), float('inf'), -float('inf')):
            with self.subTest(number=number), self.assertRaises(ValueError):
                probe_result_record('agent', (), {'timing': number})

    def test_nonfinite_json_including_overflow_rejected(self):
        for token in ('NaN', 'Infinity', '-Infinity', '1e999', '-1e999'):
            with self.subTest(token=token):
                self.details['result_json'] = artifact('{"timing":' + token + '}')
                self.assertEqual(self.check()['integrity'], 'INVALID')

    def test_unicode_and_numeric_types_retained(self):
        value = {'message': '観測', 'values': [0, -0.0, True, None, 1e-200, 1e200]}
        decoded = validate_probe_result(probe_result_record('agent', (), value))
        self.assertEqual(decoded, value)
        self.assertEqual(decoded['values'][1].hex(), (-0.0).hex())
        self.assertIs(type(decoded['values'][0]), int)
        self.assertIs(type(decoded['values'][2]), bool)

    def test_invalid_probe_metadata_rejected(self):
        for field, value in (('role', ''), ('arguments', 'execute'), ('arguments', [1]),
                             ('result_json', {'text': None, 'sha256': 'bad'})):
            original = self.details[field]
            self.details[field] = value
            with self.subTest(field=field, value=value):
                self.assertEqual(self.check()['integrity'], 'INVALID')
            self.details[field] = original

    def test_capture_is_detached_from_mutated_result(self):
        self.result['result']['total_ms'] = 999
        self.assertEqual(validate_probe_result(self.details)['result']['total_ms'], 27.080375)

    def test_gate_export_event_array_is_preserved(self):
        events = [{'event_id': 'synthetic-1', 'elapsed_ms': 0.125},
                  {'event_id': 'synthetic-2', 'elapsed_ms': 1.5}]
        self.details = probe_result_record('gate', ('export',), events)
        self.assertEqual(validate_probe_result(self.details), events)
        self.assertEqual(self.check()['integrity'], 'VERIFIED')

    def test_empty_export_array_is_captured_not_promoted(self):
        self.details = probe_result_record('gate', ('export',), [])
        self.assertEqual(validate_probe_result(self.details), [])
        self.assertEqual(self.check()['overall_safety'], 'NOT_ASSESSED')

    def test_export_object_is_not_an_event_array(self):
        with self.assertRaises(ValueError):
            probe_result_record('gate', ('export',), {'events': []})

    def test_export_nonobject_elements_rejected(self):
        for value in ([None], [1], ['event'], [[]]):
            with self.subTest(value=value), self.assertRaises(ValueError):
                probe_result_record('gate', ('export',), value)

    def test_array_exception_is_limited_to_exact_gate_export(self):
        for role, args in (('agent', ('export',)), ('gate', ('counts',)),
                           ('gate', ('export', 'extra'))):
            with self.subTest(role=role, args=args), self.assertRaises(ValueError):
                probe_result_record(role, args, [])


if __name__ == '__main__':
    unittest.main()
