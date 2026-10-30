"""Actual local-filesystem scenarios, exported observations and offline rechecking."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from importlib import metadata
from pathlib import Path
import hashlib
import json
import os
import platform
import sys
import time
import rfc8785

from . import ASSESSOR_ROOT, VERSION
from .gate import Gate, GateConfig, verify_report
from .harness import make_case, prepare_candidate, approve, make_keys
from .protocol import InputError, canonical, decode_json, digest, sha256_bytes, utc_now, exact_keys, digest_hex, MAX_HTML
from .store import LocalPublisher

ROOT = Path(__file__).resolve().parents[1]
ACCEPTANCE = ROOT / "acceptance.json"


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_manifest():
    paths = list((ROOT / "publication_pilot").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    paths += list(ROOT.glob("*.py")) + [ROOT / "requirements.txt", ACCEPTANCE]
    paths += list((ASSESSOR_ROOT / "incident_assessor").glob("*.py")) + [ASSESSOR_ROOT / "requirements.txt"]
    paths.append(ROOT.parents[1] / ".github/workflows/incident-publication-pilot.yml")
    return {os.path.relpath(path, ROOT): sha256_bytes(path.read_bytes()) for path in sorted(paths)}


class FinishFailure(LocalPublisher):
    def _finish(self, request_id, state, result):
        raise OSError("Injected local result persistence failure")


def publisher_for(case, root, cls=LocalPublisher):
    key = case["keys"]["publisher"]
    return cls(root, case["config"].route["provider_id"], key["secret"], key["key_id"])


def capture(case):
    return {"candidate": deepcopy(case["candidate"]), "trust": deepcopy(case["trust"]),
            "approval": deepcopy(case["approval"]), "config": case["config"].export()}


def release(case, publisher, **kwargs):
    inputs = capture(case)
    inputs["report"] = Gate(case["config"]).release(case["candidate"], case["trust"], case["approval"], publisher, **kwargs)
    return inputs


def observe(records, visible, *, sort_states=False, outside_write=False):
    exact_keys(visible, {"visible_count", "files"})
    states = [item["report"]["state"] for item in records]
    candidates = {(sha256_bytes(item["candidate"]["html"].encode("utf-8")), len(item["candidate"]["html"].encode("utf-8"))) for item in records}
    if type(visible.get("visible_count")) is not int or visible["visible_count"] != len(visible["files"]):
        raise InputError("Visible artifact inventory has contradictory counts")
    for name, measurement in visible["files"].items():
        if (len(name) != 69 or not name.endswith(".html") or any(c not in "0123456789abcdef" for c in name[:64]) or
                set(measurement) != {"sha256", "byte_length"} or type(measurement["byte_length"]) is not int or
                not 0 < measurement["byte_length"] <= MAX_HTML):
            raise InputError("Invalid local artifact observation")
        digest_hex(measurement["sha256"])
    result = {"states": sorted(states) if sort_states else states,
              "publication_attempts": sum(r["report"]["attempted"] is True for r in records),
              "unknown_attempt_observations": sum(r["report"]["attempted"] is None for r in records),
              "visible_count": visible["visible_count"],
              "visible_bytes_match_candidate": bool(visible["files"]) and all((m["sha256"], m["byte_length"]) in candidates for m in visible["files"].values())}
    if outside_write:
        result["outside_gate_write_observed"] = True
        result["all_route_prevention_established"] = False
    return result


def run_case(case_id, directory):
    options = {}
    if case_id == "LP-05": options["prohibited"] = ("generation",)
    if case_id in {"LP-06", "LP-16"}: options["include_approval"] = False
    if case_id == "LP-08": options["approval_seconds"] = 2
    if case_id == "LP-09": options["activity"] = None
    if case_id == "LP-12": options["interpretation"] = "unresolved"
    if case_id == "LP-17": options["disclosure_activities"] = []
    case = make_case(**options)
    if case_id in {"LP-02", "LP-10"}:
        old_approval = case["approval"]
        case["editor"].set_block("paragraph-1", "A manual replacement with unknown prehistory.", activity="manual_edit")
        candidate, trust, config = prepare_candidate(case["editor"], case["keys"], policy=case["policy"],
            request_id=case["candidate"]["evidence"]["target"]["subject"]["request_id"],
            evaluation_id=case["candidate"]["evidence"]["evaluation_id"])
        case.update(candidate=candidate, trust=trust, config=config,
                    approval=old_approval if case_id == "LP-02" else approve(candidate, case["keys"]))
    elif case_id == "LP-03":
        case["candidate"]["html"] = "<!doctype html><html><body><p>Disclosure removed.</p></body></html>\n"
    elif case_id == "LP-04":
        route = deepcopy(case["config"].route)
        route["provider_id"], route["endpoint"] = "another-venue", "local-publication://another-venue/release"
        original_config = case["config"]
        candidate, trust, _ = prepare_candidate(case["editor"], case["keys"], policy=case["policy"], route=route)
        case.update(candidate=candidate, trust=trust, config=original_config, approval=approve(candidate, case["keys"]))
    elif case_id == "LP-07":
        case["approval"] = approve(case["candidate"], make_keys())
    elif case_id == "LP-11":
        case["candidate"]["source"]["operations"].pop(0)
    publisher = publisher_for(case, directory, FinishFailure if case_id == "LP-14" else LocalPublisher)
    records = []
    if case_id == "LP-15":
        with ThreadPoolExecutor(max_workers=2) as executor:
            records = list(executor.map(lambda _: release(case, publisher), range(2)))
    else:
        records.append(release(case, publisher, **({"before_publish": lambda: time.sleep(2.1)} if case_id == "LP-08" else {})))
        if case_id in {"LP-13", "LP-14"}:
            records.append(release(case, publisher))
        elif case_id == "LP-18":
            request = case["candidate"]["evidence"]["target"]["subject"]["request_id"]
            case["editor"].set_block("paragraph-2", "A newly reviewed additional paragraph.", activity="manual_edit")
            candidate, trust, config = prepare_candidate(case["editor"], case["keys"], policy=case["policy"], request_id=request)
            case.update(candidate=candidate, trust=trust, config=config, approval=approve(candidate, case["keys"]))
            records.append(release(case, publisher))
    if case_id == "LP-16":
        name = sha256_bytes(b"explicit-outside-gate-control") + ".html"
        with (publisher.visible_root / name).open("xb") as handle:
            handle.write(case["candidate"]["html"].encode("utf-8"))
            handle.flush()
            os.fsync(handle.fileno())
    visible = publisher.inspect()
    actual = observe(records, visible, sort_states=case_id == "LP-15", outside_write=case_id == "LP-16")
    extra = {}
    if case_id in {"LP-09", "LP-10"}:
        frame = records[0]["report"]["preflight"]["assessor_frame"]["report"]
        extra = {"core_ai_involvement": frame["assessments"]["ai_involvement"],
                 "core_activity_completeness": frame["assessments"]["activity_completeness"],
                 "declared_activities": records[0]["candidate"]["disclosure"]["activities"]}
    exported = {"format": "incident-publication-case/0.1", "case_id": case_id, "synthetic": True,
                "records": records, "visible": visible, "actual": actual, "additional_observations": extra,
                "sort_states": case_id == "LP-15", "outside_gate_write_observed": case_id == "LP-16"}
    serialized = canonical(exported)
    if any(key["secret"].encode() in serialized for key in case["keys"].values()):
        raise InputError("Private test signing key appeared in public output")
    return exported


def verify_case(data):
    exact_keys(data, {"format", "case_id", "synthetic", "records", "visible", "actual", "additional_observations", "sort_states", "outside_gate_write_observed"})
    if data["format"] != "incident-publication-case/0.1" or data["synthetic"] is not True or not data["records"]:
        raise InputError("Invalid or empty synthetic case")
    if type(data["sort_states"]) is not bool or type(data["outside_gate_write_observed"]) is not bool:
        raise InputError("Invalid observation type")
    for item in data["records"]:
        exact_keys(item, {"candidate", "trust", "approval", "config", "report"})
        verify_report(item["candidate"], item["trust"], item["approval"], item["report"], GateConfig(**item["config"]))
        report = item["report"]
        if report["state"] == "LOCAL_OUTPUT_CONFIRMED":
            receipt = report["receipt"]["body"]
            actual_file = data["visible"]["files"].get(receipt["visible_name"])
            if actual_file != {"sha256": receipt["artifact_sha256"], "byte_length": receipt["byte_length"]}:
                raise InputError("Confirmed receipt differs from the retained visible-file observation")
    actual = observe(data["records"], data["visible"], sort_states=data["sort_states"], outside_write=data["outside_gate_write_observed"])
    if canonical(actual) != canonical(data["actual"]):
        raise InputError("Reported observations differ from retained gate and file records")
    extra = data["additional_observations"]
    if extra:
        first = data["records"][0]
        frame = first["report"]["preflight"]["assessor_frame"]["report"]["assessments"]
        expected = {"core_ai_involvement": frame["ai_involvement"], "core_activity_completeness": frame["activity_completeness"],
                    "declared_activities": first["candidate"]["disclosure"]["activities"]}
        if canonical(extra) != canonical(expected):
            raise InputError("Additional provenance observation does not derive from the retained evidence")
    return True


def run_suite(output, *, print_summary=False):
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise InputError("Use a new output directory; existing results are never overwritten")
    output.mkdir(parents=True)
    sources = source_manifest()
    catalogue = decode_json(ACCEPTANCE.read_bytes())
    results = []
    for entry in catalogue["cases"]:
        data = run_case(entry["case_id"], output / "runtime" / entry["case_id"])
        verify_case(data)
        actual = {**data["actual"], **data["additional_observations"]}
        differences = {key: {"expected": value, "actual": actual.get(key)} for key, value in entry["expected"].items()
                       if canonical(value) != canonical(actual.get(key))}
        filename = output / "cases" / (entry["case_id"] + ".json")
        write_json(filename, data)
        results.append({"case_id": entry["case_id"], "title": entry["title"], "expected": entry["expected"],
                        "actual": actual, "matched": not differences, "differences": differences,
                        "export_sha256": sha256_bytes(filename.read_bytes())})
    if sources != source_manifest():
        raise InputError("Source files changed during scenario execution; no completion summary is issued")
    summary = {"format": "incident-publication-summary/0.1", "implementation_version": VERSION,
               "synthetic": True, "execution": "ACTUAL_LOCAL_FILESYSTEM", "recorded_at": utc_now(),
               "source_files": sources, "source_sha256": digest(sources),
               "toolchain": {"python": sys.version, "platform": platform.platform(),
                             "cryptography": metadata.version("cryptography"), "rfc8785": rfc8785.__version__},
               "total": len(results), "matched": sum(r["matched"] for r in results),
               "all_expectations_matched": all(r["matched"] for r in results),
               "independent_reproduction": "NOT_ESTABLISHED", "external_publication": "NOT_PERFORMED",
               "real_ai_service_called": False, "all_route_prevention_established": False,
               "results": results}
    write_json(output / "summary.json", summary)
    verify_exports(output)
    print(f"{summary['matched']}/{summary['total']} measured local-publication expectations matched; not a conformance pass.")
    if print_summary:
        print("PUBLICATION_PILOT_SUMMARY_JSON=" + json.dumps(summary, ensure_ascii=False, separators=(",", ":")))
    return summary


def verify_exports(output):
    output = Path(output)
    summary = decode_json((output / "summary.json").read_bytes())
    exact_keys(summary, {"format", "implementation_version", "synthetic", "execution", "recorded_at",
                        "source_files", "source_sha256", "toolchain", "total", "matched", "all_expectations_matched",
                        "independent_reproduction", "external_publication", "real_ai_service_called",
                        "all_route_prevention_established", "results"})
    fixed = {"format": "incident-publication-summary/0.1", "implementation_version": VERSION,
             "synthetic": True, "execution": "ACTUAL_LOCAL_FILESYSTEM", "independent_reproduction": "NOT_ESTABLISHED",
             "external_publication": "NOT_PERFORMED", "real_ai_service_called": False, "all_route_prevention_established": False}
    if any(canonical(summary[key]) != canonical(value) for key, value in fixed.items()):
        raise InputError("Unsupported execution identity or assurance claim in summary")
    catalogue = decode_json(ACCEPTANCE.read_bytes())["cases"]
    expected_ids = [item["case_id"] for item in catalogue]
    if summary["source_files"] != source_manifest() or digest(summary["source_files"]) != summary["source_sha256"]:
        raise InputError("Recorded source manifest differs from the rechecking implementation")
    if [item["case_id"] for item in summary["results"]] != expected_ids:
        raise InputError("Summary case inventory differs from the fixed catalogue")
    if sorted(p.name for p in (output / "cases").iterdir()) != sorted(key + ".json" for key in expected_ids):
        raise InputError("Case exports are missing or additional files were supplied")
    for result, expected in zip(summary["results"], catalogue):
        raw = (output / "cases" / (result["case_id"] + ".json")).read_bytes()
        if sha256_bytes(raw) != result["export_sha256"]:
            raise InputError("Case export digest mismatch")
        data = decode_json(raw)
        if data["case_id"] != result["case_id"]:
            raise InputError("Case export identity mismatch")
        verify_case(data)
        actual = {**data["actual"], **data["additional_observations"]}
        differences = {key: {"expected": value, "actual": actual.get(key)} for key, value in expected["expected"].items()
                       if canonical(value) != canonical(actual.get(key))}
        recomputed = {"case_id": expected["case_id"], "title": expected["title"], "expected": expected["expected"],
                      "actual": actual, "matched": not differences, "differences": differences,
                      "export_sha256": sha256_bytes(raw)}
        if canonical(result) != canonical(recomputed):
            raise InputError("Summary findings do not recompute")
    matched = sum(result["matched"] for result in summary["results"])
    if (type(summary["total"]) is not int or type(summary["matched"]) is not int or
            type(summary["all_expectations_matched"]) is not bool or summary["total"] != len(expected_ids) or
            summary["matched"] != matched or summary["all_expectations_matched"] != (matched == len(expected_ids))):
        raise InputError("Aggregate summary counts do not recompute")
    return {"verified_exports": len(expected_ids), "filesystem_actions_reexecuted": False,
            "scope": "Recorded signatures, candidate bindings, decisions and file observations; not independent truth or external publication."}
