"""Trusted Docker controller. Only this process can manage namespaces/volumes.

Runtime probes run as the configured non-root container users. No privileged exec,
host firewall modifications, external API requests, or host-port probes are used.
"""
import errno
import json
import os
import platform
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from record_gate.bridge import export_package
from record_gate.common import require, save
from scope_verifier.crypto import digest
from . import REPO, ROOT, ROLES, VERSION
from .seed import generate

CASES = {
    '01': 'Distinct non-root users, private namespaces, zero capabilities and no privilege escalation',
    '02': 'Per-role readable config; foreign UID canaries denied by kernel DAC',
    '03': 'Read-only code/config, private role mounts, no engine socket or seed mount',
    '04': 'Only declared internal networks; no published host ports or privileged runtime',
    '05': 'Authorized agent request through gate creates exactly one mock effect',
    '06': 'Agent direct call to backend literal IPv4 cannot connect or reach handler',
    '07': 'Agent direct call to audit literal IPv4 cannot connect',
    '08': 'Agent cannot reach even an unauthenticated mock API on the private backend network',
    '09': 'Gate rejects a caller-selected target and does not proxy arbitrary paths',
    '10': 'CONNECT to gate is not an alternate backend route',
    '11': 'Deleting agent logs leaves signed audit evidence intact and verifiable',
    '12': 'Audit outage blocks a fresh operation before any API request',
    '13': 'Audit restart preserves evidence and known success without another write',
    '14': 'Negative control: added backend route is reachable, API authentication still denies write',
    '15': 'Negative control: added route plus unauthenticated mock API permits bypass; guarantee false',
    '16': 'Removing the extra route restores connection denial',
}


def command(args, *, env=None, timeout=120, check=True):
    result = subprocess.run(args, cwd=REPO, env=env, capture_output=True, text=True, timeout=timeout)
    if check and result.returncode:
        # Commands never put key material into argv; stderr is retained for diagnosis only.
        raise RuntimeError('command_failed: ' + ' '.join(args[:5]) + '\n' + result.stderr[-4000:])
    return result


