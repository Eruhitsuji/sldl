# Template Manifest Migration Guide

## Canonical file

Starting with v1.0.4, the canonical bundled template manifest is:

```text
templates/template_manifest.json
```

`templates/manifest.json` is kept only as a legacy compatibility copy.

## Recommended update flow

1. Edit `templates/template_manifest.json`.
2. Copy the same template list to `templates/manifest.json` if older tools still need it.
3. Keep `manifest_role` as `canonical` in `template_manifest.json`.
4. Keep `manifest_role` as `legacy_compatibility` and `canonical_manifest` as `template_manifest.json` in `manifest.json`.
5. Run the release gate.

```bash
python3 -S -m sldl_compiler.cli config check templates/template_manifest.json
python3 -S -m sldl_compiler.cli config check templates/manifest.json
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
```

## Build manifest traceability

Projects generated with `template project` record the canonical manifest path. `quality manifest` checks this metadata so generated outputs can be traced back to the template and schema binding used to create them.
