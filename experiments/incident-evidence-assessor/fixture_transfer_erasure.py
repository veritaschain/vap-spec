"""Synthetic facts for transfer and erasure cases; never used by runtime assessment."""

import hashlib
from copy import deepcopy

from fixture_support import AFTER, BEFORE, NOW, OPERATION, add, base, digest, finish


GRANT_FIELDS = ("actor_id", "provider_id", "endpoint", "tenant_id", "account_id", "purpose", "route_id")
ACK_AT = "2026-10-30T11:05:00Z"
COMPLETED_AT = "2026-10-30T11:15:00Z"
REVIEW_END = "2026-10-30T11:30:00Z"


def _transfer(*, changes=None, expires=AFTER, require_collector=False, broader=False):
    package, trust = base("transfer")
    subject = package["target"]["subject"]
    grant = {field: subject[field] for field in GRANT_FIELDS}
    subject.update(changes or {})
    if broader:
        package["target"]["coverage_requested"] = "broader_activity"
    policy = {
        "effective_from": BEFORE, "effective_until": expires,
        "grants": [grant], "require_collector": require_collector,
    }
    subject["policy_sha256"] = digest(policy)
    add(package, "transfer.policy", policy, role="policy", recorded_at=BEFORE, record_id="policy-record")
    return package, trust


def _decision(package, decision, *, expires=AFTER, binding=None):
    return add(package, "transfer.decision", {
        "decision": decision, "valid_from": BEFORE, "valid_until": expires,
    }, role="gateway", binding=binding, recorded_at=BEFORE, record_id="decision-record")


def _coverage(package, *, complete=True, observed=False):
    return add(package, "transfer.coverage", {
        "window_start": BEFORE, "window_end": NOW,
        "covered_routes": [package["target"]["subject"]["route_id"]],
        "complete": complete, "dispatch_observed": observed,
    }, role="collector", recorded_at=NOW, record_id="coverage-record")


def _erasure():
    package, trust = base("erasure")
    add(package, "erasure.request", {
        "requested_at": OPERATION,
        "requested_locations": ["active-serving", "backup-store"],
    }, role="responder", record_id="deletion-request")
    return package, trust


def _attestation(package, *, binding=None):
    return add(package, "erasure.provider_attestation", {
        "request_record_id": "deletion-request", "completed_at": COMPLETED_AT,
        "locations": ["active-serving"],
        "exclusions": ["backup-store", "unobserved-replicas", "downstream-recipients", "training-derivatives"],
    }, role="provider", binding=binding, recorded_at=COMPLETED_AT, record_id="provider-deletion-statement")


def approved_transfer():
    """A complete policy/permit/collector prerequisite path, independent of case IDs."""
    package, trust = _transfer(require_collector=True)
    _decision(package, "permit")
    add(package, "transfer.collector_health", {
        "checked_at": OPERATION, "available": True, "durable_acknowledged": True,
    }, role="gateway", record_id="collector-health-observation")
    return finish(package, trust)


def scoped_erasure_review():
    """A scoped provider claim and organizationally independent review chain."""
    package, trust = _erasure()
    _attestation(package)
    add(package, "erasure.review", {
        "request_record_id": "deletion-request",
        "attestation_record_id": "provider-deletion-statement",
        "method": "Synthetic reviewer inspected the listed provider evidence and named active-storage locations.",
        "evidence_record_ids": ["deletion-request", "provider-deletion-statement"],
        "window_start": OPERATION, "window_end": REVIEW_END,
        "locations": ["active-serving"],
        "limitations": [
            "No assessment of backup-store, unobserved replicas, downstream recipients or training derivatives.",
            "The signed report is a synthetic scoped reviewer claim, not proof of universal erasure.",
        ],
        "conclusion": "deletion-observed",
    }, role="reviewer", recorded_at=REVIEW_END, record_id="independent-deletion-review")
    return finish(package, trust)


def build():
    fixtures = {}

    package, trust = _transfer(changes={"endpoint": "https://unapproved.example.invalid/process"})
    _decision(package, "deny")
    _coverage(package)
    fixtures["UP-01"] = finish(package, trust)

    package, trust = _transfer(changes={"tenant_id": "tenant-personal-b"})
    _decision(package, "deny")
    fixtures["UP-02"] = finish(package, trust)

    expired = "2026-10-30T10:00:00Z"
    package, trust = _transfer(expires=expired)
    _decision(package, "permit", expires=expired)
    _coverage(package)
    fixtures["UP-03"] = finish(package, trust)

    package, trust = _transfer(changes={
        "payload_sha256": hashlib.sha256(b"synthetic payload revision b").hexdigest(),
    })
    old_binding = deepcopy(package["target"]["subject"])
    old_binding["payload_sha256"] = hashlib.sha256(b"synthetic payload revision a").hexdigest()
    _decision(package, "permit", binding=old_binding)
    _coverage(package)
    fixtures["UP-04"] = finish(package, trust)

    package, trust = _transfer()
    _decision(package, "deny")
    add(package, "transfer.egress", {"observed_at": OPERATION}, role="collector", record_id="egress-observation")
    _coverage(package, observed=True)
    fixtures["UP-05"] = finish(package, trust)

    package, trust = _transfer()
    _decision(package, "permit")
    add(package, "transfer.dispatch", {"dispatched_at": OPERATION}, role="gateway", record_id="dispatch-observation")
    timeout_at = "2026-10-30T11:01:00Z"
    add(package, "transfer.timeout", {"timed_out_at": timeout_at}, role="gateway", recorded_at=timeout_at,
        record_id="transport-timeout")
    fixtures["UP-06"] = finish(package, trust)

    package, trust = _transfer(broader=True)
    _coverage(package)
    fixtures["UP-07"] = finish(package, trust)

    package, trust = _transfer(require_collector=True)
    add(package, "transfer.collector_health", {
        "checked_at": OPERATION, "available": False, "durable_acknowledged": False,
    }, role="gateway", record_id="collector-health-observation")
    fixtures["UP-08"] = finish(package, trust)

    package, trust = _erasure()
    fixtures["ER-01"] = finish(package, trust)

    package, trust = _erasure()
    add(package, "erasure.acknowledgement", {
        "request_record_id": "deletion-request", "acknowledged_at": ACK_AT, "queue_state": "queued",
    }, role="provider", recorded_at=ACK_AT, record_id="deletion-acknowledgement")
    fixtures["ER-02"] = finish(package, trust)

    package, trust = _erasure()
    _attestation(package)
    fixtures["ER-03"] = finish(package, trust)

    package, trust = _erasure()
    wrong_binding = deepcopy(package["target"]["subject"])
    wrong_binding["object_ids"] = ["object-synthetic-elsewhere"]
    wrong_binding["tenant_id"] = "tenant-enterprise-b"
    _attestation(package, binding=wrong_binding)
    fixtures["ER-04"] = finish(package, trust)

    fixtures["ER-05"] = scoped_erasure_review()

    return fixtures
