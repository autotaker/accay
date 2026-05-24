# Component Regression 基本設計
作成日: 2026-05-24  
対象: Accay MVP  
参照: ../architecture.md, ../requirements.md

## 1. 位置づけ
Component Regression は、component 単位の受け入れレビュー回帰を行う component である。
JUnit XML と `test-map.yaml` を照合し、受け入れ済み case の保証が壊れていないかを機械的に集計する。
Accay のハーネスは最終的な受け入れ判断を行わない。
Component Regression も同じ方針に従い、意味判断、修正方針、test-map 更新の自動採用は行わない。
system trace は直接の入力にしない。
top-level regression は、全 component の `ComponentRegressionResult` を集約するだけである。
この文書は、実装時に揺らしたくない JUnit reader、merge、matching、aggregation、policy、diagnostics、handoff、failure mode、test strategy を定義する。

## 2. 目的
Component Regression が答える問いは以下である。
- `test-map.yaml` に登録された testcase は JUnit XML に存在するか。
- 登録された testcase は pass しているか。
- fail / error / skipped / missing が accepted case に影響しているか。
- component 単位で regression failure があるか。
- Output & Presentation に渡すべき warning、info、unmapped test があるか。
失敗が仕様変更、実装不具合、テスト不具合、または `test-map.yaml` の陳腐化かは判断しない。
その判断は、report を読んだ人間またはエージェントに残す。

## 3. 基本方針
Component Regression は component side の処理であり、system side の artifact loader に依存しない。
入力の正本は component 配下の `acceptance-scope.yaml`、`test-map.yaml`、および JUnit XML である。
system scenario や trace を参考情報として表示する場合も、regression 判定の入力にはしない。
JUnit XML は外部形式として境界で読み、内部では正規化済み model だけを扱う。
MVP の testcase key は `classname + name` とする。
独自 test id、file path、line number、framework 固有 id は照合キーにしない。
validation error と regression failure は分けて扱う。
入力が壊れていて信頼できない場合は result を `invalid` にする。
入力は読めるが受け入れ済み case が壊れている場合は、case result と diagnostic severity `fail` で表現する。

## 4. 責務
Component Regression の責務は以下である。
- 1 つ以上の JUnit XML を読み取る。
- JUnit testcase を `classname + name` で正規化する。
- 複数 JUnit XML を 1 つの test result set に merge する。
- duplicate testcase を validate error にする。
- `acceptance-scope.yaml` の case status を参照する。
- `test-map.yaml` の mapping と JUnit result を照合する。
- case 単位の pass / fail / error / skipped / missing を集計する。
- accepted case の failed / error / skipped / missing を regression failure として扱う。
- non-accepted case の failed / error を policy に従い warning または report only にする。
- unmapped test を diagnostics に残す。
- component regression result を Output & Presentation に渡す。

## 5. 非責務
Component Regression は以下を行わない。
- system trace、scenario、sequence の読み取り。
- 失敗原因の意味解釈。
- flaky test の自動判定。
- retry の実行。
- JUnit XML の生成。
- test runner の起動。
- `test-map.yaml` の自動更新。
- `acceptance-scope.yaml` の status 更新。
- report の最終整形。
- PR コメント投稿や CI provider 連携。

## 6. 入力
入力は component model、JUnit XML、regression rules である。
component model は Component Artifacts が読み取った結果であり、component id、acceptance cases、case status、test mappings を含む。
`acceptance-scope.yaml` は case 台帳である。
Component Regression は case ID、title、status、priority、related operations を参照する。
case の本文や semantics は意味解釈しない。
`status: accepted` の case だけを accepted case として扱う。
`draft`、`ready`、`blocked`、`deprecated` は non-accepted case として扱う。
`test-map.yaml` は受け入れレビューで認定されたテスト証拠台帳である。
MVP では `mappings` を辞書として扱い、key を case ID とする。
JUnit mapping には `junit.classname`、`junit.name`、`verifies` が必要である。
`verifies` は 1 件以上必須であり、判定には使わず report handoff 用に保持する。
JUnit XML は 1 つ以上指定できる。
指定元は CLI 引数または `.accay/config.yaml` の `junit.paths` とする。
JUnit XML は test runner の成果物であり、component directory 配下にある必要はない。
regression rules は `.accay/config.yaml` の `regression.*` から与えられる。
設定がない条件は、この文書の default policy を使う。

