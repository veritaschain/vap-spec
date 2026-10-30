# Experimental demo contract 0.2.0

**Contract ID:** `vap-interop-demo/0.2.0`  
**Status:** A local compatibility contract for synthetic interoperability tests.

The requirements in this file govern only this package. They do not amend VAP,
register a profile, define a common VAP Evidence Pack format, or create a
certification scheme. Compatibility must name this contract and the exact
committed dataset used.

## 1. Inputs and canonical bytes

Each pack and trust file must be valid UTF-8 JSON, no larger than 2 MiB.
The parser rejects a BOM, duplicate object keys, invalid UTF-8, non-finite
numbers, and nesting deeper than 16. The top-level value must have the exact
object shape specified below. Missing and additional members are rejected.

The canonicalization identifier is `DEMO-ASCII-SAFEINT-JSON-v1`.
Its admitted values are:

| Value | Constraint |
| --- | --- |
| String, including object keys | Decoded characters U+0020 through U+007E only; at most 1,024 characters |
| Integer | Inclusive range −9,007,199,254,740,991 through 9,007,199,254,740,991 |
| Boolean / null | JSON booleans and null, kept distinct from integers |
| Array / object | Recursively admitted values, subject to the depth and shape rules |

JSON number tokens containing a decimal point or exponent, and the token
`-0`, are rejected. A boolean cannot satisfy an integer field. An identifier
described as nonempty below has length 1–1,024 within the admitted ASCII range.

Canonical output recursively sorts object keys in lexical ASCII order, retains
array order, uses JSON string escaping, and emits no insignificant whitespace.
The resulting bytes are UTF-8. This deliberately restricted format is not
support for the full RFC 8785 input domain.

SHA-256 values use exactly 64 lowercase hexadecimal characters. Public keys use
canonical padded base64 of exactly 32 decoded bytes. Ed25519 signatures use
canonical padded base64 of exactly 64 decoded bytes. Alternate or permissively
decoded base64 encodings are rejected.

## 2. Exact pack shape

The pack has exactly these members:

```text
contract_id
canonicalization
hash_algorithm
signature_algorithm
scope
scope_commitment
events
merkle
producer_manifest
observer_receipt
demo_anchor_receipt
```

The identifiers are fixed:

| Member | Value |
| --- | --- |
| `contract_id` | `vap-interop-demo/0.2.0` |
| `canonicalization` | `DEMO-ASCII-SAFEINT-JSON-v1` |
| `hash_algorithm` | `SHA-256` |
| `signature_algorithm` | `Ed25519` |

There is no embedded public-key registry. Key selection and the approved scope
digest come from the separately supplied trust file.

### 2.1 Scope

The scope has exactly:

```text
chain_id, batch_id, policy_id, window_start, window_end,
in_scope_event_types, expected_attempt_count, completeness_rule
```

- `chain_id`, `batch_id`, and `policy_id` are nonempty identifiers.
- `window_start` and `window_end` are real calendar timestamps in the exact UTC
  form `YYYY-MM-DDTHH:MM:SSZ`, with years 0001–9999. Start is no later than end.
- `in_scope_event_types` is exactly
  `["AI_DECISION_ATTEMPT","AI_DECISION_OUTCOME"]`, in that order.
- `expected_attempt_count` is an integer from 1 through 64.
- `completeness_rule` is exactly `ATTEMPT_OUTCOME_BIJECTION`.

The scope commitment is SHA-256 of the canonical scope object. It must equal
both the pack's `scope_commitment` and the trust file's pinned digest.
A pack cannot replace the selected scope by re-signing a different declaration.

The pinned digest demonstrates selection of one declaration for this local
check. It does not establish who approved it, when approval occurred, whether
the source was complete, or whether the declaration describes real activity.

### 2.2 Events

The event array contains 2–128 elements. Each event has exactly:

```text
contract_id, chain_id, event_id, sequence_no, event_type, timestamp,
issuer_id, key_id, policy_id, model_id, provenance, payload_hash, signature
```

