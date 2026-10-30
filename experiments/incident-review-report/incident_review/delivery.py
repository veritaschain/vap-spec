"""Deterministic bilingual presentation and exclusive single-file delivery.

Rendering is an internal presentation step, not an evidence verifier. The public
flow verifies the fixed archive before passing its source-bound projection here.
"""

from io import BytesIO
import os
from pathlib import Path
import re
import stat
import string
import tempfile
import zipfile

from .common import (PILOTS, SCOPE, VERSION, ReviewError, digest, exact, json_bytes,
                     read_regular, safe_path, sha256, strict_json)

MAX_MEMBER = 2 * 1024 * 1024
MAX_BUNDLE = 6 * 1024 * 1024
MEMBERS = ("manifest.json", "review-en.md", "review-ja.md", "review.json")
CAPTURE_COMMIT = "1553ff9729ceb30f3ff03513cead45c5b7abd1d9"
CAPTURE_BASE = ("https://github.com/veritaschain/vap-spec/blob/" + CAPTURE_COMMIT
                + "/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/")
_EVIDENCE_FILES = {"evidence/provenance.json"}
for _pilot, _settings in PILOTS.items():
    _EVIDENCE_FILES.add("evidence/" + _pilot + "/summary.json")
    _EVIDENCE_FILES.update("evidence/" + _pilot + f"/cases/{_settings['prefix']}-{number:02d}.json"
                           for number in range(1, _settings["count"] + 1))

