"""Read explicit evidence and trust files; never contact a provider."""

import argparse
import json
import sys
from pathlib import Path

from . import InputError, assess


def main(argv=None):
    from incident_assessor.model import strict_json

    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    evaluate = subparsers.add_parser("assess")
    evaluate.add_argument("--input", required=True)
    evaluate.add_argument("--trust", required=True)
    evaluate.add_argument("--allow-synthetic", action="store_true")
    evaluate.add_argument("--output", help="Write a new report file; existing files are not overwritten")
    args = parser.parse_args(argv)
    try:
        result = assess(strict_json(args.input), strict_json(args.trust), allow_synthetic=args.allow_synthetic)
        output = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        if args.output:
            with Path(args.output).open("x", encoding="utf-8") as handle:
                handle.write(output)
        else:
            sys.stdout.write(output)
    except (InputError, OSError) as exc:
        parser.exit(2, "retention adapter: " + str(exc) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
