"""Execute fault scenarios, compare independent expectations and export public evidence."""
import copy
import importlib.metadata
import platform
import shutil
import signal
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from scope_verifier.crypto import digest, strict_json
from .common import rpc, save
from .gate import execute, reconcile
from .harness import Harness, NOW, ROOT


def auth_failures(h):
    rows = []
    for name in ('credential', 'delegation', 'approval'):
        for fault in ('forged', 'expired', 'revoked'):
            req = copy.deepcopy(h.request)
            h.revoke([])
            if fault == 'forged':
                sig = req[name]['signature']
                req[name]['signature'] = ('01' if sig[:2] != '01' else '02') + sig[2:]
                h.proof(req)
                expected = 'invalid_' + name + '_signature_or_shape'
            elif fault == 'expired':
                h.retoken(req, name, expires=NOW)
                expected = name + '_expired_or_not_yet_valid'
            else:
                h.revoke([req[name]['body']['id']])
                expected = name + '_revoked'
            result = execute(h.gate, req)
            rows.append({'input': name + '_' + fault, 'expected_reason': expected, 'actual': result,
                         'matched': result['state'] == 'denied' and result['reason'] == expected})
    h.revoke([])
    for name, fields, reason in [
        ('credential', {'audience': 'different-service'}, 'credential_audience'),
        ('delegation', {'target': 'different-target'}, 'delegation_scope'),
        ('delegation', {'subject': 'another-agent'}, 'delegation_subject'),
        ('approval', {'operation_digest': '0' * 64}, 'approval_scope'),
    ]:
        req = h.retoken(copy.deepcopy(h.request), name, **fields)
        result = execute(h.gate, req)
        rows.append({'input': name + '_out_of_scope_' + next(iter(fields)), 'expected_reason': reason,
                     'actual': result, 'matched': result['state'] == 'denied' and result['reason'] == reason})
    h.revoke([], valid_until=NOW)
    result = h.execute()
    rows.append({'input': 'stale_revocation_snapshot', 'expected_reason': 'revocation_status_stale',
                 'actual': result, 'matched': result['reason'] == 'revocation_status_stale'})
    return rows


def compact(h, result, *, final=False):
    bundle = h.evidence(final=final)
    reports = bundle['reports']
    axes = {'integrity': reports['experimental-scope']['integrity']['result'],
            'scope': reports['experimental-scope']['scope_fulfillment']['result'],
            'core_scope': reports['vap-v1.2']['scope_fulfillment'],
            'core_status': reports['vap-v1.2']['proposal_status']}
    return {**h.counts(), 'state': result['state'], 'stored_state': h.state(), **axes}, bundle


