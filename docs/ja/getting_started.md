# はじめに

このページでは、v1.0.6で推奨するワークフローを説明します。新規文書では、schema-bound templateから文書とproject JSONを生成し、project commandで各形式へ出力する流れが基本です。

## 1. テンプレートを確認する

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template check research_report_en
python3 -S -m sldl_compiler.cli template docs --format markdown -o docs/generated_template_reference.md
```

`template explain` では、テンプレート本体、document type、紐づいたschema、export label config、LaTeX build config、strict-schema設定を確認できます。v1.0.6では `text`、`markdown`、`json` の出力形式に対応しています。`templates/template_manifest.json` が正式なmanifestで、`templates/manifest.json` は互換用コピーです。

## 2. 文書とproject fileを生成する

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

生成されたprojectは、テンプレートに紐づいたschemaと既定のexport/LaTeX設定を継承します。また、document entryにはtemplate情報が記録されるため、後からbuild manifestで由来を確認できます。

## 3. 検査とビルドを行う

```bash
python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

project commandは、project側のdocument type指定とSLDL本文のdocument typeが一致するかも確認します。

## 4. release quality gateを実行する

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

release checkでは、必要ファイル、config、template manifest互換性、意図的な失敗例、project build、build manifest、golden snapshotをまとめて検査します。

## v1.0.4のtemplate manifest方針

`templates/template_manifest.json` を正式な編集対象とします。`templates/manifest.json` は古いワークフローとの互換性のために残すコピーです。release checkでは両者の内容と、build manifestに記録されたtemplate情報を検査します。