_LABELS = {
    "en": {
        "title": "Offline review of the fixed incident evidence capture",
        "headline": "53 saved cases rechecked; 53 scenario expectations matched. These are not 53 security successes.",
        "intro": "This document presents saved synthetic observations. Evidence checks were rerun; the original upload, publication and erasure actions were not repeated. Human review was not performed. The truth of the observations and independent reproduction are not established. Conformance and legal compliance are not assessed.",
        "scope": "Scope and limits", "counts": "Rechecked inventory", "bindings": "Report and input bindings",
        "metadata": "Original capture metadata", "cases": "Case observations", "sources": "Source references",
        "index": "Case index", "index_title": "Captured title", "index_states": "Recorded state list", "index_notes": "Interpretation codes",
        "index_intro": "These state lists are recorded case-level aggregates. Their positions do not pair operations with core assessments. The interpretation codes are explained in the full case entries; they are not grades.",
        "file_inventory": "Captured file inventory", "pointer_inventory": "Concrete source pointers", "file_reference": "File reference",
        "pilot": "Pilot", "count": "Saved cases", "field": "Field", "value": "Recorded value", "source": "Source",
        "json_hash": "Authoritative review.json SHA-256", "source_hash": "Reporter source SHA-256", "version": "Reporter version",
        "capture": "Whole-case capture", "title_source": "Title source", "expectation": "Scenario expectation",
        "matched": "MATCHED", "sections": "Recorded sections", "frames": "Core assessor frames",
        "case_wide": "case-wide", "operation": "original record index", "phase": "phase",
        "frame_source": "Frame or nearest existing container", "availability": "Availability", "absence": "Absence reason",
        "dimensions": "Recorded core dimensions", "findings": "Recorded core findings", "finding": "Finding index",
        "notes": "Capture interpretations", "note_intro": "The following notes interpret this fixed capture; they are not new observations or general decisions.",
        "no_notes": "No additional interpretation note is attached.", "all_from": "All values in the following table come from",
        "missing": "No core dimensions are inferred for this missing frame. The JSON fields evidence_integrity, assessments and findings remain null.",
        "root": "document root (empty JSON Pointer)", "file": "Archive member", "raw_hash": "Raw-file SHA-256", "pointer": "JSON Pointer",
        "reference_intro": "Each S-number identifies a concrete JSON Pointer and an F-number. Each F-number identifies one exact archive member and its raw-byte digest. Links point only to the fixed repository capture commit. Values remain attributable to the captured controller statements; a source link is not independent endorsement.",
        "summary": "Whole original summary", "provenance": "Original capture provenance", "pilot_source": "Original pilot source SHA-256",
        "empty": "Empty recorded array", "none_sections": "No sections recorded.", "none_frames": "No assessor frames listed.",
    },
    "ja": {
        "title": "固定されたインシデント証拠のオフライン確認レポート",
        "headline": "保存済み53ケースを再検証し、53ケースの期待結果との一致を確認しました。53件のセキュリティ上の成功を意味しません。",
        "intro": "この文書は保存された合成データの観測記録を提示します。再実行したのは証拠の検証であり、元のアップロード・公開・削除操作ではありません。人によるレビューは実施していません。観測内容の真実性と独立した再現は確立されておらず、適合性と法令遵守も評価していません。",
        "scope": "対象範囲と限界", "counts": "再検証したケース数", "bindings": "レポートと入力の結び付け",
        "metadata": "元の収集記録のメタデータ", "cases": "ケース別の観測記録", "sources": "参照元一覧",
        "index": "ケース索引", "index_title": "記録された題名", "index_states": "記録された状態の一覧", "index_notes": "解釈のコード",
        "index_intro": "この状態一覧は、ケース単位で記録された集計です。配列位置は、操作とコア評価の対応関係を示しません。解釈のコードは各ケースの詳細で説明しており、評価等級ではありません。",
        "file_inventory": "収集ファイル一覧", "pointer_inventory": "具体的な参照位置", "file_reference": "ファイル参照",
        "pilot": "実験", "count": "保存済みケース数", "field": "項目", "value": "記録された値", "source": "参照元",
        "json_hash": "正本 review.json の SHA-256", "source_hash": "レポーターのソース SHA-256", "version": "レポーターのバージョン",
        "capture": "ケース全体の収集記録", "title_source": "題名の参照元", "expectation": "シナリオの期待結果",
        "matched": "MATCHED（一致）", "sections": "記録された項目", "frames": "コア評価器の評価フレーム",
        "case_wide": "ケース全体", "operation": "元のレコード添字", "phase": "段階",
        "frame_source": "評価フレーム、または存在する最寄りのコンテナー", "availability": "記録の有無", "absence": "欠落の区分",
        "dimensions": "記録されたコア評価項目", "findings": "記録されたコア評価の所見", "finding": "所見の添字",
        "notes": "収集記録の解釈", "note_intro": "以下は、この固定された収集記録に対する解釈です。新しい観測事実や一般的な判断ではありません。",
        "no_notes": "追加の解釈注記はありません。", "all_from": "次の表の値はすべて、この参照元に基づきます：",
        "missing": "欠落したフレームにコア評価値を補っていません。JSON の evidence_integrity、assessments、findings は null のままです。",
        "root": "文書のルート（空の JSON Pointer）", "file": "アーカイブ内のファイル", "raw_hash": "元ファイルの SHA-256", "pointer": "JSON Pointer",
        "reference_intro": "S番号は、具体的な JSON Pointer と F番号を示します。F番号は、アーカイブ内の正確なファイルと元バイト列のハッシュ値を示します。リンク先は固定されたリポジトリの収集コミットのみです。値は収集したコントローラーの記述に帰属し、参照リンクは独立した保証ではありません。",
        "summary": "元のサマリー全体", "provenance": "元の収集情報", "pilot_source": "元の実験ソース SHA-256",
        "empty": "記録された空配列", "none_sections": "項目は記録されていません。", "none_frames": "評価フレームは列挙されていません。",
    },
}


def _text(value, *, limit=16384):
    if type(value) is not str or not value or len(value) > limit:
        raise ReviewError("Expected bounded nonempty presentation text")


def _index(value, *, nullable=False):
    if nullable and value is None:
        return
    if type(value) is not int or not 0 <= value <= 10000:
        raise ReviewError("Invalid original record index")


def _reference(value):
    exact(value, {"file", "sha256", "pointer"})
    if type(value["file"]) is not str or value["file"] not in _EVIDENCE_FILES:
        raise ReviewError("Presentation source is outside the fixed capture inventory")
    digest(value["sha256"])
    pointer = value["pointer"]
    if (type(pointer) is not str or len(pointer) > 2048 or (pointer and not pointer.startswith("/"))
            or re.search(r"~(?![01])", pointer)):
        raise ReviewError("Invalid presentation JSON Pointer")


