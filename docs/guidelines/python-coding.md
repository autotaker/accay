# Python コーディング規約

## 1. 基本方針

この規約は `src/accay/` と `tests/` の Python code を対象にする。

Accay の Python code は、CLI ツールとしての読みやすさ、テストしやすさ、責務境界の明確さを優先する。

## 2. Language baseline

- Python 3.11 以上を前提にする。
- type hint を付ける。
- `pathlib.Path` を使う。
- YAML / JSON / XML は専用 parser を使う。
- CLI 表示と domain logic を混ぜない。

## 3. 命名

| 対象 | 規約 | 例 |
|---|---|---|
| module | snake_case | `review_pack.py` |
| function | snake_case | `load_component_artifacts` |
| class | PascalCase | `OperationDirectory` |
| field | snake_case | `schema_ref` |
| constant | UPPER_SNAKE_CASE | `DEFAULT_CONFIG` |

名前は architecture の component 名と対応させる。`system` と `component` の意味が混ざる名前は避ける。

## 4. 関数設計

- 1 つの関数は 1 つの責務に寄せる。
- filesystem access と判定処理を分ける。
- validation と rendering を分ける。
- parser と policy 判定を分ける。
- CLI handler は orchestration だけにする。

戻り値は、呼び出し側が diagnostics を作れる情報を含める。

## 5. 型と model

内部 model は必要に応じて dataclass を使う。

使うとよい場面:

- 同じ dict key を複数箇所で参照する。
- diagnostics に location を持たせる。
- regression result を report に渡す。
- operation catalog を lookup する。

ただし architecture では dataclass 名を固定しない。実装で必要になった型を package 内に閉じる。

## 6. Error と diagnostics

利用者入力の問題は diagnostics にする。

例:

- YAML が壊れている。
- schema ref が存在しない。
- operation ID が重複している。
- mapped testcase が missing。

例外にしてよいもの:

- 到達不能な内部状態。
- programmer error。
- 想定外の parser failure。

境界で例外を捕捉し、CLI では短く説明する。

## 7. Parser rules

- YAML は safe loader を使う。
- JSON Schema は schema validator に渡す前に path 解決する。
- XML は JUnit reader に閉じ込める。
- parser は raw input を validation policy まで持ち込まない。

文字列分解で YAML / XML を処理しない。

## 8. Imports

- package 間依存は architecture に従う。
- `system -> component` を import しない。
- `component -> system` を import しない。
- `operations` から `system` / `component` を import しない。
- `output` から artifact loader を import しない。

依存方向に迷う場合は、処理を呼び出し側 CLI に戻す。

## 9. Filesystem

- `Path` を使う。
- repository root からの相対 path を保持する。
- 表示時に必要なら絶対 path に変換する。
- 既存ファイルを上書きする処理は明示的に分ける。
- generated output は `.accay/` 以下に閉じる。

## 10. Tests

- public behavior は Contract Test。
- parser / matcher は Unit Test。
- 調査用は Probe Test。
- timestamp、run id、absolute path は正規化できるようにする。

## 11. Anti-patterns

- CLI handler に validation logic を書く。
- Output で正本ファイルを読み直す。
- system validation で test-map を読む。
- component regression で trace を読む。
- parser が diagnostics 表示文を直接作る。
- dict の深い key access を各所に散らす。

## 12. Diagnostics 実装の型

diagnostics は、最低限次の情報を持てるようにする。

- severity。
- message。
- source path。
- component / scenario / case ID。
- operation。
- optional detail。

Python 実装では、文字列を各所で組み立てず、共通 formatter に渡す。

## 13. CLI 実装の型

CLI handler は以下の形に寄せる。

1. args を受け取る。
2. workspace を解決する。
3. use case component を呼ぶ。
4. Output へ summary を渡す。
5. exit code を返す。

handler 内で file format の詳細に踏み込まない。

## 14. Review checklist

- import 方向が architecture と合っている。
- public function の引数が過剰でない。
- path は `Path` で扱っている。
- parser failure が利用者向け diagnostics に変換される。
- tests で timestamp / absolute path が揺れない。