class Lab:
    def __init__(self, output):
        self.output = output
        self.project = 'vap-isolation-' + uuid.uuid4().hex[:10]
        self.image = self.project + ':local'
        self.tmp = tempfile.TemporaryDirectory(prefix='vap-isolation-seed-')
        self.seed = generate()
        seed_path = Path(self.tmp.name) / 'seed.json'
        save(seed_path, self.seed)
        seed_path.chmod(0o600)
        self.env = {**os.environ, 'LAB_IMAGE': self.image, 'LAB_SEED_DIR': self.tmp.name}
        self.prefix = ['docker', 'compose', '-f', str(ROOT / 'compose.yaml'), '-p', self.project]
        self.ids = {}

    def compose(self, *args, **kwargs):
        return command([*self.prefix, *args], env=self.env, **kwargs)

    def start(self):
        require(shutil.which('docker') is not None, 'docker_unavailable_no_os_test_executed')
        kind = command(['docker', 'info', '--format', '{{.OSType}}']).stdout.strip()
        require(kind == 'linux', 'linux_docker_engine_required')
        built = command(['docker', 'build', '-t', self.image, '-f', str(ROOT / 'Dockerfile'), str(REPO)], timeout=360, check=False)
        (self.output / 'build.log').write_text(built.stdout + built.stderr)
        require(built.returncode == 0, 'image_build_failed_see_build_log')
        self.compose('run', '--rm', '--no-deps', 'setup', timeout=60)
        self.compose('--profile', 'negative-control', 'up', '-d', '--wait', '--wait-timeout', '90', timeout=120)
        self.ids = {role: self.compose('ps', '-q', role).stdout.strip() for role in ROLES}
        require(all(self.ids.values()), 'missing_runtime_container')

    def probe(self, role, *args):
        result = self.compose('exec', '-T', role, 'python', '-m', 'isolation_lab', 'probe', *args, timeout=20)
        return json.loads(result.stdout)

    def inspect(self):
        out = {}
        for role, cid in self.ids.items():
            raw = json.loads(command(['docker', 'inspect', cid]).stdout)[0]
            out[role] = {'user': raw['Config']['User'], 'image_id': raw['Image'],
                         'readonly_rootfs': raw['HostConfig']['ReadonlyRootfs'],
                         'privileged': raw['HostConfig']['Privileged'],
                         'cap_drop': raw['HostConfig']['CapDrop'], 'cap_add': raw['HostConfig']['CapAdd'],
                         'security_opt': raw['HostConfig']['SecurityOpt'],
                         'port_bindings': raw['HostConfig']['PortBindings'],
                         'networks': {name: {'ip': n['IPAddress']} for name, n in raw['NetworkSettings']['Networks'].items()},
                         'mounts': [{'type': m['Type'], 'destination': m['Destination'], 'rw': m['RW'],
                                     'name': m.get('Name')} for m in raw['Mounts']]}
        return out

    def address(self, role, network):
        return self.inspection[role]['networks'][self.project + '_' + network]['ip']

    def counts(self, role='backend'):
        return self.probe(role, 'counts')

    def evidence(self, events):
        seed = self.seed
        return export_package(events, seed['operation'], seed['scope'], {
            'audit_public': seed['publics']['audit'], 'backend_public': seed['publics']['backend'],
            'authority_public': seed['publics']['authority'], 'exporter_public': seed['publics']['exporter'],
            'exporter_secret': seed['exporter_secret'], 'scope_receipt': seed['scope_receipt']}, final=True)

    def close(self):
        try:
            if shutil.which('docker'):
                # Scoped by the randomly generated project; never prune shared Docker resources.
                result = self.compose('--profile', 'negative-control', '--profile', 'setup', 'down', '-v',
                                      '--remove-orphans', timeout=60, check=False)
                removed = command(['docker', 'image', 'rm', self.image], check=False, timeout=30)
                save(self.output / 'cleanup.json', {'returncode': result.returncode,
                     'image_removal_returncode': removed.returncode})
                require(result.returncode == 0, 'container_or_volume_cleanup_incomplete')
                # An absent image is expected when the build failed before creating it.
                remains = command(['docker', 'image', 'inspect', self.image], check=False)
                require(remains.returncode != 0, 'temporary_image_cleanup_incomplete')
        finally:
            self.tmp.cleanup()


def summarize(rows, *, execution_error=None):
    ids = [r['case'] for r in rows]
    complete = len(ids) == len(CASES) and len(set(ids)) == len(ids) and set(ids) == set(CASES)
    matched = sum(r['matched'] is True for r in rows)
    return {'cases_executed': len(rows), 'matching_cases': matched,
            'execution_complete': complete and execution_error is None,
            'all_expectations_matched': complete and matched == len(CASES) and execution_error is None,
            'execution_error': execution_error, 'cases': rows,
            'proposal_status': 'experimental_unadopted', 'production_ready': False,
            'independent_reproduction': 'not_established', 'privileged_host_resistance': 'not_established'}


