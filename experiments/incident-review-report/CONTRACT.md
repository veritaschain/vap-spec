# Incident review report contract

An informative, deterministic presentation of the frozen synthetic 53-case
capture. This is a sibling of incident-recheck-kit; no frozen kit, original pilot,
capture, historical research asset or normative specification is changed.

## Public flow and trust

CLI: `python -m incident_review build --archive KIT.zip --expected-sha256 HEX
--output NEW_REPORT.zip`; `verify` takes those two input arguments plus
`--report REPORT.zip --expected-report-sha256 HEX` and rederives exact report bytes.
There is no input-summary/report-JSON shortcut, arbitrary template, URL fetch,
dependency installation or original pilot action invocation.

Before importing kit code, the parent verifies a local toolchain lock covering
the 136 recorded PR35 execution-source files. The expected kit archive and manifest
identities are fixed in that reviewed lock. The parent captures owned files with
the unchanged `inspect_archive`, runs the unchanged `recheck_archive` under the
same externally supplied archive hash, and requires the complete exact report
contract with 53 exports and ordered counts 17/18/18. The returned archive and
manifest hashes must match the captured bytes. Source identity is checked again
before publication. Derivation uses only retained owned evidence bytes.

This assumes a trusted local reporter checkout, interpreter, host and installed
dependencies. A source hash is a byte identity, not an independent endorsement.
The existing kit's Python audit guard remains an in-process guard, not OS isolation.

## Shared helpers

`incident_review.common` exposes `ReviewError(ValueError)`, `ROOT`,
`REPO_ROOT`, `VERSION`, `PILOTS` ordered upload/publication/erasure with case counts,
`json_bytes(value)` (deterministic ASCII JSON, sorted keys, compact plus LF),
`strict_json(raw)`, `sha256(raw)`, `reference(files,file,pointer)`,
`fact(files,file,pointer,name=None)` and `resolve_pointer(value,pointer)`.

References are exact `{file,sha256,pointer}`; SHA is always raw-file SHA-256.
Facts are exact `{name,value,source}`, where source is a reference and value is
resolved from its concrete JSON Pointer. Only owned bytes and existing concrete
paths/pointers are accepted. No wildcards or nonexistent reference targets.

## Projection API and report shape

`projection.project(files,recheck,reporter_identity)` returns a plain report dict.
It is an internal post-verification projection, not an alternative verifier.
`reporter_identity` is `{version,source_sha256,source_manifest}` for the current
reviewed reporter and frozen execution inputs; results/review/contract files are
excluded to avoid circular output hashes. It contains no clock, output location,
temporary path or newly generated identifier.

Top-level exact fields:
`format: incident-review-report/0.1`, `snapshot_id: incident-ci-2026-10-30`,
`reporter`, `input` (`archive_sha256`, `manifest_sha256`, `provenance_sha256`),
`recheck` (the complete unchanged verified kit result), `scope`, `counts`,
`pilots`, `cases`.

Scope is exactly:
`{actions_reexecuted:false, observation_truth:NOT_ESTABLISHED,
independent_reproduction:NOT_ESTABLISHED, human_review:NOT_PERFORMED,
conformance:NOT_ASSESSED, legal_compliance:NOT_ASSESSED,
dependency_scope:PINNED_VERSIONS_NOT_HERMETIC}`.
Counts: `{saved_cases_rechecked:53, scenario_expectations_matched:53,
per_pilot:{upload:17,publication:18,erasure:18}}`. Neither count is a security score.

Pilots are an ordered list of `{pilot,source_sha256,summary_source,
capture_source,metadata}`. summary_source points to the whole original summary;
capture_source points to /pilots/<pilot> in provenance; metadata is a list of facts
for recorded capture time, original execution type, independence and scope limits.
Do not include the original source_files map or summary results as metadata.

Cases are ordered by pilot then fixed case number. Each exact row:
`{pilot,case_id,capture_source,title,expectation,sections,frames,notes}`.
capture_source points to the whole raw case; title is a fact from summary title.
expectation has exact `{matched,expected,actual,differences}` fact fields from the
corresponding original summary row. Label expectation MATCHED, never PASS.

