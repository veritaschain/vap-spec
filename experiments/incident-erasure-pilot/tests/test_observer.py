import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from erasure_pilot.harness import make_case
from erasure_pilot.observer import LocalObserver
from erasure_pilot.protocol import InputError, decode_json, object_name


class ObserverTests(unittest.TestCase):
    def test_owned_readback_records_actual_changed_bytes(self):
        with TemporaryDirectory() as directory:
            case = make_case(Path(directory) / "provider")
            path = case["provider"].namespace_root / object_name(case["manifest"])
            path.chmod(0o600)
            path.write_bytes(b"Changed synthetic input")
            observation = case["observer"].observe(case["task"], "before")["body"]
            self.assertEqual(observation["measurement"]["state"], "PRESENT")
            self.assertEqual(observation["measurement"]["byte_length"], 23)
            self.assertNotEqual(observation["measurement"]["sha256"], case["manifest"]["sha256"])

    def test_observer_does_not_follow_file_symlink_or_read_fifo(self):
        with TemporaryDirectory() as directory:
            case = make_case(Path(directory) / "provider")
            path = case["provider"].namespace_root / object_name(case["manifest"])
            path.unlink()
            other = Path(directory) / "outside"
            other.write_bytes(b"outside synthetic bytes")
            path.symlink_to(other)
            with self.assertRaises(InputError):
                case["observer"].observe(case["task"], "before")
            path.unlink()
            os.mkfifo(path, 0o600)
            with self.assertRaises(InputError):
                case["observer"].observe(case["task"], "before")
            self.assertEqual(other.read_bytes(), b"outside synthetic bytes")

    def test_replaced_root_is_not_misreported_as_absent(self):
        with TemporaryDirectory() as directory:
            case = make_case(Path(directory) / "provider")
            original = case["provider"].namespace_root
            original.rename(original.with_name("old-namespace"))
            original.mkdir(mode=0o700)
            with self.assertRaises(InputError):
                case["observer"].observe(case["task"], "before")

    def test_strict_json_and_malformed_observer_task_are_rejected(self):
        for raw in (b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":2.0}', b'"\\ud800"', b'"\xff"'):
            with self.subTest(raw=raw), self.assertRaises(InputError):
                decode_json(raw)
        with TemporaryDirectory() as directory:
            case = make_case(Path(directory) / "provider")
            with self.assertRaises(InputError):
                case["observer"].observe({}, "before")
            with self.assertRaises(InputError):
                LocalObserver(case["provider"].namespace_root, case["pins"], "00" * 32)


if __name__ == "__main__":
    unittest.main()
