# Controlled payment evidence collector pilot

**Status: unadopted, informative experiment.** [日本語](README-ja.md)

This pilot adds an actual loopback collector process and separate SQLite store to
the [mock authorization pilot](../payment-authorization-pilot/README.md). It sends
the original admission record before the controlled payment POST and the original
provider receipt after a supported terminal outcome. All accounts, approvals,
keys and balance changes are synthetic. No bank or external service is connected.

The collector stores the complete selected evidence bytes, not just their hashes.
Its separately configured key signs an acknowledgment bound to those bytes and
their payment request. A fresh challenge-bound readback checks the retained record
at one observation. All processes and keys still belong to the same operator and
host user; separate processes do not establish independent custody or OS isolation.

## Run and inspect

From the complete repository checkout, with Python 3.12 and native subprocess and
loopback networking support:

```sh
python -m pip install -r experiments/payment-collector-pilot/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/payment-collector-pilot/tests -v
python -O -W error::ResourceWarning -m unittest discover -s experiments/payment-collector-pilot/tests -v
python -W error::ResourceWarning -m unittest discover -s experiments/payment-authorization-pilot/tests -v
python -W error::ResourceWarning -m unittest discover -s experiments/payment-runtime-pilot/tests -v
python experiments/payment-collector-pilot/run_demo.py --output experiments/payment-collector-pilot/generated
```

The [CI workflow](../../.github/workflows/payment-collector-pilot.yml) runs the new
suite normally and under optimized Python, then rechecks authorization and runtime
behavior. A public demo exports only `summary.json` and `evidence-bundle.json`.
The artifact allowlist excludes private keys, bearer credentials, configuration
files and databases. Temporary service files are private and are removed when the
demo exits. CI keeps the selected public artifact for 30 days.

The [preserved 6 November 2026 run](../../research-distribution/2026-11-06-payment-collector/README.md)
retains its original ZIP, complete public evidence, pinned source subset and
captured CI records separately from that expiry, with an offline historical
recheck. It covers one selected run; independent reproduction is not established.

The demo exercises five scenarios with separate temporary service stores. Counts
below refer to payment POSTs and effects; evidence collection has its own counters.

| Scenario | Financial result | Payment POSTs / effects | Custody distinction |
|---|---|---|---|
| Healthy collection | `SETTLED` | 1 / 1 | Original pre-dispatch prerequisite and outcome evidence retained |
| Collector stopped before submission | `UNKNOWN` | 0 / 0 | Later evidence recovery cannot establish the original prerequisite |
| Collector commits, ACK is lost | `UNKNOWN` | 0 / 0 | Restart can recover the same ACK without resuming payment |
| Provider commits, response is lost | `UNKNOWN` → `SETTLED` after provider GET | 1 / 1 | The original provider receipt is collected separately after reconciliation |
| Collector stops after the provider response | `SETTLED` throughout | 1 / 1 | Outcome custody is unresolved until explicit evidence recovery |

## Validation scope

The suite contains **25 unique tests**, run normally and under optimized Python.
The optimized run repeats the same cases. Existing suites retain 20 authorization,
28 native-runtime and 57 retrospective-evidence tests.

The new cases cover actual service outages, SQLite locks, process SIGKILL,
commit-with-lost-response recovery, concurrent initialized workers, exact original
byte retention, malformed/bound-to-another-record replies, historical versus fresh
observations, epoch changes, unreadable local storage, caller input mutation and
the absence of retroactive pre-dispatch coverage. Worker readiness and explicit
barriers establish the intended order; missing native process/socket capability
is a failure, not a skipped or simulated pass.

Reply-fault cases alter or re-sign bytes at a trusted receive boundary **after** a
real collector exchange. They exercise rejection rules without asserting a real
network compromise. The fresh-missing case uses an explicitly empty test collector
store under the same ephemeral key; it measures historical-versus-current status,
not rollback resistance. The demo's inspection of the collector store after an ACK
loss is a same-controller observation, separate from the client's knowledge.

## Ordering and the consumed dispatch opportunity

| Step | Required behavior | Failure consequence |
|---|---|---|
| Local admission | The existing synthetic approval checks and original admission record commit atomically with the native `CLAIMED` row | A failed transaction permits no POST and does not assert a persisted claim |
| Admission collection | Send the exact committed record to the collector outside the journal write transaction | The committed claim remains consumed even if collection is unavailable |
| Collection prerequisite | Verify the pinned collector signature and exact bindings, obtain a fresh readback, and retain the observations locally | Missing, malformed, wrong or unpersisted evidence cannot permit the payment POST |
| Payment attempt | Only the invocation that created the claim can reach its one payment POST opportunity | Repeats and recovery cannot resume that opportunity |
| Native outcome | Verify and retain the original provider receipt using the existing runtime | A missing or unverifiable receipt leaves the payment unresolved |
| Outcome collection | Collect the original verified provider receipt separately | Collection failure does not erase a supported `SETTLED` or `FAILED` payment outcome |

The trusted pre-dispatch extension is code configuration, never a field in an
untrusted payment request. It runs only for a newly committed claim. Network I/O
does not take place inside the transaction that commits admission and claim.

There is intentionally no distributed transaction spanning the journal,
collector and provider. Process death after any committed claim may leave an
unresolved payment, including when the test controller knows no POST occurred.
Conservative recovery retains that uncertainty and never rearms the claim.

## Read payment, admission and custody separately

The native `state` retains its existing meaning. `mock_admission` remains the
original historical decision under the recorded synthetic policy and supplied
status snapshot. Collector evidence is a separate observation.

