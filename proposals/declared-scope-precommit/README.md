# Draft proposal for declared scope and advance commitment

**Status:** Discussion draft, not adopted. **Formal proposal number:** Unassigned.
**Draft revision:** 0.1. **Date:** 2026-10-24 JST. **Target release:** Undecided.
**Baseline:** VAP v1.2.0 Draft 3 at commit `9465c722be9efae18622ac4f04896bb0e1ea53d7`.
**License:** CC BY 4.0 International. [日本語レビュー要約](REVIEW-ja.md).

Repository integration of this discussion draft and its experimental implementation is not normative adoption.
Its unadopted status, unassigned formal identifier and undecided target release remain unchanged after merge.

This proposal defines how an evaluator could compare a submitted evidence package with an agreed scope,
an evidenced expected set, and a disclosure policy. It addresses the open question in [Appendix D, H-5][h5]:
whether VAP should define declared scope and require advance commitment.

The proposed outcome has two separate dimensions: cryptographic integrity and scope fulfillment.
A valid signature does not establish that the evidence covers the required activity. A scope declaration
does not establish that every event was observed. Any favorable result is conditional on the stated
observation boundary, source assurances, and evidence obligations.

This draft introduces no VAP v1.2 requirement, registered event type, conformance level, or common container
format. Uppercase requirement words in sections 4–7 express **proposed requirements for the experimental
extension**, not obligations already imposed by v1.2. Formal identifiers and release applicability remain
subject to the existing change-management process.

## 1 Source basis and current behavior

The [baseline specification][spec] provides these relevant boundaries:

- INT-008 binds an anchored batch to its event count, first and last identifiers, and policy identifier.
  Sections 4.1.7 and 11.1 distinguish omission after anchoring from an event never included in a batch.
- Section 11.1 permits evidence of a missing event through another record that implies its existence.
  Events never measured, with no other record implying them, remain outside the framework's reach.
- H-5 explicitly leaves the definition and advance commitment of declared scope for a future normative proposal.
  Its correction did not adopt either requirement.
- Section 9.3 recommends Evidence Packs but leaves their format to profiles in v1.2. It does not establish
  a normative common package format.

[CHANGE-001 Annex C][deferred] refers to future CHANGE-002 work on several deferred subjects. That reference
does not assign this draft to CHANGE-002 or establish numbered scope or observer requirements.
[DOC-SYNC entry 6][doc-sync] records publication of the CAB errata and retrospective records, not approval
of this proposal. The public tree at the baseline contains no separate CHANGE-002 text. Assignment of a
formal identifier requires reconciliation with the maintainer's complete proposal register.

## 2 Intended use and limits

The initial use is an offline evaluator receiving evidence from a synthetic AI evaluation exercise.
The evaluator checks what was committed, what evidence was required, what was submitted, and which questions
remain unresolved. This complements access to the producing system; it does not replace an evaluator's
inspection of that system.

The extension does not prevent misconduct, authorize access, reconstruct an unobserved event, establish
legal compliance, or convert a producer-operated observer into an independent party. It makes no claim
about any named real-world incident or external organization's adoption.

## 3 Terms and evidence boundaries

**Scope declaration:** A versioned statement of systems, time interval, operations, event classes,
exclusions, observation boundaries, expected-set derivation, disclosure policy, and evaluation deadlines.

**Evidence obligation:** An identifiable item that the agreed evaluation policy requires. This may be an
event, a relationship between events, a commitment, or a receipt. An obligation and a real-world action
are not interchangeable.

**Expected set E:** The obligations derived by the declared rule from the declared sources. Each obligation
has a stable identifier and required evidence types. E is not simply the set supplied by the producer.

**Observed set O:** Records captured at the specified observation points. A producer's own action report
and an execution-side observation are separate sources, even when they describe the same action.

**Delivery set D:** Evidence actually available to the evaluator in the identified package revision.
Assertions that evidence exists elsewhere are not members of D.

