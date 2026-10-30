# VCP v1.2 / VAP v1.2 integrity-layer observations

**Research observation, unadopted; no formal proposal number.** These observations
are not a normative amendment, an adopted erratum, a conformance verdict or a
certification result. Existing specifications, implementations, research kits,
fixed tags, DOC-SYNC and K3 remain unchanged by this directory.

[Probe](probe.py) · [Recorded output](results/probe-output.json)

This is a separate reconstruction from pinned public sources. The earlier local
probe reported as commit `1b88644` was unavailable in the publishing environment.
This record does not claim to execute or reproduce that commit by identity. It
retains observation identifiers P1–P9 for comparison with the supplied review,
while correcting and narrowing claims as described below.

## Baselines and provenance

| Source | Pinned revision | File SHA-256 |
| --- | --- | --- |
| [VCP specification](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/spec/v1.2/VCP-Specification-v1_2_en.md) | `b23acb266f88df81d960d36d58fb64ceaa0dd5ed` (v1.2.0) | `ce94399bde111c8b805d3804fad2e6d61cab2f1839533d5009e94e812d15a942` |
| [VCP quickstart](https://github.com/veritaschain/vcp-spec/blob/b23acb266f88df81d960d36d58fb64ceaa0dd5ed/examples/python/quickstart.py) | Same VCP revision | `7f8351344667c349bd7d1c7897f388459f2548e58525e0c63d8b731b57279881` |
| [VAP Draft 3](https://github.com/veritaschain/vap-spec/blob/277b37930be858c0832708a8696d6f213b1fe7bb/spec/v1.2/VAP_Framework_Specification.md) | `277b37930be858c0832708a8696d6f213b1fe7bb` | `dbe2439d6d138929b48697cd0545a5c8324059ab032732b9a9122f993fde9f48` |
| [Reference verifier, self-described as v1.1](https://github.com/veritaschain/vcp-rta-reference/blob/3d359dce3be479632d41e4dee74c7f102766e202/tools/verifier/vcp_verifier.py) | `3d359dce3be479632d41e4dee74c7f102766e202` | `6d9fb91f268c0af1cf898a0e1a608852825d46952d13a544411634e91518c959` |

VAP's specification bytes match the supplied review's earlier `418bff4` baseline.
The probe reads Git objects at the pinned revisions, not the working-tree files.
The output also records hashes of all 40 pinned valid fixtures. The reference
verifier file is checked against its pinned hash before extracting functions.
The original Draft 2 and VSO-VAP-RD-001 files and their hashes are **not available**
for this review; no original wording or approval is inferred for them.

## Observations and measured scope

| ID | Observation | Result / limitation |
| --- | --- | --- |
| P1 | VCP §6.2.1 requires RFC 6962 construction, but the example duplicates an odd node. Both RFC 6962 and RFC 9162 define a recursive split based on leaf count. | Of sizes 1–16 tested, roots differ at 3, 5, 6, 7, 9–15. This is not merely failure to follow a newer RFC. |
| P2 | VCP §6.2.3 omits a nonexistent sibling while §6.2.1 duplicates it. | 19 of 136 generated inclusion paths fail against the example's own root under a fold using its hash rules. |
| P3 | The quickstart function starts from the raw event hash and omits leaf/internal-node prefixes. | 0 of the same 136 proofs are accepted. This is an example-code finding, not a test of every VCP implementation. |
| P4 | Odd-node duplication allows `[e0,e1,e2]` and `[e0,e1,e2,e2]` to share a root. | Same VCP-example root; different RFC roots for this pair. |
| P5 | VCP's ordinary leaf is `H(0x00 \|\| H(JCS(Header) \|\| JCS(Payload)))`; VAP Mechanism B says `H(0x00 \|\| canonical(E))`. Mechanism A additionally includes `prev_hash`. | A synthetic Header/Payload-object reading of E produces different leaves. This illustrates the missing mapping; it does not establish a unique normative definition of E or equate VAP A with every VCP hash form. |
| P6 | The VCP §6.3.1 example signs root bytes. Changing count, last ID and policy in the accompanying record leaves those signed bytes unchanged. | Real synthetic Ed25519 verification still succeeds. For an 8-leaf root presented as size 6, size-free folds and generic depth checks accept indices 0–5; strict size-6 verification rejects 4–5 but accepts 0–3. |
| P7 | The reference verifier uses `json.dumps(..., sort_keys=True)` for Header and Payload. | On the supplied synthetic sample, it rejects the JCS-based hash and accepts the `json.dumps` hash; its 3-leaf root follows odd duplication. The tool identifies itself as **v1.1**, not a v1.2 production verifier. |
| P8 | Python `rfc8785==0.1.4` rejects the pinned fixture headers with Python integer TimestampInt values. | 40/40 rejected; **40/40 timestamp values are nevertheless exactly representable in binary64**. Diagnostic equal-value float inputs are accepted for all 40. An adjacent nonrepresentable integer demonstrates the separate general precision risk. |
| P9 | Several markers alleged to originate in Draft 2 are absent in public Draft 3. | Public text search only. **Prior approval, normative adoption and historical regression remain unverified** without Draft 2 and RD-001 originals. |

P6 concerns the published root-only signature procedure and its synthetic
presentation, not an implementation that additionally authenticates the complete
AnchorRecord. Size-dependent verification alone does not replace authenticated
count/range/policy bindings: some indices in the wrong-size example still pass.
No production external timestamp or transparency service is used by this probe.

P8 distinguishes a library's integer-input restriction from the RFC number
model. It does **not** show that every integer above 2^53 is unrepresentable or
that these 40 fixtures cannot be canonicalized by any RFC 8785 implementation.
For example, `1791504000000000001` rounds to `1791504000000000000` in binary64,
whereas the fixture values tested are exact. The diagnostic checks equality
before converting and is not a recommended production workaround. VAP §7.2's
numeric-string requirement and §7.1's int64 schema notation also need explicit
mapping; no schema migration is adopted here.

P9's missing markers include EH-001–006, PRV-001–003, `anchor_sequence`,
`prev_anchor_record_hash`, `VerifyChain` and RD-001. The public text still contains
“MiFID II/III”. Missing identifiers do not by themselves prove missing semantics,
and neither observation proves that an approved earlier draft was lost. The
suggested same-name-file mix-up is unverified. Reconstruction of unavailable
text must not be represented as restoration of an authenticated original.

## Reproduce and compare

Python 3.12 or later and Git are required; the recorded run used Python 3.14.3,
`rfc8785==0.1.4` and `cryptography==50.0.2`. No Docker or privileged execution is
needed. Install the existing pinned research dependencies in a fresh environment:

```sh
python3 -m venv .venv-align
.venv-align/bin/python -m pip install -r experiments/declared-scope-verifier/requirements.txt
```

From a checkout of this PR, acquire public inputs at the pinned revisions (use a
new directory name if the example sibling path already exists):

```sh
git clone --no-checkout https://github.com/veritaschain/vcp-spec.git ../vcp-spec-alignment-input
git -C ../vcp-spec-alignment-input fetch origin b23acb266f88df81d960d36d58fb64ceaa0dd5ed
git fetch origin 277b37930be858c0832708a8696d6f213b1fe7bb
curl --fail --location https://raw.githubusercontent.com/veritaschain/vcp-rta-reference/3d359dce3be479632d41e4dee74c7f102766e202/tools/verifier/vcp_verifier.py --output /tmp/vcp-rta-alignment-verifier.py
.venv-align/bin/python -I experiments/vcp-v1.2-integrity-alignment/probe.py \
  --vcp-spec ../vcp-spec-alignment-input --vap-spec . \
  --rta-verifier /tmp/vcp-rta-alignment-verifier.py \
  --check experiments/vcp-v1.2-integrity-alignment/results/probe-output.json \
  --output /tmp/vcp-vap-alignment-probe-output.json
```

The probe itself performs no network access. It extracts only named, reviewed
pure functions from hash-checked sources; it does not run their module entry
points or networking code. Fixtures are read as data. The synthetic signing key
is public test material and must never be used for real evidence.

`--check` compares every saved field except the separately recorded `environment`
object. Environment differences should be reported even when observations match;
the probe requires rfc8785 0.1.4. Missing sources, wrong hashes or result
differences return nonzero. Duplicate saved-result members are rejected, and
comparison distinguishes JSON booleans from numbers. Exit zero means the observation run completed (and
matched when `--check` is used), **not** VCP/VAP conformance. Without `--check`,
the probe reports observations without asserting the saved counts as an oracle.

The local RFC comparator has 2,080 positive inclusions over tree sizes 1–64, with
modified-entry, surplus-path and nonempty truncated-path negative controls. The
Ed25519 checks include an altered-root rejection control. These are controls of
the probe, not additional product regression tests or independent reproduction.
Publication checks also rejected a modified source file, a changed saved count,
a boolean changed to a number, and a duplicate member in the saved output.

## Final internal review — 24 October 2026

GitHub's Markdown rendering truncated P5 at the unescaped concatenation pipes,
hiding part of the formula and its limitation. Escaping those table-cell pipes
restores the complete three-column row; GitHub's renderer was used to confirm
the repair. The probe and saved observations were not changed by this repair.

Fresh local environments, using a newly cloned VCP repository and a fresh
download of the pinned reference source, completed the documented comparison:

| Runtime | Dependencies | Outcome |
| --- | --- | --- |
| Python 3.12.14 | rfc8785 0.1.4; cryptography 50.0.2 | All non-environment fields match the saved report |
| Python 3.14.3 | Same | All non-environment fields match; output bytes match the saved report |

Seven negative checks also returned nonzero without writing a result: altered
count, boolean replaced by number, extra claim, duplicate member, malformed
JSON, changed reference-source bytes, and missing reference source. The 2,080
inclusion controls and signature controls run inside each complete probe run.

Reviewed probe SHA-256:
`88ffef24994da7640c3ca4b38aa3cce900c401d9ae6f7bfa79f038cc7c7c5e4e`.
Saved/Python 3.14 output SHA-256:
`1a97314b4fe3ce0b4c9d401588cf2b1a1a9cacc46c175bec42c09c87f5ba594e`.
Python 3.12 output SHA-256 (environment metadata differs):
`6c238f11e7f8665f1b94d076ebe699f5dde720f815aa36def153486386365444`.

These are local internal checks, not GitHub CI or independent third-party
reproduction. No remaining blocker was identified within this observation-only
scope. Merging the research record does not adopt its proposed changes or
resolve the documented VCP/VAP discrepancies or the unverified Draft 2 history.

## Existing experiments and external evaluation

The current-requirement track of the declared-scope verifier performs real
cryptographic checks over a **research adapter** and explicitly leaves full VAP
conformance unassessed. It does not consume native VCP events/AnchorRecords.
Lack of that interoperability does not mean the implementation is empty.

Evidence-set verification and pre-execution/OS isolation are separate research
questions. For a first evaluation focused on submitted evidence, use the offline
declared-scope verifier with its exact source and assumptions disclosed. Native
VCP verification, full conformance and endorsement of the specifications are
outside that scope. The existing OS kit remains a separate, explicitly requested
experiment; its ZIP and existing results are not replaced. A revised external
request must be communicated and agreed separately, not silently substituted.

No K3 fixtures were examined. Potential effects depend on which hashing, path
generation, signing and numeric-processing code was actually used. This record
does not invalidate K3 results or alter its fixed inputs, criteria or progress.
CAP mapping impacts likewise require a separate review against pinned text;
they are not experimentally established by this probe.

## Separate decisions; none enacted here

1. Obtain Draft 2 and RD-001 originals, record hashes and item-level dispositions,
   distinguish accepted draft fixes from normative adoption, and preserve later
   valid changes before preparing any revised draft.
2. Record the published RFC/code contradiction as a proposed technical erratum.
   Treat changes to signed bytes, schema and historical root interpretation as
   explicit versioned migration questions, not an assumed compatible patch.
3. Prepare a separately reviewed correction to the unconditional VCP v1.2
   “Full (reference profile)” statement. Proposed wording: “Mapping required and
   outstanding. Known integrity-layer discrepancies are under review; full
   conformance has not been established.” This directory does not edit that row.
4. Prepare K3 communication as unresolved version-impact information, with any
   additional test results separate from the existing evaluation. No message is
   sent by this experiment.

Experimental extensions remain unadopted. Internal recomputation is not
independent third-party reproduction. No production implementation, customer
system, regulatory acceptance or certification has been evaluated here.

References: [RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962.html#section-2.1),
[RFC 9162 §2.1](https://www.rfc-editor.org/rfc/rfc9162.html#section-2.1),
[RFC 8785 §3.1](https://www.rfc-editor.org/rfc/rfc8785.html#section-3.1).
Repository licensing applies; this observation does not change licensing terms.
