# SLDLドキュメント

SLDL（Structured Logical Document Language）は、研究報告書・技術文書・仕様書を、文書本体、論理的な根拠関係、スキーマ、出力設定、リリース品質検査まで含めて扱うための文書記述形式です。

v1.0.12では、英語版ドキュメントを主参照とし、日本語版ドキュメントを補助的な利用ガイドとして提供します。template-first workflowとschema-template診断を維持しつつ、診断コード、reference index、CLI help referenceを自動生成・drift checkできるようにしています。

## 最初に読むもの

1. `docs/getting_started.md` または `docs/ja/getting_started.md`
2. `examples/project_official_examples.json`
3. `docs/sldl_language_reference.md`
4. `docs/config_reference.md`
5. `docs/template_schema_binding.md` または `docs/ja/template_schema_binding.md`
6. `docs/diagnostics_reference.md` または `docs/ja/diagnostics_reference.md`
7. `docs/release_process.md`

## 公式サンプル

- `official_project_overview_en.sldl`: プロジェクト、文法、JSON、資料作成フローを説明する英語サンプル。
- `official_project_overview_ja.sldl`: 上記の日本語補助サンプル。
- `research_report_en.sldl`: 小さな英語研究報告書サンプル。
- `research_report_ja.sldl`: 小さな日本語研究報告書サンプル。
- `project_official_examples.json`: 公式サンプルをまとめてビルドするproject設定。

## ドキュメントマップ

- `template_schema_binding.md`: templateとschemaの紐づけ、manifest互換性、および診断。
- `template_manifest_migration.md`: v1.0.4の正式manifest移行ガイド。
- `generated_template_reference.md`: 生成されたtemplate reference。
- `generated_template_reference.json`: 生成された機械可読template reference。
- `diagnostics_reference.md`: 生成された診断コードリファレンス。
- `diagnostics_reference.json`: 生成された機械可読診断コードリファレンス。
- `v1_0_5_release_notes.md`: v1.0.5リリースノート。
- `v1_0_10_release_notes.md`: v1.0.10リリースノート。
- `v1_0_11_release_notes.md`: v1.0.11リリースノート。
- `v1_0_12_release_notes.md`: v1.0.12リリースノート。
- `v1_0_9_release_notes.md`: v1.0.9リリースノート。
- `v1_0_8_release_notes.md`: v1.0.8リリースノート。
- `v1_0_7_release_notes.md`: v1.0.7リリースノート。
- `v1_0_6_release_notes.md`: v1.0.6リリースノート。
- `v1_0_4_release_notes.md`: v1.0.4リリースノート。
- `v1_0_3_release_notes.md`: v1.0.3リリースノート。
- `v1_0_2_release_notes.md`: v1.0.2リリースノート。

- `reference_index.md`: 生成済みリファレンス索引。
- `cli_help_reference.md`: 生成済みCLI helpリファレンス。
