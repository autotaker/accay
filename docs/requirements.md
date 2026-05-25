# Accay 要件定義書 v8

作成日: 2026-05-24  
状態: 要件定義フェーズ完了版  
対象: OSS として公開する受け入れ駆動開発支援ツール

---

## 1. 概要

### 1.1 プロダクト名

**Accay**

`Accay` は **Acceptance** と **Assay** を合わせた造語として扱う。

- Acceptance: 変更を受け入れてよいかを判断する
- Assay: 対象を分析・検査して価値や純度を見極める

Accay は、AI コーディングエージェントが生成した変更を、単に「テストが通るか」ではなく、**意味・証拠・責務境界** に基づいて受け入れ可能か確認するためのツールである。

### 1.2 背景

AI コーディングエージェントによって、コードを書く速度は大きく上がる。  
一方で、開発のボトルネックは「コードを書くこと」から、次のような判断に移る。

- その変更は本当に受け入れ条件を満たしているか
- インターフェースの意味を壊していないか
- コンポーネントの責務境界を越えていないか
- テストは受け入れ条件の証拠になっているか
- 過去に受け入れた振る舞いが壊れていないか

Accay は、この受け入れ判断を支援するために、エージェントスキル、テンプレート、軽量ハーネスを提供する。

### 1.3 目的

Accay の目的は、ユーザのリポジトリに導入できる OSS として、AI エージェントによる受け入れ駆動開発を安定化することである。

Accay が提供する価値は次の通り。

- E2E に近い業務シナリオを Gherkin で整理する
- コンポーネント間の協調を Mermaid などで可視化する
- 机上デバッグ用の trace を YAML として管理する
- trace の `input` / `output` が JSON Schema に合致しているか機械的に検証する
- コンポーネント単位の受け入れスコープを管理する
- 受け入れレビューで認定されたテスト証拠を `test-map.yaml` に保存する
- JUnit XML と `test-map.yaml` を照合し、受け入れ済みケースの回帰を検出する
- 人間向け HTML レポートと、エージェント向け Markdown レポートを生成する

### 1.4 用語定義

Accay では、一般的な開発用語だけでなく、以下の独自用語を使う。

| 用語 | 定義 | 補足 |
|---|---|---|
| 机上デバッグ | E2E に近いシナリオを、実装やテスト実行とは独立して、システム全体の operation 列として頭の中で実行し、期待される `input` / `output`、意味の流れ、観測点を整理する工程 | 実行時デバッグではない。成果物は主に `{scenario}.trace.yaml` |
| 机上デバッグ回帰 | 既存の trace に対して、参照整合性や schema validation を機械的に確認し、意味の流れが壊れていないかを点検する工程 | 最低限はハーネスだけで回る。意味判断は必要に応じてエージェントや人間が行う |
| 受け入れレビュー | コンポーネント単位で、変更を受け入れケースとして受け入れてよいかを判定する工程 | 通常のコードレビューではなく、仕様・意味・責務境界・テスト証拠のレビュー |
| 受け入れレビュー回帰 | `acceptance-scope.yaml` と `test-map.yaml` と JUnit XML を照合し、受け入れ済みケースの保証が壊れていないか確認する工程 | 最低限はハーネスだけで回る |
| ハーネス | Accay の機械処理部分。ファイル収集、形式検証、schema validation、JUnit 照合、レポート生成を行う | 業務的な正しさや最終受け入れ判断は行わない |
| エージェントスキル | コーディングエージェントに読ませる Accay 用の手順書・テンプレート群 | `accay install` により設定されたスキルディレクトリへインストールする |

### 1.5 非目的

MVP では以下をやらない。

- エージェント実行基盤になる
- PR コメントを自動投稿する
- コードを自動修正する
- `test-map.yaml` を完全自動更新する
- 仕様変更かバグかを機械だけで判定する
- インターフェースの意味論を完全自動理解する
- trace から受け入れテストを自動生成する
- Web UI を大規模なアプリケーションとして作る
- 言語別の静的解析で `function` の存在や呼び出し順序を厳密検証する
- OpenAPI lint ツールになる

最終的な受け入れ判断は人間が行う。

---

## 2. 基本方針

### 2.1 役割分担

| 役割 | 責務 |
|---|---|
| 人間 | 意味・責務境界・最終受け入れ判断の所有者 |
| エージェント | 草案作成、机上デバッグ、受け入れレビュー、レポート作成 |
| ハーネス | 入力収集、形式検証、JUnit 照合、レポート生成 |

Accay のハーネスは判断主体ではない。  
ハーネスは、エージェントと人間が安定して判断できるように、入力・出力・形式・回帰結果を揃える。

