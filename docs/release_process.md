# Release process

## 1. Run tests

```bash
python3 -m pytest -q
```

## 2. Build the official examples

```bash
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

## 3. Run release check

```bash
python3 -S -m sldl_compiler.cli quality release   --targets examples/release_check.json   --manifest build/release_manifest.json
```

## 4. Inspect generated manifests

```bash
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
python3 -S -m sldl_compiler.cli quality manifest build/release_manifest.json
```

## 5. Confirm legacy cleanup

`examples/release_check.json` includes forbidden path/glob checks for old development samples and generated logs.

## 6. Final v1.0 step

For v1.0.0 and later releases, update version strings, release notes, snapshots, and release-check manifests before packaging.
