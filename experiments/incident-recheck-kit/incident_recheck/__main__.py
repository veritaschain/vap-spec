"""Build, inspect or recheck the fixed incident evidence snapshot."""

import argparse
import sys

from .archive import build_archive, inspect_archive
from .layout import KitError, collect_payload, json_bytes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="Build a new deterministic archive and recheck all 53 exports")
    build.add_argument("--output", required=True)
    for name in ("inspect", "verify"):
        command = commands.add_parser(name, help="Inspect integrity" if name == "inspect" else "Recheck using trusted checkout sources")
        command.add_argument("--archive", required=True)
        command.add_argument("--expected-sha256", required=True,
                             help="Expected raw ZIP hash obtained outside the candidate archive")
    args = parser.parse_args(argv)
    try:
        if args.command == "inspect":
            inspected = inspect_archive(args.archive, args.expected_sha256)
            response = {
                "format": "incident-recheck-inspection/0.1",
                "archive_sha256": inspected["archive_sha256"],
                "manifest_sha256": inspected["manifest_sha256"],
                "file_count": len(inspected["files"]),
                "payload_bytes": sum(map(len, inspected["files"].values())),
                "scope": inspected["manifest"]["scope"],
                "source_binding": "NOT_CHECKED",
                "exports_rechecked": False,
            }
        else:
            from .runner import recheck_archive
            if args.command == "build":
                measured = build_archive(args.output, collect_payload())
                response = {"format": "incident-recheck-build/0.1", **measured,
                            "report": recheck_archive(args.output, measured["archive_sha256"])}
            else:
                response = recheck_archive(args.archive, args.expected_sha256)
        sys.stdout.buffer.write(json_bytes(response))
        return 0
    except (KitError, OSError) as exc:
        print("Incident recheck failed: " + type(exc).__name__ + ": " + str(exc)[:2000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
