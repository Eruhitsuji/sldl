# Commands reference

## 基本コマンド

```bash
python3 -S -m sldl_compiler.cli check examples/official_project_overview_ja.sldl --schema examples/sldl_schema.json
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
```

英語版の完全な一覧は `docs/commands_reference.md` を参照してください。
