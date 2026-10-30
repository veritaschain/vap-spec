"""One-shot controlled local uploader over measured immutable raw bytes."""

import hashlib
from copy import deepcopy
from uuid import uuid4

from .protocol import (
    GateConfig, InputError, MAX_PAYLOAD, digest, public_key, sign_control,
    sign_record, timestamp, utc_now, validate_endpoint, verify_control,
)
from .journal import STATES
from incident_assessor.assess import assess
from incident_assessor.model import digest_hex, exact_keys, text


def _frame(package, trust, *, subject=None, operation_at=None, as_of=None):
    package, trust = deepcopy(package), deepcopy(trust)
    if subject is not None:
        package["target"]["subject"] = deepcopy(subject)
    if operation_at is not None:
        package["target"]["operation_at"] = operation_at
    if as_of is not None:
        package["as_of"] = as_of
        trust["as_of"] = as_of
    trust["target_sha256"] = digest(package["target"])
    return package, trust


def _allowed(assessment):
    return assessment["assessments"].get("transfer_authorization") == "ALLOW"


def verify_receipt(value, subject, payload_sha256, length, post_at, receiver_public, receiver_key_id):
    """Verify a receiver statement against independently supplied measured bindings."""
    if type(value) is not dict or not {"body_send_completed", "status", "receipt", "attempted_at"} <= value.keys():
        raise InputError("Receipt verification requires a structured transport observation")
    if type(subject) is not dict or "request_id" not in subject:
        raise InputError("Receipt verification requires an independently supplied subject")
    text(subject["request_id"])
    digest_hex(payload_sha256)
    if type(length) is not int or not 0 <= length <= MAX_PAYLOAD:
        raise InputError("Measured byte length must be an integer within the payload limit")
    if (value["body_send_completed"] is not True or type(value["status"]) is not int
            or not 200 <= value["status"] < 300):
        raise InputError("Transport did not establish a successful completed response")
    body = verify_control(value["receipt"], receiver_public, receiver_key_id, "upload_receipt")
    exact_keys(body, {"kind", "request_id", "subject_sha256", "payload_sha256",
                      "byte_length", "received_at", "receipt_id"})
    text(body["request_id"])
    text(body["receipt_id"])
    digest_hex(body["subject_sha256"])
    digest_hex(body["payload_sha256"])
    if type(body["byte_length"]) is not int or not 0 <= body["byte_length"] <= MAX_PAYLOAD:
        raise InputError("Receipt byte length must be an integer within the payload limit")
    if (body["request_id"] != subject["request_id"] or body["subject_sha256"] != digest(subject)
            or body["payload_sha256"] != payload_sha256 or body["byte_length"] != length):
        raise InputError("Receipt does not bind the actual request and measured bytes")
    if not timestamp(value["attempted_at"]) <= timestamp(body["received_at"]) <= timestamp(post_at):
        raise InputError("Receipt chronology is inconsistent")
    return deepcopy(value["receipt"])


def _validate_journal_row(row, request_id):
    exact_keys(row, {"request_id", "fingerprint", "state", "snapshot", "details"}, ("claim_status",))
    if row["request_id"] != request_id or row["state"] not in STATES:
        raise InputError("Journal acknowledgement refers to another request or unknown state")
    digest_hex(row["fingerprint"])
    if type(row["snapshot"]) is not dict or (row["details"] is not None and type(row["details"]) is not dict):
        raise InputError("Journal acknowledgement has malformed persisted material")


