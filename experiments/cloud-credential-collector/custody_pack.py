"""Portable, inert local-custody snapshot; not a normative VAP Evidence Pack.

Verification needs this installed code, its frozen JSON/crypto dependency, the
package, a caller-pinned public key and expected store ID. It never opens a store
or imports collector/SQLite. No artifact is extracted, decoded as a source record
or executed. A package's own checkpoint is not an independent latestness witness.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import importlib.util
import os
from pathlib import Path
import re
import stat
import sys
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def _module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError("local_pack_dependency_missing")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# This frozen module imports neither collector nor SQLite and performs no I/O
# when its pure JSON and digest functions are used.
evidence = _module("_vso_portable_custody_json", Path(__file__).resolve().parents[1]
                   / "cloud-credential-evidence" / "cloud_evidence.py")
canonical_json = evidence.canonical_json
load_json = evidence.load_json
digest = evidence.digest
bytes_digest = evidence.bytes_digest

PACK_SCHEMA = "experimental-cloud-custody-pack-v0"
RESULT_SCHEMA = "experimental-cloud-custody-pack-result-v0"
CONTEXT_SCHEMA = "experimental-cloud-custody-source-context-v0"
STORE_SCHEMA = "experimental-cloud-custody-store-v0"
RECEIPT_SCHEMA = "experimental-cloud-custody-receipt-v0"
CHECKPOINT_SCHEMA = "experimental-cloud-custody-checkpoint-v0"
SIGNING_DOMAIN = b"VSO experimental cloud custody v0\x00"
MAX_PACK_BYTES = 1048576
MAX_PACK_RECEIPTS = 256
MAX_PACK_ARTIFACTS = 256
MAX_ARTIFACT_BYTES = 65536
MAX_CONTEXT_BYTES = 16384
CHUNK_BYTES = 32768
MAX_DECODED_BYTES = MAX_PACK_BYTES
NANOSECONDS = 1000000000
HASH_RE = re.compile(r"sha256:[0-9a-f]{64}\Z")
STORE_ID_RE = re.compile(r"[0-9a-f]{32}\Z")
NANO_RE = re.compile(r"(?:0|[1-9][0-9]{0,21})\Z")


class PackError(ValueError):
    """A stable data-free rejection code; no source bytes or paths are echoed."""


def _text(value: Any, maximum: int = 4096) -> bool:
    return type(value) is str and 0 < len(value) <= maximum


def _integer(value: Any) -> bool:
    return type(value) is int and 0 <= value <= evidence.MAX_INTEGER


def _hash(value: Any) -> bool:
    return type(value) is str and HASH_RE.fullmatch(value) is not None


def _fields(value: Any, names: set[str], code: str) -> None:
    if type(value) is not dict or set(value) != names:
        raise PackError(code)


def _snapshot(value: Any) -> Any:
    try:
        if type(value) in (bytes, str):
            byte_length = len(value) if type(value) is bytes else len(value.encode("utf-8"))
            if byte_length > MAX_PACK_BYTES:
                raise PackError("package_size_limit")
            value = load_json(value)
        encoded = canonical_json(value)
        if len(encoded) > MAX_PACK_BYTES:
            raise PackError("package_size_limit")
        return load_json(encoded)
    except PackError:
        raise
    except (ValueError, TypeError, RecursionError, OverflowError) as exc:
        raise PackError("invalid_bounded_json") from exc


def _pins(trusted_public_key: Any, expected_store_id: Any) -> Ed25519PublicKey:
    if type(trusted_public_key) is not bytes or len(trusted_public_key) != 32:
        raise PackError("invalid_trusted_public_key")
    if type(expected_store_id) is not str or STORE_ID_RE.fullmatch(expected_store_id) is None:
        raise PackError("invalid_expected_store_id")
    return Ed25519PublicKey.from_public_bytes(trusted_public_key)


def _time_pair(nanoseconds: Any, seconds: Any) -> bool:
    return (type(nanoseconds) is str and NANO_RE.fullmatch(nanoseconds) is not None
            and _integer(seconds) and seconds == (int(nanoseconds) + NANOSECONDS - 1) // NANOSECONDS)


def _verify(envelope: Any, public: Ed25519PublicKey) -> dict:
    _fields(envelope, {"key_id", "payload", "signature"}, "invalid_custody_envelope")
    if (not _text(envelope["key_id"], 256) or type(envelope["payload"]) is not dict
            or type(envelope["signature"]) is not str
            or re.fullmatch(r"[0-9a-f]{128}", envelope["signature"]) is None):
        raise PackError("invalid_custody_envelope")
    try:
        signed = {"key_id": envelope["key_id"], "payload": envelope["payload"]}
        public.verify(bytes.fromhex(envelope["signature"]), SIGNING_DOMAIN + canonical_json(signed))
    except (InvalidSignature, ValueError) as exc:
        raise PackError("custody_signature_mismatch") from exc
    return envelope["payload"]


def _context(context: Any) -> None:
    _fields(context, {"schema", "adapter", "issuer", "tenant_id", "resource_id"}, "invalid_source_context")
    if (context["schema"] != CONTEXT_SCHEMA or any(not _text(context[k]) for k in (
            "adapter", "issuer", "tenant_id", "resource_id"))
            or len(canonical_json(context)) > MAX_CONTEXT_BYTES):
        raise PackError("invalid_source_context")


def _manifest(envelope: dict, public: Ed25519PublicKey, expected_store_id: str) -> dict:
    payload = _verify(envelope, public)
    _fields(payload, {"schema", "store_id", "collector_id", "created_time_ns", "created_time"},
            "invalid_store_manifest")
    if (payload["schema"] != STORE_SCHEMA or type(payload["store_id"]) is not str
            or STORE_ID_RE.fullmatch(payload["store_id"]) is None
            or not _text(payload["collector_id"], 256)
            or not _time_pair(payload["created_time_ns"], payload["created_time"])):
        raise PackError("invalid_store_manifest")
    if payload["store_id"] != expected_store_id:
        raise PackError("expected_store_id_mismatch")
    return payload


def _bound(envelope: dict, payload: dict, manifest: dict) -> None:
    if (envelope["key_id"] != manifest["key_id"]
            or any(payload[k] != manifest["payload"][k] for k in ("store_id", "collector_id"))):
        raise PackError("custody_store_binding_mismatch")


def _receipts(receipts: list, public: Ed25519PublicKey, manifest: dict) -> tuple[dict, list[str]]:
    previous = None
    previous_ns = int(manifest["payload"]["created_time_ns"])
    requests, artifacts, references = set(), {}, []
    for sequence, envelope in enumerate(receipts, 1):
        payload = _verify(envelope, public)
        _fields(payload, {"schema", "store_id", "collector_id", "request_id", "sequence",
                          "previous_receipt_sha256", "artifact_sha256", "artifact_size", "context",
                          "received_time_ns", "received_time"}, "invalid_custody_receipt")
        if (payload["schema"] != RECEIPT_SCHEMA or not _text(payload["request_id"], 256)
                or not _integer(payload["sequence"]) or payload["sequence"] != sequence
                or payload["previous_receipt_sha256"] != previous or not _hash(payload["artifact_sha256"])
                or not _integer(payload["artifact_size"]) or payload["artifact_size"] > MAX_ARTIFACT_BYTES
                or not _time_pair(payload["received_time_ns"], payload["received_time"])):
            raise PackError("invalid_receipt_prefix")
        _bound(envelope, payload, manifest)
        _context(payload["context"])
        if int(payload["received_time_ns"]) < previous_ns:
            raise PackError("receipt_clock_regressed")
        if payload["request_id"] in requests:
            raise PackError("duplicate_request_id")
        requests.add(payload["request_id"])
        artifact, size = payload["artifact_sha256"], payload["artifact_size"]
        if artifact in artifacts and artifacts[artifact] != size:
            raise PackError("artifact_size_binding_mismatch")
        artifacts[artifact] = size
        previous = digest(envelope)
        previous_ns = int(payload["received_time_ns"])
        references.append(previous)
    return artifacts, references


def _checkpoint(envelope: dict, public: Ed25519PublicKey, manifest: dict,
                receipts: list, references: list[str], *, exact_tip: bool) -> None:
    payload = _verify(envelope, public)
    _fields(payload, {"schema", "store_id", "collector_id", "sequence", "receipt_sha256",
                      "issued_time_ns", "issued_time"}, "invalid_checkpoint")
    if (payload["schema"] != CHECKPOINT_SCHEMA or not _integer(payload["sequence"])
            or payload["receipt_sha256"] is not None and not _hash(payload["receipt_sha256"])
            or not _time_pair(payload["issued_time_ns"], payload["issued_time"])):
        raise PackError("invalid_checkpoint")
    _bound(envelope, payload, manifest)
    sequence = payload["sequence"]
    if exact_tip and sequence != len(receipts):
        raise PackError("internal_checkpoint_not_exact_tip")
    if sequence > len(receipts):
        raise PackError("external_checkpoint_prefix_missing")
    expected = references[sequence - 1] if sequence else None
    if payload["receipt_sha256"] != expected:
        raise PackError("checkpoint_prefix_mismatch")
    timestamp = receipts[sequence - 1]["payload"]["received_time_ns"] if sequence else manifest["payload"][
        "created_time_ns"]
    if int(payload["issued_time_ns"]) < int(timestamp):
        raise PackError("checkpoint_predates_witnessed_prefix")


def _artifacts(items: list, required: dict) -> int:
    names = []
    total_bytes = 0
    for item in items:
        _fields(item, {"artifact_sha256", "artifact_size", "base64_chunks"}, "invalid_artifact_entry")
        name, size, chunks = item["artifact_sha256"], item["artifact_size"], item["base64_chunks"]
        if (not _hash(name) or not _integer(size) or size > MAX_ARTIFACT_BYTES
                or type(chunks) is not list or len(chunks) != (size + CHUNK_BYTES - 1) // CHUNK_BYTES):
            raise PackError("invalid_artifact_shape")
        if name in names:
            raise PackError("duplicate_artifact")
        names.append(name)
        if name not in required or required[name] != size:
            raise PackError("artifact_set_or_size_mismatch")
        total_bytes += size
        if total_bytes > MAX_DECODED_BYTES:
            raise PackError("decoded_artifact_limit")
        raw = bytearray()
        for index, chunk in enumerate(chunks):
            expected = min(CHUNK_BYTES, size - index * CHUNK_BYTES)
            if type(chunk) is not str or len(chunk) != 4 * ((expected + 2) // 3):
                raise PackError("invalid_base64_chunk_size")
            try:
                encoded = chunk.encode("ascii", errors="strict")
                decoded = base64.b64decode(encoded, validate=True)
            except (UnicodeError, ValueError, binascii.Error) as exc:
                raise PackError("invalid_base64_chunk") from exc
            if len(decoded) != expected or base64.b64encode(decoded) != encoded:
                raise PackError("noncanonical_base64_chunk")
            raw.extend(decoded)
        if len(raw) != size or bytes_digest(bytes(raw)) != name:
            raise PackError("artifact_bytes_mismatch")
    if names != sorted(names) or set(names) != set(required):
        raise PackError("artifact_set_or_order_mismatch")
    return total_bytes


def verify_pack(package, *, trusted_public_key, expected_store_id, external_checkpoint=None):
    """Pure bounded verification; no store, private key, source decoder or clock.

    package_sha256 identifies the canonical JSON value. Export writes precisely
    those bytes. External evidence must be supplied separately by the caller.
    """
    public = _pins(trusted_public_key, expected_store_id)
    package = _snapshot(package)
    _fields(package, {"schema", "manifest", "checkpoint", "receipts", "artifacts"}, "invalid_package_shape")
    if (package["schema"] != PACK_SCHEMA or type(package["receipts"]) is not list
            or len(package["receipts"]) > MAX_PACK_RECEIPTS or type(package["artifacts"]) is not list
            or len(package["artifacts"]) > MAX_PACK_ARTIFACTS):
        raise PackError("invalid_package_limits_or_schema")
    manifest = _manifest(package["manifest"], public, expected_store_id)
    required, references = _receipts(package["receipts"], public, package["manifest"])
    total = _artifacts(package["artifacts"], required)
    _checkpoint(package["checkpoint"], public, package["manifest"], package["receipts"], references, exact_tip=True)
    if external_checkpoint is not None:
        external_checkpoint = _snapshot(external_checkpoint)
        _checkpoint(external_checkpoint, public, package["manifest"], package["receipts"], references, exact_tip=False)
    return {"schema": RESULT_SCHEMA, "package_sha256": digest(package), "store_id": manifest["store_id"],
            "collector_id": manifest["collector_id"], "receipt_count": len(package["receipts"]),
            "artifact_count": len(package["artifacts"]), "total_artifact_bytes": total,
            "head_sequence": len(references), "head_receipt_sha256": references[-1] if references else None,
            "content_integrity": "supported", "internal_checkpoint_status": "matched_exported_tip",
            "external_checkpoint_status": "not_provided" if external_checkpoint is None else "matched_prefix",
            "rollback_assessment": "not_assessed" if external_checkpoint is None
            else "consistent_with_retained_checkpoint_only", "completeness": "unresolved", "latestness": "unresolved",
            "independent_custody": False, "azure_origin": "not_established", "authority": "not_assessed"}


def export_pack(store_path, output_path, *, trusted_public_key, private_key, expected_store_id,
                external_checkpoint=None, clock_ns=None, hook=None):
    """One locked snapshot; helper callbacks/clocks are API-only test facilities."""
    _pins(trusted_public_key, expected_store_id)
    if type(private_key) is not bytes or len(private_key) != 32:
        raise PackError("invalid_private_key")
    if clock_ns is not None and not callable(clock_ns) or hook is not None and not callable(hook):
        raise PackError("invalid_export_test_configuration")
    external_checkpoint = _snapshot(external_checkpoint) if external_checkpoint is not None else None
    # Export alone loads the existing storage implementation. Do not move this
    # import to module scope or call public locking methods inside the lock below.
    collector = _module("_vso_custody_pack_export_storage", Path(__file__).with_name("collector.py"))
    try:
        with collector.Collector(store_path, trusted_public_key=trusted_public_key, private_key=private_key) as store:
            with store._locked(), store._connection() as connection:
                summary, receipts, _, blobs = store._audit(connection, external_checkpoint)
                if summary["store_id"] != expected_store_id:
                    raise PackError("expected_store_id_mismatch")
                metadata = {"store_id": summary["store_id"], "receipt_count": len(receipts),
                            "head_sequence": summary["head_sequence"],
                            "head_receipt_sha256": summary["head_receipt_sha256"]}
                if hook is not None:
                    hook("snapshot_locked", _snapshot(metadata))
                if len(receipts) > MAX_PACK_RECEIPTS:
                    raise PackError("package_receipt_limit")
                if len(blobs) > MAX_PACK_ARTIFACTS:
                    raise PackError("package_artifact_limit")
                ns, seconds = collector._clock(clock_ns)
                previous_ns = int(receipts[-1]["payload"]["received_time_ns"]) if receipts else int(
                    store.manifest["payload"]["created_time_ns"])
                if int(ns) < previous_ns:
                    raise PackError("capture_clock_regressed")
                checkpoint = collector._sign({
                    "schema": CHECKPOINT_SCHEMA, "store_id": summary["store_id"],
                    "collector_id": store.manifest["payload"]["collector_id"],
                    "sequence": len(receipts), "receipt_sha256": summary["head_receipt_sha256"],
                    "issued_time_ns": ns, "issued_time": seconds,
                }, store.manifest["key_id"], store.private)
                artifacts = [{"artifact_sha256": name, "artifact_size": len(raw),
                              "base64_chunks": [base64.b64encode(raw[start:start + CHUNK_BYTES]).decode("ascii")
                                                for start in range(0, len(raw), CHUNK_BYTES)]}
                             for name, raw in sorted(blobs.items())]
                package = {"schema": PACK_SCHEMA, "manifest": store.manifest,
                           "checkpoint": checkpoint, "receipts": receipts, "artifacts": artifacts}
                report = verify_pack(package, trusted_public_key=trusted_public_key,
                                     expected_store_id=expected_store_id, external_checkpoint=external_checkpoint)
                raw = canonical_json(package)
                if len(raw) > MAX_PACK_BYTES:
                    raise PackError("package_size_limit")
                metadata["package_sha256"] = report["package_sha256"]
                if hook is not None:
                    hook("before_publish", _snapshot(metadata))
                # This frozen internal helper takes no flock. It publishes mode
                # 0600, atomically without replacement, outside the managed store.
                store._write_output(output_path, raw)
                if hook is not None:
                    hook("after_publish", _snapshot(metadata))
                return report
    except PackError:
        raise
    except (ValueError, OSError, TypeError, OverflowError) as exc:
        raise PackError("custody_snapshot_export_rejected") from exc


def _read_file(path: Path, *, maximum: int, private: bool = False) -> bytes:
    """Bounded no-follow CLI input reader; independent of every store module."""
    value = os.fspath(path)
    if not value or "\x00" in value or ".." in value.split("/"):
        raise PackError("unsafe_input_path")
    parsed = Path(value)
    parts = tuple(part for part in parsed.parts if part not in ("/", "."))
    if not parts:
        raise PackError("unsafe_input_path")
    directory = None
    fd = None
    try:
        directory = os.open("/" if parsed.is_absolute() else ".",
                            os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)
        for part in parts[:-1]:
            following = os.open(part, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC,
                                dir_fd=directory)
            os.close(directory)
            directory = following
        fd = os.open(parts[-1], os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC, dir_fd=directory)
        before = os.fstat(fd)
        if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
                or before.st_size < 0 or before.st_size > maximum):
            raise PackError("invalid_input_file")
        if private and (before.st_uid != os.geteuid() or stat.S_IMODE(before.st_mode) != 0o600):
            raise PackError("unsafe_private_key_file")
        raw = bytearray()
        while len(raw) <= maximum:
            chunk = os.read(fd, min(65536, maximum + 1 - len(raw)))
            if not chunk:
                break
            raw.extend(chunk)
        after = os.fstat(fd)
        facts = lambda item: (item.st_dev, item.st_ino, item.st_size, item.st_mtime_ns, item.st_ctime_ns)
        if len(raw) > maximum or len(raw) != before.st_size or facts(before) != facts(after):
            raise PackError("input_changed_during_read")
        return bytes(raw)
    except OSError as exc:
        raise PackError("input_file_rejected") from exc
    finally:
        if fd is not None:
            os.close(fd)
        if directory is not None:
            os.close(directory)


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        # Do not echo unrecognized values, filenames or secret-bearing arguments.
        raise PackError("invalid_command_line")


def main(argv: list[str] | None = None) -> int:
    parser = _Parser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    for command in ("export", "verify"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument("--public-key-file", required=True, type=Path)
        subparser.add_argument("--expected-store-id", required=True)
        subparser.add_argument("--external-checkpoint", type=Path)
        if command == "export":
            subparser.add_argument("--store", required=True, type=Path)
            subparser.add_argument("--out", required=True, type=Path)
            subparser.add_argument("--private-key-file", required=True, type=Path)
        else:
            subparser.add_argument("--pack", required=True, type=Path)
    try:
        args = parser.parse_args(argv)
        public_key = _read_file(args.public_key_file, maximum=32)
        external = _snapshot(_read_file(args.external_checkpoint, maximum=MAX_PACK_BYTES)) \
            if args.external_checkpoint is not None else None
        if args.command == "verify":
            report = verify_pack(_read_file(args.pack, maximum=MAX_PACK_BYTES), trusted_public_key=public_key,
                                 expected_store_id=args.expected_store_id, external_checkpoint=external)
        else:
            private_key = _read_file(args.private_key_file, maximum=32, private=True)
            report = export_pack(args.store, args.out, trusted_public_key=public_key, private_key=private_key,
                                 expected_store_id=args.expected_store_id, external_checkpoint=external)
        sys.stdout.buffer.write(canonical_json(report) + b"\n")
        return 0  # A bounded local report, never a safety, latestness or conformance pass.
    except PackError as exc:
        sys.stderr.write(canonical_json({"error": str(exc)}).decode("utf-8") + "\n")
        return 2
    except (ValueError, OSError, TypeError, OverflowError):
        sys.stderr.write('{"error":"custody_pack_operation_rejected"}\n')
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
