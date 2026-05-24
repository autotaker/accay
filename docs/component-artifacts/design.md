# Component Artifacts 基本設計

## 1. 位置づけ

Component Artifacts は、component side の正本成果物を発見し、読み取り、後続処理が扱える構造へ変換する component である。
対象は `docs/acceptance/components/{component}/` 配下のファイルである。
この component は、受け入れ判断、意味判断、JUnit XML 集計、system trace 読み取りを行わない。
主な利用者は Component Harness、Component Regression、Operation Directory である。
Component Harness は scope / test-map / semantics / interfaces を使って validation と review context pack を作る。
Component Regression は test-map の JUnit testcase 参照を使って回帰照合を行う。
Operation Directory は interfaces のファイル集合を使って `component + operation` の契約参照を提供する。
この文書では、Component Artifacts の実装境界、読み取り対象、diagnostics、handoff の基本設計を定義する。

## 2. 設計原則

- component side の成果物は system side から独立して読む。
- component の単位は `docs/acceptance/components/{component}/` とする。
- component ID は `{component}` ディレクトリ名をそのまま使う。
- `acceptance-scope.yaml` を受け入れケース台帳の正本とする。
- `test-map.yaml` を受け入れレビューで認定されたテスト証拠台帳の正本とする。
- `semantics.md` を意味論の正本として参照可能にする。
- `review-guidelines.md` をレビュー観点の補助入力として参照可能にする。
- `interfaces/*` は Operation Directory へ渡す入力として扱う。
- 欠落、構文エラー、参照不整合は diagnostics として返す。
- 1 ファイルの失敗で component 全体の読み取りを止めすぎない。
- 可能な限り partial result と diagnostics を同時に返す。
- 最終的な accept / reject は人間とエージェントに残す。

## 3. スコープ

### 3.1 責務

- component ディレクトリ一覧を発見する。
- 指定 component の存在を確認する。
- `acceptance-scope.yaml` の存在を確認する。
- `acceptance-scope.yaml` を YAML として読み取る。
- scope の case ID、title、priority、status、scenarios、operations を構造化する。
- `test-map.yaml` の存在を確認する。
- `test-map.yaml` を YAML として読み取る。
- test-map の case ID、JUnit `classname`、JUnit `name`、`verifies` を構造化する。
- `semantics.md` の存在、パス、本文を返す。
- `review-guidelines.md` の存在、パス、本文を返す。
- `interfaces/openapi.yaml` の存在とパスを返す。
- `interfaces/operations.yaml` の存在とパスを返す。
- `interfaces/schemas/*.schema.json` の候補を列挙する。
- Component Harness、Component Regression、Operation Directory への handoff に必要な情報をまとめる。

### 3.2 非責務

- system trace の読み取り。
- scenario / sequence の読み取り。
- OpenAPI の詳細解釈。
- operation contract の正規化。
- JSON Schema validation。
- JUnit XML の読み取り。
- JUnit testcase の pass / fail / error / skipped 集計。
- `test-map.yaml` の自動更新。
- `acceptance-scope.yaml` の状態更新。
- `semantics.md` の意味判断。
- `review-guidelines.md` の妥当性判断。
- Markdown / HTML report の整形。

## 4. 正本ファイル

component の正本ディレクトリは以下である。

```text
docs/acceptance/components/{component}/
```

MVP で扱う canonical files は以下である。

```text
docs/acceptance/components/{component}/
  acceptance-scope.yaml
  test-map.yaml
  semantics.md
  review-guidelines.md
  interfaces/
    openapi.yaml
    operations.yaml
    schemas/
      *.schema.json
```

| ファイル | 位置づけ | 欠落時 |
|---|---|---|
| `acceptance-scope.yaml` | 受け入れケース台帳 | error |
| `test-map.yaml` | テスト証拠台帳 | error |
| `semantics.md` | 意味論の正本 | warning |
| `review-guidelines.md` | レビュー観点の補助入力 | info |
| `interfaces/openapi.yaml` | HTTP operation の外部仕様 | 条件付き |
| `interfaces/operations.yaml` | Accay native operation 定義 | 条件付き |
| `interfaces/schemas/` | JSON Schema 置き場 | 参照時に検証 |

