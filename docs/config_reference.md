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
