# Incident fact ledger

**Last updated:** 2026-11-01 JST. Each claim retains its own check date.

**Status:** Informative / unadopted proposal

For design discussion only, not liability findings, technical attribution, vendor identification, or VAP-prevention claims. Dates retain source-local dates.

## Verdicts

- `PRIMARY_CONFIRMED`: primary source supports an attributed fact or institutional finding; this does not mean independent validation of raw forensic evidence.
- `SUPPORTED_REPORTING`: attributed secondary reporting; each section identifies the underlying material inspected or unavailable.
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

## 91APP

Company statements, the authority's narrower confirmation and reporting are kept separate.
No incident logs, customer records or forensic evidence package were accessed for this review.
See the [design note](91APP-EVIDENCE-REVIEW.md) ([日本語](91APP-EVIDENCE-REVIEW-ja.md));
none of these claims is an input to the existing synthetic experiments.

| Claim ID | Verdict | Finding or correction | Sources | Checked (JST) |
| --- | --- | --- | --- | --- |
| APP-001 | PRIMARY_CONFIRMED | 91APP dates intrusion to October 3 and containment to October 14, 2026. It reports ARTEX traces in its systems; its route reconstruction describes unpatched Appsmith, GitLab-held database credentials and the orders database. | [A1][a1] | 2026-11-01 |
| APP-002 | PRIMARY_CONFIRMED | Taiwan's Administration for Digital Industries confirmed unauthorized acquisition of some data in its October 20 notice; exact types were then still under investigation. That notice does not establish ARTEX attribution or the later maximum affected count. | [A3][a3] | 2026-11-01 |
| APP-003 | PRIMARY_CONFIRMED | The October 29 company update gives a maximum of 1,329 brands and 4,798,255 consumers, using the April 4, 2025–October 14, 2026 order-date window because the exact stolen orders could not be determined. This is not confirmation that all listed consumers' data was stolen. | [A2][a2] | 2026-11-01 |
| APP-004 | PRIMARY_CONFIRMED | The company describes Appsmith removal, credential and permission updates, and restrictions between CI and database systems. These are reported remediation actions, not this repository's validation of their effectiveness. | [A1][a1] | 2026-11-01 |
| APP-005 | CORRECTED | 91APP says it notified brands October 29. Consumer notification was planned from November 2 subject to brand authorization; an unqualified "unnotified incident" label is inappropriate. | [A2][a2], [A5][a5] | 2026-11-01 |
| APP-006 | SUPPORTED_REPORTING | CNA reports that compensation amounts and the earnings effect were not yet estimable. This does not establish a measured total of victims' financial losses. | [A4][a4] | 2026-11-01 |
| APP-007 | NOT_ESTABLISHED | Full autonomous execution, attribution to the same actors as another ARTEX incident, and a specific CVE are not established by these reviewed sources. Exact software versions and raw forensic evidence were not examined. | [A1][a1], [A2][a2], [A3][a3] | 2026-11-01 |
| APP-008 | NOT_ESTABLISHED | These sources do not establish a VAP/VCP deployment, an authenticated VAP evidence package, or that adopting either framework would have prevented this attack. | [A1][a1], [A2][a2], [A3][a3] | 2026-11-01 |

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
- **2026-11-01 — 91APP addition:** separated company claims, authority confirmation, maximum exposure, notification plans and unresolved attribution. Added an informative English/Japanese design note; no incident evidence or executed test was added.
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
| A1 | [91APP incident account][a1] | 2026-10-22; reviewed 2026-11-01 | Primary company account |
| A2 | [91APP scope update][a2] | 2026-10-29 | Primary company update |
| A3 | [Administration for Digital Industries incident notice][a3] | 2026-10-20 | Official authority notice; narrower confirmation |
| A4 | [CNA report on 91APP's updated scope and compensation][a4] | 2026-10-29 | Central News Agency; secondary reporting |
| A5 | [91APP notification and compensation information][a5] | 2026-10-29 | Primary company notice; future steps remain attributed plans |

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
[a1]: https://91app.com/91app-202610-security-incident/
[a2]: https://91app.com/blog/91app-202610-security-incident-2/
[a3]: https://moda.gov.tw/ADI/news/latest-news/21118
[a4]: https://www.cna.com.tw/news/afe/202610290355.aspx
[a5]: https://91app.com/91app-202610-security-incident-compensation/
