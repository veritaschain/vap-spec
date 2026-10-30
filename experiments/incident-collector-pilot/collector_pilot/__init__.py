"""Synthetic collector prerequisite experiment over a fixed local toolchain."""

import hashlib
import json
from pathlib import Path
import stat
import sys

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
UPLOAD_ROOT = ROOT.parent / "incident-upload-pilot"
ASSESSOR_ROOT = ROOT.parent / "incident-evidence-assessor"
VERSION = "0.1.0"
FROZEN_SOURCE_SHA256 = "1b6187b8d732e299de389e957601b96ad971f908f1b96cc6da11d2662e2efb3b"
FROZEN_COMMIT = "433f019513d991982fc6fb08bd4529808cc9f6a1"


def _regular(base, relative):
    if (type(relative) is not str or relative.startswith("/")
            or any(p in {"", ".", ".."} for p in relative.split("/"))):
        raise ImportError("Invalid fixed dependency path")
    path = base
    for component in relative.split("/"):
        path = path / component
        if path.is_symlink():
            raise ImportError("Symlink in fixed dependency path")
    if not stat.S_ISREG(path.stat().st_mode) or path.stat().st_size > 4 * 1024 * 1024:
        raise ImportError("Invalid fixed dependency file")
    return path.read_bytes()


def verify_frozen_sources():
    """Hash every frozen execution input before importing reused modules."""
    try:
        raw = _regular(ROOT, "dependency-lock.json")
        def pairs(items):
            result = {}
            for key, value in items:
                if key in result:
                    raise ImportError("Duplicate dependency lock key")
                result[key] = value
            return result
        lock = json.loads(raw, object_pairs_hook=pairs)
        if (type(lock) is not dict or set(lock) != {"format", "upstream_commit", "source_sha256", "files"}
                or lock["format"] != "collector-pilot-frozen-inputs/0.1"
                or lock["upstream_commit"] != FROZEN_COMMIT
                or lock["source_sha256"] != FROZEN_SOURCE_SHA256
                or type(lock["files"]) is not dict or len(lock["files"]) != 154):
            raise ImportError("Unexpected frozen execution inventory")
        manifest = lock["files"]
        encoded = json.dumps(manifest, sort_keys=True, ensure_ascii=True,
                             separators=(",", ":"), allow_nan=False).encode("ascii")
        if hashlib.sha256(encoded).hexdigest() != FROZEN_SOURCE_SHA256:
            raise ImportError("Frozen dependency manifest digest differs")
        for path, expected in manifest.items():
            if hashlib.sha256(_regular(REPO_ROOT, path)).hexdigest() != expected:
                raise ImportError("Frozen execution input changed: " + path)
        return manifest
    except (OSError, ValueError, TypeError) as exc:
        raise ImportError("Cannot verify fixed dependency checkout") from exc


def _check_origins():
    for package, directory in (("upload_pilot", UPLOAD_ROOT), ("incident_assessor", ASSESSOR_ROOT)):
        for name, module in tuple(sys.modules.items()):
            if name != package and not name.startswith(package + "."):
                continue
            parts = name.split(".")
            expected = directory.joinpath(*parts)
            expected = expected / "__init__.py" if len(parts) == 1 else expected.with_suffix(".py")
            filename = getattr(module, "__file__", None)
            if filename is None or Path(filename).resolve() != expected.resolve():
                raise ImportError("Reused module has an unexpected origin: " + name)


verify_frozen_sources()
_check_origins()
sys.path.insert(0, str(UPLOAD_ROOT))
sys.path.insert(0, str(ASSESSOR_ROOT))
