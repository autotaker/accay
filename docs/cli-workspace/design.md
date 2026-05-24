# CLI & Workspace 基本設計

作成日: 2026-05-24  
対象: Accay MVP  
領域: shared component  
参照: [../architecture.md](../architecture.md), [../requirements.md](../requirements.md)

## 1. この文書の位置づけ

この文書は、Accay の `CLI & Workspace` component の基本設計である。
`CLI & Workspace` は、利用者、CI、エージェントが最初に触れる入口であり、導入先 repository の作業領域を確定する shared component である。
この component は、command line を解釈し、repository root と config を決め、system / component / operation / output の各 component を適切な順序で呼び出す。
検証、回帰、意味判断の本体は持たない。

## 2. 目的

CLI & Workspace の目的は、Accay の公開振る舞いを安定した command として提供することである。

- 利用者の意図を command / option / argument として受け取る。
- 対象 repository を一意に決める。
- `.accay/config.yaml` を読み、実行時設定へ変換する。
- workspace mutation command では、必要な file / directory だけを作る。
- validation / pack / regression / serve command では、専門 component を呼び出す。
- 結果を diagnostics summary、report path、context path、exit code として返す。

Accay のハーネスは最終判断を行わない。
CLI & Workspace も判断主体ではなく、人間とエージェントが判断できるように処理を接続する。

## 3. 責務

| 分類 | 責務 |
|---|---|
| CLI parsing | command、subcommand、option、argument を解釈する。 |
| root discovery | `--root`、現在ディレクトリ、marker から repository root を決める。 |
| config loading | `.accay/config.yaml` を読み、default と統合する。 |
| path resolution | docs root、report dir、skill install dir、JUnit XML path を root 基準で解決する。 |
| workspace init | 標準 directory と default config を作る。 |
| skill install | bundled skill を `skills.install_dir` に配置する。 |
| orchestration | use case ごとに必要な component を呼び出す。 |
| diagnostics aggregation | 各 component の diagnostics を集約して Output に渡す。 |
| exit code mapping | 実行結果と severity から exit code を決める。 |
| user-facing messages | stdout / stderr に summary、path、error を表示する。 |

## 4. 非責務

CLI & Workspace は以下を行わない。

- artifact の深い構文検証。
- operation contract の意味解釈。
- OpenAPI の詳細 lint。
- JSON Schema validation の本体処理。
- JUnit XML と `test-map.yaml` の照合。
- `acceptance-scope.yaml` の受け入れ判断。
- `semantics.md` の意味判断。
- report / context の本文生成。
- HTML dashboard の画面構築。
- `test-map.yaml` の自動更新。
- PR コメント投稿。
- コード修正やエージェント実行。

CLI は各 component が返した structured result を集約する。
CLI が正本成果物を直接読んで、検証や判断を再実装してはいけない。

## 5. 設計原則

| 原則 | 内容 |
|---|---|
| orchestration に留める | CLI は処理順序と対象範囲を決める。検証本体は各 component に置く。 |
| workspace を明示する | repository root、docs root、出力先を実行前に確定する。 |
| 正本を混ぜない | system と component の正本成果物を CLI 内で意味的に結合しない。 |
| 既存 file を守る | `init` / `install` は既存 file を不用意に上書きしない。 |
| root 相対を基本にする | config と表示は repository root からの相対 path を優先する。 |
| diagnostics を捨てない | loader / harness / output が返した diagnostics を集約する。 |
| exit code を安定させる | CI が判定できる公開契約として扱う。 |

## 6. command ownership

Accay MVP の CLI command は、top-level、system-level、component-level に分ける。

