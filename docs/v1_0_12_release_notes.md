# v1.0.12 Release Notes

SLDL v1.0.12 is a CI-oriented maintenance release for the v1.0 series. It keeps the v1.0.11 generated release report workflow and adds a compact machine-readable release summary.

## Highlights

- Added `quality release --summary-json <path>` to write a `sldl.release_summary` file for CI systems.
- Added `quality release --fail-on-warning` as an explicit warning-sensitive release gate option.
- Added release-check metadata for command-level `category` / `release_category` and `severity` classification.
- Extended release manifests and generated reports with warning counts, release-category summaries, and severity summaries.
- Added `docs/release_summary.json` to the generated reference index and release gate.

## Compatibility

This release does not change SLDL source syntax. Existing v1.0.x documents, schemas, templates, and project JSON files remain compatible.
