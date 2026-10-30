"""A fixed, bounded ZIP_STORED evidence envelope; no extraction or execution."""

import binascii
import os
import re
import stat
import struct
from pathlib import Path

from .layout import (
    SNAPSHOT_ID, KitError, expected_payload_paths, json_bytes, safe_path, sha256,
    strict_json,
)


MAX_ARCHIVE = 16 * 1024 * 1024
MAX_MEMBER = 4 * 1024 * 1024
MAX_MEMBERS = 256
MAX_PAYLOAD = 12 * 1024 * 1024
MAX_CENTRAL = 128 * 1024
MANIFEST_NAME = "manifest.json"
SCOPE = {"operation": "OFFLINE_RECHECK_ONLY", "independent_reproduction": "NOT_ESTABLISHED",
         "actions_reexecuted": False, "conformance": "NOT_ASSESSED"}
LOCAL = struct.Struct("<4s5H3I2H")
CENTRAL = struct.Struct("<4s6H3I5H2I")
END = struct.Struct("<4s4H2IH")
VERSION = 20
UNIX_VERSION = (3 << 8) | VERSION
FILE_ATTRIBUTES = (stat.S_IFREG | 0o644) << 16
DOS_DATE = 33  # 1980-01-01; time is always zero.


def _path(name):
    if type(name) is not str:
        raise KitError("Archive paths must be strings")
    try:
        raw = name.encode("ascii")
    except UnicodeError as exc:
        raise KitError("Archive paths must be ASCII") from exc
    safe_path(name)
    if (not raw or len(raw) > 65535 or name.startswith("/") or "\\" in name or "\0" in name
            or ":" in name or any(part in {"", ".", ".."} for part in name.split("/"))):
        raise KitError("Unsafe archive path")
    return raw


def _inventory():
    paths = set(expected_payload_paths())
    if MANIFEST_NAME in paths or not paths or len(paths) + 1 > MAX_MEMBERS:
        raise KitError("Trusted payload inventory is outside archive bounds")
    folded = set()
    for name in paths:
        _path(name)
        if name.casefold() in folded:
            raise KitError("Trusted payload inventory contains colliding paths")
        folded.add(name.casefold())
    return paths


def _owned_payload(payload):
    if type(payload) is not dict or len(payload) + 1 > MAX_MEMBERS:
        raise KitError("Payload must be a bounded dictionary of owned bytes")
    try:
        owned = dict(payload)
    except RuntimeError as exc:
        raise KitError("Payload changed during capture") from exc
    if set(owned) != _inventory():
        raise KitError("Payload differs from the exact fixed file inventory")
    total = 0
    for name, value in owned.items():
        _path(name)
        if type(value) is not bytes or len(value) > MAX_MEMBER:
            raise KitError("Payload members must be owned bytes within the member limit")
        total += len(value)
    if total > MAX_PAYLOAD:
        raise KitError("Aggregate payload exceeds the supported limit")
    return owned, total


def _manifest(files):
    return {"format": "incident-recheck-archive/0.1", "snapshot_id": SNAPSHOT_ID,
            "scope": dict(SCOPE), "entries": [
                {"path": name, "sha256": sha256(files[name]), "byte_length": len(files[name])}
                for name in sorted(files)
            ]}


