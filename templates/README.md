# SLDL Templates

v0.4.1から、テンプレート本文は `sldl_compiler/templates.py` に直接書かず、このディレクトリで管理します。

## 独自テンプレートディレクトリ

```bash
python -m sldl_compiler.cli template list --template-dir my_templates
python -m sldl_compiler.cli template new my_paper --template-dir my_templates -o output.sldl
```

## スキーマからテンプレートを指定

```bash
python -m sldl_compiler.cli template new --schema examples/custom_article_schema_with_template.json -o examples/from_schema.sldl
```