Each event's `contract_id` is `vap-interop-demo/0.2.0`.
Identifiers are nonempty ASCII strings. `sequence_no` is an integer from 1
through 128. `event_type` is one of the two declared scope types. `timestamp`
has the same real-calendar UTC form as the scope endpoints.

All provenance objects contain nonempty `attempt_id`, `actor`, and `action`.
The exact additional members depend on event type:

| Type | Additional provenance members |
| --- | --- |
| `AI_DECISION_ATTEMPT` | `input_hash`: a SHA-256 value; `context`: exactly an object with nonempty `jurisdiction` |
| `AI_DECISION_OUTCOME` | `outcome`: `APPROVED` or `DENIED_AUTOMATION`; nonempty `reason_code`; boolean `human_review_required` |

No other provenance members are accepted.

Let the unsigned event body be the event without `payload_hash` and
`signature`. Its `payload_hash` is SHA-256 of that body's canonical bytes.
The event signature covers the canonical event with only `signature` removed,
so it includes `payload_hash`. Every event must use the key configured for
the producer role.

The verifier additionally requires:

1. Unique event IDs.
2. Sequence numbers exactly 1 through N in array order.
3. Event `chain_id` and `policy_id` equal to the selected scope.
4. Timestamps inside the inclusive scope window and nondecreasing in array order.
5. Exactly one attempt and one outcome for each `attempt_id`.
6. Equal attempt-ID and outcome-ID sets.
7. Each outcome later than its corresponding attempt in sequence order.
8. A distinct-attempt count equal to `scope.expected_attempt_count`.

These are scenario rules. They do not imply that every workflow in VAP has an
attempt/outcome bijection, or that an unobserved action can be reconstructed.

### 2.3 Merkle tree

The Merkle object has exactly `algorithm` and `root`.
Its algorithm is `RFC6962-SHA256`, and its root is a SHA-256 value.

The tree input is the complete signed events in array order. For each event E,
the leaf is SHA-256 of `0x00 || canonical(E)`. An internal node is SHA-256 of
`0x01 || left || right`. The empty-tree root is SHA-256 of the empty byte string.

