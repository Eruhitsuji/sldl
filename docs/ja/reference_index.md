# SLDL Reference Index（日本語）

生成済みリファレンス文書への入口です。v1.0.12では、template reference、diagnostics reference、CLI help reference、release report、CI向けrelease summaryをまとめて確認できます。

- version: `1.0.12`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| テンプレートリファレンス | `docs/generated_template_reference.md` | `markdown` | `` | `c66a76521208` |
| テンプレートリファレンス（日本語） | `docs/ja/generated_template_reference.md` | `markdown` | `` | `6ab864ec6516` |
| テンプレートリファレンスJSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `7d740dc93eb6` |
| 診断コードリファレンス | `docs/diagnostics_reference.md` | `markdown` | `` | `fe86d9b2f730` |
| 診断コードリファレンス（日本語） | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `0d4bf24db603` |
| 診断コードリファレンスJSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `feeae2533d3d` |
| CLI helpリファレンス | `docs/cli_help_reference.md` | `markdown` | `` | `85ec807be8dd` |
| CLI helpリファレンス（日本語） | `docs/ja/cli_help_reference.md` | `markdown` | `` | `76860290ee9c` |
| CLI helpリファレンスJSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `d0ea6e010ed5` |
| リリースレポート | `docs/release_report.md` | `markdown` | `` | `abb1aa402e04` |
| リリースレポート（日本語） | `docs/ja/release_report.md` | `markdown` | `` | `48761f4002ce` |
| リリースレポートJSON | `docs/release_report.json` | `json` | `sldl.release_report` | `7cac88f3712f` |
| リリースサマリーJSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `305c0b8097ec` |

## コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
