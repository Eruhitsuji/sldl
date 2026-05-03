# SLDL v1.0.3 Release Notes

v1.0.3 is a stable maintenance release focused on template-manifest consistency and template-first project traceability.

## Summary

- Keeps the v1.0 public syntax and v1.0.1/v1.0.2 template-schema binding behavior.
- Adds explicit JSON and Markdown output modes to `template explain`.
- Checks that `templates/template_manifest.json` and `templates/manifest.json` declare the same template set.
- Warns when a `*.sldl` file exists in the template directory but is not declared by the manifest.
- Records template metadata in generated project JSON and `sldl_build_manifest.json`.

## New command forms

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en --format text
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
```

The older `--json` flag remains available as a compatibility alias for `--format json`.

## Build manifest template metadata

When a project document contains template metadata such as `template`, `template_source`, or `template_manifest`, `project build` now writes a `template` object into the build manifest document entry. This makes generated outputs easier to audit because the manifest records which template was used to create the source document.

## Compatibility

v1.0.3 is intended to be compatible with v1.0.0, v1.0.1, and v1.0.2 documents and project files. The new checks are stricter for template manifests, but they are designed to catch packaging drift rather than change SLDL document syntax.
