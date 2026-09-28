# Verifiable AI Provenance Framework (VAP)

## Framework Specification v1.2

**Document ID:** VSO-VAP-SPEC-001
**Status:** Draft Specification (Draft 3)
**Version:** 1.2.0
**Date:** 2026-09-01 (publication folds G-2, H-2, A-4 and post-publication fold B-5 applied 2026-09-28; see Appendix D)
**Supersedes:** Draft 2 (2026-06-10). Draft 3 folds the cross-profile alignment
review **VSO-VAP-ALIGN-001** into this document. Per VSO practice, pre-release
review findings fold directly into the draft with a disposition record and do
not spawn a new change number or a version increment; the version therefore
remains **1.2.0**, and downstream profiles citing "VAP v1.2.0" require no
revision. Dispositions are recorded in **Appendix D**.
**Maintainer:** VeritasChain Standards Organization (VSO)
**License:** CC BY 4.0 International
**Website:** <https://veritaschain.org>
**Change Control:** VSO-VAP-CHANGE-001 (normative annex to this specification)

> **Implementation status (mandatory disclosure).** As of this draft: **zero
> external implementations and zero Evidence Packs accepted in any proceeding**
> — for VAP or for any VAP profile. VeritasChain Co., Ltd., which provides the
> operating base of VSO, holds ten paid service contracts with European
> organizations in regulatory technology, financial trading, and audit and
> assurance; client names are withheld pending individual consent. Those
> contracts are not external implementations and are not independent validation
> of this framework. Nothing in this document is a claim of deployment,
> adoption, or evidentiary acceptance.

> **Standing of this document.** VAP is maintained by the VeritasChain Standards
> Organization. It has not been adopted by, and carries no standing within, the
> IETF, ISO/IEC JTC 1/SC 42, ITU-T, or any other established standards body.
> The related Internet-Drafts are individual submissions (§11.4).

---

## Executive Summary

**VAP (Verifiable AI Provenance Framework)** is a **cross-domain upper-level framework** that defines the structural requirements for cryptographically verifiable decision provenance common to all high-risk AI systems.

VAP is not a regulation that restricts AI usage. Its purpose is to standardize **the provenance infrastructure required for the safe and continuous operation of AI systems.**

**The scope of VAP is explicit: domains where system failure can cause irreversible harm to human life, societal infrastructure, or democratic institutions.**

Across the mandatory application domains of finance, healthcare, transportation, energy, and public policy — and the profile-served domains of content/creative AI and capture provenance — transparency and traceability of AI decisions are not optional features. They are mandatory requirements for societal infrastructure.

**What is new in v1.2.** Version 1.2 is a **framework-compatible / certification-stricter** revision; all v1.1-conformant event data remains valid (event-data-compatible at the wire level). The revision (a) repairs the normative misalignment between VAP v1.1 and the VCP v1.1/v1.2 profile by abstracting "Hash Chain MUST" into "Cryptographic Sequence Verifiability MUST", (b) elevates external anchoring to a MUST at **all** conformance levels, and (c) promotes capabilities proven at the profile level — completeness verification (omission-evidence), policy identification, ERASURE (crypto-shredding) events, bounded RECOVERY operations, cross-party provenance, and SCITT/COSE interoperability — into the Shared Assurance Core. The full rationale, classification, migration plan, and decision log are recorded in **VSO-VAP-CHANGE-001**.

---

## Normative Position Statement

### The VAP/VSO/Profile Hierarchy

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│     VAP (Verifiable AI Provenance Framework)                    │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                    │
│     Conceptual upper-level framework for AI decision provenance │
│     Defines minimum requirements and abstract layers common     │
│     to all domains                                              │
│                                                                 │
│                          ▲                                      │
│                          │ defines & maintains                  │
│                          │                                      │
│     VSO (VeritasChain Standards Organization)                   │
│     ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                   │
│     Standards organization that develops and maintains VAP      │
│     Ensures consistency across domain profiles                  │
│                                                                 │
│                          │                                      │
│                          │ publishes profiles                   │
│                          ▼                                      │
│                                                                 │
│   ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐  │
│   │  VCP  │ │  CAP  │ │  CPP  │ │  DVP  │ │  MAP  │ │  PAP  │ …│
│   │Finance│ │Content│ │Capture│ │ Auto  │ │Medical│ │Public │  │
│   └───────┘ └───────┘ └───────┘ └───────┘ └───────┘ └───────┘  │
│                                                                 │
│     Domain-specific profile implementations                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Analogous Standards Bodies

| Standards Body            | Domain                     | Framework/Protocol                       |
| ------------------------- | -------------------------- | ---------------------------------------- |
| **W3C**                   | Web                        | HTML, CSS, DOM                           |
| **IETF**                  | Network                    | TCP/IP, HTTP, TLS                        |
| **IEEE**                  | Electronics/Communications | 802.11 (WiFi), 1588 (PTP)                |
| **FIX Trading Community** | Financial Trading          | FIX Protocol                             |
| **VSO**                   | **AI Decision Provenance** | **VAP Framework, VCP, CAP, CPP, OAP...** |

**VSO develops and maintains VAP as a standards organization for AI decision provenance.** The comparison above is structural — it identifies the layer at which VSO operates — and is not a claim of equivalent status, recognition, or adoption. VSO's neutrality rests on published mechanisms, not on legal form: specifications are published under CC BY 4.0, conformity assessment is performed by independent Conformity Assessment Bodies rather than by VSO (§10.1), and vendor non-endorsement is a published policy.

---

## Table of Contents

1. Introduction
2. High-Risk AI Domains
3. Framework Architecture
4. Core Layers (including §4.6 Cross-Cutting Capabilities)
5. Domain Profiles
6. Cryptographic Requirements
7. Data Model
8. Conformance Levels
9. Implementation Guidelines
10. Governance and Standardization
11. Relation to International Standards
12. References

---

## 1. Introduction

### 1.1 Purpose

VAP (Verifiable AI Provenance Framework) is an upper-level framework designed to address the following structural challenges:

| Challenge                    | Description                                              | VAP Mechanism                                                |
| ---------------------------- | -------------------------------------------------------- | ------------------------------------------------------------ |
| **Non-reproducibility**      | AI decision processes cannot be reproduced               | Provenance Layer records decision lineage                    |
| **Absence of records**       | Decision-making processes are not recorded               | Integrity Layer provides automated logging                   |
| **Tamperability**            | Audit records can be retroactively modified              | EventHash + Merkle Tree + External Anchoring make retroactive modification detectable (tamper-evidence) |
| **Incompleteness**           | Records can be selectively omitted or forked (split-view) | Completeness Invariant binds anchored batches to declared scope (v1.2) |
| **Ambiguous accountability** | Responsible parties cannot be identified after incidents | Accountability Layer makes responsibility boundaries visible |

### 1.2 Design Philosophy

VAP is guided by the following principle:

> **"Not a regulation that restricts AI usage, but a common provenance infrastructure for the safe and continuous operation of AI systems."**

By ensuring transparency and traceability of AI decision processes without impeding technological progress, VAP enables continued AI adoption while maintaining societal trust. The operational principle is **"Verify, Don't Trust"**: every integrity claim made by a VAP-conformant system MUST be independently verifiable without relying on the entity making the claim.

### 1.3 Scope Definition

VAP targets **"domains where system failure can cause serious and irreversible harm to human life, societal infrastructure, or democratic institutions."**

This definition is intentionally strict. VAP is not a general-purpose logging framework — it is **provenance infrastructure essential for AI systems operating as societal infrastructure.**

### 1.4 Conformance Language

In this specification, the key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, NOT RECOMMENDED, MAY, and OPTIONAL are to be interpreted as described in RFC 2119 and RFC 8174 when, and only when, they appear in all capitals.

### 1.5 Terminology

| Term             | Definition                                                                           |
| ---------------- | ------------------------------------------------------------------------------------ |
| **VAP**          | Verifiable AI Provenance Framework — Cross-domain upper-level framework              |
| **VSO**          | VeritasChain Standards Organization — Standards body that develops and maintains VAP |
| **Profile**      | Domain-specific implementation of VAP (VCP, CAP, CPP, OAP, MAP, PAP, etc.). The designation **"Protocol"** within the VAP family is reserved exclusively for **VCP**, which defines an actual wire protocol; every other family member is a Profile or a cross-cutting Capability. |
| **Cross-Cutting Capability** | An evidence requirement defined once at the Shared Assurance Core and inherited by any profile that invokes it, because it is not bounded to a domain (DAP, SMP). See §4.6. |
| **Shared Assurance Core** | The set of framework-level requirements inherited by every profile and capability without redefinition: §4.1–§4.4 layers, external anchoring (INT-006), anchor continuity (INT-007), the Completeness Invariant (INT-008), bounded RECOVERY (INT-009), ERASURE (§6.3), Policy Identification, XREF (TRC-005), and Evidence Packs (§9.3). |
| **Provenance**   | Cryptographically verifiable record of data origin, lineage, and history             |
| **High-Risk AI** | High-risk AI systems as defined in EU AI Act Article 6                               |
| **Cryptographic Sequence Verifiability** | The property that the ordering and membership of recorded events can be verified by a third party via cryptographic mechanisms (v1.2) |
| **Completeness Invariant** | The property that, for any anchored batch, omission of in-scope events after anchoring is third-party detectable (v1.2) |
| **External Anchor** | Publication of a signed Merkle Root to an independently verifiable external target (TSA, transparency log, public blockchain, or transparency service) |
| **ERASURE Event** | An append-only event recording crypto-shredding of protected fields (v1.2) |
| **Cross-Party Provenance (XREF)** | Independent, cross-referenced logging of corresponding events by two or more parties (v1.2) |

### 1.6 Legal Scope and Non-Guarantee Statement (Normative)

> VAP and its domain profiles define mechanisms for producing **cryptographically verifiable evidence** of AI system decisions. Conformance to VAP or any profile: (a) does **not** constitute compliance with the EU AI Act, GDPR, MiFID II/III, CAT Rule 613, NIS2, FDA SaMD guidance, or any other law or regulation; (b) does **not** constitute a legal determination that any technical mechanism (including crypto-shredding) satisfies a specific legal obligation; (c) does **not** warrant the correctness, fairness, or safety of the underlying AI decisions — only the integrity, completeness (at anchor granularity), and attributability of their records. VAP generates evidence; competent authorities and courts evaluate it.

Profiles SHOULD adopt this statement verbatim.

### 1.7 Change Control

Changes between v1.1 and v1.2 are governed by **VSO-VAP-CHANGE-001**, which is a normative annex of this specification. CHANGE-001 records: the problem statement (VAP/VCP normative misalignment), change classification (zero wire-format breaking changes; certification-level tightening), the migration plan and grace periods, the compatibility matrix, deferred items, and the Technical Committee decision log. Where this specification and CHANGE-001 differ in detail, this specification prevails.

---

## 2. High-Risk AI Domains

### 2.1 Normative Scope Statement

**VAP is designed as an audit infrastructure for AI decisions in domains where system failure can cause serious and irreversible harm to human life, societal infrastructure, or democratic institutions.**

The five domains in §2.2.1–§2.2.5 are **Mandatory Application Domains** for VAP. The domains in §2.2.6 are **Profile-Served Domains**: domains served by released VSO profiles on the basis of evidence-integrity and societal-trust needs, without asserting that every system in those domains meets the irreversible-harm test.

