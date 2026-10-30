# Recorded local execution

The preserved [summary](local-python-3.12/summary.json) and
[16 case captures](local-python-3.12/cases/) were generated with Python 3.12.14
at `2026-10-30T19:38:08.739884+00:00` (2026-10-31 JST). The saved capture was
then re-evaluated successfully without generating replacement inputs or keys.
These are internal synthetic results from this development environment, not
GitHub Actions artifacts or an independent provider/storage observation.

| Check | Measured result |
| --- | --- |
| New adapter, export and CLI regression tests | 42 test methods, zero failures, zero skips |
| New retention scenarios | 16/16 expected observations matched |
| Re-evaluation of the preserved signed captures | 16 rechecked; source manifest matched |
| Three cutoff-only scenarios | Same signed records; unchanged deletion assessment |
| Unchanged original assessor regression tests | 20 test methods, zero failures, zero skips |
| Original assessor scenario suite | 23/23 expected observations matched |

These counts describe different checks; they are not a combined conformance
score. The original 23-case catalogue and fixed 53-case capture are unchanged.
The fixture `as_of` values are chosen test instants, not observations of the live
clock or of a real incident.

## What the new scenarios exercised

| Cases | Observation tested |
| --- | --- |
| RT-01–03 | Moving only the pinned cutoff before, to and after a deadline changes the deadline state, never the deletion assessment |
| RT-04, RT-07 | An unknown starting event or missing schedule remains unknown; processing-region and training declarations do not fill the gap |
| RT-05, RT-16 | Completion-claim coverage is matched by request and location; full claim coverage still leaves a reached-deadline review reason |
| RT-06, RT-13, RT-15 | Later scoped presence is visible alongside historical review; out-of-scope or pre-request presence does not become a post-request deadline finding |
| RT-08–10 | Another tenant's signed statement, a modified signed body and a future record cannot establish an applicable statement |
| RT-11–12 | Exceptions and multiple statements remain visible instead of being silently discharged or replaced |
| RT-14 | Equivalent timezone-bearing instants compare equally |

The actual report, public input, separate synthetic trust and expected
observations are retained in every case file. Scenario expectations are not
runtime inputs to the adapter.

## Recheck the saved evidence

Use the complete matching repository checkout and dependencies from the
[experiment README](../README.md). From the experiment directory:

```sh
python suite.py verify results/local-python-3.12
```

The verifier checks the exact inventory, case hashes, source manifest, original
signatures, complete report equality and finite scenario expectations. Its
source manifest covers 22 files, including the new tests and contract plus the
unchanged original assessor's Python sources and requirements. A historical
capture must be checked against its matching source revision.

The saved summary's SHA-256 is:

```text
96b7ad9c574a3777fc9366dc9e5b3cf763cfce099e4e1b0771e203788774873f
```

This digest is a byte identity, not an external timestamp or trust anchor.
Obtain the repository revision or expected digest through a trusted channel
when origin matters. A party able to replace the entire capture can replace
its synthetic keys and metadata too. Successful rechecking establishes the
input/result relationship under the supplied assumptions, not who executed the
original run, when it occurred or whether a real provider adopted those keys.

Fresh suite runs use fresh in-memory signing keys, so their bytes need not match
this capture. The [dedicated workflow](../../../.github/workflows/incident-retention-adapter.yml)
generates and verifies its own captures on Python 3.12 and 3.14 and retains those
artifacts for 30 days. Consult the actual workflow run before asserting a CI
result. This preserved local capture remains available after that artifact
retention period.

No result establishes complete deletion, legal compliance, normative VAP/CAP
conformance, production integration or independent reproduction.
