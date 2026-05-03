# SLDL v1.0.1 Python Compiler

SLDL (Structured Logical Document Language) is a document source format for writing research reports, technical documents, and specifications with explicit structure, evidence, references, output settings, and release-quality checks.

v1.0.1 is a stable maintenance update on top of the v1.0.0 public baseline. It keeps the English-first/Japanese companion documentation set and adds stricter template-schema binding so bundled templates can be checked automatically before use.

## Highlights

- Schema-bound template manifest at `templates/template_manifest.json`.
- `template check <name>` for checking a bundled template against its declared schema.
- `template new` and `template project` perform generation-time schema checks when a template is bound to a schema.
- English-first documentation under `docs/`.
- Japanese companion documentation under `docs/ja/`.
- Official bilingual examples under `examples/`.
- A detailed project-overview sample describing SLDL grammar, required JSON files, and the document creation workflow.
- A single project file, `examples/project_official_examples.json`, that builds the official example set.
- Release checks that reject old development samples and verify the current docs/examples/snapshots.
- A repository-level `.gitignore` for Python, LaTeX, build, and editor artifacts.

## Quick check

```bash
python3 -m pytest -q

python3 -S -m sldl_compiler.cli template check research_report_en

python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

## Basic workflow

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
python3 -S -m sldl_compiler.cli quality snapshot-check examples/golden_snapshot.json --base-dir .
```

## Documentation

- `docs/index.md`
- `docs/getting_started.md`
- `docs/sldl_language_reference.md`
- `docs/document_model.md`
- `docs/project_workflow.md`
- `docs/commands_reference.md`
- `docs/config_reference.md`
- `docs/template_schema_binding.md`
- `docs/github_repository_guide.md`
- `docs/bilingual_documentation.md`
- `docs/compatibility_policy.md`
- `docs/v1_0_release_notes.md`
- `docs/v1_0_1_release_notes.md`
- `docs/known_limitations.md`
- `docs/release_process.md`
- Japanese companion docs: `docs/ja/`

## Official examples

- `examples/official_project_overview_en.sldl`
- `examples/official_project_overview_ja.sldl`
- `examples/research_report_en.sldl`
- `examples/research_report_ja.sldl`
- `examples/project_official_examples.json`
- `templates/template_manifest.json`

## 日本語概要

SLDLは、研究報告書・技術文書・仕様書を、文書構造、根拠、参考文献、出力設定、品質検査まで含めて扱うための文書記述言語です。v1.0.1では、英語第一の正式ドキュメント、日本語補助ドキュメント、英語・日本語の公式サンプルに加えて、テンプレートとschemaの紐づけ検査を安定機能として提供します。
