# Verifiable AI Provenance Framework (VAP)

## Framework Specification v1.1

**Document ID:** VSO-VAP-SPEC-001  
**Status:** Draft Specification  
**Version:** 1.1.0  
**Date:** 2025-12-11  
**Maintainer:** VeritasChain Standards Organization (VSO)  
**License:** CC BY 4.0 International  
**Website:** https://veritaschain.org

---

## Executive Summary

**VAP (Verifiable AI Provenance Framework)** is a **cross-domain upper-level framework** that defines the structural requirements for cryptographically verifiable decision provenance common to all high-risk AI systems.

VAP is not a regulation that restricts AI usage. Its purpose is to standardize **the provenance infrastructure required for the safe and continuous operation of AI systems.**

**The scope of VAP is explicit: domains where system failure can cause irreversible harm to human life, societal infrastructure, or democratic institutions.**

Across the five domains of finance, healthcare, transportation, energy, and public policy, transparency and traceability of AI decisions are not optional features — they are mandatory requirements for societal infrastructure.

---

## Normative Position Statement

### The VAP/VSO/VCP Hierarchy

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
│     Standards body that develops, maintains, and certifies VAP  │
│     Ensures consistency across domain profiles                  │
│                                                                 │
│                          │                                      │
│                          │ publishes profiles                   │
│                          ▼                                      │
│                                                                 │
│     ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│     │   VCP   │ │   DVP   │ │   MAP   │ │   PAP   │  ...      │
│     │Finance  │ │Automotive│ │Medical │ │Public  │           │
│     │Profile  │ │ Profile │ │Profile │ │Profile │           │
│     └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│                                                                 │
│     Domain-specific protocol implementations                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Analogous Standards Bodies

| Standards Body | Domain | Framework/Protocol |
|----------------|--------|-------------------|
| **W3C** | Web | HTML, CSS, DOM |
| **IETF** | Network | TCP/IP, HTTP, TLS |
| **IEEE** | Electronics/Communications | 802.11 (WiFi), 1588 (PTP) |
| **FIX Trading Community** | Financial Trading | FIX Protocol |
| **VSO** | **AI Decision Provenance** | **VAP Framework, VCP, DVP, MAP...** |

**VSO is positioned as an international standards body defining the foundational infrastructure for AI decision provenance and safety.**

---

## Table of Contents

