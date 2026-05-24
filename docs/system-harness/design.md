# System Harness 基本設計

作成日: 2026-05-24
対象: Accay MVP
参照: `docs/architecture.md`, `docs/requirements.md`

## 1. この文書の位置づけ

この文書は、Accay の System Harness component の基本設計である。
System Harness は、system side の validation と desk-debug context source の材料選定を担当する。
system side は、業務シナリオがどの operation 列として流れるかを扱う。
component の受け入れケースや test-map には依存しない。
System Harness は判断主体ではない。
System Harness は、エージェントと人間が判断できるように、入力、参照整合性、schema validation、diagnostics、context source を安定して揃える。
この文書では、責務、非責務、validation 項目、Operation Directory 連携、diagnostics、desk-debug context source、処理 flow、failure mode、test strategy、実装 notes を固定する。
この文書では、Python の class 名、関数 signature、Markdown template、表示 design、JSON Schema library の具体 API、cache 内部形式は固定しない。

## 2. 設計方針

System Harness は system artifact を正本として読む。
system artifact は `scenario.feature`、`sequence.md`、`trace.yaml` である。
System Harness が component side から機械的に参照してよいものは、Operation Directory が提供する operation contract と schema 参照に限定する。
System Harness は component artifact loader を直接呼ばない。
System Harness は `acceptance-scope.yaml` を読まない。
System Harness は `test-map.yaml` を読まない。
System Harness は JUnit XML を読まない。
System Harness は trace の意味が業務的に正しいかを判定しない。
System Harness は、trace が機械的に読めるか、参照先が存在するか、payload が schema に合うか、operation contract と矛盾しないかを判定する。
desk-debug context pack では、system artifact を中心に材料を選ぶ。
component semantics は参考情報であり、system の正本ではない。

## 3. 用語

| 用語 | 意味 |
|---|---|
| system artifact | scenario、sequence、trace など system side の正本成果物 |
| scenario | E2E に近い業務シナリオを表す Gherkin file |
| sequence | component 間協調を説明する Markdown file |
| trace | 机上デバッグ用 YAML。期待される operation 列と input / output を表す |
| step | trace 内の 1 operation 呼び出し単位 |
| operation contract | Operation Directory が返す component + operation の契約情報 |
| schema registry | Operation Directory から参照される JSON Schema の解決単位 |
| diagnostic | validation や context source 選定中に得られた機械的な指摘 |
| context source | Output & Presentation に渡す context Markdown 生成用の構造化材料 |

## 4. 外部インターフェース

System Harness は CLI から呼び出される。
代表的な呼び出し元は `accay system validate`、`accay validate`、`accay system pack desk-debug --scenario <scenario>` である。
`accay system validate` では system validation のみを実行する。
`accay validate` では CLI orchestration の一部として system validation を実行する。
`accay system pack desk-debug` では desk-debug context source を組み立てる。
System Harness は表示文字列の最終整形を行わない。
System Harness は Markdown file の書き込みを直接担当しない。
System Harness は Output & Presentation に渡せる構造化結果を返す。

## 5. 入出力

System Harness の入力は、System Artifacts から受け取る system artifact model、Operation Directory、schema registry、CLI command options である。
system artifact model には、scenario id、scenario path、scenario content、sequence path、sequence content、trace path、trace parse result、parse error、missing artifact 情報を含める。
Operation Directory には、component の存在確認、`component + operation` の解決、operation kind、input schema ref、output schema ref、HTTP status codes、CLI exit codes、schema ref 解決を問い合わせる。
System Harness の出力は、system diagnostics、system validation summary、desk-debug context source、referenced operation list、referenced schema list である。
system diagnostics は validation 結果の表示、exit code 判定、report 生成に使う。
desk-debug context source は context Markdown 生成の材料であり、Markdown そのものではない。
referenced operation list は trace が参照した operation の一覧である。
referenced schema list は trace が参照した schema の一覧である。

