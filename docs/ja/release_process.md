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

v1.0.9では、template referenceとdiagnostics referenceのdrift checkもrelease品質確認に含めます。次の版では、version表記、release notes、生成reference、snapshot、release-check manifestを更新してからパッケージ化します。