### 2.2 成果物の分離

| 成果物 | 単位 | 位置づけ |
|---|---|---|
| `scenario.feature` | システム全体 | E2E に近い業務シナリオ |
| `sequence.md` | システム全体 | コンポーネント間協調の説明 |
| `{scenario}.trace.yaml` | システム全体 | 机上デバッグ仕様。意味の流れと観測点を表す |
| `acceptance-scope.yaml` | コンポーネント | 受け入れケース台帳 |
| `test-map.yaml` | コンポーネント | 受け入れレビューで認定されたテスト証拠台帳 |
| `semantics.md` | コンポーネント | コンポーネントと operation の意味論 |
| `operations.yaml` | コンポーネント | Accay native の operation 定義 |
| `openapi.yaml` | コンポーネント | HTTP operation を取り込むための外部仕様 |
| JSON Schema | コンポーネント | trace `input` / `output` の構造検証元 |
| JUnit XML | テスト実行 | テスト実行結果 |

### 2.3 Operation 抽象

Accay の基本単位は **endpoint** ではなく **operation** である。

```text
component
  operation
    input schema
    output schema
```

HTTP API では OpenAPI の `operationId` を operation として扱う。  
非 HTTP コンポーネントでは Accay native の `operations.yaml` で operation を定義する。

MVP でサポートする operation kind は以下とする。

| kind | 対象 | 例 |
|---|---|---|
| `http` | HTTP API | `createOrder` |
| `cli` | CLI command | `importUsers` |
| `function` | モノリス内・処理系内の公開 API | `OrderService.createOrder` |

`message` / `job` / `file` / `grpc` / `asyncapi` などは後続フェーズの拡張対象とする。

### 2.4 回帰の原則

回帰はエージェントなしでも最低限回る必要がある。

| 回帰 | ハーネスだけで行うこと | エージェントに任せること |
|---|---|---|
| 机上デバッグ回帰 | trace の参照整合性、`input` / `output` の schema validation | 意味保存条件の解釈、仕様変更かバグかの判断 |
| 受け入れレビュー回帰 | JUnit XML と `test-map.yaml` の照合、case 単位の pass/fail 集計 | 失敗原因の仮説、修正方針、test-map 陳腐化の指摘 |

---

## 3. 導入先リポジトリ構成

### 3.1 長期保守対象

人間も読む成果物は `docs/acceptance/` 以下に置く。

```text
docs/acceptance/
  scenarios/
  sequences/
  traces/
  components/
    {component}/
      acceptance-scope.yaml
      test-map.yaml
      semantics.md
      review-guidelines.md
      interfaces/
        openapi.yaml
        operations.yaml
        schemas/
      reviews/
      reports/
```

### 3.2 設定・生成物・一時ファイル

設定・生成物・一時ファイルは `.accay/` 以下に置く。

```text
.accay/
  config.yaml
  templates/
  runs/
  reports/
    html/
    markdown/
  generated/
  cache/

.agents/
  skills/
    accay-interface-semantics/
    accay-desk-debugging/
    accay-acceptance-review/
    accay-acceptance-report/
```

### 3.3 配置ルール

| 置き場所 | 内容 | 性質 |
|---|---|---|
| `docs/acceptance/scenarios/` | Gherkin scenario | 長期保守対象 |
| `docs/acceptance/sequences/` | Mermaid 等を含む Markdown | 長期保守対象 |
| `docs/acceptance/traces/` | 机上デバッグ trace | 長期保守対象 |
| `docs/acceptance/components/{component}/` | scope / map / semantics / interfaces | 長期保守対象 |
| `.accay/runs/` | review context、decision、更新案など | 一時成果物 |
| `.accay/reports/` | HTML / Markdown レポート | 生成物 |
| `.agents/skills/accay-*` | エージェントスキル | コーディングエージェントが読む運用層。インストール先は設定可能 |

`.accay/` は Accay の設定・生成物・一時ファイルを置く場所であり、コーディングエージェントが自動的に読む前提にはしない。
エージェントスキルは `accay install` により、`.accay/config.yaml` で指定されたスキルインストール先へ配置する。
デフォルトのインストール先は `.agents/skills/` とし、スキル名には衝突回避のため `accay-` prefix を付ける。

---

## 4. Operation Contract

### 4.1 位置づけ

コンポーネントの公開契約は以下に置く。

```text
docs/acceptance/components/{component}/interfaces/openapi.yaml
docs/acceptance/components/{component}/interfaces/operations.yaml
docs/acceptance/components/{component}/interfaces/schemas/*.schema.json
```

