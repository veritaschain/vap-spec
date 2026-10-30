"""Fresh-key synthetic setup; never imported by the runtime adapter/provider."""

from copy import deepcopy
from datetime import timedelta
import secrets
import uuid

from .protocol import (EXCLUSIONS, LOCATION, digest, public_key, sign_message,
                       sign_record, timestamp, utc_now)

SYNTHETIC_CONTENT = b"SYNTHETIC LOCAL OBJECT; NO PATIENT DATA OR REAL PERSON IDENTIFIERS.\n"


def _iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def make_keys():
    now = timestamp(utc_now())
    keys, pinned = {}, {}
    for role, core_role in (("requester", "responder"), ("provider", "provider"), ("observer", "reviewer")):
        secret = secrets.token_hex(32)
        key_id = role + "-" + uuid.uuid4().hex[:12]
        keys[role] = {"secret": secret, "key_id": key_id}
        pinned[key_id] = {
            "public_key": public_key(secret), "issuer": role + "-local",
            "organization": "single-local-controller", "roles": [core_role],
            "not_before": _iso(now - timedelta(hours=1)),
            "not_after": _iso(now + timedelta(days=1)),
        }
    pins = {"provider_id": "provider-local", "tenant_id": "tenant-synthetic", "location": LOCATION,
            **{role + "_key_id": key["key_id"] for role, key in keys.items()}, "keys": pinned}
    return keys, pins


def make_task(manifest, keys, pins, *, request_id=None, evaluation_id=None, seconds=300,
              requested_locations=None, at=None):
    at = at or utc_now()
    request_id = request_id or "request-" + uuid.uuid4().hex
    evaluation_id = evaluation_id or "evaluation-" + uuid.uuid4().hex
    key = keys["requester"]
    subject = {"request_id": request_id, "provider_id": manifest["provider_id"],
               "tenant_id": manifest["tenant_id"], "object_ids": [manifest["object_id"]],
               "payload_sha256": digest(manifest), "stage": "erasure"}
    request = sign_record({
        "record_id": "request-record-" + uuid.uuid4().hex, "evaluation_id": evaluation_id,
        "kind": "erasure.request", "issuer": pins["keys"][key["key_id"]]["issuer"],
        "recorded_at": at, "binding": subject,
        "data": {"requested_at": at, "requested_locations":
                 list(requested_locations) if requested_locations is not None else [LOCATION] + EXCLUSIONS},
    }, key["secret"], key["key_id"])
    authorization = sign_message({
        "kind": "deletion_authorization", "request_sha256": digest(request),
        "manifest_sha256": digest(manifest), "authorized_at": at,
        "valid_until": _iso(timestamp(at) + timedelta(seconds=seconds)),
    }, key["secret"], key["key_id"])
    return {"format": "incident-erasure-task/0.1", "manifest": deepcopy(manifest),
            "request": request, "authorization": authorization}


def make_case(root, *, provider_class=None, task_seconds=300, content=SYNTHETIC_CONTENT):
    from .provider import LocalProvider
    from .observer import LocalObserver
    keys, pins = make_keys()
    provider = (provider_class or LocalProvider)(root, pins, keys["provider"]["secret"])
    manifest = provider.create("object-synthetic", "version-" + uuid.uuid4().hex, content)
    task = make_task(manifest, keys, pins, seconds=task_seconds)
    observer = LocalObserver(provider.namespace_root, pins, keys["observer"]["secret"])
    return {"keys": keys, "pins": pins, "provider": provider, "observer": observer,
            "task": task, "manifest": manifest}


def execute(case, *, observe_before=True, observe_after=True, **kwargs):
    from .adapter import verify_bundle
    owned = deepcopy(case["task"])
    before = case["observer"].observe(owned, "before") if observe_before else None
    result = case["provider"].delete(owned, **kwargs)
    after = case["observer"].observe(owned, "after", previous=before,
                                    completion=result["attestation"]) if observe_after else None
    bundle = {"format": "incident-erasure-bundle/0.1", "task": owned, "as_of": utc_now(),
              "provider_result": result, "before": before, "after": after}
    expected = digest(owned)
    assessment = verify_bundle(bundle, case["pins"], expected)
    return {"bundle": bundle, "pins": deepcopy(case["pins"]),
            "expected_task_sha256": expected, "assessment": assessment}
