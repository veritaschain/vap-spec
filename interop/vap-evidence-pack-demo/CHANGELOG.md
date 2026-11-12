# Experimental interoperability demo change history

This history applies only to `vap-interop-demo/0.2.0`. It is not a VAP framework
version history or adoption record.

## Unreleased implementation hardening — 2026-11-11

- Both implementations explicitly reject the eight small-order Ed25519 points
  for role keys and signature R values, noncanonical point encodings, and
  signature scalars at or above the subgroup order. The crypto library still
  verifies the equation. These are documented local demo requirements.
- A separate fixed forged-pack/trust fixture and cross-language regressions
  cover the defect. The original dataset, manifest, generator, signed artifacts
  and retained 7 November execution record remain unchanged.
- The original implementation accepts the forged fixture with Python
  `cryptography 50.0.2` and Node `22.23.4`; Node `24.22.1` already rejects it
  in its backend. Explicit prechecks make the revised rejection independent
  of that observed backend difference. See [the record](security-vectors/README.md).

The contract ID remains `vap-interop-demo/0.2.0`; the package has no released
tag asserted here. Reports must pin the implementation commit. This update is
not a VAP amendment, certification, external reproduction or trust-file
authentication mechanism.

**Publication note, 13 November 2026 (JST):** the prerelease
`vap-interop-demo-v0.2.0` exists at `cbd4502` (published 8 November 2026) and
does not include this hardening. The known issue is recorded at the top of
[RELEASE.md](RELEASE.md) and in that release's notes; its tag and assets are
unchanged.

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
