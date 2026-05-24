# Operation Directory 基本設計
作成日: 2026-05-24
対象: Accay MVP
領域: boundary
参照: [../architecture.md](../architecture.md), [../requirements.md](../requirements.md)
## 1. この文書の位置づけ
この文書は、Operation Directory の実装に必要な基本設計である。
Operation Directory は、system と component の唯一の機械的な接続点である。
ここで扱うのは、operation contract と schema registry の参照である。
意味判断、受け入れ判断、テスト証拠の妥当性判断は扱わない。
この文書では、boundary role、operation catalog、schema registry、OpenAPI handling、`operations.yaml` handling、duplicate detection、lookup API、diagnostics、caching、failure modes、test strategy、implementation notes を固定する。
Python の具体的なクラス名、parser library、diagnostics 表示テンプレート、永続 cache 形式、OpenAPI 全仕様対応は固定しない。
## 2. 設計ゴール
Operation Directory のゴールは、`component + operation` から契約情報を安定して引けるようにすることである。
system trace は component の内部成果物を直接読まない。
component validation も system trace を正本として要求しない。
両者が共有してよい機械的な境界は、Operation Directory が提供する operation contract だけである。
MVP では、読み取り対象を静的ファイルに限定する。
実行中のサーバ、実コード、テストランナー、外部 API には問い合わせない。
OpenAPI、`operations.yaml`、JSON Schema は、外部形式を内部の operation contract に写すための入力である。
## 3. 境界ロール
Operation Directory は `boundary` 領域のコンポーネントである。
`system` 領域から見ると、trace step の `component` と `operation` が存在するか確認するための参照先である。
`component` 領域から見ると、interfaces 配下の公開契約が構造化できるか確認するための参照先である。
`output` 領域から見ると、diagnostics を人間向けに表示するための入力である。
Operation Directory は system artifact loader に依存しない。
Operation Directory は component harness に依存しない。
Operation Directory は component regression に依存しない。
Operation Directory は output renderer に依存しない。
許可する依存は workspace helper、YAML / JSON parser、schema resolver、diagnostics model に限定する。
この境界により、system と component が互いの正本成果物を読み合わない設計を守る。
## 4. 責務
Operation Directory の責務は、component interfaces を operation contract として参照可能にすることである。
component 配下の `interfaces/*` を探索する。
`openapi.yaml` から HTTP operation を取り込む。
`operations.yaml` から Accay native operation を取り込む。
`schemas/*.schema.json` を schema registry に登録する。
operation の input / output schema reference を解決する。
同一 component 内の operation ID 重複を検出する。
`component + operation` の lookup API を提供する。
operation kind を返す。
HTTP status code の照合材料を返す。
CLI exit code の照合材料を返す。
参照不能な operation / schema を diagnostics として返す。
同一 run 中の読み取り結果を必要に応じて cache する。
## 5. 非責務
Operation Directory は意味判断をしない。
`semantics.md` の意味判断をしない。
`semantics.md` の生成をしない。
acceptance case の状態管理をしない。
`acceptance-scope.yaml` の承認状態判定をしない。
`test-map.yaml` の照合をしない。
JUnit XML の読み取りをしない。
trace の意味保存条件を判断しない。
OpenAPI lint 全般をしない。
OpenAPI 差分解析をしない。
security scheme の妥当性を検証しない。
server URL の到達確認をしない。
function の実コード存在確認をしない。
CLI command の実行可能性確認をしない。
operation の自動命名、merge、override をしない。
境界を越えそうな処理は、diagnostics に材料を出すだけに留める。
## 6. 入力ファイル
Operation Directory が読む入力は、component の `interfaces/` 配下に限定する。
標準配置は次の通りである。
```text
docs/acceptance/components/{component}/interfaces/
  openapi.yaml
  operations.yaml
  schemas/
    *.schema.json
```
すべての component がすべてのファイルを持つ必要はない。
HTTP API component は `openapi.yaml` だけで operation を表現できる。
非 HTTP component は `operations.yaml` を使う。
HTTP component でも OpenAPI がない場合は `operations.yaml` を使ってよい。
JSON Schema は `schemas/` 配下に置くことを標準とする。
schema reference は repository root からの相対 path も許容する。
MVP では remote URL の schema reference は扱わない。
## 7. 出力モデル
Operation Directory の主な出力は、operation catalog、schema registry、diagnostics である。
operation catalog は component ごとの operation contract 一覧である。
schema registry は schema reference から schema document を引く索引である。
diagnostics は読み取り、構造化、参照解決の問題を表す。
出力モデルは表示形式ではなく内部参照形式として設計する。
Markdown や HTML に整形する責務は Output & Presentation に残す。
System Harness と Component Harness は同じ catalog を参照してよい。
## 8. Operation catalog
operation catalog は、component 単位で operation を保持する。
MVP では、operation ID は同一 component 内で一意でなければならない。
異なる component 間では同じ operation ID を許容する。
lookup key は常に `component + operation` とする。
operation catalog の最小項目は以下である。
| 項目 | 内容 |
|---|---|
| `component` | component 名 |
| `operation_id` | component 内で一意な operation ID |
| `kind` | `http`, `cli`, `function` |
| `source` | `openapi` または `operations.yaml` |
| `source_path` | 元ファイルの path |
| `input.schema_ref` | input value の schema reference |
| `output.schema_ref` | output value の schema reference |
| `status_codes` | `http` の場合の許容 status code |
| `exit_codes` | `cli` の場合の許容 exit code |
| `metadata` | summary, method, path, command, signature など |
`metadata` は照合の必須材料ではない。
人間とエージェントが context pack で読むための補助情報として保持する。
## 9. Operation contract の正規化
OpenAPI と `operations.yaml` は入力形式が異なる。
Operation Directory は、読み取り後に共通の operation contract へ正規化する。
概念モデルは以下である。
```text
OperationContract
  component
  operation_id
  kind
  source
  source_path
  input_schema_ref
  output_schema_ref
  status_codes
  exit_codes
  metadata
```
`kind: http` の場合、`status_codes` を保持する。
`kind: cli` の場合、`exit_codes` を保持する。
`kind: function` の場合、`signature` や `errors` を `metadata` として保持する。
MVP では、`function` の error と schema validation の関係は解釈しない。
## 10. Schema registry
schema registry は、JSON Schema document を schema reference で引くための索引である。
schema registry は validation 実行そのものではない。
validation は System Harness または Component Harness が必要に応じて行う。
Operation Directory は、validation に必要な schema document と解決済み reference を提供する。
schema registry の最小項目は以下である。
| 項目 | 内容 |
|---|---|
| `schema_ref` | 利用者が参照する schema reference |
| `resolved_path` | repository root から解決した実ファイル path |
| `document` | parse 済み JSON Schema |
| `source_component` | 所属 component |
| `diagnostics` | 読み取り時の問題 |
schema reference は、repository root 相対、component `interfaces/` 相対、component `interfaces/schemas/` 相対の順で解決する。
同じ文字列の schema reference は同じ schema を指すものとして扱う。
異なる文字列が同じ実ファイルに解決される場合は alias として扱ってよい。
diagnostics では元の参照文字列を残す。
## 11. OpenAPI handling
OpenAPI は HTTP operation を Accay の operation contract に取り込む adapter として扱う。
MVP で読む項目は、`paths`、HTTP method、`operationId`、request body schema reference、response schema reference、response status code である。
`servers`、`security`、auth flow、examples、detailed description、tags の意味、parameter serialization の詳細、OpenAPI lint 全般は深く読まない。
`oneOf` / `anyOf` の高度な意味解釈も行わない。
`operationId` が存在しない HTTP operation は catalog に登録しない。
その場合は `openapi.missing_operation_id` を error として出す。
`operationId` を自動生成してはならない。
OpenAPI 由来の operation は `kind: http` とする。
`method` と `path` は `metadata` に保持する。
response status code は `status_codes` に保持する。
request / response schema がない場合も operation 自体は登録できる。
ただし、trace validation で schema が必要になる場合は、lookup 利用側で schema missing diagnostics を出せるようにする。
## 12. OpenAPI schema reference
OpenAPI 内の schema は、原則として `$ref` を取り込む。
外部 JSON Schema file への `$ref` を優先して扱う。
OpenAPI document 内の `#/components/schemas/...` 参照も許容する。
内部参照を使う場合は、`openapi.yaml#/components/schemas/Name` のような reference として扱う。
inline schema は MVP では限定対応とする。
inline schema を見つけた場合は、stable な synthetic ref を作って registry に登録するか、warning を出す。
実装初期は warning でよい。
operation 自体の取り込みは継続する。
remote `$ref` は `schema.remote_ref_unsupported` として warning にする。
## 13. OpenAPI response selection
OpenAPI の response は status code ごとに複数存在する。
Operation Directory は、status code の一覧を保持する。
output schema reference は成功系 response から選ぶ。
成功系 response は `2xx` status code を優先する。
複数の `2xx` response がある場合は、数値昇順で最初の schema を代表 output schema とする。
代表を選べない場合は、`output.schema_ref` を空にして warning を出す。
全 response schema の union 解釈は MVP では行わない。
失敗系 response の schema は、将来の拡張対象として metadata に残してもよい。
`default` response は明確な数値 status として扱わないが、metadata には残してよい。
## 14. operations.yaml handling
`operations.yaml` は Accay native の operation 定義である。
HTTP 以外の boundary を表現するために使う。
HTTP component でも OpenAPI を持たない場合は `operations.yaml` で定義してよい。
MVP で読む必須項目は、`component`、`operations.{operationId}.kind`、`operations.{operationId}.input.schema_ref`、`operations.{operationId}.output.schema_ref` である。
kind 別の追加項目は以下である。
| kind | 項目 | 扱い |
|---|---|---|
| `http` | `method`, `path`, `status_codes` | `status_codes` は照合材料 |
| `cli` | `command`, `exit_codes` | `exit_codes` は照合材料 |
| `function` | `signature`, `errors` | 参照情報 |
`operations.yaml` の top-level `component` は、配置 path の component 名と一致することを期待する。
一致しない場合は `operations.component_mismatch` を error とする。
読み取り処理は可能な範囲で継続し、他の問題もまとめて報告する。
## 15. operations.yaml の正規化
`operations.yaml` の `operations` map の key を operation ID として扱う。
operation body 内に別名の operation ID は持たない。
`kind` は必須である。
未知の `kind` は `operations.unknown_kind` とし、catalog には登録しない。
`input.schema_ref` と `output.schema_ref` は、trace の schema validation に使うための参照である。
missing の場合は error diagnostics とする。
実装初期では catalog に partial contract として保持してもよい。
partial contract を保持する場合は、lookup 結果に diagnostics を添える。
YAML parser が map key 重複を検出できない場合は、検出限界を test と diagnostics 方針に明記する。
## 16. Duplicate detection
duplicate detection は component 単位で行う。
同一 component 内では operation ID は一意でなければならない。
重複対象は、OpenAPI 内の `operationId` 同士、`operations.yaml` 内の operation key 同士、OpenAPI 由来 operation と `operations.yaml` 由来 operation である。
重複が見つかった operation は ambiguous として扱う。
ambiguous operation は lookup 成功にしてはならない。
diagnostics は `operation.duplicate_id` の error とする。
MVP では override、merge、namespace は持たない。
将来それらを追加する場合も、明示的な設定なしに自動解決してはならない。
duplicate diagnostics には component、operation、重複元の file path、可能なら line を含める。
line number が取れない parser を使う場合は、file path だけでもよい。
## 17. Lookup API expectations
Operation Directory は、利用者に対して小さな lookup API を提供する。
API は内部実装の関数でよく、公開 CLI API である必要はない。
期待する lookup は以下である。
| API | 期待動作 |
|---|---|
| `list_components()` | catalog に存在する component を返す |
| `list_operations(component)` | component の operation 一覧を返す |
| `lookup_operation(component, operation)` | operation contract を返す |
| `lookup_schema(schema_ref)` | schema document を返す |
| `resolve_schema_ref(component, schema_ref)` | component 文脈で schema ref を解決する |
| `diagnostics()` | load 中に発生した diagnostics を返す |
lookup は例外で通常制御しない。
不明 component、不明 operation、不明 schema は、結果オブジェクトと diagnostics で返す。
不正な引数などのプログラミングエラーは例外にしてよい。
## 18. lookup_operation の期待
`lookup_operation(component, operation)` は完全一致で検索する。
大文字小文字の補正はしない。
alias 解決はしない。
見つかった場合は、operation contract と関連 diagnostics を返す。
見つからない場合は、not found diagnostics を返す。
重複している場合は、duplicate diagnostics を返し、contract は返さない。
partial contract の場合は、contract と error diagnostics の両方を返してよい。
利用者は diagnostics の severity を見て処理続行可否を決める。
## 19. lookup_schema の期待
`lookup_schema(schema_ref)` は registry に登録済みの schema を検索する。
schema reference の正規化は loader 時点で行う。
lookup 時に file system を再探索しない。
見つかった場合は、schema document と resolved path を返す。
見つからない場合は、schema not found diagnostics を返す。
schema parse error がある場合は、document を返さず error diagnostics を返す。
JSON Schema として妥当かどうかの完全検証は validator 側の責務としてよい。
## 20. Diagnostics 方針
Operation Directory は、失敗をできるだけまとめて報告する。
最初のエラーで停止しすぎると、利用者が修正を繰り返す回数が増えるためである。
読み取り不能な file はその file の解析を停止する。
diagnostics は、機械処理しやすい code と人間が読める message を持つ。
severity は `error`, `warning`, `info` の 3 段階を基本とする。
`error` は、正しい lookup や validation を妨げる問題である。
`warning` は、MVP で深く扱わないが catalog の利用は継続できる問題である。
`info` は補助的な通知である。
code は安定させ、message は改善可能にする。
contract test は code と主要構造を固定する。
## 21. Diagnostics code
MVP で想定する diagnostics code は以下である。
| code | severity | 内容 |
|---|---|---|
| `interfaces.not_found` | warning | component に interfaces がない |
| `openapi.parse_error` | error | OpenAPI YAML を parse できない |
| `openapi.missing_operation_id` | error | HTTP operation に `operationId` がない |
| `openapi.unsupported_inline_schema` | warning | inline schema を完全には扱えない |
| `operations.parse_error` | error | `operations.yaml` を parse できない |
| `operations.component_mismatch` | error | path の component と YAML の component が違う |
| `operations.unknown_kind` | error | 未知の operation kind |
| `operation.duplicate_id` | error | operation ID が重複している |
| `operation.not_found` | error | lookup 対象 operation がない |
| `component.not_found` | error | lookup 対象 component がない |
| `schema.not_found` | error | schema reference を解決できない |
| `schema.parse_error` | error | JSON Schema file を parse できない |
| `schema.remote_ref_unsupported` | warning | remote `$ref` は MVP 対象外 |
## 22. Caching 方針
Operation Directory は、同一 run 中に同じ interface file を何度も読まないようにしてよい。
MVP の cache は in-memory を基本とする。
永続 cache は必須ではない。
永続 cache を導入する場合は `.accay/cache/` 以下に置く。
cache key には repository root、component name、source file path、file mtime、file size、Accay version を含める。
hash を使う場合は file content hash を使ってよい。
cache hit しても diagnostics は再利用できる必要がある。
古い diagnostics を隠してはならない。
cache は正しさより性能を優先してはならない。
実装が単純な間は、run ごとに全読み直しでよい。
## 23. Cache invalidation
mtime / size が変わった file は再読み取りする。
source file が削除された場合は cache entry を無効にする。
component 配下の `interfaces/` に新しい file が増えた場合は component cache を無効にする。
OpenAPI と `operations.yaml` の片方だけが変わった場合も、duplicate detection のため component 単位で再評価する。
schema file だけが変わった場合は、schema registry とそれを参照する diagnostics を再評価する。
永続 cache を入れる場合も、cache miss 時の挙動が正であることを contract test で守る。
## 24. Failure modes
Operation Directory は失敗を発見失敗、読み取り失敗、parse 失敗、構造失敗、参照失敗、重複失敗、未対応形式に分けて扱う。
interfaces path がない場合は warning とする。
file permission や broken symlink は error とする。
YAML / JSON の構文エラーは error とする。
必須項目 missing は error とする。
schema reference が解決できない場合は error とする。
duplicate operation ID は error とする。
remote ref や inline schema は、MVP では warning または error として明示する。
component 自体が存在しないかどうかは workspace / artifact discovery 側の責務である。
lookup 時に unknown component が渡された場合は `component.not_found` を返す。
## 25. 部分失敗時の継続
1 つの component の OpenAPI が壊れていても、他 component の読み取りは継続する。
1 つの operation が壊れていても、同じ component の他 operation は可能な限り登録する。
duplicate operation は ambiguous になるため、該当 operation の lookup は失敗扱いにする。
schema parse error があっても、operation catalog の登録は継続してよい。
その場合、schema lookup で error diagnostics を返す。
この方針により、`accay validate` は一度の実行で複数の修正点を提示できる。
## 26. System Harness からの利用
System Harness は trace step の検証で Operation Directory を使う。
trace の `component` が catalog にあるか確認する。
trace の `operation` が component 内にあるか確認する。
trace の `input.schema_ref` が operation contract と矛盾しないか確認する。
trace の `output.schema_ref` が operation contract と矛盾しないか確認する。
trace の `input.value` validation 用 schema を取得する。
trace の `output.value` validation 用 schema を取得する。
HTTP status が許容 status code に含まれるか確認する。
CLI exit code が許容 exit code に含まれるか確認する。
Operation Directory は、trace の意味が正しいかは判断しない。
## 27. Component Harness からの利用
Component Harness は component interfaces の整合性確認で Operation Directory を使う。
component interfaces が読み取れるか確認する。
`operations.yaml` の component 名が path と一致するか確認する。
operation ID 重複を確認する。
input / output schema reference が存在するか確認する。
review context pack に operation contract を含める。
`acceptance-scope.yaml` や `test-map.yaml` の整合性判断は Component Harness 側に残す。
Operation Directory は interfaces 由来の材料だけを返す。
## 28. OpenAPI と operations.yaml の併用
同一 component で OpenAPI と `operations.yaml` を併用してよい。
両方から operation を読み取り、同じ catalog に登録する。
HTTP operation は OpenAPI に置く。
CLI operation は `operations.yaml` に置く。
function operation は `operations.yaml` に置く。
OpenAPI では表しにくい補助 operation も `operations.yaml` に置ける。
ただし、同じ operation ID を両方に置くことは許容しない。
MVP では、OpenAPI の operation を `operations.yaml` で補足する merge 形式は持たない。
補足情報は `semantics.md` に書く。
## 29. Status code handling
HTTP status code は照合材料である。
OpenAPI 由来の場合は response key から status code を取り込む。
`default` response は数値 status として扱わない。
`operations.yaml` 由来の場合は `status_codes.success` と `status_codes.failure` を読み取る。
内部表現では success / failure の区分を保持してもよい。
trace validation では、少なくとも全許容 status code の集合に含まれるかを確認できればよい。
status code の業務的意味は `semantics.md` の領域である。
## 30. Exit code handling
CLI exit code は照合材料である。
Operation Directory は `operations.yaml` の `exit_codes` を読み取る。
内部表現では success / failure の区分を保持してよい。
trace validation では、出力に含まれる exit code が許容集合に含まれるか確認できればよい。
CLI の stdout / stderr / file output は、schema 化された output value として扱う。
実際に command を実行して exit code を確認することはしない。
## 31. Function handling
`kind: function` は、モノリス内や処理系内の公開 API を表す。
Operation Directory は、`signature` と `errors` を参照情報として保持する。
実コードの存在確認はしない。
言語別静的解析もしない。
function の input / output は JSON Schema で表現された value として扱う。
副作用、トランザクション境界、呼び出し順序などは `semantics.md` に書く。
## 32. Schema validation との関係
Operation Directory は schema validation の実行主体ではない。
schema document と reference 解決を提供するだけである。
System Harness は trace の `input.value` と `output.value` を schema に対して検証する。
Component Harness は interfaces の参照整合性を確認する。
JSON Schema で表しにくい意味は、schema validation の結果だけで判断しない。
その判断は人間とエージェントに残す。
## 33. 実装パッケージの目安
architecture では `operations` package が Operation Directory に相当する。
実装上の目安は以下である。
```text
src/accay/operations/
  __init__.py
  directory.py
  models.py
  openapi.py
  operations_yaml.py
  schemas.py
  diagnostics.py
```
`directory.py` は orchestration を担当する。
`openapi.py` は OpenAPI adapter を担当する。
`operations_yaml.py` は Accay native format の parser を担当する。
`schemas.py` は schema registry と reference 解決を担当する。
`models.py` は operation contract の内部モデルを担当する。
`diagnostics.py` は code と severity の定義を担当する。
## 34. 実装フロー
Operation Directory の構築フローは以下である。
1. workspace から対象 component 一覧を受け取る
2. component ごとの `interfaces/` path を解決する
3. `schemas/*.schema.json` を schema registry に登録する
4. `openapi.yaml` があれば HTTP operation を読み取る
5. `operations.yaml` があれば native operation を読み取る
6. operation contract を component catalog に追加する
7. component 内 duplicate detection を実行する
8. operation の schema reference を解決する
9. diagnostics をまとめる
10. lookup API を利用可能にする
schema registry の登録と operation 読み取りの順序は入れ替えてもよい。
ただし、最終的に schema reference diagnostics が出せる必要がある。
## 35. Path handling
path は repository root を基準に正規化する。
diagnostics では利用者がファイルを見つけやすい path を表示する。
内部的には absolute path を使ってもよい。
生成 report や golden file では repository root からの相対 path を優先する。
symbolic link は通常の file として読んでよい。
循環 symlink や repository 外への参照は、workspace policy に従って error にしてよい。
remote URL は MVP では読み取らない。
## 36. Security / safety
Operation Directory は入力ファイルを読むだけである。
入力に書かれた command、URL、function signature を実行してはならない。
OpenAPI の server URL に接続してはならない。
CLI command の存在確認として shell を起動してはならない。
JSON Schema の remote `$ref` を自動取得してはならない。
この制限により、CI とローカルで同じ静的結果を得やすくする。
## 37. Test strategy
Operation Directory のテストは、unit test と contract test の両方で持つ。
unit test は parser、resolver、duplicate detection を小さく確認する。
contract test は fixture repository を使い、CLI から見える diagnostics と lookup 結果を確認する。
golden file 比較は、diagnostics code と主要構造に限定する。
message の細かい日本語文言に過度に依存しない。
## 38. Unit test 観点
unit test では以下を確認する。
OpenAPI の `operationId` を catalog に取り込める。
OpenAPI の method / path / status code を保持できる。
OpenAPI の request / response schema ref を取り込める。
`operations.yaml` の `http` / `cli` / `function` operation を取り込める。
unknown kind を error にできる。
component mismatch を error にできる。
schema ref を repository root、interfaces、schemas directory から解決できる。
missing schema を diagnostics にできる。
duplicate operation ID を error にできる。
duplicate operation の lookup を失敗扱いにできる。
lookup not found を diagnostics にできる。
## 39. Contract test 観点
contract test では、Accay の利用者から見える振る舞いを固定する。
fixture repository に複数 component を置く。
fixture は `openapi-only`、`operations-only`、`mixed-interfaces`、`duplicate-operation`、`missing-schema`、`broken-yaml` を用意する。
CLI exit code も確認する。
error diagnostics がある場合、validate 系 command は失敗 exit code にする。
warning だけの場合は成功 exit code にしてよい。
diagnostics code は golden file または snapshot で固定する。
## 40. Probe test 観点
Probe test は、OpenAPI edge case の観察に使う。
inline schema、`oneOf` / `anyOf`、`default` response、path parameter schema、multipart request、nullable などを扱う。
Probe test は CI の必須条件にしない。
実装判断が固まったものだけ unit / contract test に昇格する。
## 41. MVP 実装順序
MVP の実装順序は以下を推奨する。
1. `operations.yaml` parser と model を作る
2. schema registry の path 解決を作る
3. lookup API を作る
4. duplicate detection を作る
5. OpenAPI adapter を作る
6. diagnostics code を contract test で固定する
7. System Harness の trace validation と接続する
8. Component Harness の interfaces validation と接続する
先に `operations.yaml` を実装すると、HTTP 以外の kind を含む Accay の抽象を確認しやすい。
OpenAPI adapter は後から同じ model に載せる。
## 42. 実装上の注意点
parser は入力形式ごとに分ける。
OpenAPI の都合を operation model に漏らしすぎない。
diagnostics は parser 内で作ってもよいが、code は中央で定義する。
lookup API は read-only にする。
catalog 構築後に利用者が operation を追加変更できる必要はない。
テストでは path の違いで失敗しないよう、repository root 相対 path を期待値に使う。
エラーがある catalog でも、取得可能な diagnostics を落とさない。
partial contract を許す場合は、その扱いを lookup result の型で明示する。
## 43. 将来拡張
MVP 後の拡張候補は、AsyncAPI adapter、gRPC / Protobuf adapter、Smithy adapter、OpenAPI 差分解析、operation contract の影響 scenario 推定、`message` / `job` / `file` kind、remote schema reference の opt-in 対応、inline schema の安定的な synthetic ref、component 間 shared schema registry、cache の永続化である。
これらを追加する場合も、Operation Directory の役割は参照境界に留める。
意味判断や受け入れ判断を追加してはならない。
## 44. 完了条件
Operation Directory の MVP は、OpenAPI から `kind: http` operation を読み取れることを満たす。
`operations.yaml` から `http` / `cli` / `function` operation を読み取れることを満たす。
JSON Schema reference を解決できることを満たす。
`component + operation` lookup ができることを満たす。
同一 component 内の duplicate operation ID を error にできることを満たす。
unknown operation を diagnostics にできることを満たす。
missing schema を diagnostics にできることを満たす。
HTTP status code の照合材料を提供できることを満たす。
CLI exit code の照合材料を提供できることを満たす。
System Harness と Component Harness が同じ catalog を参照できることを満たす。
unit test と contract test で主要ケースを固定できることを満たす。
以上を満たせば、Operation Directory は Accay MVP の boundary として十分に機能する。
