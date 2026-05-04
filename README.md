# SLDL v1.0.8 Python Compiler

SLDL (Structured Logical Document Language) is a source format and compiler workflow for writing structured reports, project documents, technical notes, and specifications with explicit schemas, citations, output settings, and release-quality checks.

v1.0.8 is a schema-template diagnostics hardening update on top of the v1.0.7 template-first documentation baseline. The core compiler behavior remains compatible with v1.0.7, while template/schema failure cases now produce clearer, release-checkable diagnostics.

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

## What v1.0.8 emphasizes

- Clear diagnostics for missing schema files, wrong schema `config_type`, and missing template files.
- Explicit warnings when a bound template schema is overridden with `--allow-schema-override`.
- Release-checkable negative examples for schema/template binding failures.
- Continued template-first onboarding: `template project` → `project check` → `project build`.
- Continued generated-reference consistency checks and build-manifest SHA-256 validation.

## Important directories

| Path | Purpose |
|---|---|
| `docs/` | English-first static Markdown documentation |
| `docs/ja/` | Japanese companion documentation |
| `examples/` | Official SLDL documents and JSON configuration files |
| `templates/` | Schema-bound SLDL templates and template manifests |
| `sldl_compiler/` | Python compiler package |
| `tests/` | Release workflow and template-binding tests |

## Non-template workflow

Existing project JSON files still work directly:

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## License

This source package is prepared for repository distribution. Add your preferred repository license file before public distribution if needed.
