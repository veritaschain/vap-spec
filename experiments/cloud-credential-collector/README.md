# Local cloud evidence collector pilot

**Status: unadopted, informative; local custody experiment using synthetic tests.**
[日本語](README-ja.md) · [Evidence checker](../cloud-credential-evidence/README.md) ·
[Design proposal](../../proposals/cloud-credential-evidence/README.md)

This pilot receives an existing local artifact, preserves its original bytes, and records a
signed collection receipt. It adds actual filesystem persistence, process restart and retry
behavior to the separate offline evidence checker. Its native-record export connects the two
experiments without manufacturing source availability, permissions or operation bindings.

The CLI does not contact Azure or collect from an authenticated cloud endpoint. Local possession
of an export and a collector signature do not establish that Microsoft produced the export.
The published demo and tests use only synthetic records and public test signing material.

## Run

Use Linux, Python 3.12 and the pinned dependency. The implementation requires `/proc/self/fd`
and `renameat2(RENAME_NOREPLACE)`; unavailable capabilities are errors. From the repository root:

```sh
python -m pip install -r experiments/cloud-credential-collector/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/cloud-credential-collector/tests -v
python -O -W error::ResourceWarning -m unittest discover -s experiments/cloud-credential-collector/tests -v
python -W error::ResourceWarning experiments/cloud-credential-collector/run_demo.py
python experiments/cloud-credential-collector/collector.py --help
```

The focused [workflow](../../.github/workflows/cloud-credential-collector.yml) runs these
checks on Ubuntu. The demo uses temporary private files and actual subprocesses, prints a
small result summary, and cleans up its local test state. A successful test run demonstrates
the named local behaviors under that test environment; it does not certify cloud collection,
independent custody, power-loss durability or prevention of an incident.

### Collector commands

Every command takes `--store` and a caller-selected `--public-key-file`. Signing commands also
take `--private-key-file`. Key files contain exactly 32 raw bytes, not hexadecimal text or PEM;
the private key is an Ed25519 seed and must correspond to the caller's public key. Provision
these files outside the store. The public key's trusted identity must be established separately.

| Command | Additional arguments and output |
| --- | --- |
| `init` | `--collector-id`, `--key-id`; create the private store and its signed manifest. |
| `collect` | `--input`, `--request-id`, `--context`; copy an existing local artifact and commit or recover its receipt. |
| `audit` | Optional `--checkpoint`; verify the current committed custody state. No private key required. |
| `checkpoint` | `--out`; write a signed checkpoint to a new private file. Its custody outside the store is the caller's responsibility. |
| `export-native` | `--request-id`, `--out`, optional `--checkpoint`; verify custody and write a native envelope to a new private file. |

The `--context` file is an object with exactly `schema`, `adapter`, `issuer`, `tenant_id` and
`resource_id`. The schema is `experimental-cloud-custody-source-context-v0`. Native export
supports the separate checker's `azure-service-principal-signin-subset-v0` and
`azure-key-vault-audit-subset-v0` mappings. A context supplied during capture is part of the
signed receipt; the export command has no argument for retagging it later.

The corresponding Python API is `initialize_store(...)` and the `Collector` context manager,
with `collect_file(...)`, `get_receipt(...)`, `audit(...)`, `checkpoint()` and
`export_native(...)`. Use the [tests](tests/test_collector.py) for explicitly synthetic invocation examples.

CLI exit **0** means the local command completed; **2** means it rejected the request or encountered
an error. A successful audit still reports `completeness: unresolved` and
`independent_custody: false`. Its `rollback_assessment` is `not_assessed` without a checkpoint,
or `consistent_with_retained_checkpoint_only` after a matching comparison. None of these exit
codes grants permission to execute a cloud operation.

## Capture and retry

The store binds a request ID to the exact input bytes and a frozen source context. The context
identifies the experimental adapter, collector issuer, tenant and resource. These are the
collector's assertions; they are not automatically the identity of the native source. The
later evidence checker compares the supplied context, native fields and caller's trust scope.

Raw bytes are copied into private content-addressed files. JSON layout, whitespace and line
endings remain part of the commitment. A normalized view never replaces the retained source.
The SQLite receipt/index transaction follows durable publication of the source artifact, and
an exclusive process lock covers verification and mutation of the store.

The store contains `index.sqlite3`, `store.lock`, `blobs/` and `staging/`; SQLite may also create
its rollback journal. Directories use mode `0700`, files use `0600`. This pilot accepts at most
65,536 bytes per raw artifact, 1,024 committed receipts and a 64 MiB database. It is not an
unbounded bulk-log importer. Audit reports uncommitted blobs and staging files separately from
committed receipts; their existence alone does not establish an accepted collection.

