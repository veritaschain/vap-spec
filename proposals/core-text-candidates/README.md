# Draft candidate text for five core subjects (F7, F9, F11, F12 first part, F13)

**Status:** Discussion draft, not adopted. **Formal proposal number:** Unassigned.
**Draft revision:** 0.1. **Date:** 2026-11-28 JST. **Target release:** Undecided.
**Baseline:** VAP v1.2.0 Draft 3 at commit `2a18ae7c77a4afcb7468345db2424076530c7630`,
specification SHA-256 `a35d5e082fd4b2f9921a78b1a71df263018320375e09fa18cf81533a18a19998`.
**License:** CC BY 4.0 International. A Japanese summary follows the English text.

Repository integration of this discussion draft is not normative adoption. Its unadopted status,
unassigned identifier and undecided target release remain unchanged after merge.

This draft introduces no VAP v1.2 requirement, event type, field, wire-format change or conformance level.
Uppercase requirement words in section 2 express **proposed** requirements only.

**Origin and limits of this draft.** The text was prepared with AI assistance (Claude, Anthropic) from VSO's
internal review of 28 November 2026 of its public incident registry. It is first-party work and has not been
independently reviewed. The registry contains records in which Anthropic is a party. VAP has no external
implementation and no Evidence Pack accepted in any proceeding.

## 1 Purpose and scope

The [CHANGE-002 preparation register](../CHANGE-002-CANDIDATES.md), section 4, lists eight subjects (F7 to
F14) that need exact text before they can be reviewed. This draft supplies candidate text for five of them.
They were chosen because each can be stated as wording in existing clauses, without a new event type, a named
field, a wire format or a verdict rule:

| Row | Subject | Kind of candidate text | Clause |
| --- | --- | --- | --- |
| F11 | Meaning of attributable | Definition | §1.5, Appendix A |
| F13 | Secret values in evidence | Proposed requirement | §7 |
| F12 (first part) | Separation of record-signing keys from the recorded actor | Proposed recommendation and declaration | §6.1.2, §8.2 |
| F9 | Evaluation dimensions | Informative note | §9.3 |
| F7 | Distinguishing evidence origins | Reservation of an optional indication | §4.2.2 |

Not covered here: three-valued verification (P1) and declared scope (P2), which have their own drafts; the
meaning and bytes of `bind`, the key and signature input policy, and numeric representation (register
section 3); the resolution invariant (F8); deployments without a domain profile (F10); key-compromise
declarations, the second part of F12; and replacement of a decision (F14).

## 2 Candidate text

### 2.1 F11 — "attributable"

**Current text.** §1.6(c) limits what conformance warrants to "the integrity, completeness (at anchor
granularity), and attributability of their records". Neither §1.5 nor Appendix A defines the term.
INT-005 makes signatures a SHOULD, and §4.4.3 records operator, approval and delegation fields.

**Candidate addition to the §1.5 table and Appendix A.**

> **Attributable** — A record is attributable when its signature verifies under a public key that the
> verifier has established, from trust information outside the record, as bound to the identified signer.
> Attributability does not establish who or what controlled the key when the record was signed, that the
> signer was authorized to perform the recorded act, or who bears legal responsibility.

**Open points.**

1. INT-005 is a SHOULD; its elevation is deferred (CHANGE-001 Annex C.2, register row D2). Whether an
   unsigned record can be called attributable has to be decided together with this definition.
2. What a verifier needs in order to treat a key as "established" (a supplied trust file, a certificate
   chain, a profile-defined registry) is not specified here. Under P1, an unestablished key would make the
   corresponding check `INDETERMINATE`.
3. Temporal validity (rotation, expiry, a later compromise claim) belongs with the second part of F12.

### 2.2 F13 — secret values in records

**Current text.** §6.3 and §7.4 cover crypto-shredding of fields that the implementation encrypted before
they were committed. Nothing in v1.2 keeps a reusable secret out of a signed or anchored record.