Accay は OpenAPI 専用ツールではない。  
OpenAPI は `kind: http` の operation を Accay の内部モデルに取り込むための adapter として扱う。  
`operations.yaml` は Accay native の operation 定義形式として扱う。

MVP では以下をサポートする。

| 入力形式 | 対象 | 備考 |
|---|---|---|
| `openapi.yaml` | `kind: http` | OpenAPI の `operationId` を operation ID として読む |
| `operations.yaml` | `kind: http` / `cli` / `function` | 非 HTTP も含む Accay native 形式 |
| JSON Schema | 独自型 / trace `input` / `output` | operation 境界の独自型定義と trace value の検証に使う |

### 4.2 OpenAPI の扱い

MVP で OpenAPI から読むものは限定する。

- `operationId` の一覧
- `operationId` の存在確認
- request / response schema の参照
- HTTP status code の存在確認

MVP で深く読まないもの。

- security scheme
- server URL
- auth flow
- examples
- detailed description
- OpenAPI 差分解析
- `oneOf` / `anyOf` の高度な意味解釈

OpenAPI は HTTP operation catalog として扱い、意味論の正本にはしない。  
意味論は `semantics.md` に書く。

### 4.3 operations.yaml の扱い

`operations.yaml` は HTTP 以外の境界を扱うための Accay native 形式である。  
HTTP でも OpenAPI を持たないプロジェクトでは `operations.yaml` を使える。

MVP で機械的に読む必須項目は以下。

- `component`
- `operations.{operationId}.kind`

`schema_refs` は、operation 境界に現れる Accay 独自型名から JSON Schema への参照辞書である。
独自型がない operation では省略してよい。
`Path` / `str` / `int` / `bool` などの標準的な型には schema 参照を付けない。
1つの schema file には `$defs` で複数の独自型をまとめてよい。

例:

```yaml
signature: loadComponentArtifacts(components_root: Path, component: str) -> ComponentArtifactSet
schema_refs:
  ComponentArtifactSet: docs/component-artifacts/interfaces/schemas/component-artifacts.yaml#/$defs/ComponentArtifactSet
```

kind 別の追加項目。

| kind | 項目 | MVPでの扱い |
|---|---|---|
| `http` | `method`, `path`, `status_codes` | `status_codes` は検証対象 |
| `cli` | `command`, `positional_arguments`, `parameters`, `environment_variables`, `standard_streams`, `exit_codes` | `command` は CLI help / usage 風の表記。`exit_codes` は検証対象 |
| `function` | `signature`, `schema_refs`, `errors` | `signature` は型付きで書く。独自型は `schema_refs` で参照する。実コード検証はしない |

`kind: cli` の `positional_arguments` / `parameters` / `environment_variables` は配列で表す。
`positional_arguments` は順序が意味を持つため、辞書ではなく配列を正本にする。
可変長 positional を扱う場合は `arity: zero_or_more` または `arity: one_or_more` とし、原則として最後の positional に限定する。

CLI の `command` は実行ログではなく、標準的な help / usage に出る構文として書く。

```yaml
command: accay component regression <component> [--junit <path>]... [--root <path>]
```

標準入出力は `standard_streams` で表す。
使用しない stream は `null` とする。
使用する stream は `media_type` で表し、MVP では多くの CLI output を `text/plain` として扱う。
stdout / stderr の完全な構造化 schema は必須にしない。

### 4.4 operationId の一意性

同一 component 内で operation ID は一意でなければならない。

- OpenAPI 由来の `operationId` と `operations.yaml` の operation ID が重複した場合、`validate` は error にする
- MVP では override / merge / namespace は持たない
- trace は `component + operation` で operation を一意に解決する

### 4.5 kind ごとの方針

| kind | 方針 |
|---|---|
| `http` | OpenAPI を使う場合は `operationId` を operation ID として扱う。OpenAPI がない場合は `operations.yaml` に書ける。 |
| `cli` | argv / env / stdin / files / stdout / stderr / exit code などの実体を、受け入れ上重要な `input` / `output` の JSON 表現に正規化して扱う。 |
| `function` | モノリス内や処理系内の公開 API を表す。`signature` や `errors` は人間・AI向け参照情報として扱い、実コード検証はしない。 |

### 4.6 JSON Schema の扱い

CLI / function の場合も、`input` / `output` の正規化表現を JSON として扱い、JSON Schema で検証する。

JSON Schema は以下に使う。

- `trace.yaml` の `input.value` の構造検証
- `trace.yaml` の `output.value` の構造検証
- HTTP / CLI / function を横断した共通の payload validation

JSON Schema で表しにくい副作用や意味は `trace.yaml` の `observations` と `semantics.md` に書く。

---

## 5. Acceptance Artifacts

### 5.1 Scenario

