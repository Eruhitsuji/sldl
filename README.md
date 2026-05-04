# SLDL v1.0.11 Python Compiler

SLDL (Structured Logical Document Language) is a source format and compiler workflow for writing structured reports, project documents, technical notes, and specifications with explicit schemas, citations, output settings, diagnostics, and release-quality checks.

v1.0.11 adds generated release reports on top of the v1.0.10 reference index baseline. Template references, diagnostics references, CLI help references, release reports, and their machine-readable JSON files can now be regenerated and drift-checked by the release gate.

## Quick Start: template-first workflow

Create a schema-bound document and project JSON from the bundled English research report template:

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

Check and build the generated project:

```bash
python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

Run the full release gate:

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

Generate or check the static release report:

```bash
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown --check docs/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format json --check docs/release_report.json
```

## Inspect templates

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
python3 -S -m sldl_compiler.cli template check research_report_en
```

Regenerate or check the static template reference:

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json
```

## Inspect diagnostics

```bash
python3 -S -m sldl_compiler.cli diagnostics list
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --check docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --language ja --check docs/ja/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json --check docs/diagnostics_reference.json
```

## Inspect generated references

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference index --format markdown --language ja --check docs/ja/reference_index.md
python3 -S -m sldl_compiler.cli reference index --format json --check docs/reference_index.json
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --language ja --check docs/ja/cli_help_reference.md
python3 -S -m sldl_compiler.cli reference cli-help --format json --check docs/cli_help_reference.json
```

## What v1.0.11 emphasizes

- Generated reference index for static generated references.
- Static CLI help reference generated from the implemented argument parser.
- Release-checkable drift checks for template, diagnostics, reference-index, and CLI-help references.
- Machine-readable config validation for `sldl.reference_index` and `sldl.cli_help_reference`.
- Continued schema-template diagnostics, template-reference drift checks, diagnostics-reference drift checks, and build-manifest SHA-256 validation.

## Important directories

| Path | Purpose |
|---|---|
| `docs/` | English-first static Markdown documentation |
| `docs/ja/` | Japanese companion documentation |
| `examples/` | Official SLDL documents and JSON configuration files |
| `templates/` | Schema-bound SLDL templates and template manifests |
| `sldl_compiler/` | Python compiler package |
| `tests/` | Release workflow, template-binding, diagnostics-reference, and generated-reference tests |

## Non-template workflow

Existing project JSON files still work directly:

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## License

This source package is prepared for repository distribution. Add your preferred repository license file before public distribution if needed.