### 2.2 Domain Definitions

#### 2.2.1 Financial Infrastructure

| Attribute         | Value                            |
| ----------------- | -------------------------------- |
| **Profile ID**    | VCP (VeritasChain Protocol)      |
| **Status**        | v1.2 Released                    |
| **Risk Category** | Systemic Risk / Market Integrity |

**Scope:** High-frequency trading (HFT) systems; AI/algorithm-driven trading strategies; exchanges, clearinghouses, prime brokers; risk management systems; credit scoring AI.

**Failure Impact:** Sudden market volatility caused by AI/HFT malfunction; cascading impact on pension funds, corporate finance, and national fiscal systems; materialization of systemic risk (2010 Flash Crash: ~$1 trillion evaporated in minutes).

**Regulatory Drivers:** EU AI Act Article 6(2) (credit scoring as high-risk AI); MiFID II Article 17 (algorithmic trading audit requirements); CAT Rule 613.

**VAP Requirements:** Cryptographic sequence-verifiable recording of trading events; preservation of AI decision rationale (DecisionFactors); nanosecond-precision timestamp synchronization at the highest tiers.

#### 2.2.2 Medical and Healthcare AI

| Attribute         | Value                          |
| ----------------- | ------------------------------ |
| **Profile ID**    | MAP (Medical AI Profile)       |
| **Status**        | v0.1.2 Working Draft           |
| **Risk Category** | Patient Safety / Life-Critical |

**Scope:** AI diagnostic support; imaging AI (radiology, pathology); triage and priority assessment; medication recommendation and drug interaction checking; surgical robot decision logic.

**Failure Impact:** Direct patient harm from diagnostic errors; severe adverse effects from medication errors; delayed appropriate care from triage misjudgment.

**Regulatory Drivers:** EU AI Act Annex III; FDA AI/ML-Based SaMD Guidance; MDR 2017/745.

**VAP Requirements:** Complete recording and reconstruction capability for diagnostic rationale; identification of data and model versions used; capability to provide evidence for incident investigation and litigation.

#### 2.2.3 Transportation and Autonomous Systems

| Attribute         | Value                                                       |
| ----------------- | ----------------------------------------------------------- |
| **Profile ID**    | DVP (Driving Vehicle Profile) / AAP (Aviation AI Profile)   |
| **Status**        | Planned                                                     |
| **Risk Category** | Physical Safety / Mass Casualty Prevention                  |

**Scope:** Autonomous vehicles (Level 3–5); ADAS; aircraft autopilot and air traffic control AI; railway operations management; autonomous drone control.

**Failure Impact:** Traffic accidents from autonomous driving misjudgment; aviation accident risk from ATC AI malfunction; service disruption from railway control errors.

**Regulatory Drivers:** EU AI Act Annex III; UNECE WP.29; FAA Advisory Circular 23.1309-1E.

**VAP Requirements:** Integration of physical flight recorder with AI decision recorder; complete causal chain recording from sensor input → decision → control output; compatibility between real-time recording and offline verification.

> **The ultimate form for this domain is AI decision-level provenance recording in addition to physical flight recorders.**

#### 2.2.4 Energy and Critical Infrastructure

| Attribute         | Value                                         |
| ----------------- | --------------------------------------------- |
| **Profile ID**    | EIP (Energy Infrastructure Profile)           |
| **Status**        | Planned                                       |
| **Risk Category** | Societal Continuity / Critical Infrastructure |

**Scope:** Power grid management and supply-demand balancing AI; water network monitoring and control; telecommunications infrastructure management AI; gas pipeline control; nuclear power plant monitoring.

**Failure Impact:** Large-scale blackouts from power grid AI malfunction; water quality and supply impacts; cascading effects on emergency services and financial systems from telecom infrastructure failure.

**Regulatory Drivers:** EU NIS2 Directive; NERC CIP Standards; EU AI Act.

**VAP Requirements:** Root cause tracking for anomalous AI decisions; state reconstruction for failure recovery; root cause analysis for cascading failures.

> **Infrastructure directly tied to societal continuity. Decision history tracing is indispensable for recovery.**

#### 2.2.5 Public Policy, Law Enforcement, and Justice

| Attribute         | Value                                |
| ----------------- | ------------------------------------ |
| **Profile ID**    | PAP (Public Administration Profile)  |
| **Status**        | Partial Draft (Track B v0.2.0)       |
| **Risk Category** | Democratic Integrity / Civil Rights  |

**Scope:** Credit scoring and loan assessment AI; welfare benefit determination; immigration and visa assessment AI; recidivism prediction; recruitment and performance evaluation AI.

**Failure Impact:** If decision rationale cannot be traced, appeals and judicial review become difficult; entrenchment of unfair determinations from biased AI; algorithmic decision-making without democratic oversight.

**Regulatory Drivers:** EU AI Act Article 6(2); GDPR Article 22; US Executive Order 14110.

**VAP Requirements:** Full explainability of decisions affecting individuals; post-hoc audit and appeal response capability; transparency for democratic oversight. The Completeness Invariant (§4.1.7) is load-bearing in this domain: proving that a decision was or was not recorded is central to appeals.

> **AI whose decision rationale cannot be traced undermines the foundation of democratic accountability.**

#### 2.2.6 Profile-Served Domains (v1.2)

| Domain | Profile | Status | Risk Category |
| ------ | ------- | ------ | ------------- |
| Content / Creative AI | **CAP** (Content / Creative AI Profile) | v1.0 Released | IP Rights / Misinformation |
| Capture Provenance | **CPP** (Capture Provenance Profile) | v1.4 Released | Evidence Integrity / Misinformation |
| Observed Artifact Provenance | **OAP** (Observed Artifact Provenance) | v0.1.1 Working Draft | Evidence Integrity / Repudiation |
| Industry Extensions | **IAP** (Industry Accountability Profile) | Announced | Sector-Specific Governance |

**CAP** defines a verifiable evidence layer for AI workflows involving content and intellectual property — covering ingestion, training, generation, and export — so that disputes can be examined with verifiable records.

**CPP** defines media capture verification — recording when, where, and by whom photographs and videos were taken — to support evidence integrity and counter synthetic-media misinformation.

**OAP** defines provenance for third-party web resources observed at a URL. Where CPP records material captured by a device the operator controls, OAP records material published by someone else, retrieved over a network, and preserved because it may later be disputed, deleted, edited, or denied.

**Naming.** "Content" is the domain term of **CAP**; "Capture" is the domain term of **CPP**. Materials, repositories, and Internet-Drafts that expand CPP as "Content Provenance Profile" are to be corrected at their next revision (VSO-VAP-ALIGN-001 §12).

### 2.3 Domain Classification Matrix

| Domain         | Profile | Failure Mode              | Time to Impact | Reversibility |
| -------------- | ------- | ------------------------- | -------------- | ------------- |
| Financial      | VCP     | Systemic Instability      | Milliseconds   | Partial       |
| Medical        | MAP     | Patient Harm              | Minutes–Hours  | Irreversible  |
| Transportation | DVP/AAP | Physical Harm             | Seconds        | Irreversible  |
| Energy         | EIP     | Infrastructure Disruption | Minutes–Days   | Slow Recovery |
| Public Policy  | PAP     | Institutional Erosion     | Months–Years   | Difficult     |
| Content/Creative | CAP   | IP Violation / Misinformation | Hours–Months | Difficult |
| Capture        | CPP     | Evidentiary Corruption    | Immediate–Years | Difficult    |
| Observed Artifact | OAP  | Repudiation / Loss of Record | Immediate–Years | Difficult |

### 2.4 Common Requirements Across Domains

| Requirement ID | Requirement                                          | Rationale                           |
| -------------- | ---------------------------------------------------- | ----------------------------------- |
| **HR-001**     | Cryptographic integrity (Sequence Verifiability)     | Tamper detection                    |
| **HR-002**     | Decision lineage recording (Provenance)              | Reconstruction capability           |
| **HR-003**     | Causal chain tracing (Traceability)                  | Root cause analysis                 |
| **HR-004**     | Accountability boundary definition (Accountability)  | Legal responsibility identification |
| **HR-005**     | Explainability                                       | Regulatory and litigation response  |
| **HR-006**     | Privacy protection (Privacy)                         | GDPR-class obligations              |
| **HR-007**     | Completeness (omission/split-view detectability)     | Evidence credibility (v1.2)         |
| **HR-008**     | External verifiability (independent anchoring)       | "Verify, Don't Trust" (v1.2)        |

### 2.5 Domain Selection Criteria

#### 2.5.1 Selection Criteria

Mandatory Application Domains were selected based on: (1) **Irreversibility** — consequences of decision errors are difficult or impossible to recover from; (2) **Scale** — impact affects society as a whole, not just individuals; (3) **Velocity** — impact propagates faster than human intervention can prevent; (4) **Regulatory Mandate** — existing or planned regulations require transparency.

#### 2.5.2 Strategic Implications

| Implication                                       | Description                                                                        |
| ------------------------------------------------- | ---------------------------------------------------------------------------------- |
| **VAP universality**                              | Demonstrates VAP as a general-purpose framework, not limited to finance            |
| **VAP necessity**                                 | Establishes positioning as the upper layer of AI societal infrastructure           |
| **Lower adoption barriers**                       | Provides rational grounds for non-financial organizations to adopt VAP conformance |
| **Prevention of standards fragmentation**         | Prevents proliferation of domain-specific protocols, ensuring interoperability     |
| **Facilitation of international standardization** | Smooths transition to ISO and other international standardization processes        |

---

## 3. Framework Architecture

### 3.1 Layered Architecture

VAP comprises the following five mandatory layers:

```
┌─────────────────────────────────────────────────────────────┐
│                   Domain Profiles Layer                      │
│   ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐        │
│   │  VCP  │ │  CAP  │ │  CPP  │ │  DVP  │ │  MAP  │  ...   │
│   └───────┘ └───────┘ └───────┘ └───────┘ └───────┘        │
├─────────────────────────────────────────────────────────────┤
│                  Accountability Layer                        │
│   Responsibility identification · Boundary definition ·     │
│   Audit trails                                               │
├─────────────────────────────────────────────────────────────┤
│                  Traceability Layer                          │
│   Causal structure reconstruction · Temporal tracking ·      │
│   Cross-party provenance (XREF) · Incident analysis          │
├─────────────────────────────────────────────────────────────┤
│                   Provenance Layer                           │
│   Actor / Input / Context / Action / Outcome recording       │
├─────────────────────────────────────────────────────────────┤
│                    Integrity Layer                           │
│   EventHash · Sequence Verifiability · Merkle Tree ·         │
│   External Anchoring · Digital Signatures                    │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Layer Dependency

```
Domain Profiles ──depends on──▶ Accountability Layer
                                       │
                               depends on
                                       ▼
                              Traceability Layer
                                       │
                               depends on
                                       ▼
                               Provenance Layer
                                       │
                               depends on
                                       ▼
                               Integrity Layer
