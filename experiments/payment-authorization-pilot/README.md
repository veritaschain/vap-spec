# Controlled payment authorization pilot

**Status: unadopted, informative experiment.** [日本語](README-ja.md)

This pilot checks a synthetic maker/checker prerequisite before a new durable
dispatch claim in the [payment runtime](../payment-runtime-pilot/README.md).
It uses actual loopback HTTP, separate provider storage and toy balance effects.
No bank, real funds, human approval system or external service is connected.

An operator separately adopts a policy, verification keys and public-key-to-person
identity mappings. The caller supplies original signed approval and status bytes.
The gate binds them to the exact native payment request, evaluates them at claim
time, and stores its admission record in the same transaction as the claim.
This is a controlled application route, not an exclusive security boundary around
the provider. The original runtime remains a primitive for trusted callers.

## Run and inspect

Run from the repository root with Python 3.12 and native loopback/process support:

```sh
python -m pip install -r experiments/payment-authorization-pilot/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/payment-authorization-pilot/tests -v
python -W error::ResourceWarning -m unittest discover -s experiments/payment-runtime-pilot/tests -v
python experiments/payment-authorization-pilot/run_demo.py --output experiments/payment-authorization-pilot/generated
```

The demo creates ephemeral mock keys and private temporary configuration/stores.
Its public outputs are `summary.json`, `admission-record.json`, and the original
`provider-receipt.json`. They contain synthetic requests, public verification
material, signed statements, recorded decisions, counters and toy balances.
Private keys, transport credentials and databases are not exported. Public keys
in an export are assertions by this same demo controller; an evaluator must adopt
trust separately. Fresh runs produce fresh keys and signatures.

The [CI workflow](../../.github/workflows/payment-authorization-pilot.yml) runs the
new tests, the original runtime suite and the public demo. Its artifact allowlist
contains only those three files. The separate
[retrospective evidence experiment](../payment-api-evidence/README.md) retains its
own schema and tests; it is not invoked to authorize a future payment.

## Validation scope

The suite contains **20 unique tests**. It covers eligible/distinct identities,
exact request and policy bindings, unusable or revoked status, an actual SQLite
lock, atomic proof/claim rollback, SIGKILL before and after commit, native client
concurrency, same-instance input snapshots, legacy claims and historical record
coherence. The same 20 also pass under optimized Python; repeated execution is
not an additional set of tests. The original runtime retains 28 test cases.

The healthy two-client scenarios wait for each worker's initialized readiness
before releasing both into the claim race, with a bounded two-second SQLite wait.
They still require one winner, one observed existing claim, and one POST/effect.
The deliberately short journal-lock failure cases and runtime defaults are unchanged.

The lock-timing test advances the client clock from a past interval to the present
while an actual writer lock is held. It checks when time is sampled, not an
authenticated clock. Corruption controls deliberately remove a SQL update guard
and recompute an outer digest; original signature/decision inconsistencies must
still prevent a supported historical admission. These are controlled fault
injections, not malicious-administrator isolation tests.

## Admission inputs and their limits

| Input | Checked binding | Trust limit |
|---|---|---|
| Operator-adopted policy | Exact context, permitted accounts and beneficiaries, amount limit and policy lifetime | This is a synthetic local policy, not bank policy or a customer's consent |
| Maker and checker statements | Verified signing key, role, exact request digest, policy digest and validity window | Two keys are insufficient: their adopted identity mappings must identify different persons |
| Adopted identity mapping | The verified public key's person, role, scope and lifetime | Person identifiers are configured test identities; real people and organizational independence are not verified |
| Signed status snapshot | Trusted status key, request/policy/approval bindings, status and claim-time freshness | The supplied snapshot is not a live fetch and cannot establish the latest real-world revocation state |
| Local claim time | Wall-clock time sampled after acquiring the SQLite write transaction | No authenticated external clock or clock-rollback protection is provided |

Caller-selected keys, person labels or a boolean such as `approved: true` cannot
replace these inputs. The gate takes canonical snapshots of the request,
configuration and original signed evidence; it does not retain a mutable pending
approval on an adapter instance. A new signature on altered payment bytes does
not repair an approval for the original request.

The policy's principal and credential identifiers are configured labels. This
pilot does not authenticate the caller's identity or require a separate agent
proof of key possession. The wrapper is invoked by its trusted local controller.

The policy's amount bound is per request. It is not an aggregate spending budget,
fraud detector or semantic duplicate detector.

## Claim ordering and retained evidence

