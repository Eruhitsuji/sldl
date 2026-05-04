# SLDL v1.0.4 リリースノート

v1.0.4は、template manifest方針、template reference生成、build manifestでの追跡性を強化する小規模保守リリースです。

## 主な変更

- `templates/template_manifest.json` を正式なtemplate manifestとして明確化しました。
- `templates/manifest.json` は互換用コピーとして残し、`manifest_role: "legacy_compatibility"` を記録します。
- `template docs --format markdown|json` を追加し、manifestからtemplate referenceを生成できるようにしました。
- `template project` が生成するproject fileに `template_manifest_role` を記録します。
- `project build` が生成するbuild manifestに、template名、source、manifest、manifest role、宣言document typeを保持します。
- `quality manifest` はtemplate情報を検査し、互換用manifestを正式manifestとして使っている場合は失敗します。
- `docs/project_workflow.md` と `docs/commands_reference.md` をv1.0.4のtemplate workflowに同期しました。

## 互換性

v1.0.1からv1.0.3までのtemplate workflowは引き続き利用できます。今後の編集対象は `templates/template_manifest.json` を優先し、`templates/manifest.json` は互換用コピーとして更新します。
