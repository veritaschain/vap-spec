# VAP Evidence Pack Interoperability Conformance v0.1

## Status

Experimental interoperability contract for public implementation testing. It
is not a VAP certification scheme.

## Required results

An implementation claiming compatibility with this demo MUST produce the
following results without modifying the committed vectors.

| Vector | Required result | Minimum detected condition |
|---|---|---|
| `valid-pack.json` | PASS | All checks succeed |
| `invalid-tampered-event.json` | FAIL | Event signature, payload hash, or Merkle integrity failure |
| `invalid-omitted-outcome.json` | FAIL | Completeness Invariant failure |
| `invalid-split-view.json` | FAIL | Cross-party Merkle-root disagreement |

## Mandatory verification checks

1. Reject unsupported data types under the demo canonicalization profile.
2. Verify every Ed25519 event signature using the referenced public key.
3. Recompute and compare every event `payload_hash`.
4. Reject duplicate event identifiers.
5. Require contiguous `sequence_no` values beginning at 1.
6. Recompute the domain-separated Merkle root over signed events in sequence
   order.
7. Recompute the scope commitment.
8. Verify producer-manifest, observer-receipt, and external-receipt signatures.
9. Require all three records to bind the same Merkle root and scope commitment.
10. Require signed event counts to equal the submitted event count.
11. Enforce `ATTEMPT_OUTCOME_BIJECTION`:
    - each attempt identifier occurs exactly once in an attempt event;
    - each attempt identifier occurs exactly once in an outcome event;
    - both identifier sets are identical;
    - the number of attempts equals `scope.expected_attempt_count`.

## Independence requirements

A submission is considered an **organizationally independent implementation**
only when all of the following are true:

- repository owner is not VSO, VeritasChain Co., Ltd., or a person acting under
  their development control;
- implementation does not import, translate mechanically, or copy logic from
  `verify_python.py` or `verify_node.mjs`;
- implementation authors document their canonicalization, Merkle, signature,
  and completeness algorithms;
- source is publicly reviewable under an OSI-approved license;
- test transcript includes toolchain versions and the exact Git commit;
- failures or specification ambiguities are reported publicly.

## Submission record

Independent implementers should publish:

```yaml
implementation_name: example-vap-verifier
repository: https://github.com/example/example-vap-verifier
commit: <40-character SHA>
language: Rust 1.xx
platform: Linux x86_64
vectors_commit: <vap-spec commit SHA>
results:
  valid-pack.json: PASS
  invalid-tampered-event.json: FAIL
  invalid-omitted-outcome.json: FAIL
  invalid-split-view.json: FAIL
code_reuse_from_vso_reference: false
```

A successful submission establishes interoperability evidence, not VAP
certification or VSO endorsement.
