# VAP-AT: AI Auditability Testing Program

## Overview

**VAP-AT (Verifiable AI Provenance - Auditability Testing)** is an open benchmark program for evaluating the auditability of AI and algorithmic decision systems against VAP Framework requirements.

> **Core Philosophy**
>
> **VAP-AT evaluates systems, not people.**  
> It is score-based, not pass/fail, and exists to support **continuous auditability improvement**.
>
> VAP-AT does not compete with professional certifications (CISSP, ISO 27001, etc.).  
> It complements them by providing AI-specific auditability metrics.

> **This is not a product. This is not an implementation proposal.**  
> It is an evaluation framework — a common yardstick for measuring "evidence quality."

## Purpose

VAP-AT provides:

- **Standardized Assessment**: Common criteria for evaluating AI system auditability
- **Regulatory Alignment**: Mapping to EU AI Act, MiFID II, and other requirements
- **Vendor Neutrality**: Implementation-agnostic evaluation based on outcomes
- **Evidence Packages**: Templates for regulatory and audit submissions

## Implementation Neutrality

> **This benchmark is implementation-agnostic.**
>
> No specific technology, protocol, library, or data structure is mandated. Scores are based solely on whether the **required outcome** (the cryptographic or audit property) is demonstrably achieved—not on how it is achieved.
>
> Reference implementations (such as VeritasChain Protocol) exist as **illustrative examples only** and do not represent the only acceptable approach.

## Evaluation Criteria

The benchmark evaluates 10 dimensions of auditability:

| # | Criterion | Key Question |
|---|-----------|--------------|
| 1 | **Third-Party Verifiability** | Can an external party independently verify the audit trail? |
| 2 | **Tamper Evidence** | Can unauthorized modifications be detected? |
| 3 | **Sequence Fixation** | Is the chronological order fixed in a tamper-evident, externally verifiable way? |
| 4 | **Decision Provenance** | Can inputs and rationale behind decisions be traced? |
| 5 | **Responsibility Boundaries** | Is it clear who approved or overrode each action? |
| 6 | **Audit Submission Readiness** | Can a complete evidence package be exported on demand? |
| 7 | **Retention & Durability** | Are records retained for required periods with verifiable integrity? |
| 8 | **Timestamp Reliability** | Are timestamps synchronized to a trusted time source? |
| 9 | **Cryptographic Strength** | Do algorithms meet current security standards? |
| 10 | **Cryptographic Agility** | Can the system migrate to new algorithms (e.g., PQC)? |

## Scoring System

### Score Scale

| Score | Meaning |
|-------|---------|
| **0** | Not implemented or fundamentally inadequate |
| **1** | Partially implemented; gaps remain |
| **2** | Fully implemented; required outcome demonstrably achieved |

### Grade Thresholds

| Score Range | Grade | Interpretation |
|-------------|-------|----------------|
| 16-20 | **Strong** | System demonstrates robust auditability |
| 11-15 | **Moderate** | Auditability present with notable gaps |
| 6-10 | **Limited** | Significant auditability deficiencies |
| 0-5 | **Inadequate** | Auditability fundamentally insufficient |

## Program Documents

| Document ID | Title | Description | File |
|-------------|-------|-------------|------|
| VSO-SCORE-001 | Scorecard v1.0 | 10 evaluation criteria with scoring rubrics | [PDF](https://github.com/veritaschain/vcp-spec/blob/main/benchmark/AI_Decision_Auditability_Benchmark_Scorecard_v1_0.pdf) |
| VSO-SCORE-002 | PoC Assessment Guide v1.0 | Minimum viable test procedures (~3 hours) | [PDF](https://github.com/veritaschain/vcp-spec/blob/main/benchmark/AI_Decision_Auditability_Benchmark_PoC_Guide_v1_0.pdf) |
| VSO-SCORE-003 | Evidence Pack Template v1.0 | Third-party submission template | [PDF](https://github.com/veritaschain/vcp-spec/blob/main/benchmark/AI_Decision_Auditability_Benchmark_Evidence_Pack_v1_0.pdf) |
| VSO-SCORE-004 | EU AI Act Mapping Annex v1.0 | Regulatory alignment mapping | [PDF](https://github.com/veritaschain/vcp-spec/blob/main/benchmark/AI_Decision_Auditability_Benchmark_EU_AI_Act_Annex_v1_0.pdf) |

Scoring rubric and improvement guidance: [`vcp-spec/benchmark`](https://github.com/veritaschain/vcp-spec/tree/main/benchmark).

## Regulatory Alignment

### EU AI Act Mapping

| VAP-AT Criterion | EU AI Act (Regulation (EU) 2024/1689) | Relevance |
|------------------|-------------------|-------------|
| Third-Party Verifiability | Article 12 | Record-keeping: automatic recording of events over the system's lifetime |
| Tamper Evidence | — | No direct counterpart. Article 12 does not specify integrity, tamper-resistance, or tamper-evidence of logs; Article 12(3) lists minimum logging content for Annex III point 1(a) systems only |
| Decision Provenance | Article 13 | Transparency and provision of information to deployers |
| Responsibility Boundaries | Article 14 | Human oversight |
| Retention & Durability | Articles 18, 19, 26(6) | Documentation keeping (Art. 18); retention of automatically generated logs for at least six months unless other Union or national law provides otherwise (Art. 19 providers; Art. 26(6) deployers) |

This is a relevance mapping, not a compliance determination (VAP v1.2 §1.6). Under Regulation (EU) 2026/1744, obligations for Annex III high-risk systems apply from 2 December 2027 and for Annex I systems from 2 August 2028.

### Additional Regulatory Coverage

- **MiFID II Art. 17 + RTS 6** (Delegated Regulation (EU) 2017/589): algorithmic trading organisational requirements
- **MiFID II RTS 25** (Delegated Regulation (EU) 2017/574): business-clock synchronisation
- **CAT Rule 613**: Consolidated Audit Trail (US)
- **GDPR Article 22**: Automated decision-making transparency

## Target Audiences

### Audit Firms

VAP-AT provides an external reference standard for AI system assurance engagements, addressing the current gap in standardized AI audit frameworks.

### RegTech Vendors

The benchmark offers a competitive differentiation framework for vendors building AI governance solutions.

### Financial Institutions

VAP-AT enables self-assessment of AI trading systems against upcoming regulatory requirements.

### Regulators

The program provides technical criteria that can inform regulatory standards and enforcement.

## Assessment Process

### Self-Assessment

1. Review the 10 criteria definitions
2. Gather evidence for each criterion
3. Score your system (0/1/2 per criterion)
4. Identify gaps and remediation priorities

### Third-Party Assessment

1. Engage an independent assessor
2. Provide system access for testing
3. Review Assessment Report
4. Address findings if applicable

## Related Resources

- [VAP Framework Specification v1.2](../../spec/v1.2/VAP_Framework_Specification.md)
- [VAP Scorecard](../../scorecard/)
- [VCP Implementation Guide](https://github.com/veritaschain/vcp-spec)

## Contributing

We welcome contributions to improve the assessment criteria and methodology. See [CONTRIBUTING.md](../../CONTRIBUTING.md).

## Contact

**VeritasChain Standards Organization (VSO)**

- Website: https://veritaschain.org
- Email: standards@veritaschain.org

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong><br/>
  <em>"Verify, Don't Trust"</em>
</p>
