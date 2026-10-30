"""Deterministic synthetic evidence. Every private key here is PUBLIC TEST MATERIAL.

No service, real incident, independent observer or production timestamp is used.
Expected outcomes are defined separately in acceptance.json, not by this generator.
"""

import copy
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from . import ADAPTER
from .crypto import audit_path, digest, leaf_hash, merkle_root, signing_bytes

EVALUATION_TIME = 2000000400
KEY_ROLES = {
    "producer": ["event", "scope", "anchor", "manifest"],
    "executor": ["event"], "notifier": ["event"],
    "inventory-authority": ["inventory", "closure"],
    "test-receipt-service": ["receipt", "register"],
}


def private_key(name):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(
        ("PUBLIC SYNTHETIC TEST KEY; NEVER USE IN PRODUCTION: " + name).encode()).digest())


def signed(body, key):
    envelope = {"body": body, "algorithm": "Ed25519", "key_id": key}
    envelope["signature"] = private_key(key).sign(signing_bytes(envelope)).hex()
    return envelope


def resign(envelope):
    return signed(envelope["body"], envelope["key_id"])


def base(notification=False, commitment=False, disagreement=False, derived=False, count=1000):
    policy = {
        "id": "synthetic-full-delivery-v1", "adapter": ADAPTER,
        "event_signers": {"producer": ["producer"], "execution": ["executor"], "notification": ["notifier"]},
        "timing_register_id": "synthetic-register-1", "multiplicity": "exactly-one-per-obligation",
        "retries_cancellations_timeouts": "No implicit expansion; enumerate a separate obligation for each required record",
        "receipt_trust": "Synthetic closed-register assertions only; not an independent production service",
        "observation_assurance": "Synthetic source boundary only; no all-real-world-activity claim",
    }
    if commitment:
        policy["id"] = "synthetic-permitted-commitment-v1"
    pd = digest(policy)

    def body(kind, **kwargs):
        return {"kind": kind, "evaluation_id": "synthetic-evaluation-001", "policy_digest": pd, **kwargs}

    obligations, envelopes = [], []
    for i in range(count):
        oid = f"record-{i:04}"
        source = "producer" if i == 0 else "execution"
        event_type = "observation"
        payload = {"value": 0, "synthetic": True}
        if disagreement and i == 1:
            payload["value"] = 999
        if notification and i == count - 1:
            source, event_type = "notification", "notification_receipt"
            payload = {"trigger": "synthetic-finding-1", "recipient": "evaluator@example.invalid",
                       "stage": "delivered_endpoint", "at": 2000000190}
        obligation = {"id": oid, "source_id": source, "event_type": event_type,
                      "disclosure": "commitment" if commitment and i == count - 1 else "full"}
        if event_type == "notification_receipt":
            obligation["notification"] = {"trigger": payload["trigger"], "recipient": payload["recipient"],
                                          "stage": payload["stage"], "deadline": 2000000200}
        obligations.append(obligation)
        key = policy["event_signers"][source][0]
        envelopes.append(signed(body("event", event_id=oid, source_id=source, event_type=event_type, payload=payload), key))
    leaves = [leaf_hash(event["body"]) for event in envelopes]
    index = [{"event_id": event["body"]["event_id"], "source_id": event["body"]["source_id"],
              "event_type": event["body"]["event_type"], "leaf_hash": leaf.hex()}
             for event, leaf in zip(envelopes, leaves)]
    events = [{"signed": envelope, "event_hash": digest(envelope["body"]), "index": i,
               "path": audit_path(leaves, i)} for i, envelope in enumerate(envelopes)]
    anchor = signed(body("anchor", batch={
        "merkle_root": merkle_root(leaves).hex(), "event_count": count,
        "first_event_id": index[0]["event_id"] if index else None,
        "last_event_id": index[-1]["event_id"] if index else None,
        "policy_digest": pd, "index_digest": digest(index),
    }), "producer")

    def receipt(target, purpose, at):
        return signed(body("receipt", target_digest=digest(target), purpose=purpose, accepted_at=at,
                           uncertainty=1, adapter="synthetic-receipt/1"), "test-receipt-service")

    scope = signed(body("scope", revision="1", previous_revision=None,
                        systems=["synthetic-system"], operations=["synthetic-evaluation"],
                        event_classes=["observation", "notification_receipt"],
                        exclusions=["All real-world activity; no real services are accessed"],
                        observation_boundary="Deterministic fixture generator's explicit record enumeration only",
                        configuration_digest=digest({"generator": "scope-fixtures/1", "boundary": "synthetic"}),
                        controllers=["VSO test fixture operator controls all test keys and all simulated sources"],
                        claimed_independence=False, start=2000000100, end=2000000200,
                        interval="[start,end]", time_basis="synthetic POSIX integer seconds",
                        commitment_cutoff=2000000050, submission_deadline=2000000300,
                        inventory_mode="derived" if derived else "fixed", derivation_rule="explicit-obligations-v1",
                        expectation_source="synthetic-source-inventory", closure_rule="signed-source-enumeration-v1",
                        expected_digest=None if derived else digest(obligations), individually_required=[],
                        relationships=[{"rule": "payload-value-equality-v1", "left": "record-0000", "right": "record-0001"}]
                        if disagreement else []), "producer")
    sd = digest(scope)
    source_records = [{"obligation": obligation} for obligation in obligations]
    inventory = signed(body("inventory", scope_digest=sd, obligations=obligations), "inventory-authority")
    closure = signed(body("closure", scope_digest=sd, source_id="synthetic-source-inventory",
                          configuration_digest=scope["body"]["configuration_digest"], end=2000000200,
                          closed=True, closed_at=2000000210, closed_sources=["producer", "execution", "notification"],
                          observation_gaps=[], expected_digest=digest(obligations),
                          source_records_digest=digest(source_records)), "inventory-authority")
    manifest = signed(body("manifest", scope_digest=sd, anchor_digest=digest(anchor), final=True,
                           finalized_at=2000000310, delivery_digest=digest({"events": events, "commitment_proofs": []}),
                           entries=[{"id": obligation["id"], "state": "included"} for obligation in obligations]), "producer")
    p = {"format": ADAPTER, "policy": policy, "events": events, "batch_index": index, "anchor": anchor,
         "anchor_receipt": receipt(anchor, "anchor", 2000000250), "commitment_proofs": [],
         "experimental": {"scope": scope, "scope_receipt": receipt(scope, "scope", 2000000040),
                          "inventory": inventory, "closure": closure, "manifest": manifest}}
    if derived:
        p["experimental"]["source_records"] = source_records
    trust = {"purpose": "synthetic-test-only", "evaluation_id": "synthetic-evaluation-001",
             "policy_digest": pd, "scope_digest": sd,
             "keys": {name: {"public_key": private_key(name).public_key().public_bytes_raw().hex(), "roles": roles}
                      for name, roles in KEY_ROLES.items()}}
    return p, trust


