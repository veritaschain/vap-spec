# Experimental pre-record gate and evidence adapter

**Research experiment, unadopted. No formal proposal number or target release is assigned.**
This is a product-side execution experiment, not a VAP v1.2 execution-control requirement.
It builds on merged [PR #10](https://github.com/veritaschain/vap-spec/pull/10), baseline
`71d22b7b3501952cb23bcb76e665e5cfb7e6fa74`, and does not change that verifier, the specification,
DOC-SYNC, K3, or the declared-scope proposal. Integration does not constitute normative adoption.

One operation is supported: `create_record` at the logical target `sandbox/records`, with one synthetic
text argument. The external API is a loopback mock with a separate process and SQLite database.
No real service, real business data, production credential, or external write is involved.

## Run and inspect

Python 3.12 or 3.14 on macOS/Linux is supported by the experiment; SIGKILL cases are POSIX-specific.
From this directory, create a virtual environment and install the pinned sibling requirements:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m record_gate run-suite
```

That single suite command starts temporary services, executes **15 gate scenarios**, compares them with
`acceptance.json`, writes public evidence/reports to `generated/`, measures ten normal operations, and stops
the services. Nonzero exit means execution or expectation comparison failed. A matched negative-control
scenario means a broken guarantee was correctly exposed; it does not mean the insecure backend is safe.
These 15 scenarios are separate from PR #10's 14 declared-scope scenarios.

Additional checks:

```sh
.venv/bin/python -W error::ResourceWarning -m unittest discover -s tests -v
.venv/bin/python -m record_gate verify-exports --output generated
```

The offline command verifies exported signatures, authorization bindings, native backend receipts,
Merkle proofs and both verifier reports without rerunning the gate. It uses the bundled **mock trust
configuration**; an evaluator must decide which authorities to trust. Digests detect artifact changes,
not independent provenance. Fresh suite runs generate fresh test keys, so signature bytes and artifact
hashes change. No private keys are included in reports. See [RUN-ja.md](RUN-ja.md) for Japanese guidance
and [results/README.md](results/README.md) for the recorded execution.

## Roles and ordering

| Role | Responsibility and retained material |
| --- | --- |
| Synthetic authority | Signs a credential, delegation, exact-operation approval and revocation snapshot |
| Agent | Possesses its request-signing key; signs the operation and token digests; local logs are untrusted |
| Gate | Verifies authority signatures and agent proof of possession; holds the dispatch credential |
| Audit process | Holds its own signing key; stores signed events and operation state in a separate database |
| Mock backend | Requires gate signature plus audit dispatch permit; atomically records one effect per operation ID |
| Evidence adapter | Rechecks recorded authorization and backend signatures, then supplies original audit envelopes to PR #10 |

The gate derives subject, delegator and approver from verified authority-issued claims, not `agent_id`
or a `human_approved` flag. Each token's audience, validity, scope and revocation status are checked.
Approval binds the exact operation digest and delegation digest. Agent proof binds the intent and all
three token envelopes. Authorization is checked again just before claiming dispatch.

The ordered steps are:

1. Validate request, credential, delegation, approval and the trusted revocation snapshot.
2. Audit transaction stores the exact request, authorization context and signed pre-record. Wait for its signed ack.
3. Compare actual dispatch target/arguments with the recorded intent and refresh authorization checks.
4. Audit transaction atomically claims dispatch, appends a signed dispatch-intent event and commits before returning a permit.
5. Send one gate-signed request with that exact permit to the fixed loopback backend.
6. Verify the backend's signed, exact-operation receipt and durably record it before reporting confirmed success.

The control envelope uses domain `pre-record-gate-experiment/1` and Ed25519/JCS. Audit events preserve the
existing research adapter's signature domain. Hashes and signatures are computed from bytes; input
booleans such as `signature_valid` never grant validity. The adapter independently repeats authorization
checks under the **recorded synthetic clock and signed status snapshot**, and checks the nested backend
receipt under a separately supplied mock backend public key. It cannot prove that the clock was accurate
or that the revocation list represented real-world state.

SQLite uses WAL, `synchronous=FULL` and `fullfsync=ON`. Acknowledgments follow commit. Process crash and
restart recovery is tested; storage-device lies, corruption, full power loss and backup rollback are not.
The audit key's signature attests to an acknowledgment by the trusted audit process, not physical storage
survival under every fault. See SQLite's [synchronous documentation](https://www.sqlite.org/pragma.html#pragma_synchronous).

## States and recovery

| Stored state | Interpretation | Recovery behavior |
| --- | --- | --- |
| No pre-record | Persistence unconfirmed; no dispatch permitted | Repair audit service and explicitly submit again |
| `prepared` | Pre-record exists, no dispatch claim | Not success; explicit resubmission of the identical authorized request may claim dispatch |
| `dispatch_intent` | A worker claimed dispatch; sending/completion may be unknown | Repeating the gate call does not send; use read-only reconciliation |
| `result_unknown` | Response invalid/missing or completion unconfirmed | Retain evidence; no automatic write retry; use read-only reconciliation |
| `confirmed_success` | Exact-operation backend receipt verified and durably stored | Return stored result without another write |

A missing lookup receipt is **not proof of nonexecution**. After a claimed dispatch it remains unknown,
even when the test harness knows that the worker was killed before sending. If result persistence fails,
the prior dispatch-intent event is the durable unresolved record; the report explicitly says the separate
unknown-outcome event was not persisted. Reconciliation is an operator-facing trusted function, not an
agent-supplied replacement authorization. It queries the backend and records a valid matching receipt;
it never issues a write.

The mock backend commits operation ID, exact argument digest and effect receipt in one transaction.
Replaying the same ID/intent returns the same receipt; a changed intent is rejected. Its state has no
expiry in this experiment. These semantics cannot be assumed for a real API or after database loss.
The rationale follows AWS's [idempotent API guidance](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/).
There is no generic exactly-once claim and no automatic write retry policy for real services.

## Verifier connection and interpretation

Before activity, the harness signs a fixed scope containing three known **evidence obligations**:
request, dispatch intent, and confirmed external result for the one operation. This is not a claim to
enumerate future events. Its scope receipt and all anchor receipts are simulated with an explicit
synthetic timeline; all receipt/export keys are controlled by the same harness operator.

The adapter preserves audit events' original signed bytes. It rejects a forged nested backend receipt,
wrong subject assertion, mismatched dispatch arguments, wrong operation binding, duplicate event ID or
invalid predecessor ordering before invoking the unchanged verifier. The native backend receipt proves
only what the trusted mock backend attests; it is not an independent external observation.

Both modes run on the same evidence:

- `vap-v1.2`: existing cryptographic/committed-set checks; experimental scope is not applied.
- `experimental-scope`: the same checks plus unadopted declared-evidence fulfillment.

For successful completion, the three declared records can be `met`. For interrupted or unresolved
operations the submission/source closure remains pending, so fulfillment is `indeterminate`, even when
all submitted signatures verify. A final submission that lacks the required result is `not_met`, without
claiming the underlying action did not happen. A dispatch-intent record does not prove network dispatch.
There is no aggregate “VAP PASS,” complete-conformance claim, or assertion that the verifier stopped an API call.

## Tested boundary and remaining limitations

The suite covers the seven requested conditions plus concurrency, lost acknowledgment, outcome-store
failure, dispatch-store failure, same-ID/different-intent reuse and an intentionally insecure backend.
See `acceptance.json` for every expected result, and `tests/test_gate.py` for signature/binding regressions.
Storage outage is tested both by stopping the audit process and by explicit trusted-harness fault injection.
Response loss occurs after a real mock backend database commit. Crash cases actually SIGKILL the gate
worker and restart the killed audit process. Deleting agent-local files preserves the separate audit database.

**The isolation is by application role and process, not an OS security boundary.** All services and the
trusted harness run under one host user. The harness creates and can read every test key. A malicious
process with that user's filesystem access, root access, or stolen gate/audit key can defeat the boundary.
Docker/container isolation, separate service identities, key management, egress control and privileged
attacker resistance were not tested. Direct unsigned and agent-signed API calls are blocked by application
credentials; the network path itself remains reachable. The insecure-backend negative control deliberately
allows bypass and reports the guarantee as false.

Authorization is a custom synthetic authority model, not production OIDC, enterprise delegation or human
approval integration. The clock is fixed test input. There is a revocation/expiry race after the final check;
no real-time continuous revocation guarantee is made. There is no token rotation, trust distribution,
secret provisioning, permit expiry, secure transport, denial-log service, queue or recovery UI. Rejections
before persistence may only appear in the caller's result; they do not have guaranteed durable denial logs.
Request plaintext and synthetic credentials are recorded; a production privacy/retention design is absent.

Audit outage intentionally stops the managed operation. Restarting services preserves their existing
SQLite stores; it does not justify deleting them or generating a new operation ID for an unresolved action.
A production pilot needs separate identities/storage, verified egress boundaries, real authority/approval
integration, storage failure and restore tests, external receipt infrastructure, and an agreed recovery policy.
The ten latency samples report local pre-dispatch overhead and full duration, excluding startup. They are
not capacity tests, a production SLA, a claim of independent reproduction, or evidence of buyer demand.
