# Operation Directory 基本設計

## 1. 役割

Operation Directory は、system と component の唯一の機械的な接続点である。

component の interface 成果物から operation catalog と schema registry を作り、`component + operation` で参照できるようにする。意味判断や受け入れ判断は行わない。

## 1.1 Interface semantics

公開 operation の意味論は [semantics.md](semantics.md) を正本とする。
この design は、その意味論を catalog 構築、schema ref 解決、status / exit code 照合としてどう実現するかを定義する。

## 2. 責務境界

### 責務

- component 配下の `interfaces/*` を読み取る。
- OpenAPI から HTTP operation を取り込む。
- Accay native `operations.yaml` から `http` / `cli` / `function` operation を取り込む。
- JSON Schema の参照を解決する。
- component 内の operation ID 重複を検出する。
- `component + operation` lookup API を提供する。
- HTTP status code と CLI exit code の照合材料を提供する。

### 非責務

- `semantics.md` の意味判断。
- acceptance case の状態管理。
- `test-map.yaml` の照合。
- trace の意味判断。
- OpenAPI lint 全般。
- function の実コード存在確認。

## 3. Operation catalog

operation catalog は、component ごとに operation を保持する。

| 項目 | 内容 |
|---|---|
| component | component 名 |
| operation id | component 内で一意な operation ID |
| kind | `http`, `cli`, `function` |
| signature | `function` の型付き境界。実コード存在確認はしない |
| schema refs | Accay 独自型名から JSON Schema `$defs` への参照 |
| status codes | `http` の場合の許容 status |
| exit codes | `cli` の場合の許容 exit code |

MVP では namespace や override は持たない。同一 component 内で OpenAPI と `operations.yaml` の operation ID が重複した場合は error にする。

## 4. Schema registry

Schema registry は、repository root からの相対 path で JSON Schema を解決する。
`operations.yaml` では `schema_refs` を使い、独自型名から `schemas/{component}.yaml#/$defs/{TypeName}` のような JSON Pointer 付き参照へ解決する。

用途:

- trace `input.value` の validation。
- trace `output.value` の validation。
- operation contract の参照整合性確認。

JSON Schema で表現しにくい意味や副作用は扱わない。それらは `semantics.md` と observations に残す。

## 5. OpenAPI の扱い

OpenAPI は HTTP operation adapter として扱う。

読むもの:

- `operationId`
- request / response schema 参照
- HTTP status code

深く読まないもの:

- security scheme
- server URL
- auth flow
- examples
- detailed description
- `oneOf` / `anyOf` の高度な意味解釈

## 6. `operations.yaml` の扱い

`operations.yaml` は Accay native の operation 定義である。

対象 kind:

- `http`
- `cli`
- `function`

`function` は人間・AI 向け参照情報として扱い、実コード検証はしない。

## 7. Lookup API

想定する問い合わせ:

- `get_component(component)`
- `get_operation(component, operation)`
- `get_input_schema(component, operation)`
- `get_output_schema(component, operation)`
- `allows_status(component, operation, status)`
- `allows_exit_code(component, operation, exit_code)`

実際の関数名は実装で決めてよい。重要なのは、system / component が raw OpenAPI や raw YAML を直接読まないことである。

## 8. Diagnostics

| severity | 例 |
|---|---|
| error | operation ID 重複、schema ref 不存在、不正 YAML |
| warning | 任意 metadata 欠落、未使用 schema |
| info | 読み込んだ operation 数 |

diagnostics には component、source file、operation id を含める。

## 9. Caching

Operation Directory は command 実行中に構築される in-memory catalog とする。

MVP では永続 cache は必須にしない。`.accay/cache/` は後続フェーズで必要になった場合に使う。

## 10. テスト観点

Contract Test:

- OpenAPI operation を trace validation で参照できる。
- `operations.yaml` operation を trace validation で参照できる。
- 重複 operation ID で validate error になる。

Unit Test:

- OpenAPI extraction。
- native operation parsing。
- schema ref resolution。
- status / exit code matching。
- missing operation lookup。

## 11. 実装メモ

- parser と catalog builder は分ける。
- YAML / JSON は専用 parser を使う。
- error を早期 return しすぎず、可能な限り diagnostics を集める。
- Operation Directory から system / component の artifact loader を呼ばない。

## 12. Catalog 構築順序

推奨する構築順序:

1. component directory を受け取る。
2. OpenAPI を読み、HTTP operation 候補を作る。
3. `operations.yaml` を読み、native operation 候補を作る。
4. operation ID 重複を検出する。
5. schema ref を registry に登録する。
6. lookup 可能な catalog を作る。
7. diagnostics を返す。

重複があっても、他の operation の diagnostics は可能な限り集める。

## 13. Lookup の失敗表現

lookup failure は例外ではなく diagnostics に変換しやすい結果として返す。

| failure | message に含める情報 |
|---|---|
| component missing | component 名、参照元 |
| operation missing | component 名、operation ID、参照元 |
| schema missing | schema ref、operation ID |
| status mismatch | status、operation ID、許容値 |
| exit code mismatch | exit code、operation ID、許容値 |

呼び出し側が user-facing message を作れるように、context を落とさない。

## 14. 完了条件

- OpenAPI と `operations.yaml` の両方を取り込める。
- `component + operation` lookup ができる。
- schema ref を解決できる。
- 重複 operation ID を error にできる。
- system / component から raw interface file を読まずに利用できる。
