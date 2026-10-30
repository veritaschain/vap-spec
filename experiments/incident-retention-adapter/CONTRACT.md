# Retention evidence adapter — implementation contract

**Version 0.1.0; experimental, informative and unadopted.** This is an offline
application adapter. Its record names and report values are not normative VAP/CAP
events, conformance decisions, enforcement actions or legal findings.

## 1. Composition with the existing assessor

The input has exactly these fields:

```json
{
  "format": "retention-evidence-input/0.1",
  "erasure": {},
  "retention_records": []
}
```

`erasure` is a complete, unchanged `incident-evidence-input/0.1` package with
workflow `erasure`, as defined in the existing
[assessor contract](../incident-evidence-assessor/CONTRACT.md) and
[erasure types](../incident-evidence-assessor/TYPE-TRANSFER-ERASURE.md#erasure).
The adapter calls the existing assessor on that package without adding or
rewriting its records.

The separately supplied trust wrapper has exactly these fields:

```json
{
  "format": "retention-evidence-trust/0.1",
  "erasure_trust": {}
}
```

`erasure_trust` is the original `incident-evidence-trust/0.1` configuration. It
pins the evaluation ID, erasure workflow, observation cutoff, complete target
digest and trusted keys. Its synthetic mode requires explicit
`allow_synthetic=True` or `--allow-synthetic`. A producer's inclusion of a trust
file in an exported case does not independently establish that trust.

The target subject includes at least `request_id`, `provider_id`, `tenant_id`,
`account_id`, nonempty `object_ids` and `payload_sha256`. Additional subject
fields permitted by the original contract are preserved and compared too.
Every retention binding uses the complete subject field set. A verified
signature for another account, object set, request, version reference or other
bound value cannot support the target's retention assessment.

Unknown fields and record kinds, malformed values, duplicate JSON keys or record
identifiers, and unsupported formats are input errors. Missing evidence remains
an evidentiary gap. Do not reinterpret unsupported material as a positive result.
Record identifiers are unique across both the original and retention record
sets. The wrapper limits each set to 256 records and each input/trust document
to 8 MiB under its parsing/canonicalization checks.

## 2. Signed retention records

Each envelope is `{algorithm, key_id, body, signature}`. The algorithm is
`Ed25519`; the signature is lowercase hexadecimal encoding of 64 bytes. The
body is `{record_id, evaluation_id, kind, issuer, recorded_at, binding, data}`.

Signed bytes are UTF-8 `incident-retention-adapter/0.1`, one zero byte, then
RFC 8785 JCS of exactly `{algorithm, key_id, body}`. The domain differs from the
old assessor's domain. Record kind, issuer, target binding and all typed data
are covered by the signature.

The existing evaluator trust supplies the expected issuer for the required role,
key validity and organization mapping. A new record must have a valid signature,
expected issuer, authorized role, matching evaluation and applicable time. Its
binding is checked separately against every target subject field. A signature
result alone is not a target-applicability result.

Records with a future `recorded_at`, an untrusted key, an incorrect issuer/role,
or an inapplicable binding do not establish an applicable retention statement or
presence report. Their failed or inapplicable checks remain visible in the report.
Signed times remain source assertions; this experiment has no independent
historical timestamp assurance.

### `retention.statement` — provider role

The data object has exactly these fields:

| Field | Shape and meaning |
| --- | --- |
| `request_record_id` | Reference to the applicable original erasure request |
| `terms_ref` | Nonempty reference identifying the stated conditions |
| `terms_sha256` | Lowercase SHA-256 hexadecimal source commitment |
| `processing_locations` | Distinct nonempty location strings; an empty array means not reported |
| `training_use` | `reported-disabled`, `reported-enabled` or `not-reported` |
| `locations` | Nonempty array of distinct locations to which the retention statement applies |
| `schedule` | One of the two shapes below |
| `exceptions` | Array of `{location, reason, until}` objects, with `until` a timezone-aware timestamp or `null` |

The explicit-deadline schedule is:

```json
{"kind": "stated-deadline", "deadline": "2026-11-30T00:00:00Z"}
```

The unresolved schedule is:

```json
{"kind": "unknown", "reason": "The retention starting event is not established."}
```

These examples are synthetic contract illustrations. They are not timestamps
attributed to any actual incident.

All timestamps include a timezone and seconds, with at most microsecond
precision, following the original parser. Version 0.1 does not calculate a
deadline from a duration or infer an undisclosed start time, timezone or
calendar-day rule. If the evidence cannot establish a precise deadline under
this contract, use the explicit unknown schedule.

The request reference must resolve to an eligible, authenticated original
erasure request for this evaluation and complete target binding. Statement
locations must be within that request's scope, and the statement cannot have
been recorded before the referenced request record. Exception locations must
also be among the statement's locations. Their reasons retain their stated
scope; an unspecified end remains unspecified. At most 256 exceptions are
accepted, and duplicate exception objects are rejected.
Neither the existence nor expiry of an exception settles legal entitlement,
actual retention or completed deletion.

The terms reference and hash are part of the provider's signed statement.
The adapter does not fetch that reference or independently verify the content,
applicability or availability of the source document. Processing locations and
training settings are declarations, not direct measurements or authorizations.

### `retention.presence` — collector role

The data object has exactly these fields:

| Field | Shape and meaning |
| --- | --- |
| `request_record_id` | Reference to the applicable original erasure request |
| `observed_at` | Time of the claimed presence observation |
| `location` | One location within the requested scope |
| `method` | Nonempty description of the observation method |
| `limitations` | Nonempty array of distinct limitations |

The original request, full subject binding and location must apply. An
observation time cannot exceed its record time or the evaluator's cutoff.
Its key must have the collector role under the separately supplied trust.
The presence record cannot predate the referenced request record; this does
not independently establish when its described observation actually occurred.

This kind attributes a statement of presence to the collector. It does not
make the adapter an observer of external storage. Presence is evaluated at its
stated time and location; later restoration or recreation is not excluded.
No absent-object type or general all-copy inventory is introduced in version 0.1.

## 3. Deadline and follow-up semantics

Compare a supported stated deadline with the evaluator's pinned `as_of` using
timezone-aware instants:

| `deadline_state` | Meaning |
| --- | --- |
| `BEFORE_DECLARED_DEADLINE` | The cutoff precedes the stated instant |
| `AT_DECLARED_DEADLINE` | The cutoff equals the stated instant |
| `AFTER_DECLARED_DEADLINE` | The cutoff follows the stated instant |
| `UNKNOWN` | No supported explicit deadline is supplied |

That comparison is about the deadline, not the action that a provider said
would occur by it. The same comparison is exposed as `boundary_state` for a
reported exception's `until`; `null` yields `UNKNOWN`.

A future deadline is valid prospective statement data. It is different from a
future record or a future claimed observation, which cannot establish evidence
at the current cutoff. An unknown schedule remains unknown as the cutoff moves.

All applicable statements are retained. Multiple applicable statements require
review; the adapter does not silently select the last input record, the latest
recorded time or the most favorable conditions. It supplies no policy-supersession
or conflict-resolution protocol.

The following implications are forbidden:

- Disabled training use implies zero retention, transfer permission or deletion.
- A local-region declaration establishes every processing or storage location.
- Chat-history removal establishes removal from provider logs or backups.
- A reached deadline generates an erasure completion record or independent review.
- Missing completion evidence proves that the provider never responded or retained data unlawfully.
- Later presence automatically disproves an earlier scoped deletion operation.
- A valid signature independently proves a condition's truth or historical event time.

Keep affirmative presence reports and applicable exceptions visible beside any
historical completion or review evidence. Follow-up can be required without
declaring a legal violation or silently rewriting the original erasure assessment.

Completion-claim coverage is assessed separately for each retention statement's
`request_record_id` and locations. An applicable attestation about one location
does not resolve another location or request. When the deadline is reached and
locations lack an applicable provider completion claim, the report retains
`COMPLETION_EVIDENCE_NEEDED_BY_CUTOFF`. Each statement identifies its matching
`provider_completion_claim_record_ids` and
`locations_without_provider_completion_claim`. At and after the deadline,
`RETENTION_DEADLINE_REACHED_REVIEW_REQUIRED` remains present even with full
coverage by provider claims. Such coverage does not establish actual deletion.
No aggregate positive result in the old erasure report substitutes for these
request/location checks.

For deadline-related presence follow-up, the observation must be at or after
the bound deletion-request time as well as the relevant stated deadline, and
the request and location must match. Historical presence can remain visible
without being classified as post-request presence. Presence at or after a
matching scoped completion claim is separately identified for review.

## 4. Report composition

The wrapper returns the original `erasure_report` unchanged, along with
`statements`, `presence_reports`, `record_checks` and `follow_up_reasons`.
These dimensions describe the supplied evidence under the evaluator's declared
trust and cutoff. The wrapper does not insert its records into the old report,
change its input hashes or upgrade its conclusions.

The wrapper reports universal deletion as `NOT_ESTABLISHED` and legal compliance
as `NOT_ASSESSED`. An existing independent-review result, if any, remains the old
assessor's scoped result; it is not a review of every retention condition or later
copy. External anchoring and production data-path verification are not performed.

`retention_evidence_integrity` is
`VERIFIED_AND_APPLICABLE_UNDER_EVALUATOR_TRUST` only when at least one new record
exists and all new records are eligible for the target. A failed signature gives
`FAILED_SIGNATURE`; other unresolved material gives `UNRESOLVED`. This field
is distinct from the original erasure report's integrity result and from the
truth of the attributed statements.

## 5. Execution and evidence exports

The command-line interface accepts separate input and trust paths:

```sh
python -m retention_adapter assess --input input.json --trust trust.json \
  --output new-report.json
```

Use `--allow-synthetic` for explicitly permitted synthetic trust. An omitted
output path prints the report. Assessment performs no network requests, model
calls, gateway actions or deletion operations.

`python suite.py run --output generated` executes the synthetic scenarios and
writes new captures. `python suite.py verify generated` re-evaluates those
captures and checks their recorded results. A successful export check supports
the captured input/result relationship under the supplied assumptions; it does
not independently establish the original provider's or collector's assertions.

Each capture contains its public synthetic input, evaluator trust, actual report,
expected observations and differences. Private fixture signing keys are kept in
memory and are not exported. Verification uses the saved signatures and trust;
it does not generate replacement keys or rebuild the fixtures. It checks the
fixed case inventory, file hashes, type-sensitive canonical report equality,
expected observations and cross-case invariants after reassessment.

The source manifest covers the runtime, suite, fixture support, Python tests,
contract, dependency requirements, dedicated workflow and the original
assessor's Python sources. Verification requires that manifest to match the
current checkout. Recheck a historical capture against its recorded source
revision; a changed implementation is not an interchangeable verifier for that
recorded execution.

The saved manifest, case hashes and public trust are supplied inside the export.
They provide consistency checks, not an external trust anchor or an immutable
execution receipt. A party able to replace the export can also replace its
synthetic keys and inputs. A successful verification therefore does not prove
who performed the original run, when it happened or that a provider adopted the
included keys. The recorded creation time and Python version are run metadata,
not independently authenticated facts.

The runtime does not inspect catalogue case IDs or expected outcomes. Retain
new case results separately from the unchanged original 23-case catalogue,
fixed 53-case capture and previous pilot records. Only actual execution records
support a claim about tests run or scenarios exercised.
