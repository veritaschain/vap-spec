# Incident recheck kit — development review

This is an internal architecture and adversarial test review. The boundary tests
were authored separately from the archive and worker implementations within the
same development team. This does not establish third-party reproduction,
independent evaluation, certification or VAP conformance.

## Reviewed operation

The kit preserves the original public Python 3.12 CI captures for three separate
synthetic pilots: 17 upload, 18 publication and 18 erasure cases. It packages the
original JSON bytes with the matching source, requirements declaration, capture
provenance and fixed file inventory. The workers invoke only the existing
`verify_exports` functions. They do not run pilot tests or scenario generators,
make a new upload, publish an article, or erase an object.

The expected archive digest comes from outside the candidate archive. Inspection
checks raw bytes and the narrow container representation, but it does not by
itself authorize the enclosed source or verify the captured observations. Before
staging any files, the runner additionally compares every archived source file
with the trusted local source tree, checks the original pilot source lock, and
checks the fixed capture provenance and original file hashes.

This separation is material: a malicious archive can contain a consistent
manifest and a changed verifier. Recomputing its internal hashes does not make
that verifier eligible for execution. The boundary tests deliberately supply a
matching external hash for such altered test archives, isolating the additional
trusted-source check from the outer checksum check.

## Archive and path boundary

The archive reader implements only the emitted, bounded `ZIP_STORED` grammar.
It checks the physical archive and external digest before parsing entries. It
requires the complete fixed inventory, sorted unique ASCII relative paths,
regular-file metadata, matching local and central headers, nonoverlapping
contiguous extents, CRCs, raw member hashes and a canonical manifest. Compression,
encryption, ZIP64, multidisk structures, symlinks, directory entries, comments,
extra fields, unknown members and trailing bytes are outside the accepted format.

The bounds are 16 MiB for the archive, 4 MiB for a member, 256 entries, 12 MiB for
payload bytes and 128 KiB for the central directory. Inspection returns owned
bytes; it does not extract files or import their code. The runner stages the
fully checked bytes only in a new private temporary directory. Existing caller
directories are not used as an extraction destination.

The original verifier manifests legitimately use paths such as
`../incident-evidence-assessor/...` and `../../.github/...`. Those references are
resolved within the known repository topology and matched against the trusted
source lock. They are never accepted verbatim as archive paths. Conflicting
shared source files cannot silently select a newer implementation.

## Original evidence and portable source

The original summary and case bytes are copied unchanged. This is stricter than
comparing parsed JSON alone: the upload verifier's case digest uses JCS of parsed
content, whereas the publication and erasure verifiers use raw file hashes. A
whitespace-only change can preserve the upload case's parsed value while no
longer being the exact captured file. The kit's locked raw-file provenance rejects
that substitution, including when an attacker rewrites the supplied provenance.

The source lock also commits to the raw provenance record. Architecture review
identified that comparing provenance only with a checkout-relative snapshot file
would make a delivered `source/` plus `evidence/` layout depend on an unbundled
original directory. The implementation instead validates the provenance digest
against the trusted lock and supports the explicit sibling `evidence/` layout.
This keeps the original capture binding while allowing a separately validated
delivery to operate outside the original checkout.

The portable bootstrap still requires reviewed source or an externally obtained
trusted archive hash. Running an unverified included launcher and accepting its
own hash would not authenticate it. A source-tree byte match is not a verification
of GitHub identity, the author's independence, or the truth of the original
observations.

## Worker execution boundary

Each pilot runs in a fresh isolated `-I -B` interpreter with a fixed module
mapping. The subprocess ignores `PYTHONPATH` and user site packages, suppresses
bytecode output, and has no candidate-selected module or entrypoint. Source
requirements are checked again before starting the worker. The original verifier
still checks its own source manifest, case inventory, signatures, bindings and
saved findings.

A Python audit hook is installed before verifier and dependency imports. It
refuses representative socket, process, write and filesystem mutation events.
Denied events remain recorded, so catching a denial inside imported code cannot
turn that worker into a successful recheck. This is an in-process guard, not an
OS sandbox; native dependencies, the interpreter and host controller remain
trusted external inputs.

The parent reads stdout and stderr incrementally with a 64 KiB limit for each
stream and a bounded worker lifetime. It requires zero exit status, no unexpected
diagnostics and the exact structured result. Counts, source identity, dependency
versions and `actions_reexecuted: false` must match the selected pilot. A failed
worker prevents a final success report rather than producing a promoted partial
result.

