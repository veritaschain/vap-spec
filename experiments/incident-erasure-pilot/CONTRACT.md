# Local erasure evidence pilot contract

Informative, synthetic application experiment. This adds no normative event,
changes no assessor runtime, and makes no conformance or legal determination.
One immutable synthetic object and one active namespace per task are intentional
bounds. Requester, provider and observer use distinct fresh keys under the same
`single-local-controller` organization; this is not independent verification.

## Common protocol

`protocol.py` imports the unchanged sibling assessor. It supplies `InputError`,
`canonical`, `digest`, `digest_hex`, `exact_keys`, `timestamp`, `utc_now`,
`identifier`, `decode_json`, `capture`, `sha256_bytes`, `public_key`, `sign_message`,
`verify_message`, `sign_record`, `verify_record`, and `object_name`.
The control signature domain is `erasure-pilot-control/0.1\0`. JSON is bounded,
duplicate keys/floating-point values/invalid Unicode are rejected. Capture
preserves the distinction between integer inputs and integral-valued floats
before JCS normalization. IDs match
`[A-Za-z0-9][A-Za-z0-9_-]{0,63}`. Object bytes are at most 1 MiB and nonempty.
`object_name(manifest)` is SHA-256(JCS of provider_id, tenant_id, object_id,
version_id) plus `.bin`; no caller-supplied paths are accepted.

`LOCATION = "active-object-namespace"`.
`EXCLUSIONS = ["backups", "replicas", "downstream-copies", "training-derivatives",
"open-handles-and-memory", "storage-media"]`.
Absence is about a directory entry at an observation time, never media sanitization.

Manifest exact fields: `provider_id`, `tenant_id`, `object_id`, `version_id`,
`sha256`, `byte_length`, `location`. All IDs are bounded IDs, the location is
LOCATION, and the byte count is an actual integer within the object limit.

Pins exact fields: `provider_id`, `tenant_id`, `location`, `requester_key_id`,
`provider_key_id`, `observer_key_id`, `keys`.
The keys map has exactly those three distinct keys, each with the unchanged core
trust metadata fields public_key, issuer, organization, roles, not_before,
not_after. Roles are respectively `["responder"]`, `["provider"]`, `["reviewer"]`;
all organizations must be `single-local-controller`. Authorities derive from pins.

## Task and authorization

Task exact fields: `format: "incident-erasure-task/0.1"`, `manifest`, `request`,
`authorization`. Request is an original core-signed `erasure.request` record.
Its exact subject is request_id, provider_id, tenant_id, object_ids (singleton),
payload_sha256 (digest of the complete manifest), stage (`erasure`).
Request data requested_at equals recorded_at. requested_locations includes
LOCATION and can include EXCLUSIONS, without duplicates or other locations.
Evaluation ID and record ID are bounded IDs. Authorization is a pilot-signed
message from the same requester key, whose exact body is kind
`deletion_authorization`, request_sha256, manifest_sha256, authorized_at,
valid_until. authorized_at equals requested_at; validity is half-open.

`adapter.validate_pins(pins)` and `validate_task(task,pins,at)` validate all
fields, original signatures, identity/role/time, full target and scope bindings,
and authorization validity at the proposed action. They return a context with
request_id, evaluation_id, subject, operation_at, valid_until, task_sha256,
manifest_sha256, request_record_id, and manifest. No file operations occur.

## Local provider

`LocalProvider(root,pins,secret,clock=utc_now)` pins the provider identity and
key. `create(object_id,version_id,content)` writes a new exclusive synthetic file
and returns the measured manifest. `namespace_root` is its owned data directory.
`inspect(manifest)` returns `{state:"PRESENT",sha256,byte_length}` or
`{state:"ABSENT",sha256:null,byte_length:null}`. It rejects unsafe/nonregular
objects and never follows symlinks. `get(request_id)` exposes a journal row.

`delete(task, *, before_unlink=None, after_unlink=None, acknowledge_only=False)`
captures canonical task bytes once. It validates authorization and the actual
object; claims a durable one-shot SQLite WAL/FULL intent; validates the claim
acknowledgement; signs an original core acknowledgement; rechecks authorization
and object identity/content immediately before unlink; performs at most one
unlink; fsyncs the directory; observes the exact entry absent; signs completion;
and validates a durable terminal result acknowledgement. Hooks are trusted test
seams; before_unlink runs before the final validation. KeyboardInterrupt is not
caught, so tests can inspect/restart after interruption. No automatic retry.

Acknowledgement-only mode commits its one-shot claim and returns ACKNOWLEDGED_ONLY
with the object retained. A replay does not resume it. It models receipt without
completion; this pilot has no production queue/reconciliation worker.

