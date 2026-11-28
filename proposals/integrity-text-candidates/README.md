# Draft candidate text for three core repair questions (`bind`, Ed25519 input policy, numeric representation)

**Status:** Discussion draft, not adopted. **Formal proposal number:** Unassigned.
**Draft revision:** 0.1. **Date:** 2026-11-28 JST. **Target release:** Undecided.
**Baseline:** VAP v1.2.0 Draft 3 at commit `34d53e166d3da9ce29963b6a5fc1d6b1c454db51`,
specification SHA-256 `a35d5e082fd4b2f9921a78b1a71df263018320375e09fa18cf81533a18a19998`.
**License:** CC BY 4.0 International. A Japanese summary follows the English text.

Repository integration of this discussion draft is not normative adoption. Its unadopted status,
unassigned identifier and undecided target release remain unchanged after merge.

This draft introduces no VAP v1.2 requirement, event type, field, wire-format change, algorithm or
conformance level. Uppercase requirement words in sections 2 to 4 express **proposed** requirements only.

**Origin and limits of this draft.** The text was prepared with AI assistance (Claude, Anthropic) on
28 November 2026. It is first-party work and has not been independently reviewed. VAP has no external
implementation and no Evidence Pack accepted in any proceeding.

## 1 Purpose and scope

Section 3 of the [CHANGE-002 preparation register](../CHANGE-002-CANDIDATES.md) lists five core repair
questions that "need exact text". [Three-valued verification](../three-valued-verification/README.md) (P1)
already has a draft. This draft supplies candidate text for three of the remaining four:

| Register row | Clause | Section here |
| --- | --- | --- |
| Meaning and bytes of `bind` | INT-008, §4.1.3, §7.5 | 2 |
| Ed25519 key and signature input policy | §4.1.5, §6.1.2 | 3 |
| Numeric representation, with question Q-a | §7.2, §7.3, §7.5 | 4 |

P-256 / ES256 is not addressed. The register requires a separately reviewed algorithm-registry proposal
for it, and no algorithm is added here.

The results named below (`VALID`, `INVALID`, `INDETERMINATE`) are the proposed values of P1. If P1 is
not adopted, the text in this draft has to be restated in v1.2's two values, and the cases marked
`INDETERMINATE` have no accurate expression.

**The framework is an abstract schema.** §7.5 is headed "abstract schema" and profiles define wire
formats. The candidate text therefore states what must be covered and what a profile must publish; it
does not fix one byte layout for all profiles. That is a real limit: two profiles could satisfy this text
with different bytes, and the IETF 127 observations (register §5, E4 to E7) show that such differences are
found only when a second party writes a verifier.

## 2 `bind` and the AnchorRecord signature

**Current text.** INT-008: "Each AnchorRecord MUST bind, at minimum: event count, first/last event
identifiers, and the policy identifier under which the batch was produced". §7.5 lists those members under
`batch` and a `security.signature`, and does not say which bytes the signature covers. §4.1.3 Mechanism B
calls `VerifySignature(A)` and `CheckCompleteness(A)` without defining either. Appendix A describes the
AnchorRecord as a "Signed record binding a Merkle root, batch scope, and external anchor proof".

**Problem.** An implementation that signs the Merkle root alone satisfies the letter of §7.5. Its
`event_count`, `first_event_id`, `last_event_id` and `policy_id` can then be changed without invalidating
the signature. The same question is open in VCP (VCP-CP-2026-003 and -004, both Draft).

**Candidate text.**

