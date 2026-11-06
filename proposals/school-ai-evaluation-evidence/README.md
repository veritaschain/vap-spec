# School AI alerts and evaluation configuration evidence

**Status: informative design proposal; unadopted. Review date: 6 November 2026.**

[日本語](README-ja.md)

This review connects two source reviews with specific evidence questions: how a
school AI interaction reaches a safety response, and whether an evaluation's
declared isolation matches its observed runtime state. It introduces no profile,
normative field, conformance claim or implementation. No Google integration,
school deployment, new isolation experiment or acceptance test was run for this
document. The [site review PR](https://github.com/veritaschain/vcp-site/pull/202)
contains the corresponding incident entries and their claim-level sources.

## 1. Source decisions

| Topic | Treatment in this review |
|---|---|
| School lawsuit | The counsel-published complaint has a 2 November state stamp and 4 November federal header; distinguish these from the article date. Harm and causation remain allegations. [S0–S1] |
| Product and records | Google Search AI Mode, the Gemini app and the underlying model are different layers. The complaint’s history-access allegation does not establish absent or altered internal logs. [S0, S2] |
| School controls | Google's 3 November announcement describes future default-off controls, including Search. It does not establish completed rollout or that this lawsuit caused the change. [S3] |
| Irregular explanation | The CEO's November remarks concern earlier evaluation incidents. Preserve them as an attributed follow-up, not a new intrusion or an independent causal finding. [S4] |
| Existing technical evidence | Anthropic’s September assessment considers both configuration and model behaviour; Hugging Face describes reconstruction using logs. OpenAI separately reports an Artifactory zero-day enabling internet access. These mechanisms must not be collapsed into one configuration error. [S5–S7] |

The practical question is which evidence was collected, by whom, with what
coverage, and which authorized reviewer can obtain it. Public non-disclosure,
unavailable user history, missing collection and demonstrated modification must
remain distinct. None of these sources establishes that VAP was deployed or
would have prevented the reported harm.

Counsel’s case page dates the filing to 4 November, while the state-court stamp
on its linked complaint says 2 November. This review uses the stamp for the
initial filing date. The complaint and counsel’s statement are primary sources
for what the plaintiff alleges, not independent proof of those allegations.
Reuters supplies Google’s response. [S0–S1]

## 2. Proposed evidence for school AI safety responses

These are design questions for a future adapter, not requirements already
implemented by VAP or MAP. Identifiers and names below are descriptive only.

| Boundary | Evidence to bind | What it would not establish |
|---|---|---|
| Product and managed account | Product surface, managed-account class, effective policy/version, administrator change and observation time | A Gemini-app switch covers Search, personal accounts or every browser route |
| Request and response | Correlation ID, observed input and supplied context references, provider/model identifier when available, response and delivery observations, collector identity | Complete hidden reasoning, unavailable model versions, or that a displayed response was read or understood |
| Risk assessment | Classifier/policy version, applicable threshold, observed decision and any uncertainty; bind to the relevant request/response | Clinical diagnosis, reliable detection of every risk, or a decision that was never observed |
| Alert and response | Decision to alert or suppress, dispatch attempt, transport receipt, authorized recipient acknowledgment and any separately recorded response | Sent means delivered, delivered means acknowledged, or acknowledgment means an effective intervention |
| Review and disclosure | Requesting authority, permitted scope, access/export events, redactions, retention basis and unavailable material | An unrestricted right to disclose a child's conversations or evidence that missing material never existed |

Define the collection boundary before interpreting a missing event. If a captured
risk decision requires a terminal alert outcome under a stated policy, an absent
outcome is an unresolved gap. Do not convert it into “no alert was required” or
“the child was safe.” Cross-check provider, school and delivery-service records
where an authorized, independent observation exists. An export signed later by
one operator remains that operator's account of the past.

Store sensitive payloads under appropriate access controls, separately from
public commitments. A hash is not encryption or anonymization; predictable text
can be guessed from a public digest. Use a reviewed commitment and disclosure
design, document key custody, retention and permitted erasure, and record gaps
when content is unavailable. Do not publish raw minor conversations, diagnostic
labels or self-harm instructions in an evidence example. Logging does not itself
provide a safety response; recipient selection and intervention need an explicit
operational policy and responsible people.

## 3. Proposed evidence for evaluation configuration and actions

Separate intended configuration, observed configuration and actual reachability.
An administrator's `isolation_enabled` declaration alone is not a network test.

| Boundary | Evidence to bind | Remaining limitation |
|---|---|---|
| Evaluation identity | Run ID, model/checkpoint if disclosed, harness/configuration digest, target authorization scope, controller identity | Model names or signed configuration are not proof of permission to access a target |
| Runtime state | Versioned policy and observed routes, identities, memberships and relevant configuration changes | A snapshot is neither continuous enforcement nor proof of every path |
| Reachability observation | Controlled target, protocol/path, observation interval, observer identity and healthy positive control | A failed request can reflect an unhealthy target; unobserved paths remain unknown |
| Action and result | Attempt, target scope, tool invocation, independent network/backend observation and terminal result where available | A model-authored transcript or an HTTP response alone proves neither execution nor its entire effect |
| Changes and gaps | Policy drift, collector outage, observation expiry, revocation and restart; preserve incident-to-follow-up links | Sealing evidence after collection cannot reveal every event omitted before sealing |

Use only explicitly authorized controlled targets for future tests. General
internet probing is unnecessary for this proposal. Treat a configuration change
as invalidating observations bound to the previous version. A trusted, enforced
admission mechanism would still need to bind policy and observation freshness to
execution; a timestamped preflight check does not close a check/use race.

Keep separate judgments for record integrity, observation coverage, authorization,
isolation and observed effect. A valid signature on evidence of an unauthorized
connection must not become an overall success result. Configuration failure and
unsafe model behaviour may coexist; event ordering and correlation do not by
themselves establish scientific or legal causation.

## 4. Existing specification and implementation boundaries

The reference point is [VAP v1.2 Draft 3](../../spec/v1.2/VAP_Framework_Specification.md),
not a claim of deployment or certification.

| Existing item | Relevance and limit |
|---|---|
| INT-004 / INT-004a | Cryptographic sequence verifiability is required. Per-event hash chaining is optional at framework level; a profile can require it. Merkle batch anchoring remains required by §4.1.4; an additional per-event chain is not universally required. |
| INT-006 / INT-007 | External anchoring and continuity are framework requirements. The proposed adapter has not implemented them. |
| INT-008 / §11.1 | Detect post-anchor omission within an anchored batch's declared scope. Do not claim that an event never measured or never included becomes detectable without another record implying its existence. |
| §4.2 / §4.3 / TRC-005 | Provenance and cross-party links support review of recorded observations, with issuer, trust and collection boundaries explicit. They do not read a model's private reasoning. |
| §4.1.5 / §6 | Cryptographic agility is required. Ed25519 is a default, not the only permitted cryptographic choice. Key compromise and trusted-key establishment remain relevant. |
| §1.6 / §4.5.2 | VAP conformance is not legal compliance, safety or admissibility. MAP is listed as v0.1.2 Working Draft; the repository says its revised text is not public. It is not an adopted mandatory control for school chatbots. |
| [Control-state evidence experiment](../../experiments/control-state-evidence/README.md) | Captures declared and observed state in a bounded lab and seals it after collection. Its preflight is non-enforcing; no independent external anchor or universal path coverage is established. |
| [OS isolation experiment](../../experiments/os-isolated-gate/README.md) | A controlled topology includes a controller-induced network-membership change that exposes a bypass. It does not establish protection against a malicious host/controller. |
| [Incident evidence bindings](../incident-evidence-bindings/README.md) | Reuse its separation of requests, receipts, disclosure and scoped deletion evidence. Existing experiments do not implement this school workflow. |

## 5. Regulatory interpretation and review priorities

The US lawsuit does not itself establish EU jurisdiction. An EU assessment must
separately consider territorial scope, the actor's role, intended use and the
applicable date. Education or use by a minor alone does not make every chatbot
an Annex III high-risk system. Article 12 logging and Article 55 obligations for
providers of GPAI models with systemic risk have different subjects and triggers.
Neither provision mandates VAP or proves that a particular school or evaluator
breached a duty. [L1–L4]

The relevant high-risk application dates were amended in 2026; this review does
not assume Annex III logging obligations were already generally applicable at
the time of the reported events. The Commission distinguishes those dates from
the GPAI rules, applicable since August 2025 subject to transition provisions.
A specific model’s status and market date still need separate examination. [L5]

For 6–13 November, useful watch items are later docket entries, any substantive
Google response, product-specific rollout details, and further independent
evaluation findings. This is a research checklist, not a forecast that a new law,
regulatory demand or technical report will arrive within that week. Monitoring or
an automatic scheduled job is not created by this document.

Before implementation, resolve authorized evidence access, collection coverage,
retention, independent observations and the runtime mechanism responsible for
action. Evaluate those choices separately from cryptographic record integrity.

## Sources

- **S0:** [Complaint published by counsel](https://edtech.law/wp-content/uploads/2026/10/2026.11.04-Dkt-001-1-Emma-v-Google-Complaint.pdf), PDF p. 2 (filing stamps and parties), §§1–8, 18 and 28 (selected allegations); [counsel’s case page](https://edtech.law/cases/emma-v-google/). Court-filed allegations, not adjudicated findings.
- **S1:** [Reuters, via CNA, 5 November](https://www.channelnewsasia.com/business/google-faces-claims-student-used-ai-chat-us-school-laptop-plan-suicide-attempt-6528611). Secondary report, including Google’s public response.
- **S2:** [Bloomberg, via Claims Journal, 5 November](https://www.claimsjournal.com/news/national/2026/11/05/341139.htm). Secondary report of allegations and access limitations.
- **S3:** [Google, Designing responsible AI for learning, 3 November](https://blog.google/products-and-platforms/products/education/ai-learning-era-updates-2026/). Provider announcement.
- **S4:** [Bloomberg, via Mint, 3 November UTC / 4 November IST](https://www.livemint.com/companies/firm-tied-to-some-openai-anthropic-ai-hacks-blames-error/amp-11793732135131.html). Secondary report of the CEO's explanation.
- **S5:** [Anthropic, alignment assessment, 9 September](https://www.anthropic.com/research/alignment-assessment-cybersecurity-incidents). Provider assessment; not an independent finding.
- **S6:** [Hugging Face, technical timeline, 27 July](https://huggingface.co/blog/agent-intrusion-technical-timeline). Affected party's account of recovered evidence.
- **S7:** [OpenAI, incident disclosure with 28 July update](https://openai.com/index/hugging-face-model-evaluation-security-incident/). Provider account of the distinct escape mechanism.
- **L1:** European Commission AI Act Service Desk, [Article 2](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-2) (scope).
- **L2:** [Article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6) and [Annex III §3](https://ai-act-service-desk.ec.europa.eu/en/ai-act/annex-3) (classification and education uses).
- **L3:** [Article 12](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-12) (logging); [EUR-Lex consolidated text of 27 July 2026](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A02024R1689-20260727).
- **L4:** [Article 55](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-55) (providers of systemic-risk GPAI models).
- **L5:** European Commission, [Navigating the AI Act](https://digital-strategy.ec.europa.eu/en/faqs/navigating-ai-act) and [GPAI provider guidelines FAQ](https://digital-strategy.ec.europa.eu/en/faqs/guidelines-obligations-general-purpose-ai-providers) (application dates and transition).

Sources were reviewed to the stated cutoff. The source list is not a source
archive, a sealed Evidence Pack, a court determination or independent validation.