**Closure evidence:** Evidence that the declared source has reached the agreed boundary, including a cutoff,
sequence or equivalent inventory, and the treatment of late arrivals. Closure of one source establishes
nothing about activity outside that source's observation boundary.

**Advance commitment:** A binding of an exact scope revision to independently checkable evidence of existence
before an agreed cutoff. A producer signature or producer-supplied timestamp alone does not prove that timing.

## 4 Proposed declaration and commitment requirements

### Declaration contents

A scope declaration MUST identify:

1. The evaluation identifier, scope revision, governing policy digest, and parties authorized to approve it.
2. The system and component identifiers, operation and event classes, and explicit exclusions.
3. The evaluation interval, endpoint inclusion rules, time basis, permitted timing uncertainty, and deadlines
   for source closure, submission, notification evidence where relevant, and evaluation.
4. Each observation point and expected-set source, its operator, keys, configuration digest, and entities able
   to alter, bypass, disable, or replace it. It MUST distinguish claimed separation from evidenced separation.
5. The expected-set derivation rule, its version, identity and deduplication rules, multiplicity rules,
   and the source closure evidence needed to determine the set.
6. Required evidence for each obligation type and the permitted handling of withheld or unavailable material.
7. The commitment mechanism, trust policy, approval evidence, amendment rules, and their verification inputs.

The declaration MUST specify how retries, cancellations, timeouts, and one-to-many relationships are resolved.
No generic attempt-to-outcome bijection is imposed on every workload. The mapping rule is part of the agreed
policy and MUST distinguish unresolved attempts from a legitimate recorded cancellation or timeout.

### Two stages for unknown future activity

The extension SHOULD support both a finite expected set known before the exercise and a set derived from
future activity. It MUST distinguish these modes:

- **Fixed inventory:** Commit the identifiers, required evidence types, and an authenticated enumeration or
  verifiable set commitment before the agreed cutoff.
- **Derived inventory:** Commit the selection rule, source identities, observation boundary, exclusions,
  and closure criteria before the cutoff. After the interval, bind the source closure evidence, derivation
  result, and expected-set commitment to that exact declaration revision.

A derived inventory MUST NOT be described as an enumeration of future events committed in advance.
It commits the rule in advance; the later inventory depends on the completeness and authenticity of its sources.
If a source was bypassable or incomplete and the evidence does not resolve that gap, an all-activity claim
is unsupported even if every available source record has a matching output.

Counts, first and last identifiers, or set roots without adequate enumeration or reconciliation proofs are
insufficient to establish fulfillment. For an enumerable set, the evaluator MUST compare distinct obligation
identifiers and required relationships, not just counts. Duplicate or substituted identifiers cannot make
up for an unsatisfied obligation.

### Timing and amendments

The exact declaration and approvals MUST be cryptographically bound to a receipt or equivalent external
evidence accepted by the evaluation trust policy. The policy MUST identify who controls the evidence source,
how the receipt is authenticated, and what it establishes about existence time and ordering.

For a time-bounded proof, the latest possible existence time supported by the receipt, including its accepted
uncertainty, MUST precede or equal the agreed commitment cutoff. The cutoff itself MUST precede the activity
that the policy requires to be covered prospectively. A verifiable ordering proof MAY be evaluated instead
only when the policy defines its equivalent cutoff semantics.

A valid late receipt does not establish advance commitment. It also does not prove that no earlier receipt
exists. Absence of timing evidence, or uncertainty spanning the cutoff, yields an unresolved obligation.
A timing violation requires stronger evidence, such as a closed trusted register establishing that the first
qualifying acceptance occurred after a policy deadline for that acceptance. A signature authenticates the
stated revision; authority to approve it requires the separately declared authorization evidence.

An amendment MUST retain and reference the previous revision, identify the change and approver, and obtain
a new commitment. Prospective and retrospective amendments MUST be distinguished. A retrospective narrowing
cannot erase an already established failure under the original scope. Reports MUST retain both assessments
when an evaluator accepts a later restatement.

## 5 Proposed packaging and submission accounting

