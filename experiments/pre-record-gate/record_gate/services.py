"""Separate audit and simulated API processes with separate SQLite stores/keys.

Same-UID processes are NOT an OS security boundary. Keys are separated by role,
not protected from a hostile host administrator. All endpoints are loopback-only.
"""
import json
from contextlib import closing
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from scope_verifier.crypto import canonical, digest
from .common import check, database, decode, intent, require, sign


class Service:
    def __init__(self, config):
        self.c = config
        with closing(database(config['database'])) as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS operations (id TEXT PRIMARY KEY, digest TEXT NOT NULL,
                    request TEXT NOT NULL, state TEXT NOT NULL, receipt TEXT);
                CREATE TABLE IF NOT EXISTS events (seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE, envelope TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS effects (id TEXT PRIMARY KEY, digest TEXT NOT NULL, receipt TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS attempts (seq INTEGER PRIMARY KEY);
            ''')

    def signed(self, body):
        return sign(body, self.c['secret'], self.c['role'])

    def event(self, db, op, suffix, payload):
        event_id = op['operation_id'] + ':' + suffix
        body = {'kind': 'event', 'evaluation_id': self.c['evaluation_id'], 'policy_digest': self.c['policy_digest'],
                'event_id': event_id, 'source_id': 'gate-audit', 'event_type': suffix,
                'payload': {'operation_digest': digest(op), **payload}}
        env = sign(body, self.c['secret'], 'audit', research=True)
        db.execute('INSERT INTO events(event_id,envelope) VALUES(?,?)', (event_id, canonical(env).decode()))

    def control(self, envelope, action):
        body = check(envelope, self.c['gate_public'], 'control', 'gate')
        require(body['action'] == action, 'control_action')
        return body

    def audit(self, path, envelope):
        action = path.removeprefix('/')
        body = self.control(envelope, action)
        # Trusted harness fault, never a request parameter.
        require(self.c.get('fail_action') != action, 'injected_storage_unavailable')
        db = database(self.c['database'])
        try:
            if action == 'export':
                events = [json.loads(row[0]) for row in db.execute('SELECT envelope FROM events ORDER BY seq')]
                return self.signed({'kind': 'audit_export', 'events': events})
            op = intent(body['intent'])
            oid, od = op['operation_id'], digest(op)
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT digest,request,state,receipt FROM operations WHERE id=?', (oid,)).fetchone()
            if row:
                require(row[0] == od, 'operation_id_intent_conflict')
            if action == 'prepare' and row is None:
                request = body['request']
                require(digest(request['intent']) == od, 'record_intent_mismatch')
                self.event(db, op, 'request', {'intent': op, 'authorization': body['authorization'], 'signed_request': request})
                db.execute('INSERT INTO operations VALUES(?,?,?,?,NULL)', (oid, od, canonical(request).decode(), 'prepared'))
                row = (od, canonical(request).decode(), 'prepared', None)
            require(row is not None, 'no_pre_record')
            if action == 'prepare':
                require(digest(json.loads(row[1])) == digest(body['request']), 'operation_id_authorization_conflict')
            state, receipt = row[2], json.loads(row[3]) if row[3] else None
            claimed = False
            if action == 'claim' and state == 'prepared':
                self.event(db, op, 'dispatch', {'intent': op, 'meaning': 'durable intent to dispatch; not proof of sending'})
                state, claimed = 'dispatch_intent', True
                db.execute('UPDATE operations SET state=? WHERE id=?', (state, oid))
            elif action == 'outcome':
                require(state in ('dispatch_intent', 'result_unknown', 'confirmed_success'), 'invalid_outcome_transition')
                if body['state'] == 'confirmed_success':
                    result = check(body['receipt'], self.c['backend_public'], 'backend_receipt', 'backend')
                    require(result['operation_id'] == oid and result['operation_digest'] == od and result['committed'] is True,
                            'backend_receipt_binding')
                    if state != 'confirmed_success':
                        receipt = body['receipt']
                        self.event(db, op, 'result', {'receipt': receipt})
                        state = 'confirmed_success'
                else:
                    require(body['state'] == 'result_unknown', 'unsupported_outcome')
                    if state == 'dispatch_intent':
                        self.event(db, op, 'unknown', {'reason': body['reason']})
                        state = 'result_unknown'
                db.execute('UPDATE operations SET state=?,receipt=? WHERE id=?',
                           (state, canonical(receipt).decode() if receipt else None, oid))
            else:
                require(action in ('prepare', 'claim', 'get'), 'unsupported_audit_action')
            db.commit()  # Only return an acknowledgment/permit AFTER this commit.
            if self.c.get('drop_ack') == action:
                return None
            return self.signed({'kind': 'audit_ack', 'action': action, 'operation_id': oid,
                                'operation_digest': od, 'state': state, 'claimed': claimed, 'receipt': receipt})
        finally:
            if db.in_transaction:
                db.rollback()
            db.close()

    def backend(self, path, envelope):
        action = path.removeprefix('/')
        if action == 'write':
            meter = database(self.c['database'])
            try:
                meter.execute('INSERT INTO attempts DEFAULT VALUES')
            finally:
                meter.close()
        if self.c.get('insecure') and action == 'write':
            body = envelope  # Deliberately broken boundary, negative-control test only.
        else:
            body = self.control(envelope, action)
        op = intent(body['intent'])
        oid, od = op['operation_id'], digest(op)
        if action == 'write' and not self.c.get('insecure'):
            ack = check(body['permit'], self.c['audit_public'], 'audit_ack', 'audit')
            require(ack['action'] == 'claim' and ack['claimed'] is True and ack['state'] == 'dispatch_intent'
                    and ack['operation_id'] == oid and ack['operation_digest'] == od, 'dispatch_permit_binding')
        db = database(self.c['database'])
        try:
            db.execute('BEGIN IMMEDIATE')
            row = db.execute('SELECT digest,receipt FROM effects WHERE id=?', (oid,)).fetchone()
            if row:
                require(row[0] == od, 'operation_id_intent_conflict')
            if action == 'lookup':
                db.commit()
                return self.signed({'kind': 'lookup', 'operation_id': oid, 'operation_digest': od,
                                    'receipt': json.loads(row[1]) if row else None})
            require(action == 'write', 'unsupported_backend_action')
            receipt = json.loads(row[1]) if row else self.signed({
                'kind': 'backend_receipt', 'operation_id': oid, 'operation_digest': od, 'committed': True})
            if not row:
                # ID + exact request digest + effect receipt commit in the same transaction.
                db.execute('INSERT INTO effects VALUES(?,?,?)', (oid, od, canonical(receipt).decode()))
            db.commit()
            if self.c.get('drop_after_commit'):
                return None  # Handler closes connection after a real SQLite commit.
            return receipt
        finally:
            if db.in_transaction:
                db.rollback()
            db.close()


def serve(config):
    service = Service(config)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_POST(self):
            try:
                self.connection.settimeout(2)
                size = int(self.headers.get('Content-Length', '-1'))
                require(0 <= size <= 1024 * 1024, 'invalid_content_length')
                request = decode(self.rfile.read(size))
                result = getattr(service, config['role'])(self.path, request)
                if result is None:
                    self.close_connection = True
                    return
                payload, status = canonical(result), 200
            except Exception as exc:
                # Synthetic service errors; never return secrets or arbitrary exception repr.
                payload, status = canonical({'error': type(exc).__name__}), 403
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
    server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    print(json.dumps({'url': 'http://127.0.0.1:' + str(server.server_port)}), flush=True)
    server.serve_forever()
