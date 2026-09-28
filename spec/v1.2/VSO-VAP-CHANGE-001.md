# VSO-VAP-CHANGE-001
## VAP Framework v1.2 Change Proposal

**Document ID:** VSO-VAP-CHANGE-001
**Status:** Change Proposal — Draft for Technical Committee Review
**Proposal Version:** 0.1
**Applies to:** VAP Framework Specification v1.1 (VSO-VAP-SPEC-001, 2025-12-11) → v1.2
**Date:** 2026-06-10
**Maintainer:** VeritasChain Standards Organization (VSO)
**License:** CC BY 4.0 International
**Normative references at time of writing:**
- VSO-VAP-SPEC-001 — VAP Framework Specification v1.1
- VSO-VCP-SPEC (v1.1, 2025-12-30; v1.2 RC1, 2026-05-31)
- VSO-SPEC-CHANGE-001 — VCP v1.2 Change Proposal (normative annex to VCP v1.2)
- CAP v1.0 (Content / Creative AI Profile), CPP v1.0 (Capture Provenance Profile)

> This document is the **change-control record** for the VAP v1.1 → v1.2 revision. Upon adoption, it becomes a **normative annex** (or change-control reference) of VAP Framework Specification v1.2. Where the v1.2 specification text and this document differ in detail, the v1.2 specification text prevails after publication; until publication, this document is authoritative for Technical Committee deliberation.

---

## 1. Executive Summary

VAP v1.2 is a **framework-compatible / certification-stricter** revision: all v1.1 event data remains valid under v1.2 (event-data-compatible at the wire level), while certification requirements are tightened. This mirrors, at the meta-framework level, the "protocol-compatible / certification-stricter" change discipline established by VCP v1.1 and VCP v1.2.

The revision has two drivers:

1. **Normative repair.** VAP v1.1 contains Integrity Layer requirements (INT-003, INT-004) that mandate per-event hash chaining (PrevHash) as a framework-level MUST. VCP — the flagship profile — made PrevHash OPTIONAL in v1.1, replacing it with a three-layer integrity model (EventHash + Merkle collection integrity + mandatory external anchoring). The profile therefore currently violates its own meta-framework. VAP v1.2 resolves this by abstracting "Hash Chain MUST" into **"Cryptographic Sequence Verifiability MUST"**, with mechanism selection delegated to profiles.

2. **Common-infrastructure consolidation.** Capabilities that VCP v1.1/v1.2 introduced at the profile level — mandatory external anchoring, completeness guarantees, policy identification, ERASURE (crypto-shredding) events, bounded RECOVERY operations, cross-party provenance (XREF), and SCITT/COSE interoperability — are generalizable to all high-risk domains (MAP, DVP, PAP, EIP, CAP, CPP). VAP v1.2 promotes them to the Shared Assurance Core so that future profiles inherit them rather than re-invent them.

**Generalization baseline:** This proposal generalizes only those VCP capabilities that are stable in VCP v1.1 or VCP v1.2 RC1. Regulatory-evidence vocabulary introduced in later VCP v1.2 working drafts is deferred to VSO-VAP-CHANGE-002 (Annex C).

**Compatibility statement:** VAP v1.2 introduces **zero wire-format breaking changes**. All v1.1-conformant event data remains valid under v1.2 verifiers. Certification requirements are tightened (external anchoring becomes MUST at all conformance levels); one framework-level requirement is relaxed-by-abstraction (INT-003/004). Existing profile certifications remain protocol-compatible; profiles must republish conformance mappings to claim VAP v1.2 alignment.

**Scope honesty:** VAP and its profiles produce **verifiable evidence**. They do not, by themselves, constitute or guarantee legal compliance with the EU AI Act, GDPR, MiFID II, or any other regulation. See Section 7.

---

## 2. Problem Statement: VAP v1.1 / VCP v1.1–v1.2 Normative Misalignment

### 2.1 Direct contradictions

| # | VAP v1.1 (framework) | VCP v1.1 / v1.2 (profile) | Conflict type |
|---|---|---|---|
| M-1 | INT-003: "Events MUST be linked via cryptographic hash"; INT-004: "Hash chain MUST maintain continuity"; validation algorithm assumes contiguous `prev_hash` | PrevHash is **OPTIONAL** (Security object, v1.1 §6.4.1); equivalent integrity achieved via Merkle (Layer 2) + mandatory external anchor (Layer 3) | **Profile violates framework MUST** |
| M-2 | INT-006: "Periodic Merkle Tree anchoring **SHOULD** be performed" | External Anchor **REQUIRED for all tiers** (v1.1 §6.3.3), incl. lightweight options for Silver; anchor continuity plan REQUIRED in v1.2 (Annex §7) | **Framework weaker than profile**; contradicts "Verify, Don't Trust" |
| M-3 | Common event structure (§7.1) has `profile.id/version` but no policy declaration | Policy Identification **REQUIRED** for all events (v1.1 §5.5): PolicyID, ConformanceTier, VerificationDepth | Framework data model incomplete relative to profile MUST |

