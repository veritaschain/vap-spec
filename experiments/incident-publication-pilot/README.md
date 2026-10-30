# Local incident publication pilot

**Experimental, synthetic and unadopted — version 0.1.0.** This application
experiment records actual local text replacements, renders a final static HTML
artifact with its visible disclosure, requires an explicit reviewer-signed
authorization for those exact bytes, and measures the local output after creation.
It invokes no real AI service and publishes to no external website or journal.

[日本語ガイド](RUN-ja.md) · [Implementation contract](CONTRACT.md) ·
[18-case catalogue](acceptance.json) · [Internal review](REVIEW.md) ·
[Execution records](results/README.md)

The unchanged [incident evidence assessor](../incident-evidence-assessor/README.md)
continues returning `publication_action: REVIEW` for eligible cases. The pilot
does not change that verdict into ALLOW. A separately signed reviewer statement
authorizes one exact local export under this application's limited rule. Test
reviewer keys are synthetic; their signatures do not establish that a real person
read the artifact or that its statements are true.

## What is bound and measured

The editor signs every actual text replacement, including same-byte replacements,
with before/after document digests, block identity, sequence, previous-envelope
digest, activity label and observation time. A signed checkpoint fixes the supplied
history and final document. Verification replays that history and checks all
signatures and transitions. Imports and manual edits retain unknown prehistory.

AI-labelled operations are **simulated local adapter operations**. The history
retains all such activities even if their output is later replaced. Only a block
whose last write has a simulated AI label is projected into an adopted current
`publication_activity`. A later manual edit invalidates that exact-output adoption;
it does not establish human-only authorship or erase the earlier activity.

The renderer creates one deterministic, self-contained HTML file containing all
final text blocks and a visible disclosure section. Author-supplied text is escaped;
scripts, external assets, raw supplied markup, figure/code attachments and arbitrary
output paths are not supported. The structured disclosure enumerates every recorded
simulated activity and states that outside origin remains unknown. No AI-text
detector, AI-generated percentage or word-level attribution is produced.

The approval binds the complete captured candidate, final HTML digest, disclosure
digest, current policy snapshot, destination and validity interval. The artifact's
own digest and approval stay outside the HTML, avoiding circular hashes or an
unapproved modification after review. Source document, edit lineage and final HTML
have separately named hashes.

## Local release rule

The gate independently pins the venue/route, applicable publication policy
ID/version/digest/stage, expected issuers, public keys, roles and validity intervals.
It first validates the original evaluator target pin, then measures the captured
source and rendered bytes. It checks the pilot reviewer authorization and the
corresponding unchanged-assessor approval record against the same target and time.

A prohibition, unresolved interpretation, missing approval, unsupported signature,
wrong venue or disclosure omission prevents output. Disclosure and approval never
override an observed prohibited activity. For this pilot's publication eligibility
rule, all recorded session activities are considered, including replaced output;
this is not a retrospective finding about the legality of earlier AI use.

The collector coverage record ends at the actual preparation observation; it is
not extended to a later release time. The core's coverage may therefore remain
`UNKNOWN`, and `activity_completeness` remains `UNKNOWN`. A reviewer can authorize
this local export under that explicit limitation. Core disclosure assessment remains
`REQUIRES_CONTENT_REVIEW`; no automatic legal or editorial judgment is claimed.

## Filesystem boundary

The publisher writes the captured immutable bytes to a fresh private staging file,
flushes it, commits a one-shot SQLite WAL/FULL intent and validates its acknowledgement.
The gate rechecks policy and approval validity immediately before publication.
The publisher then creates a non-overwriting hard link into its controlled visible
directory, synchronizes that directory, reads back the expected regular-file identity,
hash and length, signs a local receipt, and persists the terminal result.

The single HTML file makes article and disclosure visible together. An existing
filename is never overwritten or adopted, including one containing identical bytes.
Repeated or concurrent requests share one claim; another artifact under the same
request ID conflicts. A lost result after visible creation remains unresolved and
does not cause an automatic retry. Replay never reasserts an old receipt as a new
observation. Final files use read-only mode, but the trusted owner can change that
mode; this is not permanent immutability or OS isolation.

