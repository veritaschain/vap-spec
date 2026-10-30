# Incident evidence offline assessor

**Experimental, informative, unadopted — implementation 0.1.0.**
This executable research adapter assesses structured evidence derived from the
[incident-evidence proposal](../../proposals/incident-evidence-bindings/README.md).
It does not adopt the proposal or establish VAP/CAP conformance. The normative
baseline remains **VAP v1.2.0 Draft 3**.

The separate [controlled upload pilot](../incident-upload-pilot/README.md) connects
this unchanged assessor to measured immutable bytes, mandatory local pre-recording
and a separate local HTTP receiver. Its execution controls and receiver statements
remain application-side experimental behavior, not additional core verdicts.

The separate [local publication pilot](../incident-publication-pilot/README.md)
records synthetic editing operations, binds disclosure and reviewer authorization
to final rendered bytes, and measures one-shot local output. The core publication
assessment remains `REVIEW`; local output does not establish publisher acceptance.

[日本語実行ガイド](RUN-ja.md) · [Input/trust contract](CONTRACT.md) ·
[Transfer/erasure types](TYPE-TRANSFER-ERASURE.md) ·
[Publication/response types](TYPE-PUBLICATION-RESPONSE.md) ·
[Recorded synthetic execution](results/summary.json)

## What this adds

The proposal's 23 cases originally specified natural-language assumptions and
expected outcomes. This implementation supplies separate, typed, signed synthetic
inputs and derives the outcomes from those inputs. The runtime never reads case
identifiers, the catalogue's `given` prose, or its `expected` values. Only the
test runner reads the catalogue to compare named assessment fields.

| Area | Cases | Derived evidence distinctions |
| --- | ---: | --- |
| Transfer | 8 | Exact policy/permit bindings, changed payload, wrong tenant, actual action after denial, timeout, missing coverage, collector outage |
| Erasure | 5 | Request, acknowledgement, provider claim, wrong-object receipt, scoped reviewer report |
| Publication | 7 | Prohibited use, incomplete observation, changed revision, omitted figure/code disclosure, unresolved policy, self-declaration, delivery stages |
| Incident response | 2 | Information-request cutoff and absent response; urgent containment with unavailable preservation |
| Cross-party | 1 | Authentic imported statement without established XREF participation |

Ed25519 signatures are actually verified, with SHA-256 and RFC 8785
canonicalization. The expected identity and allowed role come from a **separate
evaluator trust file**, which also pins the target, workflow and observation
cutoff. Signature integrity, identity, role, time assumptions and object binding
are reported separately. A real signature for another tenant or document does
not establish applicability to this target.

The program evaluates supplied digests and observations. It does **not** read the
actual outgoing patient spreadsheet or manuscript, instrument an editor, observe
network traffic, or compute a digest from a live outgoing stream. A later
integration must obtain those observations, bind the exact bytes, and enforce
any decision on its controlled route. The fixtures contain synthetic content and
public deterministic test keys; they are not evidence from either institution.

## Reproduce

Use Python 3.12 or later. From the repository root:

```sh
python3 -m venv .venv-incident
.venv-incident/bin/python -m pip install -r experiments/incident-evidence-assessor/requirements.txt
cd experiments/incident-evidence-assessor
../../.venv-incident/bin/python -m unittest discover -s tests -v
../../.venv-incident/bin/python -m incident_assessor run-suite
```

The suite generates all 23 synthetic packages and their explicit evaluator trust
files, executes the same runtime used for individual assessment, and compares
every named expected assessment field. It creates:

- `generated/fixtures/NN.input.json` and `NN.trust.json`: signed input and separately selected trust.
- `generated/reports/NN.report.json`: derived assessments, supporting record IDs and individual evidence checks.
- `generated/summary.json`: expected and actual fields, differences, input/report hashes, source-file hashes and toolchain versions.

Here `NN` is the catalogue identifier, such as `UP-05` or `ER-03`. Matching a
negative scenario means the expected negative result was reproduced. It does not
mean that its evidence passed or that the motivating incident was prevented.
Explanatory prose in `expected.reasons` is not compared as a string; the runtime
emits its own reason codes with evidence references. The original catalogue is
preserved as the proposal-stage oracle; its `execution_status: not-executed`
records that publication state. Executed **structured translations** and their
source hashes are recorded separately here.

Assess an individual generated package:

```sh
../../.venv-incident/bin/python -m incident_assessor assess generated/fixtures/UP-05.input.json \
  --trust generated/fixtures/UP-05.trust.json --allow-synthetic \
  --output generated/example.report.json
```

Without `--allow-synthetic`, synthetic trust configurations are rejected. This
opt-in is an accident-prevention check, not a replacement for selecting trustworthy
production keys. The `explicit-evaluator` mode accepts the caller's externally
selected keys; it supplies no certificate discovery, revocation service or
institutional identity verification. Never reuse the public fixture keys for
real evidence.

The assessor makes no network requests, dereferences no URLs from evidence, and
loads no files referenced within a record. After dependencies are installed it
runs offline. Only explicitly supplied input/trust files are read by `assess`;
the optional output path is chosen through the CLI.

### Exit codes

