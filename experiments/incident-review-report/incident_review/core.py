"""Verify the frozen capture before deriving or publishing a review report."""

import importlib
from pathlib import Path
import sys

from .common import (PILOTS, REPO_ROOT, ROOT, SCOPE, VERSION, ReviewError, digest,
                     exact, json_bytes, read_regular, reference, resolve_pointer,
                     safe_path, sha256, strict_json)


FROZEN_COMMIT = "1553ff9729ceb30f3ff03513cead45c5b7abd1d9"
FROZEN_ARCHIVE = "06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f"
FROZEN_MANIFEST = "808cac08a06e2f543683e4499645d1eda3860a400406efe1cbd206614490a76d"
FROZEN_SOURCE = "8fb9b95553ef60b54419f0542b555e7c797c58cc92d1bba2a7a0c256694bd3c0"
SNAPSHOT_ID = "incident-ci-2026-10-30"
KIT_DIRECTORY = "experiments/incident-recheck-kit"
DEPENDENCIES = {"cryptography": "50.0.2", "rfc8785": "0.1.4", "cffi": "2.1.1", "pycparser": "3.12"}
PILOT_SOURCES = {
    "upload": "0f7e7f04c45baca8bc62ea0f8778c79ef5bba22e27faf49fbad92001c617df49",
    "publication": "78386924abf2ac6819f653d7c282972b86e58ac1379751c213bca1e5334c639c",
    "erasure": "fb0dc41bde92840e06f11c9077c41743dc8c1255b4404aaa464b7455fa829191",
}


def verify_toolchain():
    lock = strict_json(read_regular(ROOT, "toolchain-lock.json"))
    exact(lock, {"format", "kit_commit", "snapshot_id", "archive_sha256", "manifest_sha256", "source_sha256", "files"})
    if (lock["format"] != "incident-review-toolchain-lock/0.1" or lock["kit_commit"] != FROZEN_COMMIT
            or lock["snapshot_id"] != SNAPSHOT_ID or lock["archive_sha256"] != FROZEN_ARCHIVE
            or lock["manifest_sha256"] != FROZEN_MANIFEST or lock["source_sha256"] != FROZEN_SOURCE):
        raise ReviewError("Toolchain lock differs from the fixed reviewed snapshot")
    files = lock["files"]
    if type(files) is not dict or len(files) != 136 or sha256(json_bytes(files)[:-1]) != FROZEN_SOURCE:
        raise ReviewError("Frozen execution source inventory differs")
    for path, expected in files.items():
        safe_path(path)
        digest(expected)
        if sha256(read_regular(REPO_ROOT, path)) != expected:
            raise ReviewError("Frozen source changed before review: " + path)
    return lock


def source_identity():
    lock = verify_toolchain()
    paths = set(lock["files"])
    own = set((ROOT / "incident_review").glob("*.py"))
    own.update((ROOT / "tests").glob("*.py"))
    own.update(ROOT.glob("*.py"))
    own.update(ROOT / p for p in ("README.md", "RUN-ja.md", "requirements.txt", "toolchain-lock.json"))
    own.add(REPO_ROOT / ".github/workflows/incident-review-report.yml")
    paths.update(p.relative_to(REPO_ROOT).as_posix() for p in own)
    measured = {p: sha256(read_regular(REPO_ROOT, p)) for p in sorted(paths)}
    return {"version": VERSION, "source_sha256": sha256(json_bytes(measured)[:-1]), "source_manifest": measured}


def _check_module_origins():
    package = REPO_ROOT / KIT_DIRECTORY / "incident_recheck"
    modules = {"incident_recheck": package / "__init__.py"}
    modules.update({"incident_recheck." + name: package / (name + ".py")
                    for name in ("__main__", "archive", "layout", "runner", "worker")})
    for name, module in tuple(sys.modules.items()):
        if name != "incident_recheck" and not name.startswith("incident_recheck."):
            continue
        filename = getattr(module, "__file__", None)
        if name not in modules or not filename or Path(filename).resolve() != modules[name].resolve():
            raise ReviewError("A kit module is already loaded from an untrusted origin: " + name)


