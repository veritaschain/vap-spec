# CHANGE-002 preparation register — candidate work only

**Status: administrative discussion draft; not a formal change proposal or adoption record.**
**Prepared:** 11 November 2026 (JST). **Target release:** undecided.
**Scope assignment, formal proposal identifiers and authorized reviewer:** unresolved.

This register makes the existing work reviewable without assigning it to
`VSO-VAP-CHANGE-002`. That identifier appears in
[CHANGE-001 Annex C](../spec/v1.2/VSO-VAP-CHANGE-001.md) for deferred work;
it must not be silently reused for a different omnibus proposal. Reconciliation
with the maintainer's complete register is still required. Row labels below
are local navigation aids, not formal proposal numbers.

Baseline reviewed: VAP v1.2.0 Draft 3 at repository
[`1ce71a66f55d9a20728213b7c3a8bb79270ae579`][baseline], specification SHA-256
`a35d5e082fd4b2f9921a78b1a71df263018320375e09fa18cf81533a18a19998`.
No normative specification, CHANGE-001, profile registry, frozen dataset,
signed archive or prior adoption record is changed by this register.

## 1. Subjects already deferred in CHANGE-001

| Row | Existing reference | Deferred subject | Preparation still needed |
| --- | --- | --- | --- |
| D1 | Annex C.1 | Assess generalizing later VCP evidence-bundling, clock-evidence, change/configuration and related regulatory-evidence constructs | Pin actual final VCP sources; distinguish published constructs from the historical working-draft list; decide framework versus profile scope |
| D2 | Annex C.2 | Consider elevating INT-005 signatures from SHOULD to MUST | Assess TEE-only and constrained-device cases, compatibility, signature formats and profile impact |

The current normative obligations remain unchanged while these subjects are
deferred. Mention in Annex C is not accepted replacement text.

## 2. Twelve current proposal directories

All entries below remain **unadopted**. This directory inventory does not make
them twelve formal change proposals or assign any to CHANGE-002. Each proposal's
own dated baseline, experiments and preserved artifacts remain authoritative
for what it actually contains.

| Row | Source | Current kind | Proposed disposition to review |
| --- | --- | --- | --- |
| P1 | [Three-valued verification, revision 0.2](three-valued-verification/README.md) | Unnumbered discussion draft | Candidate core algorithm amendment; evaluate `INVALID > INDETERMINATE > VALID` with exact replacement clauses and missing-input tests |
| P2 | [Declared scope and advance commitment, revision 0.1](declared-scope-precommit/README.md) | Unnumbered discussion draft | Separate present INT-008 batch binding from a proposed advance expected-set commitment; assess trust, timing and omission boundaries |
| P3 | [Incident-derived evidence bindings](incident-evidence-bindings/README.md) | Informative discussion and local experiments | Identify reusable evidence relationships; do not import incident-specific assumptions into normative requirements without review |
| P4 | [Cloud workload credential evidence](cloud-credential-evidence/README.md) | Informative design and local experiments | Review key/workload/permission, observation and session-state bindings for possible profile or capability work |
| P5 | [Payment API authorization evidence](payment-api-evidence/README.md) | Informative design and bounded local pilots | Review exact request/authorization/execution/recovery bindings, keeping evidence and enforcement separate |
| P6 | [Wallet authorization evidence](wallet-authorization-evidence/README.md) | Informative proposal and experiment | Review delegation and wallet-specific semantics without adopting DAP or a generic wallet profile |
| P7 | [School AI alerts and evaluation configuration](school-ai-evaluation-evidence/README.md) | Informative design proposal | Review disclosure, alert handling and observed isolation evidence; no school or provider deployment is asserted |
| P8 | [Consumer-agent evidence](consumer-agent-evidence/README.md) | Informative design discussion | Review mandates, commercial disclosures, actions and retention evidence; no regulatory obligation or generic mandate schema is adopted |
| P9 | [Legal AI Profile (LAP)](legal-ai-profile/README.md) | Related external proposal, labelled VAP-LAP by its proposer | Separate possible profile-registration decision; outside the current §4.5.2 profile list |
| P10 | [Evidence for AI-assisted software changes](ai-assisted-change-evidence/README.md) | Informative research proposal and local experiment | Review the artifact, target, baseline, test, approval-condition and outcome bindings for reuse of existing core evidence relationships; no software-change profile, event code or Evidence Pack format is adopted |
| P11 | [Candidate text for five core subjects, revision 0.1](core-text-candidates/README.md) | Unnumbered discussion draft | Candidate wording for F7, F9, F11, F13 and the first part of F12 (section 4 below); review the open points listed under each subject before any of it is treated as replacement text |
| P12 | [Candidate text for three core repair questions, revision 0.1](integrity-text-candidates/README.md) | Unnumbered discussion draft | Candidate wording for the meaning and bytes of `bind`, the Ed25519 key and signature input policy, and numeric representation with Q-a (section 3 and section 5 below); depends on the third value proposed in P1; no vectors until the text is fixed |

