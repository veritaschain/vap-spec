# Execution records

Actual local-filesystem execution completed on **2026-10-30, 11:10 JST
(02:10 UTC)**. Results were retrieved from completed [GitHub Actions run
40990072945](https://github.com/veritaschain/vap-spec/actions/runs/40990072945).
The suite uses synthetic article data, simulated AI labels and synthetic reviewer
keys. It makes no external-publication or independent-reproduction claim.

## Source and extraction

- Tested head and actual checkout: [`2b126fc0dac76cf0c3a7e4a64b9cb0d9ab87c341`](https://github.com/veritaschain/vap-spec/commit/2b126fc0dac76cf0c3a7e4a64b9cb0d9ab87c341).
- Base: `d1f1441b39ffd18a5f2a274fc3739a4289dbedfd`.
- Source manifest: 27 files; SHA-256 `78386924abf2ac6819f653d7c282972b86e58ac1379751c213bca1e5334c639c`.

Each summary is the JSON retrieved from its completed job's
`PUBLICATION_PILOT_SUMMARY_JSON=` log marker, reformatted only for readability.
Job metadata and decoded logs independently supply the execution status and
test/recheck counts. The source manifest matches the reviewed local code.
Documentation and stored result records are excluded from that manifest, so this
result-recording commit does not alter the measured implementation.
[ci-record.json](ci-record.json) records the commits, run, jobs and artifact digests.

## Verified results

| Validation | Python 3.12.15 | Python 3.14.9 |
| --- | --- | --- |
| Test methods | 45 passed | 45 passed |
| Skipped tests | 0 | 0 |
| Captured finalizer errors in job logs | 0 | 0 |
| Actual local-filesystem scenario expectations | 18 / 18 matched | 18 / 18 matched |
| Saved case exports rechecked | 18 / 18 | 18 / 18 |
| Unchanged assessor unit tests | 20 passed | 20 passed |
| Unchanged assessor scenario expectations | 23 / 23 matched | 23 / 23 matched |

- Python 3.12: [job 123850067638](https://github.com/veritaschain/vap-spec/actions/runs/40990072945/job/123850067638), [retrieved summary](summary-python-3.12.json).
- Python 3.14: [job 123850067856](https://github.com/veritaschain/vap-spec/actions/runs/40990072945/job/123850067856), [retrieved summary](summary-python-3.14.json).

The local editing environment also ran all 45 methods without skips or captured
finalizer errors, all 18 scenarios matched, and all 18 exports passed the separate
recheck. Unlike the earlier upload experiment, this publication experiment needs
no socket capability; its SQLite, files, atomic links and readback are actual
local operations in both environments.

## Observed boundaries

The approved final HTML and disclosure were created and measured. Changed
artifacts, removed/incomplete disclosure, another venue, missing/untrusted approval,
prohibited activity and unresolved policy produced no new output. A real pause
after the durable intent let approval expire, and the final check prevented the
atomic publication call. Concurrent or repeated requests produced one visible file.

Result-persistence failure occurred after actual file creation in LP-14: the gate
retained `OUTCOME_UNKNOWN`, and replay did not create another output or promote a
receipt. Imported-only text retained `ai_involvement: UNKNOWN`. Replaced simulated
AI output remained historical activity while its exact current adoption was absent.
The core assessor continued returning qualified `REVIEW`/unknown results.

LP-16 deliberately wrote outside the gate after a denied request. Its matching
expected result demonstrates incomplete route control; it is not a security pass.
Synthetic reviewer signatures do not prove real human inspection. Local HTML and
receipts do not establish external delivery or editorial acceptance.

## Detailed evidence and retention

Actual HTML files, complete public cases and local journals are available in the
associated Actions artifacts with a 30-day retention period, recorded to expire
on **2026-11-29**:

- [Python 3.12 artifact](https://github.com/veritaschain/vap-spec/actions/runs/40990072945/artifacts/12949205621).
- [Python 3.14 artifact](https://github.com/veritaschain/vap-spec/actions/runs/40990072945/artifacts/12949051379).

The original result directory retains summaries, provenance metadata and source
hashes. On 2026-10-30 JST, the [offline recheck kit](../../incident-recheck-kit/README.md)
additionally preserved the exact original Python 3.12 summary and all 18 public
case exports in Git, after checking the downloaded artifact's recorded digest.
These include the synthetic article content needed for verification and remain
available after artifact expiry. Separate runtime HTML/journals and Python 3.14
case exports are not copied by the kit. A summary alone cannot replace the full
public case directory for `verify-exports`. A fresh execution uses the
[reproduction instructions](../README.md#reproduce);
fresh keys, IDs and times legitimately produce different evidence hashes.

Offline rechecking verifies supplied signatures, decisions, bindings, observations
and inventory. It does not repeat publication, inspect current files or independently
establish the truth of the original host's observations. Public cases contain only
synthetic article plaintext and public evidence; private signing keys are excluded.
