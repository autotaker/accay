# Output & Presentation 基本設計

## 1. 役割

Output & Presentation は、diagnostics、context source、regression result を、人間とエージェントが読める形へ整形する shared component である。

表示とファイル出力だけを担当し、validation / regression の本体ロジックは持たない。

## 1.1 Interface semantics

公開 operation の意味論は [semantics.md](semantics.md) を正本とする。
この design は、その意味論を diagnostics formatting、context rendering、report rendering、local viewer としてどう実現するかを定義する。

## 2. 責務境界

### 責務

- diagnostics summary を CLI 表示用に整形する。
- desk-debug context を Markdown として出力する。
- acceptance review context を Markdown として出力する。
- regression report を Markdown / HTML として出力する。
- generated report を `accay serve` で表示する。
- `.accay/runs/{run-id}/` と `.accay/reports/` への出力を管理する。

### 非責務

- system / component の正本ファイルを直接読んで判断すること。
- validation / regression の診断ロジック。
- acceptance case の状態更新。
- test-map の承認 UI。
- proposal の適用 UI。

## 3. 出力先

```text
.accay/
  runs/
    {run-id}/
      context.md
      review-report.md
      decision.yaml
      proposed/
  reports/
    html/
    markdown/
```

MVP で必須なのは `context.md` と regression / validation report である。review-report や decision は受け入れレビュー運用で使う出力先として確保する。

## 4. Diagnostics formatting

CLI summary では、severity ごとに簡潔に表示する。

表示に含めるもの:

- severity。
- message。
- source path。
- scenario / component / case ID。
- operation。
- report path。

Output は diagnostics の severity を決めない。各 harness / regression から渡された severity を整形する。

## 5. Context rendering

context は、エージェントや人間が次の判断をするための Markdown である。

種類:

- desk-debug context。
- acceptance review context。

Output は context source を受け取り、読みやすい section に並べる。何を含めるべきかの判断は System Harness / Component Harness が持つ。

## 6. Report rendering

Markdown report:

- CI log やエージェント入力として読みやすくする。
- case ID、component、status、diagnostics を明示する。
- 長い本文より、判断に必要な要点を優先する。

HTML report:

- 人間がブラウザで確認するための表示。
- MVP では静的 report を基本にする。
- 大規模な編集 UI は持たない。

## 7. `accay serve`

`serve` は生成済み report を表示する薄い viewer とする。

やること:

- report directory を読む。
- local server を起動する。
- dashboard HTML を返す。

やらないこと:

- 正本 artifact の編集。
- test-map の承認。
- proposal の適用。
- validation / regression の再計算。

## 8. Run ID

run ID は `.accay/runs/{run-id}/` の directory 名として使う。

要件:

- ある程度人間が読める。
- 同じ実行で一貫する。
- テストで正規化できる。

例:

```text
2026-05-24T120000Z-order-domain-ORD-001
```

## 9. 失敗モード

| 失敗 | 扱い |
|---|---|
| 出力先 directory が作れない | error |
| context source が不完全 | warning を含めて出力 |
| report rendering 失敗 | error |
| serve 対象 report がない | user-facing error |

## 10. テスト観点

Contract Test:

- context.md が指定 run directory に出力される。
- regression report が Markdown / HTML に出力される。
- `serve` が生成済み report を表示できる。

Unit Test:

- diagnostics formatting。
- run ID 正規化。
- report path 生成。
- context section rendering。

## 11. 実装メモ

- Output から artifact loader を呼ばない。
- rendering は pure function に寄せる。
- timestamp / absolute path はテストで正規化しやすくする。
- Markdown と HTML の情報量は揃えすぎなくてよいが、判断に必要な status は欠落させない。

## 12. 表示設計の優先順位

Output は、美しい UI よりも判断しやすさを優先する。

優先順位:

1. error / fail がすぐ見える。
2. 対象 component / scenario / case がわかる。
3. source path が辿れる。
4. 次に見るべき artifact がわかる。
5. エージェントが再入力として使える。

長い説明より、診断対象と根拠を明確にする。

## 13. Context と report の違い

| 種類 | 目的 | 読者 |
|---|---|---|
| context | 判断やレビューの入力 | agent / human |
| report | 実行結果の確認 | human / CI / agent |

context は材料を集める。report は結果を示す。両者を混ぜない。

## 14. 完了条件

- diagnostics summary を CLI に返せる。
- context.md を run directory に出力できる。
- Markdown report を出力できる。
- HTML report を出力できる。
- `serve` で生成済み report を表示できる。
- validation / regression logic を持たない。
