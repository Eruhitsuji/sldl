# SLDL v1.0.1 release notes

SLDL v1.0.1 is a maintenance release focused on template-schema binding. It keeps v1.0.0 compatibility and adds stricter checks around bundled templates.

## Added

- `templates/template_manifest.json` as the canonical bundled template manifest.
- `template check <name>` to validate a template against its bound schema.
- Generation-time validation for `template new` and `template project` when the template declares a schema.
- Manifest fields for `schema`, `default_export_config`, `default_latex_build_config`, and `strict_schema`.
- Schema-bound English/Japanese research-report and project-overview templates.
- Release-check coverage for template manifest validation and schema-bound template generation.

## Compatibility

The update is intended to be compatible with v1.0.0 documents and project JSON files. The old `templates/manifest.json` name is kept as a compatibility alias, while `templates/template_manifest.json` is the canonical name for v1.0.1 and later.
