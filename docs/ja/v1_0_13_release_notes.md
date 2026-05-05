# SLDL v1.0.13 リリースノート

v1.0.13はCI workflow連携版です。v1.0.12で追加したrelease summary基盤を維持しつつ、GitHub Actions用workflowと二言語CIドキュメントを追加します。

## 主な変更

- Python 3.10、3.11、3.12でpytestを実行する `.github/workflows/test.yml` を追加。
- `quality release` gateを実行する `.github/workflows/release-check.yml` を追加。
- `docs/ci_workflow.md` と `docs/ja/ci_workflow.md` を追加。
- CI workflowファイルとCIドキュメントをrelease check対象に追加。
- `--fail-on-warning` を使う厳密なrelease summary smoke commandを追加。
- README、documentation index、release process、release metadataをv1.0.13向けに更新。

## 推奨CIコマンド

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
```

生成される `docs/release_summary.json` は、CI artifactやstatus summaryで利用するための機械可読結果です。
