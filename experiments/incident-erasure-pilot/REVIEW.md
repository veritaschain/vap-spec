# Local erasure evidence pilot — development review

This is an internal development review of an informative, synthetic application
experiment. The boundary tests were authored separately from the provider and
adapter implementations, within the same development team and workspace. This
is not an independent third-party reproduction, security certification, legal
opinion, or VAP conformance assessment.

## Reviewed scope

The implementation performs a real local filesystem operation on one explicitly
created synthetic object. A separately pinned requester authorizes an exact
manifest and request; the provider records a durable one-shot intent before
entering `unlink`; a same-controller observer measures the bounded namespace.
The new store is separate from the earlier upload pilot. That receiver retained
measured hashes, lengths and receipts, not the uploaded body, so this experiment
does not claim to erase bytes retained by that receiver or an external service.

The signed manifest binds provider, tenant, opaque object and version identifiers,
content digest, byte length and the active namespace. In this adapter's exact
request subject, `payload_sha256` commits to the complete manifest. The content
digest remains the manifest's separate `sha256` field. Filenames derive from the
bounded identity tuple; a request cannot supply a filesystem path.

Deletion authorization is a separate control message. The unchanged erasure
assessor attributes evidence and does not authorize filesystem actions. The
request time remains the original `operation_at`; a later evidence cutoff does
not rewrite that event or renew an expired authorization. Live action and offline
receipt validation both check the authorization at the claimed unlink time.

## What the evidence establishes

The provider distinguishes a recorded request, acknowledgment, entered unlink,
scoped completion and uncertain outcome. A completion requires the exact current
object, the authorized action interval, directory synchronization, a subsequent
absence observation and a matching durable terminal acknowledgment. A failed
completion path retains a known entered attempt while withholding attestation
and receipt. Replays do not execute again or return an old receipt as a new
completion. Acknowledgment-only operation leaves the file present and does not
resume automatically on replay.

The pure adapter checks supplied signatures, issuer and role pins, full task and
manifest bindings, actual integer lengths, original record references, evidence
chronology and every result state's permitted evidence combination. Its stronger
local observation requires a matching before-present measurement, verified
provider completion and a linked after-absent observation. Missing before
evidence gives `ABSENCE_ONLY`; current absence does not prove prior presence or
that this request caused removal.

A later present observation remains visible alongside the earlier attributed
provider statement. It withholds local corroboration without silently discarding
the provider's signed history. Recreating a name after deletion does not prove
that the earlier observed unlink never happened.

Requester, provider and observer have different fresh keys under the same
`single-local-controller` organization. No local observation is translated into
`erasure.review`. The unchanged assessor can return
`PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE`; its provider completion, target
completion and out-of-scope outcome dimensions remain `UNKNOWN`, and independent
verification remains `NOT_ESTABLISHED`.

## Boundary tests and correction

The separately authored [boundary tests](tests/test_boundary.py) use actual
owned temporary directories, fresh keys and synthetic files. They cover:

- Measured removal, unchanged core uncertainty, scoped exclusions, and absence
  of private keys or object plaintext in public evidence.
- Replacement of the caller's task with another valid signed task after capture,
  without redirecting the deletion or changing its recorded identity.
- Namespace replacement immediately before or after unlink, with correct
  refusal or uncertain outcome and no completion claim.
- Validly signed requests with the wrong tenant, object, manifest digest, stage,
  scope or malformed path and length fields.
- Role widening and invented organizational independence in trust metadata.
- Missing before or after observations without promotion to observed removal.
- Authentic provider receipts with changed identity, measurements, types,
  chronology or unsupported claims.
- Authentic observer statements with mismatched predecessor, completion,
  namespace, version, time or measurements.
- Report mutations that hide attempts, relabel incomplete terminal states or
  transplant completion into acknowledgment, unknown or replay outcomes.
- Actual recreation of a removed entry, preserving the observed presence and
  attributed historical claim together.
- Historical verification after authorization expiry, without modifying the
  original request or performing another filesystem action; strict JSON parsing
  also rejects duplicate fields, nonfinite values and invalid Unicode.

