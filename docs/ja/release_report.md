# SLDL Release Report（日本語）

`quality release` の結果から生成した静的なリリースレポートです。レポート自身を検査するコマンドは循環差分を避けるため集計から除外されます。

- version: `1.0.11`
- source_manifest: `build/release_manifest.json`
- status: `passed`
- checks: `190/190 passed, 0 failed`

## カテゴリ別サマリー

| カテゴリ | 合計 | 成功 | 失敗 |
|---|---:|---:|---:|
| `build-manifest-check` | 2 | 2 | 0 |
| `command` | 56 | 56 | 0 |
| `config-check` | 16 | 16 | 0 |
| `forbidden-paths` | 1 | 1 | 0 |
| `required-file` | 107 | 107 | 0 |
| `snapshot-check` | 1 | 1 | 0 |
| `syntax-check` | 6 | 6 | 0 |
| `target-config` | 1 | 1 | 0 |

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
```
