# Component Regression 基本設計

## 1. 役割

Component Regression は、JUnit XML と `test-map.yaml` を照合し、component の受け入れ済みケースの保証が壊れていないかを集計する component である。

system trace は直接の入力にしない。top-level regression は、全 component の regression result を集約するだけである。

## 1.1 Interface semantics

公開 operation の意味論は [semantics.md](semantics.md) を正本とする。
この design は、その意味論を JUnit result set、test-map matching、case-level aggregation としてどう実現するかを定義する。

## 2. 責務境界

### 責務

- 1 つ以上の JUnit XML を読み取る。
- JUnit testcase を `classname + name` で一意化する。
- 複数 JUnit XML の test result set をマージする。
- duplicate testcase を validate error にする。
- `test-map.yaml` の mapping と JUnit result を照合する。
- case 単位の pass / fail / error / skipped / missing を集計する。
- accepted case の failed / error / skipped / missing を regression failure として扱う。
- regression result を Output に渡す。

### 非責務

- 失敗原因の意味解釈。
- 修正案作成。
- test-map の自動更新。
- system trace の読み取り。
- report の最終整形。

## 3. JUnit result set

JUnit XML は、すべての file を 1 つの result set にまとめる。

key:

```text
classname + name
```

同じ key が複数出た場合、MVP では error にする。最新結果で上書きしたり、同名 test を merge したりしない。

## 4. Matching

`test-map.yaml` は case ID から JUnit testcase への mapping を持つ。

照合手順:

1. component の test-map を読む。
2. mapping ごとに `classname + name` を作る。
3. JUnit result set で lookup する。
4. 見つかれば testcase status を case result に反映する。
5. 見つからなければ missing とする。

JUnit XML に存在するが test-map にない testcase は unmapped として扱う。

## 5. 判定

| 判定 | 意味 |
|---|---|
| pass | mapped test が成功している |
| fail | mapped test が失敗している |
| error | mapped test が error になっている |
| skipped | mapped test が skip されている |
| missing | test-map にある testcase が JUnit XML に存在しない |
| unmapped | JUnit XML にはあるが test-map にない |

case に複数 test がある場合は、最も重い状態を case status に反映する。

## 6. デフォルト policy

| 条件 | 扱い |
|---|---|
| accepted case + failed/error | fail |
| accepted case + missing | fail |
| accepted case + skipped | fail |
| non-accepted case + failed/error | warning / report only |
| unmapped test | info |

policy は `.accay/config.yaml` で後から調整可能にする。

## 7. Top-level と component-level

`accay component regression <component>` は、指定 component のみを対象にする。

`accay regression` は、全 component に対して component regression を実行し、結果を集約する。

どちらも system trace は直接読まない。

## 8. Output への handoff

Output に渡す result には以下を含める。

- component 名。
- case ID。
- case status。
- mapped testcase。
- missing testcase。
- unmapped testcase。
- policy 判定。
- diagnostics。

Output はこれを Markdown / HTML に整形する。

## 9. 失敗モード

| 失敗 | 扱い |
|---|---|
| JUnit XML が読めない | error |
| duplicate testcase | error |
| mapped testcase missing | case result missing |
| accepted case skipped | fail |
| test-map が読めない | Component Artifacts / Harness 側 error |

## 10. テスト観点

Contract Test:

- accepted case の missing で regression が fail になる。
- duplicate testcase で error になる。
- unmapped test が info として report される。

Unit Test:

- JUnit XML parser。
- status 判定。
- mapping lookup。
- case aggregation。
- policy application。

## 11. 実装メモ

- XML parser は標準 library または安定した parser を使う。
- testcase key は正規化ルールを明示する。
- result aggregation と report rendering を混ぜない。
- failure の意味解釈はエージェント / 人間に残す。

## 12. Result model の要点

Output に渡す result は、report 生成に必要な情報を持つ。

component result:

- component 名。
- overall status。
- case results。
- unmapped tests。
- diagnostics。

case result:

- case ID。
- acceptance status。
- regression status。
- mapped tests。
- missing tests。
- verifies。

test result:

- classname。
- name。
- status。
- failure message の要約。

## 13. 集計ルール

case に複数 test がある場合の優先順位:

```text
error > fail > missing > skipped > pass
```

ただし policy により、accepted case の `missing` と `skipped` は fail 扱いになる。

unmapped test は case result には入れず、component result の info として扱う。

## 14. 完了条件

- JUnit XML を複数読める。
- duplicate testcase を error にできる。
- test-map と照合できる。
- accepted case の missing / skipped を fail にできる。
- report rendering に必要な result を Output に渡せる。
