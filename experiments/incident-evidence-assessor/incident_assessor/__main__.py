"""CLI exit 0 means a report was produced, not evidence approval."""

import argparse
import json
import sys
from pathlib import Path

from .assess import assess
from .model import InputError, strict_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    evaluate = commands.add_parser("assess", help="assess a package using separately selected evaluator trust")
    evaluate.add_argument("input", type=Path)
    evaluate.add_argument("--trust", type=Path, required=True)
    evaluate.add_argument("--allow-synthetic", action="store_true")
    evaluate.add_argument("--output", type=Path)
    suite = commands.add_parser("run-suite", help="generate and compare 23 synthetic translations of the catalogue")
    suite.add_argument("--output-dir", type=Path, default=Path("generated"))
    args = parser.parse_args(argv)
    try:
        if args.command == "run-suite":
            from suite import run_suite
            return run_suite(args.output_dir)
        report = assess(strict_json(args.input), strict_json(args.trust), allow_synthetic=args.allow_synthetic)
        rendered = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        return 0
    except (InputError, OSError) as exc:
        print(json.dumps({"error": "INVALID_OR_UNREADABLE_INPUT", "detail": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