## 6. 責務

System Harness の責務は以下である。
- system validation の本体処理を担う。
- `accay system validate` に必要な diagnostics を生成する。
- `accay validate` に含まれる system validation を担う。
- scenario、sequence、trace の対応関係を検証する。
- trace の YAML 構造を検証する。
- trace step の基本構造を検証する。
- trace step id の重複を検出する。
- trace が参照する component を Operation Directory へ問い合わせる。
- trace が参照する `component + operation` を Operation Directory へ問い合わせる。
- operation kind を operation contract から取得する。
- trace `input.schema_ref` と operation contract の input schema ref を照合する。
- trace `output.schema_ref` と operation contract の output schema ref を照合する。
- trace `input.value` を JSON Schema で検証する。
- trace `output.value` を JSON Schema で検証する。
- `kind: http` の status を operation contract と照合する。
- `kind: cli` の exit code を operation contract と照合する。
- observations の最低限チェックを行う。
- desk-debug context source の材料を選定する。
- context source 内で正本情報と参考情報を区別する。
- failure mode を diagnostics として表現する。

## 7. 非責務

System Harness の非責務は以下である。
- component acceptance case の状態判定。
- `acceptance-scope.yaml` の構文検証。
- `test-map.yaml` の構文検証。
- `test-map.yaml` と JUnit XML の照合。
- component regression result の解釈。
- JUnit XML の読み取り。
- component review context pack の生成。
- component の受け入れ可否判断。
- trace の意味が業務的に正しいかの最終判断。
- 仕様変更か不具合かの判定。
- trace 更新案の自動採用。
- schema file の自動生成。
- operation contract の自動修正。
- OpenAPI lint tool としての詳細検査。
- `oneOf` / `anyOf` の高度な意味解釈。
- HTTP security scheme の検証。
- CLI command の実行。
- function signature と実コードの照合。
- context Markdown の最終デザイン。
- PR コメント投稿。
- repository file の自動修正。

## 8. System validation の対象

system validation は、既存の system artifact に対して機械的に検証できる整合性を確認する。
対象は scenario の存在、sequence の存在、trace の存在、scenario と sequence と trace の対応、trace YAML の parse 可否、trace root structure、trace scenario reference、trace steps の存在である。
対象はさらに、trace step id の一意性、trace step の component reference、operation reference、input block、output block、observations block、schema ref の解決、payload の schema validation、operation kind 別の追加検証である。
system validation は sequence の Markdown 内容を深く解釈しない。
system validation は Gherkin の全構文を厳密に lint しない。
scenario と sequence は trace の理解補助として存在確認と対応確認を行う。
trace は system validation の中心である。

## 9. trace の期待構造

MVP では trace は YAML として読み取る。
trace は実行ログではなく、期待される意味の流れを表す specification である。
trace の step は `component + operation` で operation を参照する。
operation kind は trace ではなく operation contract 側に持つ。
trace では `request` / `response` ではなく `input` / `output` を使う。
schema ref は repository root からの相対 path とする。
System Harness は trace の unknown field を即 error にする必要はない。
ただし、MVP で意味を持つ field の型が不正な場合は error とする。
必須 field の欠落は error とする。
推奨 field の欠落は warning とする。

## 10. Operation Directory との相互作用

System Harness は、Operation Directory を system と component の唯一の機械的な接続点として使う。
System Harness は component directory を自分で探索しない。
System Harness は OpenAPI file を直接 parse しない。
System Harness は operations.yaml を直接 parse しない。
System Harness は schema file の存在確認を Operation Directory 経由で行う。
`component + operation` が解決できない場合、System Harness は error diagnostic を出す。
operation contract が解決できた場合、System Harness は kind 別の検証を行う。
operation contract の input schema ref と trace の `input.schema_ref` が違う場合、System Harness は error diagnostic を出す。
operation contract の output schema ref と trace の `output.schema_ref` が違う場合、System Harness は error diagnostic を出す。
schema ref が Operation Directory に登録されていない場合、System Harness は error diagnostic を出す。
schema ref の path が repository 外を指す場合、System Harness は error diagnostic を出す。
Operation Directory 自体の構築失敗は上位 orchestration の failure として扱う。
ただし、System Harness の処理中に lookup error が返った場合は diagnostic に変換する。

