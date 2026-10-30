"""Strict offline-kit tests, including subprocess cleanup and finalizer failures."""

import argparse
import gc
import json
import sys
import unittest
import warnings


def run_checked(suite, *, require_no_skips=False):
    unraisable_count = 0
    previous_hook = sys.unraisablehook

    def record_unraisable(event):
        nonlocal unraisable_count
        unraisable_count += 1
        previous_hook(event)

    sys.unraisablehook = record_unraisable
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ResourceWarning)
            result = unittest.TextTestRunner(verbosity=2).run(suite)
            gc.collect()
    finally:
        sys.unraisablehook = previous_hook
    successful = (result.wasSuccessful() and not unraisable_count
                  and not (require_no_skips and result.skipped) and result.testsRun > 0)
    record = {
        "test_methods": result.testsRun, "failures": len(result.failures),
        "errors": len(result.errors), "skipped": len(result.skipped),
        "unraisable": unraisable_count, "successful": successful,
    }
    print("INCIDENT_RECHECK_TESTS_JSON=" + json.dumps(record, sort_keys=True, separators=(",", ":")))
    return (0 if successful else 1), record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-no-skips", action="store_true")
    args = parser.parse_args()
    return run_checked(unittest.defaultTestLoader.discover("tests"),
                       require_no_skips=args.require_no_skips)[0]


if __name__ == "__main__":
    raise SystemExit(main())
