# Verifiable AI Provenance Framework (VAP)

<p align="center">
  <strong>AI needs a Flight Recorder</strong><br>
  <em>"Verify, Don't Trust"</em>
</p>

<p align="center">
  <a href="https://veritaschain.org">Website</a> •
  <a href="./spec/v1.1/VAP_Framework_Specification.md">Specification</a> •
  <a href="#relationship">Profiles</a> •
  <a href="https://github.com/veritaschain">GitHub</a>
</p>

---

## What is VAP

**VAP (Verifiable AI Provenance Framework)** is the **cross-domain meta-framework** that defines minimum requirements for cryptographically verifiable AI decision trails.

VAP is **NOT** a regulation that restricts AI use.  
VAP **IS** an evidence infrastructure standard for safe continued AI operation.

> **"Encoding Trust in the AI Age"**

VAP's scope is deliberately strict: **domains where system failures can cause irreversible harm to human life, social infrastructure, or democratic institutions.**

---

## Relationship

**VAP defines the "what"** (common requirements).  
**Profiles define the "how"** (domain-specific implementations).

| Profile | Domain | Risk Category | Repository | Status |
|---------|--------|---------------|------------|--------|
| **VCP** | Finance & Trading | Market Stability | [veritaschain/vcp-spec](https://github.com/veritaschain/vcp-spec) | ✅ v1.1 |
| **CAP** | Content / Creative | IP Rights, Misinformation | [veritaschain/cap-spec](https://github.com/veritaschain/cap-spec) | 🚧 v0.2 |
| **DVP** | Automotive | Physical Safety | — | 📋 Planned |
| **MAP** | Medical | Patient Safety | — | 📋 Planned |
| **PAP** | Public Sector | Democratic Integrity | — | 📋 Planned |
| **EIP** | Energy Infrastructure | Critical Infrastructure | — | 📋 Planned |
| **AAP** | Aviation | Physical Safety | — | 📋 Planned |

---

## What This Repository IS / IS NOT

| ✅ IS | ❌ IS NOT |
|-------|----------|
| Framework specification | SaaS product |
| Profile architecture | Commercial software |
| Assessment programs | Certification authority |
| Open standard | Endorsement of any vendor |

**VSO maintains strict vendor neutrality.** See [VSO Non-Endorsement Policy](https://veritaschain.org/non-endorsement/).

---

## Quick Links

| Resource | Link |
|----------|------|
| **VCP** (Finance Profile) | [github.com/veritaschain/vcp-spec](https://github.com/veritaschain/vcp-spec) |
| **CAP** (Content Profile) | [github.com/veritaschain/cap-spec](https://github.com/veritaschain/cap-spec) |
| **Website** | [veritaschain.org](https://veritaschain.org) |
| **IETF Draft** | [draft-kamimura-scitt-vcp](https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/) |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│     VAP (Verifiable AI Provenance Framework)                    │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    │
│     Cross-domain meta-framework                                 │
│     Defines common minimum requirements                         │
│                                                                 │
│                          ▲                                      │
│                          │ defines & maintains                  │
│                          │                                      │
│     VSO (VeritasChain Standards Organization)                   │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                   │
│     Standards body maintaining VAP and profiles                 │
│                                                                 │
│                          │                                      │
│                          │ publishes profiles                   │
│                          ▼                                      │
│                                                                 │
│     ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐            │
│     │   VCP   │ │   CAP   │ │   DVP   │ │   MAP   │  ...       │
│     │Finance  │ │Content/ │ │Automotive│ │Medical │            │
│     │Profile  │ │Creative │ │ Profile │ │Profile │            │
│     └─────────┘ └─────────┘ └─────────┘ └─────────┘            │
│                                                                 │
│     Domain-specific protocol implementations                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core Components

### Four-Layer Architecture

All VAP profiles share this common architecture:

```
┌────────────────────────────────────────────┐
│  Layer 4: Verification Layer               │
│  Merkle Tree / External Anchoring          │
├────────────────────────────────────────────┤
│  Layer 3: Integrity Layer                  │
│  Hash Chain / Digital Signatures           │
├────────────────────────────────────────────┤
│  Layer 2: Provenance Layer                 │
│  Actor / Input / Context / Action / Outcome│
├────────────────────────────────────────────┤
│  Layer 1: Identity Layer                   │
│  UUID v7 / Timestamps / Issuer Identity    │
└────────────────────────────────────────────┘
```

### Cryptographic Primitives

| Primitive | Algorithm | Status |
|-----------|-----------|--------|
| Hash | SHA-256 | ✅ Current |
| Signature | Ed25519 | ✅ Current |
| Merkle Tree | RFC 6962 | ✅ Current |
| Post-Quantum | DILITHIUM2 | 🔮 Future |

---

## Programs

### VAP-AT: AI Auditability Testing

An open benchmark program for assessing AI system auditability against VAP requirements.

📁 See [`programs/vap-at/`](./programs/vap-at/)

### VAP Scorecard Explorer

Interactive tool for evaluating VAP compliance across different domains.

📁 See [`scorecard/`](./scorecard/)

---

## Regulatory Alignment

VAP is designed to support compliance with emerging AI regulations:

| Regulation | Jurisdiction | Relevance |
|------------|--------------|-----------|
| EU AI Act | European Union | High-Risk AI Classification (Article 6) |
| MiFID II/III | European Union | Algorithmic Trading (RTS 25) |
| GDPR | European Union | Data Privacy & Crypto-Shredding |
| CAT Rule 613 | United States | Consolidated Audit Trail |
| NIS2 Directive | European Union | Critical Infrastructure |

---

## Getting Started

### For Implementers

1. **Read the Framework Specification**: [`spec/v1.1/VAP_Framework_Specification.md`](./spec/v1.1/VAP_Framework_Specification.md)
2. **Choose Your Domain Profile**: See [Domain Profiles](#domain-profiles)
3. **Review Conformance Requirements**: Each profile defines its own test suite

### For Regulators

- **Executive Summary**: Overview of VAP's regulatory value proposition
- **Mapping Tables**: How VAP addresses specific regulatory requirements
- **Contact**: [standards@veritaschain.org](mailto:standards@veritaschain.org)

---

## Standardization

### Current Status

| Body | Document | Status |
|------|----------|--------|
| IETF SCITT | draft-kamimura-scitt-vcp | Submitted |
| ISO/TC 68 | (Financial Services) | Planned 2026 |
| ISO/IEC JTC 1/SC 42 | (AI) | Planned 2026-2027 |

### IETF Integration

VAP profiles are designed to be compatible with IETF transparency standards:

- **SCITT** (Supply Chain Integrity, Transparency, and Trust)
- **RATS** (Remote ATtestation procedureS)
- **COSE** (CBOR Object Signing and Encryption)

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