## 11. schema validation

schema validation は trace `input.value` と `output.value` に対して行う。
検証元は JSON Schema であり、JSON Schema は Operation Directory が解決する。
System Harness は schema ref の文字列一致だけでなく、実際の payload validation を行う。
`input.value` が schema に合わない場合は error とする。
`output.value` が schema に合わない場合は error とする。
schema 自体が parse できない場合は error とする。
schema が解決できない場合は error とする。
schema validation error には、trace file path、step id、`input` / `output` の区別、schema ref、validation path、error message を含める。
validation path は JSON Pointer 形式を優先する。
JSON Schema library が複数 error を返せる場合、System Harness は複数 diagnostics を返してよい。
同じ payload で error が多すぎる場合は上限を設けてよく、その場合は truncated warning を追加する。
MVP では schema の高度な意味論は扱わない。
`format` の厳密検証は JSON Schema library の設定に従う。
`oneOf` / `anyOf` / `allOf` は library が扱える範囲で検証し、高度な分岐解釈を Accay 独自に実装しない。

## 12. kind 別 validation

operation kind は Operation Directory から取得し、trace は kind を持たない。
`kind: http` では status code を検証する。
trace output に HTTP status がある場合、operation contract の status codes に含まれるか確認する。
status code が operation contract に存在しない場合は error とする。
MVP では headers、security scheme、server URL の完全検証は行わない。
`kind: cli` では exit code を検証する。
trace output に exit code がある場合、operation contract の exit codes に含まれるか確認する。
exit code が operation contract に存在しない場合は error とする。
MVP では command を実行しない。
MVP では stdout / stderr の完全一致検証は行わない。
stdout / stderr を検証したい場合は、正規化された output value の schema で扱う。
`kind: function` では input / output schema validation を主検証とする。
signature や errors は context source に含めてもよい。
MVP では実コード上の関数存在確認や呼び出し順序の静的解析を行わない。

## 13. observations の扱い

observations は、JSON Schema で表しにくい観測点や意味保存条件を書く場所である。
System Harness は observations の意味を判定しない。
System Harness は observations が空でないかを最低限確認する。
step に observations がない場合は warning とする。
observations が空 list の場合は warning とする。
observations の内容が曖昧かどうかは System Harness の判定対象ではない。
trace format が observations の型を固定した場合は、その型に従って error / warning を出す。

## 14. diagnostics model

diagnostic は、機械処理で見つかった指摘を表す。
diagnostic は、Output & Presentation が Markdown / HTML / console に整形できる構造にする。
diagnostic には、`code`、`severity`、`message`、`path`、`location`、`subject`、`details` を含める。
`code` は安定した識別子にする。
`severity` は `error`、`warning`、`info` を基本とする。
`message` は人間が読める短い説明にする。
`path` は repository root からの相対 path を基本とする。
`location` には YAML path や line / column を入れられる場合だけ入れる。
`subject` には scenario id、step id、component、operation などを入れる。
`details` には schema validation error や lookup result を入れる。
diagnostic は source file の修正を直接行わない。

## 15. diagnostics severity

severity の方針は以下である。

| severity | 意味 | exit code への影響 |
|---|---|---|
| `error` | 機械的な整合性が壊れている | non-zero |
| `warning` | 機械的には継続できるが注意が必要 | zero |
| `info` | 補足情報 | zero |

