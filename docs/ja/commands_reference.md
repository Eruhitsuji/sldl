# Commands reference

## 基本コマンド

```bash
python3 -S -m sldl_compiler.cli check examples/official_project_overview_ja.sldl --schema examples/sldl_schema.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
```

英語版の完全な一覧は `docs/commands_reference.md` を参照してください。

## template-schema binding commands (v1.0.1)

manifestで紐づけられたschemaに対してテンプレートを検査します。

```bash
python3 -S -m sldl_compiler.cli template check research_report_en
```

テンプレートから文書を生成し、その場で紐づけられたschemaで検査します。

```bash
python3 -S -m sldl_compiler.cli template new research_report_en \
  -o examples/my_report.sldl
```

テンプレートmanifestのschema/export/LaTeX既定値を反映したproject JSONも同時に生成します。

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  -o examples/my_report_project.json \
  --document-output examples/my_report.sldl
```
