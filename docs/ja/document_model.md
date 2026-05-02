# 文書モデル

SLDLの文書モデルは、source layer、configuration layer、output layerの3層で考えます。

## Source layer

`.sldl` ファイルです。文書本文、メタ情報、章節、主張、根拠、結論、参考文献などを含みます。

## Configuration layer

JSON設定です。主な種類は `sldl.schema`、`sldl.project`、`sldl.export_labels`、`sldl.latex_build`、`sldl.release_check`、`sldl.snapshot_manifest` です。

## Output layer

Markdown、HTML、LaTeX、PDF、manifestなどの生成物です。生成物は手で管理するソースではなく、`project build` で再生成する成果物として扱います。
