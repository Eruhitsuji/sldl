# コマンドリファレンス

このページはv1.0.8のtemplate-first workflowに合わせた主要コマンド一覧です。

## 推奨ワークフロー

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

## 文書コマンド

```bash
python3 -S -m sldl_compiler.cli check examples/official_project_overview_ja.sldl --schema examples/sldl_schema.json
python3 -S -m sldl_compiler.cli export examples/official_project_overview_ja.sldl --schema examples/sldl_schema.json --format markdown -o build/official_project_overview_ja.md
```

## projectコマンド

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

`project check` はproject JSONの構造に加えて、project metadataとSLDL本文のdocument typeが一致するかも検査します。

## config/schemaコマンド

```bash
python3 -S -m sldl_compiler.cli config list
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli config explain sldl.project
python3 -S -m sldl_compiler.cli config explain sldl.template_manifest
python3 -S -m sldl_compiler.cli schema check examples/sldl_schema.json
python3 -S -m sldl_compiler.cli schema list examples/sldl_schema.json
```

## template確認コマンド

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
python3 -S -m sldl_compiler.cli template check research_report_en
```

`template explain` は `text`、`markdown`、`json` に対応します。`--json` は `--format json` の互換エイリアスです。

## template生成コマンド

SLDL文書のみ生成する場合:

```bash
python3 -S -m sldl_compiler.cli template new research_report_en \
  -o examples/my_report.sldl
```

SLDL文書とproject JSONをまとめて生成する場合:

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

## template reference生成・drift check

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown -o docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja -o docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json -o docs/generated_template_reference.json

python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json
```

`template docs --check` はtemplate referenceをメモリ上で再生成し、静的ファイルが古い場合に失敗します。

## qualityコマンド

```bash
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
python3 -S -m sldl_compiler.cli quality snapshot-check examples/golden_snapshot.json --base-dir .
```

Template由来の出力では、`quality manifest` がtemplate名、source path、manifest role、template source/schema/export config/LaTeX build configなどのSHA-256を検査します。
