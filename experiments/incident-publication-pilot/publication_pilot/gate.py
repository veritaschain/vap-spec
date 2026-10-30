"""Explicit reviewer authorization for one measured local publication path."""

from copy import deepcopy
from dataclasses import dataclass

from incident_assessor.assess import assess
from incident_assessor.model import exact_keys, text, digest_hex

from .editor import verify_snapshot, disclosure_text, render_html
from .protocol import InputError, MAX_HTML, canonical, decode_json, digest, sha256_bytes, timestamp, utc_now, verify_message

ROUTE_FIELDS = {"actor_id", "provider_id", "endpoint", "tenant_id", "account_id", "purpose", "route_id", "stage"}
ROLES = {"policy", "collector", "author", "reviewer"}
BASE_KINDS = {"publication_policy", "publication_manifest", "publication_activity", "publication_coverage", "publication_disclosure"}
STATES = {"LOCAL_OUTPUT_CONFIRMED", "BLOCKED_WITHOUT_PUBLICATION", "OUTCOME_UNKNOWN", "REPLAY_NO_PUBLICATION", "REQUEST_ID_CONFLICT"}


@dataclass(frozen=True)
class GateConfig:
    route: dict
    policy_id: str
    policy_version: str
    policy_sha256: str
    keys: dict
    authorities: dict
    collector_key_id: str
    reviewer_key_id: str
    publisher_public: str
    publisher_key_id: str

    def __post_init__(self):
        exact_keys(self.route, ROUTE_FIELDS)
        exact_keys(self.authorities, ROLES)
        for value in (*self.route.values(), *self.authorities.values(), self.policy_id,
                      self.policy_version, self.collector_key_id, self.reviewer_key_id, self.publisher_key_id):
            text(value)
        if (self.route["stage"] != "publication" or
                self.route["endpoint"] != "local-publication://" + self.route["provider_id"] + "/release"):
            raise InputError("Only the configured local publication stage/venue is supported")
        digest_hex(self.policy_sha256)
        digest_hex(self.publisher_public)
        for role, key_id in (("collector", self.collector_key_id), ("reviewer", self.reviewer_key_id)):
            key = self.keys.get(key_id)
            if not key or key["issuer"] != self.authorities[role] or role not in key["roles"]:
                raise InputError("Configured key does not hold its required role")
        object.__setattr__(self, "route", deepcopy(self.route))
        object.__setattr__(self, "keys", deepcopy(self.keys))
        object.__setattr__(self, "authorities", deepcopy(self.authorities))

    def export(self):
        return deepcopy(self.__dict__)


def measured_components(view, subject):
    result = [{"artifact_id": subject["artifact_id"], "revision_id": subject["revision_id"],
               "sha256": subject["payload_sha256"], "category": "text"}]
    for block in view["adopted"]:
        result.append({"artifact_id": view["document_id"] + ":" + block["block_id"],
                       "revision_id": block["revision_id"], "sha256": block["sha256"], "category": "text"})
    return result


def adopted_data(view, subject):
    return [{"activity": item["activity"], "observed_at": item["observed_at"],
             "adoption_basis": "observed_in_artifact", "included_in_artifact_sha256": subject["payload_sha256"],
             "component": component} for item, component in zip(view["adopted"], measured_components(view, subject)[1:])]


def verify_receipt(receipt, measurements, config, final_at, post_at):
    body = verify_message(receipt, config.publisher_public, config.publisher_key_id, "local_publication_receipt")
    exact_keys(body, {"kind", "request_id", "fingerprint", "artifact_sha256", "disclosure_sha256",
                      "byte_length", "destination_id", "visible_name", "observed_at"})
    for field in ("request_id", "fingerprint", "artifact_sha256", "disclosure_sha256", "byte_length", "destination_id"):
        if canonical(body[field]) != canonical(measurements[field]):
            raise InputError("Local receipt does not match measured " + field)
    if type(body["byte_length"]) is not int or not 0 < body["byte_length"] <= MAX_HTML:
        raise InputError("Invalid local receipt length")
    expected_name = sha256_bytes(measurements["request_id"].encode("utf-8")) + ".html"
    if body["visible_name"] != expected_name:
        raise InputError("Local receipt names another output")
    if not timestamp(final_at) <= timestamp(body["observed_at"]) <= timestamp(post_at):
        raise InputError("Local receipt time is outside the publication observation")
    return body


