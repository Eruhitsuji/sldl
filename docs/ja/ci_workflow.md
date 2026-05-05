# CI workflow（日本語）

v1.0.13では、既存のrelease gateをGitHub Actionsにつなげます。ローカルで使うコマンドを正とし、CI workflowは同じ検査をクリーンなcheckout上で実行します。

## 同梱workflow

| ファイル | 目的 |
|---|---|
| `.github/workflows/test.yml` | Python 3.10、3.11、3.12でpytestを実行します。 |
| `.github/workflows/release-check.yml` | release gateを実行し、`build/release_manifest.json` と `docs/release_summary.json` を生成します。 |

## ローカルで対応するコマンド

release workflowは、リリース前に実行すべき次のコマンドと同じです。

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
```

test workflowは次を実行します。

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
```

`PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` は、runner側に入っている無関係なpytest pluginの影響を避けるための設定です。通常のローカル環境では `python3 -m pytest -q` もそのまま使えます。

## artifact

release-check workflowでは、存在する場合に次のファイルをartifactとして保存します。

- `build/release_manifest.json`
- `docs/release_summary.json`
- `docs/release_report.md`
- `docs/release_report.json`

`docs/release_summary.json` はCI向けの小さな結果ファイルです。全体status、成功/失敗数、警告数、release category別summary、severity別summary、診断コード、失敗した検査を記録します。

## branch protectionで推奨する検査

リポジトリ運用では、merge前に次の検査を必須にするのがよいです。

- `SLDL tests / pytest`
- `SLDL release check / release-check`

これにより、template-schema binding、生成reference、diagnostics reference、release report、release summary、公式サンプル、build manifestの同期を保ちやすくなります。