def _fact(value):
    exact(value, {"name", "value", "source"})
    _text(value["name"])
    _reference(value["source"])


def _list(value):
    if type(value) is not list or len(value) > 10000:
        raise ReviewError("Expected a bounded presentation array")


def _validate(report):
    from .projection import NOTE_TEXT

    exact(report, {"format", "snapshot_id", "reporter", "input", "recheck", "scope", "counts", "pilots", "cases"})
    if report["format"] != "incident-review-report/0.1" or report["snapshot_id"] != "incident-ci-2026-10-30":
        raise ReviewError("Unsupported review report identity")
    counts = {"saved_cases_rechecked": 53, "scenario_expectations_matched": 53,
              "per_pilot": {name: value["count"] for name, value in PILOTS.items()}}
    if json_bytes(report["scope"]) != json_bytes(SCOPE) or json_bytes(report["counts"]) != json_bytes(counts):
        raise ReviewError("Report scope or counts differ from the fixed qualified capture")
    identity = report["reporter"]
    exact(identity, {"version", "source_sha256", "source_manifest"})
    if identity["version"] != VERSION or type(identity["source_manifest"]) is not dict:
        raise ReviewError("Unsupported reporter source identity")
    digest(identity["source_sha256"])
    for path, measured in identity["source_manifest"].items():
        safe_path(path)
        digest(measured)
    exact(report["input"], {"archive_sha256", "manifest_sha256", "provenance_sha256"})
    for measured in report["input"].values():
        digest(measured)
    recheck = report["recheck"]
    exact(recheck, {"format", "snapshot_id", "archive_sha256", "manifest_sha256", "source_binding", "verified_exports",
                    "pilots", "actions_reexecuted", "independent_reproduction", "conformance", "dependency_scope"})
    if (recheck["format"] != "incident-recheck-report/0.1" or recheck["snapshot_id"] != report["snapshot_id"]
            or recheck["archive_sha256"] != report["input"]["archive_sha256"]
            or recheck["manifest_sha256"] != report["input"]["manifest_sha256"]
            or recheck["source_binding"] != "MATCHED_TRUSTED_CHECKOUT"
            or type(recheck["verified_exports"]) is not int or recheck["verified_exports"] != 53
            or recheck["actions_reexecuted"] is not False or recheck["independent_reproduction"] != "NOT_ESTABLISHED"
            or recheck["conformance"] != "NOT_ASSESSED" or recheck["dependency_scope"] != "PINNED_VERSIONS_NOT_HERMETIC"):
        raise ReviewError("Presentation lacks the required complete qualified recheck result")
    _list(report["pilots"])
    if [item.get("pilot") if type(item) is dict else None for item in report["pilots"]] != list(PILOTS):
        raise ReviewError("Pilot presentation order or inventory differs")
    for item in report["pilots"]:
        exact(item, {"pilot", "source_sha256", "summary_source", "capture_source", "metadata"})
        digest(item["source_sha256"])
        _reference(item["summary_source"])
        _reference(item["capture_source"])
        _list(item["metadata"])
        for fact in item["metadata"]:
            _fact(fact)
    _list(report["cases"])
    expected = [(pilot, f"{details['prefix']}-{index:02d}") for pilot, details in PILOTS.items()
                for index in range(1, details["count"] + 1)]
    if [(item.get("pilot"), item.get("case_id")) if type(item) is dict else None for item in report["cases"]] != expected:
        raise ReviewError("Case presentation order or inventory differs")
    for case in report["cases"]:
        exact(case, {"pilot", "case_id", "capture_source", "title", "expectation", "sections", "frames", "notes"})
        _reference(case["capture_source"])
        _fact(case["title"])
        _text(case["title"]["value"])
        exact(case["expectation"], {"matched", "expected", "actual", "differences"})
        for fact in case["expectation"].values():
            _fact(fact)
        if case["expectation"]["matched"]["value"] is not True:
            raise ReviewError("Fixed capture expectation must be MATCHED, not a fabricated security grade")
        actual = case["expectation"]["actual"]["value"]
        if (type(actual) is not dict or type(actual.get("states")) is not list
                or not actual["states"] or any(type(state) is not str for state in actual["states"])):
            raise ReviewError("Case index requires the recorded aggregate state list")
        for field in ("sections", "frames", "notes"):
            _list(case[field])
        for section in case["sections"]:
            exact(section, {"key", "operation_index", "facts"})
            if type(section["key"]) is not str or not re.fullmatch(r"[a-z][a-z0-9_]{0,63}", section["key"]):
                raise ReviewError("Unsupported section code")
            _index(section["operation_index"], nullable=True)
            _list(section["facts"])
            for fact in section["facts"]:
                _fact(fact)
        for frame in case["frames"]:
            exact(frame, {"operation_index", "phase", "availability", "absence_reason", "source",
                          "evidence_integrity", "assessments", "findings"})
            _index(frame["operation_index"])
            _text(frame["phase"], limit=64)
            _reference(frame["source"])
            if frame["availability"] == "RECORDED":
                if frame["absence_reason"] is not None:
                    raise ReviewError("A recorded frame cannot have an absence reason")
                for field in ("evidence_integrity", "assessments", "findings"):
                    _fact(frame[field])
                if type(frame["assessments"]["value"]) is not dict or type(frame["findings"]["value"]) is not list:
                    raise ReviewError("Recorded core dimensions or findings have an invalid shape")
            elif frame["availability"] == "FRAME_NOT_RECORDED":
                if (type(frame["absence_reason"]) is not str or frame["absence_reason"] not in {"NULL_CONTAINER", "MISSING_FIELD"}
                        or any(frame[field] is not None for field in ("evidence_integrity", "assessments", "findings"))):
                    raise ReviewError("Missing frame must retain its absence reason and null fields")
            else:
                raise ReviewError("Unsupported frame availability")
        for note in case["notes"]:
            exact(note, {"code", "sources"})
            if type(note["code"]) is not str or note["code"] not in NOTE_TEXT:
                raise ReviewError("Unknown capture interpretation code")
            exact(NOTE_TEXT[note["code"]], {"en", "ja"})
            for text in NOTE_TEXT[note["code"]].values():
                _text(text)
            _list(note["sources"])
            if not note["sources"]:
                raise ReviewError("An interpretation must identify its captured sources")
            for source in note["sources"]:
                _reference(source)


