"""Authenticate scoped statements without turning a clock into deletion evidence."""

import sys
from pathlib import Path

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

# Reuse the unchanged sibling assessor. Never modify its kinds, roles or domain.
_LEGACY = Path(__file__).resolve().parents[2] / "incident-evidence-assessor"
if str(_LEGACY) not in sys.path:
    sys.path.insert(0, str(_LEGACY))

from incident_assessor.assess import ROLES, assess as assess_erasure
from incident_assessor.evidence import Context, digest
from incident_assessor.model import (
    MAX_BYTES, InputError, canonical, digest_hex, enum, exact_keys, strings,
    subject, text, timestamp,
)

from . import DOMAIN, VERSION

KINDS = {"retention.statement": "provider", "retention.presence": "collector"}
REQUIRED_SUBJECT = {
    "request_id", "provider_id", "tenant_id", "account_id", "object_ids", "payload_sha256",
}
MAX_RECORDS = 256


def signing_bytes(envelope):
    """A distinct domain prevents reuse of legacy erasure signatures."""
    return (DOMAIN + "\0").encode("utf-8") + canonical({
        "algorithm": envelope["algorithm"], "key_id": envelope["key_id"],
        "body": envelope["body"],
    })


def _nonempty_strings(value):
    strings(value)
    if not value:
        raise InputError("Expected a nonempty string array")


def _validate_data(kind, data):
    if kind == "retention.statement":
        exact_keys(data, {
            "request_record_id", "terms_ref", "terms_sha256", "processing_locations",
            "training_use", "locations", "schedule", "exceptions",
        })
        text(data["terms_ref"])
        digest_hex(data["terms_sha256"])
        strings(data["processing_locations"])
        enum(data["training_use"], {"reported-disabled", "reported-enabled", "not-reported"})
        _nonempty_strings(data["locations"])
        schedule = data["schedule"]
        exact_keys(schedule, {"kind"}, {"deadline", "reason"})
        enum(schedule["kind"], {"stated-deadline", "unknown"})
        if schedule["kind"] == "stated-deadline":
            exact_keys(schedule, {"kind", "deadline"})
            timestamp(schedule["deadline"])
        else:
            exact_keys(schedule, {"kind", "reason"})
            text(schedule["reason"])
        exceptions = data["exceptions"]
        if type(exceptions) is not list or len(exceptions) > MAX_RECORDS:
            raise InputError("Expected at most 256 retention exceptions")
        seen = set()
        for item in exceptions:
            exact_keys(item, {"location", "reason", "until"})
            text(item["location"])
            text(item["reason"])
            if item["until"] is not None:
                timestamp(item["until"])
            if item["location"] not in data["locations"]:
                raise InputError("Retention exception lies outside the statement's locations")
            fingerprint = canonical(item)
            if fingerprint in seen:
                raise InputError("Duplicate retention exception")
            seen.add(fingerprint)
    else:
        exact_keys(data, {"request_record_id", "observed_at", "location", "method", "limitations"})
        timestamp(data["observed_at"])
        text(data["location"])
        text(data["method"])
        _nonempty_strings(data["limitations"])
    text(data["request_record_id"])


def _validate(package, trust):
    if len(canonical(package)) > MAX_BYTES or len(canonical(trust)) > MAX_BYTES:
        raise InputError("Input or trust exceeds 8 MiB")
    exact_keys(package, {"format", "erasure", "retention_records"})
    enum(package["format"], {"retention-evidence-input/0.1"})
    exact_keys(trust, {"format", "erasure_trust"})
    enum(trust["format"], {"retention-evidence-trust/0.1"})
    if type(package["erasure"]) is not dict or package["erasure"].get("workflow") != "erasure":
        raise InputError("The embedded evidence must use the unchanged erasure workflow")
    records = package["retention_records"]
    if type(records) is not list or len(records) > MAX_RECORDS:
        raise InputError("Expected at most 256 retention records")


def _validated_records(package):
    core = package["erasure"]
    target_subject = core["target"]["subject"]
    if not REQUIRED_SUBJECT.issubset(target_subject):
        raise InputError("Retention target requires request, provider, tenant, account, objects and payload digest")
    if len(core["records"]) > MAX_RECORDS:
        raise InputError("This wrapper supports at most 256 legacy records")
    record_ids = {record["body"]["record_id"] for record in core["records"]}
    for envelope in package["retention_records"]:
        exact_keys(envelope, {"algorithm", "key_id", "body", "signature"})
        enum(envelope["algorithm"], {"Ed25519"})
        text(envelope["key_id"])
        digest_hex(envelope["signature"], 64)
        body = exact_keys(envelope["body"], {
            "record_id", "evaluation_id", "kind", "issuer", "recorded_at", "binding", "data",
        })
        for key in ("record_id", "evaluation_id", "issuer"):
            text(body[key])
        enum(body["kind"], KINDS)
        timestamp(body["recorded_at"])
        subject(body["binding"], target_subject.keys())
        if body["record_id"] in record_ids:
            raise InputError("Duplicate record identifier across retention and erasure evidence")
        record_ids.add(body["record_id"])
        _validate_data(body["kind"], body["data"])


