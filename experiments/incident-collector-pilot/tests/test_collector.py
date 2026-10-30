"""Focused protocol and real process/HTTP persistence checks; no simulated RPCs."""

import hashlib
import json
import secrets
import sqlite3
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from contextlib import ExitStack, closing
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit

import collector_pilot  # Establish the pinned sibling import paths first.
from upload_pilot.protocol import sign_control as old_sign_control
from upload_pilot.transport import _LoopbackHTTPConnection

from collector_pilot.client import CollectorClient
from collector_pilot.collector import CollectorProcess, _connect
from collector_pilot.protocol import (
    MAX_CONTROL, InputError, canonical, capture, collection_id, decode_json, digest,
    public_key, sign_control, timestamp, utc_now, validate_endpoint, validate_intent,
    validate_query, verify_control, verify_receipt, verify_status,
)


PAYLOAD = b"SYNTHETIC-COLLECTOR-TEST-PAYLOAD-NOT-SENT-TO-COLLECTOR"
T0 = "2026-10-30T00:00:00Z"
T1 = "2026-10-30T00:00:01Z"
T2 = "2026-10-30T00:00:02Z"
T3 = "2026-10-30T00:00:03Z"


def keys():
    gateway, collector = secrets.token_hex(32), secrets.token_hex(32)
    return {
        "gateway": gateway, "gateway_public": public_key(gateway),
        "collector": collector, "collector_public": public_key(collector),
    }


def intent(key, request="request-synthetic", at=None):
    return sign_control({
        "kind": "collection_intent", "collector_id": "collector-synthetic",
        "collection_id": collection_id("collector-synthetic", request),
        "request_id": request, "evaluation_id": "evaluation-synthetic",
        "subject_sha256": digest({"synthetic_subject": request}),
        "payload_sha256": hashlib.sha256(PAYLOAD).hexdigest(), "byte_length": len(PAYLOAD),
        "policy_sha256": digest({"synthetic_policy": "requires-collector"}),
        "decision_sha256": digest({"synthetic_permit": request}),
        "created_at": at or utc_now(),
    }, key["gateway"], "gateway-key")


def query(key, original, at=None):
    return sign_control({
        "kind": "collection_query", "collector_id": original["body"]["collector_id"],
        "collection_id": original["body"]["collection_id"],
        "request_id": original["body"]["request_id"], "request_sha256": digest(original),
        "nonce": secrets.token_hex(32), "created_at": at or utc_now(),
    }, key["gateway"], "gateway-key")


def receipt(key, original, at=T1):
    return sign_control({
        "kind": "collection_receipt", "collector_id": original["body"]["collector_id"],
        "collection_id": original["body"]["collection_id"],
        "request_id": original["body"]["request_id"], "request_sha256": digest(original),
        "recorded_at": at, "receipt_id": "receipt-synthetic", "storage": "sqlite-wal-full",
    }, key["collector"], "collector-key")


def status(key, original, requested, saved, at=T2):
    return sign_control({
        "kind": "collection_status", "collector_id": original["body"]["collector_id"],
        "collection_id": original["body"]["collection_id"],
        "request_id": original["body"]["request_id"], "request_sha256": digest(original),
        "query_sha256": digest(requested), "nonce": requested["body"]["nonce"],
        "status": "FOUND" if saved is not None else "NOT_FOUND", "receipt": saved,
        "checked_at": at,
    }, key["collector"], "collector-key")


