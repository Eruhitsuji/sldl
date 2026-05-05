# Config reference

SLDL configuration files are JSON objects with a `config_type` field.

## `sldl.project`

Builds one or more SLDL documents into one or more output formats.

Important keys:

- `documents`
- `schemas`
- `export_config`
- `latex_build_config`
- `output_dir`
- `write_manifest`

Canonical example: `examples/project_official_examples.json`.

## `sldl.schema`

Defines document types and logic rules.

Canonical example: `examples/sldl_schema.json`.

## `sldl.export_labels`

Defines labels used by exporters.

Canonical examples:

- `examples/export_labels_en.json`
- `examples/export_labels_ja.json`

## `sldl.latex_build`

Defines a LaTeX-to-PDF build pipeline. The canonical release-check configuration uses dry-run mode.

Canonical example: `examples/latex_build_platex_dvipdfmx_dry_run.json`.

## `sldl.release_check`

Declares release-quality checks.

Important keys:

- `required_files`
- `forbidden_paths`
- `forbidden_globs`
- `config_files`
- `commands`
- `project_files`
- `build_project_files`
- `build_manifest_files`
- `golden_snapshot`
- `compile_paths`

`forbidden_paths` and `forbidden_globs` prevent old development samples and generated logs from being reintroduced.

Canonical example: `examples/release_check.json`.

## `sldl.snapshot_manifest`

Records SHA-256 hashes and file sizes for generated golden outputs.

Canonical example: `examples/golden_snapshot.json`.

## `sldl.template_manifest` additions in v1.0.2

`templates/template_manifest.json` may bind each template to supporting config files:

```json
{
  "name": "research_report_en",
  "document_type": "ResearchReport",
  "language": "en-US",
  "path": "research_report_en.sldl",
  "schema": "../examples/sldl_schema.json",
  "default_export_config": "../examples/export_labels_en.json",
  "default_latex_build_config": "../examples/latex_build_platex_dvipdfmx_dry_run.json",
  "strict_schema": true
}
```

When `strict_schema` is true, warnings found while checking a generated template are treated as errors by `template check`, `template new`, and `template project`.

## `sldl.template_manifest` compatibility checks

v1.0.6 keeps `templates/template_manifest.json` as the canonical manifest and `templates/manifest.json` as a legacy compatibility copy. Config checks verify that the two files declare the same template names, paths, document types, and schema bindings. The checker also warns when a `*.sldl` file in the template directory is not listed by the manifest.

## Template manifest policy fields (v1.0.4)

`sldl.template_manifest` may include `manifest_role` to distinguish the canonical bundled manifest from a legacy compatibility copy.

- `canonical`: use this for `templates/template_manifest.json`.
- `legacy_compatibility`: use this for `templates/manifest.json` when it is kept as a compatibility copy.
- `canonical_manifest`: in the legacy copy, this should point to `template_manifest.json`.

## `sldl.diagnostics_reference`

Records the generated diagnostics-code reference used by v1.0.16 release checks.

Important keys:

- `codes`
- `counts`
- `language`
- `version`

Canonical example: `docs/diagnostics_reference.json`.

## `sldl.reference_index`

Records paths, kinds, and SHA-256 hashes for generated static reference documents. It is drift-checked by the v1.0.16 release gate.

Important keys:

- `version`
- `language`
- `references`

## `sldl.cli_help_reference`

Records static CLI help generated from the implemented argument parser. It is drift-checked by the v1.0.16 release gate.

Important keys:

- `version`
- `language`
- `command_count`
- `commands`

## `sldl.release_report`

Generated release report for the release-quality workflow. It summarizes an `sldl.release_manifest` with stable fields for documentation and CI.

Important keys:

- `summary`: total, passed, and failed check counts after normalization.
- `category_summary`: counts grouped by release-check category.
- `diagnostic_codes`: diagnostics grouped by code.
- `failed_checks`: failed check names and diagnostics.
- `ci_summary`: machine-readable pass/fail status.

## sldl.release_summary

Compact machine-readable release summary written by `quality release --summary-json`. It records pass/fail totals, warning counts, release-category summaries, severity summaries, diagnostic code counts, and failed checks for CI systems.
