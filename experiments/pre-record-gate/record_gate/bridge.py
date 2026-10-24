"""Submit real signed audit events to the unchanged PR #10 verifier.

Scope/anchor receipts use a synthetic clock and harness-controlled keys. This is
not independent timing, a VAP gate requirement, or a proof of complete observation.
"""
from scope_verifier import ADAPTER
from scope_verifier.crypto import audit_path, digest, leaf_hash, merkle_root
from scope_verifier.verifier import verify
from .common import check, require, sign
from .auth import authorize

POLICY = {'id': 'one-mock-write-evidence/1', 'adapter': ADAPTER,
          'event_signers': {'gate-audit': ['audit']}, 'multiplicity': 'exactly-one-per-obligation',
          'timing_register_id': 'synthetic-gate-register',
          'observation_assurance': 'One specified mock operation only; no production or independent assurance'}
EVALUATION_ID = 'synthetic-gate-exercise'
EVALUATION_TIME = 2000000400


def body(kind, **fields):
    return {'kind': kind, 'evaluation_id': EVALUATION_ID, 'policy_digest': digest(POLICY), **fields}


def obligations(op):
    return [{'id': op['operation_id'] + ':' + suffix, 'source_id': 'gate-audit',
             'event_type': suffix, 'disclosure': 'full'} for suffix in ('request', 'dispatch', 'result')]


def prepare_scope(op, secret):
    """Called before dispatch, to commit the three evidence obligations (not future events)."""
    return sign(body('scope', revision='1', previous_revision=None,
        systems=['loopback-mock-api'], operations=['create_record'], event_classes=['request', 'dispatch', 'result'],
        exclusions=['All operations outside this one synthetic operation; all real-world activity'],
        observation_boundary='Role-separated local audit process; same host administrator controls all keys',
        configuration_digest=digest({'operation': op, 'adapter': 'pre-record-gate/1'}),
        controllers=['single test harness operator'], claimed_independence=False,
        start=2000000100, end=2000000200, commitment_cutoff=2000000050, submission_deadline=2000000300,
        interval='[start,end]', time_basis='synthetic POSIX integer seconds', inventory_mode='fixed',
        derivation_rule='explicit-obligations-v1', closure_rule='signed-source-enumeration-v1',
        expectation_source='gate-exercise-inventory', expected_digest=digest(obligations(op)),
        individually_required=[], relationships=[]), secret, 'exporter', research=True)


def synthetic_scope_receipt(scope, secret):
    return sign(body('receipt', target_digest=digest(scope), purpose='scope', accepted_at=2000000040,
                     uncertainty=1, adapter='synthetic-receipt/1'), secret, 'exporter', research=True)


def validate_events(events, op, audit_public, backend_public, authority_public):
    request_seen = False
    result_seen = False
    seen = set()
    for event in events:
        b = check(event, audit_public, 'event', 'audit', research=True)
        require(b['evaluation_id'] == EVALUATION_ID and b['policy_digest'] == digest(POLICY)
                and b['source_id'] == 'gate-audit' and b['payload']['operation_digest'] == digest(op), 'audit_event_binding')
        suffix = b['event_type']
        require(suffix in ('request', 'dispatch', 'result', 'unknown')
                and b['event_id'] == op['operation_id'] + ':' + suffix and suffix not in seen, 'audit_event_identity')
        seen.add(suffix)
        if suffix == 'request':
            require(digest(b['payload']['intent']) == digest(op)
                    and digest(b['payload']['signed_request']['intent']) == digest(op), 'audit_request_binding')
            recorded = b['payload']['authorization']
            verified_op, verified_auth = authorize(b['payload']['signed_request'], {
                'authority_public': authority_public, 'evaluation_time': recorded['checked_at']},
                status_envelope=recorded['revocation_snapshot'])
            require(digest(verified_op) == digest(op) and digest(verified_auth) == digest(recorded), 'recorded_authorization_mismatch')
            request_seen = True
        if suffix == 'dispatch':
            require(digest(b['payload']['intent']) == digest(op), 'dispatch_intent_binding')
        if suffix in ('dispatch', 'unknown', 'result'):
            require(request_seen, 'request_must_precede_dispatch')
        if suffix in ('unknown', 'result'):
            require('dispatch' in seen, 'dispatch_must_precede_outcome')
        if suffix == 'result':
            receipt = check(b['payload']['receipt'], backend_public, 'backend_receipt', 'backend')
            require(receipt['operation_digest'] == digest(op) and receipt['operation_id'] == op['operation_id']
                    and receipt['committed'] is True, 'native_result_binding')
            result_seen = True
    require(not result_seen or (request_seen and 'dispatch' in seen), 'missing_result_predecessors')
    return result_seen


