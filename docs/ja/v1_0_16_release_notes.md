# SLDL v1.0.16 リリースノート

v1.0.16は、v1.0.15のclean checkout修正後に行うGitHub Actions test workflow安定化版です。

## 主な変更

- test workflowをpytestの直接インストールに戻し、GitHub-hosted runnerでeditable install時に失敗しないようにしました。
- `pyproject.toml` にsetuptoolsの明示的なpackage discovery設定を追加し、Python package metadataを明確にしました。
- test workflowに軽量なpackage metadata検査stepを追加しました。
- v1.0.15のrelease-check修正を維持し、CIでは `build/release_summary.json` を出力し、`build/release_manifest.json` 生成後にrelease reportを検査します。
- v1.0.16向けに生成済みreference、release report、release summary metadataを更新しました。

## このリリースの目的

v1.0.15のtest workflowでは `python -m pip install -e ".[test]"` を使っていました。flat repository layoutでは、`docs`、`examples`、`templates`、`schemas` などのtop-level directoryをsetuptoolsが検出し、package discoveryが明示されていないとeditable installが失敗することがあります。v1.0.16ではCIをeditable installに依存させず、今後のpackagingに向けてpackage discoveryも明示します。

## 検証コマンド

```bash
python -m pip install pytest
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest -q

mkdir -p build
python -S -m sldl_compiler.cli quality release \
  --targets examples/release_check.json \
  --manifest build/release_manifest.json \
  --summary-json build/release_summary.json

python -S -m sldl_compiler.cli quality report build/release_manifest.json \
  --format json --check docs/release_report.json
```
