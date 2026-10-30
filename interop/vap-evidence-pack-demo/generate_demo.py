#!/usr/bin/env python3
"""Generate deterministic synthetic fixtures; the test private keys are PUBLIC.

Use --output-dir explicitly to write, or --check to compare committed bytes.
No external service is contacted and no production identity is represented.
"""

import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from verify_python import CANONICALIZATION, CONTRACT_ID, EVENT_TYPES, canonical, merkle_root

HERE = Path(__file__).resolve().parent
# Public TEST secrets. Never use these keys for production data or identity.
SEEDS = {"producer": bytes([0x11]) * 32, "observer": bytes([0x22]) * 32,
         "anchor": bytes([0x33]) * 32}
KEY_IDS = {role: "demo-" + role + "-key-1" for role in SEEDS}
PRIVATE_KEYS = {role: Ed25519PrivateKey.from_private_bytes(seed)
                for role, seed in SEEDS.items()}


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def sign(value, private_key):
    value = {key: item for key, item in value.items() if key != "signature"}
    value["signature"] = base64.b64encode(private_key.sign(canonical(value))).decode("ascii")
    return value


def sign_event(event, private_key):
    event = {key: item for key, item in event.items() if key not in ("payload_hash", "signature")}
    event["payload_hash"] = digest(event)
    return sign(event, private_key)


def make_scope(attempt_count):
    return {
        "chain_id": "demo-claim-triage",
        "batch_id": "demo-batch-" + str(attempt_count),
        "policy_id": "synthetic-triage-policy/1",
        "window_start": "2026-10-30T12:00:00Z",
        "window_end": "2026-10-30T12:00:10Z",
        "in_scope_event_types": list(EVENT_TYPES),
        "expected_attempt_count": attempt_count,
        "completeness_rule": "ATTEMPT_OUTCOME_BIJECTION",
    }


def make_events(scope):
    events = []
    for index in range(1, scope["expected_attempt_count"] + 1):
        for offset, kind in enumerate(EVENT_TYPES):
            sequence = (index - 1) * 2 + offset + 1
            provenance = {"attempt_id": f"attempt-{index:03}",
                          "actor": "synthetic-claim-service", "action": "claim-triage"}
            if kind == EVENT_TYPES[0]:
                provenance.update({"input_hash": hashlib.sha256(
                    f"synthetic-claim-{index:03}".encode("ascii")).hexdigest(),
                    "context": {"jurisdiction": "FICTIONAL-DEMO"}})
            else:
                denied = index == 1
                provenance.update({"outcome": "DENIED_AUTOMATION" if denied else "APPROVED",
                                   "reason_code": "LOW_CONFIDENCE" if denied else "POLICY_THRESHOLD_MET",
                                   "human_review_required": denied})
            events.append({
                "contract_id": CONTRACT_ID, "chain_id": scope["chain_id"],
                "event_id": f"event-{sequence:03}", "sequence_no": sequence,
                "event_type": kind, "timestamp": f"2026-10-30T12:00:{sequence - 1:02}Z",
                "issuer_id": "synthetic-demo-producer", "key_id": KEY_IDS["producer"],
                "policy_id": scope["policy_id"], "model_id": "fictional-triage-model/1",
                "provenance": provenance,
            })
    return events


def assemble(scope, events, producer_key=None):
    """Rebuild every event and record so semantic negative cases stay signed."""
    producer_key = producer_key or PRIVATE_KEYS["producer"]
    events = copy.deepcopy(events)
    for sequence, event in enumerate(events, 1):
        event["sequence_no"] = sequence
    events = [sign_event(event, producer_key) for event in events]
    root, commitment = merkle_root(events), digest(scope)
    pack = {
        "contract_id": CONTRACT_ID, "canonicalization": CANONICALIZATION,
        "hash_algorithm": "SHA-256", "signature_algorithm": "Ed25519",
        "scope": copy.deepcopy(scope), "scope_commitment": commitment,
        "events": events, "merkle": {"algorithm": "RFC6962-SHA256", "root": root},
    }
    for field, role, kind, second in (
        ("producer_manifest", "producer", "PRODUCER_MANIFEST", 11),
        ("observer_receipt", "observer", "OBSERVER_RECEIPT", 12),
        ("demo_anchor_receipt", "anchor", "DEMO_ANCHOR_RECEIPT", 13),
    ):
        key = producer_key if role == "producer" else PRIVATE_KEYS[role]
        pack[field] = sign({"record_type": kind, "key_id": KEY_IDS[role],
                            "merkle_root": root, "scope_commitment": commitment,
                            "event_count": len(events),
                            "issued_at": f"2026-10-30T12:00:{second:02}Z"}, key)
    return pack


