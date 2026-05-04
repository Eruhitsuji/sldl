# SLDL Reference Index

This page is the entry point for generated reference documents. In v1.0.11, the template reference, diagnostics reference, CLI help reference, and release report can be checked together.

- version: `1.0.11`
- references: `12`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| Template reference | `docs/generated_template_reference.md` | `markdown` | `` | `080403a0d191` |
| Template reference (Japanese) | `docs/ja/generated_template_reference.md` | `markdown` | `` | `e52da97e3adc` |
| Template reference JSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `20f87422d6bb` |
| Diagnostics reference | `docs/diagnostics_reference.md` | `markdown` | `` | `899245a2ee8b` |
| Diagnostics reference (Japanese) | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `45a07b8c2a2e` |
| Diagnostics reference JSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `91b73db1854e` |
| CLI help reference | `docs/cli_help_reference.md` | `markdown` | `` | `6de8e5750ad6` |
| CLI help reference (Japanese) | `docs/ja/cli_help_reference.md` | `markdown` | `` | `66ce143b86d9` |
| CLI help reference JSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `88ccdcd9eb02` |
| Release report | `docs/release_report.md` | `markdown` | `` | `c20ce5a293f7` |
| Release report (Japanese) | `docs/ja/release_report.md` | `markdown` | `` | `92631ea20ef2` |
| Release report JSON | `docs/release_report.json` | `json` | `sldl.release_report` | `ff61d0960338` |

## Commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
