# Migration guide from development v0 files to v1-ready files

Historical v0 examples are not active compatibility inputs. Migrate useful content into the current official layout instead of preserving old filenames.

## Recommended mapping

| Old role | v1-ready role |
|---|---|
| ad hoc `.sldl` sample | `examples/research_report_en.sldl` or `examples/research_report_ja.sldl` |
| explanatory sample | `examples/official_project_overview_en.sldl` or `examples/official_project_overview_ja.sldl` |
| old schema JSON | `examples/sldl_schema.json` |
| old project JSON | `examples/project_official_examples.json` |
| old release check | `examples/release_check.json` |
| old generated output directory | regenerate under `build/official_examples/` |

## Steps

1. Move only the source document content you still need.
2. Use the current schema and config names.
3. Run `config check` and `project check`.
4. Regenerate outputs with `project build`.
5. Recreate snapshots with `quality snapshot` only after the output is accepted.

The v1.0 package should not contain historical generated logs or unpublished version-numbered samples.