### 2.2 Capability gaps (no contradiction, but framework silence)

| # | Capability | Introduced in | Cross-domain relevance |
|---|---|---|---|
| G-1 | Completeness guarantees (omission / split-view detection) | VCP v1.1 §1.1 | All domains: "no required events were omitted" is as important as "no events were altered" |
| G-2 | ERASURE event (crypto-shredding, GDPR Art. 17) | VCP v1.2 §3.2.2 / Annex §3 | MAP (patient data), PAP (citizen data), CAP (creator data) face identical erasure-vs-immutability tension |
| G-3 | RECOVERY operational constraints (bounded SKIP/REBUILD/MERGE/CHECKPOINT, Emergency Override) | VCP v1.2 Annex §1 | Unbounded "recovery" is a laundering vector in every domain |
| G-4 | Cross-party provenance / dual logging (XREF), multi-actor chains | VCP v1.1 §5.6; v1.2 Annex §9 | MAP: hospital↔AI vendor; PAP: agency↔auditor; DVP: OEM↔fleet operator |
| G-5 | SCITT / COSE Receipts alignment | VCP v1.2 Annex §5 | Framework-level IETF strategy (VAP bridges SCITT and RATS) requires framework-level fields |
| G-6 | PQC status: VAP lists DILITHIUM2 / FALCON-512 as FUTURE | VCP v1.2 advances to **EXPERIMENTAL** (ML-DSA / FIPS 204, FN-DSA / FIPS 206 draft), hybrid dual signatures | Algorithm status must be set by the framework, not diverge per profile |
| G-7 | Anchor target continuity (fallback target, failover procedure) | VCP v1.1 §6.3.3 (unavailability handling); v1.2 Annex §7 | Anchor discontinuity destroys external verifiability in every domain |
| G-8 | Version compatibility management | VCP v1.2 §10.5 | VAP/profile versions will drift; a 3-tier model (VAP version / Profile version / Compatibility Matrix) is required |
| G-9 | Profile registry staleness | — | VAP v1.1 registry lists only VCP v1.0; CAP v1.0, CPP v1.0 are released; VCP is at v1.2 RC1; IAP is announced |

### 2.3 Consequence of inaction

If VAP v1.2 is not issued: (a) every CAB assessing a profile against "VAP conformance" inherits the M-1 contradiction and must improvise an interpretation; (b) new profiles (DVP, MAP, PAP) will copy capabilities from VCP ad hoc, fragmenting the Shared Assurance Core; (c) VSO's IETF positioning (framework bridging SCITT/RATS) is undermined by a framework text that does not reference the relevant work. In standards governance terms, this is not merely an editorial inconsistency; it creates an auditability defect in the conformance model itself.

---

## 3. Change Classification

| Class | Definition | Count |
|---|---|---|
| **Normative-breaking (certification-level only)** | Changes that tighten or restructure MUST-level requirements such that v1.1-certified conformance claims must be re-mapped. **No wire-format breakage.** | 3 (CH-01, CH-02, CH-03) |
| **Normative-compatible** | New MUST/SHOULD requirements that are additive (opt-in adoption, or MUST only when the feature is used) | 6 (CH-04…CH-09) |
| **Normative (status change)** | Algorithm lifecycle status updates | 1 (CH-10) |
| **Informative** | Documentation, registry, guidance | 2 (CH-11, CH-12) |
| **Wire-format breaking** | — | **0** |

---

## 4. Normative Change Set

Conformance language per RFC 2119 / RFC 8174.

---

### CH-01 — Integrity Layer re-architecture: "Hash Chain MUST" → "Cryptographic Sequence Verifiability MUST"

**Class:** Normative-breaking (certification-level)
**Sections:** VAP §4.1.2 (INT-003, INT-004), §4.1.3
**Aligns with:** VCP v1.1 three-layer architecture (§6.0); VCP Security object v1.1 §6.4

**Current text (v1.1):**
> INT-003: Events MUST be linked via cryptographic hash (SHA-256 or stronger) — MUST
> INT-004: Hash chain MUST maintain continuity — MUST

**Replacement (v1.2):**

