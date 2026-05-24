# 開発ガイドライン

この文書は、Accay MVP を実装・保守するための実務ガイドラインである。
上位文書は `docs/requirements.md` と `docs/architecture.md` である。
この文書は基本設計の意図を変更せず、実装時に迷いやすい判断を実務手順として明文化する。

## 1. 基本方針

Accay は、受け入れ判断を支援するハーネスである。
ハーネスは、入力、構造、照合結果、レポートを安定して揃える。
最終的な受け入れ判断は、人間とエージェントに残す。
実装では、機械的に確認できることと、意味判断が必要なことを分ける。
長期保守する正本成果物と、一時的な生成物を分ける。
system 側の成果物と、component 側の成果物を分ける。
表示のための整形と、検証や照合の本体ロジックを分ける。
この分離が崩れる変更は、たとえ実装量が減っても避ける。

## 2. 守るべき境界

Accay の実装では、package の便利さより責務境界を優先する。
`system` と `component` の直接依存を作らない。
system と component の接続は `operations` に寄せる。
CLI は orchestration に留める。
CLI に validation / regression の本体ロジックを置かない。
`output` は表示とファイル出力に留める。
`output` に判断ロジックを置かない。
`operations` は意味判断をしない。
`component regression` は system trace を正本として読まない。
`system validation` は component の `acceptance-scope.yaml` や `test-map.yaml` を正本として読まない。
境界を越えたくなった場合は、入力モデル、返却結果、呼び出し順序を先に見直す。

## 3. 推奨配置

基本の配置は以下を目安にする。

```text
src/accay/
  cli.py
  workspace/
  system/
  operations/
  component/
  output/
  templates/

tests/
  contract/
  unit/
  probe/
  fixtures/
  golden/
```

package 内の helper module は増やしてよい。
ただし、package 間の依存方向は崩さない。
内部型や dataclass は必要に応じて定義してよい。
それらを architecture の公開契約として扱わない。

## 4. 依存方向

許可する基本の依存方向は以下である。

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

禁止する直接依存は以下である。

```text
system -> component
component -> system
operations -> system
operations -> component
output -> system artifact loaders
output -> component artifact loaders
```

禁止依存が必要に見える場合、設計上の合図として扱う。
多くの場合、`operations` に境界データを寄せるか、CLI が両者を順に呼ぶ形にできる。

## 5. Component boundaries

`workspace` は repository root、config、初期化、skill install、既存ファイル保護を扱う。
`workspace` は acceptance artifact の深い検証をしない。
`system` は scenario、sequence、trace を扱う。
`system` が正本として読むのは `docs/acceptance/scenarios/`、`docs/acceptance/sequences/`、`docs/acceptance/traces/` である。
`system` は `test-map.yaml` を読まない。
`system` は JUnit XML を読まない。
`system` は component regression の結果を正本として扱わない。
`operations` は system と component の機械的な接続点である。
`operations` は OpenAPI、`operations.yaml`、JSON Schema を operation contract として参照可能にする。
`operations` は `semantics.md` の意味判断をしない。
`operations` は受け入れケースの状態管理をしない。
`component` は個別 component の受け入れ成果物を扱う。
`component` が正本として読むのは `acceptance-scope.yaml`、`test-map.yaml`、`semantics.md`、`review-guidelines.md`、`interfaces/` である。
`component` は system trace を正本として要求しない。
関連 trace を context pack に含める場合も、参考情報として扱う。
`output` は diagnostics、context、report、dashboard を整形する。
`output` は validation や regression の本体ロジックを持たない。

## 6. 開発ワークフロー

変更は、原則として docs-first で進める。
まず requirements または architecture と照合する。
次に対象 package の責務を確認する。
公開挙動が変わるか確認する。
公開挙動が変わる場合は Contract Test を先に考える。
局所処理が複雑な場合は Unit Test を追加する。
実装後は CLI 経由の挙動を確認する。
diagnostics と exit code を確認する。
生成物の出力先と上書き挙動を確認する。
関連ドキュメントを更新する。
小さな内部修正でも、境界をまたぐ場合は一段慎重に扱う。

## 7. Docs-first development

Accay 自身の開発でも、仕様と証拠を先に整える。
docs-first の対象は、CLI の公開挙動、exit code、diagnostics の意味、report / context の主要構造である。
`.accay/` 以下の生成物、`docs/acceptance/` 以下の正本成果物、config の設定項目、operation contract の扱いも対象である。
コードだけを先に変えて、あとから文書で追認しない。
仕様が曖昧なままなら、まず文書上で判断を固定する。
ただし、private helper や内部型の細部まで文書化しない。

