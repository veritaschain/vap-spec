"""One claimed upload attempt gated by actual scoped collector acknowledgements.

Reconciliation observes a saved request; it never resumes that request.  A fresh
readback is a point-in-time prerequisite, not continuous service availability.
"""

import hashlib
import secrets
from copy import deepcopy
from uuid import uuid4

from incident_assessor.assess import assess
from incident_assessor.model import digest_hex, exact_keys, text
from upload_pilot.gateway import verify_receipt as verify_payload_receipt
from upload_pilot.journal import STATES
from upload_pilot.protocol import (
    GateConfig, MAX_PAYLOAD, sign_control as sign_upload_control,
    verify_control as verify_upload_control,
)

from .protocol import (
    InputError, capture, collection_id, digest, public_key, sign_control,
    sign_record, timestamp, utc_now, validate_endpoint, validate_intent,
    verify_control, verify_receipt, verify_status,
)


def _identifier(value):
    text(value)
    if len(value) > 256:
        raise InputError("Collector identifiers exceed the experiment limit")
    return value


def _frame(package, trust, at, *, operation=True, health=None, dispatch=None):
    package, trust = deepcopy(package), deepcopy(trust)
    if operation:
        package["target"]["operation_at"] = at
    package["as_of"] = trust["as_of"] = at
    if health is not None:
        package["records"].append(health)
    if dispatch is not None:
        package["records"].append(dispatch)
    trust["target_sha256"] = digest(package["target"])
    return {"evidence": package, "trust": trust,
            "assessment": assess(package, trust, allow_synthetic=True)}


def _authorization(frame, *, pending):
    """Select only the exact policy/permit authenticated by the fixed assessor."""
    report = frame["assessment"]
    result = report["assessments"]
    expected = "REVIEW" if pending else "ALLOW"
    health = "UNKNOWN" if pending else "AVAILABLE_WITH_DURABLE_ACKNOWLEDGEMENT"
    if (report["evidence_integrity"] != "VERIFIED_UNDER_EVALUATOR_TRUST"
            or result["transfer_authorization"] != expected
            or result["proposed_transfer_authorization"] != expected
            or result["binding_assessment"] != "MATCH"
            or result["policy_binding"] != "CURRENT_CONTENT_BOUND"
            or result["collector_health"] != health):
        raise InputError("Current policy and permit do not authorize this measured target")
    findings = [item for item in report["findings"]
                if item["code"] == "TRANSFER_CURRENT_POLICY_AND_PERMIT_BIND_TARGET"]
    if len(findings) != 1:
        raise InputError("The assessor did not select one current policy and permit")
    selected = {item["body"]["kind"]: item for item in frame["evidence"]["records"]
                if item["body"]["record_id"] in findings[0]["record_ids"]}
    if set(selected) != {"transfer.policy", "transfer.decision"}:
        raise InputError("Selected authorization evidence is incomplete")
    policy, decision = selected["transfer.policy"], selected["transfer.decision"]
    if policy["body"]["data"]["require_collector"] is not True:
        raise InputError("This experiment requires a collector in the signed policy")
    if decision["body"]["data"]["decision"] != "permit":
        raise InputError("This experiment requires a bound permit")
    return policy, decision


