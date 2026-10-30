"""Synthetic authorities and proof of possession, not production identity integration."""
from scope_verifier.crypto import digest, strict_json
from .common import check, intent, require


def authorize(request, config, *, status_envelope=None):
    now = config['evaluation_time']  # Trusted harness clock, never supplied by the agent.
    trust = config['authority_public']
    envelope = strict_json(config['revocations']) if status_envelope is None else status_envelope
    status = check(envelope, trust, 'revocations', 'authority')
    require(type(status['issued_at']) is int and type(status['valid_until']) is int
            and status['issued_at'] <= now < status['valid_until'], 'revocation_status_stale')
    require(isinstance(status['revoked'], list) and all(isinstance(x, str) for x in status['revoked']), 'revocation_status_shape')
    claims = {}
    for name in ('credential', 'delegation', 'approval'):
        body = check(request[name], trust, name, 'authority')
        require(body['audience'] == 'experimental-gate', name + '_audience')
        require(type(body['not_before']) is int and type(body['expires']) is int
                and body['not_before'] <= now < body['expires'], name + '_expired_or_not_yet_valid')
        require(isinstance(body['id'], str) and body['id'] not in status['revoked'], name + '_revoked')
        claims[name] = body
    c, d, a = (claims[n] for n in ('credential', 'delegation', 'approval'))
    require(isinstance(c['subject'], str) and bool(c['subject']), 'credential_subject')
    require(d['subject'] == c['subject'] and isinstance(d['delegator'], str) and bool(d['delegator']), 'delegation_subject')
    op = intent(request['intent'])
    require(d['action'] == op['action'] and d['target'] == op['target'], 'delegation_scope')
    require(a['subject'] == c['subject'] and a['delegation_digest'] == digest(request['delegation'])
            and a['operation_digest'] == digest(op), 'approval_scope')
    require(isinstance(a['approver'], str) and bool(a['approver']), 'approval_approver')
    proof = check(request['proof'], c['public_key'], 'request', 'agent')
    require(proof == {'kind': 'request', 'operation_digest': digest(op),
                     **{n + '_digest': digest(request[n]) for n in claims}}, 'request_binding')
    return op, {'subject': c['subject'], 'delegator': d['delegator'], 'approver': a['approver'],
                'credential_id': c['id'], 'delegation_id': d['id'], 'approval_id': a['id'],
                'request_digest': digest(request), 'revocations_digest': digest(status),
                'revocation_snapshot': envelope, 'checked_at': now}
