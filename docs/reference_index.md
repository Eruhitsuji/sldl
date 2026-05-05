# SLDL Reference Index

This page is the entry point for generated reference documents. In v1.0.14, the template reference, diagnostics reference, CLI help reference, release report, and CI release summary can be checked together.

- version: `1.0.14`
- references: `13`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| Template reference | `docs/generated_template_reference.md` | `markdown` | `` | `c7b12d276600` |
| Template reference (Japanese) | `docs/ja/generated_template_reference.md` | `markdown` | `` | `5e18dc4e64dc` |
| Template reference JSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `f86003b124ec` |
| Diagnostics reference | `docs/diagnostics_reference.md` | `markdown` | `` | `ad1f0804d54b` |
| Diagnostics reference (Japanese) | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `f992d2b422e9` |
| Diagnostics reference JSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `00250a210173` |
| CLI help reference | `docs/cli_help_reference.md` | `markdown` | `` | `52731560e270` |
| CLI help reference (Japanese) | `docs/ja/cli_help_reference.md` | `markdown` | `` | `916f4c481a74` |
| CLI help reference JSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `2e22e7d5c6e1` |
| Release report | `docs/release_report.md` | `markdown` | `` | `4c4fd8eb362c` |
| Release report (Japanese) | `docs/ja/release_report.md` | `markdown` | `` | `3c64919b0cfd` |
| Release report JSON | `docs/release_report.json` | `json` | `sldl.release_report` | `dd54335c2211` |
| Release summary JSON | `docs/release_summary.json` | `json` | `sldl.release_summary` | `602d353e4e57` |

## Commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