The experiment SHOULD use separate, versioned sidecar objects for the declaration, expected-set evidence,
submission manifest, and evaluation report. It MUST preserve existing signed bytes and profile-defined
Evidence Packs. These object names are working terms, not registered VAP wire types.

Each sidecar MUST bind its evaluation identifier, revision, scope digest, policy digest, relevant source
commitments, and referenced package or AnchorRecord digests. Cross-exercise substitution and replay MUST
be rejected. A future wire contract must specify canonicalization, algorithms, domain separation, ordering,
duplicate handling, and test vectors before interoperability is claimed.

The submission manifest MUST associate every known expected obligation with one of these presentation states:

| State | Meaning |
| --- | --- |
| Included | The required material is in D and can be located by identifier and digest. |
| Withheld | The submitter explicitly declines to disclose material, with reason and any permitted proof. |
| Unavailable | The submitter reports inability to retrieve material, with cause and supporting evidence. |
| Unaccounted | Required material or a usable disposition is absent from the submitted package. |

Presentation states describe availability to the evaluator. They do not establish whether an event happened,
was recorded, or was deleted. A withheld or unavailable assertion is not accepted as evidence merely because
it is signed. Disposition claims and the evidence supporting them MUST be distinguishable in the report.

The report MUST separately state whether the known inventory has been accounted for and whether the required
evidence obligations have been fulfilled. Listing all 1,000 obligations with 100 marked withheld can complete
the inventory accounting while failing a policy that requires all 1,000 records in full.

If the policy permits commitment-only disclosure, a verified commitment can satisfy that narrow obligation.
It cannot establish the correctness of hidden content or satisfy a different obligation requiring its review.
Redaction, key erasure, and disclosure changes MUST preserve the original commitment and identify which
checks are no longer possible. Hashing sensitive, low-entropy data does not make it anonymous.

## 6 Proposed evaluation results

### Separate result dimensions

The evaluator MUST emit two separately scoped results, plus evidence references and reasons:

| Dimension | Results | Question |
| --- | --- | --- |
| Cryptographic integrity | Verified, Failed, Indeterminate | Do the required cryptographic checks hold? |
| Scope fulfillment | Met, Not met, Indeterminate | Are the declared evidence obligations satisfied? |

Cryptographic integrity includes only the checks named in the evaluation policy: for example, relevant
signatures, hashes, inclusion or set proofs, and external receipts. The report MUST identify the objects
and checks actually verified. Verified hashes without the required external receipt do not become a
fully verified anchoring result. Untrusted keys, unsupported algorithms, missing proof material, or an
unestablished trust path remain explicit unresolved checks; a demonstrated cryptographic mismatch fails
the affected check.

This result split does not relax v1.2 batch-completeness verification under INT-008. A verifier that claims
to check INT-008 MUST report its result in the version-specific requirement checks. Verification of the
supplied objects' cryptography cannot be substituted for that check or labelled an overall v1.2 success.

Scope fulfillment MUST use the following precedence:

1. **Not met** when validated evidence establishes at least one violation of a required obligation.
   A known counterexample can establish non-fulfillment even when the full expected set remains unresolved.
2. **Indeterminate** when no such violation is established but a required prerequisite is unresolved,
   including scope authority, commitment timing, the expected inventory, observation boundary assurances,
   disclosure evidence, or the correspondence between obligations and records.
3. **Met** only when the required prerequisites, closure conditions, distinct obligations, and relationships
   are all established under the declared policy, with no unresolved required checks.

A report MUST NOT reduce these dimensions to an unconditional overall PASS. Cryptographic failure generally
leaves dependent scope checks indeterminate; separately validated evidence can still establish a scope failure.
The report MUST identify those independent evidence paths. It MUST distinguish failure to provide required
evidence from evidence that the underlying action did not occur.

### Notification example

A monitoring finding can imply an obligation to notify only through an explicit policy rule. The rule MUST
identify the trigger, recipient, deadline, and required acknowledgement stage: attempted, accepted by a
transport, delivered to a recipient endpoint, or acknowledged by a person. These stages are not interchangeable.

