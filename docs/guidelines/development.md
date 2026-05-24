# 開発ガイドライン

## 1. 基本方針

Accay は、受け入れ判断を支援するハーネスである。開発では、機械的に確認することと、人間・エージェントが判断することを分ける。

守る境界:

- system と component の直接依存を作らない。
- system と component の接続は Operation Directory に寄せる。
- CLI は orchestration に留める。
- Output は表示とファイル出力に留める。
- 既存ファイルを不用意に上書きしない。

## 2. 開発フロー

1. 変更対象の component design を読む。
2. `docs/architecture.md` の依存方向を確認する。
3. 公開挙動が変わる場合は Contract Test を考える。
4. 局所処理が複雑なら Unit Test を追加する。
5. CLI からの利用経路を確認する。
6. diagnostics と exit code の扱いを確認する。

docs-first を基本にする。新しい責務境界や運用ルールが必要なら、実装前に docs を更新する。

## 3. Component boundary

| package | 主な責務 | 置いてはいけないもの |
|---|---|---|
| `workspace` | config、root、init、install | validation 本体 |
| `system` | scenario / sequence / trace、system validation | component scope / test-map 読み取り |
| `operations` | operation catalog、schema registry | semantics 判断、test-map 照合 |
| `component` | scope / test-map / semantics、review、regression | system trace への必須依存 |
| `output` | diagnostics / context / report / serve | validation / regression 本体 |

迷った場合は、正本として読むファイルの所有者に処理を置く。

## 4. Diagnostics

利用者が直せる問題は diagnostics として返す。

含める情報:

- severity。
- message。
- source path。
- component / scenario / case ID。
- operation。
- 可能なら修正の方向性。

severity:

| severity | 用途 |
|---|---|
| error | コマンドの目的を達成できない |
| warning | 継続可能だが確認が必要 |
| info | 参考情報 |

例外は内部不整合や予期しない失敗に残す。利用者入力の不備は diagnostics に寄せる。

## 5. Filesystem safety

- 既存ファイルは既定で上書きしない。
- `init` / `install` は created / existing を明示する。
- generated output は `.accay/` 以下に置く。
- 長期保守成果物は `docs/acceptance/` 以下に置く。
- destructive operation は MVP では持たない。

## 6. CLI behavior

CLI は薄く保つ。

- command parsing。
- root / config resolution。
- component orchestration。
- summary 表示。
- exit code 決定。

CLI に YAML / XML の詳細解析、schema validation、test matching を置かない。

## 7. Testing expectation

公開挙動は Contract Test で守る。

優先する Contract Test:

- `accay init`
- `accay install`
- `accay validate`
- `accay system validate`
- `accay component validate`
- `accay regression`
- context / report generation

Unit Test は parser、resolver、matcher、formatter などの局所処理に使う。

## 8. Commit と review

commit は意味のある単位にする。

- docs だけの変更と実装変更を混ぜすぎない。
- 生成物や `.DS_Store` を含めない。
- public behavior を変える変更には test を含める。
- architecture 境界を変える場合は docs を更新する。

review では、境界違反、公開挙動、test evidence を優先して確認する。

## 9. 実装前チェック

- どの component の責務か説明できる。
- system / component の直接依存を増やしていない。
- Output に判断ロジックを置いていない。
- CLI に本体ロジックを置いていない。
- diagnostics が利用者に理解できる。
- テスト分類が適切である。

## 10. 実装後チェック

- `git status` に不要ファイルが混ざっていない。
- generated output を正本として commit していない。
- public CLI behavior が変わる場合に Contract Test がある。
- local helper の追加が package 境界を壊していない。
- docs と実装が矛盾していない。
- warning / error の基準が曖昧なまま残っていない。

## 11. 判断に迷う例

| 状況 | 判断 |
|---|---|
| system validation で case status を見たい | 見ない。component 側の責務 |
| review context に trace を入れたい | 参考情報としてならよい |
| Output で artifact を読み直したい | 読まない。source を呼び出し元から受け取る |
| CLI で YAML を parse したい | 専用 component に移す |
| probe test が有用になった | Unit Test か Contract Test に昇格する |

## 12. MVP で広げないこと

- PR 投稿。
- 自動修正。
- test-map の完全自動更新。
- OpenAPI lint 全般。
- function の実コード静的解析。
- dashboard での正本編集。
