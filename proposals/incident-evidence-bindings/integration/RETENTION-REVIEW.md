# Separate review of saved retention evidence

**Proposed review procedure; informative and unadopted — 2026-10-31 JST.**
This document defines a bounded review target for the PR40 retention adapter.
It records expected checks, not a commissioned review, completed reviewer
statement, certification or new experiment result.

The [original review procedure](EXTERNAL-REVIEW.md) and
`external-review-template.json` identify the PR36 kit/report and 53 saved cases.
They remain unchanged targets. Do not use that template's archive identities
or case count for this separate 16-case capture.

## 1. Record the scope before execution

The question is whether the reviewer can re-evaluate the preserved signed
inputs and obtain their recorded reports and finite expected observations,
using the matching source and explicitly recorded synthetic trust assumptions.
This is a saved-evidence recheck. It performs no new provider request,
storage inspection, upload, erasure or original pilot operation.

Before running, record the reviewer or review identifier, chosen source and
capture, acquisition/trust basis, environment controller, planned commands,
expected observations and failure criteria. Preserve that plan and identify
later corrections separately. Do not enter producer results as observations
made by the reviewer.

## 2. Fix the target outside the candidate capture

| Item | Expected identity |
| --- | --- |
| Repository | https://github.com/veritaschain/vap-spec |
| Matching source checkpoint | [`62d15f1b8d3c46a1704acb7c0d5631622e1a5608`][source] |
| Experiment directory | `experiments/incident-retention-adapter/` |
| Saved capture, relative to that directory | `results/local-python-3.12/` |
| Saved summary | [`results/local-python-3.12/summary.json`][summary] |
| Summary raw-file SHA-256 | `96b7ad9c574a3777fc9366dc9e5b3cf763cfce099e4e1b0771e203788774873f` |
| Fixed case inventory | RT-01 through RT-16, in `cases/` |
| Execution source inventory | The 22 file hashes in the saved summary's `source_manifest` |

Obtain the expected source and summary digest from a source the reviewer trusts
outside the candidate capture, and record why it is trusted. A digest copied
from an unknown bundle is not an independent expected value. A matching hash
identifies bytes; it does not establish who performed the recorded run or the
truth of a provider or collector statement.

Use the complete repository checkout at the identified commit, not only a copy
of the experiment directory. The adapter imports the original assessor, and
the source manifest also covers its Python files, dependency requirements and
the dedicated workflow. Record the output of `git rev-parse HEAD` and any local
modifications. A moving branch name is not the fixed source identity.

Prepare Python 3.12 or 3.14 and install the checkpoint's existing requirements
before the offline recheck. From the repository root:

