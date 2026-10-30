# Controlled incident upload pilot

**Experimental, synthetic, unadopted — version 0.1.0.**
This application-side pilot connects the unchanged
[incident evidence assessor](../incident-evidence-assessor/README.md) to an
actual controlled upload of immutable bytes to a separate local HTTP receiver.
It adds no VAP/CAP requirement and establishes no production or all-route guarantee.

[日本語実行ガイド](RUN-ja.md) · [Contract](CONTRACT.md) ·
[Acceptance catalogue](acceptance.json) · [Internal review](REVIEW.md) ·
[Execution records](results/README.md)

## What is measured

The gateway captures a bounded payload once as immutable bytes, calculates
SHA-256 over those raw bytes, and constructs the actual target using its trusted
route configuration. An old signed permit is preserved: substituting different
bytes does not silently issue a new permit. The evaluator frame uses the current
gateway clock, so a historical evaluation time cannot refresh an expired permit.

Sending requires both an authenticated assessor `ALLOW` and acknowledgement of
a committed one-shot intent in a local SQLite WAL/FULL journal. The permission
policy deliberately has `require_collector=false`; mandatory local recording is
an **additional pilot enforcement rule**. No fabricated collector-health time is
used to make the assessor report availability at a later transport instant.

The gateway checks permission again after the commit, just before invoking its
single transport call. The receiver computes its own digest and length from the
actual HTTP body, commits the measured result, and signs a separate pilot receipt.
The suite compares those observations. All data and keys are synthetic; private
keys are freshly generated and excluded from public reports and journals.

| Observation | Interpretation |
| --- | --- |
| `BLOCKED_WITHOUT_ATTEMPT` | This invocation did not enter transport |
| Durable `dispatch_intent` | A local one-shot claim exists; it does not prove sending |
| `body_send_completed` | The HTTP client's body-send call returned; not proof of remote processing |
| Receiver row | The local test process measured and stored a body digest/length |
| `RECEIPT_CONFIRMED` | Matching signed receiver statement was checked and its result stored |
| `OUTCOME_UNKNOWN` | Response or result persistence is unresolved; no automatic resend |
| `REPLAY_NO_SEND` | A prior claim prevents another transport invocation; stored receipt truth is not reasserted |
| `REQUEST_ID_CONFLICT` | The identifier is already bound to another measured action |

The unchanged assessor's `remote_outcome` remains `UNKNOWN`. Pilot receipt
confirmation is separately named and is not inserted as a new core verifier verdict.

## Reproduce on Linux

Use Python 3.12+ and a host that permits literal loopback sockets and child
processes. The killed-worker scenario requires POSIX `SIGKILL`. From the repository root:

```sh
python3 -m venv .venv-upload
.venv-upload/bin/python -m pip install -r experiments/incident-upload-pilot/requirements.txt
cd experiments/incident-upload-pilot
PILOT_NETWORK_TESTS=1 ../../.venv-upload/bin/python -W error::ResourceWarning run_tests.py --require-network
../../.venv-upload/bin/python -m upload_pilot run-suite --output generated
../../.venv-upload/bin/python -m upload_pilot verify-exports generated
```

The suite starts only its own local receiver processes, executes 17 measured
scenarios, exports public results and stops its processes. It rejects an existing
output directory, including a symlink. Preserve earlier results and choose a fresh
path for a later run. A network startup failure, case mismatch or failed cleanup
is not a passing result. Exit 0 requires all expected observations and the export
recheck; mismatch gives 1 and invalid/incomplete execution gives 2.

For restricted editing environments, run socket-free tests with:

```sh
../../.venv-upload/bin/python -W error::ResourceWarning run_tests.py
```

That explicitly skips the four actual HTTP test methods. Such a local result
does not establish HTTP execution. The dedicated CI sets `PILOT_NETWORK_TESTS=1`,
requires **zero skipped tests**, runs the actual 17-case suite on Python 3.12 and
3.14, rechecks exports, and reruns the unchanged assessor's tests and 23-case suite.
The test runner also treats resource warnings and captured finalizer exceptions
as failures, including exceptions reported only during garbage collection.

## Seventeen observed scenarios

