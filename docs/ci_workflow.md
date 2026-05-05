# CI workflow

v1.0.14 is a CI dependency hotfix for the GitHub Actions workflows introduced in v1.0.13. The local workflow remains the source of truth, and the CI workflows run the same checks in a clean checkout with explicit dependency setup.

## Included workflows

| File | Purpose |
|---|---|
| `.github/workflows/test.yml` | Installs pytest, then runs the pytest suite on Python 3.10, 3.11, and 3.12. |
| `.github/workflows/release-check.yml` | Prepares `build/`, runs the release gate, and writes `build/release_manifest.json` plus `docs/release_summary.json`. |

## Local command equivalent

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
```

The test workflow runs this dependency setup before pytest because GitHub Actions starts from a clean Python environment:

```bash
python3 -m pip install --upgrade pip
python3 -m pip install pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
```

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` keeps CI independent from unrelated pytest plugins installed in the runner image. Normal local `python3 -m pytest -q` remains supported.

## Artifacts

The release-check workflow uploads `build/release_manifest.json`, `docs/release_summary.json`, `docs/release_report.md`, and `docs/release_report.json` when available.