> **INT-003 (revised):** Every event MUST carry an EventHash computed over its RFC 8785-canonicalized form using an approved hash algorithm (SHA-256 or stronger).
>
> **INT-004 (revised):** VAP-level event sequencing MUST be cryptographically verifiable (**Cryptographic Sequence Verifiability**). This MAY be achieved through a profile-defined combination of: (a) per-event hash chaining (PrevHash), (b) Merkle inclusion proofs over event batches (RFC 6962), (c) external anchoring of batch roots, or (d) equivalent mechanisms providing tamper-evidence and ordering guarantees of at least equal strength. **Profiles MUST specify which mechanisms are mandatory at each conformance level**, and MUST document the resulting detection latency (real-time vs. batch-time).
>
> **INT-004a (new):** Per-event hash chaining (PrevHash) is an OPTIONAL local integrity mechanism at the framework level. Profiles MAY require it (e.g., for real-time tamper detection in HFT or safety-critical control loops). Profiles for domains with regulator-familiar chain-of-custody expectations SHOULD recommend it.

**Rationale:** Preserves the framework invariant (verifiable sequencing) while removing the mechanism mandate. VCP's PrevHash-OPTIONAL design becomes conformant; profiles such as DVP/MAP that want hash chains as MUST retain that authority. The hash-chain validation algorithm in §4.1.3 is retained as the normative procedure **when PrevHash is in use**, and a Merkle/anchor verification procedure is added alongside it.

**Migration impact:** None for data. Profiles must declare their mechanism matrix per conformance level (see §5).

---

### CH-02 — External Anchoring: SHOULD → MUST at all conformance levels

**Class:** Normative-breaking (certification-level)
**Sections:** VAP §4.1.2 (INT-006), §8 (Conformance Levels)
**Aligns with:** VCP v1.1 §6.3.3 (External Anchor REQUIRED for all tiers)

**Current text (v1.1):**
> INT-006: Periodic Merkle Tree anchoring SHOULD be performed — SHOULD

**Replacement (v1.2):**

> **INT-006 (revised):** Implementations MUST periodically construct a Merkle Tree (RFC 6962, domain-separated) over event batches and MUST anchor the signed Merkle Root to an external, independently verifiable target. External anchoring is REQUIRED at **all** conformance levels, including VAP-Core. **Anchoring frequency, acceptable anchor target classes, and proof depth are delegated to profiles and conformance levels.** Lightweight or delegated anchoring mechanisms (e.g., public timestamping services) are explicitly acceptable at the lowest conformance levels.

**Design decision (recorded):** The Technical Committee considered restricting the MUST to VAP-Standard and above. Rejected: an anchorless conformance level would split the "Verify, Don't Trust" principle — a producer-trusting integrity claim is not a VAP claim. The cost objection is addressed by delegation of frequency/target to profiles (VCP precedent: Silver tier, daily, OpenTimestamps/FreeTSA acceptable).

---

### CH-03 — Anchor Target Continuity

**Class:** Normative-breaking (certification-level)
**Sections:** new §4.1.x
**Aligns with:** VCP v1.1 §6.3.3 (unavailability handling); VCP v1.2 Annex §7

**New requirement:**

> **INT-007 (new):** Implementations MUST document an **anchor continuity plan** comprising: (a) at least one designated fallback anchor target of an acceptable class, (b) a failover procedure with a maximum migration window (profiles MUST set the window; 30 days RECOMMENDED as the framework default), (c) retention of local copies of all AnchorRecords sufficient to verify historical anchors if the original target becomes unavailable. Temporary outages MUST be handled by queueing with retry; anchor gaps exceeding 2× the profile-defined anchoring interval MUST be recorded as an error-class event.

---

### CH-04 — Completeness Invariant

**Class:** Normative-compatible
**Sections:** §1 (Purpose), §4.1 (Integrity Layer)
**Aligns with:** VCP v1.1 Completeness Guarantees (§1.1)

**New text:**

> **INT-008 (new):** VAP integrity guarantees extend beyond tamper-evidence to **completeness**: a third party MUST be able to verify, for any anchored batch, that no events within the batch's declared scope were omitted after anchoring (omission / split-view detection). Each AnchorRecord MUST bind, at minimum: event count, first/last event identifiers, and the policy identifier under which the batch was produced.
>
> **Scope note (normative):** Completeness is guaranteed **at anchor time and at batch granularity**. Profiles MUST state the completeness window implied by their anchoring frequency (e.g., a 24-hour anchoring interval provides batch-level completeness with gaps possible within the window) and MUST require disclosure of this limitation when evidence is presented to authorities.

---

### CH-05 — ERASURE Event (crypto-shredding) as Shared Assurance Core capability

**Class:** Normative-compatible (MUST when erasure is performed)
**Sections:** §6.3 (Crypto-Shredding), §7.1 (Data Model)
**Aligns with:** VCP v1.2 §3.2.2 / Annex §3

