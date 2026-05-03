# SLDL v1.0.1 リリースノート

SLDL v1.0.1は、templateとschemaの紐づけを中心とした保守リリースです。v1.0.0との互換性を保ちつつ、付属テンプレートの検査を厳密化しています。

## 追加

- 付属テンプレートの正規manifestとして `templates/template_manifest.json` を追加。
- テンプレートを紐づけられたschemaで検査する `template check <name>` を追加。
- `template new` と `template project` で、schema付きテンプレートの生成時検査を追加。
- manifest項目として `schema`、`default_export_config`、`default_latex_build_config`、`strict_schema` を追加。
- 英語・日本語の研究報告書テンプレートとプロジェクト概要テンプレートをschema付きで追加。
- release checkに、template manifest検査とschema付きテンプレート生成検査を追加。

## 互換性

v1.0.0の文書とproject JSONを壊さない更新です。従来の `templates/manifest.json` も互換用エイリアスとして残していますが、v1.0.1以降の正規名は `templates/template_manifest.json` です。
