from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

VERSION="1.0.10"
CODE_RE=re.compile(r"\b[EW]_[A-Z0-9_]+\b")

CATEGORY_PREFIXES=[
    ("E_BIBTEX", "BibTeX"), ("W_BIBTEX", "BibTeX"),
    ("E_BUILD_MANIFEST", "Build manifest"), ("W_BUILD_MANIFEST", "Build manifest"),
    ("E_CONFIG", "Config"), ("W_CONFIG", "Config"),
    ("E_EXPORT_LABELS", "Export labels"), ("W_EXPORT_LABELS", "Export labels"),
    ("E_FUNCTION", "Function"), ("W_FUNCTION", "Function"),
    ("E_INVALID", "Document validation"), ("W_MISSING", "Document validation"),
    ("E_LATEX", "LaTeX build/config"), ("W_LATEX", "LaTeX build/config"),
    ("E_LOGIC", "Logic"), ("W_LOGIC", "Logic"),
    ("E_OBJECT", "Object/schema"), ("W_OBJECT", "Object/schema"),
    ("E_PROJECT", "Project"), ("W_PROJECT", "Project"),
    ("E_RELEASE", "Release check"), ("W_RELEASE", "Release check"),
    ("E_SCHEMA", "Schema"), ("W_SCHEMA", "Schema"),
    ("E_SNAPSHOT", "Snapshot"), ("W_SNAPSHOT", "Snapshot"),
    ("E_SYNTAX", "Syntax"), ("W_SYNTAX", "Syntax"),
    ("E_TEMPLATE_REFERENCE", "Template reference"), ("W_TEMPLATE_REFERENCE", "Template reference"),
    ("E_TEMPLATE_MANIFEST", "Template manifest"), ("W_TEMPLATE_MANIFEST", "Template manifest"),
    ("E_TEMPLATE_SCHEMA", "Template/schema binding"), ("W_TEMPLATE_SCHEMA", "Template/schema binding"),
    ("E_TEMPLATE", "Template"), ("W_TEMPLATE", "Template"),
    ("E_TYPE", "Type system"), ("W_TYPE", "Type system"),
    ("E_UNDEFINED", "Reference resolution"), ("W_UNUSED", "Reference resolution"),
    ("W_UNKNOWN", "Unknown item"),
]

EN_FIXES={
    "BibTeX": "Check the BibTeX source, duplicated keys, and ignored text before importing references again.",
    "Build manifest": "Regenerate the project build manifest and verify recorded template metadata, hashes, outputs, and document diagnostics.",
    "Config": "Open the JSON config, confirm config_type, required keys, value types, and referenced paths.",
    "Export labels": "Check the export label JSON and make sure label values are strings.",
    "Function": "Check function names, argument count, argument types, and the schema-defined function signatures.",
    "Document validation": "Check the SLDL block fields, required fields, table rows, chart references, and dates around the reported location.",
    "LaTeX build/config": "Check LaTeX build JSON, command steps, engine settings, and LaTeX option values.",
    "Logic": "Inspect claim/evidence/reason/conclusion links, logic endpoints, source references, cycles, and support polarity.",
    "Object/schema": "Compare object fields with the schema-defined object class and allowed field types.",
    "Project": "Check the project JSON, document input paths, output definitions, schema references, and declared document_type values.",
    "Release check": "Check examples/release_check.json and the failing release-check command, required file, config, snapshot, or manifest entry.",
    "Schema": "Check schema JSON structure, document_types, node rules, object classes, relation rules, and schema config_type.",
    "Snapshot": "Regenerate or update the golden snapshot after confirming generated files are intentionally changed.",
    "Syntax": "Fix the SLDL syntax near the reported token, delimiter, quote, or block boundary.",
    "Template reference": "Regenerate the template reference from the canonical manifest and rerun the drift check.",
    "Template manifest": "Check templates/template_manifest.json, bound schema/export/LaTeX config paths, document_type, and template file paths.",
    "Template/schema binding": "Make the template document type, manifest document_type, and bound schema document_types agree.",
    "Template": "Check the selected template name, template path, schema override policy, and generated document type.",
    "Type system": "Check the expected and actual SLDL value types around the reported field or function call.",
    "Reference resolution": "Check ids, cite keys, reference targets, and unused or missing references.",
    "Unknown item": "Check spelling and whether the referenced type, function, or object is declared in the schema.",
    "General": "Check the reported message, source location, and related configuration file.",
}

