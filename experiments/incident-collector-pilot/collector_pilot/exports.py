"""Offline signature, binding, timing, source and finite-inventory recheck."""

import hashlib
import json
from importlib.metadata import version
from pathlib import Path
import stat

from . import REPO_ROOT, ROOT, VERSION, verify_frozen_sources
from .protocol import (InputError, canonical, decode_json, digest, timestamp, validate_endpoint,
                       validate_intent, validate_query, verify_control, verify_receipt, verify_status)
from incident_assessor.assess import assess
from incident_assessor.model import digest_hex, exact_keys, text
from upload_pilot.gateway import verify_receipt as verify_payload_receipt
from upload_pilot.protocol import verify_control as verify_upload_control

MAX_EXPORT = 8 * 1024 * 1024
DEPENDENCIES = {"cryptography": "50.0.2", "rfc8785": "0.1.4", "cffi": "2.1.1", "pycparser": "3.12"}
STATES = {"BLOCKED_WITHOUT_ATTEMPT", "REPLAY_NO_SEND", "REQUEST_ID_CONFLICT", "OUTCOME_UNKNOWN", "RECEIPT_CONFIRMED"}
REPORT_FIELDS = {"format", "state", "attempted", "reason", "payload_sha256", "byte_length", "journal_state",
                 "collector_outcome", "admission", "final", "postflight", "collection_intent", "collection_exchange",
                 "collection_receipt", "status_query", "status_exchange", "collection_status", "dispatch_intent",
                 "payload_transport", "payload_receipt"}


def scope():
    return {"synthetic": True, "network_execution": "ACTUAL_LITERAL_LOOPBACK_HTTP",
            "collector_storage": "SIGNED_INTENT_METADATA_ONLY", "durability": "SQLITE_WAL_FULL_LOCAL_ASSUMPTION",
            "recovery": "READ_ONLY_NO_PAYLOAD_RESUME", "continuous_availability": "NOT_ESTABLISHED",
            "all_route_prevention": "NOT_ESTABLISHED", "independent_observation": "NOT_ESTABLISHED",
            "independent_reproduction": "NOT_ESTABLISHED", "observation_truth": "NOT_INDEPENDENTLY_ESTABLISHED",
            "conformance": "NOT_ASSESSED", "legal_compliance": "NOT_ASSESSED",
            "dependency_scope": "PINNED_VERSIONS_NOT_HERMETIC"}


def _regular(path):
    path = Path(path)
    for component in (path, *path.parents):
        if component.is_symlink():
            raise InputError("Symlink in export or implementation path")
    info = path.stat()
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_EXPORT:
        raise InputError("Expected a bounded regular JSON/source file")
    return path.read_bytes()


def read_json(path):
    return decode_json(_regular(path), max_bytes=MAX_EXPORT)


