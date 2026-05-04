# SLDL v1.0.6 リリースノート

v1.0.6は、v1.0.x系の保守・安定化リリースです。v1.0.0の公開文法とproject workflowの互換性を維持しながら、template由来projectの追跡性と検査を強化しました。

## 主な変更点

- build manifest検査で、template関連ファイルすべてのSHA-256 metadataを必須化しました。
- build manifest内のtemplate metadataが、参照先の正式template manifest entryと一致するか検査します。
- 生成されるtemplate reference JSONに `source_manifest` と `source_manifest_sha256` を記録します。
- `config check docs/generated_template_reference.json` で、生成referenceと正式template manifest metadataの一致を検査します。
- release checkに、より厳密なtemplate reference / build manifest整合性検査を含めました。

## 互換性

v1.0.6ではSLDL文法の変更はありません。既存のv1.0.x文書とprojectは引き続き有効です。templateから生成したprojectについては、最新のtemplate hash metadataを含めるために再buildすることを推奨します。

## 推奨確認コマンド

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```
