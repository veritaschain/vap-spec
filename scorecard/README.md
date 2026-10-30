# VAP Scorecard

## Overview

The VAP Scorecard is a self-assessment question set for evaluating AI systems against Verifiable AI Provenance Framework requirements (VAP v1.2).

> **Status:** Question set only. This repository publishes no web interface, API, or CLI for the Scorecard.

> **⚠️ Important Disclaimer**
>
> This scorecard is a **reference evaluation tool**, not a certification, endorsement, or regulatory approval. Assessment results do not constitute legal advice or compliance certification. Organizations should consult qualified professionals for regulatory compliance decisions.

## Purpose

The Scorecard provides:

- **Self-Assessment**: Organizations can evaluate their AI auditability readiness
- **Gap Analysis**: Identify specific areas requiring improvement
- **Roadmap Planning**: Prioritize implementation based on compliance gaps
- **Benchmarking**: Compare auditability posture across industry

## Assessment Domains

Aligned with the VAP v1.2 layers (§3.1):

| Domain | Description |
|--------|-------------|
| **Integrity** | Event identifiers and EventHash, cryptographic sequence verifiability (PrevHash and/or Merkle inclusion), RFC 6962 Merkle batching, external anchoring (required at every level), anchor continuity, Completeness Invariant, signatures |
| **Provenance** | Actor attribution, input tracing, context, decision factor recording, timestamp precision |
| **Traceability** | trace_id grouping, causal chains, cross-party provenance (XREF) |
| **Accountability** | Operator identification, approval workflows, override history |

## Scoring Levels

### Readiness Bands (indicative only)

The Scorecard uses the VAP-AT scale (10 criteria × 0/1/2 = 20 points) and the VAP-AT grade thresholds:

| Band | Score | Description |
|------|-------|-------------|
| **Strong** | 16-20 | Robust auditability demonstrated |
| **Moderate** | 11-15 | Auditability present with notable gaps |
| **Limited** | 6-10 | Significant auditability deficiencies |
| **Inadequate** | 0-5 | Auditability fundamentally insufficient |

A score is not a conformance level. VAP conformance levels (VAP-Core / VAP-Standard / VAP-Full, VAP v1.2 §8.1) are met only by satisfying every requirement of the level — there is no percentage threshold — and even VAP-Core requires external anchoring (INT-006) and an anchor continuity plan (INT-007). No conformance test suite has been published, so a Scorecard result cannot support a conformance claim.

### Implementation Neutrality

The Scorecard evaluates **capabilities and outcomes**, not specific implementations:

✅ **Evaluated**: "Does the system generate cryptographically verifiable event chains?"  
❌ **Not Evaluated**: "Does the system use PostgreSQL or MongoDB?"

## Profiles Supported

| Profile | Domain | Scorecard questions |
|---------|--------|--------|
| VCP | Finance & Trading | Available — [AI Decision Auditability Benchmark](https://github.com/veritaschain/vcp-spec/tree/main/benchmark) |
| CAP | Content / Creative AI | Not yet written |
| CPP | Capture Provenance | Not yet written |
| MAP | Medical | Not yet written (profile is a v0.1.2 Working Draft) |
| PAP / DVP / others | — | Not yet written |

## Usage

Answer the questions below (or the full VCP question set in the benchmark linked above) for your system and score each 0 / 1 / 2 as described in [VAP-AT](../programs/vap-at/). The `@veritaschain/scorecard-cli` package referenced in earlier versions of this page does not exist on the npm registry (checked 2026-09-28), and the web/API endpoints described there are not part of this repository; those references have been removed.

## Assessment Questions (Sample)

### Integrity Layer

1. Are event identifiers generated using UUID v7 (RFC 9562), and does every event carry an EventHash over its RFC 8785 canonical form?
2. How is event sequencing made cryptographically verifiable — per-event hash chaining (PrevHash), Merkle inclusion proofs, or both — and what is the resulting detection latency?
3. Are events signed using Ed25519 (or equivalent), with the algorithm identified in each event?
4. Does your system build RFC 6962 (domain-separated) Merkle trees over event batches?
5. Are signed Merkle roots anchored to an external, independently verifiable target, and at what frequency?
6. Does each anchor record bind event count, first/last event identifiers, and the policy identifier (Completeness Invariant, INT-008)?
7. Is there a documented anchor continuity plan with a fallback target (INT-007)?

### Provenance and Traceability Layers

8. What timestamp precision and clock-synchronisation evidence does your system record?
9. Are actor, input, context, action, and outcome recorded for each decision?
10. Are related events grouped by trace_id, and can causal chains be reconstructed?

## Related Resources

- [VAP Framework Specification v1.2](../spec/v1.2/VAP_Framework_Specification.md)
- [VCP benchmark: scoring rubric and PDFs](https://github.com/veritaschain/vcp-spec/tree/main/benchmark)

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines on improving the Scorecard.

---

<p align="center">
  <strong>VeritasChain Standards Organization</strong><br/>
  <em>"Verify, Don't Trust"</em>
</p>