## 8. Branching と commit

作業単位は、小さくレビュー可能に保つ。
1 branch は 1 つの目的に寄せる。
unrelated な整形や移動を混ぜない。
設計境界を変える変更は通常の実装修正と分ける。
docs-only 変更と実装変更は必要に応じて分ける。
generated file の更新は人間が確認しやすい単位にする。
commit message には変更理由が読める情報を入れる。
公開挙動の変更を隠さない。
生成物だけの変更と手書き正本の変更を混ぜすぎない。
failing test を既知の状態として残す場合は理由を明記する。
具体的な Git フローは repository の運用に従う。

## 9. CLI 実装方針

CLI は orchestration layer とする。
CLI は引数を解釈する。
CLI は repository root を決める。
CLI は config を読む。
CLI は対象 component / scenario を決める。
CLI は必要な処理の呼び出し順序を決める。
CLI は結果を output 層へ渡す。
CLI は exit code を決める。
CLI は trace の schema validation 本体を持たない。
CLI は JUnit XML の照合本体を持たない。
CLI は acceptance-scope と test-map の整合性検証本体を持たない。
CLI は report の詳細整形を持たない。
CLI は semantics の意味判断をしない。
CLI は test-map を自動更新しない。
CLI にロジックを書きたくなった場合は、対象 package に処理を移す。

## 10. CLI behavior

CLI の公開挙動は Contract Test で固定する。
固定対象は command name、required argument、optional argument、default path である。
stdout / stderr の主要メッセージ、exit code、生成ファイルの有無も固定対象である。
生成ファイルの主要構造と diagnostics の severity も固定対象である。
文言全体を過度に固定しない。
ただし、人間や CI が依存するメッセージは安定させる。
エラー時は、利用者が次に何を直せばよいか分かる情報を返す。

## 11. Exit code

exit code は利用者と CI の契約である。
成功は `0` とする。
error diagnostics がある場合は非ゼロとする。
warning / info だけなら原則 `0` とする。
CLI の使い方が誤っている場合は非ゼロとする。
内部例外は非ゼロとする。
将来、細かい exit code を分ける場合も Contract Test で固定する。
MVP では、意味を過度に細分化しない。

## 12. Diagnostics

利用者が直せる問題は diagnostics として返す。
予期しない内部不整合は例外として扱ってよい。
diagnostic には、可能な限り severity、message、対象ファイルを含める。
対象 component、対象 scenario、対象 operation、対象 case ID、修正の手がかりも含める。
`error` は処理継続または受け入れ確認を妨げる問題である。
`warning` は機械的には続行できるが注意が必要な問題である。
`info` は参考情報である。
diagnostics は機械処理しやすい構造を先に作る。
表示文言は `output` で整形する。

## 13. Filesystem safety

Accay はユーザーの repository に導入される。
ファイル操作は保守的に行う。
既存ファイルを不用意に上書きしない。
`init` は不足しているディレクトリや default config を作る。
`install` は既存 skill を不用意に上書きしない。
`.accay/runs/{run-id}/` は新しい run ごとに分ける。
report 出力は既定の出力先に限定する。
repository root の外へ勝手に書き込まない。
入力 path は repository root からの相対 path を優先する。
絶対 path を diagnostics や golden file に過剰固定しない。
上書きが必要な機能は、明示的な option を設計してから追加する。
MVP では暗黙の overwrite を避ける。

## 14. 正本成果物

長期保守対象は `docs/acceptance/` 以下に置く。
主な正本成果物は `scenario.feature`、`sequence.md`、`{scenario}.trace.yaml` である。
component 側の正本成果物は `acceptance-scope.yaml`、`test-map.yaml`、`semantics.md`、`review-guidelines.md` である。
interface 側の正本成果物は `interfaces/openapi.yaml`、`interfaces/operations.yaml`、`interfaces/schemas/*.schema.json` である。
正本成果物は人間が読み、レビューし、長期保守する。
generated report から正本成果物を暗黙更新しない。
`proposed/` 以下のファイルは更新案である。
人間の承認なしに正本へ反映しない。

## 15. 生成物

設定・生成物・一時ファイルは `.accay/` 以下に置く。
主な生成物は `.accay/runs/{run-id}/context.md` である。
review 由来の生成物は `.accay/runs/{run-id}/review-report.md` と `.accay/runs/{run-id}/decision.yaml` である。
更新案は `.accay/runs/{run-id}/proposed/test-map.yaml` と `.accay/runs/{run-id}/proposed/acceptance-scope.yaml` に置く。
report は `.accay/reports/html/` と `.accay/reports/markdown/` に置く。
その他の生成物は `.accay/generated/` と `.accay/cache/` に置く。
生成ファイルは、再生成できることを前提に扱う。
run id、timestamp、絶対 path などの揺れる値を最小化する。
golden file で比較する範囲は主要構造に限定する。
回帰は review 成果物を正本として読まない。
現在の `acceptance-scope.yaml` と `test-map.yaml` を読む。

