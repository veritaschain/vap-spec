# Offline kit execution records

The completed [implementation push run 41000265431](https://github.com/veritaschain/vap-spec/actions/runs/41000265431)
passed on **2026-10-30, 12:58 JST** using Python **3.12.15** and **3.14.9**.
Both jobs ran the exact commit
[`1205280216ba2463addc03b7c2bd55116475153a`](https://github.com/veritaschain/vap-spec/commit/1205280216ba2463addc03b7c2bd55116475153a).
Their downloaded artifacts contain byte-identical offline kit ZIPs, matching
the locally constructed ZIP. This is a recheck of saved synthetic evidence;
independent reproduction and VAP conformance remain unestablished.

## Executed checks

| Check | Python 3.12.15 | Python 3.14.9 |
|---|---:|---:|
| Test methods | 29/29 | 29/29 |
| Failures, errors, skips, unraisable finalizer exceptions | 0 | 0 |
| Original upload exports rechecked | 17/17 | 17/17 |
| Original publication exports rechecked | 18/18 | 18/18 |
| Original erasure exports rechecked | 18/18 | 18/18 |
| Identical repeated archive bytes | Yes | Yes |
| Standalone recheck and identical rebuild | Yes | Yes |
| Execution sources unchanged during tests/build/recheck | Yes | Yes |
| Downloaded artifact digest and inner kit digest matched | Yes | Yes |
| Downloaded summary matched completed job log | Yes | Yes |

The 29 methods comprise 10 archive, nine runner, six separately authored boundary
and four CLI/standalone/parser methods. They include source/worker/provenance
substitution, original raw-byte changes, hostile `PYTHONPATH`, action-denial
attempts, archive path/structure attacks, child output/time limits and cleanup.
The standalone test refuses access to the original checkout while the verified
delivered source/evidence topology rechecks all 53 cases and rebuilds identical
bytes. It does not rerun the original pilot operations.

- Python 3.12: [job 123882786419](https://github.com/veritaschain/vap-spec/actions/runs/41000265431/job/123882786419), [recorded summary](summary-python-3.12.json).
- Python 3.14: [job 123882786160](https://github.com/veritaschain/vap-spec/actions/runs/41000265431/job/123882786160), [recorded summary](summary-python-3.14.json).
- [Machine-readable CI record](ci-record.json) includes exact commits, run/jobs, artifact metadata, downloaded-byte checks and scope limits.

## Expected inner kit identity

The archive is **2,902,071 bytes** and contains 129 payload files plus one
manifest. Its SHA-256 is:

```text
06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f
```

The payload contains 72 source/license/instruction files and 57 evidence files:
53 original cases, three original summaries and one capture provenance record.
The 72 source files include 61 distinct original pilot/assessor inputs. The
manifest SHA-256 is:

```text
808cac08a06e2f543683e4499645d1eda3860a400406efe1cbd206614490a76d
```

This expected archive hash must be obtained from a reviewed result outside the
candidate archive. To recheck, use the [Japanese instructions](../RUN-ja.md) or
the [README](../README.md#recheck-from-a-trusted-checkout). The archive's own
manifest and included checksum do not authenticate themselves.

## Download and retention

| Python job | GitHub artifact | Expected expiry |
|---|---|---|
| 3.12 | [incident-recheck-python-3.12](https://github.com/veritaschain/vap-spec/actions/runs/41000265431/artifacts/12952509821) | 2026-11-29 12:58:39 JST |
| 3.14 | [incident-recheck-python-3.14](https://github.com/veritaschain/vap-spec/actions/runs/41000265431/artifacts/12952753979) | 2026-11-29 12:58:41 JST |

GitHub downloads an **outer artifact ZIP** containing `incident-ci-2026-10-30.zip`,
`SHA256SUMS` and `summary.json`. The expected inner-kit hash above applies to
`incident-ci-2026-10-30.zip`, not the outer download. The outer ZIP hashes and
lengths are recorded separately in `ci-record.json`. Both outer downloads were
retrieved and checked; each contained exactly those three files. Their inner
kit bytes matched the expected hash/length and their summary JSON matched the
completed job's summary marker. Outer hashes legitimately differ because the
job summaries contain different Python versions and execution times.

Original public pilot evidence is now retained in
[the fixed capture](../snapshots/2026-10-30-ci/provenance.json), independent of
the expiration of these Actions artifacts. A matching reviewed checkout can
regenerate the same inner ZIP. This preservation does not include original
runtime databases or the original Python 3.14 case directories. Publication case
JSON includes synthetic article plaintext and HTML needed for verification.

## Source identity and correction history

The completed CI jobs recorded the same **136-file execution source manifest**:

```text
8fb9b95553ef60b54419f0542b555e7c797c58cc92d1bba2a7a0c256694bd3c0
```

Each source-file hash was compared with the reviewed local bytes. The summary
records were retrieved from `INCIDENT_RECHECK_SUMMARY_JSON=` in completed job
logs and matched the downloaded summaries; only the stored JSON whitespace is
reformatted. Result JSON/Markdown and the review document are outside the archive
payload and execution manifest. Recording the observed result therefore changes
neither the measured execution sources nor the ZIP whose hash is recorded here.
The result-recording commit follows the tested implementation commit above.

Local Python 3.12.14 previously passed the same 29 methods and 53 rechecks with
an identical kit ZIP. The first GitHub workflow submission then failed YAML
parsing before any jobs ran: the inline dependency command contained a `: `
sequence. The command was changed to a literal block, parsed locally, and both
CI jobs completed successfully at the tested commit above. The workflow correction
changed the execution-source hash from the earlier local checkpoint but did not
change any archive member. The initial failed run and correction are retained
in `ci-record.json`; no pre-execution failure is counted as a passed CI run.

## Evidence boundary

The kit validates captured signatures, bindings, decisions, source identity and
inventory. It neither repeats upload/publication/erasure nor independently
observes their original effects. Original unknown outcomes and negative controls
remain in the records. Recheck success does not establish complete route control,
all AI involvement, universal deletion, disclosure-policy compliance or truthful
original observations. Separate keys and same-controller CI are not independent
witnesses.

Workers use a Python audit guard, not OS isolation. The interpreter, host and
installed binary dependencies remain trusted external inputs; exact dependency
versions are checked but not hermetically captured. Reports retain
`actions_reexecuted: false`, `independent_reproduction: NOT_ESTABLISHED`,
`conformance: NOT_ASSESSED` and `dependency_scope: PINNED_VERSIONS_NOT_HERMETIC`.
The fixed October 24 distribution and normative VAP v1.2 Draft 3 are unchanged.
