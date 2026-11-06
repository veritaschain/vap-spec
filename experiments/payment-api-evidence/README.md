# Payment API evidence experiment

**Status: unadopted, informative experiment.** [日本語](README-ja.md)

This is an offline verifier of deliberately synthetic payment evidence. It makes
the evidence distinctions in the [payment proposal](../../proposals/payment-api-evidence/README.md)
executable without a payment endpoint or real funds. It does not reproduce the
CRAFTY FALCON campaign, implement a bank adapter or establish VAP conformance.

The verifier evaluates signatures and the contents they bind. A valid signature
on a substituted beneficiary, a revoked credential or an observed bypass must not
turn that observation into an authorized payment.

## Four separate questions

| Claim | Meaning of `VALID`, within the caller's trust assumptions |
|---|---|
| `integrity` | Supplied evidence verifies under the separately configured keys for the required roles. This does not establish collection completeness or the truth of a signer's statement. |
| `authorization` | The observed dispatch is covered by the exact operation, policy, maker/checker identity and role bindings, approval windows and final credential-status observation. This is a retrospective evidence judgment at dispatch time. |
| `execution_match` | Authenticated dispatch and provider evidence bind the exact synthetic request and operation, with a matching terminal outcome. The separately reported outcome can be `failed` or `reversed`; `VALID` does not mean money settled successfully. |
| `control_state` | The signed route and collector observations support the declared configuration, recovery epoch and supplied-record coverage, at the recorded times and within the named scope. |

`INVALID` means a checked structural/signature failure or a contradiction in
authenticated evidence relevant to that claim. `INDETERMINATE` means necessary
evidence, trusted provenance, identity mapping, freshness or coverage is missing.
The verifier retains known contradictions even if some other evidence is missing.
An unverifiable assertion cannot establish its alleged underlying event.

These are experimental report labels, not normative VAP verdicts. The report has
no overall safety verdict, payment authorization command or VAP pass. It declares
`read_only: true` and `automatic_retry: false`.

## Run

Python 3.12 is used by the focused [workflow](../../.github/workflows/payment-api-evidence.yml).
Tests use `unittest` and `cryptography`. Test execution makes no network calls.

```sh
python -m pip install -r experiments/payment-api-evidence/requirements.txt
python -m unittest discover -s experiments/payment-api-evidence/tests -v
```

From this directory, inspect one generated report:

```python
from fixtures import make_fixture
from payment_evidence import canonical_json, verify_bundle

bundle, trusted_keys, identities, at = make_fixture("authorized")
report = verify_bundle(
    bundle, trusted_keys, identities=identities, evaluation_time=at
)
print(canonical_json(report).decode("utf-8"))
```

`python fixtures.py` prints the 24-case synthetic result matrix. The command-line
verifier also accepts separate `--bundle`, `--trust`, `--identities` and `--at`
inputs; trust public keys use lowercase raw-key hex in the JSON file. It writes a
report to stdout, returning `0` when all four evidence claims are `VALID` and `2`
otherwise. This exit status does not mean a payment succeeded: matching `failed`
or `reversed` outcomes can also have four supported evidence claims.

The API snapshots its inputs and does not read a clock, access a network, send a
request, retry a payment or change a ledger. Repeatedly checking the same bundle
does not consume its operation ID. Missing acknowledgment remains unresolved;
read-only reconciliation would need separate provider evidence.

## Trust, identities and exact request bytes

Trust keys, the identity directory and the evaluation horizon come from the
caller, outside the evidence bundle. The identity map is indexed by the verified
public key, so renaming a key ID cannot create another person. Maker/checker role,
tenant, environment and validity are checked. Two valid signing keys mapped to
the same person contradict the required separation; an absent mapping leaves the
identity question unknown.

Configured role keys are trusted for the caller's selected review context. The
verifier does not maintain a directory restricting each provider key to a
particular `provider_id`, or each policy key to a particular tenant. A key trusted
for a role can make statements for that role within this review. The caller must
not combine unrelated providers' or tenants' keys into a common authority pool.
Issuer-specific key authorization and key lifecycle/revocation are separate work.

All fixture signing seeds are public synthetic test data. The fixture producer
and its statements run in one process. Distinct fixture keys or person IDs do not
prove independent organizations, real identities, honest observers or trustworthy
clocks. A deployment would have to establish these properties separately.

The experiment has its own schemas and signature domain. Signatures cover the key
identifier and complete payload. References between records identify exact signed
envelopes. The restricted JSON encoding rejects duplicate object keys, floats,
non-NFC strings and ambiguous integer encodings; it is not an RFC 8785 implementation.

