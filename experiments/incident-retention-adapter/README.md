# Retention conditions and deletion follow-up adapter

**Experimental, synthetic, unadopted — version 0.1.0.**

This offline adapter evaluates attributed retention conditions alongside an
unchanged [incident erasure assessment](../incident-evidence-assessor/README.md).
It distinguishes a stated deadline from evidence about an action. Advancing an
observation cutoff past that deadline never creates a deletion attestation,
independent review or VAP ERASURE event.

The [source-backed design guidance](../../proposals/incident-evidence-bindings/README.md#51-retention-deadlines-do-not-establish-completed-deletion)
motivates this experiment. Its synthetic cases do not reconstruct the Panasonic
incident, authenticate that incident's provider responses or inspect an external
AI service. This adapter adds no normative VAP/CAP requirement or certification
result.

## What it evaluates

| Material | Assessment boundary |
| --- | --- |
| Provider statement about processing locations or training use | An attributed declaration, not an independently observed processing location or use |
| A provider's stated retention deadline | Whether that stated instant is reached at the evaluator's pinned cutoff |
| An unknown deadline or unresolved starting event | A retained uncertainty; the adapter does not invent an end date |
| A retention exception | The stated location, reason and bounded or unspecified end; not a legal finding |
| A separately supplied erasure request, acknowledgement, attestation or review | The original assessor's output, with its existing authentication, scope and independence conditions |
| A collector statement that a bound object was present at a later observation | A source-attributed presence statement at that time; not proof that an earlier deletion claim was false |

Processing location, training use, retention terms and deletion evidence remain
separate questions. A disabled-training declaration does not establish zero
retention, transfer permission or completion of deletion. A named processing
region does not establish where every copy, log or downstream operation resides.

The adapter accepts explicit timezone-aware deadlines and an explicit unknown
schedule. It does not calculate durations, infer a provider's starting event,
translate an unspecified calendar-day rule, or infer a timezone from a date-only
notice. Multiple applicable retention statements are preserved for review;
there is no implicit latest-statement-wins rule.

Provider completion claims are matched by request and location. A claim covering
active objects cannot resolve missing evidence for backups, and a claim about
another request cannot close this one. Reached deadlines remain subject to
evidence review even when scoped provider claims are available.

## Evidence and trust

The input wrapper contains an original erasure package and separately signed
retention records. The separately supplied trust wrapper contains the original
evaluator trust configuration. The original target, evaluation ID, cutoff and
key-role assignments govern both parts. All target fields are compared, including
request, provider, tenant, account, object set and payload digest.

New retention records use the domain `incident-retention-adapter/0.1` and are not
passed to the old erasure assessor. Valid signatures establish attribution under
the supplied trust assumptions. They do not establish truth, historical time,
source-document availability or the completeness of the supplied record set.
Public fixture keys are for synthetic tests and require explicit opt-in.

The original `erasure_report` is returned without modification. Any scoped
independent-review result in that report comes from its original evidence and
rules; the wrapper does not extend it to retention terms, later observations or
uncovered copies. Examine the wrapper's statement, presence and follow-up results
as well. A historical erasure assessment does not resolve later reappearance,
restoration or conflicting evidence by itself.

The full versioned input and signature contract is in [CONTRACT.md](CONTRACT.md).

## Run locally

Use Python 3.12 or 3.14. From this directory:

```sh
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -W error::ResourceWarning -m unittest discover -s tests -v
.venv/bin/python suite.py run --output generated
.venv/bin/python suite.py verify generated
```

Choose a new output directory for each suite run. Verification re-evaluates the
captured inputs under the supplied evaluator assumptions; it performs no remote
inspection or deletion. Generated artifacts distinguish actual test execution
from the expectations in the scenario catalogue. Runtime assessment does not
read scenario IDs or expected outcomes.

To assess separately supplied files:

```sh
.venv/bin/python -m retention_adapter assess \
  --input input.json --trust trust.json --output new-report.json
```

Add `--allow-synthetic` only for the public synthetic test configuration. Supply
the trust file separately and review its authorities and target pin; merely
receiving a trust file inside an evidence bundle does not make it trustworthy.

## Validation and recorded results

The [dedicated workflow](../../.github/workflows/incident-retention-adapter.yml)
tests the new adapter on Python 3.12 and 3.14, runs and rechecks its synthetic
suite, and reruns the unchanged assessor's regression tests and original
23-case suite. Workflow configuration alone is not a completed execution result.
The original 23-case catalogue, fixed 53-case capture and earlier pilot results
do not establish execution of the new retention cases.

CI uploads the new summary and case captures with 30-day artifact retention.
Consult the specific run, tested commit and captured summary before claiming a
test count or successful execution. This source introduction makes no independent
reproduction claim.

Retained local execution records and their reproduction instructions are indexed
in [results/README.md](results/README.md).

## Limits

The adapter sends no requests, removes no data and enforces no production policy.
It verifies supplied records under evaluator-provided keys and organizational
assignments. It does not perform identity onboarding, key revocation, external
anchoring, geographic verification, training inspection, media sanitization or
legal assessment.

A presence statement can justify follow-up about the specified object and
location. Even a later copy with matching bytes can result from restoration or
recreation; presence does not by itself disprove an earlier scoped deletion.
Absence of an applicable completion record is a gap in the supplied evidence,
not proof that the provider never responded or that deletion did not happen.
No result establishes universal deletion or disposition of unobserved copies.

Use opaque synthetic references in fixtures and publish only appropriate
metadata. Hashes and object identifiers are not inherently anonymous. Do not
copy real prompts, personal data or credentials into public evidence artifacts.
The repository's [CC BY 4.0 license](../../LICENSE) applies.
