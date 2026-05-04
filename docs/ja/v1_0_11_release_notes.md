# SLDL v1.0.11 リリースノート

v1.0.11では、v1.0安定系列に生成リリースレポートを追加しました。`quality release` が生成するrelease manifestを、確認しやすいMarkdownと機械処理しやすいJSONとして出力できます。

## 主な変更

- `sldl.release_manifest` からMarkdown/JSONを生成する `quality report` を追加しました。
- `docs/release_report.md`、`docs/ja/release_report.md`、`docs/release_report.json` を追加しました。
- `sldl.release_report` のconfig validationを追加しました。
- `examples/release_check.json` にrelease reportのdrift checkを追加しました。
- 生成リファレンス索引からrelease reportへ到達できるようにしました。
- レポート自身の検査コマンドは、循環的な差分を避けるためrelease report集計から除外します。

## 代表的なコマンド

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json

python3 -S -m sldl_compiler.cli quality report \
  build/release_manifest.json \
  --format markdown \
  --check docs/release_report.md

python3 -S -m sldl_compiler.cli quality report \
  build/release_manifest.json \
  --format json \
  --check docs/release_report.json
```
