# Execution records

Actual controlled-loopback execution was completed on **2026-10-30, 10:24 JST
(01:24 UTC)** using synthetic payloads and fresh ephemeral keys. The records below
were retrieved from the completed [GitHub Actions run
40985604010](https://github.com/veritaschain/vap-spec/actions/runs/40985604010).
They are development-run observations, not independent reproduction or VAP/CAP
conformance results.

## Tested source and extraction

- PR head: [`c47096dc23d00baf4bb1be21b1628a7af95357fe`](https://github.com/veritaschain/vap-spec/commit/c47096dc23d00baf4bb1be21b1628a7af95357fe).
- Base: `590df2ed0257e509ca3b484660dab0eec77c83e6`.
- Actual PR checkout merge: `9cbbace88a7463ef72816a714764c01eb124611b`.
- Source manifest: 28 files; SHA-256 `0f7e7f04c45baca8bc62ea0f8778c79ef5bba22e27faf49fbad92001c617df49`.

The summary JSON is extracted directly from each completed job's
`UPLOAD_PILOT_SUMMARY_JSON=` log line and reformatted only for readability.
The recorded source-file hashes were compared with the local reviewed source
and matched. Documentation and result records are intentionally outside that
manifest; recording these retrieved results does not change the measured code.
[ci-record.json](ci-record.json) records the head, actual checkout, run, jobs,
artifact identifiers/digests and validation counts.

## Retrieved results

| Validation | Python 3.12.15 | Python 3.14.9 |
| --- | --- | --- |
| Unit and real HTTP test methods | 39 passed | 39 passed |
| Skipped test methods | 0 | 0 |
| Captured finalizer errors / unclosed database warnings in job logs | 0 | 0 |
| Measured loopback scenario expectations | 17 / 17 matched | 17 / 17 matched |
| Public case exports rechecked | 17 / 17 | 17 / 17 |
| Unchanged assessor unit tests | 20 passed | 20 passed |
| Unchanged assessor scenario expectations | 23 / 23 matched | 23 / 23 matched |
| Receiver cleanup | 17 stopped; no forced termination | 17 stopped; no forced termination |

Job logs and parsed summaries:

- Python 3.12: [job 123835777774](https://github.com/veritaschain/vap-spec/actions/runs/40985604010/job/123835777774), [summary](summary-python-3.12.json).
- Python 3.14: [job 123835778225](https://github.com/veritaschain/vap-spec/actions/runs/40985604010/job/123835778225), [summary](summary-python-3.14.json).

Both jobs set `PILOT_NETWORK_TESTS=1` and required zero skips. Real body bytes were
sent to separate receiver processes. The fault scenarios used the documented
controller modes. UL-17 actually killed its dispatch worker after committing the
intent and observed exit code -9; this expected worker kill is distinct from the
receiver cleanup counters above. Initial CI exposed four leaked test connections;
the recorded run includes the fixes and stricter finalizer-error handling described
in [the review](../REVIEW.md).

## What the observations establish

Allowed bytes matched the receiver's measured digest and length. Unapproved
destination, tenant mismatch, changed payload, expiration and pre-record failure
cases produced no gateway attempts or receiver calls. Lost responses and invalid
receipts remained unresolved. Repeated and concurrent identical requests caused
one receiver acceptance; a restarted worker with an existing intent did not resend.

The deliberate UL-14 negative control observed a successful direct controller
call to an unauthenticated receiver while the gate denied its own path. Thus
`all_route_prevention_established` remains `false`. Matching this expectation is
not a security pass. A local signed receipt also does not change the unchanged
assessor's `remote_outcome: UNKNOWN` or establish an external provider outcome.

## Full evidence, retention and reproduction

Full public case exports and synthetic runtime databases are retained in the
associated GitHub Actions artifacts for 30 days, with recorded expiry on
2026-11-29. Their archive identifiers and SHA-256 digests are in
[ci-record.json](ci-record.json):

- [Python 3.12 artifact](https://github.com/veritaschain/vap-spec/actions/runs/40985604010/artifacts/12946428867).
- [Python 3.14 artifact](https://github.com/veritaschain/vap-spec/actions/runs/40985604010/artifacts/12947190656).

The repository retains the summaries and source hashes; it does not retain the
complete case exports or runtime databases after the Actions artifacts expire.
The summaries alone are not inputs for `verify-exports`: that command needs the
complete extracted run directory. For a fresh run after expiry, follow the
[reproduction instructions](../README.md#reproduce-on-linux). New keys, IDs and
observation times are expected, so new export hashes will differ.

The editing environment forbids socket creation. Its separate local result was
35 passed methods and four explicitly skipped real-HTTP methods. That local
result is not network evidence. Offline rechecking repeats signatures, bindings,
derived assessments and inventory checks without repeating the HTTP actions or
independently establishing the original host's observations. No real patient
data, external provider processing, erasure result or legal determination is used.
