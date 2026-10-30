# Proposal-to-implementation evidence map

**Informative and unadopted.** This document relates the 23 original proposal
cases to their separately recorded offline-assessor results and selected local
pilot observations. It identifies remaining integration conditions; it does not
certify coverage, authorize deployment or change any normative requirement.

The reviewed source snapshot is
[`3e621d522c4e5f536c850aa1e17821328680bfe6`][snapshot]. The
[machine-readable map](coverage-map.json) has format
`incident-integration-map/0.1`, retains `status: INFORMATIVE_UNADOPTED` and an
explicit `assessment_basis`, and fixes the raw bytes of its three inputs.
Every mapping is an interpretation of those inputs, with its reason and remaining
conditions recorded explicitly. Producing this map does not execute a case or
modify a frozen source, capture or result.

The original map and its remaining-condition descriptions stay fixed to PR36.
They are not a current inventory of later experiments; this includes UP-08's
description of the original upload pilot. The dated retention addendum below
identifies PR40 as a separate evidence set without changing the 23-entry JSON.

## Three different evidence levels

The [proposal catalogue][catalogue] remains an informative collection marked
`not-executed`: its given observations and expected assessments describe the
original proposed scenarios. The [assessor summary][assessor] records actual
offline evaluation of structured synthetic translations of all 23 cases. Its
matched expectations depend on those supplied records and trust assumptions.
The [review JSON][review] presents 53 saved cases from the separately measured
upload, publication and erasure pilots after source-bound offline rechecking.
Those three experiments have different interfaces and observation boundaries.

A proposal case, its offline translation and a related pilot case are therefore
not interchangeable. Neither 23 matched offline expectations nor 53 rechecked
captures is a deployment-success or security-success count. This map makes no
new finding about the real incidents and no claim of independent reproduction,
performed human review, complete external deletion or legal compliance.

| Input role | Fixed source | Raw-file SHA-256 |
|---|---|---|
| `catalogue` | [Proposal acceptance cases][catalogue] | `59db1059645bdfe632c7db6d707dd619b8bcfe00be36430f71ee6fa3e6bcee9b` |
| `assessor_summary` | [Recorded offline-assessor summary][assessor] | `48b44670371fd64ae6bd11701b5bd412dbea6f8b76aa48a3194c07e8d4a08493` |
| `review_json` | [Source-attributed 53-case report][review] | `0de419ece3f344b763122d0dfc69ec4649cf0867c3438e829f2e90031401a316` |

These hashes identify bytes relative to the reviewed snapshot. They are not
external anchors, identity enrollment or independent endorsements. The map uses
raw-file hashes consistently; it does not substitute the upload pilot's original
canonical-JSON export-hash convention for a raw-file digest.

## Reading a relationship

The JSON contains all 23 entries in the original catalogue order. Each
`catalogue_pointer` addresses that case in `source_refs.catalogue`; each
`assessor_result_pointer` addresses the actual matching result under the
assessor summary's `/results` array. Each `review_pointer` addresses a concrete
case under the review JSON's `/cases` array. The review row in turn retains its
original capture references, observations and assessor frames.

| Label used below | JSON relationship | Meaning |
|---|---|---|
| R | `RELATED_LOCAL_OBSERVATION` | A measured local case directly exercises a named aspect of the proposal. Its synthetic trust, local scope and remaining conditions still apply. |
| P | `PARTIAL_ANALOGUE` | The pilot illustrates a narrower or different mechanism, evidence basis, timing or operation. The stated difference prevents treating it as an execution of the full proposal scenario. |
| None | Empty `pilot_links` | No measured pilot equivalent is mapped. The offline result still exists; the row identifies the evidence needed for further integration. |

There are **27 selected links: 16 R and 11 P**, across 19 proposal entries.
Four entries deliberately have no pilot link: PB-06, IR-01, IR-02 and XR-01.
These are mapping inventories, not coverage percentages or readiness grades.
Repeated links do not create additional observations. The map is selective and
does not relabel every reliability scenario in the 53-case report as a separate
proposal requirement.

Status strings need not be equal across layers. For example, PB-03's offline
`REVIEW` and LP-02's `BLOCKED_WITHOUT_PUBLICATION` concern different decisions:
the assessor's evidence assessment and the local gate's release action. Preserve
the original fields and their times rather than converting them into one pass
or fail value.

## All 23 proposal cases

In the source-pointer column, **C** means the catalogue and **A** means the
assessor summary. Pilot pointers are relative to the review JSON. The full
`unmet_conditions` and `next_evidence` arrays are in the machine-readable map.
They describe work and observations still needed; they are not evidence that
those conditions have already been met.

