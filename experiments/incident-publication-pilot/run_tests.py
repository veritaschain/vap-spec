"""File-backed local publication test runner with strict finalizer handling."""

import argparse
import gc
import sys
import unittest
import warnings


def run_checked(suite, *, require_no_skips=False):
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
    if require_no_skips and result.skipped:
        print("Required local publication run must not skip any tests", file=sys.stderr)
    return 0 if (result.wasSuccessful() and not unraisable_count
                 and not (require_no_skips and result.skipped)) else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-no-skips", action="store_true")
    args = parser.parse_args()
    return run_checked(unittest.defaultTestLoader.discover("tests"),
                       require_no_skips=args.require_no_skips)


if __name__ == "__main__":
    raise SystemExit(main())
