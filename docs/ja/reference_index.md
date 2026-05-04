# SLDL Reference Index（日本語）

生成済みリファレンス文書への入口です。v1.0.10では、template reference、diagnostics reference、CLI help referenceをまとめて確認できます。

- version: `1.0.10`
- references: `9`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| テンプレートリファレンス | `docs/generated_template_reference.md` | `markdown` | `` | `deceb9b0a027` |
| テンプレートリファレンス（日本語） | `docs/ja/generated_template_reference.md` | `markdown` | `` | `c09e1b39e25d` |
| テンプレートリファレンスJSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `721bea080f99` |
| 診断コードリファレンス | `docs/diagnostics_reference.md` | `markdown` | `` | `fa384a30e76f` |
| 診断コードリファレンス（日本語） | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `cd997e5b04c2` |
| 診断コードリファレンスJSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `666ee32b5d81` |
| CLI helpリファレンス | `docs/cli_help_reference.md` | `markdown` | `` | `d9b9cc685eee` |
| CLI helpリファレンス（日本語） | `docs/ja/cli_help_reference.md` | `markdown` | `` | `66e25252867d` |
| CLI helpリファレンスJSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `ea0e3c2e34bd` |

## コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
