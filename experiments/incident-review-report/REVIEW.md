# Incident review report: development boundary review

This is an internal development review with separately authored boundary tests.
It is not an external security assessment, independent reproduction, human review
of the underlying incident evidence, legal opinion or VAP/CAP conformance result.
The report generator is a separate informative experiment. The frozen recheck
kit, original pilot implementations and captures, historical research assets and
normative specification are not changed by this work.

## Reviewed operation and trust boundary

The public operation consumes the fixed original kit archive and an externally
obtained expected archive digest. It presents the preserved 17 upload, 18
publication and 18 erasure cases after the unchanged kit has rechecked them.
It does not repeat the original upload, publication or erasure actions. The three
pilots remain separate experiments, not an integrated production workflow.

The reporter checks all 136 locked execution-source files before importing the
sibling kit and rejects already loaded kit modules with foreign origins. It then
inspects the archive into owned bytes and invokes the actual unchanged recheck
function under the same expected archive digest. The report requires the complete
fixed result, including exact archive and manifest identities, ordered pilot
counts and sources, dependency versions, guard labels and false action flags.
Floating-point counts and integer or string substitutes for boolean flags do not
satisfy that contract.

Projection starts only after that validation. Every displayed evidence-derived
fact retains a file, raw-byte SHA-256 and concrete JSON Pointer; the core resolves
those references and checks their values against the retained evidence bytes.
The whole-case inventory and ordering are fixed. Reporter source identities are
checked again before publication.

This boundary assumes a trusted reporter checkout, interpreter, host and installed
dependencies. The checks do not authenticate an arbitrarily hostile interpreter,
Python import machinery or native library. A source digest identifies bytes under
the expected-value assumption; it is not independent endorsement. The frozen
kit's Python audit guard remains an in-process guard, not an OS sandbox, and the
dependency description remains `PINNED_VERSIONS_NOT_HERMETIC`.

## Meaning of the displayed counts and states

The headings distinguish **saved cases rechecked** and **scenario expectations
matched** from operational outcomes. Matching a negative control can mean that
an outside-gate action or readable retained copy was observed. All 53 scenarios
can match while recorded outcomes include `OUTCOME_UNKNOWN` and explicitly
limited control coverage. No security percentage, compliance grade or human
approval is inferred from those counts.

The report preserves these distinctions:

- Upload preflight, final-gate and postflight assessments remain separate. UL-10
  retains the final-gate refusal alongside the admission-time authorization.
- UL-14 and LP-16 retain both the controlled-route block and the outside-gate
  observation. Blocking the controlled route is not relabeled as all-route control.
- An unknown returned outcome is retained alongside captured receiver or file
  observations. A positive readback does not silently replace the original state.
- LE-12/13 retain the readable excluded copy and open-handle controls. LE-15
  retains the scoped provider statement and the later present observation.
- Missing observer evidence and absence-only evidence remain distinguishable from
  an observed removal transition. Missing assessor frames remain missing, with
  their absence reason, rather than acquiring invented `UNKNOWN` dimensions.

Per-operation relationships come from the original `records` or `reports`
indices. Independently sorted summary arrays are not paired to manufacture a
chronology. `UNKNOWN`, `NOT_ESTABLISHED` and `NOT_ASSESSED` remain distinct literal
values. Notes interpret this fixed synthetic capture and are separately labeled
as interpretations, not new observations or general incident decisions.

Valid signatures still attribute statements under the captured trust
configuration. They do not independently establish statement truth, event time,
organizational independence, complete AI authorship, universal external erasure
or legal applicability. Captured synthetic reviewer authorizations do not mean
that this reporting operation performed a human review. The report retains
`human_review: NOT_PERFORMED` and its other explicit assurance limits.

## Rendering, delivery and received-report verification

The presentation consists of authoritative JSON and deterministic English and
Japanese Markdown, with a manifest binding their raw bytes. Saved article HTML,
source article text and whole signature envelopes are not inserted into the
presentation. Dynamic text is escaped as text rather than treated as Markdown,
HTML, a code fence or a URL. Evidence links are constructed only for the fixed
capture commit and allowlisted snapshot files; they are references, not
independent endorsements or remote assets loaded during generation.

All four ZIP members are completed and bounded before publication. A private
temporary file is finished and synchronized before exclusive hard-link
publication. Existing destination paths are not overwritten. Verification and
normal pre-publication failures do not expose a final success report. This is
not a crash-durability or rollback guarantee after the final link.