```

### 3.3 Cross-Cutting Concerns

| Concern                   | Description                  | Implementation Requirement             |
| ------------------------- | ---------------------------- | -------------------------------------- |
| **Privacy**               | Personal data protection     | Crypto-shredding (§6.3), anonymization |
| **Security**              | Cryptographic security       | Ed25519/ML-DSA, SHA-256/SHA3           |
| **Performance**           | Low latency, high throughput | Tier-specific performance requirements |
| **Interoperability**      | Cross-system integration     | JSON/SBE, standard APIs                |
| **Policy Identification** | Self-declared verification policy per event | `policy` object (§7.1), reverse-domain PolicyID (v1.2) |

---

## 4. Core Layers

### 4.1 Integrity Layer

#### 4.1.1 Purpose

Provides cryptographic mechanisms that make alteration **and post-anchor omission** of AI decision events detectable (tamper-evidence and omission-evidence), independently verifiable by third parties.

#### 4.1.2 Requirements

| Req ID   | Requirement                                                                                                                                                                                                                                                                                                                                                                  | Level  |
| -------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------ |
| INT-001  | All events MUST be canonicalized per RFC 8785 prior to hashing                                                                                                                                                                                                                                                                                                                | MUST   |
| INT-002  | Each event MUST have a unique identifier (UUID v7 recommended)                                                                                                                                                                                                                                                                                                                | MUST   |
| INT-003  | Every event MUST carry an EventHash computed over its canonicalized form using an approved hash algorithm (SHA-256 or stronger)                                                                                                                                                                                                                                               | MUST   |
| INT-004  | VAP-level event sequencing MUST be cryptographically verifiable (**Cryptographic Sequence Verifiability**). This MAY be achieved through a profile-defined combination of: (a) per-event hash chaining (PrevHash), (b) Merkle inclusion proofs over event batches (RFC 6962), (c) external anchoring of batch roots, or (d) equivalent mechanisms providing tamper-evidence and ordering properties of at least equal strength. Profiles MUST specify which mechanisms are mandatory at each conformance level and MUST document the resulting detection latency (real-time vs. batch-time) | MUST   |
| INT-004a | Per-event hash chaining (PrevHash) is an OPTIONAL local integrity mechanism at the framework level. Profiles MAY require it (e.g., for real-time tamper detection in HFT or safety-critical control loops). Profiles for domains with regulator-familiar chain-of-custody expectations SHOULD recommend it                                                                       | OPTIONAL |
| INT-005  | Non-repudiation SHOULD be achieved via digital signatures or TEE signatures (elevation to MUST is deferred; see VSO-VAP-CHANGE-001 Annex C.2)                                                                                                                                                                                                                                  | SHOULD |
| INT-006  | Merkle batching and external anchoring of signed roots is REQUIRED at **all** conformance levels, including VAP-Core. Anchoring frequency, acceptable anchor target classes, and proof depth are delegated to profiles and conformance levels. Lightweight or delegated anchoring mechanisms (e.g., public timestamping services) are explicitly acceptable at the lowest conformance levels | MUST   |
| INT-007  | Implementations MUST document an **anchor continuity plan**: (a) at least one designated fallback anchor target of an acceptable class; (b) a failover procedure with a maximum migration window (profile-defined; 30 days RECOMMENDED as the framework default); (c) retention of local copies of all AnchorRecords sufficient to verify historical anchors if the original target becomes unavailable. Temporary outages MUST be handled by queueing with retry; anchor gaps exceeding 2× the profile-defined anchoring interval MUST be recorded as an error-class event | MUST   |
| INT-008  | **Completeness Invariant:** a third party MUST be able to verify, for any anchored batch, that no events within the batch's declared scope were omitted after anchoring (omission / split-view detection). Each AnchorRecord MUST bind, at minimum: event count, first/last event identifiers, and the policy identifier under which the batch was produced                       | MUST   |
| INT-009  | Any recovery operation that alters the effective event sequence (SKIP, REBUILD, MERGE, CHECKPOINT, or profile-defined equivalents) MUST be **bounded** (profiles MUST define quantitative limits per operation type and conformance level), **recorded** (logged as a chained/anchored event referencing the break point and validation evidence), and **authorized** (recovery beyond profile-defined bounds MUST require an Emergency Override with explicit, recorded approval by an identified human actor, flagged in conformance reporting). Recovery events MUST NOT be filtered from anchor batches | MUST (when used) |

> **Completeness scope note (normative):** Completeness is verifiable **only at anchor time and at batch granularity**. Profiles MUST state the completeness window implied by their anchoring frequency (e.g., a 24-hour anchoring interval provides batch-level completeness, with gaps possible within the window) and MUST require disclosure of this limitation when evidence is presented to authorities.

#### 4.1.3 Sequence Verifiability Mechanisms

**Mechanism A — Per-event hash chaining (OPTIONAL, profile-mandatable):**

```
Event_n = {
    Header,
    Payload,
    Security: {
        event_hash: H(canonical(Header) || canonical(Payload) || prev_hash),
        prev_hash: Event_(n-1).event_hash,    // OPTIONAL (INT-004a)
        signature: Sign(event_hash, private_key)
    }
}
```

**Hash Chain Validation Algorithm (normative when PrevHash is in use):**

```
Algorithm: VAP Hash Chain Validation
Input: Sequence of events E₁, E₂, ..., Eₙ
Output: VALID or INVALID with error location

1: h ← GENESIS_HASH
2: for i = 1 to n do
3:     if Eᵢ.prev_hash ≠ h then
4:         return INVALID: Chain break at event i
5:     end if
6:     h' ← H(canonical(Eᵢ.Header) || canonical(Eᵢ.Payload) || h)
7:     if h' ≠ Eᵢ.event_hash then
8:         return INVALID: Hash mismatch at event i
9:     end if
10:    h ← h'
11: end for
12: return VALID
```

**Mechanism B — Merkle inclusion + external anchor (REQUIRED at all levels):**

```
Algorithm: VAP Batch Verification
Input: Event E, audit path P, AnchorRecord A, anchor target T
Output: VALID or INVALID

1: leaf ← H(0x00 || canonical(E))
2: root ← FoldAuditPath(leaf, P)            // RFC 6962 path computation
3: if root ≠ A.merkle_root then return INVALID: Inclusion failure
4: if !VerifySignature(A) then return INVALID: Anchor signature failure
5: if !VerifyExternal(A, T) then return INVALID: External anchor mismatch
6: if !CheckCompleteness(A) then return INVALID: Count/range/policy binding failure
7: return VALID
```

When PrevHash is present, verifiers SHOULD execute both mechanisms; a failure in either is a verification failure.

#### 4.1.4 Merkle Tree Anchoring

Merkle Tree construction conforming to RFC 6962 (Certificate Transparency) is **REQUIRED**:

```
Leaf(D) = H(0x00 || D)         // Leaf node
Node(L, R) = H(0x01 || L || R) // Internal node
```

**Domain Separation (0x00/0x01 prefix) is REQUIRED to prevent second preimage attacks.**

Each batch closure MUST produce a signed **AnchorRecord** (§7.5) bound to an external anchor target. Acceptable anchor target classes (profiles select per conformance level): RFC 3161 Time-Stamp Authority; RFC 6962-class public transparency log; public blockchain; SCITT-conformant transparency service (§11.3); delegated/aggregated public timestamping services (lowest levels).

#### 4.1.5 Cryptographic Algorithm Support

| Algorithm        | Type      | Status         | Post-Quantum Safe           |
| ---------------- | --------- | -------------- | --------------------------- |
| **SHA-256**      | Hash      | DEFAULT        | Partial (128-bit effective) |
| SHA3-256         | Hash      | SUPPORTED      | Partial                     |
| BLAKE3           | Hash      | SUPPORTED      | Partial                     |
| **Ed25519**      | Signature | DEFAULT        | No                          |
| ECDSA secp256k1  | Signature | SUPPORTED      | No                          |
| RSA-2048         | Signature | **DEPRECATED** (removal planned in VAP v2.0) | No |
| **ML-DSA (FIPS 204)** (formerly DILITHIUM2) | Signature | **EXPERIMENTAL** | Yes |
| **FN-DSA (FIPS 206, draft)** (formerly FALCON-512) | Signature | **EXPERIMENTAL** | Yes |

**Status semantics:** DEFAULT/SUPPORTED algorithms are eligible for conformance claims. EXPERIMENTAL algorithms are approved for testing and hybrid deployments (§6.2.2) and are not certification requirements. DEPRECATED algorithms MUST NOT be used for new deployments and will be removed in the indicated version.

**Crypto Agility Requirement:** All VAP-conformant implementations MUST include fields identifying the hash and signature algorithms in use, and MUST enable future algorithm migration.

#### 4.1.6 Recovery Operations (informative summary)

INT-009 generalizes profile experience (VCP-RECOVERY): recovery is a legitimate operational need and a potential laundering vector. The framework therefore constrains *how* recovery happens (bounded, recorded, authorized) and leaves *limits* to profiles. Unbounded or unrecorded recovery is non-conformant at every level.

#### 4.1.7 Completeness Invariant (informative summary)

Tamper-evidence answers "were these records altered?"; the Completeness Invariant answers "are these all the records?". Both are required for evidentiary credibility. The invariant is enforced through AnchorRecord bindings (count, range, policy) and external anchoring, which together make post-anchor omission and split-view presentations detectable by any verifier holding the anchor.

---

### 4.2 Provenance Layer

#### 4.2.1 Purpose

Records AI decision lineage in structured form: who acted, what they received, under what conditions, what they referenced, and what they produced.

#### 4.2.2 Abstract Data Model

```json
{
  "provenance": {
    "actor": {
      "type": "enum",           // AI_MODEL, HUMAN, EXTERNAL_AGENT, HYBRID
      "identifier": "string",
      "version": "string",      // Version info (for AI_MODEL)
      "hash": "string"          // Model parameter hash (for AI_MODEL)
    },
    "input": {
      "sources": ["array"],
      "timestamp": "int64",
      "hash": "string"
    },
    "context": {
      "parameters": "object",
      "constraints": "object",
      "environment": "object"
    },
    "action": {
      "type": "string",
      "decision": "object",
      "confidence": "string",   // 0.0–1.0, string-encoded (§7.2)
      "explainability": {
        "method": "enum",       // SHAP, LIME, GRADCAM, RULE_TRACE, NONE
        "factors": ["array"]
      }
    },
    "outcome": {
      "result": "object",
      "timestamp": "int64",
      "status": "enum"          // SUCCESS, FAILURE, PARTIAL, PENDING
    }
  }
}
```

#### 4.2.3 Domain Profile Mapping

| VAP Abstract | VCP (Finance)         | CAP (Content)              | CPP (Capture)            | DVP (Automotive)            | MAP (Medical)            | PAP (Public)            |
| ------------ | --------------------- | -------------------------- | ------------------------ | --------------------------- | ------------------------ | ----------------------- |
| actor        | Algorithm/Trader      | GenModel/Creator           | CaptureDevice/Operator   | AutonomousSystem/Driver     | DiagnosticAI/Physician   | ScoringAI/Officer       |
| input        | MarketData/Signals    | SourceAssets/Prompts       | SensorFrame/Geo/Time     | SensorData/LIDAR/Camera     | PatientData/Imaging      | ApplicationData/Records |
| context      | RiskParameters/Limits | LicenseTerms/ModelConfig   | DeviceState/Calibration  | EnvironmentConditions/Route | ClinicalProtocol/History | PolicyRules/Guidelines  |
| action       | TradeSignal/Order     | Generation/Transformation  | Capture/Attestation      | PathPlanning/Control        | Diagnosis/TreatmentPlan  | Decision/Recommendation |
| outcome      | Execution/Fill        | Export/Publication         | MediaArtifact/Proof      | VehicleState/Maneuver       | PatientOutcome/Response  | Determination/Appeal    |

---

### 4.3 Traceability Layer

#### 4.3.1 Purpose

Enables reconstruction of decision chains in both temporal sequence and causal structure — within a single party's records and, where used, across parties.

#### 4.3.2 Requirements

| Req ID  | Requirement                                                             | Level  |
| ------- | ----------------------------------------------------------------------- | ------ |
| TRC-001 | MUST be capable of expressing causal relationships between events       | MUST   |
| TRC-002 | MUST be capable of grouping related events via trace_id                 | MUST   |
| TRC-003 | SHOULD be capable of reconstructing system state at any point in time   | SHOULD |
| TRC-004 | SHOULD provide query capabilities supporting root cause analysis (RCA)  | SHOULD |
| TRC-005 | Profiles MAY define a **Cross-Party Provenance (XREF)** mechanism whereby two or more parties independently log corresponding events sharing a `cross_reference_id` (UUID v4/v7) and a shared event key with declared matching tolerance. When used: each party MUST anchor independently; party roles MUST be declared (INITIATOR / COUNTERPARTY / OBSERVER); reconciliation status and discrepancy severity MUST follow the common enums (PENDING / MATCHED / DISCREPANCY / TIMEOUT; INFO / WARNING / CRITICAL); multi-actor chains (>2 parties) MUST define ordering and reference rules | OPTIONAL (MUST-level when used) |

> **XREF detection statement:** absent collusion of all participating parties **and** compromise of their independent anchors, unilateral omission or modification is detectable. Missing counterparty records are themselves evidence.

Cross-domain instantiations (informative): trader↔broker (VCP); creator↔platform (CAP); capture device↔verification service (CPP); hospital↔AI vendor (MAP); agency↔independent auditor with OBSERVER role (PAP); OEM↔fleet operator (DVP).

#### 4.3.3 Causal Chain Model

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Input   │────▶│ Action  │────▶│ Outcome │────▶│ Impact  │
│ Event   │     │ Event   │     │ Event   │     │ Event   │
└─────────┘     └─────────┘     └─────────┘     └─────────┘
     │               │               │               │
     └───────────────┴───────────────┴───────────────┘
                          │
                    [trace_id: common]
```

