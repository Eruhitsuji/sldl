# SLDL Reference Index

This page is the entry point for generated reference documents. In v1.0.10, the template reference, diagnostics reference, and CLI help reference can be checked together.

- version: `1.0.10`
- references: `9`

| Title | Path | Kind | Config type | SHA-256 |
|---|---|---|---|---|
| Template reference | `docs/generated_template_reference.md` | `markdown` | `` | `deceb9b0a027` |
| Template reference (Japanese) | `docs/ja/generated_template_reference.md` | `markdown` | `` | `c09e1b39e25d` |
| Template reference JSON | `docs/generated_template_reference.json` | `json` | `sldl.template_reference` | `721bea080f99` |
| Diagnostics reference | `docs/diagnostics_reference.md` | `markdown` | `` | `fa384a30e76f` |
| Diagnostics reference (Japanese) | `docs/ja/diagnostics_reference.md` | `markdown` | `` | `cd997e5b04c2` |
| Diagnostics reference JSON | `docs/diagnostics_reference.json` | `json` | `sldl.diagnostics_reference` | `666ee32b5d81` |
| CLI help reference | `docs/cli_help_reference.md` | `markdown` | `` | `d9b9cc685eee` |
| CLI help reference (Japanese) | `docs/ja/cli_help_reference.md` | `markdown` | `` | `66e25252867d` |
| CLI help reference JSON | `docs/cli_help_reference.json` | `json` | `sldl.cli_help_reference` | `ea0e3c2e34bd` |

## Commands

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md
python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md
```
