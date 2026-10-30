# Transfer and erasure record types

These types belong only to the experimental offline application assessor. They
are not VAP/CAP event schemas, core-verifier verdicts, enforcement actions or
legal findings. The runtime does not read the acceptance catalogue or case IDs.
The synthetic fixtures use public deterministic keys solely for local tests.

## Common requirements

The common envelope and evaluator-supplied trust configuration are specified in
[CONTRACT.md](CONTRACT.md). All supplied kind data is strictly validated before
authentication. Unknown keys, duplicate identifiers/list items, malformed times,
and incorrectly typed values are input errors. All times include a timezone.
Every validity interval is nonempty and half-open: `[start, end)`.

Only eligible authenticated records from the expected issuer and required role
can support an assessment. Except for policy records as described below, a
record must match **every target subject field**, including any optional fields
the evaluator supplied. Evidence for another object, request, revision, tenant,
account, destination or evaluation does not apply.

Recorded time must not exceed `as_of`. Event times cannot exceed their record
times. These checks use signed statements about time; this prototype does not
independently prove when an event or signature actually occurred.

## Transfer

Required target subject fields are `request_id`, `actor_id`, `provider_id`,
`endpoint`, `tenant_id`, `account_id`, `purpose`, `payload_sha256`, `route_id`,
`policy_id`, `policy_version`, `policy_sha256`, and `stage`. `operation_at` is the proposed
transfer time. A permit is valid only for its bound request and content.

| Kind | Role | Required data fields |
|---|---|---|
| `transfer.policy` | `policy` | `effective_from`, `effective_until`, `grants`, `require_collector` |
| `transfer.decision` | `gateway` | `decision`, `valid_from`, `valid_until` |
| `transfer.dispatch` | `gateway` | `dispatched_at` |
| `transfer.egress` | `collector` | `observed_at` |
| `transfer.coverage` | `collector` | `window_start`, `window_end`, `covered_routes`, `complete`, `dispatch_observed` |
| `transfer.collector_health` | `gateway` | `checked_at`, `available`, `durable_acknowledged` |
| `transfer.timeout` | `gateway` | `timed_out_at` |

The policy `grants` array can be empty. Each grant is an exact tuple of seven
nonempty strings: `actor_id`, `provider_id`, `endpoint`, `tenant_id`, `account_id`,
`purpose`, and `route_id`. All seven values must match; provider approval alone
does not authorize other accounts or purposes. Duplicate grants are rejected.
`require_collector` is a boolean.

A policy record uses the explicitly restricted binding fields `policy_id`,
`policy_version`, `policy_sha256`, and `stage`. The digest must equal SHA-256 of RFC 8785 JCS
of the **complete policy data object**. The policy must have been recorded by
the proposed operation and cover that time. A changed policy needs a new digest
and an evaluator-approved target; old record signatures do not refresh it.

Decision values are `permit` or `deny`. Decisions must have been recorded by
the assessed action and be effective at that time. Among applicable decisions,
the latest recorded time is used; conflicting decisions at that same time require
review. A policy grant and a fully bound permit are both needed for `ALLOW`.
An explicit bound denial can support `DENY` without promoting an unknown policy
to a verified current policy. A known registry rejection also yields `DENY`.
The assessor reports what the supplied evidence supports; it dispatches nothing.

Coverage contains boolean `complete` and `dispatch_observed`, plus distinct
nonempty route strings in `covered_routes` (the array may be empty). Its window
must cover `operation_at`, end no later than the collector's record time, and be
established by `as_of`. `NOT_OBSERVED` requires a complete matching route claim
with no conflicting recorded dispatch, egress or applicable incomplete-coverage
claim. This prototype has no implicit override rule for conflicting collector
statements. It says nothing
about activity outside that route. A broader-activity query remains incompletely
covered even if the managed route has complete evidence.

Collector-health booleans are scoped to `checked_at == operation_at`; the
prototype does not extrapolate a stale health check. Unavailable collection cannot
simultaneously claim durable acknowledgement. If policy requires collection,
known unavailability yields an application-route `BLOCK`; missing evidence yields
review. Neither assessment establishes that other routes were stopped.

