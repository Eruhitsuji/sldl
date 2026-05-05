# SLDL v1.0.14 リリースノート

v1.0.14は、v1.0.13で追加したGitHub Actions workflow向けのCI依存関係hotfixです。release gateの設計は維持しつつ、GitHub-hosted runnerのクリーンな環境でも安定して動くようにします。

## 主な変更

- `.github/workflows/test.yml` にpytestの明示的なインストールstepを追加。
- `.github/workflows/release-check.yml` に `mkdir -p build` の準備stepを追加。
- `pyproject.toml` をv1.0.14へ更新し、test用optional dependency metadataを追加。
- CI workflow説明ドキュメントの日英版を、依存関係setupを含む内容に更新。
- CI workflowの依存関係setupとrelease metadataの同期を保つため、release checkとテストを拡張。

## 互換性

このリリースでは、SLDL言語文法やdocument modelの互換性変更はありません。既存のv1.0.13文書、template、schema、project fileはそのまま利用できます。
