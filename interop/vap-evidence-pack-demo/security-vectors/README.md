# Ed25519 input-policy regression — 11 November 2026

This is a **first-party synthetic security regression**, separate from the
unchanged original `test-vectors/` dataset. It is not evidence from a real
incident, an independent implementation, or VAP conformance.

## What the fixed pair represents

`invalid-small-order-pack.json` starts from the original `valid-pack.json` and
changes the first event's `model_id` to `forged-model-without-private-key`.
Its event hashes, signed-event Merkle root, and three receipt bindings have
been recomputed. Every signature has `S = 0`; R is a small-order point.

`invalid-small-order-trust.json` preserves the selected scope commitment and
the three distinct role identifiers, but replaces their keys with three
distinct small-order points:

| Role | Encoded point | Order |
| --- | --- | --- |
| producer | `01` followed by 31 zero bytes | 1 (identity) |
| observer | `ec`, 30 bytes `ff`, then `7f` | 2 |
| anchor | 32 zero bytes | 4 |

No private key was used to create these signatures. Candidate small-order R
values and receipt timestamps were selected until the original backend's
verification equation accepted them. This is possible because those role keys
have small order; their distinct byte strings do not make them valid role keys.
The accompanying manifest pins the two fixture byte strings and expected result.

**Required precondition:** the verifier's caller accepts the substituted trust
file. Replacing only the pack while retaining the original trusted role keys
does not succeed. Point screening cannot establish who supplied a trust file,
and accepting an attacker's ordinary keys still allows attacker-signed data.

## Observed original behavior

The original verifiers were extracted without alteration from
[`1ce71a66f55d9a20728213b7c3a8bb79270ae579`](https://github.com/veritaschain/vap-spec/tree/1ce71a66f55d9a20728213b7c3a8bb79270ae579/interop/vap-evidence-pack-demo).
They were run locally on the fixed pair above on 11 November 2026:

| Implementation / runtime | Result | Exit |
| --- | --- | --- |
| Original Python, Python 3.12.14 / cryptography 50.0.2 | PASS, all seven checks | 0 |
| Original Node, Node 22.23.4 | PASS, all seven checks | 0 |
| Original Node, Node 24.22.1 | FAIL: event signature does not match the supplied role key | 1 |

The Python dependency matches the repository pin. The Node 24 observation
shows why a backend upgrade alone is not a cross-runtime contract. The new
prechecks reject the trust key before invoking the signature backend.

## Required repaired behavior

From the demo directory, run:

```sh
python verify_python.py security-vectors/invalid-small-order-pack.json --trust security-vectors/invalid-small-order-trust.json --json
node verify_node.mjs security-vectors/invalid-small-order-pack.json --trust security-vectors/invalid-small-order-trust.json --json
```

Both must exit 1 with:

```json
{"contract_id":"vap-interop-demo/0.2.0","verdict":"FAIL","checks":[],"error":"trust.roles.producer.public_key is a small-order Ed25519 point"}
```

The normal reproduction command also runs `tests/test_ed25519_policy.py`.
It checks all eight distinct torsion points in every trust role and in event
and receipt R values, all 19 representable noncanonical y values with both
signs, the two invalid x-zero sign aliases, and scalar boundaries. An
independent test-only decoding/doubling calculation verifies the eight-point
table. Original positive vectors must continue to pass; malformed input and
operational failure are never treated as a successful regression result.

See [CONFORMANCE §1.1](../CONFORMANCE.md#11-ed25519-input-policy-11-november-2026-hardening)
for the local rule and [RFC 8032](https://www.rfc-editor.org/rfc/rfc8032.html#section-5.1.7)
for the underlying algorithm. Small-order rejection is an extra demo policy;
it is not asserted to be an existing normative VAP rule. Historical execution
records and fixed releases are not rewritten by this change.
