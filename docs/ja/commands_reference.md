# Commands reference

## 基本コマンド

```bash
python3 -S -m sldl_compiler.cli check examples/official_project_overview_ja.sldl --schema examples/sldl_schema.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
```

英語版の完全な一覧は `docs/commands_reference.md` を参照してください。

## template-schema binding commands (v1.0.2)

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


## Template-schema binding commands (v1.0.2)

テンプレートの紐づけ情報を確認します。

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en
```

manifestに紐づいたschemaでテンプレートを検査します。

```bash
python3 -S -m sldl_compiler.cli template check research_report_en
```

## template explainの出力形式 (v1.0.3)

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en --format text
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
```

`--json` は `--format json` の互換エイリアスとして残しています。
