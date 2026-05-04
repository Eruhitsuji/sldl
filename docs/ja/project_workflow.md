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


## v1.0.5のtemplate情報

`template project` で生成したprojectには、`template`、`template_source`、`template_manifest`、`template_manifest_role` が記録されます。`project build` では、これらが `sldl_build_manifest.json` に引き継がれます。release checkは、template由来の文書が正式な `templates/template_manifest.json` に追跡できるかを検査します。
