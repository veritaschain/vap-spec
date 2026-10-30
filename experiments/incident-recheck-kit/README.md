# Incident evidence recheck kit

**Informative development tooling.** This kit preserves the original public
Python 3.12 CI captures from three synthetic incident-derived pilots and packages
them with the matching reviewed source. It rechecks 53 saved cases without
repeating upload, publication or erasure. It does not establish independent
reproduction, truthful original observations, production route control, legal
compliance or VAP conformance. The normative VAP version remains v1.2 Draft 3.

[Japanese operating instructions](RUN-ja.md)
· [Recorded results](https://github.com/veritaschain/vap-spec/tree/main/experiments/incident-recheck-kit/results)
· [Review](https://github.com/veritaschain/vap-spec/blob/main/experiments/incident-recheck-kit/REVIEW.md)
· [Source lock](source-lock.json)
· [Capture provenance](https://github.com/veritaschain/vap-spec/blob/main/experiments/incident-recheck-kit/snapshots/2026-10-30-ci/provenance.json)

## Why preserve a kit

The earlier pilot summaries identify successful development runs, but a summary
cannot reconstruct the signed case evidence needed by `verify-exports`. The
original Actions artifacts have finite retention. This experiment retains the
exact original public JSON bytes in Git, so those particular captures can still
be rechecked after an artifact expires. A new execution would create different
keys, identifiers and timestamps and would be a different capture.

The three pilots are separate experiments. Packaging their records together does
not turn them into an integrated production workflow or establish that every
path to an AI provider, publisher or stored copy is controlled.

## Fixed capture

Snapshot identifier: `incident-ci-2026-10-30`.

| Pilot | Saved cases | Original CI run | Rechecked statements |
|---|---:|---|---|
| Controlled upload | 17 | [40985604010](https://github.com/veritaschain/vap-spec/actions/runs/40985604010) | Signatures, payload and destination bindings, decisions and recorded receiver observations |
| Local publication | 18 | [40990072945](https://github.com/veritaschain/vap-spec/actions/runs/40990072945) | Candidate and disclosure bindings, approval statements, decisions and recorded file observations |
| Local erasure | 18 | [40997508247](https://github.com/veritaschain/vap-spec/actions/runs/40997508247) | Scoped erasure statements, signatures, decisions and bounded recorded readback |

The capture contains 53 case JSON files, three original summary JSON files and
one provenance record. Each original artifact was obtained from GitHub, checked
against its already recorded raw archive SHA-256, and only its fixed public
summary/case members were copied. Original public JSON was not reformatted.
The provenance record binds every copied file's raw bytes, original artifact
digest, run, job and actual checkout commit. The upload run used a PR merge
checkout; its PR head is not misidentified as the actual checkout.

The 61 distinct original source files are locked to their raw hashes and three
original source-manifest hashes. Their common repository snapshot is
[`b72bbf05c912f5b87560f4c809298c7bbcaf05e4`](https://github.com/veritaschain/vap-spec/commit/b72bbf05c912f5b87560f4c809298c7bbcaf05e4).
That commit identifies the pilot inputs, not the later kit implementation. The
kit's own source manifest and tested commit are recorded separately in results.

Runtime databases, WAL/SHM files, private signing keys and separate runtime
objects are not copied. Publication case JSON contains synthetic article text
and HTML required by its original verifier. This is not a no-plaintext archive;
the experiment contains no real patient data or real publisher credentials.

## Recheck from a trusted checkout

Use Linux and a reviewed checkout of this kit. Python 3.12 and 3.14 are the CI
targets. First prepare dependencies explicitly; installation may need a network
connection and occurs before offline verification:

```sh
cd experiments/incident-recheck-kit
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements.txt
mkdir generated
.venv/bin/python -m incident_recheck build --output generated/incident-ci-2026-10-30.zip
```

`build` refuses an existing destination, packages the fixed inventory and then
rechecks all cases. It emits an archive hash and structured report only after all
three workers succeed. If a worker fails, the created archive may remain for
inspection, but no successful recheck report is emitted. Remove it deliberately
or choose a new output name before retrying.

For a separately obtained candidate archive, obtain the expected SHA-256 from a
reviewed result record outside that candidate and supply it explicitly:

```sh
.venv/bin/python -m incident_recheck inspect --archive /path/to/candidate.zip --expected-sha256 EXPECTED_HEX
.venv/bin/python -m incident_recheck verify --archive /path/to/candidate.zip --expected-sha256 EXPECTED_HEX
```

`inspect` checks the archive's raw hash, narrow ZIP representation, exact
inventory and member hashes. It neither imports candidate code nor rechecks the
saved exports. `verify` additionally compares every archived source file with
the trusted checkout, validates the locked original capture provenance, and then
starts the fixed recheck workers. A changed verifier cannot authorize itself by
rewriting its own manifest or source lock.

Never use only a checksum supplied inside the candidate as the expected checksum.
A matching hash identifies bytes relative to the trusted expected value; it
does not establish who authored the original statements or whether they are true.

## Portable layout and deterministic bytes

The ZIP contains `manifest.json`, `source/` with the required repository topology,
and `evidence/` with the fixed public capture. It includes the kit's launcher,
instructions, source lock, dependencies declaration and repository license. After
validating the raw hash against an independently obtained, reviewed result and
inspecting the archive with trusted code, its verified payload can be staged in
a fresh directory. The launcher under
`source/experiments/incident-recheck-kit/` automatically finds the sibling
`evidence/` directory. The standalone integration test verifies that this topology
can recheck and rebuild the same archive without access to the original checkout.

This bootstrap still requires trust in the reviewed kit source or externally
obtained expected archive hash. Running an unverified included launcher and
accepting its self-reported hash is not verification.

The format uses sorted `ZIP_STORED` entries, fixed 1980 timestamps, regular-file
mode 0644 and no extra fields, comments or data descriptors. Equal payload bytes
produce equal archive bytes across the tested Python versions. The manifest uses
the kit's deterministic JSON encoding; it is not a normative VAP format. Bounds
are 16 MiB per archive, 4 MiB per member, 256 entries, 12 MiB total payload and
128 KiB for the central directory. Unsupported ZIP features, unsafe paths,
duplicates, symlinks, extra entries, overlapping records and trailing data fail.

## Execution boundary and remaining assumptions

All source and provenance checks finish before temporary staging or worker
execution. Each worker starts a fresh `-I -B` interpreter with a fixed
pilot-to-module mapping and calls only the unchanged `verify_exports` function.
Candidate-provided import paths and entrypoints are not accepted. The worker
ignores `PYTHONPATH` and user site packages. It refuses audited socket/process
creation and filesystem mutation, and a swallowed denial still fails the run.
Output is bounded while reading; a worker timeout or malformed response fails
the entire recheck. The parent writes verified temporary staging files and
removes them on completion; this is distinct from reexecuting pilot actions.

The Python audit guard is an in-process guard, not an OS sandbox. The interpreter,
host and installed dependency binaries remain external trust assumptions. The
worker checks both distribution and loaded-module versions for `cryptography`
50.0.2, `rfc8785` 0.1.4, `cffi` 2.1.1 and `pycparser` 3.12. Dependencies are not
vendored or wheel-hash locked, so the report explicitly says
`PINNED_VERSIONS_NOT_HERMETIC`. No command downloads or installs dependencies.

Successful recheck reports retain `actions_reexecuted: false`,
`independent_reproduction: NOT_ESTABLISHED` and `conformance: NOT_ASSESSED`.
Existing unknown outcomes and negative route-control observations remain in the
original evidence. Same-controller signatures, separate keys and CI runs do not
become independent witnesses merely because they can be verified elsewhere.
This kit cannot prove an external provider deleted every copy, determine all AI
contributions from an imported article, or satisfy an institution's disclosure
policy automatically.

## Validation and versioning

```sh
.venv/bin/python -W error::ResourceWarning run_tests.py --require-no-skips
.venv/bin/python record_run.py --output generated-validation
```

Focused tests cover the archive grammar, trusted source boundary, original raw
capture binding, isolated workers, action denials, bounded child output/time,
full 53-case recheck and standalone deterministic rebuild. CI records the exact
source manifest before and after testing/building and fails on source drift.
Generated ZIPs and summaries are CI artifacts; original evidence and the source
needed to regenerate the ZIP remain in Git. Result documents are excluded from
the archived source set to avoid embedding a ZIP's own digest in its inputs.

This experiment does not modify the fixed October 24 research distribution,
historical tags/assets, original acceptance catalogue or existing pilot runtime.
A changed capture or archive format needs a new explicit identifier and reviewed
result; it must not silently replace this snapshot's recorded bytes.