**New abstract event definition (framework level):**

> When the plaintext of protected fields is rendered irrecoverable by destruction of a per-subject data-encryption key (crypto-shredding), implementations MUST record an **ERASURE event** as a new, immutable, fully chained/anchored event. ERASURE MUST NOT delete, rewrite, or re-hash any prior event; the original EventHash, Merkle inclusion, and external anchors of target events remain verifiable.

| Field | Requirement | Notes |
|---|---|---|
| `erasure_target_event_ids` | REQUIRED | Events whose protected fields are shredded |
| `erasure_reason` | REQUIRED | `SUBJECT_REQUEST` \| `RETENTION_EXPIRED` \| `LEGAL_ORDER` (profiles MAY extend) |
| `key_destruction_proof` | REQUIRED | Evidence of DEK destruction (e.g., HSM/KMS attestation) |
| `retention_exemption` | OPTIONAL | Legal basis where retention overrides erasure |
| `operator_id` | REQUIRED | Actor authorizing the erasure |

**Legal scope clause (normative, verbatim into spec):**

> Crypto-shredding **may support** erasure obligations (e.g., GDPR Art. 17), **but does not itself determine legal compliance.** Whether crypto-shredding constitutes "erasure" is jurisdiction- and case-dependent. Profiles MUST surface domain-specific tensions (e.g., SEC 17a-4 audit-trail reproducibility in finance; medical record retention statutes in healthcare; public records law in government) and MUST require the `retention_exemption` field where a retention duty overrides an erasure request. Once a DEK is destroyed, the plaintext is by design not re-creatable.

---

### CH-06 — RECOVERY Operational Constraints

**Class:** Normative-compatible (MUST when recovery operations are performed)
**Sections:** new §4.1.y
**Aligns with:** VCP v1.2 Annex §1

**New framework requirement:**

> **INT-009 (new):** Any recovery operation that alters the effective event sequence (SKIP, REBUILD, MERGE, CHECKPOINT, or profile-defined equivalents) MUST be: (a) **bounded** — profiles MUST define quantitative limits per operation type and conformance level (e.g., maximum events skipped, maximum rebuild window); (b) **recorded** — every recovery operation MUST itself be logged as a chained/anchored event referencing the break point and validation evidence; (c) **authorized** — recovery beyond profile-defined bounds MUST require an **Emergency Override** with explicit, recorded approval by an identified human actor (`operator_id`), and Emergency Overrides MUST be flagged in conformance reporting.
>
> Recovery events MUST NOT be filtered from anchor batches. Unbounded or unrecorded recovery is non-conformant at every level.

---

### CH-07 — Policy Identification in the Common Event Model

**Class:** Normative-compatible (additive field; REQUIRED for v1.2 conformance claims)
**Sections:** §7.1 (Common Event Structure)
**Aligns with:** VCP v1.1 §5.5

**Addition to the common event structure:**

```json
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
    "sequence_mechanisms": ["enum"],   // PREV_HASH | MERKLE | EXTERNAL_ANCHOR | OTHER
    "merkle_proof_required": "boolean",   // always true in v1.2
    "external_anchor_required": "boolean" // always true in v1.2
  }
}
```

> VSO does not operate a PolicyID registry; uniqueness derives from domain ownership (VCP §5.5.4 convention adopted framework-wide). `verification_depth.sequence_mechanisms` operationalizes CH-01: the event self-declares which sequencing mechanisms a verifier should apply.

---

### CH-08 — Cross-Party Provenance (XREF abstraction)

**Class:** Normative-compatible (OPTIONAL; MUST-level requirements when used)
**Sections:** §4.3 (Traceability Layer)
**Aligns with:** VCP v1.1 §5.6; VCP v1.2 Annex §9 (multi-actor)

**New Traceability Layer mechanism:**

> **TRC-005 (new, OPTIONAL):** Profiles MAY define a **Cross-Party Provenance** mechanism whereby two or more parties independently log corresponding events sharing a `cross_reference_id` (UUID v4/v7) and a shared event key with declared matching tolerance. When used: each party MUST anchor independently; party roles MUST be declared (INITIATOR / COUNTERPARTY / OBSERVER); reconciliation status and discrepancy severity MUST follow the common enums (PENDING/MATCHED/DISCREPANCY/TIMEOUT; INFO/WARNING/CRITICAL); multi-actor chains (>2 parties) MUST define ordering and reference rules per VCP v1.2 Annex §9 semantics.
>
> **Guarantee statement:** absent collusion of all participating parties **and** compromise of their independent anchors, unilateral omission or modification is detectable. Missing counterparty records are themselves evidence.