def run_suite(directory):
    output = Path(directory).resolve()
    output.mkdir(parents=True, exist_ok=True)
    rows, error, lab = [], None, None
    def record(case, details, passed):
        rows.append({'case': case, 'description': CASES[case], 'matched': bool(passed), 'observed': details})
        print(case, 'MATCH' if passed else 'MISMATCH', CASES[case], flush=True)
    try:
        lab = Lab(output)
        lab.start()
        lab.inspection = lab.inspect()
        save(output / 'runtime.json', lab.inspection)
        identities = {r: lab.probe(r, 'identity') for r in ROLES}
        record('01', identities, all(
            p['uid'] == ROLES[r] and p['gid'] == ROLES[r] and 0 not in p['groups']
            and all(int(p['security'][n], 16) == 0 for n in ('CapEff', 'CapPrm', 'CapBnd'))
            and p['security']['NoNewPrivs'] == '1' and p['security']['Seccomp'] == '2'
            and p['setuid_zero']['allowed'] is False and p['setuid_zero']['errno'] == errno.EPERM
            for r, p in identities.items()) and all(
                len({p['namespaces'][n] for p in identities.values()}) == len(ROLES) for n in ('mnt', 'pid', 'net')))
        files = {r: lab.probe(r, 'filesystem', r) for r in ROLES}
        record('02', files, all(p['own_config_readable']['allowed'] and all(
            x['allowed'] if other == r else (x['allowed'] is False and x['errno'] == errno.EACCES)
            for other, x in p['canaries'].items()) for r, p in files.items()))
        mounts = lab.inspection
        record('03', {'filesystem': files, 'runtime': mounts}, all(
            p['config_write']['allowed'] is False and p['code_write']['allowed'] is False
            and p['config_write']['errno'] in (errno.EACCES, errno.EROFS)
            and p['code_write']['errno'] in (errno.EACCES, errno.EROFS)
            and not p['docker_socket_visible'] and not p['setup_seed_visible']
            and mounts[r]['readonly_rootfs'] and not mounts[r]['privileged']
            and len([m for m in mounts[r]['mounts'] if m['destination'] == '/run/role' and not m['rw']
                     and m['name'] == lab.project + '_' + r + '-config']) == 1
            and all(m['destination'] in ('/run/role', '/data', '/canaries', '/tmp') for m in mounts[r]['mounts'])
            for r, p in files.items()))
        networks = {n: json.loads(command(['docker', 'network', 'inspect', lab.project + '_' + n]).stdout)[0]
                    for n in ('frontend', 'audit', 'backend')}
        expected_networks = {'agent': ['frontend'], 'gate': ['frontend', 'audit', 'backend'],
                             'audit': ['audit'], 'backend': ['backend'], 'open-backend': ['backend']}
        record('04', {'internal': {n: v['Internal'] for n, v in networks.items()},
                      'runtime': mounts}, all(v['Internal'] for v in networks.values()) and all(
            set(mounts[r]['networks']) == {lab.project + '_' + n for n in expected_networks[r]}
            and not mounts[r]['port_bindings'] for r in ROLES))
        before = lab.counts()
        valid = lab.probe('agent', 'execute', 'valid')
        after = lab.counts()
        record('05', {'response': valid, 'before': before, 'after': after},
               valid['http_status'] == 200 and valid['result']['state'] == 'confirmed_success'
               and before == {'effects': 0, 'requests': 0} and after == {'effects': 1, 'requests': 1})
        for number, target, net in [('06', 'backend', 'backend'), ('07', 'audit', 'audit'),
                                     ('08', 'open-backend', 'backend')]:
            request_path = '/export' if target == 'audit' else '/write'
            result = lab.probe('agent', 'network', lab.address(target, net), '8080', request_path)
            healthy = lab.probe(target, 'health')
            count = lab.counts('open-backend' if target == 'open-backend' else 'backend')
            expected = {'effects': 0, 'requests': 0} if target == 'open-backend' else after
            record(number, {'attempt': result, 'target_health': healthy, 'backend_counts': count},
                   result['connected'] is False and healthy['ready'] and count == expected)
        bad = lab.probe('agent', 'execute', 'bad-target')
        proxy = lab.probe('agent', 'network', 'gate', '8080', '/proxy')
        record('09', {'bad_target': bad, 'proxy': proxy, 'backend_counts': lab.counts()},
               bad['result']['state'] == 'denied' and proxy['http_status'] == 404 and lab.counts() == after)
        connect = lab.probe('agent', 'network', 'gate', '8080', 'backend:8080', 'CONNECT')
        record('10', {'attempt': connect, 'backend_counts': lab.counts()},
               connect['connected'] and connect['http_status'] == 501 and lab.counts() == after)
        events_before = lab.probe('gate', 'export')
        created = lab.probe('agent', 'local-log', 'create')
        deleted = lab.probe('agent', 'local-log', 'delete')
        events_after = lab.probe('gate', 'export')
        evidence = lab.evidence(events_after)
        save(output / 'evidence.json', evidence)
        record('11', {'created': created, 'deleted': deleted, 'audit_digest': digest(events_after),
                      'evidence_digest': digest(evidence)}, created['exists'] and not deleted['exists']
               and digest(events_before) == digest(events_after)
               and evidence['reports']['experimental-scope']['integrity']['result'] == 'verified'
               and evidence['reports']['experimental-scope']['scope_fulfillment']['result'] == 'met'
               and evidence['reports']['vap-v1.2']['scope_fulfillment'] is None)
        lab.compose('stop', 'audit')
        stopped = lab.probe('agent', 'execute', 'fresh')
        record('12', {'response': stopped, 'backend_counts': lab.counts()},
               stopped['result']['state'] == 'blocked' and lab.counts() == after)
        lab.compose('up', '-d', '--wait', 'audit', timeout=60)
        recovered = lab.probe('agent', 'execute', 'valid')
        record('13', {'response': recovered, 'backend_counts': lab.counts()},
               recovered['result']['state'] == 'confirmed_success' and not recovered['result']['backend_attempted']
               and lab.counts() == after and digest(lab.probe('gate', 'export')) == digest(events_after))
        # Intentional test-only topology weakening, using the trusted controller's Docker authority.
        network = lab.project + '_backend'
        command(['docker', 'network', 'connect', network, lab.ids['agent']])
        exposed = lab.probe('agent', 'network', lab.address('backend', 'backend'), '8080')
        secure_counts = lab.counts()
        record('14', {'attempt': exposed, 'backend_counts': secure_counts,
                      'network_isolation_established': False, 'unauthorized_effect': False},
               exposed['connected'] and exposed['http_status'] == 403 and secure_counts == {'effects': 1, 'requests': 2})
        bypass = lab.probe('agent', 'network', lab.address('open-backend', 'backend'), '8080')
        negative_counts = lab.counts('open-backend')
        record('15', {'attempt': bypass, 'backend_counts': negative_counts,
                      'bypass_guarantee_established': False}, bypass['connected'] and bypass['http_status'] == 200
               and negative_counts == {'effects': 1, 'requests': 1})
        command(['docker', 'network', 'disconnect', network, lab.ids['agent']])
        restored = lab.probe('agent', 'network', lab.address('open-backend', 'backend'), '8080')
        record('16', {'attempt': restored, 'backend_counts': lab.counts('open-backend')},
               restored['connected'] is False and lab.counts('open-backend') == negative_counts
               and lab.probe('open-backend', 'health')['ready'])
        save(output / 'runtime.json', lab.inspection)
        save(output / 'environment.json', {'docker': json.loads(command(['docker', 'version', '--format', '{{json .Server}}']).stdout),
            'compose': command(['docker', 'compose', 'version', '--short']).stdout.strip(),
            'kernel': command(['docker', 'info', '--format', '{{.KernelVersion}}']).stdout.strip()})
    except Exception as exc:
        error = type(exc).__name__ + ': ' + str(exc)
        print('Experiment incomplete:', error, flush=True)
        if lab and shutil.which('docker'):
            try:
                logs = lab.compose('--profile', 'negative-control', 'logs', '--no-color', '--tail', '40', check=False)
                (output / 'failure-services.log').write_text(logs.stdout + logs.stderr)
            except Exception:
                pass  # The original error and incomplete status are retained.
    finally:
        if lab:
            try:
                lab.close()
            except Exception as exc:
                error = (error or '') + ' cleanup_failed: ' + str(exc)
    summary = summarize(rows, execution_error=error)
    def git(*args):
        r = command(['git', *args], check=False)
        return r.stdout.strip() if r.returncode == 0 else 'unavailable'
    files = sorted((ROOT / 'isolation_lab').glob('*.py')) + sorted((ROOT / 'tests').glob('*.py'))
    files += [ROOT / p for p in ('compose.yaml', 'Dockerfile', 'Dockerfile.dockerignore', 'requirements.txt')]
    summary['provenance'] = {'version': VERSION, 'commit': git('rev-parse', 'HEAD'),
        'dirty': bool(git('status', '--porcelain', '--', str(ROOT))), 'controller_python': platform.python_version(),
        'source_digest': digest({str(p.relative_to(ROOT)): p.read_text() for p in files}),
        'ci_run_id': os.environ.get('GITHUB_RUN_ID'), 'os_execution_location': 'Linux Docker engine' if lab and lab.ids else 'not_executed',
        'baseline_commit': '2d4fda80b9e26cbaa51112fb2a65fdfb51d2bd1f'}
    save(output / 'summary.json', summary)
    return summary['all_expectations_matched']
