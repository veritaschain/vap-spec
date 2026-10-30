"""Scoped erasure request, receipt and review assessments, never universal erasure."""

from .model import InputError, enum, exact_keys, interval, strings, text, timestamp


KINDS = {
    "erasure.request": "responder",
    "erasure.acknowledgement": "provider",
    "erasure.provider_attestation": "provider",
    "erasure.review": "reviewer",
}
REQUIRED_SUBJECT = {"request_id", "provider_id", "tenant_id", "object_ids"}


def _nonempty_strings(value):
    strings(value)
    if not value:
        raise InputError("Evidence identifiers, locations and review limitations cannot be empty")


def validate_data(kind, data):
    if kind == "erasure.request":
        exact_keys(data, {"requested_at", "requested_locations"})
        timestamp(data["requested_at"])
        _nonempty_strings(data["requested_locations"])
    elif kind == "erasure.acknowledgement":
        exact_keys(data, {"request_record_id", "acknowledged_at", "queue_state"})
        text(data["request_record_id"])
        timestamp(data["acknowledged_at"])
        enum(data["queue_state"], {"received", "queued"})
    elif kind == "erasure.provider_attestation":
        exact_keys(data, {"request_record_id", "completed_at", "locations", "exclusions"})
        text(data["request_record_id"])
        timestamp(data["completed_at"])
        _nonempty_strings(data["locations"])
        strings(data["exclusions"])
        if set(data["locations"]) & set(data["exclusions"]):
            raise InputError("An attestation location cannot also be explicitly excluded")
    elif kind == "erasure.review":
        exact_keys(data, {"request_record_id", "attestation_record_id", "method", "evidence_record_ids",
                          "window_start", "window_end", "locations", "limitations", "conclusion"})
        for name in ("request_record_id", "attestation_record_id", "method"):
            text(data[name])
        for name in ("evidence_record_ids", "locations", "limitations"):
            _nonempty_strings(data[name])
        interval(data["window_start"], data["window_end"])
        enum(data["conclusion"], {"deletion-observed", "inconclusive"})
    else:
        raise InputError("Unsupported erasure kind")


def _timed(ctx, record, field, earliest):
    at = timestamp(record.data[field])
    if earliest <= at <= record.recorded_at <= ctx.as_of:
        return True
    ctx.finding("ERASURE_EVIDENCE_TIME_INAPPLICABLE", record)
    return False


