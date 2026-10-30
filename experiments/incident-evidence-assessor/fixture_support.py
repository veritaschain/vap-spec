"""PUBLIC deterministic keys and synthetic facts, never imported by assess runtime."""

import hashlib
from copy import deepcopy

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from incident_assessor.evidence import digest, signing_bytes
from incident_assessor.model import ROLES

NOW = "2026-10-30T12:00:00Z"
OPERATION = "2026-10-30T11:00:00Z"
BEFORE = "2026-10-30T00:00:00Z"
AFTER = "2026-10-31T00:00:00Z"


def private_key(role):
    seed = hashlib.sha256(("PUBLIC SYNTHETIC INCIDENT TEST KEY / " + role).encode()).digest()
    return Ed25519PrivateKey.from_private_bytes(seed)


def sign(body, role):
    envelope = {"algorithm": "Ed25519", "key_id": role + "-test-key", "body": deepcopy(body)}
    envelope["signature"] = private_key(role).sign(signing_bytes(envelope)).hex()
    return envelope


def base(workflow):
    subject = {
        "request_id": "request-synthetic", "actor_id": "author-synthetic",
        "provider_id": "provider-synthetic", "endpoint": "https://ai.example.invalid/process",
        "tenant_id": "tenant-enterprise-a", "account_id": "account-enterprise-a", "purpose": "approved-analysis",
        "payload_sha256": hashlib.sha256(b"synthetic payload revision a").hexdigest(),
        "artifact_id": "document-synthetic", "revision_id": "revision-a", "object_ids": ["object-synthetic-001"],
        "policy_id": "policy-synthetic", "policy_version": "policy-v1", "policy_sha256": digest({"policy": "synthetic"}),
        "stage": "submission" if workflow == "publication" else workflow, "route_id": "managed-api-route",
        "disclosure_sha256": hashlib.sha256(b"synthetic disclosure").hexdigest(),
    }
    package = {
        "format": "incident-evidence-input/0.1", "evaluation_id": "evaluation-synthetic", "workflow": workflow,
        "as_of": NOW, "target": {"subject": subject, "operation_at": OPERATION,
            "coverage_requested": "managed_route", "authorities": {role: role + "-synthetic" for role in sorted(ROLES)}},
        "records": [],
    }
    keys = {}
    for role in sorted(ROLES):
        organization = "requester-org" if role in {"gateway", "collector", "author", "responder"} else role + "-org"
        keys[role + "-test-key"] = {
            "public_key": private_key(role).public_key().public_bytes_raw().hex(),
            "issuer": role + "-synthetic", "organization": organization, "roles": [role],
            "not_before": "2026-01-01T00:00:00Z", "not_after": "2027-01-01T00:00:00Z",
        }
    trust = {"format": "incident-evidence-trust/0.1", "evaluation_id": package["evaluation_id"], "workflow": workflow, "as_of": NOW,
             "target_sha256": digest(package["target"]), "mode": "synthetic-test-only", "keys": keys}
    return package, trust


def add(package, kind, data, *, role, binding=None, recorded_at=OPERATION, record_id=None):
    body = {
        "record_id": record_id or kind + "-" + str(len(package["records"]) + 1),
        "evaluation_id": package["evaluation_id"], "kind": kind, "issuer": role + "-synthetic",
        "recorded_at": recorded_at, "binding": deepcopy(package["target"]["subject"] if binding is None else binding),
        "data": deepcopy(data),
    }
    record = sign(body, role)
    package["records"].append(record)
    return record


def finish(package, trust):
    trust["target_sha256"] = digest(package["target"])
    trust["as_of"] = package["as_of"]
    trust["workflow"] = package["workflow"]
    return package, trust
