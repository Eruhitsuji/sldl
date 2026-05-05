# SLDL CLI Help Reference（日本語）

CLIの `--help` 出力を静的ドキュメントとしてまとめたリファレンスです。ヘルプ本文はCLI実装から生成されます。

- version: `1.0.16`
- commands: `45`

## `sldlc`

```text
Command: sldlc
Usage: sldlc <command>

Description:
SLDL v1.0.16 compiler

Subcommands:
  bib
  build
  check
  config
  diagnostics
  export
  format
  grammar
  latex
  logic
  project
  quality
  reference
  schema
  template

Options:
  -h, --help - show this help message and exit
```

## `bib`

```text
Command: bib
Usage: bib <command>

Subcommands:
  check
  import

Options:
  -h, --help - show this help message and exit
```

## `bib check`

```text
Command: bib check
Usage: bib check <input>

Arguments:
  input

Options:
  -h, --help - show this help message and exit
```

## `bib import`

```text
Command: bib import
Usage: bib import <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
```

## `build`

```text
Command: build
Usage: build <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
  --schema SCHEMA
  --warnings-as-errors
  --no-source-context
```

## `check`

```text
Command: check
Usage: check <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  --schema SCHEMA
  --warnings-as-errors
  --no-source-context
```

## `config`

```text
Command: config
Usage: config <command>

Subcommands:
  check
  explain
  init
  list

Options:
  -h, --help - show this help message and exit
```

## `config check`

```text
Command: config check
Usage: config check <files> [options]

Arguments:
  files

Options:
  -h, --help - show this help message and exit
  --type TYPE - expected config_type Choices: sldl.build_manifest, sldl.cli_help_reference, sldl.diagnostics_reference, sldl.export_labels, sldl.latex_build, sldl.project, sldl.reference_index, sldl.release_check, sldl.release_manifest, sldl.release_report, sldl.release_summary, sldl.schema, sldl.snapshot_manifest, sldl.template_manifest, sldl.template_reference.
  --warnings-as-errors
  --no-path-check - do not warn when referenced files do not exist
  --json
```

## `config explain`

```text
Command: config explain
Usage: config explain <target> [options]

Arguments:
  target - config_type value or JSON file path

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
```

## `config init`

```text
Command: config init
Usage: config init <type> [options]

Arguments:
  type

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
  --force
```

## `config list`

```text
Command: config list
Usage: config list [options]

Options:
  -h, --help - show this help message and exit
  --json
```

## `diagnostics`

```text
Command: diagnostics
Usage: diagnostics <command>

Subcommands:
  docs
  list

Options:
  -h, --help - show this help message and exit
```

## `diagnostics docs`

```text
Command: diagnostics docs
Usage: diagnostics docs [options]

Options:
  -h, --help - show this help message and exit
  --root ROOT - project root used for source scanning
  --format FORMAT - Choices: markdown, json.
  --language LANGUAGE - Choices: en, ja.
  --check CHECK - compare generated output with an existing static file and fail if it differs
  -o, --output OUTPUT
```

## `diagnostics list`

```text
Command: diagnostics list
Usage: diagnostics list [options]

Options:
  -h, --help - show this help message and exit
  --root ROOT - project root used for source scanning
  --language LANGUAGE - Choices: en, ja.
  --json
```

## `export`

```text
Command: export
Usage: export <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  --format FORMAT - Choices: json, markdown, html, latex, bibtex, mermaid, logic-markdown, logic-mermaid.
  -o, --output OUTPUT
  --schema SCHEMA
  --citation-style CITATION_STYLE - citation/reference style for markdown/html export Choices: numeric, ieee, apa, author-year.
  --export-config EXPORT_CONFIG - JSON file for language-dependent export labels
  --latex-profile LATEX_PROFILE - LaTeX profile, e.g. platex-jsarticle, platex-jreport, uplatex-jsarticle, lualatex-ltjsarticle
  --latex-class LATEX_CLASS - Override LaTeX document class
  --latex-class-options LATEX_CLASS_OPTIONS - Override LaTeX document class options
  --latex-geometry LATEX_GEOMETRY - geometry package options, e.g. margin=25mm
  --latex-hyperref, --no-latex-hyperref  - Enable or disable hyperref in LaTeX output
  --latex-sloppy, --no-latex-sloppy  - Enable or disable overfull-box mitigation in LaTeX output
  --latex-table-font LATEX_TABLE_FONT - Font size for generated longtable blocks Choices: none, normalsize, small, footnotesize, scriptsize.
  --latex-top-level LATEX_TOP_LEVEL - Render top-level SLDL sections as LaTeX sections or chapters Choices: section, chapter.
  --latex-code-environment LATEX_CODE_ENVIRONMENT - Environment used for CodeBlock, Chart, and Flowchart source blocks Choices: lstlisting, verbatim.
  --latex-figure-width LATEX_FIGURE_WIDTH - Default width for Figure includegraphics, e.g. 0.9\linewidth
  --latex-code-font-size LATEX_CODE_FONT_SIZE - Font size for generated lstlisting blocks Choices: none, normalsize, small, footnotesize, scriptsize.
  --mermaid-mode MERMAID_MODE - LaTeX rendering mode for Chart/Flowchart Mermaid diagrams Choices: code, placeholder, external-image.
  --toc, --no-toc  - Enable or disable a generated table of contents for supported export formats
  --logic-source-edge-direction LOGIC_SOURCE_EDGE_DIRECTION - direction used when displaying source/cite edges in logic exports Choices: reference-to-evidence, evidence-to-reference.
  --warnings-as-errors
  --no-source-context
```

