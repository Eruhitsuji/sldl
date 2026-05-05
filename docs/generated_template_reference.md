# SLDL Template Reference

Generated from the bundled template manifest. In v1.0.12, release checks keep the template and diagnostics reference drift checks and also drift-check the reference index and CLI help reference.

| Name | Document type | Language | Schema | Role |
|---|---|---|---|---|
| `paper` | `Paper` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `paper_en` | `Paper` | `en-US` | `examples/sldl_schema.json` | `canonical` |
| `article` | `Article` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `explainer` | `Explainer` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `minutes` | `Minutes` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `research_report_en` | `ResearchReport` | `en-US` | `examples/sldl_schema.json` | `canonical` |
| `research_report_ja` | `JapaneseResearchReport` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `project_overview_en` | `ProjectOverview` | `en-US` | `examples/sldl_schema.json` | `canonical` |
| `project_overview_ja` | `ProjectOverview` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `japanese_research_report` | `JapaneseResearchReport` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `japanese_thesis` | `JapaneseThesis` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |
| `technical_specification` | `TechnicalSpecification` | `ja-JP` | `examples/sldl_schema.json` | `canonical` |

## Commands

```bash
python3 -S -m sldl_compiler.cli template list
python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown
python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md
python3 -S -m sldl_compiler.cli template project research_report_en --document-output examples/generated.sldl -o examples/generated_project.json --force
```
