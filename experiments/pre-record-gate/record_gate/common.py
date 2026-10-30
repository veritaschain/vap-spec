"""Strict JSON, domain-separated signatures and loopback-only transport."""
import json
import re
import sqlite3
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlparse
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from . import DOMAIN
from scope_verifier.crypto import canonical, digest, hex_bytes, signing_bytes, strict_json


class Rejected(ValueError):
    pass


def require(condition, reason):
    if not condition:
        raise Rejected(reason)


def decode(raw):
    require(len(raw) <= 1024 * 1024, 'input_too_large')
    def pairs(items):
        out = {}
        for key, value in items:
            require(key not in out, 'duplicate_json_key')
            out[key] = value
        return out
    value = json.loads(raw, object_pairs_hook=pairs)
    canonical(value)  # Reject NaN, unsafe integers and unsupported JCS values.
    return value


def save(path, value):
    Path(path).write_text(json.dumps(value, sort_keys=True, indent=2) + '\n', encoding='utf-8')


def key(secret):
    return Ed25519PrivateKey.from_private_bytes(hex_bytes(secret))


def public(secret):
    return key(secret).public_key().public_bytes_raw().hex()


def sign(body, secret, key_id, research=False):
    env = {'algorithm': 'Ed25519', 'key_id': key_id, 'body': body}
    data = signing_bytes(env) if research else DOMAIN + canonical(env)
    env['signature'] = key(secret).sign(data).hex()
    return env


def check(env, public_key, kind, key_id, research=False):
    try:
        require(set(env) == {'algorithm', 'key_id', 'body', 'signature'}, 'envelope_fields')
        require(env['algorithm'] == 'Ed25519' and env['key_id'] == key_id, 'key_or_algorithm')
        require(env['body']['kind'] == kind, 'object_kind')
        unsigned = {k: v for k, v in env.items() if k != 'signature'}
        data = signing_bytes(env) if research else DOMAIN + canonical(unsigned)
        Ed25519PublicKey.from_public_bytes(hex_bytes(public_key)).verify(hex_bytes(env['signature'], 64), data)
        return env['body']
    except Exception as exc:
        raise Rejected('invalid_' + kind + '_signature_or_shape') from exc


def intent(value):
    require(isinstance(value, dict) and set(value) == {'operation_id', 'action', 'target', 'args'}, 'intent_fields')
    require(isinstance(value['operation_id'], str) and re.fullmatch(r'[a-z0-9-]{1,80}', value['operation_id']), 'operation_id')
    require(value['action'] == 'create_record' and value['target'] == 'sandbox/records', 'unsupported_operation')
    require(isinstance(value['args'], dict) and set(value['args']) == {'text'}, 'argument_fields')
    require(isinstance(value['args']['text'], str) and 0 < len(value['args']['text']) <= 256, 'argument_text')
    return decode(canonical(value))


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        raise Rejected('redirect_forbidden')


def rpc(url, path, value):
    parsed = urlparse(url)
    require(parsed.scheme == 'http' and parsed.hostname == '127.0.0.1' and parsed.port is not None
            and not parsed.username and not parsed.password and parsed.path in ('', '/')
            and not parsed.query and not parsed.fragment, 'non_loopback_endpoint')
    req = Request(url.rstrip('/') + path, data=canonical(value), headers={'Content-Type': 'application/json'}, method='POST')
    # Never inherit an external proxy or redirect to a real service.
    try:
        with build_opener(ProxyHandler({}), NoRedirect()).open(req, timeout=2) as response:
            return decode(response.read(1024 * 1024 + 1))
    except HTTPError as exc:
        exc.close()
        raise Rejected('remote_service_rejected_request') from None


def database(path):
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    db.execute('PRAGMA journal_mode=WAL')
    db.execute('PRAGMA synchronous=FULL')
    db.execute('PRAGMA fullfsync=ON')
    require(db.execute('PRAGMA synchronous').fetchone()[0] == 2, 'durability_configuration')
    require(db.execute('PRAGMA journal_mode').fetchone()[0] == 'wal', 'journal_configuration')
    return db
