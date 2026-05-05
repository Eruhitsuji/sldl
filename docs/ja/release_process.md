# Release process

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --check docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json --check docs/diagnostics_reference.json
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

v1.0.12では、template referenceとdiagnostics referenceのdrift checkもrelease品質確認に含めます。次の版では、version表記、release notes、生成reference、snapshot、release-check manifestを更新してからパッケージ化します。

## v1.0.12 generated references

Before packaging, regenerate and check `template docs`, `diagnostics docs`, `reference index`, and `reference cli-help` outputs. The release gate includes drift checks for these generated files.

## v1.0.12 生成リリースレポート

release gateを実行した後、次のコマンドで静的release reportを生成または確認します。

```bash
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown --check docs/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown --language ja --check docs/ja/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format json --check docs/release_report.json
```

release report自身の検査コマンドが自分自身のsummaryを変化させないように、report-check系のcommandは集計から除外されます。
