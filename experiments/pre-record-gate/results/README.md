# Recorded internal execution

Implementation and test source commit: `56a98eec87339193831f4c78607de5b259745edc`.
The suite ran with a clean experiment working tree on Python 3.14.3/macOS arm64.
`summary.json` records source digests, dependency versions and platform.

- 15/15 gate scenarios matched their independently stored expectations.
- 31 gate regression tests passed (`regression-tests.txt`).
- 11 exported evidence bundles rechecked offline, including authorization bindings, native backend receipts
  and both modes of the unchanged verifier.
- Existing PR #10 baseline: 64 regression tests passed and 14/14 synthetic cases matched;
  see `existing-verifier-tests.txt` and `existing-verifier-summary.json`.
- Ten normal local operations: median gate entry to backend send **39.78 ms**; median full duration **92.37 ms**.
  Startup is excluded. These measurements are single-host observations, not a production SLA.

`mock-evidence-and-reports.tar.gz` contains 15 scenario artifacts, summary and latency samples.
Each scenario artifact carries the gate result and, where applicable, actual signed audit events,
public mock trust, evidence packages and verifier reports. It contains no test private keys.
The corresponding scenario's `artifact_digest` in the summary binds the complete artifact.
`SHA256SUMS` covers the archive and copied reports/logs.

To recheck the archived public evidence from the experiment directory after installing dependencies:

```sh
mkdir -p generated/recorded
# The archive contains only the recorded JSON files, with relative filenames.
tar -xzf results/mock-evidence-and-reports.tar.gz -C generated/recorded
.venv/bin/python -m record_gate verify-exports --output generated/recorded
```

This verifies the recorded bytes with bundled **synthetic trust**. It is not a gate rerun or independent
reproduction. For a fresh process/fault exercise use `python -m record_gate run-suite` instead.
All scope and anchor receipts are simulated and controlled by the test operator. The deliberately
insecure backend scenario matched by exposing a successful bypass, so its guarantee is **not established**.
Same-UID host isolation, real network egress enforcement, production readiness and formal adoption remain unestablished.