`interfaces/openapi.yaml` と `interfaces/operations.yaml` はどちらか一方だけでもよい。
両方が存在する場合、operation ID 重複の検出は Operation Directory または Component Harness の責務とする。
`semantics.md` は重要な正本だが、Component Artifacts は意味の充足性を判定しない。
`review-guidelines.md` は欠落しても読み取り不能にはしない。

## 5. 公開モデル

Component Artifacts は概念的に以下を返す。

```text
ComponentArtifactSet
  component_id
  root_path
  scope
  test_map
  semantics
  review_guidelines
  interfaces
  diagnostics
```

`component_id` は component ディレクトリ名である。
`root_path` は component ディレクトリのパスである。
`scope` は `acceptance-scope.yaml` を構造化した情報である。
`test_map` は `test-map.yaml` を構造化した情報である。
`semantics` と `review_guidelines` は Markdown 文書の参照情報である。
`interfaces` は Operation Directory に渡す interface file set である。
`diagnostics` は読み取り中に見つかった問題の一覧である。

主な下位 model は以下である。

| model | 主なフィールド |
|---|---|
| `ComponentScope` | `file_path`, `declared_component`, `cases`, `raw` |
| `AcceptanceCase` | `case_id`, `title`, `priority`, `status`, `scenarios`, `operations`, `raw` |
| `ComponentTestMap` | `file_path`, `declared_component`, `mappings`, `raw` |
| `TestMapping` | `case_id`, `tests` |
| `JUnitTestRef` | `classname`, `name`, `verifies` |
| `MarkdownArtifact` | `file_path`, `exists`, `content`, `read_error` |

内部実装では dataclass、TypedDict、Pydantic model、dict のいずれを使ってもよい。
未知フィールドは原則 error にせず、必要なら `raw` に保持する。
JUnit testcase は `classname + name` の pair として保持する。
JUnit XML 内に存在するかどうかは Component Regression が判定する。
Markdown AST 化は必須ではなく、本文を UTF-8 text として保持できればよい。

## 6. component discovery

component 発見は `docs/acceptance/components/` 直下のディレクトリを対象にする。
通常ファイルは component として扱わない。
`.` で始まるディレクトリは無視してよい。
`_` で始まるディレクトリはテンプレートや共有部品の予約にできるため、MVP では無視してよい。
空ディレクトリは component 候補として扱い、欠落 diagnostics を返す。
component 一覧は component ID の昇順など、安定した順序で返す。
ファイルシステムの列挙順には依存しない。
`accay component validate <component>` では指定 component のみを読む。
指定 component が存在しない場合は `component_not_found` diagnostic を返す。
存在しない component のために他 component を読む必要はない。
component ID はディレクトリ名をそのまま使い、大文字小文字の正規化はしない。
空白を含む component ID は warning にしてよい。
厳密な命名規則は Component Harness の validation policy に寄せる。

## 7. acceptance-scope.yaml 読み取り

`acceptance-scope.yaml` は component 単位の受け入れケース台帳である。

```yaml
component: order-domain

cases:
  ORD-001:
    title: 注文を作成できる
    priority: P0
    status: accepted
    scenarios:
      - order-checkout
    operations:
      - createOrder
```

読み取る主要項目は以下である。

| 項目 | 用途 |
|---|---|
| `component` | ディレクトリ名との整合性確認 |
| `cases.{case_id}.title` | context / report 表示 |
| `cases.{case_id}.priority` | 集計と表示 |
| `cases.{case_id}.status` | regression policy の入力 |
| `cases.{case_id}.scenarios` | scenario との参考紐づき |
| `cases.{case_id}.operations` | Operation Directory への参照確認 |

