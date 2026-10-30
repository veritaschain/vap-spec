"""Run or recheck the explicitly synthetic local-publication experiment."""

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
    verify = commands.add_parser("verify-exports")
    verify.add_argument("directory")
    args = parser.parse_args()
    try:
        if args.command == "run-suite":
            result = run_suite(args.output, print_summary=args.print_summary)
            return 0 if result["all_expectations_matched"] else 1
        print(json.dumps(verify_exports(args.directory)))
        return 0
    except (InputError, OSError, KeyError, TypeError) as exc:
        print("Invalid or incomplete experiment: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
