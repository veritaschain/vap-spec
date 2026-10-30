"""Bounded deterministic rendering and exclusive report-file publication."""

from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import html
from io import BytesIO
import os
from pathlib import Path
import re
import stat
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from incident_review import delivery
from incident_review.common import ReviewError, json_bytes, sha256, strict_json
from incident_review.projection import NOTE_TEXT
from test_support import report_fixture


def _reverse_maps(value):
    if type(value) is dict:
        return {key: _reverse_maps(value[key]) for key in reversed(value)}
    if type(value) is list:
        return [_reverse_maps(item) for item in value]
    return value


def _references(value):
    if type(value) is dict:
        if set(value) == {"file", "sha256", "pointer"}:
            yield value["file"], value["sha256"], value["pointer"]
        for item in value.values():
            yield from _references(item)
    elif type(value) is list:
        for item in value:
            yield from _references(item)


class DeliveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = report_fixture()
        cls.members = delivery.render_members(cls.report)
        cls.bundle = delivery.bundle_bytes(cls.report)

    def test_deterministic_bilingual_rendering_binds_the_authoritative_json(self):
        self.assertEqual(delivery.render_members(_reverse_maps(self.report)), self.members)
        self.assertEqual(delivery.bundle_bytes(deepcopy(self.report)), self.bundle)
        self.assertEqual(set(self.members), set(delivery.MEMBERS))
        self.assertEqual(self.members["review.json"], json_bytes(self.report))
        measured = sha256(self.members["review.json"])
        for language in ("en", "ja"):
            text = self.members["review-" + language + ".md"].decode("utf-8")
            self.assertIn(measured, text)
            self.assertIn(delivery._LABELS[language]["headline"], text)
            self.assertIn(delivery._LABELS[language]["intro"], text)
            self.assertLess(text.index(delivery._LABELS[language]["scope"]), text.index("### UL"))
            counts = [text.index("| " + pilot + " |") for pilot in ("upload", "publication", "erasure")]
            self.assertEqual(counts, sorted(counts))
            self.assertNotIn("```", text)
            self.assertNotIn("<script", text)

    def test_fixed_zip_metadata_and_hash_manifest(self):
        with zipfile.ZipFile(BytesIO(self.bundle)) as archive:
            self.assertEqual(archive.namelist(), sorted(delivery.MEMBERS))
            self.assertEqual(archive.comment, b"")
            for item in archive.infolist():
                self.assertEqual(item.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(item.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(item.create_system, 3)
                self.assertEqual(item.flag_bits, 0)
                self.assertEqual(item.extra, b"")
                self.assertEqual(item.comment, b"")
                self.assertTrue(stat.S_ISREG(item.external_attr >> 16))
                self.assertEqual(stat.S_IMODE(item.external_attr >> 16), 0o644)
                self.assertEqual(archive.read(item.filename), self.members[item.filename])
        manifest = strict_json(self.members["manifest.json"])
        self.assertEqual(set(manifest), {"format", "entries"})
        self.assertEqual(manifest["format"], "incident-review-bundle/0.1")
        self.assertEqual([entry["path"] for entry in manifest["entries"]], ["review-en.md", "review-ja.md", "review.json"])
        for entry in manifest["entries"]:
            self.assertEqual(entry, {"path": entry["path"], "sha256": sha256(self.members[entry["path"]]),
                                     "byte_length": len(self.members[entry["path"]])})

    def test_every_case_section_core_frame_and_reference_is_rendered(self):
        expected_refs = set(_references(self.report))
        expected_refs.update((source["file"], source["sha256"], source["pointer"] + "/states")
                             for case in self.report["cases"] for source in [case["expectation"]["actual"]["source"]])
        for language in ("en", "ja"):
            text = self.members["review-" + language + ".md"].decode("utf-8")
            decoded = html.unescape(text)
            expected_frames = sum(len(case["frames"]) for case in self.report["cases"])
            prefix = "##### " + delivery._LABELS[language]["operation"] + " "
            self.assertEqual(sum(line.startswith(prefix) for line in decoded.splitlines()), expected_frames)
            for case in self.report["cases"]:
                heading = "### " + case["case_id"] + " — " + case["title"]["value"]
                self.assertIn(heading, decoded)
                segment = decoded.split(heading, 1)[1].split("\n### ", 1)[0]
                for section in case["sections"]:
                    self.assertIn("##### " + section["key"] + " — ", segment)
                    for fact in section["facts"]:
                        self.assertIn(html.unescape(delivery._value(fact["value"])), segment)
                for frame in case["frames"]:
                    self.assertIn(frame["availability"], segment)
                    if frame["availability"] == "RECORDED":
                        for name, value in frame["assessments"]["value"].items():
                            self.assertIn(name, segment)
                            self.assertIn(html.unescape(delivery._value(value)), segment)
                    else:
                        self.assertIn(frame["absence_reason"], segment)
                for note in case["notes"]:
                    self.assertIn(note["code"], segment)
                    self.assertIn(NOTE_TEXT[note["code"]][language], segment)
            seen, files, pointers = set(), {}, []
            for line in text.splitlines():
                match = re.fullmatch(r"\| \[(F[0-9]+)\]\(([^)]+)\) \| (.*?) \| ([0-9a-f]{64}) \|", line)
                if match:
                    name, url, file, measured = match.groups()
                    file = html.unescape(file)
                    self.assertEqual(url, delivery.CAPTURE_BASE + file.removeprefix("evidence/"))
                    files[name] = (file, measured)
                match = re.fullmatch(r"\| S[0-9]+ \| (F[0-9]+) \| (.*?) \|", line)
                if match:
                    name, pointer = match.groups()
                    pointer = html.unescape(pointer)
                    if pointer == delivery._LABELS[language]["root"]:
                        pointer = ""
                    pointers.append((name, pointer))
            for name, pointer in pointers:
                seen.add((*files[name], pointer))
            self.assertEqual(seen, expected_refs)
            self.assertEqual(len(files), len({(file, measured) for file, measured, _ in expected_refs}))

    def test_front_index_lists_all_recorded_state_arrays_without_record_pairing(self):
        for language in ("en", "ja"):
            labels = delivery._LABELS[language]
            text = html.unescape(self.members["review-" + language + ".md"].decode())
            section = text.split("## " + labels["index"] + "\n", 1)[1].split("## " + labels["metadata"] + "\n", 1)[0]
            self.assertIn(labels["index_intro"], section)
            self.assertEqual(len(re.findall(r"^\| (?:UL|LP|LE)-[0-9]{2} \(S[0-9]+\)", section, re.MULTILINE)), 53)
            for case in self.report["cases"]:
                line = next(line for line in section.splitlines() if line.startswith("| " + case["case_id"] + " ("))
                self.assertIn(case["title"]["value"], line)
                self.assertIn(html.unescape(delivery._value(case["expectation"]["actual"]["value"]["states"])), line)
                for note in case["notes"]:
                    self.assertIn(note["code"], line)

    def test_missing_frames_and_json_null_remain_distinct_from_unknown_and_strings(self):
        report = deepcopy(self.report)
        missing = [frame for case in report["cases"] for frame in case["frames"] if frame["availability"] == "FRAME_NOT_RECORDED"]
        self.assertGreaterEqual(len(missing), 2)
        missing[0]["absence_reason"], missing[1]["absence_reason"] = "NULL_CONTAINER", "MISSING_FIELD"
        members = delivery.render_members(report)
        for language in ("en", "ja"):
            text = html.unescape(members["review-" + language + ".md"].decode())
            self.assertIn("NULL_CONTAINER", text)
            self.assertIn("MISSING_FIELD", text)
            self.assertIn(delivery._LABELS[language]["missing"], text)
        visible = [html.unescape(delivery._value(value)) for value in (None, "null", False, [], {}, "UNKNOWN")]
        self.assertEqual(visible, ["null", '"null"', "false", "[]", "{}", '"UNKNOWN"'])
        self.assertEqual(len(set(visible)), len(visible))

    def test_dynamic_markup_urls_backticks_pipes_and_newlines_are_plain_text(self):
        report = deepcopy(self.report)
        attack = '<script>alert("x")</script> | `code`\n# injected\r\t[remote](https://evil.invalid/a) ![image](javascript:evil)\u202e'
        case = report["cases"][0]
        case["title"]["value"] = attack
        case["sections"][0]["facts"][0]["name"] = attack
        case["sections"][0]["facts"][0]["value"] = attack
        case["frames"][0]["phase"] = 'phase | <img> `x`\n'
        for name, raw in delivery.render_members(report).items():
            if not name.endswith(".md"):
                continue
            text = raw.decode("utf-8")
            self.assertNotIn("<script>", text)
            self.assertNotIn("<img>", text)
            self.assertNotIn("https://evil", text)
            self.assertNotIn("javascript:evil", text)
            self.assertNotIn("\n# injected", text)
            self.assertNotIn("`", text)
            self.assertIn("&#124;", text)
            self.assertIn("&#92;n", text)
            self.assertIn("&#92;u202e", text)
            self.assertNotRegex(text, r"<[A-Za-z][^>]*>")
            links = re.findall(r"\]\(([^)]+)\)", text)
            self.assertTrue(links)
            self.assertTrue(all(link.startswith(delivery.CAPTURE_BASE) for link in links))

    def test_unsupported_references_promoted_scope_and_broken_inventory_are_rejected(self):
        for file in ("https://evil.invalid/file", "evidence/../source.py", "evidence/upload/cases/UL-99.json", []):
            with self.subTest(file=file):
                report = deepcopy(self.report)
                report["cases"][0]["capture_source"]["file"] = file
                with self.assertRaises(ReviewError):
                    delivery.render_members(report)
        for mutation in ("scope", "count", "inventory", "note", "pointer", "hash"):
            with self.subTest(mutation=mutation):
                report = deepcopy(self.report)
                if mutation == "scope":
                    report["scope"]["human_review"] = "PERFORMED"
                elif mutation == "count":
                    report["counts"]["saved_cases_rechecked"] = 53.0
                elif mutation == "inventory":
                    report["cases"].pop()
                elif mutation == "note":
                    report["cases"][0]["notes"][0]["code"] = "UNRECOGNIZED_CODE"
                elif mutation == "pointer":
                    report["cases"][0]["capture_source"]["pointer"] = "/invalid~2escape"
                else:
                    report["cases"][0]["capture_source"]["sha256"] = "F" * 64
                with self.assertRaises(ReviewError):
                    delivery.render_members(report)

    def test_member_bundle_and_owned_byte_limits_are_enforced(self):
        with patch.object(delivery, "MAX_MEMBER", len(self.members["review.json"]) - 1), self.assertRaises(ReviewError):
            delivery.render_members(self.report)
        with patch.object(delivery, "MAX_MEMBER", len(self.members["review-ja.md"]) - 1), self.assertRaises(ReviewError):
            delivery.render_members(self.report)
        with patch.object(delivery, "MAX_BUNDLE", len(self.bundle) - 1), self.assertRaises(ReviewError):
            delivery.bundle_bytes(self.report)
        for raw in (bytearray(b"not-owned-bytes"), "text", b"", b"x" * (delivery.MAX_BUNDLE + 1)):
            with self.subTest(type=type(raw).__name__), self.assertRaises(ReviewError):
                delivery.publish_bundle("unused-report.zip", raw)

    def test_publication_fsync_precedes_exclusive_link_and_temp_name_is_removed(self):
        with tempfile.TemporaryDirectory(prefix="review-delivery-") as directory:
            path = Path(directory) / "review.zip"
            events = []
            real_fsync, real_link = os.fsync, os.link

            def sync(descriptor):
                events.append("fsync")
                self.assertEqual(os.fstat(descriptor).st_size, len(self.bundle))
                return real_fsync(descriptor)

            def link(*args, **kwargs):
                events.append("link")
                self.assertEqual(events, ["fsync", "link"])
                return real_link(*args, **kwargs)

            with patch.object(delivery.os, "fsync", side_effect=sync), patch.object(delivery.os, "link", side_effect=link):
                delivery.publish_bundle(path, self.bundle)
            self.assertEqual(delivery.read_bundle(path, sha256(self.bundle)), self.bundle)
            self.assertEqual(path.stat().st_nlink, 1)
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["review.zip"])

    def test_existing_files_directories_and_symlinks_are_never_overwritten(self):
        for kind in ("file", "directory", "symlink", "dangling-symlink"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory(prefix="review-existing-") as directory:
                parent, path = Path(directory), Path(directory) / "report.zip"
                if kind == "file":
                    path.write_bytes(b"existing-owner")
                elif kind == "directory":
                    path.mkdir()
                    (path / "sentinel").write_bytes(b"existing-owner")
                elif kind == "symlink":
                    (parent / "target").write_bytes(b"existing-owner")
                    path.symlink_to("target")
                else:
                    path.symlink_to("missing-target")
                inventory = sorted(p.name for p in parent.iterdir())
                with self.assertRaises(ReviewError):
                    delivery.publish_bundle(path, b"new-complete-report")
                self.assertEqual(sorted(p.name for p in parent.iterdir()), inventory)
                if kind == "file":
                    self.assertEqual(path.read_bytes(), b"existing-owner")
                elif kind == "directory":
                    self.assertEqual((path / "sentinel").read_bytes(), b"existing-owner")
                else:
                    self.assertEqual(os.readlink(path), "target" if kind == "symlink" else "missing-target")

    def test_destination_race_and_concurrent_calls_do_not_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="review-race-") as directory:
            path = Path(directory) / "report.zip"
            real_link = os.link

            def raced_link(*args, **kwargs):
                path.write_bytes(b"racing-owner")
                return real_link(*args, **kwargs)

            with patch.object(delivery.os, "link", side_effect=raced_link), self.assertRaises(ReviewError):
                delivery.publish_bundle(path, b"would-be-report")
            self.assertEqual(path.read_bytes(), b"racing-owner")
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["report.zip"])
        with tempfile.TemporaryDirectory(prefix="review-concurrent-") as directory:
            path = Path(directory) / "report.zip"
            variants = (b"complete report A", b"complete report B")

            def publish(raw):
                try:
                    delivery.publish_bundle(path, raw)
                    return "published"
                except ReviewError:
                    return "refused"

            with ThreadPoolExecutor(max_workers=2) as executor:
                self.assertEqual(sorted(executor.map(publish, variants)), ["published", "refused"])
            self.assertIn(path.read_bytes(), variants)
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["report.zip"])

    def test_prelink_failures_leave_no_final_or_temporary_file_and_short_writes_complete(self):
        for operation in ("write", "fsync", "link"):
            with self.subTest(operation=operation), tempfile.TemporaryDirectory(prefix="review-fault-") as directory:
                path = Path(directory) / "report.zip"
                with patch.object(delivery.os, operation, side_effect=OSError("injected pre-link failure")), self.assertRaises(ReviewError):
                    delivery.publish_bundle(path, b"complete report bytes")
                self.assertEqual(list(Path(directory).iterdir()), [])
        with tempfile.TemporaryDirectory(prefix="review-short-write-") as directory:
            path = Path(directory) / "report.zip"
            real_write = os.write
            with patch.object(delivery.os, "write", side_effect=lambda fd, raw: real_write(fd, raw[:3])):
                delivery.publish_bundle(path, b"all bytes despite partial writes")
            self.assertEqual(path.read_bytes(), b"all bytes despite partial writes")

    def test_failure_after_link_does_not_claim_rollback_or_remove_final_output(self):
        with tempfile.TemporaryDirectory(prefix="review-post-link-") as directory:
            path = Path(directory) / "report.zip"
            real_stat = os.stat

            def failed_readback(name, *args, **kwargs):
                if name == path.name and os.path.lexists(path):
                    raise OSError("injected readback failure after link")
                return real_stat(name, *args, **kwargs)

            with patch.object(delivery.os, "stat", side_effect=failed_readback), self.assertRaisesRegex(ReviewError, "may remain"):
                delivery.publish_bundle(path, b"complete linked report")
            self.assertEqual(path.read_bytes(), b"complete linked report")
            self.assertEqual([p.name for p in Path(directory).iterdir()], ["report.zip"])

    def test_read_bundle_is_bounded_regular_hash_checked_capture_not_zip_parsing(self):
        with tempfile.TemporaryDirectory(prefix="review-read-") as directory:
            parent, path = Path(directory), Path(directory) / "bytes"
            raw = b"not a ZIP; this API only captures owned bytes"
            path.write_bytes(raw)
            self.assertEqual(delivery.read_bundle(path, sha256(raw)), raw)
            for expected in (None, "", "0" * 64):
                with self.subTest(expected=expected), self.assertRaises(ReviewError):
                    delivery.read_bundle(path, expected)
            (parent / "link").symlink_to(path)
            (parent / "directory").mkdir()
            os.mkfifo(parent / "fifo")
            for name in ("link", "directory", "fifo"):
                with self.subTest(name=name), self.assertRaises(ReviewError):
                    delivery.read_bundle(parent / name, sha256(raw))
            with path.open("wb") as handle:
                handle.truncate(delivery.MAX_BUNDLE + 1)
            with self.assertRaises(ReviewError):
                delivery.read_bundle(path, sha256(raw))

    def test_read_bundle_refuses_a_file_changed_during_capture(self):
        with tempfile.TemporaryDirectory(prefix="review-read-race-") as directory:
            path = Path(directory) / "report.zip"
            raw = b"original report bytes"
            path.write_bytes(raw)
            real_read, changed = os.read, []

            def changed_read(*args):
                result = real_read(*args)
                if not changed:
                    changed.append(True)
                    path.write_bytes(b"changed report bytes!")
                return result

            with patch.object(delivery.os, "read", side_effect=changed_read), self.assertRaises(ReviewError):
                delivery.read_bundle(path, sha256(raw))


if __name__ == "__main__":
    unittest.main()
