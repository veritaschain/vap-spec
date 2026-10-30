"""Run the synthetic local pilot or recheck its public exports."""

import argparse
import json
import sys
from pathlib import Path

from .protocol import InputError


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run-suite")
    run.add_argument("--output", type=Path, default=Path("generated"))
    run.add_argument("--print-summary", action="store_true")
    verify = commands.add_parser("verify-exports")
    verify.add_argument("output", type=Path)
    args = parser.parse_args(argv)
    try:
        from .suite import run_suite, verify_exports
        if args.command == "run-suite":
            return run_suite(args.output, print_summary=args.print_summary)
        print(json.dumps(verify_exports(args.output), ensure_ascii=False))
        return 0
    except (InputError, OSError) as exc:
        print(json.dumps({"error": "PILOT_NOT_COMPLETED", "detail": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
