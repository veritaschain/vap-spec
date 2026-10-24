"""Trusted setup only. Generated secrets are never copied into the image or reports."""
import os
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from record_gate.bridge import EVALUATION_ID, POLICY, prepare_scope, synthetic_scope_receipt
from record_gate.common import public, save, sign
from record_gate.harness import NOW
from scope_verifier.crypto import digest, strict_json
from . import ROLES


def generate():
    secrets = {r: Ed25519PrivateKey.generate().private_bytes_raw().hex()
               for r in (*ROLES, 'authority', 'exporter')}
    pubs = {r: public(s) for r, s in secrets.items()}
    op = {'operation_id': 'isolation-operation-001', 'action': 'create_record',
          'target': 'sandbox/records', 'args': {'text': 'synthetic isolation exercise'}}
    def token(kind, **claims):
        return sign({'kind': kind, 'id': kind + '-001', 'audience': 'experimental-gate',
                     'not_before': NOW - 100, 'expires': NOW + 100, **claims}, secrets['authority'], 'authority')
    credential = token('credential', subject='synthetic-agent', public_key=pubs['agent'])
    delegation = token('delegation', subject='synthetic-agent', delegator='synthetic-owner',
                       action=op['action'], target=op['target'])
    def request_for(operation):
        approval = token('approval', subject='synthetic-agent', approver='synthetic-approver',
                         delegation_digest=digest(delegation), operation_digest=digest(operation))
        request = {'intent': operation, 'credential': credential, 'delegation': delegation, 'approval': approval}
        request['proof'] = sign({'kind': 'request', 'operation_digest': digest(operation),
            **{n + '_digest': digest(request[n]) for n in ('credential', 'delegation', 'approval')}}, secrets['agent'], 'agent')
        return request
    request = request_for(op)
    fresh_op = {**op, 'operation_id': 'isolation-operation-002'}
    fresh_request = request_for(fresh_op)
    revocations = sign({'kind': 'revocations', 'issued_at': NOW - 1, 'valid_until': NOW + 100, 'revoked': []},
                       secrets['authority'], 'authority')
    configs = {
        'agent': {'secret': secrets['agent'], 'request': request, 'fresh_request': fresh_request},
        'gate': {'secret': secrets['gate'], 'audit_public': pubs['audit'], 'backend_public': pubs['backend'],
                 'authority_public': pubs['authority'], 'evaluation_time': NOW,
                 'revocations': '/run/role/revocations.json', 'audit_url': 'http://audit:8080',
                 'backend_url': 'http://backend:8080'},
        'audit': {'role': 'audit', 'database': '/data/ledger.sqlite', 'secret': secrets['audit'],
                  'gate_public': pubs['gate'], 'backend_public': pubs['backend'],
                  'evaluation_id': EVALUATION_ID, 'policy_digest': digest(POLICY)},
        'backend': {'role': 'backend', 'database': '/data/effects.sqlite', 'secret': secrets['backend'],
                    'gate_public': pubs['gate'], 'audit_public': pubs['audit']},
        'open-backend': {'role': 'backend', 'database': '/data/effects.sqlite', 'secret': secrets['open-backend'],
                         'gate_public': pubs['gate'], 'audit_public': pubs['audit'], 'insecure': True},
    }
    scope = prepare_scope(op, secrets['exporter'])
    return {'configs': configs, 'revocations': revocations, 'scope': scope,
            'scope_receipt': synthetic_scope_receipt(scope, secrets['exporter']),
            'operation': op, 'publics': pubs, 'exporter_secret': secrets['exporter']}


def initialize(seed_path):
    """Runs once as root in a network-less setup container, never in an agent container."""
    seed = strict_json(seed_path)
    for role, uid in ROLES.items():
        for kind in ('config', 'data'):
            path = Path('/volumes') / (role + '-' + kind)
            path.mkdir(parents=True, exist_ok=True)
            os.chown(path, uid, uid)
            path.chmod(0o700)
        config = Path('/volumes') / (role + '-config') / 'config.json'
        save(config, seed['configs'][role])
        os.chown(config, uid, uid)
        config.chmod(0o400)
        if role == 'gate':
            status = config.parent / 'revocations.json'
            save(status, seed['revocations'])
            os.chown(status, uid, uid)
            status.chmod(0o400)
        # Shared *non-secret* canaries let tests distinguish EACCES from an absent mount.
        directory = Path('/canaries') / role
        directory.mkdir(exist_ok=True)
        os.chown(directory, uid, uid)
        directory.chmod(0o700)
        marker = directory / 'marker'
        marker.write_text('public-test-canary:' + role)
        os.chown(marker, uid, uid)
        marker.chmod(0o400)
    print('{"initialized":true}')