If a required delivery receipt is absent, the evaluator can report that receipt evidence was not supplied.
Without adequate closure and correspondence evidence, it cannot conclude that the notification never happened.
Before the deadline, the obligation is pending and the result remains Indeterminate. After closure, an
authenticated submission manifest that explicitly withholds a receipt required in full establishes a
submission-policy failure; notification occurrence can still remain unknown.

### Example report shape

The following is an illustrative report, not a signed evidence package or a normative schema.
The synthetic scenario assumes a verifiable fixed inventory of 1,000 distinct obligations and a finalized
package containing required records for only 900. All supplied objects and their relevant proofs verify;
the missing records were omitted from delivery, not proven absent from the original system.

```json
{
  "proposal_status": "experimental_unadopted",
  "evaluation_id": "synthetic-delivery-example",
  "scope_revision": "example-1",
  "integrity": {
    "result": "verified",
    "checked_objects": "supplied records, scope and inventory commitments, submission manifest",
    "claim_boundary": "does not verify the payloads of 100 records absent from delivery"
  },
  "scope_fulfillment": {
    "result": "not_met",
    "expected_distinct_obligations": 1000,
    "satisfied_distinct_obligations": 900,
    "reason": "100 identified required records absent from finalized delivery",
    "occurrence_of_underlying_actions": "not_determined_by_this_result"
  },
  "overall_pass": null
}
```

## 7 Synthetic acceptance cases

The table defines expected outcomes, not evidence of conformance. An opt-in
[research verifier and execution record](../../experiments/declared-scope-verifier/README.md) now accompany
these scenarios. Its internal synthetic runs are separate from independent reproduction and normative adoption.
Except where a case changes them,
fixtures assume approved synthetic keys, valid prior commitment, evidenced source closure, an authenticated
final submission manifest, and a policy requiring full records. Simulated external receipts are test fixtures,
not independent timestamps or production anchoring. Each fixture MUST include its exact policy,
input evidence, expected per-check results, and the reason for any unknown result.

| Case | Cryptographic integrity | Scope fulfillment |
| --- | --- | --- |
| Complete delivery of 1,000 required records | Verified | Met within the declared boundary |
| 100 identified records removed after a fixed inventory was anchored | Verified for supplied objects | Not met |
| A supplied payload changed without a matching signature | Failed | Indeterminate without other valid proof |
| 1,000 supplied records include duplicates or replacements for required IDs | Verified for supplied objects | Not met |
| Expected inventory and authoritative closure evidence are unavailable | Verified for supplied objects | Indeterminate |
| Required notification receipt absent and notification evidence source not closed | Verified for supplied objects | Indeterminate |
| Receipt explicitly withheld after deadline despite full-disclosure requirement | Verified for supplied objects | Not met for delivery |
| Required record explicitly unavailable after the finalized submission deadline | Verified for supplied objects | Not met for delivery |
| Policy permits a withheld payload; its required commitment proof verifies | Verified for supplied proofs | Met for that narrow obligation |
| Valid producer and execution-side records contradict a required equality rule | Verified | Not met; truth of either claim unresolved |
| Scope signed by producer with no accepted external timing proof | Indeterminate for required timing proof | Indeterminate |
| Closed trusted register proves first qualifying acceptance missed its deadline | Verified | Not met |
| Expectation source has an unresolved observation gap | Verified for supplied objects | Indeterminate |
| Scope or inventory from another exercise is substituted | Failed binding check | Indeterminate without other valid proof |

The removal case MUST retain the earlier inventory commitment; it must not merely regenerate a new inventory
of 900 and call it the original. A separate fixture SHOULD exercise such attempted retrospective narrowing.
For derived inventories, fixtures MUST include the source records, closure evidence, derivation rule, and
expected identifiers so a second implementation can reproduce E rather than trust a supplied count.

## 8 Compatibility and implementation tracks

