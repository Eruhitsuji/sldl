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