`error` は、scenario / sequence / trace missing、YAML parse error、trace structure error、step id 重複、component / operation 欠落、Operation Directory lookup failure、schema ref 不一致、schema validation failure、HTTP status mismatch、CLI exit code mismatch に使う。
`warning` は、observations 欠落、observations 空、sequence と trace の対応が曖昧、context source の参考情報欠落、schema validation error の省略に使う。
`info` は、参照 operation 数、参照 schema 数、context source に含めた files、optional な既存 trace がなかったことに使う。
`needs_review` は diagnostic severity ではなく summary status として扱う。
意味判断が必要な状態は、warning または info の diagnostic と summary status で表す。

## 16. validation summary

System Harness は diagnostics から summary を作る。

| status | 条件 |
|---|---|
| `fail` | error diagnostic が 1 件以上ある |
| `warning` | error はないが warning が 1 件以上ある |
| `pass` | error も warning もない |
| `needs_review` | 機械検証は通ったが意味確認が必要な文脈で明示する |

`accay system validate` の exit code は、summary status が `fail` の場合だけ non-zero とする。
`needs_review` は non-zero にしない。
`needs_review` は、人間またはエージェントの意味判断が必要であることを示す。

## 17. desk-debug context source の目的

desk-debug context source は、エージェントや人間が trace 草案または trace 更新案を作るための入力である。
context source は Markdown そのものではない。
context source は、Output & Presentation が context Markdown に整形するための構造化材料である。
System Harness は、どの file、どの operation contract、どの semantics excerpt を含めるべきかを選ぶ。
context source では、正本情報と参考情報を区別する。
正本情報は system artifact である。
参考情報は operation contract と component semantics である。
schema は payload を理解するための参考情報として含める。

## 18. desk-debug context source 選定

`accay system pack desk-debug --scenario <scenario>` では、指定 scenario を中心に source を選定する。
必ず含めるものは、対象 scenario、対象 sequence、既存 trace、trace が存在しない場合の expected path、関連 operation contract、関連 schema ref の一覧である。
条件付きで含めるものは、既存 trace が参照している component semantics の抜粋、sequence に明示された component の semantics の抜粋、operation description、function signature、CLI command 情報、HTTP method / path / status codes である。
含めないものは、component acceptance scope の全量、test-map の全量、JUnit XML、component regression result、unrelated scenario、unrelated trace、unrelated component semantics である。
context source は、対象 scenario の机上デバッグに必要な最小十分な材料にする。

source selection の優先順位は以下である。
1. CLI で指定された scenario。
2. 指定 scenario に対応する sequence。
3. 指定 scenario に対応する既存 trace。
4. 既存 traceの steps が参照する operation contract。
5. operation contract が参照する schema。
6. 既存 trace の steps が参照する component の semantics。
7. sequence から抽出できる component 名に対応する semantics。

既存 trace がない場合、System Harness は scenario と sequence を中心に context source を作る。
既存 trace がない場合、operation contract の自動選定は限定的でよい。
sequence から component 名を抽出できる場合は、関連 semantics と operation catalog を参考情報として含めてよい。
component 名抽出が不確実な場合は、warning ではなく info にする。
context source 選定の失敗は、必須 source が欠けた場合だけ error とする。
参考情報の欠落は warning とする。

context source は、`primary_sources`、`reference_sources`、`operation_contracts`、`schemas`、`semantics_excerpts`、`existing_trace_summary`、`diagnostics`、`selection_notes` を持つ構造を想定する。
`primary_sources` には scenario、sequence、trace を入れる。
`reference_sources` には semantics や operation contract の file path を入れる。
`operation_contracts` には component、operation、kind、schema refs、kind 別 metadata を入れる。
`schemas` には schema ref と schema path を入れる。
`semantics_excerpts` には component ごとの抜粋を入れる。
`existing_trace_summary` には step id と operation references の一覧を入れる。
`diagnostics` には context source 選定中の注意点を入れる。
`selection_notes` には、なぜ含めたか、なぜ除外したかを入れてよい。

## 19. 処理 flow: system validate

