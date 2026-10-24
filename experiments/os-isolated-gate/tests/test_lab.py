"""Controller/adapter regressions; these do not substitute for the Linux OS suite."""
import copy
import errno
import unittest
from unittest.mock import MagicMock, patch

from isolation_lab.seed import generate
from isolation_lab.suite import CASES, summarize
from isolation_lab import probe, transport
from record_gate.auth import authorize
from record_gate.common import Rejected


class SeedTests(unittest.TestCase):
    def test_both_operations_are_independently_authorized(self):
        seed = generate()
        config = seed['configs']['gate']
        ops = [authorize(seed['configs']['agent'][key], config, status_envelope=seed['revocations'])[0]
               for key in ('request', 'fresh_request')]
        self.assertNotEqual(ops[0]['operation_id'], ops[1]['operation_id'])
        self.assertEqual(seed['operation'], ops[0])

    def test_second_request_cannot_reuse_first_approval(self):
        seed = generate()
        agent = seed['configs']['agent']
        altered = copy.deepcopy(agent['fresh_request'])
        altered['approval'] = agent['request']['approval']
        with self.assertRaises(Rejected):
            authorize(altered, seed['configs']['gate'], status_envelope=seed['revocations'])

    def test_runtime_role_configs_do_not_include_other_private_keys(self):
        seed = generate()
        secrets = {role: c['secret'] for role, c in seed['configs'].items()}
        for role, config in seed['configs'].items():
            for other, private in secrets.items():
                if other != role:
                    self.assertNotIn(private, repr(config))
            self.assertNotIn(seed['exporter_secret'], repr(config))
        self.assertEqual(len(set(secrets.values())), len(secrets))


class TransportTests(unittest.TestCase):
    def test_external_and_ambiguous_urls_are_rejected_without_network(self):
        with patch.object(transport, 'exchange') as exchange:
            for url in ('http://127.0.0.1:8080', 'http://backend:8080@evil.invalid',
                        'http://backend:8080/', 'http://backend:8080?url=evil',
                        'https://backend:8080', 'http://open-backend:8080'):
                with self.subTest(url=url), self.assertRaises(Rejected):
                    transport.service_rpc(url, '/write', {})
            exchange.assert_not_called()

    def test_non_success_including_redirects_is_not_acknowledgment(self):
        for status in (301, 302, 403, 500):
            with self.subTest(status=status), patch.object(transport, 'exchange', return_value=(status, {})):
                with self.assertRaises(Rejected):
                    transport.service_rpc('http://audit:8080', '/prepare', {})

    def test_oversized_response_fails_and_connection_is_closed(self):
        connection = MagicMock()
        connection.getresponse.return_value.read.return_value = b'x' * (1024 * 1024 + 1)
        with patch.object(transport.http.client, 'HTTPConnection', return_value=connection):
            with self.assertRaises(Rejected):
                transport.exchange('audit', 8080, '/get', {})
        connection.close.assert_called_once()

    def test_network_failure_is_not_http_rejection(self):
        with patch.object(probe, 'exchange', side_effect=TimeoutError(errno.ETIMEDOUT, 'timeout')):
            result = probe.network('192.0.2.1', 8080)
        self.assertIs(result['connected'], False)
        self.assertIsNone(result['http_status'])
        self.assertEqual(result['errno'], errno.ETIMEDOUT)
        with patch.object(probe, 'exchange', return_value=(403, {'error': 'rejected'})):
            self.assertIs(probe.network('192.0.2.1', 8080)['connected'], True)


class ReportingTests(unittest.TestCase):
    def rows(self):
        return [{'case': c, 'matched': True} for c in CASES]

    def test_missing_duplicate_and_unknown_cases_cannot_pass(self):
        for rows in ([], self.rows()[:-1], self.rows() + [self.rows()[0]],
                     self.rows()[:-1] + [{'case': 'unknown', 'matched': True}]):
            with self.subTest(rows=len(rows)):
                self.assertFalse(summarize(rows)['all_expectations_matched'])
                self.assertFalse(summarize(rows)['execution_complete'])

    def test_failed_or_nonboolean_match_does_not_pass(self):
        for value in (False, 'true', 1, None):
            rows = self.rows()
            rows[-1]['matched'] = value
            self.assertFalse(summarize(rows)['all_expectations_matched'])

    def test_cleanup_or_execution_failure_prevents_success(self):
        result = summarize(self.rows(), execution_error='cleanup incomplete')
        self.assertFalse(result['execution_complete'])
        self.assertFalse(result['all_expectations_matched'])

    def test_successful_negative_control_is_not_a_bypass_guarantee(self):
        rows = self.rows()
        rows[14]['observed'] = {'bypass_guarantee_established': False}
        result = summarize(rows)
        self.assertTrue(result['all_expectations_matched'])
        self.assertIs(result['cases'][14]['observed']['bypass_guarantee_established'], False)
        self.assertEqual(result['proposal_status'], 'experimental_unadopted')
        self.assertFalse(result['production_ready'])


if __name__ == '__main__':
    unittest.main()