def make_trust(scope):
    roles = {}
    for role, key in PRIVATE_KEYS.items():
        raw = key.public_key().public_bytes(serialization.Encoding.Raw,
                                            serialization.PublicFormat.Raw)
        roles[role] = {"key_id": KEY_IDS[role],
                       "public_key": base64.b64encode(raw).decode("ascii")}
    return {"contract_id": CONTRACT_ID, "trust_version": "demo-trust/1",
            "scope_commitment": digest(scope), "roles": roles}


def serialize(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=True,
                       allow_nan=False) + "\n").encode("ascii")


def generated_files():
    scope = make_scope(2)
    base = assemble(scope, make_events(scope))
    six_scope = make_scope(3)
    six = assemble(six_scope, make_events(six_scope))
    tampered = copy.deepcopy(base)
    tampered["events"][0]["provenance"]["action"] = "different-synthetic-action"
    omitted_outcome = assemble(scope, [event for index, event in enumerate(base["events"]) if index != 1])
    split_view = copy.deepcopy(base)
    split_view["observer_receipt"]["merkle_root"] = "ab" * 32
    split_view["observer_receipt"] = sign(split_view["observer_receipt"], PRIVATE_KEYS["observer"])
    omitted_pair = assemble(scope, base["events"][:2])
    rebound_scope = copy.deepcopy(scope)
    rebound_scope["expected_attempt_count"] = 1
    rebound = assemble(rebound_scope, base["events"][:2])
    # A fourth public TEST secret signs under the producer label, but the caller
    # still supplies the original producer public key in the separate trust file.
    untrusted_key = Ed25519PrivateKey.from_private_bytes(bytes([0x44]) * 32)
    untrusted = assemble(scope, base["events"], producer_key=untrusted_key)
    packs = {
        "valid-pack.json": base,
        "valid-six-events.json": six,
        "invalid-tampered-event.json": tampered,
        "invalid-omitted-outcome.json": omitted_outcome,
        "invalid-split-view.json": split_view,
        "invalid-omitted-pair.json": omitted_pair,
        "invalid-rebound-scope.json": rebound,
        "invalid-untrusted-signer.json": untrusted,
    }
    artifacts = {**packs, "demo-trust.json": make_trust(scope),
                 "demo-trust-six.json": make_trust(six_scope)}
    files = {name: serialize(value) for name, value in artifacts.items()}
    vectors = []
    for name, pack in packs.items():
        positive = name.startswith("valid-")
        vector = {"pack": name,
                  "trust": "demo-trust-six.json" if name == "valid-six-events.json" else "demo-trust.json",
                  "expected_verdict": "PASS" if positive else "FAIL",
                  "expected_exit_code": 0 if positive else 1}
        if positive:
            vector.update({"merkle_root": pack["merkle"]["root"],
                           "scope_commitment": pack["scope_commitment"]})
        vectors.append(vector)
    manifest = {"contract_id": CONTRACT_ID, "manifest_version": "demo-vector-manifest/1",
                "files": {name: {"sha256": hashlib.sha256(content).hexdigest(), "bytes": len(content)}
                          for name, content in files.items()}, "vectors": vectors}
    files["manifest.json"] = serialize(manifest)
    return files


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output-dir", type=Path, help="write generated copies only to this explicit directory")
    mode.add_argument("--check", action="store_true", help="compare committed fixture bytes without writing")
    args = parser.parse_args(argv)
    files = generated_files()
    if args.check:
        differences = []
        for name, expected in files.items():
            path = HERE / "test-vectors" / name
            if not path.is_file() or path.read_bytes() != expected:
                differences.append(name)
        if differences:
            print("FAIL: committed fixture bytes differ: " + ", ".join(differences))
            return 1
        print(f"PASS: {len(files)} committed fixture/manifest files match generated bytes; no files written")
        return 0
    try:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        collisions = [name for name in files if (args.output_dir / name).exists()
                      or (args.output_dir / name).is_symlink()]
        if collisions:
            print("ERROR: refusing to overwrite existing paths: " + ", ".join(collisions))
            return 2
        for name, content in files.items():
            # Exclusive creation also protects a path created after the check.
            with (args.output_dir / name).open("xb") as stream:
                stream.write(content)
    except OSError as exc:
        print("ERROR: cannot create output files: " + str(exc))
        return 2
    print(f"Wrote {len(files)} deterministic synthetic files to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
