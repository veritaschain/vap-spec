"""Source-attributed presentation after the frozen recheck gate has succeeded."""

from copy import deepcopy

from .common import PILOTS, SCOPE, ReviewError, reference, resolve_pointer, sha256, strict_json


NOTE_TEXT = {
    "EXPECTATION_IS_NOT_SECURITY_PASS": {
        "en": "A matched scenario expectation is not a security, conformance or legal-compliance pass.",
        "ja": "シナリオの期待値との一致は、セキュリティ、仕様適合、法令遵守の合格判定ではありません。",
    },
    "UPLOAD_OUTSIDE_ROUTE_BYPASS": {
        "en": "The managed route recorded no attempt, but the controller's direct request was accepted. This negative control does not establish prevention across all routes.",
        "ja": "管理対象の経路では試行されませんでしたが、制御主体による直接要求は受け付けられました。この負例は、すべての経路での防止を示しません。",
    },
    "UPLOAD_FINAL_GATE_DIFFERS": {
        "en": "The final gate required review and prevented an attempt. Admission and postflight authorization preserve the earlier operation time and do not replace the final decision.",
        "ja": "最終ゲートは再確認を求め、試行を止めました。受付時と事後評価の承認は元の操作時刻に対応するため、最終判定の代わりにはなりません。",
    },
    "UPLOAD_UNKNOWN_WITH_RECEIVER_OBSERVATION": {
        "en": "The gateway outcome remains unknown while the receiver has an accepted-request observation. The receiver observation does not retroactively confirm the gateway result.",
        "ja": "受信側には受付の観測がある一方、ゲートウェイの結果は不明のままです。受信側の観測によってゲートウェイの結果を事後的に確定させません。",
    },
    "UPLOAD_RECEIPT_NOT_PROCESSING": {
        "en": "The scoped local receiver receipt concerns matching bytes. The core remote outcome remains UNKNOWN; downstream processing or retention is not established.",
        "ja": "ローカル受信側の限定された受領記録は、バイト列の一致に関するものです。中核評価の遠隔側結果は UNKNOWN のままで、その後の処理や保持は確認されていません。",
    },
    "UPLOAD_INTENT_NOT_DISPATCH": {
        "en": "The captured worker was killed after intent and the repeated request did not resend. A durable intent is not a body-send observation.",
        "ja": "記録対象のワーカーは意図の保存後に停止され、再要求では再送しませんでした。永続化された意図は、本文送信の観測ではありません。",
    },
    "PUBLICATION_OUTSIDE_GATE_WRITE": {
        "en": "The gate blocked its publication path, but a direct outside-gate write produced a visible file. Prevention across all routes is not established.",
        "ja": "ゲート経由の公開処理は止まりましたが、ゲート外の直接書き込みにより可視ファイルが作成されました。すべての経路での防止は確認されていません。",
    },
    "PUBLICATION_UNKNOWN_ORIGIN": {
        "en": "Current AI involvement and activity completeness remain UNKNOWN. Disclosure of recorded activity, or its absence, does not establish human-only origin or complete provenance.",
        "ja": "現在のAI関与と活動の完全性は UNKNOWN のままです。記録された活動の開示や記録の欠如だけでは、人間のみの作成や完全な来歴を示せません。",
    },
    "PUBLICATION_UNKNOWN_WITH_VISIBLE_FILE": {
        "en": "A visible-file observation coexists with an unresolved publication result. The retained file does not restore the withheld completion receipt.",
        "ja": "可視ファイルの観測があっても、公開処理の結果は未確定です。ファイルが残っていることによって、発行を見合わせた完了受領記録を復活させません。",
    },
    "PUBLICATION_CORE_REMAINS_REVIEW": {
        "en": "Separate authorization permitted this local export while the unchanged core remained REVIEW. Local output is not external publisher delivery or acceptance.",
        "ja": "別の承認によってこのローカル出力が許可されても、変更していない中核評価は REVIEW のままです。ローカル出力は、外部掲載先への到達や受理を示しません。",
    },
    "PUBLICATION_FINAL_AUTHORIZATION_CHANGED": {
        "en": "Initial local authorization was true, but final authorization was false after expiry. Preserve both decisions rather than treating initial approval as current permission.",
        "ja": "当初のローカル承認は有効でしたが、期限経過後の最終承認は無効でした。初回承認を現在の許可として扱わず、両方の判定を保持します。",
    },
    "PUBLICATION_DISCLOSURE_NOT_OVERRIDE": {
        "en": "Recorded disclosure and reviewer approval did not override prohibited use under the pinned policy.",
        "ja": "記録された開示と確認者の承認によって、固定された方針の利用禁止を覆してはいません。",
    },
    "SORTED_SUMMARY_NOT_RECORD_ASSOCIATION": {
        "en": "This concurrent case sorts aggregate state arrays. Their positions are not record associations; original record indices preserve each outcome and assessment pair.",
        "ja": "この同時実行ケースでは集計状態の配列を整列しています。配列位置を記録同士の対応とみなさず、元の記録番号で結果と評価の組を保ちます。",
    },
    "ERASURE_READABLE_RETAINED_DATA": {
        "en": "A specific retained copy or open handle remained READABLE after scoped namespace removal. This is not complete erasure, and broader excluded-domain outcomes remain UNKNOWN.",
        "ja": "限定された名前空間からの削除後も、特定の別コピーまたは開いたハンドルは READABLE でした。完全消去ではなく、除外された領域全体の結果は UNKNOWN のままです。",
    },
    "ERASURE_AFTER_ONLY_ABSENCE": {
        "en": "Only the after observation is available, so local corroboration is ABSENCE_ONLY even though an attributed provider completion claim exists.",
        "ja": "事後の観測しかないため、事業者に帰属する完了申告があっても、ローカルで裏付けられるのは ABSENCE_ONLY です。",
    },
    "ERASURE_LATER_PRESENCE": {
        "en": "A later observation found the entry present despite an earlier scoped receipt. Preserve both observations; do not hide the later presence or erase the earlier attributed claim.",
        "ja": "先行する限定的な受領記録があっても、後の観測では項目が存在しました。後の存在も、先行する申告も隠さず、両方を保持します。",
    },
    "ERASURE_NO_OBSERVER": {
        "en": "Observer evidence is absent. The provider attestation remains a scoped provider claim, not independent deletion verification.",
        "ja": "観測者の証拠はありません。事業者の署名付き申告は限定された範囲の申告であり、独立した削除検証ではありません。",
    },
    "ERASURE_PROBE_REJECTED_AFTER_OPERATION": {
        "en": "The original operation has a scoped completion record; a separate altered-evidence probe was rejected. Probe rejection is not a blocked deletion operation.",
        "ja": "元の操作には限定的な完了記録があり、別途改変した証拠の検証試行は拒否されました。検証試行の拒否を、削除操作の阻止とは扱いません。",
    },
    "ERASURE_PREEXISTING_ABSENCE": {
        "en": "The entry was already absent and no unlink was attempted. ABSENCE_ONLY does not attribute a deletion operation to this request.",
        "ja": "項目は既に存在せず、unlink は試行されませんでした。ABSENCE_ONLY は、この要求による削除操作を示しません。",
    },
    "ERASURE_UNKNOWN_WITH_ABSENCE": {
        "en": "Observed absence coexists with unknown completion and a replay that issued no new completion. Do not promote absence into a confirmed deletion result.",
        "ja": "不在の観測と完了不明の結果が併存し、再要求でも新たな完了記録は出されていません。不在だけを根拠に削除完了へ昇格させません。",
    },
}


