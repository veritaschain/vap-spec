#!/usr/bin/env python3
"""Third-party run orchestration only; no protocol or cryptographic implementation."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parent
KIT_FILES = ['README.md', 'RUN-ja.md', 'EXPECTED-RESULTS.md', 'REPORTING.md', 'source-lock.json',
             'expected-results.json', 'reproduce.py', 'check_artifacts.py',
             'templates/evaluator-report.json', 'tests/test_package.py']


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate_json_key: ' + key)
            result[key] = value
        return result
    def invalid(value):
        raise ValueError('nonfinite_json: ' + value)
    return json.loads(Path(path).read_text(), object_pairs_hook=pairs, parse_constant=invalid)


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def equal(actual, expected):
    # JSON booleans and integers are distinct, unlike Python equality.
    return json.dumps(actual, sort_keys=True, allow_nan=False) == json.dumps(expected, sort_keys=True, allow_nan=False)


def environment():
    env = {k: v for k, v in os.environ.items() if k not in ('PYTHONPATH', 'PYTHONHOME', 'COMPOSE_PROFILES', 'COMPOSE_FILE')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def command(args, cwd, timeout=60):
    result = subprocess.run(args, cwd=cwd, env=environment(), text=True, capture_output=True, timeout=timeout)
    require(result.returncode == 0, 'command_failed: ' + ' '.join(args[:4]) + '\n' + result.stderr[-2000:])
    return result.stdout.strip()


def verify_source(source, lock=None):
    source = Path(source).resolve()
    lock = lock or read_json(ROOT / 'source-lock.json')
    commit = command(['git', 'rev-parse', 'HEAD'], source)
    require(commit == lock['commit'], 'wrong_source_commit: expected ' + lock['commit'])
    require(not command(['git', 'status', '--porcelain', '--untracked-files=all'], source), 'source_checkout_not_clean')
    ignored = command(['git', 'ls-files', '--others', '--ignored', '--exclude-standard', '--',
                       *lock['protected_source_prefixes'], '.env'], source)
    require(not ignored, 'ignored_files_in_execution_inputs: use a fresh source checkout')
    for name, expected in lock['files'].items():
        path = source / name
        require(path.is_file() and not path.is_symlink(), 'missing_or_symlink_source: ' + name)
        require(sha(path) == expected, 'source_hash_mismatch: ' + name)
    return {'commit': commit, 'files_checked': len(lock['files']), 'source_lock_sha256': sha(ROOT / 'source-lock.json')}


def preflight(source):
    lock = read_json(ROOT / 'source-lock.json')
    result = {'source': verify_source(source, lock), 'python': platform.python_version(),
              'host_system': platform.system(), 'host_kernel': platform.release(), 'machine': platform.machine()}
    require(platform.system() == 'Linux', 'native_linux_controller_required_for_this_package')
    require(sys.version_info >= (3, 12), 'python_3_12_or_newer_required')
    dependencies = {name: importlib.metadata.version(name) for name in lock['dependencies']}
    require(dependencies == lock['dependencies'], 'dependency_versions_do_not_match_source_lock')
    result['dependencies'] = dependencies
    # Query separately so no host names, registry credentials or full daemon configuration are collected.
    result['docker'] = {name: json.loads(command(['docker', 'info', '--format', '{{json .' + field + '}}'], source))
                        for name, field in [('os', 'OSType'), ('version', 'ServerVersion'),
                                            ('kernel', 'KernelVersion'), ('security', 'SecurityOptions')]}
    require(result['docker']['os'] == 'linux', 'linux_docker_engine_required')
    options = ' '.join(result['docker']['security'] or [])
    require('rootless' not in options and 'userns' not in options, 'rootless_or_remapped_daemon_is_outside_reference_setup')
    result['compose'] = command(['docker', 'compose', 'version', '--short'], source)
    reference = lock['reference_environment']
    result['reference_version_matches'] = {'python': result['python'] == reference['controller_python'],
        'docker': result['docker']['version'] == reference['docker'], 'compose': result['compose'] == reference['compose'],
        'kernel': result['docker']['kernel'] == reference['kernel']}
    return result


def compare_lab(summary, expectations):
    differences = []
    rows = summary.get('cases', [])
    ids = [r.get('case') for r in rows]
    expected_ids = [r['case'] for r in expectations['cases']]
    if len(ids) != len(expected_ids) or len(set(ids)) != len(ids) or set(ids) != set(expected_ids):
        return ['case_inventory_missing_duplicate_or_unexpected']
    if (summary.get('execution_complete') is not True or summary.get('all_expectations_matched') is not True
            or summary.get('execution_error') is not None or not equal(summary.get('cases_executed'), 16)
            or not equal(summary.get('matching_cases'), 16)):
        differences.append('incomplete_or_nonmatching_lab_summary')
    if summary.get('proposal_status') != 'experimental_unadopted' or summary.get('production_ready') is not False:
        differences.append('experimental_boundary_changed')
    if summary.get('independent_reproduction') != 'not_established':
        differences.append('unsupported_automatic_independence_claim')
    by_id = {r['case']: r for r in rows}
    for expected in expectations['cases']:
        row = by_id[expected['case']]
        if row.get('matched') is not True:
            differences.append(expected['case'] + ': reported non-match')
        for check in expected['equals']:
            try:
                value = row['observed']
                for part in check['path']:
                    value = value[part]
                valid = equal(value, check['value'])
            except (KeyError, TypeError, IndexError, ValueError):
                valid = False
            if not valid:
                differences.append(expected['case'] + ': ' + '/'.join(check['path']))
    return differences


def unit_log_matches(text, expected_tests):
    """unittest's Ran count includes skips and expected failures: require plain OK."""
    counts = re.findall(r'^Ran (\d+) tests? in ', text, re.MULTILINE)
    conclusions = re.findall(r'^(?:OK(?:[ \t].*)?|FAILED(?:[ \t].*)?)$', text, re.MULTILINE)
    return counts == [str(expected_tests)] and conclusions == ['OK']


