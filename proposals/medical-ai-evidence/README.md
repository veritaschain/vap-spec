# Medical AI advice and medication safety: evidence-design case notes

**Status:** Informative discussion proposal, not adopted.  
**Date:** 2026-10-31 (JST).  
**Target:** VAP cross-domain evidence design and potential future MAP (Medical / Healthcare AI Profile) work.  
**Normative effect:** None. No new event codes, schema fields, profile requirements, conformance claims, or certification criteria.  
**License:** CC BY 4.0 International.

## Purpose and provenance of this note

This note translates two October 2026 medical-AI reports into testable, **proposed** evidence-capture and verification questions. It is not a clinical assessment, legal finding, independent benchmark reproduction, or validation that VAP would have prevented an injury. Sources are attributed; an allegation, reported observation, benchmark classification, and design inference are different things.

VAP provides post-hoc tamper-evidence and scoped verification **for records that an implementation actually collects**. It does not establish clinical correctness, medically causal harm, legal liability, absence of unobserved events, or guaranteed replication of a model response. An inclusion proof alone does not establish collection completeness; INT-008 concerns the declared anchored-batch scope.

## Case A: Wan family lawsuit concerning epilepsy medication

- **2026-10-27:** Plaintiffs' counsel reports filing in San Francisco Superior Court concerning ChatGPT medication advice and Bowen Wan's death in February 2026.
- **Evidence status:** Medication advice, concealment from a physician and causation remain **plaintiffs' allegations**. The complaint reproduces conversations; this review does not establish missing or altered logs.
- **Potential evidence-design questions:** Can investigators identify exactly what the user submitted; what conversation history or summary was presented to a particular invocation; which model/configuration and safety-policy versions were *observable*; what safety check was executed, failed, skipped or unavailable; what advice and warnings were actually shown; and whether physician-referral language changed across interactions?
- **Limitations:** Provider-internal prompts, model weights, moderation state and hidden context may not be available to an independent integrator. Do not label an inferred field as observed. A protected transcript is evidence of content, not proof of medical causation.