| Command/result | Code | Meaning |
| --- | ---: | --- |
| `assess` produced a report | 0 | Includes denied, blocked, unknown and review outcomes; read the named dimensions |
| `run-suite` matched every expected field | 0 | Synthetic regression match, not conformance |
| `run-suite` found an expectation mismatch | 1 | Inspect `differences` |
| Invalid/unsupported/unreadable input | 2 | Structured error; no application assessment issued |

## Assessment boundaries

**Transfers.** A positive `ALLOW` needs a bound, effective policy, an exact
allowlist grant, a current permit and any required collector evidence. Actor,
provider, endpoint, tenant, account, purpose, route, payload, policy version and
stage are checked. The proposed operation and actual observed dispatch are
evaluated at their respective times. Expiry before dispatch cannot retain an
earlier permission. A denial or failed collector prerequisite with corresponding
observed egress remains a violation even when unrelated evidence is unavailable.

`BLOCK` and `HOLD_PENDING_CURRENT_AUTHORIZATION` are recommendations from this
offline assessment, not evidence that the program blocked traffic. A route's
`NOT_OBSERVED` finding requires a qualifying scoped coverage statement; it never
establishes organization-wide absence of uploads. Remote processing remains
unknown after a dispatch timeout. This version does not implement provider
transfer-outcome or idempotency adapters.

**Erasure.** A request is not receipt, acknowledgement is not completion, and a
provider signature attributes only the provider's scoped statement. A reviewer
report must bind the request, evidence, objects, locations, method and time; its
trusted organization must differ from both requester and provider. The program
checks the report's attribution and links. It does not perform the review method
or inspect remote storage. Limited independent-review status never resolves
excluded backups, replicas, downstream recipients or model-training derivatives.
An applicable inconclusive review prevents unqualified promotion to the positive
review status. Unsupported negative-deletion/refusal/legal-hold record types are
rejected, not treated as success.

**Publication.** Policies are bound to an exact version, content digest, stage and
effective period. A signed manifest must connect observed AI use to exact included
text, figure or code versions. A model call by itself does not establish inclusion
in the submitted work. An established prohibition yields `BLOCK` even when a
disclosure exists. An approval for old bytes does not approve later edits.

This prototype deliberately does not emit automatic publication permission.
Declared disclosure categories and a content hash cannot prove that the prose
is truthful, semantically complete, correctly placed or acceptable to a publisher.
Even the positive publication control remains `REVIEW`, while separately showing
bound approval, prepared disclosure and recipient-asserted receipt. Author
declarations remain self-declarations; an absence of captured AI events never
establishes human-only authorship.

**Response and containment.** Information replies are evaluated against the
recorded request cutoff and separately pinned evaluator time. A later response
does not rewrite the earlier cutoff result. No response leaves facts and the
reason for absence unknown. Urgent history removal can be recorded together with
an unavailable-preservation gap; later anchor claims cannot reconstruct history
or establish contemporaneous collection.

**XREF and time.** Authenticated imported provider statements have attributable
value, but this adapter never establishes positive XREF or external anchoring.
It has no verifier for independent timestamp receipts or corresponding anchored
party records. All event and key-validity comparisons use signed declared times
under evaluator assumptions; cryptographic verification alone does not prove
the historical event time. No field is a legal finding.

## Validation and recorded provenance

The regression suite exercises malformed input, duplicate keys and IDs, typed
booleans, signature tampering, authentic but mismatched records, wrong identities
and roles, key/permit expiry, changed evaluator context, observation gaps,
contradiction precedence, false organizational independence, response cutoffs,
and the runtime's independence from the catalogue. Positive controls exercise
an allowed transfer and qualifying scoped evidence states.

[results/summary.json](results/summary.json) records the actual source hashes and
execution environment for the 23-case run. The recording commit may follow the
tested source; compare the source manifest, not the synthetic local checkout's
commit identifier. GitHub Actions runs the tests and suite on Python 3.12 and
3.14 and retains generated evidence/report artifacts for 30 days. A configured
workflow is not itself a claim that a particular CI run succeeded.

The recorded local run used cryptography 50.0.2 and RFC 8785 package 0.1.4.
Because the editing environment could not reach the package index, the latter's
two source modules were retrieved from the upstream `v0.1.4` tag (tree
`4d9b161f6054301d98d0566e813d020fb019ee10`) for the temporary test environment;
their Git blob hashes matched upstream. No dependency source is vendored into
this repository. CI installs the pinned requirements normally.

This is internally executed synthetic research. Independent external reproduction,
real gateway/provider/publisher integration, disclosure-content adjudication,
production key governance and VAP/CAP conformance remain unestablished. The
normative specification, existing verifiers and fixed historical evidence
distributions are unchanged. Formal proposal number and target release remain
unassigned/undecided.

References: [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785.html),
[upstream RFC 8785 implementation](https://github.com/trailofbits/rfc8785.py/tree/v0.1.4),
[Ed25519 API](https://cryptography.io/en/50.0.2/hazmat/primitives/asymmetric/ed25519/).
The repository's [CC BY 4.0 license](../../LICENSE) applies; this experiment does
not relicense the repository.