def export_package(events, op, scope, keys, *, final):
    """Preserve audit signatures; no reconstructed/re-signed historical events."""
    audit_public, backend_public = keys['audit_public'], keys['backend_public']
    require(scope['body']['configuration_digest'] == digest({'operation': op, 'adapter': 'pre-record-gate/1'}), 'scope_operation_binding')
    result_seen = validate_events(events, op, audit_public, backend_public, keys['authority_public'])
    secret = keys['exporter_secret']
    def signed(kind, **fields):
        return sign(body(kind, **fields), secret, 'exporter', research=True)
    def receipt(target, purpose, at):
        return signed('receipt', target_digest=digest(target), purpose=purpose, accepted_at=at,
                      uncertainty=1, adapter='synthetic-receipt/1')
    leaves = [leaf_hash(e['body']) for e in events]
    index = [{'event_id': e['body']['event_id'], 'source_id': 'gate-audit',
              'event_type': e['body']['event_type'], 'leaf_hash': h.hex()} for e, h in zip(events, leaves)]
    delivered = [{'signed': e, 'event_hash': digest(e['body']), 'index': i, 'path': audit_path(leaves, i)}
                 for i, e in enumerate(events)]
    anchor = signed('anchor', batch={'merkle_root': merkle_root(leaves).hex(), 'event_count': len(events),
        'first_event_id': index[0]['event_id'] if index else None, 'last_event_id': index[-1]['event_id'] if index else None,
        'policy_digest': digest(POLICY), 'index_digest': digest(index)})
    required, sd = obligations(op), digest(scope)
    ids = {e['body']['event_id'] for e in events}
    inventory = signed('inventory', scope_digest=sd, obligations=required)
    closure = signed('closure', scope_digest=sd, source_id='gate-exercise-inventory',
        configuration_digest=scope['body']['configuration_digest'], end=2000000200, closed=final,
        closed_at=2000000210, closed_sources=['gate-audit'] if final else [], observation_gaps=[],
        expected_digest=digest(required))
    manifest = signed('manifest', scope_digest=sd, anchor_digest=digest(anchor), final=final,
        finalized_at=2000000310, delivery_digest=digest({'events': delivered, 'commitment_proofs': []}),
        entries=[{'id': r['id'], 'state': 'included' if r['id'] in ids else 'unaccounted'} for r in required])
    package = {'format': ADAPTER, 'policy': POLICY, 'events': delivered, 'batch_index': index,
        'anchor': anchor, 'anchor_receipt': receipt(anchor, 'anchor', 2000000250), 'commitment_proofs': [],
        'experimental': {'scope': scope, 'scope_receipt': keys['scope_receipt'],
                         'inventory': inventory, 'closure': closure, 'manifest': manifest}}
    trust = {'purpose': 'synthetic-test-only', 'evaluation_id': EVALUATION_ID, 'policy_digest': digest(POLICY),
        'scope_digest': sd, 'keys': {'audit': {'public_key': audit_public, 'roles': ['event']},
        'exporter': {'public_key': keys['exporter_public'], 'roles': ['scope', 'inventory', 'closure', 'manifest', 'anchor', 'receipt']}}}
    reports = {mode: verify(package, trust, mode, EVALUATION_TIME, allow_synthetic=True)
               for mode in ('vap-v1.2', 'experimental-scope')}
    return {'adapter_trust': {'operation': op, 'audit_public': audit_public, 'backend_public': backend_public,
                               'authority_public': keys['authority_public']},
            'package': package, 'trust': trust, 'evaluation_time': EVALUATION_TIME,
            'native_receipt_check': 'verified' if result_seen else 'unavailable', 'reports': reports}
