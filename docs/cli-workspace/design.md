# CLI & Workspace 基本設計

## 1. 役割

CLI & Workspace は、Accay の利用者が触れる入口であり、各 component を呼び出す orchestration layer である。

この component は、repository root、設定、command line option を確定し、必要な処理を適切な component に委譲する。validation、regression、report rendering の本体ロジックは持たない。

## 2. 責務境界

### 責務

- CLI command と option を解釈する。
- repository root を決定する。
- `.accay/config.yaml` を読み込む。
- `accay init` で標準ディレクトリと初期 config を作る。
- `accay install` で bundled skill を設定された install dir に配置する。
- 各 use case の処理順序を組み立てる。
- diagnostics summary と exit code を利用者へ返す。

### 非責務

- artifact の深い検証。
- operation contract の解釈。
- JUnit XML と `test-map.yaml` の照合。
- report / context の本文生成。
- 意味判断や最終的な accept / reject 判断。

## 3. Command ownership

| command | 主担当 | 呼び出す component |
|---|---|---|
| `accay init` | CLI & Workspace | なし |
| `accay install` | CLI & Workspace | なし |
| `accay validate` | CLI & Workspace | Operation Directory, System Harness, Component Harness, Output |
| `accay system validate` | CLI & Workspace | Operation Directory, System Harness |
| `accay component validate <component>` | CLI & Workspace | Operation Directory, Component Harness |
| `accay system pack desk-debug` | CLI & Workspace | Operation Directory, System Harness, Output |
| `accay component pack review` | CLI & Workspace | Operation Directory, Component Harness, Component Regression, Output |
| `accay regression` | CLI & Workspace | Component Artifacts, Component Regression, Output |
| `accay serve` | CLI & Workspace | Output |

CLI は「何をどの順に呼ぶか」を決める。各処理の正しさは、呼び出し先 component が持つ。

## 4. Workspace model

Workspace は、Accay を実行する対象 repository を表す。

主な要素:

- `root`: 対象 repository root。
- `config`: `.accay/config.yaml` から読んだ設定。
- `docs_root`: acceptance docs の root。既定は `docs/acceptance`。
- `skills.install_dir`: agent skill の install 先。既定は `.agents/skills`。
- `reports.html_dir`: HTML report 出力先。
- `reports.markdown_dir`: Markdown report 出力先。

path は原則として repository root からの相対パスで扱う。CLI 表示では、利用者が辿れるように実パスまたは root 相対パスを明示する。

## 5. `init` と `install`

### `accay init`

`init` は Accay を導入できる最小 workspace を作る。

作成対象:

- `.accay/config.yaml`
- `docs/acceptance/scenarios/`
- `docs/acceptance/sequences/`
- `docs/acceptance/traces/`
- `docs/acceptance/components/`
- `.accay/runs/`
- `.accay/reports/html/`
- `.accay/reports/markdown/`
- `.agents/skills/`

既存ファイルは上書きしない。すでに存在する path は `exists` として summary に出す。

### `accay install`

`install` は bundled skill を `skills.install_dir` に配置する。

対象 skill:

- `accay-interface-semantics`
- `accay-desk-debugging`
- `accay-acceptance-review`
- `accay-acceptance-report`

既存 `SKILL.md` は上書きしない。将来 `--force` を追加する場合も、既定動作は non-destructive に保つ。

## 6. Orchestration rules

`accay validate` の流れ:

1. workspace config を読む。
2. Operation Directory を構築する。
3. system validation を実行する。
4. component validation を実行する。
5. Output で diagnostics summary を整形する。
6. severity に応じて exit code を返す。

`accay regression` の流れ:

1. workspace config と regression rule を読む。
2. 対象 component artifact を読む。
3. Component Regression を実行する。
4. Output で report を生成する。
5. 結果に応じて exit code を返す。

CLI は component 間の結果を受け渡すが、結果の中身を解釈しすぎない。

## 7. Diagnostics と exit code

| 状態 | exit code | 方針 |
|---|---:|---|
| error あり | non-zero | 利用者が修正すべき問題として表示する |
| warning / info のみ | 0 | report には残すが処理成功扱い |
| 内部例外 | non-zero | 簡潔な message と必要な debug 情報を出す |

CLI は diagnostics を作りすぎない。多くの場合、diagnostics は各 harness / regression から受け取る。

## 8. 失敗モード

| 失敗 | 扱い |
|---|---|
| config が壊れている | CLI & Workspace の error |
| root が見つからない | CLI & Workspace の error |
| init 対象が file と衝突 | CLI & Workspace の error |
| install 先に既存 skill がある | `exists` として報告し成功 |
| harness が diagnostics error を返す | CLI は非ゼロ終了 |

## 9. テスト観点

Contract Test:

- `accay init` が標準ディレクトリを作る。
- `accay init` が既存 config を上書きしない。
- `accay install` が既存 skill を上書きしない。
- `accay validate` が diagnostics と exit code を返す。

Unit Test:

- root 解決。
- config 読み込み。
- path 正規化。
- command dispatch。
- exit code 判定。

## 10. 実装メモ

- CLI parser は薄く保つ。
- command handler から直接 YAML / XML の詳細解析をしない。
- filesystem 変更は `init` / `install` と Output の書き出しに限定する。
- destructive な操作は MVP では持たない。
- logging と user-facing output を混ぜない。

## 11. 実装判断

CLI & Workspace で迷いやすい判断は、次の基準で決める。

| 判断 | 方針 |
|---|---|
| command handler に処理を書くか | orchestration だけなら書く。本体ロジックなら各 component へ移す |
| file を作るか | `init` / `install` / Output 以外では原則作らない |
| config default を補うか | 読み込み時に補えるが、勝手に config file を書き換えない |
| missing config を error にするか | `init` 以外では error。`init` では作成対象 |
| path を絶対化するか | 内部では root 相対を優先し、表示や filesystem access で絶対 path を使う |

## 12. Use case 別の完了条件

| use case | 完了条件 |
|---|---|
| init | 標準ディレクトリと config の created / existing summary を返す |
| install | skill ごとの created / existing summary を返す |
| validate | system / component diagnostics をまとめて exit code を返す |
| pack | `.accay/runs/{run-id}/context.md` の path を返す |
| regression | report path と regression summary を返す |
| serve | local viewer の起動状態を返す |

## 13. 将来拡張の余地

後続フェーズで追加しうるもの:

- `--config` による config path 指定。
- `--format json` による machine-readable output。
- `--quiet` / `--verbose`。
- `install --force`。
- `validate --component` の alias。

これらを追加する場合も、CLI は orchestration layer のまま保つ。