Direct matching dispatch or egress observations survive unrelated evidence gaps.
The applicable policy, decision, and required collector health are re-evaluated
at the observed event time; a conflicting denial or known collector-prerequisite
failure yields `VIOLATION`. `proposed_transfer_authorization` preserves the
assessment at `operation_at`; `observed_action_authorization` separately reports
the evidence applicable to observed actions. An expired permit or missing
prerequisite evidence cannot authorize a later observed dispatch; such a gap
changes an overall `ALLOW` to `REVIEW`, without claiming the absence of missing
authorization records. An observed dispatch is distinct from
provider receipt or processing. A timeout following dispatch yields unknown
remote outcome and reconciliation before retry. The current type set does not
model provider transfer receipts or supply a retry/idempotency guarantee.

## Erasure

Required target subject fields are `request_id`, `provider_id`, `tenant_id`,
and nonempty `object_ids`. `operation_at` is the deletion-request time. The
requester is the externally trusted `responder` issuer, not a role asserted by
the evidence itself. Object IDs are synthetic or opaque references, not raw
personal information.

| Kind | Role | Required data fields |
|---|---|---|
| `erasure.request` | `responder` | `requested_at`, `requested_locations` |
| `erasure.acknowledgement` | `provider` | `request_record_id`, `acknowledged_at`, `queue_state` |
| `erasure.provider_attestation` | `provider` | `request_record_id`, `completed_at`, `locations`, `exclusions` |
| `erasure.review` | `reviewer` | `request_record_id`, `attestation_record_id`, `method`, `evidence_record_ids`, `window_start`, `window_end`, `locations`, `limitations`, `conclusion` |

`requested_locations` and `locations` are nonempty arrays of distinct nonempty
strings. `exclusions` is a distinct string array and may be empty; an attestation
cannot both include and explicitly exclude the same location. An empty exclusion
list never means every possible copy or derivative is covered.

Acknowledgement `queue_state` is `received` or `queued`, never a completion
signal. It must reference an eligible matching request and follow the request
time. A provider attestation has the same request-reference and time requirements;
its claimed locations must be a subset of the requested locations. It attributes
a scoped deletion claim to the provider, rather than independently proving it.
Neither an acknowledgement nor an attestation establishes universal completion.

A review references a qualifying request and provider attestation, and cites both
among nonempty `evidence_record_ids`. Every cited record must be eligible, bound,
and established by the review's evidence cutoff. `method` is nonempty descriptive
text; `limitations` is a nonempty array. `conclusion` is `deletion-observed` or
`inconclusive`. The review window starts no earlier than the request, contains
the attested completion time, and ends no later than the review record time or
`as_of`. Reviewed locations cannot exceed the provider's attested locations.

The reviewer must belong to an externally trusted organization different from
**both** the provider and requester. Missing or ambiguous organization mappings
cannot support independent-review status. A different key alone is insufficient.
The code verifies attribution, links, scope and chronology of a reviewer report;
it does not execute the review method or independently inspect remote storage.
An otherwise applicable inconclusive review prevents promotion to an unqualified
independent-review result, even if another qualifying review reports completion;
both reports remain in the findings. This conservative combination is independent
of the records' input order.

Valid scoped review evidence yields
`INDEPENDENTLY_REVIEWED_WITHIN_DECLARED_SCOPE` and
`SUPPORTED_WITHIN_REVIEW_METHOD_AND_LIMITATIONS`. Outcome outside that scope
remains `UNKNOWN`, including backups, unobserved replicas, downstream recipients,
training derivatives or any other uncovered storage. No output is a legal
compliance determination or a guarantee of irreversible universal erasure.

The current experimental type set does not model provider refusal, an explicit
finding of non-deletion, legal holds, or arbitrary contradictory external material.
Unsupported record kinds or fields are rejected, rather than silently interpreted
as evidence of success. The absence of such a record never establishes that no
contradictory evidence exists. The catalogue covers only the stated scenarios.
