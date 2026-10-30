"""Offline assessment of explicitly bound publication evidence, not editorial approval."""

import hashlib

from .evidence import digest
from .model import InputError, boolean, digest_hex, enum, exact_keys, interval, strings, text, timestamp

ACTIVITIES = {"generation", "substantive_editing", "proofreading", "translation", "code_review", "figure_generation"}
CATEGORIES = {"text", "figure", "code"}
POLICY_FIELDS = ("policy_id", "policy_version", "policy_sha256", "stage")
TARGET_FIELDS = {"request_id", "artifact_id", "revision_id", "payload_sha256", "disclosure_sha256", *POLICY_FIELDS}
KINDS = {
    "publication_policy": "policy",
    "publication_manifest": "collector",
    "publication_activity": "collector",
    "publication_coverage": "collector",
    "publication_disclosure": "author",
    "publication_declaration": "author",
    "publication_approval": "reviewer",
    "publication_dispatch": "gateway",
    "publication_receipt": "recipient",
}


def _choices(values, choices):
    strings(values)
    for value in values:
        enum(value, choices)


def _component(component):
    exact_keys(component, {"artifact_id", "revision_id", "sha256", "category"})
    text(component["artifact_id"])
    text(component["revision_id"])
    digest_hex(component["sha256"])
    enum(component["category"], CATEGORIES)


def validate_data(kind, data):
    if kind == "publication_policy":
        exact_keys(data, {"effective_from", "effective_until", "prohibited_activities", "disclosure_categories", "approval_required", "interpretation"})
        interval(data["effective_from"], data["effective_until"])
        _choices(data["prohibited_activities"], ACTIVITIES)
        _choices(data["disclosure_categories"], CATEGORIES)
        boolean(data["approval_required"])
        enum(data["interpretation"], {"resolved", "unresolved"})
    elif kind == "publication_manifest":
        exact_keys(data, {"observed_at", "components"})
        timestamp(data["observed_at"])
        if type(data["components"]) is not list or not data["components"]:
            raise InputError("Publication components require a nonempty array")
        identifiers = []
        for component in data["components"]:
            _component(component)
            identifiers.append(component["artifact_id"])
        strings(identifiers)
    elif kind == "publication_activity":
        exact_keys(data, {"activity", "observed_at", "adoption_basis", "included_in_artifact_sha256", "component"})
        enum(data["activity"], ACTIVITIES)
        timestamp(data["observed_at"])
        enum(data["adoption_basis"], {"observed_in_artifact", "unresolved"})
        digest_hex(data["included_in_artifact_sha256"])
        _component(data["component"])
    elif kind == "publication_coverage":
        exact_keys(data, {"scope", "from", "until"})
        enum(data["scope"], {"declared_editor_only", "incomplete"})
        interval(data["from"], data["until"])
    elif kind == "publication_disclosure":
        exact_keys(data, {"categories", "prepared_at", "text"})
        _choices(data["categories"], CATEGORIES)
        timestamp(data["prepared_at"])
        text(data["text"])
    elif kind == "publication_declaration":
        exact_keys(data, {"activities", "declared_at"})
        _choices(data["activities"], ACTIVITIES)
        timestamp(data["declared_at"])
    elif kind == "publication_approval":
        exact_keys(data, {"valid_from", "valid_until", "approval"})
        interval(data["valid_from"], data["valid_until"])
        enum(data["approval"], {"approved"})
    elif kind == "publication_dispatch":
        exact_keys(data, {"attempted_at"})
        timestamp(data["attempted_at"])
    elif kind == "publication_receipt":
        exact_keys(data, {"received_at", "status"})
        timestamp(data["received_at"])
        enum(data["status"], {"received", "accepted"})
    else:
        raise InputError("Unsupported publication record kind")


def _event_eligible(ctx, record, field, *, before_operation=False, after_operation=False):
    event = timestamp(record.data[field])
    if (event > record.recorded_at or event > ctx.as_of or (before_operation and event > ctx.operation_at)
            or (after_operation and event < ctx.operation_at)):
        ctx.finding("publication_event_time_inapplicable", record)
        return False
    return True


