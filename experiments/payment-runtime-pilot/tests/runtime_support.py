"""Private native-process harness used only by payment runtime tests."""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import secrets
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
WORKER = Path(__file__).with_name("runtime_worker.py")
PYTHON = [sys.executable] + (["-O"] if sys.flags.optimize else [])
sys.path.insert(0, str(ROOT))
import payment_runtime as runtime


def private_json(path, value):
    data = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data)
    if stat.S_IMODE(Path(path).stat().st_mode) != 0o600:
        raise RuntimeError("private_test_file_permissions")


class Process:
    def __init__(self, command, *, env=None):
        self.proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, env=env)
        self.buffer = b""

    def event(self, timeout=10):
        deadline = time.monotonic() + timeout
        while b"\n" not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise AssertionError("native test process did not reach its expected barrier")
            with selectors.DefaultSelector() as selector:
                selector.register(self.proc.stdout, selectors.EVENT_READ)
                if not selector.select(remaining):
                    raise AssertionError("native test process event timeout")
            chunk = os.read(self.proc.stdout.fileno(), 65536)
            if not chunk:
                raise AssertionError(f"native test process closed event pipe (exit={self.proc.poll()})")
            self.buffer += chunk
        line, self.buffer = self.buffer.split(b"\n", 1)
        value = json.loads(line)
        if value.get("event") == "error":
            raise AssertionError("native test process error: " + value["error_type"])
        return value

    def release(self, *, raise_after=False):
        self.proc.stdin.write(b"!" if raise_after else b"1")
        self.proc.stdin.flush()

    def result(self, timeout=10):
        event = self.event(timeout)
        if event.get("event") != "result":
            raise AssertionError("expected native client result, got " + str(event.get("event")))
        result = event["result"]
        raw = result.pop("receipt_hex", None)
        result["receipt_bytes"] = bytes.fromhex(raw) if raw is not None else None
        if self.proc.wait(timeout=timeout) != 0:
            raise AssertionError("native client process failed")
        return result

    def kill(self):
        self.proc.kill()
        code = self.proc.wait(timeout=10)
        if code != -signal.SIGKILL:
            raise AssertionError("test did not observe actual SIGKILL termination")
        return code

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
            try:
                self.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.proc.kill()
                self.proc.wait(timeout=5)
        for stream in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            if stream and not stream.closed:
                stream.close()


class Harness:
    def __init__(self, *, provider_options=None, start=True):
        self.temporary = tempfile.TemporaryDirectory(prefix="synthetic-payment-runtime-")
        self.root = Path(self.temporary.name)
        self.root.chmod(0o700)
        self.processes = []
        self.index = 0
        self.provider = None
        self.endpoint = None
        self.context = {"tenant": "synthetic-tenant-A", "environment": "synthetic-test",
                        "api_audience": "synthetic-loopback-payment", "idempotency_domain": "synthetic-domain-A",
                        "currency": "USD", "minor_unit_scale": 2}
        self.configuration_digest = "sha256:" + "ab" * 32
        self.recovery_epoch = 1
        self.key = Ed25519PrivateKey.generate()
        self.credential = secrets.token_hex(24)
        self.provider_path = self.root / "provider.sqlite"
        self.journal_path = self.root / "journal.sqlite"
        self.initial_balances = {"source-A": "100000", "beneficiary-A": "0", "beneficiary-B": "0"}
        self.provider_config = {
            "db_path": str(self.provider_path), "context": copy.deepcopy(self.context),
            "private_key_hex": self.key.private_bytes_raw().hex(), "credential": self.credential,
            "configuration_digest": self.configuration_digest, "recovery_epoch": self.recovery_epoch,
            "initial_balances": copy.deepcopy(self.initial_balances), "sqlite_timeout": 0.15,
            **(provider_options or {}),
        }
        self.request = runtime.make_request(
            self.context, operation_id="operation-A", idempotency_key="idempotency-A",
            configuration_digest=self.configuration_digest, recovery_epoch=self.recovery_epoch,
            source_account="source-A", beneficiary="beneficiary-A", amount_minor="1250")
        try:
            if start:
                self.start_provider()
        except BaseException:
            self.close()
            raise

    def next_file(self, stem, value):
        self.index += 1
        path = self.root / f"{self.index:03d}-{stem}.json"
        private_json(path, value)
        return path

    def start_provider(self, *, barrier=None):
        config_path = self.next_file("provider-config", self.provider_config)
        command = [*PYTHON, str(WORKER), "provider", "--config", str(config_path)]
        if barrier:
            command.extend(("--barrier", barrier))
        process = Process(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        self.processes.append(process)
        event = process.event()
        if event.get("event") != "ready":
            raise AssertionError("provider did not publish native listener readiness")
        self.provider = process
        self.endpoint = event["endpoint"]
        return process

    def stop_provider(self, *, kill=False):
        if self.provider is not None:
            if kill:
                self.provider.kill()
            self.provider.close()
            self.provider = None

    def adapter_config(self, **changes):
        result = {
            "journal_path": str(self.journal_path), "endpoint": self.endpoint,
            "context": copy.deepcopy(self.context),
            "provider_public_key_hex": self.key.public_key().public_bytes_raw().hex(),
            "credential": self.credential, "configuration_digest": self.configuration_digest,
            "recovery_epoch": self.recovery_epoch, "timeout": 2.0, "sqlite_timeout": 0.15,
        }
        result.update(changes)
        return result

    def adapter(self, **changes):
        config = self.adapter_config(**changes)
        config["provider_public_key"] = bytes.fromhex(config.pop("provider_public_key_hex"))
        return runtime.Adapter(**config)

    def worker(self, *, action="submit", request=None, barrier=None, config_changes=None, env=None):
        config = self.next_file("client-config", self.adapter_config(**(config_changes or {})))
        request_file = self.next_file("request", self.request if request is None else request)
        command = [*PYTHON, str(WORKER), "client", "--config", str(config),
                   "--request", str(request_file), "--action", action]
        if barrier:
            command.extend(("--barrier", barrier))
        process = Process(command, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})})
        self.processes.append(process)
        return process

    def counts(self):
        return runtime.provider_snapshot(str(self.provider_path))

    def close(self):
        for process in reversed(self.processes):
            process.close()
        self.temporary.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
