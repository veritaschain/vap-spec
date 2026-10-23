from __future__ import annotations

import base64
import copy
import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

ROOT = Path(__file__).resolve().parent
VECTORS = ROOT / "test-vectors"

SEEDS = {
    "operator-key-1": bytes.fromhex("11" * 32),
    "observer-key-1": bytes.fromhex("22" * 32),
    "anchor-key-1": bytes.fromhex("33" * 32),
}


def canonical(value: Any) -> bytes:
    def validate(v: Any) -> None:
        if isinstance(v, float):
            raise TypeError("floats are forbidden by the demo canonicalization profile")
        if isinstance(v, dict):
            for k, item in v.items():
                if not isinstance(k, str):
                    raise TypeError("object keys must be strings")
                validate(item)
        elif isinstance(v, list):
            for item in v:
                validate(item)
        elif v is not None and not isinstance(v, (str, int, bool)):
            raise TypeError(f"unsupported type: {type(v)!r}")

    validate(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(data: bytes) -> bytes:
    return hashlib.sha256(data).digest()


def hex_sha(data: bytes) -> str:
    return sha256(data).hex()


def b64(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def private_key(key_id: str) -> Ed25519PrivateKey:
    return Ed25519PrivateKey.from_private_bytes(SEEDS[key_id])


def sign(key_id: str, obj: dict[str, Any]) -> str:
    return b64(private_key(key_id).sign(canonical(obj)))


def event_unsigned(event: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in event.items() if k not in {"payload_hash", "signature"}}


def sign_event(event: dict[str, Any]) -> dict[str, Any]:
    unsigned = event_unsigned(event)
    event["payload_hash"] = hex_sha(canonical(unsigned))
    event["signature"] = sign(event["key_id"], {**unsigned, "payload_hash": event["payload_hash"]})
    return event


def event_bytes(event: dict[str, Any]) -> bytes:
    return canonical(event)


def leaf_hash(event: dict[str, Any]) -> bytes:
    return sha256(b"\x00" + event_bytes(event))


def node_hash(left: bytes, right: bytes) -> bytes:
    return sha256(b"\x01" + left + right)


def merkle_root(events: list[dict[str, Any]]) -> str:
    nodes = [leaf_hash(e) for e in events]
    if not nodes:
        return sha256(b"").hex()
    while len(nodes) > 1:
        next_nodes: list[bytes] = []
        for i in range(0, len(nodes), 2):
            right = nodes[i + 1] if i + 1 < len(nodes) else nodes[i]
            next_nodes.append(node_hash(nodes[i], right))
        nodes = next_nodes
    return nodes[0].hex()


def signed_record(record_type: str, key_id: str, root: str, scope_commitment: str, event_count: int, issued_at: str) -> dict[str, Any]:
    body = {
        "record_type": record_type,
        "key_id": key_id,
        "merkle_root": root,
        "scope_commitment": scope_commitment,
        "event_count": event_count,
        "issued_at": issued_at,
    }
    return {**body, "signature": sign(key_id, body)}


def make_event(seq: int, event_id: str, event_type: str, timestamp: str, attempt_id: str, actor: str, action: str, **extra: Any) -> dict[str, Any]:
    provenance = {"attempt_id": attempt_id, "actor": actor, "action": action, **extra}
    event = {
        "vap_version": "1.2",
        "chain_id": "vap-demo-chain-001",
        "event_id": event_id,
        "sequence_no": seq,
        "event_type": event_type,
        "timestamp": timestamp,
        "issuer_id": "did:web:demo.operator.example",
        "key_id": "operator-key-1",
        "policy_id": "org.veritaschain.demo:claim-triage-v1",
        "model_id": "sha256:demo-model-2026-07",
        "provenance": provenance,
    }
    return sign_event(event)


def build_pack(events: list[dict[str, Any]], scope: dict[str, Any], observer_root_override: str | None = None) -> dict[str, Any]:
    root = merkle_root(events)
    scope_commitment = hex_sha(canonical(scope))
    keys = {
        key_id: b64(private_key(key_id).public_key().public_bytes(Encoding.Raw, PublicFormat.Raw))
        for key_id in SEEDS
    }
    observer_root = observer_root_override or root
    return {
        "evidence_pack_version": "0.1.0-demo",
        "profile": "VAP-COMMON",
        "canonicalization": "JCS-CONSTRAINED-NO-FLOATS",
        "hash_algorithm": "SHA-256",
        "signature_algorithm": "Ed25519",
        "scope": scope,
        "scope_commitment": scope_commitment,
        "events": events,
        "merkle": {"algorithm": "RFC6962-DOMAIN-SEPARATED", "root": root},
        "producer_manifest": signed_record("PRODUCER_MANIFEST", "operator-key-1", root, scope_commitment, len(events), "2026-07-10T08:01:10Z"),
        "observer_receipt": signed_record("OBSERVER_RECEIPT", "observer-key-1", observer_root, scope_commitment, len(events), "2026-07-10T08:01:20Z"),
        "external_anchor_receipt": signed_record("DEMO_TRANSPARENCY_RECEIPT", "anchor-key-1", root, scope_commitment, len(events), "2026-07-10T08:01:30Z"),
        "public_keys": keys,
    }


def write(name: str, obj: dict[str, Any]) -> None:
    VECTORS.mkdir(parents=True, exist_ok=True)
    (VECTORS / name).write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    scope = {
        "chain_id": "vap-demo-chain-001",
        "batch_id": "batch-20260710-0800Z",
        "window_start": "2026-07-10T08:00:00Z",
        "window_end": "2026-07-10T08:01:00Z",
        "in_scope_event_types": ["AI_DECISION_ATTEMPT", "AI_DECISION_OUTCOME"],
        "expected_attempt_count": 2,
        "completeness_rule": "ATTEMPT_OUTCOME_BIJECTION",
    }
    events = [
        make_event(1, "01980000-0001-7000-8000-000000000001", "AI_DECISION_ATTEMPT", "2026-07-10T08:00:05Z", "attempt-001", "agent:triage-01", "EVALUATE_CLAIM", input_hash="sha256:claim-a", context={"jurisdiction": "DEMO"}),
        make_event(2, "01980000-0002-7000-8000-000000000002", "AI_DECISION_OUTCOME", "2026-07-10T08:00:06Z", "attempt-001", "agent:triage-01", "REFER_HUMAN", outcome="DENIED_AUTOMATION", reason_code="LOW_CONFIDENCE", human_review_required=True),
        make_event(3, "01980000-0003-7000-8000-000000000003", "AI_DECISION_ATTEMPT", "2026-07-10T08:00:20Z", "attempt-002", "agent:triage-01", "EVALUATE_CLAIM", input_hash="sha256:claim-b", context={"jurisdiction": "DEMO"}),
        make_event(4, "01980000-0004-7000-8000-000000000004", "AI_DECISION_OUTCOME", "2026-07-10T08:00:21Z", "attempt-002", "agent:triage-01", "APPROVE_AUTOMATION", outcome="APPROVED", reason_code="POLICY_RULES_SATISFIED", human_review_required=False),
    ]

    valid = build_pack(copy.deepcopy(events), copy.deepcopy(scope))
    write("valid-pack.json", valid)

    tampered = copy.deepcopy(valid)
    tampered["events"][1]["provenance"]["outcome"] = "APPROVED"
    write("invalid-tampered-event.json", tampered)

    omitted_events = [copy.deepcopy(e) for e in events if e["provenance"]["attempt_id"] != "attempt-002" or e["event_type"] != "AI_DECISION_OUTCOME"]
    for idx, event in enumerate(omitted_events, start=1):
        event["sequence_no"] = idx
        sign_event(event)
    omitted = build_pack(omitted_events, copy.deepcopy(scope))
    write("invalid-omitted-outcome.json", omitted)

    fake_root = "ab" * 32
    split_view = build_pack(copy.deepcopy(events), copy.deepcopy(scope), observer_root_override=fake_root)
    write("invalid-split-view.json", split_view)


if __name__ == "__main__":
    main()