def scenario(number):
    opts = {}
    if number == '04':
        opts['backend_options'] = {'drop_after_commit': True}
    if number in ('10', '13'):
        opts['audit_options'] = {'fail_action': 'outcome' if number == '10' else 'claim'}
    if number == '12':
        opts['backend_options'] = {'insecure': True}
    if number == '15':
        opts['audit_options'] = {'drop_ack': 'prepare'}
    with Harness(**opts) as h:
        details, bundle = {}, None
        if number == '01':
            result = h.execute()
            actual, bundle = compact(h, result, final=True)
            details['replay'] = h.execute()
            actual['requests_after_replay'] = h.counts()['backend_requests']
        elif number == '02':
            h.stop('audit')
            result = h.execute()
            actual = {**h.counts(), 'state': result['state']}
        elif number in ('03', '09'):
            code = h.crash_worker('crash-after-prepare' if number == '03' else 'crash-after-claim')
            h.restart('audit', kill=True)  # Exercise SQLite recovery after abrupt process termination.
            result = reconcile(h.gate, h.op)
            actual, bundle = compact(h, result)
            actual['worker_killed'] = code == -signal.SIGKILL
            if number == '09':
                details['retry'] = h.execute()
                actual['requests_after_retry'] = h.counts()['backend_requests']
        elif number == '04':
            result = h.execute()
            actual, bundle = compact(h, result)
            details['retry'] = h.execute()
            actual['requests_after_retry'] = h.counts()['backend_requests']
            details['recovery'] = reconcile(h.gate, h.op)
            actual['recovered_state'] = details['recovery']['state']
            actual['requests_after_recovery'] = h.counts()['backend_requests']
            details['recovered_evidence'] = h.evidence(final=True)
        elif number == '05':
            candidate = copy.deepcopy(h.op)
            candidate['args']['text'] = 'different synthetic content'
            result = h.execute(candidate=candidate)
            actual, bundle = compact(h, result)
            actual['reason'] = result['reason']
        elif number == '06':
            details['denials'] = auth_failures(h)
            result = {'state': 'denied'}
            actual = {**h.counts(), 'state': 'denied', 'all_reasons_match': all(r['matched'] for r in details['denials']),
                      'denials': len(details['denials'])}
        elif number in ('07', '12'):
            try:
                rpc(h.gate['backend_url'], '/write', {'intent': h.op, 'agent_id': 'trusted', 'human_approved': True})
                accepted = True
            except Exception:
                accepted = False
            result = {'state': 'bypass_accepted' if accepted else 'bypass_rejected'}
            actual = {**h.counts(), **result, 'guarantee_established_for_keyless_mock_call': not accepted}
        elif number == '08':
            result = h.execute()
            before = h.events()
            shutil.rmtree(h.root / 'agent')
            actual, bundle = compact(h, result, final=True)
            actual['audit_unchanged'] = digest(before) == digest(h.events())
            actual['agent_directory_absent'] = not (h.root / 'agent').exists()
        elif number == '10':
            result = h.execute()
            actual, bundle = compact(h, result)
            actual['unknown_outcome_persisted'] = result['unknown_outcome_persisted']
            h.configs['audit'].pop('fail_action')
            h.restart('audit')
            details['recovery'] = reconcile(h.gate, h.op)
            actual['recovered_state'] = details['recovery']['state']
            actual['requests_after_recovery'] = h.counts()['backend_requests']
        elif number == '11':
            with ThreadPoolExecutor(max_workers=4) as pool:
                details['workers'] = list(pool.map(lambda _: h.execute(), range(4)))
            result = reconcile(h.gate, h.op)
            actual, bundle = compact(h, result, final=True)
        elif number == '13':
            result = h.execute()
            actual, bundle = compact(h, result)
        elif number == '14':
            details['original'] = h.execute()
            other = copy.deepcopy(h.op)
            other['args']['text'] = 'conflicting intent'
            result = execute(h.gate, h.make_request(other))
            actual = {**h.counts(), 'state': result['state'], 'stored_state': h.state()}
        elif number == '15':
            result = h.execute()
            actual, bundle = compact(h, result)
        else:
            raise ValueError(number)
        return actual, {'result': result, 'details': details, 'evidence': bundle}


def provenance():
    def git(*args):
        p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True)
        return p.stdout.strip() if p.returncode == 0 else 'unavailable'
    files = sorted(ROOT.glob('record_gate/*.py')) + sorted(ROOT.glob('tests/*.py'))
    files += [ROOT / 'acceptance.json', ROOT / 'requirements.txt']
    verifier = ROOT.parent / 'declared-scope-verifier'
    return {'implementation_commit': git('rev-parse', 'HEAD'),
            'working_tree_dirty': bool(git('status', '--porcelain', '--', str(ROOT))),
            'source_digest': digest({str(p.relative_to(ROOT)): p.read_text() for p in files}),
            'verifier_source_digest': digest({p.name: p.read_text() for p in sorted((verifier / 'scope_verifier').glob('*.py'))}),
            'python': platform.python_version(), 'platform': platform.platform(),
            'dependencies': {n: importlib.metadata.version(n) for n in ('cryptography', 'rfc8785', 'cffi', 'pycparser')}}


