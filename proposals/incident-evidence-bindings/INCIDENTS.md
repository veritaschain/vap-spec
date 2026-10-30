# Incident fact ledger

**Last updated:** 2026-10-31 JST. Each claim retains its own check date.

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

## Panasonic group

The primary notice attributes the operation to a project member. It does not establish autonomous-agent misconduct.

| Claim ID | Verdict | Finding or correction | Sources | Checked (JST) |
| --- | --- | --- | --- | --- |
| PAN-001 | PRIMARY_CONFIRMED | Panasonic Operational Excellence's October 23 notice says a human-resources system project member uploaded personal data to a prohibited external generative-AI service. | [P1][p1] | 2026-10-31 |
| PAN-002 | PRIMARY_CONFIRMED | Reported affected groups total approximately 334,000: 75,000 employees, 178,000 former employees, 55,000 employees' family members and 26,000 former employees' family members. | [P1][p1] | 2026-10-31 |
| PAN-003 | PRIMARY_CONFIRMED | The company reports notifying Japan's Personal Information Protection Commission on September 29 and removing chat history and local PC data after discovery. | [P1][p1] | 2026-10-31 |
| PAN-004 | PRIMARY_CONFIRMED | According to the company's account of the provider's response, training use was disabled, but deleted data remained subject to 30-day security/legal-compliance retention. | [P1][p1] | 2026-10-31 |
| PAN-005 | PRIMARY_CONFIRMED | The October 23 notice says provider retention would end from October 25; it reports no confirmed public exposure or concrete misuse-related harm at publication. | [P1][p1] | 2026-10-31 |
| PAN-006 | NOT_ESTABLISHED | The notice does not identify the AI provider, exact upload/deletion dates, or an independent post-deadline examination of all copies. | [P1][p1] | 2026-10-31 |

Training settings, retention terms and later deletion observations answer different questions.
A stated retention end date is not itself an observation of deletion. Passing that date does not
upgrade an attributed statement into independently verified completion. No provider receipt from
this incident is imported into the synthetic assessor or represented as authenticated experimental evidence.

## Japanese regulatory context (not an incident finding)

| Claim ID | Verdict | Finding or correction | Sources | Checked (JST) |
| --- | --- | --- | --- | --- |
| JP-001 | PRIMARY_CONFIRMED | e-Gov case 240000133 accepts comments from October 29 through November 27, 2026, at 23:59 on amendments to the general and two specific-personal-information guidelines. | [J1][j1] | 2026-10-31 |
| JP-002 | PRIMARY_CONFIRMED | The official overview describes added/clarified examples of security measures, not new rules; examples include retaining logs for a period. | [J2][j2], pp. 3, 5, 8 | 2026-10-31 |
| JP-003 | PRIMARY_CONFIRMED | Citing large-scale unauthorized-access/leak incidents, the overview aims to bring implementation forward from the earlier April 2027 plan; it supplies no new fixed implementation date. | [J2][j2], p. 2 | 2026-10-31 |
| JP-004 | NOT_ESTABLISHED | These materials do not establish Panasonic-specific causation, an AI-specific new audit duty, or a requirement to adopt VAP or cryptographic completeness proofs. | [J1][j1], [J2][j2] | 2026-10-31 |

This is a source-bounded policy note, not an exhaustive finding that no other regulatory change occurred.

## Identifier and correction history

- **2026-10-30 — Initial verification:** distinguished evidence types; corrected chronology, log-absence claims and disclosure-versus-permission assumptions. REF-001 was initially not established because the direct citation page could not be retrieved.
- **2026-10-30 — Follow-up verification:** corroborated REF-001 through indexed AIID metadata; added the preservation/scope-timing limitation (BAY-008) and the report's journal-email date (DAR-007).
- **2026-10-31 — Primary-source addition:** added Panasonic's notice and the Japanese security-measures consultation. Separated company/provider statements, prospective retention dates and independent deletion evidence; preserved prior claim IDs and check dates.
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
| P1 | [External generative-AI upload notice (Japanese)][p1] | 2026-10-23 | Panasonic Operational Excellence; primary company notice reporting provider responses |
| J1 | [Guideline amendment consultation, case 240000133 (Japanese)][j1] | 2026-10-29 | e-Gov; official consultation and deadline |
| J2 | [Overview of additions to security-measures examples (Japanese)][j2] | 2026-10; linked from J1 | Personal Information Protection Commission; official consultation overview |

[b1]: https://www.beckershospitalreview.com/healthcare-information-technology/ai/johns-hopkins-alerts-3182-patients-after-worker-uploads-data-to-unapproved-ai-tool/
[b2]: https://www.wmar2news.com/local/patients-data-sent-to-ai-tool-johns-hopkins-bayview-medical-center-oct-23-2026
[b3]: https://www.healthcareitnews.com/news/johns-hopkins-shadow-ai-use-linked-data-breach
[b4]: https://www.wmar2news.com/local
[b5]: https://incidentdatabase.ai/apps/discover/?source_domain=healthcareitnews.com
[b6]: https://incidentdatabase.ai/apps/discover/?authors=Mike+Miliard
[d1]: https://president.dartmouth.edu/news/2026/10/update-provost-review
[d2]: https://president.dartmouth.edu/sites/president/files/2026-10/Advisory%20Committee%20Report%20to%20President%202026-10-27.pdf
[p1]: https://holdings.panasonic/jp/information/topics/20261023.html
[j1]: https://public-comment.e-gov.go.jp/pcm/detail?CLASSNAME=PCMMSTDETAIL&Mode=0&id=240000133
[j2]: https://public-comment.e-gov.go.jp/pcm/download?seqNo=0000323105
