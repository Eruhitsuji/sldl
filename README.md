# SLDL v1.0.15 Python Compiler

SLDL (Structured Logical Document Language) is a source format and compiler workflow for writing structured reports, project documents, technical notes, and specifications with explicit schemas, citations, output settings, diagnostics, and release-quality checks.

v1.0.15 fixes the CI workflow for clean GitHub Actions checkouts. The bundled workflows install test dependencies explicitly, run the full `quality release` gate without relying on a pre-existing `build/release_manifest.json`, and preserve `build/release_manifest.json` plus `build/release_summary.json` as CI artifacts.

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
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
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

## What v1.0.15 emphasizes

- GitHub Actions workflow files for pytest and release checks.
- CI artifact generation for `build/release_manifest.json` and `build/release_summary.json`.
- Bilingual CI workflow documentation.
- A strict release-summary smoke check using `--fail-on-warning`.
- Continued schema-template diagnostics, generated-reference drift checks, release-report checks, release-summary checks, and build-manifest SHA-256 validation.

## Important directories

| Path | Purpose |
|---|---|
| `.github/workflows/` | GitHub Actions workflows for tests and release checks |
| `docs/` | English-first static Markdown documentation |
| `docs/ja/` | Japanese companion documentation |
| `examples/` | Official SLDL documents and JSON configuration files |
| `templates/` | Schema-bound SLDL templates and template manifests |
| `sldl_compiler/` | Python compiler package |
| `tests/` | Release workflow, template-binding, diagnostics-reference, and generated-reference tests |

## CI workflow

See `docs/ci_workflow.md` and `docs/ja/ci_workflow.md` for the bundled GitHub Actions setup.

## Non-template workflow

Existing project JSON files still work directly:

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## License

This source package is prepared for repository distribution. Add your preferred repository license file before public distribution if needed.
