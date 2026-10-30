# Controlled collector prerequisite pilot

This informative experiment adds a real, separate loopback metadata collector to
the controlled upload path. It measures the collector outage gap identified for
**UP-08** in the [implementation handoff](../../proposals/incident-evidence-bindings/integration/COVERAGE.md).
It does not change the historical crosswalk, the original 23-case proposal, any
of the 154 frozen execution inputs, or the 53-case capture. VAP's normative
baseline remains v1.2 Draft 3; this experiment is not a conformance result.

The gateway uses a policy with `require_collector=true`. Before one payload
attempt, it requires an authenticated receipt for the exact signed intent
metadata, a fresh challenge-bound readback, and an allowed assessment under the
current policy, permit and gateway-key interval. The collector stores hashes,
identifiers and signed metadata only. A separate upload receiver measures the
actual payload bytes.

## What the experiment distinguishes

| Observation | Bounded conclusion |
|---|---|
| Collector unavailable to the gateway | Payload remains unattempted on this controlled path |
| Collector commits, then drops its response | Gateway acknowledgement remains unresolved; payload remains unattempted |
| Same collector restarts and answers a fresh query | The original metadata receipt can be recovered; payload is not resumed |
| New policy-bound request after recovery | A fresh request may proceed after all prerequisites are checked again |
| Collector signs a receipt or nonce for another binding | Response does not authorize payload transmission |
| Final prerequisite check allows, then receiver confirms bytes | Controlled payload receipt is established under controller-owned keys; later exact-time collector health can remain unresolved |

The local journal claims a request ID before collection. A **committed** claim
remains consumed even if its acknowledgement or later result is lost. A failed
pre-commit claim blocks the current call; it is not claimed to have persisted.
No automatic retry exists. Reconciliation performs only a status query; it never
resets a journal row, repeats collection, resumes or sends a payload. A later
upload requires a new explicitly authorized request ID.

## Time and evidence

The gateway records the genuine time at which it verifies the final collector
response. The unchanged assessor requires `checked_at == operation_at` for the
collector-health prerequisite. The payload transport then records its own actual
dispatch time. The earlier health check is **not rewritten** to that later time.
Accordingly, a successful case intentionally retains:

- Final-gate `transfer_authorization=ALLOW`.
- A single actual payload attempt and a verified matching receiver receipt.
- Postflight `observed_action_authorization=REVIEW`, because no exact-time health
  observation exists at the later dispatch instant.

This is a point-in-time prerequisite, not continuous availability or an atomic
collector-check-and-send operation. A metadata receipt is not proof of payload
receipt, egress, model use, retention or deletion.

For a measured transport failure, negative gateway health describes absence of
usable reachability/acknowledgement on this exchange. It does not establish
physical or global service death. A malformed or wrongly bound response cannot
create a trusted remote-state assertion. Signed `NOT_FOUND` refers only to the
fresh query time, never the complete history of collection.

## Finite scenario catalogue

[acceptance.json](acceptance.json) defines 18 expectations before execution:
normal operation; actual stopped collector; pre-commit connection drop;
post-commit lost acknowledgement and restart; fresh request after recovery;
collector stop before final readback; real permit expiry; wrong receipt;
wrong nonce; local claim failure; tenant mismatch; replay; conflicting request
binding; concurrent callers; receiver acknowledgement loss; caller mutation;
lost acknowledgement of a committed local claim; and outcome-write failure.

Each case exports original signed control messages, actual exchange observations,
owned evaluator frames, public key pins, and separate collector/receiver row and
call counts. Exports contain no signing secrets or payload plaintext. Temporary
databases are not included in the public CI artifact.

## Run and recheck

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -W error::ResourceWarning run_tests.py
.venv/bin/python -m collector_pilot run-suite --output generated --print-summary
.venv/bin/python -m collector_pilot verify-exports generated/public \
  --expected-summary-sha256 THE_HASH_FROM_THE_TRUSTED_RUN
```

Run from this directory in the complete repository checkout. The process/network
tests and all scenarios must run; missing socket capability is a failed run,
never a skip or simulated network pass. Python 3.12 and 3.14 are exercised by
[CI](../../.github/workflows/incident-collector-pilot.yml).

The verifier performs no network actions. It validates the supplied summary hash,
raw case hashes, exact source inventory, signatures, bindings, timing consistency,
unchanged assessor results and finite expectations. Obtain the expected summary
hash through a separately trusted channel. Reading a sidecar from the same
untrusted capture does not establish its origin. Keys inside the capture remain
the same controller's declared keys; rechecking is not independent reproduction
or independent proof that observations occurred.

## Implementation and remaining limits

- [CONTRACT.md](CONTRACT.md): protocol, one-shot/recovery rules and timestamp semantics.
- [RUN-ja.md](RUN-ja.md): Japanese interpretation and execution guide.
- [REVIEW.md](REVIEW.md): threat boundaries and verification decisions.
- [dependency-lock.json](dependency-lock.json): exact 154-input frozen inventory.
- [results/](results/): CI provenance when a capture has been published.

The collector and receiver are separate processes controlled by the same operator.
SQLite WAL/FULL commit and readback are local durability assumptions, not tested
power-loss survival or external attestation. The reused receiver trusts the
gateway's dispatch authorization and does not separately enforce collection.
Other routes, production identity onboarding, key revocation, remote anchoring,
provider deletion and legal compliance remain outside this measurement.
