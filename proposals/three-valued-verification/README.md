# Draft proposal for three-valued results in the core verification algorithms

**Status:** Discussion draft, not adopted. **Formal proposal number:** Unassigned.
**Draft revision:** 0.2. **Date:** 2026-10-25 JST. **Target release:** Undecided.
**Baseline:** VAP v1.2.0 Draft 3 at commit `99dae8353277cd3af86b2efb9a2bcc29e5a68924`.
**License:** CC BY 4.0 International. A Japanese summary follows the English text.

Repository integration of this discussion draft is not normative adoption. Its unadopted status,
unassigned identifier and undecided target release remain unchanged after merge.

This draft introduces no VAP v1.2 requirement, event type, field, wire-format change or conformance level.
Uppercase requirement words in section 3 express **proposed** requirements only.

## 1 Problem

[Section 4.1.3][s413] defines two normative algorithms. Both return only `VALID` or `INVALID`.

The batch-verification algorithm (Mechanism B) returns `INVALID: External anchor mismatch` whenever
`VerifyExternal(A, T)` does not succeed, and `INVALID: Anchor signature failure` whenever
`VerifySignature(A)` does not succeed. In practice those calls can fail to succeed for reasons that are
not a mismatch:

- the anchor proof or the audit path was not supplied;
- the anchor is pending (for example, a timestamp that has not yet been confirmed);
- the anchor target cannot be reached, or its class is not one the verifier's policy accepts;
- the signing key has not been established as the producer's key, or the algorithm is not supported;
- the policy identifier, count or range binding cannot be resolved from what was supplied.

A two-valued output forces each of these into one of two wrong answers. Reporting `INVALID` asserts
tampering where only material is missing. The opposite shortcut, skipping an unavailable check and
reporting `VALID`, asserts integrity that was never checked.

The second error has occurred in VSO's own reference code. On the default branch of
[`veritaschain/vcp-rta-reference`][rta-main] (commit `3d359dc`, VCP v1.1), the verifier does not check
Ed25519 signatures or the external anchor, treats the Merkle check as passed when no expected root is
supplied, and prints "All checks passed - VCP v1.1 Compliant". An unmerged branch,
[`cursor/vcp-verifier-three-valued-faf6`][rta-branch], replaces this with `VALID`, `INVALID` and
`UNVERIFIABLE` per check and records that the external anchor of that evidence pack cannot be verified
from the public materials.

## 2 Proposed result values

| Result | Meaning |
| --- | --- |
| `VALID` | Every required check was performed and matched. |
| `INVALID` | At least one required check was performed and did not match: a chain break, a hash or inclusion mismatch, a signature that fails against an established key, an anchor that commits to a different value, or a violated count, range or policy binding (INT-008). |
| `INDETERMINATE` | No required check returned `INVALID`, but at least one could not be performed with the material and trust information available. |

Precedence when combining checks: `INVALID` over `INDETERMINATE` over `VALID`.

`INDETERMINATE` is not a pass. It records that the question is open, and it can become `VALID` or
`INVALID` when the missing material or trust information becomes available.

The meanings follow the status indications of ETSI EN 319 102-1 for signature validation, clause 5.1:
TOTAL-PASSED, TOTAL-FAILED, and INDETERMINATE, where "the results of the performed checks do not allow
to ascertain" either of the other two. (Checked against Draft ETSI EN 319 102-1 V1.2.3, 2021-07; confirm
against the current published version before adoption.) The name `INDETERMINATE` is chosen over
`UNVERIFIABLE` to match that standard and the
[declared-scope proposal](../declared-scope-precommit/README.md), section 6, which already reports
cryptographic integrity as Verified, Failed or Indeterminate.

## 3 Proposed requirements

1. A verifier MUST return one of `VALID`, `INVALID` or `INDETERMINATE` for each required check and for
   the overall result, with the name of each check and a reason for every non-`VALID` result.
2. A verifier MUST NOT report `VALID` for a check it did not perform. A check that was skipped because
   its input was absent is `INDETERMINATE`.
3. A verifier MUST report `INVALID` only on a demonstrated mismatch. Absence of material, an unreachable
   or pending anchor, an unestablished key and an unsupported algorithm are `INDETERMINATE`.