def _escape(value):
    """Render dynamic plain text, including URL-looking text, without Markdown."""
    result = []
    for character in value:
        if character in "\r\n\t":
            result.append("&#92;" + {"\r": "r", "\n": "n", "\t": "t"}[character])
        elif ord(character) < 32 or ord(character) == 127 or character in "\u2028\u2029\u202a\u202b\u202c\u202d\u202e\u2066\u2067\u2068\u2069":
            result.append("&#92;u" + format(ord(character), "04x"))
        elif character in string.punctuation:
            result.append("&#" + str(ord(character)) + ";")
        else:
            result.append(character)
    return "".join(result)


def _value(value):
    # JSON notation distinguishes a literal "null" string, JSON null, false,
    # empty lists and objects without inferring missing evidence or UNKNOWN.
    return _escape(json_bytes(value).decode("ascii").rstrip("\n"))


class _Sources:
    def __init__(self):
        self.entries = {}
        self.files = {}

    def add(self, reference):
        key = (reference["file"], reference["sha256"], reference["pointer"])
        file_key = key[:2]
        if file_key not in self.files:
            self.files[file_key] = "F" + str(len(self.files) + 1).zfill(4)
        if key not in self.entries:
            self.entries[key] = "S" + str(len(self.entries) + 1).zfill(4)
        return self.entries[key]


def _table(lines, headings, rows):
    lines.append("| " + " | ".join(headings) + " |")
    lines.append("| " + " | ".join("---" for _ in headings) + " |")
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    lines.append("")


