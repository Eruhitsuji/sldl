# 既知の制限

- PDF生成には外部LaTeX環境が必要です。標準release checkではdry-runを使います。
- Mermaid図はMarkdown/HTMLではMermaidコードとして出力されます。LaTeX向けにはcode、placeholder、external-imageを選べます。
- schemaとlogic checkは文書構造の検査であり、完全な形式証明システムではありません。
- golden snapshotはバイト単位の検査です。出力を意図的に変えた場合は再生成が必要です。
