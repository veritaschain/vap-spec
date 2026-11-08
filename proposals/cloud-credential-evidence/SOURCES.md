# Source ledger — cloud workload credential evidence

**Reviewed: 7 November 2026 JST.** This is a compact source review for an unadopted design proposal.
The linked pages remain live; publication dates, revisions and observation scope are separate.
No forensic capture or independent reproduction was supplied to VSO for this note.

**Follow-up reviewed: 9 November 2026 JST.** The added incident rows and session-state discussion
below supplement the 7 November baseline; they do not change the historical implementation results.

## Incident sources

| Source | Version checked | Bounded use in the proposal |
| --- | --- | --- |
| [Microsoft Threat Intelligence / Security Research][ms] | Published 5 November 2026 | Reports at least one five-minute GitHub-to-Key-Vault case and agentic use of exposed application credentials. The separate 28-, 60- and 80-second API-adjustment examples do not form that case's disclosed full timeline. The 28-second example concerns ARM secret metadata, not proof of secret-content retrieval. |
| [Todyl][todyl] | Published 3 November; page last updated 6 November 2026, with a dated 6 November update and earlier sections retained | The updated assessment cites Microsoft's research. Earlier text says its telemetry did not show a model directing the activity. Preserve that chronology; the update is not independently supplied attacker-model telemetry. Its customer observations have their own coverage, not a campaign-wide census. |
| [Chainalysis][chainalysis] | Initial disclosure 30 October; page includes updates through 7 November 2026; checked 9 November JST | The 4 November 11:00 P.M. EST update reports exposure of all users' password hashes and live tokens, revising the earlier assessment. This motivates session-state review; the disclosure does not establish the actual token lifecycle or each attacker's autonomous step. |
| [Microsoft Threat Intelligence: Storm-3358][storm3358] | Published 6 November 2026; checked 9 November JST | Reports ARTEX-assisted intrusion and remote-access-tool deployment by Storm-3358. Defender observations motivate source-specific process/network mappings, outside the current Azure decoder. Do not merge this report with the 5 November exposed-secrets case. |

These are attributed findings, not observations produced by the proposed adapter. Their AI assessments
do not identify the internal reasoning behind every observed API request. This note makes no additional
framework attribution, victim total, loss estimate or claim that the current VAP/VCP would have prevented
the reported activity.

The 9 November session-state continuation is VSO design reasoning. Existing operation-permission
interval checks do not establish provider token expiry or effective revocation. The related
[EVIDECT contract][evidect-lifecycle] was reviewed at `3acb662fefbd03774ca61d3d588c541cae431d1a`
in [open Draft PR #37][evidect-pr]. Its mock-provider lifecycle checks are separate experimental
work, not incident reconstruction or a live provider integration. The continuation adds no tests,
acceptance-case identifiers, normative fields or claim of prevention.

## Primary technical references

| Source | Page date shown at review | Adapter implication |
| --- | --- | --- |
| [Application and service principal objects][identity] | 1 October 2024 | AppId and a tenant-local service principal identify different objects. Managed-identity service principals have no associated application object. Preserve identity kind and tenant context. |
| [AADServicePrincipalSignInLogs table][signin] | 28 August 2026 | AADTenantId, AppOwnerTenantId and ResourceOwnerTenantId have distinct meanings; TenantId denotes the logging workspace. Credential/token IDs and time fields must retain source semantics and missingness. Schema presence alone does not establish populated values or a universal join key. |
| [Azure Key Vault logging][keyvault] | 10 April 2026 | Optional client correlation and operation-specific results need explicit interpretation. The documented logging-to-Storage path can make information available up to ten minutes after the operation; this is not an incident latency measurement or a universal latency/response SLA. |
| [Key Vault Get Secret REST reference][get-secret] | API version 2025-07-01; checked 7 November 2026 | GET and HTTP 200 define the documented successful retrieval response. The offline experiment does not promote arbitrary 2xx responses or explicitly conflicting collector methods into a supported SecretGet observation. |

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

The initial English and Japanese design recorded the same ten unexecuted acceptance cases.
The subsequent [offline synthetic experiment](../../experiments/cloud-credential-evidence/README.md)
has its own restricted mapping, caller-supplied trust assumptions, executable checks and coverage.
Its generated inputs are not incident evidence, Azure-origin signatures or independent reproduction.
The subsequent [local collector pilot](../../experiments/cloud-credential-collector/README.md)
adds real local persistence and process-recovery checks with synthetic inputs. Its custody design
and external-checkpoint limits are VSO experimental choices, not Microsoft requirements or an
independent reconstruction of the incident. Its implementation references
[SQLite atomic commit](https://www.sqlite.org/atomiccommit.html) and
[Python filesystem synchronization](https://docs.python.org/3.12/library/os.html#os.fsync);
process-kill tests do not establish power-loss durability.
Updating this source review does not revise fixed evidence or specification releases.

[ms]: https://www.microsoft.com/en-us/security/blog/2026/11/05/threat-actors-use-agentic-ai-tooling-to-find-and-abuse-exposed-secrets/
[todyl]: https://www.todyl.com/blog/stolen-app-credentials-real-access-an-actor-is-signing-into-entra-id-and-azure-devops-as-your-workloads
[identity]: https://learn.microsoft.com/en-us/entra/identity-platform/app-objects-and-service-principals
[signin]: https://learn.microsoft.com/en-us/azure/azure-monitor/reference/tables/aadserviceprincipalsigninlogs
[keyvault]: https://learn.microsoft.com/en-us/azure/key-vault/general/logging
[chainalysis]: https://www.chainalysis.com/blog/security-incident-october-30/
[storm3358]: https://www.microsoft.com/en-us/security/blog/2026/11/06/artex-abuse-expands-as-cybercriminals-target-financial-sector/
[evidect-lifecycle]: https://github.com/veritaschain/evidect-site/blob/3acb662fefbd03774ca61d3d588c541cae431d1a/examples/execution-authorization/credential-lifecycle/CONTRACT.md
[evidect-pr]: https://github.com/veritaschain/evidect-site/pull/37
[get-secret]: https://learn.microsoft.com/en-us/rest/api/keyvault/secrets/get-secret/get-secret?view=rest-keyvault-secrets-2025-07-01
[vap-base]: https://github.com/veritaschain/vap-spec/tree/d97980f340ff9f81639daf8ffa6e02acbe1433ec
[registry]: https://github.com/veritaschain/vap-spec/blob/d97980f340ff9f81639daf8ffa6e02acbe1433ec/README.md#relationship
[vcp-base]: https://github.com/veritaschain/vcp-spec/tree/2dd82e2a70b7f3245ba00e851c991c035649beee
[vcp-issues]: https://github.com/veritaschain/vcp-spec/blob/2dd82e2a70b7f3245ba00e851c991c035649beee/spec/v1.2/README.md#known-issues-in-v12-informative
[bindings]: ../incident-evidence-bindings/README.md
[payment]: ../../experiments/payment-api-evidence/README.md
[scope]: ../../experiments/declared-scope-verifier/README.md