| Evidence slot | Caller-pinned role | Principal binding |
|---|---|---|
| `policy` | `policy_authority` | Allowed scope, amount/unit, configuration, epoch, provider and time window |
| `maker_approval`, `checker_approval` | `approver` | Exact operation and policy; independent caller identity/role mapping |
| `final_status` | `status_authority` | Credential state, exact approvals, operation, configuration and epoch |
| `dispatch` | `execution_observer` | Actual operation and request bytes, policy, approvals, final status, control record and time |
| `provider_receipt` | `payment_provider` | Operation, request, dispatch, provider/audience and outcome |
| `control` | `control_observer` | Named routes, operation, configuration, epoch and observation time |
| `collector` | `collector` | Exact retained signed records, known gaps and checkpoint/epoch |

Each signed payload also binds its evidence kind and run ID. The exact field
sets and type restrictions are the `*_SCHEMA` dictionaries in
[`payment_evidence.py`](payment_evidence.py). Fixture refresh helpers only issue
new synthetic statements; they must never be used to rewrite incident evidence.

The versioned synthetic request format binds the operation ID, tenant,
environment, audience, source account, beneficiary, exact amount and currency
unit, credential, configuration, policy, idempotency scope and recovery epoch.
The verifier compares actual request bytes with the approved operation and the
declared dispatched operation. This format is deliberately synthetic. It does
not decode arbitrary bank payloads, verify a beneficiary's real identity or assert
that a destination is appropriate.

Authorization is assessed for the **observed dispatch**, at its authenticated
time. The caller's evaluation horizon prevents treating later evidence as already
available. Later-dated signed observations are listed in `excluded_after_horizon`
and excluded from semantic judgments; their supplied signatures are still checked.
This uses the source's declared timestamp, not a proof of when evidence was actually
received. The final status observation and approvals must have the required
order and freshness at dispatch, and identity eligibility must also cover approval
issuance. A fresh snapshot does not close the interval
between checking a credential and executing a request.

The separately reported `settlement_confirmed` means a matching trusted synthetic
provider statement supports settlement in this report. It is not independent
confirmation of a bank transfer. `reported_status` can preserve a provider's
attributed assertion even where correspondence is not established and `status`
remains `unknown`.

## Coverage of the eight proposal groups

The suite exercises the following evidence distinctions, including unchanged
positive controls and freshly signed contradictory observations. It does not run
the full stateful adapter acceptance tests in the proposal.

| Group | What this experiment checks | What it does not establish |
|---|---|---|
| PAY-01 | Matching approval, dispatch, provider and scoped control statements can support the four separate claims. | Real settlement, safe destination or production readiness. |
| PAY-02 | Same-person maker/checker is contradicted; missing identity mapping is unknown. | Integration with an identity provider or independent governance. |
| PAY-03 | Changed beneficiary, amount, currency, tenant or environment can have valid signatures while contradicting approval and execution bindings. | Bank-specific decoding beyond the synthetic request format. |
| PAY-04 | Explicit pre-dispatch revocation differs from a missing or stale status observation. | Atomic check-to-execution enforcement or continuous revocation monitoring. |
| PAY-05 | An observed bypass contradicts control assumptions; a required unobserved route leaves coverage unknown. | Actual network/cloud isolation or exhaustive route discovery. |
| PAY-06 | Lost acknowledgment stays unknown on repeated assessment; a contradictory request binding is detected. | A durable consumption ledger, concurrent duplicate suppression, crash recovery or actual replay of a payment. |
| PAY-07 | HTTP 200 is not settlement; an authenticated receipt for another operation is a mismatch. Accepted/pending are distinguished from terminal outcomes. | Live bank reconciliation or independently observed money movement. |
| PAY-08 | Declared collection gaps remain visible; a verified old epoch or wrong retained-record binding is contradicted. | An actual collector outage, credential rotation, recovery execution or eradication of an intruder. |

Collector statements describe retained evidence and known gaps. They do not
recover records never collected, prove universal absence of omitted events or
serve as an independent external anchor. This experiment does not implement VAP's
Merkle anchoring, anchor continuity or completeness invariant. It cannot claim
VAP conformance merely because it uses Ed25519 and hashes.

## Relationship to existing work and next boundary

The implementation adapts small restricted-JSON and signature-checking patterns
from the [wallet evidence experiment](../wallet-authorization-evidence/README.md),
with its own payment schema and domain. Existing experiments and fixed evidence
archives remain unchanged. The
[pre-record gate](../pre-record-gate/README.md),
[control-state experiment](../control-state-evidence/README.md) and
[collector pilot](../incident-collector-pilot/README.md) illustrate different
bounded runtime experiments; their outcomes are not payment test results.

The next runtime step would need a controlled synthetic endpoint and a durable
consumption ledger, then restart/concurrency/lost-acknowledgment tests and read-only
reconciliation. Production use would additionally need bank-specific semantics,
trusted identity and receipt integrations, protected policy state, privacy and
retention design, independent collection, and review of privileged bypasses.
The school-alert/evaluation proposal remains a separate design workstream.

No real account identifiers, customer data, secrets, provider credentials or funds
are used. This experiment creates no new profile, normative requirement, regulatory
approval, certification or independent third-party validation.
