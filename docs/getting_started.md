# Getting Started

This guide shows the recommended v1.0.8 workflow. Start from a schema-bound template, generate a project JSON, build outputs through the project command, and verify the build manifest.

## 1. Inspect available templates

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template check research_report_en
```

`template explain` shows the source template file, document type, bound schema, default export-label config, default LaTeX build config, strict-schema setting, and manifest role. Use `--format json` when another tool should consume the binding metadata.

## 2. Generate a document and project file

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

The generated project inherits the template's schema, export config, and LaTeX build config from `templates/template_manifest.json`. The document entry also records template metadata so the build manifest can preserve provenance.

## 3. Check and build the project

```bash
python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

`project check` verifies that the project metadata and the SLDL document declaration agree on the document type. `quality manifest` verifies build-manifest structure and, for template-generated documents, template metadata and hashes.

## 4. Keep template reference docs synchronized

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json
```

These commands regenerate the reference in memory and fail if the committed static files have drifted from the canonical manifest.

## 5. Run the release quality gate

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

The release check verifies required documentation, config files, template manifest compatibility, intentional negative examples, project builds, build manifests, generated template references, and golden snapshots.

## Non-template workflow

You can still check and build an existing project directly:

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## Template manifest policy

Edit `templates/template_manifest.json` first. `templates/manifest.json` is a legacy compatibility copy for older workflows that still look for `manifest.json`. Release checks validate both files, the generated reference docs, and the template metadata recorded in build manifests.