## `format`

```text
Command: format
Usage: format <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
  --in-place
  --check
  --indent INDENT
```

## `grammar`

```text
Command: grammar
Usage: grammar [options]

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
```

## `latex`

```text
Command: latex
Usage: latex <command>

Subcommands:
  build

Options:
  -h, --help - show this help message and exit
```

## `latex build`

```text
Command: latex build
Usage: latex build <input> [options]

Arguments:
  input - input .tex file

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT - output PDF path
  --config CONFIG - external JSON build configuration
  --dry-run - print commands without executing them
```

## `logic`

```text
Command: logic
Usage: logic <command>

Subcommands:
  graph
  report

Options:
  -h, --help - show this help message and exit
```

## `logic graph`

```text
Command: logic graph
Usage: logic graph <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
  --schema SCHEMA
  --source-edge-direction SOURCE_EDGE_DIRECTION - direction used when displaying source/cite edges Choices: reference-to-evidence, evidence-to-reference.
  --warnings-as-errors
  --no-source-context
```

## `logic report`

```text
Command: logic report
Usage: logic report <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
  --schema SCHEMA
  --source-edge-direction SOURCE_EDGE_DIRECTION - direction used when displaying source/cite edges Choices: reference-to-evidence, evidence-to-reference.
  --warnings-as-errors
  --no-source-context
```

## `project`

```text
Command: project
Usage: project <command>

Subcommands:
  build
  check

Options:
  -h, --help - show this help message and exit
```

## `project build`

```text
Command: project build
Usage: project build <project> [options]

Arguments:
  project

Options:
  -h, --help - show this help message and exit
  --manifest MANIFEST - override output manifest path
  --warnings-as-errors
  --no-source-context
```

## `project check`

```text
Command: project check
Usage: project check <project> [options]

Arguments:
  project

Options:
  -h, --help - show this help message and exit
  --warnings-as-errors
  --no-source-context
```

## `quality`

```text
Command: quality
Usage: quality <command>

Subcommands:
  manifest
  release
  report
  snapshot
  snapshot-check

Options:
  -h, --help - show this help message and exit
```

## `quality manifest`

```text
Command: quality manifest
Usage: quality manifest <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  --warnings-as-errors
```

## `quality release`

```text
Command: quality release
Usage: quality release [options]

Options:
  -h, --help - show this help message and exit
  --targets TARGETS - sldl.release_check JSON target file
  --manifest MANIFEST - write an sldl.release_manifest JSON
  --warnings-as-errors
  --fail-on-warning - treat release warnings as failures; CI-friendly alias for warning-sensitive release gates
  --summary-json SUMMARY_JSON - write a compact sldl.release_summary JSON file for CI systems
  --json
```

## `quality report`

```text
Command: quality report
Usage: quality report <input> [options]

Arguments:
  input - input sldl.release_manifest JSON

Options:
  -h, --help - show this help message and exit
  --format FORMAT - Choices: markdown, json.
  --language LANGUAGE - Choices: en, ja.
  -o, --output OUTPUT
  --check CHECK - compare generated report with an existing file
```

## `quality snapshot`

```text
Command: quality snapshot
Usage: quality snapshot <files> [options]

Arguments:
  files

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
  --base-dir BASE_DIR
  --description DESCRIPTION
```

## `quality snapshot-check`

```text
Command: quality snapshot-check
Usage: quality snapshot-check <input> [options]

Arguments:
  input

Options:
  -h, --help - show this help message and exit
  --base-dir BASE_DIR
  --warnings-as-errors
  --json
```

## `reference`

```text
Command: reference
Usage: reference <command>

Subcommands:
  cli-help
  index

Options:
  -h, --help - show this help message and exit
```

## `reference cli-help`

