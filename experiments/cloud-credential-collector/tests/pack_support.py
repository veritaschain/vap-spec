"""Public-synthetic pack fixtures and a verifier process with no store imports.

Only the exporting parent uses the existing collector harness or public test
seed. The separate verification program receives the pack, a public-key file,
an externally expected store ID and optionally an external checkpoint.
"""
from __future__ import annotations

import base64
import copy
import json
from pathlib import Path
import subprocess
import sys

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

from collector_support import (
    CUSTODY_DOMAIN, Harness, PUBLIC_TEST_KEY, PUBLIC_TEST_SEED, PYTHON, ROOT,
    canonical, digest, private_json, private_write,
)

MAX_PACK_BYTES = 1_048_576
CHUNK_BYTES = 32_768
BINARY_ORIGINAL = b"\x00\xff\xfe\x80synthetic arbitrary original\r\n\x00"


def pack_module():
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    import custody_pack
    return custody_pack


def resign(envelope):
    """Independent custody encoding/signing; never calls the pack implementation."""
    signed = {key: copy.deepcopy(envelope[key]) for key in ("key_id", "payload")}
    key = Ed25519PrivateKey.from_private_bytes(PUBLIC_TEST_SEED)
    return {**signed, "signature": key.sign(CUSTODY_DOMAIN + canonical(signed)).hex()}


def verify_signature(envelope):
    signed = {key: envelope[key] for key in ("key_id", "payload")}
    Ed25519PublicKey.from_public_bytes(PUBLIC_TEST_KEY).verify(
        bytes.fromhex(envelope["signature"]), CUSTODY_DOMAIN + canonical(signed))


def resign_chain(package):
    """Refresh signatures/refs after a semantic mutation, preserving sequence data."""
    previous = None
    for index, envelope in enumerate(package["receipts"]):
        envelope["payload"]["previous_receipt_sha256"] = previous
        package["receipts"][index] = resign(envelope)
        previous = digest(canonical(package["receipts"][index]))
    checkpoint = package["checkpoint"]
    checkpoint["payload"]["sequence"] = len(package["receipts"])
    checkpoint["payload"]["receipt_sha256"] = previous
    package["checkpoint"] = resign(checkpoint)


def artifact_bytes(item):
    return b"".join(base64.b64decode(chunk, validate=True) for chunk in item["base64_chunks"])


def chunks(raw):
    return [base64.b64encode(raw[index:index + CHUNK_BYTES]).decode("ascii")
            for index in range(0, len(raw), CHUNK_BYTES)]


def export(h, target=None, *, external_checkpoint=None, **options):
    destination = h.root / "custody-pack.json" if target is None else Path(target)
    report = pack_module().export_pack(
        h.store, destination, trusted_public_key=PUBLIC_TEST_KEY, private_key=PUBLIC_TEST_SEED,
        expected_store_id=h.manifest["payload"]["store_id"],
        external_checkpoint=external_checkpoint, **options)
    return destination, json.loads(destination.read_text(encoding="utf-8")), report


def collected_pack(h, *, duplicate=True):
    h.collect("text-original")
    binary_path = private_write(h.root / "binary-source.raw", BINARY_ORIGINAL)
    h.collect("binary-original", path=binary_path)
    if duplicate:
        h.collect("binary-same-bytes-new-request", path=binary_path)
    return export(h)


# Intentionally self-contained: it never imports this helper or the public
# synthetic seed. A collector/sqlite import is an explicit test failure.
VERIFY_PROCESS_SOURCE = r'''
import builtins
import json
from pathlib import Path
import sys

real_import = builtins.__import__
def no_store_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] in {"sqlite3", "collector"}:
        raise RuntimeError("store dependency unavailable in portable verifier")
    return real_import(name, globals, locals, fromlist, level)
builtins.__import__ = no_store_import
sys.path.insert(0, sys.argv[1])
try:
    import custody_pack
    package = Path(sys.argv[2]).read_bytes()
    public_pin = Path(sys.argv[3]).read_bytes()
    expected_id = sys.argv[4]
    checkpoint = json.loads(Path(sys.argv[5]).read_text(encoding="utf-8")) if len(sys.argv) > 5 else None
    report = custody_pack.verify_pack(package, trusted_public_key=public_pin,
                                      expected_store_id=expected_id, external_checkpoint=checkpoint)
    forbidden = []
    for name, module in list(sys.modules.items()):
        filename = getattr(module, "__file__", "")
        if name.split(".")[0] == "sqlite3" or (filename and Path(filename).name == "collector.py"):
            forbidden.append(name)
    if forbidden:
        raise RuntimeError("store dependency loaded in portable verifier")
    print(json.dumps({"verification": report, "store_modules_loaded": forbidden}, sort_keys=True))
except Exception as exc:
    print(json.dumps({"error_type": type(exc).__name__}, sort_keys=True), file=sys.stderr)
    raise SystemExit(2)
'''


def standalone_verify(package_path, public_key_path, expected_store_id, *, external_checkpoint_path=None):
    command = [*PYTHON, "-c", VERIFY_PROCESS_SOURCE, str(ROOT), str(package_path),
               str(public_key_path), expected_store_id]
    if external_checkpoint_path is not None:
        command.append(str(external_checkpoint_path))
    return subprocess.run(command, capture_output=True, text=True, timeout=15, check=False)
