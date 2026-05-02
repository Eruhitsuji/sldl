# Release process

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
python3 -S -m sldl_compiler.cli quality release   --targets examples/release_check.json   --manifest build/release_manifest.json
```

v1.0.0では、このv1.0.0の二言語ドキュメント・公式サンプル構成を土台にして、バージョン表記と正式版表現を更新するのが自然です。