| Observation | Supported interpretation | Unsupported inference |
|---|---|---|
| Original collector ACK verifies | The configured collector key attested to accepting those exact bytes | The service is available now, or every relevant event was collected |
| Fresh matching readback verifies | That service returned the requested record for this challenge | Continuous availability or physical storage survival |
| Original pre-dispatch prerequisite was saved | The controlled invocation recorded its collection prerequisite before its POST opportunity | A payment was actually sent or settled |
| Admission bytes are recovered later | Those original bytes can now be retained and acknowledged | They were collected before the original payment attempt |
| Native outcome is `SETTLED`, outcome custody unresolved | A supported provider outcome exists; its collection confirmation is missing | The payment failed or should be sent again |
| Fresh signed lookup says not found | The collector did not return the record at that query | The record never existed, the payment never happened, or deletion is proven |

Every native result continues to declare `synthetic: true`,
`business_authorization_verified: false`, `production_gate: false` and
`automatic_retry: false`. No combined production authorization or VAP-conformance
verdict is introduced.

The `PRE_DISPATCH`, `POST_EFFECT` and `HISTORICAL_RECOVERY` labels belong to the
local controlled code path. The collector signs acceptance of selected bytes;
it does not independently attest to their timing relative to a provider effect.
The original prerequisite marker is a local journal record, not a separately
signed gate attestation. A journal that cannot be read reports that prerequisite
as `UNKNOWN`; `NOT_RECORDED` requires a successful query showing no marker.

## API effects

| Method on `CollectedAdapter` | Network behavior | Local meaning |
|---|---|---|
| `submit(request, evidence)` | Only the new claim owner may collect evidence and make the one payment POST; repeats make no network calls | Preserve the original admission, claim and custody history |
| `read_status(request)` | None | Read the financial result, historical admission and historical custody |
| `read_custody(request)` | None | Reverify saved observations; no present-retention assertion |
| `reconcile(request)` | Provider GET only when an unresolved claim needs lookup | Retain a verified provider result; do not collect it implicitly |
| `recover_evidence(request)` | Collector POST and fresh GET only | Append historical evidence observations; never create the original prerequisite marker |
| `check_custody(request)` | Fresh collector GETs only | Return challenged observations without changing payment or local custody records |

The local custody reader examines at most the latest 128 observations plus the
original prerequisite observation if it falls outside that window. Its returned
observation list and invalid-record count are bounded inspection results, not an
inventory or completeness proof for the entire journal.

## Recovery preserves identities and original bytes

Repeated payment submission uses the original consumed claim. Provider
reconciliation may query the provider; it never sends a payment POST. Evidence
recovery is an explicitly separate operation: it may submit the exact original
record to the collector and query the collector, but cannot create or reset a
payment claim or call payment submission.

Collector insertion is idempotent for the same request, evidence phase and exact
bytes. Repeating it recovers the original acknowledgment instead of manufacturing
a new historical collection time. Conflicting bindings cannot overwrite the
record. Admission and provider-outcome evidence are distinct phases, so an ACK
for one cannot satisfy the other. An epoch or configuration change is bound into
the request; it does not reset consumed operation or idempotency identities.

Older claims made through the raw runtime may have no admission record. Claims
made through the authorization pilot may have no original collection prerequisite.
Later recovery does not invent either historical record and cannot promote later
collection into pre-dispatch coverage. Existing signed records are reverified on
read under the configured pins; a stored status label is not sufficient.

## Verification and trust limits

The collector acknowledgment binds the collector identity, evidence phase, exact
request and retained record. Readback also binds a fresh caller challenge. Original
ACK and evidence bytes are preserved across collection retries and process restart.
The client adopts the collector and provider public keys separately from response
content. Keys included in a public demo bundle remain declarations by the demo
controller; they cannot establish their own independent provenance.

The admission record retains its existing historical coherence check. Its embedded
policy, identity map and approval keys are not transformed into independently
trusted human approval merely because a collector accepted the record. The
collector does not observe an attacker's internal reasoning or authenticate actual
people behind the synthetic roles.

The gate still evaluates supplied status at claim time. Collector latency adds to
the interval between that check and the payment effect. A signed status can already
be stale in reality, and expiry or revocation can occur during that interval. This
pilot does not create a live authority query, continuous revocation enforcement or
an atomic approval-to-provider-effect guarantee.

## Scope of the experiment

This is additional, partial runtime evidence for the custody and outage questions
in **PAY-08**, composed with the existing **PAY-06** recovery behavior and the mock
approval pilot. The [payment proposal](../../proposals/payment-api-evidence/README.md)
remains unadopted; its full eight-group acceptance contract has not been executed.
The separate 57-test retrospective verifier and its fixtures retain their own
schema and role. No future outcome is fabricated to run that verifier before a
payment.

The provider still authenticates its existing local bearer credential. A holder
of that credential can bypass these wrappers through the raw runtime or provider.
Collection is a prerequisite on this controlled application route, not exclusive
provider enforcement. SQL constraints and separate processes do not protect
against the host administrator or a process with the same user's access.

Selected full records contain synthetic request and approval data. There is no
production privacy, redaction, retention/deletion or access-control design. There
is no independent anchor, collector-wide completeness checkpoint, guaranteed
denial-log collection, authenticated external clock, key lifecycle, rollback or
full power-loss guarantee, intrusion-eradication proof, real bank settlement,
independent reproduction or production-readiness claim.