def step(name, args, cwd, output, expected_tests=None):
    try:
        r = subprocess.run(args, cwd=cwd, env=environment(), capture_output=True, text=True, timeout=600)
        text = r.stdout + '\n' + r.stderr
        result = {'step': name, 'returncode': r.returncode, 'completed': True}
    except subprocess.TimeoutExpired as exc:
        def decoded(value): return value.decode(errors='replace') if isinstance(value, bytes) else value or ''
        text = decoded(exc.stdout) + '\n' + decoded(exc.stderr)
        result = {'step': name, 'returncode': None, 'completed': False, 'error': 'timeout'}
    (output / 'logs' / (name + '.log')).write_text(text)
    result['log_sha256'] = sha(output / 'logs' / (name + '.log'))
    if expected_tests is not None:
        counts = re.findall(r'^Ran (\d+) tests? in ', text, re.MULTILINE)
        result['tests_executed'] = int(counts[-1]) if len(counts) == 1 else None
        result['expected_tests'] = expected_tests
    result['ok'] = result['completed'] and result['returncode'] == 0 and (expected_tests is None or unit_log_matches(text, expected_tests))
    print(name + ': ' + ('OK' if result['ok'] else 'INCOMPLETE OR MISMATCH'), flush=True)
    return result


def inventory(output):
    files = sorted(Path(output).rglob('*'))
    require(not any(p.is_symlink() for p in files), 'symlink_in_artifacts')
    return {str(p.relative_to(output)): sha(p) for p in files
            if p.is_file() and p != output / 'SHA256SUMS.json'}


def kit_digests():
    return {name: sha(ROOT / name) for name in KIT_FILES}