def _policy(ctx):
    candidates = []
    for record in ctx.records("publication_policy"):
        if not ctx.matches(record, POLICY_FIELDS):
            ctx.finding("publication_policy_binding_mismatch", record)
            continue
        if digest(record.data) != record.binding["policy_sha256"]:
            ctx.finding("publication_policy_content_digest_mismatch", record)
            continue
        if record.recorded_at > ctx.operation_at:
            ctx.finding("publication_policy_historical_availability_not_established", record)
            continue
        start, end = interval(record.data["effective_from"], record.data["effective_until"])
        if not start <= ctx.operation_at < end:
            ctx.finding("publication_policy_outside_effective_interval", record)
            continue
        candidates.append(record)
    # The target pins the whole rule document's digest; eligible duplicates have
    # the same rule content. No newest-policy or most-permissive selection occurs.
    return candidates[0] if candidates else None


def evaluate(ctx):
    result = {
        "publication_action": "REVIEW",
        "policy_assessment": "UNKNOWN",
        "policy_applicability": "UNRESOLVED",
        "evidence_integrity": "ESTABLISHED_UNDER_GIVEN_ASSUMPTIONS" if ctx.integrity_established else "NOT_ESTABLISHED",
        "ai_involvement": "UNKNOWN",
        "coverage": "UNKNOWN",
        "approval_applicability": "NOT_ESTABLISHED",
        "disclosure_assessment": "UNKNOWN",
        "evidence_retention": "PRESERVE_PER_STAGE_POLICY_AND_REVISION_BINDINGS",
        "evidence_basis": "UNKNOWN",
        "declarant_attribution": "NOT_ESTABLISHED",
        "activity_completeness": "UNKNOWN",
        "disclosure_preparation": "NOT_ESTABLISHED",
        "dispatch_observation": "NOT_ESTABLISHED",
        "delivery_status": "UNCONFIRMED",
        "acceptance_status": "UNKNOWN",
    }
    if not TARGET_FIELDS <= ctx.subject.keys() or ctx.operation_at > ctx.as_of:
        ctx.finding("publication_target_missing_or_operation_future")
        return result

    coverage = []
    for record in ctx.bound("publication_coverage"):
        start, end = interval(record.data["from"], record.data["until"])
        if start <= ctx.operation_at < end and start <= record.recorded_at:
            coverage.append(record)
    if coverage:
        result["coverage"] = "INCOMPLETE"
        ctx.finding("publication_capture_excludes_other_activity", *coverage)

    expected_document = {"artifact_id": ctx.subject["artifact_id"], "revision_id": ctx.subject["revision_id"],
                         "sha256": ctx.subject["payload_sha256"], "category": "text"}
    manifests = [r for r in ctx.bound("publication_manifest")
                 if _event_eligible(ctx, r, "observed_at", before_operation=True)
                 and expected_document in r.data["components"]]
    manifest_contents = {digest(r.data["components"]) for r in manifests}
    if len(manifest_contents) > 1:
        ctx.finding("publication_conflicting_component_manifests", *manifests)
        manifests = []
    activities = []
    for record in ctx.bound("publication_activity"):
        if not _event_eligible(ctx, record, "observed_at", before_operation=True):
            continue
        if (record.data["included_in_artifact_sha256"] != ctx.subject["payload_sha256"]
                or record.data["adoption_basis"] != "observed_in_artifact"
                or not any(record.data["component"] in m.data["components"] for m in manifests)):
            ctx.finding("publication_activity_adoption_not_established", record)
            continue
        activities.append(record)
    if activities:
        result["ai_involvement"] = "OBSERVED_UNDER_GIVEN_ASSUMPTIONS"
        result["evidence_basis"] = "INSTRUMENTED_OBSERVATION"
        ctx.finding("publication_activity_bound_to_artifact", *activities)
    else:
        ctx.finding("publication_missing_observation_is_not_human_only")

    declarations = [r for r in ctx.bound("publication_declaration") if _event_eligible(ctx, r, "declared_at")]
    if declarations:
        result["declarant_attribution"] = "ESTABLISHED_UNDER_GIVEN_ASSUMPTIONS"
        result["evidence_basis"] = "OBSERVED_AND_SELF_DECLARED" if activities else "SELF_DECLARED"
        ctx.finding("publication_self_declaration_does_not_establish_completeness", *declarations)
        if activities and any(not {a.data["activity"] for a in activities} <= set(d.data["activities"]) for d in declarations):
            result["declaration_consistency"] = "CONTRADICTED_BY_OBSERVED_ACTIVITY"
            ctx.finding("publication_declaration_omits_observed_activity", *declarations, *activities)

    disclosures = []
    for record in ctx.bound("publication_disclosure"):
        if not _event_eligible(ctx, record, "prepared_at", before_operation=True):
            continue
        actual_digest = hashlib.sha256(record.data["text"].encode("utf-8")).hexdigest()
        if actual_digest != ctx.subject["disclosure_sha256"]:
            ctx.finding("publication_disclosure_text_digest_mismatch", record)
            continue
        disclosures.append(record)
    if disclosures:
        result["disclosure_preparation"] = "RECORDED"
        result["disclosure_assessment"] = "REQUIRES_CONTENT_REVIEW"
        ctx.finding("publication_preparation_is_not_delivery", *disclosures)

    policy = _policy(ctx)
    if policy is None:
        ctx.finding("publication_applicable_policy_not_established")
    elif policy.data["interpretation"] == "unresolved":
        ctx.finding("publication_stage_or_interpretation_unresolved", policy)
    else:
        result["policy_applicability"] = "BOUND_AND_EFFECTIVE_UNDER_GIVEN_ASSUMPTIONS"
        prohibited = [a for a in activities if a.data["activity"] in policy.data["prohibited_activities"]]
        if prohibited:
            result["publication_action"] = "BLOCK"
            result["policy_assessment"] = "PROHIBITED_USE"
            ctx.finding("publication_disclosure_does_not_override_prohibition", policy, *prohibited)
        required = {a.data["component"]["category"] for a in activities} & set(policy.data["disclosure_categories"])
        if required and (not disclosures or any(not required <= set(d.data["categories"]) for d in disclosures)):
            result["disclosure_assessment"] = "INCOMPLETE"
            ctx.finding("publication_disclosure_omits_required_observed_components", policy, *activities, *disclosures)

    prior_approvals, current_approvals = [], []
    for record in ctx.records("publication_approval"):
        start, end = interval(record.data["valid_from"], record.data["valid_until"])
        if not start <= ctx.operation_at < end or record.recorded_at > ctx.operation_at:
            ctx.finding("publication_approval_time_inapplicable", record)
            continue
        differences = set(ctx.differences(record))
        if not differences:
            current_approvals.append(record)
        elif differences <= {"revision_id", "payload_sha256", "disclosure_sha256"}:
            prior_approvals.append(record)
        else:
            ctx.finding("publication_approval_binding_mismatch", record)
    if current_approvals:
        result["approval_applicability"] = "BOUND_APPROVAL_RECORDED"
        ctx.finding("publication_approval_not_publisher_acceptance", *current_approvals)
    elif prior_approvals:
        result["approval_applicability"] = "PRIOR_REVISION_ONLY"
        ctx.finding("publication_approval_requires_changed_artifact_reassessment", *prior_approvals)
    elif policy and policy.data["approval_required"]:
        ctx.finding("publication_required_approval_not_established", policy)

    dispatches = [r for r in ctx.bound("publication_dispatch") if _event_eligible(ctx, r, "attempted_at", after_operation=True)]
    if dispatches:
        result["dispatch_observation"] = "ATTEMPT_RECORDED"
        ctx.finding("publication_dispatch_is_not_receipt", *dispatches)
    receipts = []
    first_dispatch = min((timestamp(r.data["attempted_at"]) for r in dispatches), default=ctx.operation_at)
    for record in ctx.bound("publication_receipt"):
        if not _event_eligible(ctx, record, "received_at", after_operation=True):
            continue
        if timestamp(record.data["received_at"]) < first_dispatch:
            ctx.finding("publication_receipt_predates_bound_dispatch", record, *dispatches)
            continue
        receipts.append(record)
    if receipts:
        result["delivery_status"] = "RECIPIENT_ASSERTED_RECEIPT"
        ctx.finding("publication_receipt_supports_only_stated_scope", *receipts)
        if any(r.data["status"] == "accepted" for r in receipts):
            result["acceptance_status"] = "RECIPIENT_ASSERTED_ACCEPTANCE"
    # This prototype never emits automatic publication permission, human-only
    # authorship, complete provenance, or a legal/institutional determination.
    return result
