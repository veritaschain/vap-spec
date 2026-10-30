# Review report execution records

The completed [implementation push run 41007421315](https://github.com/veritaschain/vap-spec/actions/runs/41007421315)
passed on **2026-10-30, 14:16 JST** using Python **3.12.15** and **3.14.9** at exact
commit [`504bc1e5f43a034ef9062c9f1b5a39bb784dac60`](https://github.com/veritaschain/vap-spec/commit/504bc1e5f43a034ef9062c9f1b5a39bb784dac60).
Both downloaded report bundles and every report member were byte-identical to
each other and the verified local outputs. This is an automated view of frozen
synthetic evidence. Human review, independent reproduction and observation truth
are not established by this result.

## Read the generated report

- [Japanese report](review-ja.md): scope, 53-case index, detailed observations,
  assessor phases, missing frames, interpretation notes and source references.
- [English report](review-en.md): the same facts and scope in English.
- [Authoritative JSON](review.json): the exact machine-readable projection and
  complete source/recheck bindings.
- [Member manifest](manifest.json): hashes and lengths of those three files.
- [Machine-readable CI record](ci-record.json): exact commits, runs, jobs,
  source identities, downloaded-byte checks and artifact retention.

The four report members above are copied directly from the verified Python 3.12
CI artifact without reserialization. Both original CI summary JSON files are
also retained byte-for-byte. File references in the report use the fixed original
capture commit, raw-file hashes and concrete JSON Pointers. The F registry binds
file/hash/URL; the S registry binds F-number/pointer.

## Completed checks

| Check | Python 3.12.15 | Python 3.14.9 |
|---|---:|---:|
| Software test methods | 37/37 | 37/37 |
| Failures, errors, skips, unraisable finalizer exceptions | 0 | 0 |
| Original saved cases rechecked | 53/53 | 53/53 |
| Frozen prior input files unchanged | 136/136 | 136/136 |
| Execution-source manifest unchanged | 154/154 | 154/154 |
| Exact report rederivation | Matched | Matched |
| Downloaded outer artifact digest | Matched | Matched |
| Downloaded report ZIP and every inner/readable member | Identical to local | Identical to local |
| Downloaded execution summary versus completed job marker | Matched | Matched |

The 37 methods comprise 12 projection, 15 delivery, eight separately authored
boundary and two full CLI integration methods. The pipeline actually invokes
the unchanged verifier workers. Negative tests additionally inject malformed
results and source/output faults; those diagnostic doubles are not presented as
new observations of external systems.

The generated view preserves **53 cases, 409 recorded sections and 129 assessor
frames**, of which **100 are recorded and 29 are explicitly absent**. It contains
87 instances of fixed interpretation notes. Absence of a frame remains distinct
from an assessor explicitly returning `UNKNOWN`. The expectation count of 53
includes deliberate negative controls and is not a security-success count.

- Python 3.12: [job 123905365967](https://github.com/veritaschain/vap-spec/actions/runs/41007421315/job/123905365967), [original summary](summary-python-3.12.json).
- Python 3.14: [job 123905365782](https://github.com/veritaschain/vap-spec/actions/runs/41007421315/job/123905365782), [original summary](summary-python-3.14.json).

## Report bundle identity

The deterministic inner `incident-review.zip` is **2,237,333 bytes**, with SHA-256:

```text
df971f32b68efc20bb76352076266747485bc9c49a26e248aec6af444a399360
```

| Member | Bytes | SHA-256 |
|---|---:|---|
| review.json | 809,389 | `0de419ece3f344b763122d0dfc69ec4649cf0867c3438e829f2e90031401a316` |
| review-en.md | 698,879 | `c95ef69802b0665eeb5e3df536e3fc7b02573ed1e4b77a0e22f63db5bd71846b` |
| review-ja.md | 728,229 | `a8a52417a4f35217d83d43d9dabb3d168314dd95890627bfb71f6eda9a53284d` |
| manifest.json | 414 | `087717cf95c6056f7ca5bf955b5e7093fcb5ec3b97c183b39eab939453a3ecf7` |

The report's 154-file execution source SHA-256 is:

```text
1b6187b8d732e299de389e957601b96ad971f908f1b96cc6da11d2662e2efb3b
```

The input kit remains the original PR35 archive with SHA-256
`06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f`.
No frozen kit member, original case, prior pilot runtime or normative specification
was changed to obtain this result.

## Download and reverify

| Python job | Outer GitHub artifact | Expected expiry |
|---|---|---|
| 3.12 | [incident-review-python-3.12](https://github.com/veritaschain/vap-spec/actions/runs/41007421315/artifacts/12955803380) | 2026-11-29 14:16:03 JST |
| 3.14 | [incident-review-python-3.14](https://github.com/veritaschain/vap-spec/actions/runs/41007421315/artifacts/12956216934) | 2026-11-29 14:16:08 JST |

Each outer download contains exactly the inner report ZIP, its four members,
`summary.json` and `SHA256SUMS`. The report digest above applies to the inner
`incident-review.zip`; outer download hashes are separately retained in
`ci-record.json`. Both downloads were checked against their GitHub digests and
bounded inventories. All four outer readable members matched their inner ZIP
counterparts and local bytes. The summary matched its completed job log marker.

Use the [Japanese instructions](../RUN-ja.md) or [README](../README.md#reverify-a-received-report)
with an expected report hash obtained outside the candidate. Verification checks
the raw candidate hash, actually rechecks the original fixed evidence, rederives
the whole report and compares exact bundle bytes. A candidate cannot authorize
altered conclusions by rewriting its own JSON, Markdown and internal hashes.

After Actions retention expires, the exact report members in this directory,
the original fixed capture and reviewed source remain in Git. Recreating the
report uses those sources and evidence; it does not run the original upload,
publication or erasure operations.

## What the record does not establish

Rechecking and formatting signed statements does not establish that all original
observations were truthful, independent or complete outside their declared scope.
The report keeps source-attributed statements, recorded observations, original
assessment phases and unresolved results distinct. It generates no security grade,
human approval, universal erasure conclusion or automatic compliance decision.

The scope retains `actions_reexecuted: false`, `human_review: NOT_PERFORMED`,
`observation_truth: NOT_ESTABLISHED`, `independent_reproduction: NOT_ESTABLISHED`,
`conformance: NOT_ASSESSED`, `legal_compliance: NOT_ASSESSED` and
`dependency_scope: PINNED_VERSIONS_NOT_HERMETIC`. The interpreter, local reviewed
source, host and installed dependency binaries remain trust assumptions; the
existing Python audit hook is not an OS sandbox.

The result-recording commit follows the tested implementation above. Results,
review notes and the informative contract are excluded from the source manifest,
so preserving these observed files does not alter the report's own source inputs
or expected output hash. Local Python 3.12.14 passed the same 37 methods and
produced the identical report bundle before CI.
