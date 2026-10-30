"""Observed local text replacements and a deterministic synthetic review artifact.

AI labels describe simulated adapter operations. Neither imports nor manual
edits establish human-only origin. The collector is a configured trust assumption,
not an independent witness or a detector of AI-generated text.
"""

from copy import deepcopy
from html import escape
import re
from threading import RLock

from .protocol import (MAX_HTML, MAX_JSON, InputError, canonical, decode_json, digest,
                       identifier, public_key, sha256_bytes, sign_message, timestamp,
                       utc_now, verify_message)

FORMAT = "publication-editor-snapshot/0.1"
MAX_OPERATIONS = 64
MAX_BLOCKS = 16
MAX_BLOCK_CHARACTERS = 8192
GENESIS = "0" * 64
AI_ACTIVITIES = {"generation", "substantive_editing", "proofreading", "translation"}
ACTIVITIES = AI_ACTIVITIES | {"import", "manual_edit"}
VIEW_FIELDS = {"document_id", "revision_id", "blocks", "observed_activities", "adopted", "source_sha256", "lineage_sha256", "observed_at"}
OP_FIELDS = {"kind", "document_id", "sequence", "previous_sha256", "before_sha256", "after_sha256",
             "block_id", "text", "activity", "observed_at"}
CHECKPOINT_FIELDS = {"kind", "document_id", "sequence", "chain_head_sha256", "document", "observed_at"}


def _exact(value, fields):
    if type(value) is not dict or set(value) != fields:
        raise InputError("Unexpected editor object fields")


def _hex(value, size=64):
    if type(value) is not str or not re.fullmatch(r"[0-9a-f]{%d}" % size, value):
        raise InputError("Invalid editor digest or signature encoding")


def _key_id(value):
    if type(value) is not str or not value.strip() or len(value) > 256:
        raise InputError("Expected a bounded collector key identifier")


def _text(value):
    if type(value) is not str or len(value) > MAX_BLOCK_CHARACTERS:
        raise InputError("Block text exceeds the supported character limit")
    try:
        value.encode("utf-8")
    except UnicodeError as exc:
        raise InputError("Block text must be valid UTF-8 text") from exc
    if any((ord(c) < 32 and c not in "\r\n\t") or ord(c) == 127 for c in value):
        raise InputError("Unsupported control character in plain text")


def _sequence(value):
    if type(value) is not int or not 1 <= value <= MAX_OPERATIONS:
        raise InputError("Invalid editor operation sequence")


def _activities(value):
    if (type(value) is not list or any(type(item) is not str or item not in AI_ACTIVITIES for item in value)
            or value != sorted(set(value))):
        raise InputError("AI activities must be sorted, unique supported labels")


def _document(document, *, allow_empty=False):
    _exact(document, {"document_id", "blocks"})
    identifier(document["document_id"])
    blocks = document["blocks"]
    if type(blocks) is not list or len(blocks) > MAX_BLOCKS or (not allow_empty and not blocks):
        raise InputError("A document requires between 1 and 16 ordered blocks")
    seen = set()
    for block in blocks:
        _exact(block, {"block_id", "text"})
        identifier(block["block_id"])
        _text(block["text"])
        if block["block_id"] in seen:
            raise InputError("Duplicate block identifier")
        seen.add(block["block_id"])


def _operation_shape(body):
    _exact(body, OP_FIELDS)
    if body["kind"] != "editor_operation":
        raise InputError("Unexpected editor operation kind")
    identifier(body["document_id"])
    identifier(body["block_id"])
    _sequence(body["sequence"])
    for field in ("previous_sha256", "before_sha256", "after_sha256"):
        _hex(body[field])
    _text(body["text"])
    if type(body["activity"]) is not str or body["activity"] not in ACTIVITIES:
        raise InputError("Unsupported local activity")
    timestamp(body["observed_at"])


def _checkpoint_shape(body):
    _exact(body, CHECKPOINT_FIELDS)
    if body["kind"] != "editor_checkpoint":
        raise InputError("Unexpected editor checkpoint kind")
    identifier(body["document_id"])
    _sequence(body["sequence"])
    _hex(body["chain_head_sha256"])
    _document(body["document"])
    timestamp(body["observed_at"])


