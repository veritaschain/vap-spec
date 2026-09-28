# Verifiable AI Provenance Framework (VAP)

<p align="center">
  <strong>AI needs a Flight Recorder</strong><br>
  <em>"Verify, Don't Trust"</em>
</p>

<p align="center">
  <a href="https://veritaschain.org">Website</a> •
  <a href="./spec/v1.2/VAP_Framework_Specification.md">Specification (v1.2, Draft 3)</a> •
  <a href="#relationship">Profiles</a> •
  <a href="https://github.com/veritaschain">GitHub</a>
</p>

---

## What is VAP

**VAP (Verifiable AI Provenance Framework)** is the **cross-domain metaframework** that defines minimum requirements for cryptographically verifiable AI decision trails. Domain profiles implement it; only VCP carries the "Protocol" designation.

VAP makes AI decision records **auditable, attributable, and — at anchor granularity — completeness-verifiable after the fact**. It is post-hoc only: it does not prevent, block, or intercept any AI behaviour, and it does not warrant that any recorded decision was correct, fair, or safe.

VAP is **NOT** a regulation that restricts AI use.<br>
VAP **IS** an evidence infrastructure standard for safe continued AI operation.

> **"Encoding Trust in the AI Age"**

VAP's scope is deliberately strict: **domains where system failures can cause irreversible harm to human life, social infrastructure, or democratic institutions.**

### Implementation status (mandatory disclosure)

As of September 2026: **zero external implementations** of VAP or any VAP profile, and **zero Evidence Packs accepted in any proceeding**. VeritasChain Co., Ltd., which provides the operating base of VSO, holds ten paid service contracts with European organizations in regulatory technology, financial trading, and audit and assurance (client names withheld pending individual consent); those contracts are not external implementations and are not independent validation of VAP.

VAP has not been adopted by, and carries no standing within, the IETF, ISO/IEC JTC 1/SC 42, ITU-T, or any other established standards body.

---

## Current Specification

| Version | Status | Location |
|---------|--------|----------|
| **v1.2.0** | Draft Specification (Draft 3) — current | [`spec/v1.2/`](./spec/v1.2/) |
| v1.1.0 | Draft Specification — superseded for new work (tag `v1.1.0`) | [`spec/v1.1/`](./spec/v1.1/) |

v1.2 is framework-compatible with v1.1 (no wire-format breaking changes) and certification-stricter: external anchoring is required at every conformance level, and the Completeness Invariant (INT-008), anchor continuity (INT-007), bounded RECOVERY (INT-009), ERASURE, Policy Identification, and XREF join the Shared Assurance Core. Change control: [`VSO-VAP-CHANGE-001`](./spec/v1.2/VSO-VAP-CHANGE-001.md).

---

## Relationship

**VAP defines the "what"** (common requirements).<br>
**Profiles define the "how"** (domain-specific implementations).<br>
**Cross-cutting capabilities** are defined once at the Shared Assurance Core and composed with any profile.

Status values follow the normative registry in VAP v1.2 §4.5.2; that registry prevails over this table if they ever disagree.