#### 4.3.4 Domain-Specific Causal Chains

**Finance (VCP):** Signal Generated (SIG) → Order Sent (ORD) → Acknowledged (ACK) → Executed (EXE) → Position Closed (CLS)

**Content (CAP):** Ingestion → Training/Configuration → Generation → Transformation → Export/Publication

**Capture (CPP):** Sensor Capture → Device Attestation → Proof Generation → Registration → Verification

**Automotive (DVP):** Sensor Input → Perception → Path Planning → Control Command → Vehicle State

**Medical (MAP):** Patient Data → Analysis → Diagnosis → Treatment Plan → Outcome

**Public (PAP):** Application → Evaluation → Scoring → Decision → Notification → Appeal

---

### 4.4 Accountability Layer

#### 4.4.1 Purpose

Enables identification of responsible parties in AI-involved decisions.

#### 4.4.2 Actor Types

| Actor Type                 | Description          | Example                   |
| -------------------------- | -------------------- | ------------------------- |
| **MODEL_DEVELOPER**        | AI model developer   | Machine learning engineer |
| **AI_PROVIDER**            | AI system provider   | SaaS vendor               |
| **OPERATOR**               | Operator             | Trader, driver, physician |
| **DATA_VENDOR**            | Data provider        | Market data vendor        |
| **FINAL_DECISION_MAKER**   | Final decision maker | Risk manager              |

#### 4.4.3 Responsibility Schema

```json
{
  "accountability": {
    "operator_id": "string",
    "last_approval_by": "string",
    "approval_timestamp": "int64",
    "delegation_chain": [
      {
        "delegator": "string",
        "delegatee": "string",
        "scope": "string",
        "valid_from": "int64",
        "valid_until": "int64"
      }
    ],
    "override_history": [
      {
        "original_action": "object",
        "override_action": "object",
        "override_by": "string",
        "reason": "string",
        "timestamp": "int64"
      }
    ]
  }
}
```

#### 4.4.4 Human Oversight Requirements

Addressing EU AI Act Article 14 (Human Oversight):

| Requirement             | VAP Implementation          |
| ----------------------- | --------------------------- |
| Enable human monitoring | operator_id field           |
| Intervention capability | HALT/OVERRIDE event types   |
| Override functionality  | override_history recording  |
| Bounded recovery        | INT-009 Emergency Override (v1.2) |

---

### 4.5 Domain Profiles Layer

#### 4.5.1 Purpose

Defines domain-specific extensions on top of VAP common layers. **One Core, Many Profiles** — profiles extend the Shared Assurance Core but never replace it.

#### 4.5.2 Profile Registry

| Profile ID | Domain                           | Status                          | Specification         |
| ---------- | -------------------------------- | ------------------------------- | --------------------- |
| **VCP**    | Finance / Algorithmic Trading    | **v1.2 Released**               | VSO-VCP-SPEC          |
| **CAP**    | Content / Creative AI            | **v1.0 Released**               | veritaschain/cap-spec |
| **CPP**    | Capture Provenance               | **v1.4 Released**               | veritaschain/cpp-spec |
| **OAP**    | Observed Artifact Provenance     | v0.1.1 Working Draft            | VSO-VAP-OAP-001       |
| **MAP**    | Medical / Healthcare AI          | v0.1.2 Working Draft            | VSO-VAP-MAP-001       |
| **PAP**    | Public Sector / Government AI    | Partial Draft (Track B v0.2.0)  | VSO-VAP-PAP-001       |
| IAP        | Industry Accountability          | Announced                       | —                     |
| DVP        | Automotive / Autonomous Driving  | Planned                         | —                     |
| AAP        | Aviation / Air Traffic Control   | Planned                         | —                     |
| EIP        | Energy / Critical Infrastructure | Planned                         | —                     |

**Status vocabulary (normative for this registry).**

| Status | Meaning |
| --- | --- |
| **Released** | Published, version-tagged, and under change control. A version number without a corresponding tagged release is not a Released version. |
| **Release Candidate** | Feature-complete, published for final review; no further normative additions expected. |
| **Working Draft** | Published for technical discussion. Event names, field names, and invariant formulations are provisional and expected to change. Not for production conformance claims. |
| **Partial Draft** | One or more tracks drafted; no consolidated profile specification exists. |
| **Announced** / **Planned** | No specification document exists. |

A profile MUST NOT be described publicly at a status higher than its registry
row. Where a repository badge, website, or press material disagrees with this
registry, this registry prevails.

Profiles released after the publication of this specification MUST target VAP v1.2 at first release (VSO-VAP-CHANGE-001 Annex B.2).

**Profiles outside this registry.** Third-party documents that describe VAP or
propose a VAP profile without VSO change control are not VSO profiles and confer
no status under this specification, whether or not they are published as
Internet-Drafts. The registry above is the complete list of VSO profiles.

#### 4.5.3 Profile Extension Mechanism

```json
{
  "profile_extension": {
    "profile_id": "string",
    "profile_version": "string",
    "min_vap_version": "string",
    "domain_specific_modules": ["array"],
    "domain_specific_events": ["array"],
    "domain_specific_constraints": {
      "timestamp_precision": "enum",
      "clock_sync_requirement": "enum",
      "sequence_mechanism_matrix": "object",   // per conformance level (INT-004)
      "anchoring_policy": "object",            // frequency, target classes, proof depth (INT-006)
      "recovery_bounds": "object"              // per operation type (INT-009)
    },
    "capabilities": [                          // cross-cutting capabilities in use (§4.6)
      { "capability_id": "string", "capability_version": "string" }
    ]
  }
}
```

`capabilities` is OPTIONAL and defaults to the empty array. Verifiers
encountering an unknown `capability_id` MUST fail gracefully (ignore-unknown,
§10.4), not reject the event.

### 4.6 Cross-Cutting Capabilities

#### 4.6.1 Purpose

Some evidence requirements are not bounded to a domain. Delegated authority is
exercised by an OS assistant, a SaaS workflow agent, a trading agent, and a
clinical documentation agent alike; self-modification is performed by finance,
content, and medical AI alike. Such requirements are defined **once, at the
Shared Assurance Core**, and are inherited by every profile that invokes them —
the same consolidation principle applied to the Completeness Invariant, external
anchoring, ERASURE, bounded RECOVERY, Policy Identification, XREF, and Evidence
Packs in v1.2.

A cross-cutting capability is **not** a domain profile. It declares no domain,
occupies no row in the §4.5.2 registry, defines no conformance tiers of its own
that could compete with a profile's, and may be composed with any profile.

#### 4.6.2 Capability Registry

| Capability ID | Common Name | Scope | Status | Specification |
| ------------- | ----------- | ----- | ------ | ------------- |
| **DAP** | VAP-AGENT | Delegated Access Provenance — agent access, tool invocation, action, and data transfer under delegated authority from a principal | v0.1.0 Working Draft | VSO-VAP-DAP-001 |
| **SMP** | VAP-SLEEP | Self-Modification Provenance — post-deployment parameter update, memory consolidation, synthetic rehearsal data, and production-version promotion | v0.2.0 Working Draft | VSO-VAP-SMP-SPEC-001 |

The status vocabulary of §4.5.2 applies unchanged.

#### 4.6.3 Composition Rules

1. A deployment MAY invoke zero or more capabilities alongside exactly one
   domain profile, and MUST declare each invoked capability in
   `profile_extension.capabilities` (§4.5.3).
2. Capabilities inherit the Shared Assurance Core directly (§4.1–§4.4). They
   MUST NOT redefine framework-level events, and MUST emit the framework
   **ERASURE** event (§6.3, §7.4) where they perform crypto-shredding of
   committed items.
3. Where a capability and a domain profile both constrain the same event class,
   **the stricter constraint applies**. Neither may relax a framework MUST.
4. A capability MUST NOT define conformance level names that collide with those
   of a domain profile. (SMP v0.2.0 renamed its levels to SMP-Core /
   SMP-Standard / SMP-Full for this reason.)
5. Capabilities are versioned independently of VAP and of any profile; §10.4
   applies to them unchanged.

#### 4.6.4 Relationship to Domain Profiles

Domain profiles SHOULD state, in their VAP alignment statement, which
capabilities they expect to be composed with and what the composition means in
that domain. Examples already recorded in profile drafts: MAP composes with SMP
for post-market model updates and with DAP for clinical documentation agents;
OAP composes with DAP where the observation is performed by an autonomous agent.

---

## 5. Domain Profiles

### 5.1 VCP: Finance Profile

**Status:** v1.2 Released (Production Ready, GA 2026-07-06; tag `v1.2.0`)
**Document:** VSO-VCP-SPEC (v1.2 incorporates VSO-SPEC-CHANGE-001 as a normative annex)