Review found a namespace-binding gap: an open directory descriptor could still
refer to a moved directory after the configured namespace pathname had been
replaced. The provider now checks the named root and namespace against their
pinned identities immediately before unlink and after the absence lookup.
The regression verifies that pre-action replacement leaves the original and
replacement files intact, while post-action replacement yields an entered but
unconfirmed operation. This is consistency within a trusted-controller design,
not protection from a hostile operating-system owner.

The final integration review also closed bounded issues in capture and sampling:

- Retained-copy and open-handle observations now have a case-level cutoff;
  bundled observations cannot follow that cutoff, and the case cutoff cannot
  follow the recorded completion summary.
- Input capture rejects floating-point values before JCS can normalize an
  integral float into an integer. Declared integer lengths therefore remain a
  strict input requirement through capture, signing and verification.
- A bounded second journal lookup recognizes a concurrent request that completed
  between the first lookup and initial file inspection. Its replay does not
  become an unexplained missing-object refusal or a new attempt.
- Final object checks retain device, inode, size, modification time and change
  time across the content read and authorization recheck. An ordinary in-place
  change after the final read is rejected. The last stat and unlink are still
  separate operations, without a guarantee against every malicious same-user
  race.
- The concurrency scenario now takes both before measurements, runs both
  provider calls concurrently, joins them, and then takes after measurements.
  Previously a replay could return before the winning call had unlinked, making
  a present observation correct at that earlier time. The revised sampling
  establishes the intended after-operation window instead of treating that valid
  timing variation as a provider failure or replacing the measured result.

## Verification checkpoint

The final local development run completed **54 of 54 test methods**, with zero
skips, errors or unraisable finalizer exceptions:

| Test group | Methods passed |
| --- | ---: |
| Provider and actual filesystem behavior | 21 |
| Pure evidence adapter | 13 |
| Separately authored boundary checks | 11 |
| Same-controller observer | 4 |
| Scenario suite and export recheck | 5 |
| **Total** | **54** |

The integrated tests executed all **18 actual local filesystem scenarios**, with
all expected outcomes matched. A separate final CLI execution also matched
**18 of 18 scenarios**, and its captured public evidence passed **18 of 18
offline export rechecks**. The unchanged assessor passed its **20 test methods
and 23 catalogue cases**. These are executed development checks, distinct from
merely parsing an acceptance catalogue.

The final executable source manifest contains **28 files**, with aggregate digest
`fb0dc41bde92840e06f11c9077c41743dc8c1255b4404aaa464b7455fa829191`.
CI executions are recorded separately; this review does not preclaim a CI result
or independent reproduction.

The workflow requires Python 3.12 and 3.14 on Ubuntu, no skipped methods, and a
runner that treats ResourceWarning and unraisable finalizer errors as failures.
It executes all 18 actual filesystem scenarios, rechecks their public exports,
and reruns the unchanged assessor tests and catalogue. The source manifest covers
pilot modules, tests, the file-backed runner, requirements, the acceptance
catalogue, imported assessor modules and requirements, and the workflow. Source
hashes are compared before and after scenario execution.

CI artifact paths include only `summary.json` and `cases/`. Runtime directories,
including synthetic files deliberately retained by negative controls, are not
uploaded as public evidence artifacts. Offline rechecking validates captured
records and recomputed results; it does not repeat deletion or independently
observe the earlier filesystem state.

## Remaining limits

An unlink removes a directory entry. It does not establish media sanitization,
removal of another hard link or copy, closure of open descriptors, loss of data
already read into memory, remote deletion, training-data removal or unlearning.
The excluded-copy and open-handle scenarios make retained readable data explicit;
the assessor's general unknown domains do not erase those specific observations.

All roles and fault hooks share a trusted local controller and operating-system
user. Directory checks, read-only object modes and separate signing keys do not
establish OS isolation or prevent that owner from modifying files or signing a
false account. Signed clock statements have no external timestamp or anchor.
Historical absence is not a permanent guarantee against future recreation.

No real patient or institutional data, production credentials, remote provider,
crypto-shredding or new normative ERASURE event is used. Key revocation, general
multi-object transactions, production retry or reconciliation workers, legal
retention duties and deployment readiness remain outside this experiment.

No blocking finding remains within the declared synthetic, single-object,
same-controller scope at this development checkpoint.
