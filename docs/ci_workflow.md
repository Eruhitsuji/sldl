# CI workflow

v1.0.16 keeps the clean checkout release workflow from v1.0.15 and makes the test workflow safe on GitHub-hosted runners. The local release gate remains the source of truth; CI installs pytest directly, validates package metadata statically, and avoids relying on pre-existing `build/` files.

## Included workflows

| File | Purpose |
|---|---|
| `.github/workflows/test.yml` | Installs the test extra and runs the pytest suite on Python 3.10, 3.11, and 3.12. |
| `.github/workflows/release-check.yml` | Runs the release gate, writes CI artifacts under `build/`, then checks generated release-report drift after the manifest exists. |

## Local command equivalent

```bash
python -m pip install --upgrade pip
python -m pip install pytest
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


## Editable install metadata

The v1.0.15 test workflow used editable installation, which can fail in a flat repository layout when package discovery is not explicit. v1.0.16 avoids making CI depend on editable installation, and it also adds explicit setuptools package discovery so only `sldl_compiler` is considered package code.

## Why release-report checks run after the release gate

`docs/release_report.md` and `docs/release_report.json` are derived from `build/release_manifest.json`. A clean GitHub Actions checkout does not have that manifest before the release gate runs. Therefore, v1.0.16 keeps release-report drift checks outside the in-gate command list and runs them immediately after the manifest is generated.

## Artifacts

The release-check workflow uploads `build/release_manifest.json`, `build/release_summary.json`, `docs/release_report.md`, and `docs/release_report.json` when available.

`build/release_summary.json` is the compact CI-facing result. The tracked `docs/release_summary.json` remains a generated reference file for documentation and release verification.
