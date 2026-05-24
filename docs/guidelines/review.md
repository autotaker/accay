# レビューガイドライン

## 1. 目的

このガイドラインは、Accay 自体の code review と design review の観点を揃えるためのものである。

レビューでは、好みの設計よりも、受け入れ駆動ツールとしての境界、公開挙動、テスト証拠を優先して見る。

## 2. 優先観点

最初に見ること:

- system と component の直接依存が増えていないか。
- Operation Directory を境界として使えているか。
- CLI に validation / regression の本体ロジックが入っていないか。
- Output に判断ロジックが入っていないか。
- 既存ファイルを不用意に上書きしないか。
- Contract Test で公開挙動が固定されているか。
- diagnostics が利用者に直せる形で返っているか。

## 3. Severity

| 優先度 | 意味 | 例 |
|---|---|---|
| P0 | 重大な誤判定やデータ破壊 | failed test を pass 扱い、既存ファイル上書き |
| P1 | architecture 境界違反や主要 use case 破壊 | component regression が trace に依存 |
| P2 | 保守性や診断品質の問題 | diagnostics に path がない |
| P3 | 表現改善や軽微な整理 | docs の言い回し、名前の微修正 |

レビューコメントでは、優先度と理由を明確にする。

## 4. Architecture checks

確認する境界:

- `system` は `component` を import していないか。
- `component` は `system` を import していないか。
- `operations` は boundary として独立しているか。
- `output` は artifact loader を呼んでいないか。
- CLI は orchestration に留まっているか。

境界違反は、動いていても P1 以上として扱う。

## 5. Docs checks

docs 変更では以下を見る。

- 現在形の設計として読めるか。
- 変更履歴の説明になっていないか。
- 責務と非責務が明確か。
- 他 docs と用語が揃っているか。
- MVP 外の機能を既定にしていないか。

## 6. Test evidence checks

公開挙動が変わる場合:

- Contract Test があるか。
- exit code が検証されているか。
- generated file の主要構造が検証されているか。
- diagnostics の severity が検証されているか。

複雑な局所処理が増える場合:

- Unit Test があるか。
- edge case が fixture で表現されているか。

## 7. Review comment style

良いコメント:

- どの境界に違反しているかを書く。
- 利用者に起きる問題を書く。
- 修正方向を短く示す。
- file / line を具体的に示す。

避けるコメント:

- 好みだけの大きな変更要求。
- MVP 外機能の混入。
- 抽象的な「もっときれいに」。

## 8. Approval checklist

- architecture 境界に反していない。
- 変更範囲が説明できる。
- public behavior に test がある。
- diagnostics が利用者向けになっている。
- docs 更新が必要な場合に反映されている。
- 不要ファイルが含まれていない。

## 9. Anti-patterns

- system validation が `test-map.yaml` を読む。
- component regression が trace を読む。
- Output が validation 判定をする。
- CLI が XML / YAML の詳細解析をする。
- probe test がそのまま CI 必須になる。

## 10. Docs review checklist

- 文書が現在形で書かれている。
- 変更履歴ではなく設計として読める。
- 目的、責務、非責務がある。
- 例が多すぎて本筋を隠していない。
- 同じ説明が複数 section に重複していない。
- 「MVP でやらないこと」が明確である。

## 11. Code review checklist

- 変更対象 component が明確である。
- package 境界を越えた import が増えていない。
- CLI / Output に本体ロジックが入っていない。
- diagnostics が source path を持つ。
- public behavior に Contract Test がある。
- local helper が過度に抽象化されていない。

## 12. 承認してよい状態

- P0 / P1 が残っていない。
- P2 が残る場合、理由と後続対応が説明されている。
- テストしない場合、その理由が妥当である。
- docs-only 変更なら、対象 docs と影響範囲が説明されている。
