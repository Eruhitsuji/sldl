# SLDLドキュメント

SLDL（Structured Logical Document Language）は、研究報告書・技術文書・仕様書を、文書本体、論理的な根拠関係、スキーマ、出力設定、リリース品質検査まで含めて扱うための文書記述形式です。

v1.0.2では、英語版ドキュメントを主参照とし、日本語版ドキュメントを補助的な利用ガイドとして提供します。また、テンプレートとschemaの紐づけ検査、template explain、document type不整合診断を追加しています。

## 最初に読むもの

1. `docs/getting_started.md` または `docs/ja/getting_started.md`
2. `examples/project_official_examples.json`
3. `docs/sldl_language_reference.md`
4. `docs/config_reference.md`
5. `docs/template_schema_binding.md` または `docs/ja/template_schema_binding.md`
6. `docs/release_process.md`

## 公式サンプル

- `official_project_overview_en.sldl`: プロジェクト、文法、JSON、資料作成フローを説明する英語サンプル。
- `official_project_overview_ja.sldl`: 上記の日本語補助サンプル。
- `research_report_en.sldl`: 小さな英語研究報告書サンプル。
- `research_report_ja.sldl`: 小さな日本語研究報告書サンプル。
- `project_official_examples.json`: 公式サンプルをまとめてビルドするproject設定。

## ドキュメントマップ

- `template_schema_binding.md`: v1.0.2のtemplateとschemaの紐づけ、および診断。
- `v1_0_2_release_notes.md`: v1.0.2リリースノート。
