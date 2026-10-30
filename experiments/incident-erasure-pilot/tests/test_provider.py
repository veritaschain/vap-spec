"""Actual synthetic namespace and SQLite tests; networking is forbidden."""

import os
import socket
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from erasure_pilot.harness import SYNTHETIC_CONTENT, make_keys, make_task
from erasure_pilot.protocol import (
    EXCLUSIONS, LOCATION, MAX_OBJECT, InputError, canonical, digest, object_name,
    sha256_bytes, utc_now, verify_message, verify_record,
)
from erasure_pilot.provider import LocalProvider, ProviderError


class BeforeFinishFailure(LocalProvider):
    def _finish(self, request_id, state, result):
        raise OSError("synthetic result persistence failure")


class AfterFinishFailure(LocalProvider):
    def _finish(self, request_id, state, result):
        super()._finish(request_id, state, result)
        raise OSError("synthetic result acknowledgement loss")


class ProviderTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="erasure-provider-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "provider"
        self.keys, self.pins = make_keys()
        self.at = utc_now()
        guard = patch.object(socket, "socket", side_effect=AssertionError("Provider tests cannot open sockets"))
        guard.start()
        self.addCleanup(guard.stop)

    def provider(self, cls=LocalProvider, root=None):
        return cls(self.root if root is None else root, self.pins, self.keys["provider"]["secret"], clock=lambda: self.at)

    def case(self, cls=LocalProvider, root=None):
        provider = self.provider(cls=cls, root=root)
        manifest = provider.create("object-synthetic", "version-one", SYNTHETIC_CONTENT)
        task = make_task(manifest, self.keys, self.pins, at=self.at)
        return provider, manifest, task

    def assert_no_completion(self, result, state, attempted=False):
        self.assertEqual(result["state"], state)
        self.assertIs(result["attempted"], attempted)
        self.assertIsNone(result["attestation"])
        self.assertIsNone(result["receipt"])

    def test_real_unlink_requires_committed_intent_and_returns_scoped_evidence(self):
        provider, manifest, task = self.case()
        request_id = task["request"]["body"]["binding"]["request_id"]
        self.assertEqual(provider.inspect(manifest), {"state": "PRESENT", "sha256": sha256_bytes(SYNTHETIC_CONTENT),
                                                       "byte_length": len(SYNTHETIC_CONTENT)})
        calls = []

        def before():
            calls.append(True)
            row = provider.get(request_id)
            self.assertEqual(row["state"], "deletion_intent")
            self.assertIsNone(row["result"])
            self.assertEqual(row["snapshot"], task)
            self.assertEqual(row["fingerprint"], digest(task))
            self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")
            with closing(provider._connect()) as connection:
                self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0], "wal")
                self.assertEqual(connection.execute("PRAGMA synchronous").fetchone()[0], 2)

        result = provider.delete(task, before_unlink=before)
        self.assertEqual(result["state"], "LOCAL_UNLINK_CONFIRMED")
        self.assertTrue(result["attempted"])
        self.assertEqual(result["journal_state"], result["state"])
        self.assertEqual(calls, [True])
        self.assertEqual(provider.inspect(manifest), {"state": "ABSENT", "sha256": None, "byte_length": None})
        ack = verify_record(result["acknowledgement"], provider.public_key, provider.key_id, "erasure.acknowledgement")
        attestation = verify_record(result["attestation"], provider.public_key, provider.key_id, "erasure.provider_attestation")
        receipt = verify_message(result["receipt"], provider.public_key, provider.key_id, "local_unlink_receipt")
        self.assertEqual(ack["binding"], task["request"]["body"]["binding"])
        self.assertEqual(ack["data"]["queue_state"], "received")
        self.assertEqual(attestation["data"]["locations"], [LOCATION])
        self.assertEqual(attestation["data"]["exclusions"], EXCLUSIONS)
        self.assertEqual(attestation["data"]["completed_at"], receipt["observed_at"])
        self.assertEqual(set(receipt), {"kind", "task_sha256", "request_id", "manifest_sha256", "before",
                                       "unlinked_at", "observed_at", "after"})
        self.assertEqual(receipt["task_sha256"], digest(task))
        self.assertEqual(receipt["before"], {"sha256": manifest["sha256"], "byte_length": manifest["byte_length"]})
        self.assertEqual(receipt["after"], "ABSENT")
        exported = canonical({"result": result, "row": provider.get(request_id)})
        self.assertNotIn(SYNTHETIC_CONTENT, exported)
        for key in self.keys.values():
            self.assertNotIn(key["secret"].encode(), exported)

    def test_creation_is_exclusive_immutable_bounded_and_versioned(self):
        provider, first, task = self.case()
        second = provider.create(first["object_id"], "version-two", SYNTHETIC_CONTENT + b"SECOND VERSION")
        self.assertNotEqual(object_name(first), object_name(second))
        with self.assertRaises(FileExistsError):
            provider.create(first["object_id"], first["version_id"], b"must not replace")
        for object_id, version_id, content in (
            ("../escape", "v1", b"synthetic"), ("object", "../escape", b"synthetic"),
            ("object", "v1", b""), ("object", "v1", bytearray(b"mutable")),
            ("object", "v1", b"x" * (MAX_OBJECT + 1)),
        ):
            with self.subTest(object_id=object_id, length=len(content)), self.assertRaises(InputError):
                provider.create(object_id, version_id, content)
        self.assertEqual(provider.delete(task)["state"], "LOCAL_UNLINK_CONFIRMED")
        self.assertEqual(provider.inspect(second)["state"], "PRESENT")

    def test_provider_key_and_namespace_pins_are_required(self):
        with self.assertRaises(InputError):
            LocalProvider(self.root, self.pins, self.keys["requester"]["secret"])
        provider, manifest, task = self.case()
        for field, value in (("tenant_id", "other-tenant"), ("provider_id", "other-provider"), ("location", "backups")):
            changed = {**manifest, field: value}
            other_task = make_task(changed, self.keys, self.pins, at=self.at)
            with self.subTest(field=field), self.assertRaises(InputError):
                provider.delete(other_task)
            with self.subTest(inspect=field), self.assertRaises(InputError):
                provider.inspect(changed)
        unsigned = deepcopy(task)
        unsigned["authorization"]["body"]["valid_until"] = self.pins["keys"][provider.key_id]["not_after"]
        with self.assertRaises(InputError):
            provider.delete(unsigned)
        self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")

    def test_integral_float_length_is_rejected_before_canonical_capture(self):
        provider, manifest, task = self.case()
        floating = deepcopy(task)
        floating["manifest"]["byte_length"] = float(manifest["byte_length"])
        self.assertEqual(digest(floating), digest(task))
        with self.assertRaises(InputError):
            provider.delete(floating)
        with self.assertRaises(InputError):
            provider.inspect(floating["manifest"])
        self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")
        self.assertIsNone(provider.get(task["request"]["body"]["binding"]["request_id"]))

    def test_acknowledgement_only_does_not_resume_even_after_restart_and_expiry(self):
        provider, manifest, task = self.case()
        result = provider.delete(task, acknowledge_only=True,
                                 before_unlink=lambda: self.fail("Acknowledgement-only called unlink hook"))
        self.assert_no_completion(result, "ACKNOWLEDGED_ONLY")
        self.assertIsNotNone(result["acknowledgement"])
        self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")
        self.at = task["authorization"]["body"]["valid_until"]
        replay = self.provider().delete(task)
        self.assert_no_completion(replay, "REPLAY_NO_ACTION")
        self.assertIsNone(replay["acknowledgement"])
        self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")

    def test_expiry_blocks_initial_and_final_action_without_unlink(self):
        for index, final in enumerate((False, True)):
            with self.subTest(final=final):
                self.at = utc_now()
                provider, manifest, task = self.case(root=Path(self.directory.name) / ("expiry-" + str(index)))
                expiry = task["authorization"]["body"]["valid_until"]
                hook = None
                if final:
                    hook = lambda: setattr(self, "at", expiry)
                else:
                    self.at = expiry
                with patch.object(os, "unlink", wraps=os.unlink) as unlink:
                    result = provider.delete(task, before_unlink=hook)
                    self.assertEqual(unlink.call_count, 0)
                self.assert_no_completion(result, "BLOCKED")
                self.assertEqual(result["acknowledgement"] is not None, final)
                self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")

    def test_missing_changed_symlink_and_nonregular_targets_are_refused(self):
        outside = Path(self.directory.name) / "outside-synthetic"
        outside.write_bytes(SYNTHETIC_CONTENT)
        for index, change in enumerate(("missing", "changed", "symlink", "fifo")):
            with self.subTest(change=change):
                provider, manifest, task = self.case(root=Path(self.directory.name) / ("target-" + str(index)))
                path = provider.namespace_root / object_name(manifest)
                path.unlink()
                if change == "changed":
                    path.write_bytes(b"different synthetic bytes")
                elif change == "symlink":
                    path.symlink_to(outside)
                elif change == "fifo":
                    os.mkfifo(path, 0o600)
                with patch.object(os, "unlink", wraps=os.unlink) as unlink:
                    result = provider.delete(task)
                    self.assertEqual(unlink.call_count, 0)
                self.assert_no_completion(result, "BLOCKED")
                self.assertIsNone(result["acknowledgement"])
                self.assertIsNone(provider.get(task["request"]["body"]["binding"]["request_id"]))
        self.assertEqual(outside.read_bytes(), SYNTHETIC_CONTENT)

    def test_identical_bytes_on_a_replaced_inode_are_not_deleted(self):
        provider, manifest, task = self.case()
        path = provider.namespace_root / object_name(manifest)
        retained = Path(self.directory.name) / "retained-synthetic"

        def replace():
            path.rename(retained)
            path.write_bytes(SYNTHETIC_CONTENT)

        result = provider.delete(task, before_unlink=replace)
        self.assert_no_completion(result, "BLOCKED")
        self.assertIsNotNone(result["acknowledgement"])
        self.assertEqual(path.read_bytes(), SYNTHETIC_CONTENT)
        self.assertEqual(retained.read_bytes(), SYNTHETIC_CONTENT)

    def test_in_place_change_after_final_read_is_not_unlinked(self):
        provider, manifest, task = self.case()
        path = provider.namespace_root / object_name(manifest)
        changed = b"X" + SYNTHETIC_CONTENT[1:]
        final_read, mutated = [], []

        def before():
            measure = provider._measure

            def observe_read(directory_fd, name):
                result = measure(directory_fd, name)
                final_read.append(True)
                return result

            def final_clock():
                if final_read and not mutated:
                    path.chmod(0o600)
                    path.write_bytes(changed)
                    mutated.append(True)
                return self.at

            provider._measure = observe_read
            provider.clock = final_clock

        with patch.object(os, "unlink", wraps=os.unlink) as unlink:
            result = provider.delete(task, before_unlink=before)
            self.assertEqual(unlink.call_count, 0)
        self.assertEqual(mutated, [True])
        self.assert_no_completion(result, "BLOCKED")
        self.assertIsNotNone(result["acknowledgement"])
        self.assertEqual(path.read_bytes(), changed)

    def test_same_request_identifier_for_another_version_conflicts(self):
        provider, manifest, task = self.case()
        request_id = task["request"]["body"]["binding"]["request_id"]
        self.assertEqual(provider.delete(task)["state"], "LOCAL_UNLINK_CONFIRMED")
        second = provider.create(manifest["object_id"], "version-two", SYNTHETIC_CONTENT)
        other = make_task(second, self.keys, self.pins, request_id=request_id, at=self.at)
        result = self.provider().delete(other)
        self.assert_no_completion(result, "REQUEST_ID_CONFLICT")
        self.assertIsNone(result["acknowledgement"])
        self.assertEqual(provider.inspect(second)["state"], "PRESENT")

    def test_concurrent_requests_enter_exactly_one_unlink(self):
        provider, manifest, task = self.case()
        entered, release = threading.Event(), threading.Event()

        def wait():
            entered.set()
            if not release.wait(5):
                raise AssertionError("Controlled deletion release timed out")

        with patch.object(os, "unlink", wraps=os.unlink) as unlink:
            with ThreadPoolExecutor(max_workers=6) as executor:
                first = executor.submit(provider.delete, task, before_unlink=wait)
                self.assertTrue(entered.wait(5))
                others = [executor.submit(provider.delete, task) for _ in range(5)]
                try:
                    replays = [future.result(timeout=5) for future in others]
                finally:
                    release.set()
                result = first.result(timeout=5)
            self.assertEqual(unlink.call_count, 1)
        self.assertEqual(result["state"], "LOCAL_UNLINK_CONFIRMED")
        self.assertTrue(all(row["state"] == "REPLAY_NO_ACTION" and not row["attempted"] for row in replays))
        self.assertEqual(provider.inspect(manifest)["state"], "ABSENT")

    def test_completed_racing_request_is_resolved_after_initial_absence(self):
        interleaved = []

        class RacingRead(LocalProvider):
            ready = False

            def get(self, request_id):
                row = super().get(request_id)
                if self.ready and row is None:
                    self.ready = False
                    interleaved.append(other.delete(task))
                return row

        provider, manifest, task = self.case(cls=RacingRead)
        other = self.provider()
        provider.ready = True
        with patch.object(os, "unlink", wraps=os.unlink) as unlink:
            result = provider.delete(task)
            self.assertEqual(unlink.call_count, 1)
        self.assertEqual(interleaved[0]["state"], "LOCAL_UNLINK_CONFIRMED")
        self.assert_no_completion(result, "REPLAY_NO_ACTION")
        self.assertIsNone(result["acknowledgement"])
        self.assertEqual(provider.inspect(manifest)["state"], "ABSENT")

    def test_before_and_after_unlink_failures_keep_attempt_and_never_retry(self):
        for index, hook in enumerate(("before_unlink", "after_unlink")):
            with self.subTest(hook=hook):
                root = Path(self.directory.name) / ("hook-" + str(index))
                provider, manifest, task = self.case(root=root)

                def fail():
                    raise OSError("private diagnostic " + self.keys["provider"]["secret"])

                result = provider.delete(task, **{hook: fail})
                self.assert_no_completion(result, "OUTCOME_UNKNOWN", attempted=hook == "after_unlink")
                self.assertIsNotNone(result["acknowledgement"])
                self.assertEqual(provider.inspect(manifest)["state"], "ABSENT" if hook == "after_unlink" else "PRESENT")
                self.assertNotIn(self.keys["provider"]["secret"].encode(), canonical(result))
                replay = self.provider(root=root).delete(task)
                self.assert_no_completion(replay, "REPLAY_NO_ACTION")

    def test_interruption_before_and_after_unlink_is_one_shot_after_restart(self):
        for index, hook in enumerate(("before_unlink", "after_unlink")):
            with self.subTest(hook=hook):
                root = Path(self.directory.name) / ("interruption-" + str(index))
                provider, manifest, task = self.case(root=root)

                def interrupt():
                    raise KeyboardInterrupt("trusted harness interruption")

                with self.assertRaises(KeyboardInterrupt):
                    provider.delete(task, **{hook: interrupt})
                request_id = task["request"]["body"]["binding"]["request_id"]
                self.assertEqual(provider.get(request_id)["state"], "deletion_intent")
                result = self.provider(root=root).delete(task)
                self.assert_no_completion(result, "REPLAY_NO_ACTION")
                self.assertEqual(provider.inspect(manifest)["state"], "ABSENT" if hook == "after_unlink" else "PRESENT")

    def test_claim_acknowledgement_failure_blocks_before_unlink(self):
        mutations = (lambda row: None, lambda row: {}, lambda row: {**row, "request_id": "different-request"},
                     lambda row: {**row, "fingerprint": "0" * 64},
                     lambda row: {**row, "claim_status": "REPLAY"},
                     lambda row: {**row, "state": "LOCAL_UNLINK_CONFIRMED"})
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                root = Path(self.directory.name) / ("claim-ack-" + str(index))

                class BrokenClaim(LocalProvider):
                    def _claim(self, request_id, fingerprint, snapshot):
                        return mutate(super()._claim(request_id, fingerprint, snapshot))

                provider, manifest, task = self.case(cls=BrokenClaim, root=root)
                result = provider.delete(task)
                # A coherent REPLAY acknowledgement can only withhold action;
                # all malformed acknowledgements are explicitly blocked.
                self.assertIn(result["state"], {"BLOCKED", "REPLAY_NO_ACTION"})
                self.assertFalse(result["attempted"])
                self.assertIsNone(result["acknowledgement"])
                self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")
                self.assert_no_completion(self.provider(root=root).delete(task), "REPLAY_NO_ACTION")

    def test_committed_claim_with_lost_acknowledgement_cannot_resume(self):
        class LostClaim(LocalProvider):
            def _claim(self, request_id, fingerprint, snapshot):
                super()._claim(request_id, fingerprint, snapshot)
                raise OSError("synthetic post-commit acknowledgement loss")

        provider, manifest, task = self.case(cls=LostClaim)
        result = provider.delete(task)
        self.assert_no_completion(result, "BLOCKED")
        self.assertEqual(result["journal_state"], "deletion_intent")
        self.assert_no_completion(self.provider().delete(task), "REPLAY_NO_ACTION")
        self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")

    def test_result_persistence_failure_discards_completion_without_retry(self):
        for index, cls in enumerate((BeforeFinishFailure, AfterFinishFailure)):
            with self.subTest(fault=cls.__name__):
                root = Path(self.directory.name) / ("finish-" + str(index))
                provider, manifest, task = self.case(cls=cls, root=root)
                result = provider.delete(task)
                self.assert_no_completion(result, "OUTCOME_UNKNOWN", attempted=True)
                self.assertIsNotNone(result["acknowledgement"])
                self.assertEqual(provider.inspect(manifest)["state"], "ABSENT")
                self.assert_no_completion(self.provider(root=root).delete(task), "REPLAY_NO_ACTION")

    def test_malformed_terminal_acknowledgement_discards_completion(self):
        mutations = (lambda row: None, lambda row: {**row, "fingerprint": "0" * 64},
                     lambda row: {**row, "result": {**row["result"], "receipt": None}})
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                root = Path(self.directory.name) / ("finish-ack-" + str(index))

                class BrokenFinish(LocalProvider):
                    def _finish(self, request_id, state, result):
                        return mutate(super()._finish(request_id, state, result))

                provider, manifest, task = self.case(cls=BrokenFinish, root=root)
                result = provider.delete(task)
                self.assert_no_completion(result, "OUTCOME_UNKNOWN", attempted=True)
                self.assertEqual(provider.inspect(manifest)["state"], "ABSENT")
                self.assert_no_completion(self.provider(root=root).delete(task), "REPLAY_NO_ACTION")

    def test_late_clock_signing_or_directory_fsync_failure_is_unknown(self):
        for index, failure in enumerate(("clock", "signing", "fsync")):
            with self.subTest(failure=failure):
                self.at = utc_now()
                provider, manifest, task = self.case(root=Path(self.directory.name) / ("late-" + str(index)))
                if failure == "clock":
                    result = provider.delete(task, after_unlink=lambda: setattr(self, "at", "invalid-time"))
                elif failure == "signing":
                    with patch("erasure_pilot.provider.sign_message", side_effect=OSError("synthetic signing failure")):
                        result = provider.delete(task)
                else:
                    with patch.object(os, "fsync", side_effect=OSError("synthetic directory sync failure")):
                        result = provider.delete(task)
                self.assert_no_completion(result, "OUTCOME_UNKNOWN", attempted=True)
                self.assertIsNotNone(result["acknowledgement"])
                self.assertEqual(provider.inspect(manifest)["state"], "ABSENT")

    def test_recreated_entry_withholds_completion_and_replay_does_not_remove_it(self):
        provider, manifest, task = self.case()

        def recreate():
            provider.create(manifest["object_id"], manifest["version_id"], SYNTHETIC_CONTENT)

        result = provider.delete(task, after_unlink=recreate)
        self.assert_no_completion(result, "OUTCOME_UNKNOWN", attempted=True)
        self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")
        self.assert_no_completion(self.provider().delete(task), "REPLAY_NO_ACTION")
        self.assertEqual(provider.inspect(manifest)["state"], "PRESENT")

    def test_controller_directories_and_journal_refuse_symlinks(self):
        outside = Path(self.directory.name) / "outside"
        outside.mkdir(mode=0o700)
        for name in ("namespace", "journal.sqlite3"):
            with self.subTest(name=name):
                root = Path(self.directory.name) / ("symlink-" + name.replace(".", "-"))
                root.mkdir(mode=0o700)
                target = outside
                if name == "journal.sqlite3":
                    target = outside / "untouched"
                    target.write_bytes(b"synthetic sentinel")
                (root / name).symlink_to(target)
                with self.assertRaises((InputError, ProviderError, OSError)):
                    self.provider(root=root)
                if name == "journal.sqlite3":
                    self.assertEqual(target.read_bytes(), b"synthetic sentinel")


if __name__ == "__main__":
    unittest.main()
