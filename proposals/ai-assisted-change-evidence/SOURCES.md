# Source review — AI-assisted change evidence

**Checked:** 19 November 2026 JST. **Status:** Informative / unadopted.
Publication dates, legal application dates and this review date are distinct.
These sources motivate an engineering proposal; they do not validate its
implementation, require VAP adoption or establish a violation by a named firm.

## Sources and bounded conclusions

| ID | Primary source and date | Supported use and limit |
| --- | --- | --- |
| FCA-2026-11-02 | [Wholesale banks supervision — Insights 3 (Autumn 2026)][fca], published/updated 2 November 2026, AI section | FCA reports gaps in conditional approvals, undocumented production exceptions, and kill-switch training, testing, maintenance and operator-authority records. These are attributed supervisory observations. They do not identify the firms as the operators in the separate November outage reports or announce a new rule for the following week. |
| DORA-9 | [Regulation (EU) 2022/2554][dora], adopted 14 December 2022; Article 9(4)(e)–(f), Article 64 | Applicable financial entities need controlled ICT change processes and documented patch/update policies. Article 9 connects recording, testing, assessment, approval, implementation and verification. Application began 17 January 2025. This mapping does not determine whether a particular entity or incident is within scope or compliant. |
| AIA-2 | [AI Act Article 2, official Commission explorer][scope], text based on the 27 July 2026 consolidation | Scope can include third-country providers and deployers through EU-market or EU-output-use connections. Incident location alone does not settle applicability. System classification, exclusions and duties still need separate assessment. |
| AIA-113 | [AI Act consolidated text as at 27 July 2026][aia], Article 113(c), reflecting Regulation (EU) 2026/1744 | Chapter III Sections 1–3, except Article 6(5), apply from 2 December 2027 for Article 6(2)/Annex III systems and 2 August 2028 for Article 6(1)/Annex I systems. A November 2026 event alone does not establish a breach of these future high-risk logging obligations. |
| VAP-BASE | [VAP v1.2 Draft 3 at the reviewed repository baseline][vap], §§1.3, 1.6, 4.1.7, 4.2–4.4, 4.5.2, 4.6.3 and 8.2 | Existing record, traceability and attribution concepts; bounded completeness after anchoring; domain/capability composition; no safety or legal-compliance guarantee. The proposed application relationships are not normative additions. |

The exact artifact/environment/test/approval bindings, evaluation axes,
acceptance cases, emergency-exception design and proposed kill-switch records
are **VSO engineering choices**, not fields prescribed by any source above.
The FCA review is a source for the stated observations, not forensic evidence
imported into the experiment. Synthetic test data are labelled as such.

## Related incident review

The site's [19 November review of outages and Java4Shell][incident-review]
separates outage observations, possible AI-related change pressure and a
researcher's vulnerability-discovery account. A public report of hurried
patching does not establish absent audit logs, a specific patch's causal role,
or that VAP would have prevented the outage. Java4Shell's disclosure is not by
itself an AI-caused failure. Its public vulnerability identifier is not used as
proof that the experiment's synthetic target is affected.

The [incident-evidence fact ledger][ledger] adds the source-bounded FCA and
regulatory context while preserving earlier claim dates. The live-source links
here are inspection references, not sealed copies, external timestamps or
independent reproduction.

## Existing implementation references

- [Pre-record gate][gate]: unadopted local product-side execution experiment;
  synthetic authority and a loopback `create_record` backend.
- [Control-state evidence][control]: separates integrity and observed control
  state; its preflight evaluator is not wired into action admission.
- [AI-assisted change companion][experiment]: bounded reuse of the gate for a
  digest-bearing mock operation. Consult its current contract and results for
  the implemented subset, including unknown outcomes.

These references do not change fixed evidence, previous experiment results,
VAP normative text or the status of any profile.

[fca]: https://www.fca.org.uk/publications/multi-firm-reviews/wholesale-banks-supervision-insights-3-autumn-2026
[dora]: https://eur-lex.europa.eu/eli/reg/2022/2554/oj/eng
[scope]: https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-2
[aia]: https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:02024R1689-20260727
[vap]: https://github.com/veritaschain/vap-spec/blob/4db6c490900dac7e85773c39bbcc5cae935bd730/spec/v1.2/VAP_Framework_Specification.md
[incident-review]: https://github.com/veritaschain/vcp-site/blob/main/incidents/reviews/2026-11-19-ai-patching-and-java4shell.md
[ledger]: ../incident-evidence-bindings/INCIDENTS.md
[gate]: ../../experiments/pre-record-gate/README.md
[control]: ../../experiments/control-state-evidence/README.md
[experiment]: ../../experiments/ai-assisted-change-evidence/README.md
