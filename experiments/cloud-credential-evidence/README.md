# Cloud credential evidence experiment

**Status: unadopted, informative; offline synthetic experiment.** [日本語](README-ja.md)

This experiment makes bounded evidence distinctions from
[CE-01–CE-10](../../proposals/cloud-credential-evidence/README.md) executable.
It checks deliberately synthetic collected statements, a versioned subset of Azure-shaped
records and separately supplied trust/authority configuration. It does not connect to Azure,
reconstruct the Microsoft/Todyl incidents or establish VAP conformance.

## Run

The focused [workflow](../../.github/workflows/cloud-credential-evidence.yml) uses Python 3.12
and the pinned `cryptography` dependency. From the repository root:

```sh
python -m pip install -r experiments/cloud-credential-evidence/requirements.txt
python -m unittest discover -s experiments/cloud-credential-evidence/tests -v
python -O -m unittest discover -s experiments/cloud-credential-evidence/tests -v
python experiments/cloud-credential-evidence/fixtures.py
```

The fixture command evaluates synthetic inputs and checks their expected evidence distinctions.
Success of this command means those test expectations matched, not that an operation was safe,
an incident was prevented or a cloud environment was audited.

The library entry point is
`verify_bundle(bundle, trust, *, scope, evaluation_time)`.
Trust, review scope and the evaluation horizon are separate caller inputs, outside the submitted
evidence bundle. The checker does not read a live clock, fetch evidence, make cloud requests,
retry operations, revoke credentials or change a resource.

For a single generated case, run from this directory:

```python
from cloud_evidence import verify_bundle
from fixtures import positive_case, seal_bundle

case = positive_case()
report = verify_bundle(
    seal_bundle(case), case["trust"],
    scope=case["scope"], evaluation_time=case["evaluation_time"],
)
print({name: item["status"] for name, item in report["claims"].items()})
```

The command-line checker accepts separate `--bundle`, `--trust` and `--scope` JSON files,
plus `--at` as an integer UTC Unix timestamp. The experiment requires `synthetic: true`.
Its bounded JSON subset rejects duplicate keys, floating-point/non-finite numbers, negative
zero, non-NFC strings and excessive nesting/size. It is not a general Azure export decoder;
unsupported source representations are rejected rather than silently rewritten.

## Separate evidence questions

The report uses experimental claim labels `supported`, `contradicted` and `unresolved`.
`supported` is conditional on the caller's trust and the supplied scope. A contradiction
that can be checked is retained even when unrelated evidence is missing. There is no overall
safety verdict, admission command, certification or normative VAP result.

The CLI returns **0 when it produces an assessment**, including assessments with unresolved
or contradicted claims; it returns **2 for malformed input or configuration**.
Do not use its process exit code as permission to execute an operation.

| Question | Boundary |
| --- | --- |
| Signature and provenance | Verify signed bytes, then separately check whether the configured key may speak for the exact issuer, role, tenant and resource at the relevant time. |
| Authentication and authority | A successful sign-in is distinct from an exact-operation permission and its validity interval. |
| Resource observation | A matching, source-reported SecretGet is narrower than payload capture, onward transfer or downstream use. |
| Association | A signed collector binding can link exact supplied records under that collector's authority. A common client correlation ID, IP or nearby time is only a candidate association. |
| Evidence timing | Event, source availability, receipt and the caller's review horizon remain distinct. Later evidence does not become an earlier prerequisite. |
| Collection and containment | Evaluate the caller-declared record set and collection window. Keep coverage gaps, token-lineage gaps and other tenants visible; scoped observations do not establish universal containment. |
| AI assessments | Retain dated source judgments and their provenance. Native Agent/UserAgent fields are not direct observations of an attacker's model reasoning. |

## Native records and collector context

See the proposal's [source ledger](../../proposals/cloud-credential-evidence/SOURCES.md) for
the primary Microsoft documentation used to design the mapping. This is a restricted mapping,
not a promise to decode every Azure export schema or every cloud service.

The original UTF-8 record bytes and their commitment remain separate from the normalized view.
The checker recomputes the commitment and derives the view itself; a submitted normalized value
cannot replace what the original record says. Missing native facts remain missing.

For sign-ins, workspace `TenantId` is separate from `AADTenantId`,
`AppOwnerTenantId` and `ResourceOwnerTenantId`. For Key Vault, `resourceId` identifies the
vault; an exact request URI needs its own binding. A result field named `resultSignature`
is not an Azure cryptographic signature. Each source's result fields keep their own semantics.

Method, API plane and an exact attempt relationship are not silently invented from native fields.
Where used, a separately signed collector/request-context statement supplies and labels them.
That sidecar is a statement by its configured signer, not a provider-issued proof of causality.
Exact record references and the source operation/version/result prevent a later retry's success
from being transplanted onto the earlier failed request.