```sh
git rev-parse HEAD
git status --short
cd experiments/incident-retention-adapter
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

The requirements reuse the pinned dependencies of the original assessor.
Record the actual interpreter, dependency versions, platform, distribution
origins and restrictions. Package versions do not by themselves pin dependency
binary hashes or the complete environment. The reviewer selects an environment
suited to the source they have reviewed; the candidate evidence must not select
executable code or dependency downloads.

## 3. Compare the digest, then recheck the saved evidence

From the experiment directory, compute the saved summary's raw-file SHA-256:

```sh
.venv/bin/python -c "import hashlib,pathlib; print(hashlib.sha256(pathlib.Path('results/local-python-3.12/summary.json').read_bytes()).hexdigest())"
```

Compare the actual output with the separately obtained expected digest above.
If it differs, retain the mismatch and do not silently replace the target or
expected value. Once the intended bytes and source are established, run:

```sh
.venv/bin/python suite.py verify results/local-python-3.12
```

Preserve the actual command, interpreter, stdout, stderr and exit status.
The verifier reads the saved public signatures and synthetic evaluator trust;
it does not create replacement keys or regenerate the fixtures. It compares
the source manifest, exact case inventory, file hashes, signatures, complete
recomputed reports, finite expectations and cross-case invariants.

A successful run is expected to return exit status 0 and this JSON content
(field order and whitespace are immaterial):

```json
{
  "rechecked": 16,
  "source_manifest_matches": true,
  "cross_case_checks": {
    "clock_only_inputs_reuse_identical_signed_records": true,
    "clock_only_change_preserves_deletion_assessment": true
  }
}
```

This block is an expectation to compare with the reviewer's output, not a
prefilled result. A failure, unreadable file, source mismatch or unexpected
output is a finding. Keep the original evidence and diagnostics. If assistance
or a repair is needed, identify the revised attempt and the assistance rather
than replacing the earlier outcome.

The [producer's recorded results][results] identify 42 software test methods
and a 16-case internal execution. Those counts do not mean the reviewer ran
the tests or a fresh suite. Record either additional activity as a separate
scope if performed. A fresh suite uses fresh keys and its bytes need not equal
this saved capture. The original 23/53-case counts remain separate.

## 4. Inspect what the results mean

Each preserved case contains `input`, `trust`, `report`, `expected` and
`differences`. Cite the case file, its hash and relevant JSON Pointer in each
finding. Useful report paths are `/report/statements`, `/report/record_checks`,
`/report/presence_reports`, `/report/follow_up_reasons` and
`/report/erasure_report/assessments`.

| Cases | Suggested interpretation question |
| --- | --- |
| RT-01–03 | Does advancing only the cutoff change the deadline state while preserving the deletion assessment and identical signed records? |
| RT-04 / RT-07 | Does an unresolved schedule remain unknown even when location or training declarations are supplied? |
| RT-05 / RT-16 | Does a claim covering only some locations leave the other locations unresolved? Does a reached-deadline review reason remain even when claims cover all stated locations? |
| RT-06 | Are the historical scoped synthetic review and later presence both preserved without automatically declaring the earlier deletion claim false? |
| RT-08–10 | Are an authentic statement for another tenant, modified signed data and a future record kept from establishing an applicable statement? |
| RT-11 / RT-12 | Do expired or unspecified exceptions and multiple statements remain visible for review? |
| RT-13 / RT-15 | Are out-of-scope and historical pre-request presence kept distinct from post-request deadline follow-up? |
| RT-14 | Do equivalent timezone-bearing instants compare equally without inferring a timezone from a date-only notice? |

The fixture observation cutoffs are chosen synthetic test instants. They are
not measurements of the reviewer's current clock or of an actual incident.
An attributed presence statement is not a direct storage observation by this
program. Later presence can reflect recreation or restoration. A reached
deadline, disabled-training declaration or missing completion response does
not establish either universal deletion or a legal violation.

## 5. Return actual observations and assess independence separately

Use a separate dated reviewer record identifying this retention scope. Include:

- The source commit, capture location, computed summary digest and trust/hash acquisition basis.
- The planned scope, actual commands, environment, restrictions and modifications.
- The actual stdout, stderr, exit statuses and retained output locations/hashes.
- Checked case files and JSON Pointers, findings, failed or unperformed steps, exclusions and unresolved questions.
- The reviewer's own conclusion, assistance received and any effect on an independence claim.
- Authorization and restrictions for publishing the specific statement or artifacts.

The [original procedure's independence factors](EXTERNAL-REVIEW.md#6-return-evidence-and-assess-independence-separately)
remain relevant: involvement in the subject, control of the environment and
conclusion, and financial/contractual relationships. Different keys, processes,
agents or CI providers do not establish independence. A blank record or missing
response supplies no reviewer conclusion or publication permission.

The saved case hashes, source manifest and public trust are included in the
capture. They support consistency checks under the supplied assumptions; they
are not an external trust anchor or immutable execution receipt. A party that
can replace the whole capture can also replace its synthetic keys and metadata.
Successful rechecking does not prove original execution time, provider key
adoption, statement truth, complete deletion, deployment readiness, conformance
or legal compliance.

This procedure does not send a review request or transmit a response. Any
actual review, return channel and publication permission must be recorded for
that activity. Use the public synthetic inputs; real personal data, credentials
and private provider material require separately authorized handling.

[source]: https://github.com/veritaschain/vap-spec/commit/62d15f1b8d3c46a1704acb7c0d5631622e1a5608
[summary]: https://github.com/veritaschain/vap-spec/blob/62d15f1b8d3c46a1704acb7c0d5631622e1a5608/experiments/incident-retention-adapter/results/local-python-3.12/summary.json
[results]: https://github.com/veritaschain/vap-spec/blob/62d15f1b8d3c46a1704acb7c0d5631622e1a5608/experiments/incident-retention-adapter/results/README.md
