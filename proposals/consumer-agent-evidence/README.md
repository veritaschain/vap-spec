# Consumer-agent commercial relationships and action evidence

**Status: informative design discussion; unadopted. Reviewed: 6 November 2026 (JST).**

[日本語](README-ja.md) · [Source ledger](SOURCES.md)

**Source follow-up: 10 November 2026.** The [dated monitoring record](SOURCES.md#monitoring-follow-up-2026-11-10)
adds the official 6 November package text and the supplied 9–10 November monitoring
window. It distinguishes a guideline implementation target and deletion-policy
requests from adopted obligations. The design review below remains dated 6 November.

This VSO proposal describes evidence for reviewing a consumer-facing agent's
declared mandate, commercial relationships, recommendation context, authorized
actions and data lifecycle. The source ledger separates Japan's cyber policy
decision, budget decision,
existing data-management guidance and an individual expert's consumer-agent
discussion, preserving the dated verification status of each. The design below is VSO's
inference from those concerns, not a requirement in the cited materials.

This document introduces no adopted profile, normative field, wire format,
certification result or product capability. No consumer-agent implementation,
new acceptance test, AILEX deployment inspection or independent assessment was
performed for it. Existing experiments remain bounded research references.

## 1. The review question

An evidence package should help a reviewer compare the task a user delegated
with the configuration, declared commercial relationships, material presented
to the user and external action actually observed. It should also show which
questions remain unanswered. A valid signature can authenticate a declaration
under a trusted key; it cannot establish that the agent acted in the user's
best interests or that every commercial relationship was declared.

Record the applicable tenant, run/request identifier, evidence issuer, key and
role trust basis, policy versions, observation interval and collection boundary.
Preserve source attribution and distinguish asserted facts from observations.
Do not ask the model to generate a retrospective explanation and treat that
explanation as an execution record or access to private internal reasoning.

## 2. Candidate evidence bindings

The groups below are application-design candidates. Names are descriptive and
are not additions to a VAP, DAP or LAP schema.

| Review subject | Evidence to associate | Interpretation boundary |
|---|---|---|
| Principal and mandate | Represented user or organization; provider and operator roles; user task and constraints; delegation scope, expiry and approval; identity/key trust basis | A declared principal does not prove whose interests the behavior actually served. A historical grant does not establish current authority. |
| Commercial relationships | Declaring party, sponsor/merchant/affiliate relationship, relevant fee or commission policy, source version, effective period and scope | An absent declaration means unresolved coverage, not absence of a relationship. A signature does not establish truth or impartiality. |
| Objective and configuration | User constraints and versioned selection/ranking policy; effective configuration observations; changes and their ordering relative to the decision | Declared objectives or a configuration digest do not prove actual model optimization, fairness or that the configuration was enforced. |
| Inputs and candidate coverage | Material actually supplied, retrieval/source versions and times, returned candidate set, collection boundary and recorded exclusions | A captured result set is not the whole market. Inclusion proofs do not establish that unreturned or uncollected options were considered. |
| Disclosure and approval | Exact disclosure version/content reference; generation, rendering or delivery observations; acknowledgment; approval tied to the action | Generated, displayed, delivered and acknowledged are separate stages. None alone establishes comprehension or valid consent. |
| Action and outcome | Exact destination/account/tenant and object or item/amount; authority decision; attempted request; denial/dispatch; provider receipt; terminal result or reconciliation | Request, acceptance and completed effect differ. An authentic receipt does not resolve authorization, fairness or unobserved bypasses. |
| Retention and deletion | Data class/purpose, copy locations and controllers, dated terms, starting event/deadline, exceptions, request, ACK, scoped completion statement and separate observations | An elapsed deadline or disabled-training setting does not prove deletion. An active-store claim does not cover backups or downstream copies. |
| Coverage and custody | Observation points, exclusions, collector health, record availability, trust inputs and independently controlled observations where available | Different keys/processes under one operator do not establish independence. Later collection does not establish collection before an action. |

The issuer's relationship declaration and the reviewer’s assessment of that
declaration are different records. An operator can omit a relationship while
producing internally consistent signed logs. Cross-checks, contracts and
appropriately authorized independent evidence may be needed; cryptography
does not discover the missing relationship by itself.

An external action should be compared against the actual approved parameters.
Approval for a provider name is insufficient to establish approval for every
destination account, payload, merchant, price or permission. If configuration
or authority changes between review and execution, a recorded earlier check
alone does not close the check/use gap. Runtime enforcement needs its own
identified mechanism and evaluation.

## 3. Keep conclusions separate

A future assessor should report the evidence and unresolved issues for each
dimension, without generating an overall consumer-safe or conflict-free badge.

| Dimension | Bounded conclusion to examine |
|---|---|
| Integrity and attribution | Whether the supplied bytes/proofs verify under the stated trust assumptions |
| Scoped coverage | Whether declared observation and evidence obligations are supported, contradicted or unresolved |
| Commercial declarations | Who declared which relationship, for what scope and time; missing or conflicting information |
| Disclosure | The furthest supported observation stage, with any gaps |
| Authorization match | Whether applicable authority covers the exact observed action and relevant time |
| Action outcome | What was attempted, accepted or completed, and what remains unresolved |
| Retention and deletion | Applicable stated conditions and separately supported deletion steps, locations and limitations |

Unknown overall coverage does not erase a known contradiction. For example,
an observed action outside a recorded approval remains a mismatch even if the
full candidate inventory is unavailable. Conversely, an unavailable record is
not automatically proof that an action never occurred.

## 4. Data lifecycle and AILEX review priorities

The following is a proposed review sequence for AILEX or another legal AI
service, not a statement about its current production implementation. The
[LAP introduction](../legal-ai-profile/README.md#ailex-relationship-disclosure)
discloses the common representative and commercial relationship with VSO.

1. **Inventory data and recipients.** Identify case materials, chats, attachments,
   generated documents, retrieval/vector stores, caches, operational logs and
   backups. Map service/provider/account/tenant, subcontractors, purpose,
   responsible owner and applicable retention terms. Missing information stays
   visible rather than being assigned an invented default period.
2. **Bind lifecycle rules to the data.** Record the basis, effective version,
   starting event and deadline for each class and location. Keep exceptions or
   preservation holds separately attributable, with review conditions. Resolve
   conflicting statements explicitly; do not assume the newest text governs
   every previously created copy. Determine actual legal/contractual periods
   separately from this note.
3. **Track deletion by scope.** Distinguish request, receipt, scoped provider
   assertion and observation. Preserve uncovered backups, replicas, caches and
   downstream recipients as open questions. After restoration or recreation,
   identify the new copy and applicable deletion follow-up. Later presence does
   not by itself prove an earlier scoped deletion statement was false.
4. **Make answers reviewable.** Associate the sources actually supplied,
   available model/configuration identity, declared relationships, professional
   review and exact approved action. Do not invent unavailable provider data
   or represent a citation as proof that the cited content is correct.

Keep confidential payloads in access-controlled storage with an appropriate
retention policy. Public proofs should contain only appropriately minimized
material. A hash is neither encryption nor automatic anonymization; predictable
text can be guessed from a digest. A commitment design needs review of content
entropy, disclosure risk, key custody and the verification needed later.

Preserving a commitment while deleting or making a payload inaccessible changes
which checks a reviewer can perform. Record that limitation. Key destruction
does not remove copies already disclosed, plaintext elsewhere or unknown key
backups. A signed deletion receipt records an attributed assertion, not universal
physical erasure or a legal-compliance conclusion. An audit log is itself a data
asset with access and retention needs; recording every raw conversation forever
is not the objective of this proposal.

## 5. Proposed review cases — not executed

These cases define questions for a future evidence contract. They are not
fixtures, passing tests or acceptance results for an existing service.

| Case | Supplied situation | Expected distinction for a future review |
|---|---|---|
| CA-01 | Signed recommendation, no commercial-relationship evidence | Integrity may verify; commercial-declaration coverage remains unresolved. |
| CA-02 | Observed sponsor-priority configuration conflicts with a recorded user constraint | Preserve the discrepancy even when all supplied signatures verify; causation and legal significance require separate evaluation. |
| CA-03 | All captured candidates verify, but the source inventory has no closure evidence | Preserve the captured set's integrity and unresolved candidate/market coverage separately. |
| CA-04 | Approved merchant/item/amount differs from the observed request | Do not treat the old approval as authorization of the changed action. |
| CA-05 | Disclosure was generated, with no rendering/delivery observation | Do not promote generation to delivery; acknowledgment would still not establish understanding. |
| CA-06 | Previously valid delegation, no sufficiently current status evidence | Preserve historical evidence and unresolved authority at execution; absence of a status record does not prove revocation. |
| CA-07 | Retention deadline passed; only an ACK exists; backups are uncovered | Deadline state, completion evidence and copy coverage remain separate. |
| CA-08 | Matching data appears after a scoped deletion claim | Preserve the claim and later observation; investigate survival, restoration or recreation without silently rewriting history. |

## 6. Relationship to current repository work

The reviewed VAP baseline was
[`ce9c968951c0c92a3b5cf9d5a9a587506f8a700d`](https://github.com/veritaschain/vap-spec/tree/ce9c968951c0c92a3b5cf9d5a9a587506f8a700d).
References below describe existing abstractions or limited experiments, not
implementation of the new consumer-agent bindings.

| Reference | Useful basis and remaining boundary |
|---|---|
| [VAP v1.2 Draft 3](../../spec/v1.2/VAP_Framework_Specification.md), §§4.2–4.4 | Actor, inputs, context, action, outcome, delegation and oversight records. No adopted commercial-incentive or full candidate-inventory schema is defined by this note. |
| VAP §1.6, INT-008 / §11.1 | Integrity and post-anchor omission detection within the declared batch scope do not establish safety, fairness, legal compliance or collection of every relevant event. |
| [DAP/SMP publication status](../../README.md#relationship) and [LAP proposal](../legal-ai-profile/README.md) | DAP/SMP Working Draft texts are not public at review; LAP is a proposed profile. This note does not assume a published DAP schema or make LAP a registered profile. |
| [Declared-scope precommit proposal](../declared-scope-precommit/README.md) | Unadopted work separating expected, observed and delivered evidence; useful for specifying source boundaries and unresolved coverage. |
| [Incident evidence bindings](../incident-evidence-bindings/README.md) and [retention adapter](../../experiments/incident-retention-adapter/README.md) | Separate transfer permission, terms, deadlines and erasure evidence. The adapter evaluates synthetic supplied records; it does not inspect or delete AILEX/vendor data. |
| [Payment collector pilot](../../experiments/payment-collector-pilot/README.md) | Exact selected evidence, custody observations and financial outcome are separated. The same-operator synthetic pilot establishes neither independent custody nor this consumer-agent workflow. |

## 7. Publication and follow-up

Use the [source ledger](SOURCES.md) for claim status and unresolved primary
documents. This review does not establish a new AI-specific obligation for
AILEX, government endorsement of VAP/VCP, procurement eligibility or a market
requirement to purchase certification. It is not a comprehensive survey of
every agency or applicable law.

The 10 November source follow-up supplies the official cyber-package text.
Further review should track the PPC consultation result and final amendment,
deletion-policy proposals and subsequent Consumer Commission minutes, and
separately review an authorized deployed data path before claiming a product
improvement. A future pilot would need an explicit evidence contract,
privacy/trust boundaries and
tests of the cases above. No scheduled monitoring job is created here.
