# レビューガイドライン
## 1. 目的
このガイドラインは、Accay 自体の code review と design review の観点を揃えるためのものである。
Accay は、受け入れ判断そのものを機械に委ねるツールではない。
Accay の役割は、人間とエージェントが判断できるように、入力、構造、照合結果、レポートを安定して揃えることである。
レビューでは、好みの設計や細かい表現よりも、受け入れ駆動ツールとしての境界、公開挙動、テスト証拠を優先して見る。
この文書は、レビュー担当者が同じ基準で差分を読み、同じ強さで指摘し、同じ条件で承認できるようにするための運用文書である。
## 2. レビューの基本姿勢
レビューでは、まず変更の目的を確認する。
その変更が、要件、基本設計、既存の acceptance artifact のどれに対応するかを見る。
対応する根拠がない変更は、実装が正しそうに見えても慎重に扱う。
Accay のレビューは、単なるコード品質レビューではない。
次の 3 点を常に同時に見る。
- 意味: 受け入れ条件や operation の意味を壊していないか。
- 証拠: Contract Test、Unit Test、JUnit XML、report などで確認できるか。
- 境界: system、component、Operation Directory、Output の責務を越えていないか。
レビュー担当者は、最終判断の主体が人間であることを前提にする。
ハーネスに意味判断を押し込む変更は、たとえ便利でも慎重に扱う。
機械でできるのは、形式検証、schema validation、JUnit 照合、report / context 生成である。
仕様変更かバグか、テストを証拠として認めるか、責務境界をどう裁定するかは、人間とエージェントの判断領域として残す。
## 3. レビューの優先順位
レビューでは、次の順で確認する。
1. データ破壊や誤判定が起きないか。
2. system / component / boundary / output の責務境界が守られているか。
3. 公開 CLI の挙動、exit code、生成ファイルが意図通りか。
4. Contract Test で公開挙動が固定されているか。
5. diagnostics が利用者に直せる形になっているか。
6. docs と design artifact が実装内容に追従しているか。
7. 内部実装が保守可能な大きさに収まっているか。
8. 命名、表現、細部の読みやすさが十分か。
レビューの時間が限られる場合は、上位項目から見る。
命名や軽微な整形だけでレビューを消費しない。
ただし、公開 artifact 名、CLI 名、diagnostic code、case ID など、利用者が依存する名前は軽視しない。
## 4. Severity
指摘には、原則として severity を付ける。
severity は、好みではなく利用者への影響と設計境界への影響で決める。
| Severity | 意味 | 典型例 |
|---|---|---|
| P0 | 直ちに修正しないと危険な問題 | データ破壊、誤った pass / fail、既存ファイルの無断上書き、公開 CLI の重大破壊 |
| P1 | 承認前に直すべき主要問題 | architecture 境界違反、主要 use case の不具合、必要な Contract Test 欠落 |
| P2 | できればこの差分で直すべき問題 | diagnostics 不足、edge case 欠落、保守性低下、docs の重要な不足 |
| P3 | 任意改善 | 表現改善、軽微な読みやすさ、将来の整理 |
P0 は、原則として承認しない。
P1 は、明示的な例外合意がない限り承認しない。
P2 は、リスクと変更規模を見て、その PR で直すか follow-up にするか判断する。
P3 は、提案として扱い、承認をブロックしない。
## 5. P0 の判断基準
次のような問題は P0 とする。
- `accay init` や `accay install` が既存ファイルを確認なく上書きする。
- regression が失敗している case を pass として集計する。
- validate が error を warning として扱い、CI で成功してしまう。
- JUnit XML の重複 testcase を無視して不安定な結果を返す。
- `test-map.yaml` を自動更新し、人間の承認なしに正本を変える。
- Output 層の表示都合で正本 artifact を書き換える。
- 公開 CLI の引数互換性を破壊し、移行方針も docs もない。
P0 は、レビューコメントで影響範囲を具体的に示す。
「危険そう」ではなく、どの入力で何が壊れるかを書く。
## 6. P1 の判断基準
次のような問題は P1 とする。
- `system` から component の `acceptance-scope.yaml` や `test-map.yaml` を正本として読む。
- `component regression` が system trace を必須入力にする。
- Operation Directory を通さず、system と component が operation contract を直接読み合う。
- CLI に validation / regression の本体ロジックを置く。
- Output に validation / regression の判断ロジックを置く。
- 新しい公開 CLI 挙動に Contract Test がない。
- diagnostics が machine-readable な分類を失い、利用者が失敗原因を追えない。
- MVP 非対象の自動修正、PR 投稿、自動承認 UI を主要経路に入れる。
P1 は、設計意図を変える可能性が高い。
レビューでは、修正案だけでなく、参照すべき基本設計の章も示す。
## 7. P2 の判断基準
次のような問題は P2 とする。
- edge case の validation が不足している。
- diagnostics に component、operation、file path、case ID などの位置情報が足りない。
- report の主要構造がテストされていない。
- Unit Test で十分な複雑処理が Contract Test だけに寄っている。
- docs が実装とずれており、利用者が使い方を誤解しやすい。
- fixture が過度に巨大で、失敗時に原因を切り分けにくい。
- parser / resolver / matcher の責務が曖昧で、今後の修正が難しい。
P2 は、利用者への直接被害が限定的でも、保守性や診断可能性に影響する。
放置する場合は、follow-up issue や TODO の扱いを明確にする。
## 8. P3 の判断基準
次のような問題は P3 とする。
- コメントの言い回しが少し分かりにくい。
- 変数名をより具体的にできる。
- テーブルの列順を読みやすくできる。
- 将来の抽象化候補がある。
- docs の説明を少し補える。
P3 は、レビューの空気を悪くしないよう提案として書く。
ブロッキング指摘と混ぜない。
## 9. Architecture 境界チェック
Accay の architecture review では、まず依存方向を見る。
許可される基本方向は次の通りである。
```text
cli -> workspace
cli -> system
cli -> operations
cli -> component
cli -> output
system -> operations
system -> output
component -> operations
component -> output
```
直接依存してはいけない方向は次の通りである。
```text
system -> component
component -> system
operations -> system
operations -> component
output -> system artifact loaders
output -> component artifact loaders
```
レビューでは、import、関数呼び出し、データ構造、テスト fixture の参照を確認する。
コード上の import がなくても、ファイルパスや YAML 構造を直接知っていれば実質的な依存になる。
## 10. System Side のチェック
System side は、E2E に近い業務シナリオと operation 列を扱う。
レビューでは次を確認する。
- `scenario.feature`、`sequence.md`、`trace.yaml` を主な正本として扱っているか。
- component の `acceptance-scope.yaml` を system validation の入力にしていないか。
- component の `test-map.yaml` を system validation の入力にしていないか。
- JUnit XML を system validation で読んでいないか。
- trace の operation 参照は Operation Directory を通して解決しているか。
- schema validation は input / output の構造確認に留まっているか。
- 意味保存条件の最終判断をハーネスが行っていないか。
`system pack desk-debug` が component 情報を含める場合は、参考情報として扱う。
正本として扱っている場合は境界違反である。
## 11. Component Side のチェック
Component side は、個別 component の責務、契約、受け入れケース、テスト証拠を扱う。
レビューでは次を確認する。
- `acceptance-scope.yaml`、`test-map.yaml`、`semantics.md`、`interfaces/*` を主な正本として扱っているか。
- system trace を component validation の必須入力にしていないか。
- system trace を component regression の必須入力にしていないか。
- acceptance case ID の存在確認ができているか。
- `test-map.yaml` の `verifies` が空でないことを検証しているか。
- operation contract と schema 参照は Operation Directory を通しているか。
- review context に含める関連 trace は参考情報として明示されているか。
Component side は、受け入れ判断を助ける文脈を作ってよい。
ただし、最終 accept / reject を機械だけで確定してはいけない。
## 12. Operation Directory のチェック
Operation Directory は、system と component の唯一の機械的な接続点である。
レビューでは次を確認する。
- `component + operation` で contract を引けるか。
- OpenAPI の `operationId` を operation ID として扱っているか。
- `operations.yaml` の operation ID と OpenAPI 由来の ID 重複を検出しているか。
- input schema / output schema の参照解決ができるか。
- HTTP status code の存在確認ができるか。
- `kind: cli` の exit code が operation 定義に存在するか確認しているか。
- `semantics.md` の意味判断を Operation Directory に入れていないか。
- acceptance case の状態管理を Operation Directory に入れていないか。
- JUnit XML や `test-map.yaml` の照合を Operation Directory に入れていないか。
Operation Directory は catalog であり、裁判官ではない。
## 13. Output のチェック
Output & Presentation は、表示とファイル出力だけを扱う。
レビューでは次を確認する。
- diagnostics、context、regression result を整形するだけになっているか。
- Output が正本 artifact を直接読んで判断していないか。
- Output が validation / regression の本体ロジックを持っていないか。
- Markdown / HTML / dashboard の差が表示差分に留まっているか。
- report の都合で system と component の正本を混ぜていないか。
- `accay serve` が生成済み report を見る薄い viewer に留まっているか。
- dashboard 上で正本編集、test-map 承認 UI、proposal 適用 UI を持ち込んでいないか。
Output は利用者に分かりやすく見せるための層である。
見せ方の都合で事実を変えない。
## 14. CLI 挙動チェック
Accay は CLI ツールなので、公開挙動の確認を最優先にする。
レビューでは次を確認する。
- コマンド名、引数、オプションが docs と一致しているか。
- 成功時と失敗時の exit code が明確か。
- validation error があるときに CI で失敗できる exit code になるか。
- warning のみの場合の exit code が設計と一致しているか。
- 標準出力と標準エラーの使い分けが一貫しているか。
- 生成ファイルのパスが安定しているか。
- run id、timestamp、絶対パスなどの揺れがテストしやすい形で扱われているか。
- `--junit <path>` のような必須入力が欠けた場合に分かりやすく失敗するか。
- 存在しない component や case ID を指定したときに actionable な diagnostics が出るか。
- 既存ファイルを上書きする可能性がある場合に明示的な保護があるか。
CLI は orchestration layer である。
処理の順序を決めてよいが、validation / regression の本体ロジックを持たない。
## 15. Workspace Mutation チェック
`accay init` と `accay install` は workspace を変更する。
レビューでは特に慎重に見る。
- repository root の検出が意図通りか。
- `.accay/config.yaml` の作成と読み取りが安全か。
- `docs/acceptance/` 配下の既存ファイルを不用意に上書きしないか。
- `.agents/skills/` など skill install dir の扱いが設定に従っているか。
- 既にファイルがある場合の挙動が docs に書かれているか。
- 作成したファイル一覧を summary として返しているか。
- 失敗途中で中途半端な状態になった場合の説明があるか。
既存ファイル保護の不足は、軽微な実装ミスではない。
利用者のリポジトリに導入されるツールであることを前提に見る。
## 16. Validation チェック
`accay validate` 系のレビューでは、対象範囲と責務を確認する。
| コマンド | system validation | component validation |
|---|---:|---:|
| `accay validate` | する | 全 component に対してする |
| `accay system validate` | する | しない |
| `accay component validate <component>` | しない | 指定 component に対してする |
レビューでは次を確認する。
- Operation Directory を必要に応じて構築しているか。
- system validation と component validation の対象が混ざっていないか。
- YAML 構文エラーを分かりやすく返しているか。
- schema 参照の欠落を検出しているか。
- trace の input / output が JSON Schema で検証されているか。
- HTTP status code の参照が検証されているか。
- CLI exit code の参照が検証されているか。
- `test-map.yaml` の case ID が `acceptance-scope.yaml` に存在するか確認しているか。
- `test-map.yaml` の `verifies` が 1 件以上あることを確認しているか。
Validation は、形式と参照の検証を行う。
意味判断や仕様変更判定まで背負わせない。
## 17. Regression チェック
`accay regression` 系のレビューでは、JUnit XML と `test-map.yaml` の照合を中心に見る。
| コマンド | 対象 |
|---|---|
| `accay regression --junit <path>` | 全 component |
| `accay component regression <component> --junit <path>` | 指定 component |
レビューでは次を確認する。
- component artifact を正本として読んでいるか。
- system trace を直接読んでいないか。
- 1 つ以上の JUnit XML を読めるか。
- 複数 JUnit XML を 1 つの test result set としてマージしているか。
- `classname + name` で testcase を照合しているか。
- 同じ `classname + name` が複数出た場合に validate error になるか。
- case 単位で pass / fail / missing / unmapped を集計しているか。
- failed testcase を pass として扱う経路がないか。
- missing testcase を利用者が直せる形で report しているか。
- unmapped testcase を自動で `test-map.yaml` に追加していないか。
Regression は、失敗原因の意味解釈まではしない。
test-map の陳腐化を示すことはできるが、更新の承認は人間が行う。
## 18. Context Pack チェック
Context pack は、人間やエージェントが判断するための入力を揃える。
レビューでは次を確認する。
- `system pack desk-debug` が scenario / sequence / trace を正本としているか。
- `component pack review` が scope / test-map / semantics / interfaces を正本としているか。
- 参考情報と正本情報が混同されていないか。
- diff、tests、JUnit summary を含める場合に出典が分かるか。
- context に必要以上の巨大な情報を詰め込んでいないか。
- `context.md` の出力先が `.accay/runs/{run-id}/context.md` として扱われているか。
- context 生成が正本 artifact を変更していないか。
Context pack は判断の材料であり、判断結果ではない。
decision や proposed update と混ぜない。
## 19. Docs チェック
コード変更だけでなく、design docs の差分もレビュー対象である。
レビューでは次を確認する。
- 要件定義の非目的を広げていないか。
- 基本設計の責務境界を変えていないか。
- MVP 非対象の機能を、実装済みのように書いていないか。
- CLI 例が実装と一致しているか。
- file path、artifact 名、case ID、operation ID の表記が一貫しているか。
- `docs/acceptance/` と `.accay/` の性質の違いが守られているか。
- 正本 artifact と一時生成物の区別が明記されているか。
- Mermaid 図や sequence の依存方向が本文と一致しているか。
- docs の更新が必要な実装変更で、docs が置き去りになっていないか。
- docs だけの変更で、architecture intent が変わっていないか。
Docs は後から読む人の設計境界である。
表現の改善でも、境界が曖昧になるなら指摘する。
## 20. Acceptance Artifact チェック
Accay の利用者が保守する artifact についても、レビュー観点を揃える。
レビューでは次を確認する。
- `scenario.feature` が system 全体の業務シナリオを表しているか。
- `sequence.md` が component 間協調を説明しているか。
- `{scenario}.trace.yaml` が operation 列、input、output、観測点を表しているか。
- `acceptance-scope.yaml` が component の受け入れケース台帳になっているか。
- `test-map.yaml` が認定済みテスト証拠台帳になっているか。
- `semantics.md` が operation の意味論の正本になっているか。
- `interfaces/openapi.yaml` と `interfaces/operations.yaml` が contract catalog として扱われているか。
- JSON Schema が trace の input / output 構造検証に使われているか。
- `reviews/` や `reports/` に保存するものが正本更新と混ざっていないか。
Artifact の役割が曖昧になると、レビュー判断も曖昧になる。
差分が artifact の意味を変える場合は、実装差分と同じ強さで見る。
## 21. Test Evidence チェック
テスト証拠は、Accay のレビューで最重要の確認対象である。
レビューでは次を確認する。
- 公開 CLI 挙動に Contract Test があるか。
- exit code の期待値がテストされているか。
- diagnostics の主要構造がテストされているか。
- 生成ファイルの存在と主要構造がテストされているか。
- report / context の主要構造が golden などで確認されているか。
- parser / resolver / matcher など複雑な局所処理に Unit Test があるか。
- Probe Test を CI 必須の長期保守テストとして扱っていないか。
- fixture project が小さく、失敗原因を追えるか。
- 受け入れ条件に対応するテストが traceable か。
- テスト名が `test-map.yaml` の `classname + name` 照合と矛盾していないか。
Contract Test は、内部実装ではなく公開振る舞いを固定する。
内部関数の形を固定するためだけの Contract Test は避ける。
## 22. Diagnostics チェック
diagnostics は、利用者が問題を直すための出力である。
レビューでは次を確認する。
- severity が error / warning / info などで区別されているか。
- machine-readable な code があるか。
- message が短く具体的か。
- component、operation、case ID、scenario、file path、line などの位置情報があるか。
- expected と actual が必要な場合に示されているか。
- suggested action が利用者に実行可能か。
- 複数エラーを 1 つの曖昧な message に潰していないか。
- stack trace を通常の利用者向け message として出していないか。
- Markdown / HTML / CLI output で同じ事実を表示しているか。
- exit code と diagnostic severity が矛盾していないか。
良い diagnostics は、誰が何を直せばよいかを示す。
悪い diagnostics は、内部事情だけを説明する。
## 23. Diagnostic Message の書き方
message は、簡潔で行動可能にする。
悪い例:
```text
invalid test-map
```
良い例:
```text
test-map entry references unknown acceptance case "AUTH-003" in component "auth".
```
悪い例:
```text
schema failed
```
良い例:
```text
trace "checkout-success" output for operation "orders.createOrder" does not match output schema.
```
message には、利用者が探すための名前を含める。
ただし、長すぎる説明は report の詳細欄に分ける。
## 24. CLI Output チェック
CLI output は、人間が端末で読む最初の report である。
レビューでは次を確認する。
- 成功時の summary が短く分かりやすいか。
- 失敗時に error count と対象範囲が分かるか。
- 生成した report や context の path が表示されるか。
- 色や装飾がなくても意味が通るか。
- CI log で読める順序になっているか。
- noisy な debug output が通常出力に混ざっていないか。
- `--quiet` や `--verbose` を追加する場合、既定挙動を壊していないか。
- stdout / stderr の使い分けがテスト可能か。
CLI output は、Output 層の責務で整形する。
ただし、何を error とするかは validation / regression 側の結果で決める。
## 25. Review Comment Style
レビューコメントは、事実、影響、提案を分けて書く。
推奨形は次の通りである。
```text
[P1] Component regression should not read system traces
This path makes component regression depend on docs/acceptance/traces as a required input.
That breaks the architecture rule that component regression runs from component artifacts and JUnit XML only.
Please move the trace lookup out of the regression path, or include it only in review context as reference material.
```
日本語で書く場合も、構造は同じでよい。
```text
[P1] component regression が system trace を必須入力にしています
この経路では、component regression が docs/acceptance/traces を読めないと実行できません。
基本設計では component regression は component artifact と JUnit XML だけで最低限回る必要があります。
trace は review context の参考情報に移すか、regression 本体から外してください。
```
コメントでは、人格ではなく差分を扱う。
「なぜそうしたのか分からない」ではなく、「この入力でこの境界が壊れる」と書く。
## 26. 指摘の粒度
1 つのコメントには、原則として 1 つの問題を書く。
同じ原因から複数箇所に現れている場合は、代表箇所にまとめて書く。
広い設計論になりそうな場合は、PR コメントではなく design discussion に切り出す。
ただし、承認可否に関わる境界違反は PR 上に明示する。
軽微な好みは、nit か suggestion として書く。
nit を積み重ねて承認をブロックしない。
## 27. 承認前チェックリスト
承認前に、次を確認する。
- 変更目的が要件または設計文書と対応している。
- 変更範囲が component design と一致している。
- system と component の直接依存が増えていない。
- Operation Directory が接続点として使われている。
- CLI に validation / regression の本体ロジックが入っていない。
- Output に判断ロジックが入っていない。
- 既存ファイルを不用意に上書きしない。
- 追加・変更した公開挙動に Contract Test がある。
- Unit Test が必要な局所処理に追加されている。
- diagnostics が利用者に直せる形で返っている。
- docs の更新が必要な場合に反映されている。
- MVP 非対象の機能を混ぜていない。
- `git status` で意図しない変更が混ざっていない。
このチェックリストは、承認の最低条件である。
すべて満たしても、設計上の疑義が残る場合は質問してよい。
## 28. Design Docs 承認チェックリスト
docs だけの PR でも、次を確認する。
- 要件と基本設計の用語を変えていない。
- 新しい用語を追加する場合、定義がある。
- operation、component、case、testcase の関係が曖昧になっていない。
- MVP でやらないことを、やることとして書いていない。
- 正本と生成物の置き場所が混ざっていない。
- Mermaid 図の依存方向が本文と一致している。
- CLI 例が実装予定のコマンド体系と一致している。
- レビュー手順が人間の最終判断を前提にしている。
Design docs の変更は、後続の実装者の前提になる。
小さな文言変更でも、境界を変えるなら P1 として扱う。
## 29. Code Review Anti-Patterns
次のパターンは避ける。
- CLI が便利だからという理由で、検証ロジックを CLI に直接書く。
- Output で表示しやすいからという理由で、正本 artifact を直接読み直す。
- system validation のついでに component の `test-map.yaml` を読む。
- component regression のついでに system trace を読む。
- Operation Directory に semantics や acceptance decision を持たせる。
- JUnit XML の edge case を見なかったことにする。
- diagnostics を例外 message の文字列だけで済ませる。
- Contract Test なしで公開 CLI 挙動を変える。
- fixture を巨大にして、何を検証しているか分からなくする。
- Probe Test を長期保守テストの代わりにする。
- MVP 外の自動修正や PR 投稿を小さな便利機能として混ぜる。
便利な短絡は、後で境界の負債になる。
Accay では、少し手間がかかっても責務の置き場所を守る。
## 30. Design Review Anti-Patterns
設計レビューでは、次のパターンに注意する。
- 「将来必要そう」だけで MVP scope を広げる。
- OpenAPI lint、静的解析、エージェント実行基盤など、別プロダクトの責務を混ぜる。
- 意味判断をハーネスに寄せすぎる。
- report の見栄えを理由に正本構造を変える。
- acceptance case と testcase を 1 対 1 固定にしてしまう。
- `implemented` や `reviewed` のような一時状態を `acceptance-scope.yaml` の正本に入れる。
- `test-map.yaml` 自動更新を前提に運用を設計する。
- system と component の境界を「後で整理する」として曖昧にする。
- docs にだけ存在する概念を実装境界として扱う。
将来拡張の余地は残してよい。
ただし、MVP の責務境界をぼかしてまで先取りしない。
## 31. テスト不足を指摘する基準
テスト不足は、単に coverage の数字では判断しない。
次のいずれかに当てはまる場合は、テスト追加を求める。
- 利用者が実行する CLI の挙動が変わる。
- exit code が変わる。
- generated report / context の主要構造が変わる。
- diagnostics の code、severity、message、位置情報が変わる。
- operation lookup や schema lookup の規則が変わる。
- JUnit XML の読み取りや merge の規則が変わる。
- `test-map.yaml` の照合規則が変わる。
- 既存ファイル作成や上書き判定が変わる。
- parser / resolver / matcher の edge case を追加する。
テストを求めるときは、Contract Test か Unit Test かを明示する。
公開挙動なら Contract Test、局所処理なら Unit Test を優先する。
## 32. docs 更新を求める基準
次の変更では docs 更新を求める。
- 公開 CLI のコマンド、引数、出力が変わる。
- config の key や既定値が変わる。
- artifact の形式や必須項目が変わる。
- diagnostics の意味や severity が変わる。
- report / context の保存場所が変わる。
- MVP scope の説明に影響する。
- architecture の責務境界に影響する。
- ユーザーが migration を必要とする。
docs 更新は、実装の説明ではなく利用者と実装者の契約更新として見る。
内部 refactor だけなら docs 更新は不要な場合もある。
## 33. 例外を認める場合
原則から外れる場合は、レビューで明示する。
例外を認める条件は次の通りである。
- 例外の範囲が小さい。
- 例外の理由が要件または基本設計に照らして説明できる。
- 後で通常経路に戻す必要がある場合、follow-up がある。
- 利用者に見える公開挙動が壊れていない。
- Contract Test で例外的な挙動が固定されている。
「今回は急いでいる」は、境界違反を認める十分な理由ではない。
スコープを削る、段階的に入れる、feature を分ける、の順で検討する。
## 34. レビュー完了の判断
レビュー完了とは、コメントがなくなった状態だけを意味しない。
次の状態になっていることを確認する。
- P0 / P1 が解消されている。
- 残る P2 / P3 の扱いが合意されている。
- 変更された公開挙動にテスト証拠がある。
- architecture boundary が維持されている。
- docs と実装の説明が矛盾していない。
- diagnostics と CLI output が利用者に説明可能である。
- 意図しないファイル変更が混ざっていない。
レビュー担当者は、承認時に「何を確認して承認したか」を短く書くとよい。
例:
```text
Approved after checking CLI contract coverage, component/system boundary, and diagnostics shape.
```
日本語なら次のように書ける。
```text
CLI の公開挙動、component/system 境界、diagnostics の形を確認して承認します。
```
## 35. 迷ったときの基準
迷ったときは、次の問いに戻る。
- その変更は、人間の受け入れ判断を助けるか。
- その変更は、機械に判断を任せすぎていないか。
- その変更は、system と component の境界を保っているか。
- その変更は、公開 CLI の利用者に説明できるか。
- その変更は、Contract Test で固定できるか。
- その変更は、MVP の範囲に収まっているか。
答えが曖昧な場合は、実装を進める前に設計コメントとして確認する。
Accay のレビューでは、速さよりも境界と証拠を優先する。
