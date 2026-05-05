# SLDL Reference Index（日本語）

生成済みリファレンス文書への入口です。v1.0.14では、template reference、diagnostics reference、CLI help reference、release report、CI向けrelease summaryをまとめて確認できます。

- version: `1.0.14`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| テンプレートリファレンス | `docs/generated_template_reference.md` | `markdown` | `` | `c7b12d276600` |
| テンプレートリファレンス（日本語） | `docs/ja/generated_template_reference.md` | `markdown` | `` | `5e18dc4e64dc` |
| テンプレートリファレンスJSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `f86003b124ec` |
| 診断コードリファレンス | `docs/diagnostics_reference.md` | `markdown` | `` | `ad1f0804d54b` |
| 診断コードリファレンス（日本語） | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `f992d2b422e9` |
| 診断コードリファレンスJSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `00250a210173` |
| CLI helpリファレンス | `docs/cli_help_reference.md` | `markdown` | `` | `52731560e270` |
| CLI helpリファレンス（日本語） | `docs/ja/cli_help_reference.md` | `markdown` | `` | `916f4c481a74` |
| CLI helpリファレンスJSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `2e22e7d5c6e1` |
| リリースレポート | `docs/release_report.md` | `markdown` | `` | `4c4fd8eb362c` |
| リリースレポート（日本語） | `docs/ja/release_report.md` | `markdown` | `` | `3c64919b0cfd` |
| リリースレポートJSON | `docs/release_report.json` | `json` | `sldl.release_report` | `dd54335c2211` |
| リリースサマリーJSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `602d353e4e57` |

## コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