For more than one input, split at the largest power of two strictly smaller
than the input count, and apply the same rule recursively to the two parts.
There is no odd-node duplication or padding. This is the Merkle Tree Hash
construction in [RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962.html#section-2.1).

The pack's root must match the recomputed root. The empty-tree primitive is
defined for algorithm checks; an empty event array is outside the pack contract.

### 2.4 Signed demo records

Each of the three records has exactly:

```text
record_type, key_id, merkle_root, scope_commitment, event_count, issued_at, signature
```

| Pack member | `record_type` | Required trust role |
| --- | --- | --- |
| `producer_manifest` | `PRODUCER_MANIFEST` | producer |
| `observer_receipt` | `OBSERVER_RECEIPT` | observer |
| `demo_anchor_receipt` | `DEMO_ANCHOR_RECEIPT` | anchor |

The record signature covers the canonical record with `signature` removed.
Its key ID must match the configured role. `event_count` is an integer from
1 through 128. Every record must bind the recomputed Merkle root, recomputed
scope commitment, and actual submitted event count.

`issued_at` is a real calendar UTC timestamp in the same exact form as above,
and must be no earlier than `scope.window_end`. This is a metadata consistency
check. A valid signature over a supplied timestamp does not establish trusted
time or prove prior commitment.

## 3. Explicit synthetic trust input

A trust file has exactly `contract_id`, `trust_version`,
`scope_commitment`, and `roles`.

- `contract_id` is `vap-interop-demo/0.2.0`.
- `trust_version` is `demo-trust/1`.
- `scope_commitment` is the required pinned SHA-256 value.
- `roles` has exactly `producer`, `observer`, and `anchor`.
- Each role contains exactly a nonempty `key_id` and a canonical base64
  `public_key`.
- Key IDs and decoded public keys are distinct across the three roles.

The caller must select this file explicitly. The pack cannot supply its own
trust root or authorize a new signer.

The committed configurations bind public synthetic keys. Their private seeds
are public repeated bytes: `11` for producer, `22` for observer, and `33`
for anchor, each repeated 32 times in hexadecimal. Role pinning is demonstrable;
real-world key provenance and organizational separation are not. Anyone with
these public test secrets can create signatures accepted under the same test
configuration.

## 4. Verifier interfaces and results

```text
python verify_python.py PACK --trust TRUST [--json]
node verify_node.mjs PACK --trust TRUST [--json]
```

Missing trust is a usage error. There is no implicit key source or network
lookup.

| Verdict | Exact exit | Interpretation |
| --- | --- | --- |
| PASS | 0 | All checks in this local contract succeeded |
| FAIL | 1 | Invalid or malformed pack/trust input |
| ERROR | 2 | CLI or file-access error |

Human success starts with `PASS (experimental demo only):`.
After CLI argument parsing succeeds, `--json` results have `contract_id`, `verdict`, `checks`, and
`error`. `verdict` is PASS, FAIL, or ERROR; `error` is null or a string.
Argument-parsing errors print usage to stderr and exit 2 without a JSON result.
Long option names must be spelled fully; abbreviations are not accepted.
For PASS, the check names appear exactly in this order:

```text
contract-and-shape
pinned-scope
event-signatures
sequence-and-scope
rfc6962-root
role-receipts
attempt-outcome-bijection
```

Exact failure-message wording is not an interoperability requirement. The
verdict and exit status are. A runtime failure or unreadable file must not count
as successful detection of a negative fixture.

The Python module exports `VerificationError`, `canonical(value)`,
`strict_loads(text)`, `load_json(path)`, `merkle_root(events)`, and
`verify_pack(pack, trust)`. The Node.js module exports
`VerificationError`, `canonical(value)`, `strictParse(text)`,
`merkleRoot(events)`, and `verifyPack(pack, trust)`.
Importing either module does not execute its CLI.

## 5. Committed dataset and gates

The [README vector table](README.md#expected-vector-results) defines the eight
expected pack outcomes. The associated trust files are
`demo-trust.json` and `demo-trust-six.json`.
The manifest records SHA-256 and byte size for each of those ten files,
the selected trust file and exact verdict/exit for each vector, and root/scope
values for positive vectors.

Compatibility checks use the committed bytes without modification.
`generate_demo.py --check` regenerates expected data in memory and compares it
byte-for-byte without writing the committed files. Generation for a separate
copy requires `--output-dir DIR`.

The two JSON Schema 2020-12 files define structural constraints. Schema
validation cannot replace checks of raw JSON tokens, duplicate keys,
cryptography, role authorization, scope pinning, or relationships between
objects.

The `unittest` and CI gates cover:

- Agreement with the committed generation, digests and sizes.
- Structural validation and exact Python/Node CLI verdicts and exits.
- A six-event positive pack and independent three-/five-leaf tree checks.
- Duplicate members, safe-integer boundaries, disallowed number tokens,
  bool/integer distinction, unsupported Unicode, and unknown fields/algorithms.
- Scope pins, role/record binding, signatures, and missing-trust usage.

These are the required checks for this package. Their presence does not report
an execution result. Publish the source commit, toolchain, dataset and trust
digests, commands and complete transcript when reporting an actual run.

## 6. Claim boundary

A report may state compatibility with `vap-interop-demo/0.2.0` for a named
dataset commit and trust configuration. It must preserve the distinction
between this result and VAP/profile conformance, adoption, certification,
real-world authentication, independent observation, production anchoring,
trusted time, legal compliance, or source completeness.

The two bundled implementations are first-party. An independent implementation
or independent reproduction needs its own attributable source and execution
record, including organizational affiliations and code reuse. Passing these
public-key test fixtures cannot establish the identity or independence of the
simulated evidence parties.
