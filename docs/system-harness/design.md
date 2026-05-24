# System Harness 基本設計

## 1. 役割

System Harness は、system side の validation と desk-debug context の材料選定を担当する component である。

system side は、業務シナリオがどの operation 列として流れるかを扱う。component の受け入れケースや test-map には依存しない。

## 1.1 Interface semantics

公開 operation の意味論は [semantics.md](semantics.md) を正本とする。
この design は、その意味論を system validation、Operation Directory lookup、schema validation、context source 選定としてどう実現するかを定義する。

## 2. 責務境界

### 責務

- `accay system validate` の本体処理を担う。
- `accay validate` に含まれる system validation を担う。
- trace が参照する `component + operation` を Operation Directory へ問い合わせる。
- trace `input.value` / `output.value` の schema validation を行う。
- HTTP status / CLI exit code を operation contract と照合する。
- observations の最低限チェックを行う。
- desk-debug context の材料を選定する。

### 非責務

- component acceptance case の状態判定。
- `test-map.yaml` と JUnit XML の照合。
- component regression result の解釈。
- 机上デバッグの最終的な意味判断。
- context Markdown の最終整形。

## 3. System validation

System validation は、機械的に確認できる整合性を扱う。

主な検証:

- scenario が存在するか。
- sequence が存在するか。
- trace YAML が読めるか。
- trace step id が重複していないか。
- trace step の `component + operation` が解決できるか。
- `input.schema_ref` / `output.schema_ref` が解決できるか。
- `input.value` / `output.value` が schema に合致するか。
- `kind: http` の status が operation contract に存在するか。
- `kind: cli` の exit code が operation contract に存在するか。
- observations が空でないか。

意味保存条件の妥当性は判断しない。

## 4. Operation Directory との関係

System Harness は、trace step ごとに Operation Directory へ問い合わせる。

問い合わせるもの:

- component が存在するか。
- operation が存在するか。
- operation kind。
- input / output schema ref。
- HTTP status code。
- CLI exit code。

System Harness は component の `acceptance-scope.yaml` や `test-map.yaml` を読まない。必要な契約情報は Operation Directory から得る。

## 5. Diagnostics

| severity | 例 |
|---|---|
| error | operation 不存在、schema validation failure、schema file 不存在 |
| warning | observations 空、sequence 不在、任意情報の欠落 |
| info | 検証対象数、context 出力先 |

diagnostics には、scenario ID、trace path、step id、component、operation を含める。

## 6. Desk-debug context

desk-debug context は、trace 草案や trace 更新案を作るための入力である。

含めるもの:

- scenario。
- sequence。
- 既存 trace。
- trace が参照する operation contract。
- 必要に応じた component semantics の抜粋。

component semantics は参考情報であり、system の正本ではない。

Output & Presentation が最終的な `context.md` に整形する。

## 7. 処理フロー

`accay system validate`:

1. System Artifacts から system model を受け取る。
2. Operation Directory を受け取る。
3. scenario / sequence / trace の対応を確認する。
4. trace step を順に検証する。
5. diagnostics を返す。

`accay system pack desk-debug`:

1. 対象 scenario を決める。
2. scenario / sequence / trace を集める。
3. 関連 operation contract を集める。
4. context source を返す。

## 8. 失敗モード

| 失敗 | 扱い |
|---|---|
| trace が読めない | error |
| operation がない | error |
| schema validation failure | error |
| status code 不一致 | error |
| observations 空 | warning |
| semantics が見つからない | context では省略、validation では扱わない |

## 9. テスト観点

Contract Test:

- 不正 trace で `accay system validate` が error を返す。
- valid trace で pass する。
- desk-debug context が scenario / sequence / operation contract を含む。

Unit Test:

- step id 重複検出。
- operation lookup failure。
- schema validation failure。
- HTTP status / CLI exit code 検証。
- diagnostics の location 生成。

## 10. 実装メモ

- System Harness は component artifact loader に依存しない。
- schema validation wrapper は Operation Directory から schema を受け取る。
- context source は Markdown ではなく構造化データとして Output に渡す。
- validation は全 step を走査し、可能な限り複数 diagnostics を返す。

## 11. Validation policy

System Harness は、機械的に確認できるものを厳密に扱う。

| 対象 | error | warning |
|---|---|---|
| scenario | 必須 file が読めない | sequence が任意扱いの場合の欠落 |
| trace | YAML 不正、steps 不正 | observations が薄い |
| operation | lookup 不能 | deprecated metadata がある場合 |
| schema | ref 不存在、validation failure | schema が緩すぎる場合 |
| status / exit code | contract に存在しない | 未指定だが判断可能な場合 |

意味的に正しいかどうかは `needs_review` 相当の report 表現に寄せ、error と混同しない。

## 12. Context source の粒度

desk-debug context source は、大きすぎるとエージェントが焦点を失う。

優先順位:

1. 対象 scenario。
2. 対応 sequence。
3. 既存 trace。
4. trace が参照する operation contract。
5. operation に関係する semantics 抜粋。
6. 関連する diagnostics。

全 component の semantics を丸ごと入れない。必要な component / operation に絞る。

## 13. 完了条件

System Harness の実装は、以下を満たしたら MVP として十分である。

- valid trace が pass する。
- missing operation が error になる。
- schema validation failure が error になる。
- observations 欠落が warning になる。
- desk-debug context source を Output に渡せる。
