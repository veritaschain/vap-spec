# Internal synthetic execution record — 2026-10-24 JST

Tested code and fixture generator: [`3ecbaa226b2b371e86a1616c0444a424c9a7d5eb`](https://github.com/veritaschain/vap-spec/commit/3ecbaa226b2b371e86a1616c0444a424c9a7d5eb).
The worktree was clean during execution. Python 3.14.3, macOS arm64; exact dependencies and content digests
are in [summary.json](summary.json). This subsequent documentation commit records that run without changing
the tested implementation.

**14/14 scenario expectations matched in both modes. 49/49 additional regression tests passed.**
This is internal synthetic execution, not independent reproduction, specification adoption or full conformance.

| Case | Experimental integrity | Experimental scope | Current INT-008 |
| --- | --- | --- | --- |
| 01 Complete 1,000 records | verified | met | verified |
| 02 Remove 100 after original commitment | verified | not_met | failed |
| 03 Alter supplied payload | failed | indeterminate | indeterminate |
| 04 Duplicate records replace required IDs | verified | not_met | failed |
| 05 Inventory and source closure unavailable | verified | indeterminate | verified |
| 06 Missing notification receipt, unclosed source | verified | indeterminate | failed |
| 07 Full receipt explicitly withheld | verified | not_met | failed |
| 08 Full record unavailable | verified | not_met | failed |
| 09 Permitted hidden-content commitment | verified | met, narrow obligation | failed |
| 10 Producer/execution disagreement | verified | not_met | verified |
| 11 Missing external scope timing proof | indeterminate | indeterminate | verified |
| 12 Closed register proves late first acceptance | verified | not_met | verified |
| 13 Observation gap | verified | indeterminate | verified |
| 14 Substitute another exercise's scope | failed | indeterminate | verified |

The current-requirement mode has no scope output. Its supplied-object integrity is verified in all cases
except 03, which fails. Its remaining implemented requirement checks and explicit unsupported checks are
recorded separately. Neither mode emits an overall PASS. Negative expected outcomes above are intentional.

- [Execution archive](synthetic-evidence-and-reports.tar.gz): 59 files — 14 evidence packages, 14 evaluator
  trust files, input digest manifest, 28 detailed reports, execution summary and regression log.
- [Expected/actual comparison](summary.json), [fixture digests](fixture-manifest.json),
  [regression execution log](regression-tests.txt), [file checksums](SHA256SUMS).
- [Reproduction commands and implementation limits](../README.md), [日本語実行ガイド](../RUN-ja.md).

All signing keys are public synthetic test material. All sources, receipts and register closure assertions
are controlled by the fixture generator. The numerical evaluation time is a fixed fictional test instant.
External independent time attestation, source completeness outside the synthetic boundary, and independent
third-party reproduction have **not** been established.
