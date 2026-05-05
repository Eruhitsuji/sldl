# SLDL Reference Index

This page is the entry point for generated reference documents. In v1.0.12, the template reference, diagnostics reference, CLI help reference, release report, and CI release summary can be checked together.

- version: `1.0.12`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| Template reference | `docs/generated_template_reference.md` | `markdown` | `` | `c66a76521208` |
| Template reference (Japanese) | `docs/ja/generated_template_reference.md` | `markdown` | `` | `6ab864ec6516` |
| Template reference JSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `7d740dc93eb6` |
| Diagnostics reference | `docs/diagnostics_reference.md` | `markdown` | `` | `fe86d9b2f730` |
| Diagnostics reference (Japanese) | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `0d4bf24db603` |
| Diagnostics reference JSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `feeae2533d3d` |
| CLI help reference | `docs/cli_help_reference.md` | `markdown` | `` | `85ec807be8dd` |
| CLI help reference (Japanese) | `docs/ja/cli_help_reference.md` | `markdown` | `` | `76860290ee9c` |
| CLI help reference JSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `d0ea6e010ed5` |
| Release report | `docs/release_report.md` | `markdown` | `` | `abb1aa402e04` |
| Release report (Japanese) | `docs/ja/release_report.md` | `markdown` | `` | `48761f4002ce` |
| Release report JSON | `docs/release_report.json` | `json` | `sldl.release_report` | `7cac88f3712f` |
| Release summary JSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `305c0b8097ec` |

## Commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
