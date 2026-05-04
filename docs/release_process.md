# Release process

## 1. Run tests

```bash
python3 -m pytest -q
```

## 2. Build the official examples

```bash
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## 3. Check generated reference drift

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --check docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json --check docs/diagnostics_reference.json
```

## 4. Run release check

```bash
python3 -S -m sldl_compiler.cli quality release   --targets examples/release_check.json   --manifest build/release_manifest.json
```

## 5. Inspect generated manifests

```bash
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
python3 -S -m sldl_compiler.cli quality manifest build/release_manifest.json
```

## 6. Confirm legacy cleanup

`examples/release_check.json` includes forbidden path/glob checks for old development samples and generated logs.

## 7. Final v1.x step

For v1.0.0 and later releases, update version strings, release notes, generated references, snapshots, and release-check manifests before packaging.