def _envelope_shape(envelope, shape):
    _exact(envelope, {"algorithm", "key_id", "body", "signature"})
    if envelope["algorithm"] != "Ed25519":
        raise InputError("Unsupported editor signature algorithm")
    _key_id(envelope["key_id"])
    _hex(envelope["signature"], 128)
    shape(envelope["body"])


def _state(document_id, blocks):
    return {"document_id": document_id, "blocks": [{"block_id": key, "text": value} for key, value in blocks.items()]}


def _revision(sequence, content_digest):
    # A readable revision label; the full digests carry the integrity binding.
    return "rev-" + str(sequence) + "-" + content_digest[:24]


class Editor:
    def __init__(self, document_id, collector_secret, collector_key_id, clock=utc_now):
        identifier(document_id)
        public_key(collector_secret)
        _key_id(collector_key_id)
        if not callable(clock):
            raise InputError("Editor clock must be callable")
        self._document_id = document_id
        self._secret, self._key_id, self._clock = collector_secret, collector_key_id, clock
        self._blocks, self._operations = {}, []
        self._last_time = None
        self._lock = RLock()

    def _now(self):
        observed_at = self._clock()
        parsed = timestamp(observed_at)
        if self._last_time is not None and parsed < self._last_time:
            raise InputError("Editor clock moved backwards")
        return observed_at, parsed

    def set_block(self, block_id, text, activity="import"):
        identifier(block_id)
        _text(text)
        if type(activity) is not str or activity not in ACTIVITIES:
            raise InputError("Unsupported local activity")
        with self._lock:
            if len(self._operations) >= MAX_OPERATIONS:
                raise InputError("Editor operation limit reached")
            if block_id not in self._blocks and len(self._blocks) >= MAX_BLOCKS:
                raise InputError("Editor block limit reached")
            observed_at, parsed = self._now()
            before = _state(self._document_id, self._blocks)
            replacement = dict(self._blocks)
            replacement[block_id] = text
            after = _state(self._document_id, replacement)
            body = {
                "kind": "editor_operation", "document_id": self._document_id,
                "sequence": len(self._operations) + 1,
                "previous_sha256": digest(self._operations[-1]) if self._operations else GENESIS,
                "before_sha256": digest(before), "after_sha256": digest(after),
                "block_id": block_id, "text": text, "activity": activity,
                "observed_at": observed_at,
            }
            envelope = sign_message(body, self._secret, self._key_id)
            prospective = [*self._operations, envelope]
            # Reserve space for the separately signed final checkpoint envelope.
            if len(canonical({"operations": prospective, "document": after})) > MAX_JSON - 4096:
                raise InputError("Editor snapshot exceeds the bounded JSON budget")
            self._blocks, self._operations, self._last_time = replacement, prospective, parsed
            return deepcopy(envelope)

    def snapshot(self):
        with self._lock:
            if not self._blocks:
                raise InputError("Cannot checkpoint an empty document")
            observed_at, parsed = self._now()
            body = {
                "kind": "editor_checkpoint", "document_id": self._document_id,
                "sequence": len(self._operations), "chain_head_sha256": digest(self._operations[-1]),
                "document": _state(self._document_id, self._blocks), "observed_at": observed_at,
            }
            result = {
                "format": FORMAT, "document_id": self._document_id,
                "operations": deepcopy(self._operations),
                "checkpoint": sign_message(body, self._secret, self._key_id),
            }
            if len(canonical(result)) > MAX_JSON:
                raise InputError("Editor snapshot exceeds the bounded JSON budget")
            self._last_time = parsed
            return result