def _encode_zip(files):
    names = sorted(files)
    central_size = sum(CENTRAL.size + len(_path(name)) for name in names)
    local_size = sum(LOCAL.size + len(_path(name)) + len(files[name]) for name in names)
    if (len(names) > MAX_MEMBERS or central_size > MAX_CENTRAL
            or local_size + central_size + END.size > MAX_ARCHIVE):
        raise KitError("Encoded archive would exceed a physical format limit")
    local_parts, central_parts, offset = [], [], 0
    for name in names:
        raw_name, content = _path(name), files[name]
        if len(content) > MAX_MEMBER:
            raise KitError("Encoded archive member exceeds its size limit")
        size, crc = len(content), binascii.crc32(content) & 0xFFFFFFFF
        local_parts.extend((LOCAL.pack(b"PK\x03\x04", VERSION, 0, 0, 0, DOS_DATE,
                                       crc, size, size, len(raw_name), 0), raw_name, content))
        central_parts.extend((CENTRAL.pack(b"PK\x01\x02", UNIX_VERSION, VERSION, 0, 0, 0, DOS_DATE,
                                           crc, size, size, len(raw_name), 0, 0, 0, 0, FILE_ATTRIBUTES, offset), raw_name))
        offset += LOCAL.size + len(raw_name) + size
    ending = END.pack(b"PK\x05\x06", 0, 0, len(names), len(names), central_size, offset, 0)
    return b"".join(local_parts + central_parts + [ending])


