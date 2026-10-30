"""Controller-owned synthetic inputs and fresh ephemeral keys for this pilot."""

import hashlib
from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from upload_pilot.protocol import GateConfig, InputError, digest, public_key, sign_record, timestamp, utc_now

SYNTHETIC_BYTES = b"SYNTHETIC COLLECTOR PILOT ONLY\r\nname,record\nexample,0001\n" + "合成データ".encode("utf-8") + b"\x00\xff  \t\n"
COLLECTOR_ID = "synthetic-local-collector"


def make_keys():
    keys = {}
    for role in ("policy", "gateway", "receiver", "collector"):
        secret = Ed25519PrivateKey.generate().private_bytes_raw().hex()
        keys[role] = {"secret": secret, "public": public_key(secret),
                      "key_id": "collector-pilot-" + role, "issuer": "collector-pilot-" + role,
                      "organization": "same-controller-synthetic"}
    return keys


def _iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def make_case(payload, endpoint, *, grant_changes=None, decision="permit", expires_in=120,
              permit_payload=None, keys=None, request_id=None, evaluation_id=None):
    if type(payload) not in {bytes, bytearray} or decision not in {"permit", "deny"}:
        raise InputError("Invalid trusted collector test setup")
    keys = make_keys() if keys is None else keys
    now = timestamp(utc_now())
    before, until = _iso(now - timedelta(hours=1)), _iso(now + timedelta(seconds=expires_in))
    route = {"actor_id": "synthetic-client", "provider_id": "synthetic-receiver", "endpoint": endpoint,
             "tenant_id": "tenant-enterprise-a", "account_id": "account-enterprise-a",
             "purpose": "synthetic-collector-upload", "route_id": "controlled-collector-upload", "stage": "transfer"}
    grant = {key: value for key, value in route.items() if key != "stage"}
    if grant_changes:
        if not set(grant_changes) <= grant.keys():
            raise InputError("Unsupported grant mutation")
        grant.update(grant_changes)
    policy = {"effective_from": before, "effective_until": until, "grants": [grant], "require_collector": True}
    permitted_bytes = bytes(payload if permit_payload is None else permit_payload)
    subject = {"request_id": request_id or "collector-request-" + uuid4().hex, **route,
               "payload_sha256": hashlib.sha256(permitted_bytes).hexdigest(),
               "policy_id": "synthetic-collector-permission", "policy_version": "1", "policy_sha256": digest(policy)}
    evaluation_id = evaluation_id or "collector-evaluation-" + uuid4().hex
    records = []
    for kind, role, data in (
        ("transfer.policy", "policy", policy),
        ("transfer.decision", "gateway", {"decision": decision, "valid_from": before, "valid_until": until}),
    ):
        body = {"record_id": "initial-" + role, "evaluation_id": evaluation_id, "kind": kind,
                "issuer": keys[role]["issuer"], "recorded_at": utc_now(),
                "binding": deepcopy(subject), "data": data}
        records.append(sign_record(body, keys[role]["secret"], keys[role]["key_id"]))
    assessed_at = utc_now()
    package = {"format": "incident-evidence-input/0.1", "evaluation_id": evaluation_id,
               "workflow": "transfer", "as_of": assessed_at,
               "target": {"subject": subject, "operation_at": assessed_at, "coverage_requested": "managed_route",
                          "authorities": {role: keys[role]["issuer"] for role in ("policy", "gateway")}},
               "records": records}
    trust_keys = {}
    for role in ("policy", "gateway"):
        key = keys[role]
        trust_keys[key["key_id"]] = {"public_key": key["public"], "issuer": key["issuer"],
                                      "organization": key["organization"], "roles": [role],
                                      "not_before": _iso(now - timedelta(days=1)), "not_after": _iso(now + timedelta(days=1))}
    trust = {"format": "incident-evidence-trust/0.1", "evaluation_id": evaluation_id, "workflow": "transfer",
             "as_of": assessed_at, "target_sha256": digest(package["target"]), "mode": "synthetic-test-only", "keys": trust_keys}
    config = GateConfig(endpoint, route, keys["gateway"]["secret"], keys["gateway"]["key_id"],
                        keys["gateway"]["issuer"], keys["receiver"]["public"], keys["receiver"]["key_id"])
    return package, trust, config, deepcopy(keys["receiver"])
