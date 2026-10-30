"""Actual bounded namespace readback by the same local controller."""

import os
from pathlib import Path
import stat

from .adapter import validate_pins, validate_task
from .protocol import (InputError, MAX_OBJECT, capture, digest, object_name,
                       public_key, sha256_bytes, sign_message, timestamp, utc_now,
                       verify_message, verify_record)


def _identity(info):
    return info.st_dev, info.st_ino


class LocalObserver:
    def __init__(self, namespace_root, pins, secret, clock=utc_now):
        self.pins = validate_pins(pins)
        self.key_id = self.pins["observer_key_id"]
        self.secret = secret
        if public_key(secret) != self.pins["keys"][self.key_id]["public_key"] or not callable(clock):
            raise InputError("Observer key or clock differs from supported configuration")
        self.clock = clock
        self.namespace_root = Path(namespace_root).absolute()
        self._root_identity = None
        fd = self._open_root()
        os.close(fd)

    def _open_root(self):
        # This is an owned application directory, not an OS isolation boundary.
        if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
            raise InputError("POSIX no-follow directory operations are required")
        fd = os.open(self.namespace_root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            info = os.fstat(fd)
            named = os.stat(self.namespace_root, follow_symlinks=False)
            if (not stat.S_ISDIR(named.st_mode) or _identity(info) != _identity(named)
                    or info.st_uid != os.getuid() or info.st_mode & 0o022):
                raise InputError("Observer directory is not stable and controller-owned")
            if self._root_identity is not None and _identity(info) != self._root_identity:
                raise InputError("Observer namespace was replaced")
            self._root_identity = _identity(info)
            return fd
        except BaseException:
            os.close(fd)
            raise

    def _same_root(self, fd):
        named = os.stat(self.namespace_root, follow_symlinks=False)
        if not stat.S_ISDIR(named.st_mode) or _identity(named) != _identity(os.fstat(fd)):
            raise InputError("Observer namespace changed during read")

    def inspect(self, manifest):
        fd = self._open_root()
        handle = None
        try:
            name = object_name(manifest)
            try:
                initial = os.stat(name, dir_fd=fd, follow_symlinks=False)
            except FileNotFoundError:
                self._same_root(fd)
                return {"state": "ABSENT", "sha256": None, "byte_length": None}
            if not stat.S_ISREG(initial.st_mode):
                raise InputError("Observer refuses nonregular target")
            handle = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=fd)
            before = os.fstat(handle)
            if not stat.S_ISREG(before.st_mode) or _identity(before) != _identity(initial):
                raise InputError("Observer target changed before read")
            if not 0 < before.st_size <= MAX_OBJECT:
                raise InputError("Observer target size is outside bounds")
            chunks = []
            remaining = MAX_OBJECT + 1
            while remaining:
                chunk = os.read(handle, min(65536, remaining))
                if not chunk:
                    break
                chunks.append(chunk)
                remaining -= len(chunk)
            raw = b"".join(chunks)
            after = os.fstat(handle)
            named = os.stat(name, dir_fd=fd, follow_symlinks=False)
            stable = lambda info: (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)
            if (stable(before) != stable(after) or stable(after) != stable(named)
                    or not stat.S_ISREG(named.st_mode) or len(raw) != before.st_size):
                raise InputError("Observer target changed during read")
            self._same_root(fd)
            return {"state": "PRESENT", "sha256": sha256_bytes(raw), "byte_length": len(raw)}
        finally:
            if handle is not None:
                os.close(handle)
            os.close(fd)

    def observe(self, task, phase, previous=None, completion=None):
        owned = capture(task)
        try:
            requested_at = owned["request"]["body"]["data"]["requested_at"]
        except (KeyError, TypeError) as exc:
            raise InputError("Task lacks its original request time") from exc
        context = validate_task(owned, self.pins, requested_at)
        if phase not in {"before", "after"}:
            raise InputError("Unsupported observation phase")
        if phase == "before" and (previous is not None or completion is not None):
            raise InputError("Before observation cannot reference later evidence")
        lower = timestamp(context["operation_at"])
        if previous is not None:
            body = verify_message(previous, self.pins["keys"][self.key_id]["public_key"],
                                  self.key_id, "local_namespace_observation")
            if body["phase"] != "before" or body["task_sha256"] != context["task_sha256"]:
                raise InputError("Previous observation is for another task or phase")
            lower = max(lower, timestamp(body["window_end"]))
        if completion is not None:
            key_id = self.pins["provider_key_id"]
            body = verify_record(completion, self.pins["keys"][key_id]["public_key"],
                                 key_id, "erasure.provider_attestation")
            if body["binding"] != context["subject"] or body["evaluation_id"] != context["evaluation_id"]:
                raise InputError("Completion differs from observed task")
            lower = max(lower, timestamp(body["data"]["completed_at"]), timestamp(body["recorded_at"]))
        start = self.clock()
        if timestamp(start) < lower:
            raise InputError("Observer clock precedes linked evidence")
        measurement = self.inspect(context["manifest"])
        end = self.clock()
        key = self.pins["keys"][self.key_id]
        if not timestamp(key["not_before"]) <= timestamp(start) <= timestamp(end) < timestamp(key["not_after"]):
            raise InputError("Observation window or observer key validity is inapplicable")
        manifest = context["manifest"]
        return sign_message({
            "kind": "local_namespace_observation", "task_sha256": context["task_sha256"],
            "manifest_sha256": context["manifest_sha256"],
            **{field: manifest[field] for field in ("provider_id", "tenant_id", "location", "object_id", "version_id")},
            "phase": phase, "previous_sha256": digest(previous) if previous is not None else None,
            "completion_sha256": digest(completion) if completion is not None else None,
            "window_start": start, "window_end": end, "measurement": measurement,
        }, self.secret, self.key_id)
