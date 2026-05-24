# Output & Presentation 基本設計
## 1. 目的
Output & Presentation は、Accay の shared component として表示と生成物出力を担当する。
対象は diagnostics、context source、regression result、生成済み report である。
人間、CI、エージェントが同じ結果を読み取れるように、CLI summary、Markdown、HTML、local dashboard へ整形する。
この component は validation / regression / review の判断主体ではない。
意味判断と最終受け入れ判断は、人間とエージェントに残す。
## 2. 位置づけ
Output & Presentation は `src/accay/output/` に置く想定の component である。
許可される依存方向は次の通りである。
```text
cli -> output
system -> output
component -> output
```
Output から system artifact loader や component artifact loader へ依存しない。
Output は `Operation Directory` を直接構築しない。
Output は `acceptance-scope.yaml`、`test-map.yaml`、`trace.yaml`、`semantics.md` を正本として直接読まない。
必要な情報は System Harness、Component Harness、Component Regression、CLI から構造化済み入力として受け取る。
Output は表示用の集約を行ってよい。
ただし、集約は入力済みデータの並べ替え、件数集計、リンク生成、フォーマット変換に限定する。
## 3. 責務
- diagnostics summary を CLI 表示用に整形する。
- diagnostics を Markdown / HTML report に整形する。
- desk-debug context を Markdown として出力する。
- acceptance review context を Markdown として出力する。
- regression report を Markdown / HTML として出力する。
- generated report を `accay serve` で表示する。
- `.accay/runs/{run-id}/` への run artifact 出力を管理する。
- `.accay/reports/` への report 出力を管理する。
- run-id、出力パス、生成時刻などの表示メタ情報を付与する。
## 4. 非責務
- system / component の正本ファイルを直接読んで判断すること。
- validation の診断ロジック。
- regression の JUnit 照合ロジック。
- acceptance case の状態更新。
- `test-map.yaml` や `acceptance-scope.yaml` の自動更新。
- review decision の決定。
- `decision.yaml` の意味的妥当性判定。
- test-map の承認 UI。
- proposal の適用 UI。
- dashboard 上での正本編集。
- OpenAPI、operations.yaml、JSON Schema、JUnit XML の直接解析。
- エージェント実行。
- PR コメント投稿。
## 5. no decision logic rule
Output には decision logic を置かない。
decision logic とは、入力成果物や回帰結果から、受け入れ可否、仕様変更かバグか、責務境界違反かを決める処理である。
Output が行ってよいのは presentation logic である。
presentation logic には次を含める。
- severity ごとの並べ替え。
- status ごとの件数集計。
- component ごとの grouping。
- case ごとの report section 生成。
- Markdown / HTML escaping。
- 相対リンク生成。
- 空状態の表示。
- exit code に応じた summary 文言の選択。
Output が行ってはいけない処理は次の通りである。
- `accepted` case の失敗を fail とみなすか warning とみなすかを決める。
- JUnit testcase と test-map entry の対応を推測する。
- missing test を許容してよいかを決める。
- schema validation error の原因を業務的に解釈する。
- `needs_review` を自動で `pass` に変える。
- warning を隠すかどうかを独自判断する。
- component の責務境界違反を推論する。
- 正本ファイルの不備を補完して成功扱いにする。
判定済み status、severity、exit code hint は harness / regression / CLI から渡される。
Output はそれを忠実に表示する。
## 6. module 構成
推奨構成は次の通りである。
```text
src/accay/output/
  __init__.py
  diagnostics.py
  context.py
  reports.py
  server.py
  paths.py
  templates.py
```
`diagnostics.py` は CLI summary と diagnostics report の整形を担当する。
`context.py` は context source を `context.md` として書き出す。
`reports.py` は validation result と regression result を Markdown / HTML report に変換する。
`server.py` は生成済み HTML report を閲覧する local viewer を提供する。
`paths.py` は output directory、run-id、report filename の組み立てを扱う。
`templates.py` は Markdown / HTML の共通テンプレート補助を扱う。
細かい file 分割は実装時に変更してよい。
ただし、artifact loader や regression matcher を output package に移動しない。
## 7. 入力データ contract
Output は構造化済みの plain data を入力として受け取る。
入力は dataclass、TypedDict、Pydantic model、dict のいずれでもよい。
実装形式は固定しないが、意味的な contract は固定する。
### 7.1 Diagnostic contract
diagnostic は validation 系 harness から渡される。
最小フィールドは次の通りである。
```yaml
id: ACCAY-DIAG-001
severity: error
message: trace step references unknown operation
source: system
component: order-domain
scenario: checkout
path: docs/acceptance/traces/checkout.trace.yaml
location:
  line: 42
  column: 7
hint: define operation in interfaces/operations.yaml
```
`id` は stable な診断種別または個別診断 ID である。
`severity` は `error`、`warning`、`info` を基本とする。
`message` は CLI と Markdown の主文として使う。
`source` は `system`、`component`、`operations`、`workspace` などの発生領域を表す。
`component`、`scenario`、`path`、`location`、`hint` は任意である。
Output は `severity` を再計算しない。
未知フィールドは details として表示してもよい。
### 7.2 Context source contract
context source は pack 系 harness から渡される。
desk-debug context と review context は同じ writer で扱える。
最小フィールドは次の通りである。
```yaml
kind: component-review
title: Review context for order-domain ORD-001
run_id: 2026-05-24T120000Z-order-domain-ORD-001
subject:
  component: order-domain
  case_id: ORD-001
sections:
  - title: Acceptance case
    body: markdown text
metadata:
  generated_by: accay component pack review
  generated_at: 2026-05-24T12:00:00Z
```
`kind` は `system-desk-debug` または `component-review` を基本とする。
`sections` の順序は harness が決める。
Output は section の順序を変えない。
Output は Markdown escaping と見出し階層の調整だけを行う。
### 7.3 Regression result contract
regression result は Component Regression から渡される。
最小フィールドは次の通りである。
```yaml
run_id: 2026-05-24T120000Z-regression
summary:
  components: 2
  cases: 14
  passed: 11
  failed: 1
  error: 0
  missing: 1
  skipped: 1
  unmapped: 3
components:
  - component: order-domain
    cases:
      - case_id: ORD-001
        title: Create order
        acceptance_status: accepted
        regression_status: fail
        tests:
          - classname: tests.acceptance.order.test_create_order
            name: test_create_order_success
            status: failed
            message: assertion failed
```
`regression_status` は regression component が決めた結果である。
Output は status を変更しない。
Output は `summary` が渡された場合、それを正として表示する。
表示用の再集計が `summary` と矛盾する場合は、内部エラーとして扱い、silent に補正しない。
### 7.4 Report metadata contract
report metadata は CLI または caller が付与する。
```yaml
run_id: 2026-05-24T120000Z-regression
command: accay regression --junit reports/python-junit.xml
generated_at: 2026-05-24T12:00:00Z
workspace_root: /repo
output_paths:
  markdown: .accay/reports/markdown/regression-2026-05-24T120000Z.md
  html: .accay/reports/html/regression-2026-05-24T120000Z.html
```
`workspace_root` は report に絶対パスとして出しすぎない。
CLI 表示では相対パスへ変換する。
HTML ではユーザー環境の絶対パス露出を避ける。
## 8. 出力先
Output は `.accay/` 以下の生成物を扱う。
標準の配置は次の通りである。
```text
.accay/
  runs/
    {run-id}/
      context.md
      desk-debug-report.md
      review-report.md
      decision.yaml
      proposed/
        test-map.yaml
        acceptance-scope.yaml
  reports/
    html/
      index.html
      regression-{run-id}.html
      validation-{run-id}.html
    markdown/
      regression-{run-id}.md
      validation-{run-id}.md
```
Output が主に作るのは `context.md` と `reports/html`、`reports/markdown` である。
`decision.yaml` と `proposed/` は同じ run directory に置かれるが、Output が判断して生成するものではない。
review-report を render する場合も、内容の判定は caller から渡された report source に従う。
## 9. run-id handling
run-id は一回の pack、validation、regression、review run を識別する文字列である。
run-id は CLI が決定して Output に渡すことを基本とする。
Output は run-id が渡されない場合に限り、補助的に生成してよい。
推奨形式は次の通りである。
```text
{utc-timestamp}-{scope}
{utc-timestamp}-{component}-{case-id}
{utc-timestamp}-regression
```
例。
```text
2026-05-24T120000Z-order-domain-ORD-001
2026-05-24T120000Z-checkout
2026-05-24T120000Z-regression
```
run-id に使える文字は、英数字、hyphen、underscore、dot に制限する。
path separator、空白、制御文字は許可しない。
不正な run-id が渡された場合、Output は出力前にエラーを返す。
不正な run-id を別の値へ silent に変換しない。
同じ run-id の directory がすでに存在する場合の扱いは CLI option に従う。
MVP の推奨 default は上書きしないことである。
`--overwrite` 相当が明示された場合だけ既存生成物を置き換える。
Output は上書き可否を判断せず、caller から渡された write policy に従う。
## 10. CLI summaries
CLI summary は、人間と CI log が短時間で状況を把握するための出力である。
長い report の代替ではなく、次の行動に必要な要約を示す。
`accay validate` 系の summary は、対象範囲、error / warning / info 件数、代表的な error、report path、exit code に対応する結果文言を含める。
`pack` 系の summary は、context 種別、対象 scenario または component / case、run-id、`context.md` の相対パスを含める。
`regression` 系の summary は、対象 component 数、case 数、pass / fail / error / missing / skipped / unmapped 件数、accepted case の問題件数、report path を含める。
`serve` の summary は、bind host、port、dashboard URL、report directory、watch mode の有無を含める。
例。
```text
Accay regression: failed
components: 3
cases: 18
results: 14 passed, 1 failed, 0 error, 2 missing, 1 skipped, 4 unmapped
accepted problems: 4
reports:
  markdown: .accay/reports/markdown/regression-2026-05-24T120000Z.md
  html: .accay/reports/html/regression-2026-05-24T120000Z.html
```
## 11. diagnostics formatting
diagnostics の表示は severity を最優先にする。
推奨順序は `error`、`warning`、`info` である。
同一 severity 内では `source`、`component`、`path`、`location`、`id` の順で安定ソートする。
CLI では冗長な本文を省略し、詳細は Markdown report に逃がす。
Markdown report では全 diagnostic を表示する。
HTML report では severity filter と component filter を提供してよい。
未知 severity は `unknown` として明示する。
diagnostic message は caller の文言を保持する。
Output が message を短縮する場合、詳細 report に完全版を残す。
file path は workspace root からの相対パスで表示する。
line / column がある場合は `path:line:column` 形式で表示する。
hint がある場合は message と分けて表示する。
同じ diagnostic が複数渡された場合、Output は勝手に重複排除しない。
重複排除が必要なら harness 側で行う。
## 12. context.md writing
`context.md` はエージェントと人間が次の作業に使う Markdown context pack である。
Output は context source を `.accay/runs/{run-id}/context.md` に書き出す。
書き出し前に run directory を作成する。
親 directory は `.accay/runs/` に限定する。
推奨構成は次の通りである。
```markdown
# {title}
## Metadata
| key | value |
|---|---|
| kind | component-review |
| run-id | 2026-05-24T120000Z-order-domain-ORD-001 |
## Subject
## Context
## Diagnostics
## Instructions for agent
```
section の内容は harness が選ぶ。
Output は section を空にしない。
空 section が渡された場合は、空であることが分かる短い表示を入れる。
`context.md` は UTF-8 と LF で書く。
front matter は必須にしない。
Markdown の見出し階層は `#` から始め、渡された section は `##` 以下に正規化する。
コードブロックは閉じ忘れがないように escaping する。
Output は context source に含まれる file excerpt を改変しない。
Markdown として壊れる場合は fenced code block に包む。
## 13. report rendering
report rendering は Markdown と HTML の二系統を持つ。
Markdown はエージェント、CI log、差分レビュー向けである。
HTML は人間がブラウザで状況を俯瞰するための report である。
Markdown report は plain text として読めることを優先する。
validation report は `Summary`、`Diagnostics by Severity`、`Diagnostics by Component`、`All Diagnostics`、`Generated Files` を含める。
regression report は `Summary`、`Accepted Case Problems`、`Components`、`Unmapped Tests`、`Raw Inputs` を含める。
Markdown report には、HTML でしか見えない情報を作らない。
HTML と Markdown は同じ入力 source から生成する。
HTML report は静的ファイルとして生成できることを基本とする。
JavaScript は使ってよいが、MVP では必須にしない。
外部 CDN に依存しない。
CSS は report 内に inline するか、`.accay/reports/html/assets/` に置く。
HTML report では summary cards、severity 別 diagnostics、component 別 regression status、accepted case problems、missing / skipped / failed tests、unmapped tests、generated-at、run-id を表示する。
status color を使ってよいが、色だけに依存しない。
status text と件数を必ず表示する。
`.accay/reports/html/index.html` は生成済み report の入口である。
index は report type、run-id、generated-at、command、status、Markdown link、HTML link を表示する。
## 14. dashboard / serve behavior
`accay serve` は生成済み report を見るための薄い viewer である。
MVP では正本編集機能、proposal apply 機能、test-map 承認 UI を持たない。
server は `.accay/reports/html` を document root として扱う。
`index.html` が存在する場合はそれを返す。
`index.html` が存在しない場合は、report directory を走査して簡易 index を返してよい。
serve 起動時に validation や regression を自動実行しない。
serve 起動時に正本成果物を読んで dashboard を再計算しない。
watch mode を後続で追加する場合も、再生成は CLI orchestration 経由にする。
default bind は `127.0.0.1` とする。
port 使用中の場合は、CLI が別 port を選ぶか、エラーを返す。
server は directory traversal を防ぐ。
`.accay/reports/html` の外側の file を返さない。
MVP の dashboard は local-only を前提とする。
remote 公開、認証、multi-user 操作は扱わない。
## 15. output directory handling
Output は directory 作成を idempotent に行う。
既存 directory があることを正常系として扱う。
既存 file の上書きは write policy に従う。
write policy は `create-only`、`overwrite`、`append-index` を想定する。
`create-only` は既存 file がある場合に失敗する。
`overwrite` は対象 file を置き換える。
`append-index` は report 本体を作成し、index だけを追記または再生成する。
path は workspace root から解決する。
出力先が workspace 内の `.accay/` 配下であることを確認する。
symlink の扱いは安全側に倒す。
`.accay/` 外へ抜ける symlink を追わない。
一時 file へ書いて rename する実装を推奨する。
atomic rename が使えない環境では、失敗時に明示的な error を返す。
## 16. data flow
validation の data flow は次の通りである。
```text
CLI -> System Harness / Component Harness -> diagnostics -> Output -> CLI stdout
```
pack の data flow は次の通りである。
```text
CLI -> System Harness / Component Harness -> context source -> Output -> .accay/runs/{run-id}/context.md
```
regression の data flow は次の通りである。
```text
CLI -> Component Regression -> regression result -> Output -> .accay/reports/markdown/ and .accay/reports/html/
```
serve の data flow は次の通りである。
```text
CLI -> Output.serve_reports -> generated HTML reports -> browser
```
どの flow でも Output は正本 artifact を探しに行かない。
## 17. failure modes
| 失敗 | 扱い |
|---|---|
| run-id が不正 | 出力せず error を返す |
| 出力先が `.accay/` 外 | 出力せず error を返す |
| 既存 file があり create-only | conflict error を返す |
| directory 作成失敗 | error を返す |
| file 書き込み失敗 | error を返す |
| template rendering 失敗 | error を返す |
| unknown severity | `unknown` として表示する |
| malformed context source | 出力せず error を返す |
| summary と detail 件数が矛盾 | error を返す |
| HTML index 更新失敗 | report 本体 path と warning を返す |
| serve 対象 directory 不在 | 空 dashboard または error を返す |
| port bind 失敗 | server を起動せず error を返す |
Output の失敗は、validation / regression の結果そのものとは分けて扱う。
regression が pass でも report 書き込みに失敗した場合、CLI は出力失敗として非ゼロ終了してよい。
Output は失敗時にも原因、対象 path、復旧 hint を返す。
機密情報を含む絶対パスや環境変数を不用意に表示しない。
## 18. security and robustness
HTML では message、path、test name、component name を escape する。
Markdown でも code fence 破壊を避ける。
run-id から path traversal できないようにする。
serve では request path を正規化し、document root 外を返さない。
binary file を report として返さない。
大きな JUnit failure message は CLI summary では省略する。
Markdown / HTML report では折りたたみ、details、または code block として表示する。
非常に大きな report でも、生成時に全体を過剰に複製しない実装を推奨する。
## 19. configuration
Output は `.accay/config.yaml` の report 設定を CLI 経由で受け取る。
Output 自身が config file を直接読む必要はない。
関連する設定は次の通りである。
```yaml
reports:
  html_dir: .accay/reports/html
  markdown_dir: .accay/reports/markdown
language:
  reports: ja
```
`reports.html_dir` は HTML report と dashboard index の出力先である。
`reports.markdown_dir` は Markdown report の出力先である。
`language.reports` は report の固定文言を選ぶために使ってよい。
MVP では日本語 report を基本とする。
## 20. test strategy
Output の test は公開挙動を中心に置く。
Contract Test では CLI 経由で次を確認する。
- validate summary が diagnostics 件数を表示する。
- validation Markdown / HTML report が生成される。
- component review pack で `context.md` が指定 run directory に生成される。
- system desk-debug pack で `context.md` が指定 run directory に生成される。
- regression で Markdown / HTML report が生成される。
- `accay serve` が generated report を返す。
- 出力 path が `.accay/` 配下に収まる。
- 不正 run-id が拒否される。
Unit Test では次を確認する。
- severity sort が安定している。
- path 表示が workspace relative になる。
- Markdown escaping が code fence を壊さない。
- HTML escaping が script injection を防ぐ。
- report filename が run-id から決定できる。
- write policy が create-only / overwrite を区別する。
- summary と detail の矛盾を検出できる。
Golden Test では `context.md`、validation Markdown report、regression Markdown report、HTML report の主要構造を確認する。
golden file では timestamp、run-id、絶対パスの揺れを正規化する。
見た目の細部ではなく、section、件数、status、path の存在を重視する。
serve の test では、一時 directory に report を作り、HTTP response の status と主要 HTML を確認する。
## 21. implementation notes
Output の public API は、CLI から使いやすい関数単位で始めてよい。
例。
```python
render_diagnostics_summary(result, options) -> str
write_context(context_source, output_options) -> WrittenFile
render_regression_reports(result, output_options) -> ReportPaths
serve_reports(server_options) -> ServerHandle
```
`options` には workspace root、run-id、output directories、write policy、language を含める。
文字列 rendering と file writing は unit test しやすいように分離する。
template engine は必須ではない。
MVP では f-string や小さな helper で十分である。
HTML escape と Markdown code block 処理は helper に寄せる。
report の layout は後で変わり得るため、内部型を過度に公開契約化しない。
CLI から見える契約は、生成 path、summary text、exit code との関係で固定する。
JSON 出力を追加する場合も、判定ロジックは追加しない。
## 22. MVP acceptance criteria
- diagnostics を severity ごとに CLI 表示できる。
- diagnostics の Markdown / HTML report を生成できる。
- component review context を `.accay/runs/{run-id}/context.md` に出力できる。
- system desk-debug context を `.accay/runs/{run-id}/context.md` に出力できる。
- regression result から Markdown / HTML report を生成できる。
- report index を生成または更新できる。
- `accay serve` で生成済み report を閲覧できる。
- Output 単体が artifact loader に依存しない。
- Output 単体が validation / regression の判定ロジックを持たない。
- 不正な run-id と path traversal を拒否できる。
## 23. 将来拡張
- JSON report 出力。
- SARIF 風 diagnostics 出力。
- report assets の分離。
- watch mode。
- report retention policy。
- dashboard filter の高度化。
- multi-run comparison。
- static site としての report publish。
これらを追加する場合も、Output は表示と生成物管理に留める。
正本更新、受け入れ判断、回帰判定は、それぞれの所有 component に残す。
