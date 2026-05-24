# System Artifacts 基本設計

## 1. 役割

System Artifacts は、system side の正本成果物を読み取り、System Harness が扱える構造へ変換する component である。

対象は、業務シナリオ、シナリオ説明、机上デバッグ trace である。component の acceptance-scope や test-map は読まない。

## 2. 正本ファイル

```text
docs/acceptance/
  scenarios/
    {scenario}.feature
  sequences/
    {scenario}.md
  traces/
    {scenario}.trace.yaml
```

| ファイル | 役割 |
|---|---|
| `scenario.feature` | E2E に近い業務シナリオ |
| `sequence.md` | シナリオ理解のための説明や Mermaid |
| `{scenario}.trace.yaml` | operation 列、input / output、観測点 |

System Artifacts は、これらを system model として返す。validation は System Harness が行う。

## 3. 責務境界

### 責務

- scenario / sequence / trace を発見する。
- scenario ID と path の対応を持つ。
- trace YAML を読み、step の順序を維持する。
- trace step の `component` と `operation` を保持する。
- 読み取り不能な artifact を diagnostics に変換できる形で返す。

### 非責務

- operation の存在確認。
- schema validation。
- component artifact の読み取り。
- JUnit XML の読み取り。
- 机上デバッグの意味判断。

## 4. Discovery rules

基本規則:

- scenario ID は file stem から取る。
- sequence は同じ scenario ID の `.md` を対応候補にする。
- trace は `{scenario}.trace.yaml` を対応候補にする。
- path は repository root からの相対パスとして保持する。

例:

```text
scenarios/order-checkout.feature
sequences/order-checkout.md
traces/order-checkout.trace.yaml
```

この3つは `order-checkout` scenario の system artifact set として扱う。

## 5. Trace model

trace step で保持する主要項目:

- `id`
- `component`
- `operation`
- `input.schema_ref`
- `input.value`
- `output.schema_ref`
- `output.value`
- `output.status`
- `observations`

System Artifacts は値を読み取るだけで、意味や schema 適合は判断しない。

## 6. System Harness への handoff

System Harness へ渡すときに必要な情報:

- scenario の有無。
- sequence の有無。
- trace の有無。
- trace step の raw location。
- trace step の順序。
- schema ref。
- observation list。

location 情報は diagnostics の品質に効くため、可能な限り保持する。

## 7. エラーの扱い

| 状況 | 扱い |
|---|---|
| YAML が読めない | artifact read error として返す |
| trace が list でない | raw structure を保持し Harness に渡す |
| scenario がない | Harness で参照整合性 error |
| sequence がない | Harness で warning または error |
| trace がない | command の目的に応じて Harness が判定 |

System Artifacts は、読めるものまで読んで返す。早すぎる fail は避ける。

## 8. 他 component との関係

| 相手 | 関係 |
|---|---|
| CLI & Workspace | docs root と対象 scenario を受け取る |
| System Harness | system model を渡す |
| Operation Directory | 直接依存しない |
| Component Artifacts | 直接依存しない |
| Output | 直接依存しない |

System Artifacts は loader であり、orchestration は CLI に任せる。

## 9. テスト観点

Contract Test:

- fixture project から scenario / sequence / trace を発見できる。
- trace がない scenario を diagnostics につなげられる。

Unit Test:

- scenario ID の抽出。
- trace YAML の読み取り。
- step 順序の保持。
- 不正 YAML の扱い。
- path の root 相対化。

## 10. 実装メモ

- YAML parser は `safe_load` 相当を使う。
- 読み取り結果は、raw dict と正規化 model のどちらを残すか実装で判断してよい。
- file discovery は deterministic な sort を行う。
- component artifact を便利だからといってここで読まない。

## 11. Model に残すべき情報

System Harness が良い diagnostics を出すには、値だけでなく出所も必要である。

残すべき情報:

- source file path。
- scenario ID。
- trace step index。
- trace step id。
- component / operation。
- schema ref。
- raw value。
- 読み取り時の parser error。

逆に、System Artifacts で計算しないもの:

- operation の存在。
- schema の存在。
- status code の妥当性。
- observations の十分性。

## 12. 代表的な不正入力

| 入力 | System Artifacts の扱い |
|---|---|
| trace YAML が壊れている | read error と source path を保持 |
| steps が配列でない | raw structure を保持して Harness へ渡す |
| step に operation がない | 欠落情報として保持 |
| sequence だけ存在する | scenario 対応の候補として保持 |
| scenario だけ存在する | trace 欠落の判定材料として保持 |

System Artifacts は、可能な限り「読めた部分」を返す。

## 13. 将来拡張の余地

- trace payload の外部 file 参照。
- scenario tag の読み取り。
- sequence 内 Mermaid block の抽出。
- trace と scenario step の粗い対応確認。

これらを追加しても、component artifact を直接読む責務は持たせない。
