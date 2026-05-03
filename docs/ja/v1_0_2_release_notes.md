# SLDL v1.0.2 リリースノート

SLDL v1.0.2は、v1.0.1で追加したtemplate-schema bindingを安定化する小規模更新です。

## 主な変更

- `template explain <name>` を追加しました。
  - テンプレートに紐づくschema、export labels、LaTeX build config、document type、言語、strict設定を確認できます。
- template manifestの検査を強化しました。
  - `schema` が `sldl.schema` を指すことを検査します。
  - `default_export_config` が `sldl.export_labels` を指すことを検査します。
  - `default_latex_build_config` が `sldl.latex_build` を指すことを検査します。
  - テンプレートの `document_type` が紐づけschema内に存在することを検査します。
- template/projectのdocument type不整合診断を追加しました。
  - `template check` は、manifestの `document_type` とテンプレート本文のdocument typeが異なる場合に失敗します。
  - `project check` は、project JSONの `document_type` と実際のSLDL本文のdocument typeが異なる場合に失敗します。
- 意図的な失敗例として `examples/template_schema_binding_failure_project.json` を追加しました。
- `sldl.release_check` に expected-failure command を追加し、失敗すべき例が正しく失敗することをrelease checkで確認できるようにしました。
- READMEとドキュメントをv1.0.2のテンプレート起点ワークフローに更新しました。

## 互換性

v1.0.0/v1.0.1の公開構文とproject形式は維持しています。ただし、これまで受理されていたproject JSONやtemplate manifestでも、宣言されたtemplate/document type metadataに不整合がある場合はエラーとして検出されます。

## 推奨確認

```bash
python3 -m pytest -q

python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