def _escape(part):
    return str(part).replace("~", "~0").replace("/", "~1")


class _Sources:
    """Cache parsed owned bytes; expose only the shared concrete reference shape."""

    def __init__(self, files):
        if type(files) is not dict:
            raise ReviewError("Projection requires owned archive files")
        self.files, self.documents, self.identities = dict(files), {}, {}

    def document(self, file):
        if file not in self.documents:
            self.identities[file] = reference(self.files, file, "")
            self.documents[file] = strict_json(self.files[file])
        return self.documents[file]

    def value(self, file, pointer):
        return resolve_pointer(self.document(file), pointer)

    def reference(self, file, pointer):
        self.value(file, pointer)
        return {"file": file, "sha256": self.identities[file]["sha256"], "pointer": pointer}

    def fact(self, file, pointer, name):
        return {"name": name, "value": deepcopy(self.value(file, pointer)),
                "source": self.reference(file, pointer)}


def _fields(sources, file, base, names=None, prefix=""):
    value = sources.value(file, base)
    if type(value) is not dict:
        raise ReviewError("Recorded presentation fields require an object")
    names = sorted(value) if names is None else names
    return [sources.fact(file, base + "/" + _escape(name), prefix + name) for name in names]


def _section(key, operation_index, facts):
    return {"key": key, "operation_index": operation_index, "facts": facts}