`cases` は case ID を key にした mapping とする。
case ID は component 内で一意である。
YAML duplicate key を検出できる loader が利用できるなら使う。
未知フィールドは保持してもよいし、読み飛ばしてもよい。
未知フィールドを即 error にしない。
status は `draft`、`ready`、`accepted`、`blocked`、`deprecated` を想定する。
未知 status は diagnostic にするが、読み取りは継続する。
accepted かどうかを最終的にどう扱うかは Component Regression の判定に委ねる。
parse error の場合、scope model は空でもよい。
その場合も component ID、file path、parse diagnostic は返す。

代表 diagnostics は以下である。

- `scope_missing`: ファイルが存在しない。
- `scope_parse_error`: YAML として parse できない。
- `scope_shape_invalid`: top-level が mapping ではない。
- `scope_component_missing`: `component` がない。
- `scope_component_mismatch`: `component` がディレクトリ名と違う。
- `scope_cases_missing`: `cases` がない。
- `scope_cases_invalid`: `cases` が mapping ではない。
- `scope_case_title_missing`: case の `title` がない。
- `scope_case_status_unknown`: case の `status` が未知である。
- `scope_case_operations_invalid`: `operations` が list ではない。

## 8. test-map.yaml 読み取り

`test-map.yaml` は受け入れレビューで認定されたテスト証拠台帳である。

```yaml
component: order-domain

mappings:
  ORD-001:
    tests:
      - junit:
          classname: tests.acceptance.order.test_create_order
          name: test_create_order_success
        verifies:
          - order is persisted
          - order id is returned
```

読み取る主要項目は以下である。

| 項目 | 用途 |
|---|---|
| `component` | ディレクトリ名との整合性確認 |
| `mappings.{case_id}` | scope case との参照確認 |
| `tests[].junit.classname` | JUnit XML 照合 |
| `tests[].junit.name` | JUnit XML 照合 |
| `tests[].verifies` | 証拠説明と validation |

`mappings` は case ID を key にした mapping とする。
`tests` は JUnit testcase 参照の配列である。
JUnit testcase は `classname + name` で識別する。
独自 test ID は持たない。
test file path は MVP では持たない。
`verifies` は 1 件以上を期待する。
`verifies` の言語や表現品質は Component Artifacts では判定しない。
test-map の case ID が scope に存在するかは diagnostic 化してよい。
validation policy の最終判定は Component Harness に寄せる。
同一 `classname + name` が複数 mapping に出る場合は warning または error にできる。
JUnit XML 間の testcase 重複検出は Component Regression の責務である。

代表 diagnostics は以下である。

- `test_map_missing`: ファイルが存在しない。
- `test_map_parse_error`: YAML として parse できない。
- `test_map_shape_invalid`: top-level が mapping ではない。
- `test_map_component_missing`: `component` がない。
- `test_map_component_mismatch`: `component` がディレクトリ名と違う。
- `test_map_mappings_missing`: `mappings` がない。
- `test_map_mappings_invalid`: `mappings` が mapping ではない。
- `test_map_unknown_case`: mapping の case ID が scope に存在しない。
- `test_map_tests_invalid`: `tests` が list ではない。
- `test_map_junit_classname_missing`: `junit.classname` がない。
- `test_map_junit_name_missing`: `junit.name` がない。
- `test_map_verifies_missing`: `verifies` がない。
- `test_map_verifies_empty`: `verifies` が空である。

## 9. semantics / review-guidelines

`semantics.md` は component と operation の意味論の正本である。
Component Artifacts は file path、存在有無、本文、読み取りエラーを返す。
Markdown の見出し構造を厳密に検証しない。
意味論の充足性、矛盾、妥当性は判定しない。
Component Harness は review context pack に含める材料として使う。
Operation Directory は `semantics.md` を読まない。

