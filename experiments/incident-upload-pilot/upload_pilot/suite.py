"""Measured local HTTP scenarios. Missing transport capability is a failed run."""

import base64
import hashlib
import http.client
import json
import multiprocessing
import os
import platform
import signal
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path
from urllib.parse import urlsplit

import cryptography
import rfc8785

from . import ASSESSOR_ROOT, VERSION
from .gateway import Gateway, verify_receipt
from .harness import SYNTHETIC_BYTES, make_case, make_keys
from .journal import Journal
from .protocol import InputError, canonical, digest, sign_record, strict_json, timestamp, utc_now, verify_control
from .receiver import ReceiverProcess
from .transport import HttpTransport
from incident_assessor.assess import assess
from incident_assessor.model import digest_hex, exact_keys, text

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "acceptance.json"


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_manifest():
    paths = list((ROOT / "upload_pilot").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    paths += list(ROOT.glob("*.py")) + [ROOT / "requirements.txt", ACCEPTANCE]
    paths += list((ASSESSOR_ROOT / "incident_assessor").glob("*.py")) + [ASSESSOR_ROOT / "requirements.txt"]
    paths.append(ROOT.parents[1] / ".github/workflows/incident-upload-pilot.yml")
    return {os.path.relpath(p, ROOT): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


class ClaimFailure(Journal):
    """Trusted error injection before commit; not a physical disk-failure test."""
    def claim(self, *args, **kwargs):
        raise OSError("injected journal claim failure")


class ResultFailure(Journal):
    """Trusted error injection after a successful transport; no hidden retry."""
    def finish(self, *args, **kwargs):
        raise OSError("injected journal result persistence failure")


def _kill_after_claim(config, journal_path, package, trust, payload):
    def die():
        os.kill(os.getpid(), signal.SIGKILL)
    Gateway(config, Journal(journal_path), HttpTransport(config.endpoint)).execute(
        package, trust, payload, before_send=die)
    raise RuntimeError("Expected kill point was not reached")


def _reidentify(package, trust, request_id, evaluation_id, keys):
    package = deepcopy(package)
    trust = deepcopy(trust)
    package["evaluation_id"] = evaluation_id
    package["target"]["subject"]["request_id"] = request_id
    for index, envelope in enumerate(package["records"]):
        body = deepcopy(envelope["body"])
        body["evaluation_id"] = evaluation_id
        body["binding"]["request_id"] = request_id
        role = "policy" if body["kind"] == "transfer.policy" else "gateway"
        package["records"][index] = sign_record(body, keys[role]["secret"], keys[role]["key_id"])
    trust["evaluation_id"] = evaluation_id
    trust["target_sha256"] = digest(package["target"])
    return package, trust


def _run_case(case_id, directory):
    directory.mkdir(parents=True)
    keys = make_keys()
    mode = {"UL-07": "drop_after_commit", "UL-08": "wrong_receipt", "UL-13": "redirect",
            "UL-14": "unauthenticated"}.get(case_id, "normal")
    receiver = ReceiverProcess(directory / "receiver", gateway_public=keys["gateway"]["public"],
                               gateway_key_id=keys["gateway"]["key_id"], receiver_secret=keys["receiver"]["secret"],
                               receiver_key_id=keys["receiver"]["key_id"], mode=mode)
    reports, observations = [], {}
    payload = SYNTHETIC_BYTES
    with receiver:
        options = {"keys": keys}
        if case_id == "UL-02":
            options["grant_changes"] = {"endpoint": "http://127.0.0.1:1/upload"}
        elif case_id == "UL-03":
            options["grant_changes"] = {"tenant_id": "different-approved-tenant"}
        elif case_id == "UL-04":
            options["permit_payload"] = b"another previously approved synthetic revision"
        elif case_id == "UL-05":
            options["expires_in"] = -1
        elif case_id == "UL-10":
            options["expires_in"] = 2
        elif case_id == "UL-14":
            options["decision"] = "deny"
        package, trust, config, _ = make_case(payload, receiver.endpoint, **options)
        journal_type = ClaimFailure if case_id == "UL-06" else ResultFailure if case_id == "UL-16" else Journal
        journal_path = directory / "journal.sqlite3"
        journal = journal_type(journal_path)
        transport = HttpTransport(receiver.endpoint)
        gate = Gateway(config, journal, transport)
        if case_id == "UL-09":
            source = bytearray(payload)
            def mutate_source():
                source[:] = b"changed caller-owned bytes after gateway snapshot"
            reports.append(gate.execute(package, trust, source, after_snapshot=mutate_source))
            observations["source_mutated_after_capture"] = bytes(source) != payload
        elif case_id == "UL-10":
            expiry = timestamp(package["records"][1]["body"]["data"]["valid_until"])
            def wait_past_expiry():
                remaining = (expiry - timestamp(utc_now())).total_seconds()
                time.sleep(max(0, remaining) + 0.03)
            reports.append(gate.execute(package, trust, payload, before_send=wait_past_expiry))
            observations["admission_allowed"] = reports[0]["preflight_assessment"]["assessments"]["transfer_authorization"] == "ALLOW"
        elif case_id == "UL-15":
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = [executor.submit(gate.execute, package, trust, payload) for _ in range(2)]
                reports = sorted((future.result() for future in futures), key=lambda item: item["state"])
        elif case_id == "UL-17":
            worker = multiprocessing.get_context("spawn").Process(
                target=_kill_after_claim, args=(config, str(journal_path), package, trust, payload))
            try:
                worker.start()
                worker.join(15)
                if worker.is_alive():
                    raise InputError("Crash scenario worker failed to terminate")
                observations["worker_killed_after_intent"] = worker.exitcode == -signal.SIGKILL
                observations["worker_exitcode"] = worker.exitcode
            finally:
                if worker.is_alive():
                    worker.kill()
                    worker.join(5)
                worker.close()
            gate = Gateway(config, Journal(journal_path), HttpTransport(receiver.endpoint))
            reports.append(gate.execute(package, trust, payload))
        else:
            reports.append(gate.execute(package, trust, payload))
        if case_id in {"UL-07", "UL-11"}:
            restarted_gate = Gateway(config, Journal(journal_path), HttpTransport(receiver.endpoint))
            reports.append(restarted_gate.execute(package, trust, payload))
        elif case_id == "UL-12":
            other_payload = b"another explicitly approved synthetic payload"
            other, other_trust, _, _ = make_case(other_payload, receiver.endpoint, keys=keys)
            other, other_trust = _reidentify(other, other_trust, package["target"]["subject"]["request_id"],
                                             package["evaluation_id"], keys)
            reports.append(gate.execute(other, other_trust, other_payload))
        elif case_id == "UL-14":
            # Trusted test controller deliberately demonstrates the unprotected path.
            port = urlsplit(receiver.endpoint).port
            connection = http.client.HTTPConnection("127.0.0.1", port, timeout=2)
            try:
                connection.request("POST", "/upload", body=payload,
                                   headers={"Content-Type": "application/octet-stream", "Content-Length": str(len(payload))})
                response = connection.getresponse()
                response.read(65537)
                observations["controller_direct_status"] = response.status
                observations["all_route_prevention_established"] = False
            finally:
                connection.close()
    snapshot = receiver.snapshot()
    expected_hash = hashlib.sha256(payload).hexdigest()
    observed = {"states": [report["state"] for report in reports],
                "gateway_attempts": sum(report["attempted"] is True for report in reports),
                "handler_calls": snapshot["handler_calls"], "accepted_count": snapshot["accepted_count"],
                "received_bytes_match": bool(snapshot["rows"]) and all(row["payload_sha256"] == expected_hash
                    and row["byte_length"] == len(payload) for row in snapshot["rows"]), **observations}
    result = {"format": "incident-upload-case/0.1", "case_id": case_id, "synthetic": True,
              "actual": observed, "reports": reports, "receiver_snapshot": snapshot,
              "receiver_public": keys["receiver"]["public"], "receiver_key_id": keys["receiver"]["key_id"],
              "payload_sha256": expected_hash, "byte_length": len(payload), "cleanup": receiver.cleanup_result}
    if not result["cleanup"]["child_stopped"]:
        raise InputError("Receiver cleanup did not complete")
    serialized = json.dumps(result, ensure_ascii=False)
    if any(value["secret"] in serialized for value in keys.values()):
        raise InputError("Private test key was present in a public export")
    return result


def _check_export(case):
    if type(case.get("reports")) is not list or not case["reports"]:
        raise InputError("A saved case must contain its gateway reports")
    digest_hex(case["payload_sha256"])
    if type(case["byte_length"]) is not int or not 0 <= case["byte_length"] <= 1024 * 1024:
        raise InputError("Invalid exported measured byte length")
    for report in case["reports"]:
        if type(report.get("attempted")) is not bool:
            raise InputError("Attempt observation must be a boolean")
        if report.get("state") not in {"BLOCKED_WITHOUT_ATTEMPT", "RECEIPT_CONFIRMED", "OUTCOME_UNKNOWN", "REPLAY_NO_SEND", "REQUEST_ID_CONFLICT"}:
            raise InputError("Unknown exported gateway state")
        for prefix, evidence_key, trust_key, assessment_key in (
            ("preflight", "preflight_evidence", "preflight_trust", "preflight_assessment"),
            ("final_gate", "final_gate_evidence", "final_gate_trust", "final_gate_assessment"),
            ("postflight", "evidence", "trust", "postflight_assessment"),
        ):
            evidence, trust, stored = report.get(evidence_key), report.get(trust_key), report.get(assessment_key)
            if prefix == "final_gate" and evidence is None and trust is None and stored is None and not report["attempted"]:
                continue
            if not all(type(value) is dict for value in (evidence, trust, stored)):
                raise InputError("Incomplete saved " + prefix + " assessment frame")
            if digest(assess(evidence, trust, allow_synthetic=True)) != digest(stored):
                raise InputError("Saved " + prefix + " report differs from recomputation")
        subject = report["evidence"]["target"]["subject"]
        digest_hex(report["payload_sha256"])
        if (subject["payload_sha256"] != report["payload_sha256"]
                or type(report["byte_length"]) is not int or not 0 <= report["byte_length"] <= 1024 * 1024):
            raise InputError("Exported gateway measurement does not match its target")
        if canonical(subject) != canonical(report["preflight_evidence"]["target"]["subject"]):
            raise InputError("Postflight target differs from the captured preflight target")
        pre = report["preflight_evidence"]
        post = report["evidence"]
        final = report.get("final_gate_evidence")
        if post["target"]["operation_at"] != pre["target"]["operation_at"]:
            raise InputError("Postflight must preserve the admission operation time")
        for frame in [post] + ([final] if final is not None else []):
            if (frame["evaluation_id"] != pre["evaluation_id"] or frame["workflow"] != pre["workflow"]
                    or canonical(frame["target"]["subject"]) != canonical(subject)
                    or canonical(frame["target"]["authorities"]) != canonical(pre["target"]["authorities"])):
                raise InputError("Saved assessment frames refer to different operations or authorities")
        if final is not None and timestamp(final["target"]["operation_at"]) < timestamp(pre["target"]["operation_at"]):
            raise InputError("Final gate check predates admission")
        if report["attempted"]:
            if (report["preflight_assessment"]["assessments"]["transfer_authorization"] != "ALLOW"
                    or report["final_gate_assessment"]["assessments"]["transfer_authorization"] != "ALLOW"):
                raise InputError("Attempt lacks matching allowed admission and final gate assessments")
        if report["state"] == "RECEIPT_CONFIRMED":
            if not report["attempted"] or report["journal_state"] != "receipt_confirmed":
                raise InputError("Receipt confirmation lacks attempted/durable result state")
            observation = report.get("transport_observation")
            if type(observation) is not dict:
                raise InputError("Receipt confirmation lacks transport observation")
            observed = {**observation, "receipt": report["receipt"], "error": None}
            final_at = report["final_gate_evidence"]["target"]["operation_at"]
            post_at = report["evidence"]["as_of"]
            Gateway._transport_result(observed, final_at, post_at)
            verify_receipt(observed, subject, report["payload_sha256"], report["byte_length"], post_at,
                           case["receiver_public"], case["receiver_key_id"])
    rows = case["receiver_snapshot"]["rows"]
    if type(rows) is not list:
        raise InputError("Receiver rows must be an array")
    for field in ("handler_calls", "accepted_count"):
        if type(case["receiver_snapshot"][field]) is not int or case["receiver_snapshot"][field] < 0:
            raise InputError("Receiver counts must be nonnegative integers")
    for row in rows:
        if type(row.get("byte_length")) is not int or not 0 <= row["byte_length"] <= 1024 * 1024:
            raise InputError("Invalid receiver row byte length")
        body = verify_control(row["receipt"], case["receiver_public"], case["receiver_key_id"], "upload_receipt")
        exact_keys(body, {"kind", "request_id", "subject_sha256", "payload_sha256", "byte_length", "received_at", "receipt_id"})
        text(body["request_id"])
        text(body["receipt_id"])
        digest_hex(body["subject_sha256"])
        digest_hex(body["payload_sha256"])
        timestamp(body["received_at"])
        if type(body["byte_length"]) is not int or not 0 <= body["byte_length"] <= 1024 * 1024:
            raise InputError("Invalid receiver receipt byte length")
        if any(canonical(body[key]) != canonical(row[key]) for key in ("request_id", "subject_sha256", "payload_sha256", "byte_length")):
            raise InputError("Receiver row differs from its signed receipt")
    if len({row["request_id"] for row in rows}) != len(rows):
        raise InputError("Duplicate receiver request identifier")
    if case["receiver_snapshot"]["accepted_count"] != len(rows):
        raise InputError("Receiver inventory differs from its exported rows")
    derived = {"states": [r["state"] for r in case["reports"]],
               "gateway_attempts": sum(r["attempted"] for r in case["reports"]),
               "handler_calls": case["receiver_snapshot"]["handler_calls"], "accepted_count": len(rows),
               "received_bytes_match": bool(rows) and all(row["payload_sha256"] == case["payload_sha256"]
                   and row["byte_length"] == case["byte_length"] for row in rows)}
    if any(canonical(case["actual"].get(k)) != canonical(v) for k, v in derived.items()):
        raise InputError("Saved observation summary differs from reports and receiver rows")
    if not case["cleanup"]["child_stopped"]:
        raise InputError("Incomplete cleanup in saved export")


def run_suite(output, *, print_summary=False):
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise InputError("Output path already exists; choose a fresh destination")
    cases = strict_json(ACCEPTANCE)["cases"]
    source = source_manifest()
    output.mkdir(parents=True)
    results = []
    for case in cases:
        record = _run_case(case["id"], output / "runtime" / case["id"])
        _check_export(record)
        differences = {key: {"expected": expected, "actual": record["actual"].get(key)}
                       for key, expected in case["expected"].items()
                       if canonical(record["actual"].get(key)) != canonical(expected)}
        write_json(output / "cases" / (case["id"] + ".json"), record)
        results.append({"case_id": case["id"], "title": case["title"], "expected": case["expected"],
                        "actual": record["actual"], "matched": not differences, "differences": differences,
                        "export_sha256": digest(record), "cleanup": record["cleanup"]})
        print(case["id"] + (" MATCH" if not differences else " MISMATCH " + json.dumps(differences)), flush=True)
    if source != source_manifest():
        raise InputError("Source changed during execution")
    summary = {"format": "incident-upload-pilot-summary/0.1", "implementation_version": VERSION,
               "synthetic": True, "network_execution": "ACTUAL_LITERAL_LOOPBACK_HTTP",
               "recorded_at": utc_now(), "source_sha256": digest(source), "source_files": source,
               "toolchain": {"python": sys.version, "platform": platform.platform(),
                             "cryptography": cryptography.__version__, "rfc8785": rfc8785.__version__},
               "total": len(results), "matched": sum(item["matched"] for item in results),
               "all_expectations_matched": all(item["matched"] for item in results),
               "all_route_prevention_established": False, "independent_reproduction": "NOT_ESTABLISHED",
               "results": results}
    write_json(output / "summary.json", summary)
    verify_exports(output)
    print(str(summary["matched"]) + "/" + str(summary["total"]) + " measured scenario expectations matched; not a conformance pass.")
    if print_summary:
        print("UPLOAD_PILOT_SUMMARY_JSON=" + json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return 0 if summary["all_expectations_matched"] else 1


def verify_exports(output):
    output = Path(output)
    summary = strict_json(output / "summary.json")
    cases = strict_json(ACCEPTANCE)["cases"]
    identifiers = {case["id"] for case in cases}
    actual_ids = [case["case_id"] for case in summary["results"]]
    if len(actual_ids) != len(identifiers) or set(actual_ids) != identifiers:
        raise InputError("Saved scenario inventory does not match the fixed catalogue")
    if set(path.name for path in (output / "cases").iterdir()) != {identifier + ".json" for identifier in identifiers}:
        raise InputError("Missing or unexpected case export")
    expected_by_id = {case["id"]: case["expected"] for case in cases}
    for item in summary["results"]:
        record = strict_json(output / "cases" / (item["case_id"] + ".json"))
        if digest(record) != item["export_sha256"] or record["case_id"] != item["case_id"]:
            raise InputError("Saved export digest or identity mismatch")
        _check_export(record)
        expected = expected_by_id[item["case_id"]]
        if any(canonical(record["actual"].get(k)) != canonical(v) for k, v in expected.items()):
            raise InputError("Saved observations differ from expected scenario")
        if canonical(item["actual"]) != canonical(record["actual"]):
            raise InputError("Saved summary differs from case observations")
    if digest(summary["source_files"]) != summary["source_sha256"]:
        raise InputError("Saved source manifest digest mismatch")
    if summary["source_files"] != source_manifest():
        raise InputError("Recheck requires the recorded source snapshot")
    if (type(summary.get("total")) is not int or summary["total"] != len(identifiers)
            or type(summary.get("matched")) is not int or summary["matched"] != len(identifiers)
            or summary.get("all_expectations_matched") is not True):
        raise InputError("Saved aggregate result differs from the verified inventory")
    return {"verified_exports": len(identifiers), "network_reexecuted": False,
            "scope": "Recorded signatures, bindings, derived reports and inventory; not independent truth of observations."}
