# Commands reference

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

## Config commands

```bash
python3 -S -m sldl_compiler.cli config list
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli config explain sldl.project
python3 -S -m sldl_compiler.cli config init sldl.project -o project.json
```

## Schema commands

```bash
python3 -S -m sldl_compiler.cli schema check examples/sldl_schema.json
python3 -S -m sldl_compiler.cli schema list examples/sldl_schema.json
```

## Template commands

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template project paper_en   --document-output examples/generated_from_template.sldl   -o examples/generated_project.json   --schema examples/sldl_schema.json   --force
```

## Quality commands

```bash
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
python3 -S -m sldl_compiler.cli quality snapshot-check examples/golden_snapshot.json --base-dir .
```

## Grammar command

```bash
python3 -S -m sldl_compiler.cli grammar
```

## Template-schema binding commands (v1.0.2)

Inspect a bundled template binding:

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en
```

Check a bundled template against its manifest-bound schema:

```bash
python3 -S -m sldl_compiler.cli template check research_report_en
```

Generate a document from a template and immediately check it with the bound schema:

```bash
python3 -S -m sldl_compiler.cli template new research_report_en \
  -o examples/my_report.sldl
```

Generate a document and a project JSON with schema/export/LaTeX defaults inherited from the template manifest:

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  -o examples/my_report_project.json \
  --document-output examples/my_report.sldl
```

## Template explain output modes (v1.0.3)

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en --format text
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
```

The `--json` flag remains as a compatibility alias for `--format json`.