`review-guidelines.md` は受け入れレビューの観点を補助する文書である。
Component Artifacts は file path、存在有無、本文、読み取りエラーを返す。
欠落しても component artifact 全体は読み取り可能とする。
レビュー観点の正しさや網羅性は判定しない。
`component pack review` では context に含めてよい。

## 10. interfaces handoff

interfaces は以下に置く。

```text
docs/acceptance/components/{component}/interfaces/
```

Component Artifacts が行うのは file set の列挙である。
OpenAPI を Accay operation model に変換しない。
`operations.yaml` を完全な operation contract に正規化しない。
JSON Schema の中身を validation しない。
Operation Directory へ渡す情報は以下である。

```text
InterfaceFileSet
  component_id
  component_root
  openapi_path
  operations_path
  schema_dir
  schema_files
```

Operation Directory はこの情報を使って以下を行う。

- OpenAPI の `operationId` を読む。
- `operations.yaml` の operation を読む。
- `component + operation` の lookup を提供する。
- input / output schema 参照を解決する。
- operation ID 重複を検出する。
- HTTP status code や CLI exit code の参照確認を支援する。

Component Artifacts は Operation Directory の結果を意味判断に使わない。
依存方向は `component -> operations` を許可するが、artifact loader 同士の相互依存は作らない。

## 11. system trace からの独立

Component Artifacts は `docs/acceptance/traces/` を正本として読まない。
trace に出てくる component 名から component ディレクトリを生成しない。
trace に出てくる operation 名から `acceptance-scope.yaml` を補完しない。
trace に存在しない component でも、component ディレクトリがあれば読み取る。
component validation と component regression は component 配下の成果物だけで最低限成立する。
`component pack review` では関連 trace / scenario / sequence を参考情報として含める可能性がある。
その場合も、Component Artifacts の責務ではなく Component Harness または pack 生成処理の責務とする。
この分離により、system side と component side が互いの正本に直接依存しない。

## 12. diagnostics handoff

diagnostic は、読み取り時に見つかった問題を後続処理へ渡すための構造化情報である。
Component Artifacts は例外を外へ漏らしすぎず、diagnostic に変換する。
ただし、repository root が見つからないなどの workspace 問題は workspace 層の責務である。
component 配下の個別ファイル問題は component diagnostic として返す。

推奨フィールドは以下である。

```text
Diagnostic
  severity
  code
  message
  component_id
  file
  location
  details
```

`severity` は `error`、`warning`、`info` を想定する。
`code` は機械比較しやすい短い識別子にする。
`message` は人間が読める短文にする。
`file` は該当ファイルのパスを示す。
`location` は YAML path や line / column を持てる場合に入れる。
`details` は parser error などの補足情報を持つ。

代表 code は以下である。

| code | severity | 意味 |
|---|---|---|
| `component_not_found` | error | 指定 component が存在しない |
| `component_empty` | warning | component ディレクトリに正本ファイルがない |
| `scope_missing` | error | `acceptance-scope.yaml` がない |
| `scope_parse_error` | error | scope を parse できない |
| `test_map_missing` | error | `test-map.yaml` がない |
| `test_map_parse_error` | error | test-map を parse できない |
| `test_map_unknown_case` | error | test-map が未知の case ID を参照する |
| `test_map_verifies_empty` | error | `verifies` が空である |
| `semantics_missing` | warning | `semantics.md` がない |
| `review_guidelines_missing` | info | `review-guidelines.md` がない |
| `interfaces_missing` | warning | `openapi.yaml` も `operations.yaml` もない |

severity の最終的な exit code 反映は CLI または Component Harness が決める。
Output & Presentation は diagnostics を整形するだけで、正本ファイルを直接読まない。
そのため、Component Artifacts は report に必要な file path と message を diagnostic に含める。

## 13. 例

### 13.1 ディレクトリ

```text
docs/acceptance/components/order-domain/
  acceptance-scope.yaml
  test-map.yaml
  semantics.md
  interfaces/
    operations.yaml
    schemas/
      create-order-command.schema.json
      create-order-result.schema.json
```

