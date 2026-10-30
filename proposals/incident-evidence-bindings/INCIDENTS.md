# Incident fact ledger

**Checked:** 2026-10-30 JST

**Status:** Informative / unadopted proposal

For design discussion only, not liability findings, technical attribution, vendor identification, or VAP-prevention claims. Dates retain source-local dates.

## Verdicts

- `PRIMARY_CONFIRMED`: primary source supports an attributed fact or institutional finding.
- `SUPPORTED_REPORTING`: secondary reporting; underlying hospital notice not independently fetched.
- `INDEX_CORROBORATED`: a search-indexed database page supports the stated metadata association, not independent incident facts.
- `NOT_ESTABLISHED`: not established by inspected evidence; not necessarily false.
- `CORRECTED`: initial framing corrected below.

## Johns Hopkins Bayview Medical Center

No primary hospital notice was independently retrieved.

| Claim ID | Verdict | Finding or correction | Sources | Checked (JST) |
| --- | --- | --- | --- | --- |
| BAY-001 | SUPPORTED_REPORTING | A worker uploaded a patient spreadsheet to an unapproved public AI tool on September 21, 2026; discovery occurred that day. | [B1][b1], [B2][b2] | 2026-10-30 |
| BAY-002 | SUPPORTED_REPORTING | Approximately 3,182 patients were being notified about possible disclosure; the file may have included names, medical record numbers, treatment dates and medications. | [B1][b1] | 2026-10-30 |
| BAY-003 | SUPPORTED_REPORTING | Patient notification letters began October 22. | [B1][b1], [B2][b2] | 2026-10-30 |
| BAY-004 | SUPPORTED_REPORTING | The worker removed the prompt, conversation and document from tool history; the hospital requested provider-side deletion. | [B1][b1], [B2][b2] | 2026-10-30 |
| BAY-005 | NOT_ESTABLISHED | Completed provider-side erasure, retention duration, training use, downstream access and the provider's identity are not established by these sources. | [B1][b1], [B2][b2], [B3][b3] | 2026-10-30 |
| BAY-006 | NOT_ESTABLISHED | An absence of all audit logs, log tampering, and technically impossible retrospective investigation are not established. | [B1][b1], [B2][b2], [B3][b3] | 2026-10-30 |
| BAY-007 | CORRECTED | Reporting existed by October 23; Healthcare IT News published its account October 29. | [B2][b2], [B4][b4], [B3][b3] | 2026-10-30 |
| BAY-008 | NOT_ESTABLISHED | Whether evidence was preserved before tool-history removal, and when the full affected scope was identified, are not established by the inspected public sources. | [B1][b1], [B2][b2], [B3][b3] | 2026-10-30 |

## Dartmouth

| Claim ID | Verdict | Finding or correction | Sources | Checked (JST) |
| --- | --- | --- | --- | --- |
| DAR-001 | PRIMARY_CONFIRMED | Dartmouth announced Santiago Schnell's resignation and departure October 28, 2026. The university says Schnell decided. | [D1][d1] | 2026-10-30 |
| DAR-002 | PRIMARY_CONFIRMED | The committee's October 27 report found substantial AI assistance without required disclosure in a ChemSystemsChem manuscript. | [D2][d2], pp. 3–4 | 2026-10-30 |
| DAR-003 | CORRECTED | Enterprise Claude logs existed and were examined. Requested personal-account logs were not supplied; claiming no audit trail is inaccurate. | [D2][d2], pp. 2–3 | 2026-10-30 |
| DAR-004 | CORRECTED | The newspaper policy described in the report prohibited AI-created or manipulated submissions; disclosure alone would not resolve that restriction. | [D2][d2], p. 4 | 2026-10-30 |
| DAR-005 | PRIMARY_CONFIRMED | For a separate Springer paper, policy changes and available evidence prevented the committee from concluding a publication-policy violation. | [D2][d2], pp. 4–5 | 2026-10-30 |
| DAR-006 | PRIMARY_CONFIRMED | The committee did not conduct formal policy complaint procedures or recommend disciplinary action. | [D2][d2], p. 1 | 2026-10-30 |
| DAR-007 | PRIMARY_CONFIRMED | The report dates Schnell's journal email describing ChatGPT use but omitting Claude to October 6, 2026. | [D2][d2], p. 4 | 2026-10-30 |

## Identifier and correction history

- **2026-10-30 — Initial verification:** distinguished evidence types; corrected chronology, log-absence claims and disclosure-versus-permission assumptions. REF-001 was initially not established because the direct citation page could not be retrieved.
- **2026-10-30 — Follow-up verification:** corroborated REF-001 through indexed AIID metadata; added the preservation/scope-timing limitation (BAY-008) and the report's journal-email date (DAR-007).
- **REF-001 — `INDEX_CORROBORATED`, checked 2026-10-30 JST:** AIID's search-indexed Discover pages associate Incident `1792` with this Bayview incident and Healthcare IT News ([B5][b5], [B6][b6]). The direct citation page was not retrieved; registration date and total report count remain unverified. Incident facts rely on the reporting above, not independent confirmation by the database.
- Retain claim IDs when recording corrections and new evidence.

## Source register

| ID | Title | Published | Type |
| --- | --- | --- | --- |
| B1 | [Johns Hopkins alerts 3,182 patients after worker uploads data to unapproved AI tool][b1] | 2026-10-26 | Becker's Hospital Review; secondary reporting |
| B2 | [Johns Hopkins alerts 3,000+ patients after data sent to AI tool][b2] | 2026-10-23 | WMAR; secondary reporting; date corroborated by B4 |
| B3 | [At Johns Hopkins, shadow AI use linked to data breach][b3] | 2026-10-29 | Healthcare IT News; secondary reporting |
| B4 | [Local News][b4] | Listing checked 2026-10-30 | WMAR article index; publication-date evidence |
| B5 | [AI Incident Database Discover: Healthcare IT News][b5] | Indexed result checked 2026-10-30; registration date unverified | Database's search-indexed metadata |
| B6 | [AI Incident Database Discover: Mike Miliard][b6] | Indexed result checked 2026-10-30; registration date unverified | Database's search-indexed metadata |
| D1 | [An Update on the Provost Review][d1] | 2026-10-28 | Dartmouth president; primary announcement |
| D2 | [Review of Concerns Regarding AI Use by Provost Santiago Schnell][d2] | 2026-10-27 | Independent advisory committee; primary report |

[b1]: https://www.beckershospitalreview.com/healthcare-information-technology/ai/johns-hopkins-alerts-3182-patients-after-worker-uploads-data-to-unapproved-ai-tool/
[b2]: https://www.wmar2news.com/local/patients-data-sent-to-ai-tool-johns-hopkins-bayview-medical-center-oct-23-2026
[b3]: https://www.healthcareitnews.com/news/johns-hopkins-shadow-ai-use-linked-data-breach
[b4]: https://www.wmar2news.com/local
[b5]: https://incidentdatabase.ai/apps/discover/?source_domain=healthcareitnews.com
[b6]: https://incidentdatabase.ai/apps/discover/?authors=Mike+Miliard
[d1]: https://president.dartmouth.edu/news/2026/10/update-provost-review
[d2]: https://president.dartmouth.edu/sites/president/files/2026-10/Advisory%20Committee%20Report%20to%20President%202026-10-27.pdf
