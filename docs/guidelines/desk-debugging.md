# 机上デバッグガイドライン
## 1. 目的
この文書は、Accay の机上デバッグを実務で安定して行うためのガイドである。
机上デバッグは、E2E に近い業務シナリオを、実装やテスト実行とは独立して operation 列として確認する作業である。
ここで作る中心成果物は `docs/acceptance/traces/{scenario}.trace.yaml` である。
trace は実行ログではない。
trace は「このシナリオでは、どの component のどの operation が、どの意味を保ったまま呼ばれるべきか」を表す仕様である。
机上デバッグの目的は、次の問いに答えられる状態を作ることである。
- シナリオの目的が operation 列に落ちているか。
- 各 step の `input` / `output` が契約と整合しているか。
- 値の保存、変換、副作用、責務境界が観測可能になっているか。
- 仕様変更とバグを後で切り分けられるだけの文脈が残っているか。
- ハーネスが検証できることと、人間が判断すべきことが分かれているか。
## 2. 適用範囲
このガイドは system side の作業に適用する。
対象は主に次の成果物である。
- `docs/acceptance/scenarios/{scenario}.feature`
- `docs/acceptance/sequences/{scenario}.md`
- `docs/acceptance/traces/{scenario}.trace.yaml`
- `.accay/runs/{run-id}/context.md`
- `.accay/runs/{run-id}/desk-debug-report.md`
component side の受け入れレビューそのものは対象外である。
component の `acceptance-scope.yaml` や `test-map.yaml` は、system trace の正本ではない。
component の `semantics.md` は参考情報として読む。
operation contract と schema 参照は Operation Directory を通して扱う。
## 3. 非目的
机上デバッグでは、次のことをしない。
- 実装が正しいかを最終判定する。
- テストの pass / fail だけで受け入れ可否を決める。
- trace から受け入れテストを自動生成する。
- component の受け入れケース台帳を更新する。
- `test-map.yaml` の証拠認定を行う。
- OpenAPI の詳細な lint を行う。
- `semantics.md` の意味論を機械的に完全判定する。
- すべての内部関数呼び出しを trace に書く。
ハーネスは判断主体ではない。
ハーネスは、参照、形式、schema validation、レポート生成を安定して行うための補助である。
## 4. 入力
机上デバッグの入力は、正本と参考情報に分ける。
正本として扱う入力は次の通りである。
- `docs/acceptance/scenarios/{scenario}.feature`
- `docs/acceptance/sequences/{scenario}.md`
- 既存の `docs/acceptance/traces/{scenario}.trace.yaml`
- Operation Directory から得られる operation contract
- operation contract が参照する JSON Schema
参考情報として扱う入力は次の通りである。
- `docs/acceptance/components/{component}/semantics.md`
- `docs/acceptance/components/{component}/review-guidelines.md`
- 既存の受け入れレビュー report
- 実装 diff
- 既存テスト名や JUnit summary
- 過去の desk-debug report
参考情報は判断を助けるために使う。
参考情報を system trace の必須依存にしてはいけない。
## 5. 出力
必須出力は次のファイルである。
```text
docs/acceptance/traces/{scenario}.trace.yaml
```
必要に応じて、次の一時成果物を作る。
```text
.accay/runs/{run-id}/desk-debug-report.md
```
context pack を生成した場合は、次のファイルを読む。
```text
.accay/runs/{run-id}/context.md
```
`docs/acceptance/traces/` は長期保守対象である。
`.accay/runs/` は一時成果物である。
一時成果物にしか残っていない判断を、長期保守すべき trace の根拠にしてはいけない。
## 6. 基本フロー
机上デバッグは、次の順序で行う。
1. scenario を読み、業務目的を一文で確認する。
2. sequence を読み、component 間の自然な流れを確認する。
3. Operation Directory で利用できる operation を確認する。
4. 関連する schema を確認する。
5. 必要に応じて component semantics を読む。
6. scenario の Given / When / Then を operation 列に写像する。
7. 各 step の `input` / `output` を JSON 表現で書く。
8. 観測すべき値、状態、副作用、境界を `observations` に書く。
9. ハーネスで参照整合性と schema validation を確認する。
10. 人間またはエージェントが意味保存条件を確認する。
この順序は厳密な手続きではない。
ただし、operation 列を書く前に endpoint や内部実装の詳細へ入りすぎない。
最初に業務目的と責務境界を固定する。
## 7. Trace の基本形
trace は scenario ごとに 1 ファイルとする。
operation ごとにファイル分割しない。
基本形は次の通りである。
```yaml
scenario: order-checkout
steps:
  - id: create-order
    component: order-api
    operation: createOrder
    input:
      schema_ref: docs/acceptance/components/order-api/interfaces/schemas/create-order-input.schema.json
      value:
        customerId: cus_123
        items:
          - sku: SKU-001
            quantity: 2
    output:
      status: 201
      schema_ref: docs/acceptance/components/order-api/interfaces/schemas/create-order-output.schema.json
      value:
        orderId: ord_456
        status: created
    observations:
      - customerId is preserved as the customer identity.
      - order-api delegates payment authorization to payment component.
```
`scenario` は対応する scenario 名を示す。
`steps` は業務シナリオ上の operation 呼び出し順で並べる。
`id` は trace ファイル内で一意にする。
`component` と `operation` の組み合わせで operation contract を解決する。
`input.schema_ref` と `output.schema_ref` は repository root からの相対パスにする。
`input.value` と `output.value` は schema validation の対象である。
`observations` は空にしない。
## 8. Trace 作成ルール
trace では endpoint ではなく operation を参照する。
HTTP の path や method は operation contract 側に置く。
trace では `request` / `response` ではなく `input` / `output` を使う。
operation の `kind` は trace に書かない。
`kind` は OpenAPI または `operations.yaml` から Operation Directory が解決する。
schema 参照は repository root からの相対パスにする。
component の内部パスやローカル実行環境の絶対パスを schema 参照に使わない。
`step.id` は短く、安定し、意味が分かる名前にする。
`step.id` に HTTP method や status だけを入れない。
同じ operation を複数回呼ぶ場合は、目的が分かる suffix を付ける。
例。
```yaml
- id: reserve-inventory-first-attempt
- id: reserve-inventory-retry
```
値は受け入れ判断に必要な粒度で書く。
ランダム値や時刻は、意味を説明できる固定例にする。
秘密情報、実トークン、個人情報は書かない。
必要なら `token: example-token` のような安全な例にする。
schema に存在しない説明用フィールドを `value` に入れない。
説明は `observations` に書く。
## 9. Operation 抽象
Accay の基本単位は endpoint ではなく operation である。
operation は次のまとまりで理解する。
```text
component
  operation
    input schema
    output schema
```
HTTP API では OpenAPI の `operationId` を operation として扱う。
非 HTTP の境界では `operations.yaml` の operation を扱う。
MVP で扱う kind は次の通りである。
- `http`
- `cli`
- `function`
trace の書き手は kind を直接分岐条件にしない。
kind ごとの実体は operation contract に閉じ込める。
たとえば HTTP では status code を `output.status` に書ける。
CLI では exit code を `output.value.exit_code` など、schema が定める正規化表現で書く。
function では公開 API の入力と戻り値を JSON 表現に正規化して書く。
どの場合でも、trace は `input` / `output` の意味を扱う。
## 10. Observations の書き方
`observations` は、人間とエージェントが意味を判断するための観測点である。
schema で検証できないことを中心に書く。
良い observation は、後から読み返したときに「何を守るべきか」が分かる。
観測点に含めるべき内容は次の通りである。
- 保存されるべき識別子。
- 変換されるべき値。
- 変換してはいけない値。
- downstream call へ渡すべき意味。
- component が判断してはいけないこと。
- 副作用の有無。
- 冪等性、重複、再試行の扱い。
- エラー時に残すべき状態。
- 監査ログや通知など、schema に出にくい結果。
悪い observation は、単に実装手順を述べる。
例。
```yaml
observations:
  - customerId is preserved as external customer identity.
  - order-domain must not decide payment authorization locally.
  - duplicate request with the same idempotency key returns the same orderId.
```
次のような observation は避ける。
```yaml
observations:
  - call database function.
  - test should pass.
  - response is good.
```
`observations` は最低 1 件以上書く。
重要な step では 2 件以上に分ける。
複数の意味を 1 文に詰め込まない。
## 11. Schema Handling
JSON Schema は `input.value` と `output.value` の構造検証に使う。
schema は意味判断の完全な代替ではない。
schema で確認できることは、型、必須項目、列挙値、基本的な構造である。
schema で確認しにくいことは、意味、責務境界、副作用、値の由来である。
schema で表せる制約は schema に置く。
schema で表しにくい制約は `observations` と `semantics.md` に置く。
trace の `schema_ref` は operation contract の schema 参照と一致させる。
operation contract と違う schema を trace 側で勝手に選ばない。
schema が古いと感じた場合は、trace だけを曲げない。
その場合は、次のどれに該当するかを明示する。
- operation contract の更新漏れ。
- schema の表現不足。
- scenario の期待変更。
- component の仕様変更。
- 実装バグ。
`oneOf` / `anyOf` などの高度な意味解釈は MVP の主目的ではない。
複雑な分岐は、trace の step と observations で分かるようにする。
## 12. System / Component 境界
system side は、システム全体の業務シナリオと operation 列を扱う。
component side は、個別 component の責務、契約、受け入れケース、テスト証拠を扱う。
system trace が component 側に対して知ってよいのは、`component + operation` の契約情報である。
system trace は component の `acceptance-scope.yaml` を必須参照にしない。
system trace は component の `test-map.yaml` を読まない。
system trace は JUnit XML を正本として扱わない。
component regression は system trace に依存しない。
component review context に関連 trace が含まれることはある。
その場合も trace は参考情報であり、component の正本ではない。
境界が曖昧になったら、次の問いで切り分ける。
- シナリオ全体の流れを説明しているか。
- component 単体の受け入れ可否を説明しているか。
- operation contract の参照だけで足りるか。
- `semantics.md` の意味判断を trace に移していないか。
- test evidence の認定を trace に書いていないか。
## 13. ハーネスと人間判断
ハーネスが確認することは機械的な整合性である。
主な確認項目は次の通りである。
- scenario / sequence / trace の存在。
- trace step id の重複。
- component の参照。
- operation の参照。
- schema の参照。
- `input.value` の schema validation。
- `output.value` の schema validation。
- `kind: http` の HTTP status の存在。
- `kind: cli` の exit code の存在。
- observations の最低限の存在。
ハーネスが判断しないことは意味上の正しさである。
人間またはエージェントが判断することは次の通りである。
- 業務目的が trace に残っているか。
- 意味保存条件が本当に守られているか。
- 仕様変更かバグか。
- component の責務境界を越えていないか。
- schema の不足を trace でごまかしていないか。
- trace を更新すべきか。
- operation contract を更新すべきか。
- scenario や sequence を更新すべきか。
ハーネスの pass は、受け入れ可を意味しない。
ハーネスの fail は、まず形式または契約参照の問題として読む。
そのうえで、意味上の問題が隠れていないか確認する。
## 14. Context Pack の使い方
机上デバッグでは、必要に応じて context pack を生成する。
代表的なコマンドは次の形である。
```text
accay system pack desk-debug --scenario <scenario>
```
context pack は、エージェントや人間が読むための文脈である。
context pack は正本ではない。
正本は `docs/acceptance/` 配下の scenario、sequence、trace、operation contract、schema である。
context pack を読むときは、次の順で確認する。
1. scenario の目的。
2. sequence の component 間協調。
3. 既存 trace の有無。
4. 関連 operation contract。
5. schema 参照。
6. 関連 semantics。
7. ハーネス diagnostic。
context pack に載っていない情報を根拠にする場合は、元ファイルを直接確認する。
context pack の抜粋だけで trace を更新しない。
context pack が古い可能性がある場合は再生成する。
## 15. 作業手順
新しい trace を作る場合は、まず scenario と sequence を読む。
既存 trace を更新する場合は、差分の理由を先に確認する。
operation contract が見つからない場合は、trace に仮 operation を書かない。
その場合は、operation contract の不足として報告する。
schema が見つからない場合も、trace に独自 schema_ref を作らない。
その場合は、schema の不足として報告する。
step を書くときは、業務上の順序で並べる。
実装上の呼び出し順が業務上の意味と違う場合は、sequence と照合する。
内部最適化やキャッシュの詳細は、受け入れ判断に必要な場合だけ observations に書く。
trace を更新したら、ハーネスで検証できる形になっているか確認する。
最後に、人間が読む観点で説明不足がないか確認する。
## 16. レビュー Checklist
レビューでは、次の項目を確認する。
- scenario 名が trace の `scenario` と一致している。
- sequence の主要な component 協調が steps に反映されている。
- 各 step に一意な `id` がある。
- 各 step が `component + operation` で表されている。
- endpoint、path、method を trace の主語にしていない。
- `input` / `output` を使っている。
- `request` / `response` を使っていない。
- schema 参照が repository root からの相対パスである。
- `input.value` が schema と整合している。
- `output.value` が schema と整合している。
- HTTP status が必要な step に書かれている。
- CLI exit code が schema 上の期待位置に書かれている。
- observations が空でない。
- observations が意味保存条件を説明している。
- component の責務外の判断を trace に押し込んでいない。
- `acceptance-scope.yaml` や `test-map.yaml` への依存を書いていない。
- schema の不足を trace の独自フィールドで埋めていない。
- 一時 report にしかない判断を長期成果物へ反映している。
- 仕様変更、バグ、文書更新の区別が残っている。
## 17. 例: HTTP Operation
HTTP operation では、OpenAPI の `operationId` を operation として扱う。
trace は path や method ではなく operation を参照する。
```yaml
scenario: order-checkout
steps:
  - id: create-order-http
    component: order-api
    operation: createOrder
    input:
      schema_ref: docs/acceptance/components/order-api/interfaces/schemas/create-order-input.schema.json
      value:
        customerId: cus_123
        items:
          - sku: SKU-001
            quantity: 2
    output:
      status: 201
      schema_ref: docs/acceptance/components/order-api/interfaces/schemas/create-order-output.schema.json
      value:
        orderId: ord_456
        status: created
    observations:
      - customerId is preserved for downstream payment authorization.
      - order-api does not reserve inventory directly.
```
この例では `status: 201` は HTTP として観測すべき出力である。
method と path は operation contract 側にある。
## 18. 例: CLI Operation
CLI operation では、argv、env、stdin、files、stdout、stderr、exit code を受け入れ上必要な JSON 表現に正規化する。
```yaml
scenario: user-import
steps:
  - id: import-users
    component: user-import-cli
    operation: importUsers
    input:
      schema_ref: docs/acceptance/components/user-import-cli/interfaces/schemas/import-users-input.schema.json
      value:
        file: users.csv
        dry_run: false
    output:
      schema_ref: docs/acceptance/components/user-import-cli/interfaces/schemas/import-users-output.schema.json
      value:
        exit_code: 0
        imported_count: 120
        skipped_count: 3
    observations:
      - invalid rows are skipped, not imported.
      - duplicate users are reported without stopping the import.
```
CLI の実コマンド文字列は operation contract に置く。
trace には受け入れ判断に必要な入力と出力を書く。
## 19. 例: Function Operation
function operation は、モノリス内や処理系内の公開 API を表す。
実コードの存在や呼び出し順序を MVP のハーネスで厳密検証しない。
```yaml
scenario: order-checkout
steps:
  - id: create-order-domain
    component: order-domain
    operation: createOrder
    input:
      schema_ref: docs/acceptance/components/order-domain/interfaces/schemas/create-order-command.schema.json
      value:
        customerId: cus_123
        items:
          - sku: SKU-001
            quantity: 2
    output:
      schema_ref: docs/acceptance/components/order-domain/interfaces/schemas/create-order-result.schema.json
      value:
        orderId: ord_456
        status: created
    observations:
      - customerId is preserved as external customer identity.
      - order-domain must not decide payment authorization locally.
```
signature や errors は operation contract 側の参照情報として扱う。
trace は公開 API の意味の流れを記述する。
## 20. Anti-patterns
次の書き方は避ける。
- endpoint path を step の主語にする。
- `GET /orders/{id}` のような文字列を operation の代わりに書く。
- `request` / `response` を使う。
- kind を trace に直接書く。
- schema 参照に絶対パスを書く。
- schema にない説明用フィールドを `value` に入れる。
- observations を空配列にする。
- observations に「テストが通る」とだけ書く。
- component の内部実装手順を step として列挙する。
- database table や private function を system trace の主語にする。
- component の受け入れケース ID を system trace の必須参照にする。
- JUnit の test name を trace の正本にする。
- ハーネス pass を受け入れ承認として扱う。
- semantics の不足を trace の長文で補い続ける。
- 仕様変更を schema validation error として片付ける。
anti-pattern を見つけたら、まず境界を確認する。
system trace に書くべき内容か。
operation contract に書くべき内容か。
schema に書くべき内容か。
semantics に書くべき内容か。
component review で扱うべき内容か。
## 21. 破綻を見つけたとき
机上デバッグ中に破綻を見つけたら、すぐに trace を都合よく変えない。
まず破綻の種類を分類する。
- scenario の期待が曖昧。
- sequence が component 協調を説明していない。
- operation contract が不足している。
- schema が実際の payload を表していない。
- component semantics が不足している。
- 実装が期待と違う。
- 仕様変更が必要。
分類したうえで、更新先を決める。
trace は、期待される system flow を表す場所である。
operation contract は、公開境界の契約を表す場所である。
schema は、payload の構造を表す場所である。
semantics は、component と operation の意味を表す場所である。
component の受け入れ証拠は `test-map.yaml` で扱う。
## 22. Maintenance Rules
trace は scenario や operation contract の変更に合わせて保守する。
scenario が変わったら、trace の `scenario` と steps を確認する。
sequence が変わったら、operation 列の順序と component 協調を確認する。
operation が rename されたら、trace の `operation` を更新する。
component が分割または統合されたら、trace の `component` を更新する。
schema が変わったら、`input.value` と `output.value` を再検証する。
semantics が変わったら、observations の意味保存条件を見直す。
既存 trace の更新では、古い期待を消す理由を明確にする。
理由が仕様変更なら、scenario または sequence にも反映が必要か確認する。
理由が contract 変更なら、operation contract と schema の更新を確認する。
理由が実装バグの修正なら、trace の期待を実装に合わせて弱めない。
生成 report は長期保守対象ではない。
重要な判断は trace、scenario、sequence、semantics、operation contract のいずれかに残す。
## 23. 最小完了条件
机上デバッグは、次の状態になったら完了とみなせる。
- 対象 scenario に対応する trace が存在する。
- trace が scenario の主要な Given / When / Then を operation 列で説明している。
- すべての step が `component + operation` を持つ。
- すべての `input.value` と `output.value` が schema と整合する。
- observations が意味保存条件を説明している。
- system / component 境界を越えた依存がない。
- ハーネスが機械的検証を実行できる。
- 人間またはエージェントが残る判断点を説明できる。
この完了条件は、実装の受け入れ承認ではない。
これは、受け入れ判断に必要な system-level の文脈が揃ったことを意味する。
