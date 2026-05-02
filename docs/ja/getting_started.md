# はじめに

このガイドでは、v1.0.0の公式二言語サンプルを使います。

## 1. project設定を検査する

```bash
python3 -S -m sldl_compiler.cli config check examples/project_official_examples.json
```

## 2. projectとして文書を検査する

```bash
python3 -S -m sldl_compiler.cli project check examples/project_official_examples.json
```

## 3. 出力を生成する

```bash
python3 -S -m sldl_compiler.cli project build examples/project_official_examples.json
```

生成物は `build/official_examples/` に出力されます。

## 4. release checkを実行する

```bash
python3 -S -m sldl_compiler.cli quality release   --targets examples/release_check.json   --manifest build/release_manifest.json
```
