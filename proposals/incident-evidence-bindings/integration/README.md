# Incident integration and review handoff

**Informative, unadopted design guidance — original checkpoint 2026-10-30 JST;
retention addendum 2026-10-31 JST.**
Original evidence checkpoint: [PR36 merge, 3e621d522c](https://github.com/veritaschain/vap-spec/commit/3e621d522c4e5f536c850aa1e17821328680bfe6).
Separate retention checkpoint: [PR40 merge, 62d15f1b8d][retention-source].
Normative baseline: VAP v1.2 Draft 3. This guide introduces no conformance rule or certification.

[日本語](README-ja.md) · [23-case crosswalk](COVERAGE.md) ·
[Machine-readable crosswalk](coverage-map.json) ·
[External review procedure](EXTERNAL-REVIEW.md) ·
[Blank response template for PR36](external-review-template.json) ·
[Separate retention review](RETENTION-REVIEW.md)

The incident proposal, offline assessor, three local execution pilots and saved-evidence
report answer different questions. This handoff connects them without treating a related
local test as a completed deployment requirement. The proposed next step is a bounded
external review of the saved evidence, followed by separately scoped integration work.
No external review has been commissioned or completed by publishing this guide.

Sections 1–6 retain the PR36 baseline and its review scope. Section 7 records the
separate PR40 retention experiment. The baseline's gaps are not a current inventory
of every later experiment in this repository.

## 1. What is available at the PR36 checkpoint

| Layer | Existing deliverable | What the record supports |
| --- | --- | --- |
| Incident motivation | [Claim ledger](../INCIDENTS.md) | Attributed incident facts and explicit unknowns |
| Proposed behavior | [23 original cases][catalogue] | Natural-language assumptions and proposed application outcomes |
| Offline logic | [Assessor summary][assessor] | Structured synthetic translations of those 23 cases matched the named expectations |
| Measured local operations | [Upload][upload], [publication][publication], [erasure][erasure] | 17 local HTTP scenarios, 18 local publication scenarios and 18 local unlink scenarios |
| Preserved capture | [Fixed 53-case kit][kit] | Saved signatures, bindings, observations and original source can be rechecked |
| Review presentation | [Japanese][report-ja] / [English][report-en] / [JSON][report-json] | Source-attributed views, including missing frames, contradictions and unknowns |
| This handoff | [Crosswalk](COVERAGE.md) and [review procedure](EXTERNAL-REVIEW.md) | Related evidence, remaining conditions, and a way for a reviewer to return their own results |

These counts concern different layers. They are not additive security successes, and
53 measured local scenarios do not establish all assumptions in the 23 original cases.
The catalogue's original not-executed marker is preserved; later assessor results and
local operation results have their own provenance.
The three pilots are separate experiments: the upload receiver retains measurements and
receipts, while the erasure pilot uses a new local object store. They do not establish one
joined upload-to-retention-to-deletion lifecycle.

The report checkpoint passed 37 software test methods and rechecked all 53 saved cases
on Python 3.12.15 and 3.14.9. The [retained CI record][ci-record] identifies the original
implementation run and downloaded bytes; the [PR36 main run][main-run] confirms the
merge checkout. Those are recorded same-controller executions, not executions performed
by this documentation update or independent reproduction.

## 2. Incident facts and engineering implications

The [incident ledger](../INCIDENTS.md) remains the detailed fact register.

- **Bayview:** hospital-attributed reporting supports an unapproved upload and a later
  request for provider-side deletion. It does not establish absence of all audit logs
  or completed provider erasure. Hospital notice text was not independently retrieved.
  [Reporting][bayview]
- **Dartmouth:** the committee examined enterprise Claude logs; requested personal-account
  logs were unavailable to it. It distinguished disclosure rules, prohibited AI use and
  a case where changing policy and available evidence prevented a violation finding.
  [Committee report, pp. 2–5][dartmouth-report]

The engineering inference is to bind authorization to the actual operation, retain
scope and uncertainty, and connect disclosure to the final submitted artifact and
applicable policy. It is not a finding about either institution's technical controls,
nor a claim that this implementation would necessarily have prevented those incidents.

The two supplied background memos informed the questions about observation boundaries
and legal overclaiming. Their historical news, regulatory dates, market figures and
legacy citation identifiers are not used as new factual authority in this handoff.

## 3. Relationships that must stay explicit

The [complete crosswalk](COVERAGE.md) addresses every original proposal case at
the PR36 snapshot. In particular, UP-08 below describes the original upload pilot;
it does not assess later collector experiments. These baseline differences remain
relevant when selecting the evidence for a deployment pilot:

| Original question | Related local evidence | Condition still unestablished |
| --- | --- | --- |
| UP-05 / UP-07: denied transfer and uncovered routes | UL-14 deliberately bypasses the managed gateway | A scoped direct bypass is not organization-wide route coverage, and an observed action is not the same as an unobserved possible action |
| UP-08: unavailable collector | UL-06 injects a local journal claim failure | The pilot uses require_collector=false; real collector availability, loss and recovery were not exercised |
| PB-04: AI involvement in figures or code | LP-17 rejects omitted recorded assistance in text | The publication pilot has no figure, code or supplement workflow |
| PB-07: remote delivery and acceptance | LP-14 retains unknown outcome despite a visible local file | A local filesystem write supplies no publisher transport, receipt or editorial acceptance |
| ER-05: independent deletion review | LE-01 and LE-18 separate observed removal and provider claims | Same-controller keys/processes supply no independent review of external storage |
| IR-01 / IR-02 / XR-01 | Offline assessor scenarios | No measured information-request transport, real incident containment/preservation procedure or independently anchored cross-party exchange |

These are design judgments about the checked source and evidence, not quantitative
coverage scores. A local operation and an offline assessment may deliberately have
different states; the crosswalk does not rewrite either result to make them match.

## 4. Three review scopes

| Scope | Reviewer's activity | Result can support |
| --- | --- | --- |
| Saved evidence recheck | Obtain a reviewed checkout and external expected hashes; rerun the existing offline kit and reporter; inspect selected negative controls | That reviewer reproduced the stated evidence checks on the identified bytes and environment |
| Fresh synthetic local run | Separately run the original three pilot suites in the reviewer's own environment and retain new outputs | New local observations within the pilots' declared scope; different keys/times mean old evidence hashes need not match |
| Deployment evaluation | Design a separately authorized integration with actual route, tenant, identity and retention controls | Only the claims supported by that deployment's measured scope and findings |

Choose one scope and record it before running. A saved-evidence recheck does not perform
the original operations. A fresh local run does not inspect an external AI provider.
An independently operated recheck can become evidence for a scoped independent result;
it does not automatically become an external implementation or a conformance finding.

The first scope is ready for a reviewer to attempt using [the handoff procedure](EXTERNAL-REVIEW.md).
The other scopes have different inputs and acceptance evidence.

## 5. Proposed integration priorities and exit evidence

These are recommendations for planning, not new normative requirements.

| Priority | Bounded work item | Evidence to collect before claiming that item complete |
| --- | --- | --- |
| 1 | One controlled egress route and tenant | Route/account inventory; destination enforcement; sender/receiver evidence for allowed, denied, changed-payload, wrong-tenant and explicitly authorized bypass probes; uncovered routes retained as gaps |
| 1 | Collector availability on that route | A real collector prerequisite; outage before intent, lost acknowledgement, recovery and retry tests; evidence showing when dispatch did or did not occur |
| 2 | Final publication package | Bind manuscript, figures, code and supplements; capture policy by stage; verify post-approval changes and omitted assistance; retain actual submission/disclosure receipt if the integration supplies one |
| 2 | Scoped provider deletion | Bind transferred bytes to the actually retained object/version and deletion request; retain provider receipts and precise storage exclusions; evaluate copies and contradictory later observations; obtain a separately controlled assessment if independence is claimed |
| 3 | Information requests and preservation | Authorized request transport and cutoff tracking; controlled containment with missing preservation; evidence retention/access decisions and unresolved facts |
| 3 | Identity, anchoring and operational governance | Deployment-controlled keys and roles, rotation/revocation behavior, protected evidence access, external anchor verification and declared coverage; separate conformance mapping if one is pursued |

For every deployment task, pre-record the claim, allowed environment, expected observations,
failure criteria and retained artifacts. A failure, ambiguity or inaccessible dependency is a
reportable result. Changing a scenario or expected result after observing a mismatch requires
a separately identified revision and a preserved earlier result.

## 6. Decisions not made by this handoff

No external institution, reviewer or production service is selected. No email, review invitation
or external submission is sent. No reviewer statement, consent, acceptance or independent result
is prefilled as a completed fact.

The [existing proposed counting criteria][counting] remain proposed. Any future public
independence claim must separately disclose involvement in the work, environment control,
control of the conclusion, and financial/contractual relationships. A successful internal CI
run, a new key pair, a different process, or this guide does not resolve those factors.

The normative specification, fixed evidence and execution source keep their existing meaning.
Conformance, legal compliance, universal erasure, complete AI-use attribution and production
readiness are not established by this guide.

## 7. Retention addendum — 2026-10-31 JST

The [PR40 retention adapter][retention-adapter] adds a separately versioned offline
assessment around the unchanged erasure assessor. Its [retained internal record][retention-results]
reports 42 software test methods, 16 matched synthetic scenarios and 16 saved-evidence
rechecks. These figures refer to the adapter's prior recorded executions; this handoff
does not present them as newly executed tests or an external review. The 16 scenarios
are a separate set of synthetic inputs, not additional operations in the fixed 53-case capture or
new entries in the original 23-case catalogue.

| Implemented assessment | Boundary that remains |
| --- | --- |
| Separate attributed processing locations, training use, retention schedules and deletion evidence | Statements do not independently establish actual location, training use or transfer authorization |
| Compare an explicit timezone-bearing deadline with the pinned cutoff; retain unknown schedules and exceptions | Reaching a deadline never establishes deletion; missing starting events or calendar rules are not inferred |
| Match scoped completion claims by request and location; preserve later presence and multiple statements | Provider claims and collector statements do not themselves inspect external storage or establish independent review |
| Re-evaluate captured signed inputs and their complete reports | Supplied trust and hashes establish consistency under stated assumptions, not an external identity or timestamp anchor |

The remaining deployment work is to bind actual sent bytes to the retained object and
version, obtain attributable provider conditions and responses, establish the real
identity/role and clock assumptions, and observe the declared storage locations and
exceptions. A scoped independent assessment needs its own reviewer, method and evidence.
The adapter does not join the earlier pilots into an observed upload-to-deletion lifecycle.

Use the [separate retention review procedure](RETENTION-REVIEW.md) for the preserved
16-case capture at the PR40 source checkpoint. It identifies the source, summary hash,
commands, expected observations and information to record. The PR36 blank response
template contains different archive hashes and must not be used as the target record
for these 16 cases. Keep actual observations and any reviewer conclusion separate from
the producer's existing results and expected outputs.

[catalogue]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/proposals/incident-evidence-bindings/acceptance-cases.json
[assessor]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-evidence-assessor/results/summary.json
[upload]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-upload-pilot/README.md
[publication]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-publication-pilot/README.md
[erasure]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-erasure-pilot/README.md
[kit]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-recheck-kit/README.md
[report-ja]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-review-report/results/review-ja.md
[report-en]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-review-report/results/review-en.md
[report-json]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-review-report/results/review.json
[ci-record]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-review-report/results/ci-record.json
[main-run]: https://github.com/veritaschain/vap-spec/actions/runs/41008102580
[bayview]: https://www.beckershospitalreview.com/healthcare-information-technology/ai/johns-hopkins-alerts-3182-patients-after-worker-uploads-data-to-unapproved-ai-tool/
[dartmouth-report]: https://president.dartmouth.edu/sites/president/files/2026-10/Advisory%20Committee%20Report%20to%20President%202026-10-27.pdf
[counting]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/disclosures/2026-10-24-counting-criteria.md
[retention-source]: https://github.com/veritaschain/vap-spec/commit/62d15f1b8d3c46a1704acb7c0d5631622e1a5608
[retention-adapter]: https://github.com/veritaschain/vap-spec/blob/62d15f1b8d3c46a1704acb7c0d5631622e1a5608/experiments/incident-retention-adapter/README.md
[retention-results]: https://github.com/veritaschain/vap-spec/blob/62d15f1b8d3c46a1704acb7c0d5631622e1a5608/experiments/incident-retention-adapter/results/README.md
