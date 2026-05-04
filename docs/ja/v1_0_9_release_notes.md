# SLDL v1.0.9 リリースノート

v1.0.9は、v1.0安定系列に診断コードリファレンスの自動生成を追加する更新です。v1.0.8のschema-template診断は維持しつつ、診断コード一覧を静的ファイルとして生成し、release checkで差分確認できるようにしました。

## 追加

- compiler sourceから既知の `E_*` / `W_*` コードを一覧する `diagnostics list` コマンド。
- MarkdownまたはJSONの診断リファレンスを生成する `diagnostics docs` コマンド。
- 英語版の `docs/diagnostics_reference.md`。
- 日本語版の `docs/ja/diagnostics_reference.md`。
- 機械可読版の `docs/diagnostics_reference.json`。
- `sldl.diagnostics_reference` config validation。

## release check

release gateでは、診断リファレンスがcompiler sourceと同期しているか確認します。

```bash
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --check docs/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format markdown --language ja --check docs/ja/diagnostics_reference.md
python3 -S -m sldl_compiler.cli diagnostics docs --format json --check docs/diagnostics_reference.json
```

## 互換性

v1.xの文書・project・schema・template・exportの基本動作はv1.0.8と互換です。このリリースは主に検査・ドキュメント生成コマンドを追加するものなので、既存の妥当なprojectとtemplateは引き続き通る想定です。
