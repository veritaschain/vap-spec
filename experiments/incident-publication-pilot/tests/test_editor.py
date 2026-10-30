"""Real signed local transitions and static HTML checks; no AI detector/model."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import os
import unittest
from unittest.mock import patch

from publication_pilot.editor import Editor, disclosure_text, render_html, verify_snapshot
from publication_pilot.protocol import MAX_HTML, InputError, digest, public_key, sha256_bytes, sign_message


class _Clock:
    def __init__(self):
        self.current = datetime(2026, 10, 30, 10, 0, tzinfo=timezone.utc)

    def __call__(self):
        value = self.current.isoformat().replace("+00:00", "Z")
        self.current += timedelta(seconds=1)
        return value


class _RenderedText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags, self.blocks, self.disclosures, self.styles = [], [], [], []
        self.active, self.text = None, []
        self.in_style = False

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))
        if tag == "style":
            self.in_style = True
        if tag == "p" and dict(attrs).get("class") in {"block-text", "disclosure-text"}:
            self.active, self.text = dict(attrs)["class"], []

    def handle_data(self, data):
        if self.active:
            self.text.append(data)
        if self.in_style:
            self.styles.append(data)

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False
        if tag == "p" and self.active:
            destination = self.blocks if self.active == "block-text" else self.disclosures
            destination.append("".join(self.text))
            self.active, self.text = None, []


class EditorTests(unittest.TestCase):
    def setUp(self):
        self.secret = os.urandom(32).hex()
        self.public = public_key(self.secret)
        self.key_id = "collector-key"
        self.clock = _Clock()
        self.editor = Editor("document-example", self.secret, self.key_id, clock=self.clock)

    def _verify(self, snapshot=None):
        return verify_snapshot(self.editor.snapshot() if snapshot is None else snapshot, self.public, self.key_id)

    def _sign_body(self, envelope, **changes):
        body = deepcopy(envelope["body"])
        body.update(changes)
        return sign_message(body, self.secret, self.key_id)

    def test_replay_measures_ordered_state_and_only_final_adoption(self):
        self.editor.set_block("intro", "Imported initial text.")
        self.editor.set_block("body", "Simulated generated text.", "generation")
        self.editor.set_block("intro", "Simulated proofread intro.", "proofreading")
        snapshot = self.editor.snapshot()
        view = self._verify(snapshot)
        self.assertEqual(set(view), {"document_id", "revision_id", "blocks", "observed_activities", "adopted", "source_sha256", "lineage_sha256", "observed_at"})
        self.assertEqual([block["block_id"] for block in view["blocks"]], ["intro", "body"])
        self.assertEqual(view["observed_activities"], ["generation", "proofreading"])
        self.assertEqual([a["block_id"] for a in view["adopted"]], ["intro", "body"])
        self.assertEqual(view["source_sha256"], digest({"document_id": "document-example", "blocks": view["blocks"]}))
        self.assertEqual(view["lineage_sha256"], digest(snapshot))
        for adopted, block in zip(view["adopted"], view["blocks"]):
            self.assertEqual(adopted["sha256"], sha256_bytes(block["text"].encode("utf-8")))

    def test_manual_or_import_replacement_retains_history_without_false_adoption(self):
        for replacement in ["manual_edit", "import"]:
            with self.subTest(replacement=replacement):
                editor = Editor("same-bytes", self.secret, self.key_id, clock=_Clock())
                editor.set_block("body", "Identical output.", "generation")
                editor.set_block("body", "Identical output.", replacement)
                snapshot = editor.snapshot()
                self.assertEqual(len(snapshot["operations"]), 2)
                second = snapshot["operations"][1]["body"]
                self.assertEqual(second["before_sha256"], second["after_sha256"])
                view = verify_snapshot(snapshot, self.public, self.key_id)
                self.assertEqual(view["observed_activities"], ["generation"])
                self.assertEqual(view["adopted"], [])

    def test_last_simulated_write_adopts_only_its_current_bytes(self):
        self.editor.set_block("body", "Earlier generated text.", "generation")
        self.editor.set_block("body", "Locally revised text.", "manual_edit")
        self.editor.set_block("body", "Final simulated translation.", "translation")
        view = self._verify()
        self.assertEqual(view["observed_activities"], ["generation", "translation"])
        self.assertEqual(len(view["adopted"]), 1)
        self.assertEqual(view["adopted"][0]["activity"], "translation")
        self.assertEqual(view["adopted"][0]["sha256"], sha256_bytes(b"Final simulated translation."))

    def test_unsigned_tampering_reordering_and_truncation_are_rejected(self):
        self.editor.set_block("body", "Original.", "generation")
        self.editor.set_block("body", "Revised.", "manual_edit")
        snapshot = self.editor.snapshot()
        candidates = []
        tampered = deepcopy(snapshot)
        tampered["operations"][0]["body"]["text"] = "Different."
        candidates.append(tampered)
        reordered = deepcopy(snapshot)
        reordered["operations"].reverse()
        candidates.append(reordered)
        truncated = deepcopy(snapshot)
        truncated["operations"].pop()
        candidates.append(truncated)
        checkpoint = deepcopy(snapshot)
        checkpoint["checkpoint"]["body"]["document"]["blocks"][0]["text"] = "Unrecorded."
        candidates.append(checkpoint)
        fabricated = deepcopy(snapshot)
        fabricated["adopted"] = [{"activity": "generation"}]
        candidates.append(fabricated)
        for candidate in candidates:
            with self.assertRaises(InputError):
                self._verify(candidate)

    def test_valid_signatures_do_not_cure_false_transitions_or_checkpoint(self):
        self.editor.set_block("body", "Original.", "generation")
        snapshot = self.editor.snapshot()
        changes = [
            {"text": "Changed without a new state hash."}, {"before_sha256": "0" * 64},
            {"after_sha256": "0" * 64}, {"previous_sha256": "1" * 64},
            {"sequence": 2}, {"sequence": True}, {"document_id": "different-document"},
        ]
        for update in changes:
            candidate = deepcopy(snapshot)
            candidate["operations"][0] = self._sign_body(candidate["operations"][0], **update)
            with self.subTest(update=list(update)), self.assertRaises(InputError):
                self._verify(candidate)
        for update in [{"chain_head_sha256": "0" * 64}, {"sequence": 2},
                       {"document": {"document_id": "document-example", "blocks": [{"block_id": "body", "text": "Unobserved replacement."}]}}]:
            candidate = deepcopy(snapshot)
            candidate["checkpoint"] = self._sign_body(candidate["checkpoint"], **update)
            with self.assertRaises(InputError):
                self._verify(candidate)

    def test_trusted_key_and_document_identity_are_required(self):
        self.editor.set_block("body", "Text.")
        snapshot = self.editor.snapshot()
        with self.assertRaises(InputError):
            verify_snapshot(snapshot, public_key(os.urandom(32).hex()), self.key_id)
        with self.assertRaises(InputError):
            verify_snapshot(snapshot, self.public, "another-key")
        snapshot["document_id"] = "another-document"
        with self.assertRaises(InputError):
            self._verify(snapshot)

    def test_clock_regression_and_retrograde_checkpoint_are_rejected(self):
        values = iter(["2026-10-30T10:00:00Z", "2026-10-30T09:59:59Z", "2026-10-30T10:00:01Z"])
        editor = Editor("clock-example", self.secret, self.key_id, clock=lambda: next(values))
        editor.set_block("body", "Kept.")
        with self.assertRaises(InputError):
            editor.set_block("body", "Must not persist.")
        snapshot = editor.snapshot()
        view = verify_snapshot(snapshot, self.public, self.key_id)
        self.assertEqual(view["blocks"][0]["text"], "Kept.")
        self.assertEqual(len(snapshot["operations"]), 1)
        snapshot["checkpoint"] = self._sign_body(snapshot["checkpoint"], observed_at="2026-10-30T09:59:59Z")
        with self.assertRaises(InputError):
            verify_snapshot(snapshot, self.public, self.key_id)

    def test_returned_objects_do_not_mutate_editor_state(self):
        returned = self.editor.set_block("body", "Kept.", "generation")
        returned["body"]["text"] = "Caller mutation."
        snapshot = self.editor.snapshot()
        snapshot["checkpoint"]["body"]["document"]["blocks"][0]["text"] = "More mutation."
        self.assertEqual(self._verify()["blocks"][0]["text"], "Kept.")

    def test_nonempty_document_character_block_and_operation_limits(self):
        with self.assertRaises(InputError):
            self.editor.snapshot()
        self.editor.set_block("block0", "x" * 8192)
        with self.assertRaises(InputError):
            self.editor.set_block("block0", "x" * 8193)
        for number in range(1, 16):
            self.editor.set_block("block" + str(number), "Text.")
        with self.assertRaises(InputError):
            self.editor.set_block("block16", "Excess.")
        for number in range(48):
            self.editor.set_block("block1", "Replacement " + str(number), "manual_edit")
        with self.assertRaises(InputError):
            self.editor.set_block("block1", "Operation 65.")
        snapshot = self.editor.snapshot()
        self.assertEqual((len(snapshot["operations"]), len(self._verify(snapshot)["blocks"])), (64, 16))
        snapshot["operations"].append(deepcopy(snapshot["operations"][-1]))
        with self.assertRaises(InputError):
            self._verify(snapshot)

    def test_json_budget_rejects_before_committing_a_replacement(self):
        with patch("publication_pilot.editor.MAX_JSON", 4096), self.assertRaises(InputError):
            self.editor.set_block("body", "Bounded.")
        with self.assertRaises(InputError):
            self.editor.snapshot()
        self.editor.set_block("body", "Now accepted.")
        self.assertEqual(len(self.editor.snapshot()["operations"]), 1)

    def test_plain_text_and_disclosure_strict_inputs(self):
        for value in [None, b"bytes", "bad\x00text", "bad\x7ftext", "bad\ud800text"]:
            with self.assertRaises(InputError):
                self.editor.set_block("body", value)
        for block_id in ["../escape", "x\"onclick", "", "x" * 65]:
            with self.assertRaises(InputError):
                self.editor.set_block(block_id, "Text.")
        valid = {"activities": [], "scope": "recorded_local_session_only"}
        notice = disclosure_text(valid)
        self.assertIn("none declared", notice)
        self.assertIn("origin", notice)
        self.assertIn("unknown", notice)
        self.assertIn("does not establish human-only authorship", notice)
        self.assertIn("Synthetic", notice)
        for value in [
            {"activities": ["generation", "generation"], "scope": valid["scope"]},
            {"activities": ["translation", "generation"], "scope": valid["scope"]},
            {"activities": ["manual_edit"], "scope": valid["scope"]},
            {"activities": [True], "scope": valid["scope"]},
            {"activities": [], "scope": "all_activity"},
            {**valid, "verified": True},
        ]:
            with self.assertRaises(InputError):
                disclosure_text(value)

    def test_render_escapes_supplied_markup_and_displays_exact_disclosure(self):
        text = '日本語 😀 & <b>text</b>\r\n</p><script src="https://example.invalid/x">alert(1)</script><img src=x onerror=alert(2)>\t"quote"'
        self.editor.set_block("body", text, "generation")
        view = self._verify()
        disclosure = {"activities": ["generation"], "scope": "recorded_local_session_only"}
        rendered = render_html(view, disclosure)
        parsed = _RenderedText()
        parsed.feed(rendered.decode("utf-8"))
        self.assertEqual(parsed.blocks, [text])
        self.assertEqual(parsed.disclosures, [disclosure_text(disclosure)])
        self.assertFalse({tag for tag, attrs in parsed.tags} & {"script", "img", "iframe", "form", "link", "a"})
        self.assertFalse(any("src" in attrs or "href" in attrs or "hidden" in attrs for tag, attrs in parsed.tags))
        self.assertTrue(any(tag == "section" and attrs.get("id") == "ai-use-disclosure" for tag, attrs in parsed.tags))
        self.assertNotIn("display:none", "".join(parsed.styles))
        self.assertNotIn("visibility:hidden", "".join(parsed.styles))
        self.assertLessEqual(len(rendered), MAX_HTML)

    def test_render_is_deterministic_and_omits_checkpoint_time_and_self_hash(self):
        self.editor.set_block("body", "Stable text.")
        first = self._verify()
        second = self._verify()
        self.assertNotEqual(first["observed_at"], second["observed_at"])
        self.assertNotEqual(first["lineage_sha256"], second["lineage_sha256"])
        disclosure = {"activities": [], "scope": "recorded_local_session_only"}
        rendered = render_html(first, disclosure)
        self.assertEqual(rendered, render_html(second, disclosure))
        self.assertNotIn(first["observed_at"].encode(), rendered)
        self.assertNotIn(first["lineage_sha256"].encode(), rendered)
        self.assertNotIn(sha256_bytes(rendered).encode(), rendered)
        with patch("publication_pilot.editor.MAX_HTML", 20), self.assertRaises(InputError):
            render_html(first, disclosure)

    def test_renderer_rejects_mismatched_measured_view_and_false_adoption(self):
        self.editor.set_block("body", "Recorded text.", "generation")
        view = self._verify()
        disclosure = {"activities": ["generation"], "scope": "recorded_local_session_only"}
        changed = deepcopy(view)
        changed["blocks"][0]["text"] = "Unmeasured content."
        with self.assertRaises(InputError):
            render_html(changed, disclosure)
        changed = deepcopy(view)
        changed["adopted"][0]["sha256"] = "0" * 64
        with self.assertRaises(InputError):
            render_html(changed, disclosure)
        changed = deepcopy(view)
        changed["adopted"][0]["activity"] = "translation"
        with self.assertRaises(InputError):
            render_html(changed, disclosure)


if __name__ == "__main__":
    unittest.main()
