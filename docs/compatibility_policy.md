# Compatibility policy

v1.0.0 defines the first public compatibility baseline for SLDL syntax, JSON configuration, CLI commands, official examples, and release checks.

## v1.x compatibility policy

The earlier v0 series was an unpublished development sequence. Its sample names, generated outputs, and release-check targets are not treated as public compatibility contracts.

## Policy for v1.x

The v1.x compatibility surface should be limited to:

- core SLDL syntax documented in `docs/sldl_language_reference.md`
- documented CLI commands in `docs/commands_reference.md`
- documented config types in `docs/config_reference.md`
- official examples in `examples/`
- documented template names in `templates/manifest.json`

## Removed from compatibility scope

- old version-numbered examples
- old generated build outputs
- old release manifests
- old per-version development notes
- tests whose only role was preserving unpublished development-stage behavior
