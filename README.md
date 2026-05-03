# SLDL v1.0.3 Python Compiler

SLDL (Structured Logical Document Language) is a document source format for writing research reports, technical documents, and specifications with explicit structure, evidence, references, output settings, and release-quality checks.

v1.0.3 is a stable maintenance update on top of the v1.0.0 public baseline. It keeps the English-first/Japanese companion documentation set and strengthens the template workflow by adding manifest compatibility checks, JSON/Markdown template explanations, and template metadata in project build manifests.

## Highlights

- Schema-bound template manifest at `templates/template_manifest.json`.
- Compatibility copy at `templates/manifest.json`; release checks verify that the two manifests stay aligned.
- `template explain <name> --format text|markdown|json` for inspecting template bindings.
- `template check <name>` for checking a bundled template against its declared schema and declared document type.
- `template new` and `template project` perform generation-time schema checks when a template is bound to a schema.
- `project build` records template metadata in `sldl_build_manifest.json` when a project document was generated from a template.
- Project checks report document-type mismatches between project metadata and actual SLDL source files.
- English-first documentation under `docs/`.
- Japanese companion documentation under `docs/ja/`.
- Official bilingual examples under `examples/`.
- Release checks reject old development samples and verify the current docs/examples/snapshots.

## Quick check

```bash
python3 -m pytest -q

python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
python3 -S -m sldl_compiler.cli template check research_report_en

python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

## Template-first workflow

Create a new SLDL document and a project JSON from the bound template:

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/my_report.sldl \
  -o examples/my_report_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/my_report \
  --force
```

Then check and build the generated project:

```bash
python3 -S -m sldl_compiler.cli project check examples/my_report_project.json
python3 -S -m sldl_compiler.cli project build examples/my_report_project.json
python3 -S -m sldl_compiler.cli quality manifest build/my_report/sldl_build_manifest.json
```

## Basic workflow without templates

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## Important directories

| Path | Purpose |
|---|---|
| `docs/` | English-first static Markdown documentation |
| `docs/ja/` | Japanese companion documentation |
| `examples/` | Official SLDL documents and JSON configuration files |
| `templates/` | Schema-bound SLDL templates and template manifests |
| `sldl_compiler/` | Python compiler package |
| `tests/` | Release workflow and template-binding tests |

## License

This project is distributed as a source package for the SLDL compiler and examples. Add your preferred repository license file before public distribution if needed.
