"""Bound transfer evidence assessments; this module performs no network actions."""

from .evidence import digest
from .model import InputError, boolean, exact_keys, interval, strings, text, timestamp


KINDS = {
    "transfer.policy": "policy",
    "transfer.decision": "gateway",
    "transfer.dispatch": "gateway",
    "transfer.egress": "collector",
    "transfer.coverage": "collector",
    "transfer.collector_health": "gateway",
    "transfer.timeout": "gateway",
}
GRANT_FIELDS = (
    "actor_id", "provider_id", "endpoint", "tenant_id", "account_id", "purpose", "route_id",
)
POLICY_FIELDS = ("policy_id", "policy_version", "policy_sha256", "stage")
REQUIRED_SUBJECT = {"request_id", "payload_sha256", *GRANT_FIELDS, *POLICY_FIELDS}


def validate_data(kind, data):
    if kind == "transfer.policy":
        exact_keys(data, {"effective_from", "effective_until", "grants", "require_collector"})
        interval(data["effective_from"], data["effective_until"])
        boolean(data["require_collector"])
        if type(data["grants"]) is not list or len(data["grants"]) > 10000:
            raise InputError("Policy grants must be a bounded array")
        seen = set()
        for grant in data["grants"]:
            exact_keys(grant, GRANT_FIELDS)
            for name in GRANT_FIELDS:
                text(grant[name])
            fingerprint = digest(grant)
            if fingerprint in seen:
                raise InputError("Duplicate policy grant")
            seen.add(fingerprint)
    elif kind == "transfer.decision":
        exact_keys(data, {"decision", "valid_from", "valid_until"})
        if data["decision"] not in ("permit", "deny"):
            raise InputError("Transfer decision must be permit or deny")
        interval(data["valid_from"], data["valid_until"])
    elif kind in ("transfer.dispatch", "transfer.egress", "transfer.timeout"):
        field = {"transfer.dispatch": "dispatched_at", "transfer.egress": "observed_at",
                 "transfer.timeout": "timed_out_at"}[kind]
        exact_keys(data, {field})
        timestamp(data[field])
    elif kind == "transfer.coverage":
        exact_keys(data, {"window_start", "window_end", "covered_routes", "complete", "dispatch_observed"})
        interval(data["window_start"], data["window_end"])
        strings(data["covered_routes"])
        boolean(data["complete"])
        boolean(data["dispatch_observed"])
    elif kind == "transfer.collector_health":
        exact_keys(data, {"checked_at", "available", "durable_acknowledged"})
        timestamp(data["checked_at"])
        boolean(data["available"])
        boolean(data["durable_acknowledged"])
        if not data["available"] and data["durable_acknowledged"]:
            raise InputError("Unavailable collector cannot acknowledge durable collection")
    else:
        raise InputError("Unsupported transfer kind")


def _within(record, at, left, right):
    start, end = interval(record.data[left], record.data[right])
    return record.recorded_at <= at and start <= at < end


def _policy(ctx, at):
    current = []
    for record in ctx.bound("transfer.policy", POLICY_FIELDS):
        if digest(record.data) != ctx.subject["policy_sha256"]:
            ctx.finding("TRANSFER_POLICY_CONTENT_DIGEST_MISMATCH", record)
            continue
        if not _within(record, at, "effective_from", "effective_until"):
            ctx.finding("TRANSFER_POLICY_NOT_EFFECTIVE_AT_OPERATION", record)
            continue
        current.append(record)
    return max(current, key=lambda r: (r.recorded_at, r.record_id)) if current else None


def _decision(ctx, at):
    candidates = [r for r in ctx.bound("transfer.decision")
                  if _within(r, at, "valid_from", "valid_until")]
    if not candidates:
        return None, False
    latest = max(r.recorded_at for r in candidates)
    current = [r for r in candidates if r.recorded_at == latest]
    if len({r.data["decision"] for r in current}) != 1:
        ctx.finding("TRANSFER_CONFLICTING_CURRENT_DECISIONS", *current)
        return None, True
    return min(current, key=lambda r: r.record_id), False


