# SLDL v1.0.5 リリースノート

v1.0.5は、生成されるtemplate referenceと静的docsの一致検査、およびbuild manifestでのtemplate追跡性を強化する小規模な安定版保守リリースです。

## 主な変更

- `template docs --check <path>` を追加し、生成結果と既存の静的ファイルが一致しない場合に失敗できるようにしました。
- `template docs --language en|ja` を追加し、英語版と日本語版のtemplate referenceを同じコマンドで生成できるようにしました。
- 機械可読なtemplate referenceとして `docs/generated_template_reference.json` を追加しました。
- templateから生成されたprojectのbuild manifestに、template本体、schema、export config、LaTeX build configのSHA-256情報を記録するようにしました。
- `quality manifest` で、記録されたtemplate関連ハッシュが参照先ファイルと一致するか検査するようにしました。
- release checkで英語版、日本語版、JSON版のgenerated template referenceを検査するようにしました。

## 推奨確認コマンド

```bash
python3 -m pytest -q

python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format markdown --language ja --check docs/ja/generated_template_reference.md
python3 -S -m sldl_compiler.cli template docs --format json --check docs/generated_template_reference.json

python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

## 互換性

v1.0.5では、v1.0.0の公開言語仕様とproject workflowの互換性を維持しています。既存のv1.0.4 template projectは引き続き有効で、新しく生成されるtemplate projectには追加の追跡メタデータが含まれます。
