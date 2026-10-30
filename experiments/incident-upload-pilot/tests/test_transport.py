"""Protocol/unit checks plus opt-in real separate-process HTTP checks.

Mocked connections below exercise error classification only; they are never
reported as actual network execution. PILOT_NETWORK_TESTS=1 makes live failures
fatal. A CI run without that explicit opt-in fails a separate guard test.
"""

import base64
import hashlib
import http.client
import io
import os
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch

from upload_pilot.protocol import MAX_CONTROL, MAX_PAYLOAD, InputError, canonical, digest, public_key, sign_control, utc_now, verify_control
from upload_pilot.receiver import ReceiverProcess, _BoundedHeaderReader, _accept, _count_handler, _decode_header, _initialize, _validate_dispatch
from upload_pilot.transport import MAX_AUTH_HEADER, MAX_HEADER_BYTES, HttpTransport, _LoopbackHTTPConnection, checked_headers, content_length


def _keys():
    gateway_secret, receiver_secret = os.urandom(32).hex(), os.urandom(32).hex()
    return {
        "gateway_secret": gateway_secret, "gateway_public": public_key(gateway_secret),
        "gateway_key_id": "test-gateway-key", "receiver_secret": receiver_secret,
        "receiver_public": public_key(receiver_secret), "receiver_key_id": "test-receiver-key",
    }


def _dispatch(payload, keys, request_id="request-transport-test", **updates):
    body = {
        "kind": "dispatch_intent", "request_id": request_id,
        "subject_sha256": digest({"scope": "synthetic-controlled-route"}),
        "payload_sha256": hashlib.sha256(payload).hexdigest(), "byte_length": len(payload),
        "created_at": utc_now(),
    }
    body.update(updates)
    return sign_control(body, keys["gateway_secret"], keys["gateway_key_id"])


def _header(envelope):
    return base64.b64encode(canonical(envelope)).decode("ascii")


def _receiver(directory, keys, mode="normal"):
    return ReceiverProcess(directory, gateway_public=keys["gateway_public"], gateway_key_id=keys["gateway_key_id"],
                           receiver_secret=keys["receiver_secret"], receiver_key_id=keys["receiver_key_id"], mode=mode)


class _ResponseDouble:
    """No socket activity: only a bounded fake response for parser unit tests."""
    def __init__(self, raw=b'{}', status=200, headers=None):
        self.raw, self.status = raw, status
        self.headers = headers if headers is not None else [("Content-Type", "application/json"), ("Content-Length", str(len(raw)))]

    def getheaders(self):
        return self.headers

    def read(self, amount):
        return self.raw[:amount]


