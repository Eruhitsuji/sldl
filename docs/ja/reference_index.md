# SLDL Reference Index（日本語）

生成済みリファレンス文書への入口です。v1.0.16では、template reference、diagnostics reference、CLI help reference、release report、CI向けrelease summaryをまとめて確認できます。

- version: `1.0.16`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| テンプレートリファレンス | `docs/generated_template_reference.md` | `markdown` | `` | `bae1f2cbed41` |
| テンプレートリファレンス（日本語） | `docs/ja/generated_template_reference.md` | `markdown` | `` | `3c368926fa8a` |
| テンプレートリファレンスJSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `a90f795c244e` |
| 診断コードリファレンス | `docs/diagnostics_reference.md` | `markdown` | `` | `e79784a913c5` |
| 診断コードリファレンス（日本語） | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `9e93c5d6da79` |
| 診断コードリファレンスJSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `3d88c8c48641` |
| CLI helpリファレンス | `docs/cli_help_reference.md` | `markdown` | `` | `ee12b2cf18b3` |
| CLI helpリファレンス（日本語） | `docs/ja/cli_help_reference.md` | `markdown` | `` | `05fe8549ca90` |
| CLI helpリファレンスJSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `7c6bef9af084` |
| リリースレポート | `docs/release_report.md` | `markdown` | `` | `9cbe6165e631` |
| リリースレポート（日本語） | `docs/ja/release_report.md` | `markdown` | `` | `8b74f480aae7` |
| リリースレポートJSON | `docs/release_report.json` | `json` | `sldl.release_report` | `918996ec262b` |
| リリースサマリーJSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `54dff8ee2d0d` |

## コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
