"""Focused physical ZIP and manifest boundaries using the actual fixed payload."""

import io
import json
import os
import socket
import stat
import struct
import tempfile
import unittest
import warnings
import zipfile
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from incident_recheck.archive import (
    MAX_ARCHIVE, MAX_CENTRAL, MAX_MEMBER, MAX_MEMBERS, build_archive, inspect_archive,
)
from incident_recheck.layout import KitError, collect_payload, json_bytes, sha256


def standard_zip(items):
    """Independent stdlib writer for malformed-input and interoperability checks."""
    output = io.BytesIO()
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)  # Deliberate duplicate-name specimens.
        with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
            for name, content in sorted(items, key=lambda item: item[0]):
                info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                info.create_system, info.create_version, info.extract_version = 3, 20, 20
                info.external_attr = (stat.S_IFREG | 0o644) << 16
                archive.writestr(info, content, compress_type=zipfile.ZIP_STORED)
    return output.getvalue()


def patched(raw, offset, kind, value):
    changed = bytearray(raw)
    struct.pack_into(kind, changed, offset, value)
    return bytes(changed)


class ArchiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = collect_payload()
        cls.directory = tempfile.TemporaryDirectory(prefix="incident-archive-reference-")
        cls.addClassCleanup(cls.directory.cleanup)
        cls.reference_path = Path(cls.directory.name) / "reference.zip"
        cls.built = build_archive(cls.reference_path, cls.payload)
        cls.raw = cls.reference_path.read_bytes()
        with zipfile.ZipFile(io.BytesIO(cls.raw)) as archive:
            cls.members = {info.filename: archive.read(info) for info in archive.infolist()}
            cls.first = archive.infolist()[0]
        cls.central_offset = struct.unpack_from("<I", cls.raw, len(cls.raw) - 6)[0]

    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="incident-archive-test-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        guard = patch.object(socket, "socket", side_effect=AssertionError("Archive tests cannot open sockets"))
        guard.start()
        self.addCleanup(guard.stop)

    def specimen(self, raw, name="candidate.zip"):
        path = self.root / name
        path.write_bytes(raw)
        return path

    def assert_rejected(self, raw):
        with self.assertRaises(KitError):
            inspect_archive(self.specimen(raw), sha256(raw))

    def test_deterministic_archive_preserves_every_original_byte_without_extraction(self):
        other = self.root / "same.zip"
        result = build_archive(other, dict(reversed(list(self.payload.items()))))
        self.assertEqual(result, self.built)
        self.assertEqual(other.read_bytes(), self.raw)
        self.assertEqual(set(result), {"archive_sha256", "manifest_sha256", "file_count", "payload_bytes"})
        self.assertEqual(result["file_count"], len(self.payload))
        self.assertEqual(result["payload_bytes"], sum(map(len, self.payload.values())))
        before = set(self.root.iterdir())
        with patch.object(zipfile.ZipFile, "extractall", side_effect=AssertionError("Extraction is forbidden")):
            inspected = inspect_archive(other, result["archive_sha256"])
        self.assertEqual(set(self.root.iterdir()), before)
        self.assertEqual(set(inspected), {"manifest", "files", "archive_sha256", "manifest_sha256"})
        self.assertEqual(inspected["files"], self.payload)
        self.assertNotIn("manifest.json", inspected["files"])
        self.assertIs(inspected["manifest"]["scope"]["actions_reexecuted"], False)
        self.assertEqual(inspected["manifest"]["scope"]["independent_reproduction"], "NOT_ESTABLISHED")
        with zipfile.ZipFile(other) as archive:
            self.assertEqual(archive.testzip(), None)
            self.assertEqual(archive.namelist(), sorted(archive.namelist()))
            for member in archive.infolist():
                self.assertEqual(member.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(member.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(member.flag_bits, 0)
                self.assertEqual(member.external_attr, (stat.S_IFREG | 0o644) << 16)
                self.assertEqual((member.extra, member.comment), (b"", b""))

    def test_independent_standard_writer_matches_supported_archive_grammar(self):
        raw = standard_zip(self.members.items())
        self.assertEqual(raw, self.raw)
        self.assertEqual(inspect_archive(self.specimen(raw), sha256(raw))["files"], self.payload)

    def test_external_digest_is_mandatory_and_checked_before_zip_parsing(self):
        malformed = self.specimen(b"this is not a ZIP")
        for digest in (None, "", True, "0" * 63, "A" * 64):
            with self.subTest(digest=digest), self.assertRaises(KitError):
                inspect_archive(malformed, digest)
        with patch("incident_recheck.archive._parse_zip", side_effect=AssertionError("Parsed unauthenticated bytes")):
            with self.assertRaisesRegex(KitError, "externally supplied"):
                inspect_archive(malformed, "0" * 64)
        with self.assertRaises(KitError):
            inspect_archive(malformed, sha256(malformed.read_bytes()))

    def test_build_requires_exact_inventory_owned_bytes_and_size_bounds(self):
        first = next(iter(self.payload))
        missing, extra, mutable, oversized = (dict(self.payload) for _ in range(4))
        missing.pop(first)
        extra["evidence/unexpected.txt"] = b"not allowlisted"
        mutable[first] = bytearray(self.payload[first])
        oversized[first] = b"x" * (MAX_MEMBER + 1)
        aggregate = dict(self.payload)
        large = b"x" * MAX_MEMBER
        for name in list(aggregate)[:3]:
            aggregate[name] = large
        for label, payload in (("missing", missing), ("extra", extra), ("mutable", mutable),
                               ("member_size", oversized), ("aggregate_size", aggregate)):
            destination = self.root / (label + ".zip")
            with self.subTest(label=label), self.assertRaises(KitError):
                build_archive(destination, payload)
            self.assertFalse(destination.exists())

    def test_existing_destination_and_nonregular_or_symlink_input_are_rejected(self):
        existing = self.specimen(b"do not replace", "existing.zip")
        with self.assertRaises(KitError):
            build_archive(existing, self.payload)
        self.assertEqual(existing.read_bytes(), b"do not replace")
        alias = self.root / "alias.zip"
        alias.symlink_to(self.reference_path)
        with self.assertRaises(KitError):
            build_archive(alias, self.payload)
        with self.assertRaises(KitError):
            inspect_archive(alias, self.built["archive_sha256"])
        with self.assertRaises(KitError):
            inspect_archive(self.root, "0" * 64)
        if hasattr(os, "mkfifo"):
            fifo = self.root / "fifo.zip"
            os.mkfifo(fifo, 0o600)
            with self.assertRaises(KitError):
                inspect_archive(fifo, "0" * 64)
        large = self.root / "large.zip"
        with large.open("wb") as stream:
            stream.truncate(MAX_ARCHIVE + 1)
        with self.assertRaises(KitError):
            inspect_archive(large, "0" * 64)

    def test_member_crc_is_verified_even_with_a_matching_external_archive_hash(self):
        position = self.first.header_offset + 30 + len(self.first.filename.encode("ascii")) + len(self.first.extra)
        changed = bytearray(self.raw)
        changed[position] ^= 1
        with self.assertRaisesRegex(KitError, "CRC"):
            raw = bytes(changed)
            inspect_archive(self.specimen(raw), sha256(raw))

    def test_manifest_schema_digest_length_and_encoding_are_exact(self):
        original = json.loads(self.members["manifest.json"])
        variants = []
        bad_hash = deepcopy(original)
        bad_hash["entries"][0]["sha256"] = "0" * 64
        variants.append(json_bytes(bad_hash))
        bad_length = deepcopy(original)
        bad_length["entries"][0]["byte_length"] = True
        variants.append(json_bytes(bad_length))
        numeric_boolean = deepcopy(original)
        numeric_boolean["scope"]["actions_reexecuted"] = 0
        variants.append(json_bytes(numeric_boolean))
        extra = deepcopy(original)
        extra["unreviewed"] = "extra field"
        variants.append(json_bytes(extra))
        variants.append(json.dumps(original, indent=2).encode())
        variants.append(b'{"format":"first","format":"second"}')
        for index, manifest in enumerate(variants):
            with self.subTest(index=index):
                members = {**self.members, "manifest.json": manifest}
                self.assert_rejected(standard_zip(members.items()))

    def test_unsafe_duplicate_and_casefold_colliding_member_names_are_rejected(self):
        specimens = [
            [("same", b"a"), ("same", b"b")],
            [("same", b"a"), ("SAME", b"b")],
        ]
        for name in ("../escape", "/absolute", "C:/drive", "a\\b", "a//b", "./dot", "a/../b", "directory/", "nonascii-\u00e9"):
            specimens.append([(name, b"synthetic")])
        for index, members in enumerate(specimens):
            with self.subTest(index=index):
                self.assert_rejected(standard_zip(members))
        nul_name = bytearray(self.raw)
        nul_name[self.central_offset + 46] = 0
        self.assert_rejected(bytes(nul_name))

    def test_narrow_zip_rejects_flags_metadata_compression_overlap_and_trailing_data(self):
        central, ending = self.central_offset, len(self.raw) - 22
        second_central = central + 46 + len(self.first.filename.encode("ascii"))
        specimens = {
            "trailing": self.raw + b"trailing bytes",
            "leading": b"unreferenced prefix" + self.raw,
            "encryption": patched(self.raw, central + 8, "<H", 1),
            "descriptor": patched(self.raw, central + 8, "<H", 8),
            "compression": patched(self.raw, central + 10, "<H", 8),
            "zip64_version": patched(self.raw, central + 6, "<H", 45),
            "symlink_mode": patched(self.raw, central + 38, "<I", (stat.S_IFLNK | 0o777) << 16),
            "extra_field": patched(self.raw, central + 30, "<H", 1),
            "entry_comment": patched(self.raw, central + 32, "<H", 1),
            "timestamp": patched(self.raw, central + 14, "<H", 34),
            "local_mismatch": patched(self.raw, 14, "<I", self.first.CRC ^ 0xFFFFFFFF),
            "gap": patched(self.raw, central + 42, "<I", 1),
            "overlap": patched(self.raw, second_central + 42, "<I", 0),
            "multidisk": patched(self.raw, ending + 4, "<H", 1),
        }
        for name, raw in specimens.items():
            with self.subTest(name=name):
                self.assert_rejected(raw)

    def test_declared_member_count_size_central_and_aggregate_limits_are_enforced(self):
        central, ending = self.central_offset, len(self.raw) - 22
        counts = patched(patched(self.raw, ending + 8, "<H", MAX_MEMBERS + 1), ending + 10, "<H", MAX_MEMBERS + 1)
        sizes = patched(patched(self.raw, central + 20, "<I", MAX_MEMBER + 1), central + 24, "<I", MAX_MEMBER + 1)
        central_size = patched(self.raw, ending + 12, "<I", MAX_CENTRAL + 1)
        for name, raw in (("member_count", counts), ("member_size", sizes), ("central_size", central_size)):
            with self.subTest(name=name):
                self.assert_rejected(raw)
        members = dict(self.members)
        large = b"x" * MAX_MEMBER
        for name in list(self.payload)[:3]:
            members[name] = large
        raw = standard_zip(members.items())
        self.assertLessEqual(len(raw), MAX_ARCHIVE)
        self.assert_rejected(raw)


if __name__ == "__main__":
    unittest.main()