`accay system validate` の代表 flow は以下である。
1. CLI が repository root と config を解決する。
2. CLI が Operation Directory を構築する。
3. CLI が System Artifacts に system artifact discovery を依頼する。
4. CLI が System Harness に system artifact model と Operation Directory を渡す。
5. System Harness が scenario / sequence / trace の存在を検証する。
6. System Harness が trace YAML の parse result と root structure を確認する。
7. System Harness が step list と step id 重複を検証する。
8. System Harness が各 step の component / operation を Operation Directory へ問い合わせる。
9. System Harness が operation contract と trace schema refs を照合する。
10. System Harness が schema registry から JSON Schema を解決する。
11. System Harness が `input.value` と `output.value` を schema validation する。
12. System Harness が kind 別 metadata を検証する。
13. System Harness が observations を最低限検証する。
14. System Harness が diagnostics と summary を返す。
15. CLI が Output & Presentation に表示を依頼し、summary に基づいて exit code を決める。

System Harness は、可能な限り fail-fast しない。
1 つの trace に複数 error がある場合、できる範囲で複数 diagnostics を返す。
ただし、trace YAML が parse できない場合は step validation を継続しない。
Operation Directory が構築できていない場合は、lookup を伴う validation を継続しない。

## 20. 処理 flow: accay validate

`accay validate` では、system validation と component validation が同じ top-level command に含まれる。
System Harness の処理内容は `accay system validate` と同じである。
違いは orchestration の範囲である。
`accay validate` では、CLI が Operation Directory を一度構築し、system / component の両方に渡してよい。
System Harness は component validation の結果を読まない。
System Harness は component validation の失敗に応じて自分の結果を変えない。
Output & Presentation が system diagnostics と component diagnostics を並べて表示する。

## 21. 処理 flow: desk-debug pack

`accay system pack desk-debug --scenario <scenario>` の代表 flow は以下である。
1. CLI が repository root、config、指定 scenario id を解決する。
2. CLI が Operation Directory を構築する。
3. CLI が System Artifacts に対象 scenario / sequence / trace の読み取りを依頼する。
4. CLI が System Harness に artifact model と Operation Directory を渡す。
5. System Harness が必須 source の存在と既存 trace の有無を確認する。
6. 既存 trace がある場合、trace steps から operation references を抽出する。
7. System Harness が Operation Directory から operation contracts と schema refs を取得する。
8. System Harness が schema refs を schema registry で解決する。
9. System Harness が関連 component semantics の候補を選ぶ。
10. System Harness が正本 source と参考 source を分ける。
11. System Harness が context source を返す。
12. Output & Presentation が `.accay/runs/{run-id}/context.md` を生成する。

desk-debug pack は validation を兼ねてもよい。
ただし、context source 生成に必要な最低限の validation に限定する。
完全な validation は `accay system validate` の責務である。

## 22. failure modes

System Harness が想定する failure mode は以下である。

| failure | 代表 severity | 扱い |
|---|---|---|
| scenario missing | error | 対象 scenario を処理できない |
| sequence missing | error | system artifact の対応が崩れている |
| trace missing during validate | error | validation 対象が欠けている |
| trace missing during pack | info または warning | 新規 trace 作成文脈なら継続する |
| YAML parse error | error | step validation は中止する |
| invalid trace structure | error | 読める範囲で追加 diagnostics を出す |
| duplicate step id | error | step を一意に参照できない |
| component not found | error | operation lookup 不可 |
| operation not found | error | contract 不明 |
| schema ref mismatch | error | trace と contract が矛盾 |
| schema missing | error | payload validation 不可 |
| schema parse error | error | payload validation 不可 |
| input validation failure | error | trace payload が contract に不一致 |
| output validation failure | error | trace payload が contract に不一致 |
| HTTP status mismatch | error | contract にない status |
| CLI exit code mismatch | error | contract にない exit code |
| observations missing | warning | 意味確認の材料が不足 |
| semantics missing for context | warning | 参考情報が不足 |

