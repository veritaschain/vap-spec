"""Create or rederive source-attributed reports for the fixed incident capture."""

import argparse
import sys

from .common import ReviewError, json_bytes
from .core import build_report, verify_report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("build", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--archive", required=True, help="Original verified incident kit ZIP")
        command.add_argument("--expected-sha256", required=True, help="Kit digest obtained outside the candidate archive")
        if name == "build":
            command.add_argument("--output", required=True, help="New report ZIP; existing paths are refused")
        else:
            command.add_argument("--report", required=True)
            command.add_argument("--expected-report-sha256", required=True, help="Report digest obtained outside the candidate report")
    args = parser.parse_args(argv)
    try:
        if args.command == "build":
            result = build_report(args.archive, args.expected_sha256, args.output)
        else:
            result = verify_report(args.archive, args.expected_sha256, args.report, args.expected_report_sha256)
        sys.stdout.buffer.write(json_bytes(result))
        return 0
    except (ReviewError, OSError) as exc:
        print("Incident review failed: " + type(exc).__name__ + ": " + str(exc)[:2000], file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
