# CI workflow

v1.0.15 keeps the GitHub Actions workflows from v1.0.13 and v1.0.14, but makes them safe for a clean checkout. The local release gate remains the source of truth; CI prepares dependencies explicitly and avoids relying on pre-existing `build/` files.

## Included workflows

| File | Purpose |
|---|---|
| `.github/workflows/test.yml` | Installs the test extra and runs the pytest suite on Python 3.10, 3.11, and 3.12. |
| `.github/workflows/release-check.yml` | Runs the release gate, writes CI artifacts under `build/`, then checks generated release-report drift after the manifest exists. |

## Local command equivalent

```bash
python -m pip install -e ".[test]"
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q

mkdir -p build
python -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json build/release_summary.json

python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format markdown --check docs/release_report.md
python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format markdown --language ja --check docs/ja/release_report.md
python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format json --check docs/release_report.json
```

## Why release-report checks run after the release gate

`docs/release_report.md` and `docs/release_report.json` are derived from `build/release_manifest.json`. A clean GitHub Actions checkout does not have that manifest before the release gate runs. Therefore, v1.0.15 keeps release-report drift checks outside the in-gate command list and runs them immediately after the manifest is generated.

## Artifacts

The release-check workflow uploads `build/release_manifest.json`, `build/release_summary.json`, `docs/release_report.md`, and `docs/release_report.json` when available.

`build/release_summary.json` is the compact CI-facing result. The tracked `docs/release_summary.json` remains a generated reference file for documentation and release verification.
