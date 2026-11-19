# VSO / VAP / VCP: IETF 127 interoperability review

**Reviewed:** 20 November 2026 (JST). **Review window:** 14–20 November 2026.
**Status:** Informative research note; no specification change or adoption decision.

This note records primary-source findings and proposed follow-up work. External experiment results below are
the participants' reports, checked against their published material; they were not rerun for this note.
The individual Internet-Drafts discussed here remain work in progress. Their publication, meeting discussion,
or test results do not establish VAP/VCP implementation independence, conformance, certification or IETF adoption.

## 1. Statement identification and corrections

The 18 November SCITT WG material discusses references to particular Signed Statements and their relationships.
Issuer and subject claims can group records without uniquely identifying one statement. Re-encoding an outer
COSE object or adding a Receipt can change a digest over that object while preserving the signed input.[^scitt]

The 15 November `draft-gruszka-scitt-statement-identification-04` is a useful additional comparison:
§5.3 separates signing-input identity, a particular signature instance, serialized-object identity, and a
statement with external content/context. §6 separates unsupported, negative and indeterminate results.
It proposes requirements and illustrative cases, not an agreed reference format.[^identification]

**Proposed follow-up:** specify the target object and matching rule before choosing a stable identifier.
Test Receipt addition, encoding changes, changed protected content, missing detached inputs and unauthorized
corrections separately. Reference matching alone cannot establish signature validity or authority to correct.

## 2. Receipts across two log operators

The latest agent-action interop report, revision `-01`, describes four Signed Statements registered with
`ts.isoluce.net` and `witness.agentactioncapsule.org`, with each operator checking the other's Receipts.
Their leaf inputs differed: statement bytes versus a digest of the signing structure.[^interop]

The report also records the tree-size/index authentication problem and its implementation response:
the reader compares against a signed tree head, and `ts.isoluce.net` now signs both values in each Receipt.
This does not establish that every log or verifier has adopted that response.[^interop]
The WG report explicitly limits the exercise: no project tested against a current SCITT-plus-SCRAPI
implementation; the implementation used for that part was an archived emulator revision.[^scitt]

**Proposed follow-up:** make leaf construction, tree/proof scheme, trusted log keys and the authenticated
root/size context explicit in any interoperability test. Record inclusion and authenticated size/position
as distinct checks where the selected profile requires them.

## 3. Deterministic Encodings for COSE

Revision `-01`, dated 15 November, proposes a protected-header encoding identifier. It addresses reconstruction
when a verifier has a structured value rather than the original hashed bytes. Its `dtrm` value applies to
CBOR-related content; §4.2 expressly disallows pairing it with `application/json`.[^encoding]

The external checker matched **41/41** proposed `-01` vectors: 10 generation, 27 verification and 4 rejection
cases. The report also says the `-01` text gave the same result. In the reverse direction, the authors reported
**14/16** matches on the external checker's vectors; two cases exposed missing `-00` outcome rules.
Those reverse results were reported by the authors, not rerun by the checker author.[^interop]

**Proposed follow-up:** use explicit encoding selection and separate content-binding outcomes as design input.
This is not a proposal to apply `dtrm` to VCP JSON.

## 4. AEP and the conformance matrix

The 15 November AEP slides report a Go verifier built by Abdel Fane/OpenA2A from the documents, and an exponent
formatting disagreement between the authors' Python and JavaScript verifiers. The 22-vector round was advertised
as open through 22 November.[^aep] The later WG report records 25 textual choice points and three differences corrected
that day; it does not establish that every possible AEP interoperability issue was resolved.[^scitt]

The separate JCS comparison at matrix commit `25e3311` measured canonical-byte agreement, not complete
Evidence Pack verdict agreement:[^matrix]

| Result across four implementations | Inputs |
| --- | ---: |
| Same canonical bytes | 20,121 |
| All four rejected | 11 |
| Outcomes split | 8 |
| Total | 20,140 |

The eight splits concerned large integers, BOM handling, duplicate members and nesting limits.
The remaining 19 inputs were therefore not 19 disagreements.

**Proposed follow-up:** feed raw input bytes through parsers, then compare canonical bytes, hashes and later
verification results separately. Declare additional input restrictions as profile rules. The SDK's exact-integer
interpretation and the demo's restricted integer domain are different contracts.[^sdk][^demo]

## 5. Decision Provenance

`draft-lemonnier-scitt-decision-provenance-03`, dated 17 November, clarifies the inputs and scope for examining
presentation, effective authority, policy content, bounded standing approval and observed effects.
Its changelog places the passkey, multiple-log and outside-reader experiment additions under changes since
`-01`; they should not all be described as new in `-03`.[^decision]

**Proposed follow-up:** compare these distinctions with existing payment/wallet evidence experiments.
Keep approval authentication, authority at execution, execution matching and observed outcome separate.
An authenticated approval record does not establish the person's understanding.

## 6. VAP Framework -03

