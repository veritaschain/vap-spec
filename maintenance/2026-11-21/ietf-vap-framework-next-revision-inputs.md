# Inputs for the next revision of the VAP Internet-Draft

**Recorded:** 21 November 2026 (JST). **State:** review notes only; no text
has been edited, rebuilt or submitted.
This note assigns no revision number, submission date or decision authority.
The published document remains
[draft-kamimura-vap-framework-03][vap03] (posted 15 November 2026). A posted
Internet-Draft cannot be changed, so these points can only be addressed in a
later revision.

## 1. MiFID II RTS 25 is cited as a current rule

Two passages of -03 name RTS 25 as an applicable regulation:

| Section | Text in -03 |
| --- | --- |
| 1.2 Cross-Sector Applicability | "Algorithmic trading systems subject to regulations such as MiFID II RTS 25 and SEC Rule 17a-4." |
| 1.3.2 Other Regulatory Drivers | "MiFID II RTS 25 (clock synchronisation for trading records)" |

RTS 25 is Commission Delegated Regulation (EU) 2017/574.
[Commission Delegated Regulation (EU) 2025/1155][reg1155] (OJ L, 2025/1155,
3 November 2025) repeals it with effect from 2 March 2026 (Article 25) and
sets the business-clock synchronisation requirements in Articles 11 to 16,
which apply from the same date. The new regulation supplements Regulation
(EU) No 600/2014 (MiFIR), not Directive 2014/65/EU (MiFID II).

A later revision would need to name the replacement regulation, or describe
the requirement without a regulation number. Whether the two passages should
keep a historical mention of RTS 25 is an author decision. The appendix of -03
already records an earlier correction to the description of RTS 25; that
entry is history and does not need to change.

The same point is recorded for the VSO specification text in the
[v1.2 known issues](../../spec/v1.2/README.md) (§5.1.4). The specification
text is unchanged.

## 2. The companion VCP reference points to -05

The reference `[I-D.kamimura-scitt-vcp]` in -03 cites
`draft-kamimura-scitt-vcp-05` (24 October 2026).
[draft-kamimura-scitt-vcp-06][vcp06] was posted on 20 November 2026. It adds
an open issue on Receipt verification context and changes no requirement. The
-05 citation remains a valid reference to a fixed document; a later revision
can cite whichever revision is current when it is prepared.

**Added 24 November 2026 (JST).** [draft-kamimura-scitt-vcp-07][vcp07] was
posted on 24 November 2026 (Datatracker record time 02:34:46 UTC). It corrects
the SCRAPI description and the illustrative examples, states that the profile
relies on Receipts for inclusion only, and changes no VCP requirement. The
point above is unchanged: -05 stays a valid citation, and -07 is the current
revision. Item 2 of its Open Issues records that the VCP AnchorRecord signature
does not cover the event count, endpoints and PolicyID. Whether any passage of
the VAP draft that describes anchoring needs a matching note has not been
reviewed.

## Not covered

This note does not review the rest of -03, propose replacement wording, or
record a VSO adoption decision. It was prepared by the same first party that
maintains the draft and is not an independent review.

## Sources checked on 21 November 2026

- [draft-kamimura-vap-framework-03 (archived text)][vap03txt]
- [Commission Delegated Regulation (EU) 2025/1155][reg1155], Articles 11 to
  16, 25 and 26
- [IETF Datatracker record for draft-kamimura-scitt-vcp][vcp-dt] (checked
  again on 24 November 2026 for the addition in section 2)

[vap03]: https://datatracker.ietf.org/doc/html/draft-kamimura-vap-framework-03
[vap03txt]: https://www.ietf.org/archive/id/draft-kamimura-vap-framework-03.txt
[vcp06]: https://datatracker.ietf.org/doc/html/draft-kamimura-scitt-vcp-06
[vcp07]: https://datatracker.ietf.org/doc/html/draft-kamimura-scitt-vcp-07
[vcp-dt]: https://datatracker.ietf.org/doc/draft-kamimura-scitt-vcp/
[reg1155]: https://eur-lex.europa.eu/eli/reg_del/2025/1155/oj