A received report is not accepted because its internal manifest matches its
own contents. Verification requires an external raw candidate digest, rechecks
the original kit, rederives the expected complete report and compares exact
bytes. The candidate report ZIP is neither extracted nor used as executable
input. Rewriting the JSON, the Markdown, all member hashes and the candidate
digest does not authorize a different report.

The source identity includes the reporter's code, tests, instructions, workflow
and frozen execution inputs. Results, this review and the contract are excluded
to avoid circular output identities. Changed reporter source requires a new
report digest; deterministic bytes do not establish truth or independence.

## Independent boundary test checkpoint

The separately authored `tests/test_boundary.py` contains eight test methods:

1. Eighteen failed, incomplete or malformed recheck variants are refused before
   projection or publication. The variants include mismatched archive/manifest
   identities, type substitutions, worker omissions/order changes, changed
   dependencies, missing guards and promoted assurance claims.
2. A modified locked kit source in a private copied checkout is refused in a
   fresh interpreter before any kit import; its import sentinel remains absent.
3. Foreign cached kit modules are refused before their functions can run.
4. A fabricated displayed fact, promoted scope or missing case cannot pass the
   core's post-projection checks or reach publication.
5. A forged report with consistently rewritten JSON, Markdown and internal
   hashes fails actual source-bound rederivation, even when its supplied external
   candidate hash correctly identifies the forged bytes.
6. A wrong external report digest fails before rederivation begins.
7. A diagnostic source change at the final publication check prevents delivery.
8. The actual 53-case report retains the limited scope and an unknown operational
   outcome despite every original scenario expectation matching.

The fixture uses the unchanged frozen kit and its actual three verifier workers.
The positive generation and forged-report rederivation also run the actual
recheck path. Malformed-result, projection-tamper and final source-drift
injections are diagnostic test doubles; they are not presented as additional
incident observations or as a newly executed pilot.

The focused local command was:

```sh
/tmp/vap-recheck-venv/bin/python -W error::ResourceWarning -m unittest discover -s tests -p test_boundary.py -v
```

It completed **8/8 methods**, with zero failures, errors or skips. Resource
warnings were treated as errors. The kit's full 53-case verification was exercised
as described above. This focused result is not evidence of an independent
external run.

### Final integrated local checkpoint

The completed local `record_run.py` execution used **Python 3.12.14** and passed
**37/37 methods**: 12 projection, 15 delivery, eight boundary and two integration
methods. Its record reports zero failures, errors, skips or unraisable exceptions.
It generated the report through actual verification of all 53 saved cases and
then verified the report by exact byte-for-byte rederivation.

All **136 frozen execution-source files remained unchanged**. The complete new
execution identity covers **154 files** with aggregate SHA-256:

```text
1b6187b8d732e299de389e957601b96ad971f908f1b96cc6da11d2662e2efb3b
```

The final local report ZIP is **2,237,333 bytes**, with SHA-256:

```text
df971f32b68efc20bb76352076266747485bc9c49a26e248aec6af444a399360
```

The presentation retains **129 assessor frames: 100 recorded and 29 not
recorded**, plus 87 interpretation-note instances. Those are presentation
inventories, not additional observations or security results. The compact case
index identifies state arrays as case-level aggregates and explicitly declines
to pair their positions with operations or core assessments. The deduplicated
F/S reference registry retains each source file's raw hash and every concrete
pointer.

A final wording review read the generated Japanese and English openings and
the key unknown-outcome, final-gate, bypass, unknown-origin and erasure-control
excerpts. Both views state upfront that 53 matched scenarios are not 53 security
successes and retain the limits on observation truth, human review, independence,
conformance and legal compliance. The excerpts preserve the paired observations
and scope qualifications described above. No misleading guarantee promotion or
blocking wording issue was found; no further runtime or test changes were made.

This is the internal local development checkpoint. CI runs and any future
external reproduction must be identified separately; neither is preclaimed here.

## Remaining limits and disposition

No blocking issue was found within the declared, fixed-input reporting scope.
The separately owned projection and delivery suites cover their concrete
pointer, record association, escaping, bounds and filesystem behavior. The
boundary checks do not claim universal parser correctness or defense against a
compromised host.

The design uses observation boundaries, attribution and explicit evidence gaps
as reporting principles. It adds no current regulatory or news assertions from
the earlier internal research memos, and it makes no finding about either real
incident. A more readable view of the preserved evidence does not widen what
that evidence establishes.