```text
docs/acceptance/scenarios/{scenario}.feature
```

Gherkin 形式で書く。  
E2E に近い業務シナリオを表す。

### 5.2 Sequence

```text
docs/acceptance/sequences/{scenario}.md
```

Markdown と Mermaid などで、コンポーネント間の協調を説明する。

- 人間と AI が読めればよい
- 機械処理の正本にはしない
- シナリオの理解補助として扱う

### 5.3 Trace

```text
docs/acceptance/traces/{scenario}.trace.yaml
```

机上デバッグ用 YAML。  
実行ログではなく、期待される意味の流れを表す。

主な責務。

- シナリオ実行時にどの operation が呼ばれるかを記述する
- 各 operation の `input` / `output` がどの schema に合致すべきかを記述する
- どの値・状態・呼び出しを観測すべきかを記述する
- 意味保存条件や注意すべき観測点を記述する

決定事項。

- schema 参照はリポジトリ直下からの相対パス
- endpoint ではなく operation を参照する
- trace では `request/response` ではなく `input/output` を使う
- kind は trace ではなく operation 定義側に持つ

### 5.4 semantics.md

```text
docs/acceptance/components/{component}/semantics.md
```

コンポーネントごとに 1 つだけ置く。  
operation ごとにファイル分割しない。

書く内容。

- コンポーネント全体の責務
- ドメイン概念
- operation ごとの意味
- field ごとの意味
- 保持すべき不変条件
- 禁止される変換
- downstream call で保持すべき意味
- よくある誤解

### 5.5 acceptance-scope.yaml

```text
docs/acceptance/components/{component}/acceptance-scope.yaml
```

コンポーネント単位の受け入れケース台帳。  
正本は YAML とする。

理由。

- 進捗ボードを出したい
- status 集計したい
- component / scenario / operation / review の紐づきを扱いたい
- Markdown 正本では集計がつらい

status は MVP では最小限とする。

| status | 意味 |
|---|---|
| `draft` | 草案 |
| `ready` | 実装・レビュー対象として準備済み |
| `accepted` | 受け入れ済み |
| `blocked` | ブロック中 |
| `deprecated` | 廃止 |

`implemented` や `reviewed` は PR / run 側の一時状態として扱い、MVP の `acceptance-scope.yaml` には持たせない。

### 5.6 test-map.yaml

```text
docs/acceptance/components/{component}/test-map.yaml
```

受け入れレビューで認定されたテスト証拠台帳。  
これは Dev 成果物ではない。  
Review / QA が作成・更新案を出し、人間が承認する。

役割。

- 受け入れケースと JUnit testcase を紐づける
- 受け入れ済みケースの回帰に使う
- 「このテストは何を保証するか」を記録する

決定事項。

- `mappings` は配列ではなく辞書
- acceptance / regression の分類はしない
- 独自 test id は持たない
- path は MVP では持たない
- JUnit XML の `classname + name` で照合する
- `verifies` は自由記述の短文リストとする
- `verifies` は 1 件以上必須とする
- `verifies` の記述言語は `.accay/config.yaml` で指定できる

### 5.7 Review Artifacts

受け入れレビューの一時成果物は `.accay/runs/{run-id}/` に置く。

```text
.accay/runs/{run-id}/
  context.md
  review-report.md
  decision.yaml
  proposed/
    test-map.yaml
    acceptance-scope.yaml
```

方針。

- MVP では独自 patch DSL を持たない
- Review / QA は更新後の `test-map.yaml` / `acceptance-scope.yaml` を `proposed/` に出す
- 人間は現行ファイルとの差分を確認して取り込む
- 回帰は review 成果物を読まず、現在の `acceptance-scope.yaml` と `test-map.yaml` だけを読む
- 必要に応じて、レビュー本文や decision を `docs/acceptance/components/{component}/reviews/` や `reports/` に長期保存する

---

## 6. ワークフロー

Accay の主要ワークフローは 4 つ。

| 系統 | フェーズ | 単位 | 主な問い |
|---|---|---|---|
| 机上デバッグ | 作成 | システム全体 | このシナリオは意味的に破綻なく流れるか |
| 机上デバッグ | 回帰 | システム全体 | 既存シナリオの意味の流れが壊れていないか |
| 受け入れレビュー | 作成 | コンポーネント | この変更を受け入れてよいか |
| 受け入れレビュー | 回帰 | コンポーネント | 受け入れ済みケースの保証が壊れていないか |

### 6.1 机上デバッグ

E2E シナリオに沿って、システム全体の意味の流れを確認する。

