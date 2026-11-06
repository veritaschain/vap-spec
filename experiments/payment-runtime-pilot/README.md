# Controlled payment runtime pilot

**Status: unadopted, informative experiment.** [日本語](README-ja.md)

This pilot runs a real HTTP service on `127.0.0.1` with a separate SQLite store
for local toy balances. A client adapter durably claims a request before one
provider POST. Repeated submissions and read-only reconciliation use the saved
identity and original signed receipt. No bank, real funds or external service is
contacted.

The pilot starts **after the trusted caller's business authorization**. It does
not verify maker/checker approval, credential revocation, a live authorization
policy or collector availability. Every result declares
`business_authorization_verified: false` and `automatic_retry: false`.
The provider's local transport credential is not a human approval or business
authorization proof.

An additive [authorization pilot](../payment-authorization-pilot/README.md) wraps
this primitive with a synthetic maker/checker prerequisite and an admission record
committed with a new claim. It has a separate, limited trust model and report.
Calling this base adapter directly still performs no business authorization check.

The [offline payment evidence verifier](../payment-api-evidence/README.md) remains
a separate retrospective tool. This runtime never authorizes a new request by
inventing its future dispatch observation or provider receipt. It has a native
experimental request/receipt protocol and does not claim that these reports are
already VAP Evidence Packs or the offline verifier's report schema.

## Run and inspect

Python 3.12, `cryptography`, SQLite and native loopback/process capability are
required. The SIGKILL tests target POSIX hosts. Missing capability is a failed
run, not a skipped or simulated success.

```sh
python -m pip install -r experiments/payment-runtime-pilot/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/payment-runtime-pilot/tests -v
python experiments/payment-runtime-pilot/run_demo.py --output experiments/payment-runtime-pilot/generated
```

The demo creates temporary provider and client stores, an ephemeral signing key
and a local transport credential. The provider commits one toy transfer and
deliberately closes its connection before returning the acknowledgment. The
adapter remains `UNKNOWN`. Submitting the same request again does not send it.
A GET lookup obtains the stored receipt and establishes `SETTLED` for the local
mock effect. A final submit returns that same saved receipt without another
provider call.

The public output consists of `summary.json` and the original
`provider-receipt.json`. It contains the synthetic request, public key, result
states, receipt digest, actual provider counters and toy balances. It excludes
private keys, transport credentials and databases. The included public key is a
statement by this demo controller, not independently established provenance.
Fresh runs use fresh keys and produce different signatures.

The focused [CI workflow](../../.github/workflows/payment-runtime-pilot.yml) runs
the process tests and demo, then preserves only those two public files.

The healthy two-client concurrency test waits for both workers to finish their
own initialization before releasing their claim attempts. It uses a bounded
two-second SQLite wait and retains strict one-claim/one-POST/one-effect checks.
This separates that scenario from the deliberately short lock-failure tests;
it is not a latency guarantee or a change to runtime timeout defaults.

## What is measured

| Measurement | Meaning |
|---|---|
| Provider POST attempts | Actual write requests received by the mock service; count separately from effects |
| Provider lookup attempts | Read-only payment-status queries; they do not debit/credit accounts or reset client claims |
| Payment rows and effects | Durable mock outcomes versus successful local transfers; a failed payment can have a receipt and no transfer effect |
| Toy balances | Source and beneficiary values read from the provider's actual SQLite store |
| Client journal state | A consumed dispatch identity and any authenticated result subsequently stored |

The lookup can update observation counters, and the adapter can save its retrieved
result. “Read-only reconciliation” means it does not perform another payment
write, alter balances or clear consumption state.

## Request identity and persistence

The consumption namespace is the tuple of tenant, environment, API audience and
idempotency domain. Within it, **both operation ID and idempotency key are unique**
and immutably associated with the exact canonical request. The request also binds
configuration digest, recovery epoch, source account, beneficiary, integer amount,
currency and unit. Amounts use canonical decimal strings and bounded exact integer
arithmetic, with no floats or implicit currency conversion.

| Repeated input | Behavior |
|---|---|
| Same operation, key and bytes | Return stored result or unresolved state; no new client POST |
| Same operation, another key | Conflict; the original claim remains |
| Another operation, same key | Conflict; the original claim remains |
| Same identity, changed amount, beneficiary or other bound content | Conflict |
| Same identity, updated configuration or recovery epoch | Does not create a new consumption namespace or clear a claim |
| Both IDs changed | A distinct request; this pilot cannot recognize a business duplicate solely from semantic similarity |

