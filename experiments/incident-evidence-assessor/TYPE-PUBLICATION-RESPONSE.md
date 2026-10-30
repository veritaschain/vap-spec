# Publication, incident-response and cross-party input types

Experimental application assessment only. These records are not VAP/CAP events,
conformance results, editorial decisions, enforcement controls or legal findings.
All records use the envelope, separate evaluator trust and signature procedure in
[CONTRACT.md](CONTRACT.md). Unknown or extra data fields are rejected. Every array
of strings contains distinct, nonempty strings. Times require an explicit timezone.

## Shared applicability

All ordinary records must match every field of the evaluator-pinned target subject.
The publication policy exception compares exactly `policy_id`, `policy_version`,
`policy_sha256` and `stage`; a policy can apply to several artifacts. Eligible
signatures must also satisfy the kind's role and expected issuer. An authentic but
inapplicable record is not evidence for this target.

An event time after its signed record time or the evaluation time cannot support
a positive observation. Signed times remain assertions, not independently verified
historical timestamps. The prototype verifies no external timestamp or anchor
format. Each finding lists its supporting record IDs.

`target.operation_at` means:

| Workflow | Meaning |
| --- | --- |
| Publication | Earliest time of this target submission operation; policy and approval are evaluated at this time |
| Information request | The exact `info_request.requested_at` value |
| Containment | The exact `containment_action.removal_observed_at` value; decision time may be earlier |
| Cross-party receipt | Time of the target request; its receipt cannot precede this time |

## Publication

Required target fields are `request_id`, `artifact_id`, `revision_id`,
`payload_sha256`, `disclosure_sha256`, `policy_id`, `policy_version`,
`policy_sha256`, and `stage`. Here `payload_sha256` identifies the submitted
document bytes. A component has exactly `{artifact_id, revision_id, sha256,
category}`; categories are `text`, `figure`, and `code`.

Activity values are `generation`, `substantive_editing`, `proofreading`,
`translation`, `code_review`, and `figure_generation`. These are declared activity
classes for this adapter, not classifier outputs or registered VAP/CAP values.

| Kind | Role | Exact data fields |
| --- | --- | --- |
| `publication_policy` | policy | `effective_from`, `effective_until`, `prohibited_activities` (activity array), `disclosure_categories` (category array), `approval_required` (boolean), `interpretation` (`resolved` or `unresolved`) |
| `publication_manifest` | collector | `observed_at`, `components` (nonempty component array, unique artifact IDs) |
| `publication_activity` | collector | `activity`, `observed_at`, `adoption_basis` (`observed_in_artifact` or `unresolved`), `included_in_artifact_sha256`, `component` |
| `publication_coverage` | collector | `scope` (`declared_editor_only` or `incomplete`), `from`, `until` |
| `publication_disclosure` | author | `categories` (category array), `prepared_at`, `text` (nonempty disclosure text) |
| `publication_declaration` | author | `activities` (activity array), `declared_at` |
| `publication_approval` | reviewer | `valid_from`, `valid_until`, `approval` (only `approved`) |
| `publication_dispatch` | gateway | `attempted_at` |
| `publication_receipt` | recipient | `received_at`, `status` (`received` or `accepted`) |

### Policy and artifact rules

`policy_sha256` is SHA-256 of the RFC 8785 canonical **complete policy data
object** above. It is the structured adapter-rule digest, not a claim to have
hashed or interpreted a publisher's original webpage. The issuer and evaluator
remain responsible for mapping the applicable policy into these limited rules.
Policy validity is a half-open interval: `effective_from <= operation_at <
effective_until`. A policy first recorded after the target operation does not
establish historical availability; this prototype holds applicability unresolved.
An unresolved interpretation never becomes a permission or violation finding.

The manifest must contain a text component with the target document's exact ID,
revision and digest. An activity contributes to a prohibited-use or incomplete-
disclosure assessment only when its full component tuple matches the manifest,
its inclusion digest matches the target, and adoption is explicitly observed.
Conflicting manifests leave inclusion unresolved. These checks compare signed
claims; they do not reconstruct the document bytes or independently prove that a
collector's inclusion claim is truthful. A model call without established adoption
does not establish use in the final submission.

The disclosure digest is SHA-256 of the UTF-8 `text`, without normalization.
Category coverage can expose an omission of observed figure/code assistance, but
it cannot establish the text's semantic accuracy or sufficient disclosure under a
real policy. A signed declaration remains self-declared evidence with unknown
completeness. No absent event proves human-only authorship.

Approvals use half-open validity intervals, must be recorded by the target
operation, and must match the exact target, including document and disclosure
digests and policy version. An otherwise matching approval for another revision,
payload or disclosure is retained as prior-version evidence. A currently bound
approval does not override a prohibited activity.

