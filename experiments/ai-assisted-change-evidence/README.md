# AI-assisted change evidence companion

**Experimental, unadopted research.** This is a local policy-and-evidence
exercise built on the unchanged [pre-record gate](../pre-record-gate/README.md).
It is not a VAP requirement, a VAP/VCP conformance verifier, a Java4Shell fix,
a production deployment controller or evidence of an independent implementation.
The [design proposal](../../proposals/ai-assisted-change-evidence/README.md)
separately records the source-backed motivation and broader unimplemented work.
[日本語](README-ja.md)

## What actually runs

The harness signs a manifest committing the exact UTF-8 text of seven synthetic
artifacts: finding, patch, target baseline, environment, test plan, test results
and approval conditions. It separately supplies a policy and target snapshot.
The companion checks the signature and bytes, named required test results,
test freshness, tested patch/baseline/environment/plan bindings, and conditional
approval assertions. A valid signature on a failed test remains valid evidence;
it does not satisfy the declared test policy.

The existing synthetic authority signs an approval for one exact operation whose
text contains the manifest digest. Existing credential, delegation, proof-of-
possession, expiry and revocation checks are reused. The companion's managed call
then uses the existing gate's durable pre-record, dispatch intent and signed
backend receipt. **The backend only creates a digest-bearing mock record. It
does not apply a patch, change a service or run the test plan.** Test outcomes and
review conditions are deliberately synthetic assertions; actual unit/integration
tests exercise the binding and admission behavior, not Java or patch safety.

The manifest uses the existing gate's domain-separated Ed25519 envelope helpers
with a distinct `ai_assisted_change_evidence` kind and `change-reviewer` key ID.
Its `ai-assisted-change-evidence/0.1` format is private to this experiment.

## Results are separate

| Field | What it establishes in this experiment |
| --- | --- |
| `record_integrity` | Signature and original artifact bytes match the supplied evidence key. |
| `authorization_binding` | The signed synthetic authorization covers this exact digest-bearing request under the supplied time/revocation snapshot. |
| `test_evidence` | Submitted test assertions satisfy the named checks and freshness/binding rules of the supplied policy. |
| `approval_conditions` | Required signed condition assertions are present and say `met`; unsupported emergency exceptions are denied. |
| `admission` | The companion's policy decision for its managed mock call. |
| `mock_execution` | Existing gate outcome for the mock write; missing response stays `RESULT_UNKNOWN`. |
| `post_change_health` | `ATTESTED_*` for a matching signed synthetic observation; absent/unknown remains `NOT_ESTABLISHED`. |
| `rollback_evidence` | Separately attributed synthetic observation, never inferred from a request or absent receipt. |
| `external_anchor` | Always `NOT_ESTABLISHED` here. |

There is no overall safety or conformance PASS. A nonempty condition
`evidence_reference` is retained but not fetched or independently verified.
The signed assertion does not establish that a human actually performed the
review. Emergency override semantics, production identities, kill-switch
operations and physical rollback are not implemented.

**Enforcement boundary:** only the companion's `admit()` path applies the new
test/condition policy. The unchanged lower-level gate does not know that policy.
The `bypass-companion` negative control deliberately invokes that gate directly:
the test evidence is insufficient and the companion says `DENY`, yet the mock
write succeeds. Matching this expected result demonstrates the limitation;
it does not make the bypass safe. Non-bypassable production enforcement needs
separate credential, process and dispatch-boundary integration.

## Run

From the repository root, use Python 3.12+ and the existing pinned dependencies:

```sh
python -m pip install -r experiments/pre-record-gate/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/ai-assisted-change-evidence/tests -v
python experiments/ai-assisted-change-evidence/run.py run-suite \
  --output experiments/ai-assisted-change-evidence/generated/run-001
```

The suite runs the **17 cases** in `acceptance.json`, uses temporary loopback
HTTP services/SQLite stores, verifies the native gate bundles and writes a new
output directory. Existing output directories are refused. Process cleanup is
performed by the existing harness. Nonzero exit is a failed/incomplete run.
No private keys are exported; public mock keys and synthetic status/time inputs
are included to make verification repeatable.

The command prints the SHA-256 of `summary.json`. Retain that value through a
separately trusted channel before accepting a later copy. Recheck without
starting services:

```sh
python experiments/ai-assisted-change-evidence/run.py verify-exports \
  --output experiments/ai-assisted-change-evidence/generated/run-001 \
  --expected-summary-sha256 TRUSTED_SUMMARY_SHA256
```

Replace the placeholder with the retained 64-character digest; do not derive a
new trust value from an untrusted downloaded bundle. Verification checks the
nonempty exact case inventory, preserved case hashes, signatures, recorded
authorization snapshots, expected policy assessments and original gate receipts
through the existing `verify_bundle()` helper. It also verifies expected negative
outcomes. Same-run CI hashing is a reproducibility check, not independent custody
or an external time anchor. Harness effect/request counts are reported test
observations, not independently signed proof of all backend activity.

## Cases and limits

The cases cover ordinary admission, modified patch bytes, a newly signed patch
without a matching test, signed failed/missing/stale tests, a changed environment,
unmet conditions, unsupported emergency exception, expired/revoked approval,
approval for a different manifest, audit outage, response loss followed by
read-only reconciliation, uncertain rollback, repeated request and the explicit
lower-level bypass. Reconciliation does not resend the write. The unhealthy
observation case keeps successful mock execution, unhealthy observation and
unknown rollback separate.

All keys, signers, clocks and services are under one trusted harness operator on
one host. There is no independent observer, key custody, trusted UTC, external
anchor or protected boundary against a privileged controller. The supplied target
snapshot is not atomically bound to a real deployment; real-world configuration
drift and time-of-check/time-of-use races are not solved. The finding reference is
retained but not fetched; no vulnerability exploitation, network scanning, real
patching, rollback or kill-switch operation takes place. A signed statement can
be false when written. No completeness outside these declared artifacts or
adequacy of a real test plan is established.
