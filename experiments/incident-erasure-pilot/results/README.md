# Recorded execution evidence

The local erasure pilot executes real synthetic file creation, namespace unlink,
directory synchronization, SQLite transactions and bounded readback. It uses no
real provider or personal data. Public case exports retain original signed
evidence and public pins, with no private keys or object plaintext.

## Executed checkpoint — 2026-10-30 JST

[Implementation push run 40997508247](https://github.com/veritaschain/vap-spec/actions/runs/40997508247)
completed successfully on Python **3.12.15** and **3.14.9** at exact commit
[`ff54a5d302bc014df57736e6bcd5b0e44acc01b7`](https://github.com/veritaschain/vap-spec/commit/ff54a5d302bc014df57736e6bcd5b0e44acc01b7).
Both job logs identify that checkout, report 54 test methods without skips or
resource/finalizer errors, and contain the full scenario summary marker. Their
capture is recorded in [ci-record.json](ci-record.json).

| Measured check | Python 3.12.15 | Python 3.14.9 |
|---|---:|---:|
| Pilot test methods | 54/54 | 54/54 |
| Skipped methods | 0 | 0 |
| Actual local filesystem scenarios | 18/18 | 18/18 |
| Offline export rechecks | 18/18 | 18/18 |
| Unchanged assessor test methods | 20/20 | 20/20 |
| Unchanged assessor catalogue cases | 23/23 | 23/23 |

The original per-job summaries are retained as
[summary-python-3.12.json](summary-python-3.12.json) and
[summary-python-3.14.json](summary-python-3.14.json). They were extracted from
`ERASURE_PILOT_SUMMARY_JSON=` in the successful logs; only JSON whitespace was
reformatted. Both contain the same 28-file executable source manifest:

```text
fb0dc41bde92840e06f11c9077c41743dc8c1255b4404aaa464b7455fa829191
```

The results/documentation commit follows that tested implementation commit.
Source manifests include executable/test/acceptance/workflow inputs and the
imported core assessor; they intentionally exclude explanatory Markdown and
recorded result JSON. This avoids self-reference without claiming that the
result-recording commit itself produced the earlier run.

## Full public evidence artifacts

| Runtime | Artifact | Expected expiration |
|---|---|---|
| Python 3.12 | [incident-erasure-python-3.12](https://github.com/veritaschain/vap-spec/actions/runs/40997508247/artifacts/12952440268) | 2026-11-29 12:28:06 JST |
| Python 3.14 | [incident-erasure-python-3.14](https://github.com/veritaschain/vap-spec/actions/runs/40997508247/artifacts/12952355747) | 2026-11-29 12:28:08 JST |

Artifact IDs, ZIP SHA-256 digests, sizes and expiration timestamps are retained
in `ci-record.json`. The full artifacts contain the summary and signed case
exports. To recheck, use the matching source commit and run
`python -m erasure_pilot verify-exports EXTRACTED_DIRECTORY` from this experiment
directory, with `EXTRACTED_DIRECTORY` pointing to the extracted summary and
`cases/`. This performs no deletion.

The original Actions artifacts have 30-day retention. On 2026-10-30 JST, the
[offline recheck kit](../../incident-recheck-kit/README.md) additionally preserved
the exact original Python 3.12 summary and all 18 public case exports in Git after
checking the downloaded artifact's recorded digest. They remain recheckable after
artifact expiry. The kit does not copy the Python 3.14 case directory. This result
directory still contains summaries and CI identifiers; those summaries alone
cannot reconstruct original signed case evidence or satisfy `verify-exports`.

Rechecking requires the matching tested source manifest. It validates captured
statements under the recorded controller pins and does not perform new deletion,
prove honest execution, establish independent verification or assert universal
erasure. The runtime directory and SQLite files are not uploaded.