JA_FIXES={
    "BibTeX": "BibTeXソース、重複キー、無視されたテキストを確認してから再インポートしてください。",
    "Build manifest": "project build manifestを再生成し、template metadata、hash、出力、文書診断を確認してください。",
    "Config": "JSON設定のconfig_type、必須キー、値の型、参照パスを確認してください。",
    "Export labels": "export label JSONを確認し、label値が文字列になっているか確認してください。",
    "Function": "関数名、引数数、引数型、schemaで定義した関数シグネチャを確認してください。",
    "Document validation": "報告位置付近のSLDLブロック、必須フィールド、表の行、chart参照、日付を確認してください。",
    "LaTeX build/config": "LaTeX build JSON、コマンドステップ、engine設定、LaTeX option値を確認してください。",
    "Logic": "claim/evidence/reason/conclusionのリンク、logic endpoint、source reference、cycle、support polarityを確認してください。",
    "Object/schema": "object fieldをschemaで定義したobject classと許可field typeに照合してください。",
    "Project": "project JSON、document input path、output定義、schema参照、declared document_typeを確認してください。",
    "Release check": "examples/release_check.jsonと失敗したrelease-check command、required file、config、snapshot、manifest項目を確認してください。",
    "Schema": "schema JSONの構造、document_types、node rules、object classes、relation rules、schema config_typeを確認してください。",
    "Snapshot": "生成ファイルの変更が意図したものか確認したうえでgolden snapshotを再生成または更新してください。",
    "Syntax": "報告されたtoken、delimiter、quote、block境界付近のSLDL構文を修正してください。",
    "Template reference": "canonical manifestからtemplate referenceを再生成し、drift checkを再実行してください。",
    "Template manifest": "templates/template_manifest.json、紐づけschema/export/LaTeX config path、document_type、template file pathを確認してください。",
    "Template/schema binding": "template本文のdocument type、manifestのdocument_type、schemaのdocument_typesを一致させてください。",
    "Template": "選択したtemplate名、template path、schema override policy、生成文書のdocument typeを確認してください。",
    "Type system": "報告されたfieldまたはfunction call付近で、期待型と実際のSLDL値型を確認してください。",
    "Reference resolution": "id、cite key、reference target、未使用または未定義参照を確認してください。",
    "Unknown item": "スペルと、参照した型・関数・objectがschemaで宣言されているか確認してください。",
    "General": "報告メッセージ、source location、関連設定ファイルを確認してください。",
}


def _category(code: str) -> str:
    for prefix,category in CATEGORY_PREFIXES:
        if(code.startswith(prefix)):
            return category
    return "General"


def _title_from_code(code: str) -> str:
    parts=code.split("_", 1)
    body=parts[1] if(len(parts)>1) else code
    return body.replace("_", " ").title()


def _collect_code_sources(root: str | Path | None = None) -> dict[str, set[str]]:
    base=Path(root) if(root is not None) else Path.cwd()
    compiler_dir=base/"sldl_compiler"
    if(not compiler_dir.exists()):
        compiler_dir=Path(__file__).resolve().parent
        base=compiler_dir.parent
    result: dict[str, set[str]]={}
    for path in sorted(compiler_dir.rglob("*.py")):
        if(path.name=="diagnostic_reference.py"):
            continue
        rel=path.relative_to(base).as_posix() if(_is_relative_to(path, base)) else path.as_posix()
        text=path.read_text(encoding="utf-8")
        for match in CODE_RE.finditer(text):
            result.setdefault(match.group(0), set()).add(rel)
    return result


