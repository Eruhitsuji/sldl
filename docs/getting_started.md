# Getting Started

This guide shows the recommended v1.0.5 workflow. For new documents, start from a schema-bound template, generate a project JSON, then build all outputs through the project command.

## 1. Inspect a template

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template check research_report_en
python3 -S -m sldl_compiler.cli template docs --format markdown -o docs/generated_template_reference.md
```

`template explain` shows the template source file, document type, bound schema, export-label config, LaTeX build config, and strict-schema setting. In v1.0.5 it supports `text`, `markdown`, and `json` output formats. `templates/template_manifest.json` is the canonical manifest; `templates/manifest.json` is kept only as a compatibility copy.

## 2. Generate a document and project file

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

The generated project inherits the template's bound schema and default export/LaTeX settings. The document entry also records template metadata so the later build manifest can preserve the source template information.

## 3. Check and build

```bash
python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

The project command checks the actual SLDL document type against the project metadata. If the project says `ResearchReport` but the file declares another document type, the check fails.

## 4. Run the release quality gate

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

The release check verifies required documentation, config files, template manifest compatibility, intentional negative examples, project builds, build manifests, and golden snapshots.

## Non-template workflow

You can still check and build an existing project directly:

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## Template manifest policy in v1.0.4

Edit `templates/template_manifest.json` first. `templates/manifest.json` is a legacy compatibility copy for older workflows that still look for `manifest.json`. The release check validates both files and the build-manifest validator checks that template-generated project outputs record the canonical manifest path.