def verify_snapshot(snapshot, collector_public, collector_key_id):
    _key_id(collector_key_id)
    _exact(snapshot, {"format", "document_id", "operations", "checkpoint"})
    if snapshot["format"] != FORMAT:
        raise InputError("Unsupported editor snapshot format")
    identifier(snapshot["document_id"])
    operations = snapshot["operations"]
    if type(operations) is not list or not 1 <= len(operations) <= MAX_OPERATIONS:
        raise InputError("Invalid editor operation count")
    for envelope in operations:
        _envelope_shape(envelope, _operation_shape)
    _envelope_shape(snapshot["checkpoint"], _checkpoint_shape)
    raw = canonical(snapshot)
    if len(raw) > MAX_JSON:
        raise InputError("Editor snapshot exceeds the bounded JSON budget")
    # Own one immutable representation while checking the signed lineage.
    captured = decode_json(raw)
    document_id, blocks, last_writes = captured["document_id"], {}, {}
    previous_hash, last_time, observed = GENESIS, None, set()
    for sequence, envelope in enumerate(captured["operations"], 1):
        body = verify_message(envelope, collector_public, collector_key_id, "editor_operation")
        _operation_shape(body)
        event_time = timestamp(body["observed_at"])
        if body["document_id"] != document_id or body["sequence"] != sequence:
            raise InputError("Editor sequence or document identity mismatch")
        if body["previous_sha256"] != previous_hash or body["before_sha256"] != digest(_state(document_id, blocks)):
            raise InputError("Editor chain head or before-state mismatch")
        if last_time is not None and event_time < last_time:
            raise InputError("Editor chronology is inconsistent")
        block_id = body["block_id"]
        if block_id not in blocks and len(blocks) >= MAX_BLOCKS:
            raise InputError("Editor block limit exceeded during replay")
        blocks[block_id] = body["text"]
        if body["after_sha256"] != digest(_state(document_id, blocks)):
            raise InputError("Editor after-state mismatch")
        if body["activity"] in AI_ACTIVITIES:
            observed.add(body["activity"])
        last_writes[block_id] = body
        previous_hash, last_time = digest(envelope), event_time

    checkpoint = verify_message(captured["checkpoint"], collector_public, collector_key_id, "editor_checkpoint")
    _checkpoint_shape(checkpoint)
    final_document = _state(document_id, blocks)
    if (checkpoint["document_id"] != document_id or checkpoint["sequence"] != len(captured["operations"])
            or checkpoint["chain_head_sha256"] != previous_hash or checkpoint["document"] != final_document):
        raise InputError("Editor checkpoint does not match replayed state")
    if timestamp(checkpoint["observed_at"]) < last_time:
        raise InputError("Checkpoint predates its final operation")
    source_hash = digest(final_document)
    adopted = []
    for block_id, value in blocks.items():
        last = last_writes[block_id]
        if last["activity"] in AI_ACTIVITIES:
            block_hash = sha256_bytes(value.encode("utf-8"))
            adopted.append({
                "block_id": block_id, "revision_id": _revision(last["sequence"], block_hash),
                "sha256": block_hash, "activity": last["activity"], "observed_at": last["observed_at"],
            })
    return {
        "document_id": document_id, "revision_id": _revision(len(captured["operations"]), source_hash),
        "blocks": final_document["blocks"], "observed_activities": sorted(observed), "adopted": adopted,
        "source_sha256": source_hash, "lineage_sha256": digest(captured), "observed_at": checkpoint["observed_at"],
    }


def disclosure_text(disclosure):
    _exact(disclosure, {"activities", "scope"})
    _activities(disclosure["activities"])
    if disclosure["scope"] != "recorded_local_session_only":
        raise InputError("Unsupported disclosure scope")
    labels = ", ".join(activity.replace("_", " ") for activity in disclosure["activities"]) or "none declared"
    return (
        "Synthetic local publication pilot. Declared simulated AI activities: " + labels + ". "
        "Coverage is limited to this recorded local editing session. This editor invokes no external AI model. "
        "The origin of imported content and activity outside this session is unknown; this disclosure does not "
        "establish human-only authorship or complete AI provenance."
    )


