# Fixed research reproduction kit — 2026-10-24

**Experimental and unadopted. Independent third-party reproduction has not been
established.** This is a research distribution, separate from specification
releases. No current VAP v1.2 requirements, existing verifier, gate, OS experiment
or K3 conditions are changed by this distribution.

## Download and verify

[Download the kit and complete preserved execution evidence](https://github.com/veritaschain/vap-spec/releases/tag/research-kit-b1af0dc-20261024).
The release contains the original tested ZIP, full internal CI evidence archive,
`SHA256SUMS`, `preservation.json` and `ARCHIVE-README.md`.

| File | SHA-256 |
| --- | --- |
| `kit-b1af0dc.zip` | `9e7efa74372ec08434f2d70b2a23a41a416fb64dfa99a24c13bbca255d1c0bb9` |
| `vap-research-evidence-b1af0dc-20261024.zip` | `f2e82ed77d1a789a31e6b09f1493476db98417b8578b80c489fdea0fdba5a153` |

On Linux, download all five assets into the same directory and run
`sha256sum --check SHA256SUMS` before extraction. The release checksums are also
preserved [in this repository](SHA256SUMS). A matching checksum establishes byte
consistency with the supplied manifest, not an evaluator's identity or independence.

## Fixed versions and historical evidence

| Purpose | Version or original record |
| --- | --- |
| Merged kit source | `b1af0dc9d368b466bf74e7c1b2a6808fb41949ae` |
| Reproduced verifier, gate and OS implementation | `c8ccf972196a16d11429a478f4918a08fe27bb73` |
| Final kit CI head | `69142d98ce4bc1d8b54fddadd7995902320eea16` — [run 40059665558](https://github.com/veritaschain/vap-spec/actions/runs/40059665558) |
| Corrected implementation CI head | `3c1cad051291dd2308d85419bd2d593c6ae1906f` — [run 40059420561](https://github.com/veritaschain/vap-spec/actions/runs/40059420561) |

The two runs produced byte-identical kit ZIPs but separate execution records.
Both original artifact ZIPs, complete workflow logs and captured GitHub metadata
are retained unedited. Each artifact includes 90 output files plus its manifest.
The archive also includes a Git bundle retaining both fixed source revisions,
and separate preservation-check records. See the [machine-readable inventory](preservation.json).

The internal validation reports 27 package tests plus 138 existing tests, with
matching expectations for 16 OS, 15 gate and 14 verifier cases. Preservation checks
verified both complete inventories and rechecked both saved outputs with the
existing kit using Python 3.14.3 and locked dependencies. These preservation checks
are **not new OS executions or independent reproduction**. All ten packaged kit
files also match the merged kit source at `b1af0dc`.

The original Actions artifacts expire on 2026-11-23. These release assets are
stored separately from that 30-day retention. A byte-matched private Google Drive
backup and local archival copy are also retained by the maintainer. Copies may
still be deleted or become unavailable; this is not an immutable-storage claim.
The archive retains the tested distribution and historical evidence, rather than
relying on regeneration. It does not include the host OS, Docker, runtime base
image or external Python packages and is not a hermetic execution environment.

## Run and report

- [Fixed English instructions](https://github.com/veritaschain/vap-spec/blob/b1af0dc9d368b466bf74e7c1b2a6808fb41949ae/reproduction/os-isolation/README.md)
- [固定版の日本語手順](https://github.com/veritaschain/vap-spec/blob/b1af0dc9d368b466bf74e7c1b2a6808fb41949ae/reproduction/os-isolation/RUN-ja.md)
- [Existing report format and retention instructions](https://github.com/veritaschain/vap-spec/blob/b1af0dc9d368b466bf74e7c1b2a6808fb41949ae/reproduction/os-isolation/REPORTING.md)
- [Proposed evaluation and separate publication-consent terms](EVALUATION-TERMS.md)
- [Result-handling operating note](RESULT-HANDLING.md)

The terms are a proposal, not an evaluator's acceptance. Fresh execution,
assistance, independence and publication permissions must be assessed separately.
Keep the machine output's `independence: not_assessed` unchanged.

## Publication review and corrections

The originals and nested archives were reviewed for private-key blocks, provider
tokens, credentials and unnecessary personal contact details. Credential-looking
fields were synthetic authorization checks, and workflow authentication values
were already masked by GitHub. Fixture contacts use `example.invalid`. No unmasked
production credential or unnecessary private contact detail was identified in the
reviewed material. The public source bundle retains public Git author metadata.
This review does not guarantee detection of every possible secret pattern.

No new redactions were applied. Preserve any future edited public copy separately
from its original with a change record. Never silently replace these ZIPs or
historical results: corrections require a new identifier, checksum and advisory
linked to the affected version.