| Proposal and requirement | C / A pointers | Selected pilot links and report pointers | Remaining condition and next evidence |
|---|---|---|---|
| [UP-01][catalogue] — unapproved destination | C `/cases/0`; A `/results/0` | R [UL-02][review] `/cases/1` | Establish the intended destination/purpose registry and actual managed-route boundary; retain bound policy and egress observations. |
| [UP-02][catalogue] — wrong tenant | C `/cases/1`; A `/results/1` | R [UL-03][review] `/cases/2` | Bind authenticated provider account/tenant identity to an authoritative approval; configured synthetic labels do not enroll a real account. |
| [UP-03][catalogue] — stale authorization | C `/cases/2`; A `/results/2` | R [UL-05][review] `/cases/4`; R [UL-10][review] `/cases/9` | Supply governed policy versions, effective intervals and clock assumptions; retain admission and final-gate decisions separately. |
| [UP-04][catalogue] — changed outgoing bytes | C `/cases/3`; A `/results/3` | R [UL-04][review] `/cases/3`; R [UL-09][review] `/cases/8` | Observe the intended serializer/transport and any receiver transformation; a digest fixes bytes without classifying sensitivity or granting permission. |
| [UP-05][catalogue] — transmission contradicts denial | C `/cases/4`; A `/results/4` | P [UL-14][review] `/cases/13` | Obtain authenticated in-scope egress for the same denied request and its override history. A separate direct-controller bypass is a different conjunction. |
| [UP-06][catalogue] — unknown remote outcome | C `/cases/5`; A `/results/5` | R [UL-07][review] `/cases/6`; P [UL-16][review] `/cases/15` | Establish provider status/idempotency and an authorized reconciliation decision. A lost response and local result-persistence failure are different failure mechanisms. |
| [UP-07][catalogue] — uncovered activity unresolved | C `/cases/6`; A `/results/6` | P [UL-14][review] `/cases/13` | Declare coverage and retain uncertainty where observations are absent. UL-14 positively observes a bypass; UP-07 does not. |
| [UP-08][catalogue] — required collector unavailable | C `/cases/7`; A `/results/7` | P [UL-06][review] `/cases/5` | Exercise the actual required-collector prerequisite. UL-06 concerns a local journal rule while the signed policy uses `require_collector=false`. |
| [ER-01][catalogue] — request only | C `/cases/8`; A `/results/8` | R [LE-03][review] `/cases/37` | Establish real provider delivery separately if available; preserve the exact requested objects, versions and locations without inferring receipt. |
| [ER-02][catalogue] — acknowledgement only | C `/cases/9`; A `/results/9` | R [LE-02][review] `/cases/36` | Establish actual queue semantics and any later scoped completion or exception. The local acknowledge-only mode does not later resume its task. |
| [ER-03][catalogue] — scoped provider claim | C `/cases/10`; A `/results/10` | R [LE-01][review] `/cases/35`; R [LE-12][review] `/cases/46`; R [LE-13][review] `/cases/47` | Obtain attributable provider scope and domain-specific observations; retain readable copies/handles and unknown excluded-domain outcomes. |
| [ER-04][catalogue] — mismatched receipt | C `/cases/11`; A `/results/11` | P [LE-05][review] `/cases/39` | Distinguish an authentic wrong-target receipt from completion of the intended target. LE-05's rejected wrong-tenant probe accompanies a separate valid local operation. |
| [ER-05][catalogue] — independent scoped review | C `/cases/12`; A `/results/12` | P [LE-01][review] `/cases/35` | Establish actual reviewer independence, evidence custody, method, time, scope and limitations; same-controller readback is not that review. |
| [PB-01][catalogue] — disclosure does not override prohibition | C `/cases/13`; A `/results/13` | R [LP-05][review] `/cases/21` | Obtain the real venue's applicable policy/exception and bind its decision to the artifact and observed activity; the pilot policy is synthetic. |
| [PB-02][catalogue] — incomplete provenance | C `/cases/14`; A `/results/14` | R [LP-09][review] `/cases/25`; P [LP-10][review] `/cases/26` | State import/collaborator collection limits. LP-10 retains earlier simulated AI activity, unlike the proposal's no-AI-event premise; neither establishes human-only origin. |
| [PB-03][catalogue] — changed approved revision | C `/cases/15`; A `/results/15` | R [LP-02][review] `/cases/18`; R [LP-03][review] `/cases/19` | Bind actual final article, disclosure, policy and destination to authorization; observe and reassess any publisher-transformed or resubmitted version. |
| [PB-04][catalogue] — figure/code disclosure omitted | C `/cases/16`; A `/results/16` | P [LP-17][review] `/cases/33` | Add evidence for final figure/code components and their inclusion. The text-only omission case does not implement those attachment types. |
| [PB-05][catalogue] — stage-dependent ambiguity | C `/cases/17`; A `/results/17` | P [LP-12][review] `/cases/28` | Preserve use/submission/revision/publication policies and resolve precedence through an authorized interpretation; the local case has a single publication-stage rule. |
| [PB-06][catalogue] — self-declaration | C `/cases/18`; A `/results/18` | None | Attribute an author-only declaration without turning it into observed activity; record corroboration limits and unresolved completeness. |
| [PB-07][catalogue] — no publisher receipt/acceptance | C `/cases/19`; A `/results/19` | P [LP-01][review] `/cases/17`; P [LP-14][review] `/cases/30` | Observe an actual destination submission and its separately attributed receipt/acceptance; a local file or filesystem receipt supplies neither. |
| [IR-01][catalogue] — no response by cutoff | C `/cases/20`; A `/results/20` | None | Record an authorized external information request, delivery/receipt, cutoff and responses; absent response leaves facts and reasons unresolved. |
| [IR-02][catalogue] — urgent containment with preservation gap | C `/cases/21`; A `/results/21` | None | Record proportional preservation limits, authority and actual account-history removal without unjustified delay or compelled copying; later anchoring cannot recover missing history. |
| [XR-01][catalogue] — imported receipt is not XREF | C `/cases/22`; A `/results/22` | None | Establish participating parties' independently anchored corresponding records and matching/reconciliation rules; receipt authenticity alone does not establish XREF. |