Row P10 was added on 21 November 2026 (JST). The directory was merged on
19 November 2026 ([vap-spec #75](https://github.com/veritaschain/vap-spec/pull/75)), after this
register was prepared; the register's baseline and the other rows are unchanged.
Whether P10 is handled as acceptance material for core work or as a separate
candidate has not been decided.

Row P11 was added on 28 November 2026 (JST). It is not a new subject: it holds
candidate wording for five of the subjects already listed in section 4, and those
subjects remain unadopted and unnumbered. The section 4 entries are unchanged.

Row P12 was added on 28 November 2026 (JST). It holds candidate wording for three
of the questions in section 3. Those questions remain open; section 3 is unchanged.
P-256 / ES256 is not covered by P12.

## 3. Core repair questions that need exact text

These questions are candidate review work, not settled changes:

| Question | Current clause to inspect | Required review material |
| --- | --- | --- |
| Three-valued verification | §4.1.3 | Explicit missing/unsupported input versus demonstrated mismatch rules; check aggregation; SDK/profile compatibility |
| Meaning and bytes of `bind` | INT-008 and §7.5 | Exact signed transcript, domain separation, included/excluded fields, canonical bytes, count/range/policy binding and independently recomputable vectors |
| P-256 / ES256 | §4.1.5 and §6.1.2 | A separately reviewed algorithm-registry proposal, curve/algorithm identifiers, signature encoding, validation policy and migration effects; no algorithm is added here |
| Numeric representation | §7.2 and §7.3 | Exact field domains and canonicalization rules; boundary vectors across languages; consequences for historical signed bytes |
| Ed25519 key and signature input policy | §4.1.5 and §6.1.2 | A reviewed framework-level policy and backend-independent acceptance criteria; a repair in the experimental interop demo is not normative adoption |

Do not use an experimental verifier PASS as evidence that these normative
questions have been resolved. Existing fixed evidence may remain
indeterminate, and external implementations and independent execution need
their own attributable records.

## 4. Additional subjects raised in the 11 November follow-up

**Status for every subject below: unadopted, unnumbered candidate work.**
The source for this addition is the maintainer's 11 November 2026 follow-up,
which lists eight omitted subjects as items 7–14 of a 10 November review.
The original `claude/VSO-REVIEW_事件総括_VAP組み込み提案_2026-11-10.md`
was not available in the reviewed checkout or supplied local source files.
The labels and ordering below preserve that supplied list; they are not an
independent reconstruction of the original report. Its exact wording, item
mapping and intended scope still need reconciliation with the source.

`F7`–`F14` are navigation labels only. The clause references identify existing
text to inspect, not clauses already amended. The decisions and tests below
are proposed preparation work; no fields, enums, wire formats or verdict rules
are adopted by this inventory.

### F7. Distinguishing evidence origins (出所の区別)

- **Existing text to inspect:** §1.5 Provenance; §4.2.2 `actor` and
  `input.sources`; §4.3.2 TRC-005 party roles; §9.3 Evidence Pack.
- **Question and rationale:** distinguish a producer's assertion, an external
  observation, a derived result and synthetic test data. A signed role label
  does not by itself establish the observer's independence or the truth of
  the observation.
- **Preparation required:** define source/control relationships, the evidence
  needed to substantiate each classification, derivation references, and which
  declarations are signed. Decide framework versus profile scope.
- **Review evidence:** cases with missing origin information, a producer
  relabelled as an independent observer, a derived result without its source,
  and synthetic data presented as an observed incident. Unsupported origin
  claims must remain explicitly unresolved under any proposed policy.

### F8. Resolution invariant (解決不変量)

- **Existing text to inspect:** §4.2.2 `outcome.status`; §4.3.2 TRC-005
  reconciliation states; §5.4's informative reference to OAP attempt closure;
  §9.3. These are not already a common resolution invariant.
- **Question and rationale:** confirm what the original report intends to
  resolve. One candidate is a declared action, attempt or request being linked
  to an evidenced outcome or an explicit unresolved state, rather than silently
  disappearing when no successful artifact is produced.
- **Preparation required:** identify the quantified population, stable
  identities, allowed transitions, closure evidence, time boundaries and
  conflict rules. Distinguish attempt closure from completeness, issue
  disposition and record correction; reconcile overlap with P2 before choosing
  exact invariant text.
- **Review evidence:** missing, duplicate, conflicting, late and timeout
  outcomes; an attempted action with no resulting artifact; and an unsupported
  claim that an unresolved action is resolved. Expected verdicts remain to be
  specified, not inferred from a successful signature check.

### F9. Evaluation dimensions (評価次元)

- **Existing text to inspect:** §1.6 non-guarantees; §4.1.3 verification
  procedures; §8.1 levels; §9.3 Evidence Pack; P1's proposed verdict model.
- **Question and rationale:** establish which dimensions an assessment reports
  separately, such as record integrity, bounded completeness, attribution,
  evidence availability and the truth or quality of the recorded assertion.
  Passing a cryptographic dimension must not silently answer a different one.
- **Preparation required:** define the chosen dimensions, their evidence
  requirements, unsupported/not-assessed treatment, aggregation and reporting
  rules. Reconcile those rules with P1 and §1.6's correctness, fairness, safety
  and legal-compliance limits.
- **Review evidence:** valid signatures over a false assertion, complete
  commitments with unavailable underlying content, unsubstantiated independence
  claims, and mixed passed/failed/unknown dimensions. Include assertions that
  the resulting report does not promote unassessed dimensions to success.

### F10. Deployments without a domain profile (プロファイルなしの配備)

- **Existing text to inspect:** §3.1's mandatory layers; §4.5 and §4.6.3;
  §7.1's `profile` and policy objects; §8.1–§8.2; §9.3's profile-defined format.
- **Question and rationale:** reconcile a possible framework-only deployment
  with mandatory profile identifiers and the parameters currently delegated to
  profiles. The name VAP-Core alone does not settle those requirements.
- **Preparation required:** decide whether and under what conditions such a
  deployment is permitted, what it may claim, and where its event schema,
  sequence-mechanism matrix, anchoring intervals and evidence format come from.
  Specify migration and unknown-policy handling; do not invent an implicit
  registered profile or silently fill missing fields.
- **Review evidence:** absent, empty, unknown and version-mismatched profile
  declarations; missing delegated parameters; and an experimental deployment
  claiming an established conformance level without the necessary policy.

### F11. Meaning of attributable (attributable)

- **Existing text to inspect:** §1.5–§1.6; §4.4 actor/responsibility records;
  §6.1.2 signatures; §7.1 signer identifiers; §7.5 AnchorRecord.
- **Question and rationale:** distinguish verification under a supplied key,
  a supported binding of that key to an actor or delegated role, and a legal
  determination of responsibility. These require different evidence.
- **Preparation required:** define the term's scope, trust inputs, identity and
  delegation bindings, temporal validity and report language. Coordinate key
  compromise treatment with F12; a cryptographically valid statement is not a
  decision about who bears legal responsibility.
- **Review evidence:** valid signatures with an untrusted actor mapping,
  ambiguous operator identifiers, expired delegation and rotated keys. Specify
  how each limits the attributable claim without rewriting signed history.

### F12. Key-compromise declarations (鍵侵害宣言)

- **Existing text to inspect:** §4.1.5 agility; §6.1.2; §7.1 `signer_id`;
  §7.5 signed AnchorRecords; §9.3 supplied public keys and policies.
- **Question and rationale:** define how verifiers receive and assess a claim
  that a signing key was compromised, including uncertainty about the affected
  interval. A declaration must not erase historical evidence or automatically
  establish when compromise actually began.
- **Preparation required:** decide the authorized declarer, authenticated
  encoding, affected key/role/scope, observation versus estimated compromise
  times, distribution and freshness rules, and the effect on old/new
  assessments. Distinguish compromise, revocation, expiry and ordinary rotation.
- **Review evidence:** forged or conflicting declarations; unknown compromise
  time; records before, within and after the claimed interval; stale trust
  information; and later reassessment preserving the original signed bytes.

### F13. Secret values in evidence (秘密値)

- **Existing text to inspect:** §4.2.2 inputs/context; §6.3 and §7.4 erasure;
  §7.1 event structure; §9.3 Evidence Pack disclosure and offline verification.
- **Question and rationale:** define the treatment of credentials, private keys
  and other secret payload values in collected and exported evidence without
  turning absence or redaction into a verified assertion about their contents.
- **Preparation required:** specify collection/exclusion rules, redaction and
  encryption metadata, commitment construction, access/retention boundaries,
  and how the signed transcript and verification scope represent withheld
  values. Assess disclosure risks, including guessing attacks on low-entropy
  values; use synthetic secrets for all proposed test material.
- **Review evidence:** secret-bearing input and export paths, unauthorized
  disclosure, redacted/missing/erased content, and altered commitments. Require
  explicit limits for checks that need unavailable plaintext; do not regenerate
  or silently repair historical signatures.

### F14. Replacement of a decision (判断の置き換え)

- **Existing text to inspect:** §1.6; §4.3 causal relationships;
  §4.4.3 `override_history`; §4.4.4's record-only oversight scope.
- **Question and rationale:** reconcile the original report's intended scope:
  decision supersession, substitution by a downstream actor, or both. Records
  of a later override/correction must be distinguishable from the earlier
  decision and from evidence that the replacement was actually executed.
- **Preparation required:** define links to the original and replacement,
  actor/authority, reason, time and outcome, including conflicting replacements
  and partial execution. Preserve original records and causal history; this
  candidate does not give VAP decision-making or intervention capability.
- **Review evidence:** authorized and unauthorized replacements, conflicting
  overrides, a replacement recorded but never executed, and attempts to replace
  an earlier signed record in place. Specify the evidence needed to determine
  an applicable decision without claiming its substantive correctness.

## 5. External interoperability observations, IETF 127 (14–20 November 2026)

**Status for every item below: unadopted, unnumbered candidate review material.**
Source: VSO's 20 November 2026 (JST) check of its weekly standards brief against
the primary materials listed at the end of this section. `E1`–`E8` and
`Q-a`–`Q-d` are navigation labels only. Nothing here changes VAP v1.2,
CHANGE-001, a profile or any signed artifact.

The work described is third-party work on individual Internet-Drafts and
hackathon projects. None of it is an implementation of VAP or VCP. VAP still
has no external implementation and no Evidence Pack accepted in any
proceeding.

### What the materials state (checked 20 November 2026 JST)

| Ref | Observation | Primary source |
| --- | --- | --- |
| E1 | RFC 9943 defines no identifier for an individual Signed Statement; `iss` and `sub` group statements without selecting one. Presented at the SCITT WG on 18 November as history and a proposal for discussion; the deck states that nothing in it seeks adoption | [S1] pp. 14–19, 21–22 |
| E2 | One Signed Statement re-encoded 64 ways with six CBOR encoding freedoms gave 64 distinct data-hash values; a stock decoder rejected none of them and silently repaired 31 on read. The slide concludes that a reference by digest holds only if the bytes and their canonicalization are pinned (the slide attributes the experiment to a SCITT list post of 22 September) | [S1] p. 23 |
| E3 | Requirements gathered so far, labelled "proposed input, not WG consensus": a reference names its target and its matching rule (algorithm and exact input bytes); a missing input is never a match; an unsupported relation type is never treated as verified; a match is not signature validity or issuer trust | [S1] p. 24 |
| E4 | The same four Signed Statements were registered on two Transparency Services run by two operators (14 November), and each operator checked the other's receipts. The same statement has a different leaf on each log (the statement's bytes on one, the digest of its Sig_structure on the other). The slides state that RFC 9943 and RFC 9942 do not name the entry's serialization, so a receipt cannot be checked without the issuing service's rule. Limits stated by the authors: the two operators co-champion the same hackathon project; no signed tree head of the second log was checked; one operator's checking script and output are unpublished | [S2]; [S5] §11; [S1] pp. 30–31 |
| E5 | In an RFC 9942 inclusion receipt (RFC9162_SHA256) the signature covers the Merkle root, while the tree size and leaf index are carried in the unprotected header. Read alone, a receipt shows inclusion under a signed root, not the statement's position or the log size. One service reported that a plain receipt was accepted for the issued pair and for 31 of 8,255 edited (tree size, leaf index) pairs, and for the issued pair only when read with its signed tree head. An erratum to RFC 9942 §5.2.1 was announced on the SCITT list; its filing was not confirmed in this check | [S5] §§7, 9, 11 |
| E6 | Four JSON canonicalization implementations wrote identical bytes on 20,121 of 20,140 cases. Eight inputs split them: integers of 2^53 or more, a byte order mark, duplicate members and nesting deeper than 128. The slides conclude that a JCS profile has to say "refuse" for these | [S3] |
| E7 | The two reference verifiers of one project disagreed on one number written two ways (`1e-07` from Python, `1e-7` from JavaScript: ALLOW versus DENY). A verifier written in Go by another party from the documents alone found 25 places where the text left a choice | [S4]; [S1] p. 30 |
| E8 | `draft-mih-sokolov-cose-deterministic-encodings-01` adds a COSE Hash Envelope (RFC 9995) header parameter that identifies the deterministic encoding of the preimage. It defines only the CBOR value `"dtrm"` and forbids pairing it with `application/json` | [S6] §§3–4 |

### Where they touch VAP v1.2 (questions only)

**Q-a. Numeric representation and invalid input (row in §3).** §7.2 requires
numeric values to be encoded as strings, and §7.3 and INT-001 require RFC 8785,
whose input is the I-JSON subset (RFC 7493; duplicate property names are not
allowed). For fields encoded as strings, a number-formatting split like E7
does not arise. Still open: (i) whether the `int64` fields of the §7.5
AnchorRecord abstract schema (`event_count`, `timestamp_int`) are strings
under §7.2; (ii) the verifier's result for each E6 input (an integer of 2^53 or
more as a JSON number, a leading byte order mark, a duplicate member, deep
nesting): reject, or report as not verifiable under P1; (iii) shared boundary
vectors run in at least Python and JavaScript.

