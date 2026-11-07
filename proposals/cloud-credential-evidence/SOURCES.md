# Source ledger — cloud workload credential evidence

**Reviewed: 7 November 2026 JST.** This is a compact source review for an unadopted design proposal.
The linked pages remain live; publication dates, revisions and observation scope are separate.
No forensic capture or independent reproduction was supplied to VSO for this note.

## Incident sources

| Source | Version checked | Bounded use in the proposal |
| --- | --- | --- |
| [Microsoft Threat Intelligence / Security Research][ms] | Published 5 November 2026 | Reports at least one five-minute GitHub-to-Key-Vault case and agentic use of exposed application credentials. The separate 28-, 60- and 80-second API-adjustment examples do not form that case's disclosed full timeline. The 28-second example concerns ARM secret metadata, not proof of secret-content retrieval. |
| [Todyl][todyl] | Published 3 November; page last updated 6 November 2026, with a dated 6 November update and earlier sections retained | The updated assessment cites Microsoft's research. Earlier text says its telemetry did not show a model directing the activity. Preserve that chronology; the update is not independently supplied attacker-model telemetry. Its customer observations have their own coverage, not a campaign-wide census. |

These are attributed findings, not observations produced by the proposed adapter. Their AI assessments
do not identify the internal reasoning behind every observed API request. This note makes no additional
framework attribution, victim total, loss estimate or claim that the current VAP/VCP would have prevented
the reported activity.

## Primary technical references

| Source | Page date shown at review | Adapter implication |
| --- | --- | --- |
| [Application and service principal objects][identity] | 1 October 2024 | AppId and a tenant-local service principal identify different objects. Managed-identity service principals have no associated application object. Preserve identity kind and tenant context. |
| [AADServicePrincipalSignInLogs table][signin] | 28 August 2026 | AADTenantId, AppOwnerTenantId and ResourceOwnerTenantId have distinct meanings; TenantId denotes the logging workspace. Credential/token IDs and time fields must retain source semantics and missingness. Schema presence alone does not establish populated values or a universal join key. |
| [Azure Key Vault logging][keyvault] | 10 April 2026 | Optional client correlation and operation-specific results need explicit interpretation. The documented logging-to-Storage path can make information available up to ten minutes after the operation; this is not an incident latency measurement or a universal latency/response SLA. |

The timing, trust and acceptance requirements in the proposal are **VSO's design reasoning** from these
source distinctions, not a Microsoft or Todyl specification or endorsement. No claim is made that a
native log's HTTP result is a cryptographic signature. An imported export, a collector signature and
independently anchored cross-party evidence remain different provenance arrangements.

## Repository baseline and status

- VAP main at review: [d97980f340ff9f81639daf8ffa6e02acbe1433ec][vap-base].
  [The registry and publication notice][registry] identify VAP v1.2 Draft 3 and the unpublished
  DAP Working Draft text. This proposal does not publish or adopt DAP.
- VCP main at review: [2dd82e2a70b7f3245ba00e851c991c035649beee][vcp-base].
  [The specification status and known issues][vcp-issues] do not define an adopted generic cloud profile.
- [Existing incident bindings][bindings], [payment evidence][payment] and [declared-scope verification][scope]
  are reference work with their own limits. No existing result is counted as execution of CE-01 to CE-10.

The English and Japanese proposal share the same ten unexecuted acceptance cases. A future implementation
needs its own schema mapping, trust assumptions, actual checks and recorded results. Updating this source
review does not revise fixed evidence or specification releases.

[ms]: https://www.microsoft.com/en-us/security/blog/2026/11/05/threat-actors-use-agentic-ai-tooling-to-find-and-abuse-exposed-secrets/
[todyl]: https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads
[identity]: https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals
[signin]: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs
[keyvault]: https://learn.microsoft.com/en-us/azure/key-vault/general/logging
[vap-base]: https://github.com/veritaschain/vap-spec/tree/d97980f340ff9f81639daf8ffa6e02acbe1433ec
[registry]: https://github.com/veritaschain/vap-spec/blob/d97980f340ff9f81639daf8ffa6e02acbe1433ec/README.md#relationship
[vcp-base]: https://github.com/veritaschain/vcp-spec/tree/2dd82e2a70b7f3245ba00e851c991c035649beee
[vcp-issues]: https://github.com/veritaschain/vcp-spec/blob/2dd82e2a70b7f3245ba00e851c991c035649beee/spec/v1.2/README.md#known-issues-in-v12-informative
[bindings]: ../incident-evidence-bindings/README.md
[payment]: ../../experiments/payment-api-evidence/README.md
[scope]: ../../experiments/declared-scope-verifier/README.md
