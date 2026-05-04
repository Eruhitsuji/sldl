# SLDL v1.0.10 リリースノート

v1.0.10は、v1.0安定系列に生成リファレンス索引を追加する更新です。v1.0.9の診断コードリファレンス生成を維持しつつ、template、diagnostics、CLI helpの各リファレンスへ移動しやすい入口を追加しました。

## 主な追加点

- `reference index` を追加し、生成済みリファレンス文書のMarkdown/JSON索引を生成できるようにしました。
- `reference cli-help` を追加し、実装済みCLIの `--help` 出力を静的Markdown/JSON文書として保存できるようにしました。
- `docs/reference_index.md`、`docs/reference_index.json`、`docs/cli_help_reference.md`、`docs/cli_help_reference.json` を追加しました。
- `docs/ja/` 以下に日本語版の補助ページを追加しました。
- `sldl.reference_index` と `sldl.cli_help_reference` のconfig validationを追加しました。
- release checkにreference indexとCLI help referenceのdrift checkを追加しました。

## 推奨確認

```bash
python3 -m pytest -q
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json
```

## 新規コマンド

```bash
python3 -S -m sldl_compiler.cli reference index --format markdown
python3 -S -m sldl_compiler.cli reference index --format json
python3 -S -m sldl_compiler.cli reference cli-help --format markdown
python3 -S -m sldl_compiler.cli reference cli-help --format json
```