**Q-b. Verification context for receipts.** §11.3 keeps VAP-native
verification possible without the transparency service, so E4–E5 do not
affect VAP-native checks. Where SCITT alignment is claimed and an Evidence Pack
carries COSE Receipts, §9.3 lists receipts, public keys and policy documents,
but not the issuing service's entry serialization or a signed tree head.
Question: whether the pack should carry, per receipt, the service's entry
rule and receipt-signing key and, when a claim depends on position or log
size, a signed tree head that binds the size. Coordinate with the `bind` row in
§3 (INT-008, §7.5), since `anchor_target.proof` is target-specific.

**Q-c. References between records.** VAP identifies events by an identifier
(INT-002) and by `event_hash` over RFC 8785 canonical JSON (INT-003, §4.1.3,
§7.1), so attaching a receipt does not change `event_hash`. Some references
carry only identifiers, for example `erasure_target_event_ids` in §7.4.
Question, in the light of E3: whether such a reference should also name the
target's digest and hash algorithm, and how a verifier reports a reference
whose target is missing (cf. P1).

**Q-d. Order of work.** E4–E7 surfaced only when someone else wrote a verifier
from the documents. A reproduction kit should follow fixed normative text for
Q-a to Q-c; built first, it would fix one implementation's behaviour rather
than the specification's.