| 項目 | 内容 |
|---|---|
| 入力 | scenario, sequence, components の semantics / interfaces / schemas, 既存 trace |
| 人間 | シナリオの目的、業務的意味、責務境界、trace の承認 |
| エージェント | シナリオをステップごとに机上実行し、保存すべき値・観測点・破綻候補を抽出 |
| ハーネス | 関連ファイル収集、desk-debug context pack 生成、trace 構文チェック |
| 成果物 | `docs/acceptance/traces/{scenario}.trace.yaml` |

必要なら一時レポートを出す。

```text
.accay/runs/{run-id}/desk-debug-report.md
```

### 6.2 机上デバッグ回帰

既存のシステム横断シナリオに対して、機械的に検証できる整合性を確認する。  
MVP では意味判断そのものは機械判定しない。

ハーネスだけで行うこと。

- trace が参照する scenario が存在するか確認する
- trace が参照する component が存在するか確認する
- trace が参照する operation が存在するか確認する
- trace が参照する schema が存在するか確認する
- trace 内の step id が重複していないか確認する
- `input.value` が `input.schema_ref` に合致するか検証する
- `output.value` が `output.schema_ref` に合致するか検証する
- `kind: http` の場合、HTTP status が operation 定義または OpenAPI に存在するか確認する
- `kind: cli` の場合、exit code が operation 定義に存在するか確認する
- observations が空でないか最低限確認する

エージェントに任せること。

- 意味保存条件が本当に壊れていないか判断する
- 仕様変更かバグか判断する
- trace 更新案を作る
- 影響を受ける scenario を説明する

判定。

| 判定 | 意味 |
|---|---|
| `pass` | 機械的な整合性は維持されている |
| `fail` | schema validation や参照整合性に失敗した |
| `warning` | 機械的には通るが、空の observation など注意点がある |
| `needs_review` | 意味判断が必要 |

### 6.3 受け入れレビュー

コンポーネント単位で、次を判断する。

```text
この変更を、そのコンポーネントの受け入れケースとして受け入れてよいか
```

通常のコードレビューではなく、仕様・意味・責務境界レビューである。

| 項目 | 内容 |
|---|---|
| 入力 | component の scope / test-map / semantics / interfaces / schemas, 関連 trace / scenario / sequence, diff, tests, JUnit XML |
| 人間 | accept/reject の最終判断、test-map 更新案の承認、scope 状態更新案の承認、責務境界の裁定 |
| エージェント | 差分・テスト・trace・semantics を読み、証拠認定、違反指摘、test-map 更新案、findings report を作成 |
| ハーネス | review context pack 生成、JUnit XML 読み取り、既存 test-map 照合、review report 形式チェック |
| 成果物 | decision, findings report, proposed test-map, proposed acceptance-scope |

レビュー観点。

- acceptance-scope を満たしているか
- trace.yaml の意味保存条件を壊していないか
- コンポーネント責務を越境していないか
- 受け入れテストが証拠になっているか
- scenario / sequence / trace / implementation が矛盾していないか
- `test-map.yaml` に登録すべきテスト証拠があるか

主目的ではないもの。

- 細かい命名
- インデント
- 好みの設計
- 微細な最適化
- 「もっと綺麗に書ける」レベルの指摘

### 6.4 受け入れレビュー回帰

受け入れ済みケースの保証が壊れていないかを見る。  
これは JUnit XML と `test-map.yaml` を使って、エージェントなしで最低限回せる。

ハーネスが行うこと。

- `test-map.yaml` を読む
- 1つ以上の JUnit XML を読む
- 全 JUnit XML を 1 つの test result set としてマージする
- `classname + name` で testcase を照合する
- 同じ `classname + name` が複数出た場合は validate error とする
- case ごとに pass / fail / skipped / missing を集計する
- accepted 済み case の fail / skipped / missing を検出する
- HTML / Markdown の回帰レポートを出す

エージェントに任せること。

- regression report を読む
- fail / missing / skipped の意味を解釈する
- どの受け入れケースが危険か説明する
- 必要なら原因調査の仮説を出す
- `test-map.yaml` の陳腐化を指摘する

判定。

| 判定 | 意味 |
|---|---|
| `pass` | mapped tests がすべて通っている |
| `fail` | mapped test が失敗している |
| `error` | mapped test が error になっている |
| `missing` | `test-map.yaml` にある testcase が JUnit XML に存在しない |
| `skipped` | mapped test が skip されている |
| `unmapped` | JUnit XML にはあるが `test-map.yaml` にない |

CI での fail / warning / info ルールは `.accay/config.yaml` で設定できる。

推奨デフォルト。

| 条件 | 判定 |
|---|---|
| accepted case + failed/error | fail |
| accepted case + missing | fail |
| accepted case + skipped | fail |
| non-accepted case + failed/error | warning / report only |
| unmapped test | info |

