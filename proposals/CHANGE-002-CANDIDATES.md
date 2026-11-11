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

## 2. Nine current proposal directories

All entries below remain **unadopted**. This directory inventory does not make
them nine formal change proposals or assign any to CHANGE-002. Each proposal's
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

## 5. Decision and change log

| Date | Administrative action | Normative effect |
| --- | --- | --- |
| 2026-11-11 JST | Prepare this source-linked inventory and unresolved-decision checklist | None; no scope assignment, review clock, vote, registration or adoption |
| 2026-11-11 JST | Add the eight follow-up subjects F7–F14, attributed to the supplied follow-up list; original report reconciliation and exact text/vectors remain pending | None; all eight remain unnumbered, unadopted candidate work |

Use the [proposed change-control preparation](../governance/PROPOSED-CHANGE-PROCESS.md)
to assemble the required governance and review records. Formal identifiers,
review dates, membership, voting rules and any acceptance outcome must be
supplied by real decisions and evidence. This file contains none of them.

[baseline]: https://github.com/veritaschain/vap-spec/tree/1ce71a66f55d9a20728213b7c3a8bb79270ae579
