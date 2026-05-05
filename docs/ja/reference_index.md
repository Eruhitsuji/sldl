# SLDL Reference Index（日本語）

生成済みリファレンス文書への入口です。v1.0.13では、template reference、diagnostics reference、CLI help reference、release report、CI向けrelease summaryをまとめて確認できます。

- version: `1.0.13`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| テンプレートリファレンス | `docs/generated_template_reference.md` | `markdown` | `` | `16ad4b281fa9` |
| テンプレートリファレンス（日本語） | `docs/ja/generated_template_reference.md` | `markdown` | `` | `dfcf7da2689f` |
| テンプレートリファレンスJSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `00c509b434b4` |
| 診断コードリファレンス | `docs/diagnostics_reference.md` | `markdown` | `` | `58c8617fcf45` |
| 診断コードリファレンス（日本語） | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `0a74b9b162b0` |
| 診断コードリファレンスJSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `2597aa214ba6` |
| CLI helpリファレンス | `docs/cli_help_reference.md` | `markdown` | `` | `9fbcbe17832a` |
| CLI helpリファレンス（日本語） | `docs/ja/cli_help_reference.md` | `markdown` | `` | `27c1eb4cd681` |
| CLI helpリファレンスJSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `d82d5b3994eb` |
| リリースレポート | `docs/release_report.md` | `markdown` | `` | `396be06135fa` |
| リリースレポート（日本語） | `docs/ja/release_report.md` | `markdown` | `` | `6d2806fdc5ae` |
| リリースレポートJSON | `docs/release_report.json` | `json` | `sldl.release_report` | `713ec91db088` |
| リリースサマリーJSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `67458f5206fd` |

## コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
