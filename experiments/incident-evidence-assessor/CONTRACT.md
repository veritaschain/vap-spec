# Offline incident evidence assessor — implementation contract

Experimental, informative, unadopted. This is an application assessment adapter,
not a VAP/CAP wire format, verifier extension, enforcement gateway or legal finding.

## Input and trust boundary

The input is `{format, evaluation_id, workflow, as_of, target, records}`. Format is
`incident-evidence-input/0.1`. Workflows: `transfer`, `erasure`, `publication`,
`incident_response`, `cross_party`. `as_of` and every time are timezone-aware ISO
8601 strings. The target is `{subject, operation_at, coverage_requested, authorities}`.
`coverage_requested` is `managed_route` or `broader_activity`. Subject fields are
nonempty strings except `object_ids` (distinct nonempty strings); digest fields are
64 lowercase hex characters. Supported subject names are request_id, actor_id,
provider_id, endpoint, tenant_id, account_id, purpose, payload_sha256, artifact_id,
revision_id, object_ids, policy_id, policy_version, policy_sha256, stage, route_id,
disclosure_sha256. At least request_id is required. Every record binding has the
same field names as the target subject, but values may differ. Comparison of all
fields is the default; policy records use explicitly listed policy binding fields.

The caller supplies a separate trust file: `{format, evaluation_id, workflow, as_of, target_sha256,
mode, keys}`. Format is `incident-evidence-trust/0.1`. Modes are
`synthetic-test-only` and `explicit-evaluator`. The target hash is SHA-256/JCS of
the complete target, including authorities. A synthetic configuration requires
explicit `allow_synthetic=True` / `--allow-synthetic`. Keys map key IDs to
`{public_key, issuer, organization, roles, not_before, not_after}`. The trust file
is an evaluator decision, never automatically accepted from an evidence package.
The workflow and evaluation cutoff are also pinned by this separate configuration.
Target operation time must be at or before the observation cutoff.
Production identity onboarding, revocation and historical timestamp assurance are
outside this prototype. Roles are policy, gateway, collector, provider, author,
reviewer, responder and recipient. Every used role has an expected issuer in
target.authorities. Independent review also requires a different trusted organization
from the provider and requester; key count alone is not organizational independence.

Every signed record is `{algorithm, key_id, body, signature}`, algorithm Ed25519,
hex signature (64 bytes). Body is `{record_id, evaluation_id, kind, issuer,
recorded_at, binding, data}`. Signed bytes are UTF-8
`incident-evidence-adapter/0.1`, a zero byte, then RFC 8785 JCS of exactly
`{algorithm, key_id, body}`. Signed bytes include kind, issuer, evaluation, binding
and full typed data. Key validity and future-record checks use the stated record
time; a successful check does not prove that historical time independently.

## Python module boundaries

`model.py` supplies InputError, exact_keys(value, required, optional=()),
text(value), boolean(value), strings(value), timestamp(value), digest_hex(value),
enum(value, choices), interval(start,end) and strict_json(path). Validation rejects
unknown fields, duplicate JSON keys/IDs/list items, invalid types, nonfinite or
unsafe numbers, malformed digests, timezone-free times and reversed intervals.

`evidence.py` supplies canonical(value), digest(value), signing_bytes(envelope),
VerifiedRecord and Context. Context properties: package, trust, target, subject,
as_of (datetime), operation_at (datetime), integrity_established (bool), checks.
`ctx.records(kind)` returns only eligible authenticated records for this evaluation,
expected issuer and authorized role, not in the future. Records expose record_id,
kind, issuer, recorded_at (datetime), binding (dict), data (dict), organization.
`ctx.matches(record, fields=None)` and `ctx.differences(record, fields=None)`
compare against target.subject with JCS equality; all fields are default.
`ctx.bound(kind, fields=None)` filters records by this binding.
`ctx.finding(code, *records)` appends a reason code with the supporting record IDs.
`ctx.organization_for(role)` resolves the unique organization configured for the
expected issuer and role, or returns None if unavailable/ambiguous.

Each workflow module exports `KINDS: dict[kind, required_role]`,
`validate_data(kind, data)` and `evaluate(ctx) -> dict[str,str]`.
All supplied records are structurally validated before authentication. Missing
records mean unknown evidence; malformed supplied records are input errors.
Workflow logic must compare applicability and dates itself. Unsupported external
anchor material must never establish a positive anchor or XREF result.

`assess.py` exports `assess(package, trust, *, allow_synthetic=False) -> dict`.
The report has `assessments`, `findings`, `evidence_checks`, `limitations`, and
input/trust hashes. Runtime code never reads the 23-case catalogue or case IDs.
The suite runner alone compares the catalogue's non-reason expected fields with
actual derived fields. Matching a negative case is not evidence approval.

## Fixture support API (test support only)

`fixture_support.py` defines NOW=`2026-10-30T12:00:00Z`, OPERATION=
`2026-10-30T11:00:00Z`, BEFORE=`2026-10-30T00:00:00Z`, AFTER=
`2026-10-31T00:00:00Z`; `base(workflow)` returns `(package, trust)` with a fully
populated synthetic subject and distinct test-role organizations/keys. Mutate the
target before adding records, or pass explicit binding for old/mismatched records.
`add(package, kind, data, *, role, binding=None, recorded_at=OPERATION,
record_id=None)` signs a record with the public deterministic test key for role.
`finish(package,trust)` pins the final target digest and returns the pair.
`sign(body, role)` creates one envelope; `digest(value)` is imported from evidence.
Fixture modules export `build() -> dict[case_id, (package,trust)]`; they never copy
catalogue expected values into inputs. Fixture IDs exist only outside runtime.

Transfer/erasure modules and fixtures are developed separately from
publication/incident_response/cross_party modules and fixtures. The final README
will document supported kind-specific data and tested limitations.
