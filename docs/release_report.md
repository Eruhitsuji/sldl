# SLDL Release Report

This static release report is generated from a `quality release` manifest. Report-check commands are excluded from the aggregate to avoid circular drift.

- version: `1.0.16`
- source_manifest: `build/release_manifest.json`
- status: `passed`
- checks: `212/212 passed, 0 failed, 13 warnings`

## Category summary

| Category | Total | Passed | Failed | Warnings |
|---|---:|---:|---:|---:|
| `build-manifest-check` | 2 | 2 | 0 | 0 |
| `command` | 59 | 59 | 0 | 0 |
| `config-check` | 18 | 18 | 0 | 13 |
| `forbidden-paths` | 1 | 1 | 0 | 0 |
| `required-file` | 123 | 123 | 0 | 0 |
| `snapshot-check` | 1 | 1 | 0 | 0 |
| `syntax-check` | 7 | 7 | 0 | 0 |
| `target-config` | 1 | 1 | 0 | 0 |

## Release category summary

| Release category | Total | Passed | Failed | Warnings |
|---|---:|---:|---:|---:|
| `build-manifest-check` | 2 | 2 | 0 | 0 |
| `ci-workflow` | 1 | 1 | 0 | 0 |
| `command` | 4 | 4 | 0 | 0 |
| `config` | 8 | 8 | 0 | 0 |
| `config-check` | 18 | 18 | 0 | 13 |
| `core-cli` | 5 | 5 | 0 | 0 |
| `diagnostics` | 2 | 2 | 0 | 0 |
| `forbidden-paths` | 1 | 1 | 0 | 0 |
| `generated-reference` | 21 | 21 | 0 | 0 |
| `negative-example` | 6 | 6 | 0 | 0 |
| `release-summary` | 2 | 2 | 0 | 0 |
| `required-file` | 123 | 123 | 0 | 0 |
| `snapshot-check` | 1 | 1 | 0 | 0 |
| `syntax-check` | 7 | 7 | 0 | 0 |
| `target-config` | 1 | 1 | 0 | 0 |
| `template-workflow` | 10 | 10 | 0 | 0 |

## Severity summary

| Severity | Total | Passed | Failed | Warnings |
|---|---:|---:|---:|---:|
| `error` | 203 | 203 | 0 | 0 |
| `info` | 1 | 1 | 0 | 0 |
| `warning` | 8 | 8 | 0 | 13 |

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
python3 -S -m sldl_compiler.cli quality release --targets examples/release_summary_smoke_check.json --summary-json build/release_summary_smoke.json
```
