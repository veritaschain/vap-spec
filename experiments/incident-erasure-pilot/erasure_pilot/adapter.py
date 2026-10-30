"""Pure verification of bounded local erasure evidence under separate trust pins.

An authenticated local observation is a same-controller statement about a named
directory entry. It is never converted into independent review or media erasure.
"""

from copy import deepcopy

from incident_assessor.assess import assess
from incident_assessor.erasure import validate_data

from .protocol import (EXCLUSIONS, LOCATION, MAX_OBJECT, InputError, capture,
                       digest, digest_hex, exact_keys, identifier,
                       timestamp, verify_message, verify_record)

PIN_FIELDS = {"provider_id", "tenant_id", "location", "requester_key_id",
              "provider_key_id", "observer_key_id", "keys"}
KEY_FIELDS = {"public_key", "issuer", "organization", "roles", "not_before", "not_after"}
MANIFEST_FIELDS = {"provider_id", "tenant_id", "object_id", "version_id", "sha256", "byte_length", "location"}
SUBJECT_FIELDS = {"request_id", "provider_id", "tenant_id", "object_ids", "payload_sha256", "stage"}
RECORD_FIELDS = {"record_id", "evaluation_id", "kind", "issuer", "recorded_at", "binding", "data"}
RESULT_FIELDS = {"state", "attempted", "acknowledgement", "attestation", "receipt", "journal_state", "reason"}
RECEIPT_FIELDS = {"kind", "task_sha256", "request_id", "manifest_sha256", "before", "unlinked_at", "observed_at", "after"}
OBSERVATION_FIELDS = {"kind", "task_sha256", "manifest_sha256", "provider_id", "tenant_id", "location",
                      "object_id", "version_id", "phase", "previous_sha256", "completion_sha256",
                      "window_start", "window_end", "measurement"}
ROLE_NAMES = {"requester": "responder", "provider": "provider", "observer": "reviewer"}
TERMINALS = {"BLOCKED", "OUTCOME_UNKNOWN", "ACKNOWLEDGED_ONLY", "LOCAL_UNLINK_CONFIRMED"}
RESULT_STATES = TERMINALS | {"REPLAY_NO_ACTION", "REQUEST_ID_CONFLICT"}
JOURNAL_STATES = TERMINALS | {"NOT_CLAIMED", "UNAVAILABLE", "deletion_intent"}
LIMITATIONS = [
    "Synthetic application experiment with one immutable object and one active namespace per task.",
    "Requester, provider and observer share one local controller and organization; no independent review is established.",
    "Signatures attribute statements under separately supplied pins; they do not prove a malicious controller told the truth or establish external event time.",
    "Local observations concern a named directory entry during the stated read window, not irreversible deletion or storage-media sanitization.",
    "Absence without a matching before observation and linked completion does not establish prior presence or a removal operation.",
    "Missing evidence does not establish absence of copies, activity or contradictory evidence outside the observed namespace.",
    "No external provider integration, key revocation, normative conformance or legal-compliance determination is performed.",
]


def _capture(value):
    """Own a bounded, strict JSON representation without touching the filesystem."""
    return capture(value)


def _length(value):
    if type(value) is not int or not 1 <= value <= MAX_OBJECT:
        raise InputError("Object byte length must be a bounded positive integer")


def _key(pins, role):
    key_id = pins[role + "_key_id"]
    return key_id, pins["keys"][key_id]


def _key_time(key, at):
    if not timestamp(key["not_before"]) <= at < timestamp(key["not_after"]):
        raise InputError("Evidence or action time is outside pinned key validity")


def validate_pins(pins):
    pins = _capture(pins)
    exact_keys(pins, PIN_FIELDS)
    identifier(pins["provider_id"])
    identifier(pins["tenant_id"])
    if pins["location"] != LOCATION:
        raise InputError("Only the pinned active object namespace is supported")
    ids = []
    for role in ROLE_NAMES:
        ids.append(identifier(pins[role + "_key_id"]))
    if len(set(ids)) != 3:
        raise InputError("Requester, provider and observer require distinct key identifiers")
    exact_keys(pins["keys"], set(ids))
    public_keys = set()
    for role, expected_role in ROLE_NAMES.items():
        _, key = _key(pins, role)
        exact_keys(key, KEY_FIELDS)
        digest_hex(key["public_key"])
        identifier(key["issuer"])
        if key["organization"] != "single-local-controller" or key["roles"] != [expected_role]:
            raise InputError("Pinned organization or exact role differs from this local experiment")
        left, right = timestamp(key["not_before"]), timestamp(key["not_after"])
        if left >= right:
            raise InputError("Pinned key validity interval must be nonempty")
        public_keys.add(key["public_key"])
    if len(public_keys) != 3:
        raise InputError("The three local roles require distinct public keys")
    return pins


