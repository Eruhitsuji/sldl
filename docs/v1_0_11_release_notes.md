# SLDL v1.0.11 Release Notes

v1.0.11 adds generated release reports for the v1.0 stable series. The release manifest produced by `quality release` can now be rendered as stable Markdown and JSON for human review, documentation, and CI summaries.

## Highlights

- Added `quality report` for Markdown/JSON release reports generated from `sldl.release_manifest`.
- Added `docs/release_report.md`, `docs/ja/release_report.md`, and `docs/release_report.json`.
- Added `sldl.release_report` config validation.
- Added release-report drift checks to `examples/release_check.json`.
- Linked release report generation to the generated reference index.
- Normalized release reports so report-check commands do not create circular drift.

## Typical commands

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json

python3 -S -m sldl_compiler.cli quality report \
  build/release_manifest.json \
  --format markdown \
  --check docs/release_report.md

python3 -S -m sldl_compiler.cli quality report \
  build/release_manifest.json \
  --format json \
  --check docs/release_report.json
```
