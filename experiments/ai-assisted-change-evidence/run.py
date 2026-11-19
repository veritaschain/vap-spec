"""Run synthetic cases or recheck preserved bytes; no external deployment."""
import argparse
import hashlib
import json
from pathlib import Path

from change_evidence import (KIND, SCHEMA, admit, assess, canonical, decode, digest,
                             observe, operation, require, seal, sign, text_hash)
from record_gate.bridge import prepare_scope, synthetic_scope_receipt
from record_gate.gate import execute, reconcile
from record_gate.harness import Harness, NOW
from record_gate.suite import verify_bundle

ROOT = Path(__file__).resolve().parent


def as_text(value):
    return canonical(value).decode('utf-8') + '\n'


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Fixture:
    def __init__(self, harness, case):
        self.h = harness
        self.policy = {'id': 'synthetic-change-policy/1', 'required_cases': ['smoke', 'rollback-check'],
                       'required_conditions': ['peer-review'], 'max_test_age': 60,
                       'exception_policy': 'reject_all'}
        self.artifacts = {
            'finding.json': as_text({'kind': 'synthetic-finding', 'reference': 'urn:example:change-001',
                                    'note': 'No actual CVE or exploitable software is used.'}),
            'patch.txt': 'synthetic configuration version: 2\n',
            'baseline.json': as_text({'version': 1}),
            'environment.json': as_text({'target': 'mock/service-a', 'runtime': 'synthetic-v1'}),
            'plan.json': as_text({'kind': 'synthetic-test-plan', 'cases': self.policy['required_cases']}),
        }
        self.artifacts['test-run.json'] = as_text({
            'kind': 'synthetic-test-result', 'finished_at': NOW - 10,
            **{k: text_hash(self.artifacts[n]) for k, n in [
                ('patch_sha256', 'patch.txt'), ('baseline_sha256', 'baseline.json'),
                ('environment_sha256', 'environment.json'), ('plan_sha256', 'plan.json')]},
            'case_results': {'smoke': 'passed', 'rollback-check': 'passed'}})
        self.artifacts['conditions.json'] = as_text({
            'patch_sha256': text_hash(self.artifacts['patch.txt']), 'target': 'mock/service-a',
            'conditions': {'peer-review': {'state': 'met', 'evidence_reference': 'synthetic-checklist-001'}}})
        self.context = {'target': 'mock/service-a', 'now': NOW,
                        'baseline_sha256': text_hash(self.artifacts['baseline.json']),
                        'environment_sha256': text_hash(self.artifacts['environment.json'])}
        self.body = {'kind': KIND, 'schema': SCHEMA, 'change_id': 'synthetic-' + case,
                     'operation_id': 'change-' + case, 'target': 'mock/service-a',
                     'policy_digest': digest(self.policy), 'exception': None}
        self.reseal()

    def reseal(self):
        self.manifest = seal(self.body, self.artifacts, self.h.secrets['authority'])
        self.request = self.h.make_request(operation(self.manifest))
        self.h.op, self.h.request = operation(self.manifest), self.request
        self.h.scope = prepare_scope(self.h.op, self.h.secrets['exporter'])
        self.h.scope_receipt = synthetic_scope_receipt(self.h.scope, self.h.secrets['exporter'])

    def alter(self, name, callback):
        value = decode(self.artifacts[name])
        callback(value)
        self.artifacts[name] = as_text(value)
        self.reseal()

    def args(self):
        return {'config': self.h.gate, 'request': self.request, 'manifest': self.manifest,
                'artifacts': self.artifacts, 'policy': self.policy, 'context': self.context,
                'trusted_key': self.h.publics['authority']}