Cross-domain instantiations (informative): trader↔broker (VCP), hospital↔AI vendor (MAP), agency↔independent auditor (PAP), OEM↔fleet operator (DVP), creator↔platform (CAP).

---

### CH-09 — SCITT / COSE Alignment and Evidence Packaging

**Class:** Normative-compatible (opt-in; MUST-level when claimed)
**Sections:** §11 (currently non-normative) → partial promotion; new fields in AnchorRecord
**Aligns with:** VCP v1.2 Annex §5; draft-kamimura-vap-framework; draft-ietf-scitt-architecture; draft-ietf-cose-merkle-tree-proofs

**New text:**

> Implementations MAY register signed statements (e.g., AnchorRecords) with a SCITT-conformant transparency service and attach **COSE Receipts** as additional verifiability evidence. When SCITT alignment is claimed: receipt format MUST conform to draft-ietf-cose-merkle-tree-proofs; the transparency-service identity MUST be recorded in the AnchorRecord (`anchor_target.type = TRANSPARENCY_SERVICE`); VAP-native verification MUST remain possible without the transparency service (SCITT is additive, not substitutive).
>
> Profiles SHOULD define an **Evidence Pack**: a portable, self-verifying bundle (events + audit paths + AnchorRecords + receipts + public keys + policy documents) sufficient for an offline third party to execute the standard verification procedure. The Evidence Pack format is profile-defined in v1.2; a common container format is a candidate for VAP v1.3.

---

### CH-10 — Cryptographic Algorithm Lifecycle Update

**Class:** Normative (status change)
**Sections:** §4.1.5, §6.1, §6.2
**Aligns with:** VCP v1.2 §1.5.1, Appendix E, Annex §4

| Algorithm | v1.1 status | **v1.2 status** | Notes |
|---|---|---|---|
| Ed25519 | DEFAULT | DEFAULT | unchanged |
| ECDSA secp256k1 | SUPPORTED | SUPPORTED | unchanged |
| RSA-2048 | (unlisted/legacy) | **DEPRECATED — removal planned in VAP v2.0** | aligns with VCP deprecation timeline |
| DILITHIUM2 | FUTURE | **EXPERIMENTAL** — rename to **ML-DSA (FIPS 204)** | testing & hybrid deployments; not a certification requirement |
| FALCON-512 | FUTURE | **EXPERIMENTAL** — rename to **FN-DSA (FIPS 206, draft)** | same |

> **Hybrid dual-signature schema** (classical + PQC: `pqc_signature`, `pqc_sign_algo` fields on Security object and AnchorRecord) is adopted framework-wide as the RECOMMENDED transition mechanism. Crypto-agility requirement (algorithm identification fields, migration capability) is unchanged. The §6.2.2 migration path table is updated: Phase 2 (Hybrid) is now **available**, not future.

---

### CH-11 — Version Compatibility Management (3-tier model)

**Class:** Informative
**Sections:** new section; replaces implicit version coupling
**Aligns with:** VCP v1.2 §10.5

**Decision (recorded):** VAP and profile version numbers are **independently assigned**. Apparent synchrony (VAP v1.2 ⇔ VCP v1.2) is coincidental and MUST NOT be relied upon. Compatibility is managed through three artifacts:

1. **VAP Version** — framework requirement set;
2. **Profile Version** — each profile declares the minimum VAP version it conforms to (`vap_version` field, already present in the common event model);
3. **Compatibility Matrix** — maintained by VSO per release:

| Profile / version | VAP v1.1 | VAP v1.2 |
|---|---|---|
| VCP v1.0 | Partial (pre-dates policy ID) | Partial (legacy; certification expired per VCP grace deadlines) |
| VCP v1.1 | **Non-conformant on INT-003/004 as written** (resolved by CH-01) | **Full** |
| VCP v1.2 (RC1) | — | **Full** (reference profile) |
| CAP v1.0 | Mapping required | Mapping required (Annex B) |
| CPP v1.0 | Mapping required | Mapping required (Annex B) |
| DVP / MAP / PAP / EIP / AAP / IAP | — | MUST target VAP v1.2 at first release |

Data-format rule: v1.2 verifiers MUST accept all v1.1 events; v1.1 verifiers encountering v1.2-only constructs (ERASURE, policy object, PQC fields, SCITT receipts) MUST fail gracefully (ignore-unknown), not reject.

---

### CH-12 — Profile Registry, Roadmap, and Editorial Updates

**Class:** Informative
**Sections:** §4.5.2, §10.2, §2.2

