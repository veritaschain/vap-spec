"""Run measured synthetic local erasure or recheck its public evidence."""

import argparse
import json
import sys

from .protocol import InputError
from .suite import run_suite, verify_exports


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run-suite")
    run.add_argument("--output", required=True)
    run.add_argument("--print-summary", action="store_true")
    recheck = commands.add_parser("verify-exports")
    recheck.add_argument("directory")
    args = parser.parse_args()
    try:
        if args.command == "run-suite":
            summary = run_suite(args.output, print_summary=args.print_summary)
            return 0 if summary["all_expectations_matched"] else 1
        print(json.dumps(verify_exports(args.directory), ensure_ascii=False))
        return 0
    except (InputError, OSError) as exc:
        print("Local erasure pilot error: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
