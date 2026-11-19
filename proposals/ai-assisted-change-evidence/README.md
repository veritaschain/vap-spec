# Evidence for AI-assisted software changes

**Status:** Informative research proposal; unadopted. **Reviewed:** 19 November 2026 JST.
**Formal proposal number:** Unassigned. **Target release:** Undecided.
**Baseline:** VAP v1.2.0 Draft 3 at `4db6c490900dac7e85773c39bbcc5cae935bd730`.
**License:** CC BY 4.0 International. [日本語](README-ja.md) · [Source review](SOURCES.md).

This proposal connects a particular software change with the evidence used to
evaluate, approve and execute it. The review question is concrete: **Was this
artifact, for this target and baseline, the change covered by these tests and
this approval, and what result was observed?** The same question applies when
AI assists with finding a vulnerability, recommending a patch, writing tests or
reviewing a change. AI involvement is recorded where observable; it is not a
substitute for identifying the artifact and the responsible actors.

The FCA's November review provides a specific motivation: conditional approvals
and production exceptions were not consistently represented or tracked. DORA
provides relevant change-management duties for financial entities within its
scope. The [source review](SOURCES.md) separates those findings and duties from
VSO's proposed design. It makes no finding against the organisations mentioned
in the separate November outage reports.

## 1. Status and scope

Publication or merge does not create a VAP requirement, event code, profile,
certification level or accepted Evidence Pack format. VAP remains a framework
for retrospective evidence verification. Under [§§1.3, 4.5.2 and 4.6.3][vap],
general internal coding/patch administration has no registered domain profile;
DAP is a capability composed with a domain profile, not a standalone way to
claim conformance. A bank's use of a coding assistant does not by itself put
the workflow within VCP's trading-decision scope.

This work does not claim to collect all internal model reasoning, prove test
adequacy, discover every omitted operation, make records unalterable, or ensure
safe/legal deployment. A signed explanation remains an attributed explanation.
An observer and a verifier can check only their declared evidence boundary.

## 2. Proposed evidence relationships

The names below are **design vocabulary**, not a new wire schema or field list
required by VAP. A real integration would publish its concrete contract and
trust policy before making a verification claim.

| Stage | Evidence to bind | Question and limit |
| --- | --- | --- |
| Finding | Source/advisory reference, assessment version, asset identity and observed configuration | Does this finding concern this asset? A CVE identifier alone does not establish exposure. |
| Change | Original patch/build bytes and digest, dependencies, target, pre-change baseline and configuration digest | Is the proposed artifact unchanged, and is the intended environment identified? A digest does not show that the environment was accurately inventoried. |
| Tests | Test-plan bytes/version, tested artifact digest, test environment/baseline, run identifier/time, original results, omitted cases and stated coverage | Were the submitted results produced for this artifact and declared environment? A passing test does not establish production equivalence or sufficient coverage. |
| Approval | Approver/delegator authority, exact change-evidence digest, target, conditions, expiry and applicable policy | Does the approval cover these bytes and this action? Keep conditional approval distinct from fulfilled conditions. |
| Exception | Permitted exception policy, authorised scope, unmet conditions, reason, expiry, compensating measures and follow-up owner | Does the declared policy permit this bounded exception? Preserve the unmet test/condition result; do not relabel it as a pass. |
| Dispatch and outcome | Operation/attempt identities, exact request digest, pre-dispatch acknowledgement, receiver receipt and reconciliation evidence | Was dispatch permitted, and what does the receiving system attest? A request or timeout does not establish completion or nonexecution. |
| Health and rollback | Observed subject/configuration, observation interval, health result, rollback request/authority, restoration receipt and post-rollback observation | Was the stated condition observed, and was restoration confirmed? A rollback request is not a completed rollback. |

Preserve original result and receipt bytes separately from summaries or redacted
views. Identify who signed each statement, how the verifying party obtained the
trusted key, and which fields are covered. A checksum or signature created by
the collector is not a signature from the test runner or deployment platform.
Record retention and access policy must identify which raw inputs can be held;
the design does not require collecting credentials or every prompt.

Where available, attribute AI contributions through the service/model label as
reported by the provider, request/run/tool identifiers, and retained observable
input/output artifacts or explanations. These are attributed observations, not
access to hidden model reasoning or independent proof of which model binary ran.

## 3. Evidence evaluation and execution control

An application may choose to evaluate the evidence before allowing an operation.
That application owns its execution policy and enforcement. VAP itself does not
stop a patch, run a test, impose an emergency-approval procedure or operate a
kill switch. The proposed order for a managed integration is:

1. Capture the exact change, target, baseline, policy and test evidence.
2. Evaluate the bindings and policy conditions; obtain an approval for those
   exact objects. Retain any approved exception as an exception.
3. Bind the admission decision atomically to the operation that the receiving
   system can perform. If the artifact, target, baseline or authority changes,
   obtain a new assessment/approval as required by the declared policy.
