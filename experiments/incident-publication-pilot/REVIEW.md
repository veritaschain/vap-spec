# Internal boundary review — local publication pilot

Review date: 2026-10-30. Status: **experimental, synthetic and unadopted**.
This review was performed within the implementation task. It is not independent
third-party reproduction, evidence of real human inspection, production approval,
or VAP/CAP conformance certification.

## Reviewed boundary

The pilot imports the unchanged incident evidence assessor. Its advisory
`publication_action: REVIEW` remains unchanged when the additional local release
rule succeeds. An explicitly signed synthetic reviewer authorization supplies
that separate release decision; an assessor result alone does not authorize a
filesystem operation.

The controlled renderer creates one escaped HTML artifact containing article
blocks and a visible structured disclosure. The approval binds the captured
candidate, exact final HTML, disclosure, policy and local destination. No
approval, self-hash or new rendering is inserted after approval. The source
document-state digest and signed-lineage digest remain distinct from the hash
of the actual final HTML bytes.

Gate configuration independently pins the venue, route, policy ID/version/hash,
stage, authorities and full public-key metadata. Required evidence must have the
proper signer, role, time and full target binding. Collector operation and
checkpoint times must fall within that configured key's validity. Both forms
of reviewer authorization must agree on the same candidate, target and validity.
The local publisher's identity is checked before it can materialize bytes.

The gate checks policy and reviewer authorization again immediately before the
atomic publication call. The store requires a matching durable one-shot claim,
uses a non-overwriting same-filesystem link, fsyncs the visible directory, reads
back a bounded regular file without following symlinks, and verifies identity,
hash and length before signing a receipt. An existing output is not replaced or
adopted as a new result. Replays do not retry or reassert stored receipt truth.

## Operation history and origin claims

Actual local block replacements are signed and replayed against their before
and after document states. The checkpoint binds the operation count, chain head
and complete final state. These checks support consistency of the supplied
recorded session under the configured collector trust.

The generation, editing, proofreading and translation labels describe simulated
adapter operations. The editor calls no external AI model. The records do not
establish the origin of imported content, activity outside the editor, complete
authorship history, AI-generated percentages or the truth of article content.

Only a block whose last recorded replacement is a simulated assistance operation
qualifies as that operation's current exact output. A later manual edit or import
removes that exact-output adoption assertion while preserving the historical
activity. The disclosure retains every recorded simulated activity. The local
release policy checks that history, so replacing an output does not silently
erase a prohibited session activity. This is an explicit release-eligibility
rule, not a retroactive legal finding about earlier use.

Import-only content can be locally released with an explicit authorization, but
its core AI-involvement and activity-completeness results remain `UNKNOWN`.
Reviewer signatures attribute synthetic assertions; they do not prove that a
person actually read or understood the artifact.

## Findings resolved and preserved in tests

The independent boundary tests cover ten areas:

1. Actual final-file bytes and receipt measurements, escaped markup, unchanged
   core `REVIEW`/unknown results and exclusion of fresh private keys from exports.
2. Changed HTML, a new revision with an old approval and a newly approved notice
   that nevertheless omits recorded session activity.
3. Controller-pinned key roles, validity and issuers, policy versions, publisher
   identities and destinations.
4. Reviewer signature identity and agreement between the separate release
   authorization and the existing assessor approval record.
5. Historical prohibited activity after its exact output has been manually
   replaced, without falsely asserting current exact-output adoption.
6. Final approval expiry and collector operations outside their key validity.
7. A postpublication clock failure retaining the already known attempt and
   visible file instead of changing that observation to an unattempted operation.
8. Validly signed receipts with wrong scope, types, filename or chronology.
9. Saved reports that hide an attempt, disagree with the publisher result, lack
   committed confirmation, name another visible file or use a denied final gate.
10. Import-only provenance, missing reviewer authorization and unresolved policy.

Review corrections added the publisher-key precondition and preserved returned
IO observations before postflight clock acquisition. An unavailable observation
is explicitly unknown; it is not inferred to mean that publication did not
happen. The gate's confirmed result and offline recheck now require matching
attempt observations, terminal journal state, visible name and signed receipt.
The independent tests reproduced the missing terminal-state and filename checks
before repair.

Additional integration corrections made captured checks reproducible across JSON
dictionary ordering, compared both visible hash and length with candidate bytes,
and captured the source manifest before scenario execution. A changed source
manifest prevents issuance of a completion summary. Current file observations
are checked separately from the earlier signed receipt; later modification does
not rewrite the historical observation.

## Validation checkpoint

The final local validation completed with **45 test methods passed, zero skips
and no finalizer errors**:

| Test area | Methods |
| --- | ---: |
| Independent gate and report boundaries | 10 |
| Editor, signed lineage and rendering | 14 |
| Actual local publication store | 17 |
| Suite and observation integration | 4 |

The strict test runner treats `ResourceWarning` and unraisable finalizer errors
as failures. The final run recorded none. All **18 actual local-filesystem
scenario expectations matched**, and all **18 saved case exports rechecked**.
The publication store and boundary tests exercised real files, SQLite state,
atomic links and Ed25519 verification. No network capability or simulated HTTP
delivery was needed for these observations.

The dedicated workflow runs the strict zero-skip tests, measured scenario suite,
export recheck and unchanged assessor regression on Ubuntu with Python 3.12 and
3.14. Local completion does not establish CI completion; the workflow results
and retained artifacts for the reviewed commit determine that separately.
The subsequently retrieved successful runs and source manifest are recorded in
[Execution records](results/README.md).

The source manifest covers pilot modules, tests and root entry points, the
acceptance catalogue, requirements, imported assessor modules and the workflow.
Rechecking verifies supplied signatures, captured decisions, measurements and
inventory against that source snapshot. It does not repeat filesystem actions
or independently prove the original host's observations.

## Retained limitations

- The controller, host user, clocks, publisher and configured signing authorities
  are trusted. Distinct keys and processes do not establish independent parties
  or OS isolation.
- The one-shot journal and local fsync/readback sequence support the tested
  storage behavior. They do not establish immutable storage, external anchoring
  or survival under every hardware failure.
- Read-only file mode is not permanent immutability. The trusted owner can change
  permissions or replace a file. The explicit outside-gate write demonstrates
  the limit of this application path; matching that negative control is not an
  all-route security pass.
- Public examples retain synthetic source text, disclosure and HTML as intended.
  Private signing keys are excluded. No confidential article, patient data or
  real production credentials are used.
- There is no real AI-service invocation, external website publication, publisher
  editorial acceptance, legal determination or normative modification. Local
  output and receipt are not emitted as new core dispatch or receipt verdicts.

No blocking implementation finding remained within this declared boundary at
the local validation checkpoint.