def _manifest(manifest, pins):
    exact_keys(manifest, MANIFEST_FIELDS)
    for name in ("provider_id", "tenant_id", "object_id", "version_id"):
        identifier(manifest[name])
    digest_hex(manifest["sha256"])
    _length(manifest["byte_length"])
    for name in ("provider_id", "tenant_id", "location"):
        if manifest[name] != pins[name]:
            raise InputError("Manifest differs from the independently pinned provider, tenant or location")


def _record(envelope, pins, role, kind, *, context=None, cutoff=None):
    key_id, key = _key(pins, role)
    body = verify_record(envelope, key["public_key"], key_id, kind)
    exact_keys(body, RECORD_FIELDS)
    for name in ("record_id", "evaluation_id", "issuer"):
        identifier(body[name])
    if body["issuer"] != key["issuer"]:
        raise InputError("Record issuer differs from the separately pinned identity")
    recorded = timestamp(body["recorded_at"])
    _key_time(key, recorded)
    if cutoff is not None and recorded > cutoff:
        raise InputError("Record is later than the declared observation cutoff")
    exact_keys(body["binding"], SUBJECT_FIELDS)
    if context is not None and (body["binding"] != context["subject"]
                                or body["evaluation_id"] != context["evaluation_id"]):
        raise InputError("Record does not bind the complete target and evaluation")
    validate_data(kind, body["data"])
    return body


def validate_task(task, pins, at):
    pins, task = validate_pins(pins), _capture(task)
    action_at = timestamp(at)
    exact_keys(task, {"format", "manifest", "request", "authorization"})
    if task["format"] != "incident-erasure-task/0.1":
        raise InputError("Unsupported erasure task format")
    manifest = task["manifest"]
    _manifest(manifest, pins)
    request = _record(task["request"], pins, "requester", "erasure.request")
    subject = request["binding"]
    identifier(subject["request_id"])
    expected_subject = {
        "request_id": subject["request_id"], "provider_id": manifest["provider_id"],
        "tenant_id": manifest["tenant_id"], "object_ids": [manifest["object_id"]],
        "payload_sha256": digest(manifest), "stage": "erasure",
    }
    if subject != expected_subject:
        raise InputError("Request does not bind the complete immutable object manifest")
    data = request["data"]
    locations = data["requested_locations"]
    if LOCATION not in locations or not set(locations).issubset({LOCATION, *EXCLUSIONS}):
        raise InputError("Request contains unsupported or missing locations")
    if request["recorded_at"] != data["requested_at"]:
        raise InputError("Request record and event time must agree")
    key_id, key = _key(pins, "requester")
    authorization = verify_message(task["authorization"], key["public_key"], key_id, "deletion_authorization")
    exact_keys(authorization, {"kind", "request_sha256", "manifest_sha256", "authorized_at", "valid_until"})
    digest_hex(authorization["request_sha256"])
    digest_hex(authorization["manifest_sha256"])
    if (authorization["request_sha256"] != digest(task["request"])
            or authorization["manifest_sha256"] != digest(manifest)
            or authorization["authorized_at"] != data["requested_at"]):
        raise InputError("Authorization does not bind this exact request, manifest and request time")
    start, end = timestamp(authorization["authorized_at"]), timestamp(authorization["valid_until"])
    if not start <= action_at < end:
        raise InputError("Proposed action is outside the half-open authorization interval")
    _key_time(key, start)
    _key_time(key, action_at)
    return {
        "request_id": subject["request_id"], "evaluation_id": request["evaluation_id"],
        "subject": deepcopy(subject), "operation_at": data["requested_at"],
        "valid_until": authorization["valid_until"], "task_sha256": digest(task),
        "manifest_sha256": digest(manifest), "request_record_id": request["record_id"],
        "manifest": deepcopy(manifest),
    }


def _measurement(value):
    exact_keys(value, {"state", "sha256", "byte_length"})
    if value["state"] == "PRESENT":
        digest_hex(value["sha256"])
        _length(value["byte_length"])
    elif value["state"] == "ABSENT":
        if value["sha256"] is not None or value["byte_length"] is not None:
            raise InputError("An absent entry cannot carry content measurements")
    else:
        raise InputError("Unsupported local observation state")


