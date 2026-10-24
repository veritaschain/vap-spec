# VAP evidence delivery research verifier

**Experimental, unadopted, offline.** Implementation revision 0.1.1.
This implements the 14 synthetic acceptance scenarios in [Draft PR #10](https://github.com/veritaschain/vap-spec/pull/10)
and [the declared-scope proposal](../../proposals/declared-scope-precommit/README.md).
It does not adopt the proposal or establish full VAP conformance.
Merging this research implementation and its discussion draft into `main` does not adopt the extension.
[日本語実行ガイド](RUN-ja.md) · [Machine-readable execution summary](results/summary.json).

The verifier performs real Ed25519 verification, SHA-256 hashing, RFC 8785 canonicalization,
RFC 6962 Merkle inclusion verification, and exact object/evaluation/policy binding checks.
It does not consume `signature_valid` or other input flags as cryptographic verification results.
External receipts and source assurances in the fixtures are **simulated and signed with public test keys**.
Verifying those signatures is not independent proof of time, source completeness, or organizational separation.

## Reproduce

Use Python 3.12 or later. From the repository root:

```sh
python3 -m venv .venv-scope
.venv-scope/bin/python -m pip install -r experiments/declared-scope-verifier/requirements.txt
cd experiments/declared-scope-verifier
../../.venv-scope/bin/python -m scope_verifier run-suite
```

The last command deterministically generates all 14 evidence packages, their explicit evaluator trust
configurations, and evaluation time, then runs **both modes** and compares results with
[acceptance.json](acceptance.json). It prints MATCH/MISMATCH and writes:

- `generated/fixtures/NN.evidence.json`, `NN.trust.json`, and canonical input digests in `manifest.json`.
- `generated/NN.experimental.report.json`: integrity checks, experimental fulfillment, reasons and evidence paths.
- `generated/NN.v1.2.report.json`: only current-spec checks, with no experimental scope result.
- `generated/summary.json`: expected/actual axes, requirement results, differences, toolchain and source provenance.

The suite exits 1 for any expectation mismatch, 2 for invalid/unreadable input, and 0 only when all expectations
match. Matching a negative test is **not** an evidence pass. The suite is not an independent reproduction.

Run the additional cryptographic, malformed-input and semantic regression tests:

```sh
../../.venv-scope/bin/python -m unittest discover -s tests -v
```

Evaluate one package with an explicitly selected mode and evaluator-controlled trust file:

```sh
../../.venv-scope/bin/python -m scope_verifier verify generated/fixtures/02.evidence.json \
  --trust generated/fixtures/02.trust.json --evaluation-time 2000000400 \
  --mode experimental-scope --allow-synthetic --output generated/example.report.json
```

Use `--mode vap-v1.2` for the current-requirement track. That mode ignores the experimental sidecars;
it neither requires a scope declaration nor applies this proposal's fulfillment rules.
The `verify` command exits 0 when it produces a report, including negative or indeterminate reports;
automation must read the **named result axes**, never interpret exit 0 as conformance.

`--allow-synthetic` only works with a trust configuration explicitly marked `synthetic-test-only`.
Without this opt-in, simulated receipts remain indeterminate. No production timestamp/log adapter is
implemented; absence or unsupported proof material cannot become a successful external anchoring result.
The verifier does not contact URLs, discover keys, access services, or read files referenced inside evidence.

## Current requirements versus experiment

The baseline is **VAP v1.2.0 Draft 3**, commit `9465c722be9efae18622ac4f04896bb0e1ea53d7`.
The serialization below is a research adapter, **not** a registered profile or a normative Evidence Pack schema.

| Output | Implemented check and boundary |
| --- | --- |
| INT-001/003 | RFC 8785 canonicalization and SHA-256 hashes of supplied event bodies |
| INT-002 | Distinct supplied event IDs; UUIDv7 is recommended by the framework, not made mandatory here |
| INT-005 | Ed25519 signatures required by this experiment policy; framework event signatures remain SHOULD |
| INT-006 | Signed root, RFC 6962 inclusion, anchored index and receipt authentication; receipt trust is simulation-only |
| INT-008 | Original anchored count, distinct IDs, index positions, endpoints and policy versus actual delivery |
| INT-004 | Profile sequencing semantics beyond Merkle position are unimplemented / indeterminate |
| INT-007 | Operational continuity and fallback assurance are unimplemented / indeterminate |
| INT-009 | Recovery authorization and bounds are unimplemented / indeterminate |
| Experimental only | Pinned scope authority, advance commitment, fixed/derived inventory, source closure, dispositions, equality and notification obligations |

Neither track emits an unconditional PASS: `overall_pass` is null and `full_vap_conformance` is `not_assessed`.
In case 02, all **supplied objects** can verify while INT-008 fails and experimental fulfillment is `not_met`.
In case 09, a permitted hidden-content commitment satisfies its narrow experimental obligation while INT-008
still fails for full batch delivery. In case 03, an altered payload makes integrity fail and prevents a favorable
INT-008 result even when the claimed IDs and count have not changed.

## Experimental adapter contract

Adapter identifier: `vap-evidence-research-adapter/1`. All JSON inputs are UTF-8; duplicate member names,
nonfinite numbers, unsupported JCS values and unsafe integers are rejected. Files are limited to 32 MiB,
event/index/proof collections to 10,000 entries, and inclusion paths to 64 siblings. Counts and indices must
be nonnegative integers, not booleans. Unsupported structural input returns a structured error.
Role, signer, closure-source and observation-gap lists must be arrays; strings cannot substitute for lists
or authorize roles through substring matching. Obligation identifiers and source/type labels must be strings.

An envelope contains `body`, `algorithm` (Ed25519), `key_id`, and a lowercase hexadecimal 64-byte signature.
The signed message is UTF-8 `vap-evidence-research-adapter/1`, one zero byte, then JCS of the object containing
exactly `algorithm`, `key_id`, and `body`. Each body binds `kind`, `evaluation_id`, and `policy_digest`.
Signatures are domain-separated by the adapter prefix and signed kind; sidecars cannot be substituted across
roles, exercises or policy revisions. Envelope digests are SHA-256 of the **entire JCS envelope**, including
signature. Event hashes are SHA-256 of JCS of the event body. No historical signed bytes are rewritten.

Merkle leaves are SHA-256(`0x00 || JCS(event body)`); nodes are SHA-256(`0x01 || left || right`). The tree splits
at the largest power of two strictly smaller than its size, as in RFC 6962. It does not duplicate odd leaves.
Sibling paths run from leaf to root and must have the exact length implied by the index and tree size.
The signed anchor binds the root, count, first/last IDs, policy and digest of the complete ordered batch index.
That authenticated index binds each ID/type/source to its leaf hash, including hidden payload commitments.
This extra index is a local adapter choice, not an amendment to the framework's abstract AnchorRecord.

The trust file is an **explicit evaluator input outside the package**: keys and allowed roles, evaluation ID,
policy digest, and (experimental mode only) approved scope envelope digest. The generator supplies known test
trust files for reproduction; those are not automatically appropriate for any other evaluation. Key rotation,
revocation, certificates and production identity governance are not implemented.

The approved scope records systems, operations, classes, exclusions, source boundary and controllers, exact
configuration, interval, cutoff, deadlines, rules and relationships. An externally pinned digest represents
the evaluator's approval of that exact scope. This prototype does not prove how the approval was obtained.

- **Fixed:** the scope commits SHA-256/JCS of the ordered obligation enumeration before the cutoff.
- **Derived:** the scope commits `explicit-obligations-v1`, source, configuration and closure rule first.
  Later signed closure binds `source_records`; the verifier extracts each explicit `obligation` and compares
  the complete ordered result. Future events are not described as pre-enumerated. This deliberately small rule
  does not infer obligations from arbitrary logs or implement other profiles' derivation rules.
  Unclosed or gapped sources do not establish a complete expected-set count. Unsupported derivation rules
  leave that set unresolved while independently pinned individual obligations are still assessed.
- **Individual obligations:** `scope.individually_required` always augments the authenticated expected set,
  including when that set is available. Identical obligations with the same ID are counted once; conflicting
  definitions are rejected. A resolved expected count includes this union; it stays null if the full set is unknown.
- **Closure:** the authorized synthetic inventory authority signs the exact source, end, configuration,
  expected enumeration and closure time, and reports observation gaps. This is a test assumption about one
  synthetic boundary, not a cryptographic proof that no unobserved real-world action existed.
- **Delivery:** the signed final manifest binds scope, original anchor, actual delivered events/commitment proofs
  and per-ID states. `included`, `withheld`, `unavailable` and `unaccounted` remain distinct. Explicit dispositions
  are attributable submitter claims; full evidence withholding can establish a delivery-policy failure, not
  whether an underlying action occurred. Payload correctness is never inferred from a hidden commitment.
- **Timing:** accepted time plus uncertainty must be no later than the prior cutoff. A late receipt alone is
  indeterminate. Only a valid simulated closed register bound to that receipt, scope and agreed register can
  establish late **first** qualifying acceptance. The register's closure is a synthetic trusted assertion.
- **Multiplicity:** exactly one record per enumerated obligation. Retries, cancellations and timeouts must be
  explicitly represented as separate policy obligations; no universal attempt/outcome bijection is inferred.
- **Relationships:** only `payload-value-equality-v1` is implemented. Conflicting authenticated observations
  establish a violation of the equality rule, not which observation describes reality.
  Values are compared by their JCS representation, so JSON booleans and numbers remain distinct.
- **Notifications:** trigger, recipient, deadline and exact stage are checked. Attempted, transport accepted,
  endpoint delivered and human acknowledged are distinct. Missing receipt plus unclosed notification source is
  indeterminate. Explicit full-receipt withholding after final deadline is a delivery violation.
- **Amendments:** an unapproved changed scope fails its pinned binding. Even a newly approved revision is
  marked unresolved because amendment evaluation is unimplemented. Original conclusions cannot be silently
  overwritten. Assess original and restated scopes separately before adding amendment support.

## Aggregation and diagnostics

Integrity aggregates **failed before indeterminate before verified**. Individual failed and indeterminate
checks remain in `integrity.checks`; a failure never removes unresolved checks. This is a local implementation
rule for the experiment, not an adopted framework change. Missing signatures or trust paths are indeterminate;
an actual signature/hash/binding mismatch is failed. Semantic batch completeness remains separately reported.
Each requirement aggregates only its own dependencies: an unrelated event-signature failure does not turn
an unresolved external anchor into an INT-006 failure. Unsupported time semantics cannot establish a deadline violation.

Scope fulfillment prioritizes a validated violation (`not_met`), then unresolved required prerequisites
(`indeterminate`), then `met` within the declared boundary. Independent signed evidence can prove withholding
even if another record is corrupt or the full expected inventory is unavailable. Such violations retain their
evidence dependencies and unresolved questions. A cryptographic error is not by itself a scope violation.
`inventory_accounted_for` describes enumeration of dispositions, not fulfillment of full-record obligations.
No output asserts that notification or any other underlying action did not occur.

## Recorded execution and remaining work

[results/summary.json](results/summary.json) records the tested implementation/fixture commit, source digest,
fixture digests, Python and dependency versions, evaluation time, expected versus actual results and differences.
The full synthetic packages, evaluator configurations and detailed reports are in the adjacent execution
archive. The recording commit may follow the tested code commit; use the source digest to compare code.
GitHub Actions repeats the suite and regression tests on Python 3.12 and 3.14 and retains detailed artifacts.

This work is an internally executed synthetic experiment. Independent reproduction, institutional observer
assurance, production time services, arbitrary profiles, erasure/recovery/continuity handling, amendment
assessment and a reviewed interoperable wire contract remain unestablished. Existing K3 and normative spec
files are unchanged. The formal proposal number and target release remain unassigned/undecided.

Implementation references: [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785),
[RFC 6962 §2.1](https://www.rfc-editor.org/rfc/rfc6962.html#section-2.1),
[cryptography Ed25519 API](https://cryptography.io/en/latest/hazmat/primitives/asymmetric/ed25519/).
The repository's existing [CC BY 4.0 license](../../LICENSE) applies; this change does not relicense the repository.