class Gateway:
    def __init__(self, config, journal, transport, clock=utc_now):
        if not isinstance(config, GateConfig):
            raise InputError("Gateway requires a trusted GateConfig")
        self._config = GateConfig(
            config.endpoint, deepcopy(config.route), config.gateway_secret, config.gateway_key_id,
            config.gateway_issuer, config.receiver_public, config.receiver_key_id,
        )
        self._route = deepcopy(self._config.route)
        self._endpoint = validate_endpoint(self._config.endpoint)
        if getattr(transport, "endpoint", None) != self._endpoint:
            raise InputError("Transport endpoint differs from the controller-pinned route")
        if not callable(clock) or not callable(getattr(transport, "send", None)):
            raise InputError("Gateway requires a clock and a one-shot transport")
        self.journal, self.transport, self.clock = journal, transport, clock

    def _clock(self):
        value = self.clock()
        timestamp(value)
        return value

    def _key_authorized(self, package, trust, at):
        key = trust["keys"].get(self._config.gateway_key_id)
        if key is None:
            return False
        return (
            key["public_key"] == public_key(self._config.gateway_secret)
            and key["issuer"] == self._config.gateway_issuer
            and "gateway" in key["roles"]
            and package["target"]["authorities"].get("gateway") == self._config.gateway_issuer
            and timestamp(key["not_before"]) <= timestamp(at) < timestamp(key["not_after"])
        )

    @staticmethod
    def _report(package, trust, assessment, payload_sha256, byte_length):
        return {
            "format": "upload-pilot-report/0.1", "state": "BLOCKED_WITHOUT_ATTEMPT",
            "attempted": False, "reason": "NOT_ADMITTED", "payload_sha256": payload_sha256,
            "byte_length": byte_length, "journal_state": "NOT_CLAIMED", "receipt": None,
            "preflight_evidence": deepcopy(package), "preflight_trust": deepcopy(trust),
            "preflight_assessment": deepcopy(assessment), "evidence": deepcopy(package),
            "trust": deepcopy(trust), "postflight_assessment": deepcopy(assessment),
            "final_gate_evidence": None, "final_gate_trust": None, "final_gate_assessment": None,
            "dispatch_intent": None, "transport_observation": None,
        }

    def _journal_state(self, request_id):
        try:
            row = self.journal.get(request_id)
            if row is not None:
                _validate_journal_row(row, request_id)
            return "NOT_CLAIMED" if row is None else row["state"]
        except Exception:
            return "UNAVAILABLE"

    def _persist(self, report, request_id, state):
        report["journal_state"] = state
        try:
            row = self.journal.finish(request_id, state, deepcopy(report))
            _validate_journal_row(row, request_id)
            subject = report["preflight_evidence"]["target"]["subject"]
            fingerprint = digest({"evaluation_id": report["preflight_evidence"]["evaluation_id"],
                                  "subject": subject, "byte_length": report["byte_length"]})
            if (row["state"] != state or row["fingerprint"] != fingerprint
                    or digest(row["details"]) != digest(report)):
                raise RuntimeError("Persisted state was not confirmed")
        except Exception:
            report["state"] = "OUTCOME_UNKNOWN"
            report["reason"] = "JOURNAL_RESULT_PERSISTENCE_FAILED"
            report["receipt"] = None
            report["journal_state"] = self._journal_state(request_id)
        return report

    @staticmethod
    def _replay(report, row, fingerprint):
        report["journal_state"] = row["state"]
        if row["fingerprint"] != fingerprint:
            report["state"] = "REQUEST_ID_CONFLICT"
            report["reason"] = "REQUEST_ID_ALREADY_BOUND_TO_DIFFERENT_ACTION"
        else:
            report["state"] = "REPLAY_NO_SEND"
            report["reason"] = "REQUEST_ALREADY_CLAIMED_RECEIPT_NOT_REASSERTED"
        # Persisted details may be corrupt or transplanted. They never become a new receipt assertion.
        report["receipt"] = None
        return report

    def _postflight(self, report, at, transport_result=None):
        package, trust = _frame(report["preflight_evidence"], report["preflight_trust"], as_of=at)
        if transport_result is not None and transport_result["body_send_completed"]:
            body = {
                "record_id": "actual-dispatch-" + uuid4().hex,
                "evaluation_id": package["evaluation_id"], "kind": "transfer.dispatch",
                "issuer": self._config.gateway_issuer, "recorded_at": at,
                "binding": deepcopy(package["target"]["subject"]),
                "data": {"dispatched_at": transport_result["dispatched_at"]},
            }
            package["records"].append(sign_record(body, self._config.gateway_secret, self._config.gateway_key_id))
        report["evidence"], report["trust"] = package, trust
        report["postflight_assessment"] = assess(package, trust, allow_synthetic=True)

    @staticmethod
    def _transport_result(value, final_at, post_at):
        exact_keys(value, {"attempted", "body_send_completed", "attempted_at", "dispatched_at",
                           "status", "receipt", "error"})
        if value["attempted"] is not True or type(value["body_send_completed"]) is not bool:
            raise InputError("Transport did not establish an attempt observation")
        if not timestamp(final_at) <= timestamp(value["attempted_at"]) <= timestamp(post_at):
            raise InputError("Transport attempt chronology is inconsistent")
        if value["body_send_completed"]:
            if not timestamp(value["attempted_at"]) <= timestamp(value["dispatched_at"]) <= timestamp(post_at):
                raise InputError("Transport body completion chronology is inconsistent")
        elif value["dispatched_at"] is not None:
            raise InputError("Incomplete body send cannot establish dispatch completion time")
        if value["status"] is not None and (type(value["status"]) is not int or not 100 <= value["status"] <= 599):
            raise InputError("Invalid transport status")
        if value["error"] is not None and type(value["error"]) is not str:
            raise InputError("Invalid transport error classification")
        if value["receipt"] is not None and type(value["receipt"]) is not dict:
            raise InputError("Invalid receipt envelope")
        return deepcopy(value)

    def _receipt(self, value, subject, payload_sha256, length, post_at):
        return verify_receipt(value, subject, payload_sha256, length, post_at,
                              self._config.receiver_public, self._config.receiver_key_id)

    def execute(self, package, trust, payload, *, after_snapshot=None, before_send=None):
        package, trust = deepcopy(package), deepcopy(trust)
        # Validate the original separate evaluator pin before modifying any observation.
        assess(package, trust, allow_synthetic=True)
        if package["workflow"] != "transfer" or trust["mode"] != "synthetic-test-only":
            raise InputError("This local pilot accepts explicitly synthetic transfer evidence only")
        for hook in (after_snapshot, before_send):
            if hook is not None and not callable(hook):
                raise InputError("Fault-injection hooks must be trusted callables")
        if type(payload) not in (bytes, bytearray, memoryview):
            raise InputError("Upload payload must be bytes, bytearray or memoryview")
        if memoryview(payload).nbytes > MAX_PAYLOAD:
            raise InputError("Upload exceeds the 1 MiB pilot payload limit")
        captured = bytes(payload)
        payload_sha256, length = hashlib.sha256(captured).hexdigest(), len(captured)
        snapshot_hook_failed = False
        if after_snapshot is not None:
            try:
                after_snapshot()
            except Exception:
                snapshot_hook_failed = True
        admitted_at = self._clock()
        subject = deepcopy(package["target"]["subject"])
        subject.update(deepcopy(self._route))
        subject["payload_sha256"] = payload_sha256
        actual, actual_trust = _frame(package, trust, subject=subject, operation_at=admitted_at, as_of=admitted_at)
        preflight = assess(actual, actual_trust, allow_synthetic=True)
        report = self._report(actual, actual_trust, preflight, payload_sha256, length)
        if snapshot_hook_failed:
            report["reason"] = "TRUSTED_SNAPSHOT_HOOK_FAILED"
            return report
        request_id = subject["request_id"]
        fingerprint = digest({"evaluation_id": actual["evaluation_id"], "subject": subject, "byte_length": length})
        try:
            existing = self.journal.get(request_id)
            if existing is not None:
                _validate_journal_row(existing, request_id)
        except Exception:
            report["reason"] = "JOURNAL_UNAVAILABLE_BEFORE_CLAIM"
            report["journal_state"] = "UNAVAILABLE"
            return report
        if existing is not None:
            return self._replay(report, existing, fingerprint)
        if not _allowed(preflight):
            report["reason"] = "ASSESSOR_DID_NOT_ALLOW_MEASURED_TARGET"
            return report
        if not self._key_authorized(actual, actual_trust, admitted_at):
            report["reason"] = "CONFIGURED_GATEWAY_KEY_NOT_AUTHORIZED"
            return report
        if getattr(self.transport, "endpoint", None) != self._endpoint:
            report["reason"] = "TRANSPORT_ENDPOINT_CHANGED"
            return report
        intent = sign_control({
            "kind": "dispatch_intent", "request_id": request_id, "subject_sha256": digest(subject),
            "payload_sha256": payload_sha256, "byte_length": length, "created_at": admitted_at,
        }, self._config.gateway_secret, self._config.gateway_key_id)
        report["dispatch_intent"] = intent
        snapshot = {
            "format": "upload-pilot-intent/0.1", "request_id": request_id, "subject_sha256": digest(subject),
            "payload_sha256": payload_sha256, "byte_length": length, "prepared_at": admitted_at,
            "dispatch_intent": deepcopy(intent), "evidence": deepcopy(actual), "trust": deepcopy(actual_trust),
            "preflight_assessment": deepcopy(preflight),
        }
        try:
            claimed = self.journal.claim(request_id, fingerprint, snapshot)
        except Exception:
            report["reason"] = "JOURNAL_INTENT_COMMIT_NOT_ESTABLISHED"
            report["journal_state"] = self._journal_state(request_id)
            return report
        try:
            _validate_journal_row(claimed, request_id)
            claim_status = claimed.get("claim_status")
            if claim_status == "CLAIMED":
                if (claimed["fingerprint"] != fingerprint or claimed["state"] != "dispatch_intent"
                        or claimed["details"] is not None or digest(claimed["snapshot"]) != digest(snapshot)):
                    raise InputError("Claim acknowledgement does not bind the committed owned intent")
            elif claim_status in {"REPLAY", "CONFLICT"}:
                if claim_status != ("REPLAY" if claimed["fingerprint"] == fingerprint else "CONFLICT"):
                    raise InputError("Claim acknowledgement is inconsistent with its stored fingerprint")
            else:
                raise InputError("Claim acknowledgement is missing a supported disposition")
        except Exception:
            report["reason"] = "JOURNAL_CLAIM_ACKNOWLEDGEMENT_NOT_ESTABLISHED"
            report["journal_state"] = self._journal_state(request_id)
            return report
        if claim_status != "CLAIMED":
            return self._replay(report, claimed, fingerprint)
        report["journal_state"] = "dispatch_intent"
        hook_failed = False
        if before_send is not None:
            try:
                before_send()
            except Exception:
                hook_failed = True
        try:
            final_at = self._clock()
            if timestamp(final_at) < timestamp(admitted_at):
                raise InputError("Gateway clock regressed after admission")
            final_package, final_trust = _frame(actual, actual_trust, operation_at=final_at, as_of=final_at)
            final_assessment = assess(final_package, final_trust, allow_synthetic=True)
            report["final_gate_evidence"] = final_package
            report["final_gate_trust"] = final_trust
            report["final_gate_assessment"] = final_assessment
            self._postflight(report, final_at)
        except Exception:
            report["reason"] = "FINAL_GATE_OBSERVATION_NOT_ESTABLISHED"
            return self._persist(report, request_id, "blocked_after_intent")
        if hook_failed:
            report["reason"] = "TRUSTED_BEFORE_SEND_HOOK_FAILED"
            return self._persist(report, request_id, "blocked_after_intent")
        if not _allowed(final_assessment):
            report["reason"] = "FINAL_ASSESSOR_RECHECK_DID_NOT_ALLOW"
            return self._persist(report, request_id, "blocked_after_intent")
        if not self._key_authorized(actual, actual_trust, final_at):
            report["reason"] = "GATEWAY_KEY_NOT_AUTHORIZED_AT_SEND"
            return self._persist(report, request_id, "blocked_after_intent")
        if getattr(self.transport, "endpoint", None) != self._endpoint:
            report["reason"] = "TRANSPORT_ENDPOINT_CHANGED"
            return self._persist(report, request_id, "blocked_after_intent")

        # The durable intent exists before this sole transport invocation.
        report["attempted"] = True
        transport_exception = False
        try:
            response = self.transport.send(captured, deepcopy(intent))
        except Exception:
            response, transport_exception = None, True
        report["state"] = "OUTCOME_UNKNOWN"
        report["reason"] = "TRANSPORT_EXCEPTION" if transport_exception else "RESPONSE_NOT_CONFIRMED"
        try:
            post_at = self._clock()
            if timestamp(post_at) < timestamp(final_at):
                raise InputError("Gateway clock regressed after transport")
        except Exception:
            report["reason"] = "POSTFLIGHT_CLOCK_NOT_ESTABLISHED"
            return self._persist(report, request_id, "outcome_unknown")
        if transport_exception:
            self._postflight(report, post_at)
            return self._persist(report, request_id, "outcome_unknown")
        try:
            observed = self._transport_result(response, final_at, post_at)
        except Exception:
            self._postflight(report, post_at)
            report["reason"] = "TRANSPORT_OBSERVATION_NOT_ESTABLISHED"
            return self._persist(report, request_id, "outcome_unknown")
        report["transport_observation"] = {k: deepcopy(observed[k]) for k in (
            "attempted", "body_send_completed", "attempted_at", "dispatched_at", "status",
        )}
        if not self._key_authorized(actual, actual_trust, post_at):
            self._postflight(report, post_at)
            report["reason"] = "GATEWAY_KEY_NOT_AUTHORIZED_AT_POSTFLIGHT"
            return self._persist(report, request_id, "outcome_unknown")
        self._postflight(report, post_at, observed)
        try:
            report["receipt"] = self._receipt(observed, subject, payload_sha256, length, post_at)
        except Exception:
            report["reason"] = "RECEIVER_RECEIPT_NOT_CONFIRMED"
            return self._persist(report, request_id, "outcome_unknown")
        report["state"] = "RECEIPT_CONFIRMED"
        report["reason"] = "PINNED_RECEIVER_ATTESTED_MATCHING_BYTES"
        return self._persist(report, request_id, "receipt_confirmed")
