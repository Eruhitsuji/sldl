# Project workflow

`project build` is the standard workflow for repeatable output generation.

## Official project file

The official project is `examples/project_official_examples.json`.

It declares:

- all official English and Japanese SLDL input files
- the shared schema file
- language-specific export label files
- the LaTeX build configuration
- Markdown, HTML, LaTeX, and PDF output paths
- the build manifest path

## Commands

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## Manifest

The generated manifest records document diagnostics and output results.

```bash
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
```

## Snapshot

After accepting generated outputs, the snapshot can be regenerated with:

```bash
python3 -S -m sldl_compiler.cli quality snapshot \
  build/official_examples/official_project_overview_en.md \
  build/official_examples/official_project_overview_en.html \
  build/official_examples/official_project_overview_en.tex \
  build/official_examples/official_project_overview_ja.md \
  build/official_examples/official_project_overview_ja.html \
  build/official_examples/official_project_overview_ja.tex \
  build/official_examples/research_report_en.md \
  build/official_examples/research_report_en.html \
  build/official_examples/research_report_en.tex \
  build/official_examples/research_report_ja.md \
  build/official_examples/research_report_ja.html \
  build/official_examples/research_report_ja.tex \
  -o examples/golden_snapshot.json \
  --base-dir .
```


## v1.0.5 template metadata in build manifests

When a project is generated with `template project`, each project document records `template`, `template_source`, `template_manifest`, and `template_manifest_role`. During `project build`, these values are copied into `sldl_build_manifest.json`. The release quality gate validates this metadata so template-generated documents remain traceable to the canonical `templates/template_manifest.json`.
