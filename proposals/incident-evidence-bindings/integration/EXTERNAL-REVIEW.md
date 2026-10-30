# Bounded external review procedure

**Proposed handoff, informative and unadopted — 2026-10-30 JST.**
No reviewer has been appointed and no external result is asserted here.
This is a procedure for reporting a review, not a certification or an automatic independence decision.

Sections 1–7 retain the PR36 saved-evidence target and its 53-case review scope.
The [2026-10-31 retention addendum](#8-separate-retention-review--2026-10-31-jst)
routes the later PR40 experiment to a different source, capture and procedure.

Use [external-review-template.json](external-review-template.json) as a blank working
form. Its prefilled hashes identify the review target; they are not reviewer observations.
Empty arrays and null fields mean not recorded, not a successful check or an absence of conflicts.
When recording an actual review, replace the blank record_state with REVIEWER_STATEMENT
and fill the applicable fields. That label does not authenticate the statement.

## 1. Choose and record the question first

The default question is: can the reviewer recheck the fixed saved evidence and reproduce
the exact source-attributed report, while retaining its negative controls and limitations?
Select SAVED_EVIDENCE_RECHECK in the response only if that is the actual work performed.

FRESH_SYNTHETIC_LOCAL_RUN and DEPLOYMENT_EVALUATION are different scopes. A fresh run uses
the original pilot instructions and produces new local observations. Deployment evaluation
requires a separately scoped integration and evidence plan. Do not infer either from the
default offline recheck, or infer institutional incident reconstruction from any of them.
The template's expected archive hashes apply only to SAVED_EVIDENCE_RECHECK. For the other
scopes, retain those values as baseline references and record new artifact hashes and the
separately chosen source/target identity; do not compare a fresh capture to the old archive.

Before execution, record the reviewer, repository commit, trust/hash acquisition basis,
environment control, intended commands, review scope, expected result and failure criteria.
Keep that original plan with later corrections.

## 2. Fix the target and trust inputs

| Item | Expected identity |
| --- | --- |
| Repository | https://github.com/veritaschain/vap-spec |
| Reviewed source checkpoint | 3e621d522c4e5f536c850aa1e17821328680bfe6 |
| Kit archive SHA-256 | 06bdb46eade7ef5c2f041797007d1f7ef3aaa55ad17d88a90b28276be17d865f |
| Report archive SHA-256 | df971f32b68efc20bb76352076266747485bc9c49a26e248aec6af444a399360 |
| Report source-manifest SHA-256 | 1b6187b8d732e299de389e957601b96ad971f908f1b96cc6da11d2662e2efb3b |

Obtain the reviewed source and expected hashes outside the candidate archive. Record why
those sources are trusted. A matching download hash establishes equality to that expected
object; it does not establish truth of the recorded observations. Installing dependencies
is a separate operation before the offline check. Record actual interpreter and dependency
versions, platform, distribution origins and any restrictions or modifications.

The fixed toolchain pins dependency versions, not the complete environment or binary
distribution hashes. A Python audit hook is not an operating-system sandbox. Reviewers
choose an environment suitable for executing the identified source; candidate evidence
must not select executable entry points or dependency downloads.

## 3. Execute the saved-evidence path and retain the output

This section applies only to SAVED_EVIDENCE_RECHECK. For a fresh synthetic run,
record the separately selected pilot commands, new artifact identities and actions actually
performed. For deployment evaluation, use the separately recorded integration plan.

Use the checkpoint's [kit instructions][kit-run] and [report instructions][report-run]
([Japanese kit guide][kit-run-ja], [Japanese report guide][report-run-ja]).
All are pinned below to the reviewed commit. Existing Actions artifacts may expire;
the preserved capture in Git and existing build commands reconstruct the fixed kit.
Do not substitute a newly generated pilot capture for the original saved evidence.

1. Check the source checkout identity and the fixed source manifest.
2. Build or obtain the original kit and inspect its external expected hash.
3. Run the kit's verify command. An inspect result alone does not recheck the cases.
4. Build the report from that kit, then run the report's verify command using the external
   expected report hash. Preserve stdout, stderr, exit status and output bytes.
5. Inspect the selected cases below and record conclusions with source references.

The offline check should report 53 saved cases rechecked and actions_reexecuted=false.
These are expected outputs to compare with observations, not prefilled actual results.
The 37 reporter software tests are a separate optional scope item; do not report them as
executed merely because the retained CI record contains that count.

## 4. Minimum interpretation review

This is a finite suggested review set, not a replacement for the complete report.
For each finding, cite a report JSON Pointer and, where relevant, the underlying file/hash/pointer.

| Saved case(s) | Question to answer in the reviewer's own record |
| --- | --- |
| UL-10 | Are admission and final authorization distinguished after expiry? |
| UL-14 | Does the account preserve the managed denial and the observed outside-route acceptance? |
| LP-05 | Does disclosure leave the AI-use prohibition effective? |
| LP-09 / LP-10 | Does imported/replaced history leave origin and completeness unresolved? |
| LP-14 / LP-16 | Are unknown terminal outcome and outside-gate visible output retained? |
| LE-02 | Is an acknowledgement kept separate from completion? |
| LE-12 / LE-13 | Are readable copies/handles retained alongside scoped unlink? |
| LE-14 / LE-15 | Are after-only absence and later presence distinguished from an observed removal transition? |
| LE-18 | Does a provider statement without an observer remain a scoped attributed claim? |

Also inspect the [23-case crosswalk](COVERAGE.md). For UP-08, PB-04, PB-07,
ER-05, IR-01/02 and XR-01, explicitly record what the related local tests do not supply.

## 5. Record failures without changing the original target

Hash mismatch, dependency mismatch, unresolved identity, missing evidence, unexpected
output, unsuccessful command or an interpretation disagreement is a review finding.
Retain the original inputs and diagnostic output. Do not silently replace the expected
hash, change a captured observation, or count an unexecuted step as a success.

If producer assistance or a code change is needed, record its timing and content and
identify the revised attempt separately. A repaired run does not erase the failed run.
Assess the effect on any independence claim; do not automatically label an assisted
run independent. Do not require a reviewer to obtain a favorable result.

## 6. Return evidence and assess independence separately

Return a dated response with actual command lines, environment, exit statuses, computed
hashes, artifact locations/hashes, checked cases, findings, exclusions and unresolved items.
Record the reviewer-controlled conclusion separately from any maintainer response.
Names or a review identifier may be redacted for public distribution, with the reason recorded.

The [existing proposed criteria][counting] identify four independence factors:

- Involvement in building or running the subject.
- Control of the review environment.
- Ability to change or approve the conclusion.
- Financial and contractual relationships.

Record who assessed those factors, their evidence and unresolved questions. Different
keys, processes, agents, machines or CI providers do not themselves establish independence.
Payment alone neither establishes nor excludes independence. Publication of this
procedure does not adopt the proposed criteria or change any disclosed count.

The blank template defaults to NOT_ASSESSED for independence and NOT_GRANTED for
publication authorization. A filled form is a reviewer statement, not authenticated
evidence merely because it parses as JSON. If a signature or publication permission
is later supplied, retain its issuer, scope and independent verification basis.

## 7. Handling and publication

The public kit contains synthetic evidence, including synthetic article text. Use those
inputs for this review. A real integration's patient data, credentials, confidential
manuscripts or private account logs belong in separately authorized protected handling.
Do not attach them to a public issue or reuse public fixture keys for real identities.

The reviewer may return the form through a channel they explicitly choose. There is no
automatic transmission in this procedure. Before publishing a received result, preserve
the original response, check permission for the specific fields/artifacts, and retain
adverse findings and limitations. No response leaves review status pending or unrecorded;
it is not agreement, acceptance, rejection or evidence that the system is safe.

Any resulting claim must name the exact review scope. A saved-evidence recheck does not
establish the original events' truth, external deployment, universal deletion, complete
authorship attribution, conformance or legal compliance.

## 8. Separate retention review — 2026-10-31 JST

The PR40 retention adapter has a different preserved target: 16 synthetic cases,
an unchanged embedded erasure assessment and its own source manifest. Use
[RETENTION-REVIEW.md](RETENTION-REVIEW.md) for the fixed source checkpoint,
summary hash, commands, expected observations and return record for that scope.

The existing `external-review-template.json` identifies PR36 and its kit/report
archive hashes. Do not reuse those target identities for the retention capture,
append 16 results to its 53-case count or substitute the retention summary hash
for an archive hash. Record any retention review separately, including its actual
source, scope, trust/hash acquisition basis, commands and conclusions.

Publishing this addendum does not itself record a new adapter execution or appoint
a reviewer. A successful retention recheck evaluates saved signed inputs under supplied assumptions; it
does not inspect a provider, perform deletion or independently establish the
original statements' truth. The independence and publication considerations
above apply only after the actual activity and relationships are recorded.

[kit-run]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-recheck-kit/README.md
[report-run]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-review-report/README.md
[kit-run-ja]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-recheck-kit/RUN-ja.md
[report-run-ja]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/experiments/incident-review-report/RUN-ja.md
[counting]: https://github.com/veritaschain/vap-spec/blob/3e621d522c4e5f536c850aa1e17821328680bfe6/disclosures/2026-10-24-counting-criteria.md
