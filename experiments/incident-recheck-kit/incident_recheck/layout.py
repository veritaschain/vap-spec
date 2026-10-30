"""Fixed paths, captured provenance and source identity; standard library only."""

from datetime import datetime
import hashlib
import json
import math
import os
from pathlib import Path
import posixpath
import re
import stat


class KitError(ValueError):
    """An input, source or captured evidence requirement was not established."""


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
_LOCAL_SNAPSHOT = ROOT / "snapshots/2026-10-30-ci"
SNAPSHOT_ROOT = _LOCAL_SNAPSHOT if _LOCAL_SNAPSHOT.exists() else REPO_ROOT.parent / "evidence"
SNAPSHOT_ID = "incident-ci-2026-10-30"
PILOTS = {
    "upload": {"directory": "experiments/incident-upload-pilot", "module": "upload_pilot", "prefix": "UL", "count": 17,
               "source_sha256": "0f7e7f04c45baca8bc62ea0f8778c79ef5bba22e27faf49fbad92001c617df49"},
    "publication": {"directory": "experiments/incident-publication-pilot", "module": "publication_pilot", "prefix": "LP", "count": 18,
                    "source_sha256": "78386924abf2ac6819f653d7c282972b86e58ac1379751c213bca1e5334c639c"},
    "erasure": {"directory": "experiments/incident-erasure-pilot", "module": "erasure_pilot", "prefix": "LE", "count": 18,
                "source_sha256": "fb0dc41bde92840e06f11c9077c41743dc8c1255b4404aaa464b7455fa829191"},
}
KIT_PREFIX = "experiments/incident-recheck-kit/"
KIT_SOURCE_FILES = tuple(KIT_PREFIX + p for p in (
    "incident_recheck/__init__.py", "incident_recheck/__main__.py", "incident_recheck/layout.py",
    "incident_recheck/archive.py", "incident_recheck/runner.py", "incident_recheck/worker.py",
    "source-lock.json", "requirements.txt", "README.md", "RUN-ja.md")) + ("LICENSE",)
MAX_FILE = 4 * 1024 * 1024
MAX_JSON = MAX_FILE


def sha256(raw):
    if type(raw) is not bytes:
        raise KitError("Hash input must be owned bytes")
    return hashlib.sha256(raw).hexdigest()


def exact(value, fields):
    if type(value) is not dict or set(value) != set(fields):
        raise KitError("Object fields differ from the fixed kit contract")


def hex_digest(value, size=64):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{" + str(size) + r"}", value):
        raise KitError("Invalid lowercase hexadecimal identity")
    return value


def safe_path(value):
    if (type(value) is not str or not value or len(value) > 240
            or not re.fullmatch(r"[A-Za-z0-9_.\-/]+", value)
            or value.startswith("/") or any(p in {"", ".", ".."} for p in value.split("/"))):
        raise KitError("Unsupported archive-relative path")
    return value


def _bounded(value, depth=0):
    if depth > 64:
        raise KitError("JSON nesting exceeds the bounded contract")
    if type(value) in {dict, list}:
        if len(value) > 10000:
            raise KitError("JSON container exceeds the bounded contract")
        if type(value) is dict:
            for key, item in value.items():
                _bounded(key, depth + 1)
                _bounded(item, depth + 1)
        else:
            for item in value:
                _bounded(item, depth + 1)
    elif type(value) is str:
        value.encode("utf-8")
    elif type(value) is float and not math.isfinite(value):
        raise KitError("Non-finite JSON value")
    elif value is not None and type(value) not in {bool, int, float}:
        raise KitError("Unsupported JSON value")


def strict_json(raw):
    if type(raw) is not bytes or len(raw) > MAX_JSON:
        raise KitError("Invalid or oversized JSON input")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise KitError("Duplicate JSON object key")
            result[key] = value
        return result
    def constant(value):
        raise KitError("Non-finite JSON input")
    try:
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        _bounded(data)
        return data
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise KitError("Invalid JSON input") from exc


def json_bytes(value):
    try:
        _bounded(value)
        return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise KitError("Unsupported manifest JSON value") from exc


