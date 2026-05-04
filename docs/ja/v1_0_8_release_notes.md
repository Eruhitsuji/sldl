# SLDL v1.0.8 リリースノート

v1.0.8は、template-firstなv1.0系ワークフローの診断強化版です。v1.0.7のドキュメント導線を維持しつつ、schema/template bindingの失敗原因をより分かりやすくし、release checkで確認できるようにしました。

## 主な変更点

- schema file missing と schema `config_type` mismatch に対する明示的な診断を追加しました。
- template manifest内のtemplate file missing、bound schema missing、bound config-type mismatchの診断を強化しました。
- document_type mismatchの表示に、期待される型、実際のdocument type、schema path、修正のヒントを含めました。
- manifestに紐づいたschemaを `--allow-schema-override` で上書きした場合に、明示的な警告を出すようにしました。
- schema-template failure modeの代表例をnegative exampleとして追加し、release checkでexpect_failure検査できるようにしました。

## 互換性

v1.xの公開コマンド面はv1.0.7と互換です。既存の妥当なprojectとtemplateは引き続き通る想定です。一方で、存在しないschema/template fileや誤ったconfig_typeを参照している設定は、tracebackや曖昧な警告ではなく、より早い段階で明確に失敗する場合があります。

## 推奨チェック

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