Sources reviewed on 2026-11-05: [plaintiffs' counsel's case page](https://schenklawfirm.com/press/wan/); [public complaint copy](https://schenklawfirm.com/press/wan/complaint.pdf). Earlier reporting, retained but not rechecked in this review: [TechCrunch, 2026-10-27](https://techcrunch.com/2026/10/27/parents-sue-openai-alleging-gpt-4o-coached-their-daughter-off-seizure-medication/); [New York Times, 2026-10-27](https://www.nytimes.com/2026/10/27/well/ai-chatgpt-medication-epilepsy-death.html).

### Source review — 2026-11-05 JST

This is a primary-source recheck of the existing case, not a new incident. The complaint was obtained from plaintiffs' counsel, not a court docket. Paragraphs and printed pages below refer to that 98-page copy.

| Claim | Source locator | What the source supports |
| --- | --- | --- |
| Filing | Counsel's case page | Reports 27 October 2026; its case-number field remains pending. |
| Taper and concealment | Complaint ¶6, p.3; ¶13, p.5 | Alleges an approximately 25-day taper and advice to conceal medication changes from a physician. |
| Death and concentration | Complaint ¶¶223–225, pp.65–66 | Alleges death around 12 February 2026 and 0.64 µg/mL, approximately one-fifth of the stated therapeutic **lower bound** of 3 µg/mL. |
| Conversation provenance | Complaint footnote 1, pp.3–4 | Describes original English/Chinese logs, translations and retained native export files. |
| Model attribution | Complaint ¶129, p.33 | Alleges GPT-4o use; says specific model versions remain to be established through discovery. |

**Review limits:** The court docket, original account exports, medical records and provider-internal state were not independently inspected. These checks establish what the public complaint says, not the truth or completeness of each allegation or medical/legal causation. The supplied BMJ URL could not be retrieved and is not a checked source.

**Remaining gates:** Only Case A's public-source traceability was advanced. Case B's Doximity claims and denominators, and the legal sources below, were not rechecked in this update. Healthcare/privacy review, authenticated independent reproduction and formal MAP change control remain open. No new implementation or clinical validation is established.

**Test status:** This documentation review did not execute tests. The 18-method result in [the test record](tests/README.md) is historical internal execution, not a new result or independent reproduction.

## Case B: Doximity medication-dosing benchmark

- **2026-10-29:** Doximity published a medication-dose evaluation of nine LLMs using more than 8,000 clinical questions; its public report describes a dangerous-error frequency of approximately 20 per 1,000 answers and reports 3.4% of observed errors as potentially lethal.
- **Evidence status:** These are **benchmark classifications**, not observed clinical deaths or a patient mortality rate. Question count, answer count and dose-data-item count have different denominators. The study was published in connection with a Doximity product announcement; independent reproduction and clinical outcome validation are not established here.
- **Potential evidence-design questions:** Did a medication dose require age, weight, renal function, route, indication, formulation and contraindication context? Which context was supplied versus missing? Which dose-reference version was used? Did a deterministic checker run, warn, fail, time out or not run? Was clinician review requested or obtained? What was displayed to the user?
- **Limitations:** Cryptographic provenance may support later review of inputs, decisions and reference versions, but does not itself check that a dose is correct.

Sources: [Doximity official blog, 2026-10-29](https://blog.doximity.com/articles/over-2-of-llm-doses-are-wrong-some-can-be-lethal); [Healthcare Dive](https://www.healthcaredive.com/news/popular-ai-models-get-medication-doses-wrong-some-dangerously-doximity/873207/).

## Proposed observational binding matrix (not a wire schema)

| Evidence question | Proposed binding | Boundaries / reviewer cautions |
| --- | --- | --- |
| What entered the model call? | Request ID; exact observed input and effective context commitments; redaction status; missing-context declaration | User-entered text may differ from prompt assembled by the application; hidden provider state may be inaccessible |
| What ran? | Provider/model identifier as actually disclosed; invocation time; configuration and prompt version when available | Version names do not prove weights or reproducibility; distinguish asserted from externally observed facts |
| What safety checks happened? | Check type, rule/data version, stage, result and execution status | Preserve `passed`, `warning`, `failed`, `not_run`, `unknown` as separate states |
| What did the user see? | Final visible answer, warnings, timing and transformation/citation lineage | A raw model completion is not necessarily the final UI output |
| Which dose reference was used? | Reference identifier/version, retrieval result, relevant patient-condition presence | Source/version evidence does not establish clinical correctness |
| Who reviewed or intervened? | Reviewer role, decision/referral/override evidence and scope | A logged human action is not a clinical approval without appropriate authorization |
| What was collected, and what was not? | Declared collector boundary, outage, omitted/unknown intervals; anchored-batch manifest and proof | INT-008 addresses post-anchor omission within the declared scope, not unobserved events before collection |
| Can an exported excerpt be traced? | Original transcript commitment; export, translation, redaction and quotation derivations | Preserve source language and mark translations/interpretations as derivatives |

Protect patient information with purpose limitation, access controls, retention policy and redaction / selective disclosure. An external anchor should normally carry commitments, not patient medical plaintext. Keep event, collection, provider-claimed and anchoring timestamps separate.

## Design cases and executed synthetic checks

The nine design candidates below now have an executed **illustrative application-level classification suite**, with additional missing-input, malformed-input and local commitment checks. See the [test scope and recorded local execution](tests/README.md). Execution of those bounded checks does not establish the broader acceptance properties below: actual VAP verification, authenticated manifests, external anchoring, clinical correctness and provider integration remain unverified. No clinical real-world data is requested or implied.

1. **CHECK_NOT_RUN:** A dosage recommendation is emitted when the checker is not run. The record must not claim a passed check.
2. **CHECK_TIMEOUT:** The reference checker times out; a later batch verifies while safety-verification outcome remains unknown.
3. **DISPLAY_DIVERGENCE:** The model draft includes a warning that the final UI suppresses; source and displayed-output commitments must not be conflated.
4. **MISSING_PATIENT_CONTEXT:** Renal-function data was never supplied; distinguish missing input from a collector outage.
5. **POST_ANCHOR_OMISSION:** An anchored batch declares N events but a submitted evidence package contains fewer; evaluate per INT-008 with the declared scope and commitments.
6. **PRE_COLLECTION_GAP:** A separate channel is outside the collector; a passing anchored-batch proof must not support a global-completeness claim.
7. **TRANSLATION_DERIVATION:** Verify an exported quotation against an original-language transcript without treating a translation as original.
8. **PROVIDER_STATE_UNOBSERVABLE:** The provider does not disclose safety-filter state; verifier must not substitute a guess.
9. **MODEL_REPLAY_DIVERGENCE:** A later invocation differs from historical output; separate original evidence verification from a nondeterministic replay.

## Regulatory context (informative, not a compliance assertion)

- EU AI Act Articles **12, 19 and 26** concern logging, provider retention and deployer obligations **when the relevant high-risk classification and provisions apply**. Article **50** addresses transparency/disclosure and is not a requirement for cryptographic dosage audit logs. The Act does not prescribe adoption of VAP or a Merkle tree. Check the applicable legal text and phased dates at the time of use.
- FDA Clinical Decision Support guidance involves the software's **intended use and functionality**; not every general-purpose LLM interaction is a regulated medical device, and exclusion from a non-device CDS category does not by itself decide a particular marketing-authorization path.
- Preserve jurisdictional and factual uncertainty; nothing in these two cases establishes an EU AI Act violation by an identified party.

Sources: [EU AI Act Article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6), [Article 12](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-12), [Article 19](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-19), [Article 26](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-26), [Article 50](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-50), [FDA CDS guidance](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/clinical-decision-support-software).

## Decision gates before MAP integration

1. Verify status and scope against the **current VAP v1.2 normative registry**; MAP is a working draft, not a deployed or independently validated implementation.
2. Review collected-vs-inferred field terminology and the privacy threat model with healthcare and legal specialists.
3. Publish synthetic fixtures and expected outcomes; test an independent verifier on bounded omission, unknown observation and display divergence.
4. Keep any proposed MAP vocabulary in a separately reviewed change-control document. Adoption requires explicit governance and versioning; **merging this note does not adopt it**.

## Maturity and assurance disclosure

As of the published VAP repository disclosure of 2026-10-25: **zero external implementations** of VAP and its profiles and **zero Evidence Packs accepted in proceedings**. No authenticated independent medical-system integration or clinical effectiveness assessment is established by this note. Commercial contract/customer figures are not asserted: the repository's 2026-10-24 correction withdrew an unsubstantiated prior claim.

VAP is maintained by **VeritasChain Standards Organization (VSO)**, whose operating legal entity is **VeritasChain Co., Ltd.** VSO is not represented here as an independently incorporated nonprofit body.