| Case | Observation required by the test |
| --- | --- |
| UL-01 | Allowed bytes, including UTF-8, whitespace and non-text bytes, match the receiver's digest and length |
| UL-02–03 | Unapproved destination and wrong tenant produce zero gateway attempts and zero receiver calls |
| UL-04 | Changed bytes fail the previous permit's binding before transport |
| UL-05 | Expired permission cannot authorize current execution |
| UL-06 | Injected journal claim failure prevents transport |
| UL-07 | Receiver commits and loses the response; outcome remains unknown and retry does not resend |
| UL-08 | A validly signed response for another payload cannot confirm this upload |
| UL-09 | Caller mutation after capture cannot replace the owned outgoing snapshot |
| UL-10 | Permission expires during a real pre-send pause and the final check blocks sending |
| UL-11 | Repeated confirmed request produces only one receiver call |
| UL-12 | Reuse of an ID for newly authorized other bytes conflicts with the stored action |
| UL-13 | A 307 redirect is not followed |
| UL-14 | A deliberate unauthenticated receiver accepts a direct controller call after the gateway denied its own path |
| UL-15 | Concurrent identical calls consume one dispatch claim |
| UL-16 | Injected result-persistence failure leaves an unresolved result despite actual receiver acceptance |
| UL-17 | A worker is actually killed after committed intent; reopening the journal does not resend |

UL-14 is a deliberate negative control. Its expected bypass demonstrates that an
application gate does not control every network path. Matching that expectation
is not a security pass. UL-06 and UL-16 inject storage exceptions through trusted
harness subclasses; they do not simulate all physical disk or power failures.
UL-07 uses an actual receiver database commit followed by a dropped HTTP response.

## Evidence, state and transport boundaries

The original evaluator target pin is checked before the gateway constructs its
measured observation frame. Only actual bytes, configured route fields and
observation times are updated. Signed policy contents, permit validity, authorities
and key roles are not refreshed. Admission, final-gate and postflight frames are
exported separately and can be recomputed by the unchanged assessor.

Journal claims use an atomic transaction keyed by request ID. The request
fingerprint excludes the fresh observation clock, so repeating an identical call
cannot get another send merely by advancing time. Acknowledgements must match
the owned request, fingerprint, state and full snapshot. A failure after a claim
may leave a durable unresolved intent. There is no automatic retry, arbitrary
row reset, result overwrite or reconciliation write endpoint.

The gateway stores hashes, lengths, public signed records and decisions, not
payload plaintext or signing secrets. This is data minimization for the synthetic
experiment, not proof that a digest is anonymous. SQLite FULL commit acknowledgement
supports the tested local ordering; it is not immutable storage, external anchoring
or evidence of survival under every hardware failure.

Only the fixed `http://127.0.0.1:PORT/upload` destination is supported. The client
uses an IPv4 socket directly, sends one `application/octet-stream` body with an
explicit length, and performs no DNS lookup, proxy lookup, compression, redirect
follow or write retry. Request size is limited to 1 MiB; control JSON, headers,
duplicate names, lengths and unsupported encodings are checked. Receiver fault
modes and gateway hooks are constructor/controller controls, not HTTP request options.

The receiver authenticates the gateway dispatch signature and measured bytes;
it trusts the gateway's authorization decision. It does not independently decide
the publisher/provider policy. The trusted controller can read all ephemeral
keys, and all roles share one host user. A separate process is not a separate
security principal. No claim is inherited from the repository's distinct
[OS-isolation experiment](../os-isolated-gate/README.md).

## Outputs and rechecking

- `generated/cases/UL-NN.json`: public frames, assessments, receiver statements, actual counters and cleanup observations.
- `generated/summary.json`: expected/actual results, differences, source-file hashes, environment and per-case export hashes.
- `generated/runtime/UL-NN/`: local journal and receiver databases from that run; synthetic hashes/records only.

`verify-exports` requires the exact case inventory and recorded source snapshot.
It repeats signature, receipt, chronology and target checks; recomputes all stored
assessor frames; and cross-checks reported observations against exported reports
and receiver rows. Empty cases, missing frames, altered receipt scope, wrong
types and unrelated/denied final-gate frames cannot become successful rechecks.
The command uses the bundled synthetic evaluator trust. An external reviewer must
choose its own trusted authorities and determine whether the supplied observations
are credible. Hashes and self-contained test keys do not independently establish
the truth or completeness of the original HTTP run.

The existing [pre-record gate](../pre-record-gate/README.md) supplied useful design
precedents for one-shot claims and intent/receipt distinctions, but its text-only
`create_record` wire contract is different. This pilot imports only the unchanged
incident assessor and retains its own local binary transport contract.

Remaining work includes production identity and policy sources, secure transport,
an enforced network boundary, real provider adapters, key lifecycle management,
privacy/retention controls and independently anchored observations. No legal
compliance determination or normative adoption is made. The repository's
[CC BY 4.0 license](../../LICENSE) applies.

Implementation references: [Python HTTP client](https://docs.python.org/3.12/library/http.client.html),
[multiprocessing](https://docs.python.org/3.12/library/multiprocessing.html),
[SQLite synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous).
