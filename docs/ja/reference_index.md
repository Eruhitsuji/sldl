# SLDL Reference Index（日本語）

生成済みリファレンス文書への入口です。v1.0.11では、template reference、diagnostics reference、CLI help reference、release reportをまとめて確認できます。

- version: `1.0.11`
- references: `12`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| テンプレートリファレンス | `docs/generated_template_reference.md` | `markdown` | `` | `080403a0d191` |
| テンプレートリファレンス（日本語） | `docs/ja/generated_template_reference.md` | `markdown` | `` | `e52da97e3adc` |
| テンプレートリファレンスJSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `20f87422d6bb` |
| 診断コードリファレンス | `docs/diagnostics_reference.md` | `markdown` | `` | `899245a2ee8b` |
| 診断コードリファレンス（日本語） | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `45a07b8c2a2e` |
| 診断コードリファレンスJSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `91b73db1854e` |
| CLI helpリファレンス | `docs/cli_help_reference.md` | `markdown` | `` | `6de8e5750ad6` |
| CLI helpリファレンス（日本語） | `docs/ja/cli_help_reference.md` | `markdown` | `` | `66ce143b86d9` |
| CLI helpリファレンスJSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `88ccdcd9eb02` |
| リリースレポート | `docs/release_report.md` | `markdown` | `` | `c20ce5a293f7` |
| リリースレポート（日本語） | `docs/ja/release_report.md` | `markdown` | `` | `92631ea20ef2` |
| リリースレポートJSON | `docs/release_report.json` | `json` | `sldl.release_report` | `ff61d0960338` |

## コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