def _provider_result(result, task, pins, context, cutoff):
    if result is None:
        return [], None
    exact_keys(result, RESULT_FIELDS)
    state = result["state"]
    if type(state) is not str or state not in RESULT_STATES or type(result["attempted"]) is not bool:
        raise InputError("Invalid provider result state or attempted flag")
    journal = result["journal_state"]
    if journal is not None and (type(journal) is not str or journal not in JOURNAL_STATES):
        raise InputError("Unsupported provider journal state")
    if type(result["reason"]) is not str or not result["reason"].strip() or len(result["reason"]) > 256:
        raise InputError("Provider result requires a bounded classification reason")
    ack, attestation, receipt = (result[name] for name in ("acknowledgement", "attestation", "receipt"))
    if state == "LOCAL_UNLINK_CONFIRMED":
        if not result["attempted"] or journal != state or any(item is None for item in (ack, attestation, receipt)):
            raise InputError("Confirmed local unlink requires its complete terminal evidence")
    else:
        if attestation is not None or receipt is not None:
            raise InputError("Non-confirmed outcomes cannot carry completion evidence")
        if state != "OUTCOME_UNKNOWN" and result["attempted"]:
            raise InputError("This provider state cannot assert an entered unlink call")
        if state == "ACKNOWLEDGED_ONLY" and (ack is None or journal != state):
            raise InputError("Acknowledgement-only outcome lacks its terminal acknowledgement")
        if state in {"REPLAY_NO_ACTION", "REQUEST_ID_CONFLICT"} and ack is not None:
            raise InputError("Replay or conflict cannot return new acknowledgement evidence")
    records, ack_body = [], None
    if ack is not None:
        ack_body = _record(ack, pins, "provider", "erasure.acknowledgement", context=context, cutoff=cutoff)
        data = ack_body["data"]
        if (data["request_record_id"] != context["request_record_id"] or data["queue_state"] != "received"
                or data["acknowledged_at"] != ack_body["recorded_at"]
                or timestamp(data["acknowledged_at"]) < timestamp(context["operation_at"])):
            raise InputError("Acknowledgement has inconsistent request, queue or event time")
        records.append(ack)
    if attestation is None:
        return records, None
    attested = _record(attestation, pins, "provider", "erasure.provider_attestation", context=context, cutoff=cutoff)
    data = attested["data"]
    if (data["request_record_id"] != context["request_record_id"] or data["locations"] != [LOCATION]
            or set(data["exclusions"]) != set(EXCLUSIONS) or data["completed_at"] != attested["recorded_at"]):
        raise InputError("Provider attestation differs from the exact local scope and exclusions")
    key_id, key = _key(pins, "provider")
    body = verify_message(receipt, key["public_key"], key_id, "local_unlink_receipt")
    exact_keys(body, RECEIPT_FIELDS)
    for name in ("task_sha256", "manifest_sha256"):
        digest_hex(body[name])
        if body[name] != context[name]:
            raise InputError("Local receipt binds a different task or manifest")
    if body["request_id"] != context["request_id"] or body["after"] != "ABSENT":
        raise InputError("Local receipt request or postcondition differs")
    exact_keys(body["before"], {"sha256", "byte_length"})
    digest_hex(body["before"]["sha256"])
    _length(body["before"]["byte_length"])
    manifest = context["manifest"]
    if body["before"] != {name: manifest[name] for name in ("sha256", "byte_length")}:
        raise InputError("Receipt before measurement does not match the authorized object")
    unlinked, observed = timestamp(body["unlinked_at"]), timestamp(body["observed_at"])
    acknowledged = timestamp(ack_body["data"]["acknowledged_at"])
    if not acknowledged <= unlinked <= observed <= cutoff or body["observed_at"] != data["completed_at"]:
        raise InputError("Receipt, acknowledgement and completion chronology is inconsistent")
    _key_time(key, unlinked)
    _key_time(key, observed)
    # A later offline recheck may follow authorization expiry. The actual action
    # still must have occurred while the original authorization was applicable.
    validate_task(task, pins, body["unlinked_at"])
    records.append(attestation)
    return records, body