def run_suite(output):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for expected in strict_json(ROOT / 'acceptance.json'):
        number = expected['case']
        try:
            actual, artifacts = scenario(number)
            differences = {k: {'expected': v, 'actual': actual.get(k)}
                           for k, v in expected['expected'].items() if actual.get(k) != v}
            save(output / (number + '.json'), artifacts)
            artifact_digest = digest(artifacts)
        except Exception as exc:
            actual, differences, artifact_digest = {}, {'execution_error': str(exc)}, None
        row = {'case': number, 'description': expected['description'], 'expected': expected['expected'],
               'actual': actual, 'differences': differences, 'artifact_digest': artifact_digest}
        rows.append(row)
        print(number, 'MATCH' if not differences else 'MISMATCH', actual, differences, flush=True)
    latency = latency_samples()
    save(output / 'latency.json', latency)
    report = {'latency_digest': digest(latency), 'provenance': provenance(), 'proposal_status': 'experimental_unadopted',
        'current_v1_2_modified': False, 'independent_reproduction': 'not_established',
        'production_readiness': 'not_assessed', 'external_time_attestation': 'simulated_not_independent',
        'os_or_network_isolation': 'not_established_same_uid_loopback_processes',
        'test_execution': 'internal_synthetic_only', 'matching_cases': sum(not r['differences'] for r in rows),
        'cases_executed': len(rows), 'cases': rows}
    save(output / 'summary.json', report)
    return all(not r['differences'] for r in rows)


def latency_samples():
    import statistics
    samples = []
    with Harness() as h:
        for i in range(10):
            op = {**h.op, 'operation_id': 'latency-' + str(i)}
            result = execute(h.gate, h.make_request(op))
            if result['state'] != 'confirmed_success':
                raise RuntimeError('latency_operation_not_confirmed')
            samples.append({k: result[k] for k in ('before_send_ms', 'total_ms')})
    return {'sample_count': len(samples), 'samples': samples,
            'before_send_median_ms': statistics.median(s['before_send_ms'] for s in samples),
            'total_median_ms': statistics.median(s['total_ms'] for s in samples),
            'measurement': 'Gate-entry to first backend send includes authorization and two durable audit round trips; excludes service startup.',
            'limitations': 'Single host, loopback, 10 sequential synthetic operations; no SLA, network or production benchmark.'}


def verify_exports(output):
    """Offline cryptographic recheck of exported evidence, not re-execution of the gate."""
    from .bridge import validate_events
    from .common import require
    from scope_verifier.verifier import verify
    output = Path(output)
    summary = strict_json(output / 'summary.json')
    checked = 0
    for row in summary['cases']:
        artifact = strict_json(output / (row['case'] + '.json'))
        require(digest(artifact) == row['artifact_digest'], 'artifact_digest_mismatch')
        bundles = [artifact['evidence'], artifact['details'].get('recovered_evidence')]
        for bundle in filter(None, bundles):
            p, trust, adapter = bundle['package'], bundle['trust'], bundle['adapter_trust']
            require(trust['keys']['audit']['public_key'] == adapter['audit_public'], 'adapter_trust_mismatch')
            result_seen = validate_events([e['signed'] for e in p['events']], adapter['operation'],
                                         adapter['audit_public'], adapter['backend_public'], adapter['authority_public'])
            require(bundle['native_receipt_check'] == ('verified' if result_seen else 'unavailable'), 'native_check_mismatch')
            for mode in ('vap-v1.2', 'experimental-scope'):
                report = verify(p, trust, mode, bundle['evaluation_time'], allow_synthetic=True)
                require(digest(report) == digest(bundle['reports'][mode]), 'verifier_report_mismatch')
            checked += 1
    require(digest(strict_json(output / 'latency.json')) == summary['latency_digest'], 'latency_digest_mismatch')
    print('Offline recheck:', checked, 'evidence bundles; mock trust only; no gate execution or independent reproduction claim.')
    return True