def _view(view):
    _exact(view, VIEW_FIELDS)
    identifier(view["document_id"])
    identifier(view["revision_id"])
    document = {"document_id": view["document_id"], "blocks": view["blocks"]}
    _document(document)
    _activities(view["observed_activities"])
    for name in ("source_sha256", "lineage_sha256"):
        _hex(view[name])
    if digest(document) != view["source_sha256"]:
        raise InputError("Rendered source does not match its measured digest")
    observed_at = timestamp(view["observed_at"])
    if type(view["adopted"]) is not list or len(view["adopted"]) > MAX_BLOCKS:
        raise InputError("Invalid adopted block list")
    values, seen = {b["block_id"]: b["text"] for b in view["blocks"]}, set()
    for adopted in view["adopted"]:
        _exact(adopted, {"block_id", "revision_id", "sha256", "activity", "observed_at"})
        identifier(adopted["block_id"])
        identifier(adopted["revision_id"])
        _hex(adopted["sha256"])
        if (adopted["block_id"] in seen or adopted["block_id"] not in values
                or type(adopted["activity"]) is not str or adopted["activity"] not in view["observed_activities"]):
            raise InputError("Invalid adopted block identity or activity")
        seen.add(adopted["block_id"])
        if adopted["sha256"] != sha256_bytes(values[adopted["block_id"]].encode("utf-8")):
            raise InputError("Adopted block bytes do not match")
        if timestamp(adopted["observed_at"]) > observed_at:
            raise InputError("Adopted block postdates the checkpoint")


def _escaped_text(value):
    # Character references preserve CR text instead of HTML newline normalization.
    return escape(value, quote=True).replace("\r", "&#13;")


def render_html(view, disclosure):
    """Render a verified view; this function alone does not authenticate a view."""
    _view(view)
    notice = disclosure_text(disclosure)
    sections = []
    for block in view["blocks"]:
        label = block["block_id"].replace("_", " ").replace("-", " ")
        sections.append(
            '<section class="content-block" data-block-id="' + escape(block["block_id"], quote=True) + '">\n'
            '<h2>' + escape(label, quote=True) + '</h2>\n'
            '<p class="block-text">' + _escaped_text(block["text"]) + '</p>\n</section>'
        )
    html = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Prepared publication | ''' + escape(view["document_id"], quote=True) + '''</title>
<style>
:root{color-scheme:light}*{box-sizing:border-box}body{margin:0;background:#f3f5f8;color:#182536;font:17px/1.65 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:900px;margin:48px auto;padding:44px 52px;background:#fff;border:1px solid #dce3eb;border-radius:16px}header{padding-bottom:28px;border-bottom:1px solid #dce3eb}.eyebrow{margin:0 0 8px;color:#315779;font-size:12px;font-weight:700;letter-spacing:.12em;text-transform:uppercase}h1{font-size:36px;line-height:1.15;margin:0 0 16px;letter-spacing:-.025em}.metadata{font-size:13px;color:#526579;overflow-wrap:anywhere;margin:0}code{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}.content-block{margin:32px 0}.content-block h2{font-size:17px;text-transform:capitalize;color:#315779;margin:0 0 10px}.block-text{white-space:pre-wrap;overflow-wrap:anywhere;margin:0}#ai-use-disclosure{margin-top:40px;padding:24px;background:#edf3fa;border:1px solid #cadbed;border-radius:10px}#ai-use-disclosure h2{font-size:20px;line-height:1.3;margin:0 0 12px}.disclosure-text{margin:0;font-size:15px}footer{font-size:13px;color:#526579;margin-top:24px}@media(max-width:640px){main{margin:12px;padding:26px 22px;border-radius:10px}h1{font-size:29px}}@media print{body{background:#fff}main{margin:0;max-width:none;padding:18px;border:0}#ai-use-disclosure{break-inside:avoid}}
</style>
</head>
<body>
<main>
<header>
<p class="eyebrow">Synthetic local example</p>
<h1>Prepared publication</h1>
<p class="metadata">Document <code>''' + escape(view["document_id"], quote=True) + '''</code><br>Source revision <code>''' + escape(view["revision_id"], quote=True) + '''</code></p>
</header>
<article aria-label="Publication content">
''' + "\n".join(sections) + '''
</article>
<section id="ai-use-disclosure" aria-labelledby="disclosure-heading">
<h2 id="disclosure-heading">AI-use disclosure</h2>
<p class="disclosure-text">''' + _escaped_text(notice) + '''</p>
</section>
<footer>Prepared for local review. This file does not establish publisher receipt, acceptance, or legal compliance.</footer>
</main>
</body>
</html>
'''
    result = html.encode("utf-8")
    if len(result) > MAX_HTML:
        raise InputError("Rendered artifact exceeds the HTML byte limit")
    return result