def build_archive(destination, payload):
    """Exclusively create a deterministic archive; counts exclude manifest.json.

    The destination's parent must exist. A failed write is never reported as a
    successful archive and does not trigger replacement of an existing path.
    """
    files, total = _owned_payload(payload)
    manifest_bytes = json_bytes(_manifest(files))
    archive = _encode_zip({**files, MANIFEST_NAME: manifest_bytes})
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(Path(destination), flags, 0o600)
        try:
            remaining = memoryview(archive)
            while remaining:
                written = os.write(descriptor, remaining)
                if written <= 0:
                    raise OSError("Archive write made no progress")
                remaining = remaining[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise KitError("Cannot exclusively create and finish the requested archive") from exc
    return {"archive_sha256": sha256(archive), "manifest_sha256": sha256(manifest_bytes),
            "file_count": len(files), "payload_bytes": total}


def _file_state(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


def _read_archive(path):
    try:
        path = Path(path)
        named = path.lstat()
        if not stat.S_ISREG(named.st_mode) or not 0 < named.st_size <= MAX_ARCHIVE:
            raise KitError("Archive input must be a bounded nonempty regular file, not a symlink")
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
        descriptor = os.open(path, flags)
        try:
            opened = os.fstat(descriptor)
            if not stat.S_ISREG(opened.st_mode) or _file_state(opened) != _file_state(named):
                raise KitError("Archive input changed before it could be captured")
            chunks, total = [], 0
            while True:
                part = os.read(descriptor, min(65536, MAX_ARCHIVE + 1 - total))
                if not part:
                    break
                total += len(part)
                if total > MAX_ARCHIVE:
                    raise KitError("Archive input exceeds the physical size limit")
                chunks.append(part)
            if total != opened.st_size or _file_state(os.fstat(descriptor)) != _file_state(opened):
                raise KitError("Archive input changed during capture")
            return b"".join(chunks)
        finally:
            os.close(descriptor)
    except OSError as exc:
        raise KitError("Cannot safely read the requested regular archive") from exc


def _parse_zip(raw):
    """Accept exactly the emitted nonoverlapping stored-file ZIP grammar."""
    if len(raw) < END.size:
        raise KitError("Truncated ZIP ending")
    ending = END.unpack_from(raw, len(raw) - END.size)
    signature, disk, central_disk, on_disk, count, central_size, central_offset, comment = ending
    if (signature != b"PK\x05\x06" or disk != 0 or central_disk != 0 or on_disk != count
            or not 0 < count <= MAX_MEMBERS or comment != 0):
        raise KitError("Unsupported ZIP ending, count, comment or multidisk format")
    if (not 0 < central_size <= MAX_CENTRAL or central_offset + central_size != len(raw) - END.size
            or central_offset < LOCAL.size):
        raise KitError("ZIP central directory bounds or trailing data are invalid")
    entries, names, folded = [], set(), set()
    cursor, central_end, aggregate = central_offset, central_offset + central_size, 0
    for _ in range(count):
        if cursor + CENTRAL.size > central_end:
            raise KitError("Truncated ZIP central directory")
        fields = CENTRAL.unpack_from(raw, cursor)
        (signature, made_by, needed, flags, compression, dos_time, dos_date, crc, compressed_size,
         size, name_length, extra_length, comment_length, disk_start, internal, external, local_offset) = fields
        if (signature != b"PK\x01\x02" or made_by != UNIX_VERSION or needed != VERSION
                or flags != 0 or compression != 0 or dos_time != 0 or dos_date != DOS_DATE
                or extra_length != 0 or comment_length != 0 or disk_start != 0 or internal != 0
                or external != FILE_ATTRIBUTES):
            raise KitError("Unsupported ZIP entry flags, mode, metadata or compression")
        if compressed_size != size or size > MAX_MEMBER or name_length == 0:
            raise KitError("ZIP member size or stored encoding is invalid")
        end = cursor + CENTRAL.size + name_length
        if end > central_end:
            raise KitError("ZIP member name exceeds the central directory")
        name_bytes = raw[cursor + CENTRAL.size:end]
        try:
            name = name_bytes.decode("ascii")
        except UnicodeError as exc:
            raise KitError("ZIP member path is not ASCII") from exc
        _path(name)
        if name in names or name.casefold() in folded:
            raise KitError("Duplicate or casefold-colliding ZIP member path")
        names.add(name)
        folded.add(name.casefold())
        if name != MANIFEST_NAME:
            aggregate += size
            if aggregate > MAX_PAYLOAD:
                raise KitError("ZIP aggregate payload exceeds the limit")
        entries.append((name, name_bytes, crc, size, local_offset))
        cursor = end
    if cursor != central_end or [entry[0] for entry in entries] != sorted(names):
        raise KitError("ZIP central directory has extra records or unsorted names")
    if names != _inventory() | {MANIFEST_NAME}:
        raise KitError("ZIP member inventory differs from the fixed public payload")
    files, cursor = {}, 0
    for name, name_bytes, crc, size, local_offset in entries:
        if local_offset != cursor or cursor + LOCAL.size > central_offset:
            raise KitError("ZIP members overlap, have gaps or refer outside their physical order")
        fields = LOCAL.unpack_from(raw, cursor)
        (signature, needed, flags, compression, dos_time, dos_date, local_crc,
         compressed_size, local_size, name_length, extra_length) = fields
        if (signature != b"PK\x03\x04" or needed != VERSION or flags != 0 or compression != 0
                or dos_time != 0 or dos_date != DOS_DATE or local_crc != crc or compressed_size != size
                or local_size != size or name_length != len(name_bytes) or extra_length != 0):
            raise KitError("ZIP local header disagrees with its supported central entry")
        name_start = cursor + LOCAL.size
        data_start, end = name_start + name_length, name_start + name_length + size
        if end > central_offset or raw[name_start:data_start] != name_bytes:
            raise KitError("ZIP member extent or local name does not match the central entry")
        content = raw[data_start:end]
        if binascii.crc32(content) & 0xFFFFFFFF != crc:
            raise KitError("ZIP member CRC mismatch")
        files[name] = content
        cursor = end
    if cursor != central_offset:
        raise KitError("ZIP data contains unreferenced or trailing bytes")
    return files


def inspect_archive(path, expected_sha256):
    """Authenticate raw bytes first; then return verified payload bytes, unextracted."""
    if type(expected_sha256) is not str or not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise KitError("A separate lowercase SHA-256 digest is required")
    raw = _read_archive(path)
    actual_sha256 = sha256(raw)
    if actual_sha256 != expected_sha256:
        raise KitError("Archive does not match the externally supplied SHA-256")
    members = _parse_zip(raw)
    manifest_bytes = members.pop(MANIFEST_NAME)
    manifest = strict_json(manifest_bytes)
    expected_manifest = _manifest(members)
    if manifest_bytes != json_bytes(expected_manifest):
        raise KitError("Manifest schema, canonical encoding, inventory, digest or length does not match payload")
    return {"manifest": manifest, "files": members, "archive_sha256": actual_sha256,
            "manifest_sha256": sha256(manifest_bytes)}
