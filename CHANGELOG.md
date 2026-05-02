# Changelog

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
