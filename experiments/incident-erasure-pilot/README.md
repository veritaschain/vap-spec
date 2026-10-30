# Local incident erasure evidence pilot

**Status:** Informative, synthetic application experiment; unadopted.

This pilot performs an actual, narrowly authorized removal from a local object
namespace and retains the signed evidence needed to distinguish a request,
provider acknowledgement, provider completion claim and same-controller readback.
It extends the incident work with an executable deletion lifecycle. It does not
change the VAP specification or the existing offline assessor.

The motivation is the gap identified in the [source-checked incident ledger](../../proposals/incident-evidence-bindings/INCIDENTS.md):
removing a chat history item or requesting provider deletion does not, by itself,
establish what the provider retained. This experiment uses a new synthetic local
store. The earlier [upload pilot](../incident-upload-pilot/README.md) retained
measured receipts, not uploaded payload files; this is not a claim that its
receiver stored or erased those original payloads. No patient, university,
provider-account or production data is used here.

## What the evidence means

| Evidence or observation | Meaning in this experiment | Unestablished conclusion |
|---|---|---|
| Signed request | The pinned requester requested this exact manifest and scope | Provider receipt or completion |
| Signed acknowledgement | The local provider received the bound request | Removal of any data |
| Signed scoped attestation and local unlink receipt | The pinned provider attributes a measured removal from the active namespace to this task | Complete deletion from every copy or storage medium |
| Linked before-present and after-absent observations | The same controller observed this bound name and bytes before the operation, and absence afterward | Independent organizational verification |
| After-only absence | This name was absent at the stated observation time | Previous presence or a removal caused by this request |
| After-present observation | The named entry was present at this later read | Timeless absence from an earlier receipt |
| Retained-copy/open-handle control | The original synthetic bytes remained readable outside the removed directory entry | Deletion of that retained instance |

The unchanged core assessor's strongest result here is
`PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE`. Its `provider_completion`,
`target_completion`, `outside_scope_outcome` and `excluded_scope_outcome` remain
`UNKNOWN`; `independent_verification` remains `NOT_ESTABLISHED`. The additional
local dimension can be `REMOVAL_OBSERVED_SAME_CONTROLLER`. No observer statement
is converted into an `erasure.review` record.

The fixed uncovered domains are backups, replicas, downstream copies, training
derivatives, open handles/memory and storage media. These domain-wide outcomes
remain unknown. The negative controls separately record affirmative retained
readable bytes; those observations are not hidden under the domain-wide unknown.

## Action and trust boundary

Each task concerns one immutable synthetic object version, at most 1 MiB, in one
controller-owned POSIX namespace. The object basename derives from the provider,
tenant, object and version IDs. No evidence-supplied path is accepted. The full
manifest binds those IDs, location, SHA-256 and actual byte length.

A task retains the original Ed25519-signed assessor request and a separately
domain-signed deletion authorization. That authorization binds the complete
request and manifest digests and a half-open validity interval. The provider
captures inputs once, checks the actual file, commits a one-shot SQLite intent,
rechecks authorization and the file immediately before unlink, fsyncs the
directory and confirms absence before signing a scoped completion. It validates
both the intent acknowledgement and the terminal result acknowledgement.

The requester, provider and observer use distinct fresh keys but share the
honestly declared `single-local-controller` organization. The pure verifier
requires separately supplied public pins and an expected task digest. Pins include
the full issuer, role, organization and validity metadata, not just a public key.
Captured pins in a public test export remain the test controller's assumptions;
they are not independent identity onboarding or external trust evidence.

The original request time stays fixed when evidence is rechecked later. A valid
old receipt can be assessed after authorization expiry, while its claimed unlink
time must have been within the original authorization interval. Local clock
statements are not externally anchored timestamps.

## One-shot outcomes

