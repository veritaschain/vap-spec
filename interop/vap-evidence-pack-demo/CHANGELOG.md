# Experimental interoperability demo change history

This history applies only to `vap-interop-demo/0.2.0`. It is not a VAP framework
version history or adoption record.

## 0.2.0 — implementation merged 2026-10-30; release preparation 2026-11-07

**Publication status:** A release/tag is proposed in [RELEASE.md](RELEASE.md).
This entry does not assert that either has been created.

[PR #1](https://github.com/veritaschain/vap-spec/pull/1) replaced the earlier
prototype with an explicitly experimental local contract:

- Separate caller-selected trust input pins the scope and three distinct
  synthetic role keys. The submitted pack cannot authorize its own signers.
- `DEMO-ASCII-SAFEINT-JSON-v1` defines restricted canonical bytes and strict
  parsing. It does not implement the full RFC 8785 input domain.
- The Merkle tree uses the RFC 6962 split construction, without odd-node
  duplication. Fixed three-/five-leaf roots and a six-event pack exercise it.
- Signed role records bind the root, scope and submitted count. The scenario
  requires one later outcome for each declared attempt.
- Eight fixed pack vectors, two synthetic trust files and a digest/expectation
  manifest support Python/Node comparison. The existing suite has 32 test
  methods; an operational error is not accepted as a negative-vector result.
- [CONFORMANCE.md](CONFORMANCE.md) states the local compatibility requirements;
  [SCENARIO.md](SCENARIO.md) records assumptions and limits.

The 7 November preparation adds release documentation, a single reproduction
entry point and a dated first-party execution record. The existing read-only
CI workflow installs with the dated dependency constraints and invokes that
same entry point once. Its action/runtime pins and event/path coverage remain
unchanged. The preparation does not change the verifiers, tests, schemas,
generator, requirements or committed dataset.

## Historical July prototype — preserved, not a released baseline

The [prototype at `ec6cfba`](https://github.com/veritaschain/vap-spec/tree/ec6cfbaf901e6147f767bbe56132b1bb6211337a/interop/vap-evidence-pack-demo)
remains at its original revision. It used different signed content, trust
handling and tree construction. Its files are not inputs to version 0.2.0.
The historical `vap-evidence-pack-v0.1.0` release name in issue planning is not
reused. Historical artifacts are not rewritten or relabeled.