def _optional_body(sources, file, base, key, operation_index, fields):
    if sources.value(file, base) is None:
        facts = [sources.fact(file, base, key)]
    else:
        facts = _fields(sources, file, base + "/body", fields)
    return _section(key, operation_index, facts)


def _frame(sources, file, path, operation_index, phase):
    current, pointer, absent = sources.document(file), "", None
    for token in path:
        if current is None:
            absent = "NULL_CONTAINER"
            break
        if type(current) is dict:
            if token not in current:
                absent = "MISSING_FIELD"
                break
            current = current[token]
        elif type(current) is list and type(token) is int and 0 <= token < len(current):
            current = current[token]
        else:
            raise ReviewError("An assessor frame path traverses an unsupported value")
        pointer += "/" + _escape(token)
    if absent is None and current is None:
        absent = "NULL_CONTAINER"
    if absent is not None:
        return {"operation_index": operation_index, "phase": phase, "availability": "FRAME_NOT_RECORDED",
                "absence_reason": absent, "source": sources.reference(file, pointer),
                "evidence_integrity": None, "assessments": None, "findings": None}
    if type(current) is not dict:
        raise ReviewError("A recorded assessor frame must be an object")
    return {"operation_index": operation_index, "phase": phase, "availability": "RECORDED",
            "absence_reason": None, "source": sources.reference(file, pointer),
            **{name: sources.fact(file, pointer + "/" + name, name)
               for name in ("evidence_integrity", "assessments", "findings")}}


def _upload(sources, file, case):
    sections = [_section("actual", None, _fields(sources, file, "/actual")),
                _section("receiver", None, _fields(sources, file, "/receiver_snapshot", ["handler_calls", "accepted_count"]))]
    frames = []
    receipt_fields = ["kind", "request_id", "subject_sha256", "payload_sha256", "byte_length", "received_at", "receipt_id"]
    for index, report in enumerate(case["reports"]):
        base = "/reports/" + str(index)
        sections.append(_section("operation", index, _fields(sources, file, base,
            ["state", "attempted", "reason", "journal_state", "payload_sha256", "byte_length"])))
        transport = base + "/transport_observation"
        facts = ([sources.fact(file, transport, "transport_observation")] if report["transport_observation"] is None
                 else _fields(sources, file, transport, ["attempted", "body_send_completed", "attempted_at", "dispatched_at", "status"]))
        sections.append(_section("transport", index, facts))
        sections.append(_optional_body(sources, file, base + "/receipt", "receipt", index, receipt_fields))
        for phase, field in (("preflight", "preflight_assessment"), ("final_gate", "final_gate_assessment"),
                             ("postflight", "postflight_assessment")):
            frames.append(_frame(sources, file, ["reports", index, field], index, phase))
    for index, _ in enumerate(case["receiver_snapshot"]["rows"]):
        base = "/receiver_snapshot/rows/" + str(index) + "/receipt/body"
        sections.append(_section("receiver_receipt", None, _fields(sources, file, base, receipt_fields,
                                                                  prefix="receiver_rows[" + str(index) + "].")))
    return sections, frames


