# CI workflow

v1.0.13 connects the existing release gate to GitHub Actions. The local workflow remains the source of truth, and the CI workflows simply run the same commands in a clean checkout.

## Included workflows

| File | Purpose |
|---|---|
| `.github/workflows/test.yml` | Runs the pytest suite on Python 3.10, 3.11, and 3.12. |
| `.github/workflows/release-check.yml` | Runs the release gate and writes `build/release_manifest.json` plus `docs/release_summary.json`. |

## Local command equivalent

The release workflow runs the same command that should be used before packaging a release:

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
```

The test workflow runs:

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
```

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` keeps CI independent from unrelated pytest plugins that may be installed in the runner image. The repository's `pyproject.toml` also disables common external plugins, so normal local `python3 -m pytest -q` remains supported.

## Artifacts

The release-check workflow uploads these files when available:

- `build/release_manifest.json`
- `docs/release_summary.json`
- `docs/release_report.md`
- `docs/release_report.json`

`docs/release_summary.json` is the compact CI-facing result. It contains the overall status, total/passed/failed counts, warning counts, release-category summaries, severity summaries, diagnostic codes, and failed checks.

## Recommended branch protection

For repository operation, require these checks before merging:

- `SLDL tests / pytest`
- `SLDL release check / release-check`

This keeps template-schema bindings, generated references, diagnostics references, release reports, release summaries, official examples, and build manifests synchronized.
