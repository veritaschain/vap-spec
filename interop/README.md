# Experimental interoperability demos

This directory contains versioned, first-party demonstration contracts and
committed synthetic datasets for comparing verifier implementations.

## Current package

| Package | Local contract | Purpose |
| --- | --- | --- |
| [Evidence-pack demo](vap-evidence-pack-demo/README.md) | `vap-interop-demo/0.2.0` | Compare Python and Node.js checks of a small signed dataset, an RFC 6962 Merkle root, caller-selected synthetic trust, and a scenario-specific attempt/outcome rule |

The package's schema describes its own experimental format. VAP v1.2 leaves
Evidence Pack formats to profiles; this directory does not introduce a common
VAP container, registered profile, or adopted framework requirement.

The [declared-scope proposal](../proposals/declared-scope-precommit/README.md)
and [declared-scope research verifier](../experiments/declared-scope-verifier/README.md)
remain separate work with their own contracts and result meanings.

The bundled keys, observer role, and receipt role are synthetic and first-party.
Matching results demonstrate compatibility with the named demo contract.
Organizationally independent implementation or reproduction must be evidenced
separately; neither compatibility nor a demo PASS establishes VAP conformance,
certification, legal compliance, or the origin of real-world records.
