# Template-schema binding

SLDL binds bundled templates to schemas through `templates/template_manifest.json`. The binding makes a template more than a source-file skeleton: it also declares the document type it is meant to produce, the schema used to check it, and the default export/build configs used by generated projects.

## Template manifest fields

Each template entry may contain:

- `name`: command-line template name.
- `description`: human-readable description.
- `document_type`: expected SLDL document type.
- `language`: language tag such as `en-US` or `ja-JP`.
- `path`: SLDL template file path, relative to the manifest.
- `schema`: schema JSON path, relative to the manifest.
- `default_export_config`: default export-label JSON path.
- `default_latex_build_config`: default LaTeX build JSON path.
- `strict_schema`: when true, schema warnings are treated as generation failures.

v1.0.2 validates the binding itself. The manifest check verifies that the bound files have the expected config types and that `document_type` is defined by the bound schema.

## Commands

Inspect a template binding:

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en
```

Check a template against the schema declared in the manifest:

```bash
python3 -S -m sldl_compiler.cli template check research_report_en
```

Create a document from a schema-bound template. The generated document is checked immediately with the template's bound schema:

```bash
python3 -S -m sldl_compiler.cli template new research_report_en \
  -o examples/my_report.sldl
```

Create both a document and a project JSON. The project automatically records the template's schema, export-label config, and LaTeX build config:

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  -o examples/my_report_project.json \
  --document-output examples/my_report.sldl \
  --formats markdown,html,latex,pdf
```

## Strictness and overrides

If a template already binds a schema, schema override is blocked by default. To intentionally test a template with a different schema, pass both `--schema` and `--allow-schema-override`.

`strict_schema: true` means warnings become failures during template generation checks. This is useful for official templates because schema drift should be caught before a release.

## Negative example

`examples/template_schema_binding_failure_project.json` is intentionally invalid. It points to a ProjectOverview source file while the project entry declares `document_type: "ResearchReport"`. It should fail with `E_PROJECT_DOCUMENT_TYPE_MISMATCH`.

```bash
python3 -S -m sldl_compiler.cli project check \
  examples/template_schema_binding_failure_project.json
```

## Release check integration

`examples/release_check.json` checks template manifests, positive template commands, generated projects, and the intentional negative example. v1.0.2 adds expected-failure release commands so invalid examples can be kept in the repository without breaking the release check.

## v1.0.3 manifest compatibility and explain formats

v1.0.3 adds compatibility validation between `templates/template_manifest.json` and `templates/manifest.json`. It also adds explicit `text`, `markdown`, and `json` output modes to `template explain`. Project builds preserve template metadata in the build manifest when a document entry contains template provenance fields.

## v1.0.6 canonical manifest policy

`templates/template_manifest.json` is the canonical manifest. `templates/manifest.json` is retained as a legacy compatibility copy and should not be treated as the primary edit target. Use the following command to regenerate the template reference after changing the canonical manifest:

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown -o docs/generated_template_reference.md
```

The release check validates the manifest compatibility copy and also validates template metadata recorded in project build manifests.
