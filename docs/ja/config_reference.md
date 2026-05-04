# Config reference

SLDLの設定JSONは `config_type` を持つJSONオブジェクトです。

主な種類は以下です。

- `sldl.project`: 複数文書・複数出力のビルド設定。
- `sldl.schema`: 文書型と論理規則。
- `sldl.export_labels`: 出力ラベル。
- `sldl.latex_build`: LaTeX/PDFビルド設定。
- `sldl.release_check`: リリース品質検査。
- `sldl.snapshot_manifest`: golden snapshot。

公式例は `examples/project_official_examples.json` と `examples/sldl_schema.json` を参照してください。

## v1.0.2の`sldl.template_manifest`追加項目

`templates/template_manifest.json` では、各テンプレートにschemaや関連configを紐づけられます。

```json
{
  "name": "research_report_en",
  "document_type": "ResearchReport",
  "language": "en-US",
  "path": "research_report_en.sldl",
  "schema": "../examples/sldl_schema.json",
  "default_export_config": "../examples/export_labels_en.json",
  "default_latex_build_config": "../examples/latex_build_platex_dvipdfmx_dry_run.json",
  "strict_schema": true
}
```

`strict_schema` が true の場合、`template check`、`template new`、`template project` で生成物を検査するときに、警告も失敗として扱います。

## `sldl.template_manifest`互換性検査

v1.0.6では、`templates/template_manifest.json` を正式manifest、`templates/manifest.json` を互換用コピーとして扱います。config checkでは、両者が同じtemplate名、path、document type、schema bindingを宣言しているか確認します。また、templateディレクトリ内の未登録 `*.sldl` ファイルを警告します。

## Template manifest policy fields (v1.0.4)

`sldl.template_manifest` では、正式manifestと互換用コピーを区別するために `manifest_role` を利用できます。

- `canonical`: `templates/template_manifest.json` に使用します。
- `legacy_compatibility`: 互換用コピーである `templates/manifest.json` に使用します。
- `canonical_manifest`: 互換用コピーでは `template_manifest.json` を指すようにします。
