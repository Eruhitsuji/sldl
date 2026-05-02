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