#### 5.1.1 Overview

VCP (VeritasChain Protocol) is the financial domain profile of VAP, standardizing audit trails for algorithmic trading and AI-driven trading systems. **VCP is the first implementation profile of the VAP family and the reference profile for VAP v1.2:** its three-layer integrity architecture (EventHash / Merkle / External Anchor), mandatory all-tier anchoring, policy identification, ERASURE event, bounded RECOVERY, and XREF mechanisms are the proven origins of the corresponding v1.2 framework requirements.

#### 5.1.2 Domain-Specific Modules

| Module           | Purpose                      | VAP Layer Mapping                 |
| ---------------- | ---------------------------- | --------------------------------- |
| **VCP-CORE**     | Standard header and security | Integrity Layer                   |
| **VCP-TRADE**    | Trading payload              | Provenance Layer (action/outcome) |
| **VCP-GOV**      | Algorithm governance         | Provenance Layer (actor/context)  |
| **VCP-RISK**     | Risk parameter recording     | Provenance Layer (context)        |
| **VCP-PRIVACY**  | Crypto-shredding / ERASURE   | Cross-cutting (Privacy), §6.3     |
| **VCP-RECOVERY** | Bounded chain recovery       | Integrity Layer (INT-009)         |
| **VCP-XREF**     | Cross-party provenance       | Traceability Layer (TRC-005)      |

#### 5.1.3 Conformance Tiers (profile-defined)

| Tier         | Target        | Clock Sync   | Signature           | Anchor Frequency |
| ------------ | ------------- | ------------ | ------------------- | ---------------- |
| **Platinum** | HFT/Exchange  | PTPv2 (<1µs) | Ed25519 (Hardware)  | 10 minutes       |
| **Gold**     | Institutional | NTP (<1ms)   | Ed25519 (Client)    | 1 hour           |
| **Silver**   | Retail/MT4/5  | Best-effort  | Ed25519 (Delegated) | 24 hours         |

External anchoring is REQUIRED at every tier (lightweight targets acceptable at Silver), consistent with INT-006.

#### 5.1.4 Regulatory Mapping

| Regulation        | VCP Module  | Implementation             |
| ----------------- | ----------- | -------------------------- |
| EU AI Act Art. 12 | VCP-CORE    | Automated event logging    |
| EU AI Act Art. 13 | VCP-GOV     | DecisionFactors            |
| EU AI Act Art. 14 | VCP-GOV     | OperatorID, LastApprovalBy |
| MiFID II Art. 17  | VCP-GOV     | AlgoID, TestingRecordLink  |
| MiFID II RTS 25   | VCP-CORE    | ClockSyncStatus            |
| GDPR Art. 17      | VCP-PRIVACY | Crypto-shredding + ERASURE event |

Per §1.6, this mapping identifies which mechanisms produce evidence relevant to each provision; it is not a compliance determination.

### 5.2 CAP: Content / Creative AI Profile

**Status:** v1.0 Released

CAP defines a verifiable evidence layer for AI workflows involving content and intellectual property — ingestion, training, generation, transformation, and export — so that authorship, AI-usage, and licensing disputes can be examined with cryptographically verifiable records. Applicable sectors include games, film, animation, publishing, and music.

VAP v1.2 alignment notes (per VSO-VAP-CHANGE-001 Annex B.1): content pipelines are batch-oriented, so the sequence-mechanism matrix (INT-004) is expected to designate Merkle + external anchor as primary with PrevHash optional; ERASURE supports creator-data and opt-out obligations, with `retention_exemption` used for IP-dispute litigation holds; XREF instantiates as creator ↔ platform dual logging.

### 5.3 CPP: Capture Provenance Profile

**Status:** v1.4 Released

CPP defines media capture verification — proving when, where, and by whom photographs and videos were taken — supporting evidence integrity and countering synthetic-media misinformation.

VAP v1.2 alignment notes: capture devices MAY favor PrevHash (sequential capture) plus periodic anchoring; the ERASURE legal clause is critical where subject-erasure requests conflict with evidentiary preservation (`retention_exemption`); device resource constraints inform the deferral analysis of INT-005 elevation (VSO-VAP-CHANGE-001 Annex C.2).

### 5.4 OAP: Observed Artifact Provenance

**Status:** v0.1.1 Working Draft
**Document:** VSO-VAP-OAP-001

OAP defines provenance for records of *third-party web resources observed at a
URL* — material published by someone else, retrieved over a network, and
preserved because it may later be disputed, deleted, edited, or denied. CPP and
OAP are siblings distinguished by control of the source: CPP covers capture by a
device the operator controls; OAP covers observation of material the operator
does not control and cannot re-obtain once it is removed.

VAP v1.2 alignment notes: the Completeness Invariant (INT-008) is load-bearing,
because the disputed question is characteristically *what was observed and not
recorded*; the pre-measurement-drop boundary is correspondingly explicit, since
a resource that was never retrieved leaves no evidence of its former existence;
XREF instantiates as observer ↔ archiving service; OAP composes with DAP (§4.6)
where retrieval is performed by an autonomous agent.

### 5.5 Future Profiles (Planned)

All future profiles MUST target VAP v1.2 at first release. Design constraints inherited at birth (VSO-VAP-CHANGE-001 Annex B.2):

#### 5.5.1 DVP: Automotive Profile / AAP: Aviation Profile

**Scope:** Autonomous vehicles, ADAS, drones; aviation AI. **Key Events:** SENSOR_INPUT, PERCEPTION, PATH_PLANNING, CONTROL_COMMAND, TAKEOVER_REQUEST, EMERGENCY_STOP, COLLISION_WARNING. **v1.2 consequences:** real-time tamper-detection expectations → the profile SHOULD make PrevHash MUST at upper conformance levels (explicitly permitted by INT-004a); RECOVERY bounds map to post-crash data gap-fill.

#### 5.5.2 MAP: Medical Profile

*Superseded in part: MAP now exists as a v0.1.2 Working Draft (§4.5.2). The
design constraints below are retained as the inherited-at-birth record.*

**Scope:** AI diagnostics, imaging analysis, medication support, surgical robots. **Key Events:** IMAGING_ACQUIRED, ANALYSIS_COMPLETED, DIAGNOSIS_SUGGESTED, PHYSICIAN_REVIEWED, TREATMENT_PROPOSED, PATIENT_CONSENTED. **v1.2 consequences:** the ERASURE legal clause interacts with medical-record retention statutes — `retention_exemption` semantics MUST be specified at profile level; XREF instantiates as provider ↔ AI vendor.

#### 5.5.3 PAP: Public Administration Profile

*Superseded in part: PAP Track B (Investigative-Decision Vocabulary) exists as a
v0.2.0 draft (§4.5.2). Track A (Administrative-Decision) is scoped but not
drafted, and no consolidated PAP specification exists. Any public reference to
PAP MUST disclose this.*

**Scope:** Credit scoring, welfare determination, immigration, recruitment AI. **Key Events:** APPLICATION_RECEIVED, EVALUATION_STARTED, SCORING_COMPLETED, DECISION_MADE, NOTIFICATION_SENT, APPEAL_FILED. **v1.2 consequences:** the Completeness Invariant (INT-008) is the load-bearing mechanism for appeals; the XREF OBSERVER role (regulator read-only) is the default deployment.

#### 5.5.4 EIP: Energy Infrastructure Profile

**Scope:** Grid management AI, water/telecom/gas control, nuclear monitoring. **v1.2 consequences:** the anchor continuity plan (INT-007) MUST account for air-gapped and segmented networks — profile-defined offline anchoring queue semantics.

#### 5.5.5 IAP: Industry Accountability Profile

**Scope:** Sector-specific extensions, industry-tailored governance, regulatory mappings layered on other profiles.

---

## 6. Cryptographic Requirements

### 6.1 Algorithm Requirements

#### 6.1.1 Hash Functions

| Requirement            | Specification                |
| ---------------------- | ---------------------------- |
| Minimum Security       | 128-bit effective security   |
| Default Algorithm      | SHA-256                      |
| Alternative Algorithms | SHA3-256, BLAKE3             |
| Collision Resistance   | MUST resist birthday attacks |

#### 6.1.2 Digital Signatures

| Requirement       | Specification                              |
| ----------------- | ------------------------------------------ |
| Default Algorithm | Ed25519                                    |
| Key Size          | 256-bit (Ed25519)                          |
| Signature Size    | 64 bytes (Ed25519)                         |
| Deprecated        | RSA-2048 (removal planned in VAP v2.0)     |
| Experimental (PQC)| ML-DSA (FIPS 204), FN-DSA (FIPS 206 draft) |

### 6.2 Quantum Resistance

#### 6.2.1 Threat Analysis

```
Current Ed25519 Security:
- Classical Attack: O(2^128) operations
- Quantum Attack (Shor): O((log n)³) with ~2,000–4,000 logical qubits

Hash Function (SHA-256):
- Classical Preimage: O(2^256)
- Quantum Preimage (Grover): O(2^128) — Still secure
```

**Key Insight:** VAP hash-based integrity (EventHash, Merkle, anchors) is preserved even after quantum attacks on signatures.

#### 6.2.2 Migration Path

```
Phase 1 (Current):    Ed25519 + SHA-256
Phase 2 (AVAILABLE):  Hybrid dual signature — Ed25519 || ML-DSA   ← v1.2 status
Phase 3 (PQC):        ML-DSA + SHA3-256
```

**Hybrid dual-signature schema (RECOMMENDED transition mechanism):** the Security object and AnchorRecord carry OPTIONAL `pqc_signature` / `pqc_sign_algo` fields alongside the classical signature. Verifiers MUST treat the classical signature as authoritative for conformance until profiles declare otherwise; the PQC signature provides forward evidence against future signature forgery.

### 6.3 Crypto-Shredding for Privacy

#### 6.3.1 Mechanism

```
Before Key Destruction:
  Encrypted Data + Encryption Key → Original Data

After Key Destruction:
  Encrypted Data + [KEY DESTROYED] → Mathematically Unrecoverable
```

Protected fields are encrypted with a per-subject data-encryption key (DEK); destruction of the DEK renders the plaintext irrecoverable while leaving all hashes, Merkle structures, and anchors intact.

#### 6.3.2 Hash Chain / Anchor Preservation

| Component            | After Crypto-Shredding      |
| -------------------- | --------------------------- |
| EventHash / sequence structures | ✅ Intact         |
| Merkle Tree          | ✅ Intact                    |
| External Anchors     | ✅ Verifiable                |
| Cryptographic Proofs | ✅ Verifiable                |
| Original Data        | ❌ Permanently unrecoverable |

#### 6.3.3 ERASURE Event (v1.2, REQUIRED when erasure is performed)

When crypto-shredding is performed, implementations MUST record an **ERASURE event** as a new, append-only, fully sequenced and anchored event. ERASURE MUST NOT delete, rewrite, or re-hash any prior event; the original EventHash, Merkle inclusion, and external anchors of target events remain verifiable. Abstract schema: §7.4.