def run_case(case):
    options = {'drop_after_commit': True} if case == 'lost-response' else None
    with Harness(backend_options=options) as h:
        f = Fixture(h, case)
        if case == 'tampered-patch':
            f.artifacts['patch.txt'] = 'unsigned replacement\n'
        elif case == 'signed-untested-patch':
            f.artifacts['patch.txt'] = 'signed but untested replacement\n'
            f.reseal()
        elif case in ('signed-failed-test', 'bypass-companion'):
            f.alter('test-run.json', lambda r: r['case_results'].update(smoke='failed'))
        elif case == 'missing-test':
            f.alter('test-run.json', lambda r: r['case_results'].pop('rollback-check'))
        elif case == 'stale-test':
            f.alter('test-run.json', lambda r: r.update(finished_at=NOW - 61))
        elif case == 'wrong-environment':
            f.context['environment_sha256'] = text_hash('a different runtime')
        elif case == 'unmet-condition':
            f.alter('conditions.json', lambda r: r['conditions']['peer-review'].update(state='pending'))
        elif case == 'unsupported-exception':
            f.body['exception'] = {'requested': 'skip-review'}
            f.reseal()
        elif case == 'expired-approval':
            h.retoken(f.request, 'approval', expires=NOW)
        elif case == 'revoked-approval':
            h.revoke(['approval-001'])
        elif case == 'wrong-approved-manifest':
            f.request = h.make_request({**operation(f.manifest), 'args': {'text': 'different artifact'}})
        elif case == 'audit-unavailable':
            h.stop('audit')
        before = assess(**f.args())
        report = admit(**f.args())
        if case == 'bypass-companion':
            # Negative control: the unchanged lower-level gate does not know
            # this policy. A trusted controller with its credentials can bypass
            # the companion. No non-bypassable enforcement claim is made.
            report['gate_result'] = execute(h.gate, f.request)
            report['mock_execution'] = report['gate_result']['state'].upper()
            report['bypass'] = 'DIRECT_LOWER_LEVEL_GATE'
        observations = {'health': None, 'rollback': None}
        if case == 'rollback-unknown':
            observations['health'] = sign({'kind': 'change_observation', 'manifest_digest': digest(f.manifest),
                'stage': 'health', 'outcome': 'unhealthy', 'evidence_text': 'Synthetic negative health observation.'},
                h.secrets['backend'], 'change-observer')
        for stage, field in [('health', 'post_change_health'), ('rollback', 'rollback_evidence')]:
            report[field] = observe(f.manifest, observations[stage], h.publics['backend'], stage)
        gate_evidence = None
        if report['mock_execution'] in ('CONFIRMED_SUCCESS', 'RESULT_UNKNOWN'):
            gate_evidence = h.evidence(final=report['mock_execution'] == 'CONFIRMED_SUCCESS')
        recovered_evidence = None
        if case == 'lost-response':
            report['reconciliation'] = reconcile(h.gate, h.op)
            recovered_evidence = h.evidence(final=True)
        if case == 'duplicate-request':
            report['repeat_gate_result'] = admit(**f.args())['gate_result']
        counts = h.counts()
        return {'case': case, 'before': before, 'report': report, 'harness_counts': counts,
                'manifest': f.manifest, 'artifacts': f.artifacts, 'request': f.request,
                'policy': f.policy, 'context': f.context, 'observations': observations,
                'public_context': {'authority_public': h.publics['authority'], 'evidence_public': h.publics['authority'],
                                   'observer_public': h.publics['backend'], 'evaluation_time': NOW,
                                   'revocations': decode(Path(h.gate['revocations']).read_bytes())},
                'gate_evidence': gate_evidence, 'recovered_evidence': recovered_evidence}


def expectations():
    rows = decode((ROOT / 'acceptance.json').read_bytes())
    require(isinstance(rows, list) and bool(rows), 'empty_acceptance_inventory')
    require(all(isinstance(r, dict) and set(r) == {'case', 'expected', 'effects', 'evidence_bundles'}
                and isinstance(r['case'], str) and isinstance(r['expected'], dict) and r['expected']
                for r in rows), 'acceptance_shape')
    require(len({r['case'] for r in rows}) == len(rows), 'duplicate_acceptance_case')
    return rows


