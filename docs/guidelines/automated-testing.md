# 自動テストガイドライン
## 1. 目的
この文書は、Accay 自身の自動テストを設計・追加・保守するための実務ガイドラインである。
Accay は、ユーザーリポジトリに導入される受け入れ駆動開発支援ツールである。
そのため、自動テストは内部実装の形を固定するためではなく、CLI の公開挙動を安定させるために置く。
テストで守る中心は、次の問いである。
- Accay は入力成果物を正しく集められるか。
- Accay は system と component の責務境界を混ぜずに検証できるか。
- Accay は diagnostics、context、report を安定した構造で出せるか。
- Accay は accepted case の回帰を JUnit XML と `test-map.yaml` から検出できるか。
- Accay は失敗時に、人間とエージェントが次に読むべき情報を返せるか。
Accay のハーネスは最終的な意味判断を行わない。
自動テストもこの方針を変えない。
テストが確認するのは、形式検証、schema validation、JUnit 照合、diagnostics、report / context 生成など、ハーネスが責務として持つ機械的な振る舞いである。
意味・責務境界・最終受け入れ判断は、人間とエージェントに残す。
## 2. 基本方針
自動テストは、次の優先順位で設計する。
1. Contract Test で CLI の公開挙動を固定する。
2. Unit Test で複雑な局所処理を支える。
3. Regression Test で受け入れ済みケースの保証を守る。
4. Golden Test で report / context の主要構造を守る。
5. Probe Test で不明点を観測する。
Contract Test は最重要である。
Accay の利用者は内部関数ではなく CLI を実行するため、壊してはいけない挙動は fixture project に対する CLI 実行で確認する。
Unit Test は Contract Test の代替ではない。
Unit Test は、parser、resolver、matcher、formatter など、失敗原因を局所化したい処理に使う。
Probe Test は長期保守テストではない。
Probe Test は、外部形式の edge case や実装中の仮説を観測するために置き、価値が固まったら Contract Test または Unit Test に昇格する。
Golden file は report / context の主要構造に絞り、timestamp、run id、絶対パスなどの揺れる値は正規化する。
## 3. テスト分類
| 分類 | 目的 | CI | 主な対象 |
|---|---|---|---|
| Contract Test | CLI の公開挙動を fixture project で固定する | 必須 | `init`、`validate`、`pack`、`regression`、diagnostics、exit code |
| Unit Test | 局所処理の分岐と edge case を検証する | 必須 | parser、resolver、matcher、formatter、normalizer |
| Regression Test | 受け入れ済み case と JUnit 結果の照合を確認する | 必須 | `test-map.yaml`、JUnit XML、case 単位集計 |
| Golden Test | 出力ファイルの主要構造を固定する | 必須または任意 | Markdown report、HTML report、context.md |
| Probe Test | 調査、再現、外部形式の観測に使う | 通常除外 | OpenAPI、JUnit XML、JSON Schema、subprocess |
分類は排他的でなくてよい。
たとえば `accay regression --junit ...` を fixture project で実行し、exit code と report golden を比較するテストは、Contract Test、Regression Test、Golden Test の性質を持つ。
その場合、配置は `tests/contract/` を優先する。
## 4. 推奨ディレクトリ
```text
tests/
  contract/
  unit/
  probe/
  fixtures/
  golden/
  helpers/
```
| ディレクトリ | 役割 |
|---|---|
| `tests/contract/` | CLI と fixture project を使い、公開挙動を検証する |
| `tests/unit/` | pure function または小さな module 単位の処理を検証する |
| `tests/probe/` | 調査用テストを置く。通常 CI から外す |
| `tests/fixtures/` | 疑似リポジトリ、JUnit XML、schema、OpenAPI、operations.yaml を置く |
| `tests/golden/` | 正規化済みの期待出力を置く |
| `tests/helpers/` | fixture copy、CLI 実行、正規化、golden 比較の helper を置く |
`tests/helpers/` はテストを読みやすくする補助に限定する。
プロダクトコードの代わりになる validation logic を helper に置いてはいけない。
## 5. Contract Test
Contract Test は、Accay をユーザーが使う形に近い状態で実行する。
基本形は、小さな fixture project を一時ディレクトリにコピーし、CLI を subprocess で実行し、stdout、stderr、exit code、生成ファイルを確認することである。
Contract Test で確認するものは次の通りである。
- コマンドが受け付ける引数。
- 成功時と失敗時の exit code。
- diagnostics の severity、code、対象 path、summary。
- 生成されるファイルの有無。
- 既存ファイルを不用意に上書きしないこと。
- system validation と component validation の対象範囲。
- component regression が system trace を正本として読まないこと。
- report / context の主要 section。
Contract Test では、内部関数名、内部 dataclass、module 分割を直接検証しない。
内部構造を変えても公開挙動が同じならテストは通るべきである。
### 5.1 対象コマンド
少なくとも以下のコマンドは Contract Test を持つ。
```bash
accay init
accay install
accay validate
accay system validate
accay component validate <component>
accay system pack desk-debug --scenario <scenario>
accay component pack review <component> --case <case-id>
accay regression --junit <path>
accay component regression <component> --junit <path>
```
`accay serve` は生成済み report の薄い viewer である。
MVP では Contract Test の中心にしないが、起動引数、存在しない report dir の扱い、port 衝突時の diagnostics など、CLI として壊したくない挙動が固まったら追加する。
### 5.2 Contract Test の粒度
1 つの Contract Test は、1 つのユーザーシナリオを表す。
細かすぎる単位で CLI を実行すると、テストの意図が読みにくくなる。
一方で、1 つのテストに複数の失敗理由を詰め込みすぎると、失敗時の調査が遅くなる。
推奨する粒度は次の通りである。
- `init` が標準ディレクトリを作る。
- `init` が既存ファイルを上書きしない。
- `validate` が valid project を pass にする。
- `validate` が schema mismatch を error にする。
- `component validate` が指定 component だけを見る。
- `regression` が accepted case の missing を fail にする。
- `regression` が duplicate testcase を validation error にする。
- `pack` が必要な context section を含む。
## 6. Unit Test
Unit Test は、Contract Test だけでは失敗原因が追いづらい処理を支える。
対象例は次の通りである。
- YAML parser。
- OpenAPI operation extraction。
- `operations.yaml` reader。
- JSON Schema validation wrapper。
- trace step resolver。
- operation directory builder。
- JUnit XML reader。
- testcase matcher。
- regression case aggregator。
- diagnostics formatter。
- report context section builder。
- flaky value normalizer。
Unit Test は小さく、入力と期待値が読みやすいことを優先する。
file system や subprocess を使わずに済むなら使わない。
ただし、実際の file path 解決や XML 読み取りのように I/O 境界そのものが重要な処理では、最小限の一時ファイルを使ってよい。
### 6.1 Unit Test で固定しすぎないもの
以下は Unit Test で強く固定しすぎない。
- 内部 dataclass の private field。
- helper 関数の呼び出し順序。
- diagnostics の最終表示レイアウト。
- Markdown の空行数。
- HTML の装飾 class 名。
これらは公開挙動ではなく実装都合で変わりやすい。
必要なら Contract Test または Golden Test で、利用者に意味のある構造だけを確認する。
## 7. Probe Test
Probe Test は、調査や再現のための一時テストである。
たとえば次の用途で使う。
- OpenAPI parser が特定の `$ref` 形をどう返すか確認する。
- JUnit XML の skipped / failure / error の混在を観測する。
- JSON Schema library の error path 表現を確認する。
- subprocess の stdout / stderr encoding を再現する。
- Windows path や symlink の挙動を観測する。
Probe Test は通常 CI に入れない。
pytest を使う場合は、`probe` marker を付け、既定の CI コマンドから除外する。
Probe Test のコメントには、何を観測するためのテストかを書く。
調査目的が終わったものは削除してよい。
長期的な価値があるものは、Contract Test または Unit Test に昇格する。
## 8. Fixture Project
fixture project は、ユーザーリポジトリを小さく再現したテスト入力である。
Contract Test は fixture project を直接変更せず、毎回一時ディレクトリにコピーして実行する。
fixture project は、1 つの目的に対して最小限に保つ。
大きな万能 fixture を作ると、どの成果物がどのテストに必要なのか分からなくなる。
### 8.1 推奨 fixture 種別
| fixture | 用途 |
|---|---|
| `minimal-valid-project` | `validate` が pass する最小構成 |
| `missing-operation-project` | trace が存在しない operation を参照する |
| `schema-mismatch-project` | `input.value` または `output.value` が schema に合わない |
| `component-only-project` | component validation / regression の境界確認 |
| `regression-pass-project` | accepted case がすべて pass する |
| `regression-missing-project` | accepted case の mapped testcase が JUnit XML にない |
| `duplicate-junit-project` | 同じ `classname + name` が重複する |
| `cli-operation-project` | `kind: cli` の exit code 検証を行う |
fixture 名は、失敗条件または保証したい挙動が分かる名前にする。
### 8.2 Fixture の内容
fixture project には、テストに必要な正本成果物だけを置く。
典型的な構成は次の通りである。
```text
fixture-project/
  .accay/
    config.yaml
  docs/
    acceptance/
      scenarios/
      sequences/
      traces/
      components/
        inventory/
          acceptance-scope.yaml
          test-map.yaml
          semantics.md
          interfaces/
            operations.yaml
            schemas/
  reports/
    junit.xml
```
`docs/acceptance/` は長期保守対象の正本を表す。
`.accay/` は設定・生成物・一時成果物の領域を表す。
テストで `.accay/runs/` や `.accay/reports/` を生成する場合は、fixture ではなく一時ディレクトリ側に生成させる。
## 9. Golden file
Golden file は、生成出力の主要構造を守るために使う。
対象は主に以下である。
- `context.md`。
- regression Markdown report。
- validation Markdown summary。
- HTML report から抽出した安定 section。
- diagnostics JSON を出す場合の正規化済み JSON。
Golden file は、出力の全文を何でも固定する仕組みではない。
利用者にとって意味のある section、見出し、diagnostic code、case 集計、参照 path などを固定する。
### 9.1 Golden 比較の原則
Golden 比較では、事前に正規化を行う。
正規化対象は次の通りである。
- run id。
- timestamp。
- duration。
- 絶対パス。
- 一時ディレクトリ名。
- OS 固有の path separator。
- Python や実行環境が付ける traceback の行番号。
- HTML の nonce や生成順に依存する id。
正規化後の値は、読みやすい placeholder にする。
例:
```text
<RUN_ID>
<TIMESTAMP>
<TMPDIR>
<REPO_ROOT>
<DURATION_MS>
```
placeholder はプロジェクト全体で統一する。
### 9.2 Golden 更新
Golden file の更新は、仕様変更または意図した出力変更があるときだけ行う。
テストを通すために理由なく golden を更新してはいけない。
Golden 更新時は、差分で次を確認する。
- diagnostic code が変わっていないか。
- severity が意図せず変わっていないか。
- accepted case の集計が落ちていないか。
- context に必要な正本成果物が含まれているか。
- system と component の情報が正本として混ざっていないか。
## 10. CLI testing
CLI testing は Contract Test の中心である。
CLI は orchestration layer であり、validation / regression の本体ロジックを持たない。
しかし利用者に見える入口は CLI なので、CLI の入出力は明確にテストする。
### 10.1 CLI 実行 helper
CLI 実行 helper は、次を返す薄い wrapper にする。
- command。
- cwd。
- exit code。
- stdout。
- stderr。
- 生成ファイルの path。
helper は assertion を持ちすぎない。
assertion は各テスト本体に置き、テストの意図が読めるようにする。
### 10.2 stdout / stderr
stdout には、ユーザーが通常読む summary を出す。
stderr には、実行不能エラーや予期しないエラーを出す。
テストでは、少なくとも次を確認する。
- 成功時に必要な summary が stdout にある。
- validation fail 時に diagnostics の概要が読める。
- debug 目的でない traceback が通常出力に漏れない。
- `--help` が exit code 0 で使える。
- 不正引数が CLI parse error として扱われる。
## 11. Diagnostics と exit code
diagnostics は、人間とエージェントが失敗理由を追うための主要な契約である。
Contract Test では、文言全文よりも構造を優先して確認する。
### 11.1 Diagnostics の確認項目
diagnostics では次を確認する。
- `severity` が期待通りである。
- `code` が安定している。
- 対象 path が含まれる。
- 対象 component / scenario / operation が分かる。
- summary が空でない。
- 複数エラーがある場合に、最初の 1 件だけで処理が不自然に止まらない。
文言の自然さは重要だが、テストでは全文一致にしすぎない。
文言を固定したい重要メッセージだけ、部分一致または golden で確認する。
### 11.2 Exit code の原則
exit code は CI の契約である。
推奨する基本ルールは次の通りである。
| 状態 | exit code | 意味 |
|---|---:|---|
| success | 0 | 検証または生成が成功した |
| validation failure | 1 | 入力成果物に error diagnostic がある |
| regression failure | 1 | accepted case の fail / error / missing / skipped がある |
| CLI usage error | 2 | 引数やコマンド指定が不正 |
| internal error | 3 | 想定外の例外または実装不備 |
実装で別の体系を採用する場合でも、Contract Test で体系を固定する。
warning だけの場合に exit code 0 とするか 1 とするかは、設定と要件に合わせる。
どちらにしても、CI での扱いをテストに書く。
## 12. Operation Contract のテスト
Operation Contract は system と component の接続点である。
テストでは、Operation Directory が次を機械的に扱えることを確認する。
- component と operation の組で一意に解決できる。
- OpenAPI の `operationId` を operation ID として読める。
- `operations.yaml` の `kind` を読める。
- input / output schema 参照を解決できる。
- HTTP status code を検証できる。
- CLI exit code を検証できる。
- 同一 component 内の operation ID 重複を error にできる。
Operation Directory は意味論の正本ではない。
そのため、テストでも `semantics.md` の内容を Operation Directory の判定材料にしない。
`semantics.md` は context の材料として含めることはあるが、operation の存在判定や schema 参照の正本にはしない。
## 13. Report と context のテスト
report / context は、エージェントと人間が判断するための入力である。
Output & Presentation は表示責務を持つが、validation / regression の本体ロジックを持たない。
テストでは、この責務境界を守る。
### 13.1 context.md
`context.md` のテストでは、次を確認する。
- system desk-debug context に scenario / sequence / trace が含まれる。
- system desk-debug context で component の acceptance-scope / test-map を正本扱いしない。
- component review context に scope / test-map / semantics / interfaces が含まれる。
- component review context の関連 trace / scenario / sequence は参考情報として扱われる。
- JUnit summary が渡された場合に component review context に含まれる。
- run id や生成時刻は正規化される。
### 13.2 report
report のテストでは、次を確認する。
- validation report に error / warning / info の件数が出る。
- regression report に component 別の case 集計が出る。
- accepted case の fail / missing / skipped が目立つ位置に出る。
- unmapped test は info として扱える。
- Markdown report と HTML report の情報量が大きく食い違わない。
- report 生成が validation / regression の判定を再計算しない。
HTML report は DOM 全文一致よりも、安定した見出し、data 属性、table の主要 cell などを抽出して比較する。
## 14. Regression Test
Regression Test は、受け入れ済みケースの保証が壊れていないかを確認する。
中心は `acceptance-scope.yaml`、`test-map.yaml`、JUnit XML の照合である。
### 14.1 必須ケース
少なくとも次のケースを持つ。
- accepted case に紐づく testcase が pass している。
- accepted case に紐づく testcase が failure になっている。
- accepted case に紐づく testcase が error になっている。
- accepted case に紐づく testcase が skipped になっている。
- accepted case に紐づく testcase が missing になっている。
- non-accepted case の failure が warning または report only になる。
- JUnit XML にあるが `test-map.yaml` にない testcase が unmapped になる。
- 同じ `classname + name` が複数 JUnit XML に出た場合に validate error になる。
- 複数 JUnit XML が 1 つの test result set としてマージされる。
### 14.2 照合キー
MVP では JUnit testcase の照合キーは `classname + name` である。
path、file、line、独自 test id は照合キーにしない。
テストでは、同じ `name` でも `classname` が違えば別 testcase として扱うことを確認する。
同じ `classname + name` が複数回出た場合は、最後勝ちや先勝ちにしない。
validate error として明示的に失敗させる。
## 15. Flaky value normalization
自動テストは、実行環境で揺れる値に弱くしてはいけない。
正規化は、golden 比較だけでなく diagnostics や CLI output の比較にも使う。
正規化対象は次の通りである。
- repository root の絶対パス。
- temporary directory。
- path separator。
- run id。
- timestamp。
- duration。
- random suffix。
- process id。
- port number。
- locale に依存する日時表現。
- XML parser が返す属性順。
- JSON / YAML dumper の key order。
正規化はテスト helper に集約する。
ただし、正規化しすぎて本当の regressions を隠してはいけない。
たとえば operation ID、diagnostic code、case ID、exit code、schema path は正規化しない。
これらは公開契約として比較する。
## 16. CI 期待値
CI では、少なくとも Contract Test と Unit Test を実行する。
Probe Test は既定では実行しない。
Golden Test と Regression Test は、該当する Contract Test または Unit Test の一部として実行してよい。
推奨する CI の考え方は次の通りである。
- pull request では高速な全必須テストを実行する。
- Probe Test は手動 job またはローカル実行にする。
- golden 差分が出たら、差分をレビュー対象にする。
- accepted case の regression failure は CI fail にする。
- duplicate JUnit testcase は CI fail にする。
- warning だけの扱いは `.accay/config.yaml` の方針に合わせる。
CI は、テスト結果だけでなく生成 report の path または artifact も見つけやすくする。
失敗時に stdout / stderr と report を読めば原因に到達できる状態を目指す。
## 17. テストデータ設計
テストデータは、読み手が期待挙動を推測できる名前にする。
良い例:
- `accepted_case_missing_junit`
- `duplicate_testcase_key`
- `trace_input_schema_mismatch`
- `cli_exit_code_not_allowed`
- `component_validate_ignores_system_trace`
避ける例:
- `case1`
- `bad_project`
- `fixture_new`
- `test_all`
YAML や JSON の fixture は、必要な field だけを置く。
実際のユーザーリポジトリに近づけるために巨大化させるより、テストの意図が見えることを優先する。
## 18. 境界を守るテスト
Accay の architecture では、system と component の直接依存を避ける。
テストでもこの境界を明示的に守る。
確認すべき境界は次の通りである。
- system validation は component の `acceptance-scope.yaml` を必須入力にしない。
- system validation は component の `test-map.yaml` を読まない。
- component validation は system trace を必須入力にしない。
- component regression は system trace を正本として読まない。
- Output は正本成果物を直接読んで判定しない。
- CLI は validation / regression の本体ロジックを持たない。
これらは architecture intent の中核である。
実装が変わっても、Contract Test または Unit Test で守る。
## 19. エラーケースのテスト
成功ケースだけでは、受け入れ駆動ツールとして十分ではない。
Accay は失敗を説明するためのツールでもある。
次のエラーケースを優先してテストする。
- 必須ファイルがない。
- YAML が壊れている。
- schema file がない。
- schema validation に失敗する。
- operation が見つからない。
- operation ID が重複する。
- HTTP status code が許可されていない。
- CLI exit code が許可されていない。
- JUnit XML が壊れている。
- mapped testcase が missing。
- accepted case の testcase が skipped。
- report 出力先が作れない。
エラーケースでは、exit code だけでなく diagnostics の内容も確認する。
「失敗した」だけではなく、「どのファイルの何がなぜ失敗したか」が分かることを期待値にする。
## 20. テスト追加時のチェックリスト
新しいテストを追加するときは、次を確認する。
- その挙動は Contract Test で守るべき公開挙動か。
- Unit Test にする場合、Contract Test の代替にしていないか。
- fixture は目的に対して最小か。
- fixture 名で意図が分かるか。
- exit code を確認しているか。
- diagnostics の code / severity / path を確認しているか。
- run id、timestamp、絶対パスを正規化しているか。
- system と component の境界を混ぜていないか。
- golden file の比較範囲は広すぎないか。
- CI で実行されるべきテストか。
チェックリストに 1 つでも曖昧な点がある場合は、テスト名または fixture を先に見直す。
## 21. 既存テスト変更時のチェックリスト
既存テストを変更するときは、次を確認する。
- 仕様変更による変更か、実装都合による変更か。
- Contract Test の期待値を弱めていないか。
- Golden file の差分に意図しない情報欠落がないか。
- diagnostics code を不用意に変えていないか。
- exit code の契約を壊していないか。
- accepted case の fail / missing / skipped を見逃すようになっていないか。
- Probe Test を必須 CI に混ぜていないか。
- fixture project を他のテストと共有しすぎていないか。
テストの削除は、対象の公開挙動が不要になったことを確認してから行う。
単に実装が変わって失敗するようになっただけなら、削除ではなく期待する公開挙動を再確認する。
## 22. レビュー観点
テストレビューでは、実装の細かさよりも保証の意味を見る。
主な観点は次の通りである。
- このテストはどの利用者向け挙動を守っているか。
- 失敗したとき、原因に近いメッセージが出るか。
- 期待値が実装詳細に寄りすぎていないか。
- fixture が読み手に説明できる大きさか。
- Golden file が不要な揺れを固定していないか。
- architecture の責務境界を壊す前提になっていないか。
- CI での実行時間が妥当か。
Accay の自動テストは、単に coverage を増やすためのものではない。
受け入れ判断に必要な証拠を、安定して集め続けるための安全装置として保守する。