## 16. Dependency rules

依存追加は、必要性と保守性を確認してから行う。
標準ライブラリで足りないか確認する。
既存 dependency で足りないか確認する。
CLI ツールとして起動時間に悪影響がないか確認する。
ライセンスが OSS として扱えるか確認する。
Python version の対応範囲に合うか確認する。
セキュリティ更新が見込めるか確認する。
transitive dependency が過剰でないか確認する。
JSON Schema、YAML、JUnit XML、OpenAPI などは専用 parser を使う。
手書きの文字列処理で構造化形式を読むことは避ける。
外部プロセス呼び出しに依存する実装は慎重に扱う。

## 17. Versioning posture

MVP では、公開契約を過度に増やさない。
安定させる対象は CLI command structure、exit code の基本意味、diagnostics の主要構造である。
artifact path の基本方針、report / context の主要構造、operation kind の扱いも安定させる。
`test-map.yaml` の照合単位も安定させる。
安定化しすぎない対象は private helper、private dataclass、internal model の細部である。
report の細かい文言、dashboard の見た目、package 内部のファイル分割も固定しすぎない。
破壊的変更が必要な場合は、まず文書で影響を明示する。
公開挙動を変える場合は Contract Test を更新する。

## 18. Operation contract

operation は Accay の中心単位である。
endpoint ではなく operation を扱う。
trace は `component + operation` で解決する。
OpenAPI の `operationId` を HTTP operation ID として扱う。
`operations.yaml` は Accay native の operation 定義として扱う。
同一 component 内の operation ID 重複は validate error にする。
override / merge / namespace は MVP では持たない。
JSON Schema は `input` / `output` の構造検証に使う。
意味論は `semantics.md` に残す。
OpenAPI は HTTP operation catalog として扱う。
OpenAPI lint ツールにならない。

## 19. Validation

system validation は、scenario、sequence、trace の整合性を見る。
scenario / sequence / trace が存在するか確認する。
trace が参照する component、operation、schema が存在するか確認する。
step id が重複していないか確認する。
`input.value` と `output.value` が schema に合うか確認する。
HTTP status が operation 定義にあるか確認する。
CLI exit code が operation 定義にあるか確認する。
observations が空でないか確認する。
component validation は、component 配下の成果物の整合性を見る。
`acceptance-scope.yaml`、`test-map.yaml`、`semantics.md`、`interfaces/` を確認する。
`test-map.yaml` の case ID が scope に存在するか確認する。
`test-map.yaml` の `verifies` が 1 件以上あるか確認する。
operation contract と schema 参照が解決できるか確認する。
validation は意味保存条件の最終判断をしない。

## 20. Regression

component regression は、受け入れ済みケースの保証が壊れていないかを見る。
入力は `acceptance-scope.yaml`、`test-map.yaml`、1 つ以上の JUnit XML である。
複数 JUnit XML は 1 つの test result set として扱う。
testcase は `classname + name` で照合する。
同一 `classname + name` が複数ある場合は validate error にする。
case 単位で pass / fail / error / skipped / missing を集計する。
accepted case の failed / error / missing / skipped は fail として扱う。
unmapped test は原則 info として report に残す。
失敗原因の意味解釈はハーネスの責務ではない。

## 21. Context pack

context pack は、エージェントまたは人間に渡す判断材料である。
`system pack desk-debug` は、system 側の机上デバッグを支援する。
正本として読むものは scenario、sequence、trace である。
`component pack review` は、component 側の受け入れレビューを支援する。
正本として読むものは scope、test-map、semantics、interfaces である。
相手側の情報を参考情報として含めてもよい。
ただし、正本の所有者を混ぜない。
context pack は判断を代行しない。

## 22. Report と dashboard

Markdown report は、エージェントと人間の調査入力として扱う。
HTML report と dashboard は、人間向けの閲覧に使う。
validation / regression の結果をそのまま表示する。
表示の都合で結果を再判定しない。
重要な diagnostics を見落としにくくする。
component 別、case 別、scenario 別に辿れるようにする。
run id や出力 path を明示する。
generated report から正本を更新しない。
`accay serve` は、生成済み report を見るための薄い viewer とする。
MVP では dashboard 上で正本編集しない。

## 23. Test strategy

