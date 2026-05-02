# Getting started

This guide uses the v1.0.0 official bilingual example set.

## 1. Check the project configuration

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
```

## 2. Check all example documents through the project

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
```

## 3. Build Markdown, HTML, LaTeX, and dry-run PDF outputs

```bash
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

The build writes files under `build/official_examples/` and records the build result in `build/official_examples/sldl_build_manifest.json`.

## 4. Validate the build manifest

```bash
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
```

## 5. Run release checks

```bash
python3 -S -m sldl_compiler.cli quality release   --targets examples/release_check.json   --manifest build/release_manifest.json
```

## 6. Read the detailed sample

Open `examples/official_project_overview_en.sldl` first. It explains what SLDL is, what grammar elements are used, which JSON files are required, and how the document creation workflow proceeds.
