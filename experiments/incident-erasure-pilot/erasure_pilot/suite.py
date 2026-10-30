"""Measured local erasure scenarios and read-only rechecking of captured evidence."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from importlib import metadata
from pathlib import Path
import json
import os
import platform
import sys
import time
import uuid
import rfc8785

from . import ASSESSOR_ROOT, VERSION
from .adapter import verify_bundle
from .harness import SYNTHETIC_CONTENT, execute, make_case, make_task
from .protocol import (EXCLUSIONS, InputError, canonical, decode_json, digest, exact_keys,
                       object_name, sha256_bytes, sign_message, sign_record, timestamp,
                       utc_now, verify_message)
from .provider import LocalProvider

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "acceptance.json"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_manifest():
    paths = list((ROOT / "erasure_pilot").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    paths += list(ROOT.glob("*.py")) + [ROOT / "requirements.txt", ACCEPTANCE]
    paths += list((ASSESSOR_ROOT / "incident_assessor").glob("*.py")) + [ASSESSOR_ROOT / "requirements.txt"]
    paths.append(ROOT.parents[1] / ".github/workflows/incident-erasure-pilot.yml")
    return {os.path.relpath(path, ROOT): sha256_bytes(path.read_bytes()) for path in sorted(paths)}


class FinishFailure(LocalProvider):
    def _finish(self, request_id, state, result):
        raise OSError("Injected result persistence failure after local unlink")


class ClaimFailure(LocalProvider):
    def _claim(self, request_id, fingerprint, snapshot):
        raise OSError("Injected claim persistence failure before local unlink")


def package_record(case, result=None, before=None, after=None):
    bundle = {"format": "incident-erasure-bundle/0.1", "task": deepcopy(case["task"]),
              "as_of": utc_now(), "provider_result": result, "before": before, "after": after}
    expected = digest(bundle["task"])
    return {"bundle": bundle, "pins": deepcopy(case["pins"]), "expected_task_sha256": expected,
            "assessment": verify_bundle(bundle, case["pins"], expected)}


def probe(record):
    try:
        verify_bundle(record["bundle"], record["pins"], record["expected_task_sha256"])
        outcome = "ACCEPTED"
    except InputError:
        outcome = "REJECTED"
    return {"bundle": record["bundle"], "pins": record["pins"],
            "expected_task_sha256": record["expected_task_sha256"], "outcome": outcome}


def retained_control(case, mechanism, raw):
    key = case["keys"]["observer"]
    return sign_message({"kind": "retained_read_observation", "task_sha256": digest(case["task"]),
                         "manifest_sha256": digest(case["manifest"]), "mechanism": mechanism,
                         "state": "READABLE", "sha256": sha256_bytes(raw), "byte_length": len(raw),
                         "observed_at": utc_now()}, key["secret"], key["key_id"])


def run_case(case_id, directory):
    options = {}
    if case_id == "LE-06": options["task_seconds"] = 2
    if case_id == "LE-10": options["provider_class"] = FinishFailure
    if case_id == "LE-16": options["provider_class"] = ClaimFailure
    case = make_case(directory, **options)
    path = case["provider"].namespace_root / object_name(case["manifest"])
    records, probes, controls = [], [], []
    if case_id == "LE-03":
        records.append(package_record(case))
    elif case_id == "LE-07":
        path.chmod(0o600)
        path.write_bytes(b"CHANGED SYNTHETIC CONTENT AT THE ORIGINAL NAME.\n")
        records.append(execute(case))
    elif case_id == "LE-08":
        # Explicit test setup outside the provider: pre-existing absence.
        path.unlink()
        records.append(execute(case))
    elif case_id == "LE-11":
        # Observe before both actions, then join both provider calls before
        # post-observation. A replay may return while the winner is still busy;
        # its immediate read would legitimately see PRESENT at that time.
        before = [case["observer"].observe(case["task"], "before") for _ in range(2)]
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: case["provider"].delete(case["task"]), range(2)))
        for initial, result in zip(before, results):
            after = case["observer"].observe(case["task"], "after", previous=initial,
                                            completion=result["attestation"])
            records.append(package_record(case, result, initial, after))
    elif case_id == "LE-12":
        copy = directory / "explicitly-excluded-copy.bin"
        with copy.open("xb") as handle:
            handle.write(SYNTHETIC_CONTENT)
            handle.flush()
            os.fsync(handle.fileno())
        records.append(execute(case))
        controls.append(retained_control(case, "excluded-copy", copy.read_bytes()))
    elif case_id == "LE-13":
        with path.open("rb") as handle:
            records.append(execute(case))
            controls.append(retained_control(case, "open-handle", handle.read()))
    elif case_id == "LE-15":
        before = case["observer"].observe(case["task"], "before")
        result = case["provider"].delete(case["task"])
        # The same controller can recreate a name; prior absence is not timeless.
        case["provider"].create(case["manifest"]["object_id"], case["manifest"]["version_id"], SYNTHETIC_CONTENT)
        after = case["observer"].observe(case["task"], "after", previous=before, completion=result["attestation"])
        records.append(package_record(case, result, before, after))
    else:
        kwargs = {}
        if case_id == "LE-02": kwargs["acknowledge_only"] = True
        if case_id == "LE-06": kwargs["before_unlink"] = lambda: time.sleep(2.1)
        if case_id == "LE-14": kwargs["observe_before"] = False
        if case_id == "LE-18": kwargs.update(observe_before=False, observe_after=False)
        records.append(execute(case, **kwargs))
        if case_id in {"LE-09", "LE-10"}:
            records.append(execute(case))
        elif case_id == "LE-17":
            request_id = case["task"]["request"]["body"]["binding"]["request_id"]
            manifest = case["provider"].create("object-synthetic", "version-" + uuid.uuid4().hex, SYNTHETIC_CONTENT)
            case["manifest"] = manifest
            case["task"] = make_task(manifest, case["keys"], case["pins"], request_id=request_id)
            records.append(execute(case))
    if case_id in {"LE-04", "LE-05"}:
        attacked = deepcopy(records[0])
        result = attacked["bundle"]["provider_result"]
        if case_id == "LE-04":
            result["receipt"]["signature"] = "00" * 64
        else:
            body = deepcopy(result["attestation"]["body"])
            body["binding"]["tenant_id"] = "different-tenant"
            key = case["keys"]["provider"]
            result["attestation"] = sign_record(body, key["secret"], key["key_id"])
        probes.append(probe(attacked))
    data = {"format": "incident-erasure-case/0.1", "case_id": case_id, "synthetic": True,
            "records": records, "probes": probes, "retained_controls": controls,
            "sort_states": case_id == "LE-11", "case_as_of": utc_now()}
    data["actual"] = derive_actual(data)
    serialized = canonical(data)
    if any(key["secret"].encode() in serialized for key in case["keys"].values()):
        raise InputError("Private signing key appeared in public output")
    if SYNTHETIC_CONTENT.strip() in serialized:
        raise InputError("Synthetic object plaintext appeared in public evidence")
    return data


def derive_actual(data):
    states, observations, evidence = [], [], []
    attempts = 0
    for record in data["records"]:
        result = record["bundle"]["provider_result"]
        states.append(result["state"] if result is not None else "NO_PROVIDER_CALL")
        attempts += result is not None and result["attempted"] is True
        observations.append(record["assessment"]["local_observation"])
        evidence.append(record["assessment"]["assessor_report"]["assessments"]["deletion_evidence"])
    if data["sort_states"]:
        states, observations, evidence = sorted(states), sorted(observations), sorted(evidence)
    return {"states": states, "unlink_attempts": attempts, "local_observations": observations,
            "core_evidence": evidence, "rejected_probes": sum(p["outcome"] == "REJECTED" for p in data["probes"]),
            "retained_readable_controls": [c["body"]["mechanism"] for c in data["retained_controls"]],
            "outside_scope_remains_unknown": all(r["assessment"]["unknown_domains"] == {k: "UNKNOWN" for k in EXCLUSIONS} for r in data["records"])}


def verify_case(data):
    exact_keys(data, {"format", "case_id", "synthetic", "records", "probes", "retained_controls", "sort_states", "case_as_of", "actual"})
    cutoff = timestamp(data["case_as_of"])
    if (data["format"] != "incident-erasure-case/0.1" or data["synthetic"] is not True
            or type(data["sort_states"]) is not bool or type(data["records"]) is not list
            or not 1 <= len(data["records"]) <= 2 or type(data["probes"]) is not list
            or len(data["probes"]) > 1 or type(data["retained_controls"]) is not list
            or len(data["retained_controls"]) > 1):
        raise InputError("Invalid measured case shape")
    for record in data["records"]:
        exact_keys(record, {"bundle", "pins", "expected_task_sha256", "assessment"})
        if timestamp(record["bundle"]["as_of"]) > cutoff:
            raise InputError("Bundle cutoff exceeds the completed case observation cutoff")
        report = verify_bundle(record["bundle"], record["pins"], record["expected_task_sha256"])
        if canonical(report) != canonical(record["assessment"]):
            raise InputError("Captured assessment does not recompute")
    for attack in data["probes"]:
        exact_keys(attack, {"bundle", "pins", "expected_task_sha256", "outcome"})
        if timestamp(attack["bundle"]["as_of"]) > cutoff:
            raise InputError("Probe cutoff exceeds the completed case observation cutoff")
        if canonical(probe(attack)) != canonical(attack):
            raise InputError("Probe verdict does not recompute")
    for envelope in data["retained_controls"]:
        record = data["records"][0]
        pins, task = record["pins"], record["bundle"]["task"]
        key_id = pins["observer_key_id"]
        body = verify_message(envelope, pins["keys"][key_id]["public_key"], key_id, "retained_read_observation")
        exact_keys(body, {"kind", "task_sha256", "manifest_sha256", "mechanism", "state", "sha256", "byte_length", "observed_at"})
        if (body["mechanism"] not in {"excluded-copy", "open-handle"} or body["state"] != "READABLE"
                or body["task_sha256"] != digest(task) or body["manifest_sha256"] != digest(task["manifest"])
                or body["sha256"] != task["manifest"]["sha256"] or type(body["byte_length"]) is not int
                or body["byte_length"] != task["manifest"]["byte_length"]):
            raise InputError("Retained-data observation does not bind the original bytes")
        result = record["bundle"]["provider_result"]
        if result is None or result["state"] != "LOCAL_UNLINK_CONFIRMED":
            raise InputError("Retained-data control requires a completed local namespace removal")
        key = pins["keys"][key_id]
        observed = timestamp(body["observed_at"])
        if not (timestamp(result["receipt"]["body"]["observed_at"]) <= observed <= cutoff
                and timestamp(key["not_before"]) <= observed < timestamp(key["not_after"])):
            raise InputError("Retained read does not follow the scoped unlink receipt")
    if canonical(data["actual"]) != canonical(derive_actual(data)):
        raise InputError("Case observations do not recompute")
    return True


def comparison(data, entry):
    actual = data["actual"]
    differences = {key: {"expected": value, "actual": actual.get(key)} for key, value in entry["expected"].items()
                   if canonical(value) != canonical(actual.get(key))}
    return actual, differences


def run_suite(output, *, print_summary=False):
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise InputError("Use a fresh output directory")
    output.mkdir(parents=True)
    sources = source_manifest()
    catalogue = decode_json(ACCEPTANCE.read_bytes())
    results = []
    for entry in catalogue["cases"]:
        data = run_case(entry["case_id"], output / "runtime" / entry["case_id"])
        verify_case(data)
        actual, differences = comparison(data, entry)
        filename = output / "cases" / (entry["case_id"] + ".json")
        write_json(filename, data)
        results.append({"case_id": entry["case_id"], "title": entry["title"], "expected": entry["expected"],
                        "actual": actual, "matched": not differences, "differences": differences,
                        "export_sha256": sha256_bytes(filename.read_bytes())})
    if sources != source_manifest():
        raise InputError("Source changed during execution; no completion summary issued")
    summary = {"format": "incident-erasure-summary/0.1", "implementation_version": VERSION,
               "synthetic": True, "execution": "ACTUAL_LOCAL_FILESYSTEM", "recorded_at": utc_now(),
               "source_files": sources, "source_sha256": digest(sources),
               "toolchain": {"python": sys.version, "platform": platform.platform(),
                             "cryptography": metadata.version("cryptography"), "rfc8785": rfc8785.__version__},
               "total": len(results), "matched": sum(r["matched"] for r in results),
               "all_expectations_matched": all(r["matched"] for r in results),
               "independent_reproduction": "NOT_ESTABLISHED", "remote_provider_used": False,
               "universal_erasure": "NOT_ESTABLISHED", "raw_object_content_exported": False, "results": results}
    write_json(output / "summary.json", summary)
    verify_exports(output)
    print(f"{summary['matched']}/{summary['total']} measured local-erasure expectations matched; not a conformance pass.")
    if print_summary:
        print("ERASURE_PILOT_SUMMARY_JSON=" + json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return summary


def verify_exports(output):
    output = Path(output)
    summary = decode_json((output / "summary.json").read_bytes())
    fixed = {"format": "incident-erasure-summary/0.1", "implementation_version": VERSION,
             "synthetic": True, "execution": "ACTUAL_LOCAL_FILESYSTEM", "independent_reproduction": "NOT_ESTABLISHED",
             "remote_provider_used": False, "universal_erasure": "NOT_ESTABLISHED", "raw_object_content_exported": False}
    exact_keys(summary, set(fixed) | {"recorded_at", "source_files", "source_sha256", "toolchain", "total", "matched", "all_expectations_matched", "results"})
    if any(canonical(summary[key]) != canonical(value) for key, value in fixed.items()):
        raise InputError("Unsupported execution identity or assurance claim")
    timestamp(summary["recorded_at"])
    catalogue = decode_json(ACCEPTANCE.read_bytes())["cases"]
    ids = [entry["case_id"] for entry in catalogue]
    if summary["source_files"] != source_manifest() or digest(summary["source_files"]) != summary["source_sha256"]:
        raise InputError("Recorded source manifest differs from the rechecking implementation")
    if [item["case_id"] for item in summary["results"]] != ids:
        raise InputError("Summary case inventory differs from the catalogue")
    if sorted(p.name for p in (output / "cases").iterdir()) != sorted(key + ".json" for key in ids):
        raise InputError("Missing or extra case exports")
    for result, entry in zip(summary["results"], catalogue):
        raw = (output / "cases" / (entry["case_id"] + ".json")).read_bytes()
        if sha256_bytes(raw) != result["export_sha256"]:
            raise InputError("Case export digest mismatch")
        data = decode_json(raw)
        if data["case_id"] != entry["case_id"]:
            raise InputError("Case identity mismatch")
        if timestamp(data["case_as_of"]) > timestamp(summary["recorded_at"]):
            raise InputError("Case observation is later than its completion summary")
        verify_case(data)
        actual, differences = comparison(data, entry)
        recomputed = {"case_id": entry["case_id"], "title": entry["title"], "expected": entry["expected"],
                      "actual": actual, "matched": not differences, "differences": differences,
                      "export_sha256": sha256_bytes(raw)}
        if canonical(result) != canonical(recomputed):
            raise InputError("Summary result does not recompute")
    matched = sum(r["matched"] for r in summary["results"])
    if (type(summary["total"]) is not int or type(summary["matched"]) is not int
            or type(summary["all_expectations_matched"]) is not bool or summary["total"] != len(ids)
            or summary["matched"] != matched or summary["all_expectations_matched"] != (matched == len(ids))):
        raise InputError("Summary counts do not recompute")
    return {"verified_exports": len(ids), "filesystem_actions_reexecuted": False,
            "scope": "Captured signatures, bindings and bounded observations; not independent truth or universal erasure."}
