# Proposed VAP change-control preparation

**Status: discussion draft; not adopted and not effective.**
**Prepared:** 11 November 2026 (JST). **Formal procedure ID:** unassigned.
**Decision authority, review start/end, electorate, quorum and effective date:** not assigned.

This document prepares reviewable materials for the existing VAP change path.
Publishing or merging it neither grants authority nor starts a normative review
clock. It does not replace [VAP v1.2 §10.3][spec], change §1.7 precedence,
register a profile, or adopt any technical proposal.

## 1. Current baseline and unresolved process details

The current specification is VAP v1.2.0 Draft 3, including the 5 November 2026
editorial erratum: SHA-256
`a35d5e082fd4b2f9921a78b1a71df263018320375e09fa18cf81533a18a19998`.
The source snapshot reviewed for this preparation is
[`1ce71a66f55d9a20728213b7c3a8bb79270ae579`][baseline].

Section 10.3 already specifies proposal submission, **30 days of public
review**, Technical Committee deliberation, approval by **two-thirds majority**,
and release of the change as a normative annex. Those steps remain controlling.

The reviewed public tree does not supply an operational record that resolves
the following items for the proposed next change. They are required decision
inputs, not facts invented by this draft:

| Decision input | Record needed before an adoption claim |
| --- | --- |
| Authorized maintainer and Technical Committee | Names or public identifiers, authority and applicable terms |
| Voting eligibility, denominator and quorum | A published rule consistent with §10.3, including abstentions, recusals and conflicts of interest |
| Formal proposal register | Reconcile existing/private assignments before assigning a new identifier or the scope of CHANGE-002 |
| Review opening | Public URL, immutable proposal revision/hash, UTC start and earliest permissible close |
| Comment handling | Public disposition log, unresolved objections and the effect of substantive revisions on review timing |
| Decision and release | Recorded deliberation/vote, exact accepted diff, version, date, digests and compatibility/migration decision |

Repository merge permission does not establish Technical Committee membership.
Silence, passing tests, a draft PR and a maintainer merge provide no voting
evidence. This preparation does not assert that any committee
deliberation, ballot or approval occurred.

## 2. Proposed intake package

An editor would prepare one package per proposed decision, containing:

1. A stable candidate reference, proposer, scope and purpose; formal ID and
   release target remain unassigned until an authorized record supplies them.
2. An exact baseline and affected clauses; existing requirements, proposed
   replacement text and explanatory material are distinguished.
3. A classification: editorial correction, implementation-only repair,
   normative change, or profile/capability registration or status change.
4. Compatibility analysis for stored bytes, signatures, schemas, profiles,
   verifier verdicts, conformance levels and fixed distributions.
5. A bounded test plan with positive and negative cases, source/version pins,
   actual execution records and any untested cases or disagreements.
6. Primary references and a disposition log linking every material review
   comment to a decision or an unresolved item.
7. A release/migration plan and a list of disclosures that must change only
   after the authorized decision is recorded.

Editorial corrections must not silently change a normative requirement.
Implementation fixes may repair experimental code within its own documented
contract; that repair does not adopt a corresponding framework requirement.
Profile registration and changes to the §4.5.2 vocabulary require their own
recorded decision. An external proposal's chosen label is not registration.

## 3. Proposed public-review record

Use the following unfilled template after the process details in §1 are
resolved. Dates must remain unfilled until the review is actually opened.

| Field | Value |
| --- | --- |
| Formal proposal ID / authorized register entry | Not assigned |
| Reviewed baseline / exact candidate revision and digest | To be supplied |
| Public discussion URL | To be supplied |
| Authorized review opener | To be supplied |
| Public review start (UTC) | Not opened |
| Earliest close (UTC), at least 30 complete days later | Not scheduled |
| Material revision / review-clock disposition | Not applicable yet |
| Technical Committee / eligible voters / quorum rule | Not established in this record |
| Deliberation and individual vote record | Not held |
| Two-thirds calculation and conflict/recusal handling | Not performed |
| Accepted text / remaining objections | No text accepted |
| Release version, effective date and immutable artifacts | Not assigned |

A proposed operating rule is to calculate the earliest close as the actual
public opening time plus 30 complete 24-hour days, using UTC. A substantive
change would require a documented decision about reopening the full review
period before it can enter a ballot. These operating details remain proposals;
§10.3's 30-day minimum cannot be shortened by this document.

VCP and VAP are separately governed specifications. A VCP proposal's review
window or vote does not open, close or approve a VAP proposal. In particular,
the VCP-CP-2026-002 process does not supply missing VAP adoption evidence.

## 4. Preparing CHANGE-002 without assigning its scope

The [candidate register](../proposals/CHANGE-002-CANDIDATES.md) separates
subjects already deferred by CHANGE-001 Annex C from newer unadopted work.
It is an administrative review aid, not the formal CHANGE-002 proposal.

The next concrete steps are to reconcile the register, publish the responsible
governance record, select a coherent technical scope, prepare exact replacement
clauses and compatibility tests, and then open the required public review.
If the prerequisites remain unresolved, the work remains unadopted discussion
material. This document supplies no interim authority to bypass them.

[spec]: ../spec/v1.2/VAP_Framework_Specification.md
[baseline]: https://github.com/veritaschain/vap-spec/tree/1ce71a66f55d9a20728213b7c3a8bb79270ae579