| Field | Requirement | Notes |
|---|---|---|
| `erasure_target_event_ids` | REQUIRED | Events whose protected fields are shredded |
| `erasure_reason` | REQUIRED | `SUBJECT_REQUEST` \| `RETENTION_EXPIRED` \| `LEGAL_ORDER` (profiles MAY extend) |
| `key_destruction_proof` | REQUIRED | Evidence of DEK destruction (e.g., HSM/KMS attestation) |
| `retention_exemption` | OPTIONAL | Legal basis where a retention duty overrides erasure |
| `operator_id` | REQUIRED | Actor authorizing the erasure |

#### 6.3.4 Legal Scope (Normative)

> Crypto-shredding **may support** erasure obligations (e.g., GDPR Art. 17), **but does not itself determine legal compliance.** Whether crypto-shredding constitutes "erasure" is jurisdiction- and case-dependent. Profiles MUST surface domain-specific tensions (e.g., audit-trail reproducibility duties in finance; medical-record retention statutes in healthcare; public-records law in government) and MUST require the `retention_exemption` field where a retention duty overrides an erasure request. Once a DEK is destroyed, the plaintext is by design not re-creatable.

---

## 7. Data Model

### 7.1 Common Event Structure

All VAP-conformant events MUST have the following structure:

```json
{
  "vap_version": "1.2",
  "profile": {
    "id": "string",
    "version": "string"
  },
  "policy": {
    "policy_id": "string",            // REQUIRED — reverse-domain naming: <reverse_domain>:<local_id>
    "conformance_level": "enum",      // REQUIRED — profile-defined level (e.g., SILVER|GOLD|PLATINUM)
    "vap_conformance": "enum",        // REQUIRED — VAP-CORE | VAP-STANDARD | VAP-FULL
    "registration_policy": {
      "issuer": "string",             // REQUIRED
      "policy_uri": "string",
      "effective_date": "int64",
      "expiration_date": "int64"
    },
    "verification_depth": {
      "sequence_mechanisms": ["enum"],     // PREV_HASH | MERKLE | EXTERNAL_ANCHOR | OTHER
      "merkle_proof_required": "boolean",      // always true in v1.2
      "external_anchor_required": "boolean"    // always true in v1.2
    }
  },
  "header": {
    "event_id": "uuid_v7",
    "trace_id": "uuid_v7",
    "cross_reference_id": "uuid",     // OPTIONAL — XREF (TRC-005)
    "timestamp_int": "int64",
    "timestamp_iso": "string",
    "timestamp_precision": "enum",
    "event_type": "string",
    "event_type_code": "uint8"
  },
  "provenance": {
    "actor": { },
    "input": { },
    "context": { },
    "action": { },
    "outcome": { }
  },
  "accountability": {
    "operator_id": "string",
    "last_approval_by": "string",
    "approval_timestamp": "int64"
  },
  "domain_payload": { },
  "security": {
    "event_hash": "string",           // REQUIRED (INT-003)
    "prev_hash": "string",            // OPTIONAL (INT-004a)
    "hash_algo": "enum",              // REQUIRED (crypto agility)
    "signature": "string",
    "sign_algo": "enum",
    "pqc_signature": "string",        // OPTIONAL (hybrid, §6.2.2)
    "pqc_sign_algo": "enum",          // OPTIONAL
    "merkle_root": "string",          // bound at batch close (INT-006)
    "merkle_index": "int32",          // bound at batch close
    "anchor_reference": "string",     // bound at batch close (AnchorRecord ID)
    "signer_id": "string"
  }
}
```

**Policy identification:** VSO does not operate a PolicyID registry; uniqueness derives from domain ownership via reverse-domain naming (e.g., `org.example.trading:eu-mifid-gold-2026`). `verification_depth.sequence_mechanisms` operationalizes INT-004: each event self-declares which sequencing mechanisms a verifier should apply.

### 7.2 Numeric Precision

**All numeric values MUST be encoded as string type.**

```json
// ✅ Correct
{ "price": "123.456789", "quantity": "1000.00" }

// ❌ Wrong
{ "price": 123.456789, "quantity": 1000 }
```

### 7.3 Canonicalization

JSON canonicalization MUST conform to RFC 8785 (JSON Canonicalization Scheme).

### 7.4 ERASURE Event (abstract schema, v1.2)

```json
{
  "header": { "event_type": "ERASURE", "...": "..." },
  "domain_payload": {
    "erasure_target_event_ids": ["uuid_v7"],
    "erasure_reason": "enum",             // SUBJECT_REQUEST | RETENTION_EXPIRED | LEGAL_ORDER | profile-defined
    "key_destruction_proof": "object",    // e.g., HSM/KMS attestation reference
    "retention_exemption": "object"       // OPTIONAL — legal basis for partial retention
  },
  "accountability": { "operator_id": "string" },
  "security": { "...": "fully sequenced and anchored like any event" }
}
```

### 7.5 AnchorRecord (abstract schema, v1.2)

```json
{
  "anchor_record_id": "uuid_v7",
  "batch": {
    "merkle_root": "string",
    "event_count": "int64",               // REQUIRED (INT-008)
    "first_event_id": "uuid_v7",          // REQUIRED (INT-008)
    "last_event_id": "uuid_v7",           // REQUIRED (INT-008)
    "policy_id": "string"                 // REQUIRED (INT-008)
  },
  "anchor_target": {
    "type": "enum",                       // TSA | TRANSPARENCY_LOG | BLOCKCHAIN | TRANSPARENCY_SERVICE | TIMESTAMP_SERVICE
    "identifier": "string",
    "proof": "object"                     // target-specific (RFC 3161 token, log proof, tx ref, COSE Receipt)
  },
  "security": {
    "signature": "string", "sign_algo": "enum",
    "pqc_signature": "string", "pqc_sign_algo": "enum",   // OPTIONAL
    "signer_id": "string"
  },
  "timestamp_int": "int64"
}
```

Implementations MUST retain local copies of all AnchorRecords (INT-007).

---

## 8. Conformance Levels

### 8.1 Level Definitions

| Level            | Description          | Requirements                                                                                  |
| ---------------- | -------------------- | --------------------------------------------------------------------------------------------- |
| **VAP-Core**     | Minimum conformance  | Integrity Layer mandatory requirements — including INT-006 external anchoring and INT-007 anchor continuity plan |
| **VAP-Standard** | Standard conformance | Core + Provenance + Traceability                                                              |
| **VAP-Full**     | Full conformance     | Standard + Accountability + Profile Extensions + (when used) ERASURE, RECOVERY, and XREF conformance |

There is no anchorless conformance level. A producer-trusting integrity claim is not a VAP claim.

### 8.2 Mechanism Declaration

Profiles MUST publish a **sequence-mechanism matrix** declaring, per profile conformance level: which INT-004 mechanisms are mandatory; anchoring frequency and acceptable anchor target classes; and resulting detection latency. Events self-declare the applicable matrix via `policy.verification_depth` (§7.1).

### 8.3 Certification Program

| Certification     | Level    | Requirements                             |
| ----------------- | -------- | ---------------------------------------- |
| **VAP-Ready**     | Core     | Basic test suite pass                    |
| **VAP-Compliant** | Standard | Standard test suite pass + audit         |
| **VAP-Certified** | Full     | Full test suite pass + third-party audit |

VSO defines requirements; independent Conformity Assessment Bodies (CABs) perform audits and issue certificates (§10.1). Migration deadlines for v1.1 conformance claims are defined in VSO-VAP-CHANGE-001 §5.

---

## 9. Implementation Guidelines

### 9.1 Sidecar Pattern

Non-invasive integration with existing systems is recommended:

```
┌─────────────────────────────────────────────────┐
│                Existing System                   │
│                                                  │
└──────────────────────┬───────────────────────────┘
                       │ Events
                       ▼
┌──────────────────────────────────────────────────┐
│              VAP Sidecar Process                  │
│  Event Capture → Sequence Builder → Merkle Anchor │
└──────────────────────────────────────────────────┘
```

### 9.2 Integration Patterns

| Pattern        | Use Case                    | Complexity |
| -------------- | --------------------------- | ---------- |
| **Sidecar**    | Legacy system integration   | Low        |
| **SDK**        | New application development | Medium     |
| **Middleware** | Enterprise gateway          | High       |
| **Native**     | Ground-up implementation    | Very High  |

### 9.3 Evidence Pack (v1.2, RECOMMENDED)

Profiles SHOULD define an **Evidence Pack**: a portable, self-verifying bundle containing events, audit paths, AnchorRecords, external anchor proofs and/or receipts, public keys, and applicable policy documents — sufficient for an offline third party to execute the verification procedures of §4.1.3 without access to the producing system. The Evidence Pack format is profile-defined in v1.2; a common container format is a candidate for VAP v1.3 (see VSO-VAP-CHANGE-001 Annex C).

---

## 10. Governance and Standardization

### 10.1 VSO Structure

```
VeritasChain Standards Organization (VSO)
├── Technical Committee
│   ├── Core Working Group (VAP Framework)
│   ├── Finance Working Group (VCP)
│   ├── Content Working Group (CAP)
│   ├── Capture Working Group (CPP)
│   ├── Automotive Working Group (DVP)
│   ├── Medical Working Group (MAP)
│   └── Public Sector Working Group (PAP)
├── Certification Authority Liaison
│   └── Conformance Testing (audits performed by independent CABs)
└── Advisory Board
    ├── Industry Representatives
    └── Regulatory Liaisons
```

VSO develops and maintains specifications and defines conformance requirements; it does **not** perform audits or issue certifications, and maintains strict vendor neutrality (VSO Non-Endorsement Policy).

### 10.2 Standardization Roadmap

| Phase       | Timeline   | Activities                                                         | Status |
| ----------- | ---------- | ------------------------------------------------------------------ | ------ |
| **Phase 1** | 2025       | VCP v1.0/v1.1 Release, VAP Framework v1.0/v1.1                     | Done   |
| **Phase 2** | 2026 Q1    | IETF Internet-Drafts submitted (draft-kamimura-vap-framework, draft-kamimura-scitt-vcp); CAP v1.0, CPP v1.0; ITU-T SG17 chair-level scope dialogue | Done |
| **Phase 3** | 2026       | VAP v1.2 + VCP v1.2; ISO/TC 68 engagement; DVP/MAP development      | In progress |
| **Phase 4** | 2026–2027  | ISO/IEC JTC 1/SC 42 alignment                                       | Planned |
| **Phase 5** | 2027+      | International standard track; PQC migration (Phase 3 of §6.2.2)     | Planned |

### 10.3 Change Management

Specification changes follow this process:

1. **Change Proposal** submission (e.g., VSO-VAP-CHANGE-NNN)
2. **Public Review** period (30 days)
3. **Technical Committee** deliberation
4. **Vote** (approved by two-thirds majority)
5. **Release** (the change proposal becomes a normative annex of the revised specification)

### 10.4 Version Compatibility Management (v1.2)

VAP and profile version numbers are **independently assigned**. Apparent synchrony (e.g., VAP v1.2 ⇔ VCP v1.2) is coincidental and MUST NOT be relied upon. Compatibility is managed through three artifacts:

1. **VAP Version** — the framework requirement set (this document);
2. **Profile Version** — each profile declares the minimum VAP version it conforms to (`min_vap_version`, §4.5.3; events carry `vap_version`, §7.1);
3. **Compatibility Matrix** — maintained by VSO per release:

| Profile or capability / version | VAP v1.1 | VAP v1.2 |
|---|---|---|
| VCP v1.0 | Partial (pre-dates policy identification) | Partial (legacy; certification subject to VCP grace deadlines) |
| VCP v1.1 | Non-conformant on v1.1 INT-003/004 as written (resolved by this revision) | **Full** |
| VCP v1.2 | — | **Full** (reference profile) |
| CAP v1.0 | Mapping required | **Mapping required and outstanding** (due per VSO-VAP-CHANGE-001 §5) |
| CPP v1.4 | Mapping required | **Mapping required and outstanding** (due per VSO-VAP-CHANGE-001 §5) |
| OAP v0.1.1 (WD) | — | Targets v1.2 at first release |
| MAP v0.1.2 (WD) | — | Targets v1.2 at first release |
| PAP v0.2.0 (Track B draft) | — | Targets v1.2 at first release |
| DAP v0.1.0 (capability) | — | Targets the v1.2 requirement set (§4.6) |
| SMP v0.2.0 (capability) | — | Targets the v1.2 requirement set (§4.6) |
| DVP / AAP / EIP / IAP | — | MUST target VAP v1.2 at first release |

**Outstanding mapping obligation (honest statement).** CAP v1.0 and CPP v1.4 are
the two profiles other than VCP carrying *Released* status, and both have a v1.2 conformance
mapping that is due and not yet delivered. Until those mappings are published,
neither profile's conformance against the v1.2 requirement set has been
established, and neither may be described as VAP v1.2 conformant. A known
candidate divergence to be resolved in the CPP mapping is the treatment of
external anchoring at CPP's lowest conformance tier: §8.1 and INT-006 do not
permit external anchoring to be optional at any level.

**Data-format rule:** v1.2 verifiers MUST accept all v1.1 events. v1.1 verifiers encountering v1.2-only constructs (ERASURE, `policy` object, PQC fields, transparency-service receipts) MUST fail gracefully (ignore-unknown), not reject.

---

## 11. Relation to International Standards

### 11.1 Broader Context (Non-Normative)

VAP is an informational architectural framework: it does not introduce new network protocols, and its profiles focus on verifiable decision trails, third-party verification, and evidence packaging. VAP bridges two established IETF work streams — SCITT (verified software/statement transparency) and RATS (verified environments) — to address dynamic decision accountability, which neither fully covers alone.

The SCITT architecture and the COSE receipt format are now published as **RFC 9943** and **RFC 9942** respectively (June 2026). Other components of that work remain Internet-Drafts and MUST NOT be cited as published standards: SCRAPI (`draft-ietf-scitt-scrapi`), the CCF receipt profile (`draft-ietf-scitt-receipts-ccf-profile`), and CoRIM (`draft-ietf-rats-corim`).

**What SCITT provides and what INT-008 adds.** RFC 9943 lets a relying party assemble the set of Transparent Statements bound to a given Subject, which supports completeness and non-equivocation *over the statements that were registered*. An event that an issuer never submitted does not appear in that set. The Completeness Invariant (§4.1.7) addresses that residue: it requires the expected event set to be **declared in advance** and bound to the anchor, so that non-submission is structurally detectable. Tamper-evidence and omission-evidence are distinct properties; VAP claims the second only at anchor granularity (§4.1.7), not as mathematical completeness.

### 11.2 Standards Landscape (Non-Normative)

| Domain                  | Existing Standards     | VAP Profile Role                                     |
| ----------------------- | ---------------------- | ---------------------------------------------------- |
| Financial Trading       | FIX, ISO 20022         | VCP complements existing formats with provenance     |
| Content Provenance      | C2PA                   | CAP/CPP add decision/workflow provenance and anchoring to media provenance |
| Automotive              | ISO 26262, UNECE WP.29 | DVP adds AI decision provenance to safety standards  |
| Medical Devices         | IEC 62304, FDA SaMD    | MAP adds AI explainability to device logging         |
| Critical Infrastructure | IEC 62443, NERC CIP    | EIP adds AI provenance to SCADA/ICS logging          |

### 11.3 SCITT / COSE Alignment (v1.2, opt-in Normative)

Implementations MAY register signed statements (e.g., AnchorRecords) with a transparency service conformant to **RFC 9943** and attach **COSE Receipts** (**RFC 9942**) as additional verifiability evidence. When SCITT alignment is claimed:

- Receipt format MUST conform to **RFC 9942** (COSE Receipts);
- The transparency-service identity MUST be recorded in the AnchorRecord (`anchor_target.type = TRANSPARENCY_SERVICE`);
- VAP-native verification MUST remain possible without the transparency service (SCITT is additive, not substitutive).

### 11.4 Future Standardization

| Target | Timeline | Status |
| ------ | -------- | ------ |
| IETF Internet-Drafts | 2026– | **Five individual Internet-Drafts submitted and active**: `draft-kamimura-vap-framework-01`, `draft-kamimura-scitt-vcp-03`, `draft-kamimura-rats-behavioral-evidence-02`, `draft-kamimura-scitt-refusal-events-03`, `draft-vso-cpp-core-03`. These are **individual submissions**, not adopted by any IETF Working Group, and carry no standing in the IETF standards process. |
| ITU-T SG17 | 2026 | Liaison statement VSO-LS-SG17-001 was submitted and **returned by the TSB** against three criteria: a well-defined standardization problem, a demonstrated interoperability requirement, and implementation experience. None of the three is met at the time of writing. Re-engagement is planned once they are. |
| ISO/IEC JTC 1/SC 42 (AI) | 2026–2027 | A pre-registered gap-assessment protocol (VSO-GAP-SC42-001) exists for evaluating the relevant FDIS texts. No liaison, submission, or contribution. |
| ISO/TC 68 (Financial Services) | 2026– | Planned. No submission. |
| IEEE Standards Association | 2027+ | Under consideration. |

Submission of a document to a standards body does not imply endorsement,
adoption, or approval by that body.

---

## 12. References

### 12.1 Standards

| Standard       | Description                  |
| -------------- | ---------------------------- |
| RFC 2119 / RFC 8174 | Key words for requirement levels |
| RFC 9562       | UUID v7                      |
| RFC 8785       | JSON Canonicalization Scheme |
| RFC 6962 / RFC 9162 | Certificate Transparency |
| RFC 8032       | Ed25519 Digital Signature    |
| RFC 3161       | Time-Stamp Protocol (TSP)    |
| IEEE 1588-2019 | Precision Time Protocol      |
| FIPS 204       | ML-DSA (Module-Lattice Digital Signature) |
| FIPS 206 (draft) | FN-DSA                     |
| RFC 9943       | An Architecture for Trustworthy and Transparent Digital Supply Chains (SCITT), June 2026 |
| RFC 9942       | CBOR Object Signing and Encryption (COSE) Receipts, June 2026 |
| draft-kamimura-vap-framework | VAP Framework (individual Internet-Draft) |

### 12.2 Regulations

| Regulation     | Jurisdiction   | Relevance                   |
| -------------- | -------------- | --------------------------- |
| EU AI Act      | European Union | High-Risk AI Classification |
| MiFID II       | European Union | Financial Trading           |
| GDPR           | European Union | Data Privacy                |
| CAT Rule 613   | United States  | Consolidated Audit Trail    |
| NIS2 Directive | European Union | Critical Infrastructure     |
| FDA AI/ML SaMD | United States  | Medical AI guidance         |

### 12.3 Related VSO Documents

| Document ID          | Title                                          |
| -------------------- | ---------------------------------------------- |
| VSO-VAP-CHANGE-001   | VAP Framework v1.2 Change Proposal (normative annex) |
| VSO-VAP-ALIGN-001    | VAP v1.2 Cross-Profile Alignment Review (dispositions in Appendix D) |
| VSO-VCP-SPEC         | VeritasChain Protocol Specification (v1.2)     |
| VSO-SPEC-CHANGE-001  | VCP v1.2 Change Proposal                       |
| CAP v1.0             | Content / Creative AI Profile                  |
| CPP v1.4             | Capture Provenance Profile                     |
| VSO-VAP-OAP-001      | Observed Artifact Provenance (OAP) v0.1.1 Working Draft |
| VSO-VAP-MAP-001      | Medical AI Profile (MAP) v0.1.2 Working Draft   |
| VSO-VAP-PAP-001      | Public Administration Profile (PAP) — Investigative Decision Vocabulary v0.2.0 |
| VSO-VAP-DAP-001      | Delegated Access Provenance (DAP / VAP-AGENT) v0.1.0 Working Draft |
| VSO-VAP-SMP-SPEC-001 | Self-Modification Provenance (SMP / VAP-SLEEP) v0.2.0 Working Draft |
| VSO-TEST-001         | Conformance Test Guide                         |

---

## Appendix A: Glossary

| Term             | Definition                                                                           |
| ---------------- | ------------------------------------------------------------------------------------ |
| **Cross-Cutting Capability** | Evidence requirement defined once at the Shared Assurance Core and inherited by any profile that invokes it (DAP, SMP). See §4.6. |
| **Omission-evidence** | Detectability of events that were never submitted, as distinct from tamper-evidence (detectability of alteration to submitted records). Provided by INT-008 at anchor granularity. |
| **Pre-measurement drop** | An event that was never measured or recorded. Permanently outside the reach of any provenance mechanism, by construction. This is a structural limit of the framework, not a gap to be closed. |
| **VAP**          | Verifiable AI Provenance Framework — Cross-domain upper-level framework              |
| **VSO**          | VeritasChain Standards Organization                                                  |
| **VCP**          | VeritasChain Protocol — VAP Finance Profile                                          |
| **CAP**          | Content / Creative AI Profile — VAP content and IP-workflow profile                  |
| **CPP**          | Capture Provenance Profile — VAP first-party device-capture profile                  |
| **OAP**          | Observed Artifact Provenance — VAP third-party observed-resource profile             |
| **IAP**          | Industry Accountability Profile                                                      |
| **DVP**          | Driving Vehicle Profile — VAP automotive profile                                     |
| **MAP**          | Medical AI Profile — VAP medical and healthcare profile                              |
| **PAP**          | Public Administration Profile — VAP public-sector profile                            |
| **EIP**          | Energy Infrastructure Profile — VAP energy profile                                   |
| **AAP**          | Aviation AI Profile — VAP aviation profile                                           |
| **DAP**          | Delegated Access Provenance (VAP-AGENT) — cross-cutting capability (§4.6)            |
| **SMP**          | Self-Modification Provenance (VAP-SLEEP) — cross-cutting capability (§4.6)           |
| **Provenance**   | Cryptographically verifiable record of data origin, lineage, and history             |
| **High-Risk AI** | High-risk AI systems as defined in EU AI Act Article 6                               |
| **Cryptographic Sequence Verifiability** | Third-party-verifiable ordering and membership of recorded events (INT-004) |
| **Completeness Invariant** | Third-party detectability of post-anchor omission within an anchored batch (INT-008) |
| **AnchorRecord** | Signed record binding a Merkle root, batch scope, and external anchor proof (§7.5)   |
| **ERASURE Event**| Append-only event recording crypto-shredding of protected fields (§6.3.3, §7.4)        |
| **XREF**         | Cross-Party Provenance — independent cross-referenced logging by multiple parties (TRC-005) |
| **Evidence Pack**| Portable self-verifying bundle for offline third-party verification (§9.3)           |
| **CAB**          | Conformity Assessment Body — independent certifier                                   |