Each section is `{key,operation_index,facts}`; key is a fixed code such as
`actual`, `additional_observations`, `operation`, `retained_control`, `probe`.
operation_index is null for case-wide observations or the original record index.
facts preserve recorded operation state/attempt/reason, local observations,
local authorization phases, receipt scope and exclusions, without copying source
article HTML/text or entire signature envelopes. Never zip independently sorted
summary arrays to associate records. Preserve operation/record index order.

Each assessor frame is `{operation_index,phase,availability,absence_reason,
source,evidence_integrity,assessments,findings}`. availability is `RECORDED` or
`FRAME_NOT_RECORDED`. For recorded frames absence_reason=null and the last three
fields are facts. For missing frames, absence_reason is `NULL_CONTAINER` or
`MISSING_FIELD`, the last three fields are null and source points to the nearest
existing container that demonstrates absence. Do not invent UNKNOWN dimensions.
Preserve upload preflight/final_gate/postflight separately and publication
preflight/final_gate separately. Erasure frames retain their original record pair.

Each note is `{code,sources}` with a fixed explanatory code and one or more exact
references. All codes must be documented in `projection.NOTE_TEXT`, a mapping
code -> `{en,ja}`. Notes are interpretations of this fixed capture, not new
observations or generalized decisions. At minimum retain UL14/LP16 bypass,
UL10 final-gate distinction, UL07/08/16 unknown outcome with receiver observations,
LP09/10 unknown origin, LP14 unknown outcome with output, LE12/13 readable retained
data, LE14 absence-only, LE15 later presence and LE18 absent observer evidence.

## Rendering and single-file publication

`delivery.render_members(report)` returns exact owned bytes for `review.json`,
`review-en.md`, `review-ja.md`, `manifest.json`. JSON is the authoritative projection.
Markdown binds the JSON SHA-256, shows counts and scope first, then pilot/case
observations, all recorded core dimensions and missing frames, notes and source
references. Every factual value remains attributable to file/hash/pointer. Source
references may link only to fixed GitHub commit 1553ff9729ceb30f3ff03513cead45c5b7abd1d9
under the snapshot directory. Do not use source strings as URLs, raw HTML or code
fences. Escape Markdown/HTML special characters including pipes/backticks/newlines.
No compliance grade, green security pass or human-review signature is generated.

Manifest exact `{format:incident-review-bundle/0.1,entries:[{path,sha256,byte_length}]}`
for the other three members, sorted by path. It excludes itself.
`delivery.bundle_bytes(report)` produces a deterministic ZIP_STORED with those
four regular0644 members, sorted names, fixed1980 timestamps, no extras/comments.
Bounds: each output member <=2MiB; full bundle <=6MiB.

`delivery.publish_bundle(destination,raw)` publishes already-complete owned bytes
without overwriting an existing file, directory or symlink. Use a private temporary
file in the destination's existing parent, finish/fsync it, then exclusive hard
link publication. Clean up the temporary name on success/failure. Do not claim
crash durability or rollback after the final link; normal pre-link failures expose
no final file. A pre-existing destination always fails, including races.
`delivery.read_bundle(path,expected_sha256)` captures bounded stable regular bytes
and validates the mandatory external raw SHA; it does not parse or extract ZIP.

Core verify rederives the expected bundle through actual kit verification and
compares bytes. Edited reports, rewritten self-hashes and misleading verdicts
cannot pass even with a recomputed candidate-bundle checksum.

## Validation

Projection tests cover concrete pointers, every original case/core frame,
negative controls, phase distinctions, null frames, raw digest conventions and
record association. Delivery tests cover deterministic bilingual rendering,
escape boundaries, closed filenames, strict member/bundle limits and exclusive
publication cleanup. Separately authored boundary tests cover unsuccessful/malformed kit
results, fixed-source import poisoning, report substitution and no output on
failure. Integration verifies real53 generation and byte-identical rederivation.
CI runs Python3.12/3.14 and records sources before/after, test results and report
digest. All original frozen inputs must remain byte-identical.
