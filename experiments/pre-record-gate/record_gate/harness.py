"""Trusted synthetic test setup. Private keys never belong to the agent directory."""
import copy
import json
from contextlib import closing
import selectors
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from scope_verifier.crypto import digest
from .bridge import EVALUATION_ID, POLICY, export_package, prepare_scope, synthetic_scope_receipt
from .common import check, public, rpc, save, sign
from .gate import control, execute

ROOT = Path(__file__).resolve().parents[1]
NOW = 2000000150


class Harness:
    def __init__(self, *, audit_options=None, backend_options=None):
        self.tmp = tempfile.TemporaryDirectory(prefix='mock-record-gate-')
        self.root = Path(self.tmp.name)
        for role in ('agent', 'audit', 'gate', 'backend', 'authority', 'exporter'):
            (self.root / role).mkdir(mode=0o700)
        self.secrets = {r: Ed25519PrivateKey.generate().private_bytes_raw().hex()
                        for r in ('agent', 'audit', 'gate', 'backend', 'authority', 'exporter')}
        self.publics = {r: public(s) for r, s in self.secrets.items()}
        self.op = {'operation_id': 'synthetic-operation-001', 'action': 'create_record',
                   'target': 'sandbox/records', 'args': {'text': 'synthetic content only'}}
        self.request = self.make_request(self.op)
        self.scope = prepare_scope(self.op, self.secrets['exporter'])  # Before any dispatch.
        self.scope_receipt = synthetic_scope_receipt(self.scope, self.secrets['exporter'])
        self.configs, self.processes = {}, {}
        self.configs['audit'] = {'role': 'audit', 'database': str(self.root / 'audit' / 'ledger.sqlite'),
            'secret': self.secrets['audit'], 'gate_public': self.publics['gate'],
            'backend_public': self.publics['backend'], 'evaluation_id': EVALUATION_ID,
            'policy_digest': digest(POLICY), **(audit_options or {})}
        self.configs['backend'] = {'role': 'backend', 'database': str(self.root / 'backend' / 'effects.sqlite'),
            'secret': self.secrets['backend'], 'gate_public': self.publics['gate'],
            'audit_public': self.publics['audit'], **(backend_options or {})}
        self.gate = {'secret': self.secrets['gate'], 'audit_public': self.publics['audit'],
            'backend_public': self.publics['backend'], 'authority_public': self.publics['authority'],
            'evaluation_time': NOW, 'revocations': str(self.root / 'authority' / 'revocations.json')}
        self.revoke([])
        try:
            self.start('audit')
            self.start('backend')
        except Exception:
            self.close()
            raise
        save(self.root / 'agent' / 'request.json', self.request)
        save(self.root / 'agent' / 'local-log.json', {'self_reported': 'untrusted'})

    def make_request(self, op):
        def token(kind, **fields):
            return sign({'kind': kind, 'id': kind + '-001', 'audience': 'experimental-gate',
                         'not_before': NOW - 100, 'expires': NOW + 100, **fields}, self.secrets['authority'], 'authority')
        c = token('credential', subject='synthetic-agent', public_key=self.publics['agent'])
        d = token('delegation', subject='synthetic-agent', delegator='synthetic-owner',
                  action=op['action'], target=op['target'])
        a = token('approval', subject='synthetic-agent', approver='synthetic-approver',
                  delegation_digest=digest(d), operation_digest=digest(op))
        request = {'intent': copy.deepcopy(op), 'credential': c, 'delegation': d, 'approval': a}
        return self.proof(request)

    def proof(self, request):
        request['proof'] = sign({'kind': 'request', 'operation_digest': digest(request['intent']),
            **{n + '_digest': digest(request[n]) for n in ('credential', 'delegation', 'approval')}},
            self.secrets['agent'], 'agent')
        return request

    def retoken(self, request, name, **fields):
        request[name] = sign({**request[name]['body'], **fields}, self.secrets['authority'], 'authority')
        return self.proof(request)

    def revoke(self, ids, *, valid_until=NOW + 100):
        save(self.root / 'authority' / 'revocations.json', sign({'kind': 'revocations',
             'issued_at': NOW - 1, 'valid_until': valid_until, 'revoked': ids}, self.secrets['authority'], 'authority'))

    def start(self, role):
        path = self.root / role / 'config.json'
        save(path, self.configs[role])
        path.chmod(0o600)
        proc = subprocess.Popen([sys.executable, '-m', 'record_gate', 'service', '--config', str(path)],
                                cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.processes[role] = proc
        with selectors.DefaultSelector() as selector:
            selector.register(proc.stdout, selectors.EVENT_READ)
            if not selector.select(10):
                raise RuntimeError(role + '_startup_timeout')
            line = proc.stdout.readline()
        if not line:
            raise RuntimeError(role + '_startup_failed: ' + proc.stderr.read())
        url = json.loads(line)['url']
        self.gate[role + '_url'] = url
        return url

    def stop(self, role, *, kill=False):
        proc = self.processes.pop(role, None)
        if proc:
            if proc.poll() is None:
                proc.kill() if kill else proc.terminate()
            proc.wait(timeout=10)
            proc.stdout.close()
            proc.stderr.close()

    def restart(self, role, *, kill=False):
        self.stop(role, kill=kill)
        self.start(role)

    def execute(self, **kwargs):
        return execute(self.gate, self.request, **kwargs)

    def crash_worker(self, fault):
        path = self.root / 'gate' / 'config.json'
        save(path, self.gate)
        path.chmod(0o600)
        completed = subprocess.run([sys.executable, '-m', 'record_gate', 'worker', '--config', str(path),
            '--request', str(self.root / 'agent' / 'request.json'), '--fault', fault],
            cwd=ROOT, capture_output=True, text=True, timeout=15)
        return completed.returncode

    def counts(self):
        with closing(sqlite3.connect(self.configs['backend']['database'])) as db:
            return {'backend_requests': db.execute('SELECT count(*) FROM attempts').fetchone()[0],
                    'effects': db.execute('SELECT count(*) FROM effects').fetchone()[0]}

    def state(self):
        with closing(sqlite3.connect(self.configs['audit']['database'])) as db:
            row = db.execute('SELECT state FROM operations WHERE id=?', (self.op['operation_id'],)).fetchone()
            return row[0] if row else 'absent'

    def events(self):
        envelope = rpc(self.gate['audit_url'], '/export', control(self.gate, 'export'))
        return check(envelope, self.publics['audit'], 'audit_export', 'audit')['events']

    def evidence(self, *, final):
        return export_package(self.events(), self.op, self.scope, {
            'audit_public': self.publics['audit'], 'backend_public': self.publics['backend'],
            'exporter_secret': self.secrets['exporter'], 'exporter_public': self.publics['exporter'],
            'authority_public': self.publics['authority'], 'scope_receipt': self.scope_receipt}, final=final)

    def close(self):
        for role in list(self.processes):
            self.stop(role)
        self.tmp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
