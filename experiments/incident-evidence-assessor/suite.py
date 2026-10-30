"""Synthetic fixture generation and oracle comparison, outside the runtime package."""

import hashlib
import json
import platform
import re
import sys
from pathlib import Path

import cryptography
import rfc8785

from fixture_transfer_erasure import build as transfer_erasure
from fixture_publication_response import build as publication_response
from incident_assessor.assess import assess
from incident_assessor.evidence import digest
from incident_assessor.model import InputError, strict_json

ROOT = Path(__file__).resolve().parent
CATALOGUE = ROOT.parents[1] / "proposals/incident-evidence-bindings/acceptance-cases.json"


def fixtures():
    left, right = transfer_erasure(), publication_response()
    if left.keys() & right.keys():
        raise InputError("Duplicate fixture identifiers")
    return {**left, **right}


def source_manifest():
    paths = list((ROOT / "incident_assessor").glob("*.py")) + list((ROOT / "tests").glob("*.py"))
    paths += list(ROOT.glob("*.py")) + [ROOT / "requirements.txt"]
    return {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def run_suite(output_dir):
    catalogue = strict_json(CATALOGUE)
    scenarios, generated = catalogue["cases"], fixtures()
    identifiers = [case["id"] for case in scenarios]
    if len(set(identifiers)) != len(identifiers) or set(identifiers) != generated.keys():
        raise InputError("Fixture set does not exactly match the catalogue")
    if any(not re.fullmatch(r"[A-Z]{2}-\d{2}", identifier) for identifier in identifiers):
        raise InputError("Unsupported case identifier")
    output_dir = Path(output_dir)
    results = []
    for case in scenarios:
        package, trust = generated[case["id"]]
        actual = assess(package, trust, allow_synthetic=True)
        expected = {key: value for key, value in case["expected"].items() if key != "reasons"}
        differences = {key: {"expected": value, "actual": actual["assessments"].get(key)}
                       for key, value in expected.items() if actual["assessments"].get(key) != value}
        stem = case["id"]
        write_json(output_dir / "fixtures" / (stem + ".input.json"), package)
        write_json(output_dir / "fixtures" / (stem + ".trust.json"), trust)
        write_json(output_dir / "reports" / (stem + ".report.json"), actual)
        results.append({
            "case_id": stem, "workflow": package["workflow"], "expected_fields": expected,
            "actual_assessments": actual["assessments"], "matched": not differences, "differences": differences,
            "input_sha256": digest(package), "trust_sha256": digest(trust), "report_sha256": digest(actual),
        })
        print(stem + (" MATCH" if not differences else " MISMATCH " + json.dumps(differences)))
    manifest = source_manifest()
    summary = {
        "format": "incident-evidence-suite/0.1", "synthetic": True,
        "scope": "Offline assessment of structured translations; not real institutional evidence or independent reproduction.",
        "catalogue_path": "proposals/incident-evidence-bindings/acceptance-cases.json",
        "catalogue_sha256": hashlib.sha256(CATALOGUE.read_bytes()).hexdigest(),
        "catalogue_baseline_commit": "ff759c9f244f04edddc4bda36be8fc8e05f4a96c",
        "comparison": "All named expected assessment fields except explanatory prose reasons; no global evidence pass.",
        "source_sha256": digest(manifest), "source_files": manifest,
        "toolchain": {"python": sys.version, "platform": platform.platform(),
                      "cryptography": cryptography.__version__, "rfc8785": rfc8785.__version__},
        "total": len(results), "matched": sum(item["matched"] for item in results),
        "all_named_expectations_matched": all(item["matched"] for item in results), "results": results,
    }
    write_json(output_dir / "summary.json", summary)
    print(str(summary["matched"]) + "/" + str(summary["total"]) + " scenario expectations matched; this is not a conformance pass.")
    return 0 if summary["all_named_expectations_matched"] else 1
