# template と schema の紐づけ

SLDLでは、`templates/template_manifest.json` によって付属テンプレートとschemaを紐づけます。この紐づけにより、テンプレートは単なるSLDL本文の雛形ではなく、「どのdocument typeを生成するか」「どのschemaで検査するか」「どのexport/build設定を既定で使うか」まで持つ部品になります。

## Template manifest の主な項目

各テンプレートには主に次の項目を書けます。

- `name`: コマンドで使うテンプレート名。
- `description`: 説明文。
- `document_type`: 想定するSLDL document type。
- `language`: `en-US` や `ja-JP` などの言語タグ。
- `path`: manifestから見たSLDLテンプレートファイルのパス。
- `schema`: manifestから見たschema JSONのパス。
- `default_export_config`: 通常使うexport labels JSONのパス。
- `default_latex_build_config`: 通常使うLaTeX build JSONのパス。
- `strict_schema`: trueの場合、schema由来の警告も生成失敗として扱います。

v1.0.2では、紐づけ自体の検査を強化しました。参照先configの種類が正しいか、また `document_type` が紐づけschemaに定義されているかを確認します。

## コマンド

テンプレートに紐づく設定を確認します。

```bash
python3 -S -m sldl_compiler.cli template explain research_report_en
```

manifestに宣言されたschemaでテンプレートを検査します。

```bash
python3 -S -m sldl_compiler.cli template check research_report_en
```

schemaに紐づいたテンプレートから文書を生成します。生成された文書は、その場でschema検査されます。

```bash
python3 -S -m sldl_compiler.cli template new research_report_en \
  -o examples/my_report.sldl
```

文書とproject JSONを同時に生成します。project JSONには、テンプレート側で宣言されたschema、export labels、LaTeX build configが自動的に反映されます。

```bash
python3 -S -m sldl_compiler.cli template project research_report_en \
  -o examples/my_report_project.json \
  --document-output examples/my_report.sldl \
  --formats markdown,html,latex,pdf
```

## strict設定とoverride

テンプレートにschemaが紐づいている場合、通常は別schemaでの上書きは拒否されます。意図的に別schemaで試す場合は、`--schema` と `--allow-schema-override` を同時に指定します。

`strict_schema: true` の場合、警告もテンプレート生成検査の失敗として扱います。公式テンプレートでは、schemaとのずれをrelease前に検出するために有効です。

## 失敗例

`examples/template_schema_binding_failure_project.json` は意図的に不正な例です。ProjectOverviewのSLDL本文を参照しているにもかかわらず、project entry側で `document_type: "ResearchReport"` と宣言しています。そのため、`E_PROJECT_DOCUMENT_TYPE_MISMATCH` で失敗するのが正しい動作です。

```bash
python3 -S -m sldl_compiler.cli project check \
  examples/template_schema_binding_failure_project.json
```

## release checkとの統合

`examples/release_check.json` は、template manifest、正常系template command、生成project、意図的な失敗例を検査します。v1.0.2では expected-failure command に対応したため、失敗すべき例をリポジトリ内に保持したままrelease checkで検証できます。

## v1.0.3のmanifest互換性とexplain出力形式

v1.0.3では、`templates/template_manifest.json` と `templates/manifest.json` の互換性検査を追加しました。また、`template explain` は `text`、`markdown`、`json` の出力形式に対応します。project buildでは、document entryにtemplate由来情報がある場合、build manifestにもtemplate情報を記録します。

## v1.0.5の正式manifest方針

`templates/template_manifest.json` が正式なmanifestです。`templates/manifest.json` は互換用コピーとして残しますが、主な編集対象にはしません。正式manifestを変更した後は、次のコマンドでtemplate referenceを再生成できます。

```bash
python3 -S -m sldl_compiler.cli template docs --format markdown -o docs/generated_template_reference.md
```

release checkではmanifest互換性に加えて、project build manifestに記録されたtemplate情報も検査します。