The adapter and provider have separate databases. `BEGIN IMMEDIATE` and unique
constraints choose one claim winner among concurrent clients. The claim commits
before transport. A provider transaction atomically stores its immutable request,
stable signed result and, on success, the debit/credit effect. An identical direct
provider replay returns the same receipt without another effect; the provider's
POST counter still exposes the replay.

SQLite uses WAL and `synchronous=FULL`. These are the local storage assumptions
for the process-crash tests; they do not establish survival of dishonest storage,
physical power loss, database deletion, backup rollback or restored old snapshots.
See SQLite's primary documentation for
[transaction behavior](https://www.sqlite.org/lang_transaction.html) and
[synchronous modes](https://www.sqlite.org/pragma.html#pragma_synchronous).

Context and provider identity/key bindings are persisted. Opening an existing
store under an incompatible context fails. A provider can restart on another
ephemeral loopback port while preserving its database and verification identity.
The consumption namespace excludes the recovery epoch and transport credential,
so rotating them does not reset an existing payment identity. Historical lookup
uses the preserved original request. This is not key lifecycle or credential
revocation enforcement.

Generation checks fence new claims and new provider effects inside their respective
database transactions. A generation change cannot atomically revoke an already
claimed in-flight request across the client and provider. There is no distributed
check-to-use or continuous revocation guarantee.

## State and failure boundaries

| Client result | Interpretation and next action |
|---|---|
| `SETTLED` | A matching authenticated native receipt for a local mock transfer was durably saved; return it on repeats |
| `FAILED` | A matching authenticated terminal mock failure was saved; do not treat it as settlement |
| `UNKNOWN` | The claimed operation's result is unresolved; use explicit read-only reconciliation, never automatic write retry |
| `CONFLICT` | A consumed identity is associated with different content or another alias; keep the original row |
| `REJECTED` | Input or configured scope is unsuitable for this pilot; this does not determine a remote payment's history |
| `JOURNAL_UNAVAILABLE` | Necessary local persistence could not be confirmed; do not infer that the store retained nothing |

A committed dispatch intent is not proof that the network call happened. A worker
killed after its claim but before its POST leaves an unresolved request, even when
the test controller knows the provider saw zero attempts. A missing provider lookup
does not authorize resending that request. The design deliberately trades automatic
completion for preserving ambiguous consumption state.

Similarly, a provider may commit while its reply is lost, or the client may receive
the receipt and die before storing it. A restart preserves the prior claim. Recovery
queries the provider and authenticates the exact original receipt, rather than
generating another request or signing a replacement provider statement.

## Tests and relationship to PAY-06 / PAY-08

The tests exercise actual loopback exchanges, separate client/provider state,
concurrent processes, real worker/provider SIGKILL and restart, a real SQLite write
lock, and trusted fault hooks at defined commit/result boundaries. They inspect
attempts, effects, original receipts and balances rather than accepting returned
status labels alone. Hooks belong to the test controller; incoming payment requests
cannot select fault behavior.

This makes the durable consumption, lost-acknowledgment and read-only recovery
subset of **PAY-06** executable for the native mock protocol. For **PAY-08**, it
tests the local journal prerequisite and preservation of consumed identities across
configuration/epoch changes. It does **not** test an independent collector outage,
collector checkpoint recovery, credential revocation, intrusion eradication or the
complete eight-case adapter acceptance contract.

Business authorization and observed control routes remain separate concerns. The
existing offline experiment and its test results are unchanged. The
[pre-record gate](../pre-record-gate/README.md) supplied useful local durability and
no-resend patterns; this pilot adds explicit payment amounts, local balance effects
and scoped operation/idempotency aliases without reusing its `create_record` effect
as a payment result.

## Security and adoption scope

Transport is limited to a literal loopback endpoint, with fixed paths, bounded
requests, no proxy inheritance and no redirect following. The provider signs its
native receipts with an ephemeral key selected by the controller. The adapter
pins that public key and checks exact request/provider binding before storing a
terminal result. Provider configuration files containing the test credential and
private key must be private to their owner.

All processes and keys are controlled by the same operator and host user. This
is application-role separation, not an OS isolation boundary, independent witness,
malicious-administrator defense or production custody architecture. State retention
is indefinite in this experiment; deletion, rollback and multi-region recovery are
not covered. Changing both request identities can create a second business payment,
so callers must not manufacture new IDs to resolve an ambiguous original.

There is no generic exactly-once guarantee, real-bank compatibility, production
availability result, independent reproduction, VAP conformance, new profile or
normative requirement. Subsequent work needs an explicitly authorized payment
integration, upstream business authorization, identity/key lifecycle, independent
collection, privacy/retention and controlled storage recovery.