def _deadline_state(as_of, deadline):
    if deadline is None:
        return "UNKNOWN"
    at = timestamp(deadline)
    if as_of < at:
        return "BEFORE_DECLARED_DEADLINE"
    if as_of == at:
        return "AT_DECLARED_DEADLINE"
    return "AFTER_DECLARED_DEADLINE"


def _check(envelope, core, pins, requests):
    body = envelope["body"]
    data = body["data"]
    target = core["target"]
    as_of = timestamp(core["as_of"])
    recorded = timestamp(body["recorded_at"])
    role = KINDS[body["kind"]]
    key = pins["keys"].get(envelope["key_id"])
    differences = sorted(k for k in target["subject"]
                         if canonical(body["binding"][k]) != canonical(target["subject"][k]))
    check = {
        "record_id": body["record_id"], "kind": body["kind"],
        "signature": "UNTRUSTED_KEY", "identity": "UNKNOWN", "role": "UNKNOWN",
        "key_validity": "UNKNOWN",
        "time": "FUTURE_RECORD" if recorded > as_of else "WITHIN_CUTOFF",
        "evaluation": "MATCH" if body["evaluation_id"] == core["evaluation_id"] else "MISMATCH",
        "binding": "MATCH" if not differences else "MISMATCH",
        "binding_differences": differences, "request": "NOT_ESTABLISHED", "scope": "NOT_ESTABLISHED",
        "observation_time": "NOT_APPLICABLE", "eligibility": "INELIGIBLE",
    }
    if key is not None:
        try:
            Ed25519PublicKey.from_public_bytes(bytes.fromhex(key["public_key"])).verify(
                bytes.fromhex(envelope["signature"]), signing_bytes(envelope))
            check["signature"] = "VERIFIED"
        except InvalidSignature:
            check["signature"] = "FAILED"
        expected = target["authorities"].get(role)
        check["identity"] = "EXPECTED_ISSUER" if body["issuer"] == key["issuer"] == expected else "MISMATCH"
        check["role"] = "AUTHORIZED" if role in key["roles"] else "UNAUTHORIZED"
        check["key_validity"] = ("WITHIN_VALIDITY" if timestamp(key["not_before"]) <= recorded
                                 < timestamp(key["not_after"]) else "OUTSIDE_VALIDITY")
    request = requests.get(data["request_record_id"])
    if request is not None:
        check["request"] = "MATCH" if request.recorded_at <= recorded else "RECORD_PRECEDES_REQUEST"
        locations = data["locations"] if body["kind"] == "retention.statement" else [data["location"]]
        check["scope"] = ("WITHIN_REQUEST" if set(locations).issubset(request.data["requested_locations"])
                          else "OUTSIDE_REQUEST")
    if body["kind"] == "retention.presence":
        check["observation_time"] = ("WITHIN_RECORD_TIME" if timestamp(data["observed_at"]) <= recorded
                                     else "AFTER_RECORD")
    if (check["signature"] == "VERIFIED" and check["identity"] == "EXPECTED_ISSUER"
            and check["role"] == "AUTHORIZED" and check["key_validity"] == "WITHIN_VALIDITY"
            and check["time"] == "WITHIN_CUTOFF" and check["evaluation"] == "MATCH"
            and check["binding"] == "MATCH" and check["request"] == "MATCH"
            and check["scope"] == "WITHIN_REQUEST"
            and check["observation_time"] in {"NOT_APPLICABLE", "WITHIN_RECORD_TIME"}):
        check["eligibility"] = "ELIGIBLE"
    return check


LIMITATIONS = [
    "Experimental offline adapter; no live provider, storage inspection or deletion operation.",
    "Signatures attribute statements under evaluator-supplied identity and role assumptions; they do not prove their truth or time.",
    "A source reference and digest do not retrieve or validate the referenced terms document.",
    "Processing locations, training settings, retention exceptions and presence are attributed statements, not independent measurements by this program.",
    "Only explicit timezone-bearing deadlines are compared; durations and unknown trigger times are not calculated.",
    "Later presence may reflect recreation or restoration; it does not establish continuous retention or falsity of an earlier deletion claim.",
    "The legacy erasure report remains a separate assessment; this adapter never manufactures a completion, review or ERASURE record.",
    "No independent reproduction, external anchoring, production key onboarding/revocation, legal compliance or VAP conformance is established.",
]


