# SLDL v1.0.5 Release Notes

v1.0.5 is a small stable maintenance release focused on generated template reference consistency and stronger build-manifest traceability.

## Highlights

- Added `template docs --check <path>` to compare generated template-reference output with an existing static file and fail when the file is out of date.
- Added `template docs --language en|ja` so English and Japanese generated reference pages are produced by the same command.
- Added `docs/generated_template_reference.json` as a machine-readable template-reference artifact.
- Added template source/schema/export-config/LaTeX-build-config SHA-256 metadata to template-generated project build manifests.
- Strengthened `quality manifest` validation so recorded template hashes are checked against the referenced files.
- Updated release checks to verify English, Japanese, and JSON generated template references.

## Recommended check

```bash
python3 -m pytest -q

python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json

python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

## Compatibility

v1.0.5 keeps the v1.0.0 public language and project workflow compatible. Existing v1.0.4 template projects remain valid, while newly generated template projects include additional traceability metadata.
