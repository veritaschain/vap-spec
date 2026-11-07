# Portable custody snapshot

**Status: unadopted, informative; bounded local experiment.**
[日本語](PACK-ja.md) · [Collector](README.md) · [Evidence checker](../cloud-credential-evidence/README.md)

The local collector's native envelope does not contain its custody history. This extension
exports a single inert JSON snapshot containing original artifacts and the signed metadata
needed to recheck their retained history. The recipient can verify it without the producer's
SQLite database, original input paths, collector process or private signing key.

The recipient still needs trusted verifier code and its pinned dependency, a public key chosen
outside the snapshot, and an independently supplied expected store ID. The included checkpoint
is a statement by the collector, not an independent witness or proof of the latest history.

This work explores the offline-verification aim of [VAP §9.3](../../spec/v1.2/VAP_Framework_Specification.md#93-evidence-pack-v12-recommended).
It does not define the VAP Evidence Pack wire format or provide external anchor proofs,
applicable policy documents, profile conformance, legal acceptance or independent reproduction.

## Run

From the repository root, using the same Python 3.12 environment as the collector:

```sh
python -m pip install -r experiments/cloud-credential-collector/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/cloud-credential-collector/tests -v
python -O -W error::ResourceWarning -m unittest discover -s experiments/cloud-credential-collector/tests -v
python -W error::ResourceWarning experiments/cloud-credential-collector/run_pack_demo.py
python experiments/cloud-credential-collector/custody_pack.py --help
```

The [tests](tests/test_custody_pack.py) and [demo](run_pack_demo.py) use public synthetic signing
material and disposable private files. A separate verifier process exercises the receiving side.
This remains execution by the same local operator, not an external organization's reproduction.

### Export

```sh
python experiments/cloud-credential-collector/custody_pack.py export \
  --store /private/collector-store \
  --public-key-file /private/trusted-collector-public.bin \
  --private-key-file /private/collector-seed.bin \
  --expected-store-id EXPECTED_STORE_ID \
  --out /private/custody-snapshot.json
```

The names above are placeholders. Key files contain exactly 32 raw bytes, following the existing
collector's key convention. Obtain the expected store ID through the caller's established store
registration or retained evidence, not by automatically accepting the ID inside an incoming file.
The output is private, outside the managed store, and never replaces an existing path.

Export holds one process lock while auditing the store, copying its committed prefix, signing
the snapshot checkpoint and publishing the output. It includes every committed receipt in that
snapshot or rejects the export if the package limits would be exceeded. It does not quietly
select a convenient subset. Orphan blobs, staging files and the mutable SQLite index are not
accepted collection receipts and are not part of the snapshot.

### Verify on the receiving side

```sh
python experiments/cloud-credential-collector/custody_pack.py verify \
  --pack /private/custody-snapshot.json \
  --public-key-file /private/trusted-collector-public.bin \
  --expected-store-id EXPECTED_STORE_ID
```

Either command may also take `--external-checkpoint /private/retained-checkpoint.json`.
That file is a separate caller input. Its value as a retained witness depends on how the caller
obtained and protected it; copying the checkpoint out of the submitted package does not establish
separate custody or latestness.

Verification needs trusted copies of `custody_pack.py` and the pure helper file
`../cloud-credential-evidence/cloud_evidence.py`, preserving that repository layout, plus the
pinned `cryptography` dependency. Copying `custody_pack.py` alone is insufficient. Its code
does not import the collector or SQLite, read the producer's database, load a private key,
contact a server, extract an archive or execute anything supplied by the snapshot.
The implementation and tests currently target the Linux/Python environment described in the
collector README; a separate process does not establish cross-platform or cross-party assurance.

The Python API is:

```python
verify_pack(package, *, trusted_public_key, expected_store_id, external_checkpoint=None)
export_pack(store_path, output_path, *, trusted_public_key, private_key,
            expected_store_id, external_checkpoint=None, clock_ns=None, hook=None)
```

Clock injection and hooks are test facilities of the Python API. The CLI offers no backdating
or fault-injection options. Reports contain metadata and bounded conclusions, not raw artifacts
or private keys. The explicit snapshot output contains the original data and must remain private.

CLI exit **0** means export or custody verification completed, while **2** means the command
rejected its input or encountered an error. A successful verification still reports
`completeness: unresolved`, `latestness: unresolved` and `independent_custody: false`.
Without a separate checkpoint, `rollback_assessment` is `not_assessed`; after a matching
comparison it is `consistent_with_retained_checkpoint_only`. The exit code is not a safety,
authorization, origin or conformance verdict.

## What is bound and checked

The top-level object has exactly `schema`, `manifest`, `checkpoint`, `receipts` and `artifacts`.
The format is experimental and uses the collector's existing signature domain; it is not a
normative VAP container or an RFC 8785 JSON implementation.
There is no additional top-level package signature. Verification checks the existing signed
components and their exact commitments and membership, rather than trusting a submitted summary.

| Component | Check performed |
| --- | --- |
| Caller inputs | Validate the public key and required expected store ID separately from the submitted package. A different store using the same key still fails the ID comparison. |
| Store manifest | Verify its signature, schema, identity, collector ID and creation-time representation. |
| Receipt prefix | Check signatures, store/key/context bindings, contiguous sequence starting at one, previous-receipt commitments, request uniqueness and non-regressing recorded receipt time. |
| Original artifacts | Decode canonical base64 chunks; recompute byte size and SHA-256. Require exactly the unique artifact set referenced by the receipts, with no missing, duplicate or unreferenced entry. |
| Included checkpoint | Verify its signature and require its store, sequence and receipt commitment to match the exact exported tip. Its issue time cannot precede the receipt it describes. |
| Separate external checkpoint | Verify the caller-supplied checkpoint against the corresponding prefix, with the same identity and time-binding rules. A valid later extension is allowed. |

Arbitrary source bytes, including non-UTF-8 data, can retain custody commitments. Their inclusion
does not establish that they are valid Azure records. This verifier evaluates custody structure;
authentication, permissions, resource use and timing of pre-action evidence remain questions for
the separate evidence checker and its caller-supplied trust and scope.

## Internal checkpoint and retained witness

| Input situation | Bounded result |
| --- | --- |
| Valid package with only its included checkpoint | The supplied prefix is consistent under the caller's pins. Rollback is not assessed. |
| A separately retained checkpoint matches that prefix | The package is consistent with that checkpoint only. |
| A current package extends an older matching checkpoint | The extension is allowed; the older checkpoint does not certify the latest suffix. |
| A package omits history required by a later retained checkpoint | Reject the package/checkpoint comparison. |
| Someone substitutes another store signed by the same key | Reject the mismatch with the caller's expected store ID. |

A coherent old package and its old included checkpoint can remain valid. A matching old external
checkpoint does not reveal a suffix that arose after it and was later removed. A separately held
later checkpoint is needed to detect that particular conflict. The format establishes no trusted
wall clock, online freshness service, independent anchor or universal completeness.

## Encoding, limits and privacy

The package is bounded to **1 MiB**, at most **256 receipts** and **256 unique artifacts**.
Each original artifact retains the collector's **65,536-byte** limit. Artifact entries have
exactly `artifact_sha256`, `artifact_size` and `base64_chunks`. Raw bytes use standard base64 in
fixed **32 KiB decoded chunks**, apart from the final chunk; an empty original uses an empty
chunk list. The chunking preserves
the frozen JSON parser's per-string limit. The decoder checks canonical encoding, including
padding, rather than treating different textual encodings as interchangeable.

The report's `package_sha256` identifies the canonical JSON value. Export writes exactly those
canonical bytes, so that value also identifies the exported file. Reformatting an incoming JSON
file can preserve its value while changing its file-byte hash; this report field is not a hash
of arbitrary incoming formatting. Each source commitment still covers the decoded original
bytes, not a reserialized native JSON object or base64 display.

See [RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html#section-3.5)
and [Python's base64 documentation](https://docs.python.org/3.12/library/base64.html#base64.b64decode)
for the underlying encoding. Strict field/type/size checks and exact membership rules are choices
of this experiment. The frozen JSON subset also rejects duplicate object keys, unsupported
number representations and non-NFC metadata strings.

A store accepted by the collector may exceed the smaller export limits. Export then fails without
overwriting the destination or claiming a partial snapshot is complete. This is a bounded pilot,
not a streaming archive format or a complete database backup.

Base64 is not encryption. The snapshot contains the original collected data and signed metadata;
private file permissions do not govern a recipient's later copies. Distribution, access, retention,
redaction and deletion require explicit decisions outside this experiment. No snapshots containing
production data or real private keys belong in public repositories or CI artifacts.
