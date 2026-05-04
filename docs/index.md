# SLDL documentation

SLDL (Structured Logical Document Language) is a document source format for research reports, technical documents, and specifications. It keeps the document body, logical support relations, schemas, output settings, and release checks in a repeatable workflow.

English documentation is the primary reference for the v1.0.10 public release. Japanese documentation is provided under `docs/ja/` as a companion translation and usage guide.

## Start here

1. Read `docs/getting_started.md`.
2. Build the official bilingual examples with `examples/project_official_examples.json`.
3. Check the language syntax in `docs/sldl_language_reference.md`.
4. Check JSON configuration in `docs/config_reference.md`.
5. Check schema-bound templates with `docs/template_schema_binding.md`, `docs/generated_template_reference.md`, and `docs/generated_template_reference.json`.
6. Check diagnostic codes with `docs/diagnostics_reference.md` and `docs/diagnostics_reference.json`.
7. Use `docs/reference_index.md` as the generated-reference entry point and `docs/cli_help_reference.md` for CLI help.
8. Run release checks using `docs/release_process.md`.

## Official examples

The official example set is under `examples/`:

- `official_project_overview_en.sldl`: detailed English explanation of the project, grammar, JSON files, and workflow.
- `official_project_overview_ja.sldl`: Japanese companion version.
- `research_report_en.sldl`: compact English research report sample.
- `research_report_ja.sldl`: compact Japanese research report sample.
- `project_official_examples.json`: project file that builds all official examples.

## Documentation map

- `getting_started.md`: quick start.
- `sldl_language_reference.md`: core language syntax.
- `document_model.md`: source/config/output model.
- `project_workflow.md`: repeatable build flow.
- `config_reference.md`: JSON configuration types.
- `commands_reference.md`: CLI commands.
- `github_repository_guide.md`: GitHub-facing documentation layout.
- `bilingual_documentation.md`: English-first and Japanese companion documentation policy.
- `compatibility_policy.md`: v1.x compatibility surface.
- `v1_0_release_notes.md`: v1.0.0 release notes.
- `v1_0_1_release_notes.md`: v1.0.1 release notes.
- `v1_0_5_release_notes.md`: v1.0.5 release notes.
- `v1_0_10_release_notes.md`: v1.0.10 release notes.
- `v1_0_9_release_notes.md`: v1.0.9 release notes.
- `v1_0_8_release_notes.md`: v1.0.8 release notes.
- `v1_0_7_release_notes.md`: v1.0.7 release notes.
- `v1_0_6_release_notes.md`: v1.0.6 release notes.
- `v1_0_4_release_notes.md`: v1.0.4 release notes.
- `v1_0_3_release_notes.md`: v1.0.3 release notes.
- `v1_0_2_release_notes.md`: v1.0.2 release notes.
- `known_limitations.md`: known limitations.
- `template_schema_binding.md`: template-schema binding workflow, manifest compatibility, and diagnostics.
- `template_manifest_migration.md`: v1.0.4 canonical manifest migration guide.
- `generated_template_reference.md`: generated template reference.
- `generated_template_reference.json`: generated machine-readable template reference.
- `diagnostics_reference.md`: generated diagnostic-code reference.
- `diagnostics_reference.json`: generated machine-readable diagnostic-code reference.
- `reference_index.md`: generated reference index.
- `reference_index.json`: generated machine-readable reference index.
- `cli_help_reference.md`: generated CLI help reference.
- `cli_help_reference.json`: generated machine-readable CLI help reference.
- `release_process.md`: release checklist.
