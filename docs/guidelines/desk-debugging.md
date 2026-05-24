# 机上デバッグガイドライン

## 1. 目的

机上デバッグは、E2E に近い業務シナリオを、実装やテスト実行とは独立して operation 列として確認する作業である。

成果物の中心は `docs/acceptance/traces/{scenario}.trace.yaml` である。

## 2. 入力と出力

入力:

- `docs/acceptance/scenarios/{scenario}.feature`
- `docs/acceptance/sequences/{scenario}.md`
- 既存 trace。
- Operation Directory から得られる operation contract。
- 必要に応じた component semantics。

出力:

- `docs/acceptance/traces/{scenario}.trace.yaml`
- 必要に応じた `.accay/runs/{run-id}/desk-debug-report.md`

component semantics は参考情報であり、system の正本ではない。

## 3. 確認すること

- シナリオの目的が trace に反映されているか。
- step の順序が業務シナリオとして自然か。
- 各 step が `component + operation` で表されているか。
- `input` / `output` が schema と整合しているか。
- 保存すべき値や観測点が observations に書かれているか。
- component の責務を越えた判断を trace に押し込んでいないか。

## 4. Trace 作成ルール

- endpoint ではなく operation を参照する。
- `request` / `response` ではなく `input` / `output` を使う。
- schema 参照は repository root からの相対パスにする。
- kind は trace ではなく operation 定義側に持たせる。
- observations は空にしない。

step の最小形:

```yaml
- id: create-order
  component: order-domain
  operation: createOrder
  input:
    schema_ref: docs/acceptance/components/order-domain/interfaces/schemas/create-order-command.schema.json
    value: {}
  output:
    schema_ref: docs/acceptance/components/order-domain/interfaces/schemas/create-order-result.schema.json
    value: {}
  observations:
    - customer identity is preserved
```

## 5. Operation abstraction

Trace は `component + operation` を参照する。

operation の kind は Operation Directory が知る。

- `http`: status code を検証できる。
- `cli`: exit code を検証できる。
- `function`: signature は参照情報として扱う。

Trace は component の acceptance case ID を必須参照しない。

## 6. ハーネスが確認すること

- scenario / sequence / trace の存在。
- trace step id の重複。
- component / operation / schema の参照。
- `input.value` / `output.value` の schema validation。
- HTTP status / CLI exit code の存在。
- observations の最低限チェック。

## 7. 人間・エージェントが判断すること

- 意味保存条件が本当に守られているか。
- 仕様変更かバグか。
- component の責務境界を越えていないか。
- trace を更新すべきか。
- observations が業務的に十分か。

## 8. Context pack

`accay system pack desk-debug --scenario <scenario>` は、机上デバッグ用の `context.md` を作る。

含めるもの:

- scenario。
- sequence。
- 既存 trace。
- operation contract。
- 必要に応じた semantics。

context は入力であり、正本ではない。

## 9. Anti-patterns

- endpoint path を trace の中心にする。
- request / response という HTTP 固有語に寄せる。
- observations を空にする。
- component の受け入れ判定を trace に書く。
- schema で表せない意味を無理に JSON Schema に押し込む。

## 10. レビュー checklist

- scenario と trace の目的が一致している。
- operation 列が自然である。
- schema ref が root 相対 path である。
- input / output の値が検証可能である。
- observations が判断に役立つ。
- component の責務境界を越えていない。

## 11. 良い observations

良い observations は、後から trace を読んだ人が「何を守るべきか」を理解できる。

例:

- external customer id is preserved。
- payment authorization is not decided by order-domain。
- invalid rows are skipped, not imported。
- duplicate users are reported without stopping import。

悪い observations:

- works。
- check this。
- response is OK。
- implementation calls function X。

## 12. Maintenance

trace は仕様変更に合わせて更新してよい。

更新時に確認すること:

- scenario の目的が変わったか。
- operation contract が変わったか。
- component 責務が変わったか。
- observations を残すべきか消すべきか。
- 既存 trace の変更理由が説明できるか。

ハーネスが pass しても、意味判断が不要になるわけではない。
