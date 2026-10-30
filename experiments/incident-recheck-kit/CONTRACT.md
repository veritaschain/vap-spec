# Incident recheck kit contract

Informative offline tooling for a fixed, synthetic development evidence snapshot.
It packages existing evidence and invokes unchanged verifiers; it never runs
the original upload, publication or erasure operations. This is not independent
reproduction, an external trust anchor, a hermetic environment or conformance.
The fixed 24 October research distribution and existing pilot runtimes remain
unchanged. This new kit has snapshot ID `incident-ci-2026-10-30`.

## API and fixed inputs

The package is `incident_recheck`; its modules depend only on the standard library
until the worker explicitly imports the unchanged verifier and pinned packages.
`layout.py` exposes `KitError(ValueError)`, `ROOT` (kit directory), `REPO_ROOT`,
`SNAPSHOT_ROOT`, `SNAPSHOT_ID`, `PILOTS`, `KIT_SOURCE_FILES`, `load_source_lock()`,
`expected_payload_paths()`, `strict_json(bytes)`, `json_bytes(value)`,
`sha256(bytes)`, `safe_path(str)`, `collect_payload()` and `source_manifest()`.

PILOTS maps upload/publication/erasure to exact dict keys `directory`, `module`,
`prefix`, `count`, `source_sha256`. Counts are 17/18/18. Directories are repository
relative `experiments/incident-{upload,publication,erasure}-pilot`. Modules are
`upload_pilot`, `publication_pilot`, `erasure_pilot`.

Source lock exact fields: `format: incident-recheck-source-lock/0.1`,
`repository: veritaschain/vap-spec`, `source_commit` (the existing main SHA),
`provenance_sha256` (raw original capture record hash),
`files` (repo-relative source path to raw SHA-256), `pilots` (pilot name to
original source-manifest SHA-256). All original source manifest entries are
resolved to safe repo-relative paths in this lock, with conflicting shared
paths rejected. Tests, runners, requirements, workflows and assessor modules
required by old source manifests are included unchanged.

Snapshots retain original CI artifact bytes only: `snapshots/2026-10-30-ci/`
contains `provenance.json` and per-pilot `summary.json`, `cases/UL-01..17.json`,
`cases/LP-01..18.json`, `cases/LE-01..18.json`. Exactly 53 cases plus three summaries.
No raw runtime files, databases or private keys are copied. Publication JSON
does contain synthetic text/HTML needed for rechecking; no blanket no-plaintext
claim is made. All three captures come from the recorded Python 3.12 artifacts.

Archive payload names are `source/` plus each safe locked source path and each
fixed KIT_SOURCE_FILES path; `evidence/provenance.json`; and `evidence/` plus
pilot name and each fixed public export path. Expected paths are computed only
by trusted layout code, never by an archive-provided import path. `manifest.json`
is the sole additional archive member. Preserve original JSON bytes unchanged.

KIT_SOURCE_FILES includes the kit runtime modules, source-lock.json, explicit
requirements, generic README/RUN-ja instructions and repository LICENSE. It
excludes result records, new kit tests/CI/review and generated archives, avoiding
checksum self-reference. The new kit's separate execution source manifest still
includes tests/workflow/snapshot bytes to record its own CI inputs.

## Narrow archive format

`archive.build_archive(destination, payload: dict[str,bytes])` creates a new
archive without overwriting anything and returns archive_sha256,
manifest_sha256, file_count and payload_bytes. It requires the exact fixed payload
inventory, owned bytes and bounded sizes. It creates sorted ZIP_STORED entries,
constant 1980-01-01 timestamps, Unix regular-file mode 0644, no comments/extra
fields/encryption/data descriptors/ZIP64, and a deterministic manifest.
No generated timestamp enters the archive, so equal inputs yield equal bytes.

Manifest exact fields: `format: incident-recheck-archive/0.1`, `snapshot_id`,
`scope`, `entries`. Scope is exactly `{operation: OFFLINE_RECHECK_ONLY,
independent_reproduction: NOT_ESTABLISHED, actions_reexecuted: false,
conformance: NOT_ASSESSED}`. Entries is a path-sorted array of exact
`{path,sha256,byte_length}` for every payload file, excluding manifest.json.
`json_bytes` is sorted-key, ASCII JSON with compact separators and a trailing LF;
this archive manifest is not a new normative VAP/JCS format.

