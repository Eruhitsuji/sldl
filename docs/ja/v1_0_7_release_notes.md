# SLDL v1.0.7 リリースノート

v1.0.7は、v1.0安定系列のドキュメント・導線改善版です。v1.0.6で強化したmanifest整合性検査は維持しつつ、推奨ワークフローをより分かりやすく整理しました。

## 主な変更

- READMEのQuick Startを `template project` → `project check` → `project build` → `quality manifest` 中心に再整理しました。
- `docs/ja/getting_started.md` にtemplate-first workflowを詳しく記述しました。
- `docs/ja/commands_reference.md` にtemplate確認、生成、reference生成、drift check系コマンドを整理しました。
- `docs/ja/project_workflow.md` にbuild manifestへ記録されるtemplate metadataとSHA-256の説明を追加しました。
- `examples/README.md` に `template_schema_binding_project.json` を使った具体例を追加しました。
- 主要ドキュメントにv1.0.7のtemplate-first workflowが含まれていることをテストで確認するようにしました。

## 互換性

SLDL文法やproject JSONに破壊的変更はありません。既存のv1.0.6 projectは引き続き利用できます。

## 推奨確認コマンド

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
