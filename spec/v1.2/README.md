# VAP Framework Specification v1.2

**Document ID:** VSO-VAP-SPEC-001
**Version:** 1.2.0
**Status:** Draft Specification (Draft 3)
**Date:** 2026-09-01 (publication folds G-2, H-2, A-4 applied 2026-09-28; Appendix D)

VAP (Verifiable AI Provenance Framework) is a metaframework. It defines the
common requirements that domain profiles (VCP, CAP, CPP, OAP, MAP, PAP, …) and
cross-cutting capabilities (DAP, SMP) inherit. It makes AI decision records
auditable, attributable, and — at anchor granularity — completeness-verifiable
after the fact. It does not prevent, block, or intercept any AI behaviour.

---

## Implementation status (mandatory disclosure)

As of this draft there are **zero external implementations** of VAP or any VAP
profile, and **zero Evidence Packs accepted in any proceeding**. VeritasChain
Co., Ltd., which provides the operating base of VSO, holds ten paid service
contracts with European organizations in regulatory technology, financial
trading, and audit and assurance (client names withheld pending individual
consent). Those contracts are not external implementations and are not
independent validation of VAP.

VAP has not been adopted by, and carries no standing within, the IETF,
ISO/IEC JTC 1/SC 42, ITU-T, or any other established standards body. The
related Internet-Drafts are individual submissions (§11.4).

---

## Documents

| File | Content | SHA-256 |
|------|---------|---------|
| [`VAP_Framework_Specification.md`](VAP_Framework_Specification.md) | VAP Framework Specification v1.2.0, Draft 3 (normative) | `1a93fd0610cf7337d76e9c651e749cd512cdc7abda726c1135c05c5d2673d51c` |
| [`VSO-VAP-CHANGE-001.md`](VSO-VAP-CHANGE-001.md) | VAP v1.1 → v1.2 Change Proposal — normative annex / change-control record (§1.7) | `ec781c81b2869f06ccb53de12927da868d7990e1eea42ba8a0369425b0089fca` |

Version numbers identify documents; the SHA-256 digests above fix their exact
content. Where the specification and VSO-VAP-CHANGE-001 differ in detail, the
specification prevails (§1.7).

---

## What changed from v1.1

v1.2 is a **framework-compatible / certification-stricter** revision. All
v1.1-conformant event data remains valid; there are zero wire-format breaking
changes.

| Area | v1.1 | v1.2 |
|------|------|------|
| Sequencing (INT-003/004) | Hash chain (PrevHash) MUST | **Cryptographic Sequence Verifiability** MUST; PrevHash OPTIONAL (INT-004a), profile-mandatable |
| External anchoring (INT-006) | SHOULD | **MUST at all conformance levels**, including VAP-Core |
| Anchor continuity (INT-007) | — | MUST (fallback target, failover window, local AnchorRecord retention) |
| Completeness Invariant (INT-008) | — | MUST — post-anchor omission / split-view detectable at batch granularity |
| Recovery operations (INT-009) | — | MUST be bounded, recorded, authorized (when used) |
| Crypto-shredding | Mechanism only | **ERASURE event** + legal-scope clause (§6.3) |
| Policy identification | — | `policy` object in every event (§7.1) |
| Cross-party provenance | — | XREF, TRC-005 (OPTIONAL; MUST-level when used) |
| SCITT / COSE | — | Opt-in normative alignment with **RFC 9943** / **RFC 9942** (§11.3) |
| PQC | DILITHIUM2 / FALCON-512 "Future" | **ML-DSA (FIPS 204)** / **FN-DSA (FIPS 206, draft)** EXPERIMENTAL; hybrid dual signatures |
| Cross-cutting capabilities | — | §4.6: DAP (VAP-AGENT), SMP (VAP-SLEEP) |
| Legal scope | — | §1.6 Non-Guarantee Statement (normative) |

Migration grace periods for v1.1 conformance claims: VSO-VAP-CHANGE-001 §5.

---

## Profile and capability registry (from §4.5.2 / §4.6.2)

The specification's registry prevails over any badge, website, or press
material that disagrees with it.

| ID | Domain / scope | Status | Where |
|----|----------------|--------|-------|
| **VCP** | Finance / Algorithmic Trading | v1.2 Release Candidate (RC1) | [veritaschain/vcp-spec](https://github.com/veritaschain/vcp-spec) |
| **CAP** | Content / Creative AI | v1.0 Released | [veritaschain/cap-spec](https://github.com/veritaschain/cap-spec) |
| **CPP** | Capture Provenance | v1.4 Released | [veritaschain/cpp-spec](https://github.com/veritaschain/cpp-spec) |
| **OAP** | Observed Artifact Provenance | v0.1.1 Working Draft | VSO-VAP-OAP-001 |
| **MAP** | Medical / Healthcare AI | v0.1.2 Working Draft | VSO-VAP-MAP-001 |
| **PAP** | Public Sector / Government AI | Partial Draft (Track B v0.2.0) | VSO-VAP-PAP-001 |
| IAP | Industry Accountability | Announced | — |
| DVP / AAP / EIP | Automotive / Aviation / Energy | Planned | — |
| **DAP** (capability) | Delegated Access Provenance (VAP-AGENT) | v0.1.0 Working Draft | VSO-VAP-DAP-001 |
| **SMP** (capability) | Self-Modification Provenance (VAP-SLEEP) | v0.2.0 Working Draft | VSO-VAP-SMP-SPEC-001 |

CAP v1.0 and CPP v1.4 have a VAP v1.2 conformance mapping that is due and not
yet delivered; until it is published, neither may be described as VAP v1.2
conformant (§10.4).

---

## Legal scope (§1.6, normative)

> VAP and its domain profiles define mechanisms for producing **cryptographically verifiable evidence** of AI system decisions. Conformance to VAP or any profile: (a) does **not** constitute compliance with the EU AI Act, GDPR, MiFID II/III, CAT Rule 613, NIS2, FDA SaMD guidance, or any other law or regulation; (b) does **not** constitute a legal determination that any technical mechanism (including crypto-shredding) satisfies a specific legal obligation; (c) does **not** warrant the correctness, fairness, or safety of the underlying AI decisions — only the integrity, completeness (at anchor granularity), and attributability of their records. VAP generates evidence; competent authorities and courts evaluate it.

Events that were never measured or recorded (pre-measurement drop) are outside
the reach of any provenance mechanism, by construction.

---

## Previous version

[v1.1](../v1.1/) (2025-12-11) is retained for reference and is superseded by
this version for all new work.

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong><br/>
  <em>"Verify, Don't Trust"</em>
</p>