---

## 7. ハーネス機能要件

### 7.1 設定ファイル

```text
.accay/config.yaml
```

設定ファイルは、docs root、JUnit XML の既定パス、回帰判定ルール、レポート出力先、生成文書の言語を定義する。

主要設定。

- `docs_root`
- `skills.install_dir`
- `junit.paths`
- `regression.*`
- `reports.html_dir`
- `reports.markdown_dir`
- `language.verifies`
- `language.reports`

### 7.2 コマンド構造

Accay の CLI は、システム全体の操作とコンポーネント単位の操作を分ける。

#### Top-level

CI やダッシュボード向けの集約操作。

```bash
accay init
accay install
accay validate
accay regression --junit <path>
accay serve
```

#### System-level

シナリオ / シーケンス / trace / 机上デバッグを扱う。

```bash
accay system validate
accay system pack desk-debug --scenario <scenario>
```

#### Component-level

acceptance-scope / semantics / test-map / 受け入れレビュー / 回帰を扱う。

```bash
accay component validate <component>
accay component pack review <component> --case <case-id>
accay component regression <component> --junit <path>
```

### 7.3 validate

`accay validate` は、system validate と全 component validate をまとめて実行する。

検証対象。

- ディレクトリ構成
- scenario / sequence / trace の対応
- component の存在
- operation の存在
- 同一 component 内の operation ID 重複
- OpenAPI / operations.yaml / JSON Schema の存在
- `acceptance-scope.yaml` の構文
- `test-map.yaml` の構文
- trace `input` / `output` の schema validation
- `test-map.yaml` の case ID が `acceptance-scope.yaml` に存在するか
- `test-map.yaml` の `verifies` が空でないか

### 7.4 regression

`accay regression` は、全 component に対して受け入れレビュー回帰を実行する。  
`accay component regression <component>` は、指定 component のみを対象にする。

入力。

- `acceptance-scope.yaml`
- `test-map.yaml`
- 1つ以上の JUnit XML

出力。

- component 単位の回帰結果
- case 単位の pass / fail / error / skipped / missing
- HTML / Markdown レポート

### 7.5 pack

`pack` はエージェントに渡す Markdown context を生成する。

| コマンド | 用途 | 出力 |
|---|---|---|
| `accay system pack desk-debug --scenario <scenario>` | 机上デバッグ用 context | `.accay/runs/{run-id}/context.md` |
| `accay component pack review <component> --case <case-id>` | 受け入れレビュー用 context | `.accay/runs/{run-id}/context.md` |

### 7.6 serve

`accay serve` は、人間向け HTML レポートを表示する。

表示対象。

- component 別の受け入れケース数
- priority 別進捗
- status 別進捗
- accepted / blocked
- scenario との紐づき
- operation との紐づき
- 直近レビュー結果
- 回帰失敗中のケース

Markdown レポートは、エージェント向け入力や回帰失敗時の調査入力として利用する。

---

## 8. エージェントスキル

### 8.1 配置方針

Accay のエージェントスキルは、`.accay/skills/` ではなく、コーディングエージェントが読むスキルディレクトリへインストールする。

デフォルトのインストール先は以下とする。

```text
.agents/skills/
```

インストール先は `.accay/config.yaml` で変更できる。

```yaml
skills:
  install_dir: .agents/skills
```

スキル名には、既存スキルとの衝突を避けるため `accay-` prefix を付ける。

```text
.agents/skills/
  accay-interface-semantics/
  accay-desk-debugging/
  accay-acceptance-review/
  accay-acceptance-report/
```

### 8.2 install

`accay install` は、Accay が提供するエージェントスキルを設定されたインストール先に配置する。

方針。

- `accay init` は `.accay/config.yaml` と標準ディレクトリを作成する
- `accay install` は `skills.install_dir` に `accay-*` スキルをインストールする
- 既存スキルを不用意に上書きしない
- 上書きが必要な場合は、後続フェーズで `--force` などの扱いを設計する
- MVP では、スキルのインストールと更新は単純なファイル配置として扱う

### 8.3 スキル一覧

| Skill | 目的 |
|---|---|
| `accay-interface-semantics` | OpenAPI / operations.yaml / JSON Schema / 既存コード / README から意味論を抽出し、`semantics.md` の草案を作る |
| `accay-desk-debugging` | scenario / sequence / semantics を読み、シナリオを机上実行し、`trace.yaml` の草案を作る |
| `accay-acceptance-review` | コンポーネント単位で、変更を受け入れてよいかレビューし、findings report / decision / proposed updates を作る |
| `accay-acceptance-report` | レビュー結果や回帰結果を人間・エージェント向けに整形する |

