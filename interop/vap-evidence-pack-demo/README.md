# VAP Third-Party Verification Demo

This directory contains an executable interoperability demonstration for the
**VAP Common Evidence Layer**. It is intentionally profile-neutral: the same
verification contract can be used by VCP, CAP, CPP, and future VAP profiles.

The demo answers one concrete question:

> Can a verifier that does not operate the AI system independently determine
> whether the submitted decision evidence is authentic, collection-consistent,
> scope-bound, complete under a declared invariant, and corroborated by an
> independent observer?

## Why this is VAP-specific

Digital signatures and Merkle trees can prove that a submitted collection has
not changed. They do **not**, by themselves, prove that the collection contains
all events required by the declared decision workflow.

The critical negative vector in this demo is
`invalid-omitted-outcome.json`. It is deliberately rebuilt with internally
valid event signatures, a new valid Merkle root, and valid producer, observer,
and anchor signatures. A generic cryptographic log verifier can accept it. A
VAP-aware verifier rejects it because the declared **Completeness Invariant**
requires a one-to-one relationship between decision attempts and outcomes.

The demo combines five verification properties:

1. **Decision provenance semantics** — Actor, input, policy, model, action, and
   outcome are carried as structured evidence.
2. **Cryptographic authenticity** — Events and receipts are signed with
   Ed25519.
3. **Collection integrity** — The event collection is committed through an
   RFC 6962-style domain-separated Merkle root.
4. **Scope and completeness** — A signed scope commitment defines what must be
   present, and the verifier enforces the declared invariant.
5. **Cross-party agreement** — Producer, independent observer, and external
   receipt must agree on the same root and scope commitment.

## Contents

| Path | Purpose |
|---|---|
| `generate_demo.py` | Generates deterministic positive and negative vectors |
| `verify_python.py` | Python offline verifier |
| `verify_node.mjs` | Independently written Node.js offline verifier |
| `test-vectors/valid-pack.json` | Evidence Pack that MUST pass |
| `test-vectors/invalid-tampered-event.json` | Modified signed event; MUST fail |
| `test-vectors/invalid-omitted-outcome.json` | Cryptographically self-consistent omission; MUST fail the VAP invariant |
| `test-vectors/invalid-split-view.json` | Valid observer signature over a conflicting root; MUST fail |
| `CONFORMANCE.md` | Acceptance criteria for external implementations |
| `SCENARIO.md` | Demonstration workflow and threat model |

## Run the demo

### Python

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
python generate_demo.py
python verify_python.py test-vectors/valid-pack.json
pytest -q
```

### Node.js

Node.js 20 or later is sufficient; no npm dependencies are required.

```bash
node verify_node.mjs test-vectors/valid-pack.json
```

Both verifiers MUST print `PASS` for the valid vector and return a non-zero exit
status for every invalid vector.

## What counts as an independent implementation

The Python and Node.js verifiers demonstrate implementation diversity, but both
are published by VSO and therefore do **not** constitute organizationally
independent validation.

A genuine independent implementation must:

- be maintained outside the `veritaschain` GitHub organization;
- be written without copying either reference verifier;
- use the committed JSON vectors as its input contract;
- pass all tests in `CONFORMANCE.md`;
- publish its source, version, commit hash, and execution transcript;
- disclose any ambiguities or deviations found in the Evidence Pack contract.

See the public GitHub issue linked from the repository for the implementation
challenge.

## Security and scope limitations

- Deterministic private keys are embedded in the generator **for test vectors
  only**. They MUST NOT be used outside this demo.
- `DEMO_TRANSPARENCY_RECEIPT` is a signed test receipt, not an RFC 3161 token,
  SCITT receipt, qualified timestamp, or production transparency service.
- Canonicalization is a constrained, no-floating-point subset designed to be
  byte-identical in Python and JavaScript. Production VAP profiles must use the
  canonicalization required by their normative specification.
- This demo verifies evidence integrity and declared completeness. It does not
  prove that the original capture point observed every real-world action before
  log creation.
- Passing this demo is not certification, regulatory approval, or a guarantee
  that the underlying AI decision was correct, fair, lawful, or safe.
