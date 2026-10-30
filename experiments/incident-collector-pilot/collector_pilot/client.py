"""One measured HTTP exchange per call, to a fixed literal loopback collector."""

import http.client
import math
from urllib.parse import urlsplit

from upload_pilot.transport import _LoopbackHTTPConnection, checked_headers, content_length

from .protocol import (
    MAX_CONTROL, InputError, _hex, _text, canonical, capture, decode_json, utc_now, validate_endpoint,
)


class CollectorClient:
    def __init__(self, endpoint, collector_public, collector_key_id, timeout=1.0):
        self._endpoint = validate_endpoint(endpoint)
        self._collector_public = _hex(collector_public)
        self._collector_key_id = _text(collector_key_id)
        if type(timeout) not in {int, float} or not math.isfinite(timeout) or not 0 < timeout <= 30:
            raise InputError("Collector timeout must be finite and between 0 and 30 seconds")
        self._timeout = float(timeout)
        self._port = urlsplit(endpoint).port

    @property
    def endpoint(self):
        return self._endpoint

    @property
    def collector_public(self):
        return self._collector_public

    @property
    def collector_key_id(self):
        return self._collector_key_id

    def collect(self, signed_intent):
        return self._exchange("/collect", signed_intent)

    def status(self, signed_query):
        return self._exchange("/status", signed_query)

    def _exchange(self, path, value):
        validate_endpoint(self._endpoint)
        if urlsplit(self._endpoint).port != self._port:
            raise InputError("Collector endpoint changed after construction")
        body = canonical(capture(value))
        headers = {
            "Host": "127.0.0.1:" + str(self._port), "Content-Type": "application/json",
            "Content-Length": str(len(body)), "Connection": "close",
        }
        checked_headers(list(headers.items()))
        result = {
            "attempted": True, "attempted_at": utc_now(), "completed_at": None,
            "status": None, "response": None, "error": None,
        }
        connection = _LoopbackHTTPConnection("127.0.0.1", self._port, timeout=self._timeout)
        try:
            # Deliberately one call: no retry, redirect, DNS or proxy handling.
            connection.request("POST", path, body=body, headers=headers, encode_chunked=False)
            response = connection.getresponse()
            result["status"] = response.status
            response_headers = checked_headers(response.getheaders())
            if not 200 <= response.status < 300:
                result["error"] = "REDIRECT_NOT_FOLLOWED" if 300 <= response.status < 400 else "HTTP_NON_SUCCESS"
                return result
            length = content_length(response_headers, MAX_CONTROL)
            if response_headers.get("content-type", "").split(";", 1)[0].strip().lower() != "application/json":
                raise InputError("Expected a JSON collector response")
            raw = response.read(length)
            if len(raw) != length:
                raise InputError("Collector response length mismatch")
            value = decode_json(raw)
            if type(value) is not dict:
                raise InputError("Expected a collector response envelope")
            # This is the actual response, not evidence of successful validation.
            # The gateway verifies exact intent/query/key bindings independently.
            result["response"] = value
        except (OSError, http.client.HTTPException, InputError, ValueError, UnicodeError) as exc:
            result["response"] = None
            result["error"] = "TRANSPORT_OR_RESPONSE_" + type(exc).__name__
        finally:
            connection.close()
            result["completed_at"] = utc_now()
        return result