| Result | Meaning |
| --- | --- |
| `BLOCKED_WITHOUT_PUBLICATION` | This call created no new visible output; a collision may still have attempted the atomic link |
| `LOCAL_OUTPUT_CONFIRMED` | The configured publisher measured the expected local file and persisted its scoped receipt |
| `OUTCOME_UNKNOWN` | Publication, observation or result persistence is unresolved; a visible file may already exist |
| `REPLAY_NO_PUBLICATION` | A previously claimed request is not executed again; no receipt is freshly asserted |
| `REQUEST_ID_CONFLICT` | The request ID is already bound to another measured candidate |

`attempted` concerns the atomic-link call, not external delivery. The gate preserves
a returned publisher's attempt observation even if its later clock fails. If the
publisher invocation itself returns no attributable observation, the gate records
an unknown attempt as `null` rather than inventing a no-attempt result.

No local output or receipt is inserted as `publication_dispatch` or
`publication_receipt`. Core `delivery_status` remains `UNCONFIRMED` and
`acceptance_status` remains `UNKNOWN`.

## Reproduce

Use Python 3.12+ on Linux/POSIX with same-filesystem hard links, directory fsync and
no-follow file operations. No socket or external service is needed. From the root:

```sh
python3 -m venv .venv-publication
.venv-publication/bin/python -m pip install -r experiments/incident-publication-pilot/requirements.txt
cd experiments/incident-publication-pilot
../../.venv-publication/bin/python -W error::ResourceWarning run_tests.py --require-no-skips
../../.venv-publication/bin/python -m publication_pilot run-suite --output generated
../../.venv-publication/bin/python -m publication_pilot verify-exports generated
```

Choose a fresh output directory for every run; existing directories and symlink
output roots are refused. The suite runs 18 actual local filesystem scenarios,
including a real pre-link expiration pause and concurrent requests. Its injected
storage exceptions do not simulate every physical disk failure. Unit interruption
tests use `KeyboardInterrupt` at trusted hooks; they do not establish SIGKILL or
power-loss durability.

The runner fails on skipped tests, resource warnings and captured finalizer
exceptions. Dedicated CI executes the tests, suite and export recheck on Python
3.12 and 3.14, then repeats the unchanged assessor's tests and 23-case suite.
`run-suite` exits 0 only when all scenario expectations match and export consistency
checks complete; an expectation mismatch exits 1, invalid/incomplete input or IO exits 2.

## Outputs and rechecking

- `generated/runtime/LP-NN/visible/*.html`: actual locally created artifacts.
- `generated/runtime/LP-NN/journal.sqlite3`: one-shot intent and terminal observations.
- `generated/cases/LP-NN.json`: captured synthetic candidates, public trust, approvals,
  gate frames, local receipts and visible-file measurements.
- `generated/summary.json`: expected/actual findings, source manifest and case-file hashes.

Source hashes are captured before execution and compared afterward. They cover the
pilot runtime/tests/runner, catalogue, requirements, imported assessor runtime and
CI workflow. Documentation and stored result records are outside the manifest.

`verify-exports` recomputes the edit history, rendering, approval, policy and
preflight/final-gate assessments using the supplied synthetic public trust. It
cross-checks receipt scope, attempt/result consistency, visible-file measurements,
case inventory and summary counts. It does not repeat publication or observe the
current filesystem contents. A separate inspection of a subsequently modified
file must remain distinct from the earlier signed observation. Self-contained
test keys and matching hashes do not independently authenticate the original host.

The case exports contain synthetic article plaintext, since those bytes are the
object being reviewed. Private signing keys are excluded. This fixture format is
not a confidential-manuscript storage or retention design.

## Limits and next integration boundary

All roles share one trusted controller, clock and host user. The directory owner,
collector and reviewer keys can make false statements; no independent anchor,
real organizational identity or key revocation service is provided. LP-16 directly
writes outside the gate after a denied release to demonstrate that application
control is not complete route enforcement. Matching that negative control is not
a security or conformance pass.

Production work would require real identity and policy sources, an actual review
interface, secure confidential storage, externally enforced access control, trusted
provider instrumentation, key lifecycle handling and an adapter to the destination
publisher. Any publisher transformation must be observed and rebound to the produced
version. This experiment establishes no external acceptance, statutory disclosure
compliance, complete provenance, or normative VAP/CAP requirement.

Technical references: [Python file operations](https://docs.python.org/3.14/library/os.html),
[SQLite synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous),
[HTML escaping](https://docs.python.org/3/library/html.html#html.escape).
The repository's [CC BY 4.0 license](../../LICENSE) applies.