- Registry: VCP → v1.2 RC1; **CAP v1.0 (Content/Creative)** and **CPP v1.0 (Capture Provenance)** added as Released; **IAP (Industry Accountability Profile)** added as Announced; DVP/MAP/PAP/EIP/AAP remain Planned.
- Domain scope: §2 currently enumerates five mandatory domains; v1.2 adds Content/Creative (IP integrity, misinformation) and Capture Provenance (evidence integrity) as **profile-served domains**, with a note distinguishing "mandatory application domains" (irreversible-harm test) from "served domains".
- Roadmap actuals: IETF Internet-Draft **submitted** (draft-kamimura-vap-framework-00, January 2026; draft-kamimura-scitt-vcp); ITU-T SG17 chair-level dialogue completed (scope-boundary alignment, no-duplication principle); ISO/TC 68 and ISO/IEC JTC 1/SC 42 engagement remains Planned 2026–2027.
- References: add draft-ietf-scitt-architecture, draft-ietf-cose-merkle-tree-proofs, FIPS 204, FIPS 206 (draft), RFC 9162.

---

## 5. Migration and Grace Period

| Requirement | Who | Grace period | Hard deadline |
|---|---|---|---|
| Declare sequence-mechanism matrix per conformance level (CH-01) | All profiles | 3 months from VAP v1.2 publication | P+3m |
| External anchoring at all conformance levels (CH-02) | Implementations claiming VAP-Core | 6 months | P+6m |
| Anchor continuity plan documented (CH-03) | All implementations | 6 months | P+6m |
| Policy object in events (CH-07) | All implementations | 3 months | P+3m |
| ERASURE / RECOVERY constraints (CH-05/06) | MUST upon first use of the capability | immediate on use | — |
| XREF / SCITT / PQC hybrid (CH-08/09/10) | Opt-in | — | — |

After the hard deadlines, VAP v1.1-only conformance claims are not eligible for VAP v1.2 certification marks. Event-data interoperability is unaffected.

**Profile obligations:** Each released profile (VCP, CAP, CPP) republishes a one-page **VAP v1.2 Conformance Mapping** (template: Annex A/B tables). VCP v1.2 RC1 already satisfies CH-01…CH-07 substantively; its mapping is editorial.

---

## 6. Compatibility Matrix (data & verification)

| Producer | Consumer / Verifier | Result |
|---|---|---|
| VAP v1.1 events | v1.2 verifier | **Full** — all v1.1 events verify |
| VAP v1.2 events (no opt-ins) | v1.1 verifier | **Full** |
| VAP v1.2 events (ERASURE / policy / PQC / receipts) | v1.1 verifier | **Partial** — unknown constructs ignored gracefully; core integrity still verifiable |
| v1.1 anchors & proofs | v1.2 verifier | **Full** |
| v1.2 SCITT receipts | v1.1 verifier | Not verifiable (additive evidence only; VAP-native path unaffected) |

Wire-format breaking changes: **none**.

---

## 7. Legal Scope and Non-Guarantee Statement

The following statement is adopted into VAP v1.2 (normative) and RECOMMENDED verbatim for all profiles:

> VAP and its domain profiles define mechanisms for producing **cryptographically verifiable evidence** of AI system decisions. Conformance to VAP or any profile: (a) does **not** constitute compliance with the EU AI Act, GDPR, MiFID II/III, CAT Rule 613, NIS2, FDA SaMD guidance, or any other law or regulation; (b) does **not** constitute a legal determination that any technical mechanism (including crypto-shredding) satisfies a specific legal obligation; (c) does **not** warrant the correctness, fairness, or safety of the underlying AI decisions — only the integrity, completeness (at anchor granularity), and attributability of their records. VAP generates evidence; competent authorities and courts evaluate it.

This mirrors the honest-scoping discipline of VCP v1.2 (ERASURE legal note; Silver-tier assurance disclosure) and protects the framework from over-claim when presented to regulators, CABs, and standards bodies.

---

## 8. Proposed Text Diffs (key normative passages)

### 8.1 §4.1.2 Integrity Layer requirements table