Accay 自身のテストは、公開挙動を中心に置く。
Contract Test は最重要である。
CLI、exit code、diagnostics、生成ファイル、report / context の主要構造を固定する。
Unit Test は、parser、resolver、matcher、formatter などを支える。
複雑な局所処理や edge case を確認する。
Probe Test は調査用である。
通常 CI の必須対象にしない。
fixture project は小さく保つ。
実際のユーザー repository を模すが、大きな現実プロジェクトをそのまま持ち込まない。
golden file は主要構造確認に使う。
timestamp、run id、絶対 path を直接比較しない。

## 24. Config と template

`.accay/config.yaml` は、導入先 repository の設定を持つ。
主な設定対象は docs root、skill install dir、JUnit XML の既定 path である。
regression 判定ルール、report 出力先、generated text の言語も設定対象である。
config の追加は慎重に行う。
既定値で自然に動くことを優先する。
設定がないと動かない機能は、`accay init` の出力と整合させる。
template は、ユーザーが読み、編集し、長期保守する入口である。
生成直後に意味が分かる内容にする。
過剰に長い boilerplate にしない。

## 25. Diagnostics checklist

diagnostics を追加・変更する場合は、severity が適切か確認する。
対象ファイルが分かるか確認する。
対象 component または scenario が分かるか確認する。
対象 operation または case ID が分かるか確認する。
message が原因を説明しているか確認する。
修正の手がかりがあるか確認する。
機械処理用の構造と表示文言が分離しているか確認する。
warning と error が混ざっていないか確認する。
diagnostics は利用者との会話である。

## 26. Filesystem checklist

ファイルを書き込む処理では、書き込み先が repository root 配下か確認する。
正本成果物を書き換える処理か、生成物を書く処理か明確にする。
既存ファイルの上書き条件を明確にする。
`--force` 相当がないのに上書きしていないか確認する。
parent directory 作成の範囲が限定されているか確認する。
run ごとの出力先が衝突しないか確認する。
error 時に中途半端な正本更新を残さないか確認する。
ファイル操作は、利用者の信頼を失いやすい領域として扱う。

## 27. Dependency checklist

dependency を追加する場合は、追加理由が明確か確認する。
標準ライブラリや既存 dependency では足りないか確認する。
license が問題ないか確認する。
メンテナンスされているか確認する。
起動時間と install size が許容範囲か確認する。
transitive dependency が過剰でないか確認する。
テストで主要 edge case を確認しているか確認する。
dependency は便利さだけで追加しない。

## 28. Review checklist

実装レビューでは、system と component の直接依存がないか確認する。
CLI に検証本体が入っていないか確認する。
output に判断ロジックが入っていないか確認する。
Operation Directory 経由で契約参照しているか確認する。
正本成果物と生成物が混ざっていないか確認する。
既存ファイルを暗黙上書きしていないか確認する。
diagnostics が利用者に直せる情報になっているか確認する。
exit code が公開挙動として妥当か確認する。
Contract Test が必要な変更で追加・更新されているか確認する。
Unit Test が必要な局所処理に追加されているか確認する。
docs の更新が実装と一致しているか確認する。
この checklist は、形式確認ではなく境界確認として使う。

## 29. MVP で広げない範囲

MVP では、エージェント実行をしない。
MVP では、PR コメント投稿をしない。
MVP では、コード自動修正をしない。
MVP では、`test-map.yaml` の完全自動更新をしない。
MVP では、OpenAPI の高度な差分解析をしない。
MVP では、trace からのテスト自動生成をしない。
MVP では、Smithy / AsyncAPI / Protobuf / gRPC adapter を扱わない。
MVP では、`message` / `job` / `file` kind を扱わない。
MVP では、function の実コード存在確認をしない。
MVP では、言語別静的解析をしない。
MVP では、dashboard 上で正本編集しない。
便利そうに見えても、MVP の責務境界を広げない。

## 30. 判断に迷ったとき

まず、人間の意味判断か、機械的検証かを分ける。
次に、正本成果物がどこにあるかを確認する。
その処理の所有 package を確認する。
system と component の境界を越えていないか確認する。
Operation Directory に寄せるべき参照ではないか確認する。
CLI に置くべき orchestration か、本体ロジックか確認する。
Output に置くべき整形か、判断か確認する。
既存ファイルを安全に扱えているか確認する。
Contract Test で固定すべき公開挙動か確認する。
MVP の範囲を越えていないか確認する。
Accay の価値は、受け入れ判断の材料を安定して揃えることにある。
実装者は、便利な自動判断を増やすよりも、境界を守り、証拠を揃え、利用者が安全に判断できる状態を作る。