`archive.inspect_archive(path, expected_sha256)` requires an externally supplied
raw archive digest. It returns exact `manifest`, `files` (name->owned bytes,
payload only), `archive_sha256`, `manifest_sha256`. It does no extraction, import,
network access or action. It validates physical file bounds and external digest
before parsing ZIP. Limits: archive 16 MiB; member 4 MiB; members 256; aggregate
payload 12 MiB; central directory 128 KiB. All lengths/counts are actual integers.

Reject nonregular archive inputs/symlinks, malformed/trailing/overlapping ZIP,
duplicate or casefold-colliding names, unsupported flags/compression/encryption,
ZIP64/multidisk, nonregular entries, comments/extras and directory entries.
Require exact safe ASCII relative paths, no absolute/drive/backslash/NUL/empty/
dot/dotdot components. Verify CRC, full member inventory, raw digest and length
of every file before returning. Never call extractall or execute archive code.

## Rechecking and action boundary

`runner.recheck_archive(path, expected_sha256)` first uses inspect_archive, then
checks EVERY archived source file against the corresponding trusted local
checkout bytes and the original source lock. Evidence files are pinned by the
external archive digest; public provenance remains an attributed capture record.
Verify archived provenance matches the separately trusted source-lock hash and
summaries agree about inventory, original source
manifests, capture metadata and original raw-file hashes. The fixed capture schema
is validated strictly.

Only after complete archive/source validation, write the verified files into a
new private TemporaryDirectory, preserving `source/` repository topology and
`evidence/` fixed directories. This is bounded staging of authenticated bytes,
never general extraction into a caller-selected existing tree. Start a fresh
isolated Python worker per pilot (`-I -B`), using only the verified staged worker
and known enum-to-module mapping. Ignore PYTHONPATH and user site. The standard
library and installed third-party dependencies remain explicit external inputs.

Worker has no user-provided module/entrypoint. It imports the fixed pilot suite
and calls only `verify_exports`. No tests/run-suite/CLI action paths, HTTP calls,
publication, deletion or dependency installation are allowed. Install a Python
audit hook before verifier imports to refuse socket/process creation, filesystem
writes and mutation calls; this is an in-process guard, not OS sandboxing.
Use pinned dependency versions: cryptography 50.0.2, rfc8785 0.1.4, cffi 2.1.1,
pycparser 3.12. Missing/mismatched versions fail clearly; never auto-install.

`runner.run_worker(source_root,evidence_root,pilot, *, timeout=30)` is a test seam.
Bound stdout/stderr to 64 KiB each while reading, terminate on excess or timeout,
and require zero exit with exact structured JSON. A successful worker result has
exact fields format `incident-recheck-worker/0.1`, pilot, verified_exports,
actions_reexecuted (false), source_sha256, dependencies (exact four versions),
guard `PYTHON_AUDIT_EVENTS`. Counts/source must match the fixed PILOTS entry.
Never accept a success-looking string or a wrong/missing reexecution flag.

Final report exact fields: format `incident-recheck-report/0.1`, snapshot_id,
archive_sha256, manifest_sha256, source_binding `MATCHED_TRUSTED_CHECKOUT`,
verified_exports (53), pilots (ordered upload/publication/erasure worker results),
actions_reexecuted (false), independent_reproduction `NOT_ESTABLISHED`,
conformance `NOT_ASSESSED`, dependency_scope `PINNED_VERSIONS_NOT_HERMETIC`.
Any failed check fails the entire command; no promoted partial success report.

## CLI and evidence

`python -m incident_recheck build --output NEW.zip` collects the fixed trusted
source/snapshot files, builds, rechecks and reports the digest. Explicit
`inspect --archive ZIP --expected-sha256 HEX` and `verify --archive ZIP
--expected-sha256 HEX` commands respectively inspect or fully recheck it.
The digest must come from a reviewed source outside the candidate archive.
Users first verify a downloaded archive's raw hash before trusting its included
launcher/source. No automatic download, install or trust-on-first-use mode.

CI installs explicit dependencies, runs focused archive/runner/boundary tests,
builds twice and compares raw bytes, then verifies all 53 captures on Python
3.12 and 3.14. It records source hashes and artifact digest. Original evidence
is durably tracked as JSON; the ZIP is reproducible from those bytes after CI
artifact expiry. Neither matching hashes nor same-controller CI establishes
independent reproduction or the truth of original external-world observations.