4. A conformance claim, certification test or Evidence Pack review that requires verification MUST treat
   `INDETERMINATE` as not verified.
5. A verifier that claims to check INT-008 MUST report the count, range and policy bindings as a separate
   check. If they cannot be resolved, that check is `INDETERMINATE`, never `VALID`.
6. Missing input for one check MUST NOT cause an overall `INDETERMINATE` return before other
   independently executable required checks have been evaluated. Aggregate their results only after
   those checks have completed, retaining any demonstrated `INVALID` result.

### Revised Mechanism B (proposed text)

```
Algorithm: VAP Batch Verification
Input: Event E, audit path P, AnchorRecord A, anchor target T, verifier policy V
Output: VALID, INVALID or INDETERMINATE, with the result and reason of each check

1: inclusion, signature, external, completeness ← INDETERMINATE: anchor record missing
2: if A is present then
3:     if E is absent or P is absent then
4:         inclusion ← INDETERMINATE: event or audit path missing
5:     else
6:         inclusion ← VerifyInclusion(E, P, A, V)
7:     signature ← VerifySignature(A, V)          // independent of E and P
8:     external ← VerifyExternal(A, T, V)         // independent of E and P
9:     completeness ← CheckCompleteness(A)        // independent of the event's audit path
10: return Combine(inclusion, signature, external, completeness)
    // INVALID if any is INVALID; otherwise INDETERMINATE if any is INDETERMINATE; otherwise VALID
```

`VerifyInclusion` applies the existing proposed leaf/path computation
(`leaf = H(0x00 || canonical(E))`, `root = FoldAuditPath(leaf, P)`) and compares the computed root
with `A.merkle_root`, when the required input, algorithm and path interpretation are available.
Unsupported algorithms or unresolved prerequisites produce `INDETERMINATE`, not a silent pass.
This control-flow correction does not adopt or revise a profile's leaf encoding or proof format.

Each helper returns a result and, for a non-`VALID` result, a reason. `VerifySignature` returns
`INDETERMINATE` when the key is not established or the algorithm is unsupported; a signature
mismatch against an established key is `INVALID`. `VerifyExternal` reports `INVALID` for a
verified commitment to a different value, and `INDETERMINATE` for absent or pending proof, an
unreachable target, or a target not accepted by V. `CheckCompleteness` reports `INDETERMINATE`
when the count, range or policy binding cannot be resolved. Missing prerequisites affect only
checks that depend on them; available independent checks still run.

Presence is not a truthiness test: `P = []` is a supplied audit path, not an absent one. An empty
path can verify a single-leaf tree when the remaining tree context and root are consistent.
It must not automatically produce either `INDETERMINATE` or `VALID`.

#### Control-flow regression examples (informative)

These examples describe scheduling and aggregation, not cryptographic test vectors or evidence
of independent reproduction. `VALID` entries assume the corresponding check actually ran and matched.

| Supplied material / observation | Inclusion | Signature | External | Completeness | Overall |
| --- | --- | --- | --- | --- | --- |
| P absent; A present; signature mismatch against an established key; other checks match | INDETERMINATE | INVALID | VALID | VALID | INVALID |
| P absent; A present; all independently executable checks match | INDETERMINATE | VALID | VALID | VALID | INDETERMINATE |
| A absent | INDETERMINATE | INDETERMINATE | INDETERMINATE | INDETERMINATE | INDETERMINATE |
| P is an empty supplied path; consistent single-leaf tree; all checks match | VALID | VALID | VALID | VALID | VALID |
| E absent; A present; external commitment demonstrably differs; other checks match | INDETERMINATE | VALID | INVALID | VALID | INVALID |

### Hash chain validation

The chain algorithm keeps its `INVALID` cases. Two `INDETERMINATE` cases are added: the hash algorithm
named by the events is not supported, and the verified segment does not start at genesis and the hash of
the event before it was not supplied (the first link cannot be checked). A gap inside the supplied
sequence remains `INVALID` for that sequence; whether events were withheld or never written is a
separate question that this result does not answer.

### Reason codes (informative, provisional)