class ProtocolTests(unittest.TestCase):
    def setUp(self):
        self.key = keys()
        self.intent = intent(self.key, at=T0)

    def test_new_domain_and_owned_results(self):
        original = deepcopy(self.intent)
        parsed = verify_control(self.intent, self.key["gateway_public"], "gateway-key", "collection_intent")
        parsed["request_id"] = "caller-changed"
        self.assertEqual(self.intent, original)
        foreign = old_sign_control(original["body"], self.key["gateway"], "gateway-key")
        with self.assertRaises(InputError):
            verify_control(foreign, self.key["gateway_public"], "gateway-key", "collection_intent")
        with self.assertRaises(InputError):
            verify_control(original, self.key["collector_public"], "gateway-key", "collection_intent")

    def test_exact_schema_and_scalar_types_before_canonicalization(self):
        self.assertEqual(validate_intent(self.intent["body"]), self.intent["body"])
        for value in (True, 1.0, -1, 1024 * 1024 + 1, "1"):
            altered = {**self.intent["body"], "byte_length": value}
            with self.subTest(value=value), self.assertRaises(InputError):
                validate_intent(altered)
        altered = {**self.intent["body"], "payload": "forbidden plaintext"}
        with self.assertRaises(InputError):
            validate_intent(altered)
        for raw in (b'{"a":1,"a":2}', b'{"a":1.0}', b'{"a":NaN}', b'"\xff"'):
            with self.subTest(raw=raw), self.assertRaises(InputError):
                decode_json(raw)
        with self.assertRaises(InputError):
            capture({"byte_length": 1.0})
        requested = query(self.key, self.intent, at=T1)["body"]
        for nonce in ("short", "A" * 64, True):
            with self.subTest(nonce=nonce), self.assertRaises(InputError):
                validate_query({**requested, "nonce": nonce})

    def test_receipt_requires_exact_binding_signature_storage_and_time(self):
        saved = receipt(self.key, self.intent)
        result = verify_receipt(saved, self.intent, self.key["collector_public"], "collector-key", T2)
        self.assertEqual(result, saved["body"])
        mutations = {
            "request_sha256": "0" * 64, "collection_id": "0" * 64,
            "collector_id": "different-collector", "request_id": "different-request",
            "storage": "memory", "recorded_at": T3, "receipt_id": "",
        }
        for field, value in mutations.items():
            bad = sign_control({**saved["body"], field: value}, self.key["collector"], "collector-key")
            with self.subTest(field=field), self.assertRaises(InputError):
                verify_receipt(bad, self.intent, self.key["collector_public"], "collector-key", T2)
        early = receipt(self.key, self.intent, "2026-10-29T23:59:59Z")
        with self.assertRaises(InputError):
            verify_receipt(early, self.intent, self.key["collector_public"], "collector-key", T2)

    def test_status_challenge_and_recorded_time_cannot_be_replayed_or_substituted(self):
        requested, saved = query(self.key, self.intent, at=T1), receipt(self.key, self.intent)
        current = status(self.key, self.intent, requested, saved)
        result = verify_status(current, requested, self.intent, self.key["collector_public"], "collector-key", T3)
        self.assertEqual(result["receipt"], saved)
        self.assertEqual(result["receipt"]["body"]["recorded_at"], T1)
        later_query = query(self.key, self.intent, at=T2)
        with self.assertRaises(InputError):
            verify_status(current, later_query, self.intent, self.key["collector_public"], "collector-key", T3)
        for field, value in {"query_sha256": "0" * 64, "nonce": "0" * 64,
                             "checked_at": T0, "status": "CONFIRMED"}.items():
            altered = sign_control({**current["body"], field: value}, self.key["collector"], "collector-key")
            with self.subTest(field=field), self.assertRaises(InputError):
                verify_status(altered, requested, self.intent, self.key["collector_public"], "collector-key", T3)
        missing = status(self.key, self.intent, requested, None)
        self.assertEqual(verify_status(missing, requested, self.intent, self.key["collector_public"],
                                       "collector-key", T3)["status"], "NOT_FOUND")
        false_missing = sign_control({**missing["body"], "receipt": saved}, self.key["collector"], "collector-key")
        with self.assertRaises(InputError):
            verify_status(false_missing, requested, self.intent, self.key["collector_public"], "collector-key", T3)

    def test_endpoint_is_literal_bounded_and_getter_only(self):
        self.assertEqual(validate_endpoint("http://127.0.0.1:12345"), "http://127.0.0.1:12345")
        for endpoint in ("http://localhost:12345", "https://127.0.0.1:12345", "http://127.0.0.1:0",
                         "http://127.0.0.1:65536", "http://127.0.0.1:0123", "http://[::1]:12345",
                         "http://127.0.0.1:12345/", "http://127.0.0.1:12345?x=1",
                         "http://user@127.0.0.1:12345", "http://127.0.0.1:12345#x"):
            with self.subTest(endpoint=endpoint), self.assertRaises(InputError):
                CollectorClient(endpoint, self.key["collector_public"], "collector-key")
        client = CollectorClient("http://127.0.0.1:12345", self.key["collector_public"], "collector-key")
        with self.assertRaises(AttributeError):
            client.endpoint = "http://127.0.0.1:12346"


class CollectorProcessTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory(prefix="collector-tests-")))
        self.key = keys()
        self.options = {
            "collector_id": "collector-synthetic", "gateway_public": self.key["gateway_public"],
            "gateway_key_id": "gateway-key", "collector_secret": self.key["collector"],
            "collector_key_id": "collector-key",
        }

    def start(self, mode="normal", directory="collector"):
        server = self.stack.enter_context(CollectorProcess(self.root / directory, **self.options, mode=mode))
        client = CollectorClient(server.endpoint, self.key["collector_public"], "collector-key")
        return server, client

    def checked_receipt(self, response, original):
        self.assertEqual(set(response), {"attempted", "attempted_at", "completed_at", "status", "response", "error"})
        self.assertTrue(response["attempted"])
        self.assertEqual(response["status"], 200)
        self.assertIsNone(response["error"])
        self.assertLessEqual(timestamp(response["attempted_at"]), timestamp(response["completed_at"]))
        return verify_receipt(response["response"], original, self.key["collector_public"],
                              "collector-key", response["completed_at"])

    def checked_status(self, response, requested, original):
        self.assertEqual(response["status"], 200)
        self.assertIsNone(response["error"])
        return verify_status(response["response"], requested, original, self.key["collector_public"],
                             "collector-key", response["completed_at"])

    def test_normal_real_http_commits_metadata_only_and_closes_owned_process(self):
        server, client = self.start()
        original = intent(self.key)
        accepted = client.collect(original)
        self.checked_receipt(accepted, original)
        requested = query(self.key, original)
        found = self.checked_status(client.status(requested), requested, original)
        self.assertEqual(found["status"], "FOUND")
        self.assertEqual(found["receipt"], accepted["response"])
        snapshot = server.snapshot()
        self.assertEqual(set(snapshot), {"collect_calls", "status_calls", "accepted_count", "rows"})
        self.assertEqual((snapshot["collect_calls"], snapshot["status_calls"], snapshot["accepted_count"]), (1, 1, 1))
        self.assertEqual(set(snapshot["rows"][0]), {"collection_id", "request_id", "request_sha256", "intent", "receipt"})
        self.assertEqual(snapshot["rows"][0]["intent"], original)
        with closing(_connect(server.directory / "collector.sqlite3")) as connection:
            self.assertEqual(connection.execute("PRAGMA journal_mode").fetchone()[0], "wal")
            self.assertEqual(connection.execute("PRAGMA synchronous").fetchone()[0], 2)
        exported = canonical(snapshot)
        for forbidden in (PAYLOAD, self.key["gateway"].encode(), self.key["collector"].encode()):
            self.assertNotIn(forbidden, exported)
        server.stop()
        self.assertTrue(server.cleanup_result["child_stopped"])
        for path in server.directory.iterdir():
            for forbidden in (PAYLOAD, self.key["gateway"].encode(), self.key["collector"].encode()):
                self.assertNotIn(forbidden, path.read_bytes())

    def test_stopped_server_is_a_real_failed_exchange_and_restart_returns_not_found(self):
        server, client = self.start()
        endpoint, original = server.endpoint, intent(self.key)
        server.stop()
        failed = client.collect(original)
        self.assertTrue(failed["attempted"])
        self.assertIsNone(failed["response"])
        self.assertIsNotNone(failed["error"])
        self.assertEqual(server.snapshot()["collect_calls"], 0)
        server.restart()
        self.assertEqual(server.endpoint, endpoint)
        requested = query(self.key, original)
        missing = self.checked_status(client.status(requested), requested, original)
        self.assertEqual((missing["status"], missing["receipt"]), ("NOT_FOUND", None))
        self.assertEqual(server.snapshot()["accepted_count"], 0)

    def test_precommit_drop_rolls_back_metadata_and_has_no_usable_receipt(self):
        server, client = self.start("drop_before_commit")
        original = intent(self.key)
        failed = client.collect(original)
        self.assertIsNone(failed["response"])
        self.assertIsNotNone(failed["error"])
        self.assertEqual(server.snapshot()["collect_calls"], 1)
        self.assertEqual(server.snapshot()["accepted_count"], 0)
        requested = query(self.key, original)
        missing = self.checked_status(client.status(requested), requested, original)
        self.assertEqual(missing["status"], "NOT_FOUND")

    def test_committed_lost_ack_survives_new_process_and_readonly_reconciliation(self):
        server, client = self.start("drop_after_commit")
        original = intent(self.key)
        failed = client.collect(original)
        self.assertIsNone(failed["response"])
        self.assertIsNotNone(failed["error"])
        saved = server.snapshot()
        self.assertEqual((saved["collect_calls"], saved["accepted_count"]), (1, 1))
        endpoint = server.endpoint
        server.stop()
        replacement, new_client = self.start()
        self.assertEqual(replacement.endpoint, endpoint)
        requested = query(self.key, original)
        found = self.checked_status(new_client.status(requested), requested, original)
        self.assertEqual(found["receipt"], saved["rows"][0]["receipt"])
        after = replacement.snapshot()
        self.assertEqual(after["rows"], saved["rows"])
        self.assertEqual((after["collect_calls"], after["status_calls"], after["accepted_count"]), (1, 1, 1))

    def test_idempotency_conflicts_and_concurrent_calls_preserve_one_stable_row(self):
        server, client = self.start()
        original = intent(self.key)
        with ThreadPoolExecutor(max_workers=4) as executor:
            replies = list(executor.map(client.collect, [original] * 4))
        for reply in replies:
            self.checked_receipt(reply, original)
            self.assertEqual(reply["response"], replies[0]["response"])
        changed = sign_control({**original["body"], "payload_sha256": "0" * 64}, self.key["gateway"], "gateway-key")
        conflict = client.collect(changed)
        self.assertEqual((conflict["status"], conflict["response"]), (409, None))
        requested = query(self.key, changed)
        self.assertEqual(client.status(requested)["status"], 409)
        snapshot = server.snapshot()
        self.assertEqual((snapshot["collect_calls"], snapshot["status_calls"], snapshot["accepted_count"]), (5, 1, 1))
        self.assertEqual(snapshot["rows"][0]["intent"], original)

    def test_wrong_receipt_and_wrong_status_nonce_are_real_signed_negative_controls(self):
        for mode in ("wrong_receipt", "wrong_status_nonce"):
            with self.subTest(mode=mode):
                server, client = self.start(mode, mode)
                original = intent(self.key)
                response = client.collect(original)
                self.assertEqual(response["status"], 200)
                if mode == "wrong_receipt":
                    with self.assertRaises(InputError):
                        self.checked_receipt(response, original)
                else:
                    self.checked_receipt(response, original)
                saved = server.snapshot()["rows"][0]["receipt"]
                verify_receipt(saved, original, self.key["collector_public"], "collector-key", utc_now())
                requested = query(self.key, original)
                readback = client.status(requested)
                if mode == "wrong_status_nonce":
                    with self.assertRaises(InputError):
                        self.checked_status(readback, requested, original)
                else:
                    self.assertEqual(self.checked_status(readback, requested, original)["receipt"], saved)

    def test_persisted_identity_keys_and_endpoint_cannot_change_on_restart(self):
        server, client = self.start()
        original = intent(self.key)
        self.checked_receipt(client.collect(original), original)
        server.stop()
        other = keys()
        for field, value in {
            "collector_id": "other-collector", "gateway_public": other["gateway_public"],
            "gateway_key_id": "other-gateway-key", "collector_secret": other["collector"],
            "collector_key_id": "other-collector-key",
        }.items():
            with self.subTest(field=field), self.assertRaises(InputError):
                with CollectorProcess(server.directory, **{**self.options, field: value}):
                    self.fail("Changed persistence identity was accepted")
        port = urlsplit(server.endpoint).port
        with self.assertRaises(InputError):
            with CollectorProcess(server.directory, **self.options, port=port + 1 if port < 65535 else port - 1):
                self.fail("Changed persistence endpoint was accepted")
        server.restart()
        self.checked_receipt(client.collect(original), original)
        self.assertEqual(server.snapshot()["accepted_count"], 1)

    def test_malformed_signed_requests_are_refused_by_actual_server(self):
        server, client = self.start()
        original = intent(self.key)
        cases = [
            sign_control({**original["body"], "byte_length": True}, self.key["gateway"], "gateway-key"),
            sign_control({**original["body"], "collection_id": "0" * 64}, self.key["gateway"], "gateway-key"),
            sign_control(original["body"], self.key["collector"], "gateway-key"),
            old_sign_control(original["body"], self.key["gateway"], "gateway-key"),
        ]
        for value in cases:
            response = client.collect(value)
            self.assertEqual((response["status"], response["response"]), (400, None))
        self.assertEqual((server.snapshot()["collect_calls"], server.snapshot()["accepted_count"]), (4, 0))

    def test_http_duplicate_headers_oversize_and_integral_float_are_rejected(self):
        server, _ = self.start()
        original = intent(self.key)
        altered = deepcopy(original)
        altered["body"]["byte_length"] = float(altered["body"]["byte_length"])
        self.assertEqual(digest(original), digest(altered))  # Precisely why raw type checks matter.
        requests = [
            (canonical(original), [str(len(canonical(original)))] * 2),
            (b"", [str(MAX_CONTROL + 1)]),
            (json.dumps(altered).encode(), None),
        ]
        for body, lengths in requests:
            connection = _LoopbackHTTPConnection("127.0.0.1", urlsplit(server.endpoint).port, timeout=1.0)
            with closing(connection):
                connection.putrequest("POST", "/collect", skip_host=True, skip_accept_encoding=True)
                connection.putheader("Host", "127.0.0.1:" + str(urlsplit(server.endpoint).port))
                connection.putheader("Content-Type", "application/json")
                connection.putheader("Connection", "close")
                for length in lengths or [str(len(body))]:
                    connection.putheader("Content-Length", length)
                connection.endheaders(body)
                response = connection.getresponse()
                self.assertEqual(response.status, 400)
                response.read(MAX_CONTROL)
        self.assertEqual(server.snapshot()["accepted_count"], 0)


if __name__ == "__main__":
    unittest.main()
