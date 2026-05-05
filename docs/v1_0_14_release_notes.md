# SLDL v1.0.14 release notes

v1.0.14 is a CI dependency hotfix release for the GitHub Actions workflows introduced in v1.0.13. It keeps the same release-gate design, but makes the workflows safer in a clean GitHub-hosted runner.

## Highlights

- Added an explicit pytest installation step to `.github/workflows/test.yml`.
- Added a `mkdir -p build` preparation step to `.github/workflows/release-check.yml`.
- Updated `pyproject.toml` to v1.0.14 and added optional test dependency metadata.
- Updated bilingual CI workflow documentation to describe dependency setup.
- Extended release checks and tests so CI workflow dependency setup and release metadata stay synchronized.

## Compatibility

No SLDL language syntax or document-model compatibility changes are introduced in this release. Existing v1.0.13 documents, templates, schemas, and project files remain compatible.