def run(source, output):
    source, output = Path(source).resolve(), Path(output).absolute()
    require(not output.resolve().is_relative_to(source), 'output_must_be_outside_frozen_source')
    output.mkdir(parents=True, exist_ok=False)
    (output / 'logs').mkdir()
    report = {'format': 'vap-reproduction-run/1', 'started_at': datetime.now(timezone.utc).isoformat(),
              'status': 'incomplete', 'proposal_status': 'experimental_unadopted', 'overall_vap_pass': None,
              'independence': 'not_assessed', 'independent_reproduction': 'not_established', 'steps': [], 'kit_files_sha256': kit_digests()}
    try:
        report['preflight'] = preflight(source)
        save(output / 'preflight.json', report['preflight'])
        expectations = read_json(ROOT / 'expected-results.json')
        jobs = [('lab-unit', 'os-isolated-gate'), ('gate-unit', 'pre-record-gate'), ('verifier-unit', 'declared-scope-verifier')]
        for name, folder in jobs:
            result = step(name, [sys.executable, '-W', 'error::ResourceWarning', '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                          source / 'experiments' / folder, output, expectations['unit_tests'][name])
            report['steps'].append(result)
            require(result['ok'], 'regression_step_failed: ' + name)
        for name, folder, module in [('lab', 'os-isolated-gate', 'isolation_lab'),
                                     ('gate', 'pre-record-gate', 'record_gate'),
                                     ('verifier', 'declared-scope-verifier', 'scope_verifier')]:
            result = step(name, [sys.executable, '-m', module, 'run-suite', '--output', str(output / name)],
                          source / 'experiments' / folder, output)
            report['steps'].append(result)
            require(result['ok'], 'execution_step_failed: ' + name)
        result = step('artifact-recheck', [sys.executable, str(ROOT / 'check_artifacts.py'), '--source', str(source),
                                          '--run', str(output)], ROOT, output)
        report['steps'].append(result)
        require(result['ok'], 'artifact_recheck_failed')
        report['postflight_source'] = verify_source(source)
        require(kit_digests() == report['kit_files_sha256'], 'package_changed_during_execution')
        report['status'] = 'matched'
    except Exception as exc:
        report['error'] = type(exc).__name__ + ': ' + str(exc)
        print('Package incomplete: ' + report['error'], flush=True)
    finally:
        report['finished_at'] = datetime.now(timezone.utc).isoformat()
        save(output / 'run-report.json', report)
        save(output / 'SHA256SUMS.json', inventory(output))
    return report['status'] == 'matched'


def check_run(source, output):
    frozen = verify_source(source)
    output = Path(output).resolve()
    hashes = read_json(output / 'SHA256SUMS.json')
    require(equal(hashes, inventory(output)), 'artifact_inventory_or_hash_mismatch')
    report = read_json(output / 'run-report.json')
    require(report['status'] == 'matched' and report['independence'] == 'not_assessed'
            and report['proposal_status'] == 'experimental_unadopted' and report['overall_vap_pass'] is None
            and report['independent_reproduction'] == 'not_established',
            'run_not_complete_or_boundary_changed')
    require(report['kit_files_sha256'] == kit_digests(), 'wrong_package_revision_for_recheck')
    expected_names = ['lab-unit', 'gate-unit', 'verifier-unit', 'lab', 'gate', 'verifier', 'artifact-recheck']
    require([r['step'] for r in report['steps']] == expected_names, 'step_inventory_mismatch')
    require(equal(report['preflight'], read_json(output / 'preflight.json')), 'preflight_report_mismatch')
    require(equal(report['postflight_source'], frozen), 'postflight_source_mismatch')
    expected_tests = read_json(ROOT / 'expected-results.json')['unit_tests']
    for result in report['steps']:
        require(result['ok'] is True and result['completed'] is True and equal(result['returncode'], 0), 'unsuccessful_step')
        log = output / 'logs' / (result['step'] + '.log')
        require(sha(log) == result['log_sha256'], 'step_log_mismatch')
        if result['step'] in expected_tests:
            count = expected_tests[result['step']]
            require(re.findall(r'^Ran (\d+) tests? in ', log.read_text(), re.MULTILINE) == [str(count)], 'unit_test_count_missing_or_wrong')
            require(unit_log_matches(log.read_text(), count), 'unit_tests_not_all_passed')
            require(equal(result['tests_executed'], count) and equal(result['expected_tests'], count), 'unit_test_count_report_mismatch')
    print(command([sys.executable, str(ROOT / 'check_artifacts.py'), '--source', str(Path(source).resolve()),
                   '--run', str(output)], ROOT, timeout=180))
    print('Saved artifacts rechecked; this is not OS re-execution or an independence attestation.')


def pack(output):
    output = Path(output)
    hashes = kit_digests()
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED) as archive:
        for name in KIT_FILES:
            info = zipfile.ZipInfo('vap-os-isolation-kit/' + name, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, (ROOT / name).read_bytes())
        sums = ''.join(value + '  ' + name + '\n' for name, value in sorted(hashes.items()))
        archive.writestr(zipfile.ZipInfo('vap-os-isolation-kit/SHA256SUMS', date_time=(1980, 1, 1, 0, 0, 0)), sums)
    print('Created ' + str(output) + ' sha256=' + sha(output))


def main():
    parser = argparse.ArgumentParser(description='Unadopted research reproduction package; never certifies independence')
    sub = parser.add_subparsers(dest='command', required=True)
    for name in ('verify-source', 'preflight', 'run', 'check'):
        p = sub.add_parser(name); p.add_argument('--source', required=True)
        if name in ('run', 'check'): p.add_argument('--output', required=True)
    p = sub.add_parser('pack'); p.add_argument('--output', required=True)
    args = parser.parse_args()
    try:
        if args.command == 'verify-source': print(json.dumps(verify_source(args.source), indent=2))
        elif args.command == 'preflight': print(json.dumps(preflight(args.source), indent=2))
        elif args.command == 'run': return 0 if run(args.source, args.output) else 1
        elif args.command == 'check': check_run(args.source, args.output)
        else: pack(args.output)
        return 0
    except Exception as exc:
        print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