def _observation(envelope, phase, pins, context, cutoff):
    if envelope is None:
        return None
    key_id, key = _key(pins, "observer")
    body = verify_message(envelope, key["public_key"], key_id, "local_namespace_observation")
    exact_keys(body, OBSERVATION_FIELDS)
    if body["phase"] != phase:
        raise InputError("Observation phase differs from its bundle position")
    for name in ("task_sha256", "manifest_sha256"):
        digest_hex(body[name])
        if body[name] != context[name]:
            raise InputError("Observation binds a different task or manifest")
    for name in ("provider_id", "tenant_id", "location", "object_id", "version_id"):
        if body[name] != context["manifest"][name]:
            raise InputError("Observation binds a different provider, tenant or object namespace")
    for name in ("previous_sha256", "completion_sha256"):
        if body[name] is not None:
            digest_hex(body[name])
        if phase == "before" and body[name] is not None:
            raise InputError("Before observation cannot reference previous or completion evidence")
    left, right = timestamp(body["window_start"]), timestamp(body["window_end"])
    if not timestamp(context["operation_at"]) <= left <= right <= cutoff:
        raise InputError("Observation window is outside the task chronology or cutoff")
    _key_time(key, left)
    _key_time(key, right)
    _measurement(body["measurement"])
    return body


def verify_bundle(bundle, pins, expected_task_sha256):
    """Validate supplied evidence; never inspect storage, mutate it or sign claims."""
    pins, bundle = validate_pins(pins), _capture(bundle)
    digest_hex(expected_task_sha256)
    exact_keys(bundle, {"format", "task", "as_of", "provider_result", "before", "after"})
    if bundle["format"] != "incident-erasure-bundle/0.1":
        raise InputError("Unsupported erasure evidence bundle")
    if digest(bundle["task"]) != expected_task_sha256:
        raise InputError("Task differs from the independently supplied task digest")
    cutoff = timestamp(bundle["as_of"])
    task = bundle["task"]
    # Validate shape before extracting the historical request time.
    exact_keys(task, {"format", "manifest", "request", "authorization"})
    request = _record(task["request"], pins, "requester", "erasure.request", cutoff=cutoff)
    context = validate_task(task, pins, request["data"]["requested_at"])
    records, receipt = _provider_result(bundle["provider_result"], task, pins, context, cutoff)
    before = _observation(bundle["before"], "before", pins, context, cutoff)
    after = _observation(bundle["after"], "after", pins, context, cutoff)
    if before is not None and receipt is not None:
        if timestamp(before["window_end"]) > timestamp(receipt["unlinked_at"]):
            raise InputError("Before observation follows the claimed unlink operation")
    if after is not None and before is not None:
        if after["previous_sha256"] is not None and after["previous_sha256"] != digest(bundle["before"]):
            raise InputError("After observation references a different supplied before observation")
        if timestamp(after["window_start"]) < timestamp(before["window_end"]):
            raise InputError("After observation precedes the supplied before observation")
    if after is not None and receipt is not None:
        attestation = bundle["provider_result"]["attestation"]
        if after["completion_sha256"] is not None and after["completion_sha256"] != digest(attestation):
            raise InputError("After observation references a different supplied completion attestation")
        if timestamp(after["window_start"]) < timestamp(receipt["observed_at"]):
            raise InputError("After observation precedes completion")

    target = {
        "subject": context["subject"], "operation_at": context["operation_at"],
        "coverage_requested": "managed_route",
        "authorities": {core_role: _key(pins, role)[1]["issuer"] for role, core_role in ROLE_NAMES.items()},
    }
    package = {
        "format": "incident-evidence-input/0.1", "evaluation_id": context["evaluation_id"],
        "workflow": "erasure", "as_of": bundle["as_of"], "target": target,
        "records": [task["request"], *records],
    }
    trust = {
        "format": "incident-evidence-trust/0.1", "evaluation_id": context["evaluation_id"],
        "workflow": "erasure", "as_of": bundle["as_of"], "target_sha256": digest(target),
        "mode": "synthetic-test-only", "keys": deepcopy(pins["keys"]),
    }
    report = assess(package, trust, allow_synthetic=True)
    local = "NOT_OBSERVED" if before is None else "NOT_ESTABLISHED"
    if after is not None:
        if after["measurement"]["state"] == "PRESENT":
            local = "PRESENT_AT_OBSERVATION"
        else:
            local = "ABSENCE_ONLY"
            expected_measurement = {"state": "PRESENT", **{name: context["manifest"][name] for name in ("sha256", "byte_length")}}
            if (before is not None and receipt is not None and before["measurement"] == expected_measurement
                    and after["previous_sha256"] == digest(bundle["before"])
                    and after["completion_sha256"] == digest(bundle["provider_result"]["attestation"])):
                local = "REMOVAL_OBSERVED_SAME_CONTROLLER"
    return {
        "format": "incident-erasure-assessment/0.1", "task_sha256": context["task_sha256"],
        "assessor_report": report, "local_observation": local,
        "unknown_domains": {location: "UNKNOWN" for location in EXCLUSIONS},
        "limitations": LIMITATIONS.copy(),
    }