def source_manifest():
    if {name: version(name) for name in DEPENDENCIES} != DEPENDENCIES:
        raise InputError("Installed dependency versions differ from the pinned experiment")
    files = dict(verify_frozen_sources())
    paths = list((ROOT / "collector_pilot").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    paths += list(ROOT.glob("*.py")) + list(ROOT.glob("*.md"))
    paths += [ROOT / name for name in ("requirements.txt", "dependency-lock.json", "acceptance.json")]
    paths.append(REPO_ROOT / ".github/workflows/incident-collector-pilot.yml")
    for path in sorted(paths):
        files[path.relative_to(REPO_ROOT).as_posix()] = hashlib.sha256(_regular(path)).hexdigest()
    return dict(sorted(files.items()))


def _equal(left, right, message):
    if canonical(left) != canonical(right):
        raise InputError(message)


def _integer(value, maximum=10000):
    if type(value) is not int or not 0 <= value <= maximum:
        raise InputError("Expected bounded nonnegative integer")


def _exchange(value):
    exact_keys(value, {"attempted", "attempted_at", "completed_at", "status", "response", "error"})
    if value["attempted"] is not True:
        raise InputError("Saved collector exchange must represent one actual call")
    if timestamp(value["attempted_at"]) > timestamp(value["completed_at"]):
        raise InputError("Collector exchange clock regressed")
    if value["status"] is not None and (type(value["status"]) is not int or not 100 <= value["status"] <= 599):
        raise InputError("Invalid HTTP status")
    if value["response"] is not None and type(value["response"]) is not dict:
        raise InputError("Invalid saved collector response")
    if value["error"] is not None:
        text(value["error"])


def _success(value):
    return (value is not None and value["error"] is None and type(value["status"]) is int
            and 200 <= value["status"] < 300 and type(value["response"]) is dict)


def _frame(frame):
    exact_keys(frame, {"evidence", "trust", "assessment"})
    _equal(assess(frame["evidence"], frame["trust"], allow_synthetic=True), frame["assessment"],
           "Saved evaluator result differs from unchanged assessor")


def _intent(envelope, case, subject=None, frame=None):
    key = case["keys"]["gateway"]
    body = verify_control(envelope, key["public"], key["key_id"], "collection_intent")
    validate_intent(body)
    if body["collector_id"] != case["collector_id"]:
        raise InputError("Intent changed collector identity")
    if subject is not None and (body["request_id"] != subject["request_id"]
            or body["subject_sha256"] != digest(subject) or body["payload_sha256"] != subject["payload_sha256"]
            or body["policy_sha256"] != subject["policy_sha256"]):
        raise InputError("Intent does not bind measured subject, route or policy")
    if frame is not None:
        evidence = frame["evidence"]
        permits = [item for item in evidence["records"] if item["body"]["kind"] == "transfer.decision"
                   and item["body"]["binding"] == subject and item["body"]["data"]["decision"] == "permit"]
        if body["evaluation_id"] != evidence["evaluation_id"] or body["decision_sha256"] not in {digest(item) for item in permits}:
            raise InputError("Intent does not bind the admitted evaluation and exact signed permit")
    return body


def _query(envelope, intent, case):
    key = case["keys"]["gateway"]
    body = verify_control(envelope, key["public"], key["key_id"], "collection_query")
    validate_query(body)
    for name in ("collector_id", "collection_id", "request_id"):
        if body[name] != intent["body"][name]:
            raise InputError("Query differs from the owned intent")
    if body["request_sha256"] != digest(intent):
        raise InputError("Query substitutes collection bytes")
    return body


def _check_report(report, case):
    exact_keys(report, REPORT_FIELDS)
    if report["format"] != "collector-pilot-report/0.1" or report["state"] not in STATES or type(report["attempted"]) is not bool:
        raise InputError("Invalid gateway outcome")
    digest_hex(report["payload_sha256"])
    _integer(report["byte_length"], 1024 * 1024)
    for name in ("admission", "final", "postflight"):
        if name == "final" and report[name] is None:
            continue
        _frame(report[name])
    admission, final, post = report["admission"]["evidence"], report["final"], report["postflight"]["evidence"]
    subject = admission["target"]["subject"]
    if subject["payload_sha256"] != report["payload_sha256"]:
        raise InputError("Gateway measurement differs from its evidence subject")
    for frame in (post, *((final["evidence"],) if final else ())):
        for name in ("evaluation_id", "workflow"):
            _equal(frame[name], admission[name], "Assessment frame changed operation identity")
        for name in ("subject", "authorities"):
            _equal(frame["target"][name], admission["target"][name], "Assessment frame changed target or authority")
        original = [item for item in frame["records"] if item["body"]["kind"] in {"transfer.policy", "transfer.decision"}]
        _equal(original, admission["records"], "A later frame changed the collected policy or permit evidence")
    if (timestamp(admission["as_of"]) > timestamp(post["as_of"])
            or timestamp(post["as_of"]) > timestamp(case["recorded_at"])):
        raise InputError("Assessment chronology exceeds the saved case observation")
    for frame in (report["admission"], report["postflight"], *((final,) if final else ())):
        for role in ("policy", "gateway"):
            key = case["keys"][role]
            declared = frame["trust"]["keys"].get(key["key_id"])
            if (declared is None or declared["public_key"] != key["public"] or declared["issuer"] != key["issuer"]
                    or declared["organization"] != key["organization"] or declared["roles"] != [role]):
                raise InputError("Assessment frame substituted a controller-declared authority")
    for exchange in (report["collection_exchange"], report["status_exchange"]):
        if exchange is not None:
            _exchange(exchange)
            if timestamp(exchange["completed_at"]) > timestamp(post["as_of"]):
                raise InputError("Collector exchange postdates its result frame")
    intent = report["collection_intent"]
    if intent is not None:
        body = _intent(intent, case, subject, report["admission"])
        if body["byte_length"] != report["byte_length"]:
            raise InputError("Collection byte length differs from measured bytes")
        if report["collection_exchange"] is not None and not (
                timestamp(admission["target"]["operation_at"]) <= timestamp(body["created_at"])
                <= timestamp(report["collection_exchange"]["attempted_at"])):
            raise InputError("Intent or collector request predates admission")
    elif any(report[field] is not None for field in ("collection_exchange", "collection_receipt", "status_query", "status_exchange", "collection_status")):
        raise InputError("Collector evidence lacks its exact signed intent")
    collector = case["keys"]["collector"]
    if report["collection_receipt"] is not None:
        if not _success(report["collection_exchange"]):
            raise InputError("Accepted collector receipt lacks a successful exchange")
        _equal(report["collection_receipt"], report["collection_exchange"]["response"], "Acknowledgement substitutes received bytes")
        verify_receipt(report["collection_receipt"], intent, collector["public"], collector["key_id"], report["collection_exchange"]["completed_at"])
    if report["status_query"] is not None:
        query = _query(report["status_query"], intent, case)
        if report["status_exchange"] is None or timestamp(query["created_at"]) > timestamp(report["status_exchange"]["attempted_at"]):
            raise InputError("Status query lacks a later exchange")
        if (report["collection_receipt"] is None
                or timestamp(query["created_at"]) < timestamp(report["collection_exchange"]["completed_at"])):
            raise InputError("Final readback must follow authenticated collection acknowledgement")
    if report["collection_status"] is not None:
        if not _success(report["status_exchange"]):
            raise InputError("Accepted readback lacks a successful exchange")
        _equal(report["collection_status"], report["status_exchange"]["response"], "Readback substitutes received bytes")
        body = verify_status(report["collection_status"], report["status_query"], intent,
                             collector["public"], collector["key_id"], report["status_exchange"]["completed_at"])
        if body["status"] == "FOUND":
            _equal(body["receipt"], report["collection_receipt"], "Readback changed original committed receipt")
    if final:
        final_evidence = final["evidence"]
        final_at = final_evidence["target"]["operation_at"]
        if not timestamp(admission["target"]["operation_at"]) <= timestamp(final_at) <= timestamp(post["as_of"]):
            raise InputError("Final gate predates admission")
        if post["target"]["operation_at"] != final_at:
            raise InputError("Postflight must preserve the final prerequisite observation time")
        health = [r for r in final_evidence["records"] if r["body"]["kind"] == "transfer.collector_health"]
        post_health = [r for r in post["records"] if r["body"]["kind"] == "transfer.collector_health"]
        _equal(health, post_health, "Postflight created or rewrote collector health after dispatch")
        for item in health:
            data = item["body"]["data"]
            if data["available"] and data["durable_acknowledged"]:
                if report["collection_status"] is None or report["collection_status"]["body"]["status"] != "FOUND":
                    raise InputError("Positive health lacks exact authenticated current readback")
                if not timestamp(report["status_exchange"]["completed_at"]) <= timestamp(data["checked_at"]) == timestamp(final_at):
                    raise InputError("Health was backdated before response verification")
    if report["attempted"]:
        if (final is None or final["assessment"]["assessments"]["transfer_authorization"] != "ALLOW"
                or report["collector_outcome"] != "FRESH_READBACK_CONFIRMED"
                or report["collection_receipt"] is None or report["collection_status"] is None):
            raise InputError("Payload attempt lacks required final authorization and collector evidence")
        from .gateway import _authorization
        policy, permit = _authorization(report["admission"], pending=True)
        final_policy, final_permit = _authorization(final, pending=False)
        _equal(policy, final_policy, "Final allowed policy differs from collected authorization")
        _equal(permit, final_permit, "Final allowed permit differs from collected authorization")
        eligible = [item for item in final["evidence"]["records"] if item["body"]["kind"] == "transfer.collector_health"
                    and item["body"]["binding"] == subject and item["body"]["data"] == {
                        "checked_at": final["evidence"]["target"]["operation_at"], "available": True, "durable_acknowledged": True}]
        if len(eligible) != 1:
            raise InputError("Payload attempt lacks one exact positive collector prerequisite")
        dispatch = verify_upload_control(report["dispatch_intent"], case["keys"]["gateway"]["public"],
                                         case["keys"]["gateway"]["key_id"], "dispatch_intent")
        exact_keys(dispatch, {"kind", "request_id", "subject_sha256", "payload_sha256", "byte_length", "created_at"})
        if (dispatch["request_id"] != subject["request_id"] or dispatch["subject_sha256"] != digest(subject)
                or dispatch["payload_sha256"] != report["payload_sha256"] or type(dispatch["byte_length"]) is not int
                or dispatch["byte_length"] != report["byte_length"]):
            raise InputError("Payload dispatch intent changed measured binding")
        value = report["payload_transport"]
        if value is not None:
            if value["attempted"] is not True or type(value["body_send_completed"]) is not bool:
                raise InputError("Invalid payload transport observation")
            if not timestamp(final["evidence"]["target"]["operation_at"]) <= timestamp(value["attempted_at"]) <= timestamp(post["as_of"]):
                raise InputError("Payload attempt violates final-gate chronology")
            dispatch_records = [r for r in post["records"] if r["body"]["kind"] == "transfer.dispatch"]
            if value["body_send_completed"]:
                if not timestamp(value["attempted_at"]) <= timestamp(value["dispatched_at"]) <= timestamp(post["as_of"]):
                    raise InputError("Transport dispatch chronology differs")
                if len(dispatch_records) != 1 or dispatch_records[0]["body"]["data"]["dispatched_at"] != value["dispatched_at"]:
                    raise InputError("Evidence did not preserve actual transport dispatch time")
            elif dispatch_records or value["dispatched_at"] is not None:
                raise InputError("Uncompleted body send fabricated a dispatch event")
        if report["state"] not in {"RECEIPT_CONFIRMED", "OUTCOME_UNKNOWN"}:
            raise InputError("Attempted payload has a no-attempt outcome")
    elif report["payload_transport"] is not None or report["payload_receipt"] is not None:
        raise InputError("No-attempt outcome includes a payload operation")
    if report["state"] == "RECEIPT_CONFIRMED":
        if not report["attempted"] or report["journal_state"] != "receipt_confirmed":
            raise InputError("Receiver confirmation lacks a persisted attempted outcome")
        _equal(report["payload_receipt"], report["payload_transport"]["receipt"], "Payload receipt differs from actual response")
        verify_payload_receipt(report["payload_transport"], subject, report["payload_sha256"], report["byte_length"],
                               post["as_of"], case["keys"]["receiver"]["public"], case["keys"]["receiver"]["key_id"])


def derive_actual(case):
    reports, reconciliations = case["reports"], case["reconciliations"]
    collector, receiver = case["collector_snapshot"], case["receiver_snapshot"]
    return {"states": [r["state"] for r in reports], "collector_outcomes": [r["collector_outcome"] for r in reports],
            "payload_attempts": sum(r["attempted"] is True for r in reports),
            "collector_write_attempts": sum(r["collection_exchange"] is not None for r in reports),
            "collector_read_attempts": sum(r["status_exchange"] is not None for r in reports + reconciliations),
            "collector_collect_calls": collector["collect_calls"], "collector_status_calls": collector["status_calls"],
            "collector_rows": collector["accepted_count"], "receiver_calls": receiver["handler_calls"],
            "receiver_rows": receiver["accepted_count"],
            "receiver_bytes_match": bool(receiver["rows"]) and all(row["payload_sha256"] == case["payload_sha256"]
                and row["byte_length"] == case["byte_length"] for row in receiver["rows"]),
            "reconciliation_states": [r["state"] for r in reconciliations],
            "final_authorizations": [None if r["final"] is None else r["final"]["assessment"]["assessments"]["transfer_authorization"] for r in reports],
            "postflight_observed_authorizations": [r["postflight"]["assessment"]["assessments"]["observed_action_authorization"] for r in reports]}


def check_case(case):
    exact_keys(case, {"format", "case_id", "recorded_at", "collector_id", "collector_endpoint", "keys", "payload_sha256", "byte_length",
                      "reports", "reconciliations", "collector_snapshot", "receiver_snapshot", "cleanup", "actual"})
    if case["format"] != "collector-pilot-case/0.1" or type(case["reports"]) is not list or not case["reports"]:
        raise InputError("Incomplete saved collector case")
    timestamp(case["recorded_at"])
    validate_endpoint(case["collector_endpoint"])
    digest_hex(case["payload_sha256"])
    _integer(case["byte_length"], 1024 * 1024)
    exact_keys(case["keys"], {"policy", "gateway", "receiver", "collector"})
    for key in case["keys"].values():
        exact_keys(key, {"public", "key_id", "issuer", "organization"})
        digest_hex(key["public"])
        for name in ("key_id", "issuer", "organization"):
            text(key[name])
        if key["organization"] != "same-controller-synthetic":
            raise InputError("Pilot keys cannot claim independent organizations")
    for report in case["reports"]:
        _check_report(report, case)
    intents = {digest(r["collection_intent"]): r["collection_intent"] for r in case["reports"] if r["collection_intent"] is not None}
    collector_key = case["keys"]["collector"]
    for result in case["reconciliations"]:
        exact_keys(result, {"format", "request_id", "state", "reason", "journal_state", "attempted", "upload_resumed",
                           "collection_intent", "status_query", "status_exchange", "collection_status", "collection_receipt"})
        if result["format"] != "collector-pilot-reconciliation/0.1" or result["attempted"] is not False or result["upload_resumed"] is not False:
            raise InputError("Reconciliation cannot send or resume payloads")
        if result["collection_intent"] is not None and digest(result["collection_intent"]) not in intents:
            raise InputError("Reconciliation changed the original intent")
        if result["status_exchange"] is not None:
            _exchange(result["status_exchange"])
            _query(result["status_query"], result["collection_intent"], case)
        if result["state"] in {"FOUND", "NOT_FOUND"}:
            if not _success(result["status_exchange"]):
                raise InputError("Reconciliation lacks authenticated current response")
            _equal(result["collection_status"], result["status_exchange"]["response"], "Reconciliation substituted response")
            body = verify_status(result["collection_status"], result["status_query"], result["collection_intent"],
                                 collector_key["public"], collector_key["key_id"], result["status_exchange"]["completed_at"])
            if timestamp(result["status_exchange"]["completed_at"]) > timestamp(case["recorded_at"]):
                raise InputError("Reconciliation exchange postdates case observation")
            if body["status"] != result["state"] or body["request_id"] != result["request_id"]:
                raise InputError("Reconciled outcome differs from signed query response")
            _equal(body["receipt"], result["collection_receipt"], "Reconciliation receipt changed")
    collector = case["collector_snapshot"]
    exact_keys(collector, {"collect_calls", "status_calls", "accepted_count", "rows"})
    for field in ("collect_calls", "status_calls", "accepted_count"):
        _integer(collector[field])
    row_ids = set()
    for row in collector["rows"]:
        exact_keys(row, {"collection_id", "request_id", "request_sha256", "intent", "receipt"})
        intent = row["intent"]
        body = _intent(intent, case)
        if digest(intent) not in intents or body["collection_id"] in row_ids:
            raise InputError("Collector inventory has substituted or duplicate intent")
        row_ids.add(body["collection_id"])
        for field in ("collection_id", "request_id"):
            if row[field] != body[field]:
                raise InputError("Collector row differs from signed intent")
        if row["request_sha256"] != digest(intent):
            raise InputError("Collector fingerprint differs from saved intent")
        verify_receipt(row["receipt"], intent, collector_key["public"], collector_key["key_id"], case["recorded_at"])
    if collector["accepted_count"] != len(row_ids):
        raise InputError("Collector count differs from complete row inventory")
    receiver = case["receiver_snapshot"]
    exact_keys(receiver, {"handler_calls", "accepted_count", "rows"})
    _integer(receiver["handler_calls"])
    _integer(receiver["accepted_count"])
    attempts = {r["admission"]["evidence"]["target"]["subject"]["request_id"]: r for r in case["reports"] if r["attempted"]}
    if len(attempts) != sum(r["attempted"] for r in case["reports"]):
        raise InputError("Same request produced multiple payload attempts")
    receiver_ids = set()
    for row in receiver["rows"]:
        exact_keys(row, {"request_id", "subject_sha256", "payload_sha256", "byte_length", "receipt"})
        if row["request_id"] not in attempts or row["request_id"] in receiver_ids:
            raise InputError("Receiver accepted an unattempted or duplicate request")
        receiver_ids.add(row["request_id"])
        report = attempts[row["request_id"]]
        subject = report["admission"]["evidence"]["target"]["subject"]
        body = verify_upload_control(row["receipt"], case["keys"]["receiver"]["public"], case["keys"]["receiver"]["key_id"], "upload_receipt")
        for name in ("request_id", "subject_sha256", "payload_sha256", "byte_length"):
            _equal(row[name], body[name], "Receiver row differs from signed receipt")
        if row["subject_sha256"] != digest(subject) or row["payload_sha256"] != report["payload_sha256"] or row["byte_length"] != report["byte_length"]:
            raise InputError("Receiver received a different measured subject or payload")
        _integer(row["byte_length"], 1024 * 1024)
    if receiver["accepted_count"] != len(receiver_ids):
        raise InputError("Receiver count differs from complete row inventory")
    exact_keys(case["cleanup"], {"collector", "receiver"})
    for cleanup in case["cleanup"].values():
        exact_keys(cleanup, {"child_stopped", "forced_termination"})
        if cleanup["child_stopped"] is not True or type(cleanup["forced_termination"]) is not bool:
            raise InputError("Owned child process cleanup is not established")
    actual = derive_actual(case)
    if (collector["collect_calls"] > actual["collector_write_attempts"]
            or collector["status_calls"] > actual["collector_read_attempts"]
            or receiver["handler_calls"] > actual["payload_attempts"]):
        raise InputError("Server observed more calls than the recorded transport attempts")
    _equal(case["actual"], actual, "Saved aggregate changed measured observations")


def verify_exports(output, *, expected_summary_sha256):
    digest_hex(expected_summary_sha256)
    output = Path(output)
    raw = _regular(output / "summary.json")
    if hashlib.sha256(raw).hexdigest() != expected_summary_sha256:
        raise InputError("Summary differs from the externally supplied expected bytes")
    summary = decode_json(raw, max_bytes=MAX_EXPORT)
    exact_keys(summary, {"format", "implementation_version", "recorded_at", "scope", "source_sha256", "source_files", "toolchain", "total", "matched", "results"})
    if summary["format"] != "collector-pilot-summary/0.1" or summary["implementation_version"] != VERSION:
        raise InputError("Unsupported saved collector implementation")
    _equal(summary["scope"], scope(), "Capture changed its assurance boundary")
    exact_keys(summary["toolchain"], {"python", "platform", "dependencies"})
    text(summary["toolchain"]["python"])
    text(summary["toolchain"]["platform"])
    _equal(summary["toolchain"]["dependencies"], DEPENDENCIES, "Capture declared different dependency versions")
    _equal(summary["source_files"], source_manifest(), "Recheck requires the recorded trusted implementation checkout")
    if summary["source_sha256"] != digest(summary["source_files"]):
        raise InputError("Source inventory digest mismatch")
    cases = read_json(ROOT / "acceptance.json")["cases"]
    if type(summary["total"]) is not int or summary["total"] != len(cases) or type(summary["matched"]) is not int or summary["matched"] != len(cases):
        raise InputError("Saved counts do not cover the full finite catalogue")
    if len(summary["results"]) != len(cases) or set(p.name for p in output.iterdir()) != {"summary.json", "cases"}:
        raise InputError("Unexpected public export inventory")
    if set(p.name for p in (output / "cases").iterdir()) != {case["id"] + ".json" for case in cases}:
        raise InputError("Missing or unexpected case file")
    for expected, item in zip(cases, summary["results"]):
        exact_keys(item, {"case_id", "title", "expected", "actual", "matched", "differences", "file_sha256"})
        if item["case_id"] != expected["id"] or item["title"] != expected["title"] or item["matched"] is not True or item["differences"] != {}:
            raise InputError("Saved case identity or match result differs")
        _equal(item["expected"], expected["expected"], "Saved expectation differs from fixed local catalogue")
        raw_case = _regular(output / "cases" / (expected["id"] + ".json"))
        if hashlib.sha256(raw_case).hexdigest() != item["file_sha256"]:
            raise InputError("Case bytes differ from pinned summary")
        case = decode_json(raw_case, max_bytes=MAX_EXPORT)
        if case["case_id"] != expected["id"]:
            raise InputError("Case file changed its identity")
        if timestamp(case["recorded_at"]) > timestamp(summary["recorded_at"]):
            raise InputError("Case observation postdates summary")
        check_case(case)
        _equal(item["actual"], case["actual"], "Summary changed case observations")
        for name, value in expected["expected"].items():
            _equal(case["actual"].get(name), value, "Saved scenario failed fixed expectation: " + name)
    return {"verified_exports": len(cases), "expected_summary_sha256": expected_summary_sha256,
            "source_sha256": summary["source_sha256"], "actions_reexecuted": False,
            "scope": "Signatures, bindings, actual-time consistency, unchanged evaluator, source and finite inventory; observation truth is not independently established."}