## 7. test-map.yaml の前提
MVP の mapping 例は以下である。
```yaml
component: order-domain
mappings:
  ORD-001:
    tests:
      - junit:
          classname: tests.acceptance.order.test_create_order
          name: test_create_order_success
        verifies:
          - order persisted
```
`mappings` は配列ではなく辞書である。
acceptance / regression の分類は持たない。
独自 test id は持たない。
path は MVP では持たない。
JUnit XML の `classname + name` で照合する。
`verifies` は自由記述の短文リストであり、1 件以上を必須とする。

## 8. 出力
出力は `ComponentRegressionResult` である。
Output & Presentation はこの result を受け取り、Markdown / HTML / dashboard に整形する。
Component Regression は Markdown や HTML の最終テンプレートを持たない。
出力には component summary、case results、testcase results、regression failures、warnings、info diagnostics、unmapped tests、validate errors、input metadata、applied policy を含める。
CLI は result summary を見て exit code を決める。
基本ルールは、validate error または severity `fail` が 1 件以上あれば non-zero とする。

## 9. JUnit reader
JUnit reader は XML file を読み、内部の `TestcaseResult` に変換する。
reader は XML parse と正規化だけを行い、regression policy は扱わない。
MVP では root が `testsuite` または `testsuites` の JUnit XML に対応する。
`testsuite/testcase` と `testsuites/testsuite/testcase` を読む。
namespace がある場合でも local name で `testsuite` と `testcase` を判定する。
`testcase` からは `classname`、`name`、`time`、`file`、`line` を読む。
`classname` と `name` は必須である。
どちらかが空の場合は invalid testcase とし、通常の照合対象から除外する。
`time`、`file`、`line` は任意であり report 補足に使う。
XML として parse できない file は input-level validate error とする。
parse error がある場合、component result は `invalid` とし、case 単位の missing を大量生成しない。

## 10. JUnit status 判定
testcase の status は子要素で決める。
`failure` があれば `fail` とする。
`error` があれば `error` とする。
`skipped` があれば `skipped` とする。
上記がなければ `pass` とする。
`failure` と `error` が同時にある場合は `error` を優先する。
`skipped` と `failure` または `error` が同時にある場合は validate warning とし、`error > fail > skipped` の順で status を決める。
`failure`、`error`、`skipped` の `message` と `type` は diagnostics 用に保持する。
body text は長くなりやすいため、handoff 用には上限を設ける。
truncation した場合は result model にその事実を残す。

## 11. Test result set
`TestcaseKey` は `classname` と `name` の 2 要素で構成する。
parent testsuite name、file、line は key に含めない。
表示用には `classname::name` のような文字列を作ってよい。
内部 key は delimiter 衝突を避けるため tuple 相当で扱う。
`TestcaseResult` は key、status、source path、suite name、time、message、type、raw location を持つ。
`TestResultSet` は key から `TestcaseResult` への辞書、duplicates、invalid testcases、input errors、source files を持つ。
すべての指定 JUnit XML は同一 run の test result set として扱う。

## 12. result merge rules
同じ `classname + name` の testcase が複数回出現した場合は duplicate testcase とする。
duplicate は validate error であり、last wins や worst wins の上書きは行わない。
duplicate の検出範囲は、同一 JUnit XML 内、複数 JUnit XML 間、複数 testsuite 間のすべてである。
parent testsuite name は key に含めないため、suite が違っても `classname + name` が同じなら duplicate である。
duplicate がある component result は `invalid` とする。
case aggregation を補助的に継続してもよいが、CI 判定では validate error を優先する。
report には duplicate key、source path、suite name を渡す。
指定 JUnit XML path が存在しない場合は `missing testcase` ではなく input error とする。

