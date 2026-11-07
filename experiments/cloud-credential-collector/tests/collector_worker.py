"""Test-only collector subprocess with parent-controlled durability barriers.

Fault control is kept in this test worker. The production CLI exposes no crash
flags. Job files and subprocess output contain only synthetic test data.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from collector_support import PUBLIC_TEST_KEY, PUBLIC_TEST_SEED, load_collector


def emit(value):
    print(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--job", required=True, type=Path)
    args = parser.parse_args()
    job = json.loads(args.job.read_text(encoding="utf-8"))
    collector = load_collector()

    def hook(stage, metadata):
        if stage == job["barrier"]:
            emit({"event": "barrier", "stage": stage, "metadata": metadata, "pid": os.getpid()})
            if sys.stdin.buffer.read(1) != b"1":
                raise RuntimeError("test barrier was not released")

    if job["start_barrier"]:
        emit({"event": "ready", "pid": os.getpid()})
        if sys.stdin.buffer.read(1) != b"1":
            raise RuntimeError("test start barrier was not released")
    with collector.Collector(job["store"], trusted_public_key=PUBLIC_TEST_KEY,
                             private_key=PUBLIC_TEST_SEED, hook=hook) as store:
        if job["action"] == "collect":
            result = store.collect_file(job["input"], request_id=job["request_id"], context=job["context"])
        elif job["action"] == "audit":
            result = store.audit(checkpoint=job.get("checkpoint"))
        elif job["action"] == "receipt":
            result = store.get_receipt(job["request_id"])
        elif job["action"] == "export":
            result = store.export_native(job["request_id"], job["output"], checkpoint=job.get("checkpoint"))
        else:
            raise ValueError("unknown test worker action")
        emit({"event": "result", "result": result, "pid": os.getpid()})
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Never include raw bytes, request contents, paths or private keys.
        emit({"event": "error", "error_type": type(exc).__name__})
        raise SystemExit(2)