def _publication(sources, file, case):
    actual = _fields(sources, file, "/actual") + [sources.fact(file, "/sort_states", "sort_states")]
    sections, frames = [_section("actual", None, actual)], []
    if case["additional_observations"]:
        sections.append(_section("additional_observations", None, _fields(sources, file, "/additional_observations")))
    for index, item in enumerate(case["records"]):
        base, report = "/records/" + str(index), item["report"]
        facts = _fields(sources, file, base + "/report", ["state", "attempted", "reason", "post_at"])
        store = base + "/report/publication"
        if report["publication"] is None:
            facts.append(sources.fact(file, store, "publication"))
        else:
            facts.extend(_fields(sources, file, store, ["journal_state", "visible_name"], prefix="publication."))
        sections.append(_section("operation", index, facts))
        sections.append(_section("disclosure", index, _fields(sources, file, base + "/candidate/disclosure", ["activities", "scope"])))
        for phase in ("preflight", "final_gate"):
            phase_path = base + "/report/" + phase
            facts = ([sources.fact(file, phase_path, phase)] if report[phase] is None else
                     _fields(sources, file, phase_path, ["at", "authorized_local_export", "reason"]))
            sections.append(_section("authorization_" + phase, index, facts))
            frames.append(_frame(sources, file, ["records", index, "report", phase, "assessor_frame", "report"], index, phase))
        sections.append(_optional_body(sources, file, base + "/report/receipt", "receipt", index,
            ["kind", "request_id", "fingerprint", "artifact_sha256", "disclosure_sha256", "byte_length",
             "destination_id", "visible_name", "observed_at"]))
    return sections, frames


def _erasure(sources, file, case):
    actual = _fields(sources, file, "/actual") + [sources.fact(file, "/sort_states", "sort_states"),
                                                 sources.fact(file, "/case_as_of", "case_as_of")]
    sections, frames = [_section("actual", None, actual)], []
    for index, record in enumerate(case["records"]):
        base = "/records/" + str(index)
        result_path, result = base + "/bundle/provider_result", record["bundle"]["provider_result"]
        facts = ([sources.fact(file, result_path, "provider_result")] if result is None else
                 _fields(sources, file, result_path, ["state", "attempted", "reason", "journal_state"]))
        facts.append(sources.fact(file, base + "/assessment/local_observation", "local_observation"))
        sections.append(_section("operation", index, facts))
        if result is not None:
            for field, names in (("acknowledgement", ["request_record_id", "acknowledged_at", "queue_state"]),
                                 ("attestation", ["request_record_id", "completed_at", "locations", "exclusions"])):
                path = result_path + "/" + field
                facts = ([sources.fact(file, path, field)] if result[field] is None else
                         _fields(sources, file, path + "/body/data", names))
                sections.append(_section(field, index, facts))
            sections.append(_optional_body(sources, file, result_path + "/receipt", "receipt", index,
                ["kind", "task_sha256", "request_id", "manifest_sha256", "before", "unlinked_at", "observed_at", "after"]))
        for phase in ("before", "after"):
            path, observation = base + "/bundle/" + phase, record["bundle"][phase]
            facts = ([sources.fact(file, path, phase)] if observation is None else
                     _fields(sources, file, path + "/body", ["provider_id", "tenant_id", "location", "object_id", "version_id",
                                                             "phase", "window_start", "window_end", "measurement"]))
            sections.append(_section("namespace_" + phase, index, facts))
        sections.append(_section("unknown_domains", index, _fields(sources, file, base + "/assessment/unknown_domains")))
        frames.append(_frame(sources, file, ["records", index, "assessment", "assessor_report"], index, "erasure"))
    for index, _ in enumerate(case["retained_controls"]):
        base = "/retained_controls/" + str(index) + "/body"
        sections.append(_section("retained_control", None, _fields(sources, file, base,
            ["kind", "task_sha256", "manifest_sha256", "mechanism", "state", "sha256", "byte_length", "observed_at"],
            prefix="retained_controls[" + str(index) + "].")))
    for index, _ in enumerate(case["probes"]):
        base = "/probes/" + str(index)
        sections.append(_section("probe", None, _fields(sources, file, base, ["outcome", "expected_task_sha256"],
                                                       prefix="probes[" + str(index) + "].")))
    return sections, frames


