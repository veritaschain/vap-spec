"""Native authorization-pilot test worker with explicit parent-controlled barriers."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT.parent / "payment-runtime-pilot"))
from payment_runtime import Adapter
from authorization_gate import AuthorizedAdapter, GateConfig


def private_json(path):
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        raise ValueError("test_input_must_be_owner_private")
    return json.loads(path.read_text(encoding="utf-8"))


def emit(value):
    print(json.dumps(value, sort_keys=True, separators=(",", ":")), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--request", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--action", choices=("submit", "reconcile", "read_status"), default="submit")
    parser.add_argument("--barrier", choices=("after_authorization_proof", "after_claim", "after_response"))
    args = parser.parse_args()
    config = private_json(args.config)
    request = private_json(args.request)
    evidence = {name: bytes.fromhex(raw) for name, raw in private_json(args.evidence).items()}

    def hook(stage, details):
        if stage == args.barrier:
            emit({"event": "barrier", "stage": stage, "pid": os.getpid()})
            if not sys.stdin.buffer.read(1):
                raise RuntimeError("test_barrier_release_closed")

    native = config["runtime"]
    native["provider_public_key"] = bytes.fromhex(native.pop("provider_public_key_hex"))
    native["fault_hook"] = hook
    gate = config["gate"]
    gate["trusted_keys"] = {
        role: {key: bytes.fromhex(public) for key, public in keys.items()}
        for role, keys in gate["trusted_keys"].items()}
    adapter = AuthorizedAdapter(Adapter(**native), GateConfig(**gate), fault_hook=hook)
    result = (adapter.submit(request, evidence) if args.action == "submit"
              else getattr(adapter, args.action)(request))
    safe = dict(result)
    receipt = safe.pop("receipt_bytes", None)
    safe["receipt_hex"] = receipt.hex() if receipt is not None else None
    emit({"event": "result", "result": safe, "pid": os.getpid()})
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Configuration and ephemeral credentials/keys are never printed.
        emit({"event": "error", "error_type": type(exc).__name__})
        raise SystemExit(1)
