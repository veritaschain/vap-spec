# 第三者向け再現手順

**未採択の研究実装です。第三者による独立再現は未成立です。** このパッケージの公開・CI成功は、独立した第三者による再現成立、正式採択、VAP適合、本番運用の証明ではありません。現行v1.2、DOC-SYNC、K3、既存検証器、既存ゲート、OS隔離実験は変更しません。凍結した既存実装を呼び出して試験と証拠の再検証を行います。

## 準備する環境

使い捨てのLinuxホストまたはLinux VMを用意し、Git、Python 3.12以上、venv、pip、Linux Docker Engine、Compose v2を事前に導入してください。Dockerを操作できる利用者で実行します。ホスト・操作者・Dockerデーモン・制御プログラムは信頼境界の内側です。macOS/Windows上の制御プログラム、rootless Docker、デーモンのuserns-remapは今回の対象外です。

過去の内部試験環境はUbuntu 24.04 x86_64／Python 3.12.15／Docker 28.0.4／Compose 2.38.2／Linux 6.17.0-1022-azureです。完全なVMイメージを配布するものではなく、実際のバージョンと差異を記録します。Python依存関係は4件すべて固定し、コンテナーのベースも既存Dockerfileでダイジェスト固定しています。初回はGitHub・Pythonパッケージ配布元・コンテナーレジストリへ接続します。完全オフライン／完全に密閉されたビルドではありません。

試験は実在サービスを操作せず、模擬APIと試験用鍵のみを使用します。迂回できる負例も意図的に実行します。準備用コンテナーは権限設定のためrootで動き、試験対象の5役割は別々の非root UIDで動作します。本番環境と共用しないでください。

## 1. パッケージと対象実装の取得

このPRのCI成果物からZIPを取得するか、レビューするパッケージのコミットを取得して次を実行します。

```sh
python3 reproduction/os-isolation/reproduce.py pack --output /absolute/path/kit.zip
```

ZIPを新しい場所に展開し、`vap-os-isolation-kit/`に移動します。ZIPのSHA-256、取得元、パッケージのコミットを別途記録してください。

```sh
sha256sum -c SHA256SUMS
KIT_DIR="$PWD"
```

同梱チェックサムは内容の整合性確認用です。作成者の真正性を証明しません。コミット・ZIPハッシュの取得元は評価者自身が確認してください。

以下の`/absolute/path/reproduction-work`を、新規作業ディレクトリの絶対パスに置き換えます。

```sh
WORK_DIR=/absolute/path/reproduction-work
mkdir "$WORK_DIR"
git clone --no-checkout https://github.com/veritaschain/vap-spec.git "$WORK_DIR/source"
git -C "$WORK_DIR/source" checkout --detach c8ccf972196a16d11429a478f4918a08fe27bb73
python3 "$KIT_DIR/reproduce.py" verify-source --source "$WORK_DIR/source"
python3.12 -m venv "$WORK_DIR/venv"
"$WORK_DIR/venv/bin/python" -m pip install -r "$WORK_DIR/source/experiments/os-isolated-gate/requirements.txt"
"$WORK_DIR/venv/bin/python" "$KIT_DIR/reproduce.py" preflight --source "$WORK_DIR/source"
```

対象はマージ済みPR #12のコミットに固定します。最新ブランチへの置き換えは禁止です。ソースの未保存変更・追加ファイル・実行に影響する無視ファイル・ハッシュ不一致があれば停止します。venvと出力は必ずソースの外に置いてください。

## 2. 実行と保存証拠の再検証

```sh
"$WORK_DIR/venv/bin/python" "$KIT_DIR/reproduce.py" run --source "$WORK_DIR/source" --output "$WORK_DIR/results-001"
"$WORK_DIR/venv/bin/python" "$KIT_DIR/reproduce.py" check --source "$WORK_DIR/source" --output "$WORK_DIR/results-001"
```

`results-001`は未作成のパスにします。再試行は`results-002`など別パスへ出力し、失敗した証拠を上書きしません。

期待値は回帰試験 **28＋46＋64件**、OS実験 **16ケース**、既存ゲート **15ケース・11証拠束**、既存検証器 **14ケース・両モード**です。16ケースの一覧と比較規則は[EXPECTED-RESULTS.md](EXPECTED-RESULTS.md)にあります。ケース14は経路の隔離が破れた状態、15は迂回が成功する負例です。これらの期待一致を「常に迂回できない」と読み替えません。

`run`は実際にOS試験を実行します。`check`は保存データを再照合し、既存実装を用いて署名・ハッシュ・結び付けを再検証します。`check`だけではOS試験の再実行や操作者の申告の認証にはなりません。IP、名前空間ID、鍵、署名、時間値のバイト一致は求めず、役割間の関係・判定・証拠内部の整合性を確認します。

試験件数だけでなく全件成功の結論を確認し、スキップや期待された失敗があれば未完了とします。各レポートのPython・依存ライブラリの記録も、事前確認と固定条件に照合します。

すべて一致した場合にのみ`run-report.json`が`matched`になります。終了コードは0＝要求処理完了、1＝開始後の試験未完了／不一致、2＝入力・事前確認・保存結果照合などのエラーです。全体適合判定は常にnull、採択状態は未採択、独立性は未評価のままです。

## 3. 第三者による報告

出力ディレクトリ全体、ZIPのSHA-256、取得元を保存し、[評価者報告テンプレート](templates/evaluator-report.json)を別の場所へコピーして記入します。氏名・所属・開発者との関係・独立した実行の有無・実環境・差異・失敗・限界を記録してください。報告の記入や送付は自動では行いません。

[REPORTING.md](REPORTING.md)に成果物一覧と失敗時の対応があります。途中停止・Dockerの問題・後片付けの未確認は成功扱いしません。負例の危険性や外部環境の保証を広げず、実際に観測した範囲を報告します。
