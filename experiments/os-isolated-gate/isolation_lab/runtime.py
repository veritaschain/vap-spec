"""Container-only HTTP adapter around the unchanged PR #11 services and gate."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from record_gate import gate
from record_gate.common import canonical, decode, require
from record_gate.services import Service
from scope_verifier.crypto import strict_json
from .transport import service_rpc


def serve(role):
    config = strict_json('/run/role/config.json')
    service = None if role == 'gate' else Service(config)
    # Dependency injection is confined to this new process; no prior source is edited.
    gate.rpc = service_rpc
    allowed = {'gate': {'/execute'}, 'audit': {'/prepare', '/claim', '/get', '/outcome', '/export'},
               'backend': {'/write', '/lookup'}, 'open-backend': {'/write', '/lookup'}}[role]
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def respond(self, status, value):
            data = canonical(value)
            self.send_response(status)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self):
            self.respond(200 if self.path == '/health' else 404, {'role': role, 'ready': self.path == '/health'})

        def do_POST(self):
            if self.path not in allowed:
                self.respond(404, {'error': 'path_not_allowed'})
                return
            try:
                self.connection.settimeout(3)
                length = int(self.headers.get('Content-Length', '-1'))
                require(0 <= length <= 1024 * 1024, 'invalid_length')
                request = decode(self.rfile.read(length))
                if role == 'gate':
                    result = gate.execute(config, request)
                else:
                    result = getattr(service, config['role'])(self.path, request)
                self.respond(200, result)
            except Exception as exc:
                self.respond(403, {'error': type(exc).__name__})
    server = ThreadingHTTPServer(('0.0.0.0', 8080), Handler)
    print('{"ready":true}', flush=True)
    server.serve_forever()