class ProtocolUnitTests(unittest.TestCase):
    def setUp(self):
        self.keys = _keys()
        self.payload = b"synthetic raw bytes\x00\xff\r\n"

    def test_ci_requires_live_network_opt_in(self):
        if os.environ.get("CI", "").lower() in {"1", "true", "yes"}:
            self.assertEqual(os.environ.get("PILOT_NETWORK_TESTS"), "1", "CI must execute real HTTP tests, not silently skip them")

    def test_fixed_endpoint_and_payload_bounds(self):
        for endpoint in ["http://localhost:1234/upload", "http://127.0.0.1:1234/other", "http://127.0.0.1:1234/upload?q=x",
                         "http://127.0.0.1:1234/upload#fragment", "http://user@127.0.0.1:1234/upload", "https://127.0.0.1:1234/upload",
                         "http://127.0.0.1:0/upload", "http://127.0.0.1:65536/upload", "http://127.1:1234/upload"]:
            with self.subTest(endpoint=endpoint), self.assertRaises(InputError):
                HttpTransport(endpoint)
        transport = HttpTransport("http://127.0.0.1:1234/upload")
        with self.assertRaises(AttributeError):
            transport.endpoint = "http://127.0.0.1:4321/upload"
        for payload in [bytearray(self.payload), "text", b"x" * (MAX_PAYLOAD + 1)]:
            with patch("upload_pilot.transport._LoopbackHTTPConnection") as connection, self.assertRaises(InputError):
                transport.send(payload, {})
            connection.assert_not_called()
        for timeout in [True, 0, -1, float("inf"), float("nan"), 31]:
            with self.assertRaises(InputError):
                HttpTransport(transport.endpoint, timeout)

    def test_dispatch_signature_body_binding_and_exact_fields(self):
        envelope = _dispatch(self.payload, self.keys)
        body = _validate_dispatch(_header(envelope), self.payload, self.keys["gateway_public"], self.keys["gateway_key_id"], utc_now())
        self.assertEqual(body["payload_sha256"], hashlib.sha256(self.payload).hexdigest())
        invalid = [
            _dispatch(self.payload, self.keys, byte_length=True),
            _dispatch(self.payload, self.keys, byte_length=len(self.payload) + 1),
            _dispatch(self.payload, self.keys, payload_sha256="0" * 64),
            _dispatch(self.payload, self.keys, subject_sha256="A" * 64),
            _dispatch(self.payload, self.keys, extra_field="unsupported"),
            _dispatch(self.payload, self.keys, kind="upload_receipt"),
            _dispatch(self.payload, self.keys, created_at="2099-01-01T00:00:00Z"),
        ]
        tampered = deepcopy(envelope)
        tampered["signature"] = ("0" if tampered["signature"][0] != "0" else "1") + tampered["signature"][1:]
        invalid.append(tampered)
        for candidate in invalid:
            with self.subTest(candidate=candidate["body"].get("kind")), self.assertRaises(InputError):
                _validate_dispatch(_header(candidate), self.payload, self.keys["gateway_public"], self.keys["gateway_key_id"], utc_now())
        with self.assertRaises(InputError):
            _validate_dispatch(_header(envelope), self.payload + b"changed", self.keys["gateway_public"], self.keys["gateway_key_id"], utc_now())

    def test_canonical_base64_json_and_header_limits(self):
        self.assertEqual(_decode_header("e30="), {})
        invalid = [None, "", "not base64!", "e31=", "A" * (MAX_AUTH_HEADER + 4),
                   base64.b64encode(b'{"x":1,"x":2}').decode(), base64.b64encode(b" { } ").decode()]
        for value in invalid:
            with self.subTest(value_type=type(value).__name__), self.assertRaises(InputError):
                _decode_header(value)
        for headers in [[("Content-Length", "1"), ("content-length", "1")], [("X-A", "bad\r\n continuation")], [("X-A", "bad\x01value")],
                        [("X-A", "x" * 17000)], [("X-" + str(i), "a") for i in range(33)]]:
            with self.assertRaises(InputError):
                checked_headers(headers)
        for headers in [{}, {"content-length": "-1"}, {"content-length": "+1"}, {"content-length": "1,1"},
                        {"content-length": "1", "transfer-encoding": "chunked"}, {"content-length": "1", "content-encoding": "gzip"},
                        {"content-length": str(MAX_PAYLOAD + 1)}]:
            with self.assertRaises(InputError):
                content_length(headers, MAX_PAYLOAD)

    def test_header_budget_is_enforced_during_parsing(self):
        original = io.BytesIO(b"X-Long: " + b"x" * (MAX_HEADER_BYTES * 2) + b"\r\n\r\n")
        with self.assertRaises(http.client.HTTPException):
            http.client.parse_headers(_BoundedHeaderReader(original))
        self.assertLessEqual(original.tell(), MAX_HEADER_BYTES + 1)
        with self.assertRaises(http.client.HTTPException):
            http.client.parse_headers(_BoundedHeaderReader(io.BytesIO(b"X-A: b\r\n" * 33 + b"\r\n")))

    def test_socket_connect_uses_no_dns(self):
        sock = MagicMock()
        with patch("upload_pilot.transport.socket.socket", return_value=sock) as make_socket, patch("socket.getaddrinfo", side_effect=AssertionError("DNS was invoked")):
            connection = _LoopbackHTTPConnection("127.0.0.1", 1234, timeout=1)
            connection.connect()
            sock.connect.assert_called_once_with(("127.0.0.1", 1234))
            self.assertEqual(make_socket.call_args.args[:2], (__import__("socket").AF_INET, __import__("socket").SOCK_STREAM))
            connection.close()

    def test_request_completion_timestamp_is_after_request_return(self):
        connection = MagicMock()
        connection.getresponse.return_value = _ResponseDouble()
        times = ["2026-10-30T10:00:00Z", "2026-10-30T10:00:01Z"]
        with patch("upload_pilot.transport._LoopbackHTTPConnection", return_value=connection), patch("upload_pilot.transport.utc_now", side_effect=times) as clock:
            connection.request.side_effect = lambda *args, **kwargs: self.assertEqual(clock.call_count, 1)
            report = HttpTransport("http://127.0.0.1:1234/upload").send(self.payload, _dispatch(self.payload, self.keys))
        self.assertTrue(report["body_send_completed"])
        self.assertEqual(report["dispatched_at"], times[1])
        self.assertEqual(connection.request.call_args.args, ("POST", "/upload"))
        self.assertIs(connection.request.call_args.kwargs["body"], self.payload)
        self.assertEqual(connection.request.call_count, 1)
        connection.close.assert_called_once()

    def test_partial_write_and_missing_response_never_retry(self):
        for failure_at in ["request", "getresponse"]:
            with self.subTest(failure_at=failure_at):
                connection = MagicMock()
                getattr(connection, failure_at).side_effect = OSError("synthetic unit failure, no socket")
                with patch("upload_pilot.transport._LoopbackHTTPConnection", return_value=connection):
                    report = HttpTransport("http://127.0.0.1:1234/upload").send(self.payload, _dispatch(self.payload, self.keys))
                self.assertTrue(report["attempted"])
                self.assertEqual(report["body_send_completed"], failure_at == "getresponse")
                self.assertEqual(report["dispatched_at"] is None, failure_at == "request")
                self.assertIsNone(report["receipt"])
                self.assertIsNotNone(report["error"])
                self.assertEqual(connection.request.call_count, 1)

    def test_response_parser_rejects_ambiguous_framing_and_json(self):
        responses = [
            _ResponseDouble(headers=[("Content-Length", "2"), ("content-length", "2")]),
            _ResponseDouble(headers=[("Content-Type", "application/json"), ("Content-Length", str(MAX_CONTROL + 1))]),
            _ResponseDouble(headers=[("Content-Type", "application/json"), ("Content-Length", "3")]),
            _ResponseDouble(raw=b'{"body":1,"body":2}'), _ResponseDouble(raw=b'[]'),
            _ResponseDouble(headers=[("Content-Type", "application/json"), ("Transfer-Encoding", "chunked")]),
        ]
        for response in responses:
            connection = MagicMock()
            connection.getresponse.return_value = response
            with patch("upload_pilot.transport._LoopbackHTTPConnection", return_value=connection):
                report = HttpTransport("http://127.0.0.1:1234/upload").send(self.payload, _dispatch(self.payload, self.keys))
            self.assertIsNone(report["receipt"])
            self.assertIsNotNone(report["error"])
            self.assertEqual(connection.request.call_count, 1)

    def test_redirect_and_proxy_environment_do_not_change_destination(self):
        connection = MagicMock()
        connection.getresponse.return_value = _ResponseDouble(status=307, headers=[("Location", "http://127.0.0.1:4321/upload")])
        with patch.dict(os.environ, {"HTTP_PROXY": "http://127.0.0.1:9", "ALL_PROXY": "http://127.0.0.1:9"}), patch("upload_pilot.transport._LoopbackHTTPConnection", return_value=connection) as factory:
            report = HttpTransport("http://127.0.0.1:1234/upload").send(self.payload, _dispatch(self.payload, self.keys))
        self.assertEqual(report["error"], "REDIRECT_NOT_FOLLOWED")
        self.assertIsNone(report["receipt"])
        factory.assert_called_once_with("127.0.0.1", 1234, timeout=1.0)
        self.assertEqual(connection.request.call_count, 1)

    def test_sqlite_measurements_and_idempotency_without_claiming_http_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receiver.sqlite3"
            _initialize(path)
            envelope = _dispatch(self.payload, self.keys)
            dispatch = _validate_dispatch(_header(envelope), self.payload, self.keys["gateway_public"], self.keys["gateway_key_id"], utc_now())
            _count_handler(path)
            first = _accept(path, dispatch, self.payload, utc_now(), self.keys["receiver_secret"], self.keys["receiver_key_id"])
            again = _accept(path, dispatch, self.payload, utc_now(), self.keys["receiver_secret"], self.keys["receiver_key_id"])
            self.assertEqual(first, again)
            with self.assertRaises(InputError):
                _accept(path, dispatch, self.payload + b"different", utc_now(), self.keys["receiver_secret"], self.keys["receiver_key_id"])
            snapshot = _receiver(directory, self.keys).snapshot()
            self.assertEqual((snapshot["handler_calls"], snapshot["accepted_count"]), (1, 1))
            self.assertEqual(snapshot["rows"][0]["payload_sha256"], hashlib.sha256(self.payload).hexdigest())
            self.assertEqual(snapshot["rows"][0]["byte_length"], len(self.payload))
            self.assertEqual(snapshot["rows"][0]["receipt"], first)