```diff
- INT-003 | Events MUST be linked via cryptographic hash (SHA-256 or stronger) | MUST
- INT-004 | Hash chain MUST maintain continuity                                | MUST
+ INT-003 | Every event MUST carry an EventHash over its RFC 8785 canonical
+           form (SHA-256 or stronger)                                         | MUST
+ INT-004 | Event sequencing MUST be cryptographically verifiable via a
+           profile-defined combination of PrevHash, Merkle inclusion proofs,
+           external anchoring, or equivalent mechanisms; profiles MUST
+           specify mandatory mechanisms per conformance level               | MUST
+ INT-004a| PrevHash (hash chain) is an OPTIONAL local mechanism; profiles
+           MAY require it                                                    | OPTIONAL
  INT-005 | Non-repudiation SHOULD be achieved via digital signatures or
            TEE signatures (unchanged in v1.2 — elevation deferred,
            see Annex C.2)                                                   | SHOULD
- INT-006 | Periodic Merkle Tree anchoring SHOULD be performed                 | SHOULD
+ INT-006 | Merkle batching and external anchoring of signed roots is
+           REQUIRED at all conformance levels; frequency/target/proof depth
+           delegated to profiles                                             | MUST
+ INT-007 | Anchor continuity plan (fallback target, failover, local
+           AnchorRecord retention)                                           | MUST
+ INT-008 | Completeness invariant: anchored batches MUST be third-party
+           verifiable as complete (count + first/last IDs + policy bound)   | MUST
+ INT-009 | Recovery operations MUST be bounded, recorded, and authorized    | MUST (when used)
```
### 8.2 §7.1 Common Event Structure

```diff
  {
    "vap_version": "1.2",
    "profile": { "id": "string", "version": "string" },
+   "policy": {
+     "policy_id": "string",
+     "conformance_level": "enum",
+     "vap_conformance": "enum",
+     "registration_policy": { ... },
+     "verification_depth": { ... }
+   },
    "header": { ... },
    "provenance": { ... },
    "accountability": { ... },
    "domain_payload": { ... },
    "security": {
      "event_hash": "string",
-     "prev_hash": "string",
+     "prev_hash": "string",            // OPTIONAL (see INT-004a)
      "hash_algo": "enum",
      "signature": "string",
      "sign_algo": "enum",
+     "pqc_signature": "string",        // OPTIONAL (hybrid)
+     "pqc_sign_algo": "enum",          // OPTIONAL
+     "merkle_root": "string",          // REQUIRED at batch close
+     "merkle_index": "int32",          // REQUIRED at batch close
+     "anchor_reference": "string",     // REQUIRED at batch close
      "signer_id": "string"
    }
  }
```

### 8.3 §8 Conformance Levels

```diff
  VAP-Core     | Minimum conformance  | Integrity Layer mandatory requirements
-                                       only
+                                       only — including INT-006 external
+                                       anchoring and INT-007 continuity plan
  VAP-Standard | Standard conformance | Core + Provenance + Traceability
  VAP-Full     | Full conformance     | Standard + Accountability + Profile
                                        Extensions + (when used) ERASURE,
                                        RECOVERY, XREF conformance
```

---

## Annex A: Mapping to VCP v1.1 / v1.2 (RC1)

| VAP v1.2 change | VCP source | VCP status |
|---|---|---|
| CH-01 sequence verifiability | v1.1 §6.0 three-layer architecture; §6.4.1 PrevHash OPTIONAL | Implemented |
| CH-02 anchor MUST all levels | v1.1 §6.3.3 (all tiers REQUIRED; Silver lightweight options) | Implemented |
| CH-03 anchor continuity | v1.1 §6.3.3 unavailability handling; v1.2 Annex §7 | Implemented (v1.2 cert requirement) |
| CH-04 completeness | v1.1 §1.1 Completeness Guarantees; Silver scope note §2.2.3 | Implemented |
| CH-05 ERASURE | v1.2 §3.2.2 / Annex §3 | Implemented |
| CH-06 RECOVERY constraints | v1.2 Annex §1 (SKIP/REBUILD/MERGE/CHECKPOINT bounds, Emergency Override) | Implemented |
| CH-07 policy identification | v1.1 §5.5 (PolicyID, ConformanceTier, VerificationDepth, reverse-domain naming) | Implemented |
| CH-08 XREF | v1.1 §5.6; v1.2 Annex §9 multi-actor | Implemented |
| CH-09 SCITT/COSE | v1.2 Annex §5; draft-kamimura-scitt-vcp | Implemented (opt-in) |
| CH-10 PQC EXPERIMENTAL | v1.2 §1.5.1, Appendix E, Annex §4 | Implemented |
| CH-11 compatibility matrix | v1.2 §10.5 | Implemented |

**Conclusion:** VCP v1.2 RC1 is the **reference implementation profile** of VAP v1.2; no VCP changes are required by this proposal. VCP's VAP v1.2 Conformance Mapping is editorial.

---

## Annex B: Mapping to CAP v1.0 / CPP v1.0 / future DVP, MAP, PAP, EIP, AAP

### B.1 Released profiles — mapping obligations