## Differences that must survive an implementation handoff

### A denial, an unobserved route and an observed bypass

UP-05 assumes a separately authenticated transmission observation for the same
denied request inside the declared monitoring scope. UL-14 instead measures a
separate direct controller request to an intentionally unauthenticated receiver
after the gateway refused its own route. UP-07 assumes no observation resolving
the uncovered path; UL-14 has affirmative bypass evidence. Its partial links
preserve these different premises. The [upload boundary][upload-boundary] and
the report's original observations remain the controlling descriptions.

UP-08 is also not a renamed storage-failure case. The upload pilot deliberately
uses `require_collector=false` and separately requires a local durable journal
claim. UL-06 measures failure of that additional local rule. A deployment that
requires collector availability needs evidence for that actual prerequisite;
this map does not assert that the pilot already measured it.

### Scoped removal and independent review

ER-04's only available receipt is authentic but binds a different object and
tenant, leaving the target unresolved. LE-05 rejects a wrong-tenant probe after
a valid measured local operation, and its valid completion evidence remains.
Those different evidence sets cannot be collapsed into an identical assessment.

ER-05's independent-review result exists in the offline synthetic translation
under its supplied assumptions. The [erasure pilot][erasure-boundary] instead
declares one controller for provider and observer; it produces no `erasure.review`
record. Its scoped attestation, retained readable controls and same-controller
readback do not establish actual reviewer independence or universal deletion.

### Publication evidence has distinct origins, stages and destinations

PB-04 requires figure and code provenance bound to the submitted component
versions. LP-17 detects a disclosure omission in a text-only editor. Figures and
code attachments are unsupported by the [publication pilot][publication-boundary].
PB-05 also exceeds the local case: a single unresolved publication-stage rule
does not demonstrate policy precedence across drafting and later submissions.

PB-06 concerns an attributed self-declaration without contemporaneous activity
corroboration. Instrumented edit history, a structured disclosure and an
author-only assertion have different evidence bases, so no measured equivalent
is assigned. A signature can attribute the declaration while its completeness
remains unknown.

PB-07 concerns an external publication destination. LP-01 measures a local HTML
file with its disclosure; LP-14 retains an unknown local result despite a visible
file. Neither is an external submission or publisher receipt. The pilot does
not emit core `publication_dispatch` or `publication_receipt` records for local
filesystem operations, and editorial acceptance remains a separate question.

### Investigation and cross-party participation still need measured integration

IR-01 and IR-02 have offline results but no measured information-request or urgent
account-history-containment pilot. An object unlink is not an account-history
removal workflow. Preservation guidance does not compel indiscriminate copying
or justify delaying urgent authorized containment. Source, time, authority,
unavailable material and remaining unknowns must stay explicit.

