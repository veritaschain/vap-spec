"""Public synthetic inputs; no runtime policy depends on catalogue case IDs."""

import hashlib
from copy import deepcopy

from fixture_support import AFTER, BEFORE, NOW, OPERATION, add, base, digest, finish


def _sha(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _publication(*, prohibited=(), categories=(), interpretation="resolved", revision="revision-a", disclosure="Synthetic disclosure: proofreading assistance to prose."):
    package, trust = base("publication")
    subject = package["target"]["subject"]
    subject["endpoint"] = "https://submissions.example.invalid/submit"
    subject["purpose"] = "publication_submission"
    subject["revision_id"] = revision
    subject["payload_sha256"] = _sha("synthetic document " + revision)
    subject["disclosure_sha256"] = _sha(disclosure)
    policy = {
        "effective_from": BEFORE, "effective_until": AFTER,
        "prohibited_activities": list(prohibited), "disclosure_categories": list(categories),
        "approval_required": True, "interpretation": interpretation,
    }
    subject["policy_sha256"] = digest(policy)
    return package, trust, policy, disclosure


def _document(package):
    subject = package["target"]["subject"]
    return {"artifact_id": subject["artifact_id"], "revision_id": subject["revision_id"],
            "sha256": subject["payload_sha256"], "category": "text"}


def _manifest(package, extras=()):
    return add(package, "publication_manifest", {"observed_at": OPERATION, "components": [_document(package), *extras]}, role="collector")


def _activity(package, activity, component=None, *, binding=None, observed_at=OPERATION, recorded_at=OPERATION):
    bound = package["target"]["subject"] if binding is None else binding
    return add(package, "publication_activity", {
        "activity": activity, "observed_at": observed_at, "adoption_basis": "observed_in_artifact",
        "included_in_artifact_sha256": bound["payload_sha256"],
        "component": _document(package) if component is None else component,
    }, role="collector", binding=binding, recorded_at=recorded_at)


def _disclosure(package, text, categories=("text",)):
    return add(package, "publication_disclosure", {"categories": list(categories), "prepared_at": OPERATION, "text": text}, role="author")


def _approval(package, binding=None):
    return add(package, "publication_approval", {"valid_from": BEFORE, "valid_until": AFTER, "approval": "approved"}, role="reviewer", binding=binding)


def build():
    cases = {}

    package, trust, policy, disclosure = _publication(
        prohibited=("substantive_editing",), categories=("text",),
        disclosure="Synthetic disclosure: AI substantive editing was used for the text.")
    add(package, "publication_policy", policy, role="policy")
    _manifest(package)
    _activity(package, "substantive_editing")
    _disclosure(package, disclosure)
    cases["PB-01"] = finish(package, trust)

    package, trust, policy, disclosure = _publication()
    add(package, "publication_policy", policy, role="policy")
    add(package, "publication_coverage", {"scope": "declared_editor_only", "from": BEFORE, "until": AFTER}, role="collector")
    cases["PB-02"] = finish(package, trust)

    package, trust, policy, disclosure = _publication(revision="revision-b")
    add(package, "publication_policy", policy, role="policy")
    prior_binding = deepcopy(package["target"]["subject"])
    prior_binding["revision_id"] = "revision-a"
    prior_binding["payload_sha256"] = _sha("synthetic document revision-a")
    _approval(package, prior_binding)
    cases["PB-03"] = finish(package, trust)

    package, trust, policy, disclosure = _publication(categories=("text", "figure", "code"))
    add(package, "publication_policy", policy, role="policy")
    figure = {"artifact_id": "figure-synthetic", "revision_id": "figure-revision-3", "sha256": _sha("synthetic figure revision 3"), "category": "figure"}
    code = {"artifact_id": "code-synthetic", "revision_id": "code-revision-7", "sha256": _sha("synthetic code revision 7"), "category": "code"}
    _manifest(package, [figure, code])
    _activity(package, "figure_generation", figure)
    _activity(package, "code_review", code)
    _disclosure(package, disclosure)
    cases["PB-04"] = finish(package, trust)

    package, trust, policy, disclosure = _publication(interpretation="unresolved", revision="revision-b")
    add(package, "publication_policy", policy, role="policy")
    prior_policy = deepcopy(policy)
    prior_policy.update({"effective_from": "2026-10-29T00:00:00Z", "effective_until": OPERATION,
                         "interpretation": "resolved", "prohibited_activities": ["generation"]})
    prior_binding = deepcopy(package["target"]["subject"])
    prior_binding.update({"policy_version": "policy-v0", "policy_sha256": digest(prior_policy), "stage": "drafting",
                          "revision_id": "revision-a", "payload_sha256": _sha("synthetic document revision-a")})
    add(package, "publication_policy", prior_policy, role="policy", binding=prior_binding, recorded_at=BEFORE)
    old_component = {"artifact_id": prior_binding["artifact_id"], "revision_id": "revision-a",
                     "sha256": prior_binding["payload_sha256"], "category": "text"}
    _activity(package, "generation", old_component, binding=prior_binding, observed_at=BEFORE, recorded_at=BEFORE)
    _manifest(package)
    _activity(package, "substantive_editing")
    cases["PB-05"] = finish(package, trust)

    package, trust, policy, disclosure = _publication()
    add(package, "publication_declaration", {"activities": ["proofreading"], "declared_at": OPERATION}, role="author")
    cases["PB-06"] = finish(package, trust)

    package, trust, policy, disclosure = _publication(categories=("text",))
    add(package, "publication_policy", policy, role="policy")
    _disclosure(package, disclosure)
    add(package, "publication_dispatch", {"attempted_at": OPERATION}, role="gateway")
    cases["PB-07"] = finish(package, trust)

    package, trust = base("incident_response")
    request = add(package, "info_request", {
        "questions": ["processing_activity", "account_log_availability"],
        "requested_at": OPERATION, "observation_cutoff": NOW,
        "authority_basis": "Synthetic authorized-review mandate; no compulsory powers asserted.",
    }, role="reviewer")
    add(package, "info_receipt", {"received_at": OPERATION, "request_record_id": request["body"]["record_id"]}, role="recipient")
    cases["IR-01"] = finish(package, trust)

    package, trust = base("incident_response")
    action = add(package, "containment_action", {
        "decision_at": OPERATION, "removal_observed_at": OPERATION,
        "authority_basis": "Synthetic applicable containment policy authorizes this responder and removal.",
        "source_account_id": package["target"]["subject"]["account_id"],
        "urgency": "urgent", "delay_justified": False, "minimum_evidence_available": False,
        "unavailable_material": ["minimum_relevant_account_history"],
        "access_constraints": ["authorized_incident_reviewers_only"],
        "retention_basis": "Synthetic restricted incident-review retention; no missing personal data copied.",
    }, role="responder")
    add(package, "containment_anchor_claim", {
        "anchor_time": NOW, "record_ids": [action["body"]["record_id"]],
        "format": "synthetic-unsupported-anchor", "material_sha256": _sha("synthetic anchor claim"),
    }, role="collector", recorded_at=NOW)
    cases["IR-02"] = finish(package, trust)

    package, trust = base("cross_party")
    add(package, "cross_provider_receipt", {
        "received_at": OPERATION,
        "statement": "Synthetic provider acknowledges receipt of the bound request; no independently anchored exchange is supplied.",
        "statement_scope": ["request_receipt_only"],
    }, role="provider")
    cases["XR-01"] = finish(package, trust)
    return cases


def publication_ready():
    """Supported positive evidence controls; still REVIEW, never automatic permission."""
    package, trust, policy, disclosure = _publication(categories=("text",))
    add(package, "publication_policy", policy, role="policy")
    _manifest(package)
    _activity(package, "proofreading")
    _disclosure(package, disclosure)
    _approval(package)
    add(package, "publication_dispatch", {"attempted_at": OPERATION}, role="gateway")
    add(package, "publication_receipt", {"received_at": NOW, "status": "accepted"}, role="recipient", recorded_at=NOW)
    return finish(package, trust)


def information_response():
    """Authenticated substantive response control; its factual claims remain unproven."""
    package, trust = build()["IR-01"]
    request = next(r["body"] for r in package["records"] if r["body"]["kind"] == "info_request")
    add(package, "info_response", {
        "responded_at": NOW, "request_record_id": request["record_id"], "status": "complete",
        "answers": [
            {"question": "processing_activity", "answer": "Provider asserts processing was limited to the stated purpose."},
            {"question": "account_log_availability", "answer": "Provider asserts a scoped export can be supplied."},
        ],
    }, role="recipient", recorded_at=NOW)
    return finish(package, trust)
