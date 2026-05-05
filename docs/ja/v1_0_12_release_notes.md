# v1.0.12 リリースノート

SLDL v1.0.12は、v1.0系のCI利用を強化する保守リリースです。v1.0.11の生成リリースレポートの流れを維持しつつ、機械可読なrelease summaryを追加しました。

## 主な更新

- `quality release --summary-json <path>` を追加し、CI向けの `sldl.release_summary` を出力できるようにしました。
- 警告を失敗として扱う明示的なrelease gateとして `quality release --fail-on-warning` を追加しました。
- release checkのcommandに `category` / `release_category` と `severity` の分類メタデータを記述できるようにしました。
- release manifestと生成release reportに、警告数、release-category別集計、severity別集計を追加しました。
- `docs/release_summary.json` を生成リファレンス索引とrelease gateの対象に追加しました。

## 互換性

SLDL本文の構文は変更していません。既存のv1.0.x文書、schema、template、project JSONはそのまま利用できます。