def _facts(lines, facts, labels, sources):
    _table(lines, [labels["field"], labels["value"], labels["source"]],
           [(_escape(fact["name"]), _value(fact["value"]), sources.add(fact["source"])) for fact in facts])


def _markdown(report, language, report_digest):
    from .projection import NOTE_TEXT

    labels, sources = _LABELS[language], _Sources()
    lines = ["# " + labels["title"], "", "**" + labels["headline"] + "**", "", labels["intro"], "",
             "## " + labels["scope"], ""]
    _table(lines, [labels["field"], labels["value"]],
           [(_escape(name), _value(value)) for name, value in report["scope"].items()])
    lines.extend(["## " + labels["counts"], ""])
    _table(lines, [labels["pilot"], labels["count"]],
           [(pilot, str(report["counts"]["per_pilot"][pilot])) for pilot in PILOTS])
    lines.extend(["## " + labels["bindings"], ""])
    bindings = [(labels["json_hash"], report_digest), (labels["version"], report["reporter"]["version"]),
                (labels["source_hash"], report["reporter"]["source_sha256"])]
    bindings.extend((name, value) for name, value in report["input"].items())
    _table(lines, [labels["field"], labels["value"]], [(_escape(name), _escape(value)) for name, value in bindings])
    lines.extend(["## " + labels["index"], "", labels["index_intro"], ""])
    index_rows = []
    for case in report["cases"]:
        actual = case["expectation"]["actual"]
        # The verified fact identifies the entire actual object; its recorded
        # states child therefore has this concrete source pointer. No record
        # association is inferred from the aggregate list's order.
        states_source = {**actual["source"], "pointer": actual["source"]["pointer"] + "/states"}
        notes = []
        for note in case["notes"]:
            refs = ", ".join(sources.add(source) for source in note["sources"])
            notes.append(_escape(note["code"]) + " (" + refs + ")")
        index_rows.append((
            _escape(case["case_id"]) + " (" + sources.add(case["capture_source"]) + ")",
            _escape(case["title"]["value"]) + " (" + sources.add(case["title"]["source"]) + ")",
            _value(actual["value"]["states"]) + " (" + sources.add(states_source) + ")",
            "; ".join(notes) if notes else labels["no_notes"],
        ))
    _table(lines, ["Case" if language == "en" else "ケース", labels["index_title"], labels["index_states"], labels["index_notes"]], index_rows)
    lines.extend(["## " + labels["metadata"], ""])
    for pilot in report["pilots"]:
        lines.extend(["### " + pilot["pilot"], "", labels["pilot_source"] + ": " + pilot["source_sha256"], "",
                      labels["summary"] + ": " + sources.add(pilot["summary_source"]), "",
                      labels["provenance"] + ": " + sources.add(pilot["capture_source"]), ""])
        _facts(lines, pilot["metadata"], labels, sources)
    lines.extend(["## " + labels["cases"], ""])
    for case in report["cases"]:
        lines.extend(["### " + _escape(case["case_id"]) + " — " + _escape(case["title"]["value"]), "",
                      labels["capture"] + ": " + sources.add(case["capture_source"]), "",
                      labels["title_source"] + ": " + sources.add(case["title"]["source"]), "",
                      "#### " + labels["expectation"] + ": " + labels["matched"], ""])
        _facts(lines, [case["expectation"][name] for name in ("matched", "expected", "actual", "differences")], labels, sources)
        lines.extend(["#### " + labels["sections"], ""])
        if not case["sections"]:
            lines.extend([labels["none_sections"], ""])
        for section in case["sections"]:
            location = labels["case_wide"] if section["operation_index"] is None else labels["operation"] + " " + str(section["operation_index"])
            lines.extend(["##### " + _escape(section["key"]) + " — " + location, ""])
            _facts(lines, section["facts"], labels, sources)
        lines.extend(["#### " + labels["frames"], ""])
        if not case["frames"]:
            lines.extend([labels["none_frames"], ""])
        for frame in case["frames"]:
            lines.extend(["##### " + labels["operation"] + " " + str(frame["operation_index"]) + " — "
                          + labels["phase"] + " " + _escape(frame["phase"]), "",
                          labels["frame_source"] + ": " + sources.add(frame["source"]), ""])
            _table(lines, [labels["field"], labels["value"]],
                   [(labels["availability"], _value(frame["availability"])), (labels["absence"], _value(frame["absence_reason"]))])
            if frame["availability"] == "FRAME_NOT_RECORDED":
                lines.extend([labels["missing"], ""])
                continue
            _facts(lines, [frame["evidence_integrity"]], labels, sources)
            lines.extend(["###### " + labels["dimensions"], "", labels["all_from"] + " " + sources.add(frame["assessments"]["source"]), ""])
            _table(lines, [labels["field"], labels["value"]],
                   [(_escape(name), _value(value)) for name, value in sorted(frame["assessments"]["value"].items())])
            lines.extend(["###### " + labels["findings"], "", labels["all_from"] + " " + sources.add(frame["findings"]["source"]), ""])
            findings = frame["findings"]["value"]
            if findings:
                _table(lines, [labels["finding"], labels["value"]], [(str(index), _value(value)) for index, value in enumerate(findings)])
            else:
                lines.extend([labels["empty"] + ": " + _value([]), ""])
        lines.extend(["#### " + labels["notes"], "", labels["note_intro"], ""])
        if not case["notes"]:
            lines.extend([labels["no_notes"], ""])
        for note in case["notes"]:
            refs = ", ".join(sources.add(source) for source in note["sources"])
            lines.extend(["**" + _escape(note["code"]) + "** — " + _escape(NOTE_TEXT[note["code"]][language]), "",
                          labels["source"] + ": " + refs, ""])
    lines.extend(["## " + labels["sources"], "", labels["reference_intro"], ""])
    lines.extend(["### " + labels["file_inventory"], ""])
    rows = []
    for (file, measured), name in sources.files.items():
        # Only these fixed, already validated inventory names form URLs. A fact
        # value or JSON Pointer is never interpolated into a link destination.
        url = CAPTURE_BASE + file.removeprefix("evidence/")
        rows.append(("[" + name + "](" + url + ")", _escape(file), measured))
    _table(lines, [labels["file_reference"], labels["file"], labels["raw_hash"]], rows)
    lines.extend(["### " + labels["pointer_inventory"], ""])
    pointer_rows = [(name, sources.files[(file, measured)], _escape(pointer) if pointer else labels["root"])
                    for (file, measured, pointer), name in sources.entries.items()]
    _table(lines, [labels["source"], labels["file_reference"], labels["pointer"]], pointer_rows)
    result = ("\n".join(lines).rstrip("\n") + "\n").encode("utf-8")
    if len(result) > MAX_MEMBER:
        raise ReviewError("Rendered Markdown exceeds the member limit")
    return result


