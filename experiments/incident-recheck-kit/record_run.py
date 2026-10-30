"""Record strict tests, repeatable archive bytes and a complete offline recheck."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
import unittest

from incident_recheck.archive import build_archive
from incident_recheck.layout import KitError, collect_payload, json_bytes, sha256, source_manifest
from incident_recheck.runner import recheck_archive
from run_tests import run_checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New output directory; existing paths are refused")
    args = parser.parse_args()
    try:
        before = source_manifest()
        output = Path(args.output)
        output.mkdir(mode=0o700)
        status, tests = run_checked(unittest.defaultTestLoader.discover("tests"), require_no_skips=True)
        if status:
            raise KitError("Strict tests failed; no successful capture is recorded")
        payload = collect_payload()
        first = output / "incident-ci-2026-10-30.zip"
        second = output / "repeat-build.zip"
        measured = build_archive(first, payload)
        repeated = build_archive(second, payload)
        if first.read_bytes() != second.read_bytes() or measured != repeated:
            raise KitError("Identical payload did not produce identical archive bytes")
        second.unlink()
        report = recheck_archive(first, measured["archive_sha256"])
        after = source_manifest()
        if before != after:
            raise KitError("Execution source changed during tests, build or recheck")
        summary = {
            "format": "incident-recheck-execution/0.1",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(), "platform": platform.system(),
            "source_manifest": before, "source_sha256": sha256(json_bytes(before)[:-1]),
            "source_unchanged": True, "tests": tests, "build": measured,
            "deterministic_rebuild": True, "report": report,
        }
        (output / "summary.json").write_bytes(json_bytes(summary))
        (output / "SHA256SUMS").write_text(measured["archive_sha256"] + "  " + first.name + "\n", encoding="ascii")
        print("INCIDENT_RECHECK_SUMMARY_JSON=" + json_bytes(summary).decode("ascii").rstrip("\n"))
        return 0
    except (KitError, OSError) as exc:
        print("Incident recheck recording failed: " + str(exc)[:2000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
