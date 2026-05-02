# GitHub repository guide

This file is a GitHub-facing Markdown guide intended to be stored statically under `docs/`.

## Recommended public entry points

- `README.md`: short project overview, quick start, and links.
- `docs/index.md`: documentation home.
- `docs/getting_started.md`: first command sequence.
- `docs/sldl_language_reference.md`: language reference.
- `docs/config_reference.md`: JSON configuration reference.
- `docs/commands_reference.md`: CLI reference.
- `examples/README.md`: sample-file map.

## Language policy

English is the primary documentation language. Japanese companion documents are stored under `docs/ja/` with the same conceptual structure.

## Sample policy

Official examples should be source files and JSON configurations. Generated outputs should be reproducible through `project build` and should not be treated as hand-maintained source documentation.

## v1.0 public release rule

The v1.0 release should keep the cleaned v1.0.0 structure: no unpublished historical v0 sample tree, no generated logs as examples, and no per-version development notes in the public documentation path.
