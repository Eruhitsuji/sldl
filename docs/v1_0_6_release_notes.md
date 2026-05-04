# SLDL v1.0.6 Release Notes

v1.0.6 is a maintenance hardening release for the v1.0.x line. It keeps the public language and project workflow compatible with v1.0.0, while making template-generated projects more auditable.

## Highlights

- Build manifest validation now requires SHA-256 metadata for every recorded template-related file.
- Build manifest validation now checks template metadata against the referenced canonical template manifest entry.
- Generated template reference JSON now records `source_manifest` and `source_manifest_sha256`.
- `config check docs/generated_template_reference.json` now verifies that the generated reference still matches the canonical template manifest metadata.
- Release checks include stricter template reference and build-manifest consistency validation.

## Compatibility

No SLDL grammar change is introduced in v1.0.6. Existing v1.0.x documents and projects remain valid. Projects generated from templates should be rebuilt so their `sldl_build_manifest.json` files include the latest template hash metadata.

## Recommended check

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
