#!/usr/bin/env python3
"""Recheck saved observations using the frozen implementations; no new verifier."""
import argparse
from pathlib import Path
import re
import sys

from reproduce import ROOT, compare_lab, equal, read_json, require, verify_source


def validate_environment_record(record, lock):
    require(equal(record['dependencies'], lock['dependencies']), 'recorded_dependencies_do_not_match_lock')
    version = record['python']
    require(isinstance(version, str) and re.fullmatch(r'\d+\.\d+\.\d+', version) is not None,
            'invalid_recorded_python_version')
    require(tuple(map(int, version.split('.'))) >= (3, 12), 'unsupported_recorded_python_version')
    reference = lock['reference_environment']
    matches = {'python': version == reference['controller_python'],
               'docker': record['docker']['version'] == reference['docker'],
               'compose': record['compose'] == reference['compose'],
               'kernel': record['docker']['kernel'] == reference['kernel']}
    require(equal(record['reference_version_matches'], matches), 'recorded_reference_comparison_mismatch')


def validate_runtime_record(value, preflight):
    require(equal(value['python'], preflight['python']), 'recorded_python_changed')
    require(equal(value['dependencies'], preflight['dependencies']), 'recorded_dependencies_changed')


def check(source, output):
    source, output = Path(source).resolve(), Path(output).resolve()
    frozen = verify_source(source)
    expectations = read_json(ROOT / 'expected-results.json')
    preflight = read_json(output / 'preflight.json')
    validate_environment_record(preflight, read_json(ROOT / 'source-lock.json'))
    sys.path.insert(0, str(source / 'experiments/os-isolated-gate'))
    from isolation_lab import ROLES
    from isolation_lab.checks import filesystem_permissions_match, runtime_mounts_match
    from record_gate.suite import verify_bundle, verify_exports
    from scope_verifier.crypto import digest, strict_json
    from scope_verifier.fixtures import EVALUATION_TIME
    from scope_verifier.verifier import verify

    def same(actual, expected, message):
        require(equal(actual, expected), message)

    def provenance(value, fixtures=False):
        validate_runtime_record(value, preflight)
        same(value['implementation_commit'], frozen['commit'], 'wrong_implementation_commit')
        require(value['working_tree_dirty'] is False, 'dirty_implementation')
        if fixtures:
            same(value['fixture_commit'], frozen['commit'], 'wrong_fixture_commit')
            same(value['independent_reproduction'], 'not_established', 'independence_not_automatically_established')

    lab = strict_json(output / 'lab/summary.json')
    require(not compare_lab(lab, expectations), 'lab_observation_mismatch: ' + str(compare_lab(lab, expectations)))
    same(lab['provenance']['commit'], frozen['commit'], 'wrong_lab_commit')
    require(lab['provenance']['dirty'] is False, 'dirty_lab_source')
    same(lab['provenance']['controller_python'], preflight['python'], 'lab_controller_python_changed')
    same(lab['provenance']['input_digests'], expectations['lab_input_digests'], 'lab_input_digest_mismatch')
    same(lab['provenance']['os_execution_location'], 'Linux Docker engine', 'os_execution_missing')
    rows = {r['case']: r['observed'] for r in lab['cases']}
    same(sorted(rows['01']), sorted(ROLES), 'identity_inventory')
    for namespace in ('mnt', 'pid', 'net'):
        values = [r['namespaces'][namespace] for r in rows['01'].values()]
        require(all(isinstance(v, str) and v for v in values) and len(set(values)) == len(ROLES), 'namespace_isolation_missing')
    require(filesystem_permissions_match(rows['02']), 'filesystem_permissions_mismatch')
    same(rows['03']['filesystem'], rows['02'], 'filesystem_observations_disagree')
    for observation in rows['02'].values():
        for field in ('config_write', 'code_write'):
            require(type(observation[field]['errno']) is int and observation[field]['errno'] in (13, 30), 'write_denial_not_permission_or_readonly')
    runtime = strict_json(output / 'lab/runtime.json')
    same(runtime, rows['03']['runtime'], 'runtime_observations_disagree')
    same(runtime, rows['04']['runtime'], 'network_observations_disagree')
    same(sorted(runtime), sorted(ROLES), 'runtime_role_inventory')
    volume = next(m['name'] for m in runtime['agent']['mounts'] if m['destination'] == '/run/role')
    require(re.fullmatch(r'vap-isolation-[0-9a-f]{10}_agent-config', volume) is not None, 'unexpected_project_volume_name')
    project = volume.removesuffix('_agent-config')
    networks = {'agent': ['frontend'], 'gate': ['frontend', 'audit', 'backend'],
                'audit': ['audit'], 'backend': ['backend'], 'open-backend': ['backend']}
    for role in ROLES:
        require(runtime_mounts_match(role, runtime[role], project), 'runtime_mount_mismatch: ' + role)
        same(sorted(runtime[role]['networks']), sorted(project + '_' + n for n in networks[role]), 'network_membership_mismatch')
        same(runtime[role]['port_bindings'], {}, 'unexpected_published_port')
    bundle = strict_json(output / 'lab/evidence.json')
    verify_bundle(bundle)  # Actual signatures, hashes, bindings and both modes from unchanged code.
    same(digest(bundle), rows['11']['evidence_digest'], 'lab_evidence_digest_mismatch')
    same(digest([e['signed'] for e in bundle['package']['events']]), rows['11']['audit_digest'], 'lab_audit_digest_mismatch')
    for mode in ('vap-v1.2', 'experimental-scope'):
        same(bundle['reports'][mode]['integrity']['result'], 'verified', 'normal_lab_evidence_integrity')
    require(bundle['reports']['vap-v1.2']['scope_fulfillment'] is None, 'scope_leaked_into_current_mode')
    same(bundle['reports']['experimental-scope']['scope_fulfillment']['result'], 'met', 'normal_lab_scope_not_met')
    cleanup = strict_json(output / 'lab/cleanup.json')
    for field in ('returncode', 'image_removal_returncode', 'image_listing_returncode'):
        same(cleanup[field], 0, 'cleanup_incomplete: ' + field)
    require(cleanup['image_absence_confirmed'] is True, 'temporary_image_absence_not_confirmed')
    environment = strict_json(output / 'lab/environment.json')
    same(preflight['source'], frozen, 'preflight_source_mismatch')
    same(preflight['host_system'], 'Linux', 'non_linux_controller')
    same(environment['docker']['Os'], 'linux', 'non_linux_engine')
    same(environment['docker']['Version'], preflight['docker']['version'], 'docker_version_changed')
    same(environment['kernel'], preflight['docker']['kernel'], 'docker_kernel_changed')
    same(environment['compose'], preflight['compose'], 'compose_version_changed')

    verify_exports(output / 'gate')
    gate = strict_json(output / 'gate/summary.json')
    provenance(gate['provenance'])
    same(gate['proposal_status'], 'experimental_unadopted', 'gate_status_changed')
    require(gate['current_v1_2_modified'] is False, 'current_version_changed')
    same(gate['independent_reproduction'], 'not_established', 'gate_independence_claim')
    same(gate['cases_executed'], expectations['gate_cases'], 'gate_case_count')
    gate_expected = strict_json(source / 'experiments/pre-record-gate/acceptance.json')
    same(sum(r['evidence_bundles'] for r in gate_expected), expectations['gate_bundles'], 'gate_bundle_count')

    verifier = output / 'verifier'
    summary = strict_json(verifier / 'summary.json')
    provenance(summary['provenance'], fixtures=True)
    same(summary['proposal_status'], 'experimental_unadopted', 'verifier_status_changed')
    require(summary['overall_vap_pass'] is None, 'unsupported_overall_pass')
    same(summary['cases_executed'], expectations['verifier_cases'], 'verifier_case_count')
    same(summary['matching_cases'], expectations['verifier_cases'], 'verifier_matching_count')
    same(summary['mismatching_cases'], [], 'verifier_mismatches')
    same(summary['evaluation_time'], EVALUATION_TIME, 'evaluation_time_mismatch')
    acceptance = strict_json(source / 'experiments/declared-scope-verifier/acceptance.json')
    manifest = strict_json(verifier / 'fixtures/manifest.json')
    same(digest(manifest), summary['fixture_manifest_digest'], 'fixture_manifest_digest')
    expected_ids = sorted(r['case'] for r in acceptance)
    for collection in (manifest, summary['cases']):
        same(sorted(r['case'] for r in collection), expected_ids, 'verifier_case_inventory')
    manifest = {r['case']: r for r in manifest}
    summary_rows = {r['case']: r for r in summary['cases']}
    for expected in acceptance:
        case = expected['case']
        package = strict_json(verifier / 'fixtures' / (case + '.evidence.json'))
        trust = strict_json(verifier / 'fixtures' / (case + '.trust.json'))
        same(manifest[case]['evaluation_time'], EVALUATION_TIME, 'fixture_time')
        for name, value in [('evidence_digest', digest(package)), ('trust_digest', digest(trust))]:
            same(manifest[case][name], value, 'fixture_digest: ' + case)
            same(summary_rows[case][name], value, 'summary_fixture_digest: ' + case)
        results = {}
        for mode, suffix in [('vap-v1.2', 'v1.2'), ('experimental-scope', 'experimental')]:
            actual = verify(package, trust, mode, EVALUATION_TIME, allow_synthetic=True)
            saved = strict_json(verifier / (case + '.' + suffix + '.report.json'))
            provenance(saved.pop('provenance'), fixtures=True)
            same(saved, actual, 'recomputed_report_mismatch: ' + case + '/' + mode)
            results[mode] = actual
        core, experimental = results['vap-v1.2'], results['experimental-scope']
        require(core['scope_fulfillment'] is None and core['proposal_status'] == 'not_applied', 'mode_isolation_changed')
        requirements = {c['check']: c['result'] for c in experimental['v1_2_requirements']}
        same({c['check']: c['result'] for c in core['v1_2_requirements']}, requirements, 'mode_requirement_isolation_changed')
        actual = {'core_integrity': core['integrity']['result'], 'integrity': experimental['integrity']['result'],
                  'scope': experimental['scope_fulfillment']['result'], 'INT-008': requirements['INT-008']}
        for key, value in actual.items():
            same(value, expected[key], 'verifier_acceptance: ' + case + '/' + key)
        reasons = sorted({r['code'] for r in experimental['scope_fulfillment']['violations'] + experimental['scope_fulfillment']['unresolved']})
        require(not expected['reason'] or expected['reason'] in reasons, 'verifier_reason_mismatch')
        for key, value in expected.get('requirements', {}).items():
            same(requirements[key], value, 'verifier_requirement_mismatch')
        for key, value in [('actual', actual), ('requirements', requirements), ('reasons', reasons), ('expected', expected), ('differences', {})]:
            same(summary_rows[case][key], value, 'verifier_summary_mismatch: ' + case + '/' + key)
    print('Rechecked: 16 OS cases, 15 gate cases / 11 bundles, 14 verifier cases in both modes. Experimental, unadopted; independence not assessed.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source', required=True)
    parser.add_argument('--run', required=True)
    args = parser.parse_args()
    try:
        check(args.source, args.run)
    except Exception as exc:
        print(type(exc).__name__ + ': ' + str(exc), file=sys.stderr)
        sys.exit(1)