def assess(package, trust, *, allow_synthetic=False):
    """Assess supplied evidence only. No output is a universal deletion result."""
    _validate(package, trust)
    core = package["erasure"]
    pins = trust["erasure_trust"]
    # The original package and signatures enter the original assessor unchanged.
    erasure_report = assess_erasure(core, pins, allow_synthetic=allow_synthetic)
    _validated_records(package)
    ctx = Context(core, pins, ROLES)
    requests = {
        r.record_id: r for r in ctx.bound("erasure.request")
        if timestamp(r.data["requested_at"]) == ctx.operation_at
        and ctx.operation_at <= r.recorded_at <= ctx.as_of
    }
    attested_ids = {identifier for finding in erasure_report["findings"]
                   if finding["code"] == "ERASURE_PROVIDER_CLAIM_REMAINS_SCOPED"
                   for identifier in finding["record_ids"]}
    attestations = [r for r in ctx.bound("erasure.provider_attestation") if r.record_id in attested_ids]
    checks, statements, presence, follow_up = [], [], [], set()
    for envelope in sorted(package["retention_records"], key=lambda x: x["body"]["record_id"]):
        body = envelope["body"]
        check = _check(envelope, core, pins, requests)
        checks.append(check)
        if check["eligibility"] != "ELIGIBLE":
            continue
        data = body["data"]
        common = {"record_id": body["record_id"], "issuer": body["issuer"],
                  "recorded_at": body["recorded_at"], "request_record_id": data["request_record_id"]}
        if body["kind"] == "retention.statement":
            schedule = dict(data["schedule"])
            exceptions = [{**item, "boundary_state": _deadline_state(ctx.as_of, item["until"])}
                          for item in data["exceptions"]]
            matching_claims = [r for r in attestations
                               if r.data["request_record_id"] == data["request_record_id"]
                               and set(r.data["locations"]) & set(data["locations"])]
            covered_locations = {location for r in matching_claims for location in r.data["locations"]}
            missing_locations = sorted(set(data["locations"]) - covered_locations)
            statement = {
                **common, "evidence_basis": "AUTHENTICATED_PROVIDER_STATEMENT",
                "terms_ref": data["terms_ref"], "terms_sha256": data["terms_sha256"],
                "processing_locations": sorted(data["processing_locations"]),
                "training_use": data["training_use"], "locations": sorted(data["locations"]),
                "schedule": schedule, "deadline_state": _deadline_state(ctx.as_of, schedule.get("deadline")),
                "exceptions": sorted(exceptions, key=canonical),
                "provider_completion_claim_record_ids": sorted(r.record_id for r in matching_claims),
                "locations_without_provider_completion_claim": missing_locations,
            }
            statements.append(statement)
            if statement["deadline_state"] == "UNKNOWN":
                follow_up.add("UNKNOWN_DEADLINE")
            elif statement["deadline_state"] in {"AT_DECLARED_DEADLINE", "AFTER_DECLARED_DEADLINE"}:
                follow_up.add("RETENTION_DEADLINE_REACHED_REVIEW_REQUIRED")
                if missing_locations:
                    follow_up.add("COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF")
            if exceptions:
                follow_up.add("REPORTED_RETENTION_EXCEPTION")
        else:
            presence.append({**common, "evidence_basis": "AUTHENTICATED_COLLECTOR_STATEMENT",
                             "observed_at": data["observed_at"], "location": data["location"],
                             "method": data["method"], "limitations": list(data["limitations"])})
    if not statements:
        follow_up.add("NO_APPLICABLE_RETENTION_STATEMENT")
    if len(statements) > 1:
        follow_up.add("MULTIPLE_STATEMENTS_REQUIRE_REVIEW")
    for observation in presence:
        for statement in statements:
            deadline = statement["schedule"].get("deadline")
            if (deadline is not None and observation["location"] in statement["locations"]
                    and observation["request_record_id"] == statement["request_record_id"]
                    and timestamp(observation["observed_at"]) >= ctx.operation_at
                    and timestamp(observation["observed_at"]) >= timestamp(deadline)):
                follow_up.add("PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE")
    # Preserve scoped provider claims/reviews while flagging later presence for review.
    for attestation in attestations:
        for observation in presence:
            if (observation["request_record_id"] == attestation.data["request_record_id"]
                    and observation["location"] in attestation.data["locations"]
                    and timestamp(observation["observed_at"]) >= timestamp(attestation.data["completed_at"])):
                follow_up.add("PRESENCE_REPORTED_AT_OR_AFTER_COMPLETION_CLAIM")
    integrity = ("VERIFIED_AND_APPLICABLE_UNDER_EVALUATOR_TRUST" if checks and all(
        c["eligibility"] == "ELIGIBLE" for c in checks) else "FAILED_SIGNATURE" if any(
        c["signature"] == "FAILED" for c in checks) else "UNRESOLVED")
    return {
        "format": "retention-evidence-report/0.1", "adapter": DOMAIN, "implementation_version": VERSION,
        "evaluation_id": core["evaluation_id"], "as_of": core["as_of"],
        "synthetic": erasure_report["synthetic"], "input_sha256": digest(package),
        "trust_sha256": digest(trust), "target_sha256": digest(core["target"]),
        "retention_evidence_integrity": integrity, "record_checks": checks,
        "statements": statements, "presence_reports": presence, "follow_up_reasons": sorted(follow_up),
        "erasure_report": erasure_report, "universal_deletion": "NOT_ESTABLISHED",
        "legal_compliance": "NOT_ASSESSED", "full_vap_conformance": "NOT_ASSESSED",
        "external_anchor_verification": "NOT_IMPLEMENTED", "limitations": LIMITATIONS.copy(),
    }
