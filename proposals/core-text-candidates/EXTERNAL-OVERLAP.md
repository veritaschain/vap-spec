# Overlap with `draft-mih-scitt-agent-action-capsule` and its IPR disclosures

**Status:** Informative review note for the candidate text in this directory. Not a legal opinion, not a
freedom-to-operate analysis, and not a statement by or on behalf of the draft's author.
**Checked:** 28 November 2026 (JST), with AI assistance (Claude, Anthropic). First-party work, not
independently reviewed.

Earlier VSO reviews deferred drafting on record origin (F7), the resolution invariant (F8) and evaluation
dimensions (F9) until the IPR statements on this Internet-Draft had been read. This note records what was
read and what follows for drafting.

## 1 What was read

| Item | Finding | Source |
| --- | --- | --- |
| Draft | `draft-mih-scitt-agent-action-capsule-06`, dated 24 November 2026, expires 28 May 2027. Individual submission by one author (Action State Group, Inc.); not adopted by a working group; the stated venue for discussion is the SCITT WG list | [Datatracker][dt] |
| Disclosures on file | Eight | [Datatracker API][api] |
| Disclosures of 13 June 2026 (#7347 to #7350) | Four statements by the author as patent holder, each naming one US application dated 26 May 2026 and one part of revision 00: section 5.4 (verdict lifecycle and ledger model), section 5.4 (approver and `human_disposed` model), section 5.2 (confirmed-effect binding) and section 8.1 (deterministic predicate). Each carried a royalty-free reasonable-and-non-discriminatory licensing declaration | [API][api], [#7347][i7347], [#7348][i7348], [#7349][i7349] |
| Updates of 6 July 2026 (#7384 to #7387) | Each updates one of the four. Each states that the application was expressly abandoned on 6 July 2026 under 37 CFR 1.138, that nothing is pending and no continuation, conversion or priority claim will be filed, and changes the licensing declaration to "No License Required for Implementers". Each lists revisions 00 to 02 and no sections. Each says a public non-assertion covenant is to be published on the holder's website, with the link to follow | [#7384][i7384], [#7385][i7385], [#7386][i7386], [#7387][i7387] |

**Not confirmed.**

- The text of the non-assertion covenant. The holder's website was not retrieved in this check, so
  whether the covenant has been published, and its scope and conditions, are unknown here.
- The status of the four applications at the patent office. The findings above are the holder's own
  statements in the disclosures.
- Whether any disclosure covers revisions 03 to 06. None on file lists them.
- Sections 6 to 16 and the appendices of revision 06. The retrieval returned the document up to
  section 5.5.5 only.
- The earlier VSO note that the Datatracker API showed twelve disclosure records. The API returned eight
  on this date; the difference was not investigated.

## 2 Where the draft and the candidate subjects meet

From revision 06, sections 1 to 5.5.5. Field and value names are the draft's and are cited as identifiers.

| VAP candidate subject | Related material in the draft | Section |
| --- | --- | --- |
| F7, origin of a record | Grades for how an effect was attested (`effect_attestation`); `attestation_mode` separating self-attested from anchored; a ranking of counterparty evidence (`cross_party_rung`); self-attested versus witnessed time (`time_rung`) | 5.3, 5.4, 5.4.1, 5.4.3 |
| F8, resolution invariant | A predicate for open items by verdict, closed by a later record linked with `supersedes`; a binding rule for the closing record; a rule for concurrent closures | 5.5.4 |
| F9, evaluation dimensions | Separation of an effect that was dispatched from one whose result was observed and bound, with a status that the verifier re-derives from the evidence | 1, 5.3, 5.4 |
| F14, replacement of a decision | A later resolution as a separate record linked to the earlier one, which is never changed | 5.5.4 |
| Approval references (earlier candidate N-3) | A disposition block with a closed set of approver kinds, a flag that is true only when a human acted, and an opaque reference to the authority behind a non-human disposition | 5.5 |

The draft is a SCITT statement profile for one record type with its own fields and verifier classes. VAP is
a metaframework whose candidate text states distinctions and leaves fields to profiles. The two are at
different levels, and the overlap is in the distinctions, not in shared text or shared structures.

## 3 What follows for drafting

1. **The stated reason for deferral no longer holds on the record read.** Each disclosure now on file
   declares that no licence is required and that the underlying application was abandoned. That is the
   holder's statement, and the covenant it mentions was not read; subject to those two limits, the
   disclosures do not give a reason to withhold candidate text on F7, F8 or F9.
2. **Write at the level of distinctions.** The candidate text in [README.md](README.md) names no fields
   and no enumerations for F7 and F9. Keep it so. If names are needed later, either reference the draft's
   identifiers explicitly or choose VAP's own; do not reproduce the draft's tables or prose. The draft's
   text is under the IETF Trust's licence terms.
3. **Derive F8 from the VAP family's own invariants.** CAP v1.0 (attempt and outcome accounting), DAP
   and SMP already contain invariants of the same shape. An F8 draft should generalize those and cite the
   Internet-Draft as related work.
4. **Cite it as related work.** No VAP text or public material should state or imply that no other
   specification makes these distinctions.
5. **Re-check before a normative proposal.** Read the covenant if published, read sections 6 to 8 of the
   current revision (verification classes and the deterministic predicate), and look again at the
   disclosure list. VAP is not an IETF document; whether VSO needs its own IPR policy for contributions to
   VAP is a separate question that this note does not answer.

## Sources

- [Datatracker document page][dt]; [revision 06][d06]
- [Datatracker API, IPR records for the draft][api]
- IPR disclosures [#7347][i7347], [#7348][i7348], [#7349][i7349], [#7384][i7384], [#7385][i7385],
  [#7386][i7386], [#7387][i7387]. Disclosure #7350 was read only through the API record and the update
  that supersedes it.

[dt]: https://datatracker.ietf.org/doc/draft-mih-scitt-agent-action-capsule/
[d06]: https://datatracker.ietf.org/doc/html/draft-mih-scitt-agent-action-capsule-06
[api]: https://datatracker.ietf.org/api/v1/ipr/iprdocrel/?document__name=draft-mih-scitt-agent-action-capsule&format=json&limit=50
[i7347]: https://datatracker.ietf.org/ipr/7347/
[i7348]: https://datatracker.ietf.org/ipr/7348/
[i7349]: https://datatracker.ietf.org/ipr/7349/
[i7384]: https://datatracker.ietf.org/ipr/7384/
[i7385]: https://datatracker.ietf.org/ipr/7385/
[i7386]: https://datatracker.ietf.org/ipr/7386/
[i7387]: https://datatracker.ietf.org/ipr/7387/