## 9. MVP スコープ

### 9.1 MVP でやる

- `accay init`
- `accay install`
- `accay validate`
- `accay system validate`
- `accay component validate <component>`
- `accay system pack desk-debug --scenario <scenario>`
- `accay component pack review <component> --case <case-id>`
- `accay regression --junit <path>`
- `accay component regression <component> --junit <path>`
- `accay serve`
- OpenAPI から `kind: http` operation を読み取る
- `operations.yaml` から `kind: http` / `cli` / `function` operation を読み取る
- trace `input` / `output` の schema validation
- `kind: http` の status code 検証
- `kind: cli` の exit code 検証
- JUnit XML と `test-map.yaml` の照合
- 複数 JUnit XML のマージ
- component 別 regression report
- review context pack 生成
- Markdown report 生成
- 簡易 HTML dashboard

### 9.2 MVP でやらない

- エージェント実行
- PR 投稿
- 自動修正
- `test-map.yaml` 自動更新
- 仕様変更かバグかの完全自動判定
- OpenAPI の高度な差分解析
- trace からのテスト生成
- Smithy / AsyncAPI / Protobuf / gRPC adapter
- `message` / `job` / `file` kind
- function の実コード存在確認
- 言語別静的解析

### 9.3 Accay 自体の受け入れ条件

| ID | 条件 |
|---|---|
| ACCAY-001 | `accay init` で標準ディレクトリと設定ファイルが作成され、既存ファイルを不用意に上書きしない |
| ACCAY-002 | `accay install` で `skills.install_dir` に `accay-*` スキルをインストールできる |
| ACCAY-003 | OpenAPI の `operationId` と `operations.yaml` の `http` / `cli` / `function` operation を読み取れる |
| ACCAY-004 | 同一 component 内で operation ID が重複した場合に validate error を出せる |
| ACCAY-005 | trace の YAML 構造、`input` / `output` schema、HTTP status、CLI exit code を検証できる |
| ACCAY-006 | `test-map.yaml` の case ID が `acceptance-scope.yaml` に存在するか確認できる |
| ACCAY-007 | `test-map.yaml` の `verifies` が 1 件以上あることを検証できる |
| ACCAY-008 | 複数 JUnit XML を 1 つの test result set としてマージできる |
| ACCAY-009 | 同一 `classname + name` の testcase が複数 JUnit XML に出た場合に validate error を出せる |
| ACCAY-010 | JUnit XML と `test-map.yaml` を `classname + name` で照合し、case 単位で集計できる |
| ACCAY-011 | accepted case の failed / error / missing / skipped を検出し、Markdown / HTML レポートを出せる |
| ACCAY-012 | system-level と component-level の context pack を生成できる |
| ACCAY-013 | 受け入れレビュー成果物として `proposed/test-map.yaml` と `proposed/acceptance-scope.yaml` を扱える |

---

## 10. 後続フェーズの残課題

以下は要件定義フェーズでは決めない。設計フェーズまたは実装フェーズで判断する。

| 優先度 | 論点 | 後続フェーズで決めること |
|---|---|---|
| P1 | HTML dashboard の実装方式 | 静的生成のみか、`accay serve` でローカルサーバを立てるか |
| P1 | trace の外部 payload 参照 | `value_ref` で外部 JSON/YAML を参照可能にするか |
| P1 | review report の詳細テンプレート | severity、decision、missing evidence の具体フォーマット |
| P1 | proposed file の適用支援 | `accay diff-proposal` や `accay apply-proposal` を作るか |
| P2 | PR 連携 | GitHub API / PR コメント / CI annotation を扱うか |
| P2 | OpenAPI 差分解析 | operation contract の差分から影響 scenario を推定するか |
| P2 | test-map 更新支援 | unmapped tests の提案や UI 上の承認を扱うか |
| P2 | Smithy / AsyncAPI / Protobuf adapter | 外部インターフェース記述から operation contract を取り込むか |
| P2 | 追加 kind | `message` / `job` / `file` / `grpc` などをサポートするか |
| P2 | function 静的解析 | 言語別に signature 存在や境界越境を検出するか |

---

## Appendix A. サンプル構成

