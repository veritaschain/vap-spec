"""Fixed Docker service endpoints; no proxy variables, redirects or caller-selected URLs."""
import http.client
from record_gate.common import canonical, decode, require

ENDPOINTS = {'http://audit:8080': ('audit', 8080), 'http://backend:8080': ('backend', 8080)}


def exchange(host, port, path, payload=None, method='POST', timeout=2):
    connection = http.client.HTTPConnection(host, port, timeout=timeout)
    try:
        raw = None if payload is None else canonical(payload)
        connection.request(method, path, body=raw, headers={'Content-Type': 'application/json'})
        response = connection.getresponse()
        data = response.read(1024 * 1024 + 1)
        require(len(data) <= 1024 * 1024, 'response_too_large')
        try:
            body = decode(data)
        except ValueError:
            body = {'non_json_response': True}
        return response.status, body
    finally:
        connection.close()


def service_rpc(url, path, payload):
    require(url in ENDPOINTS, 'endpoint_not_in_fixed_topology')
    status, body = exchange(*ENDPOINTS[url], path, payload)
    require(status == 200, 'service_rejected_request')
    return body
