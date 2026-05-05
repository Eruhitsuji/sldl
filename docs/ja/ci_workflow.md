# CI workflow（日本語）

v1.0.16では、v1.0.15のclean checkout向けrelease workflowを維持しつつ、GitHub-hosted runner上でtest workflowが安全に動くようにします。ローカルのrelease gateを正とし、CIではpytestを直接インストールし、package metadataを静的に検査し、既存の `build/` ファイルに依存しない形にします。

## 同梱workflow

| ファイル | 目的 |
|---|---|
| `.github/workflows/test.yml` | test extraをインストールし、Python 3.10、3.11、3.12でpytestを実行します。 |
| `.github/workflows/release-check.yml` | release gateを実行し、CI artifactを `build/` 以下に出力した後、manifest生成後にrelease reportのdrift checkを実行します。 |

## ローカルで対応するコマンド

```bash
python -m pip install --upgrade pip
python -m pip install pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q

mkdir -p build
python -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json build/release_summary.json

python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format markdown --check docs/release_report.md
python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format markdown --language ja --check docs/ja/release_report.md
python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format json --check docs/release_report.json
```


## editable install metadata

v1.0.15のtest workflowではeditable installを使っていましたが、flat repository layoutではpackage discoveryが明示されていないと失敗することがあります。v1.0.16ではCIをeditable installに依存させず、さらにsetuptoolsのpackage discoveryを明示して `sldl_compiler` だけをpackage対象にします。

## release report検査をrelease gate後に置く理由

`docs/release_report.md` と `docs/release_report.json` は `build/release_manifest.json` から生成されます。GitHub Actionsのclean checkoutでは、release gate実行前にこのmanifestが存在しません。そのためv1.0.16では、release reportのdrift checkをrelease gate内部のcommand listから外し、manifest生成直後にworkflow側で実行します。

## artifact

release-check workflowでは、`build/release_manifest.json`、`build/release_summary.json`、`docs/release_report.md`、`docs/release_report.json` をartifactとして保存します。