class CollectorGateway:
    def __init__(self, config, journal, transport, collector, *, collector_id,
                 collector_public, collector_key_id, clock=utc_now):
        if not isinstance(config, GateConfig):
            raise InputError("Collector gateway requires a trusted upload GateConfig")
        self._config = GateConfig(
            config.endpoint, config.route, config.gateway_secret, config.gateway_key_id,
            config.gateway_issuer, config.receiver_public, config.receiver_key_id,
        )
        self._collector_id = _identifier(collector_id)
        digest_hex(collector_public)
        self._collector_public = collector_public
        self._collector_key_id = _identifier(collector_key_id)
        self._collector_endpoint = validate_endpoint(getattr(collector, "endpoint", None))
        if getattr(transport, "endpoint", None) != self._config.endpoint:
            raise InputError("Payload transport differs from the pinned route")
        if not callable(clock) or any(not callable(getattr(obj, method, None)) for obj, method in (
                (journal, "get"), (journal, "claim"), (journal, "finish"),
                (transport, "send"), (collector, "collect"), (collector, "status"))):
            raise InputError("Collector gateway dependencies do not implement the fixed interface")
        self.journal, self.transport, self.collector, self.clock = journal, transport, collector, clock

    def _clock(self, not_before=None):
        at = self.clock()
        parsed = timestamp(at)
        if not_before is not None and parsed < timestamp(not_before):
            raise InputError("Gateway clock regressed")
        return at

    def _pins(self):
        return {
            "collector_id": self._collector_id, "collector_endpoint": self._collector_endpoint,
            "collector_public": self._collector_public, "collector_key_id": self._collector_key_id,
            "gateway_public": public_key(self._config.gateway_secret),
            "gateway_key_id": self._config.gateway_key_id, "gateway_issuer": self._config.gateway_issuer,
            "receiver_public": self._config.receiver_public,
            "receiver_key_id": self._config.receiver_key_id,
            "endpoint": self._config.endpoint, "route": deepcopy(self._config.route),
        }

    def _key_authorized(self, frame, at):
        package, trust = frame["evidence"], frame["trust"]
        key = trust["keys"].get(self._config.gateway_key_id)
        return key is not None and (
            key["public_key"] == public_key(self._config.gateway_secret)
            and key["issuer"] == self._config.gateway_issuer
            and "gateway" in key["roles"]
            and package["target"]["authorities"].get("gateway") == self._config.gateway_issuer
            and timestamp(key["not_before"]) <= timestamp(at) < timestamp(key["not_after"])
        )

    def _fingerprint(self, frame, length):
        return digest({"evaluation_id": frame["evidence"]["evaluation_id"],
                       "subject": frame["evidence"]["target"]["subject"],
                       "byte_length": length, "pins": self._pins()})

    @staticmethod
    def _report(admission, payload_sha256, length):
        return {
            "format": "collector-pilot-report/0.1", "state": "BLOCKED_WITHOUT_ATTEMPT",
            "attempted": False, "reason": "NOT_ADMITTED", "payload_sha256": payload_sha256,
            "byte_length": length, "journal_state": "NOT_CLAIMED", "collector_outcome": "NOT_CONTACTED",
            "admission": deepcopy(admission), "final": None, "postflight": deepcopy(admission),
            "collection_intent": None, "collection_exchange": None, "collection_receipt": None,
            "status_query": None, "status_exchange": None, "collection_status": None,
            "dispatch_intent": None, "payload_transport": None, "payload_receipt": None,
        }

    def _snapshot(self, report, prepared_at):
        return {
            "format": "collector-pilot-intent/0.1",
            "request_id": report["admission"]["evidence"]["target"]["subject"]["request_id"],
            "payload_sha256": report["payload_sha256"], "byte_length": report["byte_length"],
            "prepared_at": prepared_at, "pins": self._pins(),
            "admission": deepcopy(report["admission"]),
            "collection_intent": deepcopy(report["collection_intent"]),
            "dispatch_intent": deepcopy(report["dispatch_intent"]),
        }

    def _row(self, value, request_id):
        row = capture(value)
        exact_keys(row, {"request_id", "fingerprint", "state", "snapshot", "details"}, ("claim_status",))
        if row["request_id"] != request_id or row["state"] not in STATES:
            raise InputError("Journal row has another identity or unsupported state")
        digest_hex(row["fingerprint"])
        if row["details"] is not None and type(row["details"]) is not dict:
            raise InputError("Journal details are malformed")
        snapshot = row["snapshot"]
        exact_keys(snapshot, {"format", "request_id", "payload_sha256", "byte_length", "prepared_at",
                              "pins", "admission", "collection_intent", "dispatch_intent"})
        if (snapshot["format"] != "collector-pilot-intent/0.1" or snapshot["request_id"] != request_id
                or snapshot["pins"] != self._pins()):
            raise InputError("Journal snapshot does not match the independently configured pins")
        length = snapshot["byte_length"]
        if type(length) is not int or not 0 <= length <= MAX_PAYLOAD:
            raise InputError("Journal payload length is invalid")
        digest_hex(snapshot["payload_sha256"])
        frame = snapshot["admission"]
        exact_keys(frame, {"evidence", "trust", "assessment"})
        actual_assessment = assess(frame["evidence"], frame["trust"], allow_synthetic=True)
        if digest(actual_assessment) != digest(frame["assessment"]):
            raise InputError("Journal admission assessment does not reproduce")
        self._input(frame["evidence"], frame["trust"])
        policy, decision = _authorization(frame, pending=True)
        subject = frame["evidence"]["target"]["subject"]
        if (subject["request_id"] != request_id or subject["payload_sha256"] != snapshot["payload_sha256"]
                or any(subject[key] != item for key, item in self._config.route.items())
                or frame["evidence"]["target"]["operation_at"] != snapshot["prepared_at"]
                or frame["evidence"]["as_of"] != snapshot["prepared_at"]
                or not self._key_authorized(frame, snapshot["prepared_at"])
                or self._fingerprint(frame, length) != row["fingerprint"]):
            raise InputError("Journal measured target or authorization is inconsistent")
        intent = validate_intent(verify_control(
            snapshot["collection_intent"], public_key(self._config.gateway_secret),
            self._config.gateway_key_id, "collection_intent"))
        expected_intent = self._intent_body(frame, length, decision, snapshot["prepared_at"])
        if intent != expected_intent:
            raise InputError("Journal collection intent does not bind its owned snapshot")
        dispatch = verify_upload_control(snapshot["dispatch_intent"], public_key(self._config.gateway_secret),
                                         self._config.gateway_key_id, "dispatch_intent")
        if dispatch != self._dispatch_body(subject, length, snapshot["prepared_at"]):
            raise InputError("Journal payload intent does not bind its owned snapshot")
        return row

    @staticmethod
    def _input(package, trust):
        if package["workflow"] != "transfer" or trust["mode"] != "synthetic-test-only":
            raise InputError("Only explicitly synthetic transfer contexts are supported")
        if any(item["body"]["kind"] not in {"transfer.policy", "transfer.decision"}
               for item in package["records"]):
            raise InputError("Initial inputs may contain policy and decision records only")

    def _intent_body(self, frame, length, decision, at):
        package = frame["evidence"]
        subject = package["target"]["subject"]
        return {
            "kind": "collection_intent", "collector_id": self._collector_id,
            "collection_id": collection_id(self._collector_id, subject["request_id"]),
            "request_id": subject["request_id"], "evaluation_id": package["evaluation_id"],
            "subject_sha256": digest(subject), "payload_sha256": subject["payload_sha256"],
            "byte_length": length, "policy_sha256": subject["policy_sha256"],
            "decision_sha256": digest(decision), "created_at": at,
        }

    @staticmethod
    def _dispatch_body(subject, length, at):
        return {"kind": "dispatch_intent", "request_id": subject["request_id"],
                "subject_sha256": digest(subject), "payload_sha256": subject["payload_sha256"],
                "byte_length": length, "created_at": at}

    def _journal_state(self, request_id):
        try:
            row = self.journal.get(request_id)
            return "NOT_CLAIMED" if row is None else self._row(row, request_id)["state"]
        except Exception:
            return "UNAVAILABLE"

    def _persist(self, report, state):
        request_id = report["admission"]["evidence"]["target"]["subject"]["request_id"]
        report["journal_state"] = state
        try:
            row = self._row(self.journal.finish(request_id, state, deepcopy(report)), request_id)
            if (row["state"] != state or row["fingerprint"] != self._fingerprint(report["admission"], report["byte_length"])
                    or digest(row["details"]) != digest(report)):
                raise InputError("Journal result acknowledgement differs from the owned report")
        except Exception:
            report["state"] = "OUTCOME_UNKNOWN"
            report["reason"] = "JOURNAL_RESULT_PERSISTENCE_FAILED"
            report["payload_receipt"] = None
            report["journal_state"] = self._journal_state(request_id)
        return report

    @staticmethod
    def _replay(report, row, fingerprint):
        report["journal_state"] = row["state"]
        if row["fingerprint"] != fingerprint:
            report["state"], report["reason"] = "REQUEST_ID_CONFLICT", "REQUEST_ID_ALREADY_BOUND_TO_DIFFERENT_ACTION"
        else:
            report["state"], report["reason"] = "REPLAY_NO_SEND", "REQUEST_ALREADY_CLAIMED"
        return report

    def _health(self, frame, at, health):
        if health is None or not self._key_authorized(frame, at):
            return None
        body = {
            "record_id": "collector-check-" + uuid4().hex, "kind": "transfer.collector_health",
            "evaluation_id": frame["evidence"]["evaluation_id"], "issuer": self._config.gateway_issuer,
            "recorded_at": at, "binding": deepcopy(frame["evidence"]["target"]["subject"]),
            "data": {"checked_at": at, "available": health[0], "durable_acknowledged": health[1]},
        }
        return sign_record(body, self._config.gateway_secret, self._config.gateway_key_id)

    def _set_final(self, report, at, health=None):
        admission = report["admission"]
        report["final"] = _frame(admission["evidence"], admission["trust"], at,
                                 health=self._health(admission, at, health))
        report["postflight"] = deepcopy(report["final"])

    def _block(self, report, reason, *, at=None, health=None):
        report["reason"] = reason
        if at is not None:
            try:
                self._set_final(report, at, health)
            except Exception:
                report["reason"] = "FINAL_GATE_OBSERVATION_NOT_ESTABLISHED"
        return self._persist(report, "blocked_after_intent")

    def _collector_pinned(self):
        return getattr(self.collector, "endpoint", None) == self._collector_endpoint

    @staticmethod
    def _exchange(value, request_at, observed_at):
        value = capture(value)
        exact_keys(value, {"attempted", "attempted_at", "completed_at", "status", "response", "error"})
        if value["attempted"] is not True:
            raise InputError("Collector exchange did not establish an attempted RPC")
        if not (timestamp(request_at) <= timestamp(value["attempted_at"])
                <= timestamp(value["completed_at"]) <= timestamp(observed_at)):
            raise InputError("Collector exchange chronology is inconsistent")
        if value["status"] is not None and (type(value["status"]) is not int or not 100 <= value["status"] <= 599):
            raise InputError("Collector exchange status is invalid")
        if value["response"] is not None and type(value["response"]) is not dict:
            raise InputError("Collector response is not an envelope object")
        if value["error"] is not None:
            _identifier(value["error"])
        return value

    @staticmethod
    def _response_usable(exchange):
        return (exchange["error"] is None and type(exchange["status"]) is int
                and 200 <= exchange["status"] < 300 and exchange["response"] is not None)

    @staticmethod
    def _failed_check(exchange):
        # A measured failure of this gateway's check, not physical service death.
        return (False, False) if exchange["response"] is None else None

    def _query(self, intent, at):
        body = intent["body"]
        return sign_control({
            "kind": "collection_query", "collector_id": self._collector_id,
            "collection_id": body["collection_id"], "request_id": body["request_id"],
            "request_sha256": digest(intent), "nonce": secrets.token_hex(32), "created_at": at,
        }, self._config.gateway_secret, self._config.gateway_key_id)

    @staticmethod
    def _transport_observation(value, final_at, post_at):
        value = capture(value)
        exact_keys(value, {"attempted", "body_send_completed", "attempted_at", "dispatched_at",
                           "status", "receipt", "error"})
        if value["attempted"] is not True or type(value["body_send_completed"]) is not bool:
            raise InputError("Payload transport did not establish an attempt")
        if not timestamp(final_at) <= timestamp(value["attempted_at"]) <= timestamp(post_at):
            raise InputError("Payload attempt chronology is inconsistent")
        if value["body_send_completed"]:
            if not timestamp(value["attempted_at"]) <= timestamp(value["dispatched_at"]) <= timestamp(post_at):
                raise InputError("Payload completion chronology is inconsistent")
        elif value["dispatched_at"] is not None:
            raise InputError("An incomplete payload send has no completion timestamp")
        if value["status"] is not None and (type(value["status"]) is not int or not 100 <= value["status"] <= 599):
            raise InputError("Payload transport status is invalid")
        if value["receipt"] is not None and type(value["receipt"]) is not dict:
            raise InputError("Payload receipt must be an envelope object")
        if value["error"] is not None:
            _identifier(value["error"])
        return value

    def _postflight(self, report, at, observation=None):
        final = report["final"]
        dispatch = None
        if observation is not None and observation["body_send_completed"]:
            dispatch = sign_record({
                "record_id": "actual-dispatch-" + uuid4().hex, "kind": "transfer.dispatch",
                "evaluation_id": final["evidence"]["evaluation_id"], "issuer": self._config.gateway_issuer,
                "recorded_at": at, "binding": deepcopy(final["evidence"]["target"]["subject"]),
                "data": {"dispatched_at": observation["dispatched_at"]},
            }, self._config.gateway_secret, self._config.gateway_key_id)
        report["postflight"] = _frame(final["evidence"], final["trust"], at, operation=False, dispatch=dispatch)

    def execute(self, package, trust, payload, before_final_check=None):
        package, trust = capture(package), capture(trust)
        assess(package, trust, allow_synthetic=True)
        self._input(package, trust)
        if before_final_check is not None and not callable(before_final_check):
            raise InputError("The fault hook must be a trusted callable")
        if type(payload) not in {bytes, bytearray, memoryview} or memoryview(payload).nbytes > MAX_PAYLOAD:
            raise InputError("Payload must be bounded bytes")
        captured = bytes(payload)
        payload_sha256, length = hashlib.sha256(captured).hexdigest(), len(captured)
        at = self._clock(package["as_of"])
        subject = package["target"]["subject"]
        subject.update(deepcopy(self._config.route))
        subject["payload_sha256"] = payload_sha256
        request_id = _identifier(subject["request_id"])
        admission = _frame(package, trust, at)
        report = self._report(admission, payload_sha256, length)
        fingerprint = self._fingerprint(admission, length)
        try:
            existing = self.journal.get(request_id)
            if existing is not None:
                existing = self._row(existing, request_id)
        except Exception:
            report["reason"], report["journal_state"] = "JOURNAL_UNAVAILABLE_BEFORE_CLAIM", "UNAVAILABLE"
            return report
        if existing is not None:
            return self._replay(report, existing, fingerprint)
        try:
            policy, decision = _authorization(admission, pending=True)
        except InputError:
            report["reason"] = "POLICY_OR_PERMIT_NOT_AUTHORIZED"
            return report
        if not self._key_authorized(admission, at):
            report["reason"] = "CONFIGURED_GATEWAY_KEY_NOT_AUTHORIZED"
            return report
        if getattr(self.transport, "endpoint", None) != self._config.endpoint or not self._collector_pinned():
            report["reason"] = "CONFIGURED_ENDPOINT_CHANGED"
            return report
        intent_body = validate_intent(self._intent_body(admission, length, decision, at))
        report["collection_intent"] = sign_control(intent_body, self._config.gateway_secret, self._config.gateway_key_id)
        report["dispatch_intent"] = sign_upload_control(self._dispatch_body(subject, length, at),
                                                        self._config.gateway_secret, self._config.gateway_key_id)
        snapshot = self._snapshot(report, at)
        try:
            claimed = self.journal.claim(request_id, fingerprint, deepcopy(snapshot))
        except Exception:
            report["reason"] = "JOURNAL_INTENT_COMMIT_NOT_ESTABLISHED"
            report["journal_state"] = self._journal_state(request_id)
            return report
        try:
            claimed = self._row(claimed, request_id)
            disposition = claimed.get("claim_status")
            if disposition == "CLAIMED":
                if (claimed["fingerprint"] != fingerprint or claimed["state"] != "dispatch_intent"
                        or claimed["details"] is not None or digest(claimed["snapshot"]) != digest(snapshot)):
                    raise InputError("Journal claim does not acknowledge the owned intent")
            elif disposition in {"REPLAY", "CONFLICT"}:
                if disposition != ("REPLAY" if claimed["fingerprint"] == fingerprint else "CONFLICT"):
                    raise InputError("Journal claim disposition contradicts its fingerprint")
            else:
                raise InputError("Journal claim disposition is unsupported")
        except Exception:
            report["reason"] = "JOURNAL_CLAIM_ACKNOWLEDGEMENT_NOT_ESTABLISHED"
            report["journal_state"] = self._journal_state(request_id)
            return report
        if disposition != "CLAIMED":
            return self._replay(report, claimed, fingerprint)
        report["journal_state"] = "dispatch_intent"
        report["collector_outcome"] = "ACKNOWLEDGEMENT_NOT_ESTABLISHED"
        try:
            if not self._collector_pinned():
                raise InputError("Collector endpoint changed before collection")
            raw = self.collector.collect(deepcopy(report["collection_intent"]))
            collected_at = self._clock(at)
            exchange = self._exchange(raw, at, collected_at)
            report["collection_exchange"] = exchange
        except Exception:
            return self._block(report, "COLLECTOR_ACKNOWLEDGEMENT_NOT_ESTABLISHED")
        if not self._response_usable(exchange):
            return self._block(report, "COLLECTOR_ACKNOWLEDGEMENT_NOT_ESTABLISHED", at=collected_at,
                               health=self._failed_check(exchange))
        try:
            verify_receipt(exchange["response"], report["collection_intent"],
                           self._collector_public, self._collector_key_id, exchange["completed_at"])
        except Exception:
            return self._block(report, "COLLECTOR_ACKNOWLEDGEMENT_NOT_ESTABLISHED", at=collected_at)
        report["collection_receipt"] = deepcopy(exchange["response"])
        report["collector_outcome"] = "ACKNOWLEDGED"
        if before_final_check is not None:
            try:
                before_final_check()
            except Exception:
                return self._block(report, "TRUSTED_BEFORE_FINAL_HOOK_FAILED")
        report["collector_outcome"] = "READBACK_NOT_ESTABLISHED"
        try:
            query_at = self._clock(collected_at)
            report["status_query"] = self._query(report["collection_intent"], query_at)
            if not self._collector_pinned():
                raise InputError("Collector endpoint changed before status query")
            raw = self.collector.status(deepcopy(report["status_query"]))
            checked_at = self._clock(query_at)
            exchange = self._exchange(raw, query_at, checked_at)
            report["status_exchange"] = exchange
        except Exception:
            return self._block(report, "COLLECTOR_READBACK_NOT_ESTABLISHED")
        if not self._response_usable(exchange):
            return self._block(report, "COLLECTOR_READBACK_NOT_ESTABLISHED", at=checked_at,
                               health=self._failed_check(exchange))
        try:
            status = verify_status(exchange["response"], report["status_query"], report["collection_intent"],
                                   self._collector_public, self._collector_key_id, exchange["completed_at"])
            report["collection_status"] = deepcopy(exchange["response"])
            if status["status"] == "FOUND" and digest(status["receipt"]) != digest(report["collection_receipt"]):
                raise InputError("Collector readback changed the original saved receipt")
        except Exception:
            report["collection_status"] = None
            return self._block(report, "COLLECTOR_READBACK_NOT_ESTABLISHED", at=checked_at)
        if status["status"] == "NOT_FOUND":
            return self._block(report, "COLLECTOR_RECORD_NOT_FOUND", at=checked_at, health=(True, False))
        try:
            final_at = self._clock(checked_at)
            self._set_final(report, final_at, (True, True))
        except Exception:
            return self._block(report, "FINAL_GATE_OBSERVATION_NOT_ESTABLISHED")
        report["collector_outcome"] = "FRESH_READBACK_CONFIRMED"
        if not self._key_authorized(admission, final_at):
            return self._block(report, "GATEWAY_KEY_NOT_AUTHORIZED_AT_SEND")
        try:
            _, final_decision = _authorization(report["final"], pending=False)
            if digest(final_decision) != intent_body["decision_sha256"]:
                raise InputError("The current permit differs from the collected permit")
        except InputError:
            return self._block(report, "FINAL_ASSESSOR_RECHECK_DID_NOT_ALLOW")
        if getattr(self.transport, "endpoint", None) != self._config.endpoint or not self._collector_pinned():
            return self._block(report, "CONFIGURED_ENDPOINT_CHANGED")
        report["attempted"] = True
        report["state"], report["reason"] = "OUTCOME_UNKNOWN", "RESPONSE_NOT_CONFIRMED"
        try:
            raw = self.transport.send(captured, deepcopy(report["dispatch_intent"]))
        except Exception:
            raw = None
            report["reason"] = "TRANSPORT_EXCEPTION"
        try:
            post_at = self._clock(final_at)
            self._postflight(report, post_at)
        except Exception:
            report["reason"] = "POSTFLIGHT_CLOCK_NOT_ESTABLISHED"
            return self._persist(report, "outcome_unknown")
        if raw is None:
            return self._persist(report, "outcome_unknown")
        try:
            observation = self._transport_observation(raw, final_at, post_at)
            report["payload_transport"] = observation
        except Exception:
            report["reason"] = "TRANSPORT_OBSERVATION_NOT_ESTABLISHED"
            return self._persist(report, "outcome_unknown")
        if not self._key_authorized(admission, post_at):
            report["reason"] = "GATEWAY_KEY_NOT_AUTHORIZED_AT_POSTFLIGHT"
            return self._persist(report, "outcome_unknown")
        self._postflight(report, post_at, observation)
        try:
            report["payload_receipt"] = verify_payload_receipt(
                observation, subject, payload_sha256, length, post_at,
                self._config.receiver_public, self._config.receiver_key_id)
        except Exception:
            report["reason"] = "RECEIVER_RECEIPT_NOT_CONFIRMED"
            return self._persist(report, "outcome_unknown")
        report["state"], report["reason"] = "RECEIPT_CONFIRMED", "PINNED_RECEIVER_ATTESTED_MATCHING_BYTES"
        return self._persist(report, "receipt_confirmed")

    def reconcile(self, request_id):
        _identifier(request_id)
        report = {
            "format": "collector-pilot-reconciliation/0.1", "request_id": request_id,
            "state": "NOT_ESTABLISHED", "reason": "READBACK_NOT_ESTABLISHED",
            "journal_state": "NOT_CLAIMED", "attempted": False, "upload_resumed": False,
            "collection_intent": None, "status_query": None, "status_exchange": None,
            "collection_status": None, "collection_receipt": None,
        }
        try:
            row = self.journal.get(request_id)
            if row is None:
                report["state"], report["reason"] = "REQUEST_NOT_FOUND", "NO_OWNED_JOURNAL_REQUEST"
                return report
            row = self._row(row, request_id)
            report["journal_state"] = row["state"]
        except Exception:
            report["state"], report["reason"] = "JOURNAL_UNAVAILABLE", "JOURNAL_SNAPSHOT_NOT_ESTABLISHED"
            report["journal_state"] = "UNAVAILABLE"
            return report
        snapshot = row["snapshot"]
        report["collection_intent"] = deepcopy(snapshot["collection_intent"])
        try:
            query_at = self._clock(snapshot["prepared_at"])
            if not self._key_authorized(snapshot["admission"], query_at) or not self._collector_pinned():
                raise InputError("Configured gateway key or collector endpoint is unavailable")
            report["status_query"] = self._query(report["collection_intent"], query_at)
            raw = self.collector.status(deepcopy(report["status_query"]))
            observed_at = self._clock(query_at)
            exchange = self._exchange(raw, query_at, observed_at)
            report["status_exchange"] = exchange
            if not self._response_usable(exchange):
                return report
            status = verify_status(exchange["response"], report["status_query"], report["collection_intent"],
                                   self._collector_public, self._collector_key_id, exchange["completed_at"])
            report["collection_status"] = deepcopy(exchange["response"])
            report["collection_receipt"] = deepcopy(status["receipt"])
            report["state"] = status["status"]
            report["reason"] = ("COLLECTOR_RECORD_FOUND_NO_UPLOAD_RESUMED" if status["status"] == "FOUND"
                                else "COLLECTOR_RECORD_NOT_FOUND_AT_CHECK")
        except Exception:
            return report
        return report