```text
docs/acceptance/
  scenarios/
    order-checkout.feature

  sequences/
    order-checkout.md

  traces/
    order-checkout.trace.yaml

  components/
    order-api/
      acceptance-scope.yaml
      test-map.yaml
      semantics.md
      review-guidelines.md

      interfaces/
        openapi.yaml
        operations.yaml
        schemas/
          create-order-input.schema.json
          create-order-output.schema.json

      reviews/
      reports/

    user-import-cli/
      acceptance-scope.yaml
      test-map.yaml
      semantics.md
      interfaces/
        operations.yaml
        schemas/
          import-users-input.schema.json
          import-users-output.schema.json
      reviews/
      reports/

    order-domain/
      acceptance-scope.yaml
      test-map.yaml
      semantics.md
      interfaces/
        operations.yaml
        schemas/
          create-order-command.schema.json
          create-order-result.schema.json
      reviews/
      reports/

.accay/
  config.yaml
  runs/
  reports/

.agents/
  skills/
    accay-interface-semantics/
    accay-desk-debugging/
    accay-acceptance-review/
    accay-acceptance-report/
```

---

## Appendix B. operations.yaml 例

### B.1 kind: http

```yaml
component: order-api

operations:
  createOrder:
    kind: http
    method: POST
    path: /orders
    schema_refs:
      CreateOrderInput: docs/acceptance/components/order-api/interfaces/schemas/order-api.yaml#/$defs/CreateOrderInput
      CreateOrderOutput: docs/acceptance/components/order-api/interfaces/schemas/order-api.yaml#/$defs/CreateOrderOutput
    status_codes:
      success: [201]
      failure: [400, 409, 500]
```

### B.2 kind: cli

```yaml
component: user-import-cli

operations:
  importUsers:
    kind: cli
    command: user-import
    summary: Import users from a CSV file
    schema_refs:
      ImportUsersInput: docs/acceptance/components/user-import-cli/interfaces/schemas/user-import-cli.yaml#/$defs/ImportUsersInput
      ImportUsersResult: docs/acceptance/components/user-import-cli/interfaces/schemas/user-import-cli.yaml#/$defs/ImportUsersResult
    exit_codes:
      success: [0]
      failure: [1]
```

### B.3 kind: function

```yaml
component: order-domain

operations:
  createOrder:
    kind: function
    signature: createOrder(command: CreateOrderCommand) -> CreateOrderResult
    summary: Create an order through the order domain service
    schema_refs:
      CreateOrderCommand: docs/acceptance/components/order-domain/interfaces/schemas/order-domain.yaml#/$defs/CreateOrderCommand
      CreateOrderResult: docs/acceptance/components/order-domain/interfaces/schemas/order-domain.yaml#/$defs/CreateOrderResult
    errors:
      - InventoryShortageError
      - PaymentAuthorizationError
```

---

## Appendix C. Acceptance Artifacts 例

### C.1 scenario.feature

```gherkin
Feature: Order checkout

  Scenario: Customer places an order successfully
    Given a customer has items in their cart
    And the items are in stock
    When the customer places the order
    Then the order should be created
    And the payment should be authorized
    And the inventory should be reserved
```

### C.2 trace.yaml: function operation

```yaml
scenario: order-checkout

steps:
  - id: create-order
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
      - customerId is preserved as external customer identity
      - order-domain must not decide payment authorization locally
```

### C.3 trace.yaml: http operation

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
      - customerId is preserved for payment authorization
```

### C.4 trace.yaml: cli operation

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
      - invalid rows are skipped, not imported
      - duplicate users are reported without stopping the import
```

### C.5 semantics.md

```markdown
# Semantics: order-domain

## Component responsibility

## Domain concepts

## Operations

### createOrder

#### Meaning

#### Field semantics

#### Invariants

#### Forbidden transformations

#### Downstream calls
```

### C.6 acceptance-scope.yaml

```yaml
component: order-domain

cases:
  ORD-001:
    title: 注文を作成できる
    priority: P0
    status: accepted
    scenarios:
      - order-checkout
    operations:
      - createOrder
```

### C.7 test-map.yaml

```yaml
component: order-domain

mappings:
  ORD-001:
    tests:
      - junit:
          classname: tests.acceptance.order.test_create_order
          name: test_create_order_success
        verifies:
          - order persisted
          - payment authorized
```

### C.8 Review run directory

```text
.accay/runs/2026-05-24T120000Z-order-domain-ORD-001/
  context.md
  review-report.md
  decision.yaml
  proposed/
    test-map.yaml
    acceptance-scope.yaml
```

---

## Appendix D. config.yaml 例

```yaml
docs_root: docs/acceptance

skills:
  install_dir: .agents/skills

language:
  verifies: ja
  reports: ja

junit:
  paths:
    - reports/python-junit.xml
    - reports/frontend-junit.xml

regression:
  accepted_failed: fail
  accepted_error: fail
  accepted_missing: fail
  accepted_skipped: fail
  non_accepted_failed: warning
  unmapped: info

reports:
  html_dir: .accay/reports/html
  markdown_dir: .accay/reports/markdown
```