@unittest.skipUnless(os.environ.get("PILOT_NETWORK_TESTS") == "1", "Real loopback HTTP tests disabled locally; CI requires PILOT_NETWORK_TESTS=1")
class LiveReceiverTests(unittest.TestCase):
    """Actual sockets and a separate process. Startup/network errors are failures."""
    def setUp(self):
        self.keys = _keys()
        self.payload = b"synthetic actual HTTP bytes\x00\xff\r\n"
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)

    def _directory(self, name):
        return Path(self.temp.name) / name

    def test_actual_raw_body_receipt_idempotency_conflict_and_cleanup(self):
        with _receiver(self._directory("normal"), self.keys) as receiver:
            self.assertNotEqual(receiver.pid, os.getpid())
            transport = HttpTransport(receiver.endpoint)
            envelope = _dispatch(self.payload, self.keys)
            first = transport.send(self.payload, envelope)
            self.assertIsNone(first["error"])
            body = verify_control(first["receipt"], self.keys["receiver_public"], self.keys["receiver_key_id"], "upload_receipt")
            self.assertEqual((body["payload_sha256"], body["byte_length"]), (hashlib.sha256(self.payload).hexdigest(), len(self.payload)))
            second = transport.send(self.payload, envelope)
            self.assertEqual(second["receipt"], first["receipt"])
            changed = self.payload + b"different"
            conflict = transport.send(changed, _dispatch(changed, self.keys))
            self.assertEqual(conflict["status"], 409)
            self.assertIsNone(conflict["receipt"])
            snapshot = receiver.snapshot()
            self.assertEqual((snapshot["handler_calls"], snapshot["accepted_count"]), (3, 1))
            self.assertEqual(snapshot["rows"][0]["receipt"], first["receipt"])
        self.assertTrue(receiver.cleanup_result["child_stopped"])
        self.assertEqual(receiver.snapshot(), snapshot)

    def test_actual_fault_modes_keep_measured_persistence(self):
        for mode in ["drop_after_commit", "wrong_receipt", "redirect"]:
            with self.subTest(mode=mode), _receiver(self._directory(mode), self.keys, mode) as receiver:
                report = HttpTransport(receiver.endpoint).send(self.payload, _dispatch(self.payload, self.keys))
                snapshot = receiver.snapshot()
                self.assertEqual(snapshot["handler_calls"], 1)
                self.assertEqual(snapshot["accepted_count"], 0 if mode == "redirect" else 1)
                if mode == "drop_after_commit":
                    self.assertIsNone(report["receipt"])
                    self.assertIsNotNone(report["error"])
                elif mode == "redirect":
                    self.assertEqual(report["error"], "REDIRECT_NOT_FOLLOWED")
                else:
                    returned = verify_control(report["receipt"], self.keys["receiver_public"], self.keys["receiver_key_id"], "upload_receipt")
                    stored = verify_control(snapshot["rows"][0]["receipt"], self.keys["receiver_public"], self.keys["receiver_key_id"], "upload_receipt")
                    self.assertNotEqual(returned["payload_sha256"], stored["payload_sha256"])
                    self.assertEqual(stored["payload_sha256"], hashlib.sha256(self.payload).hexdigest())

    def test_actual_authorization_is_required_except_explicit_negative_control(self):
        for mode in ["normal", "unauthenticated"]:
            with self.subTest(mode=mode), _receiver(self._directory(mode), self.keys, mode) as receiver:
                port = int(receiver.endpoint.split(":")[2].split("/")[0])
                connection = _LoopbackHTTPConnection("127.0.0.1", port, timeout=2)
                try:
                    connection.request("POST", "/upload", body=self.payload, headers={"Content-Type": "application/octet-stream", "Content-Length": str(len(self.payload)), "X-Pilot-Mode": "unauthenticated", "Connection": "close"})
                    response = connection.getresponse()
                    self.assertEqual(response.status, 200 if mode == "unauthenticated" else 400)
                    response.read()
                finally:
                    connection.close()
                snapshot = receiver.snapshot()
                self.assertEqual((snapshot["handler_calls"], snapshot["accepted_count"]), (1, 1 if mode == "unauthenticated" else 0))

    def test_actual_duplicate_request_headers_are_rejected(self):
        with _receiver(self._directory("duplicates"), self.keys) as receiver:
            port = int(receiver.endpoint.split(":")[2].split("/")[0])
            connection = _LoopbackHTTPConnection("127.0.0.1", port, timeout=2)
            try:
                connection.putrequest("POST", "/upload")
                connection.putheader("Content-Type", "application/octet-stream")
                connection.putheader("Content-Length", str(len(self.payload)))
                connection.putheader("Content-Length", str(len(self.payload)))
                connection.putheader("X-Pilot-Authorization", _header(_dispatch(self.payload, self.keys)))
                connection.endheaders(self.payload)
                response = connection.getresponse()
                self.assertEqual(response.status, 400)
                response.read()
            finally:
                connection.close()
            snapshot = receiver.snapshot()
            self.assertEqual((snapshot["handler_calls"], snapshot["accepted_count"]), (1, 0))


if __name__ == "__main__":
    unittest.main()
