# Project workflow

標準的な出力生成は `project build` で行います。

公式projectは `examples/project_official_examples.json` です。

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

生成されたmanifestは次で検査できます。

```bash
python3 -S -m sldl_compiler.cli quality manifest build/official_examples/sldl_build_manifest.json
```