**Candidate addition to §7.**

> Reusable authentication secrets — including passwords, bearer tokens, API keys, private keys, session
> cookies and recovery codes — MUST NOT appear in plaintext in any field that enters an EventHash or a
> Merkle leaf. A record that refers to a credential MUST use a non-secret identifier assigned by the
> credential's issuer. A hash of a low-entropy secret is not a non-secret identifier. ERASURE (§6.3, §7.4)
> applies only to fields that were encrypted before commitment; it does not withdraw a secret committed
> in plaintext.

**Open points.**

1. Whether the rule also covers values captured from inputs (for example a prompt or a tool result that
   happens to contain a credential), and what a producer records when it withholds such a value.
2. How a verifier reports a field that was withheld or redacted. It must not treat the absence as a
   verified statement about the content (register F13).
3. Test material must use synthetic secrets only.
4. A third party can demonstrate a violation of this rule and cannot demonstrate compliance with it.
   The [screening experiment](../../experiments/secret-value-screening/README.md) shows the limit on
   fourteen synthetic cases: a reference that is a hash of a low-entropy secret is not distinguishable
   from any other digest. Review text should state that the rule is checkable only in the negative.

### 2.3 F12, first part — where record-signing keys are held

**Current text.** INT-006 requires external anchoring of signed roots at all levels. v1.2 does not say where
record-signing keys or anchor-submission credentials are held relative to the system being recorded.

**Candidate addition to §6.1.2, with a declaration item in §8.2.**

> Implementations SHOULD hold record-signing keys and anchor-submission credentials in a trust boundary
> that the recorded actor, and software running with the recorded actor's privileges, cannot use or modify.
> Profiles MUST require implementations to declare whether this separation is in place. Where it is not,
> records signed after a compromise of the recorded system cannot be distinguished by signature from
> records signed before it; only batches anchored before the compromise retain an independent reference
> (INT-006).

**Open points.**

1. "Trust boundary" is not yet a checkable term. A reviewable version needs examples of what does and does
   not count (a separate host, a separate OS user, a hardware-backed key, a TEE) and what evidence supports
   the declaration.
2. The declaration is a statement by the implementer. It is itself an assertion and should be reported as
   one (see 2.5).
3. The second part of F12 — an authenticated, dated declaration of key compromise and its effect on
   records before, within and after the affected interval — needs a design for the declarer, distribution
   and freshness, and is left for a later draft.

### 2.4 F9 — what a verification result does not answer

**Current text.** §4.1.3 returns a result about the records presented. §9.3 describes the Evidence Pack and
leaves its format to profiles. §1.6 states the limits on correctness, fairness, safety and legal compliance.

**Candidate informative note for §9.3.**

> A verification result under §4.1.3 concerns the records presented. It does not answer whether the
> recorded act was authorized, whether what was executed matches what was approved, or what state was
> observed and from where. A report on an Evidence Pack SHOULD state each of these separately and SHOULD
> mark each as not assessed where the pack carries no evidence for it. Acceptance of a credential or a
> valid signature is not evidence of authorization. Absence of a record is not evidence that an act did
> not occur.

**Open points.**

1. Five existing experiments make the same separation under different names (wallet authorization, payment
   API, cloud credential, the incident evidence assessor, and the two result dimensions of the
   declared-scope draft). A single vocabulary has not been chosen.
2. P1 reserves `VALID`, `INVALID` and `INDETERMINATE` for record verification. Results for the other
   questions need different words so that a cryptographic pass is not read as an answer to them.
3. Making this more than a note depends on the common Evidence Pack container deferred in CHANGE-001
   Annex C.

### 2.5 F7 — origin of a record

**Current text.** §4.2.2 has `actor` and `input.sources`; TRC-005 defines party roles for cross-party
provenance, which presupposes a prior arrangement between the parties.

