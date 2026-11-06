# Source ledger — Japan policy review, 6 November 2026

**Informative review. Cutoff: 6 November 2026 (JST).**

[English design note](README.md) · [日本語設計ノート](README-ja.md)

This ledger records what was directly inspected and which claims remain
attributed to reporting. It is not a sealed source archive or a comprehensive
legal applicability assessment. The design proposals in the linked notes are
VSO analysis; they are not instructions issued by the cited institutions.

| ID | Source and date | Verified proposition and documentary status |
|---|---|---|
| JP-CYBER-01 | [財務省・閣議後記者会見](https://www.mof.go.jp/public_relations/conference/my20261106.html), 6 November | Official transcript: Cabinet approved JPY 10 billion in reserve spending, including JPY 2 billion for AI-assisted checks of important government systems. At this morning statement, the package was still described as forthcoming. Budget approval and later package adoption are distinct. |
| JP-CYBER-02 | [共同通信「政府、ブロッキング検討 サイバー対策にAI活用」 via Livedoor](https://news.livedoor.com/article/detail/32750577/), 6 November; inspected page shows 18:28 JST | Media report of package adoption at the ministerial meeting. It describes planned expert teams and consideration of access blocking. It does not establish an implemented blocking regime. The final official package text was not directly retrieved in this review. |
| JP-DATA-01 | [NCO「不正アクセスによる漏えい等の事案を踏まえた対応について」, official copy hosted by MHLW](https://www.mhlw.go.jp/content/001765075.pdf), 9 October, pp. 2–4 | Existing government advisory: vendor/subcontractor oversight and end-of-work deletion; data inventory, purpose and retention periods; minimization, backup protection and access logs. This is not the 6 November package or a newly enacted AI-specific duty. |
| JP-AGENT-01 | [消費者委員会](https://www.cao.go.jp/consumer/) and [第14回会議資料](https://www.cao.go.jp/consumer/kabusoshiki/ai_technology/014/shiryou/index.html) | The homepage announces materials on 6 November; the meeting was 5 November, 10:00 JST. The inspected meeting page lists the agenda and Professor Tokutsu's presentation. Minutes were marked in preparation. |
| JP-AGENT-02 | [得津晶教授「AI vs AI」時代の消費者保護法制](https://www.cao.go.jp/consumer/kabusoshiki/ai_technology/doc/014_261105_shiryou1.pdf), 5 November; pp. 3, 6–8 | Individual expert presentation: provider/user conflicts, possible sponsor-biased output, foreign agent-design models and co-regulation questions. These are discussion points, including an anecdote, not an adopted Japanese regime or a verified manipulation incident. The inspected slides do not require cryptographic audit logs or VAP. |
| JP-AGENT-03 | [第14回議事次第](https://www.cao.go.jp/consumer/kabusoshiki/ai_technology/doc/014_261105_gijishidai.pdf), 5 November | The agenda includes a secretariat progress report, but its published distribution list contains the professor's presentation only. Do not invent a separately published new secretariat proposal or infer committee consensus from this agenda. |
| JP-VENDOR-01 | [楽天証券「委託先への不正アクセスによるメールアドレスの漏えいの可能性について」](https://www.rakuten-sec.co.jp/web/info/info20261105-01.html), 5 November | Company notice of possible exposure of 2,109 alert-service email addresses through MINKABU's mail contractor Arara. It attributes the access to Arara, not Rakuten Securities' systems. The notice does not identify AI involvement. This is a vendor-risk example, not a verified AI attack or a finding of completed leakage. |

## Verification boundaries / 確認の境界

- **Final policy wording:** Adoption is supported by the cited reporting;
  the directly read MOF transcript supports the budget decision. Failure to
  retrieve the final package does not prove that it has not been published.
  Its exact retention/deletion wording remains unverified here.
- **Dates:** 5 November meeting, 6 November materials publication and the
  9 October advisory are different events. The Kyodo page inspected at review
  shows 18:28; an earlier distribution time must not replace its current display.
- **Legal effect:** A policy package, budget decision, advisory, expert's model
  and enacted obligation have different status. The materials reviewed do not
  establish a newly applicable AI-specific AILEX duty or VAP/VCP mandate.
  This bounded finding is not an assurance that no other obligation exists.
- **Evidence design:** Commercial-relationship bindings, candidate inventories,
  display observations and deletion assessment cases in this proposal are VSO
  design choices. The presentation is not evidence that an operator lacked
  logs, that a sponsor manipulated a particular result or that VAP would have
  prevented an incident.
- **Vendor incident:** Keep JP-VENDOR-01's possibility qualifier and the specific
  email-service route. No AI attribution in the notice is not proof that AI was
  absent. The example does not establish deficient logs or a VAP-preventable cause.

日本語での運用上の区分は、**「予算措置は一次確認」「パッケージ採択は報道確認・
最終本文は未取得」「消費者エージェント規律は有識者の議論」「保存・削除の具体論は
10月9日の既存注意喚起」**となる。これらを混同して、新法成立、VAP導入義務、
政府の承認、製品の適合確認と表現しない。

## Follow-up evidence / 次に確認する証拠

Obtain the final government package and its official decision record; then
compare the exact operative wording and any implementation documents. Review
published committee minutes and separately identifiable official proposals
before attributing a position to the committee. Any obligation claim needs its
own authoritative text, covered actor/use, applicability date and analysis.
These are verification tasks, not predictions that new rules will arrive within
a fixed week.