Dispatch and receipt cannot predate `operation_at`. A receipt cannot predate the
earliest matching dispatch when dispatch evidence is present. A separately
authenticated recipient receipt can be reported without a local dispatch record,
but remains a recipient assertion. `accepted` records only that recipient's
acceptance assertion, not policy compliance or a legal determination.

### Deliberately limited decision output

The only publication actions are `BLOCK` for a bound, effective prohibition and
observed adopted activity, or `REVIEW`. This prototype never emits automatic
permission or complete disclosure. The `publication_ready()` fixture exercises
positive policy, artifact, approval, preparation, dispatch and recipient-receipt
checks and intentionally remains `REVIEW`. Other dimensions expose those supported
facts separately; the helper name is not a readiness certification.

## Information requests and containment

Both branches require target `request_id`, `object_ids`, `provider_id` and
`tenant_id`. Containment also requires a matching target `account_id`.

| Kind | Role | Exact data fields |
| --- | --- | --- |
| `info_request` | reviewer | `questions` (nonempty string array), `requested_at`, `observation_cutoff`, `authority_basis` |
| `info_receipt` | recipient | `received_at`, `request_record_id` |
| `info_response` | recipient | `responded_at`, `request_record_id`, `status` (`complete` or `partial`), `answers` (nonempty array of `{question, answer}`, distinct questions) |
| `containment_action` | responder | `decision_at`, `removal_observed_at`, `authority_basis`, `source_account_id`, `urgency` (`urgent` or `routine`), `delay_justified` (boolean), `minimum_evidence_available` (boolean), `unavailable_material` (string array), `access_constraints` (string array), `retention_basis` |
| `containment_anchor_claim` | collector | `anchor_time`, `record_ids` (nonempty string array), `format`, `material_sha256` |

A request names the recipient through the evaluator-pinned `authorities.recipient`.
The requested time must precede the declared cutoff. Exactly one eligible request
is required for an unambiguous response assessment. Receipts and responses must
reference that record ID, match its full target, and not predate the request.
Answers must concern its declared questions.

The effective observation cutoff is the earlier of the requested cutoff and
`as_of`. Both a response's claimed event time and its signed record time must be
at or before that cutoff to count as available then. A later response is reported
separately; it does not rewrite the earlier no-response observation. If the
requested cutoff has not been reached, the output says no response observed as of
the evaluation rather than pretending the full window elapsed. A complete
response requires answers for every requested question and the corresponding
status; its answers remain recipient assertions. `requested_facts` remains
`UNKNOWN`. The `information_response()` control demonstrates this distinction.

`authority_basis` records an asserted mandate. Authenticating an expected reviewer
does not independently establish legal powers or compel a response. Silence does
not prove refusal, misconduct, non-use, or erasure.

A containment decision cannot follow its observed removal. The account and target
operation time must match. Missing minimum evidence requires an identified
`unavailable_material` gap. Multiple inconsistent records require review. The
urgent, no-justified-delay branch records the responder's authority assertion and
the preservation gap without requiring indiscriminate copying or delayed
containment. An availability assertion alone is not proof of preservation.

The anchor record is deliberately a **claim**, with a digest/reference to
unsupported external material. A later claimed anchor supports only the negative
conclusion that it cannot establish contemporaneous capture or reconstruct missing
history. `anchor_verification` is always `NOT_SUPPORTED`.

## Cross-party imported evidence

Required target fields are `request_id`, `provider_id`, `tenant_id` and `object_ids`.

| Kind | Role | Exact data fields |
| --- | --- | --- |
| `cross_provider_receipt` | provider | `received_at`, `statement` (nonempty text), `statement_scope` (nonempty string array) |
| `cross_anchor_claim` | collector | `anchor_time`, `format`, `material_sha256`, `record_ids` (nonempty string array), `party_ids` (nonempty string array) |

An authenticated, fully matching provider receipt can establish attribution under
the evaluator's trust assumptions. It does not establish statement truth,
universal coverage, or independently anchored matching between parties.
Unsupported anchor claims cannot change `xref_assessment=NOT_ESTABLISHED` or
`anchor_verification=NOT_SUPPORTED`. Lack of XREF does not make an otherwise
authenticated receipt false or worthless.

## Fixtures and runtime separation

`fixture_publication_response.build()` returns ten synthetic signed input/trust
pairs for PB-01 through PB-07, IR-01/IR-02 and XR-01. Fixture IDs exist only in test
support. Runtime modules read neither the catalogue nor expected outputs. The
fixture helpers use public deterministic test keys and are not identity onboarding
or evidence of external interoperability.
