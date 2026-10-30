# Boundary review — controlled upload pilot

Review date: 2026-10-30. Status: **experimental and unadopted**. This is an
implementation review within the development task, not independent third-party
reproduction, production approval, or VAP/CAP conformance certification.

## Reviewed boundary

The pilot imports the unchanged sibling incident evidence assessor. Its runtime
owns a bounded immutable copy of the outgoing bytes, constructs the measured
target from the controller configuration, and verifies the original evaluator
pin before changing the observation frame. Existing signed policy and permit
records remain unchanged. A different payload digest, destination, tenant or
other mismatched permission therefore cannot gain authorization through the
new target hash.

Two distinct prerequisites govern the controlled route: authenticated assessor
`ALLOW`, then acknowledged local durable recording. The synthetic policy uses
`require_collector=false`; the pilot separately requires a SQLite WAL/FULL
dispatch-intent commit. This does not manufacture collector-health observations
or establish route completeness. The final permission check uses the gateway
clock after the commit and preserves a separate final assessment frame, so an
initially permitted request can expire before transport without rewriting its
admission history.

The journal claim is one-shot, including across concurrent callers and process
restart. A persisted intent is not an observed dispatch. The latter is added
only after the transport reports completion of its actual HTTP request call.
That completion describes the sender's call, not receiver processing. The local
receiver separately measures the raw body digest and length and signs its own
receipt. Missing, invalid or incorrectly bound responses leave the outcome
unresolved, and do not trigger a write retry.

The receiver's receipt check requires the pinned signer, exact typed fields,
request/subject/payload/length bindings and a receipt time between the transport
attempt and the postflight observation. The same check is used when rechecking
public exports. Even a confirmed local receipt leaves the unchanged assessor's
`remote_outcome` at `UNKNOWN`.

## Findings and regression coverage

The independent tests in `tests/test_boundary_review.py` cover ten areas:

1. Strict JSON and literal endpoint parsing, including duplicate keys, nonfinite
   values, invalid encodings, URL normalization variants and out-of-range ports.
2. Control-signature domain separation, key identity, record kind and signed
   body binding, using fresh keys and actual Ed25519 verification.
3. Rejection of a changed original evaluator pin before constructing the actual
   measured target.
4. Preservation of signed policy and permit records when bytes are measured;
   payload, tenant, endpoint and explicit-denial cases do not dispatch.
5. Current admission time and a second permission check after durable recording,
   including expiration between those two checks.
6. Separation of intent, attempted transport and completed dispatch; failed
   attempts do not manufacture `transfer.dispatch` observations.
7. Validly signed but malformed, mismatched, early, future or wrongly attributed
   receiver receipts, including a boolean used as a one-byte length.
8. Absence of exact fresh private-key values and raw payload bytes from public
   reports and journal contents; configuration diagnostics also hide the gateway
   secret.
9. Transplanted receipt details, inconsistent journal bindings and malformed
   stored JSON: none cause a resend or a fresh receipt-confirmation assertion.
10. Offline export consistency: mandatory assessment frames, reproduced
    assessments, receipt chronology and field shape, strict lengths, internally
    consistent attempt/receiver counts and the final frame's relationship to
    the captured request.

The offline recheck tests initially reproduced a weaker validation path than
the live gateway: missing frames and reports could be accepted, malformed or
chronologically impossible signed receipts could pass, and reported counters
were not derived from the retained reports and receiver rows. The repair uses
the shared receipt verifier, requires the relevant frames, and checks the
derived observation summary. A further regression covers an unrelated final
frame whose own assessment correctly denies permission; that frame cannot
support a claimed attempted execution of the original request.

Gateway tests separately cover commit acknowledgement shape, failures before
and after commit, concurrent claims, restarts, caller mutation, conflicting
request identifiers and failure to persist an otherwise valid response.
Transport tests distinguish deterministic parser/transport doubles from actual
HTTP execution.

## Validation record and required live execution

After the review corrections, the final local invocation discovered **39 test
methods: 35 passed and four live HTTP methods were explicitly skipped**. All
ten independent boundary-review methods passed, including the offline-recheck
regressions that failed before repair. The local command was
`python -W error::ResourceWarning run_tests.py`. No blocking implementation
finding remained within this declared boundary. Actual live execution and
retrieved CI results are recorded in [Execution records](results/README.md);
no local result substitutes for them.

The first actual CI run matched all 17 scenarios on both Python versions, but
inspection of the Python 3.14 logs found four unclosed test SQLite connections.
Those finalizer warnings had not failed unittest despite `-W error`. The test
connections now close explicitly while preserving transaction commits. A
separate audit of the 22 affected methods observed 216 connections created and
216 explicitly closed, with no unraisable exceptions. Runtime journal code did
not require a change. The file-backed runner now captures finalizer exceptions,
performs garbage collection before its final decision, and returns failure if
any were observed. Two subprocess regressions check clean success and failure
for an otherwise-passing test with an unraisable resource warning.

This workspace does not permit loopback socket creation. The independent
boundary tests therefore use explicitly named transport doubles while exercising
real signatures and SQLite state. They do not establish network delivery.
Four separate-process HTTP tests are explicitly disabled in the ordinary local
test invocation. `PILOT_NETWORK_TESTS=1` enables them and leaves runtime failures
fatal. A CI guard rejects a CI invocation that omits that flag.

The reviewed `.github/workflows/incident-upload-pilot.yml` runs on Ubuntu with
Python 3.12 and 3.14, sets `PILOT_NETWORK_TESTS=1`, and calls the file-backed
`run_tests.py --require-network` entry point. That runner rejects missing network
opt-in, any skipped test and captured finalizer exceptions. The workflow then runs all 17 actual loopback
scenarios, rechecks the exports, repeats the unchanged assessor tests and
catalogue, and retains generated evidence even when a later step fails.

The actual suite must run on an environment permitting the controlled loopback
processes. Its run fails if those processes cannot start; there is no fabricated
HTTP fallback. The suite compares actual receiver counters, measured digests,
gateway reports, source hashes and cleanup with the fixed scenario catalogue.
The CI run and its retained artifacts for the exact reviewed commit determine
whether live validation completed. An offline export recheck does not rerun the
HTTP exchange or independently authenticate the host's observations.

## Claim limits retained

- The controller, clock, gateway, receiver, local host and synthetic authority
  assignments are trusted. Fresh keys are ephemeral test authority, not real
  organizational identity or independently operated witnesses.
- SQLite FULL and successful acknowledgement establish the tested local storage
  ordering. They do not make the disk tamper-proof, provide an external anchor,
  or establish physical power-loss behavior on every storage system.
- No OS isolation or all-route prevention is claimed. The explicit
  unauthenticated receiver negative control demonstrates the outside-route
  bypass. Matching that expected result is not an overall security pass.
- No real provider, patient data or AI processing is used. The pilot establishes
  no external data deletion, retention or training-use result.
- No VAP/CAP core schema, event registration, standard requirement or conformity
  verdict is added by this application experiment.
