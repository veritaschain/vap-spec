"""Capture the existing OS lab without changing its code or fixed evidence.

Only a disposable Docker lab is exercised. Private signing keys stay in memory.
The trusted controller observes both sides of selected probes; this is not remote
attestation or proof against a compromised Docker daemon/controller.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
from control_evidence import ARTIFACTS, artifact, digest, read_json, seal, verify, preflight, probe_result_record

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def save(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def source_state():
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=REPO, text=True).strip()
    paths = sorted(HERE.glob('*.py')) + [REPO / '.github/workflows/control-state-evidence.yml']
    files = {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    return commit, digest(files), files


def run(output):
    # No reuse, truncation, or deletion of previous results, including symlinks.
    output = Path(output).absolute()
    output.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(HERE.parent / 'os-isolated-gate'))
    from isolation_lab import suite
    original_lab, original_command = suite.Lab, suite.command
    run_id = uuid.uuid4().hex
    observations, active = [], []
    before_commit, before_digest, source_files = source_state()
    def observe(kind, details):
        observations.append({'seq': len(observations) + 1, 'run_id': run_id,
                             'monotonic_ns': time.monotonic_ns(),
                             'wall_time': datetime.now(timezone.utc).isoformat(),
                             'observer': 'trusted-controller', 'kind': kind, 'details': details})
    def topology(lab):
        measured = lab.inspect()
        expected = {'agent': ['frontend'], 'gate': ['frontend', 'audit', 'backend'],
                    'audit': ['audit'], 'backend': ['backend'], 'open-backend': ['backend']}
        # Compare the declared topology to actual Docker inspection, not to a flag.
        expected = {role: sorted(lab.project + '_' + n for n in nets) for role, nets in expected.items()}
        actual = {role: sorted(state['networks']) for role, state in measured.items()}
        return {'declared_networks': expected, 'observed_networks': actual,
                'runtime': measured, 'config_digest': digest(measured),
                'declared_matches_observed': actual == expected}
    class ObservedLab(original_lab):
        def start(self):
            super().start()
            active.append(self)
            self.preflight_state = topology(self)
            self.preflight_ns = time.monotonic_ns()
            observe('initial-topology', self.preflight_state)
            # Resolve only the known, co-networked mock gate. No public DNS name,
            # remote URL or host service is used. This is NOT a DNS-tunnel test.
            code = ("import json,socket,os;from pathlib import Path;"
                    "print(json.dumps({'gate_ipv4':sorted({x[4][0] for x in socket.getaddrinfo('gate',8080,socket.AF_INET,socket.SOCK_STREAM)}),"
                    "'ipv6_interfaces':Path('/proc/net/if_inet6').read_text(),"
                    "'proxy_environment_present':any(k.lower() in ('http_proxy','https_proxy','all_proxy') for k in os.environ)}))")
            result = self.compose('exec', '-T', 'agent', 'python', '-c', code, timeout=20)
            observe('bounded-network-context', read_json(result.stdout))
        def probe(self, role, *args):
            sensitive = role == 'agent' and args and args[0] in ('execute', 'network')
            measured = topology(self) if sensitive else None
            if measured:
                observe('pre-action-topology', measured)
                # Demonstrate config invalidation only. No path measurement is
                # invented: every required path remains unknown in this receipt.
                prior = {'run_id': run_id, 'config_digest': self.preflight_state['config_digest'],
                         'measured_ns': self.preflight_ns, 'paths': {}}
                decision = preflight(prior, run_id=run_id, config_digest=measured['config_digest'],
                                     now_ns=time.monotonic_ns(), max_age_ns=10**15,
                                     required_paths=['literal_ipv4', 'named_ipv4', 'ipv6', 'dns', 'proxy'])
                observe('preflight-evaluation-not-enforced', decision)
            try:
                result = super().probe(role, *args)
                observe('probe-result', probe_result_record(role, args, result))
                return result
            except Exception as exc:
                observe('probe-error', {'role': role, 'arguments': list(args), 'error_type': type(exc).__name__})
                raise
            finally:
                if sensitive:
                    observe('post-action-topology', topology(self))
    def command(args, **kwargs):
        change = args[:3] in (['docker', 'network', 'connect'], ['docker', 'network', 'disconnect'])
        if change:
            observe('topology-change-request', {'arguments': args})
        result = original_command(args, **kwargs)
        if change:
            observe('topology-change-result', {'returncode': result.returncode,
                                               'measured': topology(active[0])})
        return result
    suite.Lab, suite.command = ObservedLab, command
    try:
        matched = suite.run_suite(output / 'legacy')
    finally:
        suite.Lab, suite.command = original_lab, original_command
        save(output / 'observations.json', observations)
    after_commit, after_digest, _ = source_state()
    missing = [name for name in ARTIFACTS if not (output / 'legacy' / name).is_file()]
    if missing:
        save(output / 'incomplete.json', {'missing_artifacts': missing, 'execution_complete': False})
        raise RuntimeError('Incomplete lab; no complete signed bundle produced: ' + ', '.join(missing))
    payload = {'run_id': run_id, 'observations': observations,
               'source_commit_before': before_commit, 'source_commit_after': after_commit,
               'source_digest_before': before_digest, 'source_digest_after': after_digest,
               'source_files': source_files, 'ci_run_id': os.environ.get('GITHUB_RUN_ID'),
               'scope': 'listed controller observations and exact raw artifacts of this run only',
               'external_anchor': 'not_established', 'independent_reproduction': 'not_established',
               'artifacts': {name: artifact((output / 'legacy' / name).read_text(encoding='utf-8')) for name in ARTIFACTS}}
    key = Ed25519PrivateKey.generate()
    public = key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
    envelope = seal(payload, key)
    save(output / 'bundle.json', envelope)
    (output / 'test-public-key.hex').write_text(public.hex() + '\n')
    (output / 'run-id.txt').write_text(run_id + '\n')
    report = verify(envelope, public, run_id)
    save(output / 'verification.json', report)
    print('TEST_KEY_SHA256=' + hashlib.sha256(public).hexdigest())
    print('RUN_ID=' + run_id)
    print(json.dumps(report, indent=2))
    # The deliberately induced bypass MUST remain visible, even when all expected
    # test outcomes match. This exit code is not an overall security verdict.
    if (not matched or report['integrity'] != 'VERIFIED' or
            report['case_inventory'] != 'COMPLETE_RECORDED_INVENTORY' or
            report['isolation'] != 'VIOLATED_IN_NEGATIVE_CONTROL'):
        raise RuntimeError('Expected experiment results not established')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    cmd = commands.add_parser('run')
    cmd.add_argument('--output', type=Path, required=True)
    check = commands.add_parser('verify')
    check.add_argument('bundle', type=Path)
    check.add_argument('--trusted-key', type=Path, required=True)
    check.add_argument('--run-id', required=True)
    args = parser.parse_args()
    if args.command == 'run':
        run(args.output)
    else:
        report = verify(read_json(args.bundle.read_text()),
                        bytes.fromhex(args.trusted_key.read_text().strip()), args.run_id)
        print(json.dumps(report, indent=2))
        if report['integrity'] != 'VERIFIED':
            raise SystemExit(1)


if __name__ == '__main__':
    main()
