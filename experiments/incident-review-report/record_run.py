"""Record strict tests, real frozen-kit rechecks and deterministic report delivery."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import platform
import sys
from tempfile import TemporaryDirectory
import unittest

from incident_review.common import ReviewError, json_bytes, sha256
from incident_review.core import (FROZEN_ARCHIVE, _load_kit, generate_report,
                                  source_identity, verify_report)
from incident_review.delivery import bundle_bytes, publish_bundle, render_members
from run_tests import run_checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New output directory; existing paths are refused")
    args = parser.parse_args()
    try:
        before = source_identity()
        output = Path(args.output)
        output.mkdir(mode=0o700)
        status, tests = run_checked(unittest.defaultTestLoader.discover("tests"), require_no_skips=True)
        if status:
            raise ReviewError("Strict tests failed; no successful execution record was produced")
        _load_kit()
        from incident_recheck.archive import build_archive
        from incident_recheck.layout import collect_payload
        with TemporaryDirectory(prefix="review-record-kit-") as temporary:
            original = Path(temporary) / "frozen-kit.zip"
            built = build_archive(original, collect_payload())
            if built["archive_sha256"] != FROZEN_ARCHIVE:
                raise ReviewError("Frozen kit regeneration differs from the supported input")
            report = generate_report(original, FROZEN_ARCHIVE)
            members = render_members(report)
            raw = bundle_bytes(report)
            destination = output / "incident-review.zip"
            publish_bundle(destination, raw)
            checked = verify_report(original, FROZEN_ARCHIVE, destination, sha256(raw))
        if json_bytes(source_identity()) != json_bytes(before) or json_bytes(report["reporter"]) != json_bytes(before):
            raise ReviewError("Execution sources changed during tests or report generation")
        for name, content in members.items():
            with (output / name).open("xb") as handle:
                handle.write(content)
        checksums = {"incident-review.zip": sha256(raw), **{name: sha256(value) for name, value in members.items()}}
        with (output / "SHA256SUMS").open("x", encoding="ascii") as handle:
            handle.write("".join(checksums[name] + "  " + name + "\n" for name in sorted(checksums)))
        frames = [frame for row in report["cases"] for frame in row["frames"]]
        summary = {
            "format": "incident-review-execution/0.1",
            "recorded_at": datetime.now(timezone.utc).isoformat(),
            "python": platform.python_version(), "platform": platform.system(),
            "source_manifest": before["source_manifest"], "source_sha256": before["source_sha256"],
            "source_unchanged": True, "frozen_kit_unchanged": True,
            "tests": tests, "report_verification": checked, "deterministic_rederivation": True,
            "members": {name: {"sha256": sha256(content), "byte_length": len(content)}
                        for name, content in sorted(members.items())},
            "presentation_counts": {"cases": len(report["cases"]), "frames": len(frames),
                "recorded_frames": sum(f["availability"] == "RECORDED" for f in frames),
                "not_recorded_frames": sum(f["availability"] == "FRAME_NOT_RECORDED" for f in frames),
                "notes": sum(len(row["notes"]) for row in report["cases"])},
        }
        with (output / "summary.json").open("xb") as handle:
            handle.write(json_bytes(summary))
        print("INCIDENT_REVIEW_SUMMARY_JSON=" + json_bytes(summary).decode("ascii").rstrip("\n"))
        return 0
    except (ReviewError, OSError, ValueError) as exc:
        print("Incident review recording failed: " + str(exc)[:2000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
