# Collector prerequisite pilot — implementation contract

Informative synthetic experiment, version 0.1. This is not a VAP requirement or
conformance result. The unchanged normative baseline is VAP v1.2 Draft 3.

## Boundary and sequence

The new `collector_pilot` runtime imports the pinned, unchanged assessor and upload
transport/receiver/journal primitives. A separate loopback HTTP collector commits
only signed intent metadata to SQLite WAL/FULL; it never receives payload bytes.
The controller owns all ephemeral keys and both services. Separate processes do
not establish independent observation or resistance to a malicious controller.

1. Capture owned immutable payload bytes and independently pinned evaluation
   context. Bind the measured digest/length and the configured complete route.
2. Evaluate policy and permit with `require_collector=true`. Missing collector
   evidence is provisional only; a policy/permit/key failure cannot proceed.
3. Atomically claim the request ID in the durable local journal **before any
   collector write**. A committed claim consumes the request even when its
   acknowledgement is lost. An unestablished claim blocks the current call and
   never triggers an automatic retry; a pre-commit storage failure is not claimed
   to have durably consumed the ID. This conservative pilot deliberately has no
   resumable same-request upload state.
4. Submit the exact signed metadata intent once. Require a correctly bound,
   authenticated collector receipt returned after commit and readback.
5. After any trusted fault hook, issue a fresh signed read-only status query with
   an unpredictable nonce. Verify the complete query/intent/receipt binding.
6. At the real response-verification time, create a gateway-signed
   `transfer.collector_health` record with both booleans true and reassess the
   unchanged evaluator at that time. Recheck current policy, permit and gateway
   key authority. Only a final `ALLOW` permits one payload transport call.
7. Preserve the transport's actual timestamps and receipt separately. No health
   observation is backdated to the later dispatch event. The unchanged evaluator
   can therefore retain postflight observed-action `REVIEW` after a valid final
   gate and a confirmed receiver receipt.

An unavailable, unauthenticated, mismatched or ambiguous collector exchange cannot
authorize the payload call. A failed exchange establishes absence of a usable
acknowledgement, not physical service death or absence of durable records.
Acknowledgement and fresh readback establish point-in-time prerequisites; they do
not prove continuous collector availability or atomicity with later payload send.

`reconcile` performs only a fresh authenticated status query for the exact saved
intent. It never collects, resets a journal row, resumes or uploads. Repeating
`execute` after a claim yields replay or conflict with zero new RPC/upload calls.
After recovery, a payload attempt requires a new explicitly authorized request ID.

## Fixed control protocol

Control envelopes have exactly `algorithm`, `key_id`, `body`, `signature`.
Ed25519 signs the ASCII domain `collector-pilot-control/0.1`, one NUL byte
(`0x00`), then `JCS(unsigned_envelope)`.
Keys are pinned out of band. No key or endpoint is selected by received content.
Digests are lowercase SHA-256. Integers exclude booleans. Strings are bounded.

The signed `collection_intent` body has exactly:

```
kind, collector_id, collection_id, request_id, evaluation_id,
subject_sha256, payload_sha256, byte_length, policy_sha256,
decision_sha256, created_at
```

`collection_id = SHA256(JCS({collector_id, request_id}))`; `subject_sha256` binds
the complete measured transfer subject, including route, tenant and policy.
`decision_sha256` binds the exact signed permit envelope selected for this subject.
`request_sha256` below is SHA256(JCS(the complete signed collection intent)).

The signed `collection_receipt` body has exactly:

```
kind, collector_id, collection_id, request_id, request_sha256,
recorded_at, receipt_id, storage
```

`storage` is `sqlite-wal-full`. `recorded_at` is the record's pre-commit time, never
called commit-completion time. The server returns the stable saved receipt only
after successful FULL commit and readback. This is a local storage assumption,
not a power-loss test or remote attestation of hardware.

The signed `collection_query` body has exactly:

```
kind, collector_id, collection_id, request_id, request_sha256, nonce, created_at
```

The signed `collection_status` body has exactly:

```
kind, collector_id, collection_id, request_id, request_sha256,
query_sha256, nonce, status, receipt, checked_at
```

`query_sha256` binds the complete signed query. `status` is `FOUND` or `NOT_FOUND`;
only `FOUND` carries the original saved receipt. `NOT_FOUND` is an observation at
the query time, not historical proof that collection never occurred. A conflicting
binding under the same collection/request identity is refused. A found receipt's
original `recorded_at` is preserved across readbacks and process restart.

## Process and transport constraints

Only literal `http://127.0.0.1:PORT` collector endpoints are accepted; the client
appends fixed `/collect` or `/status` paths. Bounded JSON and HTTP headers, one
attempt per call, no redirect, proxy, DNS, compression or implicit retry.
SQLite connections close explicitly. Server fault modes are trusted constructor
configuration, never parameters accepted from request content.

Collector restart keeps the exact database, collector identity, gateway pin,
collector key and endpoint. Changed identity/key configuration is refused.
Snapshots are controller observations of local database state, not signed
independent testimony or a substitute for an authenticated network response.
The reused receiver trusts gateway dispatch authorization; it does not separately
enforce the collector prerequisite.

## Shared implementation API

`collector_pilot.protocol` exports the old safe utility names (`InputError`,
`canonical`, `digest`, `decode_json`, `public_key`, `sign_record`, `timestamp`,
`utc_now`) plus new-domain `sign_control` / `verify_control`,
`collection_id(collector_id, request_id)`, `validate_intent(body)`,
`validate_query(body)`, `verify_receipt(envelope, intent, public_key, key_id, at)`,
`verify_status(envelope, query, intent, public_key, key_id, at)` and
`validate_endpoint(endpoint)`. Verification returns owned body dictionaries.

`CollectorClient(endpoint, collector_public, collector_key_id, timeout=1.0)` has
`collect(signed_intent)` and `status(signed_query)`. Each returns exactly:
`attempted`, `attempted_at`, `completed_at`, `status` (HTTP integer/null),
`response` (decoded envelope/null), `error` (string/null). Gate code verifies
responses against independently held intent/query/keys; client success alone
never permits payload transmission.

`CollectorProcess(directory, *, collector_id, gateway_public, gateway_key_id,
collector_secret, collector_key_id, port=0, mode="normal")` is a context manager
with `.endpoint`, `.stop()`, `.restart(mode="normal")`, `.snapshot()`.
Modes: `normal`, `drop_before_commit`, `drop_after_commit`, `wrong_receipt`,
`wrong_status_nonce`. Snapshots include integer `collect_calls`, `status_calls`,
`accepted_count`, and `rows` with the original signed intent and receipt.

`CollectorGateway(config, journal, transport, collector, *, collector_id,
collector_public, collector_key_id, clock=utc_now)` uses the unchanged upload
`GateConfig`, `Journal`, `HttpTransport`. `execute(package, trust, payload,
before_final_check=None)` returns a report with payload state, collector outcome,
actual exchanges and reproducible evaluator frames. The callback is trusted test
configuration and executes after collect acknowledgement, before the final fresh
status query. `reconcile(request_id)` reads the owned journal snapshot and issues
only a status query. Its result never changes the prior payload outcome.

The report must distinguish collector RPC calls, metadata rows, payload transport
attempts and receiver observations. It exports no secret key or payload plaintext.
New finite expectations and source inventory apply only to this pilot; the 154
frozen execution inputs and historical 53-case captures remain unchanged.
