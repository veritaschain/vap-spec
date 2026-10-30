# 53ケースのオフライン再検証手順

このキットは、入力制御17件・公開前レビュー18件・限定された削除証跡18件の
**保存済み合成データ**を、対応するソースと一緒に再検証する実験用ツールです。
元のアップロード・公開・削除操作は実行しません。実際の患者情報や外部サービスの
認証情報は含みません。公開前レビューのケースには、検証に必要な合成記事本文・
HTMLが含まれています。

## 1. 信頼するソースと期待ハッシュを決める

まずレビュー済みのGitコミットを取得してください。候補ZIPを検証するときは、
そのZIPの外にある確認済みの[実行結果](https://github.com/veritaschain/vap-spec/tree/main/experiments/incident-recheck-kit/results)から期待SHA-256を
取得します。候補ZIPに同梱されたハッシュだけでは、そのZIP自身を信用する根拠に
なりません。`source-lock.json`のコミットは既存3パイロットの共通ソースを示し、
今回のキット実装のコミットは実行結果に別途記録します。

## 2. 実行環境を明示的に準備する

Linux上のPython 3.12または3.14を使用します。依存関係の導入は再検証の前に
別の操作として行います。導入時にはネットワークが必要になる場合があります。

```sh
cd experiments/incident-recheck-kit
python3 -m venv .venv
.venv/bin/python -m pip install --only-binary=:all: -r requirements.txt
```

検証プロセスは、固定した4パッケージの配布メタデータと読み込んだモジュールの
版を確認します。不足・不一致なら失敗し、自動で追加インストールしません。
Python本体や依存ライブラリのバイナリまで固定する構成ではありません。

## 3. 保存済み証拠からZIPを作る

```sh
mkdir generated
.venv/bin/python -m incident_recheck build --output generated/incident-ci-2026-10-30.zip
```

新しい出力先だけを受け付けます。既存ファイルは上書きしません。同じ入力からは
同じZIPバイト列になります。作成後に53件すべてを再検証し、全件が成功した場合に
限って成功レポートを出します。再検証が失敗した場合、調査用のZIPが残ることが
ありますが、それを検証成功として扱うことはできません。

## 4. 取得したZIPを検査・再検証する

`EXPECTED_HEX`を、ZIP外から取得した64桁の期待SHA-256に置き換えます。

```sh
.venv/bin/python -m incident_recheck inspect --archive /path/to/candidate.zip --expected-sha256 EXPECTED_HEX
.venv/bin/python -m incident_recheck verify --archive /path/to/candidate.zip --expected-sha256 EXPECTED_HEX
```

`inspect`はZIP全体・構造・ファイル一覧・各バイト列の整合性を確認します。
ケースの署名や判断までは再検証しません。`verify`は追加で、同梱された全ソースを
信頼するチェックアウトのソースと照合し、元のCI証拠のバイト列と来歴を確認して
から、固定された3つの検証関数を別プロセスで呼び出します。

確認済みペイロードの構成は`source/`と`evidence/`です。元の作業ディレクトリが
なくても、`source/experiments/incident-recheck-kit/`のランチャーは隣接する
`evidence/`を見つけ、再検証と同一ZIPの再作成ができます。独立に取得した期待
ハッシュによる照合と、信頼するコードによるZIP検査を済ませてから、新しい空の
ディレクトリに配置してください。未確認ZIP内のランチャーを先に実行することは
信用の起点にはなりません。自動ダウンロードや任意パスへの展開機能はありません。

## 成功が意味する範囲

| レポート項目 | 成功時の意味 |
|---|---|
| `verified_exports: 53` | 保存された53ケースの署名・結び付け・判断・一覧を元の検証関数で再検証できた |
| `source_binding: MATCHED_TRUSTED_CHECKOUT` | 同梱コードが、実行者の信頼するチェックアウトと一致した |
| `actions_reexecuted: false` | 元のアップロード・公開・削除操作を再実行していない |
| `independent_reproduction: NOT_ESTABLISHED` | 元の操作の独立した再現や、観測内容の真実性は確立していない |
| `conformance: NOT_ASSESSED` | VAP適合性・法令遵守を判定していない |
| `dependency_scope: PINNED_VERSIONS_NOT_HERMETIC` | 依存版は固定しているが、実行環境全体を封じ込めたものではない |

親プロセスは検証済みファイルの一時配置と後片付けを行います。子プロセスでは
監査フックで通信・プロセス生成・ファイル変更を拒否しますが、これはOSによる
サンドボックスではありません。ホスト、Python、導入済み依存関係への信頼は
残ります。元の証拠にある不明な結果や迂回経路の観測を、成功へ書き換えません。
外部事業者の完全削除や、文章の全AI関与、学術誌の開示義務充足を証明する機能
ではありません。

元のCIアーティファクトには期限がありますが、このキットの公開JSONはGitに
保存されています。期限後も同じ記録を再検証できます。別の実行で新しい鍵や時刻を
作ることは、保存済み記録の再検証とは異なります。規範仕様はv1.2 Draft 3のままで、
既存の固定研究配布物やパイロット実行コードは変更しません。
