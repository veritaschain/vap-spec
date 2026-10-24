"""Fail-closed package checks, independent of Docker availability."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import reproduce as r


class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)
        self.expected = r.read_json(r.ROOT / 'expected-results.json')

    def summary(self):
        rows = []
        for entry in self.expected['cases']:
            observed = {}
            for check in entry['equals']:
                target = observed
                for part in check['path'][:-1]:
                    target = target.setdefault(part, {})
                target[check['path'][-1]] = copy.deepcopy(check['value'])
            rows.append({'case': entry['case'], 'matched': True, 'observed': observed})
        return {'cases': rows, 'execution_complete': True, 'all_expectations_matched': True,
                'execution_error': None, 'cases_executed': 16, 'matching_cases': 16,
                'proposal_status': 'experimental_unadopted', 'production_ready': False,
                'independent_reproduction': 'not_established'}

    def test_json_rejects_duplicates_and_nonfinite(self):
        for text in ('{"x":1,"x":2}', '{"x":NaN}', '{"x":Infinity}'):
            path = self.path / 'bad.json'; path.write_text(text)
            with self.subTest(text=text), self.assertRaises(ValueError): r.read_json(path)

    def test_boolean_is_not_number(self):
        self.assertFalse(r.equal({'result': True}, {'result': 1}))
        self.assertFalse(r.equal(False, 0))

    def test_expected_observations_match(self):
        self.assertEqual(r.compare_lab(self.summary(), self.expected), [])

    def test_missing_duplicate_and_unexpected_cases_fail(self):
        for mutation in ('missing', 'duplicate', 'unexpected'):
            summary = self.summary()
            if mutation == 'missing': summary['cases'].pop()
            if mutation == 'duplicate': summary['cases'][-1] = summary['cases'][0]
            if mutation == 'unexpected': summary['cases'][-1]['case'] = '17'
            with self.subTest(mutation=mutation): self.assertTrue(r.compare_lab(summary, self.expected))

    def test_unsupported_independence_or_adoption_fails(self):
        for key, value in [('independent_reproduction', 'established'), ('proposal_status', 'adopted'), ('production_ready', True)]:
            summary = self.summary(); summary[key] = value
            with self.subTest(key=key): self.assertTrue(r.compare_lab(summary, self.expected))

    def test_incomplete_or_wrong_counts_fail(self):
        for key, value in [('execution_complete', False), ('execution_error', 'cleanup failed'), ('cases_executed', 15), ('matching_cases', True)]:
            summary = self.summary(); summary[key] = value
            with self.subTest(key=key): self.assertTrue(r.compare_lab(summary, self.expected))

    def test_match_flag_cannot_hide_changed_or_missing_observation(self):
        for mutation in ('changed', 'missing', 'wrong_type'):
            summary = self.summary()
            row = next(r for r in summary['cases'] if r['case'] == '15')
            if mutation == 'missing': row['observed'].pop('bypass_guarantee_established')
            else: row['observed']['bypass_guarantee_established'] = True if mutation == 'changed' else 0
            with self.subTest(mutation=mutation): self.assertTrue(r.compare_lab(summary, self.expected))

    def test_existing_output_is_not_overwritten(self):
        (self.path / 'keep').write_text('old evidence')
        with self.assertRaises(FileExistsError): r.run(self.path / 'source', self.path)
        self.assertEqual((self.path / 'keep').read_text(), 'old evidence')

    def test_output_inside_source_rejected(self):
        with self.assertRaisesRegex(ValueError, 'outside_frozen_source'): r.run(self.path, self.path / 'output')
        self.assertFalse((self.path / 'output').exists())

    def test_preflight_failure_records_incomplete(self):
        output = self.path / 'output'
        with patch.object(r, 'preflight', side_effect=ValueError('wrong source')):
            self.assertFalse(r.run(self.path / 'source', output))
        report = r.read_json(output / 'run-report.json')
        self.assertEqual(report['status'], 'incomplete')
        self.assertEqual(report['steps'], [])
        self.assertEqual(r.inventory(output), r.read_json(output / 'SHA256SUMS.json'))

    def test_inventory_includes_nested_manifest_and_rejects_symlink(self):
        (self.path / 'nested').mkdir()
        (self.path / 'SHA256SUMS.json').write_text('{}')
        (self.path / 'nested/SHA256SUMS.json').write_text('{}')
        self.assertEqual(set(r.inventory(self.path)), {'nested/SHA256SUMS.json'})
        (self.path / 'link').symlink_to(self.path / 'nested')
        with self.assertRaisesRegex(ValueError, 'symlink'): r.inventory(self.path)

    def test_inventory_detects_mutation_and_extra_file(self):
        (self.path / 'evidence').write_text('original')
        original = r.inventory(self.path)
        (self.path / 'evidence').write_text('changed')
        self.assertNotEqual(original, r.inventory(self.path))
        (self.path / 'evidence').write_text('original')
        (self.path / 'extra').write_text('extra')
        self.assertNotEqual(original, r.inventory(self.path))

    def test_source_commit_cleanliness_hash_and_symlink(self):
        file = self.path / 'input.py'; file.write_text('fixed')
        lock = {'commit': 'fixed-commit', 'protected_source_prefixes': ['experiment'], 'files': {'input.py': r.sha(file)}}
        with patch.object(r, 'command', side_effect=['fixed-commit', '', '']):
            self.assertEqual(r.verify_source(self.path, lock)['files_checked'], 1)
        for commands in (['wrong'], ['fixed-commit', ' M input.py'], ['fixed-commit', '', 'ignored.py']):
            with self.subTest(commands=commands), patch.object(r, 'command', side_effect=commands), self.assertRaises(ValueError):
                r.verify_source(self.path, lock)
        file.write_text('changed')
        with patch.object(r, 'command', side_effect=['fixed-commit', '', '']), self.assertRaisesRegex(ValueError, 'hash_mismatch'):
            r.verify_source(self.path, lock)
        file.unlink(); (self.path / 'target').write_text('fixed'); file.symlink_to(self.path / 'target')
        with patch.object(r, 'command', side_effect=['fixed-commit', '', '']), self.assertRaisesRegex(ValueError, 'symlink'):
            r.verify_source(self.path, lock)

    def test_non_linux_preflight_never_executes_docker(self):
        with patch.object(r, 'verify_source', return_value={}), patch.object(r.platform, 'system', return_value='Darwin'), patch.object(r, 'command') as command:
            with self.assertRaisesRegex(ValueError, 'native_linux'): r.preflight(self.path)
            command.assert_not_called()

    def test_step_checks_process_exit_and_exact_test_count(self):
        (self.path / 'logs').mkdir()
        samples = [(0, 'Ran 28 tests in 0.1s', True), (1, 'Ran 28 tests in 0.1s', False),
                   (0, 'Ran 27 tests in 0.1s', False), (0, 'nothing ran', False),
                   (0, 'Ran 28 tests in 0.1s\nRan 28 tests in 0.1s', False)]
        for code, log, success in samples:
            with self.subTest(code=code, log=log), patch.object(r.subprocess, 'run', return_value=subprocess.CompletedProcess([], code, '', log)):
                self.assertIs(r.step('test', ['mock'], self.path, self.path, 28)['ok'], success)

    def test_timeout_is_incomplete(self):
        (self.path / 'logs').mkdir()
        with patch.object(r.subprocess, 'run', side_effect=subprocess.TimeoutExpired('mock', 1, output=b'partial')):
            result = r.step('test', ['mock'], self.path, self.path)
        self.assertFalse(result['ok']); self.assertFalse(result['completed'])
        self.assertIn('partial', (self.path / 'logs/test.log').read_text())

    def test_pack_is_deterministic_complete_and_exclusive(self):
        first, second = self.path / 'a.zip', self.path / 'b.zip'
        r.pack(first); r.pack(second)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with zipfile.ZipFile(first) as archive:
            prefix = 'vap-os-isolation-kit/'
            self.assertEqual(set(archive.namelist()), {prefix + p for p in r.KIT_FILES + ['SHA256SUMS']})
            for line in archive.read(prefix + 'SHA256SUMS').decode().splitlines():
                digest, name = line.split('  ', 1)
                self.assertEqual(hashlib.sha256(archive.read(prefix + name)).hexdigest(), digest)
        with self.assertRaises(FileExistsError): r.pack(first)

    def completed_output(self):
        output = self.path / 'complete'; output.mkdir(); (output / 'logs').mkdir()
        frozen = {'commit': 'fixed'}
        preflight = {'source': frozen}
        r.save(output / 'preflight.json', preflight)
        report = {'status': 'matched', 'independence': 'not_assessed',
                  'proposal_status': 'experimental_unadopted', 'overall_vap_pass': None,
                  'kit_files_sha256': r.kit_digests(), 'preflight': preflight,
                  'postflight_source': frozen, 'steps': []}
        for name in ['lab-unit', 'gate-unit', 'verifier-unit', 'lab', 'gate', 'verifier', 'artifact-recheck']:
            log = output / 'logs' / (name + '.log')
            count = self.expected['unit_tests'].get(name)
            log.write_text('Ran ' + str(count) + ' tests in 0.1s' if count else 'complete')
            result = {'step': name, 'ok': True, 'completed': True, 'returncode': 0, 'log_sha256': r.sha(log)}
            if count: result.update(tests_executed=count, expected_tests=count)
            report['steps'].append(result)
        r.save(output / 'run-report.json', report)
        r.save(output / 'SHA256SUMS.json', r.inventory(output))
        return output, report, frozen

    def test_saved_run_checks_all_steps_and_counts(self):
        output, report, frozen = self.completed_output()
        with patch.object(r, 'verify_source', return_value=frozen), patch.object(r, 'command', return_value='rechecked') as check:
            r.check_run(self.path / 'source', output)
            check.assert_called_once()
        # Rewrite even the unsigned hashes: the fixed step inventory must still reject this.
        report['steps'].pop()
        r.save(output / 'run-report.json', report); r.save(output / 'SHA256SUMS.json', r.inventory(output))
        with patch.object(r, 'verify_source', return_value=frozen), self.assertRaisesRegex(ValueError, 'step_inventory'):
            r.check_run(self.path / 'source', output)

    def test_saved_run_rejects_skipped_tests_even_with_rehashed_report(self):
        output, report, frozen = self.completed_output()
        log = output / 'logs/lab-unit.log'; log.write_text('Ran 0 tests in 0.0s')
        report['steps'][0].update(log_sha256=r.sha(log), tests_executed=0)
        r.save(output / 'run-report.json', report); r.save(output / 'SHA256SUMS.json', r.inventory(output))
        with patch.object(r, 'verify_source', return_value=frozen), self.assertRaisesRegex(ValueError, 'unit_test_count'):
            r.check_run(self.path / 'source', output)

    def test_saved_run_rejects_added_file(self):
        output, report, frozen = self.completed_output()
        (output / 'extra').write_text('extra')
        with patch.object(r, 'verify_source', return_value=frozen), self.assertRaisesRegex(ValueError, 'inventory_or_hash'):
            r.check_run(self.path / 'source', output)

    def test_environment_drops_import_and_compose_overrides(self):
        with patch.dict(r.os.environ, {'PYTHONPATH': '/bad', 'PYTHONHOME': '/bad', 'COMPOSE_PROFILES': 'bad', 'COMPOSE_FILE': 'bad'}):
            env = r.environment()
        for key in ('PYTHONPATH', 'PYTHONHOME', 'COMPOSE_PROFILES', 'COMPOSE_FILE'): self.assertNotIn(key, env)
        self.assertEqual(env['PYTHONDONTWRITEBYTECODE'], '1')


if __name__ == '__main__': unittest.main()