---

## Appendix B: Version History

| Version | Date       | Changes                                                                                              | Author                  |
| ------- | ---------- | ----------------------------------------------------------------------------------------------------- | ----------------------- |
| 1.0.0   | 2025-12-11 | Initial Release                                                                                       | VSO Technical Committee |
| 1.1.0   | 2025-12-11 | Added High-Risk AI Domains, VSO/VAP/VCP hierarchy clarification                                       | VSO Technical Committee |
| 1.2.0 (Draft 3) | 2026-09-01 | Pre-publication fold of **VSO-VAP-ALIGN-001** (cross-profile alignment review). Editorial and registry corrections only; no wire-format change, no conformance-level change. Version number unchanged per VSO pre-release practice. Dispositions: Appendix D | VSO Technical Committee |
| 1.2.0 (Draft 3, as published) | 2026-09-28 | Publication folds G-2 (implementation-status disclosure), H-2 (capability-language corrections), A-4 (Declaration and hierarchy diagram aligned with the Normative Position Statement and §10.1); K-1 closed by publication of this draft in `veritaschain/vap-spec` `spec/v1.2/`. Editorial only; no normative requirement, wire format, or conformance level changed. Dispositions: Appendix D | VSO Technical Committee |
| 1.2.0 (Draft 3, fold B-5) | 2026-09-28 | Post-publication fold B-5: profile registry and related rows record VCP as v1.2 Released (GA 2026-07-06, tag `v1.2.0`) instead of v1.2 (RC1). Editorial only; no normative requirement, wire format, or conformance level changed. Disposition: Appendix D | VSO Technical Committee |
| 1.2.0 (Draft 2) | 2026-06-10 | Per VSO-VAP-CHANGE-001: Cryptographic Sequence Verifiability abstraction (INT-003/004/004a); external anchoring MUST at all levels (INT-006) with anchor continuity (INT-007); Completeness Invariant (INT-008); bounded RECOVERY (INT-009); ERASURE event + legal scope clause; policy identification; XREF (TRC-005); SCITT/COSE opt-in alignment; PQC EXPERIMENTAL status (ML-DSA/FN-DSA), hybrid signatures, RSA-2048 deprecation; version compatibility management; profile registry update (VCP v1.2 RC1, CAP v1.0, CPP v1.0, IAP); Legal Scope and Non-Guarantee Statement | VSO Technical Committee |

---

## Appendix C: License

This specification is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

---

## Appendix D: VSO-VAP-ALIGN-001 Disposition Record

Findings of the 2026-09-01 cross-profile alignment review and their disposition
in this draft. Per VSO practice, pre-release review findings fold directly into
the draft with a disposition record; they do not spawn a change number.

| ID | Finding | Disposition |
| --- | --- | --- |
| A-1 | §2.2.2–§2.2.5 expanded MAP, DVP, AAP, EIP, and PAP as "Protocol", contradicting the family rule reserving that designation for VCP, and contradicting §5.5 of this same document | **Applied.** All four corrected to "Profile"; the reservation rule is now normative text in §1.5 |
| A-2 | The hierarchy diagram described profiles as "domain-specific protocol implementations" | **Applied.** Corrected to "profile implementations" |
| B-1 | §4.5.2 listed MAP as Planned (actual: v0.1.2 Working Draft) and PAP as Planned (actual: Track B v0.2.0 draft) | **Applied** |
| B-2 | §4.5.2 listed CPP at v1.0; the tagged release is 1.4 | **Applied.** CPP recorded as v1.4 Released. The repository badge pointing to v1.5 and the two files annotated "Main specification" are repository-side defects to correct; v1.5 is not a tagged release and is therefore not a Released version under the §4.5.2 status vocabulary |
| B-3 | Status values Released / Announced / Planned were used without definition across a growing registry | **Applied.** Status vocabulary added and made normative for the registry, with precedence over badges, website, and press material |
| B-4 | OAP v0.1.1 declared itself a VAP v1.2 domain profile citing §4.5.2, but had no registry row | **Applied.** Registry row and §5.4 added |
| C-1 | DAP and SMP declared themselves cross-cutting capabilities at the Shared Assurance Core, and DAP asserted that "VAP v1.2 consolidates … VAP-SLEEP/SMP at the Shared Assurance Core" — while this document contained zero occurrences of DAP, SMP, SLEEP, or OAP. Two working drafts asserted an inheritance relationship the parent document did not declare | **Applied.** §4.6 Cross-Cutting Capabilities added with a capability registry and composition rules; `profile_extension.capabilities` added at §4.5.3. Because v1.2 is unpublished and there are zero external implementations, no compatibility surface is affected |
| D-1 | §10.4 stated MAP/PAP/others "MUST target v1.2 at first release" after those drafts had in fact done so | **Applied.** Matrix updated; the outstanding CAP and CPP mapping obligation is now stated explicitly, including the CPP lowest-tier anchoring divergence from §8.1/INT-006 |
| E-1 | §11.3 normatively required a draft superseded by RFC 9942; §12.1 listed both SCITT and COSE Receipts as drafts, contrary to §11.3's own supersession clause | **Applied.** RFC 9943 and RFC 9942 substituted; the still-draft components are named so they are not miscited |
| E-2 | The SCITT-versus-INT-008 distinction was not stated in the specification, only in sales material, leaving the claim unsourced where a reader could check it | **Applied.** §11.1 now states what RFC 9943 provides and what INT-008 adds, at the accurate claim level |
| F-1 | §11.4 recorded two submitted drafts and omitted the ITU-T SG17 outcome | **Applied.** Five drafts recorded with their non-adopted status; the SG17 return and its three unmet criteria recorded verbatim in substance |
| G-1 | The mandatory three-item implementation-status disclosure appeared in OAP but not in this framework document | **Applied** to the header block |
| A-3 | Appendix A glossary expanded DVP, MAP, PAP, EIP, and AAP as "Protocol" and CAP as "Creative AI Profile" | **Applied.** Glossary corrected; OAP, DAP, and SMP entries added |
| H-1 | §1.1 used a "VAP Solution" column header and "cryptographic guarantees" | **Applied.** "VAP Mechanism"; "make retroactive modification detectable (tamper-evidence)" |
| I-1 | "Content" was claimed by both CAP and CPP across VSO surfaces | **Applied.** CAP holds "Content / Creative AI"; CPP holds "Capture". §2.2.6 records the correction obligation for materials and Internet-Drafts still using "Content Provenance Profile" |
| J-1 | Third-party Internet-Drafts describing VAP or proposing profiles had no stated status | **Applied.** §4.5.2 closing paragraph |
| K-1 | This specification was never published; the public repository carries v1.1 only, while five downstream drafts cite v1.2.0 as their normative parent | **Not a document defect — a publication action.** Closed by publication of this draft, with VSO-VAP-CHANGE-001, in `veritaschain/vap-spec` `spec/v1.2/` |

**Publication folds (2026-09-28).** Applied at publication under the same
pre-release practice. None changes a normative requirement, a field, or a
conformance level.

| ID | Finding | Disposition |
| --- | --- | --- |
| G-2 | The header disclosure's paying-customer item was inaccurate: VeritasChain Co., Ltd. holds ten paid service contracts with European organizations. A disclosure that is inaccurate in the direction of modesty is still inaccurate | **Applied.** The paying-customer item is replaced by a statement of the ten contracts (client names withheld pending consent) and an explicit statement that they are neither external implementations nor independent validation. The two remaining items (zero external implementations; zero Evidence Packs accepted in any proceeding) are unchanged. Profiles that carry the three-item form (e.g., OAP v0.1.1 §15.3) align at their next revision |
| H-2 | Capability language exceeded the framework's claim level: "immutable" (§1.5, §6.3.3, Appendix A) for an event whose property is append-only and tamper-evident; "guarantees" / "guaranteed" (Executive Summary, §4.1.1, INT-004, §4.1.2 scope note, §4.3.2, §5.5.3) where the framework makes alteration and post-anchor omission detectable and warrants nothing (§1.6) | **Applied.** "append-only"; "completeness verification (omission-evidence)"; "make alteration and post-anchor omission detectable (tamper-evidence and omission-evidence)"; "ordering properties"; "verifiable only at anchor time and at batch granularity"; "XREF detection statement"; "load-bearing mechanism". Requirement levels and semantics unchanged |
| A-4 | The Declaration described VSO as "positioned alongside W3C, IETF, IEEE, and FIX … as an international standards body" and VAP as infrastructure for "provenance and safety", contradicting the Standing statement, the structural-comparison note in the Normative Position Statement, and §1.6. The hierarchy diagram described VSO as the body that "certifies VAP", contradicting §10.1 | **Applied.** The Declaration now uses the Normative Position Statement's wording and restates that the comparison is structural, not a claim of equivalent status; "and safety" removed. Diagram corrected to "develops and maintains VAP" |


**Post-publication fold (2026-09-28).** Applied under the same practice after
publication. It changes no normative requirement, field, or conformance level.

| ID | Finding | Disposition |
| --- | --- | --- |
| B-5 | §2.2.1, §4.5.2, §5.1, §10.4 and §12 recorded VCP at v1.2 (RC1). VCP v1.2 was declared Production Ready (GA) on 2026-07-06; the GA text and its normative annex VSO-SPEC-CHANGE-001 are published in `veritaschain/vcp-spec` `spec/v1.2/` and tagged `v1.2.0`, which meets the §4.5.2 definition of *Released* | **Applied.** VCP recorded as v1.2 Released in those locations. VSO-VAP-CHANGE-001 is unchanged: its normative baseline is VCP v1.2 RC1 (2026-05-31), whose technical content is identical to the Released text. The Draft 2 version-history row keeps its historical wording |
---

## Contact Information

**VeritasChain Standards Organization (VSO)**
Website: <https://veritaschain.org>
Email: <standards@veritaschain.org>
Technical: <technical@veritaschain.org>
GitHub: <https://github.com/veritaschain>

---

## Declaration

> **VAP (Verifiable AI Provenance Framework), as the uppermost conceptual layer of AI societal infrastructure, defines the foundational infrastructure for AI decision provenance in domains where system failure can cause serious and irreversible harm to human life, societal infrastructure, or democratic institutions.**
>
> VSO develops and maintains this framework as a **standards organization for AI decision provenance.** The comparison with W3C, IETF, IEEE, and FIX in the Normative Position Statement identifies the layer at which VSO operates; it is not a claim of equivalent status, recognition, or adoption.
>
> VCP is the first implementation profile of the VAP family and the reference profile for v1.2; CAP, CPP, and OAP extend the same Shared Assurance Core to content, capture, and observed-artifact provenance; DAP and SMP extend it across domains as cross-cutting capabilities.
>
> **What this framework does not do.** VAP makes AI decision records auditable, attributable, and — at anchor granularity — completeness-verifiable after the fact. It does not prevent, block, or intercept any AI behaviour, and it does not warrant that any recorded decision was correct, fair, or safe (§1.6). Events that were never measured are permanently outside its reach by construction, and no revision of this framework will change that.

---

*"Encoding Trust in the AI Age" — "Verify, Don't Trust"*

*End of Verifiable AI Provenance Framework (VAP) Specification v1.2*
