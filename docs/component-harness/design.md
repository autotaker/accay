# Component Harness 基本設計

## 1. 役割

Component Harness は、component validation と acceptance review context の材料選定を担当する component である。

component side は、個別 component の成果物に閉じて最低限回る必要がある。system trace は参考情報として扱えるが、正本にはしない。

## 2. 責務境界

### 責務

- `accay component validate <component>` の本体処理を担う。
- `accay validate` に含まれる component validation を担う。
- `acceptance-scope.yaml` の構文と基本項目を検証する。
- `test-map.yaml` の構文と case 参照を検証する。
- `test-map.yaml` の `verifies` が 1 件以上あることを確認する。
- component interfaces を Operation Directory と照合する。
- acceptance review context の材料を選定する。

### 非責務

- JUnit XML と test-map の回帰判定。
- 最終 accept / reject 判断。
- test-map の自動更新。
- system trace を必須入力とする検証。
- review context Markdown の最終整形。

## 3. Component validation

主な検証:

- `acceptance-scope.yaml` が読めるか。
- component 名が directory と矛盾しないか。
- case ID が重複していないか。
- case status が許可値か。
- `test-map.yaml` が読めるか。
- test-map の case ID が scope に存在するか。
- `verifies` が 1 件以上あるか。
- operation reference が Operation Directory で解決できるか。
- input / output schema ref が解決できるか。

component validation は scenario / trace の存在を必須にしない。

## 4. Operation Directory との関係

Component Harness は、interfaces の整合性と operation reference を確認するために Operation Directory を使う。

確認するもの:

- operation ID 重複。
- kind。
- schema ref。
- status code / exit code 定義。

Component Harness は raw OpenAPI や raw `operations.yaml` を直接深く解釈しない。

## 5. Review context

review context は、component の受け入れレビューを行うための入力である。

含めるもの:

- 対象 component。
- 対象 case。
- acceptance-scope。
- test-map。
- semantics。
- interfaces / operation contract。
- 任意の JUnit summary。
- 必要に応じた関連 trace / scenario / sequence。

関連 trace / scenario / sequence は参考情報であり、component validation / regression の正本にはしない。

## 6. Diagnostics

| severity | 例 |
|---|---|
| error | scope 不正、test-map case 不存在、verifies 空、operation 不存在 |
| warning | semantics 不在、review-guidelines 不在、任意 metadata 欠落 |
| info | case 数、mapping 数、context 出力先 |

diagnostics には component、case ID、source file を含める。

## 7. 処理フロー

`accay component validate <component>`:

1. Component Artifacts から component model を受け取る。
2. Operation Directory を受け取る。
3. scope と test-map を検証する。
4. operation / schema reference を検証する。
5. diagnostics を返す。

`accay component pack review`:

1. 対象 component と case ID を決める。
2. component 正本を集める。
3. operation contract を集める。
4. 任意で JUnit summary を受け取る。
5. context source を Output に渡す。

## 8. 失敗モード

| 失敗 | 扱い |
|---|---|
| scope が読めない | error |
| test-map が読めない | error |
| case ID 不一致 | error |
| verifies 空 | error |
| semantics 不在 | warning |
| 関連 trace 不在 | review context では省略 |

## 9. テスト観点

Contract Test:

- 不正 test-map で component validate が error を返す。
- review context が scope / test-map / semantics / interfaces を含む。

Unit Test:

- case ID 参照チェック。
- verifies 必須チェック。
- status 許可値チェック。
- operation lookup failure。
- diagnostics location 生成。

## 10. 実装メモ

- Component Harness は Component Regression を直接実行しない。
- review context に JUnit summary を含める場合も、判定は Regression 側で済ませる。
- context source は Markdown ではなく構造化データとして Output に渡す。
- validation は複数 diagnostics を返す。

## 11. Review context の選別

review context は大きければよいわけではない。

優先順位:

1. 対象 case の scope。
2. 対象 case に紐づく test-map。
3. component semantics。
4. 対象 operation contract。
5. JUnit summary。
6. 関連 trace / scenario / sequence。

関連 trace は参考情報である。review の正本は component artifact に置く。

## 12. Validation policy

| 対象 | error | warning |
|---|---|---|
| scope | YAML 不正、case 重複 | optional field 欠落 |
| test-map | YAML 不正、case 参照不正、verifies 空 | mapped test が古そう |
| semantics | なし | file 不在、operation 説明不足 |
| interfaces | operation 重複、schema ref 不在 | description 欠落 |

warning は review context に残し、人間が判断できるようにする。

## 13. 完了条件

- scope と test-map の基本整合性を診断できる。
- Operation Directory と照合できる。
- review context source を Output に渡せる。
- system trace なしでも component validation が動く。
- related trace を参考情報として扱える。