### Sources for this section

- [S1] SCITT WG session slides, IETF 127, 18 November 2026: <https://datatracker.ietf.org/meeting/127/materials/slides-127-scitt-ietf-127-scitt-working-group-sf-00> (identification part also as <https://datatracker.ietf.org/meeting/127/materials/slides-127-scitt-unique-identification-semantic-correlation-00>)
- [S2] Hackathon results, "Agent action evidence interop": <https://datatracker.ietf.org/meeting/127/materials/slides-127-hackathon-sessd-agent-action-evidence-interop-results-01>
- [S3] Hackathon results, "Agent evidence conformance matrix": <https://datatracker.ietf.org/meeting/127/materials/slides-127-hackathon-sessd-agent-evidence-conformance-matrix-01>
- [S4] Hackathon results, "Action Evidence Packages for AI agents: recompute, don't inherit": <https://datatracker.ietf.org/meeting/127/materials/slides-127-hackathon-sessd-action-evidence-packages-for-ai-agents-recompute-dont-inherit-03>
- [S5] `draft-lemonnier-scitt-decision-provenance-03`: <https://datatracker.ietf.org/doc/html/draft-lemonnier-scitt-decision-provenance-03>
- [S6] `draft-mih-sokolov-cose-deterministic-encodings-01`: <https://datatracker.ietf.org/doc/html/draft-mih-sokolov-cose-deterministic-encodings-01>
- RFC 8785 <https://www.rfc-editor.org/rfc/rfc8785>, RFC 9942 <https://www.rfc-editor.org/rfc/rfc9942>, RFC 9943 <https://www.rfc-editor.org/rfc/rfc9943>