| コマンド | 目的 | CLI の役割 |
|---|---|---|
| `accay init` | workspace 初期化 | 本体を所有する。 |
| `accay install` | agent skill install | 本体を所有する。 |
| `accay validate` | system と全 component の検証 | 対象範囲を決め、各 harness を呼ぶ。 |
| `accay regression --junit <path>` | 全 component の回帰 | Component Regression を呼ぶ。 |
| `accay serve` | 生成済み report の表示 | Output viewer を起動する。 |
| `accay system validate` | system 成果物の検証 | System Harness を呼ぶ。 |
| `accay system pack desk-debug --scenario <scenario>` | 机上デバッグ context 生成 | System Harness と Output を呼ぶ。 |
| `accay component validate <component>` | component 成果物の検証 | Component Harness を呼ぶ。 |
| `accay component pack review <component> --case <case-id>` | review context 生成 | Component Harness と Output を呼ぶ。 |
| `accay component regression <component> --junit <path>` | 指定 component の回帰 | Component Regression を呼ぶ。 |

CLI が本体を所有するのは workspace mutation だけである。
validation、pack、regression、serve は orchestration とする。

## 7. repository root discovery

repository root は、Accay が読み書きする path の基準である。
解決順序は次の通りとする。

| 優先順位 | 入力 | 規則 |
|---:|---|---|
| 1 | `--root <path>` | 指定 path を正規化し、存在する directory であることを確認する。 |
| 2 | 現在ディレクトリから上方向探索 | `.accay/config.yaml` または `.git/` を marker として探索する。 |
| 3 | 現在ディレクトリ | marker がない場合、`init` だけは現在ディレクトリを root として扱える。 |

root discovery の rule。

- `init` 以外の command では、root を決められない場合は error にする。
- `--root` が file を指す場合は error にする。
- `--root` が存在しない場合は error にする。
- symbolic link は実装上正規化してよい。
- 表示では root 相対 path を優先する。

## 8. config discovery

config file の既定位置は `.accay/config.yaml` である。
解決順序は次の通りとする。

| 優先順位 | 入力 | 規則 |
|---:|---|---|
| 1 | `--config <path>` | root 相対または絶対 path として解決する。 |
| 2 | root 配下の `.accay/config.yaml` | 存在すれば読む。 |
| 3 | default config | `init` と `install` の補助に使う。 |

config discovery の rule。

- `init` は config が存在しない状態でも実行できる。
- `install` は config がない場合、default config を使って実行できる。
- validation / pack / regression / serve は、原則として config を読む。
- config が壊れている場合は、対象 command を実行せず error にする。
- unknown key は MVP では warning に留める。
- 必須 key の型が不正な場合は error にする。

## 9. config model

MVP の主要設定は requirements の `config.yaml` 例に合わせる。

| key | 内容 | 既定 |
|---|---|---|
| `docs_root` | 長期保守成果物の root。 | `docs/acceptance` |
| `skills.install_dir` | agent skill の install 先。 | `.agents/skills` |
| `language.verifies` | `test-map.yaml` の `verifies` 記述言語。 | `ja` |
| `language.reports` | report / context の生成言語。 | `ja` |
| `junit.paths` | JUnit XML の既定 path。 | 空配列 |
| `regression.*` | 回帰結果の fail / warning / info rule。 | requirements の例に従う。 |
| `reports.html_dir` | HTML report 出力先。 | `.accay/reports/html` |
| `reports.markdown_dir` | Markdown report 出力先。 | `.accay/reports/markdown` |

CLI は config を読み、path を repository root からの絶対 path に解決して各 component へ渡す。
diagnostics 表示では root 相対 path に戻す。

## 10. workspace layout

CLI & Workspace が理解する標準 layout は次の通りである。

