# SLDL v1.0.10 Release Notes

v1.0.10 is a generated reference index update for the v1.0 stable series. It keeps the v1.0.9 diagnostics reference workflow and adds a single generated entry point for template, diagnostics, and CLI help references.

## Highlights

- Added `reference index` to generate Markdown/JSON indexes for generated reference documents.
- Added `reference cli-help` to capture implemented CLI `--help` output as static Markdown/JSON documentation.
- Added `docs/reference_index.md`, `docs/reference_index.json`, `docs/cli_help_reference.md`, and `docs/cli_help_reference.json`.
- Added Japanese companion pages under `docs/ja/`.
- Added config validation for `sldl.reference_index` and `sldl.cli_help_reference`.
- Extended release checks so generated reference index and CLI help documents are drift-checked.

## Recommended verification

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

## New commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown
python3 -S -m sldl_compiler.cli reference index --format json
python3 -S -m sldl_compiler.cli reference cli-help --format markdown
python3 -S -m sldl_compiler.cli reference cli-help --format json
```