## 13. test-map matching
matching は以下の順序で行う。
1. `acceptance-scope.yaml` から case dictionary を作る。
2. `test-map.yaml` の mapping を case ID ごとに読む。
3. mapping の case ID が scope に存在するか確認する。
4. mapping 内の `junit.classname + junit.name` から key を作る。
5. `TestResultSet` に key が存在するか確認する。
6. testcase status を case aggregation に渡す。
7. result set に存在するが mapping されていない testcase を unmapped として残す。
`test-map.yaml` の case ID が scope に存在しない場合は validate error とする。
同一 case の `tests` 内で同じ testcase key が複数回出る場合も validate error とする。
同じ testcase key が複数 case に mapping されることは許可する。
1 つのテストが複数の受け入れ case を保証することはあり得るためである。
unmapped test は JUnit XML には存在するが `test-map.yaml` に登録されていない testcase である。
unmapped test は regression failure ではなく、default policy では info とする。

## 14. case aggregation
`CaseResult` は case ID、title、scope status、priority、testcase results、aggregate status、severity、diagnostics を持つ。
case に複数 testcase がある場合、最も重い status を case の aggregate status とする。
優先順は `error > fail > missing > skipped > pass` である。
`missing` は実行結果ではなく照合結果である。
`test-map.yaml` にある testcase key が `TestResultSet` に存在しない場合、その testcase は `missing` になる。
すべての mapped testcase が pass の場合、case aggregate status は `pass` とする。
fail が 1 件以上あれば `fail`、error が 1 件以上あれば `error` とする。
skipped が 1 件以上あり、error / fail / missing がなければ `skipped` とする。
missing が 1 件以上あり、error / fail がなければ `missing` とする。
scope に存在するが `test-map.yaml` に mapping がない case は、通常は regression 主対象ではない。
ただし accepted case に mapping がない場合は warning diagnostic を出す。

## 15. policy defaults
設定がない場合、以下を default policy とする。
| 条件 | severity |
|---|---|
| accepted case + failed | fail |
| accepted case + error | fail |
| accepted case + missing | fail |
| accepted case + skipped | fail |
| non-accepted case + failed | warning |
| non-accepted case + error | warning |
| non-accepted case + missing | info |
| non-accepted case + skipped | info |
| unmapped test | info |
| accepted case without mapping | warning |
| validate error | fail |
accepted case は `status: accepted` の case だけである。
`ready` はまだ accepted ではなく、`deprecated` も accepted として扱わない。
deprecated case に mapping が残っている場合は info diagnostic とする。
policy は severity を決める。
policy は testcase status や case aggregate status を変更しない。

## 16. diagnostics model
Diagnostic は、人間とエージェントが原因調査を始めるための構造化情報である。
項目は code、severity、message、component、case_id、testcase_key、source、details とする。
code は安定した診断 code である。
severity は fail / warning / info のいずれかである。
message は短い説明である。
source は JUnit XML または artifact path を指す。
details は duplicate 出現元、XML parse error、testcase message などの補足を持つ。
diagnostic code は report、CI、dashboard filter で使うため安定させる。
message は改善してよいが、code の意味は互換性を保つ。