## 6. Suggested order of work (28 November 2026)

**Status: a recommendation from VSO's internal review of 28 November 2026; not a
scope assignment, a decision or a schedule.** The review was first-party and
AI-assisted, and has not been independently reviewed. It read the public incident
registry at 88 records
([vcp-site `591e68c`](https://github.com/veritaschain/vcp-site/blob/591e68cf8fc480d0baeba24cbec68b8fcf084bfe/incidents/incidents.json))
against this register. Incident counts are VSO's editorial classification and are
not evidence of need.

| Order | Subjects | Why here | Material that exists |
| --- | --- | --- | --- |
| 1 | P1 three-valued verification; meaning and bytes of `bind`; Ed25519 key and signature input policy; numeric representation with Q-a (section 3, section 5) | Later subjects report results that depend on a not-verified outcome; these rest on verifier findings and the IETF 127 observations, not on incidents | P1 revision 0.2; [P12](integrity-text-candidates/README.md), revision 0.1, with open points; demo security vectors. Shared boundary vectors are deliberately not written yet (Q-d) |
| 2 | F11, F13, first part of F12, F9 as an informative note, F7 as an optional reservation | Can be stated as wording in existing clauses | [P11](core-text-candidates/README.md), revision 0.1, with open points; for F13, [fourteen synthetic screening cases](../experiments/secret-value-screening/README.md), which show that the rule can be checked only in the negative |
| 3 | P2, limited to defining the declared scope and binding a digest of the scope or policy text; F10 | P2's own section 9 lists six open decisions on advance commitment. F10 depends on publishing the DAP Working Draft and reconciling it with v1.2 Draft 3 | P2 revision 0.1 with a verifier and 14 synthetic scenarios; no text for F10 |
| Later | Advance commitment under P2; F8; second part of F12 (compromise declarations); F14 | Each needs design work. F8 overlaps a third-party Internet-Draft; its IPR disclosures were read on 28 November 2026 ([note](core-text-candidates/EXTERNAL-OVERLAP.md)), the covenant they mention was not | Local experiments only |

Not proposed for any release: detection, blocking or runtime intervention;
obligations on systems operated by an attacker; new domain-specific normative
text for wallets, payment APIs or cloud credentials; a wider scope for VCP.

Nothing in this order can be acted on as a normative change until the decision
inputs in [the proposed change-control preparation](../governance/PROPOSED-CHANGE-PROCESS.md),
section 1, are supplied: the Technical Committee, the voting rule, the formal
register and an opened public review.

## 7. Decision and change log

| Date | Administrative action | Normative effect |
| --- | --- | --- |
| 2026-11-11 JST | Prepare this source-linked inventory and unresolved-decision checklist | None; no scope assignment, review clock, vote, registration or adoption |
| 2026-11-11 JST | Add the eight follow-up subjects F7–F14, attributed to the supplied follow-up list; original report reconciliation and exact text/vectors remain pending | None; all eight remain unnumbered, unadopted candidate work |
| 2026-11-20 JST | Add §5: external observations E1–E8 from IETF 127 materials and questions Q-a–Q-d, from the check of the 20 November weekly standards brief | None; questions only, unadopted; no external implementation of VAP is implied |
| 2026-11-28 JST | Add row P11 (candidate wording for F7, F9, F11, F13 and the first part of F12) and §6 (suggested order of work) from the 28 November internal review of the incident registry at 88 records | None; candidate wording and a recommendation only; no scope assignment, review opening, vote or adoption |
| 2026-11-28 JST | Add row P12 (candidate wording for `bind`, the Ed25519 input policy and numeric representation), a review note on overlap with `draft-mih-scitt-agent-action-capsule` and its IPR disclosures, and a synthetic screening experiment for F13; update §6 to point to them | None; candidate wording, a review note and a local experiment only; no scope assignment, review opening, vote or adoption |

Use the [proposed change-control preparation](../governance/PROPOSED-CHANGE-PROCESS.md)
to assemble the required governance and review records. Formal identifiers,
review dates, membership, voting rules and any acceptance outcome must be
supplied by real decisions and evidence. This file contains none of them.

[baseline]: https://github.com/veritaschain/vap-spec/tree/1ce71a66f55d9a20728213b7c3a8bb79270ae579