4. Preserve the request and dispatch state, then record the receiver's outcome.
   Reconcile an unresolved dispatch through a read-only operation; do not treat
   an absent receipt as permission to repeat the write.
5. Record health and rollback observations under separately stated scope and
   authority. Preserve unknown outcomes and unsuccessful restoration attempts.

This order is a design proposal, not proof of an atomic production implementation.
The existing [control-state companion][control] explicitly documents that its
`preflight()` is not connected to admission. A preflight check or signed test
report alone cannot close the gap between the checked state and the executed
state.

For a kill-switch integration, proposed records would bind the controlled
system/version, authorised operators, exercise scenario and time, observed
response, maintenance state and follow-up. These are proposed evidence
relationships, not an FCA-prescribed schema. No kill switch is implemented here.

## 4. Separate conclusions

The [companion experiment][experiment] uses separate reporting axes. A reviewer
should preserve their different meanings rather than creating a universal pass:

| Report field | Meaning within a declared boundary |
| --- | --- |
| `record_integrity` | The submitted artifact inventory, original-text digests and manifest signature were checked under a stated key. |
| `authorization_binding` | The supplied authority and approval cover the exact requested mock operation. |
| `test_evidence` | Submitted evidence satisfies or fails the declared test policy, or cannot be assessed. It is not a safety verdict. |
| `approval_conditions` | Submitted condition states and references meet the declared condition policy, or do not. References are not independently resolved. |
| `admission` | The local evaluator permits or denies the managed mock write. This is not VAP conformance. |
| `mock_execution` | The mock gate reports dispatch state: a digest-bearing record operation may be unattempted, rejected, confirmed or unresolved. |
| `post_change_health` | A separate synthetic health statement is attributed as `ATTESTED_*`; absent/unknown evidence remains `NOT_ESTABLISHED`. |
| `rollback_evidence` | A separate synthetic restoration statement is attributed as `ATTESTED_*`; absent/unknown evidence remains `NOT_ESTABLISHED`. |
| `external_anchor` | Not established by this local experiment. |

A correctly signed failed-test report can pass integrity verification while
failing the test policy. A correctly signed deployment receipt can coexist with
an unhealthy service. A valid signature and complete submitted inventory do not
establish that all relevant real-world events were captured.

## 5. Implementation connection and remaining work

The [new companion][experiment] imports the existing [pre-record gate][gate]
machinery. The gate's supported backend operation is `create_record` at
`sandbox/records`. The companion uses that mock operation to carry a digest of
the change evidence; the receipt confirms mock record acceptance, **not patch
installation**. The experiment's README and executable tests define the actual
implemented subset: the manifest binds submitted UTF-8 finding, patch,
baseline, environment, test-plan, test-run and condition artifacts. A declared
policy checks required passing cases, freshness, matching target/baseline and
submitted condition status before the managed mock operation. A nonempty
condition evidence reference is required, but the referenced evidence is not
retrieved or independently verified. Approval is bound to the operation carrying
the manifest digest. Unsupported emergency exceptions are rejected; the richer
exception design in §2 remains proposed.

This proposal's broader relationships, including enterprise authority,
production-state observation and kill-switch evidence, are design work, not
implemented capabilities. Synthetic health and rollback observations do not
show that a real deployment or restoration occurred.

The companion enforces its declared policy only on calls made through its
managed entry point. The unchanged lower-level gate does not evaluate this
test/condition policy: calling it directly can commit a signed mock operation
whose change evidence the companion rejects. The `bypass-companion` case makes
that limitation explicit. A non-bypassable production enforcement boundary is
not established; a denied assessment must not be mistaken for proof that no
write occurred through another path.

The existing gate provides local durable request/dispatch records, synthetic
authority checks, mock backend receipts and read-only reconciliation. Its
trusted harness, clocks, keys and backend are controlled by one operator. Those
assumptions do not establish independent provenance, real-time revocation,
trusted UTC, an external anchor or a production security boundary.

Useful acceptance cases include artifact substitution after testing, an
environment or baseline mismatch, stale test evidence, unmet approval
conditions, revoked/expired authority, unavailable audit storage, a lost response
and unresolved rollback. Exact implemented cases and their results belong to
the companion's versioned run, not to this proposal. No prior fixed run or
historical artifact is relabelled as execution of these new cases.

Before extending this to a real platform, the integration would need a scoped
target contract, enterprise authority/identity binding, independent collection
or explicit trust assumptions, a tested enforcement boundary, secure key and
retention handling, and recovery semantics agreed with the receiving system.
That work must establish what the platform actually did, separately from what
its logs or operator state it did.

[vap]: https://github.com/veritaschain/vap-spec/blob/4db6c490900dac7e85773c39bbcc5cae935bd730/spec/v1.2/VAP_Framework_Specification.md
[gate]: ../../experiments/pre-record-gate/README.md
[control]: ../../experiments/control-state-evidence/README.md
[experiment]: ../../experiments/ai-assisted-change-evidence/README.md
