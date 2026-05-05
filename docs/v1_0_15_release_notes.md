# SLDL v1.0.15 release notes

v1.0.15 is a clean-checkout CI fix for the GitHub Actions workflows introduced in v1.0.13 and hotfixed in v1.0.14.

The main issue fixed in this release is that local validation could pass when `build/release_manifest.json` already existed, while a clean GitHub Actions checkout could fail because release-report checks tried to read that manifest before the release gate had generated it.

## Changes

- Removed self-dependent `quality-report-*` commands from the in-gate `examples/release_check.json` command list.
- Moved release-report drift checks to the GitHub Actions workflow after the release gate has generated `build/release_manifest.json`.
- Updated the release-check workflow to write CI output to `build/release_summary.json` instead of modifying the tracked `docs/release_summary.json` during CI.
- Updated release-report tests so they generate a temporary manifest instead of relying on a pre-existing `build/release_manifest.json`.
- Updated CI documentation to describe the clean-checkout workflow.
- Updated version metadata to v1.0.15.

## Verification

The intended clean workflow is:

```bash
rm -rf build .pytest_cache
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format markdown --check docs/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format markdown --language ja --check docs/ja/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format json --check docs/release_report.json
```