```text
Command: reference cli-help
Usage: reference cli-help [options]

Options:
  -h, --help - show this help message and exit
  --format FORMAT - Choices: markdown, json.
  --language LANGUAGE - Choices: en, ja.
  --check CHECK - compare generated output with an existing static file and fail if it differs
  -o, --output OUTPUT
```

## `reference index`

```text
Command: reference index
Usage: reference index [options]

Options:
  -h, --help - show this help message and exit
  --root ROOT - project root used for hashing referenced files
  --format FORMAT - Choices: markdown, json.
  --language LANGUAGE - Choices: en, ja.
  --check CHECK - compare generated output with an existing static file and fail if it differs
  -o, --output OUTPUT
```

## `schema`

```text
Command: schema
Usage: schema <command>

Subcommands:
  check
  explain
  list

Options:
  -h, --help - show this help message and exit
```

## `schema check`

```text
Command: schema check
Usage: schema check <schema_files> [options]

Arguments:
  schema_files

Options:
  -h, --help - show this help message and exit
  --warnings-as-errors
```

## `schema explain`

```text
Command: schema explain
Usage: schema explain <schema_files> [options]

Arguments:
  schema_files

Options:
  -h, --help - show this help message and exit
  --document-type DOCUMENT_TYPE
  -o, --output OUTPUT
```

## `schema list`

```text
Command: schema list
Usage: schema list <schema_files> [options]

Arguments:
  schema_files

Options:
  -h, --help - show this help message and exit
  --json
```

## `template`

```text
Command: template
Usage: template <command>

Subcommands:
  check
  docs
  explain
  list
  new
  project

Options:
  -h, --help - show this help message and exit
```

## `template check`

```text
Command: template check
Usage: template check <name> [options]

Arguments:
  name - template name

Options:
  -h, --help - show this help message and exit
  --template-dir TEMPLATE_DIR
  --schema SCHEMA - schema override; requires --allow-schema-override when the template already binds a schema
  --strict-schema - treat schema warnings as errors
  --allow-schema-override - allow overriding the schema bound by the template manifest
```

## `template docs`

```text
Command: template docs
Usage: template docs [options]

Options:
  -h, --help - show this help message and exit
  --template-dir TEMPLATE_DIR
  --format FORMAT - Choices: markdown, json.
  --language LANGUAGE - Choices: en, ja.
  --check CHECK - compare generated output with an existing static file and fail if it differs
  -o, --output OUTPUT
```

## `template explain`

```text
Command: template explain
Usage: template explain <name> [options]

Arguments:
  name - template name

Options:
  -h, --help - show this help message and exit
  --template-dir TEMPLATE_DIR
  --format FORMAT - Choices: text, markdown, json.
  --json - deprecated alias for --format json
  -o, --output OUTPUT - write explanation to a file
```

## `template list`

```text
Command: template list
Usage: template list [options]

Options:
  -h, --help - show this help message and exit
  --template-dir TEMPLATE_DIR
```

## `template new`

```text
Command: template new
Usage: template new <name> [options]

Arguments:
  name

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT
  --force
  --template-dir TEMPLATE_DIR
  --schema SCHEMA - create from schema when name is omitted, or override a named template schema when allowed
  --document-type DOCUMENT_TYPE - document_types.<TypeName> to use when a schema contains multiple document types
  --strict-schema - treat schema warnings as errors during generation check
  --allow-schema-override - allow overriding the schema bound by the template manifest
```

## `template project`

```text
Command: template project
Usage: template project <name> [options]

Arguments:
  name - template name

Options:
  -h, --help - show this help message and exit
  -o, --output OUTPUT - project JSON output path
  --document-output DOCUMENT_OUTPUT - SLDL document output path
  --force
  --template-dir TEMPLATE_DIR
  --schema SCHEMA - schema JSON override; by default the template manifest binding is used
  --export-config EXPORT_CONFIG - export label config override; by default the template manifest value is used
  --latex-build-config LATEX_BUILD_CONFIG - LaTeX build config override; by default the template manifest value is used
  --strict-schema - treat schema warnings as errors during generation check
  --allow-schema-override - allow overriding the schema bound by the template manifest
  --build-dir BUILD_DIR - generated output directory used inside the project JSON
  --formats FORMATS - comma-separated output formats
  --citation-style CITATION_STYLE
  --toc, --no-toc 
  --latex-profile LATEX_PROFILE
  --latex-geometry LATEX_GEOMETRY
  --latex-top-level LATEX_TOP_LEVEL - Choices: section, chapter.
  --latex-code-font-size LATEX_CODE_FONT_SIZE - Choices: none, normalsize, small, footnotesize, scriptsize.
  --mermaid-mode MERMAID_MODE - Choices: code, placeholder, external-image.
```
