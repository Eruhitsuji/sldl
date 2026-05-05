# CI workflow（日本語）

v1.0.14は、v1.0.13で追加したGitHub Actions workflow向けのCI依存関係hotfixです。ローカルで使うコマンドを正とし、CI workflowは依存関係を明示的に準備したうえで、同じ検査をクリーンなcheckout上で実行します。

## 同梱workflow

| ファイル | 目的 |
|---|---|
| `.github/workflows/test.yml` | pytestをインストールしてから、Python 3.10、3.11、3.12でpytestを実行します。 |
| `.github/workflows/release-check.yml` | `build/` を準備し、release gateを実行し、`build/release_manifest.json` と `docs/release_summary.json` を生成します。 |

## ローカルで対応するコマンド

```bash
python3 -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json docs/release_summary.json
```

GitHub ActionsのPython環境はクリーンなため、test workflowではpytestの前に次の依存関係setupを行います。

```bash
python3 -m pip install --upgrade pip
python3 -m pip install pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -q
```
