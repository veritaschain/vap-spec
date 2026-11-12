# Experimental demo 0.2.0 release preparation

> **Publication record and known issue — added 13 November 2026 (JST).**
> The prerelease prepared below was published on 8 November 2026
> (`2026-11-08T03:09:00Z`) as
> [`vap-interop-demo-v0.2.0`](https://github.com/veritaschain/vap-spec/releases/tag/vap-interop-demo-v0.2.0)
> at commit [`cbd4502a0a6d1cd9b7b9d611a849888272d14abb`](https://github.com/veritaschain/vap-spec/commit/cbd4502a0a6d1cd9b7b9d611a849888272d14abb),
> and [Issue #3](https://github.com/veritaschain/vap-spec/issues/3) is closed.
> The preparation text below is retained as written on 7 November. Its
> statements that no tag or release exists, that Issue #3 remains open and that
> the final commit is still to be selected describe that date, not the present.
>
> **Known issue in the tagged source.** The two verifiers at `cbd4502` are
> byte-identical to the revision examined in the
> [11 November security record](security-vectors/README.md). They do not screen
> Ed25519 inputs before backend verification. When the caller accepts a
> substituted trust file whose role keys are small-order points, the fixed
> altered pack in `security-vectors/` passes all seven checks under Python
> `cryptography` 50.0.2 and Node 22.23.4; Node 24.22.1, the release toolchain,
> rejects it. With the original `demo-trust.json` the same pack is rejected.
> A party able to substitute the trust file can also sign with ordinary keys,
> so the trust file needs its own authentication in every case.
>
> The explicit input policy merged on 11 November 2026
> ([PR #68](https://github.com/veritaschain/vap-spec/pull/68), `35e56ba`) is on
> `main` only. It is not part of the tag, the attached source ZIP or the
> 32-test record of that release. The release is immutable: its tag and assets
> are unchanged, and only its notes carry the same known-issue statement. No
> replacement release has been published or scheduled here. Reports that use
> the demo must pin the implementation commit. These are first-party
> observations on synthetic data, not an independent reproduction.

**Status at 7 November 2026 (JST):** proposed prerelease; no tag or release is
created by this preparation. [Issue #3](https://github.com/veritaschain/vap-spec/issues/3)
tracks publication and remains open until the release evidence is linked.

## Version and scope decision

| Item | Proposed value |
| --- | --- |
| Local contract | `vap-interop-demo/0.2.0` |
| Git tag | `vap-interop-demo-v0.2.0` |
| Release title | Experimental interoperability demo 0.2.0 — first-party synthetic baseline |
| GitHub release classification | Prerelease; not the latest VAP framework release |
| Final release commit | To be selected from the reviewed preparation; not assigned here |

The accepted scope is [CONFORMANCE.md](CONFORMANCE.md): a local compatibility
contract for one synthetic attempt/outcome scenario. Its requirements do not
amend VAP, register a profile or define a common VAP Evidence Pack format.
[CHANGELOG.md](CHANGELOG.md) preserves the transition from the July prototype.

The candidate source baseline is
[`d97980f340ff9f81639daf8ffa6e02acbe1433ec`](https://github.com/veritaschain/vap-spec/commit/d97980f340ff9f81639daf8ffa6e02acbe1433ec).
The implementation merged through
[PR #1](https://github.com/veritaschain/vap-spec/pull/1), merge
`af856dd357f3cb8767fea3cb5b198ea4aac5c7a8`.
The [successful prior CI run](https://github.com/veritaschain/vap-spec/actions/runs/41057936560)
tested `3dea7ce88dbe7a0af22740602d17129dc80febaa`. The original demo and workflow
blobs in base commit `d97980f` match that tested revision. This preparation
changes the workflow to exercise the new entry point and constraints; the
earlier CI run does not test that change.

## Reproduce with one check command

Prerequisites: Python 3.12, Node.js 24, and a POSIX shell. From the repository
root, prepare an isolated environment once:

```sh
python3.12 -m venv /tmp/vap-interop-demo-env
. /tmp/vap-interop-demo-env/bin/activate
python -m pip install -r interop/vap-evidence-pack-demo/requirements.txt \
  -c interop/vap-evidence-pack-demo/release-preparation/2026-11-07/constraints.txt
```

Use a new environment path if that path already exists. Installation may need
network access. The constraints record the packages resolved for the dated
local run; they are not a wheel archive or a guarantee of future availability.

Then run one command from the repository root:

```sh
sh interop/vap-evidence-pack-demo/reproduce.sh
```

`VAP_DEMO_PYTHON` can select an existing Python executable; it is not a command
string. The entry point checks Python 3.12, Node.js 24 and the two direct
dependency versions, compares all 11 committed fixture/manifest files without
rewriting them, and runs the existing 32-test suite. Those tests execute both
verifier CLIs against all eight vectors: two expected PASS/exit 0 and six
expected FAIL/exit 1. Usage/file-access errors are not accepted in place of
the specified negative result. The checks run locally without fetching trust
or evidence. Temporary test files may be created outside the fixed dataset.

The runner exits nonzero if setup or a check fails. Its success is evidence
only for the named experimental contract and supplied synthetic inputs.

The [CI workflow](../../.github/workflows/vap-evidence-demo.yml) installs the
unchanged requirements with the dated constraints and runs `sh reproduce.sh`
once, replacing its previous separate generator/test steps. The action/runtime
pins, read-only permissions and event/path coverage remain unchanged. A new
exact-head CI result is required for this modified workflow; the local record
below is not a GitHub Actions execution.

## Fixed inputs and observed preparation evidence

The existing [vector manifest](test-vectors/manifest.json) contains exact
SHA-256 digests, sizes, trust choices and expected verdicts/exits for eight
packs and two trust files. It describes expectations, not an observed run.

The dated record keeps those facts separate:

- [reproduction.json](release-preparation/2026-11-07/reproduction.json) records
  the base commit, actual runtime versions, original source-file commitments,
  changed runner/workflow digests, executed command and observed exit.
- [reproduction.txt](release-preparation/2026-11-07/reproduction.txt) retains
  the complete output of the local check command.
- [constraints.txt](release-preparation/2026-11-07/constraints.txt) records
  the observed Python dependency versions.
- [SHA256SUMS](release-preparation/2026-11-07/SHA256SUMS) commits to those three
  evidence files. It deliberately does not hash itself.

The refreshed record was produced after the workflow edit. It preserves
commitments to 22 unchanged original demo/license files and separately records
the uncommitted runner and modified workflow. Documentation is also
uncommitted. These file digests identify the actual inputs; no future release
commit or publication is inferred from them. The recorded dependency install
uses the same requirements and constraints as the updated workflow.
This is first-party execution in the same operator's environment. It is not
an organizationally independent implementation or reproduction.

## Proposed publication assets

Create these only after selecting and testing the final reviewed commit:

| Asset | Content |
| --- | --- |
| `vap-interop-demo-v0.2.0-source.zip` | A `git archive` of the exact final commit |
| `manifest.json` | Byte-for-byte copy of the existing vector manifest |
| `reproduction.txt` | Complete final-candidate execution transcript |
| `SOURCE.json` | Source, environment, execution and asset commitments described below |
| `SHA256SUMS` | Hashes of the preceding assets; excludes itself |

`SOURCE.json` records the exact tag target/tree, contract, original code
baseline, command, runtime/dependency versions, CI/run references and asset
hashes/sizes. It identifies the environment of the accompanying transcript.

The source archive preserves repository context. Only
`interop/vap-evidence-pack-demo/` is the contract released here; inclusion of
other files does not release or adopt their experimental contracts. Keep the
existing license and attribution. Do not regenerate fixtures for publication.

Generate the source archive from the selected commit, not a working directory.
Generate `SOURCE.json` afterwards; it may hash the source archive, manifest
and transcript but must not contain its own hash. Generate `SHA256SUMS` last.
External release metadata can bind the final commit without embedding a
self-referential commit or file digest in that commit's contents. Preserve the
final-head CI record as execution evidence; an earlier run is not proof that
new source was tested. Do not overwrite an existing release artifact or move
an existing published tag to repair a mismatch.

Before publication, verify that the tag resolves to the selected commit, every
asset matches its recorded digest, the final-head checks passed, and the eight
vectors, two trust files and original manifest remain byte-identical. Link the
result in #3 and use that exact release baseline for the challenge in #2.
This preparation does not perform those publication actions.

## Release-note claim boundaries

The two verifiers and all evidence roles are first-party synthetic work.
The producer, observer and anchor private seeds are deliberately public.
They exercise signatures and configured role binding; they do not establish
a real producer's identity or an independent observer.

The package checks its restricted canonical representation, hashes,
signatures, ordering, pinned scope, RFC 6962 tree and scenario-specific
attempt/outcome relation. Re-signed omission vectors test that selected local
rule. The anchor receipt is a local fixture, not an external anchor or trusted
time service. A record that was never captured cannot be recovered or proved
complete by this package.

No result establishes full VAP/profile conformance, an adopted common format,
organizational independence, capture completeness, production anchoring,
trusted time, regulatory approval or certification. The declared-scope
research kit and Draft #60's cloud/custody experiments use separate contracts.
No compatibility with those formats is claimed.
