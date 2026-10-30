# Controlled upload pilot: implementation contract

Non-normative synthetic local experiment. Import the unchanged sibling
incident-evidence-assessor. Do not import its fixture keys or expected outcomes.
No external provider, patient data, real AI invocation, production credential,
OS isolation or VAP/CAP conformance claim. The existing pre-record gate and
OS-isolation experiments remain separate and unchanged.

## Two prerequisites and measured bytes

The trusted controller supplies an assessor evidence package and separate trust,
a fixed route configuration and signing keys. The application supplies only bytes.
Gateway first validates the original evaluator pin. It takes one immutable bytes
snapshot (max 1 MiB), computes SHA-256(raw bytes), and constructs the actual target
from the pinned subject plus the controller-configured route and measured digest.
The actual operation_at/as_of come from the gateway clock at admission. Updating
this evaluator observation frame never updates any signed policy or permit.

Send requires BOTH authenticated assessor ALLOW and a successfully committed
local journal dispatch intent. The synthetic permission policy sets
require_collector=false; the pilot independently imposes mandatory SQLite FULL
pre-recording. Do not manufacture collector_health with a backdated timestamp.
Signed permit validity is checked again after journal commit, immediately before
transport. No automatic write retry is allowed once an intent is claimed.

Raw payloads are sent unchanged as POST /upload, application/octet-stream,
Content-Length, no compression, redirects or proxy environment handling.
Only a controller-pinned http://127.0.0.1:PORT/upload endpoint is supported.
DNS, alternate hosts/paths, userinfo, query strings and fragments are forbidden.

## Shared APIs (root owns protocol.py and harness/suite)

`upload_pilot.protocol` imports the sibling assessor with a fixed sibling path and
exports canonical, digest, strict_json, InputError, timestamp, sign_record,
sign_control, verify_control, decode_json, validate_endpoint and utc_now.

sign_record(body, secret_hex, key_id) uses the existing incident adapter domain;
sign_control(body, secret_hex, key_id) uses upload-pilot-control/0.1 plus zero byte
and JCS of {algorithm,key_id,body}; verify_control(envelope,public_hex,key_id,kind)
checks exact envelope fields, signature and kind, returning the body or InputError.

GateConfig is a frozen dataclass with endpoint, route (the seven transfer grant
fields plus stage), gateway_secret, gateway_key_id, gateway_issuer,
receiver_public, receiver_key_id. All are trusted controller inputs; gateway
snapshots route/config on construction. Default clock is utc_now() -> ISO8601Z.

Receiver receipt signed body:
{kind:"upload_receipt", request_id, subject_sha256, payload_sha256, byte_length,
received_at, receipt_id}. Digest/length are measured from actual HTTP body bytes.
Gateway dispatch header signed body:
{kind:"dispatch_intent", request_id, subject_sha256, payload_sha256, byte_length,
created_at}. X-Pilot-Authorization is base64 of its canonical envelope.
The receiver verifies the configured gateway key and the exact request/body
digest+length, but trusts the gateway's authorization decision; no independent
production identity or policy adjudication is claimed.

`HttpTransport(endpoint, timeout=1.0).send(payload:bytes, dispatch_envelope)`
returns dict {attempted:true, body_send_completed:bool, attempted_at:str,
dispatched_at:str|null, status:int|null, receipt:object|null, error:str|null}.
dispatched_at is obtained only after HTTPConnection.request returns, never from
the earlier intent. Transport catches network/HTTP/JSON errors conservatively;
redirects and non-2xx responses yield no usable receipt. It makes exactly one
request, never follows a redirect and never retries. No caller URL overrides.

`ReceiverProcess(directory, *, gateway_public, gateway_key_id, receiver_secret,
receiver_key_id, mode="normal")` is a context manager launching a separate
loopback HTTP process. Exposes endpoint and snapshot() returning actual SQLite
handler_calls, accepted_count and rows (request_id,subject_sha256,payload_sha256,
byte_length,receipt). Supported trusted test modes: normal, drop_after_commit,
wrong_receipt, redirect, unauthenticated (negative control). Modes cannot be set
by an HTTP request. Provider plaintext need not be persisted; digest and length
are computed from raw bytes at receipt. Handler counts distinguish an attempted
request from an accepted record. Cleanup must terminate/join its own child.

## Gateway/journal API (gate agent owns)

Journal(path) creates/checks SQLite WAL and synchronous FULL. Each method opens
its own connection to support threads and process restart. Atomic claim by
request_id prevents a second send. Same-ID different binding is rejected.
claim(request_id, fingerprint, snapshot)->dict records state dispatch_intent;
get(request_id)->dict|None; finish(request_id,state,details)->dict persists result.
Rows keep measured hashes/length, signed records and decisions, not raw payloads
or secret keys. Claimed state survives restart. Unknown outcomes never auto-resend.
No tamper-proof disk, external anchor or physical power-loss assurance is claimed.

Gateway(config,journal,transport,clock=utc_now).execute(package,trust,payload,
*,after_snapshot=None,before_send=None) -> report. Hooks are trusted harness fault
injection only, never request fields. after_snapshot() can mutate a caller-owned
bytearray to demonstrate immutable capture; before_send() runs after durable
claim, then final deadline reassessment runs. Source bytes are never reopened.

Report fields: state (BLOCKED_WITHOUT_ATTEMPT, RECEIPT_CONFIRMED,
OUTCOME_UNKNOWN, REPLAY_NO_SEND, REQUEST_ID_CONFLICT), attempted (bool), reason,
payload_sha256, byte_length, journal_state, preflight_assessment, receipt (nullable),
evidence (postflight package), trust (postflight separate evaluator config),
postflight_assessment. Returned public material must contain no private keys.
Input malformed errors can be InputError (CLI emits exit2); evidence/policy
denials are normal BLOCKED_WITHOUT_ATTEMPT results. Receipt confirmation requires
actual signature and all request/subject/payload/length bindings plus chronology.
An invalid/missing response or failure persisting the result leaves unknown.

Before transport, store an intent, not transfer.dispatch. Add signed
transfer.dispatch only when body_send_completed is true and use the transport's
actual completion time. Sign at a later/current record time and advance as_of
honestly. The unchanged assessor's remote_outcome remains UNKNOWN; receiver
receipt confirmation is a separately named pilot result.

## Suite and preservation

The suite uses only synthetic bytes and fresh ephemeral keys. Actual HTTP
observations are compared with a separate fixed acceptance catalogue. Existing
output directories are rejected to prevent mixed results. Export public keys,
signed evidence, report hashes, measured receiver counters, source hashes and
cleanup result; never private keys. A missing/failed HTTP run is not success.
Offline recheck verifies signatures, bindings, report reproduction and exact
inventory; it does not rerun HTTP or establish independent truth.
