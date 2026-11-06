"""Owner-private native process helpers for the separate payment collector tests."""
from __future__ import annotations

import copy
import http.client
import importlib.util
import os
from pathlib import Path
import secrets
import sys
from urllib.parse import urlsplit

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
WORKER = Path(__file__).with_name("collector_worker.py")


def _load_authorization_support():
    path = ROOT.parent / "payment-authorization-pilot" / "tests" / "authorization_support.py"
    spec = importlib.util.spec_from_file_location("_collector_test_authorization_support", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


authorization_support = _load_authorization_support()
runtime = authorization_support.runtime
authorization = authorization_support.authorization
PYTHON = authorization_support.native_support.PYTHON
sys.path.insert(0, str(ROOT))
import payment_collector as collector


def _restore_bytes(value):
    if type(value) is dict:
        if set(value) == {"test_bytes_hex"}:
            return bytes.fromhex(value["test_bytes_hex"])
        return {key: _restore_bytes(item) for key, item in value.items()}
    if type(value) is list:
        return [_restore_bytes(item) for item in value]
    return value


class Process(authorization_support.Process):
    def result(self, timeout=10):
        event = self.event(timeout)
        if event.get("event") != "result":
            raise AssertionError("expected collector client result, got " + str(event.get("event")))
        if self.proc.wait(timeout=timeout) != 0:
            raise AssertionError("collector test client process failed")
        return _restore_bytes(event["result"])


class Harness(authorization_support.Harness):
    def __init__(self, *, collector_options=None, start_collector=True, **options):
        super().__init__(**options)
        self.collector_key = Ed25519PrivateKey.generate()
        self.collector_credential = secrets.token_hex(24)
        self.collector_path = self.root / "collector.sqlite"
        self.collector_process = None
        self.collector_endpoint = None
        self.collector_config = {
            "db_path": str(self.collector_path), "context": copy.deepcopy(self.context),
            "private_key_hex": self.collector_key.private_bytes_raw().hex(),
            "credential": self.collector_credential, "recovery_epoch": 1,
            "sqlite_timeout": 0.15, **(collector_options or {}),
        }
        try:
            if start_collector:
                self.start_collector()
        except BaseException:
            self.close()
            raise

    def start_collector(self, *, barrier=None, kind=None):
        config_path = self.next_file("collector-config", self.collector_config)
        command = [*PYTHON, str(WORKER), "collector", "--config", str(config_path)]
        if barrier:
            command.extend(("--barrier", barrier))
        if kind:
            command.extend(("--kind", kind))
        process = Process(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.processes.append(process)
        event = process.event()
        if event.get("event") != "ready":
            raise AssertionError("collector did not publish native listener readiness")
        self.collector_process = process
        self.collector_endpoint = event["endpoint"]
        return process

    def stop_collector(self, *, kill=False):
        if self.collector_process is not None:
            if kill:
                self.collector_process.kill()
            self.collector_process.close()
            self.collector_process = None

    def client_config(self, **changes):
        result = {"endpoint": self.collector_endpoint, "context": copy.deepcopy(self.context),
                  "public_key_hex": self.collector_key.public_key().public_bytes_raw().hex(),
                  "credential": self.collector_credential, "recovery_epoch": 1, "timeout": 2.0}
        result.update(changes)
        return result

    def client(self, **changes):
        config = self.client_config(**changes)
        config["public_key"] = bytes.fromhex(config.pop("public_key_hex"))
        return collector.CollectorClient(**config)

    def collected(self, *, gate=None, client=None, fault_hook=None):
        return collector.CollectedAdapter(
            self.gate() if gate is None else gate,
            self.client() if client is None else client, fault_hook=fault_hook)

    def collected_worker(self, *, action="submit", request=None, evidence=None,
                         barrier=None, kind=None, start_barrier=False,
                         config_changes=None, client_changes=None):
        config = {
            "runtime": self.adapter_config(**(config_changes or {})),
            "gate": {"policy": self.policy, "trusted_keys": {
                role: {name: public.hex() for name, public in keys.items()}
                for role, keys in self.trust.items()}, "identities": self.identities,
                "max_status_age_ms": 30000},
            "collector": self.client_config(**(client_changes or {})),
        }
        config_file = self.next_file("collected-client-config", config)
        request_file = self.next_file("collected-request", self.request if request is None else request)
        evidence_file = self.next_file("collected-evidence", {
            name: raw.hex() for name, raw in (self.evidence if evidence is None else evidence).items()})
        command = [*PYTHON, str(WORKER), "client", "--config", str(config_file),
                   "--request", str(request_file), "--evidence", str(evidence_file), "--action", action]
        if barrier:
            command.extend(("--barrier", barrier))
        if kind:
            command.extend(("--kind", kind))
        if start_barrier:
            command.append("--start-barrier")
        process = Process(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.processes.append(process)
        return process

    def collector_counts(self):
        return collector.collector_snapshot(str(self.collector_path))

    def next_request(self, name, *, amount_minor="1250"):
        return {**self.request, "operation_id": "operation-" + name,
                "idempotency_key": "idempotency-" + name, "amount_minor": amount_minor}


def direct_http(endpoint, method, path, *, raw=None, credential=None):
    """Exercise the actual loopback server, without proxy or redirect support."""
    parsed = urlsplit(endpoint)
    if (parsed.scheme != "http" or parsed.hostname != "127.0.0.1"
            or parsed.username is not None or parsed.password is not None
            or parsed.path not in ("", "/") or parsed.query or parsed.fragment):
        raise ValueError("test_http_requires_literal_loopback")
    headers = {"Content-Type": "application/json"}
    if credential is not None:
        headers["Authorization"] = "Bearer " + credential
    connection = http.client.HTTPConnection("127.0.0.1", parsed.port, timeout=3)
    try:
        connection.request(method, path, body=raw, headers=headers)
        response = connection.getresponse()
        return response.status, response.read()
    finally:
        connection.close()