## 17. diagnostic codes
代表的な diagnostic code は以下である。
| code | 意味 |
|---|---|
| `REG-JUNIT-PARSE-ERROR` | JUnit XML を parse できない |
| `REG-JUNIT-FILE-MISSING` | 指定 JUnit XML が存在しない |
| `REG-JUNIT-INVALID-TESTCASE` | testcase の必須属性がない |
| `REG-JUNIT-DUPLICATE-TESTCASE` | `classname + name` が重複 |
| `REG-MAP-UNKNOWN-CASE` | test-map の case ID が scope にない |
| `REG-MAP-DUPLICATE-TEST` | 同一 case 内で testcase mapping が重複 |
| `REG-MAP-EMPTY-VERIFIES` | verifies が空 |
| `REG-CASE-FAILED` | case に failed testcase がある |
| `REG-CASE-ERROR` | case に error testcase がある |
| `REG-CASE-SKIPPED` | case に skipped testcase がある |
| `REG-CASE-MISSING` | mapped testcase が JUnit XML にない |
| `REG-CASE-NO-MAPPING` | accepted case に mapping がない |
| `REG-TEST-UNMAPPED` | JUnit XML の testcase が map されていない |

## 18. results model
`ComponentRegressionResult` は component id、status、summary、case results、unmapped tests、diagnostics、inputs、policy を持つ。
`status` は result が信頼できるかを表し、`valid` または `invalid` とする。
validate error がある component は `status: invalid` になる。
case の regression failure は `status: valid` のまま、diagnostic severity `fail` として表現する。
summary は report と CLI 表示のための集計値である。
summary には total cases、accepted cases、mapped cases、passed cases、failed cases、error cases、skipped cases、missing cases、unmapped tests、validate errors、warnings、infos を含める。
`TopLevelRegressionResult` は、複数 component の `ComponentRegressionResult` を集約した result である。
top-level regression は JUnit XML と `test-map.yaml` の照合ロジックを再実装しない。
CLI が component ごとに Component Regression を呼び、結果をまとめる。

## 19. component-level regression
`accay component regression <component>` は指定 component だけを対象にする。
入力は、その component の `acceptance-scope.yaml`、`test-map.yaml`、指定 JUnit XML である。
component-level result は、1 component の詳細調査に向く。
処理順は component artifacts の load、JUnit XML read、result set merge、test-map matching、case aggregation、component result build、Output handoff である。
component-level regression でも system trace は読まない。

## 20. top-level regression
`accay regression` は全 component を対象にする。
top-level regression は component ごとの result を集約するだけである。
system trace は読まず、system side の desk-debug regression とは別 workflow とする。
top-level regression では、同じ JUnit XML result set を複数 component に対して使ってよい。
monorepo で 1 つの test run が複数 component の証拠を含む場合があるためである。
MVP では CLI 引数または config の `junit.paths` を共通入力として扱う。

## 21. report handoff
Component Regression は `ComponentRegressionResult` を返す。
Output & Presentation は result を受け取り、Markdown / HTML / dashboard に変換する。
Output 側は、追加で component artifact を読んで判定を変えてはならない。
handoff では component id、run metadata、source JUnit XML paths、applied policy、case result table、failed / error / skipped / missing details、unmapped tests、duplicate diagnostics、invalid input diagnostics、verifies text、testcase message summary を渡す。
表示の推奨優先順は、validate error、accepted case の fail / error / missing / skipped、accepted case without mapping、non-accepted case warning、unmapped test、pass summary とする。
JUnit の failure body は長くなりやすいため、handoff 用には短い message summary を用意する。

## 22. failure modes
代表的な failure mode は以下である。
| failure mode | 扱い |
|---|---|
| JUnit XML path がない | `REG-JUNIT-FILE-MISSING`。input-level validate error |
| XML が壊れている | `REG-JUNIT-PARSE-ERROR`。component result は invalid |
| testcase 必須属性がない | `REG-JUNIT-INVALID-TESTCASE`。該当 testcase は照合対象外 |
| duplicate testcase | `REG-JUNIT-DUPLICATE-TESTCASE`。component result は invalid |
| scope にない case ID が map にある | `REG-MAP-UNKNOWN-CASE`。validate error |
| 同一 case 内の duplicate mapping | `REG-MAP-DUPLICATE-TEST`。validate error |
| verifies が空 | `REG-MAP-EMPTY-VERIFIES`。validate error |
| mapped testcase がない | `REG-CASE-MISSING`。accepted case では fail |
| mapped testcase が skipped | `REG-CASE-SKIPPED`。accepted case では fail |
| JUnit XML が空 | input warning。accepted mapping は missing になる |
file missing は testcase missing とは区別する。
input が信頼できない場合は、case missing を大量生成するより input-level error を優先する。