def refresh_manifest(p):
    manifest = p["experimental"]["manifest"]
    manifest["body"]["delivery_digest"] = digest({"events": p["events"], "commitment_proofs": p["commitment_proofs"]})
    p["experimental"]["manifest"] = resign(manifest)


def disposition(p, event_id, state):
    for entry in p["experimental"]["manifest"]["body"]["entries"]:
        if entry["id"] == event_id:
            entry.update(state=state, reason="Synthetic acceptance fixture disposition")


def cases():
    ordinary = base()
    for number in range(1, 15):
        if number in (6, 7):
            p, trust = base(notification=True)
        elif number == 9:
            p, trust = base(commitment=True)
        elif number == 10:
            p, trust = base(disagreement=True)
        else:
            p, trust = copy.deepcopy(ordinary)
        x = p["experimental"]
        if number == 2:
            p["events"] = p["events"][:900]
            for i in range(900, 1000):
                disposition(p, f"record-{i:04}", "unaccounted")
        elif number == 3:
            p["events"][10]["signed"]["body"]["payload"]["value"] = 314159
        elif number == 4:
            p["events"] = p["events"][:900] + copy.deepcopy(p["events"][:100])
            for i in range(900, 1000):
                disposition(p, f"record-{i:04}", "unaccounted")
        elif number == 5:
            x["inventory"] = None
            x["closure"] = None
        elif number in (6, 7, 8, 9):
            removed = p["events"].pop()
            disposition(p, "record-0999", {6: "unaccounted", 7: "withheld", 8: "unavailable", 9: "withheld"}[number])
            if number == 6:
                x["closure"]["body"]["closed_sources"].remove("notification")
                x["closure"] = resign(x["closure"])
            if number == 9:
                p["commitment_proofs"] = [{**p["batch_index"][-1], "index": removed["index"], "path": removed["path"]}]
        elif number == 11:
            x["scope_receipt"] = None
        elif number == 12:
            x["scope_receipt"]["body"]["accepted_at"] = 2000000060
            x["scope_receipt"] = resign(x["scope_receipt"])
            x["timing_register"] = signed({"kind": "register", "evaluation_id": trust["evaluation_id"],
                "policy_digest": trust["policy_digest"], "scope_digest": trust["scope_digest"],
                "register_id": "synthetic-register-1", "receipt_digest": digest(x["scope_receipt"]),
                "closed": True, "closed_at": 2000000250, "first_accepted_at": 2000000060}, "test-receipt-service")
        elif number == 13:
            x["closure"]["body"]["observation_gaps"] = ["Synthetic source was disabled during part of the interval"]
            x["closure"] = resign(x["closure"])
        elif number == 14:
            x["scope"]["body"]["evaluation_id"] = "different-exercise"
            x["scope"] = resign(x["scope"])
        refresh_manifest(p)
        yield f"{number:02}", p, trust


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def generate(directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    manifest = []
    for case, package, trust in cases():
        write_json(directory / f"{case}.evidence.json", package)
        write_json(directory / f"{case}.trust.json", trust)
        manifest.append({"case": case, "evidence_digest": digest(package), "trust_digest": digest(trust),
                         "evaluation_time": EVALUATION_TIME})
    write_json(directory / "manifest.json", manifest)
    return manifest
