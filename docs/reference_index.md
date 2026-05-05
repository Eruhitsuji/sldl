# SLDL Reference Index

This page is the entry point for generated reference documents. In v1.0.13, the template reference, diagnostics reference, CLI help reference, release report, and CI release summary can be checked together.

- version: `1.0.13`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| Template reference | `docs/generated_template_reference.md` | `markdown` | `` | `16ad4b281fa9` |
| Template reference (Japanese) | `docs/ja/generated_template_reference.md` | `markdown` | `` | `dfcf7da2689f` |
| Template reference JSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `00c509b434b4` |
| Diagnostics reference | `docs/diagnostics_reference.md` | `markdown` | `` | `58c8617fcf45` |
| Diagnostics reference (Japanese) | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `0a74b9b162b0` |
| Diagnostics reference JSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `2597aa214ba6` |
| CLI help reference | `docs/cli_help_reference.md` | `markdown` | `` | `9fbcbe17832a` |
| CLI help reference (Japanese) | `docs/ja/cli_help_reference.md` | `markdown` | `` | `27c1eb4cd681` |
| CLI help reference JSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `d82d5b3994eb` |
| Release report | `docs/release_report.md` | `markdown` | `` | `396be06135fa` |
| Release report (Japanese) | `docs/ja/release_report.md` | `markdown` | `` | `6d2806fdc5ae` |
| Release report JSON | `docs/release_report.json` | `json` | `sldl.release_report` | `713ec91db088` |
| Release summary JSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `67458f5206fd` |

## Commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
