"""Counterexamples from PR #12 final review; no simulated result counts as OS execution."""
import copy
import errno
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from isolation_lab import ROLES
from isolation_lab import suite
from isolation_lab.checks import filesystem_permissions_match, runtime_mounts_match
from record_gate.common import Rejected


class InventoryTests(unittest.TestCase):
    def observations(self):
        return {role: {'own_config_readable': {'allowed': True},
                       'canaries': {other: {'allowed': other == role,
                                           'errno': None if other == role else errno.EACCES}
                                    for other in ROLES}} for role in ROLES}

    def mounts(self):
        return {'mounts': [
            {'destination': '/run/role', 'type': 'volume', 'name': 'test_agent-config', 'rw': False},
            {'destination': '/data', 'type': 'volume', 'name': 'test_agent-data', 'rw': True},
            {'destination': '/canaries', 'type': 'volume', 'name': 'test_canaries', 'rw': False}],
                'tmpfs': {'/tmp': 'rw,noexec,nosuid,size=16m,mode=1777'}}

    def test_complete_filesystem_matrix_passes(self):
        self.assertTrue(filesystem_permissions_match(self.observations()))

    def test_missing_extra_or_empty_role_inventory_fails(self):
        for mode in ('empty', 'missing', 'extra'):
            data = self.observations()
            if mode == 'empty': data.clear()
            elif mode == 'missing': del data['agent']
            else: data['extra'] = data['agent']
            with self.subTest(mode=mode): self.assertFalse(filesystem_permissions_match(data))

    def test_missing_extra_or_empty_canary_inventory_fails(self):
        for mode in ('empty', 'missing', 'extra'):
            data = self.observations()
            canaries = data['agent']['canaries']
            if mode == 'empty': canaries.clear()
            elif mode == 'missing': del canaries['gate']
            else: canaries['extra'] = canaries['gate']
            with self.subTest(mode=mode): self.assertFalse(filesystem_permissions_match(data))

    def test_wrong_error_or_nonboolean_permission_does_not_pass(self):
        for change in ({'allowed': True}, {'allowed': 0}, {'errno': errno.ENOENT}, {'errno': '13'}):
            data = self.observations()
            data['agent']['canaries']['gate'].update(change)
            with self.subTest(change=change): self.assertFalse(filesystem_permissions_match(data))
        data = self.observations()
        data['agent']['own_config_readable']['allowed'] = 1
        self.assertFalse(filesystem_permissions_match(data))

    def test_complete_role_private_mounts_pass(self):
        self.assertTrue(runtime_mounts_match('agent', self.mounts(), 'test'))

    def test_missing_duplicate_substituted_or_writable_foreign_mount_fails(self):
        valid = self.mounts()
        mutations = []
        for changes in ({'name': 'test_gate-data'}, {'type': 'bind'}, {'rw': 1}):
            data = copy.deepcopy(valid); data['mounts'][1].update(changes); mutations.append(data)
        data = copy.deepcopy(valid); data['mounts'][0]['rw'] = True; mutations.append(data)
        data = copy.deepcopy(valid); data['mounts'].pop(); mutations.append(data)
        data = copy.deepcopy(valid); data['mounts'].append(data['mounts'][0]); mutations.append(data)
        data = copy.deepcopy(valid); data['mounts'][-1] = data['mounts'][0]; mutations.append(data)
        for tmpfs in ({}, {'/tmp': 'rw'}, {'/tmp': 'rw,noexec,nosuid,suid'}, {'/secret': 'rw,noexec,nosuid'}):
            data = copy.deepcopy(valid); data['tmpfs'] = tmpfs; mutations.append(data)
        for data in mutations:
            with self.subTest(data=data): self.assertFalse(runtime_mounts_match('agent', data, 'test'))


class CleanupTests(unittest.TestCase):
    def exercise(self, *, removal=0, listing=0, listed='', built=True, down=0):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        lab = suite.Lab(Path(directory.name))
        lab.build_attempted = True
        lab.image_built = built
        lab.compose = MagicMock(return_value=SimpleNamespace(returncode=down))
        replies = [SimpleNamespace(returncode=removal), SimpleNamespace(returncode=listing, stdout=listed)]
        with patch.object(suite.shutil, 'which', return_value='/mock/docker'), patch.object(suite, 'command', side_effect=replies):
            try:
                lab.close()
            finally:
                self.assertFalse(Path(lab.tmp.name).exists())
        return json.loads((Path(directory.name) / 'cleanup.json').read_text())

    def test_success_requires_confirmed_image_absence(self):
        self.assertIs(self.exercise()['image_absence_confirmed'], True)

    def test_failed_removal_or_query_is_not_absence(self):
        for removal, listing in ((1, 1), (1, 0), (0, 1)):
            with self.subTest(removal=removal, listing=listing), self.assertRaises(Rejected):
                self.exercise(removal=removal, listing=listing)

    def test_remaining_image_prevents_cleanup_success(self):
        with self.assertRaises(Rejected): self.exercise(listed='sha256:still-present\n')

    def test_failed_build_requires_a_successful_absence_query(self):
        self.assertTrue(self.exercise(removal=1, built=False)['image_absence_confirmed'])
        with self.assertRaises(Rejected): self.exercise(removal=1, listing=1, built=False)

    def test_container_teardown_failure_is_retained(self):
        with self.assertRaises(Rejected): self.exercise(down=1)


