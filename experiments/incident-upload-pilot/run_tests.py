"""File-backed unittest entry point so spawned HTTP processes can import main."""

import argparse
import gc
import os
import sys
import unittest
import warnings


def run_checked(suite, *, require_network=False):
    """Fail on finalizer exceptions that unittest would otherwise only print."""
    unraisable_count = 0
    previous_hook = sys.unraisablehook

    def record_unraisable(event):
        nonlocal unraisable_count
        # Do not retain the exception, traceback or finalizing object.
        unraisable_count += 1
        previous_hook(event)

    sys.unraisablehook = record_unraisable
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ResourceWarning)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            # Collect unreachable connections while the failure hook is active.
            gc.collect()
    finally:
        sys.unraisablehook = previous_hook
    if unraisable_count:
        print(f"Unraisable exceptions observed: {unraisable_count}", file=sys.stderr)
    if require_network and result.skipped:
        print("Required network run must not skip any tests", file=sys.stderr)
    return 0 if (result.wasSuccessful() and not unraisable_count
                 and not (require_network and result.skipped)) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-network", action="store_true")
    args = parser.parse_args()
    if args.require_network and os.environ.get("PILOT_NETWORK_TESTS") != "1":
        print("PILOT_NETWORK_TESTS=1 is required for this run", file=sys.stderr)
        return 2
    return run_checked(unittest.defaultTestLoader.discover("tests"),
                       require_network=args.require_network)


if __name__ == "__main__":
    raise SystemExit(main())
