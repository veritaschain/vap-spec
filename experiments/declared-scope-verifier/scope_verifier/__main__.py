"""python -m scope_verifier run-suite | verify | generate"""

import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
from pathlib import Path

from .crypto import InputError, digest, strict_json
from .fixtures import EVALUATION_TIME, generate, write_json
from .verifier import verify

ROOT = Path(__file__).resolve().parent.parent


def provenance():
    def git(*args):
        result = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, check=False)
        return result.stdout.strip() if result.returncode == 0 else "unavailable"
    source_files = sorted(ROOT.glob("scope_verifier/*.py")) + sorted(ROOT.glob("tests/*.py"))
    source_files += [ROOT / "requirements.txt", ROOT / "acceptance.json"]
    return {
        "implementation_commit": git("rev-parse", "HEAD"), "fixture_commit": git("rev-parse", "HEAD"),
        "working_tree_dirty": bool(git("status", "--porcelain", "--", str(ROOT))),
        "source_digest": digest({str(p.relative_to(ROOT)): p.read_text(encoding="utf-8") for p in source_files}),
        "python": platform.python_version(), "platform": platform.platform(),
        "dependencies": {name: importlib.metadata.version(name) for name in ("cryptography", "rfc8785", "cffi", "pycparser")},
        "independent_reproduction": "not_established",
    }


def suite(output):
    output = Path(output)
    fixture_manifest = generate(output / "fixtures")
    expectations = strict_json(ROOT / "acceptance.json")
    rows, mismatches = [], []
    run_provenance = provenance()
    for expected in expectations:
        case = expected["case"]
        package = strict_json(output / "fixtures" / f"{case}.evidence.json")
        trust = strict_json(output / "fixtures" / f"{case}.trust.json")
        result = verify(package, trust, "experimental-scope", EVALUATION_TIME, True)
        result["provenance"] = run_provenance
        core = verify(package, trust, "vap-v1.2", EVALUATION_TIME, True)
        core["provenance"] = run_provenance
        write_json(output / f"{case}.experimental.report.json", result)
        write_json(output / f"{case}.v1.2.report.json", core)
        requirements = {c["check"]: c["result"] for c in result["v1_2_requirements"]}
        actual = {"integrity": result["integrity"]["result"], "core_integrity": core["integrity"]["result"],
                  "scope": result["scope_fulfillment"]["result"],
                  "INT-008": requirements["INT-008"]}
        reasons = {item["code"] for item in result["scope_fulfillment"]["violations"] + result["scope_fulfillment"]["unresolved"]}
        differences = {key: {"expected": expected[key], "actual": actual[key]}
                       for key in actual if expected[key] != actual[key]}
        for key, value in expected.get("requirements", {}).items():
            if requirements[key] != value:
                differences[key] = {"expected": value, "actual": requirements[key]}
        core_requirements = {c["check"]: c["result"] for c in core["v1_2_requirements"]}
        if core_requirements != requirements:
            differences["mode_requirement_isolation"] = {"core": core_requirements, "extension": requirements}
        if expected["reason"] and expected["reason"] not in reasons:
            differences["reason"] = {"expected": expected["reason"], "actual": sorted(reasons)}
        if core["scope_fulfillment"] is not None or core["proposal_status"] != "not_applied":
            differences["mode_isolation"] = "Experimental semantics leaked into current-spec mode"
        rows.append({"case": case, "description": expected["description"], "expected": expected,
                     "actual": actual, "requirements": requirements, "reasons": sorted(reasons),
                     "evidence_digest": digest(package), "trust_digest": digest(trust), "differences": differences})
        if differences:
            mismatches.append(case)
        print(f"{case} {'MATCH' if not differences else 'MISMATCH'}: "
              f"core={actual['core_integrity']} integrity={actual['integrity']} scope={actual['scope']} INT-008={actual['INT-008']}")
    report = {"provenance": run_provenance, "evaluation_time": EVALUATION_TIME,
              "test_execution": "internal_synthetic_only", "proposal_status": "experimental_unadopted",
              "external_time_attestation": "simulated_not_independent", "cases_executed": len(rows),
              "matching_cases": len(rows) - len(mismatches), "mismatching_cases": mismatches,
              "fixture_manifest_digest": digest(fixture_manifest), "cases": rows,
              "overall_vap_pass": None, "full_conformance": "not_assessed"}
    write_json(output / "summary.json", report)
    return 1 if mismatches else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline research verifier; never an overall VAP PASS")
    sub = parser.add_subparsers(dest="command", required=True)
    g = sub.add_parser("generate", help="Generate deterministic public-key synthetic evidence")
    g.add_argument("--output", default="generated/fixtures")
    s = sub.add_parser("run-suite", help="Generate and execute all 14 acceptance cases in both modes")
    s.add_argument("--output", default="generated")
    v = sub.add_parser("verify")
    v.add_argument("evidence")
    v.add_argument("--trust", required=True, help="Evaluator-supplied trust; never loaded from evidence")
    v.add_argument("--mode", required=True, choices=["vap-v1.2", "experimental-scope"])
    v.add_argument("--evaluation-time", required=True, type=int, help="Explicit POSIX seconds; no implicit wall clock")
    v.add_argument("--allow-synthetic", action="store_true", help="Opt in to simulated test-only receipts")
    v.add_argument("--output")
    args = parser.parse_args(argv)
    try:
        if args.command == "generate":
            generate(args.output)
            return 0
        if args.command == "run-suite":
            return suite(args.output)
        result = verify(strict_json(args.evidence), strict_json(args.trust), args.mode,
                        args.evaluation_time, args.allow_synthetic)
        result["provenance"] = provenance()
        if args.output:
            write_json(args.output, result)
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        # Zero means report produced, never evidence passed. Check its named axes.
        return 0
    except (InputError, OSError) as exc:
        print(json.dumps({"error": "invalid_or_unreadable_input", "detail": str(exc), "overall_pass": None}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
