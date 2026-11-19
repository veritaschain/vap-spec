"""Declared-policy checks before a digest-bearing mock write; unadopted research."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pre-record-gate'))

from record_gate.auth import authorize
from record_gate.common import canonical, check, decode, require, sign
from record_gate.gate import execute
from scope_verifier.crypto import digest

SCHEMA = 'ai-assisted-change-evidence/0.1'
KIND = 'ai_assisted_change_evidence'
ARTIFACTS = {'finding.json', 'patch.txt', 'baseline.json', 'environment.json',
             'plan.json', 'test-run.json', 'conditions.json'}


def text_hash(text):
    require(isinstance(text, str), 'artifact_not_utf8_text')
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def seal(body, artifacts, secret):
    """Synthetic producer signs original-text digests, not a claim of independent truth."""
    body = {**body, 'artifacts': {name: text_hash(text) for name, text in artifacts.items()}}
    return sign(body, secret, 'change-reviewer')


def operation(manifest):
    body = manifest['body']
    return {'operation_id': body['operation_id'], 'action': 'create_record',
            'target': 'sandbox/records',
            'args': {'text': 'change-evidence-sha256:' + digest(manifest)}}


def inspect_records(manifest, artifacts, trusted_key):
    body = check(manifest, trusted_key, KIND, 'change-reviewer')
    require(set(body) == {'kind', 'schema', 'change_id', 'operation_id', 'target',
                         'policy_digest', 'artifacts', 'exception'}, 'manifest_fields')
    require(body['schema'] == SCHEMA and isinstance(body['change_id'], str)
            and bool(body['change_id']) and isinstance(body['target'], str)
            and bool(body['target']), 'manifest_identity')
    require(set(artifacts) == ARTIFACTS and set(body['artifacts']) == ARTIFACTS, 'artifact_inventory')
    require(all(text_hash(artifacts[name]) == body['artifacts'][name] for name in ARTIFACTS),
            'artifact_digest_mismatch')
    return body


def inspect_tests(body, artifacts, policy, context):
    """Compare signed assertions to a separately supplied policy and target snapshot."""
    require(body['policy_digest'] == digest(policy), 'policy_mismatch')
    require(body['target'] == context['target'], 'target_mismatch')
    hashes = body['artifacts']
    require(hashes['baseline.json'] == context['baseline_sha256'], 'baseline_mismatch')
    require(hashes['environment.json'] == context['environment_sha256'], 'environment_mismatch')
    plan = decode(artifacts['plan.json'])
    required = policy['required_cases']
    require(isinstance(required, list) and bool(required)
            and all(isinstance(x, str) and x for x in required)
            and len(set(required)) == len(required), 'policy_case_inventory')
    require(plan == {'kind': 'synthetic-test-plan', 'cases': required}, 'test_plan_mismatch')
    result = decode(artifacts['test-run.json'])
    require(set(result) == {'kind', 'patch_sha256', 'baseline_sha256', 'environment_sha256',
                            'plan_sha256', 'finished_at', 'case_results'}, 'test_result_fields')
    require(result['kind'] == 'synthetic-test-result', 'test_result_kind')
    for key, name in [('patch_sha256', 'patch.txt'), ('baseline_sha256', 'baseline.json'),
                      ('environment_sha256', 'environment.json'), ('plan_sha256', 'plan.json')]:
        require(result[key] == hashes[name], 'tested_' + key + '_mismatch')
    require(type(context['now']) is int and type(result['finished_at']) is int
            and type(policy['max_test_age']) is int and policy['max_test_age'] >= 0
            and 0 <= context['now'] - result['finished_at'] <= policy['max_test_age'],
            'test_time_stale_or_future')
    require(isinstance(result['case_results'], dict)
            and set(result['case_results']) == set(required), 'test_case_inventory')
    require(all(result['case_results'][name] == 'passed' for name in required), 'test_case_not_passed')


def inspect_conditions(body, artifacts, policy):
    require(policy['exception_policy'] == 'reject_all' and body['exception'] is None,
            'emergency_exception_unsupported')
    conditions = decode(artifacts['conditions.json'])
    require(set(conditions) == {'patch_sha256', 'target', 'conditions'}, 'condition_fields')
    require(conditions['patch_sha256'] == body['artifacts']['patch.txt']
            and conditions['target'] == body['target'], 'condition_subject_mismatch')
    required = policy['required_conditions']
    require(isinstance(required, list) and bool(required)
            and all(isinstance(x, str) and x for x in required)
            and len(set(required)) == len(required), 'policy_condition_inventory')
    require(isinstance(conditions['conditions'], dict)
            and set(conditions['conditions']) == set(required), 'condition_inventory')
    for name in required:
        item = conditions['conditions'][name]
        require(isinstance(item, dict) and set(item) == {'state', 'evidence_reference'}
                and item['state'] == 'met' and isinstance(item['evidence_reference'], str)
                and bool(item['evidence_reference']), 'condition_not_met')


def assess(config, request, manifest, artifacts, policy, context, trusted_key, *, status_envelope=None):
    """No network calls. No overall safety, conformance or real-deployment verdict."""
    report = {'record_integrity': 'NOT_ESTABLISHED', 'authorization_binding': 'NOT_ESTABLISHED',
              'test_evidence': 'NOT_ESTABLISHED', 'approval_conditions': 'NOT_ESTABLISHED',
              'admission': 'DENY', 'mock_execution': 'NOT_ATTEMPTED',
              'post_change_health': 'NOT_ESTABLISHED', 'rollback_evidence': 'NOT_ESTABLISHED',
              'external_anchor': 'NOT_ESTABLISHED', 'reasons': []}
    try:
        body = inspect_records(manifest, artifacts, trusted_key)
        report['record_integrity'] = 'VERIFIED'
    except Exception as exc:
        report['record_integrity'] = 'INVALID'
        report['reasons'].append('records:' + str(exc))
        return report
    try:
        actual, _ = authorize(request, config, status_envelope=status_envelope)
        require(actual == operation(manifest), 'approved_manifest_mismatch')
        require(config['evaluation_time'] == context['now'], 'evaluation_time_mismatch')
        report['authorization_binding'] = 'VERIFIED'
    except Exception as exc:
        report['authorization_binding'] = 'INVALID'
        report['reasons'].append('authorization:' + str(exc))
    for axis, validator, args in [
            ('test_evidence', inspect_tests, (body, artifacts, policy, context)),
            ('approval_conditions', inspect_conditions, (body, artifacts, policy))]:
        try:
            validator(*args)
            report[axis] = 'SATISFIED_DECLARED_POLICY'
        except Exception as exc:
            report[axis] = 'NOT_SATISFIED'
            report['reasons'].append(axis + ':' + str(exc))
    if (report['authorization_binding'] == 'VERIFIED'
            and report['test_evidence'] == report['approval_conditions'] == 'SATISFIED_DECLARED_POLICY'):
        report['admission'] = 'ALLOW_MOCK_WRITE'
    return report


def admit(config, request, manifest, artifacts, policy, context, trusted_key):
    # Freeze the reviewed bytes and exact request before the managed call. The
    # target snapshot is supplied, not an atomic observation of a real deployer.
    snapshot = decode(canonical({'request': request, 'manifest': manifest, 'artifacts': artifacts,
                                  'policy': policy, 'context': context}))
    report = assess(config, **snapshot, trusted_key=trusted_key)
    if report['admission'] == 'ALLOW_MOCK_WRITE':
        outcome = execute(config, snapshot['request'])
        report['mock_execution'] = outcome['state'].upper()
        report['gate_result'] = outcome
    return report


def observe(manifest, envelope, trusted_key, stage):
    """Signed health/rollback statements are attributed assertions, not real effects."""
    if envelope is None:
        return 'NOT_ESTABLISHED'
    try:
        body = check(envelope, trusted_key, 'change_observation', 'change-observer')
        require(set(body) == {'kind', 'manifest_digest', 'stage', 'outcome', 'evidence_text'},
                'observation_fields')
        require(body['manifest_digest'] == digest(manifest) and body['stage'] == stage,
                'observation_binding')
        allowed = {'health': {'healthy', 'unhealthy', 'unknown'},
                   'rollback': {'completed', 'failed', 'unknown'}}
        require(stage in allowed and body['outcome'] in allowed[stage]
                and isinstance(body['evidence_text'], str) and bool(body['evidence_text']),
                'observation_outcome')
        return 'NOT_ESTABLISHED' if body['outcome'] == 'unknown' else 'ATTESTED_' + body['outcome'].upper()
    except Exception:
        return 'INVALID'
