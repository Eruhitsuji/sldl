# SLDL Release Report

This static release report is generated from a `quality release` manifest. Report-check commands are excluded from the aggregate to avoid circular drift.

- version: `1.0.11`
- source_manifest: `build/release_manifest.json`
- status: `passed`
- checks: `190/190 passed, 0 failed`

## Category summary

| Category | Total | Passed | Failed |
|---|---:|---:|---:|
| `build-manifest-check` | 2 | 2 | 0 |
| `command` | 56 | 56 | 0 |
| `config-check` | 16 | 16 | 0 |
| `forbidden-paths` | 1 | 1 | 0 |
| `required-file` | 107 | 107 | 0 |
| `snapshot-check` | 1 | 1 | 0 |
| `syntax-check` | 6 | 6 | 0 |
| `target-config` | 1 | 1 | 0 |

## Diagnostic codes

| Code | Level | Count |
|---|---|---:|
| `W_CONFIG_PATH_MISSING` | `warning` | 12 |
| `W_TEMPLATE_MANIFEST_LEGACY` | `warning` | 1 |

## Failed checks

None.

## Commands

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown --check docs/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format json --check docs/release_report.json
```
