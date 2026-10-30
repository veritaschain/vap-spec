"""Bound information requests and containment records, with explicit evidence gaps."""

from .evidence import digest
from .model import InputError, boolean, digest_hex, enum, exact_keys, interval, strings, text, timestamp

KINDS = {
    "info_request": "reviewer",
    "info_receipt": "recipient",
    "info_response": "recipient",
    "containment_action": "responder",
    "containment_anchor_claim": "collector",
}
TARGET_FIELDS = {"request_id", "object_ids", "provider_id", "tenant_id"}


def validate_data(kind, data):
    if kind == "info_request":
        exact_keys(data, {"questions", "requested_at", "observation_cutoff", "authority_basis"})
        strings(data["questions"])
        if not data["questions"]:
            raise InputError("Information requests require at least one question")
        interval(data["requested_at"], data["observation_cutoff"])
        text(data["authority_basis"])
    elif kind == "info_receipt":
        exact_keys(data, {"received_at", "request_record_id"})
        timestamp(data["received_at"])
        text(data["request_record_id"])
    elif kind == "info_response":
        exact_keys(data, {"responded_at", "request_record_id", "status", "answers"})
        timestamp(data["responded_at"])
        text(data["request_record_id"])
        enum(data["status"], {"complete", "partial"})
        if type(data["answers"]) is not list or not data["answers"]:
            raise InputError("A substantive response requires a nonempty answers array")
        questions = []
        for answer in data["answers"]:
            exact_keys(answer, {"question", "answer"})
            text(answer["question"])
            text(answer["answer"])
            questions.append(answer["question"])
        strings(questions)
    elif kind == "containment_action":
        exact_keys(data, {"decision_at", "removal_observed_at", "authority_basis", "source_account_id", "urgency",
                          "delay_justified", "minimum_evidence_available", "unavailable_material", "access_constraints", "retention_basis"})
        timestamp(data["decision_at"])
        timestamp(data["removal_observed_at"])
        if timestamp(data["decision_at"]) > timestamp(data["removal_observed_at"]):
            raise InputError("Containment decision cannot follow its reported action")
        for field in ("authority_basis", "source_account_id", "retention_basis"):
            text(data[field])
        enum(data["urgency"], {"urgent", "routine"})
        boolean(data["delay_justified"])
        boolean(data["minimum_evidence_available"])
        strings(data["unavailable_material"])
        strings(data["access_constraints"])
        if not data["minimum_evidence_available"] and not data["unavailable_material"]:
            raise InputError("Unavailable preservation needs an identified evidence gap")
    elif kind == "containment_anchor_claim":
        exact_keys(data, {"anchor_time", "record_ids", "format", "material_sha256"})
        timestamp(data["anchor_time"])
        strings(data["record_ids"])
        if not data["record_ids"]:
            raise InputError("Anchor claim must identify its records")
        text(data["format"])
        digest_hex(data["material_sha256"])
    else:
        raise InputError("Unsupported incident-response record kind")


def _time_ok(ctx, record, field):
    event = timestamp(record.data[field])
    if event > record.recorded_at or event > ctx.as_of:
        ctx.finding("incident_response_event_time_inapplicable", record)
        return False
    return True


