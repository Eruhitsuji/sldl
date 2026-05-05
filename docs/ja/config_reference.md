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

## `sldl.diagnostics_reference`

v1.0.15のrelease checkで使用する、生成済み診断コードリファレンスです。

主なキー:

- `codes`
- `counts`
- `language`
- `version`

代表例: `docs/diagnostics_reference.json`。

## `sldl.reference_index`

生成済みリファレンス文書のパス、種別、SHA-256を記録する索引です。v1.0.15のrelease checkでdrift checkされます。

重要キー:

- `version`
- `language`
- `references`

## `sldl.cli_help_reference`

実装済みCLI parserから生成されるCLI helpの静的リファレンスです。v1.0.15のrelease checkでdrift checkされます。

重要キー:

- `version`
- `language`
- `command_count`
- `commands`

## `sldl.release_report`

release品質確認ワークフロー用の生成済みリリースレポートです。`sldl.release_manifest` をもとに、ドキュメント確認とCIで扱いやすい安定したサマリーを記録します。

重要なキー:

- `summary`: 正規化後の検査合計、成功数、失敗数。
- `category_summary`: release checkカテゴリごとの件数。
- `diagnostic_codes`: 診断コードごとの件数。
- `failed_checks`: 失敗した検査名と診断。
- `ci_summary`: 機械処理しやすい成功/失敗ステータス。

## sldl.release_summary

`quality release --summary-json` が出力するCI向けの機械可読release summaryです。成功/失敗数、警告数、release-category別集計、severity別集計、診断コード数、失敗した検査を記録します。
