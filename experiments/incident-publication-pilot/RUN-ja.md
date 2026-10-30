# 原稿・開示・承認を結びつけるローカル公開実験

この実験は、本文とAI利用開示を一つのHTMLにまとめ、その完成版に対応する署名付き承認を確認してから、
管理されたローカルディレクトリへ出力します。出力後のファイルを読み直し、ハッシュとバイト数を確認します。
外部サイトへの投稿、実際のAIサービス呼び出し、本番の人間による査読は行いません。

## 実行方法

Python 3.12以降と、ハードリンク・ディレクトリ同期・シンボリックリンクを追わないファイル操作を利用できる
Linux環境を使います。ソケットや外部ネットワークは不要です。リポジトリのルートから実行してください。

```sh
python3 -m venv .venv-publication
.venv-publication/bin/python -m pip install -r experiments/incident-publication-pilot/requirements.txt
cd experiments/incident-publication-pilot
../../.venv-publication/bin/python -W error::ResourceWarning run_tests.py --require-no-skips
../../.venv-publication/bin/python -m publication_pilot run-suite --output generated
../../.venv-publication/bin/python -m publication_pilot verify-exports generated
```

既存の結果を上書きしないため、再実行では別の出力先を指定してください。
終了コード0は、18シナリオの期待値との一致と、出力証拠の整合性確認が完了した場合です。
期待値との不一致は1、入力・実行が不完全な場合は2になります。

## 確認できること

編集器は、各操作の前後の文書ハッシュ、操作順、対象段落、操作種別、観測時刻を署名付きで残します。
過去にAI相当の操作が記録されていても、その後に手動で置き換えた段落を「AI出力がそのまま残った段落」とは扱いません。
過去の操作履歴は残し、開示対象から黙って取り除くこともしません。

承認対象には、完成HTML、開示文、掲載先、規程の版・内容、編集履歴、有効期間を結びつけます。
本文・開示・掲載先などが変わった場合に、古い承認で出力することはできません。
開示が正しくても、適用する公開規程がその操作を禁止していれば止めます。

出力予定をSQLiteに保存した後、出力の直前に承認と規程の有効性を再確認します。
同じ要求を再実行しても重複出力せず、既存ファイルを上書きしません。
ファイル作成後に結果の保存が失敗した場合は、出力済みの可能性を残したまま結果を未確定にします。

## 結果の読み方

| 結果 | 意味 |
| --- | --- |
| `LOCAL_OUTPUT_CONFIRMED` | ローカル出力の一致を計測し、受領証を保存した |
| `BLOCKED_WITHOUT_PUBLICATION` | この呼び出しでは新しい出力を作成しなかった |
| `OUTCOME_UNKNOWN` | 出力・観測・結果保存のどこかが未確定。自動再実行しない |
| `REPLAY_NO_PUBLICATION` | 既存の要求記録があるため、出力し直さない |
| `REQUEST_ID_CONFLICT` | 同じ要求IDが別の原稿に使われている |

前段の評価器は引き続き `publication_action: REVIEW` を返します。
この実験の出力許可は、別途署名されたレビュー担当者の承認に基づくアプリ側の処理です。
実験用の承認署名は、本物の人間が読んだことを証明しません。

取り込んだ文章の由来、編集器の外での作業、記録以前のAI利用は不明のままです。
「記録がないから人間だけで書いた」「AI生成率は何％」とは判定しません。
操作のAIラベルも合成実験の指定であり、外部AIの実行証明ではありません。

実際のHTMLは `generated/runtime/LP-NN/visible/`、署名・承認・評価結果は `generated/cases/` に出力されます。
公開証拠には合成原稿の本文を含みますが、秘密署名鍵は含めません。
保存済み証拠の再検証は公開操作を繰り返さず、現在の出力ファイルを新たに観測するものでもありません。
実行結果は [実行記録](results/README.md)、信頼する範囲は [README](README.md) を参照してください。
