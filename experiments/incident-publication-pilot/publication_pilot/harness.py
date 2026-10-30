"""Synthetic setup and reviewer assertions; not a production identity service."""

from copy import deepcopy
from datetime import timedelta
from uuid import uuid4

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from .editor import Editor, verify_snapshot, disclosure_text, render_html
from .gate import GateConfig, measured_components, adopted_data
from .protocol import digest, public_key, sign_record, sign_message, sha256_bytes, timestamp, utc_now


def iso(value):
    return value.isoformat(timespec="microseconds").replace("+00:00", "Z")


def make_keys():
    now = timestamp(utc_now())
    result = {}
    for role in ("policy", "collector", "author", "reviewer", "publisher"):
        secret = Ed25519PrivateKey.generate().private_bytes_raw().hex()
        result[role] = {"secret": secret, "public": public_key(secret), "key_id": "publication-" + role,
                        "issuer": "synthetic-" + role, "organization": "single-test-controller",
                        "role": role, "not_before": iso(now - timedelta(days=1)), "not_after": iso(now + timedelta(days=1))}
    return result


def _record(kind, data, role, keys, subject, evaluation_id, recorded_at):
    key = keys[role]
    return sign_record({"record_id": "record-" + uuid4().hex, "evaluation_id": evaluation_id,
                        "kind": kind, "issuer": key["issuer"], "recorded_at": recorded_at,
                        "binding": deepcopy(subject), "data": deepcopy(data)}, key["secret"], key["key_id"])


def prepare_candidate(editor, keys, *, request_id=None, evaluation_id=None, policy=None,
                      policy_version="1", route=None, disclosure_activities=None):
    source = editor.snapshot()
    collector = keys["collector"]
    view = verify_snapshot(source, collector["public"], collector["key_id"])
    disclosure = {"activities": list(view["observed_activities"] if disclosure_activities is None else disclosure_activities),
                  "scope": "recorded_local_session_only"}
    html, notice = render_html(view, disclosure), disclosure_text(disclosure)
    now = timestamp(utc_now())
    if policy is None:
        policy = {"effective_from": iso(now - timedelta(hours=1)), "effective_until": iso(now + timedelta(minutes=5)),
                  "prohibited_activities": [], "disclosure_categories": ["text"],
                  "approval_required": True, "interpretation": "resolved"}
    policy = deepcopy(policy)
    route = deepcopy(route) if route is not None else {
        "actor_id": "synthetic-author", "provider_id": "synthetic-venue",
        "endpoint": "local-publication://synthetic-venue/release", "tenant_id": "synthetic-tenant",
        "account_id": "synthetic-account", "purpose": "synthetic_local_export",
        "route_id": "controlled-local-publication", "stage": "publication"}
    subject = {"request_id": request_id or "publication-" + uuid4().hex, **route,
               "artifact_id": view["document_id"], "revision_id": view["revision_id"],
               "payload_sha256": sha256_bytes(html), "disclosure_sha256": sha256_bytes(notice.encode("utf-8")),
               "policy_id": "synthetic-publication-policy", "policy_version": policy_version,
               "policy_sha256": digest(policy)}
    evaluation_id = evaluation_id or "evaluation-" + uuid4().hex
    prepared_at = utc_now()
    entries = [("publication_policy", policy, "policy"),
               ("publication_manifest", {"observed_at": prepared_at, "components": measured_components(view, subject)}, "collector"),
               ("publication_coverage", {"scope": "declared_editor_only", "from": source["operations"][0]["body"]["observed_at"],
                                          "until": prepared_at}, "collector"),
               ("publication_disclosure", {"categories": ["text"] if disclosure["activities"] else [],
                                            "prepared_at": prepared_at, "text": notice}, "author")]
    entries += [("publication_activity", data, "collector") for data in adopted_data(view, subject)]
    authorities = {role: keys[role]["issuer"] for role in ("policy", "collector", "author", "reviewer")}
    package = {"format": "incident-evidence-input/0.1", "evaluation_id": evaluation_id,
               "workflow": "publication", "as_of": prepared_at,
               "target": {"subject": subject, "operation_at": prepared_at,
                          "coverage_requested": "managed_route", "authorities": authorities},
               "records": [_record(kind, data, role, keys, subject, evaluation_id, prepared_at) for kind, data, role in entries]}
    public_keys = {keys[role]["key_id"]: {"public_key": keys[role]["public"], "issuer": keys[role]["issuer"],
                  "organization": keys[role]["organization"], "roles": [role],
                  "not_before": keys[role]["not_before"], "not_after": keys[role]["not_after"]}
                   for role in authorities}
    trust = {"format": "incident-evidence-trust/0.1", "evaluation_id": evaluation_id,
             "workflow": "publication", "as_of": prepared_at, "target_sha256": digest(package["target"]),
             "mode": "synthetic-test-only", "keys": public_keys}
    config = GateConfig(route, subject["policy_id"], policy_version, subject["policy_sha256"], public_keys,
                        authorities, collector["key_id"], keys["reviewer"]["key_id"],
                        keys["publisher"]["public"], keys["publisher"]["key_id"])
    candidate = {"format": "incident-publication-candidate/0.1", "source": source,
                 "disclosure": disclosure, "html": html.decode("utf-8"), "evidence": package}
    return candidate, trust, config


def approve(candidate, keys, *, seconds=120):
    """Create a synthetic reviewer assertion, not evidence of real human reading."""
    key, at = keys["reviewer"], utc_now()
    until = iso(timestamp(at) + timedelta(seconds=seconds))
    subject = candidate["evidence"]["target"]["subject"]
    body = {"kind": "release_approval", "request_id": subject["request_id"], "candidate_sha256": digest(candidate),
            "artifact_sha256": subject["payload_sha256"], "disclosure_sha256": subject["disclosure_sha256"],
            "policy_sha256": subject["policy_sha256"], "destination_id": subject["provider_id"],
            "approved_at": at, "valid_until": until, "decision": "approve",
            "review_scope": "exact_local_artifact_and_disclosure"}
    record = _record("publication_approval", {"valid_from": at, "valid_until": until, "approval": "approved"},
                     "reviewer", keys, subject, candidate["evidence"]["evaluation_id"], at)
    return {"release": sign_message(body, key["secret"], key["key_id"]), "evidence": record}


def make_case(activity="generation", *, prohibited=(), interpretation="resolved", include_approval=True,
              approval_seconds=120, policy_seconds=300, disclosure_activities=None):
    keys = make_keys()
    collector = keys["collector"]
    editor = Editor("synthetic-note", collector["secret"], collector["key_id"])
    editor.set_block("paragraph-1", "Synthetic research note. Imported text has unknown origin.")
    if activity is not None:
        editor.set_block("paragraph-1", "Simulated assistance revised this synthetic paragraph. 日本語 <script> is plain text.", activity=activity)
    now = timestamp(utc_now())
    policy = {"effective_from": iso(now - timedelta(hours=1)), "effective_until": iso(now + timedelta(seconds=policy_seconds)),
              "prohibited_activities": list(prohibited), "disclosure_categories": ["text"],
              "approval_required": True, "interpretation": interpretation}
    candidate, trust, config = prepare_candidate(editor, keys, policy=policy, disclosure_activities=disclosure_activities)
    approval = approve(candidate, keys, seconds=approval_seconds) if include_approval else None
    return {"candidate": candidate, "trust": trust, "approval": approval, "config": config,
            "keys": keys, "editor": editor, "policy": policy}
