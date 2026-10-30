# Incident evidence review report

**Informative, automated presentation of a fixed synthetic capture.** This tool
turns the completed 53-case offline recheck into a source-attributed JSON report
and Japanese/English Markdown. The count means saved cases were rechecked; it is
not a count of secure operations or prevented incidents. Human review,
independent reproduction, observation truth, legal compliance and conformance
are not established by generating this report.

[Japanese instructions](RUN-ja.md) · [Japanese report](results/review-ja.md)
· [English report](results/review-en.md) · [Report JSON](results/review.json)
· [Execution record](results/README.md) · [Review](REVIEW.md)

## What this adds

The frozen [offline kit](../incident-recheck-kit/README.md) already retains exact
original signed cases and matching source. Reading a successful recheck summary
alone can hide the distinction between a matched test expectation and a favorable
operational result. A negative control can match its expectation because a bypass
or retained copy was observed. An authentic scoped statement can coexist with an
unknown outcome or an apparently conflicting observation at another time.

This report keeps those dimensions visible. Every evidence-derived fact points
to its original file, raw-file SHA-256 and concrete JSON Pointer. Case details
preserve the actual operation/record index, authorization phase, assessor values,
missing frames, receipt scope, exclusions, findings and relevant control
observations. Original article text/HTML and entire signature envelopes are not
copied into the presentation.

| Preserved distinction | Fixed capture examples |
|---|---|
| Controlled-path block and outside-path activity | UL-14 and LP-16 |
| Admission/postflight authorization and final gate | UL-10 |
| Unknown returned outcome and positive captured receiver/file observation | UL-07/08/16 and LP-14 |
| Declared activities and unknown origin/completeness | LP-09/10 |
| Scoped namespace removal and readable excluded copy/open handle | LE-12/13 |
| Absence-only evidence and completed deletion | LE-14 |
| Provider's scoped statement and later present observation | LE-15 |
| Provider evidence and missing observer evidence | LE-18 |

These are interpretations of the preserved synthetic cases, not additional
observations of external systems. The original pilot records and their limitations
remain available through each report's evidence references.

## Verification before presentation

