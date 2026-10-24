# PR #13 final review — 2026-10-24

Disposition: the two reproduced review findings below are fixed. No remaining
blocker was found for merging this **reproduction package**. This review and CI
are internal. **Independent third-party reproduction has not been established.**
Merging the package does not adopt the experimental extension or approve it for
production or full VAP conformance.

## Review boundary

The initial reviewed head was `b3b279091bcd3fc6275406a74582c4b97ed05e9f`.
The corrected package implementation is
`3c1cad051291dd2308d85419bd2d593c6ae1906f`.
The subject being reproduced remains frozen at
`c8ccf972196a16d11429a478f4918a08fe27bb73`.

The PR adds only this package and `.github/workflows/reproduction-kit.yml`.
VAP v1.2, DOC-SYNC, K3, the existing verifier, existing pre-record gate and existing
OS-isolation experiment — including their tests and acceptance expectations —
have no changes. No formal proposal number, adoption or version is assigned.
The package delegates cryptographic verification to those unchanged implementations.

## Findings and repairs

1. **A matching unittest count did not prove the tests passed.** A real child
   process with one `unittest.skip` test returned zero, printed `Ran 1 test` and
   was incorrectly accepted by the old `step` function. Unittest's count also
   includes expected failures. Both execution and saved-log rechecks now require
   the expected count and one plain `OK` conclusion. Skips, expected failures,
   missing/ambiguous conclusions and unsuccessful process exits are rejected.
   Regression tests run real skipped/expected-failure child suites and also test
   a rehashed saved log with 28 skipped tests.

2. **Runtime provenance was not reconciled with preflight.** Changing only the
   stored gate dependency version to `0.0.0` in a separate copy of genuine CI
   output still passed the old artifact checker. The checker now rejects that
   copy with `recorded_dependencies_changed`. Recorded dependencies must match
   the lock; recorded Python must satisfy the supported version; reference
   comparison flags are recomputed. Gate, verifier summary and every verifier
   report must agree with preflight on Python and dependencies. The OS lab's
   controller Python is checked too. This checks record consistency, not the
   authenticity of the host or operator.

The report explicitly retains `independent_reproduction: not_established`, in
addition to `independence: not_assessed`, `proposal_status: experimental_unadopted`
and `overall_vap_pass: null`. A saved report claiming independence is rejected.

## Validation evidence

[Corrected implementation CI 40059420561](https://github.com/veritaschain/vap-spec/actions/runs/40059420561)
succeeded. It independently checked out the **source directories** for package
and frozen subject, then built, extracted, checksum-checked and executed the ZIP.
Separate directories here do not imply an independent evaluator.

- Package tests: **27 passed** on Python 3.12; also passed locally on Python 3.14.
- Unchanged regressions: **28 OS + 46 gate + 64 verifier = 138 passed**.
- Scenarios: **16 OS, 15 gate, 14 verifier cases matched**.
- Evidence: **11 gate bundles** and the OS evidence were reverified; all 14
  verifier fixtures were recomputed in both modes.
- Actual environment: Linux 6.17.0-1022-azure, x86_64, Python 3.12.15,
  Docker 28.0.4 and Compose 2.38.2, with the four exact locked dependencies.
- Source identity, output inventory and cleanup checks passed. The downloaded
  corrected-run artifacts also passed a local offline recheck, without claiming
  a local OS run.

The tested inner `kit.zip` SHA-256 is
`9e7efa74372ec08434f2d70b2a23a41a416fb64dfa99a24c13bbca255d1c0bb9`.
The [final-review evidence directory](validation/final-review-2026-10-24/) contains
unmodified copies of the run report, preflight and complete-output checksum
manifest, plus the package-test log excerpt. The manifest describes the full CI
output, not that compact directory. Full artifacts have 30-day CI retention.
The earlier `validation/internal-2026-10-24/` record remains historical evidence
for the earlier package revision; it has not been relabeled as this run.

## Limits retained

This is a synthetic research experiment with a trusted operator, host, Docker
daemon and controller. Checksums do not authenticate the evaluator. Mock signatures
and receipts do not establish independent time attestation. Saved-file rechecking
is not a new OS execution. Negative controls intentionally demonstrate successful
bypass when a route and unauthenticated API are provided. Host/kernel resistance,
production isolation, hermetic builds and full VAP conformance remain unestablished.
A third party must perform and document their own new execution before independent
reproduction can be assessed; this merge does not supply that evidence.
