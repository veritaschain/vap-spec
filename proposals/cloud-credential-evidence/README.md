# Cloud workload credential evidence — informative proposal

**Status: proposed, unadopted; design with a bounded offline experiment.** Reviewed **7 November 2026 JST**.
[日本語](README-ja.md) · [Source ledger](SOURCES.md)

Baseline: VAP repository commit
[d97980f](https://github.com/veritaschain/vap-spec/tree/d97980f340ff9f81639daf8ffa6e02acbe1433ec).
The acceptance cases below are proposed criteria. The
[offline synthetic experiment](../../experiments/cloud-credential-evidence/README.md)
now exercises bounded distinctions for CE-01–CE-10; its executable coverage and limits are recorded
separately. There is no live cloud adapter or deployed control, and no new normative field,
profile or conformance result.

## Motivation and source boundary

[Microsoft's 5 November report][ms] describes exposed application credentials enabling cloud
access, including at least one five-minute progression from GitHub secret discovery to Key Vault
data exfiltration. Its separate API-adjustment examples are not a single incident timeline.
[Todyl's live report][todyl] contains a 6 November assessment update and an earlier, less certain
account. Preserve the source version, observation scope and confidence of each statement.

These reports motivate evidence questions; this proposal contains no incident logs or reconstruction.
The defender's observations cannot reveal an attacker's private model reasoning. Source-attributed
AI assessments remain separate from locally verified cloud operations.

## Existing foundation

| Existing work | Relevance and boundary |
| --- | --- |
| [VAP §§4.2–4.4][vap] | Actor, context, action, outcome, delegation and trace relationships provide the framework. |
| [Incident evidence bindings][bindings] | Exact operation, destination, policy and observation scope; imported responses are not automatically independent XREF. |
| [Payment evidence experiment][payment] | Separates supplied-record integrity, authority, observed result and controls. Its synthetic payment encoding is not an Azure adapter; its role-key pool is not a cross-tenant issuer directory. |
| [Declared-scope verifier][scope] | Examines a declared expected set and its gaps under explicit trust assumptions; its results do not cover these proposed cases. |

The [registry and publication disclosure][registry] identify VAP v1.2 as Draft 3 and DAP as a
registered Working Draft whose text is not public. This note does not assume a published DAP schema.
VCP is the finance/algorithmic-trading profile, not an adopted generic cloud-access profile.
Its [known integrity and mapping issues][vcp-issues] remain open.

## Candidate information to bind

The following groups are proposed adapter information, **not new VAP wire fields**. A report would
assess record integrity/provenance, authentication, operation authority, observed result and correlation
separately, retaining contradictions and unresolved evidence rather than emitting an overall safety pass.
Preserve a protected source record and a separately labelled normalized view, including the mapping
version and any redactions. Missing source facts are not values for the adapter to invent.

| Information | Proposed review binding |
| --- | --- |
| Identity namespaces | Preserve source product/schema and identity kind. For application identities, distinguish AppId, application owner tenant and tenant-local service principal; keep resource tenant and logging workspace separate. Managed identities need their own mapping, not an invented app object. |
| Authority | Bind the exact action, resource, audience, tenant, applicable grant/policy, decision source and validity interval. Cloud sign-in success and a business authorization decision answer different questions. |
| Credential reference | Preserve an issuer-provided non-secret credential/key or token identifier only when actually recorded, with its source meaning and missingness. Do not publish secrets, bearer tokens or retrieved secret contents. A guessed mapping or hash of a low-entropy secret is not a safe substitute. |
| Operation and result | Preserve the API plane, endpoint/resource, method, version, attempt ID, native result and available response evidence. Distinguish token issuance, metadata enumeration, content retrieval and observed onward transfer. |
| Association | Keep source-native IDs and the versioned matching rule. Client correlation IDs, shared IPs, nearby timestamps or a common AppId alone do not prove a causal chain. Retain ambiguous candidate matches. |
| Time | Preserve event/source time, known source-availability time, collector receipt, alert and control-action time, with clock assumptions. Unknown availability stays unknown; later collection cannot become an earlier authorization prerequisite. |
| Provenance and scope | Bind original record commitments, export/query scope, interval, pagination/closure, gaps and collector identity. Establish key authority for the relevant issuer, role, tenant and resource outside the submitted evidence. |
| Source assessment | Preserve the publisher, publication/update time, supporting observation and limits of an AI-attribution statement. A telemetry field named Agent, a user agent string or fast execution alone is not proof of attacker model control. |

### Azure adapter pitfalls to resolve

The [service-principal log table][signin] distinguishes **AADTenantId**, **AppOwnerTenantId**
and **ResourceOwnerTenantId**; its **TenantId** denotes the Log Analytics workspace.
They cannot be normalized into one unqualified tenant field. Credential and token identifiers
listed in that schema are not guaranteed to be populated or shared by other services.
CreatedDateTime and TimeGenerated retain their source meanings; neither automatically supplies
source-availability or collector-receipt time.
[Microsoft's identity model][identity] distinguishes a global application from its tenant-local
service principals; managed-identity service principals have no associated application object.

[Key Vault logging][keyvault] describes an optional, client-provided correlation ID and distinguishes
vault/key information operations from secret operations. A control-plane HTTP 200 or a token for a
Key Vault audience does not establish secret-content retrieval. Even a supported SecretGet observation
supports only the source-reported read; full payload capture, an external exfiltration destination or
further use needs corresponding evidence. This adapter boundary does not revise Microsoft's incident findings.

That logging document describes availability up to ten minutes after an operation for the documented
logging-to-Storage path. This is not measured latency for the reported attack, a universal export
latency or a response SLA. Evaluate event-to-evidence and evidence-to-response delay separately.
Signing exported logs does not make a post-event observation a preventive control.

## Proposed acceptance matrix

All inputs below are hypothetical synthetic review cases. Their expected distinctions are proposed
criteria, not test results. Case labels are local discussion identifiers. The initial design recorded
these cases as unexecuted; subsequent synthetic execution is described in the
[experiment coverage](../../experiments/cloud-credential-evidence/README.md#acceptance-coverage).

| Case | Candidate input | Distinction required for review |
| --- | --- | --- |
| CE-01 | Matching source provenance, tenant-local identity, current exact-operation authority and resource observation | Support only the demonstrated operation and collection scope; do not infer downstream use or universal completeness. |
| CE-02 | Successful sign-in/token issuance, but no resource event or operation approval; separately, an evidenced policy denial | Keep authentication evidence. Resource use and authority remain unresolved when missing; preserve the specific contradiction when established. |
| CE-03 | Same AppId in two customer tenants; or workspace TenantId substituted for an identity tenant | Do not merge tenant-local principals or carry one tenant's grant into another. Missing namespace mapping remains unresolved. |
| CE-04 | Cryptographically valid record under a key with no established authority for this issuer/role/tenant/resource | Separate mathematical signature validity from trusted provenance and the truth of the underlying assertion. |
| CE-05 | Matching client correlation ID, IP or close time with conflicting or missing resource/identity bindings | Preserve candidate associations; a common label does not establish causality or independently anchored XREF. |
| CE-06 | ARM metadata request returns 200; compare with a source-bound SecretGet event | Do not label metadata success as secret-content retrieval. Preserve the actual operation and the scope of any retrieval evidence. |
| CE-07 | Event predates the action, but export/receipt occurs after it or availability is unknown | Do not backdate evidence into a pre-action check. Measure only supported delay intervals; retain unknown clocks/availability. |
| CE-08 | Failed request followed by an altered method/version/target and a successful response | Keep each attempt and its exact bindings. Do not overwrite the failure or transplant a response onto the earlier request. |
| CE-09 | Rotation or one tenant's clean log query, with missing token lineage, another tenant or an unclosed collection window | Retain the scoped finding and gaps. Neither rotation nor missing records establishes complete containment or absence of access. |
| CE-10 | Earlier uncertain source assessment, later revised assessment, or an Agent/UserAgent field alone | Preserve dated source judgments. Do not silently overwrite history or invent direct telemetry of attacker reasoning. |

## Review handoff

The offline experiment supplies a restricted versioned mapping, synthetic fixtures,
caller-supplied trust/authority configuration and a declared collection boundary. Its positive
control and independently altered bindings use no live credentials. A real integration still needs
environment-specific mapping, ingestion and authority provisioning.
Native log provenance and availability must be established for that environment; this note does not
assume that ordinary Azure log exports carry independently verifiable provider event signatures.

An export collector's signature protects its captured statement after collection; it does not by itself
establish Azure origin, completeness or authorization. Separately named keys under the same compromised
operator do not establish independent custody; cross-party XREF requires its existing independent logging and
anchoring conditions. Protected original evidence and a minimized public view need separate access
and retention decisions. Collection or hashing cannot recover an action never observed.

Prevention, credential revocation and runtime enforcement need their own controls and measurements.
The existing experiments, fixed evidence, normative specifications and release statuses are unchanged.
No cloud integration, independent reproduction, formal adoption or production-readiness result is claimed.

[ms]: https://www.microsoft.com/en-us/security/blog/2026/11/05/threat-actors-use-agentic-ai-tooling-to-find-and-abuse-exposed-secrets/
[todyl]: https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads
[signin]: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs
[identity]: https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals
[keyvault]: https://learn.microsoft.com/en-us/azure/key-vault/general/logging
[vap]: ../../spec/v1.2/VAP_Framework_Specification.md
[bindings]: ../incident-evidence-bindings/README.md
[payment]: ../../experiments/payment-api-evidence/README.md
[scope]: ../../experiments/declared-scope-verifier/README.md
[registry]: ../../README.md#relationship
[vcp-issues]: https://github.com/veritaschain/vcp-spec/blob/2dd82e2a70b7f3245ba00e851c991c035649beee/spec/v1.2/README.md#known-issues-in-v12-informative