| Provider state | Local behavior |
|---|---|
| `LOCAL_UNLINK_CONFIRMED` | Entered one unlink; scoped absence, signed completion and terminal persistence acknowledgement were established |
| `ACKNOWLEDGED_ONLY` | Committed receipt without removal; this pilot does not later resume that task |
| `BLOCKED` | No unlink was entered; current authorization, target or durable prerequisites were not established |
| `OUTCOME_UNKNOWN` | A later operation or evidence/persistence step was uncertain; no completion is returned |
| `REPLAY_NO_ACTION` | The same task was already claimed; no unlink or refreshed completion evidence is produced |
| `REQUEST_ID_CONFLICT` | The request ID already binds a different task; no new action is performed |

`attempted` records whether the provider entered an unlink call. It is not a
remote deletion assertion. A lost terminal acknowledgement after deletion leaves
an unknown result and a consumed request ID. A replay does not retry, reassert
old completion or delete a recreated entry. The experiment intentionally has no
production reconciliation/resumption worker.

Filesystem checks reject unsafe roots, symlinks, nonregular files, replaced
directories and changed file identity/content. These checks assume a trusted
host/controller; a final stat and an unlink are not a single atomic operation
against an adversary with the same OS privileges. Neither read-only file mode
nor SQLite establishes tamper-proof storage against that controller.

## Run

Use Linux/POSIX and Python 3.12 or 3.14. From this directory:

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -W error::ResourceWarning run_tests.py --require-no-skips
.venv/bin/python -m erasure_pilot run-suite --output generated --print-summary
.venv/bin/python -m erasure_pilot verify-exports generated
```

Every run-suite output directory must be new. The test runner rejects skipped
tests and otherwise easy-to-miss finalizer/resource errors. The scenario runner
returns a nonzero exit status for a failed expectation. No sockets, AI service,
real provider or account credentials are required.

The [18-case catalogue](acceptance.json) covers normal removal, acknowledgement
and request-only states; forged/misbound evidence; final authorization expiry;
changed or already absent objects; repeated and concurrent requests; lost result
persistence; retained copies and file handles; after-only absence; recreation;
failed durable intent; conflicting request IDs; and provider-only attestations.
Runtime modules do not read catalogue IDs or expected verdicts.

## Public evidence and reproducibility

The suite writes actual runtime state under `generated/runtime/`, signed public
case evidence under `generated/cases/`, and `generated/summary.json`. Only the
summary and case evidence are uploaded by CI. The object plaintext, runtime
files and SQLite files are excluded from the uploaded artifact; private keys are
never exported. Opaque identifiers and content digests are still metadata and
are not asserted to be anonymous or safe for production personal data.

The source manifest hashes the runtime, tests, runner, catalogue, requirements,
imported unchanged assessor and workflow before and after execution. Offline
rechecking verifies original signatures, exact bindings, chronology, verdicts,
case digests and aggregate counts under that same source manifest. It does not
execute deletion, inspect current remote storage or prove that a malicious
controller produced truthful observations. A case cutoff bounds all its
observations, and every case must precede the summary completion time.

[Recorded results](results/README.md) identify actual CI runs and artifact
retention. A workflow configuration alone is not a successful execution claim.
[REVIEW.md](REVIEW.md) records internal adversarial review and remaining limits.
[CONTRACT.md](CONTRACT.md) defines the exact application protocol;
[RUN-ja.md](RUN-ja.md) provides Japanese instructions.

## Technical references and limits

Python documents that on Unix an unlink removes a directory entry while an
already-open file can remain in use; see [os.remove / os.unlink](https://docs.python.org/3/library/os.html#os.remove).
SQLite's [WAL documentation](https://www.sqlite.org/wal.html) describes its
commit and synchronization behavior. Those prerequisites depend on the local
filesystem and hardware; this pilot does not run power-loss or storage-media
sanitization experiments. Controlled interruption tests use `KeyboardInterrupt`
at explicit seams, not a power failure or a forced external process kill.

Other limits include same-controller trust, no OS privilege separation, no
external anchoring, no key revocation, no real provider API integration, no
independent reproduction and no legal or VAP/CAP conformance determination.
The repository's [CC BY 4.0 license](../../LICENSE) applies.