The accompanying implementation uses explicit `vap-v1.2` and `experimental-scope` modes. Its local integrity
aggregation rule is Failed before Indeterminate before Verified, retaining every individual check. This is
an experimental implementation decision, not a newly adopted v1.2 rule. The implemented subset, unsupported
requirements, adapter format, synthetic receipt limits and reproducible commands are documented
[with the code](../../experiments/declared-scope-verifier/README.md).

The **v1.2 verifier track** checks the implemented subset of current profile and framework requirements
against a pinned specification and policy. It does not require this draft's fields or claim full conformance
from a small set of passing tests. Missing required proof material must be reported without manufacturing
a success result.

The **experimental extension track** adds the objects and result dimensions proposed here, uses an explicitly
different mode or package identifier, and labels all outputs experimental and unadopted. Results from either
track retain the version, policy, implementation commit, fixture commit, toolchain, and checked requirements.
No historical signed event or AnchorRecord is rewritten to add the extension.

The [existing demo PR][demo] at `ec6cfbaf901e6147f767bbe56132b1bb6211337a` is a candidate input for implementation
review, not a normative source. Its scope commitment and attempt/outcome rule must be assessed as demo contract
choices. Two implementations published by VSO do not establish organizationally independent verification.
This draft neither merges that PR nor asserts that it implements these proposed semantics.

OAP's ObservationScopeManifest and MAP's ScopeManifest are named in H-5. Their actual definitions and versioned
requirements must be obtained and mapped before adoption; equivalence cannot be inferred from their names.
The review must also assess TRC-005 relationships, INT-007 continuity, INT-009 recovery, and ERASURE effects.
Institutional observer independence and trustworthy observation remain separate assurance questions.

Existing K3 work remains a separate evaluation with its own agreed baseline. This proposal does not stop,
reissue, or silently migrate its fixtures or conclusions to a new VAP or VCP version.

## 9 Decisions needed before a normative proposal

The recommended next step is an opt-in experiment around evidence delivery, followed by a review of whether
the resulting requirements belong in the common framework, a capability, or a profile. The following decisions
remain open:

1. Formal proposal identifier, relationship to other pending work, target version, and affected levels.
2. Which uses require advance commitment, the cutoff and amendment rules, and accepted timing evidence.
3. Minimum assurances for expected-set sources and observation boundaries, including who can control both.
4. Disclosure policies and evidence obligations under which withholding can or cannot satisfy a check.
5. Wire contract and independent test vectors, including clock uncertainty and empty or unbounded sets.
6. Profile mapping, compatibility impact, migration process, review ownership, and actual adoption evidence.

A declaration makes commitments inspectable but cannot itself ensure source completeness. Proof of an
independently operated observer requires evidence about governance and control, not merely another key.

Before requesting external reproduction, publish synthetic evidence, verifier code, exact expected outcomes,
and limits together. Record internal execution separately from independently reported reproduction.
Passing the experiment does not adopt the proposal. Any normative change follows [section 10.3][process],
with a separate submission, review, deliberation, decision record, and release.

[h5]: https://github.com/veritaschain/vap-spec/blob/9465c722be9efae18622ac4f04896bb0e1ea53d7/spec/v1.2/VAP_Framework_Specification.md#L1486
[spec]: https://github.com/veritaschain/vap-spec/blob/9465c722be9efae18622ac4f04896bb0e1ea53d7/spec/v1.2/VAP_Framework_Specification.md
[deferred]: https://github.com/veritaschain/vap-spec/blob/9465c722be9efae18622ac4f04896bb0e1ea53d7/spec/v1.2/VSO-VAP-CHANGE-001.md#annex-c-deferred-items
[doc-sync]: https://github.com/veritaschain/vap-spec/blob/9465c722be9efae18622ac4f04896bb0e1ea53d7/DOC-SYNC.md#6-vap-spec-main--merge-of-the-cab-errata-and-this-doc-sync
[demo]: https://github.com/veritaschain/vap-spec/pull/1
[process]: https://github.com/veritaschain/vap-spec/blob/9465c722be9efae18622ac4f04896bb0e1ea53d7/spec/v1.2/VAP_Framework_Specification.md#103-change-management
