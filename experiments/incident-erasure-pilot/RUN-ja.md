# 削除証跡のローカル実証

この実験は、削除要求・事業者の受領・限定された削除確認・同一管理者による観測を
区別して記録します。合成データ1件のファイル操作を実行し、元の署名付き証跡を
オフラインで再検証できます。VAPの規範仕様、既存評価器の判定、医療・大学の
実データを変更するものではありません。

## 実行方法

Linux/POSIX、Python 3.12 または 3.14 で、このディレクトリから実行します。

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -W error::ResourceWarning run_tests.py --require-no-skips
.venv/bin/python -m erasure_pilot run-suite --output generated --print-summary
.venv/bin/python -m erasure_pilot verify-exports generated
```

`generated` は存在しない新しいディレクトリを指定してください。既存の結果は
上書きしません。ネットワーク、AIサービス、実アカウントの認証情報は不要です。

## 判定の読み方

| 出力 | 確認できたこと |
|---|---|
| `REQUEST_ONLY` | 対象と範囲を結び付けた削除要求 |
| `ACKNOWLEDGED` | 事業者役が要求を受領したこと。削除完了を意味しない |
| `PROVIDER_ATTESTED_WITHIN_DECLARED_SCOPE` | 事業者役による対象範囲内の削除声明 |
| `REMOVAL_OBSERVED_SAME_CONTROLLER` | 同一管理者が、対象の存在と内容、操作後の名前の不在を観測したこと |
| `ABSENCE_ONLY` | 観測時点で名前が見つからないこと。以前の存在や当該操作による削除は確定しない |
| `PRESENT_AT_OBSERVATION` | 後の観測時点でファイルが存在すること |
| `OUTCOME_UNKNOWN` | 操作や結果保存に不確実性が残ること。完了証明は返さない |

既存評価器の `target_completion`、`provider_completion`、対象外の結果は
`UNKNOWN` のままです。独立検証も `NOT_ESTABLISHED` のままです。別の署名鍵を
使っても、同じ管理者・実行環境からの観測を第三者監査にはしません。

18シナリオには、受領だけでファイルが残るケース、削除直前の権限期限切れ、
内容・テナント・署名の不一致、二重要求・競合、削除後の結果保存失敗、
事前から不在だった対象、削除後の再作成、開いたままのファイルと別コピーの
読み取りを含みます。最後の2件は、名前を削除しても元の合成データが読めることを
実際に測定する確認用ケースです。

## 証拠の保存と再検証

`generated/cases/` に署名付きの元要求、応答、観測、公開鍵設定、判定を保存し、
`generated/summary.json` に結果と実行ソースのハッシュを保存します。CIが
公開するのはこの2種類です。合成オブジェクト本文、秘密鍵、実行用DBは含めません。
不透明なIDやハッシュもメタデータであり、実データの匿名化保証ではありません。

`verify-exports` は同じソースで、保存された署名・結び付け・時系列・集計を
再確認します。削除を再実行せず、外部事業者のストレージも調査しません。
公開鍵設定自体が実験管理者の仮定であり、独立した本人確認や外部タイムスタンプは
ありません。実行ソースが変わった場合は、対応するコミットで再検証してください。

削除操作はリクエストIDに対して一度だけです。結果保存が失敗しても自動再試行
しません。受領のみのケースも、同じ要求の再送によって削除へ進みません。
本番向けの再調整・再開ワーカーは、この実験の対象外です。

実測結果は [results/README.md](results/README.md)、内部レビューは
[REVIEW.md](REVIEW.md)、詳細な境界は [README.md](README.md) と
[CONTRACT.md](CONTRACT.md) を参照してください。バックアップ、学習派生物、
下流コピー、メモリ、記憶媒体の完全消去や法令適合は証明しません。