def _grant_matches(ctx, policy):
    return any(all(grant[name] == ctx.subject[name] for name in GRANT_FIELDS)
               for grant in policy.data["grants"])


def _grant_failure(ctx, policy):
    grants = policy.data["grants"]
    dimensions = (
        ("tenant_id", "TENANT_MISMATCH"), ("account_id", "ACCOUNT_MISMATCH"),
        ("actor_id", "ACTOR_MISMATCH"), ("purpose", "PURPOSE_MISMATCH"),
        ("route_id", "ROUTE_MISMATCH"), ("endpoint", "ENDPOINT_NOT_APPROVED"),
        ("provider_id", "PROVIDER_NOT_APPROVED"),
    )
    for dimension, label in dimensions:
        if any(grant[dimension] != ctx.subject[dimension]
               and all(grant[name] == ctx.subject[name] for name in GRANT_FIELDS if name != dimension)
               for grant in grants):
            return label
    return "NO_MATCHING_APPROVAL"


def _events(ctx, kind, field):
    selected = []
    for record in ctx.bound(kind):
        at = timestamp(record.data[field])
        if ctx.operation_at <= at <= record.recorded_at <= ctx.as_of:
            selected.append(record)
        else:
            ctx.finding("TRANSFER_EVENT_TIME_INAPPLICABLE", record)
    return selected


def _health_at(ctx, at):
    health = []
    for record in ctx.bound("transfer.collector_health"):
        checked_at = timestamp(record.data["checked_at"])
        if checked_at == at and checked_at <= record.recorded_at <= ctx.as_of:
            health.append(record)
    unavailable = [r for r in health if not r.data["available"] or not r.data["durable_acknowledged"]]
    return health, unavailable


