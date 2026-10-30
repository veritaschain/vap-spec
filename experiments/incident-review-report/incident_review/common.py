"""Bounded data helpers for a fixed informative evidence presentation."""

import hashlib
import json
import math
import os
from pathlib import Path
import re
import stat


class ReviewError(ValueError):
    """A report input, binding or publication requirement was not established."""


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
VERSION = "0.1.0"
PILOTS = {"upload": {"count": 17, "prefix": "UL"},
          "publication": {"count": 18, "prefix": "LP"},
          "erasure": {"count": 18, "prefix": "LE"}}
SCOPE = {
    "actions_reexecuted": False, "observation_truth": "NOT_ESTABLISHED",
    "independent_reproduction": "NOT_ESTABLISHED", "human_review": "NOT_PERFORMED",
    "conformance": "NOT_ASSESSED", "legal_compliance": "NOT_ASSESSED",
    "dependency_scope": "PINNED_VERSIONS_NOT_HERMETIC",
}
MAX_INPUT = 4 * 1024 * 1024


def sha256(raw):
    if type(raw) is not bytes:
        raise ReviewError("Hash input must be owned bytes")
    return hashlib.sha256(raw).hexdigest()


def digest(value):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ReviewError("Expected a lowercase SHA-256 value")
    return value


def exact(value, keys):
    if type(value) is not dict or set(value) != set(keys):
        raise ReviewError("Fields differ from the fixed presentation contract")


def safe_path(value):
    if (type(value) is not str or len(value) > 240
            or not re.fullmatch(r"[A-Za-z0-9_.\-/]+", value)
            or value.startswith("/") or any(p in {"", ".", ".."} for p in value.split("/"))):
        raise ReviewError("Unsupported repository or evidence path")
    return value


def _bounded(value, depth=0):
    if depth > 64:
        raise ReviewError("JSON depth exceeds the presentation limit")
    if type(value) in {dict, list}:
        if len(value) > 10000:
            raise ReviewError("JSON container exceeds the presentation limit")
        if type(value) is dict:
            for key, item in value.items():
                if type(key) is not str:
                    raise ReviewError("JSON object keys must be strings")
                _bounded(key, depth + 1)
                _bounded(item, depth + 1)
        else:
            for item in value:
                _bounded(item, depth + 1)
    elif type(value) is str:
        value.encode("utf-8")
    elif type(value) is float and not math.isfinite(value):
        raise ReviewError("Non-finite JSON value")
    elif value is not None and type(value) not in {str, bool, int, float}:
        raise ReviewError("Unsupported presentation JSON value")


def strict_json(raw):
    if type(raw) is not bytes or len(raw) > MAX_INPUT:
        raise ReviewError("Invalid or oversized JSON bytes")
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ReviewError("Duplicate JSON object key")
            result[key] = value
        return result
    def constant(value):
        raise ReviewError("Non-finite JSON constant")
    try:
        value = json.loads(raw.decode("utf-8"), object_pairs_hook=pairs, parse_constant=constant)
        _bounded(value)
        return value
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise ReviewError("Invalid presentation JSON") from exc


def json_bytes(value):
    try:
        _bounded(value)
        return (json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False) + "\n").encode("ascii")
    except (UnicodeError, ValueError, TypeError, RecursionError) as exc:
        raise ReviewError("Unsupported presentation JSON") from exc


def resolve_pointer(value, pointer):
    if type(pointer) is not str or len(pointer) > 2048 or (pointer and not pointer.startswith("/")):
        raise ReviewError("Invalid concrete JSON Pointer")
    if pointer == "":
        return value
    for part in pointer[1:].split("/"):
        if re.search(r"~(?![01])", part):
            raise ReviewError("Invalid JSON Pointer escape")
        part = part.replace("~1", "/").replace("~0", "~")
        if type(value) is dict:
            if part not in value:
                raise ReviewError("JSON Pointer refers to a missing field")
            value = value[part]
        elif type(value) is list:
            if not re.fullmatch(r"0|[1-9][0-9]*", part) or len(part) > 6 or int(part) >= len(value):
                raise ReviewError("JSON Pointer refers to a missing index")
            value = value[int(part)]
        else:
            raise ReviewError("JSON Pointer traverses a scalar")
    return value


def reference(files, file, pointer):
    safe_path(file)
    if not file.startswith("evidence/") or type(files) is not dict or file not in files:
        raise ReviewError("Source reference is outside the captured evidence")
    raw = files[file]
    resolve_pointer(strict_json(raw), pointer)
    return {"file": file, "sha256": sha256(raw), "pointer": pointer}


def fact(files, file, pointer, name=None):
    source = reference(files, file, pointer)
    value = resolve_pointer(strict_json(files[file]), pointer)
    return {"name": pointer if name is None else name, "value": value, "source": source}


def read_regular(root, relative, *, limit=MAX_INPUT):
    """Capture stable bounded local bytes without following named symlinks."""
    safe_path(relative)
    root = Path(root).absolute()
    try:
        current = root
        if not stat.S_ISDIR(root.lstat().st_mode):
            raise ReviewError("Input root is not a regular directory")
        for part in relative.split("/")[:-1]:
            current /= part
            if not stat.S_ISDIR(current.lstat().st_mode):
                raise ReviewError("Input traverses a symlink or non-directory")
        path = root / relative
        before = path.lstat()
        if not stat.S_ISREG(before.st_mode) or not 0 <= before.st_size <= limit:
            raise ReviewError("Input is not a bounded regular file")
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        try:
            state = lambda s: (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)
            opened = os.fstat(descriptor)
            if state(opened) != state(before):
                raise ReviewError("Input changed before capture")
            chunks, size = [], 0
            while size <= limit:
                part = os.read(descriptor, min(65536, limit + 1 - size))
                if not part:
                    break
                chunks.append(part)
                size += len(part)
            if (size != opened.st_size or state(os.fstat(descriptor)) != state(opened)
                    or state(path.lstat()) != state(opened)):
                raise ReviewError("Input changed during capture")
            return b"".join(chunks)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise ReviewError("Cannot read the required regular source file") from exc