| VAP v1.2 requirement | CAP v1.0 (Content/Creative) | CPP v1.0 (Capture) |
|---|---|---|
| CH-01 mechanism matrix | Declare per level; content pipelines are batch-oriented → Merkle+anchor primary, PrevHash optional | Capture devices may favor PrevHash (sequential capture) + periodic anchor |
| CH-02 anchoring | Map ingestion/training/generation/export checkpoints to anchor batches | Map capture sessions to anchor batches |
| CH-05 ERASURE | Creator data / opt-out erasure; retention_exemption for IP-dispute holds | Subject erasure vs. evidentiary preservation tension — retention_exemption critical |
| CH-06 RECOVERY | Pipeline replay bounds | Device offline gap-fill bounds |
| CH-08 XREF | creator ↔ platform dual logging | capture device ↔ verification service |
| Legal non-guarantee (§7) | Adopt verbatim (copyright/IP determinations are out of scope) | Adopt verbatim (evidentiary admissibility is court-determined) |

VSO action: request CAP/CPP working groups to publish v1.2 conformance mappings within the §5 grace window.

### B.2 Future profiles — design constraints inherited at birth

DVP, MAP, PAP, EIP, AAP, IAP MUST target VAP v1.2 at first release. Notable per-domain consequences:

- **DVP/AAP:** real-time tamper detection expectations → profile SHOULD make PrevHash MUST at upper levels (CH-01 explicitly permits this); RECOVERY bounds map to post-crash data gap-fill.
- **MAP:** ERASURE legal clause interacts with medical-record retention statutes — `retention_exemption` REQUIRED semantics to be specified at profile level; XREF instantiation: provider ↔ AI vendor.
- **PAP:** completeness invariant is the load-bearing guarantee (proving a decision was *not* made/recorded is central to appeals); OBSERVER role (regulator read-only) from CH-08 is the default deployment.
- **EIP:** anchor continuity (CH-03) must account for air-gapped/segmented networks — profile-defined offline anchoring queue semantics.

---

## Annex C: Deferred Items

### C.1 Constructs pending VCP v1.2 final publication

The following constructs are referenced in VCP v1.2 **working-draft material** but are **not present in VCP v1.2 RC1 (2026-05-31)**, which is the normative baseline for this proposal: *Regulatory Profile, ClockEvidence, ChangeEvent, PTCSnapshot, PMM Manifest, Erasure Certificate v2, Regulatory Evidence Bundle.*

Disposition: **deferred**. If these constructs are published in VCP v1.2 final or a subsequent VCP revision, VSO will assess framework-level generalization in **VSO-VAP-CHANGE-002** (candidate scope: evidence bundling — partially anticipated by CH-09's Evidence Pack; clock evidence — anticipated by the existing ClockSyncStatus generalization; change/configuration events — candidate Provenance Layer extension). No CH-xx in this proposal depends on the deferred items.

### C.2 INT-005 elevation (non-repudiation: SHOULD → MUST)

Elevation of INT-005 (digital/TEE signatures for non-repudiation) from SHOULD to MUST was considered and **deferred to VSO-VAP-CHANGE-002**. Rationale: (a) CHANGE-001 is scoped to repairing VAP/VCP normative misalignment, and INT-005 elevation is not required for that repair; (b) the binding framework-level integrity guarantee at all conformance levels is already provided by CH-02 (mandatory external anchoring of signed Merkle roots); (c) VCP independently requires per-event signatures at all tiers, so the flagship profile's guarantee is unaffected by deferral; (d) framework-wide elevation requires an impact assessment for TEE-only and resource-constrained device classes anticipated in future DVP/CPP/AAP profiles.

---

## Annex D: Decision Log

| ID | Decision | Resolution |
|---|---|---|
| D-a | Anchor MUST scope | **All conformance levels**, incl. VAP-Core; frequency/method/assurance depth delegated to profiles/levels |
| D-b | ERASURE legal posture | Framework-level capability; explicit non-determination clause ("may support erasure obligations, does not itself determine legal compliance") |
| D-c | Version numbering | **Independent assignment**; 3-tier management (VAP Version / Profile Version / Compatibility Matrix); apparent synchrony non-normative |
| D-d | Hash chain posture | "Hash Chain MUST" abstracted to "Cryptographic Sequence Verifiability MUST"; mechanism choice delegated; profiles may re-mandate PrevHash |
| D-e | INT-005 (signature) elevation | **Deferred** to VSO-VAP-CHANGE-002 (Annex C.2) — keeps CHANGE-001 scoped to misalignment repair; anchoring of signed Merkle roots (CH-02) carries the framework-level non-repudiation burden in the interim |

---

## Process

Per VAP §10.3 change management: this change proposal → 30-day public review → Technical Committee deliberation → two-thirds vote → release as normative annex of VAP Framework Specification v1.2.

---

*VeritasChain Standards Organization — "Verify, Don't Trust"*
*End of VSO-VAP-CHANGE-001*