```text
docs/acceptance/
  scenarios/
  sequences/
  traces/
  components/
.accay/
  config.yaml
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

`docs/acceptance/` は人間も読む長期保守成果物である。
`.accay/` は Accay の設定、生成物、一時成果物、cache を置く領域である。
`.agents/skills/` は agent が読む skill install 先であり、config で変更できる。

## 11. data / file ownership

CLI & Workspace の file ownership は限定する。

| path | 所有者 | CLI の権限 |
|---|---|---|
| `.accay/config.yaml` | CLI & Workspace | `init` で作成する。既存 file は保持する。 |
| `.accay/runs/` | Output & Presentation | directory を準備できる。本文生成は Output に委譲する。 |
| `.accay/reports/` | Output & Presentation | directory を準備できる。report 生成は Output に委譲する。 |
| `.accay/cache/` | 各 component | directory を準備できる。cache 内容の意味は所有しない。 |
| `.agents/skills/accay-*` | CLI & Workspace | `install` で bundled skill を配置する。 |
| `docs/acceptance/` | user / harness domain | `init` で標準 directory を作る。正本内容は更新しない。 |

CLI は `docs/acceptance/components/{component}` の正本 file を自動修正しない。
CLI は `test-map.yaml` を自動更新しない。
CLI は generated report を Output から受け取り、path を表示する。

## 12. `accay init`

`accay init` は、Accay を導入できる workspace を準備する。

処理順序。

1. repository root を決定する。
2. `.accay/` を作る。
3. `.accay/config.yaml` がなければ default config を作る。
4. `docs_root` に基づく標準 directory を作る。
5. `.accay/runs/` と report directory を作る。
6. 作成 / 既存 / skip の summary を表示する。

作成対象。

| directory / file | 用途 |
|---|---|
| `.accay/config.yaml` | Accay 設定。 |
| `docs/acceptance/scenarios/` | Gherkin scenario。 |
| `docs/acceptance/sequences/` | sequence / Mermaid markdown。 |
| `docs/acceptance/traces/` | desk-debug trace。 |
| `docs/acceptance/components/` | component acceptance artifacts。 |
| `.accay/runs/` | context pack などの一時成果物。 |
| `.accay/reports/html/` | HTML report。 |
| `.accay/reports/markdown/` | Markdown report。 |

上書き rule。

- 既存 directory は成功扱いにする。
- 既存 `.accay/config.yaml` は上書きしない。
- 既存 file と作成予定 directory が衝突する場合は error にする。
- default config の再生成は行わない。
- agent skill は install しない。

## 13. `accay install`

`accay install` は、Accay が提供する agent skill を config の install dir に配置する。

処理順序。

1. repository root を決定する。
2. config を読む。なければ default config を使う。
3. `skills.install_dir` を root 相対 path として解決する。
4. install dir を作る。
5. bundled skill template を `accay-*` directory として配置する。
6. 作成 / 既存 / skip の summary を表示する。

MVP の skill directory。

| skill | 用途 |
|---|---|
| `accay-interface-semantics` | interface の意味論を書く。 |
| `accay-desk-debugging` | system trace を使った机上デバッグを行う。 |
| `accay-acceptance-review` | component acceptance review を行う。 |
| `accay-acceptance-report` | 受け入れ結果を report 化する。 |

install rule。

- `.accay/skills/` には配置しない。
- 既存 skill directory は上書きしない。
- 既存 directory がある場合は skip として summary に出す。
- 既存 path が file の場合は error にする。
- `--force` は MVP では設計対象外とする。

## 14. validation orchestration

validation command は、Operation Directory を境界にして system / component の検証を呼び出す。
CLI は validation logic を持たない。

共通処理。

1. root と config を解決する。
2. docs root と component 対象範囲を決める。
3. 必要に応じて Operation Directory を構築する。
4. 対象に応じて artifact loader を呼ぶ。
5. 対象に応じて harness を呼ぶ。
6. diagnostics を集約する。
7. Output に diagnostics summary を整形させる。
8. exit code を決める。

対象範囲。

| コマンド | system validation | component validation |
|---|---:|---:|
| `accay validate` | する | 全 component |
| `accay system validate` | する | しない |
| `accay component validate <component>` | しない | 指定 component |

Operation Directory の構築に失敗した場合は、対象 harness を呼ばず error にする。
component が存在しない場合は error にする。
component が 0 件の場合、`accay validate` は warning を出して system validation は継続できる。

## 15. pack orchestration

pack command は、エージェントまたは人間に渡す Markdown context を生成する。
CLI は材料の大枠を選ぶが、context 本文の整形は Output に委譲する。

| コマンド | 正本として読むもの | 参考情報 |
|---|---|---|
| `system pack desk-debug` | scenario / sequence / trace | operation contract, component semantics |
| `component pack review` | scope / test-map / semantics / interfaces | related trace / scenario / sequence, JUnit summary |

共通処理。

1. root と config を解決する。
2. run id を作る。
3. `.accay/runs/{run-id}/` を準備する。
4. 対象 artifact を loader から取得する。
5. 必要な harness に context source を作らせる。
6. Output に `context.md` を書かせる。
7. 作成した path を表示する。

run id は timestamp と対象名から読める形にする。
重複時は suffix を付けて回避してよい。

## 16. regression orchestration

regression command は Component Regression を呼び出す。
CLI は JUnit XML と `test-map.yaml` の照合を実装しない。

共通処理。

1. root と config を解決する。
2. `--junit` または `junit.paths` から JUnit XML path を決める。
3. 対象 component を決める。
4. Component Artifacts を読み込ませる。
5. Component Regression に照合させる。
6. Output に Markdown / HTML report を生成させる。
7. summary、report path、exit code を返す。

| コマンド | 対象 |
|---|---|
| `accay regression --junit <path>` | 全 component |
| `accay component regression <component> --junit <path>` | 指定 component |

JUnit XML path が 1 件もない場合は error にする。
JUnit XML file が存在しない場合は error にする。
回帰結果の severity は config の `regression.*` に従う。

## 17. serve orchestration

`accay serve` は、生成済み report を見るための薄い viewer である。

処理順序。

1. root と config を解決する。
2. `reports.html_dir` を解決する。
3. Output & Presentation に viewer 起動を委譲する。
4. 起動 URL または参照 path を表示する。

`serve` は正本成果物を編集しない。
`serve` は validation / regression を自動実行しない。
`serve` は test-map 承認 UI や proposal 適用 UI を持たない。

## 18. diagnostics policy

diagnostics は、各 component から返された structured message を CLI が集約する。
CLI が追加してよい diagnostics は、command 実行前後の workspace error に限る。

| severity | 意味 | exit code への影響 |
|---|---|---|
| `error` | command を失敗させる問題。 | 非ゼロ |
| `warning` | 実行はできるが注意が必要な問題。 | 原則 0。将来 strict mode で非ゼロ化できる。 |
| `info` | 利用者への補足。 | なし |

diagnostic の最小項目。

| field | 内容 |
|---|---|
| `code` | 機械的に識別できる code。 |
| `severity` | `error` / `warning` / `info`。 |
| `message` | 人間向けの短い説明。 |
| `path` | 関係する root 相対 path。任意。 |
| `component` | 関係する component 名。任意。 |
| `operation` | 関係する operation ID。任意。 |

text 表示では error を先に出す。
JSON 表示を実装する場合は stable field を優先する。

## 19. exit code policy

exit code は CLI の公開契約である。

| exit code | 意味 |
|---:|---|
| 0 | 成功。error diagnostic がない。 |
| 1 | validation / regression / workspace 処理が失敗した。 |
| 2 | CLI usage error。command、argument、option が不正。 |
| 3 | config error。config が読めない、型が不正、path 解決不能。 |
| 4 | unexpected error。未捕捉例外または内部不整合。 |

優先順位は usage error、config error、unexpected error、validation / regression / workspace failure、success の順とする。
予期しない例外は stack trace を通常表示しない。
`--verbose` が指定された場合のみ、debug 用の補足を stderr に出してよい。

## 20. component interaction

CLI & Workspace が直接呼んでよい component は、architecture の依存方向に従う。

| 呼び出し先 | CLI から渡すもの | CLI が受け取るもの |
|---|---|---|
| System Artifacts | docs root、scenario selector | system artifact set |
| System Harness | artifact set、operation directory | diagnostics、context source |
| Operation Directory | component interface roots | operation catalog、schema resolver |
| Component Artifacts | docs root、component selector | component artifact set |
| Component Harness | artifact set、operation directory | diagnostics、context source |
| Component Regression | artifact set、JUnit paths、policy | regression result |
| Output & Presentation | diagnostics / context source / result | formatted text、written paths、server status |

CLI は System Artifacts から得た内容を Component Harness に直接渡さない。
CLI は Component Artifacts から得た内容を System Harness に正本として渡さない。
参考情報として含める場合は、pack 用の明示的な context source として扱う。

## 21. orchestration rules

共通 rule。

- root / config の解決を最初に行う。
- usage error は component 呼び出し前に返す。
- config error は component 呼び出し前に返す。
- Operation Directory が必要な command では、harness より前に構築する。
- artifact loader が返した diagnostics は捨てない。
- 片方の validation が失敗しても、可能な範囲で残りの validation を継続してよい。
- report / context の書き込みは Output に委譲する。
- exit code は最後に一度だけ決める。

| error | 継続方針 |
|---|---|
| usage error | 即停止 |
| config parse error | 即停止 |
| root 不明 | 即停止 |
| Operation Directory 構築不能 | validation / pack は停止 |
| ある component の artifact 不正 | 他 component の検証は継続可能 |
| report 書き込み失敗 | command は失敗 |

## 22. failure modes

| 状況 | severity | exit code | 補足 |
|---|---|---:|---|
| unknown command | error | 2 | usage help を出す。 |
| 必須 argument 不足 | error | 2 | 対象 command の help を出す。 |
| `--root` が存在しない | error | 1 | workspace error とする。 |
| config YAML が parse できない | error | 3 | component は呼ばない。 |
| config key の型が不正 | error | 3 | path と key を表示する。 |
| `docs_root` が file と衝突 | error | 1 | `init` でも上書きしない。 |
| component が存在しない | error | 1 | 指定名を表示する。 |
| JUnit XML が存在しない | error | 1 | regression は実行しない。 |
| report directory に書けない | error | 1 | Output の error を伝える。 |
| unexpected exception | error | 4 | `--verbose` 以外では短く表示する。 |

failure message は、何が起きたか、どの path か、利用者が次に何を確認すべきかを短く示す。

## 23. test strategy

CLI & Workspace のテストは Contract Test を中心にする。
Accay はユーザー repository に導入される CLI tool なので、内部関数より公開挙動を固定する。

| 分類 | 対象 |
|---|---|
| Contract Test | fixture repository に対する CLI 挙動、exit code、生成 file、diagnostics。 |
| Unit Test | root discovery、config merge、path normalization、exit code mapping。 |
| Golden Test | diagnostics summary、context path 表示、report path 表示、JSON field structure。 |

主要観点。

- `init` が標準 directory と config を作成し、既存 file を上書きしない。
- `install` が `skills.install_dir` に `accay-*` skill を配置し、既存 skill を上書きしない。
- `--root` 指定時に対象 repository が切り替わる。
- validation command が対象に応じた component を呼び出す。
- regression command が JUnit path と component selector を渡す。
- pack command が `.accay/runs/{run-id}/context.md` を出力する。
- error 時に非ゼロ、usage error 時に 2 を返す。
- timestamp、run id、絶対 path は golden test で正規化する。

## 24. implementation notes

実装 package の目安は architecture に合わせる。

```text
src/accay/
  cli.py
  workspace/
    config.py
    init.py
    skills.py
```

| module | 役割 |
|---|---|
| `cli.py` | parser、command dispatch、exit code mapping。 |
| `workspace/config.py` | config discovery、load、default merge、path resolve。 |
| `workspace/init.py` | `accay init` の directory / config 作成。 |
| `workspace/skills.py` | bundled skill の install。 |

実装時の注意。

- CLI に validation rule を追加したくなったら、まず所有 component を確認する。
- path は早い段階で絶対 path にし、表示直前に root 相対へ戻す。
- `--force`、`--dry-run`、strict mode は MVP 必須ではない。
- exception は command boundary で捕捉し、exit code に変換する。
- system / component / operations / output の内部 model を CLI の公開 model にしない。
