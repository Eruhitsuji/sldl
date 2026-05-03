# SLDL v1.0.3 リリースノート

v1.0.3は、テンプレートmanifestの整合性とテンプレート起点のproject生成履歴を強化する安定版メンテナンスリリースです。

## 概要

- v1.0系の公開文法と、v1.0.1/v1.0.2のtemplate-schema bindingの挙動を維持します。
- `template explain` にJSON形式とMarkdown形式の出力を追加しました。
- `templates/template_manifest.json` と `templates/manifest.json` が同じテンプレート集合を宣言しているか検査します。
- templateディレクトリにある未登録の `*.sldl` ファイルを警告します。
- 生成project JSONと `sldl_build_manifest.json` にテンプレート情報を記録します。

## 新しいコマンド形式

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en --format text
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template explain research_report_en --format json
```

従来の `--json` は `--format json` の互換エイリアスとして残しています。

## build manifestへのtemplate情報記録

project documentに `template`、`template_source`、`template_manifest` が含まれている場合、`project build` はbuild manifest内のdocument entryに `template` オブジェクトを記録します。これにより、生成された成果物がどのテンプレート由来なのかを後から確認しやすくなります。

## 互換性

v1.0.3は、v1.0.0、v1.0.1、v1.0.2の文書とproject fileとの互換性を保つことを意図しています。新しい検査はtemplate manifestに対して厳密ですが、SLDL文法を変更するものではなく、配布物のずれを検出するためのものです。