def build_diagnostics_reference(root: str | Path | None = None, language: str = "en") -> dict[str, Any]:
    sources=_collect_code_sources(root)
    fixes=JA_FIXES if(language=="ja") else EN_FIXES
    codes=[]
    for code in sorted(sources):
        category=_category(code)
        level="error" if(code.startswith("E_")) else "warning"
        codes.append({
            "code": code,
            "level": level,
            "category": category,
            "title": _title_from_code(code),
            "meaning": _meaning(code, category, language),
            "fix": fixes.get(category, fixes["General"]),
            "sources": sorted(sources[code]),
        })
    return {
        "config_type": "sldl.diagnostics_reference",
        "description": "Generated SLDL diagnostics code reference" if(language=="en") else "生成されたSLDL診断コードリファレンス",
        "version": VERSION,
        "language": language,
        "generator": "sldl_compiler.diagnostic_reference",
        "source_root": "sldl_compiler",
        "counts": {
            "total": len(codes),
            "errors": sum(1 for item in codes if(item["level"]=="error")),
            "warnings": sum(1 for item in codes if(item["level"]=="warning")),
        },
        "codes": codes,
    }


def render_diagnostics_reference_markdown(reference: dict[str, Any], language: str = "en") -> str:
    codes=reference.get("codes", []) if(isinstance(reference.get("codes"), list)) else []
    counts=reference.get("counts", {}) if(isinstance(reference.get("counts"), dict)) else {}
    if(language=="ja"):
        lines=[
            "# SLDL 診断コードリファレンス",
            "",
            "このファイルは `sldl_compiler` のソースから生成した診断コード一覧です。",
            "",
            f"- version: `{reference.get('version', '')}`",
            f"- total: `{counts.get('total', len(codes))}`",
            f"- errors: `{counts.get('errors', 0)}`",
            f"- warnings: `{counts.get('warnings', 0)}`",
            "",
            "## 使い方",
            "",
            "エラーや警告が出たら、まず `Code` を確認し、この表の `Category` と `Fix` を見て原因の範囲を絞ります。v1.0.10では、この一覧を `diagnostics docs` で再生成・差分確認でき、`reference index` から他の生成リファレンスとまとめて参照できます。",
            "",
        ]
    else:
        lines=[
            "# SLDL Diagnostics Reference",
            "",
            "This file is generated from diagnostic codes found in the `sldl_compiler` source tree.",
            "",
            f"- version: `{reference.get('version', '')}`",
            f"- total: `{counts.get('total', len(codes))}`",
            f"- errors: `{counts.get('errors', 0)}`",
            f"- warnings: `{counts.get('warnings', 0)}`",
            "",
            "## How to use this reference",
            "",
            "When an error or warning appears, look up its `Code`, then use `Category` and `Fix` to narrow down the relevant file, schema, project, template, or source block. In v1.0.10, this list can be regenerated and drift-checked with `diagnostics docs`, and it is linked from the generated `reference index`.",
            "",
        ]
    lines.extend([
        "## Codes",
        "",
        "| Code | Level | Category | Meaning | Fix | Sources |",
        "|---|---|---|---|---|---|",
    ])
    for item in codes:
        sources=", ".join(item.get("sources", []))
        lines.append("| {code} | {level} | {category} | {meaning} | {fix} | {sources} |".format(
            code=_md(item.get("code", "")),
            level=_md(item.get("level", "")),
            category=_md(item.get("category", "")),
            meaning=_md(item.get("meaning", "")),
            fix=_md(item.get("fix", "")),
            sources=_md(sources),
        ))
    lines.append("")
    return "\n".join(lines)


def render_diagnostics_reference_json(reference: dict[str, Any]) -> str:
    return json.dumps(reference, ensure_ascii=False, indent=2)+"\n"


def _meaning(code: str, category: str, language: str) -> str:
    title=_title_from_code(code)
    if(language=="ja"):
        level="エラー" if(code.startswith("E_")) else "警告"
        return f"{category}に関する{level}: {title}。"
    level="error" if(code.startswith("E_")) else "warning"
    return f"{level.title()} related to {category}: {title}."


def _md(value: Any) -> str:
    text=str(value).replace("|", "\\|").replace("\n", " ")
    return text


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