class Gate:
    def __init__(self, config, clock=utc_now):
        self.config = GateConfig(**config.export())
        self.clock = clock

    def check(self, candidate, trust, approval, *, at):
        """Pure recomputable check; no writes, signing or fixture catalogue access."""
        result = {"at": at, "authorized_local_export": False, "reason": None,
                  "measurements": None, "assessor_frame": None}
        try:
            candidate, trust, approval = [decode_json(canonical(value)) for value in (candidate, trust, approval)]
            timestamp(at)
            exact_keys(candidate, {"format", "source", "disclosure", "html", "evidence"})
            if candidate["format"] != "incident-publication-candidate/0.1":
                raise InputError("Unsupported candidate format")
            config = self.config
            if trust["mode"] != "synthetic-test-only" or canonical(trust["keys"]) != canonical(config.keys):
                raise InputError("Evaluator trust differs from the controller-pinned key metadata")
            package = candidate["evidence"]
            if package["workflow"] != "publication" or package["target"]["authorities"] != config.authorities:
                raise InputError("Unexpected workflow or publication authorities")
            assess(package, trust, allow_synthetic=True)  # Original evaluator pin first.
            if timestamp(package["as_of"]) > timestamp(at):
                raise InputError("Candidate preparation is after the current operation")
            collector = config.keys[config.collector_key_id]
            view = verify_snapshot(candidate["source"], collector["public_key"], config.collector_key_id)
            for envelope in [*candidate["source"]["operations"], candidate["source"]["checkpoint"]]:
                observed = timestamp(envelope["body"]["observed_at"])
                if not timestamp(collector["not_before"]) <= observed < timestamp(collector["not_after"]):
                    raise InputError("Editor signing key was outside its configured validity")
            if timestamp(view["observed_at"]) > timestamp(package["as_of"]):
                raise InputError("Source checkpoint follows candidate preparation")
            notice = disclosure_text(candidate["disclosure"])
            if type(candidate["html"]) is not str:
                raise InputError("Candidate HTML must be UTF-8 text")
            html = candidate["html"].encode("utf-8")
            if not 0 < len(html) <= MAX_HTML or html != render_html(view, candidate["disclosure"]):
                raise InputError("Final HTML differs from the controlled article/disclosure rendering")
            subject = {"request_id": package["target"]["subject"]["request_id"], **config.route,
                       "artifact_id": view["document_id"], "revision_id": view["revision_id"],
                       "payload_sha256": sha256_bytes(html), "disclosure_sha256": sha256_bytes(notice.encode("utf-8")),
                       "policy_id": config.policy_id, "policy_version": config.policy_version,
                       "policy_sha256": config.policy_sha256}
            if canonical(subject) != canonical(package["target"]["subject"]):
                raise InputError("Candidate target differs from measured bytes, revision, venue or policy")
            measurements = {"request_id": subject["request_id"], "candidate_sha256": digest(candidate),
                            "source_sha256": view["source_sha256"], "lineage_sha256": view["lineage_sha256"],
                            "artifact_sha256": subject["payload_sha256"], "disclosure_sha256": subject["disclosure_sha256"],
                            "byte_length": len(html), "destination_id": config.route["provider_id"]}
            measurements["fingerprint"] = digest(measurements)
            result["measurements"] = measurements
            records = package["records"]
            if any(r["body"]["kind"] not in BASE_KINDS or canonical(r["body"]["binding"]) != canonical(subject) for r in records):
                raise InputError("Candidate record kind or full target binding is unsupported")
            by_kind = {kind: [r["body"]["data"] for r in records if r["body"]["kind"] == kind] for kind in BASE_KINDS}
            if any(len(by_kind[k]) != 1 for k in BASE_KINDS - {"publication_activity"}):
                raise InputError("Required candidate record is missing or duplicated")
            prepared_at = package["as_of"]
            if by_kind["publication_manifest"] != [{"observed_at": prepared_at, "components": measured_components(view, subject)}]:
                raise InputError("Manifest differs from actually rendered adopted components")
            if sorted(map(canonical, by_kind["publication_activity"])) != sorted(map(canonical, adopted_data(view, subject))):
                raise InputError("Activity projection differs from the verified final block history")
            categories = ["text"] if candidate["disclosure"]["activities"] else []
            if by_kind["publication_disclosure"] != [{"categories": categories, "prepared_at": prepared_at, "text": notice}]:
                raise InputError("Disclosure record differs from the rendered structured notice")
            coverage = by_kind["publication_coverage"][0]
            first_at = candidate["source"]["operations"][0]["body"]["observed_at"]
            if coverage != {"scope": "declared_editor_only", "from": first_at, "until": prepared_at}:
                raise InputError("Coverage record must retain only the observed preparation interval")
            if not set(view["observed_activities"]) <= set(candidate["disclosure"]["activities"]):
                raise InputError("Disclosure omits a recorded session activity")
            if set(candidate["disclosure"]["activities"]) != set(view["observed_activities"]):
                raise InputError("Disclosure claims an unrecorded simulated activity")
            policy = by_kind["publication_policy"][0]
            frame = deepcopy(package)
            frame["as_of"] = frame["target"]["operation_at"] = at
            if approval is not None:
                exact_keys(approval, {"release", "evidence"})
                frame["records"].append(deepcopy(approval["evidence"]))
            frame_trust = deepcopy(trust)
            frame_trust["as_of"], frame_trust["target_sha256"] = at, digest(frame["target"])
            report = assess(frame, frame_trust, allow_synthetic=True)
            result["assessor_frame"] = {"evidence": frame, "trust": frame_trust, "report": report}
            if report["evidence_integrity"] != "VERIFIED_UNDER_EVALUATOR_TRUST":
                raise InputError("Required evidence signature, identity, role or recording time failed")
            assessments = report["assessments"]
            if assessments["policy_applicability"] != "BOUND_AND_EFFECTIVE_UNDER_GIVEN_ASSUMPTIONS":
                raise InputError("Publication policy applicability or interpretation is unresolved")
            if (assessments["publication_action"] == "BLOCK" or
                    set(view["observed_activities"]) & set(policy["prohibited_activities"])):
                raise InputError("Recorded session activity is prohibited by the pinned release policy")
            if assessments["disclosure_preparation"] != "RECORDED" or assessments["disclosure_assessment"] != "REQUIRES_CONTENT_REVIEW":
                raise InputError("Required disclosure evidence is not established")
            self._approval(candidate, approval, subject, measurements, at)
            if assessments["approval_applicability"] != "BOUND_APPROVAL_RECORDED":
                raise InputError("Current fully bound reviewer approval is not established")
            result["authorized_local_export"] = True
            result["reason"] = "Explicit reviewer authorization for the exact local artifact; core assessment remains REVIEW"
        except (InputError, KeyError, TypeError, UnicodeError) as exc:
            result["reason"] = str(exc)
        return result

    def _approval(self, candidate, approval, subject, measurements, at):
        if approval is None:
            raise InputError("Separate explicit reviewer release authorization is required")
        config = self.config
        key = config.keys[config.reviewer_key_id]
        body = verify_message(approval["release"], key["public_key"], config.reviewer_key_id, "release_approval")
        fields = {"kind", "request_id", "candidate_sha256", "artifact_sha256", "disclosure_sha256",
                  "policy_sha256", "destination_id", "approved_at", "valid_until", "decision", "review_scope"}
        exact_keys(body, fields)
        for name in ("request_id", "candidate_sha256", "artifact_sha256", "disclosure_sha256", "destination_id"):
            if body[name] != measurements[name]:
                raise InputError("Release authorization no longer matches " + name)
        if body["policy_sha256"] != config.policy_sha256 or body["decision"] != "approve" or body["review_scope"] != "exact_local_artifact_and_disclosure":
            raise InputError("Unexpected reviewer decision, scope or policy")
        approved, until, now = timestamp(body["approved_at"]), timestamp(body["valid_until"]), timestamp(at)
        if not timestamp(candidate["evidence"]["as_of"]) <= approved <= now < until:
            raise InputError("Reviewer authorization is premature, future or expired")
        if not timestamp(key["not_before"]) <= approved < timestamp(key["not_after"]):
            raise InputError("Reviewer key was not valid at approval")
        record = approval["evidence"]
        expected_data = {"valid_from": body["approved_at"], "valid_until": body["valid_until"], "approval": "approved"}
        if (record["key_id"] != config.reviewer_key_id or record["body"]["issuer"] != config.authorities["reviewer"] or
                record["body"]["kind"] != "publication_approval" or record["body"]["recorded_at"] != body["approved_at"] or
                canonical(record["body"]["binding"]) != canonical(subject) or record["body"]["data"] != expected_data):
            raise InputError("Pilot authorization and assessor approval disagree")

    def release(self, candidate, trust, approval, publisher, *, after_snapshot=None, before_publish=None):
        at = self.clock()
        try:
            owned, pinned, approved = [decode_json(canonical(value)) for value in (candidate, trust, approval)]
        except InputError as exc:
            return {"format": "incident-publication-release/0.1", "state": "BLOCKED_WITHOUT_PUBLICATION", "attempted": False,
                    "reason": str(exc), "preflight": None, "final_gate": None, "publication": None,
                    "receipt": None, "post_at": at}
        preflight = self.check(owned, pinned, approved, at=at)
        report = {"format": "incident-publication-release/0.1", "state": "BLOCKED_WITHOUT_PUBLICATION", "attempted": False,
                  "reason": preflight["reason"], "preflight": preflight, "final_gate": None,
                  "publication": None, "receipt": None, "post_at": at}
        if not preflight["authorized_local_export"]:
            return report
        if (publisher.destination_id != self.config.route["provider_id"] or
                publisher.public_key != self.config.publisher_public or publisher.key_id != self.config.publisher_key_id):
            report["reason"] = "Publisher destination or signing identity differs from the controller pin"
            return report
        html = owned["html"].encode("utf-8")
        if after_snapshot is not None:
            after_snapshot()

        def final_gate():
            if before_publish is not None:
                before_publish()
            final_at = self.clock()
            result = self.check(owned, pinned, approved, at=final_at)
            if timestamp(final_at) < timestamp(at):
                result["authorized_local_export"] = False
                result["reason"] = "Clock moved backwards before publication"
            report["final_gate"] = result
            return result["authorized_local_export"]

        measured = preflight["measurements"]
        report["post_at"] = None
        try:
            result = publisher.publish(measured["request_id"], measured["fingerprint"], html,
                                       measured["disclosure_sha256"], before_link=final_gate)
            if (type(result) is not dict or result.get("state") not in STATES or type(result.get("attempted")) is not bool):
                raise InputError("Malformed local publisher result")
            report["publication"] = deepcopy(result)
            report["attempted"] = result["attempted"]
            report["state"], report["reason"] = result["state"], result["reason"]
            report["post_at"] = self.clock()
            timestamp(report["post_at"])
            if result["state"] == "LOCAL_OUTPUT_CONFIRMED":
                if not result["attempted"] or not report["final_gate"] or not report["final_gate"]["authorized_local_export"]:
                    raise InputError("Output confirmation lacks its final authorization")
                receipt_body = verify_receipt(result["receipt"], measured, self.config, report["final_gate"]["at"], report["post_at"])
                if result["journal_state"] != "local_output_confirmed" or result["visible_name"] != receipt_body["visible_name"]:
                    raise InputError("Publisher confirmation lacks matching persistence or visible filename")
                report["receipt"] = deepcopy(result["receipt"])
        except (InputError, OSError) as exc:
            report["state"], report["reason"] = "OUTCOME_UNKNOWN", str(exc)
            report["receipt"] = None
            if report["publication"] is None:
                report["attempted"] = None  # Publisher invocation did not return an attributable observation.
        return report