The [Get Secret REST reference](https://learn.microsoft.com/en-us/rest/api/keyvault/secrets/get-secret/get-secret?view=rest-keyvault-secrets-2025-07-01)
documents GET and HTTP 200 for successful retrieval. The checker rejects an explicitly conflicting
collector method and does not turn HTTP 202/204 into a supported SecretGet read. Missing method
information stays missing; it is not inserted into the native record.

## Trust and interpretation

- The submitted bundle cannot install its own trusted keys or widen the caller's grants.
- Key authority is scoped by issuer, role, tenant, resource and validity, not merely by a key's name.
- Mathematical signature validity is reported separately from trusted provenance. A trusted
  collector's signature protects its collected statement; it does not prove Azure origin,
  honest collection, an authoritative source clock or completeness of unobserved activity.
- The review scope pins the operation, attempt, principal, vault, exact request URI, audience,
  action, window and expected evidence set. Missing mappings are not inferred from a shared AppId.
- The caller also supplies the expected sign-in resource identity, owner tenant and resource
  service principal. A source GUID is not assumed to be the same identifier as an OAuth audience.
- Key-grant intervals apply to the statement's asserted receipt time. This check cannot prove
  when a key signed, its real lifecycle or the truth of the asserted clock.
- The experiment's restricted JSON/signature domain is its own encoding, not RFC 8785 or a VAP
  wire format. Raw source records have independent byte commitments.
- Fixture signing seeds are deliberately public synthetic data. Different fixture keys do not
  establish separate organizations or independent custody.

The caller's `scope.action_time` is an evidence-availability checkpoint.
`prerequisite_record_ids` identifies the authentication/permission evidence expected before it;
later resource outcomes and collection receipts are not prerequisites. Permission validity for
an observed operation is checked against that operation's native event time. Unknown operation
time cannot establish that retrospective authorization.

Envelope times are integer UTC Unix seconds. Supported native UTC timestamps retain up to seven
fractional digits in comparisons. Ordering checks use the supplied clocks as an assumption,
not a trusted timestamp service. Impossible source/availability/receipt ordering remains visible
separately from the checkpoint result, and a collection cannot close a future review window.

Exact-envelope references in bindings, collection statements and assessment revisions also check
receipt order: a referring envelope cannot be received before the envelope it claims to reference.
This uses comparable asserted receipt clocks. Source event/availability times describe underlying
observations, not when the complete later wrapper was signed or published; a retrospective wrapper
can therefore be received later. There is no proof of a signing or full-wrapper publication time.

## Acceptance coverage

The ten identifiers are proposal groups, not a count of real incidents or an assertion that
every production adapter requirement is complete. The tests include re-signed semantic
contradictions, so a changed binding must be detected even when the signature is valid.

| Group | Executable distinction |
| --- | --- |
| CE-01 | Matching evidence supports only its scoped operation and declared collection. |
| CE-02 | Sign-in success, absent resource use/permission, and an explicit permission denial remain distinct. |
| CE-03 | A repeated AppId or a workspace identifier cannot merge tenant-local principals or grants. |
| CE-04 | A valid signature does not supply missing issuer/role/tenant/resource authority. |
| CE-05 | Weak correlation remains a candidate; missing or conflicting exact bindings remain visible. |
| CE-06 | Metadata success and source-reported secret-content access have different outcomes. |
| CE-07 | Late or unknown availability/receipt cannot support a pre-action use claim. |
| CE-08 | Failed and changed retry attempts retain their own signed bindings and results. |
| CE-09 | Rotation and a scoped query do not establish complete containment across tokens, tenants and time. |
| CE-10 | Earlier and later source assessments remain separate, and agent labels do not expose private reasoning. |

## Remaining implementation boundary

The separate [local collector pilot](../cloud-credential-collector/README.md) now supplies
raw-byte custody, signed collection receipts, process-recovery tests and native-envelope export.
It leaves this checker's semantics unchanged. Actual local receipt time stays a receipt time;
source availability, permissions, exact operation bindings and collection closure are not invented
by the bridge. Its local signatures and checkpoint comparisons do not establish Azure origin or
independent custody.

This directory contains a reproducible offline semantics experiment. It does not contain a live
Azure collector, cloud credential store, API connector, complete cloud schema decoder or runtime
authorization gate. There is no incident forensic dataset, independent third-party execution,
cross-party anchor, immutable storage service, deployment assurance or prevention measurement.

Real integration would need authenticated ingestion and source-specific mapping, protected raw
evidence, scoped trust provisioning and lifecycle, clock/availability measurements, privacy and
retention controls, and tests against the actual collection environment. Evidence absent from
collection cannot be recovered by hashing or signing. Synthetic fixtures contain no production
credentials, customer data or retrieved secret contents.
