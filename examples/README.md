# SLDL official examples

This directory contains the v1.0.9 official bilingual example set and the template-first workflow examples used by the release checks.

## Recommended template workflow

For new material, start by generating a schema-bound project from a template.

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  --document-output examples/template_schema_binding_report.sldl \
  -o examples/template_schema_binding_project.json \
  --formats markdown,html,latex,pdf \
  --build-dir ../build/template_schema_binding \
  --force

python3 -S -m sldl_compiler.cli project check examples/template_schema_binding_project.json
python3 -S -m sldl_compiler.cli project build examples/template_schema_binding_project.json
python3 -S -m sldl_compiler.cli quality manifest build/template_schema_binding/sldl_build_manifest.json
```

This flow preserves template metadata: the template name, template source, canonical manifest path, and template/config SHA-256 hashes in the build manifest.

## Source examples

- `official_project_overview_en.sldl`: detailed English explanation of SLDL, grammar, required JSON files, and the document creation workflow.
- `official_project_overview_ja.sldl`: Japanese companion version of the project overview.
- `research_report_en.sldl`: compact English research report example.
- `research_report_ja.sldl`: compact Japanese research report example.
- `template_schema_binding_report.sldl`: generated template-bound example source.

## Project and configuration files

- `sldl_schema.json`: schema used by all official examples.
- `project_official_examples.json`: project build configuration for all official examples.
- `template_schema_binding_project.json`: generated schema-bound template project example.
- `template_schema_binding_failure_project.json`: intentional negative example for document-type mismatch diagnostics.
- `template_manifest_bad_missing_schema.json`: intentional negative example for missing bound schema diagnostics.
- `template_manifest_bad_wrong_config_type.json`: intentional negative example for bound config-type mismatch diagnostics.
- `template_manifest_bad_missing_template.json`: intentional negative example for missing template file diagnostics.
- `export_labels_en.json`: English export label configuration.
- `export_labels_ja.json`: Japanese export label configuration.
- `latex_build_platex_dvipdfmx_dry_run.json`: dry-run PDF build configuration.
- `latex_build_platex_dvipdfmx.json`: real pLaTeX + dvipdfmx build configuration.
- `release_check.json`: release-quality check target.
- `golden_snapshot.json`: SHA-256 snapshot for generated official outputs.

## Official examples build

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
```

## Template reference checks

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json
```

The negative examples are checked through expected-failure release commands. Legacy `v0*` examples and generated-output archives are intentionally removed from this tree. The v1.0 series should be distributed with this curated example set rather than historical development samples.

## Diagnostics reference checks

```bash
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --check docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --language ja --check docs/ja/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json --check docs/diagnostics_reference.json
```

## v1.0.16 release summary smoke target

`release_summary_smoke_check.json` is a small non-recursive release target used to test `quality release --summary-json` during the main release gate.
