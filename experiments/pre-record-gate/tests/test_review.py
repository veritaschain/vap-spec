"""Reproductions from PR #11 final review."""
import copy
import json
import tarfile
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import record_gate
from record_gate import gate
from record_gate.common import Rejected, save, sign
from record_gate.gate import reconcile, unresolved
from record_gate.harness import Harness, ROOT
from record_gate.suite import verify_bundle, verify_exports
from scope_verifier.crypto import digest


class ReviewGateTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def intercept_ack(self, intercepted, change):
        h, original = self.h, gate.rpc
        def intercept(url, path, message):
            if path == '/' + intercepted:
                answer = original(url, '/get', gate.control(h.gate, 'get', intent=message['body']['intent']))
                answer['body']['action'] = intercepted
                change(answer['body'])
                return sign(answer['body'], h.secrets['audit'], 'audit')
            return original(url, path, message)
        return patch.object(gate, 'rpc', side_effect=intercept)

    def test_wrong_outcome_ack_does_not_report_success(self):
        h = self.h
        with self.intercept_ack('outcome', lambda ack: None):
            result = h.execute()
        self.assertEqual(result['state'], 'result_unknown')
        self.assertFalse(result['unknown_outcome_persisted'])
        self.assertEqual(h.state(), 'dispatch_intent')
        self.assertEqual(h.counts()['effects'], 1)

    def test_claim_ack_requires_dispatch_state_before_any_send(self):
        h = self.h
        with self.intercept_ack('claim', lambda ack: ack.update(claimed=True)):
            result = h.execute()
        self.assertEqual(result['state'], 'blocked')
        self.assertEqual(h.counts()['backend_requests'], 0)
        self.assertEqual(h.state(), 'prepared')

    def test_malformed_ack_does_not_escape_as_uncaught_error(self):
        h, original = self.h, gate.rpc
        def intercept(url, path, message):
            answer = original(url, path, message)
            if path == '/prepare':
                del answer['body']['state']
                answer = sign(answer['body'], h.secrets['audit'], 'audit')
            return answer
        with patch.object(gate, 'rpc', side_effect=intercept):
            result = h.execute()
        self.assertEqual(result['state'], 'blocked')
        self.assertEqual(h.counts()['backend_requests'], 0)

    def test_durable_success_survives_lookup_service_outage(self):
        h = self.h
        self.assertEqual(h.execute()['state'], 'confirmed_success')
        h.stop('backend')
        self.assertEqual(reconcile(h.gate, h.op)['state'], 'confirmed_success')
        self.assertEqual(h.counts()['backend_requests'], 1)

    def test_concurrent_confirmation_is_not_called_an_unknown_event(self):
        h = self.h
        h.execute()
        result = unresolved(h.gate, h.op, 'late_response_timeout')
        self.assertEqual(result['state'], 'confirmed_success')
        self.assertFalse(result['unknown_outcome_persisted'])
        self.assertNotIn('unknown', [e['body']['event_type'] for e in h.events()])

    def test_adapter_rejects_unknown_after_confirmation(self):
        h = self.h
        h.execute()
        events = h.events()
        bad = copy.deepcopy(events[-1]['body'])
        bad.update(event_id=h.op['operation_id'] + ':unknown', event_type='unknown',
                   payload={'operation_digest': digest(h.op), 'reason': 'late timeout'})
        events.append(sign(bad, h.secrets['audit'], 'audit', research=True))
        from record_gate.bridge import validate_events
        with self.assertRaisesRegex(Rejected, 'unknown_after_confirmed_result'):
            validate_events(events, h.op, h.publics['audit'], h.publics['backend'], h.publics['authority'])

    def test_offline_adapter_rechecks_scope_operation_binding(self):
        bundle = self.h.evidence(final=False)
        bundle['package']['experimental']['scope']['body']['configuration_digest'] = '0' * 64
        with self.assertRaisesRegex(Rejected, 'scope_operation_binding'):
            verify_bundle(bundle)

    def test_losing_claim_observes_concurrent_durable_success(self):
        h, original = self.h, gate.audit_call
        triggered = False
        def intercept(config, action, op, **fields):
            nonlocal triggered
            answer = original(config, action, op, **fields)
            if action == 'prepare' and not triggered:
                triggered = True
                self.assertEqual(h.execute()['state'], 'confirmed_success')
            return answer
        with patch.object(gate, 'audit_call', side_effect=intercept):
            result = h.execute()
        self.assertEqual(result['state'], 'confirmed_success')
        self.assertFalse(result['backend_attempted'])
        self.assertEqual(h.counts()['backend_requests'], 1)

    def test_caller_mutation_cannot_swap_final_authorization(self):
        h, original = self.h, gate.audit_call
        request = h.request
        other_op = copy.deepcopy(h.op)
        other_op['args']['text'] = 'another intent'
        other = h.make_request(other_op)
        h.retoken(other, 'approval', id='approval-002')
        def intercept(config, action, op, **fields):
            answer = original(config, action, op, **fields)
            if action == 'prepare':
                h.revoke(['approval-001'])
                request.clear()
                request.update(other)
            return answer
        with patch.object(gate, 'audit_call', side_effect=intercept):
            result = gate.execute(h.gate, request)
        self.assertEqual(result['state'], 'denied')
        self.assertEqual(result['reason'], 'approval_revoked')
        self.assertEqual(h.counts()['backend_requests'], 0)