def _load_kit():
    lock = verify_toolchain()
    _check_module_origins()
    trusted_path = str(REPO_ROOT / KIT_DIRECTORY)
    old_path = sys.path[:]
    try:
        sys.path.insert(0, trusted_path)
        archive = importlib.import_module("incident_recheck.archive")
        runner = importlib.import_module("incident_recheck.runner")
        _check_module_origins()
    except ImportError as exc:
        raise ReviewError("Cannot import the fixed local recheck toolchain") from exc
    finally:
        sys.path[:] = old_path
    return archive.inspect_archive, runner.recheck_archive, lock


def _validate_recheck(value, inspected, lock):
    exact(inspected, {"manifest", "files", "archive_sha256", "manifest_sha256"})
    if (inspected["archive_sha256"] != lock["archive_sha256"]
            or inspected["manifest_sha256"] != lock["manifest_sha256"]
            or type(inspected["files"]) is not dict
            or any(type(raw) is not bytes for raw in inspected["files"].values())):
        raise ReviewError("Inspection is not the fixed owned capture")
    exact(value, {"format", "snapshot_id", "archive_sha256", "manifest_sha256", "source_binding",
                  "verified_exports", "pilots", "actions_reexecuted", "independent_reproduction",
                  "conformance", "dependency_scope"})
    if (value["format"] != "incident-recheck-report/0.1" or value["snapshot_id"] != SNAPSHOT_ID
            or value["archive_sha256"] != inspected["archive_sha256"]
            or value["manifest_sha256"] != inspected["manifest_sha256"]
            or value["source_binding"] != "MATCHED_TRUSTED_CHECKOUT"
            or type(value["verified_exports"]) is not int or value["verified_exports"] != 53
            or value["actions_reexecuted"] is not False or value["independent_reproduction"] != "NOT_ESTABLISHED"
            or value["conformance"] != "NOT_ASSESSED" or value["dependency_scope"] != "PINNED_VERSIONS_NOT_HERMETIC"):
        raise ReviewError("A complete successful frozen-kit recheck was not established")
    if type(value["pilots"]) is not list or len(value["pilots"]) != 3:
        raise ReviewError("Missing fixed pilot results")
    for (name, config), worker in zip(PILOTS.items(), value["pilots"]):
        exact(worker, {"format", "pilot", "verified_exports", "actions_reexecuted", "source_sha256", "dependencies", "guard"})
        if (worker["format"] != "incident-recheck-worker/0.1" or worker["pilot"] != name
                or type(worker["verified_exports"]) is not int or worker["verified_exports"] != config["count"]
                or worker["actions_reexecuted"] is not False or worker["source_sha256"] != PILOT_SOURCES[name]
                or type(worker["dependencies"]) is not dict or worker["dependencies"] != DEPENDENCIES
                or worker["guard"] != "PYTHON_AUDIT_EVENTS"):
            raise ReviewError("Frozen worker identity, count, dependencies or scope differs")