### 13.2 acceptance-scope.yaml

```yaml
component: order-domain

cases:
  ORD-001:
    title: 注文を作成できる
    priority: P0
    status: accepted
    scenarios:
      - order-checkout
    operations:
      - createOrder
```

### 13.3 test-map.yaml

```yaml
component: order-domain

mappings:
  ORD-001:
    tests:
      - junit:
          classname: tests.acceptance.order.test_create_order
          name: test_create_order_success
        verifies:
          - order is persisted
          - order id is returned
```

### 13.4 handoff 結果

```text
ComponentArtifactSet
  component_id: order-domain
  scope.cases: [ORD-001]
  test_map.mappings: [ORD-001]
  semantics.exists: true
  review_guidelines.exists: false
  interfaces.operations_path: docs/acceptance/components/order-domain/interfaces/operations.yaml
  diagnostics: [review_guidelines_missing]
```

`review-guidelines.md` は任意なので、この例では info diagnostic として扱える。
Component Artifacts は、後続が判断できるよう scope、test-map、Markdown、interfaces をまとめて返す。

## 14. テスト戦略

### 14.1 Unit Test

- component ディレクトリを安定順序で列挙できる。
- 指定 component が存在しない場合に `component_not_found` を返せる。
- `acceptance-scope.yaml` を正常に parse できる。
- scope の parse error を diagnostic にできる。
- scope の component mismatch を検出できる。
- `test-map.yaml` を正常に parse できる。
- test-map の parse error を diagnostic にできる。
- test-map の unknown case を検出できる。
- `verifies` 空配列を検出できる。
- `semantics.md` 欠落を warning にできる。
- `review-guidelines.md` 欠落を info にできる。
- interface file set を列挙できる。
- system trace がなくても読み取りが成立する。

### 14.2 Contract Test

- `accay component validate <component>` が対象 component だけを読む。
- `accay validate` が全 component を安定順序で扱う。
- 欠落ファイルと parse error の file path が CLI diagnostics に出る。
- system trace が存在しなくても component validation が動く。
- Operation Directory へ interfaces が渡り、operation 参照確認に使われる。

Contract Test は fixture project を使う。
内部 model の形ではなく、CLI 出力、exit code、生成 report の主要構造を確認する。

### 14.3 Probe Test

Probe Test は調査用に置いてよい。
例として、YAML duplicate key の loader 挙動や Markdown 読み取りの edge case を観察する。
Probe Test は通常 CI の必須対象にしない。

## 15. 実装メモ

YAML parser は安全な loader を使う。
可能なら line / column を diagnostic に残せる parser を選ぶ。
YAML parse error は `*_parse_error` diagnostic に変換する。
Markdown は UTF-8 text として読む。
内部では repository root からの相対パスを保持すると report が安定しやすい。
実ファイル読み取りには絶対パスを使ってよい。
diagnostic には人間が辿りやすい相対パスを入れる。
読み取りは partial success を許容する。
scope が壊れていても test-map の parse を試みる。
test-map が壊れていても semantics と interfaces の存在確認を行う。
未知フィールドは原則として破壊しない。
Component Artifacts は自動更新を行わないため、未知フィールド保持は必須ではない。
MVP では component 数が大きくない前提でよい。
それでも同じ file を複数回読まないようにする。
`accay validate` では artifact set を一度読み、Component Harness と Operation Directory へ渡す。
キャッシュは必須ではない。
キャッシュを入れる場合も正本ファイルの更新検出を誤らないようにする。
ファイルシステムエラー、権限エラー、文字コードエラーは diagnostic に変換する。
Python の具体的な class 名、diagnostics の最終 JSON 形式、Markdown report の見た目はこの文書では固定しない。
ただし、component side が system trace を正本入力にしないこと、Operation Directory を境界にすること、意味判断を外へ残すことは維持する。
