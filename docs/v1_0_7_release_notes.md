# SLDL v1.0.7 Release Notes

v1.0.7 is a documentation and onboarding update for the v1.0 stable series. It keeps the v1.0.6 manifest-consistency hardening intact and makes the recommended user workflow easier to find and repeat.

## Highlights

- README Quick Start now begins with `template project` and continues through `project check`, `project build`, and `quality manifest`.
- `docs/getting_started.md` now presents a complete template-first flow.
- `docs/commands_reference.md` now documents the template inspection, generation, reference generation, and drift-check commands in one place.
- `docs/project_workflow.md` now explains how template metadata and SHA-256 hashes are preserved in build manifests.
- `examples/README.md` now includes a concrete template workflow using `template_schema_binding_project.json`.
- Release tests now verify that the main user-facing documents contain the v1.0.7 template-first workflow commands.

## Compatibility

No SLDL syntax or project JSON breaking change is introduced. Existing v1.0.6 projects remain compatible.

## Recommended verification

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
