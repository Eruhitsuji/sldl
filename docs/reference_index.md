# SLDL Reference Index

This page is the entry point for generated reference documents. In v1.0.16, the template reference, diagnostics reference, CLI help reference, release report, and CI release summary can be checked together.

- version: `1.0.16`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| Template reference | `docs/generated_template_reference.md` | `markdown` | `` | `bae1f2cbed41` |
| Template reference (Japanese) | `docs/ja/generated_template_reference.md` | `markdown` | `` | `3c368926fa8a` |
| Template reference JSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `a90f795c244e` |
| Diagnostics reference | `docs/diagnostics_reference.md` | `markdown` | `` | `e79784a913c5` |
| Diagnostics reference (Japanese) | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `9e93c5d6da79` |
| Diagnostics reference JSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `3d88c8c48641` |
| CLI help reference | `docs/cli_help_reference.md` | `markdown` | `` | `ee12b2cf18b3` |
| CLI help reference (Japanese) | `docs/ja/cli_help_reference.md` | `markdown` | `` | `05fe8549ca90` |
| CLI help reference JSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `7c6bef9af084` |
| Release report | `docs/release_report.md` | `markdown` | `` | `9cbe6165e631` |
| Release report (Japanese) | `docs/ja/release_report.md` | `markdown` | `` | `8b74f480aae7` |
| Release report JSON | `docs/release_report.json` | `json` | `sldl.release_report` | `918996ec262b` |
| Release summary JSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `54dff8ee2d0d` |

## Commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
