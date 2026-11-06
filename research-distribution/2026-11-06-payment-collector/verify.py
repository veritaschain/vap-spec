#!/usr/bin/env python3
"""Recheck one preserved synthetic run offline; never execute a payment demo.

Checksums require a separately trusted copy/commit of this distribution. Embedded
keys are the original controller's declarations, not independent trust. Replaying
a saved readback does not establish present retention or independent event time.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import zipfile


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parent
COMMIT = "ce9c968951c0c92a3b5cf9d5a9a587506f8a700d"
ARTIFACT_ID = 13495277522
RUN_ID = 42203872859
JOB_ID = 127845525323
ARCHIVE_DIGEST = "b93f40c33d1ae946d25f881527a4b2fcf32b704b745e7980aed0182060923bca"
ARCHIVE = "original/payment-collector-public-demo-13495277522.zip"
MEMBERS = {"summary.json", "evidence-bundle.json"}

# stage, financial state, POSTs, effects, GETs, original prerequisite,
# admission custody, outcome custody, retained collector records.
EXPECTED = {
    "healthy": [
        ("original_collection_and_payment", "SETTLED", 1, 1, 0, "VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2),
        ("repeat_returns_original_result", "SETTLED", 1, 1, 0, "VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2),
    ],
    "collector_stopped": [
        ("collector_unreachable_before_payment", "UNKNOWN", 0, 0, 0, "NOT_RECORDED", "UNKNOWN", "UNKNOWN", 0),
        ("later_evidence_recovery", "UNKNOWN", 0, 0, 0, "NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1),
        ("repeat_does_not_resume_payment", "UNKNOWN", 0, 0, 0, "NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1),
    ],
    "collector_ack_lost": [
        ("collector_committed_ack_lost", "UNKNOWN", 0, 0, 0, "NOT_RECORDED", "UNKNOWN", "UNKNOWN", 1),
        ("recover_original_collection_ack", "UNKNOWN", 0, 0, 0, "NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1),
        ("repeat_still_consumed", "UNKNOWN", 0, 0, 0, "NOT_RECORDED", "ACKNOWLEDGED", "UNKNOWN", 1),
    ],
    "provider_response_lost": [
        ("provider_committed_response_lost", "UNKNOWN", 1, 1, 0, "VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "UNKNOWN", 1),
        ("provider_get_only_reconciliation", "SETTLED", 1, 1, 1, "VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "UNKNOWN", 1),
        ("collect_original_provider_receipt", "SETTLED", 1, 1, 1, "VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2),
    ],
    "outcome_collection_stopped": [
        ("financial_settled_outcome_custody_unresolved", "SETTLED", 1, 1, 0, "VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "UNKNOWN", 1),
        ("recover_outcome_evidence_only", "SETTLED", 1, 1, 0, "VERIFIED_PREREQUISITE", "ACKNOWLEDGED", "ACKNOWLEDGED", 2),
    ],
}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def unique_pairs(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def parse(raw):
    return json.loads(raw, object_pairs_hook=unique_pairs)


def byte_reference(raw):
    return {"original_bytes_digest": "sha256:" + sha256(raw), "byte_length": len(raw)}


def decode(value):
    require(type(value) is dict and set(value) == {"encoding", "bytes"}, "original byte wrapper")
    require(value["encoding"] == "hex" and type(value["bytes"]) is str
            and re.fullmatch(r"(?:[0-9a-f]{2})+", value["bytes"]), "original byte encoding")
    return bytes.fromhex(value["bytes"])


def check_files():
    expected = {}
    for line in (ROOT / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  ([A-Za-z0-9_./-]+)", line)
        require(match is not None, "checksum manifest syntax")
        wanted, name = match.groups()
        require(not name.startswith("/") and ".." not in Path(name).parts
                and name not in expected and name != "SHA256SUMS", "checksum path")
        expected[name] = wanted
    all_paths = list(ROOT.rglob("*"))
    require(not any(path.is_symlink() for path in all_paths), "symlinks are not preserved payload")
    actual = {str(path.relative_to(ROOT)) for path in all_paths
              if path.is_file() and path != ROOT / "SHA256SUMS"}
    require(actual == set(expected), "distribution file inventory differs")
    for name, wanted in expected.items():
        require(sha256((ROOT / name).read_bytes()) == wanted, "checksum mismatch: " + name)
    return len(expected)


def check_provenance():
    preserved = parse((ROOT / "preservation.json").read_bytes())
    run = parse((ROOT / "github/run.json").read_bytes())
    jobs = parse((ROOT / "github/jobs.json").read_bytes())["jobs"]
    artifacts = parse((ROOT / "github/artifacts.json").read_bytes())["artifacts"]
    require(preserved["source"]["commit"] == COMMIT, "pinned source commit")
    require(run["id"] == RUN_ID and run["head_sha"] == COMMIT
            and run["run_attempt"] == 1 and run["conclusion"] == "success", "original run identity")
    require(len(jobs) == 1 and jobs[0]["id"] == JOB_ID
            and jobs[0]["conclusion"] == "success", "original job identity")
    require(len(artifacts) == 1, "original artifact inventory")
    artifact = artifacts[0]
    require(artifact["id"] == ARTIFACT_ID and artifact["workflow_run"]["id"] == RUN_ID
            and artifact["workflow_run"]["head_sha"] == COMMIT
            and artifact["digest"] == "sha256:" + ARCHIVE_DIGEST, "artifact provenance binding")
    archive = (ROOT / ARCHIVE).read_bytes()
    require(sha256(archive) == ARCHIVE_DIGEST and len(archive) == artifact["size_in_bytes"], "original ZIP digest")
    with zipfile.ZipFile(ROOT / ARCHIVE) as stream:
        require(len(stream.infolist()) == 2 and set(stream.namelist()) == MEMBERS, "original ZIP member inventory")
        for name in MEMBERS:
            require(stream.read(name) == (ROOT / "original" / name).read_bytes(), "extracted member differs: " + name)
    log = (ROOT / "github/job-127845525323.log").read_text(encoding="utf-8")
    require("SHA256 digest of uploaded artifact zip is " + ARCHIVE_DIGEST in log,
            "original upload log digest")
    require("Artifact ID " + str(ARTIFACT_ID) in log, "original upload log artifact identity")
    require(COMMIT in log, "original checkout commit in log")
    for source in preserved["source"]["snapshots"]:
        require(source["preserved_path"] == "source/" + source["path"], "source snapshot path")
        raw = (ROOT / source["preserved_path"]).read_bytes()
        git_blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
        require(len(raw) == source["bytes"] and sha256(raw) == source["sha256"]
                and git_blob == source["git_blob_sha"], "source snapshot bytes: " + source["path"])


def offline_guard(event, _args):
    # This guard catches accidental service/process use, not malicious-host code.
    if event in {"socket.__new__", "subprocess.Popen", "os.system", "os.posix_spawn", "os.exec"}:
        raise RuntimeError("offline recheck forbids " + event)


def load_verifiers():
    sys.addaudithook(offline_guard)
    path = ROOT / "source/experiments/payment-collector-pilot/payment_collector.py"
    spec = importlib.util.spec_from_file_location("_preserved_payment_collector", path)
    require(spec is not None and spec.loader is not None, "preserved verifier unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module, module.authorization, module.runtime


def check_scenario(case, summary, collection, admission, runtime):
    name = case["scenario"]
    require(name == summary["scenario"] and name in EXPECTED, "scenario identity")
    raw_request = decode(case["request"])
    request = runtime.load_json(raw_request)
    require(runtime.request_bytes(request) == raw_request, "original canonical request")
    request_digest = runtime.bytes_digest(raw_request)
    pins = case["configured_public_pins"]
    context = {key: request[key] for key in runtime.CONTEXT_FIELDS}
    require(pins["context"] == context and pins["independent_trust_established"] is False, "declared public pin scope")
    proof = decode(case["admission_record"])
    checked = admission.recheck_record(proof)
    require(checked["verdict"] == "SUPPORTED" and checked["independent_trust_established"] is False
            and checked["current_authorization_asserted"] is False, "historical admission coherence")
    require(runtime.load_json(proof)["request_bytes"] == raw_request.hex(), "admission request binding")
    receipt = decode(case["provider_receipt"]) if case["provider_receipt"] is not None else None
    if receipt is not None:
        outcome = runtime.verify_receipt(receipt, raw_request,
            bytes.fromhex(pins["provider_public_key_hex"]), pins["provider_id"])
        require(outcome["status"] == "settled", "this captured provider outcome")
    expected_evidence = {"admission_record": proof, "provider_receipt": receipt}
    saved = {}
    for item in case["original_custody_records"]:
        raw = decode(item["record_bytes"])
        record = collection.load_json(raw)
        identifier = item["observation_digest"]
        require(identifier == collection.bytes_digest(raw) and identifier not in saved, "original custody record digest")
        require(record["schema"] == collection.OBSERVATION_SCHEMA
                and record["request_digest"] == request_digest, "custody request binding")
        package_bytes = bytes.fromhex(record["package_bytes"])
        package = collection.validate_package(package_bytes, context)
        require(package["request_bytes"] == raw_request.hex()
                and package["kind"] == record["kind"]
                and bytes.fromhex(package["evidence_bytes"]) == expected_evidence[record["kind"]],
                "custody preserves the original selected evidence")
        require(record["stage"] in {"PRE_DISPATCH", "POST_EFFECT", "HISTORICAL_RECOVERY"}
                and (record["stage"] != "PRE_DISPATCH" or record["kind"] == "admission_record"), "local stage label")
        identity = {"collector_id": pins["collector_id"], "public_key": pins["collector_public_key_hex"], "context": context}
        require(record["collector_identity_digest"] == collection.digest(identity)
                and type(record["collector_epoch"]) is int
                and 0 <= record["collector_epoch"] <= pins["collector_epoch"], "custody pin or epoch")
        response = collection.canonical_json({key: record[key]
            for key in ("readback_bytes", "ack_bytes", "package_bytes")})
        observed = collection.verify_readback(response, package_bytes,
            bytes.fromhex(pins["collector_public_key_hex"]), nonce=record["nonce"],
            collector_id=pins["collector_id"], recovery_epoch=record["collector_epoch"])
        require(observed["state"] == "PRESENT", "saved readback must match original bytes")
        saved[identifier] = {"observation_digest": identifier, "stage": record["stage"], "kind": record["kind"],
            "package_digest": collection.bytes_digest(package_bytes), "nonce": record["nonce"],
            "collector_epoch": record["collector_epoch"], "package_bytes": byte_reference(package_bytes),
            "ack_bytes": byte_reference(observed["ack_bytes"]), "readback_bytes": byte_reference(observed["readback_bytes"]),
            "record_bytes": byte_reference(raw)}
    steps = summary["steps"]
    observations = case["observations"]
    require(len(steps) == len(observations) == len(EXPECTED[name]), "scenario stage inventory")
    for step, observation, wanted in zip(steps, observations, EXPECTED[name]):
        custody = step["custody"]
        actual = (step["stage"], step["state"], step["payment_posts"], step["payment_effects"],
            step["provider_lookups"], custody["pre_dispatch"]["state"], custody["admission_record"]["state"],
            custody["provider_receipt"]["state"], step["collector"]["records"])
        require(actual == wanted, "preserved stage outcome: " + name + ":" + step["stage"])
        require(step["request_digest"] == request_digest and observation["stage"] == step["stage"]
                and observation["local_custody"] == custody, "summary/bundle stage binding")
        returned = observation["returned"]
        require(returned["state"] == step["state"] and returned["request_digest"] == request_digest
                and returned["synthetic"] is True and returned["business_authorization_verified"] is False
                and returned["production_gate"] is False and returned["automatic_retry"] is False,
                "returned financial result and scope")
        require(returned["mock_admission"]["proof_digest"] == runtime.bytes_digest(proof)
                and returned["mock_admission"]["verdict"] == "AUTHORIZED", "returned historical admission")
        require(custody["present_retention"] == "NOT_CHECKED" and custody["unverifiable_observations"] == 0,
                "historical custody is not current retention")
        for observed in custody["observations"]:
            require(saved.get(observed["observation_digest"]) == observed, "compact observation differs from original bytes")
        if step["state"] == "SETTLED":
            require(receipt is not None and returned["receipt_bytes"] == byte_reference(receipt), "settled receipt binding")
    require(set(saved) == {item["observation_digest"] for item in steps[-1]["custody"]["observations"]},
            "final exported custody inventory")
    return len(saved), int(receipt is not None)


def main():
    count = check_files()
    check_provenance()
    collection, admission, runtime = load_verifiers()
    summary = parse((ROOT / "original/summary.json").read_bytes())
    bundle = parse((ROOT / "original/evidence-bundle.json").read_bytes())
    require(summary["schema"] == "synthetic-payment-collector-demo-summary-v0"
            and bundle["schema"] == "synthetic-payment-collector-demo-evidence-v0", "original demo schemas")
    require(summary["synthetic"] is True and bundle["public_keys_are_same_operator_declarations"] is True,
            "original synthetic/trust scope")
    for flag in ("business_authorization_verified", "production_gate", "independent_custody_established",
                 "complete_collection_asserted", "automatic_payment_retry"):
        require(summary[flag] is False, "unsupported claim: " + flag)
    require([case["scenario"] for case in bundle["scenarios"]] == list(EXPECTED)
            and [case["scenario"] for case in summary["scenarios"]] == list(EXPECTED), "original scenario inventory")
    counts = [check_scenario(case, view, collection, admission, runtime)
              for case, view in zip(bundle["scenarios"], summary["scenarios"])]
    require(summary["scenario_count"] == 5 and summary["stage_count"] == 13
            and sum(value[0] for value in counts) == 10 and sum(value[1] for value in counts) == 3,
            "original evidence inventory totals")
    print(json.dumps({"result": "PRESERVED_EVIDENCE_RECHECKED", "source_commit": COMMIT,
        "artifact_id": ARTIFACT_ID, "archive_sha256": ARCHIVE_DIGEST, "manifest_files": count,
        "scenarios": 5, "stages": 13, "admission_records_rechecked": 5,
        "provider_receipts_rechecked": 3, "saved_custody_observations_rechecked": 10,
        "fresh_service_execution": False, "independent_trust_established": False,
        "present_retention_established": False, "VAP_conformance_established": False,
        "production_readiness_established": False}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(json.dumps({"result": "RECHECK_FAILED", "error": type(exc).__name__ + ": " + str(exc)}), file=sys.stderr)
        raise SystemExit(1)
