# SLDL v1.0.9 Release Notes

v1.0.9 is a generated diagnostics reference update for the v1.0 stable series. It keeps the v1.0.8 schema-template diagnostics behavior and adds a static, release-checkable reference for diagnostic codes.

## Added

- `diagnostics list` command for listing known `E_*` and `W_*` codes discovered in compiler sources.
- `diagnostics docs` command for generating Markdown or JSON diagnostics references.
- `docs/diagnostics_reference.md` as the English diagnostics reference.
- `docs/ja/diagnostics_reference.md` as the Japanese companion diagnostics reference.
- `docs/diagnostics_reference.json` as the machine-readable diagnostics reference.
- `sldl.diagnostics_reference` config validation.

## Release checks

The release gate now verifies that diagnostics references are synchronized with the compiler source:

```bash
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --check docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --language ja --check docs/ja/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json --check docs/diagnostics_reference.json
```

## Compatibility

The public v1.x document, project, schema, template, and export behavior remains compatible with v1.0.8. This release adds inspection and documentation commands, so existing valid projects and templates should continue to pass.
