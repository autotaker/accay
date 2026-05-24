# Python コーディング規約
## 1. 対象
この規約は `src/accay/` と `tests/` に置く Python code を対象にする。
ドキュメント生成用の一時 script や調査用 script も、リポジトリに残す場合はこの規約に従う。
ただし、probe test や一時的な検証 script は、読み捨てであることを file 名や配置で明確にしてよい。
この規約は実装の実用標準であり、architecture の公開契約を増やすものではない。
内部 class 名、dataclass 名、関数シグネチャは、実装中に必要に応じて調整してよい。
守るべき中心は、system / component / boundary / output の責務境界である。
## 2. Python version
Accay は Python 3.11 以上を前提にする。
Python 3.11 で標準提供される typing 機能は使ってよい。
`list[str]`、`dict[str, object]`、`str | None` のような組み込み generic と union 記法を使う。
`from __future__ import annotations` は、循環参照回避や annotation 評価遅延が必要な module で使ってよい。
3.12 以上でしか動かない構文や標準 library API は、採用前に runtime 要件を更新する。
外部 package に依存する場合は、標準 library だけで十分でない理由を明確にする。
小さな helper のためだけに依存 package を増やさない。
## 3. 基本スタイル
読みやすさと境界の明確さを、短さより優先する。
module の公開 API は小さく保つ。
domain logic、parser、filesystem access、rendering を不用意に混ぜない。
file / path は `pathlib.Path` を使う。
YAML / JSON / XML は専用 parser を使い、文字列分解に頼らない。
例外は利用者向け diagnostics に変換できる境界で捕捉する。
ハーネスは最終的な意味判断を行わない。
「不明」「要レビュー」「形式不正」は diagnostics として表現し、accept / reject を勝手に決めない。
## 4. 命名
| 対象 | 規約 | 例 |
|---|---|---|
| module | snake_case | `review_pack.py` |
| function | snake_case | `load_component_artifacts` |
| class | PascalCase | `OperationDirectory` |
| dataclass field | snake_case | `schema_ref` |
| constant | UPPER_SNAKE_CASE | `DEFAULT_CONFIG` |
| pytest fixture | snake_case | `fixture_repo` |
| CLI option | kebab-case | `--component-dir` |
名前は責務を表す。
`data`、`obj`、`info` のような広すぎる名前は避ける。
短い局所変数では `path`、`name`、`item` を使ってよい。
公開関数では `result` だけを返すより、何の結果かがわかる型や名前にする。
boolean は `is_`、`has_`、`should_`、`allow_` などで意味を明確にする。
否定形 boolean は読み間違えやすいため避ける。
## 5. module 境界
`workspace` は repository root、config、初期化、skill install を扱う。
`system` は scenario、sequence、trace、system validation、desk-debug context を扱う。
`operations` は OpenAPI、operations.yaml、JSON Schema を operation contract として参照可能にする。
`component` は acceptance-scope、test-map、semantics、interfaces、review context、JUnit regression を扱う。
`output` は diagnostics、context、report、dashboard 表示を扱う。
`cli.py` は orchestration layer とする。
CLI は処理順序を決めてよい。
CLI に validation logic や regression logic の本体を置かない。
`output` は表示用の集約をしてよい。
`output` が system / component の正本 file を直接読んで判断しない。
`system` から `component` の artifact loader を呼ばない。
`component` から `system` の artifact loader を呼ばない。
`operations` から `system` や `component` の具体 artifact を読まない。
共通 helper が必要な場合は、依存方向を壊さない場所に置く。
共通化のためだけに責務境界を薄めない。
## 6. imports
import は標準 library、third-party、local の順にまとめる。
同じ group 内では module 名の辞書順を基本にする。
循環 import が起きたら、型定義の移動より先に module 責務を見直す。
型だけに必要な import は `typing.TYPE_CHECKING` を使ってよい。
wildcard import は使わない。
relative import は package 内の近い module に限って使ってよい。
遠い package へ `...` を重ねる import は避ける。
公開 API を module の上部に寄せる必要がある場合は、`__all__` を使ってよい。
ただし、`__all__` で隠すより、module を小さくすることを優先する。
## 7. formatting
formatter はプロジェクトで採用した標準設定に従う。
1 行は無理に詰め込まない。
長い dict literal や list literal は複数行に分ける。
条件式が長い場合は、名前付き helper に分ける。
深い nest は早期 return や小さな関数で浅くする。
blank line は意味のあるまとまりを区切るために使う。
コメントで章立てを作るほど長い関数は分割を検討する。
formatting のためだけに domain logic を読みにくくしない。
## 8. typing
公開関数と module 境界を越える関数には type hint を付ける。
test helper にも、読み手が迷う引数や戻り値には type hint を付ける。
`Any` は境界で受け取った未検証データに限定する。
`Any` を内部に流し続けない。
YAML / JSON parser の戻り値は、早い段階で検証して typed object に寄せる。
`dict[str, Any]` を広く持ち回らない。
`object` は「中身をまだ信用しない値」に使う。
`cast` は最後の手段にする。
`cast` を使う場合は、その直前で runtime validation が済んでいることを読み取れるようにする。
`Literal` は固定文字列の状態値に使ってよい。
状態値が増える、または複数 module で共有される場合は enum 相当の表現を検討する。
`Optional[T]` より `T | None` を使う。
`Sequence[T]`、`Mapping[K, V]` は、変更しない入力に使う。
戻り値として変更可能な値を返す場合は `list[T]` や `dict[K, V]` を使ってよい。
## 9. dataclasses
内部モデルは dict のまま広げず、必要に応じて dataclass へ変換する。
dataclass は処理の境界を明確にするために使う。
architecture では dataclass 名を固定しない。
公開契約ではなく実装都合の型として扱う。
不変でよい model は `frozen=True` を検討する。
順序比較が不要な dataclass では `order=True` を付けない。
大量の instance を作る model では `slots=True` を検討する。
ただし、debug や test のしやすさを損なうなら無理に使わない。
default value に mutable object を直接置かない。
`field(default_factory=list)` のように factory を使う。
validation を dataclass の `__post_init__` に詰め込みすぎない。
外部入力の validation は parser / loader 側で行う。
dataclass は検証済みの値を表す形に寄せる。
## 10. function design
1 つの関数は 1 つの責務に寄せる。
CLI 引数の処理と domain logic を混ぜない。
filesystem access は artifact loader や workspace helper に寄せる。
pure function にできる処理は pure function にする。
report rendering と validation logic を同じ関数に混ぜない。
関数名は副作用の有無がわかる動詞にする。
`load_` は filesystem など外部から読む処理に使う。
`parse_` は文字列や bytes を構造化する処理に使う。
`validate_` は diagnostics を返す処理に使う。
`render_` は表示用文字列や文書を作る処理に使う。
`write_` は filesystem へ書く処理に使う。
戻り値と例外の使い分けを揃える。
通常の入力不備は diagnostics として返す。
programmer error は例外としてよい。
呼び出し側が自然に回復できる失敗は、例外より結果型で返すことを検討する。
引数が多くなったら、dataclass や設定 object への集約を検討する。
ただし、意味の異なるものを雑に `Context` へ詰め込まない。
## 11. error handling
外部 file の欠落、形式不正、schema validation failure は diagnostics に変換する。
diagnostic は、どの file のどの要素がなぜ問題かを示す。
可能なら path、line、field、component、operation、case id を含める。
例外 message だけをそのまま user output に出さない。
例外を握りつぶさない。
`except Exception` は CLI 境界や top-level 境界に限定する。
捕捉した例外は、diagnostic に変換するか、文脈を追加して再送出する。
stack trace は debug 用に有用だが、通常の user output では読みやすい summary を優先する。
「見つからない」と「読めない」と「形式が違う」は別の diagnostic にする。
複数 file を検証するときは、1 つの失敗で可能な範囲の検証全体を止めない。
ただし、後続処理の前提が壊れている場合は、その範囲だけを止める。
## 12. diagnostics
diagnostics は共通の型で扱う。
severity は散在する文字列にしない。
代表的な severity は `error`、`warning`、`info`、`needs_review` とする。
`needs_review` は意味判断が必要な状態に使う。
ハーネスが判断できないことを `error` にしない。
機械的な形式不正や参照不整合は `error` にする。
生成 report では、diagnostic の順序が安定するようにする。
同じ入力から同じ順序の output が出ることを重視する。
diagnostic code を導入する場合は、長期的に変更しにくい名前にする。
message は人間が読んで次の行動を取れる粒度にする。
## 13. pathlib と filesystem
path は `str` ではなく `Path` で受け渡す。
CLI 引数として受け取った path は、CLI 境界で `Path` に変換する。
表示用に文字列化する場合だけ `str(path)` を使う。
repository root からの相対 path を user output に出すことを優先する。
絶対 path は debug や machine-readable output で必要な場合に限定する。
file 存在確認と読み込みの間に状態が変わる可能性を考慮する。
`exists()` だけに頼らず、読み込み時の例外も扱う。
text file は encoding を明示する。
基本は UTF-8 とする。
newline の違いに依存する比較を避ける。
生成 file は deterministic にする。
timestamp、run id、絶対 path は test で差し替えられるようにする。
既存 file を上書きする処理は、上書き条件を明確にする。
`init` や `install` は既存成果物を不用意に壊さない。
一時 file は `.accay/runs/`、`.accay/generated/`、`.accay/cache/` など目的に合う場所へ置く。
## 14. YAML
YAML は専用 parser で読む。
文字列 split や正規表現で YAML 構造を読まない。
YAML から読んだ値は信用しない。
期待する mapping、sequence、scalar を runtime で確認する。
必須 field と任意 field を loader で明確に扱う。
unknown field を許すかどうかは artifact ごとに決める。
trace、acceptance-scope、test-map、operations.yaml は、用途ごとに loader を分ける。
system trace の loader が component scope を読まない。
component artifact loader が system trace を正本として要求しない。
YAML の anchor や merge key に依存した仕様は避ける。
人間が読み書きする file なので、error message は field path を示す。
## 15. JSON と JSON Schema
JSON は標準 library または採用済み parser で読む。
JSON 文字列を手で連結して生成しない。
JSON output は key order が必要な箇所では安定させる。
schema file は `Path` と schema id / ref の両方を意識して扱う。
schema validation の失敗は diagnostics に変換する。
validation error には、schema path と instance path を含める。
trace の `input` / `output` は JSON Schema で検証する。
JSON Schema で表せない意味は `semantics.md` や observations の領域に残す。
schema resolver は operations package 側に寄せる。
component validation が独自に schema 解決規則を持たない。
## 16. XML と JUnit
XML は専用 parser で読む。
JUnit XML を正規表現で読まない。
外部 XML では entity 展開や巨大 input への耐性を意識する。
JUnit testcase は `classname + name` を基本 key とする。
同一 key が複数 JUnit XML に出た場合は validate error にする。
複数 JUnit XML は 1 つの test result set として扱う。
XML parser の低レベル例外は、file path 付き diagnostic に変換する。
JUnit XML の仕様差は probe test で観察してから本実装へ取り込む。
component regression は JUnit XML と `test-map.yaml` を照合する。
component regression が system trace を読まない。
## 17. parser と validator
parser は外部形式を内部表現へ変換する。
validator は内部表現の整合性を確認して diagnostics を返す。
parser と validator を同じ module に置いてよいが、責務は分ける。
parser は可能な範囲で構文エラーと型エラーを具体化する。
validator は参照整合性、必須関係、schema validation などを扱う。
意味判断が必要なものは validator で断定しない。
境界の parser は外部形式ごとに置く。
OpenAPI、operations.yaml、JSON Schema、JUnit XML は、それぞれ専用の読み取り箇所を持つ。
parser の返す object は、後続処理で扱いやすい最小構造にする。
元 file の location 情報が diagnostics に必要なら、内部表現へ保持する。
## 18. CLI code
CLI は user input を受け取り、処理を組み立て、exit code を返す。
CLI は validation / regression の本体 logic を持たない。
引数 parsing、config loading、repository root 検出は workspace / CLI 境界に寄せる。
stdout は user が読む summary に使う。
stderr は error summary や diagnostics に使ってよい。
machine-readable output を追加する場合は、人間向け output と混ぜない。
exit code は command ごとに一貫させる。
形式不正や validation error がある場合は non-zero にする。
`needs_review` だけで non-zero にするかは command の契約として明示する。
CLI option の default は config と矛盾しないようにする。
環境変数を読む場合は、読み取り箇所を限定する。
CLI から各 package を呼ぶ順序は architecture の代表シーケンスに従う。
## 19. output と report
output package は結果を読みやすく整形する。
output package は正本 artifact を直接読んで判断しない。
Markdown report と HTML report は同じ source result から作る。
表示のために validation result を改変しない。
report は deterministic にする。
同じ input から同じ主要構造が出るようにする。
HTML escaping を忘れない。
Markdown に user input を埋め込む場合も、意図しない構造化に注意する。
context pack はエージェントや人間が読む前提で、必要な情報を過不足なく並べる。
context pack が正本 file を更新しない。
## 20. tests
テストは Contract Test、Unit Test、Probe Test に分ける。
Contract Test は Accay の公開振る舞いを固定する。
Contract Test は CLI と fixture project を中心にする。
Unit Test は parser、resolver、matcher、formatter など局所処理を支える。
Probe Test は調査用であり、通常 CI の対象にしない。
fixture は最小にする。
1 つの fixture に複数の無関係な scenario を詰め込まない。
test name は壊れたときに対象挙動がわかる名前にする。
implementation detail ではなく公開される振る舞いを優先して assert する。
diagnostics の test では code、severity、path、message の主要部分を確認する。
message 全文の完全一致は、必要な箇所に限定する。
golden file は report / context の主要構造確認に使う。
timestamp、run id、絶対 path は fixture で固定または正規化する。
filesystem を使う test は `tmp_path` を使う。
test が user の実 repository や home directory に依存しないようにする。
## 21. test data
YAML、JSON、XML の fixture は、人間が意図を読める大きさにする。
正常系 fixture と異常系 fixture を混ぜない。
異常系 fixture は、何が壊れているか file 名でわかるようにする。
JUnit XML fixture は duplicate、missing、failed、skipped を必要に応じて分ける。
OpenAPI fixture は operationId、schema ref、status code の焦点を分ける。
trace fixture は system side の正本として扱う。
component fixture は component side の正本として扱う。
相手側の成果物を参考情報として含める test では、その前提を test 名に含める。
## 22. comments
なぜその境界にしているかを補足するコメントは書いてよい。
コードを読めばわかる処理の説明は書かない。
複雑な validation rule の前には短い意図コメントを置く。
外部仕様の癖を扱う箇所では、仕様名や理由をコメントに残す。
一時的な回避策には、条件と削除の目安を書く。
TODO は owner や判断条件がないまま放置しない。
コメントで古い設計を温存しない。
設計が変わったらコメントも更新する。
## 23. configuration
config loader は workspace package に寄せる。
config の default は 1 箇所で管理する。
config file がない場合の挙動を command ごとに明確にする。
config の値は読み取り時に型と範囲を検証する。
path 設定は repository root 基準か current working directory 基準かを明確にする。
環境変数で上書きできる値は限定する。
secret を扱う設計にしない。
MVP では外部 service token を前提にしない。
## 24. security and robustness
ユーザー repository の file を読む前提なので、入力は常に不正であり得る。
path traversal を許すような path join をしない。
repository root 外へ書く処理は原則として避ける。
外部 file 参照を解決する場合は、許可された root 内か確認する。
巨大 file で process が落ちないよう、必要なら size limit を設ける。
再帰 traversal では ignore 対象や上限を意識する。
HTML report では escaping を行う。
XML、YAML、JSON の parser は安全な設定を使う。
## 25. performance
MVP では単純で正しい実装を優先する。
ただし、同じ file を何度も読む構造は避ける。
operation directory は必要に応じて構築し、複数 validation で使い回してよい。
cache を導入する場合は、invalidate 条件を明確にする。
処理順序の安定性を performance より優先する場面がある。
大量 diagnostics の sort は deterministic にする。
早すぎる最適化で module 境界を壊さない。
## 26. anti-patterns
system validation から component の `test-map.yaml` を直接読む。
component regression から system trace を正本として読む。
CLI に validation logic を詰め込む。
output package で artifact を読み直して判断する。
YAML / JSON / XML を文字列 split や正規表現で読む。
未検証の `dict[str, Any]` を多段に渡す。
`except Exception: pass` で失敗を隠す。
user 向け message に Python 例外だけをそのまま出す。
絶対 path や timestamp を test で固定せずに golden file へ入れる。
複数の責務を `utils.py` に集め続ける。
意味判断が必要な状態を機械的に `accepted` と断定する。
外部仕様の差異を probe test なしに本実装へ押し込む。
## 27. review checklist
変更した module は architecture の依存方向を守っているか。
CLI に domain logic が入り込んでいないか。
parser は専用 parser を使っているか。
未検証の外部入力を typed model として扱っていないか。
diagnostic は user が次に何を直せばよいかわかるか。
filesystem access と pure logic は分けられているか。
Path、encoding、newline の扱いは明示されているか。
test は公開挙動または重要な局所処理を確認しているか。
fixture は必要最小限で、意図が file 名からわかるか。
run id、timestamp、絶対 path による揺れを test で抑えているか。
## 28. 迷ったときの優先順
第 1 に、architecture の責務境界を守る。
第 2 に、利用者が直せる diagnostics を出す。
第 3 に、外部形式を専用 parser と検証で扱う。
第 4 に、テストしやすい pure logic を保つ。
第 5 に、実装を小さく保つ。
短い code より、壊れたときに原因を追える code を優先する。
便利な共通化より、system / component の正本を混ぜないことを優先する。
ハーネスが判断しすぎそうな場合は、diagnostic と context に戻す。
最終的な受け入れ判断は、人間とエージェントが行う。