> **Bound.** A value is *bound* by an AnchorRecord when it is part of the byte string over which the
> AnchorRecord signature is computed. A value that the record carries outside that byte string is not
> bound, whatever the record's schema calls it.
>
> **Signed statement.** The AnchorRecord signature MUST be computed over a byte string that begins with a
> domain-separation prefix reserved for AnchorRecord signatures and continues with the canonical form
> (§7.3) of a statement containing, at minimum: `anchor_record_id`; every member of `batch`
> (`merkle_root`, `event_count`, `first_event_id`, `last_event_id`, `policy_id`); the hash and signature
> algorithm identifiers; `signer_id`; `timestamp_int`; and the `type` and `identifier` of the intended
> anchor target. The signature value and any external anchor proof or receipt MUST NOT be part of the
> signed statement. A signature computed over the Merkle root alone does not satisfy INT-008.
>
> **External commitment.** The value committed to the external anchor target MUST be derived from the
> signed statement together with its signature, under a second domain-separation prefix, so that an
> anchor proof refers to one statement and one signature and never to a preimage that contains the
> proof itself.
>
> **Profile obligation.** A profile MUST publish the exact domain-separation prefixes, the members of its
> signed statement and their canonical form, and test vectors from which a
> third party can recompute the signed bytes, the signature input and the external commitment.
>
> **Checking the binding.** A verifier that reports the Completeness Invariant MUST compare the bound
> `event_count`, `first_event_id` and `last_event_id` with the batch it was given, and the bound
> `policy_id` with the `policy.policy_id` of each event it was given. If the full batch was not supplied,
> the count and range checks are `INDETERMINATE`. A demonstrated difference is `INVALID`. A verifier MUST
> NOT report these checks as passed on the basis of the signature alone.

**Open points.**

1. Whether a batch may contain events under more than one `policy_id`. The candidate text assumes one.
2. A digest of the policy document is not included here. Binding the policy text belongs with the
   declared-scope draft (P2).
3. Whether `timestamp_int` in the statement is the signer's claimed time only. An external anchor's
   time is separate evidence and should be reported separately.
4. Hybrid signatures (`pqc_signature`): whether both signatures cover the same statement bytes.
5. Receipts from a transparency service (register §5, Q-b): what an Evidence Pack must carry so that a
   receipt can be checked without the issuing service. Not addressed.
6. Existing AnchorRecords signed over the root alone are not rewritten. How a verifier reports them
   (the count, range and policy checks cannot pass) needs a migration statement per profile.

**Alignment with VCP.** VCP-CP-2026-004 section 4 proposes a protected statement, an outer signature and
detached receipts, with a commitment over statement plus signature. The candidate text above is the
framework-level statement of the same structure. VCP and VAP are separately governed; nothing here
decides a VCP proposal, and neither draft is adopted.

## 3 Ed25519 key and signature input policy

**Current text.** §4.1.5 and §6.1.2 name Ed25519 as the default signature algorithm. Neither says which
public keys or signature encodings a verifier accepts.

**Problem.** RFC 8032 section 5.1.7 requires decoding the public key and the signature and checking that
the scalar S is in range; it does not require rejecting small-order public keys. With a small-order key
and a matching degenerate signature, some backends accept any message. The repository's demo verifier
accepted such a fixture until explicit checks were added on 11 November 2026; the published tag
`vap-interop-demo-v0.2.0` does not contain them. That repair is a local demo requirement and is not
framework text.

**Candidate text.**

> A verifier of an Ed25519 signature MUST, before evaluating the signature equation:
>
> 1. reject a public key or a signature point R whose encoding is not canonical (the encoded y
>    coordinate is not less than 2^255 − 19, or the sign bit is set when x is zero);
> 2. reject a public key or a signature point R that is one of the eight points of small order;
> 3. reject a signature whose scalar S is not less than the group order L.
>
> A public key that fails checks 1 or 2 MUST NOT be accepted as a signer key, a trust anchor or an
> anchoring key, and a producer MUST NOT publish one. A verifier MUST NOT treat a public key as
> established because it is carried in the same input as the record it is meant to verify.
>
> These checks are additional to RFC 8032 and do not establish that a key belongs to the prime-order
> subgroup.

**Open points.**

1. The result when a supplied trust file contains a key that fails these checks. The candidate reading
   is `INVALID` for a signature under that key, because the failure is demonstrated and not a missing
   input; a reviewer may prefer a distinct reason code.
2. Cofactored versus cofactorless verification (RFC 8032 section 8.8). Implementations can disagree on a
   signature that passes the checks above. Whether the framework fixes one equation is undecided.
3. Corresponding rules for ECDSA secp256k1 (encoding, low-S) are not drafted.
4. Backend independence: the checks must be made on the decoded bytes by the verifier itself, since
   libraries differ (the demo record notes one runtime version accepting and another rejecting the same
   fixture).

**Existing material.** `interop/vap-evidence-pack-demo/CONFORMANCE.md` section 1.1 and
`interop/vap-evidence-pack-demo/security-vectors/` (local to the demo contract);
`experiments/ed25519-key-admission/` (local to the payment and cloud experiments).

