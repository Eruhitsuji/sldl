# Changelog

## 1.0.8 - schema-template diagnostics hardening

- Added explicit diagnostics for missing schema files and schema config-type mismatches.
- Strengthened template manifest validation for missing template files, missing bound schemas, and bound config-type mismatches.
- Improved template/project document-type mismatch messages with expected type, actual type, schema path, and recovery hints.
- Added a visible warning for explicit schema overrides with `--allow-schema-override`.
- Added negative examples and release-check `expect_failure` commands for representative schema-template failure modes.

## 1.0.7 - template-first documentation workflow update

- Reorganized README Quick Start around `template project` followed by `project check` and `project build`.
- Expanded English and Japanese getting-started guides for template-bound project creation, build manifest validation, and generated template reference checks.
- Rewrote English and Japanese commands references to include `template explain`, `template check`, `template docs --check`, and template-bound project commands.
- Updated project workflow documentation to explain template metadata and SHA-256 provenance in build manifests.
- Added release checks and tests that keep documentation-oriented workflow examples present and synchronized.

## 1.0.7 - template/build manifest consistency hardening

- Require template-related SHA-256 metadata in build manifest validation.
- Validate build manifest template metadata against the referenced canonical template manifest entry.
- Add source manifest metadata to generated template reference JSON.
- Strengthen release checks for generated template reference and template-bound build manifests.

## 1.0.5 - generated template reference consistency update

- Added `template docs --check <path>` for release-checkable drift detection between generated template references and static documentation files.
- Added `template docs --language en|ja` so English and Japanese generated template references are produced by the same command.
- Added `docs/generated_template_reference.json` as a machine-readable generated template reference.
- Strengthened project build manifests with template source/schema/export/LaTeX config SHA-256 metadata.
- Strengthened `quality manifest` checks so recorded template hashes are validated against the referenced files.
- Updated release checks to verify generated English, Japanese, and JSON template references.

## 1.0.4 - canonical template manifest policy update

- Formalized `templates/template_manifest.json` as the canonical template manifest.
- Kept `templates/manifest.json` as a legacy compatibility copy with explicit `manifest_role` and `canonical_manifest` metadata.
- Added `template docs --format markdown|json` to regenerate a template reference from the manifest.
- Added generated template reference documentation under `docs/`.
- Strengthened build-manifest validation so template-generated documents must record canonical template manifest metadata.
- Updated project workflow and commands documentation for the v1.0.4 template policy.

## 1.0.3 - template manifest compatibility update

- Added `template explain <name> --format markdown|json|text` while keeping `--json` as a compatibility alias.
- Added template manifest compatibility checks between `templates/template_manifest.json` and `templates/manifest.json`.
- Added detection of unlisted `*.sldl` files in template directories.
- Added template metadata to generated project JSON and project build manifests.
- Updated getting-started documentation for the template-first workflow.
- Updated release checks for the new explain output modes and manifest compatibility validation.

## 1.0.2 - template binding diagnostics update

- Added `template explain <name>` for inspecting template-schema/export/LaTeX bindings.
- Strengthened `sldl.template_manifest` validation for bound config types and schema-defined document types.
- Added template and project document-type mismatch diagnostics.
- Added `expect_failure` support for release-check commands.
- Added `examples/template_schema_binding_failure_project.json` as an intentional negative example.
- Updated README and template-schema binding documentation for the v1.0.2 workflow.

## 1.0.1 - template-schema binding stability update

- Added `templates/template_manifest.json` as the canonical bundled template manifest.
- Added schema-bound template checking with `template check <name>`.
- Updated `template new` and `template project` so generated files are checked against the template's bound schema.
- Added manifest fields for `schema`, `default_export_config`, `default_latex_build_config`, and `strict_schema`.
- Added schema-bound official templates for English/Japanese research reports and project overviews.
- Updated release checks so bundled templates fail the release if they drift from the declared schema.

## 1.0.0 - stable bilingual public release

- Promoted the cleaned SLDL tree to the first stable public release.
- Updated package, CLI, config, snapshot, and release-check metadata to `1.0.0`.
- Added repository-level `.gitignore` for Python, LaTeX, build, snapshot, and editor artifacts.
- Replaced pre-release planning documents with stable release notes and bilingual-documentation guidance.
- Kept the v1.0 compatibility surface focused on current public syntax, JSON configs, official examples, and release checks.
- Kept official English and Japanese SLDL examples as the canonical sample set.
- Updated release check and golden snapshot targets for the v1.0.0 official example set.

## 0.15.3 - bilingual official examples preparation

- Added English-first documentation entry point `docs/index.md`.
- Added Japanese companion documentation under `docs/ja/`.
- Added `docs/github_repository_guide.md` for static GitHub-facing Markdown documentation.
- Added official English and Japanese SLDL examples.
- Added detailed project-overview examples that explain SLDL grammar, required JSON files, and the document creation workflow.
- Replaced the single v1-ready sample project with `examples/project_official_examples.json`.
- Updated release check and golden snapshot targets for the bilingual official example set.
- Updated version metadata to `0.15.3`.

## 0.15.2 - v1.0 compatibility reset preparation

- Removed historical development examples and generated build logs from the distribution tree.
- Rebuilt `examples/` around a curated v1-ready canonical workflow.
- Rebuilt `docs/` around current user-facing references instead of historical development notes.
- Added `forbidden_paths` and `forbidden_globs` to `sldl.release_check`.
- Updated `quality release` to fail when removed legacy paths are accidentally reintroduced.
- Updated the `grammar` command to print `docs/sldl_language_reference.md`.
- Prepared the repository so v1.0.0 can be released with fresh samples, fresh docs, and no v0 development logs.

## 0.15.1 - RC polish and example cleanup

- Final pre-reset RC polish stage.
- Historical details before v0.15.2 are intentionally summarized rather than kept as active release material.
