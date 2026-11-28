# Secret-value screening experiment (experimental, unadopted)

This is a research experiment on synthetic input. It is not a VAP v1.2 requirement, a conformance
verifier, a production secret scanner or an independent reproduction. It changes no normative text,
no other experiment and no fixed evidence.

**Prepared:** 28 November 2026 (JST), with AI assistance (Claude, Anthropic). First-party work, not
independently reviewed. [日本語要約](#日本語要約)

## What it exercises

The [candidate text for register row F13](../../proposals/core-text-candidates/README.md) proposes that
reusable authentication secrets must not appear in plaintext in a member that enters an EventHash or a
Merkle leaf, and that a record refer to a credential by a non-secret identifier assigned by its issuer.
That text is unadopted. This experiment asks a narrower question: given a record, what can a third party
show about that rule, and what can it not show?

`secret_screen.py` walks the string values of a synthetic event and reports, per JSON Pointer, values
of six known shapes (a PEM private-key header, a three-part token beginning `eyJ`, a bearer token, a URL
with embedded user information, a cookie header, a named assignment such as a password in free text) and
non-empty values of members whose name says they hold a secret.

| Result | Meaning |
| --- | --- |
| `SECRET_PATTERN_FOUND` | A value of a known shape is present at the reported pointer. This is a demonstrated finding |
| `NO_PATTERN_MATCHED` | None of the patterns matched in the screened members. **This is not evidence that the record holds no secret** |
| `INPUT_REJECTED` | The input has a byte order mark, duplicate member names, malformed JSON or a non-object top level. It is not repaired |

Members that the caller declares withheld or encrypted before commitment are listed under
`not_assessed`, and `complete_coverage` is then false. Nothing is concluded about their content.

The report gives the pointer, the pattern class and the length of the string. It never contains the
matched text, so that the report does not itself become a record that carries the secret.

## What the cases show

Fourteen synthetic cases in `cases.json`:

- eight in which a secret-shaped value sits in the recorded input, a tool result, the context, a
  profile-defined payload or free text, and is reported (`S02` to `S08`, `S13`);
- three in which nothing is reported and nothing should be: a clean record, digests and a signature, and
  an issuer-assigned identifier of the kind the candidate rule asks for (`S01`, `S09`, `S10`);
- one declared member that is not assessed (`S12`);
- one rejected input (`S14`);
- **one known limit (`S11`).** The record refers to a credential by a hash of a low-entropy secret. The
  candidate rule does not accept that as a non-secret identifier, because the secret can be recovered by
  guessing. Screening cannot tell that hash from any other digest and returns `NO_PATTERN_MATCHED`.

The consequence for the candidate text: a third party can demonstrate a violation of the rule and
cannot demonstrate compliance with it. A producer obligation of this kind is checkable only in the
negative, and review text for F13 should say so.

## Limits

- Pattern screening finds known shapes. It misses secrets with no recognisable shape, secrets split
  across members, encoded or compressed secrets, and member names in other languages or conventions.
- It reports false positives: a member named `secret` may hold something harmless.
- The screened scope is every member except the top-level `security` block. That is a local assumption;
  which members enter a hash or a Merkle leaf is profile-defined.
- Member names are not screened as values.
- All material is synthetic. Case files hold placeholders, and the secret-shaped strings are assembled
  at run time from fragments, so that no secret-shaped literal is stored in the repository. A test
  checks this. Do not add real credentials to the cases.

## Reproduce

Python 3.12 or later, standard library only.

```sh
cd experiments/secret-value-screening
python -W error -m unittest discover -s tests -v
python secret_screen.py run-suite
python secret_screen.py screen path/to/event.json --not-assessed /provenance/context/protected
```

`run-suite` exits 0 when all fourteen cases match their expected results. `screen` exits 0 only for
`NO_PATTERN_MATCHED`.

A successful run establishes that this implementation returns the expected results on these synthetic
cases. It does not adopt the candidate text, test a real system or show that any record is free of secrets.

## 日本語要約

**実験・未採択。** VAP v1.2 の要件でも、適合の検証器でも、実運用向けの秘密情報スキャナでもありません。
入力はすべて合成データです。

登録簿の F13 の文案（再利用できる認証用の秘密値を、EventHash や Merkle の葉に入るメンバーに平文で入れない）
について、第三者が記録から何を示せて何を示せないかを確かめます。`secret_screen.py` は合成イベントの文字列値を
たどり、既知の形（PEM の秘密鍵ヘッダ、`eyJ` で始まる 3 部構成のトークン、ベアラトークン、ユーザー情報を含む
URL、Cookie ヘッダ、文中の代入）と、名前が秘密を示すメンバーの値を、JSON Pointer ごとに報告します。

- `SECRET_PATTERN_FOUND`：既知の形の値がある（示された所見）。
- `NO_PATTERN_MATCHED`：どのパターンにも当たらなかった。**秘密値がないことの証拠ではありません。**
- `INPUT_REJECTED`：BOM、重複メンバー、不正な JSON などで、直さずに拒否。

暗号化済み・非開示と宣言されたメンバーは `not_assessed` に挙げ、内容については何も結論しません。報告には
一致した文字列そのものを載せません。

14 件の合成ケースのうち 1 件（`S11`）は既知の限界です。低エントロピーの秘密値のハッシュを参照に使った記録は、
文案上は認められませんが、スクリーニングでは他のダイジェストと区別できません。つまり、この規則は違反を示すこと
はできても、遵守を示すことはできません。F13 のレビュー用の文言はその点を書く必要があります。

ケースのファイルには置き換え用の印だけを置き、秘密値の形をした文字列は実行時に断片から組み立てます。
実在の資格情報をケースに足さないでください。