XR-01 likewise has no measured pilot equivalent. An imported authentic provider
receipt is attributed evidence; it does not establish participating parties'
independently anchored corresponding records. The [offline assessor][assessor-limits]
does not implement positive XREF or external-anchor verification. Separate keys
or local processes do not establish organizational independence.

Finally, these mappings do not join the three pilots into one data lifecycle.
The upload receiver retained measurements and receipts, not uploaded payload
files. The erasure pilot uses a new local object store. Any future relationship
between sent bytes, a retained object/version and a deletion request needs its
own explicit binding and observations. The machine-readable `next_evidence`
fields identify evidence still to obtain; they are not present deployment facts.

## Retention addendum — 2026-10-31 JST

The separate [PR40 source checkpoint][retention-source] contains the
[retention adapter][retention-adapter] and its [preserved execution record][retention-results].
It evaluates provider retention statements and collector presence statements
alongside the unchanged erasure report. Its 16 synthetic cases do not extend the
23-case catalogue, the 27 selected links above or the fixed 53-case capture.
They do not measure new provider-side storage or deletion operations.

The following relationships describe this additional assessment logic. The case
references are relative to the preserved [retention case directory][retention-cases];
they are not pointers into the original 53-case review JSON.

| New cases | Additional question exercised | Evidence still needed for a deployment claim |
| --- | --- | --- |
| RT-01–03 | Do identical signed records keep their deletion assessment when only the cutoff crosses a stated deadline? | Actual completion evidence; reaching an attributed deadline alone does not supply it |
| RT-04 / RT-07 | Do an unknown trigger or missing schedule remain unresolved despite processing-region and training declarations? | Attributable conditions, their effective version, starting event, timezone and calculation rule; actual processing/use evidence where claimed |
| RT-05 / RT-16 | Does partial versus full location coverage of the same request affect follow-up while leaving reached-deadline review required? | Real request/object/version binding, provider claim scope and observations of declared locations and excluded copies |
| RT-06 / RT-13 / RT-15 | Are later scoped presence, out-of-scope presence and pre-request presence interpreted distinctly alongside a historical synthetic review? | Actual observation method, custody and time; separately established reviewer independence; evidence distinguishing retention from restoration or recreation |
| RT-08–10 | Are wrong-tenant, modified-signature-data and future-record statements excluded from applicable retention evidence? | Real identity and role enrollment, key lifecycle, target identity and time assurance |
| RT-11 / RT-12 | Are exceptions and multiple statements preserved for review? | Evidence of applicable terms and exceptions; an authorized resolution of supersession or conflict |
| RT-14 | Are equivalent timezone-bearing deadline instants compared equally? | Evidence establishing the relevant timezone and deadline; a date-only notice does not supply an instant |

Each saved case preserves its original input, synthetic trust, report and finite
expectations. Useful paths include `/report/statements`, `/report/record_checks`,
`/report/presence_reports`, `/report/follow_up_reasons` and
`/report/erasure_report/assessments`. The terms reference and hash remain signed
assertions; this program does not fetch or authenticate the underlying terms
document. A presence record attributes the collector's statement without making
the program an observer of external storage.

Use [the separate retention review procedure](RETENTION-REVIEW.md) to recheck
those preserved records. Its source and summary identity differ from the PR36
kit and report. The existing machine-readable map and blank review template
continue to identify their original targets. No independent result or new
execution is established by adding this explanatory crosswalk.

[snapshot]: https://github.com/veritaschain/vap-spec/commit/3e621d522c4e5f536c850aa1e17821328680bfe6
[catalogue]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/proposals/incident-evidence-bindings/acceptance-cases.json
[assessor]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-evidence-assessor/results/summary.json
[review]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-review-report/results/review.json
[upload-boundary]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-upload-pilot/README.md
[erasure-boundary]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-erasure-pilot/README.md
[publication-boundary]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-publication-pilot/README.md
[assessor-limits]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-evidence-assessor/README.md
[retention-source]: https://github.com/veritaschain/vap-spec/commit/62d15f1b8d3c46a1704acb7c0d5631622e1a5608
[retention-adapter]: https://github.com/veritaschain/vap-spec/blob/62d15f1b8d3c46a1704acb7c0d5631622e1a5608/experiments/incident-retention-adapter/README.md
[retention-results]: https://github.com/veritaschain/vap-spec/blob/62d15f1b8d3c46a1704acb7c0d5631622e1a5608/experiments/incident-retention-adapter/results/README.md
[retention-cases]: https://github.com/veritaschain/vap-spec/tree/62d15f1b8d3c46a1704acb7c0d5631622e1a5608/experiments/incident-retention-adapter/results/local-python-3.12/cases