def _notes(sources, file, summary_file, summary_index, case):
    result = [{"code": "EXPECTATION_IS_NOT_SECURITY_PASS", "sources": [
        sources.reference(summary_file, "/results/" + str(summary_index) + "/matched"),
        sources.reference(summary_file, "/results/" + str(summary_index) + "/expected")]}]

    def add(code, pointers):
        result.append({"code": code, "sources": [sources.reference(file, pointer) for pointer in pointers]})

    cid = case["case_id"]
    if cid == "UL-14":
        add("UPLOAD_OUTSIDE_ROUTE_BYPASS", ["/reports/0/state", "/actual/gateway_attempts", "/actual/handler_calls",
                                           "/actual/accepted_count", "/actual/controller_direct_status", "/actual/all_route_prevention_established"])
    if cid == "UL-10":
        add("UPLOAD_FINAL_GATE_DIFFERS", ["/reports/0/preflight_assessment/assessments/transfer_authorization",
            "/reports/0/final_gate_assessment/assessments/transfer_authorization",
            "/reports/0/postflight_assessment/assessments/transfer_authorization", "/reports/0/attempted"])
    if cid in {"UL-07", "UL-08", "UL-16"}:
        add("UPLOAD_UNKNOWN_WITH_RECEIVER_OBSERVATION", ["/reports/0/state", "/reports/0/receipt", "/receiver_snapshot/accepted_count",
                                                        "/reports/0/postflight_assessment/assessments/remote_outcome"])
    if cid.startswith("UL-"):
        for index, report in enumerate(case["reports"]):
            if report["state"] == "RECEIPT_CONFIRMED":
                add("UPLOAD_RECEIPT_NOT_PROCESSING", ["/reports/" + str(index) + "/state",
                    "/reports/" + str(index) + "/postflight_assessment/assessments/remote_outcome"])
    if cid == "UL-17":
        add("UPLOAD_INTENT_NOT_DISPATCH", ["/actual/worker_killed_after_intent", "/actual/worker_exitcode",
                                           "/reports/0/journal_state", "/actual/gateway_attempts"])
    if cid == "LP-16":
        add("PUBLICATION_OUTSIDE_GATE_WRITE", ["/records/0/report/state", "/records/0/report/publication",
            "/actual/publication_attempts", "/actual/visible_count", "/outside_gate_write_observed", "/actual/all_route_prevention_established"])
    if cid in {"LP-09", "LP-10"}:
        add("PUBLICATION_UNKNOWN_ORIGIN", ["/additional_observations/core_ai_involvement",
            "/additional_observations/core_activity_completeness", "/additional_observations/declared_activities"])
    if cid == "LP-14":
        add("PUBLICATION_UNKNOWN_WITH_VISIBLE_FILE", ["/records/0/report/state", "/records/0/report/receipt", "/visible/visible_count"])
    if cid.startswith("LP-"):
        for index, item in enumerate(case["records"]):
            if item["report"]["state"] == "LOCAL_OUTPUT_CONFIRMED":
                add("PUBLICATION_CORE_REMAINS_REVIEW", ["/records/" + str(index) + "/report/preflight/authorized_local_export",
                    "/records/" + str(index) + "/report/preflight/assessor_frame/report/assessments/publication_action"])
    if cid == "LP-08":
        add("PUBLICATION_FINAL_AUTHORIZATION_CHANGED", ["/records/0/report/preflight/authorized_local_export",
                                                        "/records/0/report/final_gate/authorized_local_export", "/records/0/report/attempted"])
    if cid == "LP-05":
        add("PUBLICATION_DISCLOSURE_NOT_OVERRIDE", ["/records/0/report/preflight/assessor_frame/report/assessments/publication_action",
                                                    "/records/0/report/preflight/assessor_frame/report/assessments/policy_assessment"])
    if cid in {"LP-15", "LE-11"}:
        add("SORTED_SUMMARY_NOT_RECORD_ASSOCIATION", ["/sort_states", "/actual", "/records"])
    if cid in {"LE-12", "LE-13"}:
        add("ERASURE_READABLE_RETAINED_DATA", ["/records/0/bundle/provider_result/state", "/records/0/assessment/local_observation",
            "/retained_controls/0/body/mechanism", "/retained_controls/0/body/state", "/retained_controls/0/body/observed_at",
            "/records/0/assessment/unknown_domains"])
    if cid == "LE-14":
        add("ERASURE_AFTER_ONLY_ABSENCE", ["/records/0/bundle/before", "/records/0/bundle/after/body/measurement/state",
                                          "/records/0/assessment/local_observation", "/records/0/bundle/provider_result/state"])
    if cid == "LE-15":
        add("ERASURE_LATER_PRESENCE", ["/records/0/bundle/provider_result/state", "/records/0/bundle/provider_result/receipt/body/observed_at",
                                      "/records/0/bundle/after/body/measurement/state", "/records/0/assessment/local_observation"])
    if cid == "LE-18":
        add("ERASURE_NO_OBSERVER", ["/records/0/bundle/before", "/records/0/bundle/after", "/records/0/assessment/local_observation",
                                    "/records/0/assessment/assessor_report/assessments/deletion_evidence"])
    if cid in {"LE-04", "LE-05"}:
        add("ERASURE_PROBE_REJECTED_AFTER_OPERATION", ["/records/0/bundle/provider_result/state", "/probes/0/outcome"])
    if cid == "LE-08":
        add("ERASURE_PREEXISTING_ABSENCE", ["/records/0/bundle/provider_result/attempted", "/records/0/assessment/local_observation"])
    if cid == "LE-10":
        add("ERASURE_UNKNOWN_WITH_ABSENCE", ["/records/0/bundle/provider_result/state", "/records/0/bundle/provider_result/receipt",
            "/records/0/assessment/local_observation", "/records/1/bundle/provider_result/state"])
    return result


