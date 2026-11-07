"""Small public-synthetic helpers shared by native-process tests and the demo.

This module performs no ingestion itself. Its key seed is deliberately PUBLIC
test material. Every process runs under the same local test operator identity.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import select
import signal
import stat
import subprocess
import sys
import tempfile
import time

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


ROOT = Path(__file__).resolve().parents[1]
WORKER = Path(__file__).with_name("collector_worker.py")
PYTHON = [sys.executable, *(["-O"] if sys.flags.optimize else [])]
PUBLIC_TEST_SEED = hashlib.sha256(b"PUBLIC SYNTHETIC CLOUD COLLECTOR TEST KEY / NEVER USE FOR REAL DATA").digest()
PUBLIC_TEST_KEY = Ed25519PrivateKey.from_private_bytes(PUBLIC_TEST_SEED).public_key().public_bytes(
    serialization.Encoding.Raw, serialization.PublicFormat.Raw)
SIGNIN_ADAPTER = "azure-service-principal-signin-subset-v0"
KEYVAULT_ADAPTER = "azure-key-vault-audit-subset-v0"
TENANT = "11111111-1111-4111-8111-111111111111"
PRINCIPAL = "55555555-5555-4555-8555-555555555555"
APP = "77777777-7777-4777-8777-777777777777"
RESOURCE_PRINCIPAL = "88888888-8888-4888-8888-888888888888"
RESOURCE_IDENTITY = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
VAULT = "/subscriptions/aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa/resourceGroups/synthetic/providers/Microsoft.KeyVault/vaults/fixture-a"
SECRET_URI = "https://fixture-a.invalid/secrets/synthetic-secret/version-1?api-version=7.4"
SENSITIVE_SENTINEL = "SYNTHETIC-PRIVATE-SOURCE-MARKER-583071-NOT-A-REAL-SECRET"
CUSTODY_DOMAIN = b"VSO experimental cloud custody v0\x00"
COLLECTOR_ID = "synthetic-local-cloud-collector"
KEY_ID = "PUBLIC-SYNTHETIC-CLOUD-COLLECTOR-KEY"


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(raw):
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def utc(seconds):
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def native_record(adapter=KEYVAULT_ADAPTER, *, at):
    """Source-shaped synthetic records, including an intentionally private marker."""
    if adapter == SIGNIN_ADAPTER:
        return {
            "Id": "synthetic-native-signin-1", "AADTenantId": TENANT,
            "TenantId": "44444444-4444-4444-8444-444444444444", "AppId": APP,
            "AppOwnerTenantId": "33333333-3333-4333-8333-333333333333",
            "ResourceOwnerTenantId": TENANT, "ServicePrincipalId": PRINCIPAL,
            "ResourceServicePrincipalId": RESOURCE_PRINCIPAL, "ResourceIdentity": RESOURCE_IDENTITY,
            "ServicePrincipalCredentialKeyId": "99999999-9999-4999-8999-999999999999",
            "UniqueTokenIdentifier": "synthetic-nonsecret-token-id", "ResultType": "Success",
            "ResultSignature": "0", "CreatedDateTime": utc(at), "TimeGenerated": utc(at),
            "CorrelationId": "synthetic-shared-correlation", "IPAddress": "192.0.2.10",
            "FixturePrivateMarker": SENSITIVE_SENTINEL,
        }
    if adapter != KEYVAULT_ADAPTER:
        raise ValueError("unknown synthetic test adapter")
    return {
        "time": utc(at), "resourceId": VAULT, "operationName": "SecretGet", "operationVersion": "7.4",
        "resultType": "Success", "resultSignature": "OK", "correlationId": "synthetic-shared-correlation",
        "identity": {"claim": {"appid": APP, "oid": PRINCIPAL, "tid": TENANT}},
        "properties": {"requestUri": SECRET_URI, "httpStatusCode": 200},
        "FixturePrivateMarker": SENSITIVE_SENTINEL, "FixtureNote": "合成記録",
    }


def raw_record(adapter=KEYVAULT_ADAPTER, *, at):
    # Deliberate leading/trailing whitespace and layout are part of the evidence.
    return (" \n" + json.dumps(native_record(adapter, at=at), ensure_ascii=False,
                               indent=2, allow_nan=False) + "\n\t").encode("utf-8")


def private_write(path, data):
    path = Path(path)
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(fd, "wb") as target:
            target.write(data)
    except BaseException:
        # The descriptor is owned by fdopen once it succeeds.
        raise
    return path


def private_json(path, value):
    return private_write(path, canonical(value))


def context(adapter=KEYVAULT_ADAPTER):
    return {"schema": "experimental-cloud-custody-source-context-v0", "adapter": adapter,
            "issuer": "synthetic-local-collector", "tenant_id": TENANT, "resource_id": VAULT}


def load_collector():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import collector
    return collector


class Harness:
    """Actual private files and store; every restart constructs a fresh collector."""
    def __init__(self, *, raw=None, source_context=None, initialize=True, clock_ns=None):
        self.temp = tempfile.TemporaryDirectory(prefix="synthetic-cloud-custody-")
        self.root = Path(self.temp.name)
        self.store = self.root / "store"
        self.input = self.root / "source.raw"
        self.source_at = int(time.time()) - 60
        self.raw = raw_record(at=self.source_at) if raw is None else raw
        private_write(self.input, self.raw)
        self.context = context() if source_context is None else source_context
        self.processes = []
        self.file_number = 0
        self.manifest = None
        if initialize:
            self.manifest = load_collector().initialize_store(
                self.store, collector_id=COLLECTOR_ID, key_id=KEY_ID,
                private_key=PUBLIC_TEST_SEED, trusted_public_key=PUBLIC_TEST_KEY, clock_ns=clock_ns)

    def open(self, *, writable=True, **options):
        return load_collector().Collector(self.store, trusted_public_key=PUBLIC_TEST_KEY,
                                         private_key=PUBLIC_TEST_SEED if writable else None, **options)

    def collect(self, request_id="request-1", *, path=None, source_context=None, **options):
        with self.open(**options) as store:
            return store.collect_file(self.input if path is None else path, request_id=request_id,
                                      context=self.context if source_context is None else source_context)

    def audit(self, **options):
        with self.open(writable=False) as store:
            return store.audit(**options)

    def checkpoint(self):
        with self.open() as store:
            return store.checkpoint()

    def db_path(self):
        for path in self.store.rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue
            with path.open("rb") as source:
                if source.read(16) == b"SQLite format 3\x00":
                    return path
        raise RuntimeError("synthetic test could not locate the SQLite index")

    def blob_path(self, raw=None):
        wanted = self.raw if raw is None else raw
        for path in self.store.rglob("*"):
            if path.is_symlink() or not path.is_file():
                continue
            if path.read_bytes() == wanted:
                return path
        raise RuntimeError("synthetic test could not locate the committed original bytes")

    def job(self, action="collect", *, request_id="request-1", path=None, source_context=None,
            barrier=None, start_barrier=False, **extras):
        self.file_number += 1
        data = {"action": action, "store": str(self.store), "input": str(self.input if path is None else path),
                "request_id": request_id, "context": self.context if source_context is None else source_context,
                "barrier": barrier, "start_barrier": start_barrier, **extras}
        job = private_json(self.root / ("job-%d.json" % self.file_number), data)
        process = Process([*PYTHON, str(WORKER), "--job", str(job)])
        self.processes.append(process)
        return process

    def close(self):
        for process in self.processes:
            process.close()
        self.temp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


def tree_snapshot(root):
    """Content/mode snapshot for no-repair assertions; filesystem atime is irrelevant."""
    result = {}
    for path in sorted(Path(root).rglob("*")):
        info = path.lstat()
        item = {"mode": stat.S_IMODE(info.st_mode)}
        if stat.S_ISLNK(info.st_mode):
            item["link"] = os.readlink(path)
        elif stat.S_ISREG(info.st_mode):
            item["sha256"] = digest(path.read_bytes())
        elif stat.S_ISDIR(info.st_mode):
            item["directory"] = True
        else:
            item["nonregular"] = True
        result[str(path.relative_to(root))] = item
    return result


class Process:
    """A real subprocess with bounded JSON-line barriers, no sleep-based races."""
    def __init__(self, command):
        self.proc = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
                                     bufsize=0)
        self.buffer = bytearray()

    def event(self, timeout=10):
        # readline on an unbuffered pipe can still block on a partial line;
        # bound every read and retain bytes locally instead.
        import time
        deadline = time.monotonic() + timeout
        while b"\n" not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not select.select([self.proc.stdout], [], [], max(0, remaining))[0]:
                raise RuntimeError("synthetic child event timed out")
            chunk = os.read(self.proc.stdout.fileno(), 65536)
            if not chunk:
                raise RuntimeError("synthetic child ended before its expected event")
            self.buffer.extend(chunk)
        line, _, remaining = self.buffer.partition(b"\n")
        self.buffer = bytearray(remaining)
        return json.loads(line)

    def release(self):
        self.proc.stdin.write(b"1")
        self.proc.stdin.flush()

    def result(self, timeout=10):
        event = self.event(timeout)
        code = self.proc.wait(timeout=timeout)
        if event.get("event") != "result" or code != 0:
            raise RuntimeError("synthetic child did not complete successfully")
        return event["result"]

    def kill(self):
        self.proc.kill()
        code = self.proc.wait(timeout=10)
        if code != -signal.SIGKILL:
            raise RuntimeError("synthetic child was not terminated by SIGKILL")
        return code

    def close(self):
        if self.proc.poll() is None:
            self.proc.kill()
            self.proc.wait(timeout=10)
        for pipe in (self.proc.stdin, self.proc.stdout, self.proc.stderr):
            pipe.close()
