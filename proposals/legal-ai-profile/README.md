# VAP-LAP — Legal AI Profile

**Proposed domain profile · Informative introduction**

VAP-LAP is AILEX's proposed Legal AI Profile for recording AI-assisted legal work and professional review.
It connects legal consultation, document generation, and fact-checking with the people who review their outputs.

## Reference draft

| Item | Reference |
|------|-----------|
| Internet-Draft | [`draft-ailex-vap-legal-ai-provenance-05`](https://datatracker.ietf.org/doc/draft-ailex-vap-legal-ai-provenance/05/) |
| Publication date | 26 October 2026 |
| Profile identifiers | `profile.id: LAP`; `profile.version: 0.6.0` (§13.1) |
| Publication status | Active individual Internet-Draft; the text's intended status is Experimental |
| Current revision history | [IETF Datatracker](https://datatracker.ietf.org/doc/draft-ailex-vap-legal-ai-provenance/) |

The fixed `-05` link identifies the edition summarized here. An individual Internet-Draft is work in progress,
not an IETF standard.

## Legal workflows

The draft's §§13–16 describe these uses:

| Workflow | Records to examine |
|----------|--------------------|
| Legal consultation | The question and its response, refusal, or error |
| Document generation | The drafting request and resulting output |
| Fact-checking | The verification request and its outcome |
| Human review | A professional's acceptance, modification, or rejection of an AI output |

These records support later examination of recorded actions and responsibility.

## Relationship to VAP

LAP draws on the VAP framework and remains a proposed profile outside the
[VAP v1.2 §4.5.2 registry](../../spec/v1.2/VAP_Framework_Specification.md#452-profile-registry).
This page introduces the proposal and its reference service; the framework specification and registry remain unchanged.

## AILEX reference

[AILEX](https://ailex.co.jp/service/) provides a practical reference for legal AI workflows. Its current AILEX v2
service page describes case management, document drafting, fact-checking, and operational audit logs for law firms.
The [AILEX standardization page](https://ailex.co.jp/ietf/) explains the LAP proposal and its implementation status.
Use the service documentation for currently available product features and the reference draft for the profile design.

Appendix C of `-05` reports no independently validated conforming implementation of that revision. This introduction
makes no LAP or VAP conformance or certification claim for AILEX.

[Return to the VAP family overview](../../README.md#relationship)
