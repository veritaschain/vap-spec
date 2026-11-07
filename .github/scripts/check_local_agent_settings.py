#!/usr/bin/env python3
"""Reject tracked Claude Code local permission settings without reading contents.

Run from a Git working tree, or pass --repo PATH. Only the current Git index is
inspected, including force-added files and paths outside a nested working
directory. Shared .claude/settings.json files remain allowed.

This path check is not a content/history secret scan. CI runs after a push; it
cannot stop an earlier disclosure or replace credential revocation.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


LOCAL_SETTINGS_PATH = b".claude/settings.local.json"


class InspectionError(Exception):
    """A Git working tree could not be inspected safely."""


def run_git(repo: Path, *args: str) -> bytes:
    """Return Git output, withholding raw diagnostics and paths on failure."""
    env = os.environ.copy()
    # The caller must not turn the top-level :/ selector into a literal path or
    # otherwise change its meaning through inherited pathspec modes.
    for name in (
        "GIT_LITERAL_PATHSPECS",
        "GIT_GLOB_PATHSPECS",
        "GIT_NOGLOB_PATHSPECS",
        "GIT_ICASE_PATHSPECS",
    ):
        env.pop(name, None)
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(repo), *args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
            env=env,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InspectionError from exc
    if result.returncode != 0:
        raise InspectionError
    return result.stdout


def tracked_local_settings_count(repo: Path) -> int:
    """Count matching index paths; never open a tracked or working-tree file."""
    if run_git(repo, "rev-parse", "--is-inside-work-tree").strip() != b"true":
        raise InspectionError

    # NUL delimiters preserve arbitrary filename bytes. The top-level pathspec
    # includes the whole repository even when --repo selects a subdirectory.
    listing = run_git(
        repo, "ls-files", "--cached", "-z", "--full-name", "--", ":/"
    )
    if listing and not listing.endswith(b"\0"):
        raise InspectionError
    paths = set(listing.split(b"\0"))
    return sum(
        path == LOCAL_SETTINGS_PATH
        or path.endswith(b"/" + LOCAL_SETTINGS_PATH)
        for path in paths
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo", type=Path, default=Path("."), help="Git working tree or subdirectory"
    )
    args = parser.parse_args()
    try:
        count = tracked_local_settings_count(args.repo)
    except InspectionError:
        print("ERROR: Git could not inspect the selected working tree.", file=sys.stderr)
        return 2
    if count:
        # Counts only: even a filename could contain a secret or a CI annotation.
        print(
            f"ERROR: {count} tracked local agent settings file(s) found. "
            "Remove .claude/settings.local.json files from the Git index.",
            file=sys.stderr,
        )
        return 1
    print("OK: no tracked .claude/settings.local.json files found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