The reporter pins the 136 execution-source files recorded for the frozen kit
merged at [`1553ff9729ceb30f3ff03513cead45c5b7abd1d9`](https://github.com/veritaschain/vap-spec/commit/1553ff9729ceb30f3ff03513cead45c5b7abd1d9).
It verifies those file hashes before importing the sibling kit. Already loaded
kit modules from a different origin are refused. Module names, templates and
entrypoints cannot come from a candidate archive or report.

The reporter inspects the kit into owned bytes and actually invokes the unchanged
`recheck_archive` under the same externally supplied archive digest. It requires
the exact complete result: 53 exports, ordered 17/18/18 pilot results, matching
archive and manifest hashes, matched source, exact pinned dependencies and false
action-reexecution flags. It accepts no precomputed success JSON as a substitute.
Only after those checks does it derive the report from the owned evidence bytes.
Every projected fact is checked against its concrete source pointer, and source
identities are checked again before a final report can be published.

Uniform reference hashes are computed over raw file bytes. This matters because
the old upload summary's export hash used canonical parsed JSON, whereas the
publication and erasure summaries hashed raw files. The report does not silently
treat those conventions as interchangeable.

## Build on Linux

Use a trusted, reviewed checkout containing this reporter and the unchanged
frozen kit. Python 3.12 and 3.14 are CI targets. Prepare dependencies explicitly
before offline work:

```sh
cd experiments/incident-review-report
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements.txt
```

Obtain the original kit using its [documented instructions](../incident-recheck-kit/RUN-ja.md).
The supported inner kit ZIP has SHA-256:

```text
06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f
```

Then build a new report ZIP:

```sh
.venv/bin/python -m incident_review build \
  --archive /absolute/path/incident-ci-2026-10-30.zip \
  --expected-sha256 06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f \
  --output /absolute/path/new-review.zip
```

The output parent must already exist. The tool completes validation and renders
all bytes before writing a private temporary file in that parent. It finishes
and synchronizes that file, then publishes it with an exclusive hard link.
Existing files, directories and symlinks are never overwritten. Normal failures
before publication leave no final report. This is not a crash-durability or
post-publication rollback guarantee.

## Reverify a received report

Obtain the expected report ZIP digest from a reviewed result outside that
candidate report. `verify` checks its raw digest, rechecks the original kit,
rederives the complete expected report and compares exact bytes:

```sh
.venv/bin/python -m incident_review verify \
  --archive /absolute/path/incident-ci-2026-10-30.zip \
  --expected-sha256 06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f \
  --report /absolute/path/received-review.zip \
  --expected-report-sha256 EXPECTED_REPORT_HEX
```

Rewriting a displayed outcome, its JSON, the inner manifest and the candidate's
self-reported checksums cannot satisfy this comparison. No candidate report code
is executed, and the verifier does not extract or parse its ZIP members. Report
contents remain untrusted until this source-bound rederivation succeeds.

## Deterministic bundle and traceability

The four fixed ZIP members are:

- `review.json`: authoritative projection, including input hashes, reporter-source
  identity, full recheck result, scope, pilot metadata and all 53 source-attributed cases.
- `review-en.md` and `review-ja.md`: deterministic views with the JSON hash,
  literal verdict values, separate stages and concrete evidence references.
- `manifest.json`: raw hashes and lengths of the other three files; it excludes
  itself to avoid circular identity.

ZIP entries are stored without compression, sorted, stamped with fixed 1980
timestamps and regular-file mode 0644. New clocks, random identifiers, temporary
paths and output names do not enter report content. Each member is bounded to
2 MiB and the complete bundle to 6 MiB. Same source and same fixed capture produce
the same bytes across the tested Python versions.

Markdown escapes source text and uses only fixed-commit GitHub evidence links.
It does not insert saved article HTML as markup, use arbitrary evidence strings
as URLs or load remote assets. Original `UNKNOWN`, `NOT_ESTABLISHED`,
`NOT_ASSESSED` and missing-frame states remain distinct. Sorted summary arrays
are never zipped into invented record associations; the original `records` or
`reports` indices supply those relationships.

## Assurance limits and source versioning

The report labels `human_review: NOT_PERFORMED`. Its notes are fixed presentation
guidance for a frozen synthetic dataset, not human approvals, general-purpose
incident judgments, legal advice or a standards conformance assessment. It keeps
`actions_reexecuted: false`, `observation_truth: NOT_ESTABLISHED`,
`independent_reproduction: NOT_ESTABLISHED`, `conformance: NOT_ASSESSED`,
`legal_compliance: NOT_ASSESSED` and `dependency_scope: PINNED_VERSIONS_NOT_HERMETIC`.

The interpreter, local reporter checkout, host and installed dependencies remain
trusted. The sibling kit's worker audit hook is an in-process guard, not an OS
sandbox or a defense against a hostile interpreter/native library. A valid
signature attributes a statement under the captured trust assumptions; it does
not independently establish its truth. Rendering the evidence does not widen
its observation boundary or recover events that were never recorded.

The kit's original archive, existing pilot runtime, captured cases, normative
VAP v1.2 Draft 3 and fixed historical research assets remain unchanged. This is
a separate, unadopted experiment. Different capture bytes or a changed reporter
source require a new report digest and a reviewed execution record. Results,
review notes and this contract are excluded from the execution-source manifest;
generic operating instructions are included. Do not embed a report's own output
digest into its measured source inputs.

## Development validation

```sh
.venv/bin/python -W error::ResourceWarning run_tests.py --require-no-skips
.venv/bin/python -W error::ResourceWarning record_run.py --output generated
```

Tests cover real frozen evidence projection, phase/record associations, negative
controls, missing frames, reference correctness, malformed verification results,
source/import substitution, Markdown escaping, deterministic delivery, exclusive
publication and report rederivation. CI records sources before and after testing
and rendering, performs actual 53-case rechecks and preserves the report bundle
and readable views. It performs no original upload, publication or erasure run.
