# Evidence retention and evaluator report

Preserve the **whole fresh output directory**, including failed runs:

| Artifact | Purpose |
| --- | --- |
| `run-report.json` | Start/end times, package-file hashes, preflight/postflight source identity, ordered steps and completion status. |
| `SHA256SUMS.json` | Byte hashes and exact inventory of output files except this manifest itself; integrity inventory, not a signature. |
| `preflight.json` | Source lock/hash count, Python and dependency versions, host/kernel, Docker/Compose versions and reference deviations. Absent if preflight could not complete. |
| `logs/*.log` | Original stdout/stderr and regression totals for every started step. |
| `lab/` | 16-case observations, build log, runtime inspection, environment, cleanup and signed evidence bundle. |
| `gate/` | 15-case summary, individual scenarios, exported bundles and synthetic latency samples. |
| `verifier/` | 14 generated evidence/trust fixtures, manifest, both modes' reports and summary. |

Retain the package ZIP and its SHA-256 and source acquisition URL/commit too.
Copy `templates/evaluator-report.json` **outside** the checksummed results and
fill unknown fields honestly (leave null if unverified). Record affiliation,
relationship to implementers, who provisioned/controlled the machine, whether
the evaluator personally performed a new run, all deviations, artifact locations
and conclusions. No report is automatically posted or sent anywhere.

`matched` is a machine comparison result. A person reviewing provenance must
separately decide whether the evaluator and execution are independent. Downloading
an author's successful outputs and running `check` is an offline artifact check,
**not** an independent OS reproduction. Self-declared affiliation is not identity
verification. Even another evaluator's successful fresh run is evidence limited
to that environment and the listed tests, not specification adoption.

## Failure handling

- Wrong commit, dirty or ignored execution inputs: preserve any relevant work and
  obtain a new clone at the pinned commit. Do not weaken the source lock.
- Missing/wrong dependencies or unavailable Docker: repair the isolated environment,
  record the change, run `preflight` again. Preflight never installs software or
  grants privileges automatically.
- Existing output path: use another new path. Do not delete a failed run to hide it.
- Scenario mismatch, missing evidence or regression-count discrepancy: keep logs,
  actual results and exact environment. Do not alter `expected-results.json` or
  claim success from the top-level exit code of an individual verifier.
- Timeout, interruption, host loss or cleanup failure: mark the run incomplete.
  Automatic cleanup is best effort on abrupt termination. Inspect only this run's
  `vap-isolation-<10 hex digits>` Compose project and temporary image; identify it
  from the logs/runtime volume names before removing anything. Record any manual
  cleanup. Never use global Docker prune as part of this procedure.
- Changed artifact hash or unexpected extra file: retain both copies and investigate.
  Do not regenerate `SHA256SUMS.json` to make an altered evidence set pass as the
  original run. Store annotations separately.

Re-run the entire `run` command into a new output directory after repairs. Every
attempt keeps a separate report. A discrepancy is useful reproducibility evidence,
not a reason to silently select only successful cases.

## Known distribution limits

The fixed commit and per-file hashes constrain the subject source; exact Python
versions constrain dependencies by release number, not artifact hash. The pinned
base image does not freeze the host or the package indexes. Supply-chain authenticity,
full bit-for-bit builds and offline installation are outside this package. Original
cryptographic verification uses **mock** trust; it does not authenticate the human
operator, Linux host or the result manifest. Do not include real credentials or
unnecessary personal/host information in public reports. Review raw logs before
publishing; this kit does not send them to any external evaluator.
