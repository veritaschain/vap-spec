# Internal package validation — 2026-10-24

**Internal CI execution and artifact review, not independent third-party reproduction.**
The extension remains unadopted. Current v1.2, the existing verifier, pre-record
gate and OS lab are unchanged. No full VAP conformity or production claim is made.

- Package implementation tested: `1d9b5c98e8814ddd5a3a3b70694bef531cd348a2`.
- Frozen subject: `c8ccf972196a16d11429a478f4918a08fe27bb73` (merged PR #12).
- Successful run: [GitHub Actions 40058921954](https://github.com/veritaschain/vap-spec/actions/runs/40058921954).
- Artifact name: `reproduction-kit-and-internal-validation` (30-day retention).
- Inner `distribution/kit.zip` SHA-256:
  `f722c310df75e7a767bceba0df99eb469a74144c46675ba567e1906f3b46214d`.
  This is the kit ZIP hash, not the outer GitHub artifact archive hash.
- Earlier successful packaging run: [40058817040](https://github.com/veritaschain/vap-spec/actions/runs/40058817040)
  on `f0bcf95d4baf56eeb494b1e826646f807706323f` (before three additional saved-output regression tests).

The workflow checked out the package and subject separately, verified 71 source
hashes before dependency installation, built a ZIP, extracted it, verified its
checksums, and ran the extracted kit. It did not use previously recorded outputs
as the new run's inputs. The run completed from 03:35:29 to 03:37:28 UTC; the
subsequent saved-artifact check also succeeded.

| Check | Actual result |
| --- | --- |
| Package regression tests, Python 3.12 | 21 passed |
| Original OS lab regressions | 28 passed |
| Original gate regressions | 46 passed |
| Original verifier regressions | 64 passed |
| OS observations | 16/16 expected results matched, including bypass-negative control |
| Gate scenarios / signed bundles | 15/15 matched; 11 bundles reverified |
| Verifier fixtures | 14/14 matched; both modes reverified |
| Source before/after | Same pinned commit and 71 file hashes |
| Cleanup | Original lab recorded successful resource cleanup and temporary image absence |

Actual environment: Ubuntu 24.04 GitHub-hosted runner, x86_64, Python 3.12.15,
Docker 28.0.4, Compose 2.38.2, Linux 6.17.0-1022-azure. All four recorded reference
version comparisons matched. Exact dependency versions and environment fields
are in `preflight.json`.

Additional local checks used macOS/Python 3.14: 21 package tests from the extracted
ZIP, successful offline recheck of the downloaded Linux evidence, and rejection
of a separate copy with a single modified event-signature byte
(`tampered-signature-check.txt`). No local OS-isolation execution is claimed.

`run-report.json`, `preflight.json`, and `SHA256SUMS.json` are unmodified copies
from that CI output. The checksum manifest refers to the **complete original
output directory**, not this compact record. Full logs, fixtures and evidence are
in the CI artifact during its retention window; download them if long-term
retention is required. This compact record alone is not enough for `check`.
The kit can also be regenerated from the tested package commit after expiry.

The original synthetic suites intentionally retain their internal/simulated
labels. A later external evaluator records their own execution and provenance in
a separate report; these results cannot be relabeled as that person's run.
