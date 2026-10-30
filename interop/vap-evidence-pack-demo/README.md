# Experimental evidence-pack interoperability demo

**Contract:** `vap-interop-demo/0.2.0`  
**Status:** First-party, experimental, offline; unadopted as a VAP format or requirement.

This package gives Python and Node.js verifiers the same small, committed
synthetic dataset and an explicit trust configuration. It demonstrates local
agreement on document structure, signatures, event ordering, an RFC 6962
Merkle root, signed record bindings, and one scenario-specific rule:
each declared attempt has exactly one later outcome.

A successful result means that the submitted files satisfy **this demo
contract**. It does not establish full VAP conformance, a profile mapping,
production anchoring, organizational independence, or the truth and
completeness of real-world observations.

## Contract and history

The local contract is defined in [CONFORMANCE.md](CONFORMANCE.md).
[SCENARIO.md](SCENARIO.md) explains the synthetic workflow and its assumptions.

The [July 2026 prototype at `ec6cfba`](https://github.com/veritaschain/vap-spec/tree/ec6cfbaf901e6147f767bbe56132b1bb6211337a/interop/vap-evidence-pack-demo)
remains available at its original commit. The 0.2.0 contract uses its own
identifier, exact object shapes, an external trust input, and new deterministic
vectors. It changes the tree construction and the signed content. Old prototype
packs are not inputs to this version; preserve them with their original
verification context.

The events are flat **demo events**, and the three signed records are **demo
records**. Their shapes are not the abstract event or AnchorRecord structures
shown in VAP v1.2 §7. No `vap_version`, `VAP-COMMON` profile, or embedded
public-key registry is asserted by this contract.

The [declared-scope proposal](../../proposals/declared-scope-precommit/README.md)
and [declared-scope research verifier](../../experiments/declared-scope-verifier/README.md)
use different contracts. This package neither adopts that proposal nor replaces
its `vap-v1.2` and `experimental-scope` modes.

## Files

| Path | Purpose |
| --- | --- |
| `generate_demo.py` | Deterministic generation into an explicitly selected directory; read-only comparison with committed fixtures |
| `verify_python.py` | Python verifier and importable local verification functions |
| `verify_node.mjs` | Node.js verifier and importable local verification functions |
| `schema/evidence-pack.schema.json` | JSON Schema 2020-12 structural contract for demo packs |
| `schema/demo-trust.schema.json` | JSON Schema 2020-12 structural contract for synthetic trust input |
| `test-vectors/*.json` | Eight pack vectors, two trust files, and a manifest |
| `test-vectors/manifest.json` | Expected verdicts, exact exit codes, trust-file choices, and file digests and sizes |
| `tests/` | Schema, deterministic-generation, CLI, cryptographic and boundary checks using `unittest` |
| `CONFORMANCE.md` | Local compatibility requirements and the exact byte and object contracts |
| `SCENARIO.md` | Synthetic workflow, negative-vector construction, and claim boundaries |

The schemas cover structure. Signature verification, hashes, relationships,
strict JSON token parsing, and trusted-role bindings are verifier checks.
Passing schema validation alone is not a demo PASS.

## Run the committed dataset

Use Python 3.12 and Node.js 24 for the documented toolchain. From the repository
root:

```sh
cd interop/vap-evidence-pack-demo
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt

python generate_demo.py --check
python -m unittest discover -s tests -v

python verify_python.py test-vectors/valid-pack.json --trust test-vectors/demo-trust.json
node verify_node.mjs test-vectors/valid-pack.json --trust test-vectors/demo-trust.json
```

Use the six-event pack with its own pinned trust file:

```sh
python verify_python.py test-vectors/valid-six-events.json --trust test-vectors/demo-trust-six.json --json
node verify_node.mjs test-vectors/valid-six-events.json --trust test-vectors/demo-trust-six.json --json
```

`--trust` is required. The verifier does not fetch keys, receipts, or other
evidence over the network. Use `--json` to receive `contract_id`, `verdict`,
`checks`, and `error` as a machine-readable result.
Argument-parsing errors (including a missing `--trust`) print usage to stderr
and exit 2 before JSON output is available. Long options must be spelled fully.

| Verdict | Exit | Meaning |
| --- | --- | --- |
| PASS | 0 | All local checks for this contract succeeded |
| FAIL | 1 | The pack or trust input is malformed or violates the local contract |
| ERROR | 2 | CLI usage or file-access failure prevented evaluation |

Human-readable success starts with `PASS (experimental demo only):`.
A negative fixture is accepted by the test harness only when verification exits
**exactly 1**. An operational error is not evidence that the intended negative
condition was detected.

### Generate a separate copy

Choose a new output directory:

```sh
python generate_demo.py --output-dir /tmp/vap-interop-demo-0.2.0
```

Generation requires an explicit `--output-dir`. `--check` performs a
byte-for-byte comparison with the committed fixture files without writing them.
Generation refuses to overwrite any of its destination filenames, including
symlinks. Use a new directory for each copy; historical evidence is not migrated
in place.

## Expected vector results

These are contract expectations, not an execution transcript or a claim that a
particular CI run passed. Exact filenames, digests, sizes, expected exits and
trust choices are recorded in [the manifest](test-vectors/manifest.json).

| Vector | Trust file | Expected result | Condition exercised |
| --- | --- | --- | --- |
| `valid-pack.json` | `demo-trust.json` | PASS / 0 | Two complete attempt/outcome pairs |
| `valid-six-events.json` | `demo-trust-six.json` | PASS / 0 | Three complete pairs; a non-power-of-two Merkle tree |
| `invalid-tampered-event.json` | `demo-trust.json` | FAIL / 1 | Modification of signed event content |
| `invalid-omitted-outcome.json` | `demo-trust.json` | FAIL / 1 | One outcome omitted while the remaining pack is re-signed |
| `invalid-split-view.json` | `demo-trust.json` | FAIL / 1 | A signed observer record names a conflicting root |
| `invalid-omitted-pair.json` | `demo-trust.json` | FAIL / 1 | A complete pair omitted while the pinned expected count remains unchanged |
| `invalid-rebound-scope.json` | `demo-trust.json` | FAIL / 1 | A changed scope attempts to replace the caller-pinned declaration |
| `invalid-untrusted-signer.json` | `demo-trust.json` | FAIL / 1 | A signer is outside the configured role binding |

The workflow checks committed-fixture reproducibility, both structural schemas,
meaningful parser and cryptographic boundaries, and the exact CLI outcomes of
both implementations. Results belong to the particular source commit,
toolchain, dataset and trust files used for that run.

## Synthetic trust and receipts

The caller supplies `--trust` separately from the pack. That file pins a scope
digest and three distinct key IDs and public keys for producer, observer and
anchor roles. The supplied files are **synthetic test configurations**.

The deterministic private keys are public: the producer, observer and anchor
use 32-byte seeds consisting respectively of `0x11`, `0x22` and `0x33`
repeated 32 times. Anyone can sign with them. Verifying these signatures
demonstrates a cryptographic check and a local key/role binding; it does not
authenticate a real producer, prove record origin, or demonstrate an independent
observer.

`demo_anchor_receipt` carries a `DEMO_ANCHOR_RECEIPT`. It is a signed fixture,
not a receipt from a TSA, SCITT service, public log, or blockchain. Record
timestamps are checked for format and consistency with the declared window.
No trusted time, advance commitment, or independent anchoring is established.

## Informative relationship to VAP and current research

This table identifies related ideas and boundaries. It is **not a clause-level
conformance mapping**. The framework context is
[VAP v1.2 Draft 3 at `589d6b5`](https://github.com/veritaschain/vap-spec/blob/589d6b522c8d23261e9bfce1103784ac460c85ee/spec/v1.2/VAP_Framework_Specification.md).

| Reference or topic | This demo checks | Boundary |
| --- | --- | --- |
| INT-001 / INT-003; §7.3 | Deterministic bytes and SHA-256 over the defined demo objects | `DEMO-ASCII-SAFEINT-JSON-v1` is a constrained local format, not support for the full RFC 8785 input domain or VAP event serialization |
| INT-002 / INT-004 | Unique demo event IDs, contiguous sequence numbers, and scope/time membership | Profile-specific sequence mechanisms and detection latency are not assessed |
| INT-005 | Ed25519 signatures under explicitly configured test-role keys | Public test secrets cannot establish real-world signer identity or non-repudiation |
| INT-006; §4.1.4 | RFC 6962 SHA-256 tree construction and agreement on the computed root | No production external anchor, target-specific receipt proof, or full INT-006 assessment |
| INT-008; §7.5 | A pinned demo scope, signed counts, root agreement, and this scenario's attempt/outcome bijection | The bijection is a local rule. It is not the framework's anchor-granularity Completeness Invariant, and these records are not VAP AnchorRecords |
| TRC-005 / cross-party evidence | Agreement among the three configured synthetic roles | Role separation in a test file does not demonstrate institutional independence or which claim describes reality |
| Declared-scope proposal | A fixed declaration selected through a caller-pinned digest | No proof of advance acceptance, source closure, complete expected-event inventory, disclosure duties, or proposal adoption |
| Declared-scope research verifier | A separate small Python/Node interoperability exercise | No compatibility claim with `vap-evidence-research-adapter/1` or either research-verifier mode |

The demo does not assess INT-007 continuity, INT-009 recovery, ERASURE, operational
capture controls, or full profile conformance. It cannot reveal actions that no
available record implies. A matching pair of synthetic records also says
nothing about whether the stated action occurred.

## Reporting interoperability work

For a reproduction or a new implementation, record the implementation source
and commit, toolchain versions, fixture-manifest digest, selected trust-file
digests, exact commands, outputs and exit codes. Disclose affiliations, code
reuse, deviations and unresolved ambiguities.

Both bundled verifiers are first-party work. Independent reproduction and an
organizationally independent implementation are separate claims requiring their
own evidence. A compatibility claim should name `vap-interop-demo/0.2.0` and
the exact dataset commit; it should not be presented as VAP certification or
adoption of this format.
