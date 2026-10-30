# Synthetic interoperability scenario

**Contract:** `vap-interop-demo/0.2.0`

## Workflow

The dataset describes a fictional claim-triage exercise dated 30 October 2026.
It contains no real subject, claim, customer, production system, or external
transaction.

The primary positive pack has two attempts:

| Attempt | Synthetic recorded outcome |
| --- | --- |
| `attempt-001` | Automatic processing denied; human review requested because confidence is low |
| `attempt-002` | Automatic processing approved under the fixture's stated policy |

A second positive pack adds a third complete attempt/outcome pair. Its six
events exercise an RFC 6962 tree whose leaf count is not a power of two.

For this local scenario, each attempt has exactly one
`AI_DECISION_ATTEMPT` event followed by exactly one
`AI_DECISION_OUTCOME` event with the same `attempt_id`. The sets of IDs
must match, and their size must equal the selected scope's expected count.
The event IDs are distinct; sequence numbers start at one; chain, policy,
event types and timestamps must fit the declared scope.

This bijection is a choice of the demo contract. Other workflows can include
retries, cancellations, timeouts or multiple outcomes and need their own
versioned rules. The fixture's action and outcome labels are assertions in a
synthetic record, not evidence that a real action was performed.

## Parties and trust

| Role | Local action | Assurance boundary |
| --- | --- | --- |
| Producer | Signs events and a manifest of the submitted collection | First-party synthetic role with a public test secret |
| Observer | Signs a record naming a root, scope digest and count | Simulated agreement; no independent observation occurs |
| Anchor | Signs a `DEMO_ANCHOR_RECEIPT` over the same values | Local test record; no request to an external anchor service |
| Verifier caller | Supplies the pack and a separate trust file | Selects test keys, roles and one approved scope digest for this evaluation |

All three private keys are published in the generator. The 32-byte seed for
each role repeats one byte: producer `0x11`, observer `0x22`, anchor
`0x33`. Their different key IDs and public keys let the verifier test role
binding. They do not make the roles organizationally independent or prove a
real producer's identity.

The primary pack uses `demo-trust.json`; the six-event pack uses
`demo-trust-six.json`. A verifier must not derive its trusted keys or approved
scope from the submitted pack.

## What the signed records bind

The three records must agree with the verifier's recomputed Merkle root,
scope digest, and submitted event count. The separately selected trust file
pins the scope digest, so a submitter cannot replace the declaration merely by
re-signing another pack.

The scope states a chain, batch, policy, time window, allowed event types,
expected count and the attempt/outcome rule. This pinned declaration is an
input assumption. It does not prove that its expected count covers all real
activity or that the declaration existed before any real event.

Record issue times must be real UTC timestamps no earlier than the declared
window end. Event timestamps must lie within that window in nondecreasing
order. These checks compare supplied metadata; they do not authenticate clocks
or establish external time.

## Negative vectors

The negative vectors isolate different local checks. Where a vector is
described as re-signed, the generator uses the public test secrets to make the
remaining cryptographic records internally consistent.

| Vector | Synthetic change | Expected reason to reject |
| --- | --- | --- |
| `invalid-tampered-event.json` | Changes an event after signing | Its content no longer matches its hash/signature binding |
| `invalid-omitted-outcome.json` | Removes one outcome and rebuilds/re-signs the submitted collection | An attempt lacks its required outcome |
| `invalid-split-view.json` | Signs an observer record over a different root | The role records disagree on the submitted collection |
| `invalid-omitted-pair.json` | Removes a complete attempt/outcome pair and rebuilds/re-signs the collection | The distinct-attempt count differs from the pinned declaration |
| `invalid-rebound-scope.json` | Changes the declaration to make a reduced collection appear complete | The replacement scope digest differs from the caller's trust file |
| `invalid-untrusted-signer.json` | Uses a signer outside the configured role binding | The configured key cannot authorize that event or record |

The omission cases distinguish internal cryptographic consistency from
fulfillment of an agreed local rule. They do not define a universal VAP
completeness rule. In particular, the demo's re-signed collection is not an
independently witnessed original anchor, and the expected-attempt count is not
a proven inventory of all real-world actions.

## Relationship to current VAP research

VAP INT-008 concerns omission evidence at anchor granularity. This demo's
attempt/outcome rule and pinned synthetic scope are additional local choices;
a demo PASS is not an INT-008 or profile-conformance finding.

The [declared-scope proposal](../../proposals/declared-scope-precommit/README.md)
and its [research verifier](../../experiments/declared-scope-verifier/README.md)
have separate adapter formats and distinguish current-requirement checks from
experimental fulfillment. That work also addresses source closure, delivery
states and timing assumptions beyond this scenario. This package makes no
compatibility claim with either research mode and does not adopt the proposal.

No event that went unobserved can be recovered from these files. The example
does not establish trusted advance commitment, operational capture controls,
a complete source inventory, external anchoring, production identity,
organizational independence, legal compliance, or the correctness of an AI
decision. The fictional workflow makes no legal classification of an actual
insurance or administrative system.

## Reproduction record

The manifest specifies expected outcomes, not observed results.
A published reproduction should retain the exact source commit, fixture and
trust hashes, runtime versions, commands, full outputs and exits, and any
deviations or code reuse. A report from an independent party remains distinct
from the first-party fixture generator and the simulated evidence roles.