class OutputTests(unittest.TestCase):
    def test_existing_results_refused_before_any_new_lab(self):
        with tempfile.TemporaryDirectory() as directory:
            old = Path(directory) / 'evidence.json'
            old.write_text('{"old_run":true}')
            with patch.object(suite, 'Lab') as lab, self.assertRaisesRegex(ValueError, 'choose_a_fresh_output'):
                suite.run_suite(directory)
            lab.assert_not_called()
            self.assertEqual(old.read_text(), '{"old_run":true}')
            self.assertFalse((Path(directory) / 'summary.json').exists())

    def test_existing_empty_directory_and_symlink_are_refused(self):
        with tempfile.TemporaryDirectory() as directory:
            link = Path(directory) / 'link'
            link.symlink_to(Path(directory) / 'absent', target_is_directory=True)
            for path in (Path(directory), link):
                with self.subTest(path=path), self.assertRaises(ValueError): suite.prepare_output(path)

    def test_missing_docker_writes_only_a_fresh_incomplete_report(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / 'new-run'
            with patch.object(suite.shutil, 'which', return_value=None):
                self.assertFalse(suite.run_suite(output))
            self.assertEqual({p.name for p in output.iterdir()}, {'summary.json'})
            summary = json.loads((output / 'summary.json').read_text())
            self.assertFalse(summary['execution_complete'])
            self.assertEqual(summary['cases_executed'], 0)
            self.assertEqual(summary['provenance']['os_execution_location'], 'not_executed')


class ProvenanceTests(unittest.TestCase):
    def fixture(self, directory):
        repo = Path(directory)
        root = repo / 'experiments/os-isolated-gate'
        root.mkdir(parents=True)
        for name in ('compose.yaml', 'Dockerfile', 'Dockerfile.dockerignore', 'requirements.txt'):
            (root / name).write_text('fixture')
        for name, package in [('pre-record-gate', 'record_gate'), ('declared-scope-verifier', 'scope_verifier')]:
            target = root.parent / name
            (target / package).mkdir(parents=True)
            (target / package / '__init__.py').write_text('# fixture')
            (target / 'requirements.txt').write_text('# fixture')
        workflow = repo / '.github/workflows/os-isolated-gate.yml'
        workflow.parent.mkdir(parents=True); workflow.write_text('fixture')
        return repo, root

    def test_modified_imported_source_changes_its_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, root = self.fixture(directory)
            with patch.object(suite, 'ROOT', root), patch.object(suite, 'REPO', repo), patch.object(suite, 'command', return_value=SimpleNamespace(returncode=0, stdout='')):
                before = suite.source_snapshot()
                (root.parent / 'pre-record-gate/record_gate/__init__.py').write_text('# changed fixture')
                after = suite.source_snapshot()
            self.assertEqual(before['input_digests']['os-isolated-gate'], after['input_digests']['os-isolated-gate'])
            self.assertNotEqual(before['input_digests']['pre-record-gate'], after['input_digests']['pre-record-gate'])

    def test_dirty_check_includes_imported_code_and_workflow(self):
        with tempfile.TemporaryDirectory() as directory:
            repo, root = self.fixture(directory)
            with patch.object(suite, 'ROOT', root), patch.object(suite, 'REPO', repo), patch.object(suite, 'command', return_value=SimpleNamespace(returncode=0, stdout=' M imported.py')) as cmd:
                self.assertTrue(suite.source_snapshot()['dirty'])
            status = next(c.args[0] for c in cmd.call_args_list if c.args[0][1] == 'status')
            self.assertIn(str(root.parent / 'pre-record-gate'), status)
            self.assertIn(str(root.parent / 'declared-scope-verifier'), status)
            self.assertIn(str(repo / '.github/workflows/os-isolated-gate.yml'), status)


if __name__ == '__main__':
    unittest.main()
