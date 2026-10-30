"""Execute synthetic scenarios, then recheck their captured public evidence."""

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import sys

from fixture_support import AFTER_DEADLINE, BEFORE_DEADLINE, DEADLINE, FreshFixture
from retention_adapter import DOMAIN, InputError, assess
from incident_assessor.evidence import digest
from incident_assessor.model import canonical, exact_keys, strict_json, text, timestamp

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent.parent
LEGACY = ROOT.parent / "incident-evidence-assessor"


def expectations():
    def expected(states, deletion="REQUEST_ONLY", presence=0, required=(), forbidden=()):
        return {"deadline_states": states, "deletion_evidence": deletion, "presence_count": presence,
                "required_follow_up": list(required), "forbidden_follow_up": list(forbidden)}
    return {
        "RT-01": expected(["BEFORE_DECLARED_DEADLINE"], forbidden=["COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF"]),
        "RT-02": expected(["AT_DECLARED_DEADLINE"], required=["COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF"]),
        "RT-03": expected(["AFTER_DECLARED_DEADLINE"], required=["COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF"]),
        "RT-04": expected(["UNKNOWN"], required=["UNKNOWN_DEADLINE"]),
        "RT-05": expected(["AFTER_DECLARED_DEADLINE"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE",
                          required=["COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF"]),
        "RT-06": expected(["AFTER_DECLARED_DEADLINE"], "INDEPENDENTLY_REVIEWED_WITHIN_DECLARED_SCOPE", 1,
                          required=["PRESENCE_REPORTED_AT_OR_AFTER_COMPLETION_CLAIM",
                                    "PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE"]),
        "RT-07": expected(["UNKNOWN"], required=["UNKNOWN_DEADLINE"]),
        "RT-08": expected([], required=["NO_APPLICABLE_RETENTION_STATEMENT"]),
        "RT-09": expected([], required=["NO_APPLICABLE_RETENTION_STATEMENT"]),
        "RT-10": expected([], required=["NO_APPLICABLE_RETENTION_STATEMENT"]),
        "RT-11": expected(["AFTER_DECLARED_DEADLINE"], required=["REPORTED_RETENTION_EXCEPTION"]),
        "RT-12": expected(["AFTER_DECLARED_DEADLINE", "BEFORE_DECLARED_DEADLINE"],
                          required=["MULTIPLE_STATEMENTS_REQUIRE_REVIEW"]),
        "RT-13": expected(["AFTER_DECLARED_DEADLINE"], forbidden=["PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE"]),
        "RT-14": expected(["AT_DECLARED_DEADLINE"]),
        "RT-15": expected(["AFTER_DECLARED_DEADLINE"], presence=1,
                          forbidden=["PRESENCE_REPORTED_AT_OR_AFTER_DEADLINE"]),
        "RT-16": expected(["AFTER_DECLARED_DEADLINE"], "PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE",
                          required=["RETENTION_DEADLINE_REACHED_REVIEW_REQUIRED"],
                          forbidden=["COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF"]),
    }


def build_cases():
    """Fresh synthetic keys stay in memory; only public records leave the fixture."""
    cases = {}
    fixed = FreshFixture()
    fixed.statement()
    for name, cutoff in (("RT-01", BEFORE_DEADLINE), ("RT-02", DEADLINE), ("RT-03", AFTER_DEADLINE)):
        cases[name] = fixed.inputs(as_of=cutoff)
    f = FreshFixture()
    f.statement(schedule={"kind": "unknown", "reason": "Duration reported; no established start or calculation rule."})
    cases["RT-04"] = f.inputs()
    f = FreshFixture()
    f.statement()
    f.attestation()
    cases["RT-05"] = f.inputs()
    f = FreshFixture()
    f.statement()
    f.attestation()
    f.review()
    f.presence()
    cases["RT-06"] = f.inputs()
    f = FreshFixture()
    f.statement(schedule={"kind": "unknown", "reason": "Neither location nor training declarations establish a deadline."})
    cases["RT-07"] = f.inputs()
    f = FreshFixture()
    statement = f.statement()
    statement["body"]["binding"]["tenant_id"] = "other-synthetic-tenant"
    f.resign(statement)
    cases["RT-08"] = f.inputs()
    f = FreshFixture()
    statement = f.statement()
    statement["body"]["data"]["training_use"] = "reported-enabled"
    cases["RT-09"] = f.inputs()
    f = FreshFixture()
    f.statement(recorded_at="2026-11-01T00:00:00Z")
    cases["RT-10"] = f.inputs()
    f = FreshFixture()
    f.statement(exceptions=[
        {"location": "active", "reason": "Synthetic bounded retention exception", "until": "2026-10-30T00:00:00Z"},
        {"location": "provider-log", "reason": "Synthetic exception with no reported end", "until": None},
    ])
    cases["RT-11"] = f.inputs()
    f = FreshFixture()
    f.statement(record_id="a-earlier")
    f.statement(record_id="b-later", deadline="2026-11-30T00:00:00Z", recorded_at="2026-10-02T00:00:00Z")
    cases["RT-12"] = f.inputs()
    f = FreshFixture()
    f.statement()
    f.presence(location="uncovered-synthetic-location")
    cases["RT-13"] = f.inputs()
    f = FreshFixture(as_of=DEADLINE)
    f.statement(deadline="2026-10-31T09:00:00+09:00")
    cases["RT-14"] = f.inputs()
    f = FreshFixture()
    f.statement(deadline="2026-09-29T00:00:00Z")
    f.presence(observed_at="2026-09-30T00:00:00Z")
    cases["RT-15"] = f.inputs()
    f = FreshFixture()
    f.statement(locations=["active"])
    f.attestation()
    cases["RT-16"] = f.inputs()
    return cases


def check_result(report, expected):
    errors = []
    values = {
        "deadline_states": [s["deadline_state"] for s in report["statements"]],
        "deletion_evidence": report["erasure_report"]["assessments"]["deletion_evidence"],
        "presence_count": len(report["presence_reports"]),
    }
    for key, actual in values.items():
        if actual != expected[key]:
            errors.append(key + " differs from expected observation")
    for reason in expected["required_follow_up"]:
        if reason not in report["follow_up_reasons"]:
            errors.append("Missing follow-up: " + reason)
    for reason in expected["forbidden_follow_up"]:
        if reason in report["follow_up_reasons"]:
            errors.append("Unexpected follow-up: " + reason)
    if report["universal_deletion"] != "NOT_ESTABLISHED" or report["legal_compliance"] != "NOT_ASSESSED":
        errors.append("Unsupported universal or legal result")
    for dimension in ("target_completion", "provider_completion", "outside_scope_outcome"):
        if report["erasure_report"]["assessments"][dimension] != "UNKNOWN":
            errors.append("Unsupported deletion completion: " + dimension)
    return errors


def source_manifest():
    paths = [ROOT / name for name in ("suite.py", "fixture_support.py", "requirements.txt", "CONTRACT.md")]
    for folder in (ROOT / "retention_adapter", ROOT / "tests", LEGACY / "incident_assessor"):
        paths.extend(folder.rglob("*.py"))
    paths.extend([LEGACY / "requirements.txt", REPO / ".github/workflows/incident-retention-adapter.yml"])
    result = {}
    for path in sorted(set(paths)):
        if path.is_symlink() or not path.is_file():
            raise InputError("Missing or symlinked source file: " + str(path))
        result[path.relative_to(REPO).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def _write_new(path, value):
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, sort_keys=True, indent=2)
        handle.write("\n")


def _cross_case_checks(captures):
    clock = [captures[name] for name in ("RT-01", "RT-02", "RT-03")]
    first = clock[0]
    same_evidence = all(
        digest(c["input"]["erasure"]["records"]) == digest(first["input"]["erasure"]["records"])
        and digest(c["input"]["retention_records"]) == digest(first["input"]["retention_records"])
        for c in clock)
    same_assessment = all(canonical(c["report"]["erasure_report"]["assessments"])
                          == canonical(first["report"]["erasure_report"]["assessments"]) for c in clock)
    return {"clock_only_inputs_reuse_identical_signed_records": same_evidence,
            "clock_only_change_preserves_deletion_assessment": same_assessment}


def run_suite(output):
    output = Path(output)
    if output.exists() or output.is_symlink():
        raise InputError("Output directory must be new")
    before = source_manifest()
    output.mkdir(parents=True, exist_ok=False)
    (output / "cases").mkdir()
    captures, inventory = {}, {}
    expected = expectations()
    inputs = build_cases()
    if inputs.keys() != expected.keys():
        raise InputError("Case inventory differs from expectations")
    for case_id in sorted(inputs):
        package, trust = inputs[case_id]
        report = assess(package, trust, allow_synthetic=True)
        errors = check_result(report, expected[case_id])
        capture = {"format": "retention-synthetic-case/0.1", "case_id": case_id,
                   "input": package, "trust": trust, "report": report,
                   "expected": expected[case_id], "differences": errors}
        filename = "cases/" + case_id + ".json"
        _write_new(output / filename, capture)
        captures[case_id] = capture
        inventory[case_id] = {"path": filename, "sha256": hashlib.sha256((output / filename).read_bytes()).hexdigest(),
                              "matches_expectations": not errors}
    after = source_manifest()
    if before != after:
        raise InputError("Source changed during execution")
    cross_checks = _cross_case_checks(captures)
    passed = sum(item["matches_expectations"] for item in inventory.values())
    summary = {
        "format": "retention-synthetic-summary/0.1", "adapter": DOMAIN,
        "created_at": datetime.now(timezone.utc).isoformat(), "python_version": platform.python_version(),
        "case_count": len(inventory), "passed": passed, "failed": len(inventory) - passed,
        "source_manifest": before, "cases": inventory, "cross_case_checks": cross_checks,
        "limitations": "Internal synthetic execution only. Captured public pins are test assumptions, not independent identity or storage evidence.",
    }
    _write_new(output / "summary.json", summary)
    if passed != len(inventory) or not all(cross_checks.values()):
        raise InputError("A measured scenario or cross-case expectation failed")
    return summary


def verify_exports(output):
    output = Path(output)
    if output.is_symlink() or not output.is_dir():
        raise InputError("Expected a real capture directory")
    summary_path = output / "summary.json"
    cases_dir = output / "cases"
    if summary_path.is_symlink() or cases_dir.is_symlink() or not cases_dir.is_dir():
        raise InputError("Capture paths must not be symlinks")
    summary = strict_json(summary_path)
    exact_keys(summary, {"format", "adapter", "created_at", "python_version", "case_count", "passed", "failed",
                         "source_manifest", "cases", "cross_case_checks", "limitations"})
    if summary["format"] != "retention-synthetic-summary/0.1" or summary["adapter"] != DOMAIN:
        raise InputError("Unsupported capture summary")
    timestamp(summary["created_at"])
    text(summary["python_version"])
    text(summary["limitations"])
    expected = expectations()
    exact_keys(summary["cases"], expected)
    if summary["source_manifest"] != source_manifest():
        raise InputError("Source or case inventory differs")
    wanted = {case_id + ".json" for case_id in expected}
    if {p.name for p in cases_dir.iterdir()} != wanted:
        raise InputError("Capture case files differ from the expected inventory")
    captures = {}
    for case_id in sorted(expected):
        item = summary["cases"][case_id]
        exact_keys(item, {"path", "sha256", "matches_expectations"})
        filename = "cases/" + case_id + ".json"
        if item["path"] != filename or item["matches_expectations"] is not True:
            raise InputError("Invalid case path or failed expectation")
        path = output / filename
        if path.is_symlink() or not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
            raise InputError("Case file is missing, unsafe or changed")
        capture = strict_json(path)
        exact_keys(capture, {"format", "case_id", "input", "trust", "report", "expected", "differences"})
        if (capture["format"] != "retention-synthetic-case/0.1" or capture["case_id"] != case_id
                or canonical(capture["expected"]) != canonical(expected[case_id])):
            raise InputError("Case identity or expectation differs")
        report = assess(capture["input"], capture["trust"], allow_synthetic=True)
        errors = check_result(report, expected[case_id])
        if (canonical(report) != canonical(capture["report"]) or errors
                or canonical(capture["differences"]) != canonical(errors)):
            raise InputError("Captured report differs from original signed evidence or expected observations")
        captures[case_id] = capture
    cross_checks = _cross_case_checks(captures)
    if canonical(cross_checks) != canonical(summary["cross_case_checks"]) or not all(cross_checks.values()):
        raise InputError("Clock-only evidence invariant failed")
    for key, number in (("case_count", len(expected)), ("passed", len(expected)), ("failed", 0)):
        if type(summary[key]) is not int or summary[key] != number:
            raise InputError("Summary counts differ from rechecked cases")
    return {"rechecked": len(captures), "cross_case_checks": cross_checks, "source_manifest_matches": True}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run = commands.add_parser("run")
    run.add_argument("--output", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("directory")
    args = parser.parse_args(argv)
    try:
        result = run_suite(args.output) if args.command == "run" else verify_exports(args.directory)
    except (InputError, OSError) as exc:
        parser.exit(2, "retention suite: " + str(exc) + "\n")
    if args.command == "run":
        result = {k: result[k] for k in ("case_count", "passed", "failed", "cross_case_checks")}
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