failure mode は、できるだけ diagnostic code と 1 対 1 に近づける。
ただし、schema validation error は同じ code で複数 path を表してよい。

## 23. diagnostic code 案

MVP の diagnostic code は、安定性を優先して短い prefix を使う。
System Harness の prefix は `SYS` とする。
代表 code は `SYS001_SCENARIO_MISSING`、`SYS002_SEQUENCE_MISSING`、`SYS003_TRACE_MISSING`、`SYS004_TRACE_YAML_PARSE_ERROR`、`SYS005_TRACE_STRUCTURE_INVALID` である。
代表 code は続けて、`SYS006_STEP_ID_DUPLICATED`、`SYS007_STEP_COMPONENT_MISSING`、`SYS008_STEP_OPERATION_MISSING`、`SYS009_COMPONENT_NOT_FOUND`、`SYS010_OPERATION_NOT_FOUND` である。
schema 系 code は、`SYS011_INPUT_SCHEMA_REF_MISMATCH`、`SYS012_OUTPUT_SCHEMA_REF_MISMATCH`、`SYS013_SCHEMA_NOT_FOUND`、`SYS014_SCHEMA_PARSE_ERROR`、`SYS015_INPUT_SCHEMA_VALIDATION_FAILED`、`SYS016_OUTPUT_SCHEMA_VALIDATION_FAILED` である。
kind / context 系 code は、`SYS017_HTTP_STATUS_NOT_ALLOWED`、`SYS018_CLI_EXIT_CODE_NOT_ALLOWED`、`SYS019_OBSERVATIONS_MISSING`、`SYS020_CONTEXT_REFERENCE_MISSING` である。
code は表示文言より安定させる。
code は test の assertion に使えるようにする。

## 24. データ構造の目安

実装上は、`SystemValidationResult`、`TraceStepReference`、`DeskDebugContextSource` のような構造を持つと扱いやすい。
`SystemValidationResult` は diagnostics、summary、referenced operations、referenced schemas を持つ。
`TraceStepReference` は step id、component、operation、input schema ref、output schema ref を持つ。
`DeskDebugContextSource` は scenario source、sequence source、trace source、operation contracts、schemas、semantics excerpts、diagnostics を持つ。
これらは設計上の目安であり、実装の class 名を固定しない。
ただし、Output & Presentation に渡す境界では、辞書の形を安定させる。

## 25. 他 component との境界

System Artifacts は file discovery と基本的な読み取りを担当する。
System Harness は、System Artifacts が返した artifact model を検証する。
System Harness は repository を再帰探索しない。
System Harness は scenario id から file path を推測する処理を持たない。
System Harness は artifact model に欠落情報があれば diagnostic に変換する。
Output & Presentation は、diagnostics や context source を人間向けに整形する。
System Harness は terminal color、HTML、dashboard 表示、Markdown report の見た目を扱わない。
ただし、context source の section 名や diagnostics の field は、Output が安定して使える形にする。

## 26. cache / performance 方針

MVP では cache は必須ではない。
Operation Directory が schema や contract を cache する場合、System Harness はその実装を知らなくてよい。
System Harness 内で cache する場合は、1 command 実行中の in-memory cache に限定する。
repository をまたいだ永続 cache は System Harness の責務にしない。
schema validation の結果 cache は、MVP では不要である。
同じ schema ref を複数 step で使う場合、schema object の解決は再利用してよい。
Operation Directory lookup は、step ごとに呼んでもよい。
実装が簡単なら、trace 内の operation references を重複排除してから lookup してもよい。
diagnostics の順序は、file order と step order に合わせる。
並列処理は必須ではない。

## 27. safety 方針

System Harness は、trace や schema に書かれた command を実行しない。
System Harness は、schema ref が repository root 外を指す場合に error とする。
System Harness は network access を前提にしない。
外部 URL の schema ref は MVP では解決しない。
外部 URL schema が必要な場合は、後続フェーズで明示的に扱う。
context source には secret を含めないことが望ましい。
ただし、secret detection は MVP の System Harness の責務ではない。