| Profile | Domain | Risk Category | Repository / Document | Status |
|---------|--------|---------------|------------|--------|
| **VCP** | Finance & Algorithmic Trading | Market Integrity | [veritaschain/vcp-spec](https://github.com/veritaschain/vcp-spec) | v1.2 Release Candidate (RC1) |
| **CAP** | Content / Creative AI | IP Rights, Misinformation | [veritaschain/cap-spec](https://github.com/veritaschain/cap-spec) | v1.0 Released |
| **CPP** | Capture Provenance | Evidence Integrity, Misinformation | [veritaschain/cpp-spec](https://github.com/veritaschain/cpp-spec) | v1.4 Released |
| **OAP** | Observed Artifact Provenance | Evidence Integrity, Repudiation | VSO-VAP-OAP-001 | v0.1.1 Working Draft |
| **MAP** | Medical / Healthcare AI | Patient Safety | VSO-VAP-MAP-001 | v0.1.2 Working Draft |
| **PAP** | Public Sector | Democratic Integrity | VSO-VAP-PAP-001 | Partial Draft (Track B v0.2.0 only; no consolidated specification) |
| **IAP** | Industry Accountability | Sector-Specific Governance | — | Announced |
| **DVP** | Automotive | Physical Safety | — | Planned |
| **AAP** | Aviation | Physical Safety | — | Planned |
| **EIP** | Energy Infrastructure | Critical Infrastructure | — | Planned |

| Capability | Scope | Document | Status |
|------------|-------|----------|--------|
| **DAP** (VAP-AGENT) | Delegated Access Provenance | VSO-VAP-DAP-001 | v0.1.0 Working Draft |
| **SMP** (VAP-SLEEP) | Self-Modification Provenance | VSO-VAP-SMP-SPEC-001 | v0.2.0 Working Draft |

CAP v1.0 and CPP v1.4 owe a VAP v1.2 conformance mapping that has not yet been published; until it is, neither may be described as VAP v1.2 conformant (VAP v1.2 §10.4).

---

## What This Repository IS / IS NOT

| ✅ IS | ❌ IS NOT |
|-------|----------|
| Framework specification | SaaS product |
| Profile architecture | Commercial software |
| Assessment programs | Certification authority |
| Open standard | Endorsement of any vendor |

**VSO maintains strict vendor neutrality.** See [VSO Non-Endorsement Policy](https://veritaschain.org/non-endorsement/). Conformity assessment is performed by independent Conformity Assessment Bodies, not by VSO (VAP v1.2 §10.1).

---

## Quick Links

| Resource | Link |
|----------|------|
| **VAP v1.2 Specification** | [spec/v1.2/VAP_Framework_Specification.md](./spec/v1.2/VAP_Framework_Specification.md) |
| **VCP** (Finance Profile) | [github.com/veritaschain/vcp-spec](https://github.com/veritaschain/vcp-spec) |
| **CAP** (Content / Creative AI Profile) | [github.com/veritaschain/cap-spec](https://github.com/veritaschain/cap-spec) |
| **CPP** (Capture Provenance Profile) | [github.com/veritaschain/cpp-spec](https://github.com/veritaschain/cpp-spec) |
| **Website** | [veritaschain.org](https://veritaschain.org) |
| **IETF Internet-Draft (VAP)** | [draft-kamimura-vap-framework](https://datatracker.ietf.org/doc/draft-kamimura-vap-framework/) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│     VAP (Verifiable AI Provenance Framework)                    │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    │
│     Cross-domain metaframework                                  │
│     Defines common minimum requirements                         │
│                                                                 │
│                          ▲                                      │
│                          │ defines & maintains                  │
│                          │                                      │
│     VSO (VeritasChain Standards Organization)                   │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                   │
│     Standards organization maintaining VAP and profiles         │
│                                                                 │
│                          │                                      │
│                          │ publishes profiles                   │
│                          ▼                                      │
│                                                                 │
│   ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐   │
│   │  VCP  │ │  CAP  │ │  CPP  │ │  OAP  │ │  MAP  │ │  PAP  │  …│
│   │Finance│ │Content│ │Capture│ │Observd│ │Medical│ │Public │   │
│   └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘   │
│                                                                 │
│     Domain-specific profile implementations                     │
│     + cross-cutting capabilities (DAP, SMP)                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### Five-Layer Architecture (VAP v1.2 §3.1)

All VAP profiles share this common architecture:

```
┌────────────────────────────────────────────┐
│  Domain Profiles Layer                     │
│  VCP / CAP / CPP / OAP / MAP / PAP ...     │
├────────────────────────────────────────────┤
│  Accountability Layer                      │
│  Responsibility identification · Overrides │
├────────────────────────────────────────────┤
│  Traceability Layer                        │
│  Causal chains · trace_id · XREF           │
├────────────────────────────────────────────┤
│  Provenance Layer                          │
│  Actor / Input / Context / Action / Outcome│
├────────────────────────────────────────────┤
│  Integrity Layer                           │
│  EventHash · Sequence Verifiability ·      │
│  Merkle Tree · External Anchoring (MUST) · │
│  Completeness Invariant · Signatures       │
└────────────────────────────────────────────┘
```

### Cryptographic Primitives

| Primitive | Algorithm | Status |
|-----------|-----------|--------|
| Hash | SHA-256 | DEFAULT (SHA3-256, BLAKE3 supported) |
| Signature | Ed25519 | DEFAULT (ECDSA secp256k1 supported; RSA-2048 deprecated) |
| Merkle Tree | RFC 6962 (domain-separated) | REQUIRED |
| External Anchor | TSA / transparency log / blockchain / RFC 9943 transparency service | REQUIRED at all conformance levels |
| Post-Quantum | ML-DSA (FIPS 204), FN-DSA (FIPS 206, draft) | EXPERIMENTAL — hybrid dual signatures available |

---

## Programs

### VAP-AT: AI Auditability Testing

An open benchmark program for assessing AI system auditability against VAP requirements. It is score-based and is not a conformance or certification scheme.

📁 See [`programs/vap-at/`](./programs/vap-at/)

### VAP Scorecard

Self-assessment question set for evaluating auditability readiness. No web, API, or CLI tool has been published yet.

📁 See [`scorecard/`](./scorecard/)

---

## Regulatory Context

VAP produces evidence relevant to provisions such as the following. This is not a compliance mapping: conformance to VAP does not constitute compliance with any law or regulation (VAP v1.2 §1.6), and each regime applies only within its own jurisdiction.

| Regulation | Jurisdiction | Relevance |
|------------|--------------|-----------|
| EU AI Act (Regulation (EU) 2024/1689) | European Union | High-risk classification (Art. 6); record-keeping (Art. 12); human oversight (Art. 14) |
| MiFID II + RTS 6 / RTS 25 | European Union | Algorithmic trading organisational requirements (RTS 6); business-clock synchronisation (RTS 25) |
| GDPR | European Union | Right to erasure (Art. 17) — crypto-shredding may support, does not determine, compliance |
| CAT (SEC Rule 613) | United States | Consolidated Audit Trail |
| NIS2 Directive | European Union | Critical infrastructure |

> **Legal scope (VAP v1.2 §1.6, normative).** VAP and its domain profiles define mechanisms for producing **cryptographically verifiable evidence** of AI system decisions. Conformance to VAP or any profile: (a) does **not** constitute compliance with the EU AI Act, GDPR, MiFID II/III, CAT Rule 613, NIS2, FDA SaMD guidance, or any other law or regulation; (b) does **not** constitute a legal determination that any technical mechanism (including crypto-shredding) satisfies a specific legal obligation; (c) does **not** warrant the correctness, fairness, or safety of the underlying AI decisions — only the integrity, completeness (at anchor granularity), and attributability of their records. VAP generates evidence; competent authorities and courts evaluate it.

---

## Getting Started

### For Implementers

1. **Read the Framework Specification**: [`spec/v1.2/VAP_Framework_Specification.md`](./spec/v1.2/VAP_Framework_Specification.md)
2. **Choose Your Domain Profile**: See [Relationship](#relationship)
3. **Declare your sequence-mechanism matrix and anchoring policy** per conformance level (VAP v1.2 §8.2)
4. **Review Conformance Requirements**: Each profile defines its own test suite

### For Regulators

- **Legal scope and limits**: VAP v1.2 §1.6 and the Declaration section
- **Completeness claim level**: VAP v1.2 §4.1.7 and §11.1 (omission-evidence at anchor granularity only)
- **Contact**: [standards@veritaschain.org](mailto:standards@veritaschain.org)

---

## Standardization

### Current Status

| Body | Document | Status |
|------|----------|--------|
| IETF | `draft-kamimura-vap-framework-01`, `draft-kamimura-scitt-vcp-03`, `draft-kamimura-rats-behavioral-evidence-02`, `draft-kamimura-scitt-refusal-events-03`, `draft-vso-cpp-core-03` | Individual Internet-Drafts, active. Not adopted by any IETF Working Group; no standing in the IETF standards process |
| ITU-T SG17 | VSO-LS-SG17-001 | Returned by the TSB; the three criteria (well-defined standardization problem, demonstrated interoperability requirement, implementation experience) are not yet met |
| ISO/IEC JTC 1/SC 42 | Pre-registered gap-assessment protocol VSO-GAP-SC42-001 | No liaison, submission, or contribution |
| ISO/TC 68 | (Financial Services) | Planned. No submission |

Submission of a document to a standards body does not imply endorsement, adoption, or approval by that body.

### IETF Alignment

VAP profiles are designed to interoperate with IETF transparency work:

- **SCITT** — architecture published as **RFC 9943** (June 2026)
- **COSE Receipts** — published as **RFC 9942** (June 2026)
- **RATS** (Remote ATtestation procedureS)

SCRAPI (`draft-ietf-scitt-scrapi`) and CoRIM (`draft-ietf-rats-corim`) remain Internet-Drafts.

---

## Contributing

We welcome contributions from the community. Please see:

- [CONTRIBUTING.md](./CONTRIBUTING.md) - Contribution guidelines
- [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) - Community standards
- [SECURITY.md](./SECURITY.md) - Security policy

### How to Contribute

1. **Issues**: Report bugs or suggest features
2. **Pull Requests**: Submit improvements to specifications
3. **Discussions**: Join technical discussions on GitHub
4. **New Profiles**: Propose new domain profiles

---

## License

This specification is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

See [LICENSE](./LICENSE) for details.

---

## Contact

**VeritasChain Standards Organization (VSO)**

| Channel | Contact |
|---------|---------|
| Website | [https://veritaschain.org](https://veritaschain.org) |
| Email (General) | [info@veritaschain.org](mailto:info@veritaschain.org) |
| Email (Standards) | [standards@veritaschain.org](mailto:standards@veritaschain.org) |
| Email (Technical) | [technical@veritaschain.org](mailto:technical@veritaschain.org) |
| GitHub | [https://github.com/veritaschain](https://github.com/veritaschain) |

---

<p align="center">
  <em>"Verify, Don't Trust"</em><br>
  <strong>VeritasChain Standards Organization</strong>
</p>
