"""Validate an archive before staging it and invoking fixed, read-only workers."""

import os
from pathlib import Path
import selectors
import subprocess
import sys
from tempfile import TemporaryDirectory
import time

from .archive import inspect_archive
from .layout import (KIT_SOURCE_FILES, PILOTS, REPO_ROOT, SNAPSHOT_ID, KitError,
                     expected_payload_paths, load_source_lock, read_regular,
                     safe_path, sha256, strict_json, validate_provenance)
from .worker import DEPENDENCIES

PILOT_ORDER = ("upload", "publication", "erasure")
WORKER_PATH = "experiments/incident-recheck-kit/incident_recheck/worker.py"
OUTPUT_LIMIT = 64 * 1024


def _source_requirements():
    lock = load_source_lock()
    paths = sorted(set(lock["files"]) | set(KIT_SOURCE_FILES))
    trusted = {}
    for path in paths:
        safe_path(path)
        raw = read_regular(REPO_ROOT, path)
        if path in lock["files"] and sha256(raw) != lock["files"][path]:
            raise KitError("Trusted checkout differs from the original source lock: " + path)
        trusted[path] = raw
    return trusted


def _validate_archived_sources(files):
    if type(files) is not dict or set(files) != expected_payload_paths() or any(type(raw) is not bytes for raw in files.values()):
        raise KitError("Archive payload differs from the exact owned-byte inventory")
    for path, raw in _source_requirements().items():
        if files["source/" + path] != raw:
            raise KitError("Archived source differs from the trusted checkout: " + path)


def _validate_worker_tree(source_root):
    # This public test seam also refuses a caller-selected script or modified
    # module tree. recheck_archive has already checked these bytes before staging.
    for path, raw in _source_requirements().items():
        if read_regular(source_root, path) != raw:
            raise KitError("Worker source tree differs from trusted source: " + path)


def _capture_child(command, *, cwd, timeout):
    """Read both pipes incrementally; never buffer unbounded child output."""
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    environment.pop("PYTHONHOME", None)
    process = subprocess.Popen(command, cwd=cwd, env=environment, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True, bufsize=0)
    selector = None
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    deadline = time.monotonic() + timeout
    try:
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ, "stdout")
        selector.register(process.stderr, selectors.EVENT_READ, "stderr")
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise KitError("Offline recheck worker exceeded its time limit")
            for key, _ in selector.select(min(remaining, 0.1)):
                name = key.data
                chunk = os.read(key.fd, min(8192, OUTPUT_LIMIT + 1 - len(captured[name])))
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                captured[name].extend(chunk)
                if len(captured[name]) > OUTPUT_LIMIT:
                    raise KitError("Offline recheck worker exceeded its " + name + " limit")
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise KitError("Offline recheck worker exceeded its time limit")
        try:
            returncode = process.wait(timeout=remaining)
        except subprocess.TimeoutExpired as exc:
            raise KitError("Offline recheck worker exceeded its time limit") from exc
        return returncode, bytes(captured["stdout"]), bytes(captured["stderr"])
    finally:
        if selector is not None:
            selector.close()
        if process.poll() is None:
            process.kill()
        try:
            process.wait(timeout=5)
        finally:
            for pipe in (process.stdout, process.stderr):
                if pipe is not None:
                    pipe.close()


def _validate_worker_result(value, pilot):
    required = {"format", "pilot", "verified_exports", "actions_reexecuted", "source_sha256", "dependencies", "guard"}
    if type(value) is not dict or set(value) != required:
        raise KitError("Worker did not return the exact structured result")
    selected = PILOTS[pilot]
    if (value["format"] != "incident-recheck-worker/0.1" or value["pilot"] != pilot
            or type(value["verified_exports"]) is not int or value["verified_exports"] != selected["count"]
            or value["actions_reexecuted"] is not False or value["source_sha256"] != selected["source_sha256"]
            or type(value["dependencies"]) is not dict or value["dependencies"] != DEPENDENCIES
            or value["guard"] != "PYTHON_AUDIT_EVENTS"):
        raise KitError("Worker result differs from the fixed pilot, dependency or action boundary")
    return value


def run_worker(source_root, evidence_root, pilot, *, timeout=30):
    if type(pilot) is not str or pilot not in PILOT_ORDER:
        raise KitError("Unsupported fixed pilot")
    if type(timeout) not in {int, float} or not 0 < timeout <= 30:
        raise KitError("Worker timeout must be positive and at most 30 seconds")
    source_root, evidence_root = Path(source_root).absolute(), Path(evidence_root).absolute()
    _validate_worker_tree(source_root)
    worker = source_root / WORKER_PATH
    code, stdout, stderr = _capture_child(
        [sys.executable, "-I", "-B", str(worker), str(source_root), str(evidence_root), pilot],
        cwd=source_root, timeout=timeout,
    )
    if code != 0:
        detail = stderr.decode("utf-8", errors="replace").strip()[:2048]
        raise KitError("Offline recheck worker failed for " + pilot + (": " + detail if detail else ""))
    if stderr:
        raise KitError("Offline recheck worker emitted unexpected diagnostics")
    return _validate_worker_result(strict_json(stdout), pilot)


def recheck_archive(path, expected_sha256):
    inspected = inspect_archive(path, expected_sha256)
    files = inspected["files"]
    # These checks must all precede staging or importing anything from the
    # candidate archive. In particular, an archive's self-consistent source
    # hashes do not authorize its source code for execution.
    _validate_archived_sources(files)
    validate_provenance(files)
    with TemporaryDirectory(prefix="incident-recheck-") as temporary:
        staging = Path(temporary)
        for relative, raw in sorted(files.items()):
            safe_path(relative)
            destination = staging / relative
            destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            with destination.open("xb") as handle:
                handle.write(raw)
            destination.chmod(0o400)
        results = [run_worker(staging / "source", staging / "evidence", pilot) for pilot in PILOT_ORDER]
    return {
        "format": "incident-recheck-report/0.1", "snapshot_id": SNAPSHOT_ID,
        "archive_sha256": inspected["archive_sha256"], "manifest_sha256": inspected["manifest_sha256"],
        "source_binding": "MATCHED_TRUSTED_CHECKOUT", "verified_exports": sum(item["verified_exports"] for item in results),
        "pilots": results, "actions_reexecuted": False, "independent_reproduction": "NOT_ESTABLISHED",
        "conformance": "NOT_ASSESSED", "dependency_scope": "PINNED_VERSIONS_NOT_HERMETIC",
    }
