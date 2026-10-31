# Integrity test limitations

This suite is an illustrative **SHA-256 Merkle commitment experiment** only. It does not implement or assert conformance with VAP INT-008, RFC 9162, SCITT receipts, signed statements, or independently witnessed external anchoring. The tree construction (including odd-leaf handling) is demonstration-only. It checks that mutations, omissions and reordering alter a locally computed commitment, not that real-world capture is complete.

No cryptographic keys, anchor services, patient data, medical model or provider integration are used. A successful test is **not** evidence of independent reproduction or MAP readiness. To claim INT-008 validation, supply official canonicalization, domain separation, inclusion/consistency verification, declared-scope manifests, independent anchor receipts and adversarial test vectors against the exact normative specification.