def render_members(report):
    raw = json_bytes(report)
    if len(raw) > MAX_MEMBER:
        raise ReviewError("Authoritative report JSON exceeds the member limit")
    captured = strict_json(raw)
    _validate(captured)
    members = {"review.json": raw}
    measured = sha256(raw)
    members["review-en.md"] = _markdown(captured, "en", measured)
    members["review-ja.md"] = _markdown(captured, "ja", measured)
    manifest = {
        "format": "incident-review-bundle/0.1",
        "entries": [{"path": name, "sha256": sha256(value), "byte_length": len(value)} for name, value in sorted(members.items())],
    }
    members["manifest.json"] = json_bytes(manifest)
    if set(members) != set(MEMBERS) or any(type(value) is not bytes or len(value) > MAX_MEMBER for value in members.values()):
        raise ReviewError("Rendered members differ from the bounded fixed inventory")
    return members


def bundle_bytes(report):
    members = render_members(report)
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_STORED, allowZip64=False) as archive:
        archive.comment = b""
        for name, raw in sorted(members.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.create_system = 3
            entry.compress_type = zipfile.ZIP_STORED
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            entry.extra = entry.comment = b""
            archive.writestr(entry, raw)
    raw = buffer.getvalue()
    if len(raw) > MAX_BUNDLE:
        raise ReviewError("Review bundle exceeds the total byte limit")
    return raw


def publish_bundle(destination, raw):
    if type(raw) is not bytes or not 0 < len(raw) <= MAX_BUNDLE:
        raise ReviewError("Publication requires complete bounded owned bytes")
    destination = Path(destination).absolute()
    parent = destination.parent
    temporary = None
    descriptor = directory = None
    linked, temporary_identity = False, None
    try:
        initial = parent.lstat()
        if not stat.S_ISDIR(initial.st_mode):
            raise ReviewError("Destination parent must be an existing real directory")
        directory = os.open(parent, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        identity = lambda info: (info.st_dev, info.st_ino)
        if identity(os.fstat(directory)) != identity(initial):
            raise ReviewError("Destination directory changed before staging")
        try:
            os.stat(destination.name, dir_fd=directory, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise ReviewError("Destination already exists; no overwrite is permitted")
        descriptor, temporary_path = tempfile.mkstemp(prefix=".incident-review-", suffix=".tmp", dir=parent)
        temporary = Path(temporary_path)
        opened = os.fstat(descriptor)
        temporary_identity = identity(opened)
        if (not stat.S_ISREG(opened.st_mode)
                or identity(opened) != identity(os.stat(temporary.name, dir_fd=directory, follow_symlinks=False))):
            raise ReviewError("Temporary report file does not belong to the pinned destination directory")
        offset = 0
        while offset < len(raw):
            written = os.write(descriptor, raw[offset:])
            if written <= 0:
                raise ReviewError("Report write did not complete")
            offset += written
        os.fsync(descriptor)
        if (identity(parent.lstat()) != identity(os.fstat(directory))
                or identity(os.stat(temporary.name, dir_fd=directory, follow_symlinks=False)) != identity(opened)
                or os.fstat(descriptor).st_size != len(raw)):
            raise ReviewError("Report staging or destination changed before publication")
        os.link(temporary.name, destination.name, src_dir_fd=directory, dst_dir_fd=directory, follow_symlinks=False)
        linked = True
        published = os.stat(destination.name, dir_fd=directory, follow_symlinks=False)
        if (identity(parent.lstat()) != identity(os.fstat(directory))
                or not stat.S_ISREG(published.st_mode) or identity(published) != temporary_identity
                or published.st_size != len(raw)):
            raise ReviewError("Destination changed after publication; the linked file may remain")
    except OSError as exc:
        detail = " after publication; the complete linked file may remain" if linked else " before publication"
        raise ReviewError("Cannot publish the report" + detail) from exc
    finally:
        cleanup_error = None
        try:
            if descriptor is not None:
                try:
                    os.close(descriptor)
                except OSError as exc:
                    cleanup_error = exc
            if temporary is not None:
                # Cleanup addresses only this call's private temporary name; an
                # already-linked final file is never rolled back or removed.
                try:
                    remaining = os.stat(temporary.name, dir_fd=directory, follow_symlinks=False)
                    if temporary_identity is not None and (remaining.st_dev, remaining.st_ino) != temporary_identity:
                        raise ReviewError("Temporary name was replaced; unrelated content was not removed")
                    os.unlink(temporary.name, dir_fd=directory)
                except FileNotFoundError:
                    pass
                except OSError as exc:
                    cleanup_error = exc
        finally:
            if directory is not None:
                os.close(directory)
        if cleanup_error is not None:
            suffix = "; the linked final file may remain" if linked else "; publication did not complete"
            raise ReviewError("Temporary report cleanup failed" + suffix) from cleanup_error


def read_bundle(path, expected_sha256):
    digest(expected_sha256)
    path = Path(path).absolute()
    raw = read_regular(path.parent, path.name, limit=MAX_BUNDLE)
    if not raw or sha256(raw) != expected_sha256:
        raise ReviewError("Report bundle differs from its mandatory external digest")
    return raw
