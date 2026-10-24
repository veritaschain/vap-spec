"""One dispatch attempt after durable recording; recovery only queries the mock API."""
import os
import signal
import time

from scope_verifier.crypto import digest
from .auth import authorize
from .common import canonical, check, decode, intent, require, rpc, sign


def control(config, action, **fields):
    return sign({'kind': 'control', 'action': action, **fields}, config['secret'], 'gate')


def audit_call(config, action, op, **fields):
    env = rpc(config['audit_url'], '/' + action, control(config, action, intent=op, **fields))
    ack = check(env, config['audit_public'], 'audit_ack', 'audit')
    require(ack['action'] == action and ack['operation_id'] == op['operation_id']
            and ack['operation_digest'] == digest(op), 'audit_ack_binding')
    state = ack.get('state')
    require(state in ('prepared', 'dispatch_intent', 'result_unknown', 'confirmed_success')
            and type(ack.get('claimed')) is bool and 'receipt' in ack, 'audit_ack_state_shape')
    if state == 'confirmed_success':
        receipt_check(config, ack['receipt'], op)
    else:
        require(ack['receipt'] is None, 'unexpected_audit_receipt')
    if action == 'claim':
        require(state != 'prepared' and (not ack['claimed'] or state == 'dispatch_intent'), 'audit_claim_not_recorded')
    else:
        require(ack['claimed'] is False, 'unexpected_dispatch_claim')
    if action == 'outcome':
        permitted = ('confirmed_success',) if fields['state'] == 'confirmed_success' else ('result_unknown', 'confirmed_success')
        require(state in permitted, 'audit_outcome_not_recorded')
    return env, ack


def receipt_check(config, receipt, op):
    body = check(receipt, config['backend_public'], 'backend_receipt', 'backend')
    require(body['operation_id'] == op['operation_id'] and body['operation_digest'] == digest(op)
            and body['committed'] is True, 'backend_receipt_binding')


def unresolved(config, op, reason):
    try:
        _, ack = audit_call(config, 'outcome', op, state='result_unknown', reason=reason)
        if ack['state'] == 'confirmed_success':
            return {'state': 'confirmed_success', 'reason': 'durable_result_already_confirmed',
                    'unknown_outcome_persisted': False, 'automatic_write_retry': False}
        durable = True
    except Exception:
        # At least the prior dispatch intent remains; success needs a valid acknowledgment.
        durable = False
    return {'state': 'result_unknown', 'reason': reason, 'unknown_outcome_persisted': durable,
            'automatic_write_retry': False}


def execute(config, request, *, candidate=None, fault=None):
    started = time.perf_counter_ns()
    try:
        # Own a canonical snapshot: caller mutations cannot swap the final authorization.
        request = decode(canonical(request))
        op, identity = authorize(request, config)
    except Exception as exc:
        return {'state': 'denied', 'reason': str(exc), 'backend_attempted': False}
    try:
        _, ack = audit_call(config, 'prepare', op, request=request, authorization=identity)
    except Exception:
        return {'state': 'blocked', 'reason': 'pre_record_not_acknowledged', 'backend_attempted': False}
    if ack['state'] == 'confirmed_success':
        return {'state': 'confirmed_success', 'reason': 'previously_confirmed_no_resend', 'backend_attempted': False}
    if ack['state'] != 'prepared':
        return {'state': 'result_unknown', 'reason': 'prior_dispatch_requires_reconciliation', 'backend_attempted': False}
    if fault == 'crash-after-prepare':
        os.kill(os.getpid(), signal.SIGKILL)
    try:
        actual = intent(candidate if candidate is not None else op)
        require(digest(actual) == digest(op), 'recorded_request_mismatch')
        # Refresh trusted revocation status and validity immediately before claiming.
        refreshed_op, _ = authorize(request, config)
        require(digest(refreshed_op) == digest(op), 'authorization_intent_changed')
    except Exception as exc:
        return {'state': 'denied', 'reason': str(exc), 'backend_attempted': False}
    try:
        permit, ack = audit_call(config, 'claim', op)
    except Exception:
        return {'state': 'blocked', 'reason': 'dispatch_record_not_acknowledged', 'backend_attempted': False}
    if ack['claimed'] is not True:
        if ack['state'] == 'confirmed_success':
            return {'state': 'confirmed_success', 'reason': 'concurrent_durable_confirmation', 'backend_attempted': False}
        return {'state': 'result_unknown', 'reason': 'dispatch_already_claimed', 'backend_attempted': False}
    if fault == 'crash-after-claim':
        os.kill(os.getpid(), signal.SIGKILL)
    before_send_ms = (time.perf_counter_ns() - started) / 1e6
    try:
        receipt = rpc(config['backend_url'], '/write', control(config, 'write', intent=actual, permit=permit))
        receipt_check(config, receipt, op)
    except Exception:
        return {**unresolved(config, op, 'response_missing_or_invalid'), 'backend_attempted': True,
                'before_send_ms': before_send_ms}
    try:
        audit_call(config, 'outcome', op, state='confirmed_success', receipt=receipt)
    except Exception:
        return {**unresolved(config, op, 'result_not_durably_recorded'), 'backend_attempted': True,
                'before_send_ms': before_send_ms}
    return {'state': 'confirmed_success', 'reason': 'signed_backend_receipt_durably_recorded',
            'backend_attempted': True, 'before_send_ms': before_send_ms,
            'total_ms': (time.perf_counter_ns() - started) / 1e6}


def reconcile(config, op):
    op = intent(op)
    # Read-only lookup cannot replay a write. A missing lookup is NOT proof of nonexecution.
    try:
        _, ack = audit_call(config, 'get', op)
        if ack['state'] == 'confirmed_success':
            return {'state': 'confirmed_success', 'reason': 'previously_confirmed_no_lookup'}
        if ack['state'] == 'prepared':
            return {'state': 'not_dispatched', 'reason': 'no_durable_dispatch_intent'}
        answer = rpc(config['backend_url'], '/lookup', control(config, 'lookup', intent=op))
        lookup = check(answer, config['backend_public'], 'lookup', 'backend')
        require(lookup['operation_id'] == op['operation_id'] and lookup['operation_digest'] == digest(op), 'lookup_binding')
        if lookup['receipt'] is None:
            return {'state': 'result_unknown', 'reason': 'no_receipt_found_not_proof_of_nonexecution'}
        receipt_check(config, lookup['receipt'], op)
        audit_call(config, 'outcome', op, state='confirmed_success', receipt=lookup['receipt'])
        return {'state': 'confirmed_success', 'reason': 'reconciled_by_read_only_lookup'}
    except Exception:
        return {'state': 'result_unknown', 'reason': 'reconciliation_unavailable_or_invalid'}
