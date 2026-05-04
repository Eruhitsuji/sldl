# Template Manifest移行ガイド

## 正式なファイル

v1.0.4以降、同梱テンプレートの正式なmanifestは次です。

```text
templates/template_manifest.json
```

`templates/manifest.json` は古いワークフローとの互換用コピーとして残します。

## 推奨更新手順

1. `templates/template_manifest.json` を編集します。
2. 古いツールが必要な場合に備えて、同じtemplate listを `templates/manifest.json` に反映します。
3. `template_manifest.json` の `manifest_role` は `canonical` にします。
4. `manifest.json` の `manifest_role` は `legacy_compatibility`、`canonical_manifest` は `template_manifest.json` にします。
5. release gateを実行します。

```bash
python3 -S -m sldl_compiler.cli config check templates/template_manifest.json
python3 -S -m sldl_compiler.cli config check templates/manifest.json
python3 -S -m sldl_compiler.cli quality release --targets examples/release_check.json --manifest build/release_manifest.json
```

## build manifestでの追跡性

`template project` で生成したprojectは正式manifestへのpathを記録します。`quality manifest` はこの情報を検査し、生成物がどのtemplate/schema bindingから作られたかを追跡できるようにします。
