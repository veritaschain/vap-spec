"""One bounded raw POST to a controller-pinned literal loopback endpoint."""

import base64
import http.client
import math
import re
import socket
from urllib.parse import urlsplit

from .protocol import MAX_CONTROL, MAX_PAYLOAD, InputError, canonical, decode_json, utc_now, validate_endpoint

MAX_AUTH_BYTES = 8 * 1024
MAX_AUTH_HEADER = 4 * ((MAX_AUTH_BYTES + 2) // 3)
MAX_HEADER_BYTES = 16 * 1024
MAX_HEADER_COUNT = 32


class _LoopbackHTTPConnection(http.client.HTTPConnection):
    """Use AF_INET directly so no name resolver, proxy or redirect is involved."""

    def connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        try:
            sock.connect(("127.0.0.1", self.port))
        except BaseException:
            sock.close()
            raise
        self.sock = sock


def checked_headers(items):
    """Reject duplicates/continuations and keep this experiment's framing small."""
    if len(items) > MAX_HEADER_COUNT:
        raise InputError("Too many HTTP headers")
    result, size = {}, 0
    for name, value in items:
        if type(name) is not str or type(value) is not str:
            raise InputError("Invalid HTTP header")
        try:
            size += len(name.encode("ascii")) + len(value.encode("latin-1")) + 4
        except UnicodeError as exc:
            raise InputError("Invalid HTTP header encoding") from exc
        if (not re.fullmatch(r"[!#$%&'*+.^_`|~0-9A-Za-z-]+", name)
                or any(ord(c) < 32 or ord(c) == 127 for c in value)):
            raise InputError("Invalid HTTP header or continuation")
        key = name.lower()
        if key in result:
            raise InputError("Duplicate HTTP header")
        result[key] = value
    if size > MAX_HEADER_BYTES:
        raise InputError("HTTP headers exceed the experiment limit")
    return result


def content_length(headers, maximum):
    if "transfer-encoding" in headers or "content-encoding" in headers:
        raise InputError("Transfer/content encoding is not supported")
    value = headers.get("content-length")
    if type(value) is not str or not re.fullmatch(r"[0-9]{1,10}", value):
        raise InputError("One bounded Content-Length is required")
    length = int(value)
    if length > maximum:
        raise InputError("HTTP body exceeds the experiment limit")
    return length


class HttpTransport:
    def __init__(self, endpoint, timeout=1.0):
        validate_endpoint(endpoint)
        if type(timeout) not in {int, float} or not math.isfinite(timeout) or not 0 < timeout <= 30:
            raise InputError("HTTP timeout must be finite and between 0 and 30 seconds")
        self._endpoint = endpoint
        self._port = urlsplit(endpoint).port
        self._timeout = float(timeout)

    @property
    def endpoint(self):
        return self._endpoint

    def send(self, payload, dispatch_envelope):
        if type(payload) is not bytes or len(payload) > MAX_PAYLOAD:
            raise InputError("Transport requires an immutable bounded bytes payload")
        encoded = canonical(dispatch_envelope)
        if len(encoded) > MAX_AUTH_BYTES:
            raise InputError("Dispatch authorization exceeds the header limit")
        authorization = base64.b64encode(encoded).decode("ascii")
        headers = {
            "Host": "127.0.0.1:" + str(self._port),
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(payload)),
            "Connection": "close",
            "X-Pilot-Authorization": authorization,
        }
        checked_headers(list(headers.items()))
        result = {
            "attempted": True, "body_send_completed": False,
            "attempted_at": utc_now(), "dispatched_at": None,
            "status": None, "receipt": None, "error": None,
        }
        connection = _LoopbackHTTPConnection("127.0.0.1", self._port, timeout=self._timeout)
        try:
            # Exactly one call. A partial write, refusal, timeout or response error
            # never triggers another attempt, even when its outcome is unknown.
            connection.request("POST", "/upload", body=payload, headers=headers, encode_chunked=False)
            result["body_send_completed"] = True
            result["dispatched_at"] = utc_now()
            response = connection.getresponse()
            result["status"] = response.status
            response_headers = checked_headers(response.getheaders())
            if not 200 <= response.status < 300:
                result["error"] = "REDIRECT_NOT_FOLLOWED" if 300 <= response.status < 400 else "HTTP_NON_SUCCESS"
                return result
            length = content_length(response_headers, MAX_CONTROL)
            if response_headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise InputError("Expected a JSON control response")
            raw = response.read(length)
            if len(raw) != length:
                raise InputError("Response body length mismatch")
            receipt = decode_json(raw, max_bytes=MAX_CONTROL)
            if type(receipt) is not dict:
                raise InputError("Expected a receipt object")
            # Cryptographic and target validation belong to the gateway. This is
            # only the bounded response object actually returned by the server.
            result["receipt"] = receipt
        except (OSError, http.client.HTTPException, InputError, ValueError, UnicodeError) as exc:
            result["error"] = "TRANSPORT_OR_RESPONSE_" + type(exc).__name__
            result["receipt"] = None
        finally:
            connection.close()
        return result