## 4 Numeric representation and invalid input

**Current text.** §7.2: "All numeric values MUST be encoded as string type." §7.3 requires RFC 8785.
The abstract schemas in §7.1 and §7.5 type several members as `int64`, `int32` or `uint8`
(`timestamp_int`, `event_count`, `effective_date`, `merkle_index`, `event_type_code` and others).
Register question Q-a(i) asks whether those members are strings under §7.2.

**Problem.** RFC 8785 serializes JSON numbers as IEEE 754 double precision, so an `int64` nanosecond
timestamp written as a JSON number cannot be canonicalized exactly. The IETF 127 materials record four
canonicalization implementations disagreeing on integers of 2^53 or more, a byte order mark, duplicate
members and deep nesting, and two verifiers of one project disagreeing on one number written two ways.

**Candidate text.**

> **Type names.** The names `int64`, `int32`, `uint8` and the like in §7.1, §7.4 and §7.5 state the
> value domain of a member. They do not state its JSON type.
>
> **Framework-defined members.** In any serialization that enters an EventHash or an AnchorRecord signed
> statement, a framework-defined member with an integer value domain MUST be a JSON string holding the
> decimal form of the integer: `0`, or a non-zero ASCII digit followed by ASCII digits, preceded by `-`
> only where the member's domain includes negative values. A plus sign, leading zeros, whitespace, a
> decimal point and an exponent MUST NOT appear. `-0` MUST NOT appear.
>
> **Profile-defined members.** A profile MUST declare, for each numeric member it defines, its value
> domain and its JSON representation. A non-integer value MUST be a string in a lexical form the profile
> specifies exactly. A JSON number MAY be used only for an integer whose declared domain lies within
> −(2^53 − 1) to 2^53 − 1.
>
> **Input a verifier does not repair.** A verifier MUST NOT canonicalize, and MUST report as `INVALID`
> for the affected record, a serialization that contains: a byte order mark; an object with duplicate
> member names; ill-formed UTF-8; a JSON number outside the range above or with a fraction or exponent
> where the member's declared representation is an integer; or a string that does not match the member's
> declared lexical form. A verifier MUST NOT normalize such input and then verify the normalized form.
> Input that exceeds a limit of the verifier itself, such as its maximum nesting depth, is
> `INDETERMINATE`, and the verifier MUST state the limit.

**Open points.**

1. **Compatibility.** This is the reading of §7.2 as written, applied to the members §7.5 types as
   `int64`. Existing serializations that write those members as JSON numbers would not satisfy it, and
   changing a member's JSON type changes hash inputs. No existing signed bytes are rewritten; each
   profile needs its own inventory and migration statement. VCP-CP-2026-004 section 5 prefers decimal
   strings for the same members and treats the change as requiring explicit approval and migration.
2. **Alternative.** Keep JSON numbers for framework integers and restrict their domain to the safe
   integer range, changing timestamp units. That keeps wire types and gives up nanosecond `int64`
   timestamps. This draft prefers strings; the choice is the reviewer's.
3. Booleans, `null` and enumerations are unaffected. Whether `timestamp_iso`, where present, must agree
   exactly with `timestamp_int` is not addressed.
4. A maximum nesting depth and a maximum input size are left to profiles. Whether the framework sets a
   floor is undecided.
5. References between records (register §5, Q-c): whether a reference such as
   `erasure_target_event_ids` should also carry the target's `event_hash` and hash algorithm, and the
   result when the target is missing. Not drafted; under P1 a missing target would be `INDETERMINATE`.

**Order of work (register §5, Q-d).** Shared boundary vectors in at least two languages should be written
after this text is fixed. Built first, they would record one implementation's behaviour and not the
specification's. No vectors are supplied with this draft for that reason.

## 5 What this draft does not change

- No normative text, CHANGE-001, profile, dataset, signed artifact or experiment.
- VAP has no monitoring, intervention or override role (§4.4.4); nothing here adds one.
- A valid signature under an admitted key shows that the signed statement was signed with that key. It
  does not show who controlled the key, that the statement is true, or that the batch contains every
  event that occurred (§1.6; Appendix A, Pre-measurement drop).
