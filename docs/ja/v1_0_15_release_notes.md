# SLDL v1.0.15 リリースノート

v1.0.15は、v1.0.13で追加し、v1.0.14で依存関係をhotfixしたGitHub Actions workflow向けのclean checkout修正版です。

主な修正点は、ローカルでは既存の `build/release_manifest.json` が残っているため検査が通る一方、GitHub Actionsのクリーンなcheckoutでは、release gateがmanifestを生成する前にrelease report検査がmanifestを読もうとして失敗する問題です。

## 変更点

- `examples/release_check.json` の中から、自己依存になっていた `quality-report-*` コマンドを除外。
- release reportのdrift checkを、`build/release_manifest.json` 生成後にGitHub Actions workflow側で実行するように変更。
- CI中は追跡対象の `docs/release_summary.json` を変更せず、`build/release_summary.json` にCI結果を書き出すように変更。
- release report関連テストを、既存の `build/release_manifest.json` に依存せず、一時manifestを生成して検査する形に変更。
- clean checkoutでのCI手順をドキュメントに反映。
- version metadataをv1.0.15に更新。
