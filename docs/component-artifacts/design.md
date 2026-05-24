# Component Artifacts 基本設計

## 1. 役割

Component Artifacts は、component side の正本成果物を読み取り、Component Harness と Component Regression が扱える構造へ変換する component である。

component side は、個別コンポーネントの責務、契約、受け入れケース、テスト証拠を扱う。system trace は必須入力にしない。

## 1.1 Interface semantics

公開 operation の意味論は [semantics.md](semantics.md) を正本とする。
この design は、その意味論を component discovery、scope / test-map 読み取り、interface path の受け渡しとしてどう実現するかを定義する。

## 2. 正本ファイル

```text
docs/acceptance/components/{component}/
  acceptance-scope.yaml
  test-map.yaml
  semantics.md
  review-guidelines.md
  interfaces/
    openapi.yaml
    operations.yaml
    schemas/
```

| ファイル | 役割 |
|---|---|
| `acceptance-scope.yaml` | 受け入れケース台帳 |
| `test-map.yaml` | 受け入れ証拠と JUnit testcase の対応 |
| `semantics.md` | component と operation の意味論 |
| `review-guidelines.md` | component 固有のレビュー観点 |
| `interfaces/*` | operation contract の入力 |

## 3. 責務境界

### 責務

- component directory を発見する。
- `acceptance-scope.yaml` を読み取る。
- `test-map.yaml` を読み取る。
- `semantics.md` と `review-guidelines.md` を参照可能にする。
- `interfaces/*` の path を Operation Directory へ渡せるようにする。
- component model、acceptance case、test mapping を返す。

### 非責務

- system trace の読み取り。
- operation contract の正規化。
- JUnit XML の集計。
- acceptance review の意味判断。
- test-map の自動更新。

## 4. Component discovery

component 名は `docs/acceptance/components/{component}/` の directory 名を基本とする。

discovery では以下を行う。

- components directory を deterministic に sort する。
- directory だけを component 候補にする。
- missing file は loader で落とさず、Harness が diagnostics 化できる情報を残す。

## 5. `acceptance-scope.yaml`

読み取る主な項目:

- component 名。
- case ID。
- title。
- priority。
- status。
- scenarios。
- operations。

Component Artifacts は status の意味判断をしない。許可値チェックは Component Harness が行う。

## 6. `test-map.yaml`

読み取る主な項目:

- component 名。
- mapping の case ID。
- JUnit `classname`。
- JUnit `name`。
- `verifies`。

`classname + name` を testcase の照合キーとして保持する。

## 7. semantics と interfaces

`semantics.md` は意味論の正本である。ただし、機械的に意味判断する対象ではない。

`interfaces/*` は Operation Directory の入力である。Component Artifacts は path を渡すだけで、operation catalog の構築は行わない。

## 8. 他 component との関係

| 相手 | 関係 |
|---|---|
| Component Harness | component model を渡す |
| Component Regression | test mapping を渡す |
| Operation Directory | interfaces path を渡す |
| System Artifacts | 直接依存しない |
| Output | 直接依存しない |

## 9. エラーの扱い

| 状況 | 扱い |
|---|---|
| scope が読めない | read error として保持 |
| test-map が読めない | read error として保持 |
| semantics がない | Component Harness で diagnostics |
| interfaces がない | Operation Directory / Harness で diagnostics |
| system trace がない | 問題にしない |

## 10. テスト観点

Contract Test:

- component 一覧を発見できる。
- scope / test-map を regression に渡せる。

Unit Test:

- YAML 読み取り。
- case ID の保持。
- JUnit key の保持。
- missing file の扱い。
- path の root 相対化。

## 11. 実装メモ

- loader は validation をやりすぎない。
- raw data と normalized model の境界は実装で決めてよい。
- system trace を便利だからといってここで読まない。
- test-map の自動修正は MVP では行わない。

## 12. Model に残すべき情報

Component Harness と Component Regression のため、次の情報を落とさない。

- component directory path。
- scope source path。
- test-map source path。
- semantics path。
- interface directory path。
- case ID。
- case status。
- mapped testcase key。
- verifies。
- YAML parser error。

特に source path は diagnostics と review context の品質に影響する。

## 13. 読み取りと検証の分離

Component Artifacts は loader である。

ここで行う:

- file discovery。
- YAML 読み取り。
- raw structure の保持。
- 最低限の model 化。

ここで行わない:

- status 許可値判定。
- case ID 参照判定。
- verifies 必須判定。
- operation contract 判定。

これらは Component Harness が行う。

## 14. 完了条件

- component 一覧を安定順で返せる。
- scope / test-map を読み取れる。
- missing file を diagnostics 化できる材料として返せる。
- interfaces path を Operation Directory に渡せる。
- system trace なしで動作する。
