"""Unadopted controller-evidence experiment, not a VAP verifier or safety gate.

Signatures authenticate post-capture bytes under an explicitly supplied test key.
They do not authenticate a compromised controller, pre-seal completeness or UTC.
The deliberately narrow canonical encoding here is NOT RFC 8785 / VAP wire format.
"""
from __future__ import annotations
import hashlib
import json
import math
from typing import Any
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

FORMAT = 'vso-control-state-experiment/1'
DOMAIN = b'VSO experimental controller evidence v1\x00'
CASES = [f'{n:02}' for n in range(1, 17)]
ARTIFACTS = ('summary.json', 'runtime.json', 'environment.json', 'cleanup.json', 'evidence.json')


def canonical(value: Any) -> bytes:
    def check(v):
        if v is None or type(v) in (str, bool, int):
            return
        if isinstance(v, list):
            for child in v:
                check(child)
            return
        if isinstance(v, dict) and all(type(k) is str for k in v):
            for child in v.values():
                check(child)
            return
        raise ValueError('unsupported canonical value (floats are not accepted)')
    check(value)
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('ascii')


def read_json(text: str) -> Any:
    def pairs(items):
        obj = {}
        for key, value in items:
            if key in obj:
                raise ValueError('duplicate JSON key')
            obj[key] = value
        return obj
    def invalid_constant(_):
        raise ValueError('invalid JSON constant')
    def finite_float(token):
        value = float(token)
        if not math.isfinite(value):
            raise ValueError('non-finite JSON number')
        return value
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid_constant,
                      parse_float=finite_float)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def artifact(text: str) -> dict:
    return {'text': text, 'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest()}


def probe_result_record(role: str, arguments, result: Any) -> dict:
    """Commit a reserialized parsed probe result without changing numeric values.

    The inner JSON may contain finite measured timings. It is opaque text to the
    restricted outer canonicalizer, not original wire bytes or RFC 8785 encoding.
    No timing is dropped, rounded to an integer, or used as trusted UTC.
    """
    text = json.dumps(result, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
    details = {'role': role, 'arguments': list(arguments), 'result_json': artifact(text)}
    validate_probe_result(details)
    return details


def validate_probe_result(details: dict) -> Any:
    if (not isinstance(details, dict) or set(details) != {'role', 'arguments', 'result_json'} or
            type(details['role']) is not str or not details['role'] or
            not isinstance(details['arguments'], list) or
            any(type(arg) is not str for arg in details['arguments'])):
        raise ValueError('invalid probe-result metadata')
    entry = details['result_json']
    if (not isinstance(entry, dict) or set(entry) != {'text', 'sha256'} or
            type(entry['text']) is not str or artifact(entry['text']) != entry):
        raise ValueError('probe-result bytes mismatch')
    decoded = read_json(entry['text'])
    if details['role'] == 'gate' and details['arguments'] == ['export']:
        if not isinstance(decoded, list) or any(not isinstance(event, dict) for event in decoded):
            raise ValueError('audit export must be an array of event objects')
    elif not isinstance(decoded, dict):
        raise ValueError('probe-result JSON must be an object')
    return decoded


def seal(payload: dict, key: Ed25519PrivateKey) -> dict:
    # The signer is not taken from attacker-controlled bundle metadata.
    body = {'format': FORMAT, 'payload': payload}
    return {**body, 'signature': key.sign(DOMAIN + canonical(body)).hex()}


def preflight(observation: dict, *, run_id: str, config_digest: str,
              now_ns: int, max_age_ns: int, required_paths: list[str]) -> dict:
    """Evaluate one declared window under a trusted single monotonic clock.

    This function is NOT wired into execution and cannot prevent an action. An actual
    admission controller must enforce its decision and bind it atomically to use.
    """
    def result(status, reason):
        return {'control_status': status, 'reason': reason, 'runtime_enforcement': 'not_implemented'}
    if (not isinstance(required_paths, list) or not required_paths or
            any(type(p) is not str or not p for p in required_paths) or
            len(set(required_paths)) != len(required_paths)):
        return result('NOT_ESTABLISHED', 'invalid_path_scope')
    if (type(now_ns) is not int or type(max_age_ns) is not int or now_ns < 0 or max_age_ns < 0 or
            not isinstance(observation, dict) or type(observation.get('measured_ns')) is not int):
        return result('NOT_ESTABLISHED', 'missing_or_invalid_clock')
    if observation.get('run_id') != run_id or not run_id:
        return result('NOT_ESTABLISHED', 'run_mismatch')
    if observation.get('config_digest') != config_digest or not config_digest:
        return result('NOT_ESTABLISHED', 'configuration_changed')
    age = now_ns - observation['measured_ns']
    if age < 0 or age > max_age_ns:
        return result('NOT_ESTABLISHED', 'stale_or_future_observation')
    paths = observation.get('paths')
    if not isinstance(paths, dict):
        return result('NOT_ESTABLISHED', 'missing_observations')
    if any(isinstance(paths.get(p), dict) and paths[p].get('reachable') is True for p in required_paths):
        return result('VIOLATED', 'reachable_path')
    if any(not isinstance(paths.get(p), dict) or paths[p].get('reachable') is not False or
           paths[p].get('target_healthy') is not True for p in required_paths):
        return result('NOT_ESTABLISHED', 'missing_unknown_or_unhealthy_path')
    return result('MET_FOR_DECLARED_PATHS', 'healthy_targets_unreachable_in_observation_window')


def verify(envelope: dict, trusted_public_key: bytes, expected_run_id: str) -> dict:
    """Verify all supplied bytes, then return independent semantic judgments.

    Expected run ID and trusted key must come from outside the untrusted envelope.
    An exported test public key is only a reproducibility aid, not a trust service.
    """
    unknown = {'integrity': 'INVALID', 'case_inventory': 'NOT_ESTABLISHED',
               'isolation': 'NOT_ESTABLISHED', 'action': 'NOT_ESTABLISHED',
               'external_anchor': 'NOT_ESTABLISHED', 'overall_safety': 'NOT_ASSESSED'}
    try:
        if set(envelope) != {'format', 'payload', 'signature'} or envelope['format'] != FORMAT:
            raise ValueError('unsupported envelope')
        payload = envelope['payload']
        if not expected_run_id or payload['run_id'] != expected_run_id:
            raise ValueError('unexpected run')
        Ed25519PublicKey.from_public_bytes(trusted_public_key).verify(
            bytes.fromhex(envelope['signature']),
            DOMAIN + canonical({'format': FORMAT, 'payload': payload}))
        records = payload['artifacts']
        if set(records) != set(ARTIFACTS):
            raise ValueError('artifact inventory mismatch')
        decoded = {}
        for name in ARTIFACTS:
            entry = records[name]
            if set(entry) != {'text', 'sha256'} or artifact(entry['text']) != entry:
                raise ValueError('artifact bytes mismatch')
            decoded[name] = read_json(entry['text'])
        events = payload['observations']
        if not isinstance(events, list) or not events:
            raise ValueError('missing controller observations')
        previous = -1
        for seq, event in enumerate(events, 1):
            if (event['seq'] != seq or type(event['seq']) is not int or
                    event['run_id'] != expected_run_id or type(event['monotonic_ns']) is not int or
                    event['monotonic_ns'] < previous):
                raise ValueError('observation binding or ordering mismatch')
            previous = event['monotonic_ns']
            if event.get('kind') == 'probe-result':
                validate_probe_result(event['details'])
        if any(not isinstance(value, dict) for value in decoded.values()):
            raise ValueError('artifact JSON must be an object')
        rows = decoded['summary.json'].get('cases', [])
        if not isinstance(rows, list) or any(not isinstance(row, dict) or
                not isinstance(row.get('observed', {}), dict) for row in rows):
            raise ValueError('malformed case observations')
        for row in rows:
            if type(row.get('case')) is not str:
                raise ValueError('case identifier must be a string')
            observed = row.get('observed', {})
            if any(not isinstance(observed.get(field, {}), dict)
                   for field in ('attempt', 'backend_counts')):
                raise ValueError('malformed observed network result')
        if type(decoded['cleanup.json'].get('returncode')) is not int:
            raise ValueError('cleanup returncode must be an integer')
        if payload['source_commit_before'] != payload['source_commit_after']:
            raise ValueError('source changed during capture')
        if payload['source_digest_before'] != payload['source_digest_after']:
            raise ValueError('observer code changed during capture')
    except (InvalidSignature, ValueError, TypeError, KeyError, AttributeError) as exc:
        return {**unknown, 'error': type(exc).__name__ + ': ' + str(exc)}
    # Valid signatures do not turn incomplete or negative test observations into safety.
    summary = decoded['summary.json']
    rows = summary.get('cases', [])
    inventory = [row.get('case') for row in rows if isinstance(row, dict)]
    complete = (inventory == CASES and summary.get('execution_complete') is True and
                summary.get('execution_error') is None and decoded['cleanup.json'].get('returncode') == 0)
    by_case = {row.get('case'): row.get('observed', {}) for row in rows if isinstance(row, dict)}
    neg = by_case.get('15', {})
    bypass = (neg.get('attempt', {}).get('connected') is True and
              neg.get('attempt', {}).get('http_status') == 200 and
              type(neg.get('backend_counts', {}).get('effects')) is int and
              neg['backend_counts']['effects'] > 0)
    return {**unknown, 'integrity': 'VERIFIED',
            'case_inventory': 'COMPLETE_RECORDED_INVENTORY' if complete else 'NOT_ESTABLISHED',
            'isolation': 'VIOLATED_IN_NEGATIVE_CONTROL' if bypass else 'NOT_ESTABLISHED',
            'action': 'BYPASS_EFFECT_OBSERVED' if bypass else 'NOT_ESTABLISHED',
            'observation_count': len(events),
            'unmeasured_paths': ['arbitrary_ipv6', 'dns_tunnels', 'general_proxy_egress', 'host_services'],
            'trust_boundary': 'trusted_controller_and_export_time_test_key'}
