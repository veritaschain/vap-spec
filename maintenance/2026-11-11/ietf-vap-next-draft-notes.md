# Proposed editorial note for the next VAP Internet-Draft

**Prepared:** 11 November 2026 (JST). **State:** proposed text only; not submitted or adopted.
This is a maintenance note, not the original IETF source. It assigns no next
revision number, review period, effective date or decision authority. The
published document remains [draft-kamimura-vap-framework-02][vap-current].

## Observed baseline and purpose

The published [VAP draft §4.1][vap-architecture] presents three conceptual
groups and distinguishes its architecture discussion from VSO's detailed
requirements. VSO's [VAP v1.2 §3.1][vap-spec] defines five mandatory layers.
The count difference does not establish a normative contradiction; the missing
editorial explanation is how the two presentations correspond.

The VSO text reviewed here is fixed at repository commit
`1ce71a66f55d9a20728213b7c3a8bb79270ae579`, file
`spec/v1.2/VAP_Framework_Specification.md`, SHA-256
`a35d5e082fd4b2f9921a78b1a71df263018320375e09fa18cf81533a18a19998`.
The crosswalk below is a **proposed explanatory mapping**, not an already
adopted interpretation or a change to that specification.

## Proposed replacement for §4.1 — Layered Architecture

The following English text is proposed for author review:

> This document uses three conceptual groups to organize its discussion of
> IETF technologies: Integrity, Provenance, and Accountability. This grouping
> summarizes the architecture; it does not replace the five mandatory layers
> in the separate VSO specification [VAP-SPEC], Section 3.1, or change their
> requirements and dependencies.
>
> **Integrity group:** Covers record hashes, cryptographically verifiable
> sequencing, batch commitments and external anchoring. Per-event hash chaining
> is one optional framework mechanism under INT-004a; a profile may require it.
> Profiles specify their sequencing mechanisms and associated requirements.
> The grouping does not make chaining mandatory or relax the specification's
> external-anchoring requirements.
>
> **Provenance group:** Covers records of actors, inputs, context, actions and
> outcomes. For this overview, causal and temporal relationships between records
> are discussed here while retaining Traceability as a distinct layer in the
> VSO specification.
>
> **Accountability group:** Covers responsibility boundaries, evidence for
> examination and verification across organizations. Cross-party traceability,
> including cross-references where used, connects these responsibilities to the
> relevant records; it remains subject to the separate Traceability requirements.
>
> The relationship to the five-layer specification is summarized below:
>
> | VSO specification layer | Treatment in this document's conceptual overview |
> | --- | --- |
> | Integrity | Integrity group |
> | Provenance | Provenance group |
> | Traceability | Causal and temporal relationships in the Provenance discussion; cross-party relationships in the Accountability discussion |
> | Accountability | Accountability group |
> | Domain Profiles | Profile specialization described separately in Sections 4.2 and 7 |
>
> Domain Profiles are therefore not omitted from the architecture, and
> Traceability is not removed as a requirement layer. Implementations may
> combine components, but any claim against the VSO specification is assessed
> against its own requirements, not merely these three explanatory groups.

## Proposed reference updates

1. **VCP reference:** In `[I-D.kamimura-scitt-vcp]`, replace revision `-04`
   with the published `-05`, date **24 October 2026**, and the fixed URL below.
   Preserve the title and Work in Progress status:

   Kamimura, T., *A SCITT Profile for Verifiable Audit Trails in Algorithmic
   Trading: The VeritasChain Protocol (VCP)*, Work in Progress, Internet-Draft,
   `draft-kamimura-scitt-vcp-05`, 24 October 2026,
   <https://datatracker.ietf.org/doc/html/draft-kamimura-scitt-vcp-05>.

   [VCP -05 Appendix C][vcp-changes] corrects the description of AnchorRef and
   schema requirements. The existing `-04` citation remains a valid historical
   reference; this update is proposed so the next draft discusses the newer
   published baseline.

2. **Optional VSO source-pin refresh:** `[VAP-SPEC]` currently fixes commit
   `b5ef9316717bebe638d5eca621327b54cdda93e1`. For a refreshed baseline, use
   [the exact `1ce71a6` file][vap-spec] and digest recorded above, retaining
   **v1.2.0 Draft 3** and its separate VSO status. The older pin is not an
   invalid reference. If retained, identify it as the historical baseline;
   if refreshed, recheck surrounding status summaries against the new pin.

## Checks before any author submission

- Retrieve the authoritative editable source for published `-02`; apply this
  proposal there only after its wording and mapping have been reviewed.
- Rebuild text/HTML with the document's normal toolchain; inspect the generated
  diff and run reference/format checks such as xml2rfc and idnits.
- Verify section references, bibliography dates, fixed source links and the
  author-selected revision metadata. Preserve historical change entries.
- Confirm that the result introduces no new framework requirement, conformance
  claim, adoption record or IETF endorsement. Record actual checks separately.

None of those source-editing, rebuilding or submission steps was performed by
creating this note.

[vap-current]: https://datatracker.ietf.org/doc/draft-kamimura-vap-framework/
[vap-architecture]: https://www.ietf.org/archive/id/draft-kamimura-vap-framework-02.html#section-4.1
[vap-spec]: https://github.com/veritaschain/vap-spec/blob/1ce71a66f55d9a20728213b7c3a8bb79270ae579/spec/v1.2/VAP_Framework_Specification.md
[vcp-changes]: https://www.ietf.org/archive/id/draft-kamimura-scitt-vcp-05.html#appendix-C