Result exact fields: state, attempted, acknowledgement, attestation, receipt,
journal_state, reason. `attempted` means an unlink call was entered, not external
deletion. States: LOCAL_UNLINK_CONFIRMED, ACKNOWLEDGED_ONLY, BLOCKED,
OUTCOME_UNKNOWN, REPLAY_NO_ACTION, REQUEST_ID_CONFLICT. A replay has no new
acknowledgement, attestation or receipt. Unknown never returns completion.
The store may return a valid acknowledgement after later failure.

`_claim(request_id,fingerprint,snapshot)` and `_finish(request_id,state,result)`
are fault seams; strict matching durable acknowledgements are mandatory.
Rows have request_id, fingerprint, state, snapshot, result. Claim additionally
returns claim_status CLAIMED/REPLAY/CONFLICT. Fingerprint is digest(task).
Snapshot is the canonical task. A terminal state equals the returned result state.
Claim is made before unlink; failed or ambiguous attempts cannot be replayed.
Actual missing/changed targets are blocked, never adopted as prior completion.

Core acknowledgement data references the original request record and uses queue
state received. Core attestation claims exactly `[LOCATION]` and excludes all
EXCLUSIONS. Both retain the exact subject and evaluation ID. Completion is signed
only after absence lookup. Receipt is a provider-signed pilot message with exact
body: kind `local_unlink_receipt`, task_sha256, request_id, manifest_sha256,
before `{sha256,byte_length}`, unlinked_at, observed_at, after `ABSENT`.
Receipt times follow request/ack time, and attestation completed_at equals the
receipt observed_at. Record recorded_at equals its event time. No raw content
is written into the journal or exported evidence.

## Local observer and pure adapter

`LocalObserver(namespace_root,pins,secret,clock=utc_now).observe(task,phase,
previous=None,completion=None)` independently looks up the bounded basename
using no-follow readback. It signs a pilot message whose exact body is kind
`local_namespace_observation`, task_sha256, manifest_sha256, provider_id,
tenant_id, location, object_id, version_id, phase (`before`/`after`),
previous_sha256 (before null; after digest of previous or null), completion_sha256
(before null; after digest of the original core provider attestation or null), window_start, window_end,
measurement (the exact inspect shape). A zero-duration read window is allowed;
signed clock statements are not external timestamp evidence.

Bundle exact fields: format `incident-erasure-bundle/0.1`, task, as_of,
provider_result (or null), before (or null), after (or null).
`adapter.verify_bundle(bundle,pins,expected_task_sha256)` performs no I/O,
signing, deletion or retry. Historical task validation uses the authorized
request time, not the later evidence cutoff. It checks the separately pinned
task digest, all supplied signatures/bindings/types, chronology and receipt/result
consistency, then passes original request/ack/attestation records to the unchanged
assessor. Supplied invalid evidence is rejected with InputError, not promoted.

Return exact top fields: format `incident-erasure-assessment/0.1`, task_sha256,
assessor_report, local_observation, unknown_domains, limitations.
Local observation is one of NOT_OBSERVED, ABSENCE_ONLY, PRESENT_AT_OBSERVATION,
REMOVAL_OBSERVED_SAME_CONTROLLER, NOT_ESTABLISHED. Promotion requires a matching
before-present digest/length, verified LOCAL_UNLINK_CONFIRMED terminal result,
and a linked after-absent observation after completion. After-only absence does
not prove previous presence or a deletion operation. A missing referenced before
observation or attestation cannot support removal; a supplied but mismatched
reference is rejected. A present after observation
does not erase an attributed provider claim, but withholds local corroboration.
All unknown_domains map the fixed EXCLUSIONS to UNKNOWN. Core target_completion,
provider_completion, independent_verification, and out-of-scope dimensions remain
unchanged. No local observation is converted into an erasure.review record.

## Execution evidence and limits

The suite performs actual synthetic writes, unlink, directory fsync, SQLite
transactions and observer reads. It exports public pins, original signed task,
provider results, linked observations and reproducible assessments, without
private keys or object plaintext. Source hashes are captured before and after
execution. A case cutoff follows every bundled observation, and the summary
completion time follows every case cutoff. An offline recheck validates captured records and source identity;
it does not reexecute deletion or prove a malicious controller told the truth.
An excluded-copy control and an open-handle control demonstrate why namespace
removal is narrower than complete erasure. No real patient or institutional data
is involved. User/OS isolation, external anchoring, remote provider integration,
key revocation, storage-media sanitization and legal conclusions are not assessed.
