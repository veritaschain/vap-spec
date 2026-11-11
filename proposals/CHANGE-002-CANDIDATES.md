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

## 4. Decision and change log

| Date | Administrative action | Normative effect |
| --- | --- | --- |
| 2026-11-11 JST | Prepare this source-linked inventory and unresolved-decision checklist | None; no scope assignment, review clock, vote, registration or adoption |

Use the [proposed change-control preparation](../governance/PROPOSED-CHANGE-PROCESS.md)
to assemble the required governance and review records. Formal identifiers,
review dates, membership, voting rules and any acceptance outcome must be
supplied by real decisions and evidence. This file contains none of them.

[baseline]: https://github.com/veritaschain/vap-spec/tree/1ce71a66f55d9a20728213b7c3a8bb79270ae579