def evaluate(ctx):
    missing = REQUIRED_SUBJECT - ctx.subject.keys()
    if missing:
        raise InputError("Transfer target lacks fields: " + repr(sorted(missing)))
    result = {
        "transfer_authorization": "UNKNOWN", "transfer_observation": "UNKNOWN",
        "coverage": "INCOMPLETE", "binding_assessment": "UNRESOLVED",
        "policy_binding": "EXPIRED_OR_UNRESOLVED",
        "dispatch_action": "HOLD_PENDING_CURRENT_AUTHORIZATION",
        "control_assessment": "UNKNOWN", "remote_outcome": "UNKNOWN",
        "retry_action": "NOT_ASSESSED", "collector_health": "UNKNOWN",
        "application_route_action": "REVIEW", "external_activity_assessment": "UNKNOWN",
        "proposed_transfer_authorization": "UNKNOWN", "observed_action_authorization": "UNKNOWN",
    }
    if ctx.operation_at > ctx.as_of:
        ctx.finding("TRANSFER_OPERATION_AFTER_AS_OF")
        return result

    policy = _policy(ctx, ctx.operation_at)
    decision, conflict = _decision(ctx, ctx.operation_at)
    allowed_by_registry = policy is not None and _grant_matches(ctx, policy)
    if policy is not None:
        result["policy_binding"] = "CURRENT_CONTENT_BOUND"
    if policy is not None and not allowed_by_registry:
        result["transfer_authorization"] = "DENY"
        result["binding_assessment"] = _grant_failure(ctx, policy)
        ctx.finding("TRANSFER_APPROVAL_REGISTRY_DOES_NOT_AUTHORIZE_TARGET", policy)
    elif decision is not None and decision.data["decision"] == "deny":
        result["transfer_authorization"] = "DENY"
        result["binding_assessment"] = "MATCH"
        ctx.finding("TRANSFER_BOUND_DENIAL", decision)
    elif policy is not None and allowed_by_registry and decision is not None and not conflict:
        result["transfer_authorization"] = "ALLOW"
        result["binding_assessment"] = "MATCH"
        result["dispatch_action"] = "PERMITTED_WITHIN_BOUND_SCOPE"
        result["application_route_action"] = "PERMITTED_WITHIN_BOUND_SCOPE"
        ctx.finding("TRANSFER_CURRENT_POLICY_AND_PERMIT_BIND_TARGET", policy, decision)
    else:
        result["transfer_authorization"] = "REVIEW"
        ctx.finding("TRANSFER_CURRENT_AUTHORIZATION_NOT_ESTABLISHED")

    # An applicable permit for other bytes cannot authorize the actual target.
    if result["transfer_authorization"] != "ALLOW":
        for record in ctx.records("transfer.decision"):
            if (set(ctx.differences(record)) == {"payload_sha256"}
                    and record.data["decision"] == "permit"
                    and _within(record, ctx.operation_at, "valid_from", "valid_until")):
                result["transfer_authorization"] = "DENY"
                result["binding_assessment"] = "PAYLOAD_MISMATCH"
                ctx.finding("TRANSFER_PERMIT_BINDS_DIFFERENT_PAYLOAD", record)

    health, unavailable = _health_at(ctx, ctx.operation_at)
    for record in ctx.bound("transfer.collector_health"):
        if record not in health:
            ctx.finding("TRANSFER_COLLECTOR_HEALTH_TIME_INAPPLICABLE", record)
    if health:
        if unavailable:
            result["collector_health"] = "UNAVAILABLE"
            ctx.finding("TRANSFER_COLLECTOR_UNAVAILABLE_OR_NOT_DURABLE", *unavailable)
            if policy is not None and policy.data["require_collector"]:
                result["application_route_action"] = "BLOCK"
                result["transfer_authorization"] = "DENY"
                ctx.finding("TRANSFER_REQUIRED_COLLECTOR_PRECONDITION_FAILED", policy, *unavailable)
        else:
            result["collector_health"] = "AVAILABLE_WITH_DURABLE_ACKNOWLEDGEMENT"
    elif policy is not None and policy.data["require_collector"]:
        if result["transfer_authorization"] == "ALLOW":
            result["transfer_authorization"] = "REVIEW"
            result["application_route_action"] = "REVIEW"
        ctx.finding("TRANSFER_REQUIRED_COLLECTOR_HEALTH_UNKNOWN", policy)

    if result["transfer_authorization"] == "DENY":
        result["dispatch_action"] = "BLOCK_CONTROLLED_ROUTE"
        result["application_route_action"] = "BLOCK"
    elif result["transfer_authorization"] != "ALLOW":
        result["dispatch_action"] = "HOLD_PENDING_CURRENT_AUTHORIZATION"
    result["proposed_transfer_authorization"] = result["transfer_authorization"]

    coverage = []
    for record in ctx.bound("transfer.coverage"):
        left, right = interval(record.data["window_start"], record.data["window_end"])
        if (left <= ctx.operation_at < right <= record.recorded_at <= ctx.as_of
                and ctx.subject["route_id"] in record.data["covered_routes"]):
            coverage.append(record)
        else:
            ctx.finding("TRANSFER_COVERAGE_WINDOW_OR_ROUTE_INAPPLICABLE", record)
    complete = [r for r in coverage if r.data["complete"]]
    incomplete = [r for r in coverage if not r.data["complete"]]
    if complete and incomplete:
        ctx.finding("TRANSFER_COVERAGE_COMPLETENESS_CONFLICT", *coverage)
    if complete and not incomplete and ctx.target["coverage_requested"] == "managed_route":
        result["coverage"] = "DECLARED_GATEWAY_ROUTE_ONLY"
        ctx.finding("TRANSFER_COVERAGE_LIMITED_TO_DECLARED_ROUTE", *complete)
    elif ctx.target["coverage_requested"] == "broader_activity":
        ctx.finding("TRANSFER_BROADER_ACTIVITY_OUTSIDE_DECLARED_ROUTE")

    dispatches = _events(ctx, "transfer.dispatch", "dispatched_at")
    egresses = _events(ctx, "transfer.egress", "observed_at")
    if egresses:
        result["transfer_observation"] = "OBSERVED"
        ctx.finding("TRANSFER_BOUND_EGRESS_OBSERVED", *egresses)
    elif dispatches:
        result["transfer_observation"] = "DISPATCH_OBSERVED"
        ctx.finding("TRANSFER_BOUND_DISPATCH_OBSERVED", *dispatches)
    elif (complete and result["coverage"] == "DECLARED_GATEWAY_ROUTE_ONLY"
          and all(not r.data["dispatch_observed"] for r in coverage)):
        result["transfer_observation"] = "NOT_OBSERVED"
        ctx.finding("TRANSFER_NOT_OBSERVED_WITHIN_COVERED_ROUTE", *complete)
    elif any(r.data["dispatch_observed"] for r in coverage):
        ctx.finding("TRANSFER_COVERAGE_CLAIM_NEEDS_EVENT_LEVEL_EVIDENCE", *coverage)

    # Direct observed action is not erased by absent or incomplete coverage data.
    event_assessments = []
    for event in egresses + dispatches:
        field = "observed_at" if event.kind == "transfer.egress" else "dispatched_at"
        event_at = timestamp(event.data[field])
        event_policy = _policy(ctx, event_at)
        event_decision, event_conflict = _decision(ctx, event_at)
        registry_denies = event_policy is not None and not _grant_matches(ctx, event_policy)
        decision_denies = event_decision is not None and event_decision.data["decision"] == "deny"
        event_health, event_unavailable = _health_at(ctx, event_at)
        collector_required = event_policy is not None and event_policy.data["require_collector"]
        collector_denies = collector_required and bool(event_unavailable)
        if registry_denies or (decision_denies and not event_conflict) or collector_denies:
            event_assessments.append("DENY")
            result["control_assessment"] = "VIOLATION"
            supports = [event]
            if registry_denies:
                supports.append(event_policy)
            if decision_denies:
                supports.append(event_decision)
            if collector_denies:
                supports.extend([event_policy, *event_unavailable])
            ctx.finding("TRANSFER_OBSERVED_ACTION_CONFLICTS_WITH_BOUND_DENIAL", *supports)
        elif (event_policy is not None and event_decision is not None and not event_conflict
              and event_decision.data["decision"] == "permit"
              and (not collector_required or bool(event_health))):
            event_assessments.append("ALLOW")
            ctx.finding("TRANSFER_OBSERVED_ACTION_HAS_APPLICABLE_AUTHORIZATION", event, event_policy, event_decision,
                        *event_health)
        else:
            event_assessments.append("REVIEW")
            ctx.finding("TRANSFER_OBSERVED_ACTION_AUTHORIZATION_NOT_ESTABLISHED", event)
    if event_assessments:
        if "DENY" in event_assessments:
            result["observed_action_authorization"] = "DENY"
            result["transfer_authorization"] = "DENY"
            result["dispatch_action"] = "BLOCK_CONTROLLED_ROUTE"
            result["application_route_action"] = "BLOCK"
        elif "REVIEW" in event_assessments:
            result["observed_action_authorization"] = "REVIEW"
            if result["transfer_authorization"] == "ALLOW":
                result["transfer_authorization"] = "REVIEW"
                result["dispatch_action"] = "HOLD_PENDING_CURRENT_AUTHORIZATION"
                result["application_route_action"] = "REVIEW"
        else:
            result["observed_action_authorization"] = "ALLOW"

    timeouts = _events(ctx, "transfer.timeout", "timed_out_at")
    for timeout in timeouts:
        at = timestamp(timeout.data["timed_out_at"])
        preceding = [r for r in dispatches if timestamp(r.data["dispatched_at"]) <= at]
        if preceding:
            result["retry_action"] = "RECONCILE_BEFORE_RETRY"
            ctx.finding("TRANSFER_TIMEOUT_DOES_NOT_RESOLVE_REMOTE_OUTCOME", timeout, *preceding)
        else:
            ctx.finding("TRANSFER_TIMEOUT_WITHOUT_BOUND_DISPATCH", timeout)
    return result
