"""File-backed unittest entry point so spawned HTTP processes can import main."""

import argparse
import os
import sys
import unittest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-network", action="store_true")
    args = parser.parse_args()
    if args.require_network and os.environ.get("PILOT_NETWORK_TESTS") != "1":
        print("PILOT_NETWORK_TESTS=1 is required for this run", file=sys.stderr)
        return 2
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover("tests"))
    if args.require_network and result.skipped:
        print("Required network run must not skip any tests", file=sys.stderr)
    return 0 if result.wasSuccessful() and not (args.require_network and result.skipped) else 1


if __name__ == "__main__":
    raise SystemExit(main())
