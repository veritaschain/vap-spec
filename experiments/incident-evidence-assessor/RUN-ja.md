# インシデント証拠評価器：日本語実行ガイド

これは、[提案の23件の受入条件](../../proposals/incident-evidence-bindings/acceptance-cases.json)を
構造化した合成証拠で試す、非規範的なオフライン参照実装です。
VAP/CAPへの適合、実際のアップロード防止、外部サービスの完全削除、出版社の開示承認を
判定するものではありません。仕様の位置付けは VAP v1.2.0 Draft 3 のままです。

## 1. 全ケースを再実行する

Python 3.12 以降を使い、リポジトリのルートから実行します。

```sh
python3 -m venv .venv-incident
.venv-incident/bin/python -m pip install -r experiments/incident-evidence-assessor/requirements.txt
cd experiments/incident-evidence-assessor
../../.venv-incident/bin/python -m unittest discover -s tests -v
../../.venv-incident/bin/python -m incident_assessor run-suite
```

各行に `MATCH` が表示され、最後に `23/23 scenario expectations matched` と表示されれば、
指定された判定項目が一致しています。否定ケースの `MATCH` は「期待どおり拒否・不明・要確認に
なった」という意味で、証拠の合格や事件の防止を意味しません。

`generated/fixtures/` に合成入力と評価者の信頼設定、`generated/reports/` に個別の評価結果、
`generated/summary.json` に期待値・実測値・差分・各種ハッシュ・実行環境が保存されます。
ランタイムはケースIDや期待値を読みません。テスト側だけが、判定処理の結果と元のカタログを比較します。

## 2. 一つの証拠パッケージを評価する

```sh
../../.venv-incident/bin/python -m incident_assessor assess generated/fixtures/UP-05.input.json \
  --trust generated/fixtures/UP-05.trust.json --allow-synthetic \
  --output generated/example.report.json
```

`UP-05` は、拒否された要求と同じ対象について送信が観測されたケースです。
結果では `transfer_authorization: DENY`、`transfer_observation: OBSERVED`、
`control_assessment: VIOLATION` が別々に表示されます。署名が正しいことと、操作が許可されることを
分けて確認できます。

`--trust` は、評価者が証拠とは別に選ぶ設定ファイルです。対象、評価時点、workflow、発行者、
公開鍵、役割、組織を固定します。配布されたテスト設定を実データにそのまま使わないでください。
合成鍵には `--allow-synthetic` が必要です。公開されているテスト秘密鍵は実運用には使えません。

`assess` の終了コード `0` は、結果ファイルを作れたことだけを表します。
拒否・要確認・不明の結果でも `0` です。自動処理は必ず `assessments` の各項目を読みます。
不正な入力は `2`、全ケース比較の不一致は `1` です。

## 3. 結果を読む

| 主な項目 | 確認すること |
| --- | --- |
| `evidence_checks` | 署名、信頼する発行者、役割、時刻の前提、対象の不一致 |
| `proposed_transfer_authorization` / `observed_action_authorization` | 許可時と実送信時を分けた評価 |
| `deletion_evidence` | 要求のみ、受付、事業者の限定的主張、対象を限定した審査報告の区別 |
| `publication_action` / `disclosure_assessment` | 禁止利用、開示不足、版の変更、確認すべき内容 |
| `response_status` | 指定された締切までに観測された応答 |
| `findings` | 判定理由のコードと根拠にした記録ID |

証拠が正しく署名されていても、患者オブジェクト・テナント・文書版が異なれば、その対象についての
根拠にはできません。記録がない場合も、観測対象外の操作がなかったとは判定しません。
削除の受付は削除完了ではなく、事業者の署名付き完了申告も外部ストレージを独立検査した結果ではありません。

公開前の文章審査は自動完了させません。開示の本文が真実で必要十分か、適切な場所に掲載されたかなどは
このコードでは審査しないため、正しく準備された公開用の正例も `REVIEW` を保ちます。
禁止されたAI利用が対象の成果物に結び付く場合は、開示があっても `BLOCK` を返します。

このコードは外部通信、削除、提出、通知を実行しません。実送信の直前に同じ判定を使うには、
対象バイト列を計測して署名する処理と、送信を制御するゲートウェイを接続する必要があります。
詳細な入力型と実装範囲は [README](README.md) と [契約](CONTRACT.md) に記載しています。