def verify_report(candidate, trust, approval, report, config):
    """Recompute supplied observations; does not repeat or independently prove IO."""
    exact_keys(report, {"format", "state", "attempted", "reason", "preflight", "final_gate", "publication", "receipt", "post_at"})
    if report["format"] != "incident-publication-release/0.1" or report["state"] not in STATES:
        raise InputError("Invalid release report")
    if type(report["attempted"]) is not bool and not (report["attempted"] is None and report["state"] == "OUTCOME_UNKNOWN" and report["publication"] is None):
        raise InputError("Invalid or contradictory attempt observation")
    gate = Gate(config)
    preflight = report.get("preflight")
    if preflight is None:
        raise InputError("Missing captured preflight frame")
    if canonical(preflight) != canonical(gate.check(candidate, trust, approval, at=preflight["at"])):
        raise InputError("Preflight check does not recompute")
    final = report.get("final_gate")
    if final is not None:
        if timestamp(final["at"]) < timestamp(preflight["at"]):
            raise InputError("Final gate predates admission")
        if canonical(final) != canonical(gate.check(candidate, trust, approval, at=final["at"])):
            raise InputError("Final gate check does not recompute")
    if report["attempted"] and (not preflight["authorized_local_export"] or not final or not final["authorized_local_export"]):
        raise InputError("Publication attempt lacks explicit current authorization")
    if report["post_at"] is None:
        if report["state"] != "OUTCOME_UNKNOWN":
            raise InputError("Missing postflight time cannot support a resolved outcome")
    elif timestamp(report["post_at"]) < timestamp((final or preflight)["at"]):
        raise InputError("Postflight observation predates the gate")
    publication = report.get("publication")
    if publication is not None:
        exact_keys(publication, {"state", "attempted", "visible_name", "receipt", "journal_state", "reason"})
        if (publication["state"] not in STATES or type(publication["attempted"]) is not bool or
                report["attempted"] is not publication["attempted"]):
            raise InputError("Publisher and gate attempt observations disagree")
        if report["state"] != publication["state"] and report["state"] != "OUTCOME_UNKNOWN":
            raise InputError("Publisher and gate outcomes disagree")
        if not preflight["authorized_local_export"]:
            raise InputError("Publisher invoked despite denied preflight")
    elif report["attempted"] is True:
        raise InputError("Attempt observation lacks its publisher result")
    if report["state"] == "LOCAL_OUTPUT_CONFIRMED":
        if not report["attempted"] or not report.get("receipt"):
            raise InputError("Confirmed output lacks attempt or receipt")
        verify_receipt(report["receipt"], preflight["measurements"], config, final["at"], report["post_at"])
        publication = report.get("publication")
        if not publication or publication["state"] != report["state"] or canonical(publication["receipt"]) != canonical(report["receipt"]):
            raise InputError("Stored publication confirmation differs from release receipt")
        if (publication["journal_state"] != "local_output_confirmed" or
                publication["visible_name"] != report["receipt"]["body"]["visible_name"]):
            raise InputError("Confirmation lacks matching terminal persistence and visible filename")
    elif report.get("receipt") is not None:
        raise InputError("Unconfirmed report must not promote a receipt")
    if not preflight["authorized_local_export"] and (report["state"] != "BLOCKED_WITHOUT_PUBLICATION" or report.get("publication") is not None or final is not None):
        raise InputError("Denied preflight cannot reach publication")
    return True
