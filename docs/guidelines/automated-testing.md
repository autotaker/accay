# 自動テストガイドライン

## 1. 目的

Accay 自体の自動テストは、ユーザーリポジトリに対する CLI の公開挙動を安定させるために置く。

内部実装の形を固定しすぎず、受け入れ駆動ツールとして壊してはいけない振る舞いを Contract Test で守る。

## 2. テスト分類

| 分類 | 目的 | CI |
|---|---|---|
| Contract Test | CLI の公開挙動を fixture project で固定する | 必須 |
| Unit Test | parser / resolver / matcher / formatter など局所処理を検証する | 必須 |
| Probe Test | 調査、再現、edge case 観察に使う | 通常除外 |

受け入れ条件に対応するテストは Contract Test として扱う。

## 3. ディレクトリ

```text
tests/
  contract/
  unit/
  probe/
  fixtures/
  golden/
```

| directory | 役割 |
|---|---|
| `contract` | CLI と fixture project で公開挙動を検証 |
| `unit` | 局所処理を検証 |
| `probe` | 調査用 |
| `fixtures` | 疑似 repository、JUnit XML、schema |
| `golden` | context / report の期待構造 |

## 4. Contract Test

Contract Test は CLI を実行して確認する。

対象例:

- `accay init` が標準ディレクトリを作る。
- `accay init` が既存ファイルを上書きしない。
- `accay install` が skill を配置する。
- `accay validate` が diagnostics と exit code を返す。
- `accay regression` が accepted case の missing を fail にする。
- context / report が主要構造を持つ。

Contract Test は実装内部の class 名や関数名に依存しない。

## 5. Unit Test

Unit Test は、Contract Test だけでは失敗原因が追いづらい局所処理を支える。

対象例:

- YAML parser。
- OpenAPI operation extraction。
- JSON Schema validation wrapper。
- JUnit XML reader。
- testcase matcher。
- diagnostics formatter。

## 6. Fixture

fixture project は小さく保つ。

含めるもの:

- valid component。
- invalid component。
- valid trace。
- invalid trace。
- JUnit XML。
- schema。

fixture は「何を検証するためのものか」が名前からわかるようにする。

## 7. Golden file

golden file は report / context の主要構造を固定するために使う。

ルール:

- run id、timestamp、絶対パスは正規化する。
- 完全一致がつらい場合は重要 section の比較に留める。
- 文言の微修正だけで壊れすぎる golden は避ける。

## 8. Diagnostics / exit code

Contract Test では、少なくとも以下を確認する。

- error があると non-zero。
- warning / info のみなら zero。
- diagnostics に source path が含まれる。
- component / scenario / case ID が含まれる。

## 9. Probe Test

Probe Test は、実装中の仮説検証や外部形式の edge case 観察に使う。

- 通常 CI には入れない。
- 長期保守する価値が出たら Contract Test または Unit Test に昇格する。
- 調査目的が終わったら削除してよい。

## 10. 追加時チェック

- 公開挙動なら Contract Test か。
- 局所処理なら Unit Test か。
- 調査用なら Probe Test か。
- fixture は最小か。
- golden は揺れに強いか。
- system / component 境界をまたいだ前提を置いていないか。

## 11. Regression testing

Component Regression のテストでは、次を必ず分ける。

- JUnit XML parser の Unit Test。
- test-map matching の Unit Test。
- accepted case policy の Unit Test。
- CLI から regression を実行する Contract Test。

Contract Test では、少なくとも missing、failed、skipped、unmapped を 1 つずつ確認する。

## 12. Report / context testing

report / context は全文を固定しすぎない。

確認するもの:

- 必須 section がある。
- component / scenario / case ID が出る。
- diagnostics severity が出る。
- report path が返る。
- 不安定値が正規化される。

## 13. CI expectations

CI では通常以下を実行する。

- Unit Test。
- Contract Test。
- lint / format check。

Probe Test は明示的に指定されたときだけ実行する。