## 23. implementation notes
実装は architecture の `component` 領域に置く。
想定 module は `accay/component/regression.py`、`accay/component/junit.py`、`accay/component/regression_models.py` である。
実際の file 分割は実装時に調整してよい。
ただし、JUnit reader、matching、aggregation、policy application は関心を分ける。
JUnit XML の file read 以外は pure function に寄せる。
推奨する関数境界は `read_junit_files(paths) -> TestResultSet`、`merge_testcases(testcase_lists) -> TestResultSet`、`match_test_map(component_model, result_set) -> MatchResult`、`aggregate_cases(match_result, policy) -> list[CaseResult]`、`build_component_result(...) -> ComponentRegressionResult` である。
result model に入れる path は repository root からの相対 path を優先する。
出力の安定性のため、case ID、testcase key、source path は sort する。
run id は CLI または workspace 層が生成し、Component Regression は渡された metadata を result に含めるだけでよい。
diagnostic code は英数字で固定し、message は `language.reports` に応じて差し替えられる余地を残す。

## 24. test strategy
unit test は pure function を中心にする。
JUnit reader では root `testsuite`、root `testsuites`、namespace 付き XML、pass / fail / error / skipped、`classname` 欠落、`name` 欠落を確認する。
merge test では複数 XML、同一 XML 内 duplicate、複数 XML 間 duplicate、file missing、parse error を確認する。
matching test では missing testcase、unmapped testcase、same testcase の複数 case mapping、同一 case 内 duplicate mapping、unknown case、empty verifies を確認する。
aggregation test では accepted skipped の fail severity、accepted missing の fail severity、non-accepted failed の warning、unmapped の info を確認する。
fixture project を使い、実際の `acceptance-scope.yaml`、`test-map.yaml`、JUnit XML を組み合わせて検証する。
fixture は小さく保ち、1 fixture につき 1 つの主眼を持たせる。
CLI integration test では `accay component regression <component> --junit <path>`、`accay regression --junit <path>`、fail severity 時の non-zero、warning / info のみの zero、invalid input の non-zero を確認する。
Output & Presentation との結合では Markdown / HTML の golden test を置いてよい。
Component Regression の unit test は report の文面に依存しない。
diagnostic code、case aggregate status、summary count は snapshot 対象にしてよい。

## 25. 受け入れ条件
MVP の Component Regression は少なくとも以下を満たす。
- 1 つ以上の JUnit XML を読める。
- 複数 JUnit XML を 1 つの result set として merge できる。
- `classname + name` で testcase を一意化できる。
- duplicate testcase を validate error にできる。
- `test-map.yaml` と JUnit result を照合できる。
- accepted case の fail / error / skipped / missing を fail severity にできる。
- non-accepted case の fail / error を warning にできる。
- unmapped test を info として report handoff できる。
- component-level regression result を返せる。
- top-level regression が component result の集約として表現できる。
- Output & Presentation に判断済みの構造化 result を渡せる。

## 26. 将来拡張
MVP では扱わないが、将来の拡張候補は以下である。
- component ごとの JUnit path 設定。
- flaky test の履歴表示。
- unmapped test の `test-map.yaml` 追加候補生成。
- test framework 固有 metadata の取り込み。
- testcase path / line による補助表示。
- report 上での filter / drill down。
- PR コメント投稿。
- retry 結果の扱い。
- junit attachment の参照。
- language-aware test discovery。
これらは現在の architecture intent を変えない範囲で追加する。
特に、system trace を Component Regression の正本入力にしない方針は維持する。
