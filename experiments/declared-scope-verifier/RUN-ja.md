# VAP 証拠提出検証器：実行ガイド

**実験用・未採択。VAP全体への適合判定や認証を行うものではありません。**
PR #10の14ケースを、実際の署名・ハッシュ・Merkle証明と提出条件の照合で実行します。
英語の[実装範囲と保存形式](README.md)が、この実験の詳細な説明です。

## 一括実行

Python 3.12以降を使用します。リポジトリ直下で初回の準備を行います。

```sh
python3 -m venv .venv-scope
.venv-scope/bin/python -m pip install -r experiments/declared-scope-verifier/requirements.txt
cd experiments/declared-scope-verifier
```

以後、次の一つのコマンドで合成データ生成・両モードの検証・14ケースの期待値照合を実行できます。

```sh
../../.venv-scope/bin/python -m scope_verifier run-suite
```

`MATCH`は期待する判定と一致した意味です。「欠落を検出する試験が成功した」ことを、
「その証拠が完全だった」と読み替えないでください。差分があれば`MISMATCH`と終了コード1を返します。

追加の回帰テストは次で実行します。

```sh
../../.venv-scope/bin/python -m unittest discover -s tests -v
```

## 結果の読み方

| 項目 | 意味 |
| --- | --- |
| `integrity.result` | 対象とした暗号学的検証：`verified`／`failed`／`indeterminate` |
| `v1_2_requirements` | 現行v1.2の要件別結果。未実装の要件も不明として表示 |
| `scope_fulfillment.result` | 実験的な提出要件：`met`／`not_met`／`indeterminate` |
| `violations` | 有効な証拠に基づく不充足の理由と参照先 |
| `unresolved` | 未解決事項。不充足や暗号学的失敗があっても消さない |
| `inventory_accounted_for` | 目録が揃っているか。本文の提出充足とは別 |

暗号学的整合性は「失敗＞不明＞検証済み」の順で集約します。これは実験用の実装規則です。
全体を無条件で合格とする出力はなく、`overall_pass`は常にnullです。

たとえば100件を抜いたケースでは、提出された900件の署名などが正しくても、INT-008は失敗、
提出要件は不充足です。非開示本文のコミットメントだけでよい合意のケースは、その狭い要件を
充足しても、全文のバッチ提出を確認した扱いにはしません。

## 二つのモード

- `--mode vap-v1.2`：現行要件の実装済み部分。宣言スコープを要求せず、拡張の判定は出しません。
- `--mode experimental-scope`：現行要件の結果に加え、未採択の実験的拡張を別項目で出します。

実装した暗号方式はEd25519とSHA-256です。`signature_valid: true`のような入力による検証の省略はできません。
信頼する鍵、ポリシー、評価ID、承認したスコープは評価者の別ファイルから読みます。

模擬受領証を使う個別実行には`--allow-synthetic`が必要です。省略すると外部証拠は不明になります。
試験用の鍵はすべて公開された合成データ用です。受領証の署名を検証できても、独立した第三者が時刻を
証明したことにはなりません。署名された観測終了の主張も、現実の全行動を観測した保証にはなりません。

## 保存される成果物

`generated/fixtures/`に14ケースの入力証拠・ポリシー・信頼鍵が入り、評価時刻は明示的に固定されます。
各ケースの詳細は`generated/NN.experimental.report.json`と`NN.v1.2.report.json`です。
`generated/summary.json`に期待判定との差分、実装と試験データのコミット、ファイル内容のダイジェスト、
Pythonと依存関係の版を記録します。

公開した実行記録は[results/summary.json](results/summary.json)と同じフォルダーの圧縮アーカイブです。
結果保存のコミットと実際に実行したコードのコミットは異なる場合があります。レポートの記録を参照してください。

実行記録は内部の合成データ試験です。第三者による再現確認、本番の外部アンカー、組織的な独立性、
VAP全要件への適合は未確認です。正式番号・採択・適用バージョンは未決定のままです。
