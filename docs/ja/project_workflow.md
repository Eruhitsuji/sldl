# Project workflow

再現可能な出力生成は `project build` で行います。v1.0.16では、新規資料の入口として `template project` を推奨します。これはSLDL本文とschema-bound project JSONを同時に生成できるためです。

## template-bound project flow

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force

python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

生成されたprojectは、templateに紐づくschema、export config、LaTeX build configを継承します。各document entryには、`template`、`template_source`、`template_manifest`、`template_manifest_role` などのtemplate metadataが記録されます。

## build manifestでの由来確認

`project build` の実行時、template metadataは `sldl_build_manifest.json` に引き継がれます。template由来文書では、以下のSHA-256も記録されます。

- template source file
- canonical template manifest
- schema file
- export config file
- LaTeX build config file

これにより、生成された出力がどのtemplate/configに基づくものか追跡できます。

## 公式project file

公式projectは `examples/project_official_examples.json` です。

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
```

## template schema binding project example

`examples/template_schema_binding_project.json` は、release check内で `template project research_report_en` により再生成されるschema-bound project例です。

```bash
python3 -S -m sldl_compiler.cli project check examples/template_schema_binding_project.json
python3 -S -m sldl_compiler.cli project build examples/template_schema_binding_project.json
python3 -S -m sldl_compiler.cli quality manifest build/template_schema_binding/sldl_build_manifest.json
```
