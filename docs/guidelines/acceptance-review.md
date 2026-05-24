# 受け入れレビューガイドライン
## 1. 目的
受け入れレビューは、通常の code review ではない。
目的は、component 単位で変更を受け入れてよいかを判断することである。
Accay では、変更の良し悪しを「テストが通ったか」だけで判断しない。
仕様、意味、責務境界、テスト証拠をそろえて確認する。
ハーネスは判断主体ではない。
ハーネスは、入力、構造、照合結果、レポートを安定して揃える。
最終的な accept / reject は人間が所有する。
## 2. 位置づけ
この文書は、component acceptance review を行うための実務ガイドである。
architecture の意図は変更しない。
system side と component side は混ぜない。
Operation Directory は契約参照の境界であり、意味判断の正本ではない。
`semantics.md` が component の意味論の正本である。
`test-map.yaml` は受け入れレビューで認定された証拠台帳である。
`.accay/runs/` の成果物は一時成果物であり、自動で正本へ適用しない。
## 3. レビュー対象
レビュー対象は、component と case ID の組で表す。
```text
component: order-domain
case: ORD-001
```
1 回のレビューでは、可能な限り 1 component を主語にする。
複数 component にまたがる変更でも、受け入れ判断は component ごとに分ける。
system scenario は背景として参照してよい。
system scenario を component の受け入れ台帳として扱わない。
## 4. 入力
受け入れレビューの主入力は component 配下の正本成果物である。
- `docs/acceptance/components/{component}/acceptance-scope.yaml`
- `docs/acceptance/components/{component}/test-map.yaml`
- `docs/acceptance/components/{component}/semantics.md`
- `docs/acceptance/components/{component}/interfaces/openapi.yaml`
- `docs/acceptance/components/{component}/interfaces/operations.yaml`
- `docs/acceptance/components/{component}/interfaces/schemas/*`
- 対象 diff
- テスト結果
- JUnit XML
必要に応じて、関連 scenario / sequence / trace を参照してよい。
ただし、それらは参考情報である。
component validation / component regression の正本ではない。
## 5. 出力
レビューの出力は、判断と証拠が追える形にする。
最低限、以下を残す。
- decision
- findings report
- 認定できるテスト証拠
- 認定できない、または不足している証拠
- proposed updates の有無
- 人間判断が必要な論点
一時成果物は以下に置く。
```text
.accay/runs/{run-id}/
  context.md
  review-report.md
  decision.yaml
  proposed/
    test-map.yaml
    acceptance-scope.yaml
```
正本へ自動適用してはならない。
人間が差分を確認し、必要なものだけ取り込む。
## 6. レビュー roles
受け入れレビューには 3 つの役割がある。
| role | 主な責務 |
|---|---|
| 人間 | 最終判断、責務境界の裁定、仕様変更の承認、提案ファイルの採否 |
| エージェント | 差分読解、証拠認定案、違反指摘、更新案作成、レポート作成 |
| ハーネス | context pack 生成、形式検証、JUnit XML 読み取り、既存 test-map 照合、レポート整形 |
エージェントは判断を支援する。
エージェントは、人間の代わりに正本を承認しない。
ハーネスの pass は、受け入れ可能を意味しない。
## 7. 基本順序
推奨する順序は次の通りである。
1. 対象 component と case ID を確認する。
2. `acceptance-scope.yaml` の case 定義を読む。
3. `semantics.md` の責務、operation 意味、不変条件を読む。
4. `interfaces/*` で operation contract を確認する。
5. 対象 diff がどの operation と case に関係するか確認する。
6. テストと JUnit XML を確認する。
7. 既存 `test-map.yaml` との関係を見る。
8. 証拠を認定できるか判断する。
9. decision と findings を書く。
10. 必要なら proposed updates を出す。
証拠認定の前に、意味と責務境界を読むことを推奨する。
## 8. acceptance-scope checks
`acceptance-scope.yaml` は、受け入れケース台帳である。
- 対象 case ID が存在するか。
- case title が変更内容と一致しているか。
- case status がレビュー対象として妥当か。
- case priority がリスクと整合しているか。
- case の operations が実際の変更点と対応しているか。
- case の scenarios が参考情報として妥当か。
- deprecated case を誤って受け入れ対象にしていないか。
`accepted` は、過去に受け入れ済みであることを表す。
`implemented` や `reviewed` は、MVP の `acceptance-scope.yaml` には持たせない。
PR や run の一時状態を、正本の status と混ぜない。
## 9. test-map checks
`test-map.yaml` は、受け入れレビューで認定されたテスト証拠台帳である。
Dev が単に追加したテスト一覧ではない。
- `mappings` に対象 case ID があるか。
- 既存 mapping が今回の変更でも有効か。
- JUnit の `classname + name` が実行結果に存在するか。
- `verifies` が 1 件以上あるか。
- `verifies` が受け入れ条件を説明しているか。
- テスト内容が本当に case を保証しているか。
- 失敗時にどの受け入れ条件が壊れたか説明できるか。
`test-map.yaml` に登録する証拠は、安定して回帰に使える必要がある。
探索的テストは、証拠候補にはなっても、そのまま認定しない。
## 10. semantics checks
`semantics.md` は、component の意味論の正本である。
- component 全体の責務に沿っているか。
- operation ごとの意味を変えていないか。
- field semantics と異なる解釈を入れていないか。
- 不変条件を破っていないか。
- 禁止される変換を追加していないか。
- downstream call に渡す意味を失っていないか。
- よくある誤解に該当する変更をしていないか。
意味違反は、テストが通っていても重大である。
意味を変える必要がある場合は、実装だけでなく `semantics.md` の更新案が必要である。
## 11. interface checks
interface checks では、operation contract と実装・テストの対応を見る。
- 変更対象 operation が interfaces に存在するか。
- operation kind が妥当か。
- input schema と実装の受け取り値が矛盾しないか。
- output schema と実装の返却値が矛盾しないか。
- HTTP status code が contract に存在するか。
- CLI exit code が contract に存在するか。
- function operation の公開境界が曖昧になっていないか。
- schema の構造変更が backward compatibility を壊していないか。
OpenAPI は HTTP operation catalog として扱う。
OpenAPI の description だけで意味判断を完結しない。
意味判断は `semantics.md` と人間の判断に戻す。
## 12. scope and responsibility boundary checks
component の責務境界は、受け入れレビューの重要観点である。
- 変更が対象 component の責務内に収まっているか。
- upstream の都合を component 内に過剰に持ち込んでいないか。
- downstream の内部事情に依存していないか。
- system scenario の都合で component の意味をねじ曲げていないか。
- 他 component の case を、この component の証拠として扱っていないか。
- Operation Directory を越えて直接相手側 artifact を正本扱いしていないか。
責務境界が曖昧な場合は、`needs_human_decision` を使う。
境界の裁定は人間が行う。
## 13. test evidence certification
証拠認定とは、テストを受け入れ条件の証拠として認めることである。
単にテストが存在することではない。
認定できるテストの条件。
- 対象 case の受け入れ条件を直接または十分に近く検証している。
- 失敗したときに、どの保証が壊れたか説明できる。
- JUnit XML で安定して特定できる。
- fixture や mock が意味をすり替えていない。
- `verifies` に短文で保証内容を書ける。
- 回帰実行で継続的に使える。
認定しにくいテストの例。
- 単に実装詳細を固定しているだけのテスト。
- mock の呼び出し回数だけを見ているテスト。
- case の主要条件を通らない happy path だけのテスト。
- ランダム性や外部状態に強く依存するテスト。
- JUnit XML 上で一意に識別できないテスト。
## 14. 証拠不足の扱い
証拠不足は reject とは限らない。
ただし、accept にはできないことが多い。
証拠不足として扱う例。
- 実装は妥当に見えるが、受け入れ条件を検証するテストがない。
- テストはあるが、case の一部しか保証していない。
- JUnit XML が提出されていない。
- JUnit XML に該当 testcase が存在しない。
- `verifies` が曖昧で、何を保証するか分からない。
- 既存 accepted case の回帰結果が確認できない。
証拠追加で解決できるなら `needs_changes` が妥当である。
仕様や責務境界の裁定が必要なら `needs_human_decision` が妥当である。
## 15. decision categories
レビュー結果は、少なくとも以下のいずれかに分類する。
| decision | 意味 |
|---|---|
| `accept` | 受け入れ可能 |
| `reject` | 受け入れ不可 |
| `needs_changes` | 修正後に再確認 |
| `needs_human_decision` | 責務境界や仕様判断を人間が裁定する必要がある |
`accept` は、証拠と意味判断がそろっている場合に使う。
`reject` は、受け入れ条件や意味論に明確に反する場合に使う。
`needs_changes` は、修正や証拠追加で解決できる場合に使う。
`needs_human_decision` は、レビュー担当だけでは裁定してはいけない場合に使う。
## 16. accept / reject の基準
`accept` の前提。
- 対象 case の目的を満たしている。
- component の責務を越えていない。
- `semantics.md` に反していない。
- operation contract と矛盾していない。
- 受け入れ証拠として認定できるテストがある。
- JUnit XML で該当 testcase を確認できる。
- 既存 accepted case の明確な回帰がない。
`reject` の例。
- case の目的を満たしていない。
- component の責務外の判断を実装している。
- field semantics を壊している。
- 禁止される変換を追加している。
- operation contract と実装が矛盾している。
- accepted case の保証を壊している。
reject の報告では、好みではなく受け入れ条件との関係を書く。
## 17. needs_changes の基準
`needs_changes` は、修正後に再確認すれば受け入れ可能性がある場合に使う。
- テスト証拠が不足している。
- `verifies` の記述が曖昧である。
- schema 参照が不足している。
- edge case が acceptance case の重要条件に含まれるのに未検証である。
- 実装の一部が semantics とずれているが修正範囲が明確である。
- `test-map.yaml` の proposed update が必要である。
指摘は、次に何を直せばよいか分かる形にする。
## 18. needs_human_decision の基準
`needs_human_decision` は、推測で決めてはいけない場合に使う。
- 仕様変更として受け入れるべきか、バグとして戻すべきか判断が必要。
- component の責務境界を変更する可能性がある。
- operation の意味を変更する可能性がある。
- accepted case を deprecated にするか判断が必要。
- system scenario と component semantics のどちらを更新するか裁定が必要。
- 互換性を壊す interface 変更を許容するか判断が必要。
この decision では、選択肢と影響を明確に書く。
## 19. proposed updates
Review / QA は、必要に応じて更新案を `.accay/runs/{run-id}/proposed/` に出す。
```text
.accay/runs/{run-id}/proposed/
  test-map.yaml
  acceptance-scope.yaml
```
MVP では、提案ファイルを正本へ自動適用しない。
人間が差分を確認して取り込む。
- 認定済み証拠を追加した `test-map.yaml`。
- 陳腐化した証拠を削除した `test-map.yaml`。
- `verifies` を具体化した `test-map.yaml`。
- case status の変更案を含む `acceptance-scope.yaml`。
- case の operations / scenarios の補正案。
- 自信のない推測更新。
- 人間裁定前の仕様変更。
- system trace を理由にした component 台帳の自動書き換え。
- unrelated case の整理。
## 20. 正本更新の原則
正本更新は最小限にする。
`test-map.yaml` を更新する場合は、対象 case と認定証拠に限定する。
`acceptance-scope.yaml` を更新する場合は、レビュー対象 case に限定する。
`semantics.md` や interfaces の更新が必要な場合は、別の明示的な作業として扱う。
ついでの整理で正本を大きく変えない。
## 21. human judgment boundaries
人間が判断すべきことを、エージェントやハーネスに委ねない。
人間が判断すること。
- 最終的な accept / reject。
- 仕様変更の採否。
- component 責務境界の変更。
- accepted case の deprecated 化。
- backward compatibility の破壊を許容するか。
- proposed updates を正本へ取り込むか。
エージェントは、判断材料、矛盾、証拠認定案、更新案、選択肢と影響を整理する。
ハーネスは、ファイル収集、形式検証、JUnit XML 読み取り、照合、レポート生成を行う。
## 22. component regression との関係
受け入れレビューと component regression は別の工程である。
受け入れレビューは、変更を受け入れてよいか判断する。
component regression は、受け入れ済み case の保証が壊れていないか機械的に照合する。
component regression の入力は、現在の `acceptance-scope.yaml`、`test-map.yaml`、JUnit XML である。
review run の `proposed/` は regression の正本ではない。
regression が fail / missing / skipped を出した場合、レビューでは意味を解釈する。
ハーネスは、失敗原因が仕様変更かバグかを決めない。
## 23. report structure
レビュー報告は、短くても判断根拠が追える形にする。
推奨構成。
```text
# Acceptance Review Report
component:
case:
decision:
## Summary
## Findings
## Certified Evidence
## Missing Evidence
## Semantics and Boundary Notes
## Interface Notes
## Regression Notes
## Proposed Updates
## Human Decisions Needed
```
findings は severity を付けると読みやすい。
| severity | 使い方 |
|---|---|
| P0 | 受け入れ不可の重大違反 |
| P1 | accept 前に修正が必要 |
| P2 | follow-up 可能だが記録すべき |
| P3 | 補足、改善提案 |
## 24. findings の書き方
finding は、観点、根拠、影響、必要な対応を含める。
良い例。
```text
[P1] ORD-001 の重複注文防止条件が証拠化されていない。
acceptance-scope は createOrder における注文作成を対象にしているが、
提出された JUnit XML には通常作成成功の testcase しかない。
semantics.md では idempotency key による重複防止が不変条件として扱われている。
重複入力時の保証を検証するテストを追加し、test-map の verifies に記録する必要がある。
```
避ける例。
```text
テストが弱い気がする。
```
根拠が追えない指摘は、レビューを進めにくくする。
## 25. certified evidence の書き方
認定証拠は、JUnit testcase と保証内容を対応させて書く。
例。
```yaml
ORD-001:
  tests:
    - junit:
        classname: tests.acceptance.order.test_create_order
        name: test_create_order_success
      verifies:
        - order is persisted with requested items
        - createOrder returns order id and accepted status
```
`verifies` は短文でよい。
ただし、「正常系を確認」のような曖昧な表現は避ける。
何が壊れたらこのテストが落ちるべきかを意識して書く。
## 26. missing evidence の書き方
不足証拠は、どの case のどの保証が不足しているかを書く。
例。
```text
Missing evidence:
- ORD-001: duplicate idempotency key の扱いを検証する JUnit testcase がない。
- ORD-001: payment authorization failure 時に order が persisted されないことの証拠がない。
```
不足がある場合でも、実装を断定的に否定しない。
証拠不足と実装不備は分けて書く。
## 27. note examples
interface note の例。
```text
Interface notes:
- createOrder は OpenAPI の operationId と一致している。
- 201 response は schema `CreateOrderResponse` を参照している。
- 実装は 409 を返すが、OpenAPI に 409 response がない。
```
semantics note の例。
```text
Semantics notes:
- semantics.md は `customer_id` を internal customer identity と定義している。
- diff では external account id を `customer_id` に代入している。
- この変換は field semantics と矛盾するため accept できない。
```
契約不足なのか、実装違反なのかを分ける。
判断できない場合は、人間判断の論点に回す。
## 28. decision examples
`accept` の例。
```text
decision: accept
ORD-001 は createOrder の成功時保存と response contract を満たしている。
JUnit XML で認定対象 testcase の pass を確認した。
既存 accepted case の mapped tests に fail / missing はない。
```
`needs_changes` の例。
```text
decision: needs_changes
実装は概ね case 目的に沿っているが、重複注文防止の証拠がない。
idempotency key 重複時の testcase を追加し、verifies に保証内容を記録する必要がある。
```
`needs_human_decision` の例。
```text
decision: needs_human_decision
今回の変更は createOrder が inventory reservation を直接判断する設計に変えている。
これは order-domain の責務に含めるか、inventory component に残すかの裁定が必要である。
```
`reject` の例。
```text
decision: reject
semantics.md では accepted order は payment authorization 後にのみ作成される。
diff は authorization failure 後も order を persisted にしており、不変条件に反する。
```
## 29. anti-patterns
受け入れレビューで避けること。
- テストが通っただけで accept する。
- code style の好みを主 finding にする。
- component の正本を読まずに system trace だけで判断する。
- system trace を component regression の正本として扱う。
- `test-map.yaml` を Dev のテスト一覧として扱う。
- `verifies` に「正常系」「異常系」だけを書く。
- JUnit XML に存在しない testcase を証拠として登録する。
- 人間裁定が必要な仕様変更を `needs_changes` に押し込む。
- proposed updates を正本へ自動適用する。
- unrelated case の整理を同じレビューに混ぜる。
## 30. よくある誤解
「ハーネスが pass したので accept でよい」は誤りである。
ハーネスの pass は、形式や照合が通ったことを意味する。
意味的に受け入れ可能かは別である。
「E2E scenario が通るので component case も accepted」は誤りである。
component の受け入れは component の scope / semantics / interfaces / test-map で判断する。
「テストを追加したので test-map に入れる」は誤りである。
`test-map.yaml` に入れるのは、受け入れレビューで証拠として認定されたテストである。
## 31. レビュー前チェックリスト
- 対象 component が明確である。
- 対象 case ID が明確である。
- 対象 diff を取得できる。
- `acceptance-scope.yaml` を読める。
- `test-map.yaml` を読める。
- `semantics.md` を読める。
- interfaces と schemas を読める。
- テスト結果を確認できる。
- JUnit XML を確認できる。
- 関連 trace / scenario / sequence の扱いが参考情報であると分かっている。
## 32. scope チェックリスト
- case ID は存在する。
- case status はレビュー対象として妥当である。
- case title と変更内容が矛盾しない。
- operations は変更対象と対応している。
- scenarios は背景情報として妥当である。
- deprecated case を対象にしていない。
- 別 component の case を混ぜていない。
- run の一時状態を scope status に持ち込んでいない。
## 33. semantics チェックリスト
- component 責務に収まっている。
- operation の意味を変えていない。
- field semantics を壊していない。
- 不変条件を守っている。
- 禁止変換を追加していない。
- downstream に渡す意味を失っていない。
- 意味変更が必要な場合、文書更新と人間判断の論点になっている。
## 34. interface チェックリスト
- operation ID が存在する。
- operation kind が妥当である。
- input schema と実装が矛盾しない。
- output schema と実装が矛盾しない。
- HTTP status code が契約にある。
- CLI exit code が契約にある。
- schema 変更の影響が説明されている。
- OpenAPI description だけで意味判断していない。
## 35. evidence チェックリスト
- JUnit XML がある。
- testcase を `classname + name` で一意に特定できる。
- testcase は対象 case の主要保証を検証している。
- `verifies` が 1 件以上ある。
- `verifies` は保証内容を短文で説明している。
- テスト fixture が意味をすり替えていない。
- 失敗時に壊れた保証を説明できる。
- 回帰実行に継続利用できる。
## 36. regression チェックリスト
- 既存 `test-map.yaml` の mapped tests を確認した。
- accepted case の fail がない。
- accepted case の error がない。
- accepted case の missing がない。
- accepted case の skipped がない、または扱いが明確である。
- unmapped tests を証拠候補として確認した。
- regression 結果の意味解釈をハーネスに任せていない。
## 37. proposed update チェックリスト
- proposed update は `.accay/runs/{run-id}/proposed/` にある。
- 対象 case 以外を不用意に変更していない。
- `test-map.yaml` の mapping は認定証拠だけを含む。
- `verifies` は空でない。
- JUnit testcase は実行結果に存在する。
- `acceptance-scope.yaml` の status 変更は人間承認が必要である。
- 正本へ自動適用していない。
- report で proposed update の有無を明記している。
## 38. 最終レビュー報告チェックリスト
- component と case ID を書いた。
- decision を書いた。
- 主要 findings を severity 付きで書いた。
- 認定できるテスト証拠を書いた。
- 不足している証拠を書いた。
- semantics / boundary の論点を書いた。
- interface の論点を書いた。
- regression の確認結果を書いた。
- proposed updates の有無を書いた。
- 人間判断が必要な論点を書いた。
## 39. 簡易テンプレート
```text
# Acceptance Review Report
component: <component>
case: <case-id>
decision: <accept|reject|needs_changes|needs_human_decision>
## Summary
- <短い結論>
## Findings
- [P1] <根拠、影響、必要な対応>
## Certified Evidence
- <case-id>: <classname>::<name> verifies <保証内容>
## Missing Evidence
- <case-id>: <不足している保証>
## Semantics and Boundary Notes
- <意味論や責務境界の確認結果>
## Interface Notes
- <operation contract との整合>
## Regression Notes
- <既存 accepted case の回帰状況>
## Proposed Updates
- <あり / なし>
## Human Decisions Needed
- <人間裁定が必要な論点、なければ none>
```
## 40. 最後に確認すること
レビューは、変更を止めるための儀式ではない。
変更を安全に受け入れるための、意味と証拠の整理である。
迷ったら、次の問いに戻る。
- この component の case として受け入れてよいか。
- その判断を支える証拠は何か。
- その証拠は `test-map.yaml` に残せるほど安定しているか。
- 人間が裁定すべき仕様や責務境界を、勝手に決めていないか。