class ReviewExportTests(unittest.TestCase):
    def test_empty_summary_does_not_succeed_without_verifying_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save(root / 'latency.json', {})
            save(root / 'summary.json', {'cases': [], 'latency_digest': digest({})})
            with self.assertRaises(Rejected):
                verify_exports(root)


class ReviewArchiveTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        # Use actual recorded public evidence; copy only simple JSON filenames.
        with tarfile.open(ROOT / 'results' / 'mock-evidence-and-reports.tar.gz') as archive:
            for member in archive.getmembers():
                if member.isfile() and '/' not in member.name and member.name.endswith('.json'):
                    save(self.root / member.name, json.loads(archive.extractfile(member).read()))
        self.summary = json.loads((self.root / 'summary.json').read_text())

    def rewrite_artifact(self, case, change):
        path = self.root / (case + '.json')
        artifact = json.loads(path.read_text())
        change(artifact)
        save(path, artifact)
        for row in self.summary['cases']:
            if row['case'] == case:
                row['artifact_digest'] = digest(artifact)
        save(self.root / 'summary.json', self.summary)

    def test_missing_primary_evidence_not_skipped_even_if_digest_updated(self):
        self.rewrite_artifact('01', lambda artifact: artifact.update(evidence=None))
        with self.assertRaisesRegex(Rejected, 'missing_or_unexpected_evidence_bundle'):
            verify_exports(self.root)

    def test_missing_recovered_evidence_not_skipped(self):
        self.rewrite_artifact('04', lambda artifact: artifact['details'].pop('recovered_evidence'))
        with self.assertRaisesRegex(Rejected, 'missing_or_unexpected_evidence_bundle'):
            verify_exports(self.root)

    def test_recovery_report_cannot_accept_missing_result_evidence(self):
        from scope_verifier.verifier import verify
        def remove_result(artifact):
            bundle = artifact['details']['recovered_evidence']
            package = bundle['package']
            package['events'] = [e for e in package['events'] if e['signed']['body']['event_type'] != 'result']
            bundle['native_receipt_check'] = 'unavailable'
            bundle['reports'] = {mode: verify(package, bundle['trust'], mode, bundle['evaluation_time'], True)
                                 for mode in ('vap-v1.2', 'experimental-scope')}
        self.rewrite_artifact('04', remove_result)
        with self.assertRaisesRegex(Rejected, 'recovery_evidence_not_confirmed'):
            verify_exports(self.root)

    def test_duplicate_case_cannot_stand_in_for_a_missing_case(self):
        self.summary['cases'][-1] = copy.deepcopy(self.summary['cases'][0])
        save(self.root / 'summary.json', self.summary)
        with self.assertRaisesRegex(Rejected, 'invalid_case_inventory'):
            verify_exports(self.root)

    def test_case_name_cannot_escape_export_directory(self):
        self.summary['cases'][0]['case'] = '../outside'
        save(self.root / 'summary.json', self.summary)
        with self.assertRaisesRegex(Rejected, 'invalid_case_inventory'):
            verify_exports(self.root)