def _validate_projection(report, files, checked, identity):
    exact(report, {"format", "snapshot_id", "reporter", "input", "recheck", "scope", "counts", "pilots", "cases"})
    expected_counts = {"saved_cases_rechecked": 53, "scenario_expectations_matched": 53,
                       "per_pilot": {p: c["count"] for p, c in PILOTS.items()}}
    expected_input = {"archive_sha256": checked["archive_sha256"], "manifest_sha256": checked["manifest_sha256"],
                      "provenance_sha256": sha256(files["evidence/provenance.json"])}
    if (report["format"] != "incident-review-report/0.1" or report["snapshot_id"] != SNAPSHOT_ID
            or json_bytes(report["reporter"]) != json_bytes(identity)
            or json_bytes(report["recheck"]) != json_bytes(checked)
            or json_bytes(report["input"]) != json_bytes(expected_input)
            or json_bytes(report["scope"]) != json_bytes(SCOPE)
            or json_bytes(report["counts"]) != json_bytes(expected_counts)):
        raise ReviewError("Projection changed the verified source, count or assurance boundary")
    if (type(report["cases"]) is not list or len(report["cases"]) != 53
            or type(report["pilots"]) is not list or len(report["pilots"]) != 3
            or [p.get("pilot") for p in report["pilots"]] != list(PILOTS)):
        raise ReviewError("Projection differs from the complete case/pilot inventory")
    expected_cases = [(name, f"{config['prefix']}-{i:02d}") for name, config in PILOTS.items()
                      for i in range(1, config["count"] + 1)]
    for row, (name, case) in zip(report["cases"], expected_cases):
        exact(row, {"pilot", "case_id", "capture_source", "title", "expectation", "sections", "frames", "notes"})
        expected_file = f"evidence/{name}/cases/{case}.json"
        if (row["pilot"] != name or row["case_id"] != case
                or row["capture_source"] != reference(files, expected_file, "")):
            raise ReviewError("Case projection substituted an original capture identity")

    parsed = {}
    def check_source(source):
        exact(source, {"file", "sha256", "pointer"})
        file = source["file"]
        safe_path(file)
        if not file.startswith("evidence/") or file not in files or sha256(files[file]) != source["sha256"]:
            raise ReviewError("A projected source reference differs from owned evidence bytes")
        if file not in parsed:
            parsed[file] = strict_json(files[file])
        return resolve_pointer(parsed[file], source["pointer"])

    def visit(value):
        if type(value) is dict:
            if set(value) == {"name", "value", "source"}:
                if type(value["name"]) is not str or json_bytes(value["value"]) != json_bytes(check_source(value["source"])):
                    raise ReviewError("A displayed fact differs from its concrete source pointer")
            elif set(value) == {"file", "sha256", "pointer"}:
                check_source(value)
            for item in value.values():
                visit(item)
        elif type(value) is list:
            for item in value:
                visit(item)
    visit(report)


def generate_report(archive, expected_sha256):
    digest(expected_sha256)
    if expected_sha256 != FROZEN_ARCHIVE:
        raise ReviewError("This report version supports only its fixed reviewed kit archive")
    before = source_identity()
    inspect_archive, recheck_archive, lock = _load_kit()
    try:
        inspected = inspect_archive(archive, expected_sha256)
        checked = recheck_archive(archive, expected_sha256)
    except (ValueError, OSError) as exc:
        raise ReviewError("Frozen kit verification failed; no review report was generated") from exc
    _validate_recheck(checked, inspected, lock)
    from .projection import project
    report = project(inspected["files"], checked, before)
    _validate_projection(report, inspected["files"], checked, before)
    if json_bytes(source_identity()) != json_bytes(before):
        raise ReviewError("Execution sources changed during review generation")
    return report


def _result(report, raw, format):
    return {"format": format, "kit_archive_sha256": report["input"]["archive_sha256"],
            "report_sha256": sha256(raw), "report_byte_length": len(raw),
            "reporter_source_sha256": report["reporter"]["source_sha256"],
            "saved_cases_rechecked": 53, "actions_reexecuted": False,
            "independent_reproduction": "NOT_ESTABLISHED", "human_review": "NOT_PERFORMED",
            "conformance": "NOT_ASSESSED"}


def build_report(archive, expected_sha256, destination):
    from .delivery import bundle_bytes, publish_bundle
    report = generate_report(archive, expected_sha256)
    raw = bundle_bytes(report)
    if json_bytes(source_identity()) != json_bytes(report["reporter"]):
        raise ReviewError("Execution sources changed before report publication")
    publish_bundle(destination, raw)
    return _result(report, raw, "incident-review-build/0.1")


def verify_report(archive, expected_sha256, report_path, expected_report_sha256):
    from .delivery import bundle_bytes, read_bundle
    candidate = read_bundle(report_path, expected_report_sha256)
    report = generate_report(archive, expected_sha256)
    expected = bundle_bytes(report)
    if candidate != expected:
        raise ReviewError("Candidate report differs from exact verified rederivation")
    if json_bytes(source_identity()) != json_bytes(report["reporter"]):
        raise ReviewError("Execution sources changed during report verification")
    return _result(report, expected, "incident-review-verification/0.1")
