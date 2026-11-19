# External implementation handoff for the experimental evidence-pack demo

**Prepared:** 20 November 2026 (JST). **Status:** supplementary implementation and reporting guidance.

This brief supports the existing [implementation challenge][challenge], [recruitment brief][recruitment],
and [submission review][review]. Those issues and the selected contract determine the challenge.
This document does not change their acceptance criteria, select a replacement release, or introduce a
VAP requirement. It provides a way to make the inputs and interpretation of each comparison explicit.

## 1. Identify the baseline before comparing results

The contract ID alone does not identify every revision of its text or verifier implementation.

| Comparison | Exact source | Scope |
| --- | --- | --- |
| Published challenge | `cbd4502a0a6d1cd9b7b9d611a849888272d14abb` | Prerelease selected in #2/#4 |
| Supplemental snapshot | `a9ee3a54c3b4e086051c9b7ec80374f2b3b92298` | Includes 11 November hardening |

The 8 November prerelease is `vap-interop-demo-v0.2.0`. Both snapshots use contract ID
`vap-interop-demo/0.2.0`. The later snapshot is not a replacement published release or a
silent change to the challenge baseline. Identify the contract-text commit, implementation commit,
dataset commit and trust inputs independently in every report.

The [published release][release] and [dated release note][release-note] document a known issue in the
tagged verifiers: acceptance of a supplied small-order-key fixture depends on the crypto backend and
on a substituted trust configuration. The explicit screening introduced by [PR #68][hardening] is
absent from the tag and its source ZIP. The release's historical execution record does not establish
that screening. Read this limitation before selecting a comparison.

The original eight packs, two trust files and [manifest][release-manifest] remain the published
dataset. The later [security dataset][security] has its own manifest and recorded conditions.
Report a supplemental security run separately; do not add its cases to the release's historical
eight-vector result or infer that an eight-vector pass exercised the hardening. Trust-file origin
needs separate authentication in either comparison; accepting a replacement trust file can also
authorize ordinary attacker-controlled keys.

## 2. Preserve a reproducible input record

This suggested capture form adds no report schema or acceptance gate.

| Record | Information to retain |
| --- | --- |
| Implementation | Repository URL, full commit SHA, license, maintainer, implementation method and code reuse |
| Contract | Contract ID, exact `CONFORMANCE.md` commit and file digest, explicitly selected comparison |
| Dataset | Source commit, manifest digest, input filenames, byte sizes and digests |
| Trust | Explicitly selected trust file and digest for each pack; how the reviewer selected that input |
| Environment | Operating system, architecture, language/runtime and cryptographic dependency versions |
| Execution | Exact build/run commands, working directory, UTC execution time, stdout, stderr and exit codes |
| Deviations | Missing dependencies, unsupported checks, altered setup, ambiguities and affected cases |
| Additional probes | Separate raw-input files and digests, targeted contract clauses and observed outcomes |

The demo has no external evaluation-time or configurable verification-policy CLI argument.
Its scope and timestamp checks use the supplied records and selected trust input. Do not invent
such inputs for this contract. For a different experimental profile that actually uses them,
record the selected policy and evaluation time when reporting that profile.

Confirm input digests before the run and retain the original bytes. Parsing and reserializing
a JSON file can erase duplicate keys or change number tokens before verification starts.
Generated or modified probes belong in a separately identified dataset.

## 3. Implement the selected contract and record the complete matrix

The existing challenge calls for a publicly reviewable, OSI-licensed implementation maintained
outside the VeritasChain organization, with the independence and disclosure requirements in
[issues #2][challenge] and [#4][recruitment]. It excludes importing, copying or mechanically
translating VSO reference code. Report the method and any reused libraries; another language,
process or signing key does not itself establish independent authorship.

The published [manifest][release-manifest] selects the trust input and expected result for each
of eight packs: two `PASS` / exit `0`, and six `FAIL` / exit `1`.
Keep a result row for every case. The selected contract governs interfaces, JSON output and the
required successful check names/order. Exact failure-message wording is not a compatibility
requirement. `ERROR` / exit `2`, including a file-access or usage error, does not satisfy an
expected negative result.

Distinguish expected values from observations. A case that was not run has no observed verifier
verdict. A missing tool or unsupported implementation feature should be recorded as an execution
or coverage limitation, not rewritten as the expected `FAIL`. These reporting distinctions do
not add new CLI verdicts to the contract or relax its required behavior.

Keep the external maintainer's run, VSO's reproduction, and reference comparisons separately attributable.

## 4. Localize disagreements without expanding the contract

Optional diagnostics can record canonical bytes, hash/signature inputs, computed roots and the first
differing check. They add no required interface. Compare equivalent configured inputs before verdicts.

The restricted representation already defines ASCII strings, safe integers, integer-only number
tokens, strict UTF-8, duplicate-key rejection, and size/depth limits. It is not full RFC 8785.
For example, both `1e-07` and `1e-7` are outside this demo's input domain because they contain
an exponent. A generic JCS comparison should not silently expand that domain.

For supplementary probes, test raw parser input as well as cryptographic relationships. Retain
which clause and stage were exercised; a malformed-input rejection does not establish that
signature or relationship checks ran. Likewise, successful cryptography does not replace scope,
role, sequence or attempt/outcome checks.

## 5. Route the findings through existing work

Use [#2][challenge] for an attributable submission and [#5][review] for reproduction and discrepancy
review. [#3][publication] records the completed prerelease publication; its older preparation text
is historical. [#4][recruitment] tracks recruitment separately.

If a discrepancy requires another baseline or contract interpretation, record that proposal and
its compatibility effect in the existing review rather than silently changing the inputs.
This brief records no external submission, outreach, new execution result, release or completed gate.

A supported result concerns the named experimental contract, dataset and trust configuration.
It does not establish VAP/profile conformance, certification, production anchoring, trusted time,
source completeness or the identity of the synthetic evidence parties.

[challenge]: https://github.com/veritaschain/vap-spec/issues/2
[publication]: https://github.com/veritaschain/vap-spec/issues/3
[recruitment]: https://github.com/veritaschain/vap-spec/issues/4
[review]: https://github.com/veritaschain/vap-spec/issues/5
[release]: https://github.com/veritaschain/vap-spec/releases/tag/vap-interop-demo-v0.2.0
[release-note]: https://github.com/veritaschain/vap-spec/blob/a9ee3a54c3b4e086051c9b7ec80374f2b3b92298/interop/vap-evidence-pack-demo/RELEASE.md
[release-manifest]: https://github.com/veritaschain/vap-spec/blob/cbd4502a0a6d1cd9b7b9d611a849888272d14abb/interop/vap-evidence-pack-demo/test-vectors/manifest.json
[hardening]: https://github.com/veritaschain/vap-spec/pull/68
[security]: https://github.com/veritaschain/vap-spec/blob/a9ee3a54c3b4e086051c9b7ec80374f2b3b92298/interop/vap-evidence-pack-demo/security-vectors/README.md