**Candidate reservation in §4.2.2.** Reserve an OPTIONAL indication, per record, of how the recorded content
came to the producer:

- stated by the actor being recorded;
- observed by a component outside that actor's control;
- a counterparty record under TRC-005;
- imported from a party with which there was no prior arrangement;
- derived from other records;
- synthetic test data.

A signed indication of origin does not establish the observer's independence or the truth of what was
observed. No field name or encoding is proposed here.

**Open points.** The evidence needed to substantiate each class, the treatment of an unsupported claim (it
stays unresolved), and whether this belongs in the framework or in profiles (register F7).

## 3 Basis in the incident registry

Counts are from VSO's public registry at 88 records
([`incidents.json`](https://github.com/veritaschain/vcp-site/blob/591e68cf8fc480d0baeba24cbec68b8fcf084bfe/incidents/incidents.json),
as of 28 November 2026) and its classification file
([`vap-map.json`](https://github.com/veritaschain/vcp-site/blob/591e68cf8fc480d0baeba24cbec68b8fcf084bfe/incidents/vap-map.json)).
T1 to T13 are VSO's editorial labels, not specification identifiers. One record can carry several labels.

| Subject | Label | Records |
| --- | --- | --- |
| F7 | T1, whose record was it | 24 |
| F9, F11 | T5, a valid credential is not authorization | 24 |
| F13 | T8, secrets that entered a record | 9: V1020RAILWAY, V1026CAIRN, V1029CURSOR, V1104CHAINALYSIS, V1105AZURE, V1106WORKOS, V1110BARRACUDA, V1121TOGETHERAI, V1124MINIMAX |
| F12 | T6, code that ran ahead of, or with the same privileges as, the recording point | 7: V1026CAIRN, V1029CURSOR, V1105, V1115MICOLLAB, V1117AGENTFRAMEWORK, V1120CERTIN, V1123GT13CHECKPOINT |

Three of the seven T6 records were added between 24 and 27 November: an advisory stating that a
verification source must not be alterable through the same compromised environment (V1120CERTIN), a report
of an internal certificate authority being copied (V1123GT13CHECKPOINT), and a report of local logs edited
by an intruder with root (V1115MICOLLAB). That is the reason for bringing the first part of F12 forward.

**These counts are not evidence of need.** VSO selected and classified the incidents, most of the work was
AI-assisted, and 47 of the 88 records were verified in November 2026. Allegations in litigation records are
untested. In none of the 88 records did the Completeness Invariant (INT-008) decide the question; where
records were deleted or edited, they were records that had not been anchored.

## 4 What this draft does not change

- VAP has no monitoring, intervention or override role (§4.4.4). None of the candidate text detects, blocks
  or stops anything while a system is running.
- VAP places no obligation on an attacker's own systems. Nineteen of the 88 records carry the label for AI operated
  by an attacker (T10); for those, VAP can bear only on what the targeted party recorded itself.
- A record that was never made cannot be recovered (Appendix A, Pre-measurement drop), and a faithfully
  kept record of a false statement remains false.
- The §1.6 statement stands: conformance "does **not** warrant the correctness, fairness, or safety of the
  underlying AI decisions — only the integrity, completeness (at anchor granularity), and attributability
  of their records".

## 5 Compatibility

- No existing signed record, AnchorRecord, dataset or archive is rewritten.
- 2.1, 2.4 and 2.5 add no producer obligation. 2.2 and the declaration in 2.3 would be new obligations
  for producers and profiles if adopted.
- Released profile texts (VCP v1.2, CAP v1.0, CPP v1.4) are not changed by this draft. If any of this text
  were adopted, the effect on each profile would be handled through its own change control and a reissued
  conformance mapping (§10.4).
- VCP and VAP are separately governed. Nothing here opens, closes or decides a VCP proposal.

## 6 Decisions needed before a normative proposal

1. A formal proposal identifier and target version, under an operative change path
   ([governance/PROPOSED-CHANGE-PROCESS.md](../../governance/PROPOSED-CHANGE-PROCESS.md), section 1).
2. Whether the five subjects go forward together or separately, and their order relative to P1.
3. Resolution of the open points listed under each subject.
4. Review cases for each subject, with expected results, taken from the lists in register section 4.
5. Overlap with `draft-mih-scitt-agent-action-capsule` for F7 and F9. The IPR disclosures on file were
   read on 28 November 2026 and are recorded in [EXTERNAL-OVERLAP.md](EXTERNAL-OVERLAP.md); the
   non-assertion covenant they mention and sections 6 onward of the current revision were not read.

Any normative change follows VAP v1.2 §10.3, with a separate submission, public review, deliberation,
decision record and release.

## 日本語要約

**状態：検討用の草案。未採択、正式な提案番号なし、対象リリース未定。** リポジトリへの統合は採択を意味しません。

CHANGE-002 準備用登録簿の §4 が「正確な文言が要る」とする 8 項目（F7〜F14）のうち、新しいイベント種別・欄名・
ワイヤ形式・判定規則を足さずに、既存の条項への文言として書ける 5 項目について、文案を示します。

| 行 | 内容 | 文案の種類 | 条項 |
| --- | --- | --- | --- |
| F11 | attributable の定義。署名が、検証者が記録の外の信頼情報から確立した鍵で検証できることまでを指し、鍵を誰が制御していたか、行為が認可されていたか、法的責任は示さない | 定義 | §1.5、Appendix A |
| F13 | 再利用できる認証用の秘密値（パスワード、ベアラトークン、API キー、秘密鍵など）を、EventHash や Merkle の葉に入る欄に平文で入れない。資格情報は発行者が付けた非秘密の識別子で参照する | 提案要件 | §7 |
| F12 前半 | 記録の署名鍵とアンカー提出の資格情報を、記録される行為者と同じ権限で使えない信頼境界に置く（SHOULD）。分離の有無は宣言する（MUST） | 推奨と宣言 | §6.1.2、§8.2 |
| F9 | §4.1.3 の検証結果は提示された記録についてのもので、認可、承認と実行の一致、観測された状態には答えない。有効な署名や資格情報の受理は認可の証拠ではなく、記録の欠如は行為の不存在の証拠ではない | informative の注記 | §9.3 |
| F7 | 記録の内容がどこから来たか（行為者自身の申告、行為者の制御の外の観測、TRC-005 の相手方、事前の取り決めのない当事者からの取り込み、導出、合成）の任意の表示を予約する。欄名と符号化は提案しない | OPTIONAL の予約 | §4.2.2 |

根拠は VSO の公開レジストリ 88 件（2026-11-28 時点）の分類です。T ラベルは VSO の編集上の分類で、仕様の識別子
ではありません。件数は必要性の証拠ではありません。事件は VSO が選んで検証・分類したもので、作業の大半は AI の
支援によるものです。88 件のどれでも、Completeness Invariant（INT-008）が決め手になってはいません。

F12 の前半を先に出すのは、T6 の 7 件のうち 3 件（V1120CERTIN、V1123GT13CHECKPOINT、V1115MICOLLAB）が
11 月 24〜27 日に加わったためです。後半（鍵侵害の宣言）は、宣言の主体・配布・鮮度の設計が要るので扱いません。

この草案は、VAP に監視・介入・上書きの機能を足しません（§4.4.4）。攻撃者自身のシステムには何の義務も課さず、
記録されなかった事象を回復しません。§1.6 の非保証文はそのままです。既存の署名済み記録は書き換えません。
VAP の外部実装はゼロ、手続で受理された Evidence Pack はゼロです。

規範としての変更は、VAP v1.2 §10.3 の手続（提案、30 日の公開レビュー、審議、議決、リリース）に従います。
その経路はまだ運用されていません。