- VCP v1.2, CAP v1.0 and CPP v1.4 are not changed.

## 6 Decisions needed before a normative proposal

1. An operative change path ([governance/PROPOSED-CHANGE-PROCESS.md](../../governance/PROPOSED-CHANGE-PROCESS.md),
   section 1) and a formal identifier.
2. Whether P1 is adopted first. Sections 2 to 4 depend on its third value.
3. The numeric choice in section 4 (strings, or JSON numbers within the safe integer range).
4. Whether the framework fixes domain-separation prefixes itself or leaves them to profiles.
5. Order relative to VCP-CP-2026-003 and -004, so that the parent definition is not written to fit a
   child decision after the fact.
6. Vectors, written by more than one party, after the text is fixed.

Any normative change follows VAP v1.2 §10.3.

## Sources

- RFC 8032, sections 5.1.3, 5.1.7 and 8.8: <https://www.rfc-editor.org/rfc/rfc8032>
- RFC 8785: <https://www.rfc-editor.org/rfc/rfc8785>
- RFC 7493 (I-JSON): <https://www.rfc-editor.org/rfc/rfc7493>
- IETF 127 materials: listed in [register §5](../CHANGE-002-CANDIDATES.md)
- VCP-CP-2026-004 draft: <https://github.com/veritaschain/vcp-spec/blob/03bbfe5f68ec9a81f32108146a3ebe43d0800541/proposals/integrity-2026-10-24/normative-change-draft.md>

## 日本語要約

**状態：検討用の草案。未採択、正式な提案番号なし、対象リリース未定。** リポジトリへの統合は採択を意味しません。

CHANGE-002 準備用登録簿の §3 が「正確な文言が要る」とする中核の修正のうち、三値化（P1）以外の 3 点について文案を
示します。P-256／ES256 は扱いません。

| 項目 | 文案の要点 |
| --- | --- |
| `bind` と AnchorRecord の署名（INT-008、§7.5） | 「束縛される」とは、AnchorRecord の署名が計算されるバイト列に含まれること。署名は、専用の領域分離の接頭辞と、識別子・`batch` の全メンバー・アルゴリズム識別子・`signer_id`・`timestamp_int`・アンカー先の種別と識別子を含む文の正準形に対して行う。Merkle 根だけへの署名は INT-008 を満たさない。外部へのコミットは「文＋署名」から導く。プロファイルは接頭辞・対象メンバー・再計算できるベクタを公表する。検証器は件数・先頭と末尾・ポリシー識別子を実際のバッチと照合し、バッチ全体がなければ `INDETERMINATE` とする |
| Ed25519 の鍵・署名入力（§4.1.5、§6.1.2） | 署名式の評価の前に、非正準のエンコード、位数の小さい 8 点（公開鍵と R）、範囲外の S を拒否する。記録と同じ入力に入っている公開鍵を、それだけで確立された鍵として扱わない。RFC 8032 への追加であり、素数位数の部分群への所属は示さない |
| 数値表現（§7.2、§7.3、§7.5） | `int64` などは値の範囲の名前で、JSON の型ではない。枠組みが定める整数メンバーは 10 進の文字列（符号は負のときだけ、先頭の 0・小数点・指数は不可）。プロファイル定義のメンバーは表現を宣言し、JSON の数値は ±(2^53−1) の整数に限る。BOM、重複メンバー、不正な UTF-8、範囲外や形式違いの数値は直さずに `INVALID`、検証器自身の上限を超えた入力は `INDETERMINATE` |

主な未決事項：P1 が先に採択されるか（本草案は第三の値に依存します）。数値を文字列にするか、安全な整数の範囲に
制限した JSON の数値にするか。領域分離の接頭辞を枠組みが決めるかプロファイルに委ねるか。VCP-CP-2026-003／004
との順序。既存の署名済みバイト列は書き換えません。プロファイルごとに棚卸しと移行の記述が要ります。

共通の境界ベクタは、文言が固まってから 2 つ以上の言語で書きます（登録簿 §5 の Q-d）。先に作ると、仕様ではなく
1 つの実装の挙動を固定してしまうため、本草案にはベクタを付けていません。

VAP の外部実装はゼロ、手続で受理された Evidence Pack はゼロです。規範としての変更は VAP v1.2 §10.3 に従います。
