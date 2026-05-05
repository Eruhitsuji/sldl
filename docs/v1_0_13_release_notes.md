# SLDL v1.0.13 release notes

v1.0.13 is the CI workflow integration release. It keeps the v1.0.12 release-summary foundation and adds repository-ready GitHub Actions workflows plus bilingual CI documentation.

## Highlights

- Added `.github/workflows/test.yml` for pytest checks on Python 3.10, 3.11, and 3.12.
- Added `.github/workflows/release-check.yml` for the full `quality release` gate.
- Added `docs/ci_workflow.md` and `docs/ja/ci_workflow.md`.
- Added release-check coverage for CI workflow files and CI documentation.
- Added a strict release-summary smoke command using `--fail-on-warning`.
- Updated README, documentation index, release process notes, and release metadata to v1.0.13.

## Recommended CI command

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
```

The generated `docs/release_summary.json` is intended for CI artifacts and status summaries.