| Situation | Required behavior |
| --- | --- |
| New request | Retain the bytes and context, then commit a signed receipt with store identity, sequence, previous receipt commitment and collector receipt time. |
| Same request, bytes and context | Recheck the store and retained bytes, then return the original receipt and time. |
| Same request, changed bytes or context | Reject the conflicting retry. |
| Process stops before receipt commit | No accepted receipt exists. A retry may finish capture with a new current receipt time. An exact uncommitted artifact may be reused after verification. |
| Process stops after commit, before responding | A restart and retry recover the original committed receipt. |
| A retained artifact or indexed receipt is missing or changed | Report an error; do not repair, silently recapture or assign a replacement historical receipt. |
| Initialization is repeated on an existing store | Verify a complete existing store and preserve its identity. Reject a partial layout without recreating missing files or directories. |

The collector does not resend a cloud operation. Retrying collection only attempts to preserve
an already available local artifact. It cannot reconstruct data never received, prove a cloud
query was complete, or infer missing pagination and collection-window closure.

## Audit, trust and checkpoints

Audit requires a public key supplied by the caller. A key named inside the store cannot make
itself trusted. The audit rereads committed artifact bytes, verifies signed receipts and the
store manifest, and checks the receipt/index chain. The artifact's hash is a commitment to
its content, not encryption or proof of its origin.

An optional caller-retained signed checkpoint identifies a store, a sequence and the receipt
commitment at that sequence. Its meaning is deliberately limited:

| Available evidence | Conclusion the audit may make |
| --- | --- |
| Internally consistent store, no external checkpoint | The supplied bytes and chain are internally consistent under the pinned key. Rollback is not assessed. |
| Valid matching checkpoint for a prefix of the current store | The current store is consistent with that checkpoint; later receipts may legitimately extend it. |
| Later retained checkpoint, but current store lacks that sequence | The supplied store conflicts with the checkpoint. |
| Checkpoint for another store, another chain or an untrusted key | Reject the checkpoint comparison. |

A matching old checkpoint cannot show that an even later suffix was never removed. A checkpoint
stored beside the database can be rolled back with it and is not an independently retained
observation. This pilot does not distribute checkpoints to a witness, implement a transparency
service, or establish independent logging or anchoring for XREF.

The threat model covers accidental damage, tampering observable against a caller's pinned key
or retained checkpoint, process interruption and cooperating concurrent collector processes.
An administrator or a holder of the collector private key can alter the environment and produce
new assertions. Local permissions, locks and signatures do not remove that trust assumption.

## Native export and time

The export bridge first verifies custody and then emits the existing checker's signed native
envelope. It carries the original UTF-8 text and byte commitment, the capture-bound context,
and the original collector receipt time. It does not reserialize the source JSON. Unsupported bytes
or mappings may remain preserved as custody artifacts while native export fails explicitly.
The native envelope references the custody receipt by commitment but does not embed the custody
store or its receipt chain. The separate evidence checker evaluates the exported statement;
repeating custody audit still requires the retained store, caller-pinned public key and any retained checkpoint.

The CLI obtains receipt time from the host clock. It has no clock override or backdating option.
Tests may inject a clock through the Python API. The custody receipt retains nanosecond precision
as a decimal string. The older checker's integer-second `received_time` is rounded **up** from
that value, so conversion cannot move receipt before its recorded capture time. This can add
less than one second of conservative delay and is not a measured transport delay.

Source event time and source availability remain unknown in the exported wrapper. The existing
checker independently parses supported event timestamps from the original native record. A
source event timestamp does not establish when the collector could obtain it. Host-clock truth,
clock synchronization and source authenticity still require evidence from the real environment.

Native export supplies no permission statement, exact attempt binding, collection-completeness
statement or claim of AI orchestration. A caller may provide separate, explicitly synthetic
policy and context in an integration test. Even then, a record received after an action cannot
be promoted into a prerequisite available before that action. A supported retrospective
source-reported read remains narrower than observed external exfiltration or complete containment.

## Private files and operational limits

The local store uses private directories and files, bounded reads, and checks for unsafe file
types and path aliases. The ordinary CLI output omits raw source contents and private key bytes.
An explicit native export contains the source contents and must be handled as private evidence;
its output is created without overwriting an existing file. Do not put a real store, private
key, native export or customer log in the repository or public CI artifacts.

The tests use Linux filesystem and process behavior. They do not establish Windows support,
network-filesystem correctness, resistance to an administrator replacing paths during a call,
encrypted storage, retention/deletion governance, protected signing hardware or trusted time.
Process-kill recovery is distinct from operating-system or hardware power-loss testing. SQLite
and explicit synchronization still depend on the underlying filesystem and hardware honoring
their documented contracts; see [SQLite atomic commit](https://www.sqlite.org/atomiccommit.html)
and [Python filesystem synchronization](https://docs.python.org/3.12/library/os.html#os.fsync).

This is an additive experiment, with its own custody encoding. It does not change normative VAP
fields, adopt a generic cloud profile, provide VC-Certified results or implement a runtime
authorization gate. The separate evidence checker's existing synthetic requirements and
claim boundaries continue to apply.
