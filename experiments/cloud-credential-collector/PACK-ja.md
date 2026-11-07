# 持ち運べる保管スナップショット

**位置付け：未採択の参考実験。範囲を限定したローカル実装。**
[English](PACK.md) · [収集器](README-ja.md) · [証拠検証器](../cloud-credential-evidence/README-ja.md)

収集器が出力するnativeエンベロープには、保管履歴の全体は含まれません。この拡張は、原本と、
その受領履歴を再検査するための署名付き情報を、実行機能を持たない1つのJSONファイルへまとめます。
ここでいうスナップショットは、その時点のコミット済み原本と受領履歴を保存したものです。
受取側は、作成側のSQLiteデータベース、元の入力パス、収集プロセス、署名用秘密鍵なしで検証できます。

受取側には、信頼する検証コードと版を固定した依存ライブラリ、ファイルの外で選んだ公開鍵、
別途指定する期待保存先IDが必要です。同梱のチェックポイントは収集者の記述であり、
独立した観測者や最新履歴の証明にはなりません。

[VAP第9.3節](../../spec/v1.2/VAP_Framework_Specification.md#93-evidence-pack-v12-recommended)の
オフライン検証という目的に関係する実験です。VAPのEvidence Packの規範的な形式を定義したものではなく、
外部アンカーの証明、適用する方針文書、プロファイルへの適合性、法的な受理、独立再現を成立させません。

導入時の認可と証跡の共有については、[認可と機密性の境界](SECURITY-BOUNDARIES-ja.md)を参照してください。これらのツールは原本を保持し、秘密情報のスキャンや提供の認可は行いません。

## 実行方法

収集器と同じPython 3.12環境で、リポジトリのルートから実行します。

```sh
python -m pip install -r experiments/cloud-credential-collector/requirements.txt
python -W error::ResourceWarning -m unittest discover -s experiments/cloud-credential-collector/tests -v
python -O -W error::ResourceWarning -m unittest discover -s experiments/cloud-credential-collector/tests -v
python -W error::ResourceWarning experiments/cloud-credential-collector/run_pack_demo.py
python experiments/cloud-credential-collector/custody_pack.py --help
```

[テスト](tests/test_custody_pack.py)と[デモ](run_pack_demo.py)は、公開の合成署名鍵と一時的な非公開ファイルを
使います。受取側の検証を別プロセスで実行しますが、同じローカル運用者による実行であり、
社外の組織による独立再現とは扱いません。

### 出力

```sh
python experiments/cloud-credential-collector/custody_pack.py export \
  --store /private/collector-store \
  --public-key-file /private/trusted-collector-public.bin \
  --private-key-file /private/collector-seed.bin \
  --expected-store-id EXPECTED_STORE_ID \
  --out /private/custody-snapshot.json
```

上の名前は置き換えて使う例です。鍵ファイルは既存収集器と同じ、ちょうど32バイトの生データです。
期待保存先IDは、呼出側の保存先登録や保持した証拠など、既に確立した経路から取得します。
受け取ったファイルの中のIDを自動的に正解として採用しません。出力は管理対象の保存先の外へ、
非公開ファイルとして作り、既存のパスを置き換えません。

保存先の監査、コミット済み履歴の読取り、スナップショットのチェックポイントへの署名、
出力の確定まで、1つのプロセス間ロックを保持します。その時点でコミットされている受領書をすべて含めるか、
上限を超えるなら出力を拒否します。都合のよい部分だけを黙って選びません。
索引のない原本、作業途中のファイル、変更されるSQLite索引は、受理済みの収集受領書ではなく、
このスナップショットには含めません。

### 受取側で検証

```sh
python experiments/cloud-credential-collector/custody_pack.py verify \
  --pack /private/custody-snapshot.json \
  --public-key-file /private/trusted-collector-public.bin \
  --expected-store-id EXPECTED_STORE_ID
```

どちらのコマンドにも、任意で`--external-checkpoint /private/retained-checkpoint.json`を渡せます。
これはファイル本体とは別の呼出側入力です。保持した観測としての意味は、呼出側がどのように取得し、
保護したかに依存します。提出ファイルの中からチェックポイントをコピーしただけでは、
別の保管経路や最新性が成立するわけではありません。

検証には、信頼する`custody_pack.py`と、純粋な処理を提供する
`../cloud-credential-evidence/cloud_evidence.py`をリポジトリと同じ相対配置で用意し、
版を固定した`cryptography`を入れる必要があります。`custody_pack.py`だけのコピーでは動きません。
収集器やSQLiteをインポートせず、
作成側のデータベースや秘密鍵も読みません。サーバーへ接続せず、アーカイブを展開せず、
提出ファイルに入った内容を実行しません。実装とテストは収集器READMEに記したLinux・Python環境を対象とし、
別プロセスで動いたことだけで、他のOSや別組織での保証が成立するとは扱いません。

Python APIは次のとおりです。

```python
verify_pack(package, *, trusted_public_key, expected_store_id, external_checkpoint=None)
export_pack(store_path, output_path, *, trusted_public_key, private_key,
            expected_store_id, external_checkpoint=None, clock_ns=None, hook=None)
```

時計の注入とフックはPython APIのテスト用機能です。CLIに過去日時の指定や障害注入の引数はありません。
結果はメタデータと範囲を限定した判定を含み、原本や秘密鍵を出力しません。
明示的に作るスナップショットファイルには原本が含まれるため、非公開として扱う必要があります。

CLIの終了コード**0**は出力または保管検証の完了、**2**は入力の拒否またはエラーを示します。
検証に成功しても、`completeness: unresolved`、`latestness: unresolved`、
`independent_custody: false`を返します。別途与えたチェックポイントがなければ
`rollback_assessment`は`not_assessed`、比較が一致した場合は
`consistent_with_retained_checkpoint_only`です。終了コードは、安全性、権限、出典、適合性の判定ではありません。

## 結び付けと検証

最上位オブジェクトのフィールドは`schema`、`manifest`、`checkpoint`、`receipts`、`artifacts`だけです。
実験用の形式であり、収集器の既存の署名ドメインを使用します。VAPの規範的コンテナや、
RFC 8785のJSON実装ではありません。
ファイル全体に別の署名を追加する形式ではありません。既存の署名付き要素、正確なコミットメント、
含まれる記録の集合を検証し、提出物の要約をそのまま信頼しません。

| 要素 | 検査すること |
| --- | --- |
| 呼出側の入力 | 提出物とは別に公開鍵と必須の期待保存先IDを確認する。同じ鍵で署名された別の保存先でもIDが違えば拒否する。 |
| 保存先情報 | 署名、形式、保存先ID、収集者ID、作成時刻の表現を検証する。 |
| 受領履歴 | 署名、保存先・鍵・文脈の対応、1から始まる連続した連番、前の受領書のコミットメント、要求IDの重複、受領時刻の逆行を検査する。 |
| 原本 | 正規のbase64チャンクから戻し、バイト数とSHA-256を再計算する。受領書が参照する一意の原本集合と正確に一致させ、欠落・重複・余分な原本を拒否する。 |
| 同梱チェックポイント | 署名を確認し、保存先・連番・受領書のコミットメントが出力履歴の末尾と一致することを検査する。発行時刻が対象の受領より前なら拒否する。 |
| 外部保持チェックポイント | 呼出側が別途指定したものを、同じID・時刻の規則で対応する履歴と照合する。その後に正当に追加された履歴は認める。 |

UTF-8でないデータを含む任意の原本にも、保管のコミットメントを保持できます。
含まれていることだけで、有効なAzureログとは確認できません。この検証器は保管構造を評価します。
認証、権限、リソース利用、操作前の証拠の利用可能性は、既存の証拠検証器と、
呼出側が別途与える信頼設定・対象範囲で評価する問いです。

## 同梱チェックポイントと外部で保持した観測

| 入力の状態 | 言える範囲 |
| --- | --- |
| 有効なファイルと、その中のチェックポイントだけ | 呼出側が指定した鍵・IDの下で、提示された履歴は整合する。巻き戻しは未評価。 |
| 別途保持したチェックポイントが一致 | そのチェックポイントとの整合性に限って確認できる。 |
| 現在のファイルが、古い一致したチェックポイントの先まで伸びている | 追加を認める。古いチェックポイントは最新の末尾を保証しない。 |
| 後の時点の外部保持チェックポイントが要求する履歴を欠く | ファイルとチェックポイントの比較を拒否する。 |
| 同じ鍵で署名した別の保存先に差し替えられた | 呼出側の期待保存先IDとの不一致として拒否する。 |

整合した古いファイルと古い同梱チェックポイントは、有効なまま残り得ます。
古い外部保持チェックポイントが一致しても、その後に追加されてから消された末尾は分かりません。
その矛盾を検出するには、より後のチェックポイントを別に保持している必要があります。
信頼できる実時刻、最新性を返すオンラインサービス、独立したアンカー、普遍的な完全性は確立しません。

## 形式・上限・非公開性

ファイル全体は**1 MiB**、受領書は**256件**、一意の原本も**256件**までです。
原本1件は収集器と同じ最大**65,536バイト**です。原本の項目は`artifact_sha256`、
`artifact_size`、`base64_chunks`だけを持ちます。元バイト列を標準のbase64で保持し、
復号後の大きさが**32 KiB**のチャンクに分けます。最後のチャンクはそれ以下です。
空の原本は空のチャンク配列で表します。
これにより、既存のJSON処理の文字列長上限を維持します。パディングを含む正規の表現を検査し、
異なる文字表現を無条件で同じものとして受け入れません。

結果の`package_sha256`は正規化したJSON値を識別します。出力時はその正規化バイト列をそのまま書くため、
出力したファイルのハッシュとも一致します。受け取ったJSONの配置を変えると、値を維持したまま
ファイル自体のバイト列のハッシュは変わり得ます。この結果フィールドは、任意の受信時の書式のハッシュではありません。
各原本のコミットメントは、復元した元バイト列を対象とし、元のJSONを再シリアライズしたものや
base64の表示文字列を対象にしません。基礎となる符号化は
[RFC 4648](https://www.rfc-editor.org/rfc/rfc4648.html#section-3.5)と
[Pythonのbase64文書](https://docs.python.org/3.12/library/base64.html#base64.b64decode)を参照してください。
厳格なフィールド・型・サイズの検査と、正確な原本集合の一致は本実験で定めた規則です。
既存のJSON処理も、重複キー、未対応の数値表現、NFCでないメタデータ文字列を拒否します。

収集器が受け入れた保存先でも、より小さい出力上限を超える場合があります。その場合、出力先を上書きせず失敗し、
一部だけのスナップショットを全体だと主張しません。範囲を限定したパイロットであり、
ストリーミングのアーカイブ形式や、データベース全体のバックアップではありません。

base64は暗号化ではありません。ファイルには原本と署名付き情報が含まれ、ローカルの非公開権限では、
受取側が後から作るコピーまで制御できません。配布、アクセス、保存、秘匿化、削除には別の判断が必要です。
本番データを含むスナップショットや実際の秘密鍵を、公開リポジトリやCI成果物へ置かないでください。