def project(files, recheck, reporter_identity):
    """Project verified owned evidence. This internal API does not verify a kit."""
    sources = _Sources(files)
    pilots, cases, per_pilot, matched = [], [], {}, 0
    metadata_fields = {
        "upload": ["recorded_at", "network_execution", "synthetic", "independent_reproduction", "all_route_prevention_established"],
        "publication": ["recorded_at", "execution", "synthetic", "independent_reproduction", "external_publication",
                        "real_ai_service_called", "all_route_prevention_established"],
        "erasure": ["recorded_at", "execution", "synthetic", "independent_reproduction", "remote_provider_used",
                    "universal_erasure", "raw_object_content_exported"],
    }
    functions = {"upload": _upload, "publication": _publication, "erasure": _erasure}
    for pilot, spec in PILOTS.items():
        summary_file = "evidence/" + pilot + "/summary.json"
        summary = sources.document(summary_file)
        identifiers = [spec["prefix"] + "-" + str(number).zfill(2) for number in range(1, spec["count"] + 1)]
        if [item["case_id"] for item in summary["results"]] != identifiers:
            raise ReviewError("Projection case inventory differs from the fixed verified snapshot")
        pilots.append({"pilot": pilot, "source_sha256": summary["source_sha256"],
                       "summary_source": sources.reference(summary_file, ""),
                       "capture_source": sources.reference("evidence/provenance.json", "/pilots/" + pilot),
                       "metadata": _fields(sources, summary_file, "", metadata_fields[pilot])})
        per_pilot[pilot] = spec["count"]
        for index, cid in enumerate(identifiers):
            entry = summary["results"][index]
            if entry["matched"] is not True:
                raise ReviewError("The fixed post-verification projection requires every saved expectation match")
            matched += 1
            file = "evidence/" + pilot + "/cases/" + cid + ".json"
            case = sources.document(file)
            if case["case_id"] != cid:
                raise ReviewError("Case file and summary identity differ")
            sections, frames = functions[pilot](sources, file, case)
            row_path = "/results/" + str(index)
            cases.append({"pilot": pilot, "case_id": cid, "capture_source": sources.reference(file, ""),
                          "title": sources.fact(summary_file, row_path + "/title", "title"),
                          "expectation": {name: sources.fact(summary_file, row_path + "/" + name, name)
                                          for name in ("matched", "expected", "actual", "differences")},
                          "sections": sections, "frames": frames,
                          "notes": _notes(sources, file, summary_file, index, case)})
    return {"format": "incident-review-report/0.1", "snapshot_id": "incident-ci-2026-10-30",
            "reporter": deepcopy(reporter_identity),
            "input": {"archive_sha256": recheck["archive_sha256"], "manifest_sha256": recheck["manifest_sha256"],
                      "provenance_sha256": sha256(files["evidence/provenance.json"])},
            "recheck": deepcopy(recheck), "scope": dict(SCOPE),
            "counts": {"saved_cases_rechecked": len(cases), "scenario_expectations_matched": matched, "per_pilot": per_pilot},
            "pilots": pilots, "cases": cases}