## 28. test strategy

System Harness の test は、contract test と unit test を中心にする。
test は System Harness 単体の責務境界を守る。
Operation Directory は fake または fixture を使う。
component artifact loader を実 test で直接呼ばない。
Output & Presentation の見た目は System Harness test の対象にしない。

unit test では、missing scenario、missing sequence、missing trace、YAML parse error、invalid trace structure、duplicate step id、missing component field、missing operation field が error になることを確認する。
unit test では、Operation Directory lookup failure、schema ref mismatch、input schema validation failure、output schema validation failure、HTTP status mismatch、CLI exit code mismatch が error になることを確認する。
unit test では、observations missing が warning になること、diagnostics が step order で返ることを確認する。
contract test では、`accay system validate` が valid fixture で exit code 0 になり、invalid fixture で non-zero になることを確認する。
contract test では、diagnostics code、schema validation error の path、`accay validate` 内の system diagnostics が出力に含まれることを確認する。
context source test では、scenario、sequence、existing trace、operation contract、schema refs、関連 semantics が入ることを確認する。
context source test では、unrelated semantics、`acceptance-scope.yaml`、`test-map.yaml`、JUnit XML が入らないことを確認する。
context source test では、trace がない新規作成文脈でも context source を作れることを確認する。
fixture は小さく保ち、valid fixture は http、cli、function を最低 1 つずつ含める。
invalid fixture は failure mode ごとに分け、1 fixture に複数 failure を詰め込みすぎない。
schema validation failure は input と output を分けて持つ。
context source fixture は unrelated component を含めて除外を確認する。

## 29. implementation notes

実装では、validation の core logic と CLI 表示を分ける。
System Harness の public function は、入力 model を受け取り、result object を返す形を基本にする。
例外は programmer error や予期しない internal error に限定する。
利用者が直せる artifact error は diagnostic に変換する。
diagnostic code は enum または定数として管理する。
severity は文字列の直書きを避ける。
path は repository root からの相対 path に正規化する。
内部処理では absolute path を使ってもよいが、出力境界では repository 相対 path に戻す。
schema validation library の error object はそのまま外へ出さず、Accay diagnostic に変換する。
YAML line / column が取れる parser を使う場合は location に入れる。
line / column が取れない場合も diagnostic は出す。
trace step は読み取り順を保持する。
duplicate step id があっても、可能なら両方の location を details に入れる。
Operation Directory lookup は、失敗理由をできるだけ details に残す。
desk-debug context source は file content と metadata を分けて持つ。
large file の全量を含めるか抜粋にするかは Output 側で調整できるようにする。

## 30. 拡張余地

後続フェーズで追加しうるものは、`value_ref` による外部 JSON / YAML payload 参照、message / job / file / grpc / asyncapi operation kind、trace と sequence Mermaid の対応検証、Gherkin scenario のより厳密な lint である。
後続フェーズで追加しうるものは、semantics からの関連 operation 推定、context source の token budget 最適化、schema validation profile の設定、external schema registry、secret detection、web dashboard 向けの詳細 diagnostics である。
これらは System Harness の現在の責務を広げすぎない範囲で追加する。
component acceptance や regression の責務を System Harness に移さない。

## 31. 境界の最終確認

System Harness は system side の component である。
System Harness は system artifact を正本として読む。
System Harness は Operation Directory を通じて operation contract と schema を参照する。
System Harness は component acceptance artifact を直接読まない。
System Harness は JUnit XML を読まない。
System Harness は意味判断をしない。
System Harness は、機械的に確認できる整合性を diagnostics として返す。
System Harness は、desk-debug context source の材料を選ぶ。
System Harness は、Accay の「判断と機械処理を分ける」設計方針を守る。
