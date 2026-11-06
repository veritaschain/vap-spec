# Integrity test limitations

This suite is an illustrative **SHA-256 Merkle commitment experiment** only.
For the small JSON fixtures, it computes:

- An event digest over Python `json.dumps(sort_keys=True, separators=(",", ":"))` bytes.
- A leaf as `SHA256(0x00 || event_digest)`, with a single-byte prefix.
- A parent as `SHA256(0x01 || left || right)`, with a single-byte prefix.
- An unmatched node is carried to the next level; empty input is rejected.

The fixed 1-, 2-, 3- and 5-leaf values were calculated separately using recursive
largest-power-of-two splits over literal ASCII JSON fixtures. They pin this
custom demonstration's byte convention and catch the former literal-backslash
prefix mistake. They are internal vectors, not independent validation or VAP
conformance vectors. Python JSON serialization here is not asserted to implement
RFC 8785 or the complete canonicalization rules of a VAP profile.

Mutation, omission and reordering tests compare local commitments. A finite
negative control creates two distinct full histories, one containing an
out-of-scope event, which produce the same collected commitment. It demonstrates
an observation boundary; it does not establish what any real collector missed.

This suite does not implement or assert conformance with VAP INT-008, RFC 9162,
SCITT receipts, signed statements or independently witnessed external anchoring.
No cryptographic keys, anchor services, patient data, medical model or provider
integration are used. A successful test is not evidence of independent
reproduction or MAP readiness. INT-008 evaluation still requires a verifier of
the exact normative specification, its canonicalization and declared scope,
applicable authenticated manifests and external-anchor evidence, and adversarial
vectors for the required proof and completeness checks.