The runtime checks both installed distribution and loaded-module versions for
cryptography 50.0.2, rfc8785 0.1.4, cffi 2.1.1 and pycparser 3.12. It does not
download or install dependencies. The kit does not vendor or hash-lock those
binary distributions, so version checks do not make it a hermetic environment.

## Separately authored boundary tests

[test_boundary.py](tests/test_boundary.py) contains six executed methods:

1. A changed assessor plus a rewritten internal source hash and archive manifest
   is refused before temporary staging or a worker call. Its execution sentinel
   remains absent.
2. A replacement packaged worker with a success-looking output and an execution
   sentinel is refused at the same boundary.
3. A reserialized original upload capture is rejected, both with the original
   provenance and with matching attacker-rewritten provenance hashes.
4. Changed capture-origin metadata and an updated archived provenance commitment
   cannot replace the trusted original record.
5. A complete real recheck still verifies all 53 captured cases while hostile
   `PYTHONPATH` modules and `sitecustomize.py` attempt to introduce code. Their
   sentinel remains absent and the limited assurance fields remain unchanged.
6. A fresh guarded child actually attempts write-open, update-open, `os.open`,
   unlink, rename, mkdir, chmod, socket creation and process creation. All nine
   operations are refused and recorded. Read-only access still works; the
   original file remains unchanged and no created or renamed target appears.

The focused boundary run completed **6 of 6 methods**, without skips or
ResourceWarning output, using the matching pinned dependency environment. Its
positive test rechecked **17 + 18 + 18 = 53 original captured cases**. These are
executed checks, not inferred from the acceptance catalogue.

Separate archive tests cover the byte grammar, limits, path attacks and
deterministic encoding. Separate runner tests cover malformed successful output,
nonzero exits, diagnostics, output flooding, timeouts, dependency mismatches and
staging cleanup.

## Integrated development checkpoint

The final local `record_run` checkpoint on Python **3.12.14** completed **29 of 29
methods**, with zero failures, errors, skips or unraisable finalizer exceptions:

| Test group | Methods passed |
| --- | ---: |
| Archive grammar and limits | 10 |
| Worker execution and result contract | 9 |
| Separately authored trust-boundary checks | 6 |
| CLI, standalone delivery and bounded JSON parsing | 4 |
| **Total** | **29** |

All **53 original captured cases** rechecked. The standalone delivery test staged
the verified payload outside the original checkout, refused attempts to access
that checkout through an audit hook, and successfully verified the captures and
rebuilt an identical archive. The local execution source manifest remained
unchanged during the recorded run.

The final checkpoint includes rejection of JSON numeric overflow and the
standalone instruction-link corrections. Its **136-file** execution source
manifest has aggregate SHA-256
`925ee33f4a3d5bd9c8babdd430a9329e07a20e6c5eb8cb20d5db23078e81e5ec`.
The deterministic archive contains **2,902,071 bytes**, with SHA-256
`06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f`.

These are internal development results. The final CI record separately identifies
its exact source and archive hashes and Python matrix executions; this review
does not preclaim those runs or independent reproduction. Subsequent instruction
or parser changes require the corresponding checks to run again against that
final source.

## Remaining limits and versioning

This is a bounded Linux/POSIX source-and-evidence distribution. It is not a
cross-platform executable image. Temporary staging and cleanup are parent
operations, distinct from repeating the pilot actions. The audit guard is not
a guarantee against arbitrary native code or a hostile same-user controller.

Original signatures attribute statements under the original declared trust
assumptions. Packaging them together does not create an integrated production
workflow, independent witnesses, complete route coverage, complete AI provenance,
universal deletion, disclosure-policy compliance or legal conclusions. The final
report retains `actions_reexecuted: false`,
`independent_reproduction: NOT_ESTABLISHED`, `conformance: NOT_ASSESSED` and
`dependency_scope: PINNED_VERSIONS_NOT_HERMETIC`.

Only original public summaries and cases are preserved here, not the complete
original runtime databases or all contents of their CI artifact ZIPs. Publication
cases contain synthetic text and HTML needed for verification; a blanket claim
that the archive contains no plaintext would be incorrect. Private keys and
production credentials are not intentionally included.

The fixed 24 October research distribution, historical tags and assets, prior
pilot runtimes and original signed captures remain separate and unchanged. A
changed capture or format needs a new explicit version and review. Neither a
matching checksum nor an internal successful CI run establishes independent
reproduction.

No blocking finding remains in the reviewed archive-to-worker trust boundary at
this development checkpoint.