The 15 November publication adds a correspondence between the draft's three conceptual groups and the
VSO specification's five mandatory layers. It updates the VCP reference to `-05` and the fixed VSO source
reference while retaining that source's v1.2.0 Draft 3 status. Its changes section states that no framework
requirement is added or changed.[^vap]

**Follow-up:** record the publication in current navigation while preserving the dated 11 November proposal
as preparation history. Publication does not establish the proposal's submission process or normative adoption.

## 7. WIMSE Architecture

Datatracker records revision `-09` on 16 November; the document itself is dated 17 November.
The 18 November WG minutes record an intention to start Working Group Last Call within the following weeks;
they do not report that the call had started or completed.[^wimse]
Track this work when relating workload identity and delegated authority to evidence; an identity credential
alone does not supply every authorization or execution fact.

## Follow-up within existing VSO work

| Workstream | Existing location | Proposed next evidence |
| --- | --- | --- |
| VCP verification rules | Known issues and existing integrity/numeric proposals[^vcp] | Explicit byte/signature/tree rules and migration analysis; no new adoption claim |
| Independent demo implementation | [#2](https://github.com/veritaschain/vap-spec/issues/2), [#4](https://github.com/veritaschain/vap-spec/issues/4), [#5](https://github.com/veritaschain/vap-spec/issues/5) | Attributable external source, exact commits, fixed inputs and reproduced results |
| SDK comparison | Existing interoperability workplan[^sdk] | Raw-input boundary cases and stage-specific expectations |

Use the existing challenge rather than opening a duplicate. Its published prerelease and the later main-branch
security hardening are distinct baselines; a submission must identify the exact contract and implementation
revisions it evaluates. Baseline selection is not changed by this note.[^release]

A reproducible comparison fixes the evidence bytes, contract/version, trust inputs, policy and any evaluation
time used by that contract. It preserves expected rejection, missing/unsupported evidence and operational
errors as different outcomes. Completion requires an attributable implementation and recorded reproduction;
a workplan or another first-party language implementation does not supply that evidence.

## Sources

[^scitt]: [IETF 127 SCITT WG slides, 18 November, revision -00](https://datatracker.ietf.org/meeting/127/materials/slides-127-scitt-ietf-127-scitt-working-group-sf-00), identification discussion and Hackathon report.
[^identification]: [Statement Identification -04](https://datatracker.ietf.org/doc/html/draft-gruszka-scitt-statement-identification-04), §§5–6 and change history.
[^interop]: [Agent action evidence interop results -01](https://datatracker.ietf.org/meeting/127/materials/slides-127-hackathon-sessd-agent-action-evidence-interop-results-01.pdf), pp. 2–4.
[^encoding]: [Deterministic Encodings for COSE -01](https://datatracker.ietf.org/doc/html/draft-mih-sokolov-cose-deterministic-encodings-01), §§3–4.
[^aep]: [Action Evidence Packages Hackathon results -03](https://datatracker.ietf.org/meeting/127/materials/slides-127-hackathon-sessd-action-evidence-packages-for-ai-agents-recompute-dont-inherit-03.pdf), 15 November.
[^matrix]: [Cross-implementation results at 25e3311](https://github.com/probityai/agent-evidence-matrix/blob/25e3311/libraries/RESULTS.md).
[^decision]: [Decision Provenance -03](https://datatracker.ietf.org/doc/html/draft-lemonnier-scitt-decision-provenance-03), §6 and changes since -02/-01.
[^vap]: [VAP Framework -03](https://datatracker.ietf.org/doc/html/draft-kamimura-vap-framework-03), §4.1 and changes from -02.
[^wimse]: [WIMSE history](https://datatracker.ietf.org/doc/draft-ietf-wimse-arch/history/), [-09 text](https://datatracker.ietf.org/doc/html/draft-ietf-wimse-arch-09), and [18 November minutes](https://datatracker.ietf.org/doc/minutes-127-wimse-202611182200/).
[^sdk]: [SDK interoperability workplan at a81806d](https://github.com/veritaschain/vcp-sdk/blob/a81806d5f6fd8ab7b6a4a60fa2530ba07abb2940/docs/INTEROPERABILITY_WORKPLAN.md) and its linked interpretations.
[^demo]: [Demo contract at a9ee3a5](https://github.com/veritaschain/vap-spec/blob/a9ee3a54c3b4e086051c9b7ec80374f2b3b92298/interop/vap-evidence-pack-demo/CONFORMANCE.md).
[^vcp]: [VCP v1.2 known issues at ab5c851](https://github.com/veritaschain/vcp-spec/blob/ab5c851ce937763104204d8c4ab09197e16799f1/spec/v1.2/README.md), including links to unadopted proposals.
[^release]: [Demo release record at a9ee3a5](https://github.com/veritaschain/vap-spec/blob/a9ee3a54c3b4e086051c9b7ec80374f2b3b92298/interop/vap-evidence-pack-demo/RELEASE.md), including the 13 November security-hardening note.