def read_regular(root, relative):
    """Read one bounded, stable regular file without following path symlinks."""
    safe_path(relative)
    root = Path(root).absolute()
    current = root
    if not stat.S_ISDIR(root.lstat().st_mode):
        raise KitError("Input root is not a real directory")
    for part in relative.split("/")[:-1]:
        current /= part
        if not stat.S_ISDIR(current.lstat().st_mode):
            raise KitError("Input path traverses a non-directory or symlink")
    path = root / relative
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or not 0 <= info.st_size <= MAX_FILE:
        raise KitError("Input is not a bounded regular file")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        before = os.fstat(fd)
        state = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
        if state(before) != state(info):
            raise KitError("Input changed before read")
        chunks, size = [], 0
        while size <= MAX_FILE:
            chunk = os.read(fd, min(65536, MAX_FILE + 1 - size))
            if not chunk:
                break
            chunks.append(chunk)
            size += len(chunk)
        after = os.fstat(fd)
        if size != before.st_size or state(before) != state(after) or state(after) != state(path.lstat()):
            raise KitError("Input changed during read")
        return b"".join(chunks)
    finally:
        os.close(fd)


def load_source_lock():
    data = strict_json(read_regular(ROOT, "source-lock.json"))
    exact(data, {"format", "repository", "source_commit", "provenance_sha256", "files", "pilots"})
    if data["format"] != "incident-recheck-source-lock/0.1" or data["repository"] != "veritaschain/vap-spec":
        raise KitError("Unsupported source lock")
    hex_digest(data["source_commit"], 40)
    hex_digest(data["provenance_sha256"])
    if data["pilots"] != {name: p["source_sha256"] for name, p in PILOTS.items()}:
        raise KitError("Pilot source identities differ from fixed implementation")
    if type(data["files"]) is not dict or not 1 <= len(data["files"]) <= 128:
        raise KitError("Unsupported source inventory")
    for path, digest in data["files"].items():
        safe_path(path)
        hex_digest(digest)
    if len({p.casefold() for p in data["files"]}) != len(data["files"]):
        raise KitError("Source inventory has case-colliding paths")
    return data


def evidence_files(pilot):
    p = PILOTS[pilot]
    return ["summary.json"] + [f"cases/{p['prefix']}-{number:02d}.json" for number in range(1, p["count"] + 1)]


def expected_payload_paths():
    sources = set(load_source_lock()["files"]) | set(KIT_SOURCE_FILES)
    names = {"source/" + p for p in sources} | {"evidence/provenance.json"}
    for pilot in PILOTS:
        names.update("evidence/" + pilot + "/" + p for p in evidence_files(pilot))
    for name in names:
        safe_path(name)
    return names


