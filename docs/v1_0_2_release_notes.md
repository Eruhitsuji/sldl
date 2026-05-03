# SLDL v1.0.2 release notes

SLDL v1.0.2 is a small stability update for the template-schema binding system introduced in v1.0.1.

## Main changes

- Added `template explain <name>` to show a template's bound schema, export-label config, LaTeX build config, document type, language, and strictness policy.
- Strengthened template manifest validation.
  - The manifest now checks that `schema` points to an `sldl.schema` file.
  - It checks that `default_export_config` points to an `sldl.export_labels` file.
  - It checks that `default_latex_build_config` points to an `sldl.latex_build` file.
  - It checks that the template's declared `document_type` exists in the bound schema.
- Added document-type mismatch diagnostics for template and project workflows.
  - `template check` fails when a template file declares a different document type from the manifest.
  - `project check` fails when a project document entry declares a different `document_type` from the actual SLDL source file.
- Added an intentional negative example: `examples/template_schema_binding_failure_project.json`.
- Added expected-failure command support to `sldl.release_check` so release checks can verify that invalid examples fail for the right reason.
- Updated README and documentation for the v1.0.2 template-first workflow.

## Compatibility

This release keeps the v1.0.0/v1.0.1 public syntax and project format compatible. The stricter checks may report errors for project files or template manifests that were previously accepted even though their declared template/document-type metadata was inconsistent.

## Recommended check

```bash
python3 -m pytest -q

python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
