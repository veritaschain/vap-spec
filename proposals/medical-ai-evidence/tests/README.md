# Synthetic evidence-design tests

Run from the repository root with:

```sh
python -m unittest discover -s proposals/medical-ai-evidence/tests -p 'test_*.py' -v
```

## Classifier boundary

The nine synthetic catalogue cases exercise **illustrative application-level
classifications only**. The separate [classifier](../synthetic_assessment.py)
accepts only the evidence object and returns all supported dimensions. Fixture
IDs and expected labels do not select its execution path.

Missing, malformed or unsupported observations remain `UNKNOWN`; they never
become a passed check through a default value. Explicitly reported check results
remain declarations. A declared full collection scope is `DECLARED_FULL`, not
proof of global completeness. Patient-field checks concern declared presence
only, not clinical necessity, valid values or sufficient clinical context.

`INCOMPLETE_SUBMISSION`, `COUNTS_MATCH` and `COUNT_CONFLICT` are comparisons
of fixture counts under a declared `manifest_bound` flag. The flag is not
cryptographically authenticated. Digest comparisons require two syntactically
complete SHA-256 strings; neither their syntax nor equality authenticates the
underlying observations. A declared translation parent is not a verified lineage.
`UNKNOWN` is not a verified denial.

## Local commitment demonstration

The separate integrity tests exercise a bounded custom SHA-256 construction,
including fixed small-tree vectors, mutation, omission, reordering and empty
input. A negative control uses two different full histories that project to the
same collected events, showing why that local commitment cannot reveal the
unobserved event. See [the exact construction and limits](INTEGRITY-LIMITATIONS.md).

## Recorded local execution — 2026-11-01 JST

The command above completed with **18 test methods, zero failures and zero
skips** with Python 3.12.14 in the development environment. One method checks the nine catalogue
fixtures as subtests; these counts are not additive acceptance or conformance
scores. This is a local internal test result, not a claim that a later CI run or
an independent review has completed.

One [GitHub Actions workflow](../../../.github/workflows/medical-ai-evidence.yml)
runs the same suite. Consult its actual run and tested commit before asserting a
CI result. The former duplicate workflow has been removed.

The checks do not implement VAP cryptographic verification, INT-008 proofs,
external anchoring, medical dose validation, provider integration or independent
reproduction. They create no MAP normative requirement or conformance claim.
