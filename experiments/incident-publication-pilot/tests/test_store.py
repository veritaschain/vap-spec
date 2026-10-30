"""Actual local filesystem publication tests; sockets are forbidden."""

import os
import socket
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from publication_pilot.protocol import InputError, canonical, digest, sha256_bytes, verify_message
from publication_pilot.store import LocalPublisher, StoreError


HTML = b'<!doctype html><html><body><p>SYNTHETIC ONLY</p><aside>Simulated AI use disclosed.</aside></body></html>'
DISCLOSURE = sha256_bytes(b"Simulated AI use disclosed.")
FINGERPRINT = digest({"synthetic": "candidate-and-policy-binding"})
REQUEST = "synthetic-request-001"


class BeforeFinishFailure(LocalPublisher):
    def _finish(self, request_id, state, result):
        raise OSError("synthetic result persistence failure")


class AfterFinishFailure(LocalPublisher):
    def _finish(self, request_id, state, result):
        super()._finish(request_id, state, result)
        raise OSError("synthetic result acknowledgement loss")


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="publication-store-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "store"
        self.secret = Ed25519PrivateKey.generate().private_bytes_raw().hex()
        self.key_id, self.destination = "synthetic-publisher", "synthetic-local-destination"
        guard = patch.object(socket, "socket", side_effect=AssertionError("Store tests cannot open sockets"))
        guard.start()
        self.addCleanup(guard.stop)

    def publisher(self, cls=LocalPublisher, root=None):
        return cls(self.root if root is None else root, self.destination, self.secret, self.key_id)

    def test_actual_file_is_measured_after_committed_intent_and_signed(self):
        publisher = self.publisher()
        callback_calls = []

        def final_gate():
            callback_calls.append(True)
            row = publisher.get(REQUEST)
            self.assertEqual(row["state"], "publication_intent")
            self.assertIsNone(row["result"])
            self.assertEqual(row["snapshot"]["artifact_sha256"], sha256_bytes(HTML))
            self.assertEqual(publisher.inspect()["visible_count"], 0)
            stages = list(publisher.private_root.iterdir())
            self.assertEqual(len(stages), 1)
            self.assertEqual(stages[0].read_bytes(), HTML)
            with closing(publisher._connect()) as connection:
                self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0], "wal")
                self.assertEqual(connection.execute("PRAGMA synchronous").fetchone()[0], 2)
            return True

        result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE, before_link=final_gate)
        self.assertEqual(result["state"], "LOCAL_OUTPUT_CONFIRMED")
        self.assertTrue(result["attempted"])
        self.assertEqual(callback_calls, [True])
        self.assertEqual(result["visible_name"], sha256_bytes(REQUEST.encode()) + ".html")
        visible = publisher.visible_root / result["visible_name"]
        self.assertEqual(visible.read_bytes(), HTML)
        body = verify_message(result["receipt"], publisher.public_key, self.key_id, "local_publication_receipt")
        self.assertEqual(set(body), {"kind", "request_id", "fingerprint", "artifact_sha256", "disclosure_sha256",
                                     "byte_length", "destination_id", "visible_name", "observed_at"})
        self.assertEqual(body["artifact_sha256"], sha256_bytes(HTML))
        self.assertEqual(body["disclosure_sha256"], DISCLOSURE)
        self.assertEqual(body["byte_length"], len(HTML))
        self.assertEqual(publisher.inspect(), {"visible_count": 1, "files": {
            result["visible_name"]: {"sha256": sha256_bytes(HTML), "byte_length": len(HTML)}}})
        self.assertEqual(list(publisher.private_root.iterdir()), [])
        self.assertNotIn(self.secret.encode(), canonical(result))
        stored = canonical(publisher.get(REQUEST))
        self.assertNotIn(self.secret.encode(), stored)
        self.assertNotIn(HTML, stored)

    def test_immutable_bytes_and_safe_identifiers_are_required(self):
        publisher = self.publisher()
        for request, fingerprint, payload, disclosure in (
            (REQUEST, FINGERPRINT, bytearray(HTML), DISCLOSURE),
            ("../escape", FINGERPRINT, HTML, DISCLOSURE),
            (REQUEST, "not-a-digest", HTML, DISCLOSURE),
            (REQUEST, FINGERPRINT, HTML, "0" * 63),
            (REQUEST, FINGERPRINT, b"x" * (1024 * 1024 + 1), DISCLOSURE),
        ):
            with self.subTest(request=request, size=len(payload)), self.assertRaises(InputError):
                publisher.publish(request, fingerprint, payload, disclosure)
        self.assertEqual(publisher.inspect()["visible_count"], 0)
        self.assertIsNone(publisher.get(REQUEST))

    def test_final_false_blocks_after_claim_and_replay_never_rechecks(self):
        publisher = self.publisher()
        result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE, before_link=lambda: False)
        self.assertEqual(result["state"], "BLOCKED_WITHOUT_PUBLICATION")
        self.assertFalse(result["attempted"])
        self.assertEqual(publisher.get(REQUEST)["state"], "blocked_after_intent")
        self.assertEqual(publisher.inspect()["visible_count"], 0)
        replay = self.publisher().publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE,
                                          before_link=lambda: self.fail("Replay invoked final gate"))
        self.assertEqual(replay["state"], "REPLAY_NO_PUBLICATION")
        self.assertIsNone(replay["receipt"])

    def test_before_link_exception_leaves_unknown_without_atomic_attempt(self):
        publisher = self.publisher()

        def fail():
            raise OSError("fault containing private diagnostic " + self.secret)

        result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE, before_link=fail)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertFalse(result["attempted"])
        self.assertEqual(publisher.inspect()["visible_count"], 0)
        self.assertNotIn(self.secret.encode(), canonical(result))
        self.assertEqual(self.publisher().publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)["state"], "REPLAY_NO_PUBLICATION")

    def test_after_link_exception_preserves_visible_output_without_receipt(self):
        publisher = self.publisher()

        def fail():
            self.assertEqual(publisher.inspect()["visible_count"], 1)
            self.assertEqual(publisher.get(REQUEST)["state"], "publication_intent")
            raise OSError("synthetic post-link failure")

        result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE, after_link=fail)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertTrue(result["attempted"])
        self.assertIsNone(result["receipt"])
        self.assertEqual(publisher.inspect()["visible_count"], 1)
        replay = self.publisher().publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
        self.assertEqual(replay["state"], "REPLAY_NO_PUBLICATION")
        self.assertIsNone(replay["receipt"])
        self.assertEqual((publisher.visible_root / result["visible_name"]).read_bytes(), HTML)

    def test_concurrent_calls_publish_exactly_one_file(self):
        publisher = self.publisher()
        entered, release = threading.Event(), threading.Event()

        def wait():
            entered.set()
            if not release.wait(5):
                raise AssertionError("Controlled publication release timed out")
            return True

        with patch.object(os, "link", wraps=os.link) as atomic_link:
            with ThreadPoolExecutor(max_workers=6) as executor:
                first = executor.submit(publisher.publish, REQUEST, FINGERPRINT, HTML, DISCLOSURE, before_link=wait)
                self.assertTrue(entered.wait(5))
                others = [executor.submit(publisher.publish, REQUEST, FINGERPRINT, HTML, DISCLOSURE) for _ in range(5)]
                try:
                    replays = [future.result(timeout=5) for future in others]
                finally:
                    release.set()
                initial = first.result(timeout=5)
            self.assertEqual(atomic_link.call_count, 1)
        self.assertEqual(initial["state"], "LOCAL_OUTPUT_CONFIRMED")
        self.assertTrue(all(r["state"] == "REPLAY_NO_PUBLICATION" and not r["attempted"] for r in replays))
        self.assertEqual(publisher.inspect()["visible_count"], 1)

    def test_changed_bytes_disclosure_or_fingerprint_conflict_after_claim(self):
        publisher = self.publisher()
        self.assertEqual(publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)["state"], "LOCAL_OUTPUT_CONFIRMED")
        for fingerprint, payload, disclosure in (
            (FINGERPRINT, HTML + b"changed", DISCLOSURE),
            (FINGERPRINT, HTML, sha256_bytes(b"changed disclosure")),
            (digest({"new": "authorization"}), HTML, DISCLOSURE),
        ):
            with self.subTest(payload_length=len(payload), disclosure=disclosure):
                result = self.publisher().publish(REQUEST, fingerprint, payload, disclosure)
                self.assertEqual(result["state"], "REQUEST_ID_CONFLICT")
                self.assertFalse(result["attempted"])
                self.assertIsNone(result["receipt"])
        self.assertEqual(publisher.inspect()["visible_count"], 1)

    def test_preexisting_visible_names_are_never_replaced_or_adopted(self):
        for index, existing in enumerate((b"existing different file", HTML)):
            with self.subTest(identical=existing == HTML):
                publisher = self.publisher(root=Path(self.directory.name) / ("collision-" + str(index)))
                name = sha256_bytes(REQUEST.encode()) + ".html"
                (publisher.visible_root / name).write_bytes(existing)
                result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
                self.assertEqual(result["state"], "BLOCKED_WITHOUT_PUBLICATION")
                self.assertTrue(result["attempted"])
                self.assertEqual(result["reason"], "VISIBLE_NAME_ALREADY_EXISTS")
                self.assertIsNone(result["receipt"])
                self.assertEqual((publisher.visible_root / name).read_bytes(), existing)

    def test_interruption_before_or_after_link_survives_restart(self):
        for index, when in enumerate(("before_link", "after_link")):
            with self.subTest(when=when):
                root = Path(self.directory.name) / ("interrupted-" + str(index))
                publisher = self.publisher(root=root)

                def interrupt():
                    raise KeyboardInterrupt("trusted harness interruption")

                with self.assertRaises(KeyboardInterrupt):
                    publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE, **{when: interrupt})
                self.assertEqual(publisher.get(REQUEST)["state"], "publication_intent")
                expected_count = 0 if when == "before_link" else 1
                self.assertEqual(publisher.inspect()["visible_count"], expected_count)
                restarted = self.publisher(root=root)
                replay = restarted.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
                self.assertEqual(replay["state"], "REPLAY_NO_PUBLICATION")
                self.assertFalse(replay["attempted"])
                self.assertIsNone(replay["receipt"])
                self.assertEqual(restarted.inspect()["visible_count"], expected_count)

    def test_result_persistence_failures_discard_confirmation_and_never_retry(self):
        for index, cls in enumerate((BeforeFinishFailure, AfterFinishFailure)):
            with self.subTest(failure=cls.__name__):
                root = Path(self.directory.name) / ("persistence-" + str(index))
                publisher = self.publisher(cls=cls, root=root)
                result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
                self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
                self.assertTrue(result["attempted"])
                self.assertIsNone(result["receipt"])
                self.assertEqual(publisher.inspect()["visible_count"], 1)
                replay = self.publisher(root=root).publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
                self.assertEqual(replay["state"], "REPLAY_NO_PUBLICATION")
                self.assertIsNone(replay["receipt"])

    def test_missing_or_mismatched_claim_acknowledgements_do_not_publish(self):
        variants = (
            lambda row: None,
            lambda row: {},
            lambda row: {**row, "request_id": "other-request"},
            lambda row: {**row, "state": "local_output_confirmed"},
            lambda row: {**row, "fingerprint": "0" * 64},
            lambda row: {**row, "snapshot": {**row["snapshot"], "byte_length": 0}},
        )
        for index, mutation in enumerate(variants):
            with self.subTest(index=index):
                root = Path(self.directory.name) / ("ack-" + str(index))

                class MalformedClaim(LocalPublisher):
                    def _claim(self, request_id, fingerprint, snapshot):
                        return mutation(super()._claim(request_id, fingerprint, snapshot))

                publisher = self.publisher(cls=MalformedClaim, root=root)
                result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
                self.assertEqual(result["state"], "BLOCKED_WITHOUT_PUBLICATION")
                self.assertFalse(result["attempted"])
                self.assertEqual(publisher.inspect()["visible_count"], 0)
                self.assertEqual(self.publisher(root=root).publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)["state"],
                                 "REPLAY_NO_PUBLICATION")

    def test_post_commit_claim_acknowledgement_loss_does_not_retry(self):
        class LostClaimAcknowledgement(LocalPublisher):
            def _claim(self, request_id, fingerprint, snapshot):
                super()._claim(request_id, fingerprint, snapshot)
                raise OSError("synthetic acknowledgement loss after commit")

        publisher = self.publisher(cls=LostClaimAcknowledgement)
        result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
        self.assertFalse(result["attempted"])
        self.assertEqual(publisher.get(REQUEST)["state"], "publication_intent")
        self.assertEqual(self.publisher().publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)["state"], "REPLAY_NO_PUBLICATION")
        self.assertEqual(publisher.inspect()["visible_count"], 0)

    def test_malformed_result_acknowledgements_discard_confirmation(self):
        variants = (
            lambda row: None,
            lambda row: {**row, "state": "publication_intent"},
            lambda row: {**row, "snapshot": {**row["snapshot"], "disclosure_sha256": "0" * 64}},
            lambda row: {**row, "result": {**row["result"], "receipt": None}},
        )
        for index, mutation in enumerate(variants):
            with self.subTest(index=index):
                root = Path(self.directory.name) / ("result-ack-" + str(index))

                class MalformedFinish(LocalPublisher):
                    def _finish(self, request_id, state, result):
                        return mutation(super()._finish(request_id, state, result))

                publisher = self.publisher(cls=MalformedFinish, root=root)
                result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
                self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
                self.assertTrue(result["attempted"])
                self.assertIsNone(result["receipt"])
                self.assertEqual(publisher.inspect()["visible_count"], 1)
                replay = self.publisher(root=root).publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
                self.assertEqual(replay["state"], "REPLAY_NO_PUBLICATION")
                self.assertIsNone(replay["receipt"])

    def test_replaced_file_after_link_is_not_confirmed_or_deleted(self):
        publisher = self.publisher()
        name = sha256_bytes(REQUEST.encode()) + ".html"

        def replace():
            visible = publisher.visible_root / name
            visible.unlink()
            visible.write_bytes(b"changed by trusted fault hook")

        result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE, after_link=replace)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertTrue(result["attempted"])
        self.assertIsNone(result["receipt"])
        self.assertEqual((publisher.visible_root / name).read_bytes(), b"changed by trusted fault hook")

    def test_visible_directory_fsync_failure_is_unknown_after_link(self):
        publisher = self.publisher()
        identity = publisher.visible_root.stat()
        original = os.fsync

        def fail_visible(descriptor):
            info = os.fstat(descriptor)
            if (info.st_dev, info.st_ino) == (identity.st_dev, identity.st_ino):
                raise OSError("synthetic visible directory synchronization failure")
            return original(descriptor)

        with patch.object(os, "fsync", fail_visible):
            result = publisher.publish(REQUEST, FINGERPRINT, HTML, DISCLOSURE)
        self.assertEqual(result["state"], "OUTCOME_UNKNOWN")
        self.assertIsNone(result["receipt"])
        self.assertEqual(publisher.inspect()["visible_count"], 1)

    def test_control_directories_and_journal_reject_symlinks(self):
        outside = Path(self.directory.name) / "outside"
        outside.mkdir()
        for name in ("private", "visible", "journal.sqlite3"):
            with self.subTest(name=name):
                root = Path(self.directory.name) / ("symlink-" + name.replace(".", "-"))
                root.mkdir()
                target = outside
                if name == "journal.sqlite3":
                    target = outside / "untouched-file"
                    target.write_bytes(b"must remain unchanged")
                (root / name).symlink_to(target)
                with self.assertRaises((InputError, OSError)):
                    self.publisher(root=root)
                if name == "journal.sqlite3":
                    self.assertEqual(target.read_bytes(), b"must remain unchanged")

    def test_inspection_never_follows_a_visible_symlink(self):
        publisher = self.publisher()
        outside = Path(self.directory.name) / "outside-data"
        outside.write_bytes(b"outside synthetic content")
        (publisher.visible_root / (sha256_bytes(REQUEST.encode()) + ".html")).symlink_to(outside)
        with self.assertRaises((StoreError, OSError)):
            publisher.inspect()
        self.assertEqual(outside.read_bytes(), b"outside synthetic content")


if __name__ == "__main__":
    unittest.main()
