"""Shared real frozen capture for focused tests; no original pilot actions."""

from copy import deepcopy
from functools import cache
from pathlib import Path
from tempfile import TemporaryDirectory

from incident_review.core import _load_kit, source_identity


@cache
def _capture():
    inspect, recheck, lock = _load_kit()
    from incident_recheck.archive import build_archive
    from incident_recheck.layout import collect_payload
    with TemporaryDirectory(prefix="review-test-kit-") as temporary:
        path = Path(temporary) / "kit.zip"
        built = build_archive(path, collect_payload())
        assert built["archive_sha256"] == lock["archive_sha256"]
        inspected = inspect(path, lock["archive_sha256"])
        checked = recheck(path, lock["archive_sha256"])
        raw = path.read_bytes()
    return raw, inspected, checked


def capture_fixture():
    raw, inspected, checked = _capture()
    return {"archive_bytes": raw, "files": dict(inspected["files"]),
            "inspected": deepcopy(inspected), "recheck": deepcopy(checked),
            "identity": source_identity()}


def report_fixture():
    from incident_review.projection import project
    captured = capture_fixture()
    return project(captured["files"], captured["recheck"], captured["identity"])
