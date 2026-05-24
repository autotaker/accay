# 受け入れレビューガイドライン

## 1. 目的

受け入れレビューは、通常の code review ではなく、component 単位で変更を受け入れてよいかを判断する作業である。

主な観点は、仕様、意味、責務境界、テスト証拠である。

## 2. 入力と出力

入力:

- `acceptance-scope.yaml`
- `test-map.yaml`
- `semantics.md`
- `interfaces/*`
- 対象 diff。
- テスト結果。
- JUnit XML。
- 必要に応じた関連 scenario / sequence / trace。

出力:

- review findings。
- decision。
- 認定できるテスト証拠。
- 不足している証拠。
- 必要に応じた proposed updates。

関連 scenario / sequence / trace は参考情報であり、component validation / regression の正本ではない。

## 3. 役割

| 役割 | 責務 |
|---|---|
| 人間 | 最終 accept / reject、責務境界の裁定 |
| エージェント | 差分・仕様・テスト証拠の整理、findings 作成 |
| ハーネス | context pack、JUnit 読み取り、既存 map との照合材料 |

ハーネスは最終判断を行わない。

## 4. 確認すること

- acceptance-scope の対象 case を満たしているか。
- component の責務を越えていないか。
- semantics に反する変換や判断が入っていないか。
- operation contract と実装・テストが矛盾していないか。
- テストが受け入れ証拠として十分か。
- `test-map.yaml` に登録すべき証拠があるか。
- 既存 accepted case の保証を壊していないか。

## 5. 証拠認定

テスト証拠として見るもの:

- 受け入れ case と直接対応する test。
- 重要な意味保存条件を確認する test。
- regression で継続的に実行できる test。
- JUnit XML で `classname + name` が安定している test。

証拠として弱いもの:

- 実装詳細だけを確認する test。
- case と対応が説明できない test。
- skip される test。
- 手元だけで再現する test。

## 6. Decision

| decision | 意味 |
|---|---|
| accept | 受け入れ可能 |
| reject | 受け入れ不可 |
| needs_changes | 修正後に再確認 |
| needs_human_decision | 責務境界や仕様判断を人間が裁定する必要がある |

decision には理由と証拠を添える。

## 7. Proposed updates

必要に応じて以下を `.accay/runs/{run-id}/proposed/` に出す。

```text
proposed/
  test-map.yaml
  acceptance-scope.yaml
```

MVP では提案ファイルを正本へ自動適用しない。人間が差分を確認して取り込む。

## 8. Component regression との関係

component regression は、既に test-map に登録された証拠が壊れていないかを見る。

受け入れレビューは、今回の変更を受け入れてよいか、新しい証拠を test-map に登録すべきかを見る。

両者は近いが同じではない。

## 9. 報告構成

review report には以下を含める。

- 対象 component。
- 対象 case ID。
- decision。
- findings。
- 認定できる証拠。
- 不足している証拠。
- proposed update の有無。
- 人間判断が必要な論点。

## 10. Anti-patterns

- code style 指摘だけで受け入れ判断を止める。
- test が通っただけで accept する。
- semantics を読まずに判断する。
- component の責務外の修正を受け入れる。
- test-map を自動更新する。

## 11. Checklist

- scope の case を満たしている。
- semantics と矛盾しない。
- operation contract と矛盾しない。
- テスト証拠が説明できる。
- JUnit XML で継続確認できる。
- proposed update が必要なら分離されている。
- 最終判断者が明確である。

## 12. Findings の書き方

finding は、受け入れ判断に関係するものを優先する。

含めるもの:

- 対象 case ID。
- 問題の内容。
- なぜ受け入れ判断に影響するか。
- 参照した artifact。
- 必要な対応。

避けるもの:

- 好みの命名だけの指摘。
- 受け入れ条件に関係しない refactor 要望。
- MVP 外の機能要求。

## 13. 証拠不足の扱い

証拠不足は reject とは限らない。

| 状況 | 扱い |
|---|---|
| 実装は妥当だが test がない | needs_changes |
| 責務境界が曖昧 | needs_human_decision |
| test はあるが case と対応しない | needs_changes |
| semantics と矛盾 | reject または needs_human_decision |

判断の理由を report に残す。
