"""Run the collector pilot or recheck an externally pinned public capture."""

import argparse
import json
from pathlib import Path
import sys

from .protocol import InputError


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run-suite")
    run.add_argument("--output", type=Path, default=Path("generated"))
    run.add_argument("--print-summary", action="store_true")
    verify = commands.add_parser("verify-exports")
    verify.add_argument("output", type=Path)
    verify.add_argument("--expected-summary-sha256", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "run-suite":
            from .suite import run_suite
            return run_suite(args.output, print_summary=args.print_summary)
        from .exports import verify_exports
        print(json.dumps(verify_exports(args.output, expected_summary_sha256=args.expected_summary_sha256), ensure_ascii=False))
        return 0
    except (InputError, OSError, ImportError) as exc:
        print(json.dumps({"error": "COLLECTOR_PILOT_NOT_COMPLETED", "detail": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
