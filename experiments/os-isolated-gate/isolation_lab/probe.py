"""Benign probes executed under each container's actual UID/namespaces/capabilities."""
import os
from contextlib import closing
from pathlib import Path
import sqlite3

from record_gate.common import check
from record_gate.gate import control
from scope_verifier.crypto import strict_json
from . import ROLES
from .transport import exchange, service_rpc


def attempt(operation):
    try:
        operation()
        return {'allowed': True, 'errno': None}
    except OSError as exc:
        return {'allowed': False, 'errno': exc.errno, 'error': type(exc).__name__}


def identity():
    status = {}
    for line in Path('/proc/self/status').read_text().splitlines():
        if ':' in line:
            k, v = line.split(':', 1)
            if k in ('CapEff', 'CapPrm', 'CapBnd', 'NoNewPrivs', 'Seccomp'):
                status[k] = v.strip()
    return {'uid': os.getuid(), 'gid': os.getgid(), 'groups': os.getgroups(), 'security': status,
            'namespaces': {n: os.readlink('/proc/self/ns/' + n) for n in ('mnt', 'pid', 'net')},
            'setuid_zero': attempt(lambda: os.setuid(0))}


def filesystem(role):
    reads = {other: attempt(lambda other=other: (Path('/canaries') / other / 'marker').read_bytes())
             for other in ROLES}
    return {'canaries': reads,
            'config_write': attempt(lambda: Path('/run/role/config.json').open('ab').close()),
            'code_write': attempt(lambda: Path('/app/write-probe').write_bytes(b'probe')),
            'docker_socket_visible': Path('/var/run/docker.sock').exists(),
            'setup_seed_visible': Path('/seed').exists(),
            'own_config_readable': attempt(lambda: Path('/run/role/config.json').read_bytes())}


def network(host, port, path='/write', method='POST', operation_id='direct-bypass-001'):
    op = {'operation_id': operation_id, 'action': 'create_record', 'target': 'sandbox/records',
          'args': {'text': 'synthetic direct-call probe'}}
    connected = False
    def mark_connected():
        nonlocal connected
        connected = True
    try:
        status, body = exchange(host, port, path, {'intent': op}, method=method, on_connected=mark_connected)
        return {'connected': True, 'http_status': status, 'body': body}
    except (OSError, TimeoutError) as exc:
        return {'connected': connected, 'http_status': None, 'error': type(exc).__name__, 'errno': getattr(exc, 'errno', None)}


def execute_request(kind):
    config = strict_json('/run/role/config.json')
    request = config['fresh_request' if kind == 'fresh' else 'request']
    if kind == 'bad-target':
        request['intent']['target'] = 'http://backend:8080/write'
    status, body = exchange('gate', 8080, '/execute', request, timeout=10)
    return {'http_status': status, 'result': body}


def counts():
    config = strict_json('/run/role/config.json')
    with closing(sqlite3.connect(config['database'])) as db:
        return {'effects': db.execute('SELECT count(*) FROM effects').fetchone()[0],
                'requests': db.execute('SELECT count(*) FROM attempts').fetchone()[0]}


def export_events():
    config = strict_json('/run/role/config.json')
    envelope = service_rpc(config['audit_url'], '/export', control(config, 'export'))
    return check(envelope, config['audit_public'], 'audit_export', 'audit')['events']


def local_log(action):
    path = Path('/data/agent-log.json')
    if action == 'create':
        path.write_text('{"self_reported":"untrusted"}')
    else:
        path.unlink()
    return {'exists': path.exists()}
