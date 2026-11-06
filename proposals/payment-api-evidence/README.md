# Payment API authorization evidence — informative proposal

**Status: proposed, unadopted; informative design.** Checked 6 November 2026 JST against
repository baseline `1e6fff1bab50caf467b2a6b9e9f7de3d23d1c67a`. [日本語](README-ja.md)

This note proposes evidence bindings for a future payment adapter. It adds no normative
fields, profile registration or conformance claim. An additive
[offline synthetic evidence experiment](../../experiments/payment-api-evidence/README.md)
now exercises the evidence distinctions behind all eight candidate groups. The full adapter
acceptance cases below have **not been implemented or executed**: there is no payment
endpoint, durable consumption ledger, real collector outage or actual bank settlement test.

## Source and scope

CERT-In's [4 November update][c58] identifies CRAFTY FALCON and four offensive AI frameworks,
and reports payment-API abuse and cryptocurrency-wallet theft. Its [9 October advisory][c46]
already described stolen long-lived tokens and recommended binding transaction stages and
second-level approval. [15 October guidance][c49] already described repeat attacks after
incomplete remediation. [Reuters][reuters] did not establish a link between its separate
roughly USD 2 million case and this campaign. These are attributed public reports, not
forensic evidence collected by VSO.

The companion [site source review, PR #202][site-review] separates dates, claims and sources.
It was merged on 6 November 2026 and the [CRAFTY FALCON entry][site-entry] was published.
Publication of that review does not adopt this proposal or validate an implementation.

The [current registry](../../spec/v1.2/README.md) distinguishes **VAP v1.2 Draft 3**, **VCP v1.2
specification GA**, and **DAP v0.1.0 Working Draft**. VCP's finance/algorithmic-trading scope
does not establish a generic payment or wallet-custody profile. This proposal changes none
of those statuses and makes no CERT-In endorsement claim.

## Existing work and the remaining boundary

| Existing work | Bounded capability described there | Additional payment question |
| --- | --- | --- |
| [Pre-record gate](../../experiments/pre-record-gate/README.md) | Exact-operation approval, durable dispatch intent and a matching signed receipt for one loopback mock operation | Can an adapter bind actual bank semantics and independently governed approval identities? |
| [OS-isolated gate](../../experiments/os-isolated-gate/README.md) | Controlled network isolation and deliberate privileged bypass cases | Which production, cloud-management and deployment routes can reach the payment authority? |
| [Control-state evidence](../../experiments/control-state-evidence/README.md) | Scoped runtime observations; non-enforcing preflight | Can execution be bound atomically to the checked configuration and revocation epoch? |
| [Wallet authorization evidence](../wallet-authorization-evidence/README.md) | Separately assessed integrity, authorization, execution matching and observed delegation state | How are payment acceptance, settlement, reversal and reconciliation distinguished? |

Those experiments retain their existing code, test evidence and limitations. Their outcomes
do not establish that these payment cases pass. In particular, the wallet verifier has no
consumption ledger; the pre-record mock's idempotency cannot be assumed for another API.

## Candidate evidence contract

**1. Exact operation and context.** A candidate envelope would identify the tenant, environment,
workload/run, observed principal, declared delegation and intended API audience. Bind the
source account, destination/beneficiary, action, exact amount and currency, request/payload
digest, operation ID, nonce/idempotency domain, policy version/digest and validity window.
The amount needs an explicit unit and exact representation. A versioned adapter would define
canonical encoding and show how API bytes map to these meanings; a digest alone does not
decode a bank's payload or establish that a destination is appropriate.

**2. Business approval.** Each maker/checker approval would bind that same operation and policy.
Use a separately trusted identity/role source to establish eligibility and separation of
duties. Two signatures or two keys do not establish two independent people. The verifier's
trust roots cannot come solely from the evidence bundle. Approval issuance and expiry need
an explicit clock assumption and ordering relative to dispatch.

**3. Final state and recovery.** Bind the final credential/delegation-status observation to
the operation, approval, issuer, configuration and recovery/revocation epoch. Record the
observation time and its freshness basis. Revocation observed before execution contradicts
authorization; missing or stale observations leave it unknown. A fresh snapshot alone does
not close the interval before execution. An atomic enforcement design, protected policy
state and a durable consumption ledger remain separate work. Rotation or a successful
retest does not establish eradication of every persistence path.

**4. Observable control routes.** Record which production, test, cloud-management, deployment
and signing routes were inspected, their configuration identity, observer and observation
time. An observed bypass can coexist with valid record signatures. An unobserved route is
unknown. A malicious administrator who controls both execution and the evidence authority
can defeat the assumed separation; separately named keys alone do not remove this risk.

**5. Execution and outcome.** Link dispatch intent, API invocation, authenticated provider
receipt and reconciliation evidence to the exact operation. Retain the distinction between
accepted, pending, settled, failed, reversed and unknown results. HTTP success is not proof
of settlement. A bank/aggregator receipt is an assertion by that trusted source, not VSO's
independent observation. Ambiguous outcomes require read-only reconciliation; do not infer
nonexecution from silence or automatically resend an unresolved payment.

**6. Evidence custody and privacy.** A candidate independent collector would acknowledge the
specific evidence it retained and declare coverage, gaps, checkpoints and recovery epochs.
This is VSO's design proposal, not a custody architecture specified by CIAD-2026-0058.
Preserve original signed bytes and the provenance of separately adopted trust keys.
Post-collection integrity checks cannot recover omitted or fabricated pre-collection events.
Do not include private keys, bearer tokens or unnecessary account/personal data. Opaque
references, access controls and retention rules are preferable where feasible; pseudonyms
and digests, especially of guessable values, may still expose sensitive information.

## Proposed adapter acceptance cases — not executed

Review four separate dimensions: **record integrity (I), operation authorization (A), execution
matching (E), and observed control state (C)**. These are discussion labels, not VAP verdicts
or a new wire schema. A supported observation is limited to its trusted source and recorded
scope. Unknown evidence may block admission while remaining unknown in retrospective review.

| Candidate | Synthetic condition to exercise | Required distinction to review |
| --- | --- | --- |
| PAY-01 | Complete matching approvals, scoped observations and authenticated settlement evidence | I may verify; A and E may be supported; C covers only the observed routes/time. No universal safety verdict. |
| PAY-02 | Two valid signing keys resolve to the same person where policy requires different people | I may verify while A is violated. An absent identity mapping instead leaves A unknown. |
| PAY-03 | A newly signed execution changes beneficiary, amount, currency, tenant or environment relative to approval | I may verify while approval binding and E fail. Include an unchanged positive control. |
| PAY-04 | Revocation precedes execution; separately, the final status observation is missing or stale | A is violated in the evidenced revocation case; otherwise unknown. Neither case permits evidence-based admission. |
| PAY-05 | A cloud/deployment route bypasses the gate; separately, one required route was not observed | C is violated for the observed bypass and unknown for missing coverage, even if I verifies. |
| PAY-06 | Lost acknowledgment followed by replay of an operation ID, or reuse with altered payload | Unresolved E stays unknown; no automatic write retry. Test a real adapter's durable consumption behavior before claiming duplicate suppression. |
| PAY-07 | HTTP 200 without settlement evidence; separately, an authenticated receipt describes another operation | E is unknown in the first case and mismatched in the second. Receipt authenticity does not repair the mismatch. |
| PAY-08 | Collector outage before a checkpoint, followed by credential rotation and an old-epoch recovery record | Record known gaps; reject known epoch/binding mismatches; keep unobserved actions and eradication unknown. |

## Review handoff

A later stateful implementation needs synthetic endpoints, healthy positive controls and
negative controls that demonstrate the adapter's actual failures. The offline companion
verifies signed synthetic evidence and includes unchanged positive controls; it does not
execute these endpoints or establish the stateful guarantees in PAY-06 and PAY-08.
Obtain trusted identity,
revocation, bank and collector observations without using real payment credentials or funds.
Inspect substantive assertions rather than comparing supplied expectation labels.

Open questions include bank-specific payload semantics, clock trust, atomic execution binding,
replay storage, privileged bypasses, privacy and independent reproduction. They require their
own implementation and review. This document establishes no test pass, production readiness,
completeness outside a declared collection boundary, or formal adoption.

A defender can record observed requests and effects; it cannot directly observe the attacker's
private agent reasoning. VAP/VCP evidence alone does not prevent compromise or unauthorized
transfers, enforce approval, rotate secrets or prove that an attack never happened.

[c58]: https://www.cert-in.org.in/s2cMainServlet?VLCODE=CIAD-2026-0058&pageid=PUBVLNOTES02
[c46]: https://cert-in.org.in/s2cMainServlet?VLCODE=CIAD-2026-0046&pageid=PUBVLNOTES02
[c49]: https://cert-in.org.in/s2cMainServlet?VLCODE=CIAD-2026-0049&pageid=PUBVLNOTES02
[reuters]: https://www.reuters.com/legal/government/india-flags-chinese-linked-ai-tools-hacking-campaign-against-financial-firms-2026-11-05/
[site-review]: https://github.com/veritaschain/vcp-site/pull/202
[site-entry]: https://veritaschain.org/incidents/#V1104CRAFTY
