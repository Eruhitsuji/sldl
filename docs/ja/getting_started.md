# はじめに

このページでは、v1.0.8で推奨する流れを説明します。基本は、schema-bound templateからSLDL文書とproject JSONを生成し、project commandで出力し、最後にbuild manifestを検査する流れです。

## 1. 利用できるテンプレートを確認する

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template check research_report_en
```

`template explain` では、template本体、document type、紐づいたschema、既定のexport label config、既定のLaTeX build config、strict-schema設定、manifest roleを確認できます。機械処理したい場合は `--format json` を使います。

## 2. 文書とproject fileを生成する

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

生成されたprojectは、`templates/template_manifest.json` に記録されたschema、export config、LaTeX build configを継承します。また、document entryにはtemplate情報が記録されるため、build manifestから由来を追跡できます。

## 3. projectを検査してビルドする

```bash
python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

`project check` は、project metadataとSLDL本文のdocument typeが一致するかを検査します。`quality manifest` はbuild manifestの構造と、template由来文書のmetadata/hashを検査します。

## 4. template reference docsの同期を確認する

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json
```

これらはtemplate referenceをメモリ上で再生成し、静的ファイルが正式manifestからずれている場合に失敗します。

## 5. release quality gateを実行する

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

release checkでは、必要ファイル、config、template manifest互換性、意図的な失敗例、project build、build manifest、generated template reference、golden snapshotをまとめて検査します。

## templateを使わない流れ

既存のproject JSONはそのまま直接検査・ビルドできます。

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## template manifest方針

編集対象は `templates/template_manifest.json` です。`templates/manifest.json` は古いワークフローとの互換性のために残すコピーです。release checkでは、両manifest、generated reference docs、build manifest内のtemplate metadataを検査します。
