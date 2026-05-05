# SLDL Release Report（日本語）

`quality release` の結果から生成した静的なリリースレポートです。レポート自身を検査するコマンドは循環差分を避けるため集計から除外されます。

- version: `1.0.16`
- source_manifest: `build/release_manifest.json`
- status: `passed`
- checks: `212/212 passed, 0 failed, 13 warnings`

## カテゴリ別サマリー

| カテゴリ | 合計 | 成功 | 失敗 | 警告 |
|---|---:|---:|---:|---:|
| `build-manifest-check` | 2 | 2 | 0 | 0 |
| `command` | 59 | 59 | 0 | 0 |
| `config-check` | 18 | 18 | 0 | 13 |
| `forbidden-paths` | 1 | 1 | 0 | 0 |
| `required-file` | 123 | 123 | 0 | 0 |
| `snapshot-check` | 1 | 1 | 0 | 0 |
| `syntax-check` | 7 | 7 | 0 | 0 |
| `target-config` | 1 | 1 | 0 | 0 |

## リリース分類別サマリー

| リリース分類 | 合計 | 成功 | 失敗 | 警告 |
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

## 重要度別サマリー

| 重要度 | 合計 | 成功 | 失敗 | 警告 |
|---|---:|---:|---:|---:|
| `error` | 203 | 203 | 0 | 0 |
| `info` | 1 | 1 | 0 | 0 |
| `warning` | 8 | 8 | 0 | 13 |

## 診断コード

| Code | Level | Count |
|---|---|---:|
| `W_CONFIG_PATH_MISSING` | `warning` | 12 |
| `W_TEMPLATE_MANIFEST_LEGACY` | `warning` | 1 |

## 失敗した検査

なし。

## コマンド

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown --check docs/release_report.md
python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format json --check docs/release_report.json
python3 -S -m sldl_compiler.cli quality release --targets examples/release_summary_smoke_check.json --summary-json build/release_summary_smoke.json
```