`MISSING_AUDIT_PATH`, `MISSING_ANCHOR_RECORD`, `MISSING_ANCHOR_PROOF`, `ANCHOR_PENDING`,
`ANCHOR_TARGET_UNREACHABLE`, `ANCHOR_TARGET_NOT_ACCEPTED`, `KEY_NOT_ESTABLISHED`,
`ALGORITHM_UNSUPPORTED`, `PRIOR_HASH_MISSING`, `BINDING_UNRESOLVED`. These names are proposals for
discussion. They are not registered identifiers.

## 4 What this does not change

- No event, field, wire format or conformance level changes. Producers are unaffected.
- `INDETERMINATE` does not relax INT-008 or any other check. It replaces silent passes and false
  failures with an explicit open result.
- It does not make an event that was never recorded detectable (Appendix A, *Pre-measurement drop*).
- It does not say whether an underlying AI decision was correct, fair or safe (§1.6(c)).

## 5 Open questions

1. Whether VCP and the other profiles adopt the same values, and in which version.
2. Whether certification test suites must include `INDETERMINATE` fixtures for each reason code.
3. How long a pending anchor may stay `INDETERMINATE` before a profile treats it as a failure of the
   producer's anchoring obligation (INT-006, INT-007). That is a producer-conformance question, distinct
   from the verification result.
4. Whether the editorial verdicts VSO uses for incident verification (`UNVERIFIABLE` for a source that
   could not be retrieved) should be renamed for consistency. They concern sources, not cryptographic
   checks, and this proposal does not change them.

## 日本語要約

VAP v1.2 §4.1.3 の2つの検証アルゴリズムは `VALID` か `INVALID` しか返さない。Mechanism B は、外部アンカーの
証明がない、確定待ち、アンカー先に到達できない、鍵が確立していない、といった「確かめられない」状態も
`INVALID`（不一致）として返す。逆に、確かめられない検査を飛ばして `VALID` とする実装も生まれる。
VSO の vcp-rta-reference の main（VCP v1.1）の検証器は、署名と外部アンカーを検査せず、期待する Merkle 根が
与えられないと比較なしで合格とし、「All checks passed - VCP v1.1 Compliant」と表示する。

本案は結果を `VALID`／`INVALID`／`INDETERMINATE` の3値にする。`INVALID` は不一致を実際に示せた場合に限り、
材料の欠如・確定待ち・到達不能・鍵未確立・未対応アルゴリズムは `INDETERMINATE` とする。優先順位は
`INVALID`、`INDETERMINATE`、`VALID` の順。`INDETERMINATE` は合格ではなく、適合主張・認証試験・Evidence Pack の
審査では「未検証」として扱う。意味は ETSI EN 319 102-1 §5.1 の TOTAL-PASSED／TOTAL-FAILED／INDETERMINATE に
揃え、宣言スコープ提案（§6）の Verified／Failed／Indeterminate とも整合させる。イベント・フィールド・
ワイヤ形式・適合レベルは変えない。採択されていない議論用の草案である。

2026-10-25 の草案修正では、監査経路などが欠けた時点で全体を早期終了する処理を除いた。
不足する入力に依存する検査だけを `INDETERMINATE` とし、実行可能な署名・外部アンカー・完全性の検査を
続けてから集約する。既知の不一致を、別の入力不足によって隠してはならない。空の監査経路 `[]` は
未提供と区別し、整合する単一葉の木であれば包含検証を実行する。5つの説明例は制御フローの確認用であり、
暗号学的試験や独立再現の成立を示すものではない。規範本文・既存実装・固定配布物は変更しない。

[s413]: https://github.com/veritaschain/vap-spec/blob/99dae8353277cd3af86b2efb9a2bcc29e5a68924/spec/v1.2/VAP_Framework_Specification.md#413-sequence-verifiability-mechanisms
[rta-main]: https://github.com/veritaschain/vcp-rta-reference/blob/3d359dce3be479632d41e4dee74c7f102766e202/tools/verifier/vcp_verifier.py
[rta-branch]: https://github.com/veritaschain/vcp-rta-reference/tree/cursor/vcp-verifier-three-valued-faf6
