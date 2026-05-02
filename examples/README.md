# SLDL official examples

This directory contains the v1.0.0 official bilingual example set for v1.0 public release.

## Source examples

- `official_project_overview_en.sldl`: detailed English explanation of SLDL, grammar, required JSON files, and the document creation workflow.
- `official_project_overview_ja.sldl`: Japanese companion version of the project overview.
- `research_report_en.sldl`: compact English research report example.
- `research_report_ja.sldl`: compact Japanese research report example.

## Configuration files

- `sldl_schema.json`: schema used by all official examples.
- `project_official_examples.json`: project build configuration for all official examples.
- `export_labels_en.json`: English export label configuration.
- `export_labels_ja.json`: Japanese export label configuration.
- `latex_build_platex_dvipdfmx_dry_run.json`: dry-run PDF build configuration.
- `latex_build_platex_dvipdfmx.json`: real pLaTeX + dvipdfmx build configuration.
- `release_check.json`: release-quality check target.
- `golden_snapshot.json`: SHA-256 snapshot for generated official outputs.

## Build

```bash
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

Legacy `v0*` examples and generated-output archives are intentionally removed from this tree. The v1.0 release should be distributed with this curated example set rather than historical development samples.
