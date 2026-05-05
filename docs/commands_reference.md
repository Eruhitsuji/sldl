# Commands reference

This reference is synchronized with the v1.0.12 template-first workflow with generated diagnostics references.

## Recommended workflow commands

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force

python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

## Document commands

```bash
python3 -S -m sldl_compiler.cli check examples/official_project_overview_en.sldl --schema examples/sldl_schema.json
python3 -S -m sldl_compiler.cli build examples/official_project_overview_en.sldl --schema examples/sldl_schema.json -o build/official_project_overview_en_ast.json
python3 -S -m sldl_compiler.cli export examples/official_project_overview_en.sldl --schema examples/sldl_schema.json --format markdown -o build/official_project_overview_en.md
```

## Project commands

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

`project check` validates project JSON structure and also checks document-type agreement between project metadata and SLDL source files. `project build` writes requested outputs and a `sldl_build_manifest.json` file.

## Config commands

```bash
python3 -S -m sldl_compiler.cli config list
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli config explain sldl.project
python3 -S -m sldl_compiler.cli config explain sldl.template_manifest
python3 -S -m sldl_compiler.cli config init sldl.project -o project.json
```

## Schema commands

```bash
python3 -S -m sldl_compiler.cli schema check examples/sldl_schema.json
python3 -S -m sldl_compiler.cli schema list examples/sldl_schema.json
```

## Template inspection commands

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
python3 -S -m sldl_compiler.cli template check research_report_en
```

`template explain` supports `text`, `markdown`, and `json`. The `--json` flag remains as a compatibility alias for `--format json`.

## Template generation commands

Generate only an SLDL document:

```bash
python3 -S -m sldl_compiler.cli template new research_report_en \
  -o examples/my_report.sldl
```

Generate both an SLDL document and a project JSON with schema/export/LaTeX defaults inherited from the canonical template manifest:

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

## Template reference generation and drift checks

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown -o docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja -o docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json -o docs/generated_template_reference.json

python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json
```

`template docs --check` regenerates the reference in memory and fails if the static file is stale.


## Diagnostics reference commands

```bash
python3 -S -m sldl_compiler.cli diagnostics list
python3 -S -m sldl_compiler.cli diagnostics list --json
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown -o docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --language ja -o docs/ja/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json -o docs/diagnostics_reference.json

python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --check docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --language ja --check docs/ja/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json --check docs/diagnostics_reference.json
```

`diagnostics docs --check` regenerates the diagnostic-code reference in memory and fails if the static file is stale. Use `docs/diagnostics_reference.md` when an `E_*` or `W_*` code appears in command output.

## Quality commands

```bash
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
python3 -S -m sldl_compiler.cli quality snapshot-check examples/golden_snapshot.json --base-dir .
```

For template-generated outputs, `quality manifest` verifies template name, source path, manifest role, and SHA-256 hashes for the template source, template manifest, schema, export config, and LaTeX build config.

## Grammar command

```bash
python3 -S -m sldl_compiler.cli grammar
```

## Generated reference commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference index --format markdown --language ja --check docs/ja/reference_index.md
python3 -S -m sldl_compiler.cli reference index --format json --check docs/reference_index.json
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --language ja --check docs/ja/cli_help_reference.md
python3 -S -m sldl_compiler.cli reference cli-help --format json --check docs/cli_help_reference.json
```

## Release report commands

```bash
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown --language ja --check docs/ja/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format json --check docs/release_report.json
python3 -S -m sldl_compiler.cli config explain sldl.release_report
```

`quality report` renders an `sldl.release_manifest` as stable human-readable Markdown or machine-readable JSON. The generated report excludes report-check commands from its aggregate summary to avoid circular drift.

## CI release summary

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json \
  --fail-on-warning
```