def validate_provenance(files):
    raw = files["evidence/provenance.json"]
    lock = load_source_lock()
    if sha256(raw) != lock["provenance_sha256"]:
        raise KitError("Provenance differs from the trusted fixed capture record")
    data = strict_json(raw)
    exact(data, {"format", "snapshot_id", "repository", "pilot_source_snapshot_commit", "capture_method", "independent_reproduction", "pilots"})
    if (data["format"] != "incident-recheck-provenance/0.1" or data["snapshot_id"] != SNAPSHOT_ID
            or data["repository"] != "veritaschain/vap-spec" or data["pilot_source_snapshot_commit"] != lock["source_commit"]
            or data["capture_method"] != "ORIGINAL_CI_ARTIFACT_BYTES" or data["independent_reproduction"] != "NOT_ESTABLISHED"):
        raise KitError("Unsupported capture provenance or assurance claim")
    exact(data["pilots"], PILOTS)
    for name, p in PILOTS.items():
        item = data["pilots"][name]
        exact(item, {"workflow_run_id", "workflow_run_url", "workflow_event", "job_id", "checkout_commit", "artifact_id", "artifact_sha256", "artifact_byte_length", "original_artifact_expires_at", "python_series", "source_sha256", "case_count", "files"})
        for key in ("workflow_run_id", "job_id", "artifact_id", "artifact_byte_length", "case_count"):
            if type(item[key]) is not int or item[key] <= 0:
                raise KitError("Invalid capture identifier or count")
        if (item["source_sha256"] != p["source_sha256"] or item["case_count"] != p["count"]
                or item["python_series"] != "3.12" or item["workflow_event"] not in {"push", "pull_request"}
                or item["workflow_run_url"] != f"https://github.com/veritaschain/vap-spec/actions/runs/{item['workflow_run_id']}"):
            raise KitError("Capture metadata differs from the selected pilot")
        hex_digest(item["checkout_commit"], 40)
        hex_digest(item["artifact_sha256"])
        try:
            if datetime.fromisoformat(item["original_artifact_expires_at"].replace("Z", "+00:00")).tzinfo is None:
                raise ValueError("Missing time zone")
        except (AttributeError, ValueError) as exc:
            raise KitError("Invalid recorded artifact expiry") from exc
        exact(item["files"], evidence_files(name))
        for relative, measurement in item["files"].items():
            exact(measurement, {"sha256", "byte_length"})
            hex_digest(measurement["sha256"])
            content = files["evidence/" + name + "/" + relative]
            if (type(measurement["byte_length"]) is not int or measurement["byte_length"] != len(content)
                    or measurement["sha256"] != sha256(content)):
                raise KitError("Original public capture bytes differ from the pinned provenance")
        summary = strict_json(files["evidence/" + name + "/summary.json"])
        if (summary.get("source_sha256") != p["source_sha256"] or type(summary.get("total")) is not int
                or summary["total"] != p["count"] or type(summary.get("matched")) is not int
                or summary["matched"] != p["count"] or summary.get("all_expectations_matched") is not True):
            raise KitError("Original summary identity or counts differ")
        manifest = summary["source_files"]
        if type(manifest) is not dict or sha256(json_bytes(manifest)[:-1]) != p["source_sha256"]:
            raise KitError("Original source manifest digest differs")
        # Original keys legitimately use ../ within the fixed repo topology;
        # normalize to safe locked paths rather than treating them as ZIP names.
        for relative, digest in manifest.items():
            if type(relative) is not str or relative.startswith("/") or "\\" in relative:
                raise KitError("Unsupported original source reference")
            mapped = safe_path(posixpath.normpath(posixpath.join(p["directory"], relative)))
            if lock["files"].get(mapped) != digest or sha256(files["source/" + mapped]) != digest:
                raise KitError("Original source manifests disagree with the frozen source tree")
    return data


def collect_payload():
    names = expected_payload_paths()
    expected_capture = {p.removeprefix("evidence/") for p in names if p.startswith("evidence/")}
    actual_capture = set()
    expected_dirs = {"."}
    for relative in expected_capture:
        expected_dirs.update(str(p) for p in Path(relative).parents)
    for current, dirs, files in os.walk(SNAPSHOT_ROOT, followlinks=False):
        rel = Path(current).relative_to(SNAPSHOT_ROOT).as_posix()
        if rel not in expected_dirs or Path(current).is_symlink():
            raise KitError("Unexpected or unsafe capture directory")
        for child in dirs:
            if (Path(current) / child).is_symlink():
                raise KitError("Capture directory symlink is unsupported")
        for child in files:
            actual_capture.add((Path(current) / child).relative_to(SNAPSHOT_ROOT).as_posix())
    if actual_capture != expected_capture:
        raise KitError("Fixed capture inventory contains missing or additional files")
    payload = {}
    for name in sorted(names):
        root, relative = (REPO_ROOT, name.removeprefix("source/")) if name.startswith("source/") else (SNAPSHOT_ROOT, name.removeprefix("evidence/"))
        payload[name] = read_regular(root, relative)
    for path, digest in load_source_lock()["files"].items():
        if sha256(payload["source/" + path]) != digest:
            raise KitError("Trusted pilot source differs from its frozen lock")
    validate_provenance(payload)
    return payload


def source_manifest():
    paths = {REPO_ROOT / p for p in load_source_lock()["files"]}
    paths.update(REPO_ROOT / p for p in KIT_SOURCE_FILES)
    paths.update((ROOT / "incident_recheck").glob("*.py"))
    paths.update((ROOT / "tests").glob("*.py"))
    paths.update(ROOT.glob("*.py"))
    paths.update(SNAPSHOT_ROOT.rglob("*.json"))
    paths.add(REPO_ROOT / ".github/workflows/incident-recheck-kit.yml")
    return {p.relative_to(REPO_ROOT).as_posix(): sha256(read_regular(REPO_ROOT, p.relative_to(REPO_ROOT).as_posix())) for p in sorted(paths)}