1. [Introduction](#1-introduction)
2. [High-Risk AI Domains](#2-high-risk-ai-domains)
3. [Framework Architecture](#3-framework-architecture)
4. [Core Layers](#4-core-layers)
5. [Domain Profiles](#5-domain-profiles)
6. [Cryptographic Requirements](#6-cryptographic-requirements)
7. [Data Model](#7-data-model)
8. [Conformance Levels](#8-conformance-levels)
9. [Implementation Guidelines](#9-implementation-guidelines)
10. [Governance and Standardization](#10-governance-and-standardization)
11. [Relation to International Standards (Non-Normative)](#11-relation-to-international-standards)
12. [References](#12-references)

---

## 1. Introduction

### 1.1 Purpose

VAP (Verifiable AI Provenance Framework) is an upper-level framework designed to address the following structural challenges:

| Challenge | Description | VAP Solution |
|-----------|-------------|--------------|
| **Non-reproducibility** | AI decision processes cannot be reproduced | Provenance Layer records decision lineage |
| **Absence of records** | Decision-making processes are not recorded | Integrity Layer provides automated logging |
| **Tamperability** | Audit records can be retroactively modified | Hash Chain + Merkle Tree provide cryptographic guarantees |
| **Ambiguous accountability** | Responsible parties cannot be identified after incidents | Accountability Layer makes responsibility boundaries visible |

### 1.2 Design Philosophy

VAP is guided by the following principle:

> **"Not a regulation that restricts AI usage, but a common provenance infrastructure for the safe and continuous operation of AI systems."**

By ensuring transparency and traceability of AI decision processes without impeding technological progress, VAP enables continued AI adoption while maintaining societal trust.

### 1.3 Scope Definition

VAP targets **"domains where system failure can cause serious and irreversible harm to human life, societal infrastructure, or democratic institutions."**

This definition is intentionally strict. VAP is not a general-purpose logging framework — it is **provenance infrastructure essential for AI systems operating as societal infrastructure.**

### 1.4 Conformance Language

In this specification, the following keywords are interpreted in accordance with RFC 2119:

- **MUST** / **REQUIRED** / **SHALL**: Absolute requirement
- **MUST NOT** / **SHALL NOT**: Absolute prohibition
- **SHOULD** / **RECOMMENDED**: Recommended (deviation permitted with justifiable reason)
- **MAY** / **OPTIONAL**: Optional

### 1.5 Terminology

| Term | Definition |
|------|------------|
| **VAP** | Verifiable AI Provenance Framework — Cross-domain upper-level framework |
| **VSO** | VeritasChain Standards Organization — Standards body that develops and maintains VAP |
| **Profile** | Domain-specific implementation of VAP (VCP, DVP, MAP, etc.) |
| **Provenance** | Cryptographically verifiable record of data origin, lineage, and history |
| **High-Risk AI** | High-risk AI systems as defined in EU AI Act Article 6 |

---

## 2. High-Risk AI Domains

### 2.1 Normative Scope Statement

**VAP (Verifiable AI Provenance Framework) is designed as an audit infrastructure for AI decisions in domains where system failure can cause serious and irreversible harm to human life, societal infrastructure, or democratic institutions.**

The following five domains are defined as **Mandatory Application Domains** for VAP.

### 2.2 Domain Definitions

#### 2.2.1 Financial Infrastructure

| Attribute | Value |
|-----------|-------|
| **Profile ID** | VCP (VeritasChain Protocol) |
| **Status** | v1.0 Released |
| **Risk Category** | Systemic Risk / Market Integrity |

**Scope:**
- High-frequency trading (HFT) systems
- AI/algorithm-driven trading strategies
- Exchanges, clearinghouses, prime brokers
- Risk management systems
- Credit scoring AI

**Failure Impact:**
- Sudden market volatility caused by AI/HFT malfunction
- Cascading impact on pension funds, corporate finance, and national fiscal systems
- Materialization of systemic risk (2010 Flash Crash: $1 trillion evaporated in minutes)

**Regulatory Drivers:**
- EU AI Act Article 6(2) — Credit scoring classified as high-risk AI
- MiFID II Article 17 — Algorithmic trading audit requirements
- CAT Rule 613 — Consolidated Audit Trail

**VAP Requirements:**
- Cryptographic chain recording of trading events
- Preservation of AI decision rationale (DecisionFactors)
- Nanosecond-precision timestamp synchronization

---

#### 2.2.2 Medical and Healthcare AI

| Attribute | Value |
|-----------|-------|
| **Profile ID** | MAP (Medical AI Protocol) |
| **Status** | Planned |
| **Risk Category** | Patient Safety / Life-Critical |

**Scope:**
- AI diagnostic support systems
- Imaging AI (radiology, pathology)
- Triage and priority assessment AI
- Medication recommendation and drug interaction checking
- Surgical robot decision logic

**Failure Impact:**
- Direct patient harm from diagnostic errors
- Severe adverse effects from medication errors
- Delayed appropriate care from triage misjudgment

**Regulatory Drivers:**
- EU AI Act Annex III — Medical device AI classified as high-risk
- FDA AI/ML-Based SaMD Guidance
- MDR (Medical Device Regulation) 2017/745

**VAP Requirements:**
- Complete recording and reconstruction capability for diagnostic rationale
- Identification of data and model versions used in decision-making
- Capability to provide evidence for medical incident investigation and litigation

---

#### 2.2.3 Transportation and Autonomous Systems

| Attribute | Value |
|-----------|-------|
| **Profile ID** | DVP (Driving Vehicle Protocol) / AAP (Aviation AI Protocol) |
| **Status** | Planned |
| **Risk Category** | Physical Safety / Mass Casualty Prevention |

**Scope:**
- Autonomous vehicles (Level 3–5)
- ADAS (Advanced Driver-Assistance Systems)
- Aircraft autopilot and air traffic control AI
- Railway operations management systems
- Autonomous drone control

**Failure Impact:**
- Traffic accidents from autonomous driving misjudgment
- Aviation accident risk from ATC AI malfunction
- Service disruption from railway control errors

**Regulatory Drivers:**
- EU AI Act Annex III — Transport safety AI classified as high-risk
- UNECE WP.29 — Automated driving system regulations
- FAA Advisory Circular 23.1309-1E

**VAP Requirements:**
- Integration of physical flight recorder with AI decision recorder
- Complete causal chain recording from sensor input → decision → control output
- Compatibility between real-time recording and offline verification

**Unique Characteristic:**
> **The ultimate form for this domain is AI decision-level provenance recording in addition to physical flight recorders.**

---

#### 2.2.4 Energy and Critical Infrastructure

| Attribute | Value |
|-----------|-------|
| **Profile ID** | EIP (Energy Infrastructure Protocol) |
| **Status** | Planned |
| **Risk Category** | Societal Continuity / Critical Infrastructure |

**Scope:**
- Power grid management and supply-demand balancing AI
- Water network monitoring and control systems
- Telecommunications infrastructure management AI
- Gas pipeline control
- Nuclear power plant monitoring systems

**Failure Impact:**
- Large-scale blackouts from power grid AI malfunction (affecting medical devices, HVAC)
- Water quality and supply impacts from water system errors
- Cascading effects on emergency services and financial systems from telecom infrastructure failure

**Regulatory Drivers:**
- EU NIS2 Directive — Critical infrastructure security
- NERC CIP Standards — Power system cybersecurity
- EU AI Act — Energy management AI classified as high-risk

**VAP Requirements:**
- Root cause tracking for anomalous AI decisions
- State reconstruction for failure recovery
- Root cause analysis for cascading failures

**Unique Characteristic:**
> **Infrastructure directly tied to societal continuity. Decision history tracing is indispensable for recovery.**

---

#### 2.2.5 Public Policy, Law Enforcement, and Justice

| Attribute | Value |
|-----------|-------|
| **Profile ID** | PAP (Public Administration Protocol) |
| **Status** | Planned |
| **Risk Category** | Democratic Integrity / Civil Rights |

**Scope:**
- Credit scoring and loan assessment AI
- Welfare benefit determination systems
- Immigration and visa assessment AI
- Recidivism prediction
- Recruitment and performance evaluation AI

**Failure Impact:**
- If decision rationale cannot be traced, appeals and judicial review become difficult
- Entrenchment of unfair determinations from biased AI
- Algorithmic decision-making without democratic oversight

**Regulatory Drivers:**
- EU AI Act Article 6(2) — AI affecting fundamental rights classified as high-risk
- GDPR Article 22 — Right to object to automated decision-making
- US Executive Order 14110 — AI safety

**VAP Requirements:**
- Full explainability of decisions affecting individuals
- Post-hoc audit and appeal response capability
- Transparency for democratic oversight

**Unique Characteristic:**
> **AI whose decision rationale cannot be traced undermines the foundation of democratic accountability.**

---

### 2.3 Domain Classification Matrix

| Domain | Profile | Failure Mode | Time to Impact | Reversibility |
|--------|---------|--------------|----------------|---------------|
| Financial | VCP | Systemic Instability | Milliseconds | Partial |
| Medical | MAP | Patient Harm | Minutes–Hours | Irreversible |
| Transportation | DVP/AAP | Physical Harm | Seconds | Irreversible |
| Energy | EIP | Infrastructure Disruption | Minutes–Days | Slow Recovery |
| Public Policy | PAP | Institutional Erosion | Months–Years | Difficult |

### 2.4 Common Requirements Across Domains

Requirements common to all High-Risk Domains:

| Requirement ID | Requirement | Rationale |
|----------------|-------------|-----------|
| **HR-001** | Cryptographic integrity (Hash Chain) | Tamper detection |
| **HR-002** | Decision lineage recording (Provenance) | Reconstruction capability |
| **HR-003** | Causal chain tracing (Traceability) | Root cause analysis |
| **HR-004** | Accountability boundary definition (Accountability) | Legal responsibility identification |
| **HR-005** | Explainability | Regulatory and litigation response |
| **HR-006** | Privacy protection (Privacy) | GDPR compliance |

### 2.5 Domain Selection Criteria

#### 2.5.1 Selection Criteria

VAP Mandatory Application Domains were selected based on the following criteria:

1. **Irreversibility**: Consequences of decision errors are difficult or impossible to recover from
2. **Scale**: Impact affects society as a whole, not just individuals
3. **Velocity**: Impact propagates faster than human intervention can prevent
4. **Regulatory Mandate**: Existing or planned regulations require transparency

#### 2.5.2 Strategic Implications

The explicit definition of these five domains provides:

| Implication | Description |
|-------------|-------------|
| **VAP universality** | Demonstrates VAP as a general-purpose framework, not limited to finance |
| **VAP necessity** | Establishes positioning as the upper layer of AI societal infrastructure |
| **Lower adoption barriers** | Provides rational grounds for non-financial organizations to adopt VAP compliance |
| **Prevention of standards fragmentation** | Prevents proliferation of domain-specific protocols, ensuring interoperability |
| **Facilitation of international standardization** | Smooths transition to ISO and other international standardization processes |

---

## 3. Framework Architecture

### 3.1 Layered Architecture

VAP comprises the following five mandatory layers:

```
┌─────────────────────────────────────────────────────────────┐
│                   Domain Profiles Layer                      │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│   │   VCP   │ │   DVP   │ │   MAP   │ │   PAP   │   ...    │
│   │(Finance)│ │ (Auto)  │ │(Medical)│ │(Public) │          │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
├─────────────────────────────────────────────────────────────┤
│                  Accountability Layer                        │
│   Responsibility identification · Boundary definition ·     │
│   Audit trails                                               │
├─────────────────────────────────────────────────────────────┤
│                  Traceability Layer                          │
│   Causal structure reconstruction · Temporal tracking ·      │
│   Incident analysis                                          │
├─────────────────────────────────────────────────────────────┤
│                   Provenance Layer                           │
│   Actor / Input / Context / Action / Outcome recording       │
├─────────────────────────────────────────────────────────────┤
│                    Integrity Layer                           │
│   Hash Chain · Merkle Tree · Digital Signatures              │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Layer Dependency

Each layer depends on the layers below it:

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

The following concerns span all layers:

| Concern | Description | Implementation Requirement |
|---------|-------------|---------------------------|
| **Privacy** | Personal data protection | Crypto-shredding, anonymization |
| **Security** | Cryptographic security | Ed25519/Dilithium, SHA-256/SHA3 |
| **Performance** | Low latency, high throughput | Tier-specific performance requirements |
| **Interoperability** | Cross-system integration | JSON/SBE, standard APIs |

---

## 4. Core Layers

### 4.1 Integrity Layer

#### 4.1.1 Purpose

Provides cryptographic guarantees of tamper-resistance for all AI decision events.

#### 4.1.2 Requirements

| Req ID | Requirement | Level |
|--------|-------------|-------|
| INT-001 | All events MUST be canonicalized | MUST |
| INT-002 | Each event MUST have a unique identifier (UUID v7 recommended) | MUST |
| INT-003 | Events MUST be linked via cryptographic hash (SHA-256 or stronger) | MUST |
| INT-004 | Hash chain MUST maintain continuity | MUST |
| INT-005 | Non-repudiation SHOULD be achieved via digital signatures or TEE signatures | SHOULD |
| INT-006 | Periodic Merkle Tree anchoring SHOULD be performed | SHOULD |

#### 4.1.3 Hash Chain Construction

```
Event_n = {
    Header,
    Payload,
    Security: {
        event_hash: H(canonical(Header) || canonical(Payload) || prev_hash),
        prev_hash: Event_(n-1).event_hash,
        signature: Sign(event_hash, private_key)
    }
}
```

**Hash Chain Validation Algorithm:**

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

#### 4.1.4 Merkle Tree Anchoring

Merkle Tree construction conforming to RFC 6962 (Certificate Transparency) is **REQUIRED**:

```
Leaf(D) = H(0x00 || D)        // Leaf node
Node(L, R) = H(0x01 || L || R) // Internal node
```

**Domain Separation (0x00/0x01 prefix) is REQUIRED to prevent second preimage attacks.**

#### 4.1.5 Cryptographic Algorithm Support

| Algorithm | Type | Status | Post-Quantum Safe |
|-----------|------|--------|-------------------|
| **SHA-256** | Hash | DEFAULT | Partial (128-bit effective) |
| SHA3-256 | Hash | SUPPORTED | Partial |
| BLAKE3 | Hash | SUPPORTED | Partial |
| **Ed25519** | Signature | DEFAULT | No |
| ECDSA secp256k1 | Signature | SUPPORTED | No |
| **DILITHIUM2** | Signature | FUTURE | Yes |
| FALCON-512 | Signature | FUTURE | Yes |

**Crypto Agility Requirement:** All VAP-compliant implementations MUST include a field identifying the signature algorithm and MUST enable future algorithm migration.

---

### 4.2 Provenance Layer

#### 4.2.1 Purpose

Records AI decision lineage in structured form: who acted, what they received, under what conditions, what they referenced, and what they produced.

#### 4.2.2 Abstract Data Model

VAP defines a domain-independent abstract model:

```json
{
  "provenance": {
    "actor": {
      "type": "enum",           // AI_MODEL, HUMAN, EXTERNAL_AGENT, HYBRID
      "identifier": "string",   // Unique identifier
      "version": "string",      // Version info (for AI_MODEL)
      "hash": "string"          // Model parameter hash (for AI_MODEL)
    },
    "input": {
      "sources": ["array"],     // List of input data sources
      "timestamp": "int64",     // Input acquisition time
      "hash": "string"          // Input data hash
    },
    "context": {
      "parameters": "object",   // Active parameters
      "constraints": "object",  // Applied constraints
      "environment": "object"   // Execution environment info
    },
    "action": {
      "type": "string",         // Type of decision/proposal/recommendation
      "decision": "object",     // AI decision content
      "confidence": "string",   // Confidence score (0.0–1.0)
      "explainability": {
        "method": "enum",       // SHAP, LIME, GRADCAM, RULE_TRACE, NONE
        "factors": ["array"]    // Factors contributing to decision
      }
    },
    "outcome": {
      "result": "object",       // Execution result
      "timestamp": "int64",     // Result finalization time
      "status": "enum"          // SUCCESS, FAILURE, PARTIAL, PENDING
    }
  }
}
```

#### 4.2.3 Domain Profile Mapping

| VAP Abstract | VCP (Finance) | DVP (Automotive) | MAP (Medical) | PAP (Public) |
|--------------|---------------|------------------|---------------|--------------|
| actor | Algorithm/Trader | AutonomousSystem/Driver | DiagnosticAI/Physician | ScoringAI/Officer |
| input | MarketData/Signals | SensorData/LIDAR/Camera | PatientData/Imaging | ApplicationData/Records |
| context | RiskParameters/Limits | EnvironmentConditions/Route | ClinicalProtocol/History | PolicyRules/Guidelines |
| action | TradeSignal/Order | PathPlanning/Control | Diagnosis/TreatmentPlan | Decision/Recommendation |
| outcome | Execution/Fill | VehicleState/Maneuver | PatientOutcome/Response | Determination/Appeal |

---

### 4.3 Traceability Layer

#### 4.3.1 Purpose

Enables reconstruction of decision chains in both temporal sequence and causal structure.

#### 4.3.2 Requirements

| Req ID | Requirement | Level |
|--------|-------------|-------|
| TRC-001 | MUST be capable of expressing causal relationships between events | MUST |
| TRC-002 | MUST be capable of grouping related events via trace_id | MUST |
| TRC-003 | SHOULD be capable of reconstructing system state at any point in time | SHOULD |
| TRC-004 | SHOULD provide query capabilities supporting root cause analysis (RCA) | SHOULD |

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

**Finance (VCP):**
```
Signal Generated (SIG) → Order Sent (ORD) → Acknowledged (ACK) → Executed (EXE) → Position Closed (CLS)
```

**Automotive (DVP):**
```
Sensor Input → Perception → Path Planning → Control Command → Vehicle State
```

**Medical (MAP):**
```
Patient Data → Analysis → Diagnosis → Treatment Plan → Outcome
```

**Public (PAP):**
```
Application → Evaluation → Scoring → Decision → Notification → Appeal
```

---

### 4.4 Accountability Layer

#### 4.4.1 Purpose

Enables identification of responsible parties in AI-involved decisions.

#### 4.4.2 Actor Types

| Actor Type | Description | Example |
|------------|-------------|---------|
| **MODEL_DEVELOPER** | AI model developer | Machine learning engineer |
| **AI_PROVIDER** | AI system provider | SaaS vendor |
| **OPERATOR** | Operator | Trader, driver, physician |
| **DATA_VENDOR** | Data provider | Market data vendor |
| **FINAL_DECISION_MAKER** | Final decision maker | Risk manager |

#### 4.4.3 Responsibility Schema

```json
{
  "accountability": {
    "operator_id": "string",           // Operator identifier
    "last_approval_by": "string",      // Final approver
    "approval_timestamp": "int64",     // Approval time
    "delegation_chain": [              // Delegation chain
      {
        "delegator": "string",
        "delegatee": "string",
        "scope": "string",
        "valid_from": "int64",
        "valid_until": "int64"
      }
    ],
    "override_history": [              // Override history
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

| Requirement | VAP Implementation |
|-------------|-------------------|
| Enable human monitoring | operator_id field |
| Intervention capability | HALT/OVERRIDE event types |
| Override functionality | override_history recording |

---

### 4.5 Domain Profiles Layer

#### 4.5.1 Purpose

Defines domain-specific extensions on top of VAP common layers.

#### 4.5.2 Profile Registry

| Profile ID | Domain | Status | Specification |
|------------|--------|--------|---------------|
| **VCP** | Finance / Algorithmic Trading | **v1.0 Released** | VSO-VCP-SPEC-001 |
| DVP | Automotive / Autonomous Driving | Planned | — |
| AAP | Aviation / Air Traffic Control | Planned | — |
| MAP | Medical / Healthcare AI | Planned | — |
| EIP | Energy / Critical Infrastructure | Planned | — |
| PAP | Public Sector / Government AI | Planned | — |

#### 4.5.3 Profile Extension Mechanism

Each profile can define the following extension points:

```json
{
  "profile_extension": {
    "profile_id": "string",
    "profile_version": "string",
    "domain_specific_modules": ["array"],
    "domain_specific_events": ["array"],
    "domain_specific_constraints": {
      "timestamp_precision": "enum",
      "clock_sync_requirement": "enum"
    }
  }
}
```

---

## 5. Domain Profiles

### 5.1 VCP: Finance Profile

**Status:** v1.0 Released  
**Document:** VSO-VCP-SPEC-001

#### 5.1.1 Overview

VCP (VeritasChain Protocol) is the financial domain profile of VAP, standardizing audit trails for algorithmic trading and AI-driven trading systems.

**VCP is the first implementation profile of the VAP family, positioned as the provenance standard for the finance and algorithmic trading domain.**

#### 5.1.2 Domain-Specific Modules

| Module | Purpose | VAP Layer Mapping |
|--------|---------|-------------------|
| **VCP-CORE** | Standard header and security | Integrity Layer |
| **VCP-TRADE** | Trading payload | Provenance Layer (action/outcome) |
| **VCP-GOV** | Algorithm governance | Provenance Layer (actor/context) |
| **VCP-RISK** | Risk parameter recording | Provenance Layer (context) |
| **VCP-PRIVACY** | Crypto-shredding | Cross-cutting (Privacy) |
| **VCP-RECOVERY** | Chain recovery | Integrity Layer |

#### 5.1.3 Compliance Tiers

| Tier | Target | Clock Sync | Signature | Anchor Frequency |
|------|--------|------------|-----------|------------------|
| **Platinum** | HFT/Exchange | PTPv2 (<1µs) | Ed25519 (Hardware) | 10 minutes |
| **Gold** | Institutional | NTP (<1ms) | Ed25519 (Client) | 1 hour |
| **Silver** | Retail/MT4/5 | Best-effort | Ed25519 (Delegated) | 24 hours |

#### 5.1.4 Regulatory Compliance

| Regulation | VCP Module | Implementation |
|------------|------------|----------------|
| EU AI Act Art. 12 | VCP-CORE | Automated event logging |
| EU AI Act Art. 13 | VCP-GOV | DecisionFactors |
| EU AI Act Art. 14 | VCP-GOV | OperatorID, LastApprovalBy |
| MiFID II Art. 17 | VCP-GOV | AlgoID, TestingRecordLink |
| MiFID II RTS 25 | VCP-CORE | ClockSyncStatus |
| GDPR Art. 17 | VCP-PRIVACY | Crypto-shredding |

---

### 5.2 Future Profiles (Planned)

#### 5.2.1 DVP: Automotive Profile

**Scope:** Autonomous vehicles, ADAS, drones

**Key Events:**
- SENSOR_INPUT, PERCEPTION, PATH_PLANNING, CONTROL_COMMAND
- TAKEOVER_REQUEST, EMERGENCY_STOP, COLLISION_WARNING

#### 5.2.2 MAP: Medical Profile

**Scope:** AI diagnostics, imaging analysis, medication support, surgical robots

**Key Events:**
- IMAGING_ACQUIRED, ANALYSIS_COMPLETED, DIAGNOSIS_SUGGESTED
- PHYSICIAN_REVIEWED, TREATMENT_PROPOSED, PATIENT_CONSENTED

#### 5.2.3 PAP: Public Administration Profile

**Scope:** Credit scoring, welfare determination, immigration, recruitment AI

**Key Events:**
- APPLICATION_RECEIVED, EVALUATION_STARTED, SCORING_COMPLETED
- DECISION_MADE, NOTIFICATION_SENT, APPEAL_FILED

---

## 6. Cryptographic Requirements

### 6.1 Algorithm Requirements

#### 6.1.1 Hash Functions

| Requirement | Specification |
|-------------|---------------|
| Minimum Security | 128-bit effective security |
| Default Algorithm | SHA-256 |
| Alternative Algorithms | SHA3-256, BLAKE3 |
| Collision Resistance | MUST resist birthday attacks |

#### 6.1.2 Digital Signatures

| Requirement | Specification |
|-------------|---------------|
| Default Algorithm | Ed25519 |
| Key Size | 256-bit (Ed25519) |
| Signature Size | 64 bytes (Ed25519) |
| Future Migration | DILITHIUM2, FALCON-512 |

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

**Key Insight:** VAP hash chain integrity is preserved even after quantum attacks.

#### 6.2.2 Migration Path

```
Phase 1 (Current): Ed25519 + SHA-256
Phase 2 (Hybrid):  Ed25519 || Dilithium (dual signature)
Phase 3 (PQC):     Dilithium2 + SHA3-256
```

### 6.3 Crypto-Shredding for Privacy

#### 6.3.1 Mechanism

```
Before Key Destruction:
  Encrypted Data + Encryption Key → Original Data

After Key Destruction:
  Encrypted Data + [KEY DESTROYED] → Mathematically Unrecoverable
```

#### 6.3.2 Hash Chain Preservation

| Component | After Crypto-Shredding |
|-----------|------------------------|
| Hash Chain Structure | ✅ Intact |
| Merkle Tree | ✅ Intact |
| Cryptographic Proofs | ✅ Verifiable |
| Original Data | ❌ Permanently unrecoverable |

---

## 7. Data Model

### 7.1 Common Event Structure

All VAP-compliant events MUST have the following structure:

```json
{
  "vap_version": "1.1",
  "profile": {
    "id": "string",
    "version": "string"
  },
  "header": {
    "event_id": "uuid_v7",
    "trace_id": "uuid_v7",
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
    "event_hash": "string",
    "prev_hash": "string",
    "hash_algo": "enum",
    "signature": "string",
    "sign_algo": "enum",
    "signer_id": "string"
  }
}
```

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

---

## 8. Conformance Levels

### 8.1 Level Definitions

| Level | Description | Requirements |
|-------|-------------|--------------|
| **VAP-Core** | Minimum conformance | Integrity Layer mandatory requirements only |
| **VAP-Standard** | Standard conformance | Core + Provenance + Traceability |
| **VAP-Full** | Full conformance | Standard + Accountability + Profile Extensions |

### 8.2 Certification Program

| Certification | Level | Requirements |
|---------------|-------|--------------|
| **VAP-Ready** | Core | Basic test suite pass |
| **VAP-Compliant** | Standard | Standard test suite pass + audit |
| **VAP-Certified** | Full | Full test suite pass + third-party audit |

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
│  Event Capture → Chain Builder → Merkle Anchor   │
└──────────────────────────────────────────────────┘
```

### 9.2 Integration Patterns

| Pattern | Use Case | Complexity |
|---------|----------|------------|
| **Sidecar** | Legacy system integration | Low |
| **SDK** | New application development | Medium |
| **Middleware** | Enterprise gateway | High |
| **Native** | Ground-up implementation | Very High |

---

## 10. Governance and Standardization

### 10.1 VSO Structure

```
VeritasChain Standards Organization (VSO)
├── Technical Committee
│   ├── Core Working Group (VAP Framework)
│   ├── Finance Working Group (VCP)
│   ├── Automotive Working Group (DVP)
│   ├── Medical Working Group (MAP)
│   └── Public Sector Working Group (PAP)
├── Certification Authority
│   └── Conformance Testing
└── Advisory Board
    ├── Industry Representatives
    └── Regulatory Liaisons
```

### 10.2 Standardization Roadmap

| Phase | Timeline | Activities |
|-------|----------|------------|
| **Phase 1** | 2025 Q1–Q2 | VCP v1.0 Release, VAP Framework Draft |
| **Phase 2** | 2025 Q3–Q4 | VAP v1.0 Formalization, IETF Internet-Draft |
| **Phase 3** | 2026 | ISO TC 68 Submission, DVP/MAP Development |
| **Phase 4** | 2027+ | International Standard, PQC Migration |

### 10.3 Change Management

Specification changes follow this process:

1. **RFC (Request for Comments)** submission
2. **Public Review** period (30 days)
3. **Technical Committee** deliberation
4. **Vote** (approved by two-thirds majority)
5. **Release**

---

## 11. Relation to International Standards (Non-Normative)

### 11.1 Broader AI Provenance Framework Context

VCP is designed as the **financial profile** of the broader Verifiable AI Provenance (VAP) framework, applicable in the future to other domains as well.

### 11.2 Standards Landscape

| Domain | Existing Standards | VAP Profile Role |
|--------|-------------------|------------------|
| Financial Trading | FIX, ISO 20022 | VCP complements existing formats with provenance |
| Automotive | ISO 26262, UNECE WP.29 | DVP adds AI decision provenance to safety standards |
| Medical Devices | IEC 62304, FDA SaMD | MAP adds AI explainability to device logging |
| Critical Infrastructure | IEC 62443, NERC CIP | EIP adds AI provenance to SCADA/ICS logging |

### 11.3 Future Standardization

VSO plans the following standardization activities:

| Target | Timeline | Status |
|--------|----------|--------|
| IETF Internet-Draft | 2025 Q3 | Planned |
| ISO/TC 68 (Financial Services) | 2026 | Planned |
| ISO/IEC JTC 1/SC 42 (AI) | 2026–2027 | Planned |
| IEEE Standards Association | 2027+ | Under consideration |

---

## 12. References

### 12.1 Standards

| Standard | Description |
|----------|-------------|
| RFC 9562 | UUID v7 |
| RFC 8785 | JSON Canonicalization Scheme |
| RFC 6962 | Certificate Transparency |
| RFC 8032 | Ed25519 Digital Signature |
| IEEE 1588-2019 | Precision Time Protocol |

### 12.2 Regulations

| Regulation | Jurisdiction | Relevance |
|------------|--------------|-----------|
| EU AI Act | European Union | High-Risk AI Classification |
| MiFID II | European Union | Financial Trading |
| GDPR | European Union | Data Privacy |
| CAT Rule 613 | United States | Consolidated Audit Trail |
| NIS2 Directive | European Union | Critical Infrastructure |

### 12.3 Related VSO Documents

| Document ID | Title |
|-------------|-------|
| VSO-VCP-SPEC-001 | VeritasChain Protocol Specification v1.0 |
| VSO-SDK-SPEC-001 | VCP SDK Specification v1.0 |
| VSO-TEST-001 | VCP Conformance Test Guide v1.0 |

---

## Appendix A: Glossary

| Term | Definition |
|------|------------|
| **VAP** | Verifiable AI Provenance Framework — Cross-domain upper-level framework |
| **VSO** | VeritasChain Standards Organization — Standards body that develops and maintains VAP |
| **VCP** | VeritasChain Protocol — VAP Finance Profile |
| **DVP** | Driving Vehicle Protocol — VAP Automotive Profile |
| **MAP** | Medical AI Protocol — VAP Medical Profile |
| **PAP** | Public Administration Protocol — VAP Public Sector Profile |
| **EIP** | Energy Infrastructure Protocol — VAP Energy Profile |
| **AAP** | Aviation AI Protocol — VAP Aviation Profile |
| **Provenance** | Cryptographically verifiable record of data origin, lineage, and history |
| **High-Risk AI** | High-risk AI systems as defined in EU AI Act Article 6 |

---

## Appendix B: Version History

| Version | Date | Changes | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-12-11 | Initial Release | VSO Technical Committee |
| 1.1.0 | 2025-12-11 | Added High-Risk AI Domains, VSO/VAP/VCP hierarchy clarification | VSO Technical Committee |

---

## Appendix C: License

This specification is licensed under **Creative Commons Attribution 4.0 International (CC BY 4.0)**.

---

## Contact Information

**VeritasChain Standards Organization (VSO)**  
Website: https://veritaschain.org  
Email: standards@veritaschain.org  
Technical: technical@veritaschain.org  
GitHub: https://github.com/veritaschain

---

## Declaration

> **VAP (Verifiable AI Provenance Framework), as the uppermost conceptual layer of AI societal infrastructure, defines the foundational infrastructure for AI decision provenance and safety in domains where system failure can cause serious and irreversible harm to human life, societal infrastructure, or democratic institutions.**
>
> VSO, positioned alongside W3C (Web), IETF (Network), IEEE (Communications), and FIX (Financial Trading), develops and maintains this framework as an **international standards body for AI decision provenance.**
>
> VCP is the first implementation profile of the VAP family, operating as the provenance standard for the finance and algorithmic trading domain.

---

*"Encoding Trust in the AI Age"*

*End of Verifiable AI Provenance Framework (VAP) Specification v1.1*
