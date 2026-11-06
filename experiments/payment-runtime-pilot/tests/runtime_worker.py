"""Subprocess entry point for the pilot's tests; never a payment integration.

The parent can observe an exact committed stage and send a real SIGKILL. Blocking
barriers use stdin, not sleeps. Secret configuration stays in private temp files.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from payment_runtime import Adapter, ProviderConfig, serve_provider


def read_private(path: Path):
    if stat.S_IMODE(path.stat().st_mode) != 0o600:
        raise ValueError("test_configuration_must_be_mode_0600")
    return json.loads(path.read_text(encoding="utf-8"))


def emit(value):
    print(json.dumps(value, sort_keys=True, separators=(",", ":")), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("role", choices=("provider", "client"))
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--request", type=Path)
    parser.add_argument("--action", choices=("submit", "reconcile", "read_status"), default="submit")
    parser.add_argument("--barrier", choices=("after_claim", "after_response", "after_commit"))
    args = parser.parse_args()
    config = read_private(args.config)

    def hook(stage, details):
        if stage == args.barrier:
            emit({"event": "barrier", "stage": stage, "pid": os.getpid()})
            release = sys.stdin.buffer.read(1)
            if not release:
                raise RuntimeError("test_barrier_release_pipe_closed")
            if release == b"!":
                raise RuntimeError("test_result_handling_failure_after_real_response")

    if args.role == "provider":
        config["private_key"] = bytes.fromhex(config.pop("private_key_hex"))
        config["fault_hook"] = hook
        serve_provider(ProviderConfig(**config), ready=lambda endpoint: emit({
            "event": "ready", "endpoint": endpoint, "pid": os.getpid()}))
        return 0

    config["provider_public_key"] = bytes.fromhex(config.pop("provider_public_key_hex"))
    config["fault_hook"] = hook
    adapter = Adapter(**config)
    request = read_private(args.request)
    result = getattr(adapter, args.action)(request)
    safe = dict(result)
    receipt = safe.pop("receipt_bytes", None)
    safe["receipt_hex"] = receipt.hex() if receipt is not None else None
    emit({"event": "result", "result": safe, "pid": os.getpid()})
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Do not print configuration, credentials, secret key bytes or reprs.
        emit({"event": "error", "error_type": type(exc).__name__})
        raise SystemExit(1)
