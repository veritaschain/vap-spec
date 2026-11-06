"""Actual native collector/client subprocesses with parent-controlled barriers."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT.parent / "payment-runtime-pilot"))
sys.path.insert(0, str(ROOT.parent / "payment-authorization-pilot"))
sys.path.insert(0, str(ROOT))
from payment_runtime import Adapter
from authorization_gate import AuthorizedAdapter, GateConfig
from payment_collector import CollectorConfig, CollectorClient, CollectedAdapter, serve_collector


def private_json(path):
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        raise ValueError("test_input_must_be_owner_private")
    return json.loads(path.read_text(encoding="utf-8"))


def encode_bytes(value):
    if type(value) is bytes:
        return {"test_bytes_hex": value.hex()}
    if type(value) is dict:
        return {key: encode_bytes(item) for key, item in value.items()}
    if type(value) is list:
        return [encode_bytes(item) for item in value]
    return value


def emit(value):
    print(json.dumps(encode_bytes(value), sort_keys=True, separators=(",", ":")), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("collector", "client"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--evidence", type=Path)
    parser.add_argument("--action", choices=("submit", "reconcile", "read_status", "read_custody",
                                           "recover_evidence", "check_custody"), default="submit")
    parser.add_argument("--barrier")
    parser.add_argument("--kind")
    parser.add_argument("--start-barrier", action="store_true")
    args = parser.parse_args()
    config = private_json(args.config)

    def hook(stage, details):
        if stage == args.barrier and (args.kind is None or details.get("kind") == args.kind):
            emit({"event": "barrier", "stage": stage, "kind": details.get("kind"),
                  "request_digest": details.get("request_digest"), "pid": os.getpid()})
            release = sys.stdin.buffer.read(1)
            if release == b"!":
                raise OSError("requested_test_barrier_fault")
            if release != b"1":
                raise RuntimeError("test_barrier_release_invalid")

    if args.mode == "collector":
        config["private_key"] = bytes.fromhex(config.pop("private_key_hex"))
        config["fault_hook"] = hook
        serve_collector(CollectorConfig(**config), ready=lambda endpoint: emit({
            "event": "ready", "endpoint": endpoint, "pid": os.getpid()}))
        return 0

    request = private_json(args.request)
    evidence = {name: bytes.fromhex(raw) for name, raw in private_json(args.evidence).items()}
    native = config["runtime"]
    native["provider_public_key"] = bytes.fromhex(native.pop("provider_public_key_hex"))
    native["fault_hook"] = hook
    gate = config["gate"]
    gate["trusted_keys"] = {
        role: {key: bytes.fromhex(public) for key, public in keys.items()}
        for role, keys in gate["trusted_keys"].items()}
    client = config["collector"]
    client["public_key"] = bytes.fromhex(client.pop("public_key_hex"))
    adapter = CollectedAdapter(AuthorizedAdapter(Adapter(**native), GateConfig(**gate), fault_hook=hook),
                               CollectorClient(**client), fault_hook=hook)
    if args.start_barrier:
        # Every store constructor and owned input read has finished before either
        # healthy concurrent caller is released into the claim transaction.
        emit({"event": "ready", "stage": "initialized", "pid": os.getpid()})
        if sys.stdin.buffer.read(1) != b"1":
            raise RuntimeError("test_start_barrier_release_invalid")
    result = (adapter.submit(request, evidence) if args.action == "submit"
              else getattr(adapter, args.action)(request))
    emit({"event": "result", "result": result, "pid": os.getpid()})
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Never echo private configuration, credentials, signing keys or records.
        emit({"event": "error", "error_type": type(exc).__name__})
        raise SystemExit(1)
