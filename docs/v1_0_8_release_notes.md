# SLDL v1.0.8 Release Notes

v1.0.8 is a diagnostics hardening update for the template-first v1.0 workflow. It keeps the v1.0.7 documentation flow intact and makes schema/template binding failures easier to understand and easier to check in the release gate.

## Highlights

- Added explicit schema input diagnostics for missing schema files and wrong schema `config_type` values.
- Improved template manifest diagnostics for missing template files, missing bound schemas, and bound config-type mismatches.
- Improved document-type mismatch messages so they identify the expected type, actual document type, schema path, and recovery hint.
- Added a visible warning when a manifest-bound template schema is overridden with `--allow-schema-override`.
- Added release-checkable negative examples for common schema-template failure modes.

## Compatibility

The public v1.x command surface remains compatible with v1.0.7. Existing valid projects and templates should continue to pass. Configurations that reference missing or wrongly typed schema/template files may now fail earlier with clearer diagnostics instead of producing a later traceback or generic warning.

## Recommended check

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
