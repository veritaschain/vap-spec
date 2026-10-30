"""File-backed test runner; process/socket tests are required, never skipped."""

import gc
import sys
import unittest
import warnings


def main():
    count = 0
    previous = sys.unraisablehook
    def record(event):
        nonlocal count
        count += 1
        previous(event)
    sys.unraisablehook = record
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ResourceWarning)
            result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.discover("tests"))
            gc.collect()
    finally:
        sys.unraisablehook = previous
    if result.skipped or count:
        print("Required run observed skipped tests or unraisable exceptions", file=sys.stderr)
    return 0 if result.wasSuccessful() and not result.skipped and not count and result.testsRun else 1


if __name__ == "__main__":
    raise SystemExit(main())
