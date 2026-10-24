"""Failure-path regression tests, beyond the executable acceptance scenarios."""
import copy
import unittest
from unittest.mock import patch

import record_gate  # Makes the unchanged sibling verifier importable.
from scope_verifier.crypto import digest
from record_gate.auth import authorize
from record_gate.bridge import export_package
from record_gate.common import Rejected, check, decode, rpc, sign
from record_gate.gate import audit_call, control, execute, receipt_check, reconcile
from record_gate.harness import Harness, NOW


class GateTests(unittest.TestCase):
    def setUp(self):
        self.h = Harness()
        self.addCleanup(self.h.close)

    def package(self, events):
        h = self.h
        return export_package(events, h.op, h.scope, {
            'audit_public': h.publics['audit'], 'backend_public': h.publics['backend'],
            'exporter_secret': h.secrets['exporter'], 'exporter_public': h.publics['exporter'],
            'authority_public': h.publics['authority'], 'scope_receipt': h.scope_receipt}, final=True)

    def test_agent_proof_is_checked(self):
        h = self.h
        h.request['proof']['signature'] = '00' * 64
        self.assertEqual(h.execute()['reason'], 'invalid_request_signature_or_shape')
        self.assertEqual(h.counts()['backend_requests'], 0)

    def test_self_reported_identity_does_not_override_verified_claims(self):
        h = self.h
        h.request.update(agent_id='administrator', human_approved=True, delegator='forged-owner')
        self.assertEqual(h.execute()['state'], 'confirmed_success')
        auth = h.events()[0]['body']['payload']['authorization']
        self.assertEqual(auth['subject'], 'synthetic-agent')
        self.assertEqual(auth['delegator'], 'synthetic-owner')

    def test_missing_approval_cannot_be_replaced_by_boolean(self):
        h = self.h
        del h.request['approval']
        h.request['human_approved'] = True
        self.assertEqual(h.execute()['state'], 'denied')
        self.assertEqual(h.counts()['backend_requests'], 0)

    def test_missing_revocation_status_blocks(self):
        h = self.h
        (h.root / 'authority' / 'revocations.json').unlink()
        self.assertEqual(h.execute()['state'], 'denied')
        self.assertEqual(h.counts()['backend_requests'], 0)

    def test_bool_expiry_rejected(self):
        h = self.h
        h.retoken(h.request, 'approval', expires=True)
        self.assertEqual(h.execute()['reason'], 'approval_expired_or_not_yet_valid')

    def test_proof_cannot_bind_different_credential(self):
        h = self.h
        old_proof = copy.deepcopy(h.request['proof'])
        h.retoken(h.request, 'credential', id='credential-002')
        h.request['proof'] = old_proof
        self.assertEqual(h.execute()['reason'], 'request_binding')

    def test_revocation_between_prepare_and_claim_blocks(self):
        h = self.h
        from record_gate import gate
        real = gate.audit_call
        def intercept(config, action, op, **fields):
            result = real(config, action, op, **fields)
            if action == 'prepare':
                h.revoke(['approval-001'])
            return result
        with patch.object(gate, 'audit_call', side_effect=intercept):
            result = h.execute()
        self.assertEqual(result['reason'], 'approval_revoked')
        self.assertEqual(h.counts()['backend_requests'], 0)
        self.assertEqual(h.state(), 'prepared')

    def test_record_cannot_be_reused_for_another_target(self):
        h = self.h
        op = copy.deepcopy(h.op)
        op['target'] = 'sandbox/other'
        self.assertEqual(h.execute(candidate=op)['state'], 'denied')
        self.assertEqual(h.counts()['backend_requests'], 0)

    def test_same_intent_id_different_actor_authorization_is_rejected(self):
        h = self.h
        op, auth = authorize(h.request, h.gate)
        audit_call(h.gate, 'prepare', op, request=h.request, authorization=auth)
        req = h.make_request(op)
        h.retoken(req, 'approval', id='approval-002')
        self.assertEqual(execute(h.gate, req)['state'], 'blocked')
        self.assertEqual(h.counts()['backend_requests'], 0)

    def test_direct_call_signed_by_agent_not_gate_is_rejected(self):
        h = self.h
        forged = sign({'kind': 'control', 'action': 'write', 'intent': h.op}, h.secrets['agent'], 'gate')
        with self.assertRaises(Rejected):
            rpc(h.gate['backend_url'], '/write', forged)
        self.assertEqual(h.counts()['effects'], 0)

    def test_gate_signature_without_audit_permit_is_rejected(self):
        h = self.h
        with self.assertRaises(Rejected):
            rpc(h.gate['backend_url'], '/write', control(h.gate, 'write', intent=h.op))
        self.assertEqual(h.counts()['effects'], 0)

    def test_prepare_ack_is_not_a_dispatch_permit(self):
        h = self.h
        op, auth = authorize(h.request, h.gate)
        ack, _ = audit_call(h.gate, 'prepare', op, request=h.request, authorization=auth)
        with self.assertRaises(Rejected):
            rpc(h.gate['backend_url'], '/write', control(h.gate, 'write', intent=op, permit=ack))
        self.assertEqual(h.counts()['effects'], 0)

    def test_permit_cannot_authorize_different_arguments(self):
        h = self.h
        op, auth = authorize(h.request, h.gate)
        audit_call(h.gate, 'prepare', op, request=h.request, authorization=auth)
        permit, _ = audit_call(h.gate, 'claim', op)
        changed = copy.deepcopy(op)
        changed['args']['text'] = 'different'
        with self.assertRaises(Rejected):
            rpc(h.gate['backend_url'], '/write', control(h.gate, 'write', intent=changed, permit=permit))
        self.assertEqual(h.counts()['effects'], 0)

    def test_backend_atomic_idempotency_and_parameter_mismatch(self):
        h = self.h
        op, auth = authorize(h.request, h.gate)
        audit_call(h.gate, 'prepare', op, request=h.request, authorization=auth)
        permit, _ = audit_call(h.gate, 'claim', op)
        message = control(h.gate, 'write', intent=op, permit=permit)
        first = rpc(h.gate['backend_url'], '/write', message)
        second = rpc(h.gate['backend_url'], '/write', message)
        self.assertEqual(first, second)
        self.assertEqual(h.counts()['effects'], 1)
        # Even a trusted harness-created permit cannot change an already committed ID.
        changed = copy.deepcopy(op)
        changed['args']['text'] = 'different'
        forged_permit = sign({**permit['body'], 'operation_digest': digest(changed)}, h.secrets['audit'], 'audit')
        with self.assertRaises(Rejected):
            rpc(h.gate['backend_url'], '/write', control(h.gate, 'write', intent=changed, permit=forged_permit))
        self.assertEqual(h.counts()['effects'], 1)

    def test_fake_backend_receipt_cannot_mark_success(self):
        h = self.h
        op, auth = authorize(h.request, h.gate)
        audit_call(h.gate, 'prepare', op, request=h.request, authorization=auth)
        audit_call(h.gate, 'claim', op)
        forged = sign({'kind': 'backend_receipt', 'operation_id': op['operation_id'],
                       'operation_digest': digest(op), 'committed': True}, h.secrets['agent'], 'backend')
        with self.assertRaises(Rejected):
            audit_call(h.gate, 'outcome', op, state='confirmed_success', receipt=forged)
        self.assertEqual(h.state(), 'dispatch_intent')

    def test_valid_receipt_for_other_operation_is_rejected(self):
        h = self.h
        h.execute()
        receipt = h.events()[-1]['body']['payload']['receipt']
        other = copy.deepcopy(h.op)
        other['operation_id'] = 'other-operation'
        with self.assertRaises(Rejected):
            receipt_check(h.gate, receipt, other)

    def test_invalid_response_retains_unknown(self):
        h = self.h
        from record_gate import gate
        original = gate.rpc
        def corrupt(url, path, value):
            answer = original(url, path, value)
            if path == '/write':
                answer['signature'] = '00' * 64
            return answer
        with patch.object(gate, 'rpc', side_effect=corrupt):
            result = h.execute()
        self.assertEqual(result['state'], 'result_unknown')
        self.assertEqual(h.counts()['effects'], 1)
        self.assertEqual(h.state(), 'result_unknown')

    def test_unavailable_reconciliation_does_not_repeat_write(self):
        h = self.h
        op, auth = authorize(h.request, h.gate)
        audit_call(h.gate, 'prepare', op, request=h.request, authorization=auth)
        audit_call(h.gate, 'claim', op)
        h.stop('backend')
        result = reconcile(h.gate, h.op)
        self.assertEqual(result['state'], 'result_unknown')
        self.assertEqual(h.counts()['backend_requests'], 0)

    def test_audit_tampering_detected(self):
        h = self.h
        h.execute()
        events = h.events()
        events[0]['body']['payload']['authorization']['subject'] = 'forged'
        with self.assertRaises(Rejected):
            self.package(events)

    def test_adapter_verifies_nested_receipt_even_if_audit_signs_it(self):
        h = self.h
        h.execute()
        events = h.events()
        events[-1]['body']['payload']['receipt']['signature'] = '00' * 64
        events[-1] = sign(events[-1]['body'], h.secrets['audit'], 'audit', research=True)
        with self.assertRaises(Rejected):
            self.package(events)

    def test_adapter_rejects_substituted_native_receipt(self):
        h = self.h
        h.execute()
        events = h.events()
        native = events[-1]['body']['payload']['receipt']['body']
        native['operation_id'] = 'different-operation'
        events[-1]['body']['payload']['receipt'] = sign(native, h.secrets['backend'], 'backend')
        events[-1] = sign(events[-1]['body'], h.secrets['audit'], 'audit', research=True)
        with self.assertRaises(Rejected):
            self.package(events)

    def test_missing_result_pending_vs_final_are_distinct(self):
        h = self.h
        h.execute()
        events = h.events()[:-1]
        final = self.package(events)
        self.assertEqual(final['reports']['experimental-scope']['scope_fulfillment']['result'], 'not_met')
        self.assertEqual(final['reports']['vap-v1.2']['scope_fulfillment'], None)
        # Presenting all committed records is not the same as submitting required result evidence.
        self.assertEqual(final['reports']['vap-v1.2']['integrity']['result'], 'verified')

    def test_adapter_rejects_duplicate_audit_events(self):
        h = self.h
        h.execute()
        events = h.events()
        with self.assertRaises(Rejected):
            self.package(events + [events[0]])

    def test_adapter_rejects_result_before_dispatch(self):
        h = self.h
        h.execute()
        events = h.events()
        with self.assertRaises(Rejected):
            self.package([events[0], events[2], events[1]])

    def test_adapter_rechecks_authorization_not_just_audit_signature(self):
        h = self.h
        h.execute()
        events = h.events()
        events[0]['body']['payload']['authorization']['subject'] = 'forged-subject'
        events[0] = sign(events[0]['body'], h.secrets['audit'], 'audit', research=True)
        with self.assertRaises(Rejected):
            self.package(events)

    def test_adapter_rechecks_dispatch_arguments(self):
        h = self.h
        h.execute()
        events = h.events()
        events[1]['body']['payload']['intent']['args']['text'] = 'different'
        events[1] = sign(events[1]['body'], h.secrets['audit'], 'audit', research=True)
        with self.assertRaises(Rejected):
            self.package(events)

    def test_control_signature_not_research_signature(self):
        h = self.h
        body = {'kind': 'event', 'payload': 'test'}
        env = sign(body, h.secrets['audit'], 'audit')
        with self.assertRaises(Rejected):
            check(env, h.publics['audit'], 'event', 'audit', research=True)


class InputTests(unittest.TestCase):
    def test_duplicate_json_keys_rejected(self):
        with self.assertRaises(Rejected):
            decode(b'{"key":1,"key":2}')

    def test_nonfinite_json_rejected(self):
        with self.assertRaises(ValueError):
            decode(b'{"key":NaN}')

    def test_unsafe_json_integer_rejected(self):
        with self.assertRaises(ValueError):
            decode(b'{"key":9007199254740993}')

    def test_nonloopback_url_rejected_before_network(self):
        for url in ('https://example.invalid', 'http://localhost:123', 'http://127.0.0.1:123@evil.invalid',
                    'http://127.0.0.1:123/?redirect=evil'):
            with self.subTest(url=url), self.assertRaises(Rejected):
                rpc(url, '/write', {})


if __name__ == '__main__':
    unittest.main()