1. Snapshot and validate the native request and per-call evidence.
2. Acquire the existing journal's `BEGIN IMMEDIATE` write transaction.
3. Resolve previously consumed operation/idempotency identities first. A repeat
   does not create another claim, refresh its admission record or send a POST.
4. For a new request, verify the persisted runtime generation, sample claim time,
   and evaluate the adopted policy, distinct approvers and signed status snapshot.
5. Only an authorized mock decision may insert its original evidence/admission
   record and the `CLAIMED` row in the same transaction. Commit before one POST
   opportunity. An interrupted or rejected transaction cannot retain just one.
6. Use the original runtime's provider receipt verification, monotone result
   storage and read-only reconciliation.

The companion authorization table is bound to the native claim and retains its
original record. SQL constraints/triggers help ordinary application use; they are
not tamper-proof storage against the host administrator. Signed approval/status
bytes retain their cryptographic verification value under the adopted keys.
The local admission record is not a separately signed gate attestation. Its
embedded public trust/identity context cannot establish its own external provenance.

## Read the two results separately

`state` describes the native payment outcome. `mock_admission` describes the
bounded synthetic prerequisite. It does not replace the offline verifier's four
claims or introduce a normative VAP verdict.

| Mock admission | New dispatch behavior | Interpretation |
|---|---|---|
| `AUTHORIZED` | May consume a new claim and obtain one POST opportunity | Required synthetic bindings held at the recorded claim time |
| `DENIED` | No new claim or payment POST | A verified condition contradicts the prerequisite, such as the same person in both roles or a revoked status |
| `UNKNOWN` | No new claim or payment POST | Required trustworthy evidence cannot establish admission, for example missing, unverifiable or stale status |

A blocked new submission returns `REJECTED`. Rejections before a claim are not a
durable denial-log service. Storage failure is not evidence of authorization or
nonexecution. An authorized admission followed by a lost response can still have
payment state `UNKNOWN`; only an authenticated matching provider receipt can
establish the supported terminal payment outcome.

Every result retains `business_authorization_verified: false`,
`production_gate: false`, `automatic_retry: false` and `synthetic: true`.
`AUTHORIZED` means the configured mock admission rules passed; it does not assert
independently verified human approval or production business authorization.

## Repeats, recovery and older claims

An identical request uses its original stored admission record and native claim,
including after its approvals expire or a later status reports revocation. This
is a historical result, not a fresh grant. Reconciliation issues no payment POST
and cannot release, replace or rearm the claim. Newly supplied statements cannot
overwrite the original authorization record.

Reading the record rechecks its original signed evidence and internal bindings
under the saved policy, identity/trust manifests, maximum status age and recorded
claim time. It must reproduce the saved decision. This historical coherence check
does not reauthorize the request under today's clock or authority state and does
not independently establish the recorded trust configuration.

`recheck_record(record_bytes)` is a pure offline helper for that limited replay.
Its `SUPPORTED` result explicitly includes `recorded_inputs_only: true`,
`independent_trust_established: false` and `current_authorization_asserted: false`.
These flags also apply when a record's embedded signatures verify successfully.

A claim created earlier through the raw runtime may lack an authorization record.
The wrapper preserves its payment state but reports the admission as unknown.
It never attaches a later approval to that historical claim. A matching provider
receipt alone does not demonstrate that the wrapper authorized the payment.

## What remains outside this pilot

The signed status may be old even within its permitted age. Revocation or expiry
may occur after the local claim and before the provider effect. There is no
continuous revocation guarantee, atomic authority-update-to-bank-execution
transaction, current authority query or cancellation of an already claimed send.

The provider authenticates its existing local transport credential; it does not
itself validate this new approval format. A holder of that credential can bypass
the wrapper by calling the raw runtime or provider. All test roles and keys are
controlled by the same operator and host user. This does not establish OS
isolation, privileged-bypass resistance or independent observation.

There is no independent collector/anchor, guaranteed denial-log collection,
enterprise identity integration, real approval UI, bank-specific settlement,
storage rollback or full power-loss guarantee. An authority that approves a new
pair of operation/idempotency IDs can still authorize a business duplicate.

This provides partial runtime evidence for the maker/checker and exact-request
questions in **PAY-02/PAY-03**, supplied-status checks in **PAY-04**, and composition
with the existing **PAY-06** recovery behavior. It does not establish every
PAY-01–PAY-08 acceptance condition, VAP conformance, a new profile, formal adoption,
independent reproduction or production readiness. See the
[payment proposal](../../proposals/payment-api-evidence/README.md).
