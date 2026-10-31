# Synthetic evidence-design tests

Run with `python -m unittest discover -s proposals/medical-ai-evidence/tests -p 'test_*.py'`.

Nine synthetic cases exercise **illustrative application-level classifications only**. They do not implement VAP cryptographic verification, INT-008 proofs, real anchoring, medical dose validation, provider integration, or independent reproduction. `INCOMPLETE_SUBMISSION` is a simulated manifest-count discrepancy, **not** a cryptographic proof. `UNKNOWN` is not a verified denial. These tests do not create a MAP normative requirement or conformance claim.
