"""Regression for CI success despite an unraisable ResourceWarning."""

from pathlib import Path
import subprocess
import sys
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]


class RunnerTests(unittest.TestCase):
    def invoke(self, body):
        source = "import unittest\nfrom run_tests import run_checked\n" + textwrap.dedent(body)
        return subprocess.run([sys.executable, "-c", source], cwd=ROOT,
                              capture_output=True, text=True, timeout=10)

    def test_clean_suite_passes(self):
        result = self.invoke("""
            def check():
                pass
            raise SystemExit(run_checked(unittest.TestSuite([unittest.FunctionTestCase(check)])))
        """)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Unraisable exceptions observed", result.stderr)

    def test_finalizer_resource_warning_fails_even_if_test_passes(self):
        result = self.invoke("""
            import warnings
            class LeakedResource:
                def __del__(self):
                    warnings.warn("synthetic unclosed resource", ResourceWarning)
            def check():
                resource = LeakedResource()
                resource.cycle = resource
            raise SystemExit(run_checked(unittest.TestSuite([unittest.FunctionTestCase(check)])))
        """)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("Ran 1 test", result.stderr)
        self.assertIn("OK", result.stderr)
        self.assertIn("ResourceWarning: synthetic unclosed resource", result.stderr)
        self.assertIn("Unraisable exceptions observed: 1", result.stderr)


if __name__ == "__main__":
    unittest.main()
