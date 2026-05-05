# SLDL v1.0.16 release notes

v1.0.16 is a GitHub Actions test-workflow stabilization release after the v1.0.15 clean-checkout fix.

## Highlights

- Changed the test workflow back to direct pytest installation so GitHub-hosted runners do not fail during editable installation.
- Added explicit setuptools package discovery in `pyproject.toml` so the repository still has clear Python package metadata.
- Added a lightweight package-metadata validation step to the test workflow.
- Kept the v1.0.15 release-check cleanup: CI writes `build/release_summary.json`, then checks generated release reports after `build/release_manifest.json` exists.
- Refreshed generated references, release reports, and release summary metadata for v1.0.16.

## Why this release exists

The v1.0.15 test workflow used `python -m pip install -e ".[test]"`. In a flat repository layout, editable installation can fail when setuptools sees top-level directories such as `docs`, `examples`, `templates`, or `schemas` and package discovery is not explicit. v1.0.16 removes that CI dependency while also making package discovery explicit for future packaging work.

## Validation

Recommended validation commands:

```bash
python -m pip install pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q

mkdir -p build
python -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json build/release_summary.json

python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format json --check docs/release_report.json
```