def _information(ctx, result):
    requests = []
    for record in ctx.bound("info_request"):
        if not _time_ok(ctx, record, "requested_at"):
            continue
        if timestamp(record.data["requested_at"]) != ctx.operation_at:
            ctx.finding("info_request_target_operation_time_mismatch", record)
            continue
        requests.append(record)
    if len(requests) != 1:
        ctx.finding("info_request_missing_or_ambiguous", *requests)
        return
    request = requests[0]
    requested = timestamp(request.data["requested_at"])
    cutoff = min(timestamp(request.data["observation_cutoff"]), ctx.as_of)
    if request.recorded_at > cutoff:
        ctx.finding("info_request_not_recorded_by_cutoff", request)
        return
    result["request_status"] = "REQUEST_RECORDED"
    ctx.finding("info_recording_request_does_not_create_compulsion_authority", request)
    receipts = []
    for record in ctx.bound("info_receipt"):
        if record.data["request_record_id"] != request.record_id:
            ctx.finding("info_receipt_request_reference_mismatch", record)
            continue
        if not _time_ok(ctx, record, "received_at"):
            continue
        received = timestamp(record.data["received_at"])
        if received < requested:
            ctx.finding("info_receipt_predates_request", record, request)
        elif received <= cutoff and record.recorded_at <= cutoff:
            receipts.append(record)
        else:
            ctx.finding("info_receipt_not_available_by_cutoff", record)
    if receipts:
        result["request_delivery"] = "RECEIPT_ESTABLISHED_UNDER_GIVEN_ASSUMPTIONS"
        ctx.finding("info_request_receipt_is_not_answer", *receipts)

    responses, later = [], []
    for record in ctx.bound("info_response"):
        if record.data["request_record_id"] != request.record_id:
            ctx.finding("info_response_request_reference_mismatch", record)
            continue
        if not _time_ok(ctx, record, "responded_at"):
            continue
        responded = timestamp(record.data["responded_at"])
        if responded < requested:
            ctx.finding("info_response_predates_request", record, request)
            continue
        answered = {a["question"] for a in record.data["answers"]}
        if not answered <= set(request.data["questions"]):
            ctx.finding("info_response_questions_outside_request", record, request)
            continue
        if responded <= cutoff and record.recorded_at <= cutoff:
            responses.append(record)
        else:
            later.append(record)
    if responses:
        complete = [r for r in responses if r.data["status"] == "complete"
                    and {a["question"] for a in r.data["answers"]} == set(request.data["questions"])]
        result["response_status"] = "COMPLETE_RESPONSE_RECORDED_BY_CUTOFF" if complete else "PARTIAL_RESPONSE_RECORDED_BY_CUTOFF"
        ctx.finding("info_response_content_remains_recipient_assertions", *responses)
    else:
        result["response_status"] = ("NO_RESPONSE_OBSERVED_BY_CUTOFF" if timestamp(request.data["observation_cutoff"]) <= ctx.as_of
                                     else "NO_RESPONSE_OBSERVED_AS_OF_EVALUATION")
        ctx.finding("info_missing_response_does_not_establish_requested_facts_or_refusal", request)
    if later:
        result["later_response_status"] = "RECORDED_AFTER_CUTOFF"
        ctx.finding("info_later_response_preserves_earlier_cutoff_observation", *later)
    # Receipt and response authenticity do not decide the truth of answers.


def _containment(ctx, result):
    actions = []
    for record in ctx.bound("containment_action"):
        if record.data["source_account_id"] != ctx.subject.get("account_id"):
            ctx.finding("containment_source_account_mismatch", record)
            continue
        if timestamp(record.data["removal_observed_at"]) != ctx.operation_at:
            ctx.finding("containment_target_operation_time_mismatch", record)
            continue
        if _time_ok(ctx, record, "removal_observed_at"):
            actions.append(record)
    if len({digest(r.data) for r in actions}) > 1:
        ctx.finding("containment_conflicting_records_require_review", *actions)
        return
    if not actions:
        return
    action = actions[0]
    data = action.data
    result["containment_action"] = ("AUTHORIZED_HISTORY_REMOVAL_RECORDED" if data["urgency"] == "urgent" and not data["delay_justified"]
                                    else "HISTORY_REMOVAL_RECORDED_REQUIRES_REVIEW")
    ctx.finding("containment_scope_and_authority_are_recorded_assertions", action)
    if not data["minimum_evidence_available"]:
        result["preservation_status"] = "MINIMUM_HISTORY_UNAVAILABLE"
        result["evidence_gap"] = "SOURCE_TIME_AND_UNAVAILABLE_MATERIAL_RECORDED"
        ctx.finding("containment_missing_preservation_remains_evidence_gap", action)
    else:
        result["preservation_status"] = "AVAILABILITY_REPORTED_WITHOUT_PRESERVATION_PROOF"
    removal = timestamp(data["removal_observed_at"])
    for record in ctx.bound("containment_anchor_claim"):
        if action.record_id not in record.data["record_ids"]:
            ctx.finding("containment_anchor_record_reference_mismatch", record)
            continue
        if not _time_ok(ctx, record, "anchor_time"):
            continue
        ctx.finding("containment_external_anchor_material_not_verified", record)
        if timestamp(record.data["anchor_time"]) > removal:
            result["capture_timing"] = "LATER_ANCHOR_DOES_NOT_ESTABLISH_CONTEMPORANEOUS_CAPTURE"
            ctx.finding("containment_later_anchor_cannot_reconstruct_missing_history", action, record)


def evaluate(ctx):
    result = {
        "request_delivery": "UNKNOWN",
        "response_status": "UNKNOWN",
        "requested_facts": "UNKNOWN",
        "reason_for_absent_response": "UNKNOWN",
        "containment_action": "UNKNOWN",
        "preservation_status": "UNKNOWN",
        "evidence_gap": "UNKNOWN",
        "missing_history_and_downstream_activity": "UNKNOWN",
        "capture_timing": "NOT_INDEPENDENTLY_ESTABLISHED",
        "anchor_verification": "NOT_SUPPORTED",
    }
    if not TARGET_FIELDS <= ctx.subject.keys():
        ctx.finding("incident_response_target_incomplete")
        return result
    if ctx.records("info_request") or ctx.records("info_receipt") or ctx.records("info_response"):
        _information(ctx, result)
    _containment(ctx, result)
    return result
