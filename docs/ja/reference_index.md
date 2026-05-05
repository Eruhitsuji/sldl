# SLDL Reference Index（日本語）

生成済みリファレンス文書への入口です。v1.0.15では、template reference、diagnostics reference、CLI help reference、release report、CI向けrelease summaryをまとめて確認できます。

- version: `1.0.15`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| テンプレートリファレンス | `docs/generated_template_reference.md` | `markdown` | `` | `d3e3887000cc` |
| テンプレートリファレンス（日本語） | `docs/ja/generated_template_reference.md` | `markdown` | `` | `579ddf5e7e18` |
| テンプレートリファレンスJSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `328d7ab62f37` |
| 診断コードリファレンス | `docs/diagnostics_reference.md` | `markdown` | `` | `121476119bcd` |
| 診断コードリファレンス（日本語） | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `5b76d954a256` |
| 診断コードリファレンスJSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `25ea7f3004de` |
| CLI helpリファレンス | `docs/cli_help_reference.md` | `markdown` | `` | `b1c6d1e64151` |
| CLI helpリファレンス（日本語） | `docs/ja/cli_help_reference.md` | `markdown` | `` | `99bebc58c3a6` |
| CLI helpリファレンスJSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `fc86845eee89` |
| リリースレポート | `docs/release_report.md` | `markdown` | `` | `e1971ccf806e` |
| リリースレポート（日本語） | `docs/ja/release_report.md` | `markdown` | `` | `b46f7f52998b` |
| リリースレポートJSON | `docs/release_report.json` | `json` | `sldl.release_report` | `028198efd96a` |
| リリースサマリーJSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `2874938a09b4` |

## コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