def evaluate(ctx):
    missing = REQUIRED_SUBJECT - ctx.subject.keys()
    if missing:
        raise InputError("Erasure target lacks fields: " + repr(sorted(missing)))
    result = {
        "deletion_evidence": "UNKNOWN", "provider_completion": "UNKNOWN",
        "independent_verification": "NOT_ESTABLISHED", "excluded_scope_outcome": "UNKNOWN",
        "outside_scope_outcome": "UNKNOWN", "target_completion": "UNKNOWN",
        "receipt_applicability": "NOT_ESTABLISHED", "binding_assessment": "UNRESOLVED",
        "review_result": "NOT_ESTABLISHED",
    }
    if ctx.operation_at > ctx.as_of:
        ctx.finding("ERASURE_OPERATION_AFTER_AS_OF")
        return result

    requests = {}
    for record in ctx.bound("erasure.request"):
        requested_at = timestamp(record.data["requested_at"])
        if requested_at == ctx.operation_at and _timed(ctx, record, "requested_at", ctx.operation_at):
            requests[record.record_id] = record
        else:
            ctx.finding("ERASURE_REQUEST_TIME_DOES_NOT_BIND_OPERATION", record)
    if requests:
        result["deletion_evidence"] = "REQUEST_ONLY"
        result["binding_assessment"] = "MATCH"
        ctx.finding("ERASURE_LOCAL_REQUEST_ESTABLISHED", *requests.values())

    acknowledgements = {}
    for record in ctx.bound("erasure.acknowledgement"):
        request = requests.get(record.data["request_record_id"])
        if request is None:
            ctx.finding("ERASURE_ACKNOWLEDGEMENT_REQUEST_NOT_ESTABLISHED", record)
            continue
        if (not _timed(ctx, record, "acknowledged_at", timestamp(request.data["requested_at"]))
                or request.recorded_at > record.recorded_at):
            continue
        acknowledgements[record.record_id] = record
        ctx.finding("ERASURE_ACKNOWLEDGEMENT_IS_NOT_COMPLETION", request, record)
    if acknowledgements:
        result["deletion_evidence"] = "ACKNOWLEDGED"
        result["receipt_applicability"] = "MATCHED_WITHIN_DECLARED_SCOPE"

    attestations = {}
    for record in ctx.bound("erasure.provider_attestation"):
        request = requests.get(record.data["request_record_id"])
        if request is None:
            ctx.finding("ERASURE_ATTESTATION_REQUEST_NOT_ESTABLISHED", record)
            continue
        if (not _timed(ctx, record, "completed_at", timestamp(request.data["requested_at"]))
                or request.recorded_at > record.recorded_at):
            continue
        if not set(record.data["locations"]).issubset(request.data["requested_locations"]):
            ctx.finding("ERASURE_ATTESTATION_LOCATIONS_OUTSIDE_REQUEST", request, record)
            continue
        attestations[record.record_id] = record
        ctx.finding("ERASURE_PROVIDER_CLAIM_REMAINS_SCOPED", request, record)
    if attestations:
        result["deletion_evidence"] = "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE"
        result["receipt_applicability"] = "MATCHED_WITHIN_DECLARED_SCOPE"

    mismatched = []
    for kind in ("erasure.acknowledgement", "erasure.provider_attestation"):
        for record in ctx.records(kind):
            differences = set(ctx.differences(record))
            if differences:
                mismatched.append((record, differences))
                ctx.finding("ERASURE_RECEIPT_BINDING_MISMATCH", record)
    if mismatched and not (acknowledgements or attestations):
        result["receipt_applicability"] = "UNUSABLE_FOR_TARGET_CLAIM"
        if any({"object_ids", "tenant_id"}.issubset(fields) for _, fields in mismatched):
            result["binding_assessment"] = "OBJECT_AND_TENANT_MISMATCH"
        else:
            result["binding_assessment"] = "TARGET_BINDING_MISMATCH"

    provider_org = ctx.organization_for("provider")
    requester_org = ctx.organization_for("responder")
    evidence = {**requests, **acknowledgements, **attestations}
    supported_reviews = []
    inconclusive_reviews = []
    for review in ctx.bound("erasure.review"):
        request = requests.get(review.data["request_record_id"])
        attestation = attestations.get(review.data["attestation_record_id"])
        if request is None or attestation is None:
            ctx.finding("ERASURE_REVIEW_REFERENCED_EVIDENCE_NOT_ESTABLISHED", review)
            continue
        if attestation.data["request_record_id"] != request.record_id:
            ctx.finding("ERASURE_REVIEW_REQUEST_ATTESTATION_LINK_MISMATCH", review, request, attestation)
            continue
        if (provider_org is None or requester_org is None or request.organization != requester_org
                or attestation.organization != provider_org
                or review.organization in {provider_org, requester_org, request.organization}):
            ctx.finding("ERASURE_REVIEW_ORGANIZATIONAL_INDEPENDENCE_NOT_ESTABLISHED", review, request, attestation)
            continue
        left, right = interval(review.data["window_start"], review.data["window_end"])
        completed_at = timestamp(attestation.data["completed_at"])
        if not (ctx.operation_at <= left <= completed_at < right <= review.recorded_at <= ctx.as_of):
            ctx.finding("ERASURE_REVIEW_TIME_WINDOW_INAPPLICABLE", review, attestation)
            continue
        cited_ids = set(review.data["evidence_record_ids"])
        if not {request.record_id, attestation.record_id}.issubset(cited_ids):
            ctx.finding("ERASURE_REVIEW_DOES_NOT_CITE_REQUIRED_EVIDENCE", review)
            continue
        cited = [evidence[identifier] for identifier in cited_ids if identifier in evidence]
        if len(cited) != len(cited_ids) or any(r.recorded_at > right for r in cited):
            ctx.finding("ERASURE_REVIEW_EVIDENCE_SET_NOT_ESTABLISHED_BY_CUTOFF", review)
            continue
        if not set(review.data["locations"]).issubset(attestation.data["locations"]):
            ctx.finding("ERASURE_REVIEW_LOCATIONS_EXCEED_PROVIDER_CLAIM", review, attestation)
            continue
        if review.data["conclusion"] != "deletion-observed":
            ctx.finding("ERASURE_INDEPENDENT_REVIEW_INCONCLUSIVE", review)
            inconclusive_reviews.append(review)
            continue
        supported_reviews.append(review)
        ctx.finding("ERASURE_INDEPENDENT_REVIEW_REMAINS_SCOPED", review, *cited)
    if supported_reviews and not inconclusive_reviews:
        result["deletion_evidence"] = "INDEPENDENTLY_REVIEWED_WITHIN_DECLARED_SCOPE"
        result["independent_verification"] = "ESTABLISHED_WITHIN_REVIEW_METHOD_AND_SCOPE"
        result["review_result"] = "SUPPORTED_WITHIN_REVIEW_METHOD_AND_LIMITATIONS"
    elif inconclusive_reviews:
        result["review_result"] = "INCONCLUSIVE_OR_CONFLICTING_REVIEWS" if supported_reviews else "INCONCLUSIVE"
        ctx.finding("ERASURE_UNQUALIFIED_REVIEW_PROMOTION_WITHHELD", *supported_reviews, *inconclusive_reviews)
    return result
