#!/usr/bin/env python3
"""Exercise the shipped ignore rule and guard in disposable Git repositories.

Tests never change global Git configuration, commit files, use the network, or
touch real Claude settings. unittest assertions remain active under python -O.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("check_local_agent_settings.py").resolve()
REPOSITORY_IGNORE = SCRIPT.parents[2] / ".gitignore"
SENTINEL = "SYNTHETIC_LOCAL_SETTINGS_CONTENT_MUST_NOT_APPEAR_IN_OUTPUT"


class LocalAgentSettingsTests(unittest.TestCase):
    def setUp(self) -> None:
        scratch = tempfile.TemporaryDirectory(prefix="local-agent-settings-test-")
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name)
        self.repo = self.scratch / "repo"
        self.repo.mkdir()
        self.env = {
            key: value for key, value in os.environ.items() if not key.startswith("GIT_")
        }
        self.env.update(
            GIT_CONFIG_NOSYSTEM="1",
            GIT_CONFIG_GLOBAL=os.devnull,
            GIT_TERMINAL_PROMPT="0",
            GIT_CEILING_DIRECTORIES=str(self.scratch),
        )
        self.git("init", "--quiet")
        (self.repo / ".gitignore").write_bytes(REPOSITORY_IGNORE.read_bytes())
        self.git("add", "--", ".gitignore")

    def git(self, *args: str, input_bytes: bytes | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["git", "-C", str(self.repo), *args],
            input=input_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
            env=self.env,
            timeout=30,
        )

    def write(self, path: str, content: str = SENTINEL) -> None:
        destination = self.repo / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")

    def inspect(
        self, directory: Path | None = None, *, git_env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess:
        command = [sys.executable]
        if sys.flags.optimize:
            command.append("-O")
        command.extend([str(SCRIPT), "--repo", str(directory or self.repo)])
        env = self.env.copy()
        if git_env:
            env.update(git_env)
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
            timeout=40,
        )
        self.assertNotIn(SENTINEL.encode(), result.stdout + result.stderr)
        return result

    def test_root_and_nested_local_settings_are_ignored(self) -> None:
        paths = [
            ".claude/settings.local.json",
            "packages/demo/.claude/settings.local.json",
        ]
        for path in paths:
            self.write(path)
        encoded_paths = b"".join(path.encode() + b"\0" for path in paths)
        ignored = self.git("check-ignore", "-z", "--stdin", input_bytes=encoded_paths)
        self.assertEqual(ignored.stdout, encoded_paths)
        self.git("add", "--all")
        tracked = self.git("ls-files", "--cached", "-z").stdout.split(b"\0")
        for path in paths:
            self.assertNotIn(path.encode(), tracked)
        self.assertEqual(self.inspect().returncode, 0)

    def test_force_added_root_local_settings_are_rejected(self) -> None:
        path = ".claude/settings.local.json"
        self.write(path)
        self.git("add", "--force", "--", path)
        result = self.inspect()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"1 tracked local agent settings file(s)", result.stderr)

    def test_force_added_nested_local_settings_are_rejected(self) -> None:
        path = "packages/demo/.claude/settings.local.json"
        self.write(path)
        self.git("add", "--force", "--", path)
        self.assertEqual(self.inspect().returncode, 1)

    def test_multiple_blocked_paths_are_counted(self) -> None:
        paths = [
            ".claude/settings.local.json",
            "nested/.claude/settings.local.json",
        ]
        for path in paths:
            self.write(path)
        self.git("add", "--force", "--", *paths)
        result = self.inspect()
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"2 tracked local agent settings file(s)", result.stderr)

    def test_shared_settings_remain_allowed(self) -> None:
        paths = [".claude/settings.json", "nested/.claude/settings.json"]
        for path in paths:
            self.write(path)
        self.git("add", "--", *paths)
        tracked = self.git("ls-files", "--cached", "-z").stdout.split(b"\0")
        for path in paths:
            self.assertIn(path.encode(), tracked)
        self.assertEqual(self.inspect().returncode, 0)

    def test_similarly_named_unrelated_files_remain_allowed(self) -> None:
        paths = [
            "settings.local.json",
            ".claude-extra/settings.local.json",
            ".claude/settings.local.json.example",
            "nested/.claude/settings.local.json.template",
        ]
        for path in paths:
            self.write(path)
        self.git("add", "--", *paths)
        self.assertEqual(self.inspect().returncode, 0)

    def test_subdirectory_inspection_includes_root_paths(self) -> None:
        path = ".claude/settings.local.json"
        self.write(path)
        self.git("add", "--force", "--", path)
        subdirectory = self.repo / "nested"
        subdirectory.mkdir()
        self.assertEqual(self.inspect(subdirectory).returncode, 1)

    def test_inherited_pathspec_modes_cannot_hide_local_settings(self) -> None:
        path = ".claude/settings.local.json"
        self.write(path)
        self.git("add", "--force", "--", path)
        modes = (
            "GIT_LITERAL_PATHSPECS",
            "GIT_GLOB_PATHSPECS",
            "GIT_NOGLOB_PATHSPECS",
            "GIT_ICASE_PATHSPECS",
        )
        for mode in modes:
            with self.subTest(mode=mode):
                self.assertEqual(self.inspect(git_env={mode: "1"}).returncode, 1)
        with self.subTest(mode="all modes together"):
            self.assertEqual(
                self.inspect(git_env={mode: "1" for mode in modes}).returncode, 1
            )

    def test_output_does_not_reveal_file_contents_or_untrusted_paths(self) -> None:
        path = f"{SENTINEL}/.claude/settings.local.json"
        self.write(path)
        self.git("add", "--force", "--", path)
        result = self.inspect()
        self.assertEqual(result.returncode, 1)
        self.assertNotIn(path.encode(), result.stdout + result.stderr)

    def test_non_git_directory_fails_closed(self) -> None:
        outside = self.scratch / SENTINEL
        outside.mkdir()
        result = self.inspect(outside)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(b"OK:", result.stdout)

    def test_nonexistent_directory_fails_closed(self) -> None:
        result = self.inspect(self.scratch / SENTINEL)
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(b"OK:", result.stdout)

    def test_invalid_git_index_fails_closed(self) -> None:
        (self.repo / ".git" / "index").write_bytes(b"invalid synthetic Git index\n")
        result = self.inspect()
        self.assertEqual(result.returncode, 2)
        self.assertNotIn(b"OK:", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
