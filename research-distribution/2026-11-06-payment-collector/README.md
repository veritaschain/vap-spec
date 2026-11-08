# Preserved payment collector evidence — 2026-11-06

**Experimental and unadopted. Independent reproduction, independent custody and
VAP conformance are not established.** [日本語](README-ja.md)

This distribution preserves the original public output of one completed
[payment collector pilot](../../experiments/payment-collector-pilot/README.md)
CI run, together with its source subset, captured GitHub records and an offline
recheck. The original Actions artifact has a 30-day lifetime. Keeping these bytes
in repository history makes this selected run available separately from that
expiry; it does not create immutable storage or extend retention for other runs.

## Fixed identity and original bytes

| Item | Preserved identity |
| --- | --- |
| Source commit | [`ce9c968951c0c92a3b5cf9d5a9a587506f8a700d`](https://github.com/veritaschain/vap-spec/tree/ce9c968951c0c92a3b5cf9d5a9a587506f8a700d) |
| Original workflow | [Run 42203872859, attempt 1](https://github.com/veritaschain/vap-spec/actions/runs/42203872859), `push` on `main`, successful |
| Original job | [`collect-and-recover`, 127845525323](https://github.com/veritaschain/vap-spec/actions/runs/42203872859/job/127845525323), successful |
| Original artifact | `payment-collector-public-demo`, ID `13495277522` |
| Created / scheduled expiry | `2026-11-06T10:36:34Z` / `2026-12-06T10:36:33Z` |
| Preserved ZIP | [original/payment-collector-public-demo-13495277522.zip](original/payment-collector-public-demo-13495277522.zip), 84,274 bytes |
| ZIP SHA-256 | `b93f40c33d1ae946d25f881527a4b2fcf32b704b745e7980aed0182060923bca` |

The ZIP is the downloaded original, with no repacking or redaction. Its digest
matches both the captured GitHub artifact metadata and the original job's upload
log. The two files in `original/` are also provided uncompressed for inspection:
they are byte-identical to the corresponding ZIP members, including their final
newlines. No fresh demo output replaces the historical output.

| ZIP member / extracted file | Bytes | SHA-256 |
| --- | ---: | --- |
| [summary.json](original/summary.json) | 28,056 | `4d8e01c31c5e02754d6d92ed04bb13ffc624c9ea3a82766d448e654eff9eca49` |
| [evidence-bundle.json](original/evidence-bundle.json) | 871,431 | `48f50aa31933719643c9b9049c583cf323b6d490a3943b2fd75bb3362d79acff` |

## Contents and provenance

| Location | Purpose and boundary |
| --- | --- |
| `original/` | Original ZIP and its two complete public members, including original signed evidence bytes encoded as hex |
| `github/` | Captured run, job and artifact metadata, plus the complete decoded log of the selected job |
| `source/` | Ten byte-identical files from the pinned commit: producer and verifier dependencies, original requirement files, workflow and license; this is not a full repository snapshot |
| [preservation.json](preservation.json) | Machine-readable identities, byte counts, SHA-256 and Git blob IDs, original environment, validation scope and limits |
| [SHA256SUMS](SHA256SUMS) | Every file in this distribution except the manifest itself |
| [verify.py](verify.py) | Added preservation recheck using the preserved verifier functions; it does not run the payment demo |
| [requirements-recheck.txt](requirements-recheck.txt) | Dependency versions recorded in the original job; package binaries are not included |

The GitHub JSON and log are the connector-returned decoded text, saved as UTF-8.
They are not raw HTTP transport bytes or an independently signed provenance
attestation. The source files were retrieved from the pinned Git revision and
checked against their Git blob IDs. The local archive recheck checks those saved
IDs and hashes; it does not contact GitHub to authenticate the original commit.

Trust a separately obtained distribution commit or checksum before using this
package. A manifest and evidence changed together can agree with each other.
Public keys inside the original bundle are declarations by the same controller,
not an external source of identity or trust.

## Recheck without running services

Copy the entire directory, including `source/.github/`, before checking it. Keep
the virtual environment and any recheck output **outside** this directory: the
checker rejects unexpected files as well as missing or changed files. With
Python 3.12, run the following from the repository root:

```sh
VAP_PAYMENT_ARCHIVE=research-distribution/2026-11-06-payment-collector
(cd "$VAP_PAYMENT_ARCHIVE" && sha256sum --check SHA256SUMS)
python3.12 -m venv /tmp/vap-payment-recheck-venv
/tmp/vap-payment-recheck-venv/bin/python -m pip install -r "$VAP_PAYMENT_ARCHIVE/requirements-recheck.txt"
/tmp/vap-payment-recheck-venv/bin/python "$VAP_PAYMENT_ARCHIVE/verify.py"
/tmp/vap-payment-recheck-venv/bin/python -O "$VAP_PAYMENT_ARCHIVE/verify.py"
```

The dependency installation may use the network. Prepare it before disconnecting
or use an already prepared environment with these dependencies. The two rechecks
need only the preserved directory and installed Python dependencies; they do not
need the rest of the repository, Git, GitHub access, a service database, private
keys, sockets or subprocesses. An audit hook rejects accidental socket creation
and subprocess execution during verification. It is not an OS security boundary.

Successful verification exits zero and prints `PRESERVED_EVIDENCE_RECHECKED`, with
5 scenarios, 13 stages, 5 original admission records, 3 provider receipts and
10 saved custody observations rechecked. A failed check exits nonzero with
`RECHECK_FAILED`. The checks cover:

- Complete file inventory and checksums; original ZIP digest and member equality;
  source file hashes and blob IDs; captured run, job, artifact and upload-log binding.
- Historical admission signatures and request bindings, using the original
  embedded synthetic policy, status and identity map.
- Original provider signatures under the controller-declared provider public pin.
- Original collector ACK and readback signatures, exact retained evidence bytes,
  recorded challenges, identities and epochs under the declared collector pin.
- The original five scenario summaries and their 13 stage views, including the
  separation between payment outcomes, original prerequisites and later custody.

Reading a saved challenge response again is a **historical recheck**, not a fresh
collector query. `fresh_service_execution`, `independent_trust_established`,
`present_retention_established`, `VAP_conformance_established` and
`production_readiness_established` remain `false`.

## Original environment and validation scope

The preserved job log records Ubuntu 24.04.5 LTS, runner image
`ubuntu-24.04` version `20261101.360.1`, Actions runner `2.338.2`, CPython `3.12.16`,
`cryptography==50.0.2`, `cffi==2.1.1` and `pycparser==3.12`.

That original job passed 25 collector tests normally and repeated the same 25
under optimized Python, then passed 20 authorization and 28 runtime tests:
**73 unique tests**, not 98. It also produced the five-scenario, 13-stage public
demo preserved here. The separate 57-test retrospective verifier and other
workflows are not part of this selected job's evidence.

The offline recheck does not re-execute service outages, process death, locks,
network exchanges, balances or recovery. It checks the saved evidence using
the pinned implementation. All original processes and keys were controlled by
one operator and host user. The provider still accepted its local bearer
credential through routes outside the controlled wrapper. Historical admission
does not assert current authorization; local stage labels and collection ACKs
do not independently prove timing relative to a payment effect.

The host OS, package binaries, private service configuration and databases are
not preserved. This is not a hermetic execution environment, complete PAY-01 to
PAY-08 acceptance, continuous retention evidence, independent reproduction or a
production-readiness result. The archive adds no VAP requirement or specification
release and retains the pilot's unadopted status.

## Publication review and corrections

The two original members, their nested decoded JSON evidence and the captured
job log were inspected for private-key blocks, unmasked provider or GitHub
credentials and private contact details. Credential-named evidence fields contain
synthetic identifiers. GitHub's workflow authentication value was already masked.
No unmasked production secret or private contact detail was identified in the
reviewed material; this does not guarantee every possible secret pattern was
detected. Captured metadata retains public repository and account attribution.

No additional redactions were applied. Preserve these original bytes and their
identity. If a correction is needed, publish a separately identified distribution
with new checksums and an advisory linking back to this version; do not silently
replace the original ZIP, evidence, source snapshot or historical results.