def verify_case(artifact, expected):
    public = artifact['public_context']
    replay = assess({'authority_public': public['authority_public'], 'evaluation_time': public['evaluation_time']},
                    artifact['request'], artifact['manifest'], artifact['artifacts'], artifact['policy'],
                    artifact['context'], public['evidence_public'], status_envelope=public['revocations'])
    require(replay == artifact['before'], 'offline_assessment_mismatch')
    report = artifact['report']
    for key in ('record_integrity', 'authorization_binding', 'test_evidence', 'approval_conditions', 'admission'):
        require(report[key] == replay[key], 'reported_assessment_mismatch')
    for stage, field in [('health', 'post_change_health'), ('rollback', 'rollback_evidence')]:
        require(report[field] == observe(artifact['manifest'], artifact['observations'][stage],
                                        public['observer_public'], stage), 'observation_report_mismatch')
    require((artifact['gate_evidence'] is not None) == (expected['evidence_bundles'] >= 1)
            and (artifact['recovered_evidence'] is not None) == (expected['evidence_bundles'] == 2),
            'gate_evidence_inventory')
    count = 0
    for field in ('gate_evidence', 'recovered_evidence'):
        bundle = artifact[field]
        if bundle is None:
            continue
        verify_bundle(bundle)
        adapter = bundle['adapter_trust']
        require(adapter['operation'] == operation(artifact['manifest'])
                and adapter['authority_public'] == public['authority_public'], 'gate_change_binding')
        requests = [event['signed']['body']['payload'] for event in bundle['package']['events']
                    if event['signed']['body']['event_type'] == 'request']
        require(len(requests) == 1, 'gate_request_inventory')
        require(digest(requests[0]['signed_request']) == digest(artifact['request']), 'gate_request_binding')
        recorded = requests[0]['authorization']
        require(recorded['checked_at'] == public['evaluation_time']
                and digest(recorded['revocation_snapshot']) == digest(public['revocations']),
                'gate_authorization_snapshot_binding')
        count += 1
        if field == 'gate_evidence':
            receipt_seen = bundle['native_receipt_check'] == 'verified'
            require((report['mock_execution'] == 'CONFIRMED_SUCCESS') == receipt_seen, 'execution_receipt_mismatch')
        else:
            require(bundle['native_receipt_check'] == 'verified'
                    and report['reconciliation']['state'] == 'confirmed_success', 'recovery_receipt_mismatch')
    require(count == expected['evidence_bundles'], 'gate_evidence_inventory')
    counts = artifact['harness_counts']
    require(isinstance(counts, dict) and set(counts) == {'effects', 'backend_requests'}
            and all(type(value) is int for value in counts.values())
            and counts == {'effects': expected['effects'], 'backend_requests': expected['effects']},
            'harness_effect_expectation')
    require(report['external_anchor'] == 'NOT_ESTABLISHED', 'external_anchor_not_established')
    require(all(report.get(k) == v for k, v in expected['expected'].items()), 'scenario_expectation_mismatch')


def run_suite(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for expected in expectations():
        artifact = run_case(expected['case'])
        verify_case(artifact, expected)
        path = output / (expected['case'] + '.json')
        save(path, artifact)
        rows.append({'case': expected['case'], 'sha256': file_hash(path)})
    summary = {'format': SCHEMA, 'cases': rows, 'scenario_expectations_matched': len(rows),
               'scope': 'Synthetic declared-policy and loopback mock-write exercise only; no patch application.',
               'trust': 'All keys, status snapshots and clocks controlled by the same harness operator.'}
    save(output / 'summary.json', summary)
    print(json.dumps({'cases': len(rows), 'summary_sha256': file_hash(output / 'summary.json')}, sort_keys=True))


def verify_exports(output, expected_summary_sha256):
    output = Path(output)
    require(file_hash(output / 'summary.json') == expected_summary_sha256, 'summary_pin_mismatch')
    summary = decode((output / 'summary.json').read_bytes())
    expected = {r['case']: r for r in expectations()}
    rows = summary.get('cases')
    require(summary.get('format') == SCHEMA and isinstance(rows, list)
            and len(rows) == len(expected) and summary.get('scenario_expectations_matched') == len(expected),
            'incomplete_case_inventory')
    ids = [r.get('case') for r in rows if isinstance(r, dict)]
    require(len(ids) == len(expected) and len(set(ids)) == len(ids) and set(ids) == set(expected),
            'invalid_case_inventory')
    for row in rows:
        path = output / (row['case'] + '.json')
        require(file_hash(path) == row['sha256'], 'case_pin_mismatch')
        artifact = decode(path.read_bytes())
        require(artifact['case'] == row['case'], 'case_identity_mismatch')
        verify_case(artifact, expected[row['case']])
    print(json.dumps({'offline_cases_checked': len(rows), 'mock_trust_only': True}, sort_keys=True))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['run-suite', 'verify-exports'])
    p.add_argument('--output', required=True)
    p.add_argument('--expected-summary-sha256')
    args = p.parse_args()
    if args.command == 'run-suite':
        run_suite(args.output)
    else:
        if args.expected_summary_sha256 is None:
            p.error('--expected-summary-sha256 is required')
        verify_exports(args.output, args.expected_summary_sha256)


if __name__ == '__main__':
    main()
