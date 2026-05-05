from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

from .checker import check
from .exporter_html import export_html
from .exporter_json import export_json
from .exporter_latex import export_latex
from .latex_builder import build_latex_pdf
from .exporter_markdown import export_markdown
from .exporter_mermaid import export_mermaid
from .logic import run_logic_checks, export_logic_report, export_logic_mermaid
from .formatter import format_document
from .parser import parse_source
from .resolver import resolve
from .templates import get_template, get_template_from_schema, list_templates, template_info, template_info_markdown
from .schema_tools import check_schema_files, schema_explain, schema_summary
from .semantic import install_schema_semantics, check_semantics
from .bibtex_importer import attach_bibtex_references, parse_bibtex, bibtex_to_sldl_fragment, reference_id_from_bibkey
from .config_tools import SUPPORTED_CONFIG_TYPES, check_config_file, config_summary, explain_config_file, explain_config_type, init_config_data
from .quality import build_release_summary, check_snapshot, make_snapshot, run_release_check, validate_build_manifest
from .release_report import build_release_report, render_release_report_json, render_release_report_markdown
from .diagnostics import Diagnostic
from .diagnostic_reference import build_diagnostics_reference, render_diagnostics_reference_json, render_diagnostics_reference_markdown
from .reference_docs import (
    build_cli_help_reference,
    build_reference_index,
    render_cli_help_reference_json,
    render_cli_help_reference_markdown,
    render_reference_index_json,
    render_reference_index_markdown,
)

try:
    from .schemas import load_schema_registry, check_with_schema
except Exception:
    load_schema_registry=None
    check_with_schema=None

try:
    from .exporter_bibtex import export_bibtex
except Exception:
    export_bibtex=None

def load_and_analyze(path: Path, schema_path: str | list[str] | None = None):
    source=path.read_text(encoding="utf-8")
    doc=parse_source(source)
    attach_bibtex_references(doc, path)
    resolve(doc)
    check(doc)
    schema_paths=[]
    if(schema_path):
        schema_paths=[schema_path] if(isinstance(schema_path, str)) else list(schema_path)
    if(check_with_schema is not None and load_schema_registry is not None):
        if(schema_paths and _append_schema_input_diagnostics(doc, schema_paths)):
            run_logic_checks(doc, None)
            return doc, source
        registry=load_schema_registry([Path(p) for p in schema_paths])
        if(schema_paths):
            doc.schema_info={
                "sources": [str(p) for p in schema_paths],
                "document_type": doc.type_name,
                "known_document_type": doc.type_name in registry.document_schemas,
            }
        install_schema_semantics(doc, registry)
        check_with_schema(doc, registry)
        check_semantics(doc)
        run_logic_checks(doc, registry)
    else:
        run_logic_checks(doc, None)
    return doc, source


def print_diagnostics(doc, source: str | None = None, path: Path | None = None, show_source: bool = True) -> None:
    for diag in doc.diagnostics:
        try:
            print(diag.format(source if(show_source) else None, str(path) if(path) else None))
        except TypeError:
            print(diag.format())


def has_errors(doc, warnings_as_errors: bool = False) -> bool:
    if(any(d.level=="error" for d in doc.diagnostics)):
        return True
    if(warnings_as_errors and any(d.level=="warning" for d in doc.diagnostics)):
        return True
    return False


def _append_schema_input_diagnostics(doc, schema_paths: list[str]) -> bool:
    has_schema_error=False
    for raw_path in schema_paths:
        path=Path(raw_path)
        if(not path.exists()):
            doc.diagnostics.append(Diagnostic(
                "error",
                "E_SCHEMA_FILE_MISSING",
                f"Schema file does not exist: {path}. Check the --schema argument, project schemas entry, or template manifest schema binding.",
                doc.line,
                doc.column,
            ))
            has_schema_error=True
            continue
        try:
            data=json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            doc.diagnostics.append(Diagnostic(
                "error",
                "E_SCHEMA_JSON",
                f"Invalid JSON in schema file: {path}: {exc.msg}",
                exc.lineno,
                exc.colno,
            ))
            has_schema_error=True
            continue
        except OSError as exc:
            doc.diagnostics.append(Diagnostic(
                "error",
                "E_SCHEMA_FILE_READ",
                f"Cannot read schema file: {path} ({exc})",
                doc.line,
                doc.column,
            ))
            has_schema_error=True
            continue
        if(not isinstance(data, dict)):
            doc.diagnostics.append(Diagnostic(
                "error",
                "E_SCHEMA_ROOT",
                f"Schema file root must be a JSON object: {path}",
                doc.line,
                doc.column,
            ))
            has_schema_error=True
            continue
        config_type=data.get("config_type")
        if(config_type is not None and config_type!="sldl.schema"):
            doc.diagnostics.append(Diagnostic(
                "error",
                "E_SCHEMA_CONFIG_TYPE",
                f"Schema path must reference config_type sldl.schema, but {path} declares {config_type!r}. Use a schema JSON file or fix the template/project binding.",
                doc.line,
                doc.column,
            ))
            has_schema_error=True
    return has_schema_error


def print_warning_policy_note(doc, warnings_as_errors: bool) -> None:
    if(warnings_as_errors and any(d.level=="warning" for d in doc.diagnostics) and not any(d.level=="error" for d in doc.diagnostics)):
        print("FAILED: warnings treated as errors")


def command_check(args) -> int:
    path=Path(args.input)
    doc,source=load_and_analyze(path, args.schema)
    if(doc.diagnostics): print_diagnostics(doc, source, path, not args.no_source_context)
    print_warning_policy_note(doc, args.warnings_as_errors)
    if(has_errors(doc, args.warnings_as_errors)): return 1
    print(f"OK: {path}")
    return 0


def command_build(args) -> int:
    path=Path(args.input)
    doc,source=load_and_analyze(path, args.schema)
    if(doc.diagnostics): print_diagnostics(doc, source, path, not args.no_source_context)
    print_warning_policy_note(doc, args.warnings_as_errors)
    if(has_errors(doc, args.warnings_as_errors)):
        return 1
    output=export_json(doc)
    if(args.output):
        _write_text_file(Path(args.output), output)
        print(f"Wrote: {args.output}")
    else:
        print(output)
    return 0


def export_document_output(
    doc,
    input_path: Path,
    fmt: str,
    citation_style: str | None = None,
    export_config: str | None = None,
    logic_source_edge_direction: str = "reference-to-evidence",
    latex_options: dict | None = None,
    toc: bool | None = None,
) -> str:
    actual_format="json" if(fmt=="sldj") else fmt
    if(actual_format=="json"):
        return export_json(doc)
    if(actual_format=="markdown"):
        return export_markdown(doc, citation_style=citation_style, export_config_path=export_config, base_path=str(input_path.parent), toc=toc)
    if(actual_format=="html"):
        return export_html(doc, citation_style=citation_style, export_config_path=export_config, base_path=str(input_path.parent), toc=toc)
    if(actual_format=="latex"):
        if(toc is not None):
            latex_options=dict(latex_options or {})
            latex_options["toc"]=toc
        return export_latex(doc, citation_style=citation_style, export_config_path=export_config, base_path=str(input_path.parent), latex_options=latex_options)
    if(actual_format=="bibtex"):
        if(export_bibtex is None):
            raise RuntimeError("BibTeX exporter is not available in this build.")
        return export_bibtex(doc)
    if(actual_format=="mermaid"):
        return export_mermaid(doc)
    if(actual_format=="logic-markdown"):
        return export_logic_report(doc, source_edge_direction=logic_source_edge_direction)
    if(actual_format=="logic-mermaid"):
        return export_logic_mermaid(doc, source_edge_direction=logic_source_edge_direction)
    raise ValueError(f"Unsupported format: {fmt}")


def _collect_latex_options(*sources) -> dict:
    options={}
    legacy_map={
        "latex_profile":"profile",
        "latex_engine":"engine",
        "latex_class":"document_class",
        "latex_class_options":"class_options",
        "latex_geometry":"geometry",
        "latex_hyperref":"hyperref",
        "latex_sloppy":"sloppy",
        "latex_table_font":"table_font",
        "latex_top_level":"top_level",
        "latex_code_environment":"code_environment",
        "latex_figure_width":"figure_width",
        "latex_code_font_size":"code_font_size",
        "latex_mermaid_mode":"mermaid_mode",
        "latex_toc":"toc",
    }
    keys=[
        "profile",
        "engine",
        "document_class",
        "class_options",
        "geometry",
        "hyperref",
        "sloppy",
        "table_font",
        "top_level",
        "code_environment",
        "figure_width",
        "code_font_size",
        "mermaid_mode",
        "toc",
    ]
    for source in sources:
        if(not source):
            continue
        merged={}
        if(isinstance(source, dict)):
            merged.update(source)
            latex_block=source.get("latex")
            if(isinstance(latex_block, dict)):
                merged.update(latex_block)
        else:
            continue
        for key in keys:
            if(key in merged and merged[key] is not None):
                options[key]=merged[key]
        for src_key,dst_key in legacy_map.items():
            if(src_key in merged and merged[src_key] is not None):
                options[dst_key]=merged[src_key]
    return options

def _write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def command_export(args) -> int:
    path=Path(args.input)
    doc,source=load_and_analyze(path, args.schema)
    if(doc.diagnostics): print_diagnostics(doc, source, path, not args.no_source_context)
    print_warning_policy_note(doc, args.warnings_as_errors)
    if(has_errors(doc, args.warnings_as_errors)):
        return 1
    latex_options=_collect_latex_options({
        "profile": getattr(args, "latex_profile", None),
        "document_class": getattr(args, "latex_class", None),
        "class_options": getattr(args, "latex_class_options", None),
        "geometry": getattr(args, "latex_geometry", None),
        "hyperref": getattr(args, "latex_hyperref", None),
        "sloppy": getattr(args, "latex_sloppy", None),
        "table_font": getattr(args, "latex_table_font", None),
        "top_level": getattr(args, "latex_top_level", None),
        "code_environment": getattr(args, "latex_code_environment", None),
        "figure_width": getattr(args, "latex_figure_width", None),
        "code_font_size": getattr(args, "latex_code_font_size", None),
        "mermaid_mode": getattr(args, "mermaid_mode", None),
    })
    try:
        output=export_document_output(doc, path, args.format, args.citation_style, args.export_config, getattr(args, "logic_source_edge_direction", "reference-to-evidence"), latex_options=latex_options, toc=getattr(args, "toc", None))
    except (RuntimeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    if(args.output):
        _write_text_file(Path(args.output), output)
        print(f"Wrote: {args.output}")
    else:
        print(output)
    return 0

def command_logic(args) -> int:
    path=Path(args.input)
    doc,source=load_and_analyze(path, args.schema)
    if(doc.diagnostics): print_diagnostics(doc, source, path, not args.no_source_context)
    print_warning_policy_note(doc, args.warnings_as_errors)
    if(has_errors(doc, args.warnings_as_errors)):
        return 1
    source_edge_direction=getattr(args, "source_edge_direction", "reference-to-evidence")
    output=export_logic_mermaid(doc, source_edge_direction=source_edge_direction) if(args.logic_command=="graph") else export_logic_report(doc, source_edge_direction=source_edge_direction)
    if(args.output):
        _write_text_file(Path(args.output), output)
        print(f"Wrote: {args.output}")
    else:
        print(output)
    return 0

def command_format(args) -> int:
    path=Path(args.input)
    source=path.read_text(encoding="utf-8")
    doc=parse_source(source)
    resolve(doc)
    check(doc)
    if(has_errors(doc)):
        print_diagnostics(doc, source, path, True)
        return 1
    output=format_document(doc, indent=args.indent)
    if(args.check):
        normalized=source.rstrip()+"\n"
        if(normalized!=output):
            print(f"FORMAT NEEDED: {path}")
            return 1
        print(f"OK: {path}")
        return 0
    if(args.in_place): path.write_text(output, encoding="utf-8")
    elif(args.output): _write_text_file(Path(args.output), output)
    else: print(output, end="")
    return 0


def _paths_equivalent(a: str | Path | None, b: str | Path | None) -> bool:
    if(a is None or b is None):
        return a is b
    try:
        return Path(a).resolve()==Path(b).resolve()
    except OSError:
        return str(a)==str(b)


def _schema_for_template(args, tmpl) -> str | None:
    override=getattr(args, "schema", None)
    if(override and tmpl.schema and not getattr(args, "allow_schema_override", False) and not _paths_equivalent(override, tmpl.schema)):
        raise ValueError(
            "Schema override is not allowed for this template. "
            f"template={tmpl.name}; bound_schema={tmpl.schema}; requested_schema={override}; "
            f"document_type={tmpl.document_type or '-'}; strict_schema={tmpl.strict_schema}. "
            "Use --allow-schema-override to override it explicitly, or remove --schema to use the manifest-bound schema."
        )
    return override or tmpl.schema


def _schema_override_active(args, tmpl) -> bool:
    override=getattr(args, "schema", None)
    return bool(override and tmpl.schema and getattr(args, "allow_schema_override", False) and not _paths_equivalent(override, tmpl.schema))


def _print_schema_override_warning(args, tmpl) -> None:
    if(_schema_override_active(args, tmpl)):
        print(
            "WARNING: schema override enabled; "
            f"template={tmpl.name}; bound_schema={tmpl.schema}; requested_schema={getattr(args, 'schema', None)}; "
            f"document_type={tmpl.document_type or '-'}; strict_schema={_strict_for_template(args, tmpl)}",
            file=sys.stderr,
        )


def _strict_for_template(args, tmpl) -> bool:
    return bool(getattr(args, "strict_schema", False) or getattr(tmpl, "strict_schema", False))


def _append_document_type_mismatch(doc, expected_type: str | None, context: str, schema_path: str | None = None) -> None:
    if(expected_type and doc.type_name and doc.type_name!=expected_type):
        schema_part=f"; schema={schema_path}" if(schema_path) else ""
        doc.diagnostics.append(Diagnostic(
            "error",
            "E_TEMPLATE_DOCUMENT_TYPE_MISMATCH",
            f"{context}: document_type mismatch; manifest/project expects {expected_type}, but the SLDL document declares {doc.type_name}{schema_part}. "
            "Fix the document header, choose a matching template, or update the manifest/project document_type binding."
        ))


def _check_template_path(path: Path, schema_path: str | None, strict_schema: bool, label: str, expected_document_type: str | None = None) -> bool:
    if(not schema_path):
        print(f"OK: {label} (no schema bound)")
        return True
    doc,source=load_and_analyze(path, schema_path)
    _append_document_type_mismatch(doc, expected_document_type, f"Template {label}", schema_path)
    if(doc.diagnostics):
        print_diagnostics(doc, source, path, True)
    print_warning_policy_note(doc, strict_schema)
    if(has_errors(doc, strict_schema)):
        return False
    print(f"OK: {label} --schema {schema_path}")
    return True


def _check_template_content(tmpl, schema_path: str | None, strict_schema: bool) -> bool:
    if(tmpl.source_path is not None):
        return _check_template_path(tmpl.source_path, schema_path, strict_schema, tmpl.name, tmpl.document_type)
    with tempfile.NamedTemporaryFile("w", suffix=".sldl", encoding="utf-8", delete=False) as tmp:
        tmp.write(tmpl.content)
        tmp_path=Path(tmp.name)
    try:
        return _check_template_path(tmp_path, schema_path, strict_schema, tmpl.name, tmpl.document_type)
    finally:
        try:
            tmp_path.unlink()
        except OSError:
            pass



def _template_reference_display_path(value: str) -> str:
    if(not value):
        return ""
    path=Path(value)
    if(path.is_absolute()):
        try:
            return os.path.relpath(path, Path.cwd())
        except ValueError:
            return str(path)
    return value


def _sha256_path(path: str | Path | None) -> str | None:
    if(path is None):
        return None
    value=Path(path)
    if(not value.exists() or not value.is_file()):
        return None
    digest=hashlib.sha256()
    with value.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _template_docs_output(template_dir: str | None, fmt: str, language: str = "en") -> str:
    items=list_templates(template_dir)
    display_items=[]
    for item in items:
        copied=dict(item)
        for key in ("source_path", "schema", "default_export_config", "default_latex_build_config", "manifest_path"):
            if(key in copied):
                copied[key]=_template_reference_display_path(str(copied.get(key) or ""))
        display_items.append(copied)
    source_manifest=""
    source_manifest_sha256=None
    for item in display_items:
        if(item.get("manifest_role")=="canonical" and item.get("manifest_path")):
            source_manifest=str(item.get("manifest_path"))
            break
    if(not source_manifest and display_items):
        source_manifest=str(display_items[0].get("manifest_path") or "")
    if(source_manifest):
        source_manifest_sha256=_sha256_path(source_manifest)
    if(fmt=="json"):
        payload={
            "config_type":"sldl.template_reference",
            "version":"1.0.14",
            "language":language,
            "source_manifest": source_manifest or None,
            "source_manifest_sha256": source_manifest_sha256,
            "templates":display_items,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)+"\n"
    if(language=="ja"):
        lines=["# SLDL Template Reference（日本語）", "", "同梱template manifestから生成したテンプレート一覧です。v1.0.14では、template referenceとdiagnostics referenceに加えて、reference indexとCLI help referenceもrelease checkで差分確認できます。", "", "| Name | Document type | Language | Schema | Role |", "|---|---|---|---|---|"]
    else:
        lines=["# SLDL Template Reference", "", "Generated from the bundled template manifest. In v1.0.14, release checks keep the template and diagnostics reference drift checks and also drift-check the reference index and CLI help reference.", "", "| Name | Document type | Language | Schema | Role |", "|---|---|---|---|---|"]
    for item in display_items:
        lines.append(f"| `{item['name']}` | `{item.get('document_type','')}` | `{item.get('language','')}` | `{item.get('schema','')}` | `{item.get('manifest_role','')}` |")
    lines.append("")
    lines.append("## コマンド" if(language=="ja") else "## Commands")
    lines.append("")
    lines.append("```bash")
    lines.append("python3 -S -m sldl_compiler.cli template list")
    lines.append("python3 -S -m sldl_compiler.cli template explain research_report_en --format markdown")
    lines.append("python3 -S -m sldl_compiler.cli template docs --format markdown --check docs/generated_template_reference.md")
    lines.append("python3 -S -m sldl_compiler.cli template project research_report_en --document-output examples/generated.sldl -o examples/generated_project.json --force")
    lines.append("```")
    return "\n".join(lines)+"\n"



def _diagnostics_docs_output(fmt: str, language: str = "en", root: str | None = None) -> str:
    reference=build_diagnostics_reference(root, language)
    if(fmt=="json"):
        return render_diagnostics_reference_json(reference)
    return render_diagnostics_reference_markdown(reference, language)


def command_diagnostics(args) -> int:
    if(args.diagnostics_command=="list"):
        reference=build_diagnostics_reference(args.root, getattr(args, "language", "en"))
        if(getattr(args, "json", False)):
            print(render_diagnostics_reference_json(reference), end="")
        else:
            for item in reference.get("codes", []):
                print(f"{item['code']}	{item['level']}	{item['category']}")
        return 0
    if(args.diagnostics_command=="docs"):
        output=_diagnostics_docs_output(args.format, getattr(args, "language", "en"), getattr(args, "root", None))
        if(getattr(args, "check", None)):
            target=Path(args.check)
            if(not target.exists()):
                print(f"Diagnostics reference target does not exist: {target}", file=sys.stderr)
                return 1
            current=target.read_text(encoding="utf-8")
            if(current!=output):
                print(f"DIAGNOSTICS DOCS OUT OF DATE: {target}", file=sys.stderr)
                return 1
            print(f"OK: {target} matches generated diagnostics docs")
            return 0
        if(args.output):
            _write_text_file(Path(args.output), output)
            print(f"Wrote: {args.output}")
        else:
            print(output, end="")
        return 0
    return 2


def _reference_check_or_write(output: str, args, label: str) -> int:
    if(getattr(args, "check", None)):
        target=Path(args.check)
        if(not target.exists()):
            print(f"{label} target does not exist: {target}", file=sys.stderr)
            return 1
        current=target.read_text(encoding="utf-8")
        if(current!=output):
            print(f"{label} OUT OF DATE: {target}", file=sys.stderr)
            return 1
        print(f"OK: {target} matches generated {label.lower()}")
        return 0
    if(getattr(args, "output", None)):
        _write_text_file(Path(args.output), output)
        print(f"Wrote: {args.output}")
    else:
        print(output, end="")
    return 0


def _reference_index_output(fmt: str, language: str = "en", root: str | None = None) -> str:
    index=build_reference_index(root, language)
    if(fmt=="json"):
        return render_reference_index_json(index)
    return render_reference_index_markdown(index, language)


def _cli_help_reference_output(fmt: str, language: str = "en") -> str:
    parser=build_arg_parser()
    reference=build_cli_help_reference(parser, language)
    if(fmt=="json"):
        return render_cli_help_reference_json(reference)
    return render_cli_help_reference_markdown(reference, language)


def _release_report_output(input_path: str, fmt: str, language: str = "en") -> str:
    report=build_release_report(input_path, language)
    if(fmt=="json"):
        return render_release_report_json(report)
    return render_release_report_markdown(report, language)


def command_reference(args) -> int:
    if(args.reference_command=="index"):
        output=_reference_index_output(args.format, getattr(args, "language", "en"), getattr(args, "root", None))
        return _reference_check_or_write(output, args, "REFERENCE INDEX")
    if(args.reference_command=="cli-help"):
        output=_cli_help_reference_output(args.format, getattr(args, "language", "en"))
        return _reference_check_or_write(output, args, "CLI HELP REFERENCE")
    return 2

def command_template(args) -> int:
    if(args.template_command=="list"):
        for item in list_templates(args.template_dir):
            schema=item.get("schema", "")
            strict="strict" if(item.get("strict_schema")) else ""
            role=item.get("manifest_role", "")
            print(f"{item['name']}\t{item['description']}\t{item['document_type']}\t{item['language']}\t{schema}\t{strict}\t{role}")
        return 0
    if(args.template_command=="docs"):
        try:
            output=_template_docs_output(args.template_dir, args.format, getattr(args, "language", "en"))
        except (KeyError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if(getattr(args, "check", None)):
            target=Path(args.check)
            if(not target.exists()):
                print(f"Template reference target does not exist: {target}", file=sys.stderr)
                return 1
            current=target.read_text(encoding="utf-8")
            if(current!=output):
                print(f"TEMPLATE DOCS OUT OF DATE: {target}", file=sys.stderr)
                return 1
            print(f"OK: {target} matches generated template docs")
            return 0
        if(args.output):
            _write_text_file(Path(args.output), output)
            print(f"Wrote: {args.output}")
        else:
            print(output, end="")
        return 0
    if(args.template_command=="explain"):
        try:
            fmt=getattr(args, "format", "text")
            if(getattr(args, "json", False)):
                fmt="json"
            info=template_info(args.name, args.template_dir)
            if(fmt=="json"):
                output=json.dumps(info, ensure_ascii=False, indent=2)+"\n"
            elif(fmt=="markdown"):
                output=template_info_markdown(args.name, args.template_dir)
            else:
                lines=[
                    f"# Template: {info['name']}",
                    f"description: {info['description']}",
                    f"document_type: {info['document_type'] or '-'}",
                    f"language: {info['language'] or '-'}",
                    f"source_path: {info['source_path'] or '-'}",
                    f"schema: {info['schema'] or '-'}",
                    f"default_export_config: {info['default_export_config'] or '-'}",
                    f"default_latex_build_config: {info['default_latex_build_config'] or '-'}",
                    f"strict_schema: {info['strict_schema']}",
                    f"manifest_path: {info['manifest_path'] or '-'}",
                    f"manifest_version: {info['manifest_version'] or '-'}",
                    f"manifest_role: {info['manifest_role'] or '-'}",
                ]
                output="\n".join(lines)+"\n"
        except (KeyError, FileNotFoundError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if(getattr(args, "output", None)):
            _write_text_file(Path(args.output), output)
            print(f"Wrote: {args.output}")
        else:
            print(output, end="")
        return 0
    if(args.template_command=="check"):
        try:
            tmpl=get_template(args.name, args.template_dir)
            schema_path=_schema_for_template(args, tmpl)
            _print_schema_override_warning(args, tmpl)
            strict_schema=_strict_for_template(args, tmpl)
        except (KeyError, FileNotFoundError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0 if(_check_template_content(tmpl, schema_path, strict_schema)) else 1
    if(args.template_command=="new"):
        try:
            if(args.schema and not args.name):
                tmpl=get_template_from_schema(args.schema, args.document_type)
                schema_path=args.schema
            else:
                if(not args.name):
                    print("Template name is required unless --schema is given.", file=sys.stderr)
                    return 2
                tmpl=get_template(args.name, args.template_dir)
                schema_path=_schema_for_template(args, tmpl)
                _print_schema_override_warning(args, tmpl)
            strict_schema=_strict_for_template(args, tmpl)
        except (KeyError, FileNotFoundError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
        output=tmpl.content
        if(args.output):
            out_path=Path(args.output)
            if(out_path.exists() and not args.force):
                print(f"File exists: {out_path}. Use --force to overwrite.", file=sys.stderr)
                return 1
            out_path.write_text(output, encoding="utf-8")
            print(f"Created: {out_path}")
            if(not _check_template_path(out_path, schema_path, strict_schema, str(out_path), tmpl.document_type)):
                return 1
        else:
            if(schema_path and not _check_template_content(tmpl, schema_path, strict_schema)):
                return 1
            print(output, end="")
        return 0
    if(args.template_command=="project"):
        return command_template_project(args)
    return 2

def _path_from_cwd(value: str | Path) -> Path:
    path=Path(value)
    return path if(path.is_absolute()) else (Path.cwd()/path).resolve()


def _project_relative_ref(project_output: Path, value: str | Path | None) -> str | None:
    if(value is None):
        return None
    value_path=_path_from_cwd(value)
    project_dir=_path_from_cwd(project_output).parent
    try:
        return os.path.relpath(value_path, project_dir)
    except ValueError:
        return str(value)


def _parse_format_list(value: str) -> list[str]:
    known={"markdown", "html", "latex", "pdf", "sldj", "json", "bibtex", "mermaid", "logic-markdown", "logic-mermaid"}
    formats=[]
    for item in value.replace(";", ",").split(","):
        fmt=item.strip()
        if(not fmt):
            continue
        if(fmt not in known):
            raise ValueError(f"Unsupported template project output format: {fmt}")
        if(fmt not in formats):
            formats.append(fmt)
    if(not formats):
        raise ValueError("At least one output format is required.")
    return formats


def _output_extension(fmt: str) -> str:
    return {
        "markdown": "md",
        "html": "html",
        "latex": "tex",
        "pdf": "pdf",
        "sldj": "sldj",
        "json": "json",
        "bibtex": "bib",
        "mermaid": "mmd",
        "logic-markdown": "logic.md",
        "logic-mermaid": "logic.mmd",
    }.get(fmt, fmt)


def _effective_template_project_refs(args, tmpl) -> tuple[str | None, str | None, str | None]:
    schema_ref=_schema_for_template(args, tmpl)
    export_config=getattr(args, "export_config", None) or getattr(tmpl, "default_export_config", None) or "examples/export_labels_ja.json"
    latex_build_config=getattr(args, "latex_build_config", None) or getattr(tmpl, "default_latex_build_config", None) or "examples/latex_build_platex_dvipdfmx_dry_run.json"
    return schema_ref, export_config, latex_build_config


def _make_template_project_config(args, tmpl) -> dict:
    project_output=Path(args.output)
    document_output=Path(args.document_output)
    document_ref=_project_relative_ref(project_output, document_output)
    doc_stem=document_output.stem
    build_dir=args.build_dir or f"../build/{project_output.stem}"
    formats=_parse_format_list(args.formats)
    schema_path,export_config_path,latex_build_config_path=_effective_template_project_refs(args, tmpl)
    outputs=[]
    for fmt in formats:
        if(fmt=="pdf"):
            out={
                "format": "pdf",
                "path": f"{build_dir}/{doc_stem}.pdf",
                "tex_path": f"{build_dir}/{doc_stem}_pdf.tex",
            }
        else:
            out={"format": fmt, "path": f"{build_dir}/{doc_stem}.{_output_extension(fmt)}"}
        outputs.append(out)

    config={
        "config_type": "sldl.project",
        "description": f"SLDL v1.0.14 project generated from template: {tmpl.name}",
        "version": "1.0.14",
        "output_dir": build_dir,
        "citation_style": args.citation_style,
        "toc": args.toc,
        "mermaid_mode": args.mermaid_mode,
        "latex": {
            "profile": args.latex_profile,
            "geometry": args.latex_geometry,
            "hyperref": True,
            "top_level": args.latex_top_level,
            "code_font_size": args.latex_code_font_size,
            "mermaid_mode": args.mermaid_mode,
        },
        "documents": [
            {
                "name": doc_stem,
                "input": document_ref,
                "template": tmpl.name,
                "template_source": _project_relative_ref(project_output, tmpl.source_path) if(tmpl.source_path is not None) else None,
                "template_manifest": _project_relative_ref(project_output, tmpl.manifest_path) if(tmpl.manifest_path is not None) else None,
                "template_manifest_role": tmpl.manifest_role,
                "template_schema": _project_relative_ref(project_output, schema_path) if(schema_path) else None,
                "template_export_config": _project_relative_ref(project_output, export_config_path) if(export_config_path) else None,
                "template_latex_build_config": _project_relative_ref(project_output, latex_build_config_path) if(latex_build_config_path) else None,
                "document_type": tmpl.document_type,
                "outputs": outputs,
            }
        ],
        "write_manifest": f"{build_dir}/sldl_build_manifest.json",
    }
    schema_ref=_project_relative_ref(project_output, schema_path) if(schema_path) else None
    if(schema_ref):
        config["schemas"]=[schema_ref]
    export_config_ref=_project_relative_ref(project_output, export_config_path) if(export_config_path) else None
    if(export_config_ref):
        config["export_config"]=export_config_ref
    latex_build_ref=_project_relative_ref(project_output, latex_build_config_path) if(latex_build_config_path) else None
    if(latex_build_ref):
        config["latex_build_config"]=latex_build_ref
    return config

def command_template_project(args) -> int:
    if(not args.output):
        print("Project output path is required. Use -o or --output.", file=sys.stderr)
        return 2
    if(not args.document_output):
        print("Document output path is required. Use --document-output.", file=sys.stderr)
        return 2
    try:
        tmpl=get_template(args.name, args.template_dir)
        schema_path=_schema_for_template(args, tmpl)
        _print_schema_override_warning(args, tmpl)
        strict_schema=_strict_for_template(args, tmpl)
        config=_make_template_project_config(args, tmpl)
    except (KeyError, FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    project_path=Path(args.output)
    document_path=Path(args.document_output)
    for path in (document_path, project_path):
        if(path.exists() and not args.force):
            print(f"File exists: {path}. Use --force to overwrite.", file=sys.stderr)
            return 1
    _write_text_file(document_path, tmpl.content)
    _write_text_file(project_path, json.dumps(config, ensure_ascii=False, indent=2)+"\n")
    print(f"Created: {document_path}")
    print(f"Created: {project_path}")
    if(not _check_template_path(document_path, schema_path, strict_schema, str(document_path))):
        return 1
    return 0


def command_bib(args) -> int:
    bib_path=Path(args.input)
    try:
        source=bib_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"Cannot read BibTeX file: {bib_path} ({exc})", file=sys.stderr)
        return 1
    entries,diagnostics=parse_bibtex(source)
    for diag in diagnostics:
        try:
            print(diag.format(source, str(bib_path)))
        except TypeError:
            print(diag.format())
    if(any(d.level=="error" for d in diagnostics)):
        return 1

    if(args.bib_command=="check"):
        print(f"OK: {bib_path} ({len(entries)} entries)")
        for entry in entries:
            print(f"{entry.key}\t@{entry.entry_type}\t->\t{reference_id_from_bibkey(entry.key)}")
        return 0

    if(args.bib_command=="import"):
        output=bibtex_to_sldl_fragment(entries, str(bib_path))
        if(args.output):
            Path(args.output).write_text(output, encoding="utf-8")
            print(f"Created: {args.output}")
        else:
            print(output, end="")
        return 0
    return 2


def _project_path(base_dir: Path, value: str | None) -> Path | None:
    if(value is None):
        return None
    path=Path(value)
    return path if(path.is_absolute()) else base_dir/path


def _project_schema_paths(base_dir: Path, config: dict, doc_cfg: dict) -> list[str]:
    values=[]
    for src in (config, doc_cfg):
        if("schema" in src): values.append(src["schema"])
        values.extend(src.get("schemas", []))
    return [str(_project_path(base_dir, str(v))) for v in values]


def _diagnostic_counts(doc) -> dict:
    return {
        "errors": sum(1 for d in doc.diagnostics if(d.level=="error")),
        "warnings": sum(1 for d in doc.diagnostics if(d.level=="warning")),
        "infos": sum(1 for d in doc.diagnostics if(d.level=="info")),
    }


def command_project(args) -> int:
    project_path=Path(args.project)
    base_dir=project_path.parent
    try:
        config=json.loads(project_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"Cannot read project file: {project_path} ({exc})", file=sys.stderr)
        return 1
    documents=config.get("documents")
    if(not isinstance(documents, list) or not documents):
        print("Project file must contain a non-empty documents list.", file=sys.stderr)
        return 1

    project_warnings_as_errors=bool(config.get("warnings_as_errors", False) or args.warnings_as_errors)
    manifest={"config_type": "sldl.build_manifest", "description": "SLDL project build manifest", "project": str(project_path), "version": config.get("version", "0.8"), "documents": []}
    failed=False
    for doc_cfg in documents:
        if(not isinstance(doc_cfg, dict) or "input" not in doc_cfg):
            print("Each project document must be an object with input.", file=sys.stderr)
            failed=True
            continue
        input_path=_project_path(base_dir, str(doc_cfg["input"]))
        assert input_path is not None
        schema_paths=_project_schema_paths(base_dir, config, doc_cfg)
        warnings_as_errors=bool(project_warnings_as_errors or doc_cfg.get("warnings_as_errors", False))
        doc,source=load_and_analyze(input_path, schema_paths)
        expected_doc_type=doc_cfg.get("document_type")
        if(isinstance(expected_doc_type, str) and expected_doc_type and doc.type_name!=expected_doc_type):
            doc.diagnostics.append(Diagnostic(
                "error",
                "E_PROJECT_DOCUMENT_TYPE_MISMATCH",
                f"Project document expects document_type {expected_doc_type}, but {input_path} declares {doc.type_name}"
            ))
        if(doc.diagnostics):
            print_diagnostics(doc, source, input_path, not args.no_source_context)
        print_warning_policy_note(doc, warnings_as_errors)
        template_meta=None
        if(doc_cfg.get("template") or doc_cfg.get("template_source") or doc_cfg.get("template_manifest")):
            template_meta={
                "name": doc_cfg.get("template"),
                "source": doc_cfg.get("template_source"),
                "manifest": doc_cfg.get("template_manifest"),
                "manifest_role": doc_cfg.get("template_manifest_role"),
                "declared_document_type": expected_doc_type,
                "schema": doc_cfg.get("template_schema") or (config.get("schemas", [None])[0] if(isinstance(config.get("schemas"), list) and config.get("schemas")) else config.get("schema")),
                "export_config": doc_cfg.get("template_export_config") or config.get("export_config"),
                "latex_build_config": doc_cfg.get("template_latex_build_config") or config.get("latex_build_config"),
            }
            for key,path_value in (("source", template_meta.get("source")), ("manifest", template_meta.get("manifest")), ("schema", template_meta.get("schema")), ("export_config", template_meta.get("export_config")), ("latex_build_config", template_meta.get("latex_build_config"))):
                if(isinstance(path_value, str) and path_value):
                    resolved=_project_path(base_dir, path_value)
                    digest=_sha256_path(resolved) if(resolved is not None) else None
                    if(digest):
                        template_meta[f"{key}_sha256"]=digest
        doc_result={
            "name": doc_cfg.get("name", input_path.stem),
            "input": str(input_path),
            "schemas": schema_paths,
            "document_type": doc.type_name,
            "template": template_meta,
            "diagnostics": [d.__dict__ for d in doc.diagnostics],
            "diagnostic_counts": _diagnostic_counts(doc),
            "outputs": [],
        }
        if(has_errors(doc, warnings_as_errors)):
            failed=True
            manifest["documents"].append(doc_result)
            continue
        print(f"OK: {input_path}")
        if(args.project_command=="build"):
            outputs=doc_cfg.get("outputs") or config.get("outputs") or []
            if(not outputs):
                output_dir=_project_path(base_dir, str(config.get("output_dir", "build")))
                outputs=[{"format":"sldj", "path": str((output_dir or Path("build"))/(input_path.stem+".sldj"))}]
            for out_cfg in outputs:
                fmt=str(out_cfg.get("format", "json"))
                out_path=_project_path(base_dir, str(out_cfg.get("path", f"build/{input_path.stem}.{fmt}")))
                citation_style=out_cfg.get("citation_style", doc_cfg.get("citation_style", config.get("citation_style")))
                export_config=out_cfg.get("export_config", doc_cfg.get("export_config", config.get("export_config")))
                export_config_path=_project_path(base_dir, export_config) if(export_config) else None
                toc=out_cfg.get("toc", doc_cfg.get("toc", config.get("toc")))
                try:
                    latex_options=_collect_latex_options(config, doc_cfg, out_cfg)
                    assert out_path is not None
                    if(fmt in {"pdf", "latex-pdf"}):
                        tex_value=out_cfg.get("tex_path") or out_cfg.get("latex_path") or str(out_path.with_suffix(".tex"))
                        tex_path=_project_path(base_dir, str(tex_value))
                        assert tex_path is not None
                        tex_output=export_document_output(doc, input_path, "latex", citation_style, str(export_config_path) if(export_config_path) else None, latex_options=latex_options, toc=toc)
                        _write_text_file(tex_path, tex_output)
                        build_config=out_cfg.get("latex_build_config", doc_cfg.get("latex_build_config", config.get("latex_build_config")))
                        build_config_path=_project_path(base_dir, build_config) if(build_config) else None
                        build_result=build_latex_pdf(tex_path, pdf_path=out_path, config_path=build_config_path)
                        output_info={"format": fmt, "path": str(out_path), "tex_path": str(tex_path), "latex_bytes": len(tex_output.encode("utf-8")), "latex_build": build_result.to_manifest()}
                        if(out_path.exists()):
                            output_info["bytes"]=out_path.stat().st_size
                            print(f"Wrote: {out_path}")
                        elif(build_result.success and build_result.dry_run):
                            print(f"Would write: {out_path}")
                        if(build_result.warning_count):
                            print(f"LATEX BUILD WARNINGS: {tex_path}: {build_result.warning_count}")
                        if(not build_result.success):
                            failed=True
                            output_info["error"]=build_result.error
                            print(f"LATEX BUILD FAILED: {tex_path}: {build_result.error}", file=sys.stderr)
                        doc_result["outputs"].append(output_info)
                    else:
                        output=export_document_output(doc, input_path, fmt, citation_style, str(export_config_path) if(export_config_path) else None, latex_options=latex_options, toc=toc)
                        _write_text_file(out_path, output)
                        print(f"Wrote: {out_path}")
                        doc_result["outputs"].append({"format": fmt, "path": str(out_path), "bytes": len(output.encode("utf-8"))})
                except Exception as exc:
                    failed=True
                    doc_result["outputs"].append({"format": fmt, "path": str(out_path), "error": str(exc)})
                    print(f"EXPORT FAILED: {input_path} -> {fmt}: {exc}", file=sys.stderr)
        manifest["documents"].append(doc_result)

    if(args.project_command=="build"):
        manifest_path=_project_path(base_dir, args.manifest or config.get("write_manifest") or str((Path(config.get("output_dir", "build"))/"sldl_build_manifest.json")))
        assert manifest_path is not None
        _write_text_file(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2)+"\n")
        print(f"Manifest: {manifest_path}")
    return 1 if(failed) else 0


def command_schema(args) -> int:
    schema_paths=[Path(p) for p in args.schema_files]
    diagnostics=check_schema_files(schema_paths)
    if(args.schema_command=="check"):
        for diag in diagnostics:
            print(diag.format())
        if(any(d.level=="error" for d in diagnostics)):
            return 1
        if(args.warnings_as_errors and any(d.level=="warning" for d in diagnostics)):
            print("FAILED: warnings treated as errors")
            return 1
        print(f"OK: {len(schema_paths)} schema file(s)")
        return 0
    if(any(d.level=="error" for d in diagnostics)):
        for diag in diagnostics:
            print(diag.format())
        return 1
    registry=load_schema_registry(schema_paths)
    if(args.schema_command=="list"):
        data=schema_summary(registry, [str(p) for p in schema_paths])
        if(args.json):
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print("Document types:")
            for name in data["document_types"]:
                print(f"  {name}")
            print("Node kinds:")
            for name in data["node_kinds"]:
                print(f"  {name}")
            print("Object classes:")
            for name in data["object_classes"]:
                print(f"  {name}")
            print("Type aliases:")
            for name in data.get("type_aliases", []):
                print(f"  {name}")
            print("Enum types:")
            for name in data.get("enum_types", []):
                print(f"  {name}")
            print("Function signatures:")
            for name in data.get("function_signatures", []):
                print(f"  {name}")
            print("Relation rules:")
            for name in data.get("relation_rules", []):
                print(f"  {name}")
        return 0
    if(args.schema_command=="explain"):
        output=schema_explain(registry, args.document_type)
        if(args.output):
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0
    return 2


def command_config(args) -> int:
    if(args.config_command=="list"):
        data={key: {"title": value["title"], "description": value["description"], "required": value["required"], "important": value["important"]} for key,value in SUPPORTED_CONFIG_TYPES.items()}
        if(args.json):
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            for key,value in data.items():
                print(f"{key}\t{value['title']}")
        return 0
    if(args.config_command=="check"):
        failed=False
        for file_name in args.files:
            diagnostics=check_config_file(file_name, expected_type=args.type, check_paths=not args.no_path_check)
            if(args.json):
                print(json.dumps({"file": file_name, "diagnostics": [d.to_dict() for d in diagnostics]}, ensure_ascii=False, indent=2))
            else:
                for diag in diagnostics:
                    print(diag.format(path=file_name))
                if(not diagnostics):
                    summary=config_summary(file_name)
                    print(f"OK: {file_name} ({summary.get('config_type')})")
                elif(not any(d.level=="error" for d in diagnostics)):
                    summary=config_summary(file_name)
                    print(f"OK: {file_name} ({summary.get('config_type')}) with {len(diagnostics)} warning(s)")
            if(any(d.level=="error" for d in diagnostics)):
                failed=True
            if(args.warnings_as_errors and any(d.level=="warning" for d in diagnostics)):
                failed=True
        if(failed and args.warnings_as_errors):
            print("FAILED: warnings treated as errors")
        return 1 if(failed) else 0
    if(args.config_command=="explain"):
        target=args.target
        path=Path(target)
        try:
            if(path.exists()):
                output=explain_config_file(path)
            else:
                output=explain_config_type(target)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        if(args.output):
            _write_text_file(Path(args.output), output)
            print(f"Wrote: {args.output}")
        else:
            print(output, end="")
        return 0
    if(args.config_command=="init"):
        try:
            data=init_config_data(args.type)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        output=json.dumps(data, ensure_ascii=False, indent=2)+"\n"
        if(args.output):
            out_path=Path(args.output)
            if(out_path.exists() and not args.force):
                print(f"File exists: {out_path}. Use --force to overwrite.", file=sys.stderr)
                return 1
            _write_text_file(out_path, output)
            print(f"Created: {out_path}")
        else:
            print(output, end="")
        return 0
    return 2


def command_latex(args) -> int:
    if(args.latex_command=="build"):
        result=build_latex_pdf(args.input, pdf_path=args.output, config_path=args.config, dry_run=args.dry_run)
        for step in result.steps:
            prefix="DRY-RUN" if(step.skipped) else "RUN"
            print(f"{prefix}: {step.name}: {' '.join(step.command)}")
            if(step.returncode not in (None, 0)):
                if(step.stdout_tail):
                    print(step.stdout_tail)
                if(step.stderr_tail):
                    print(step.stderr_tail, file=sys.stderr)
                if(step.error_summary):
                    print(f"ERROR SUMMARY: {step.error_summary}", file=sys.stderr)
        if(result.warning_count):
            print(f"LATEX WARNINGS: {result.warning_count}")
            for warning in result.warnings[:5]:
                print(f"WARNING: {warning}")
        if(result.success):
            if(result.dry_run):
                print(f"Would write: {result.pdf_path}")
            else:
                print(f"Wrote: {result.pdf_path}")
            return 0
        print(f"LATEX BUILD FAILED: {result.error}", file=sys.stderr)
        return 1
    return 2


def command_grammar(args) -> int:
    grammar_path=Path(__file__).resolve().parent.parent/"docs"/"sldl_language_reference.md"
    if(args.output): Path(args.output).write_text(grammar_path.read_text(encoding="utf-8"), encoding="utf-8")
    else: print(grammar_path.read_text(encoding="utf-8"))
    return 0


def command_quality(args) -> int:
    if(args.quality_command=="manifest"):
        diagnostics=validate_build_manifest(args.input)
        for diag in diagnostics:
            print(diag.format(path=args.input))
        if(any(d.level=="error" for d in diagnostics)):
            return 1
        if(args.warnings_as_errors and any(d.level=="warning" for d in diagnostics)):
            print("FAILED: warnings treated as errors")
            return 1
        print(f"OK: {args.input} (sldl.build_manifest)")
        return 0
    if(args.quality_command=="snapshot"):
        try:
            data=make_snapshot(args.files, base_dir=args.base_dir, description=args.description)
        except OSError as exc:
            print(str(exc), file=sys.stderr)
            return 1
        output=json.dumps(data, ensure_ascii=False, indent=2)+"\n"
        if(args.output):
            _write_text_file(Path(args.output), output)
            print(f"Wrote: {args.output}")
        else:
            print(output, end="")
        return 0
    if(args.quality_command=="snapshot-check"):
        diagnostics,details=check_snapshot(args.input, base_dir=args.base_dir)
        if(args.json):
            print(json.dumps({"input": args.input, "diagnostics": [d.to_dict() for d in diagnostics], "details": details}, ensure_ascii=False, indent=2))
        else:
            for diag in diagnostics:
                print(diag.format(path=args.input))
            if(not diagnostics):
                print(f"OK: {args.input} ({len(details.get('files', []))} file(s))")
        if(any(d.level=="error" for d in diagnostics)):
            return 1
        if(args.warnings_as_errors and any(d.level=="warning" for d in diagnostics)):
            print("FAILED: warnings treated as errors")
            return 1
        return 0
    if(args.quality_command=="report"):
        try:
            output=_release_report_output(args.input, args.format, getattr(args, "language", "en"))
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return _reference_check_or_write(output, args, "RELEASE REPORT")
    if(args.quality_command=="release"):
        target=args.targets or "examples/release_check.json"
        fail_on_warning=bool(getattr(args, "fail_on_warning", False))
        exit_code,manifest=run_release_check(target, args.manifest, args.warnings_as_errors or fail_on_warning)
        if(getattr(args, "summary_json", None)):
            summary_payload=build_release_summary(manifest)
            summary_path=Path(args.summary_json)
            summary_path.parent.mkdir(parents=True, exist_ok=True)
            summary_path.write_text(json.dumps(summary_payload, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
        if(args.json):
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
        else:
            for item in manifest.get("checks", []):
                status="OK" if(item.get("ok")) else "NG"
                print(f"{status}: {item.get('category')}: {item.get('name')}")
                if(not item.get("ok")):
                    for diag in item.get("diagnostics", []):
                        level=diag.get("level", "error").upper() if(isinstance(diag, dict)) else "ERROR"
                        code=diag.get("code", "") if(isinstance(diag, dict)) else ""
                        message=diag.get("message", str(diag)) if(isinstance(diag, dict)) else str(diag)
                        print(f"  {level} {code}: {message}")
            summary=manifest.get("summary", {})
            print(f"Release check: {summary.get('passed', 0)}/{summary.get('total', 0)} passed, {summary.get('failed', 0)} failed")
            if(args.manifest):
                print(f"Manifest: {args.manifest}")
            if(getattr(args, "summary_json", None)):
                print(f"Summary JSON: {args.summary_json}")
        return exit_code
    return 2


def build_arg_parser() -> argparse.ArgumentParser:
    parser=argparse.ArgumentParser(prog="sldlc", description="SLDL v1.0.14 compiler")
    sub=parser.add_subparsers(dest="command", required=True)
    p_check=sub.add_parser("check", help="check SLDL file"); p_check.add_argument("input"); p_check.add_argument("--schema", action="append"); p_check.add_argument("--warnings-as-errors", action="store_true"); p_check.add_argument("--no-source-context", action="store_true"); p_check.set_defaults(func=command_check)
    p_build=sub.add_parser("build", help="build JSON AST"); p_build.add_argument("input"); p_build.add_argument("-o","--output"); p_build.add_argument("--schema", action="append"); p_build.add_argument("--warnings-as-errors", action="store_true"); p_build.add_argument("--no-source-context", action="store_true"); p_build.set_defaults(func=command_build)
    p_export=sub.add_parser("export", help="export document")
    p_export.add_argument("input")
    p_export.add_argument("--format", choices=["json","markdown","html","latex","bibtex","mermaid","logic-markdown","logic-mermaid"], required=True)
    p_export.add_argument("-o", "--output")
    p_export.add_argument("--schema", action="append")
    p_export.add_argument("--citation-style", choices=["numeric","ieee","apa","author-year"], help="citation/reference style for markdown/html export")
    p_export.add_argument("--export-config", help="JSON file for language-dependent export labels")
    p_export.add_argument("--latex-profile", default=None, help="LaTeX profile, e.g. platex-jsarticle, platex-jreport, uplatex-jsarticle, lualatex-ltjsarticle")
    p_export.add_argument("--latex-class", default=None, help="Override LaTeX document class")
    p_export.add_argument("--latex-class-options", default=None, help="Override LaTeX document class options")
    p_export.add_argument("--latex-geometry", default=None, help="geometry package options, e.g. margin=25mm")
    p_export.add_argument("--latex-hyperref", action=argparse.BooleanOptionalAction, default=None, help="Enable or disable hyperref in LaTeX output")
    p_export.add_argument("--latex-sloppy", action=argparse.BooleanOptionalAction, default=None, help="Enable or disable overfull-box mitigation in LaTeX output")
    p_export.add_argument("--latex-table-font", choices=["none", "normalsize", "small", "footnotesize", "scriptsize"], default=None, help="Font size for generated longtable blocks")
    p_export.add_argument("--latex-top-level", choices=["section", "chapter"], default=None, help="Render top-level SLDL sections as LaTeX sections or chapters")
    p_export.add_argument("--latex-code-environment", choices=["lstlisting", "verbatim"], default=None, help="Environment used for CodeBlock, Chart, and Flowchart source blocks")
    p_export.add_argument("--latex-figure-width", default=None, help="Default width for Figure includegraphics, e.g. 0.9\\linewidth")
    p_export.add_argument("--latex-code-font-size", choices=["none", "normalsize", "small", "footnotesize", "scriptsize"], default=None, help="Font size for generated lstlisting blocks")
    p_export.add_argument("--mermaid-mode", choices=["code", "placeholder", "external-image"], default=None, help="LaTeX rendering mode for Chart/Flowchart Mermaid diagrams")
    p_export.add_argument("--toc", action=argparse.BooleanOptionalAction, default=None, help="Enable or disable a generated table of contents for supported export formats")
    p_export.add_argument("--logic-source-edge-direction", choices=["reference-to-evidence","evidence-to-reference"], default="reference-to-evidence", help="direction used when displaying source/cite edges in logic exports")
    p_export.add_argument("--warnings-as-errors", action="store_true")
    p_export.add_argument("--no-source-context", action="store_true")
    p_export.set_defaults(func=command_export)
    p_logic=sub.add_parser("logic", help="Inspect SLDL logic graph and consistency")
    logic_sub=p_logic.add_subparsers(dest="logic_command", required=True)
    p_logic_report=logic_sub.add_parser("report", help="write a Markdown logic report")
    p_logic_report.add_argument("input")
    p_logic_report.add_argument("-o", "--output")
    p_logic_report.add_argument("--schema")
    p_logic_report.add_argument("--source-edge-direction", choices=["reference-to-evidence","evidence-to-reference"], default="reference-to-evidence", help="direction used when displaying source/cite edges")
    p_logic_report.add_argument("--warnings-as-errors", action="store_true")
    p_logic_report.add_argument("--no-source-context", action="store_true")
    p_logic_report.set_defaults(func=command_logic)
    p_logic_graph=logic_sub.add_parser("graph", help="write a Mermaid logic graph")
    p_logic_graph.add_argument("input")
    p_logic_graph.add_argument("-o", "--output")
    p_logic_graph.add_argument("--schema")
    p_logic_graph.add_argument("--source-edge-direction", choices=["reference-to-evidence","evidence-to-reference"], default="reference-to-evidence", help="direction used when displaying source/cite edges")
    p_logic_graph.add_argument("--warnings-as-errors", action="store_true")
    p_logic_graph.add_argument("--no-source-context", action="store_true")
    p_logic_graph.set_defaults(func=command_logic)

    p_format=sub.add_parser("format", help="format SLDL file"); p_format.add_argument("input"); p_format.add_argument("-o","--output"); p_format.add_argument("--in-place", action="store_true"); p_format.add_argument("--check", action="store_true"); p_format.add_argument("--indent", type=int, default=4); p_format.set_defaults(func=command_format)
    p_diagnostics=sub.add_parser("diagnostics", help="list and generate SLDL diagnostics code references"); diagnostics_sub=p_diagnostics.add_subparsers(dest="diagnostics_command", required=True)
    p_diagnostics_list=diagnostics_sub.add_parser("list", help="list known diagnostics codes found in compiler sources"); p_diagnostics_list.add_argument("--root", help="project root used for source scanning"); p_diagnostics_list.add_argument("--language", choices=["en", "ja"], default="en"); p_diagnostics_list.add_argument("--json", action="store_true"); p_diagnostics_list.set_defaults(func=command_diagnostics)
    p_diagnostics_docs=diagnostics_sub.add_parser("docs", help="generate or check diagnostics reference documents"); p_diagnostics_docs.add_argument("--root", help="project root used for source scanning"); p_diagnostics_docs.add_argument("--format", choices=["markdown", "json"], default="markdown"); p_diagnostics_docs.add_argument("--language", choices=["en", "ja"], default="en"); p_diagnostics_docs.add_argument("--check", help="compare generated output with an existing static file and fail if it differs"); p_diagnostics_docs.add_argument("-o", "--output"); p_diagnostics_docs.set_defaults(func=command_diagnostics)
    p_reference=sub.add_parser("reference", help="generate and check generated reference documents"); reference_sub=p_reference.add_subparsers(dest="reference_command", required=True)
    p_reference_index=reference_sub.add_parser("index", help="generate or check the generated reference index"); p_reference_index.add_argument("--root", help="project root used for hashing referenced files"); p_reference_index.add_argument("--format", choices=["markdown", "json"], default="markdown"); p_reference_index.add_argument("--language", choices=["en", "ja"], default="en"); p_reference_index.add_argument("--check", help="compare generated output with an existing static file and fail if it differs"); p_reference_index.add_argument("-o", "--output"); p_reference_index.set_defaults(func=command_reference)
    p_reference_help=reference_sub.add_parser("cli-help", help="generate or check the static CLI help reference"); p_reference_help.add_argument("--format", choices=["markdown", "json"], default="markdown"); p_reference_help.add_argument("--language", choices=["en", "ja"], default="en"); p_reference_help.add_argument("--check", help="compare generated output with an existing static file and fail if it differs"); p_reference_help.add_argument("-o", "--output"); p_reference_help.set_defaults(func=command_reference)
    p_template=sub.add_parser("template", help="work with file-based templates"); template_sub=p_template.add_subparsers(dest="template_command", required=True)
    p_template_list=template_sub.add_parser("list", help="list templates"); p_template_list.add_argument("--template-dir"); p_template_list.set_defaults(func=command_template)
    p_template_docs=template_sub.add_parser("docs", help="generate or check a template reference document from the manifest"); p_template_docs.add_argument("--template-dir"); p_template_docs.add_argument("--format", choices=["markdown", "json"], default="markdown"); p_template_docs.add_argument("--language", choices=["en", "ja"], default="en"); p_template_docs.add_argument("--check", help="compare generated output with an existing static file and fail if it differs"); p_template_docs.add_argument("-o", "--output"); p_template_docs.set_defaults(func=command_template)
    p_template_explain=template_sub.add_parser("explain", help="explain a template and its bound configuration files"); p_template_explain.add_argument("name", help="template name"); p_template_explain.add_argument("--template-dir"); p_template_explain.add_argument("--format", choices=["text", "markdown", "json"], default="text"); p_template_explain.add_argument("--json", action="store_true", help="deprecated alias for --format json"); p_template_explain.add_argument("-o", "--output", help="write explanation to a file"); p_template_explain.set_defaults(func=command_template)
    p_template_check=template_sub.add_parser("check", help="check a template against its bound schema"); p_template_check.add_argument("name", help="template name"); p_template_check.add_argument("--template-dir"); p_template_check.add_argument("--schema", help="schema override; requires --allow-schema-override when the template already binds a schema"); p_template_check.add_argument("--strict-schema", action="store_true", help="treat schema warnings as errors"); p_template_check.add_argument("--allow-schema-override", action="store_true", help="allow overriding the schema bound by the template manifest"); p_template_check.set_defaults(func=command_template)
    p_template_new=template_sub.add_parser("new", help="create a new file from a template"); p_template_new.add_argument("name", nargs="?"); p_template_new.add_argument("-o","--output"); p_template_new.add_argument("--force", action="store_true"); p_template_new.add_argument("--template-dir"); p_template_new.add_argument("--schema", help="create from schema when name is omitted, or override a named template schema when allowed"); p_template_new.add_argument("--document-type", help="document_types.<TypeName> to use when a schema contains multiple document types"); p_template_new.add_argument("--strict-schema", action="store_true", help="treat schema warnings as errors during generation check"); p_template_new.add_argument("--allow-schema-override", action="store_true", help="allow overriding the schema bound by the template manifest"); p_template_new.set_defaults(func=command_template)
    p_template_project=template_sub.add_parser("project", help="create a document and project JSON from a template")
    p_template_project.add_argument("name", help="template name")
    p_template_project.add_argument("-o", "--output", required=True, help="project JSON output path")
    p_template_project.add_argument("--document-output", required=True, help="SLDL document output path")
    p_template_project.add_argument("--force", action="store_true")
    p_template_project.add_argument("--template-dir")
    p_template_project.add_argument("--schema", default=None, help="schema JSON override; by default the template manifest binding is used")
    p_template_project.add_argument("--export-config", default=None, help="export label config override; by default the template manifest value is used")
    p_template_project.add_argument("--latex-build-config", default=None, help="LaTeX build config override; by default the template manifest value is used")
    p_template_project.add_argument("--strict-schema", action="store_true", help="treat schema warnings as errors during generation check")
    p_template_project.add_argument("--allow-schema-override", action="store_true", help="allow overriding the schema bound by the template manifest")
    p_template_project.add_argument("--build-dir", default=None, help="generated output directory used inside the project JSON")
    p_template_project.add_argument("--formats", default="markdown,html,latex,pdf", help="comma-separated output formats")
    p_template_project.add_argument("--citation-style", default="author-year")
    p_template_project.add_argument("--toc", action=argparse.BooleanOptionalAction, default=True)
    p_template_project.add_argument("--latex-profile", default="platex-jreport")
    p_template_project.add_argument("--latex-geometry", default="margin=25mm")
    p_template_project.add_argument("--latex-top-level", choices=["section", "chapter"], default="chapter")
    p_template_project.add_argument("--latex-code-font-size", choices=["none", "normalsize", "small", "footnotesize", "scriptsize"], default="small")
    p_template_project.add_argument("--mermaid-mode", choices=["code", "placeholder", "external-image"], default="placeholder")
    p_template_project.set_defaults(func=command_template)
    p_bib=sub.add_parser("bib", help="work with BibTeX references"); bib_sub=p_bib.add_subparsers(dest="bib_command", required=True)
    p_bib_check=bib_sub.add_parser("check", help="parse and check a BibTeX file"); p_bib_check.add_argument("input"); p_bib_check.set_defaults(func=command_bib)
    p_bib_import=bib_sub.add_parser("import", help="convert a BibTeX file to SLDL reference blocks"); p_bib_import.add_argument("input"); p_bib_import.add_argument("-o","--output"); p_bib_import.set_defaults(func=command_bib)
    p_schema=sub.add_parser("schema", help="check and inspect schema files"); schema_sub=p_schema.add_subparsers(dest="schema_command", required=True)
    p_schema_check=schema_sub.add_parser("check", help="validate schema JSON files"); p_schema_check.add_argument("schema_files", nargs="+"); p_schema_check.add_argument("--warnings-as-errors", action="store_true"); p_schema_check.set_defaults(func=command_schema)
    p_schema_list=schema_sub.add_parser("list", help="list document types, nodes, and object classes after schema merge"); p_schema_list.add_argument("schema_files", nargs="*"); p_schema_list.add_argument("--json", action="store_true"); p_schema_list.set_defaults(func=command_schema)
    p_schema_explain=schema_sub.add_parser("explain", help="explain one document type from schema"); p_schema_explain.add_argument("schema_files", nargs="*"); p_schema_explain.add_argument("--document-type"); p_schema_explain.add_argument("-o","--output"); p_schema_explain.set_defaults(func=command_schema)
    p_project=sub.add_parser("project", help="check or build documents from a project JSON file"); project_sub=p_project.add_subparsers(dest="project_command", required=True)
    p_project_check=project_sub.add_parser("check", help="check all documents in a project"); p_project_check.add_argument("project"); p_project_check.add_argument("--warnings-as-errors", action="store_true"); p_project_check.add_argument("--no-source-context", action="store_true"); p_project_check.set_defaults(func=command_project)
    p_project_build=project_sub.add_parser("build", help="check and export all documents in a project"); p_project_build.add_argument("project"); p_project_build.add_argument("--manifest", help="override output manifest path"); p_project_build.add_argument("--warnings-as-errors", action="store_true"); p_project_build.add_argument("--no-source-context", action="store_true"); p_project_build.set_defaults(func=command_project)
    p_config=sub.add_parser("config", help="check, explain, and create SLDL JSON config files"); config_sub=p_config.add_subparsers(dest="config_command", required=True)
    p_config_list=config_sub.add_parser("list", help="list supported config_type values"); p_config_list.add_argument("--json", action="store_true"); p_config_list.set_defaults(func=command_config)
    p_config_check=config_sub.add_parser("check", help="validate one or more SLDL config JSON files"); p_config_check.add_argument("files", nargs="+"); p_config_check.add_argument("--type", choices=sorted(SUPPORTED_CONFIG_TYPES.keys()), help="expected config_type"); p_config_check.add_argument("--warnings-as-errors", action="store_true"); p_config_check.add_argument("--no-path-check", action="store_true", help="do not warn when referenced files do not exist"); p_config_check.add_argument("--json", action="store_true"); p_config_check.set_defaults(func=command_config)
    p_config_explain=config_sub.add_parser("explain", help="explain a config type or config JSON file"); p_config_explain.add_argument("target", help="config_type value or JSON file path"); p_config_explain.add_argument("-o", "--output"); p_config_explain.set_defaults(func=command_config)
    p_config_init=config_sub.add_parser("init", help="write a minimal config JSON template"); p_config_init.add_argument("type", choices=sorted(SUPPORTED_CONFIG_TYPES.keys())); p_config_init.add_argument("-o", "--output"); p_config_init.add_argument("--force", action="store_true"); p_config_init.set_defaults(func=command_config)
    p_latex=sub.add_parser("latex", help="build LaTeX outputs such as PDF"); latex_sub=p_latex.add_subparsers(dest="latex_command", required=True)
    p_latex_build=latex_sub.add_parser("build", help="run a configured LaTeX-to-PDF build pipeline")
    p_latex_build.add_argument("input", help="input .tex file")
    p_latex_build.add_argument("-o", "--output", help="output PDF path")
    p_latex_build.add_argument("--config", help="external JSON build configuration")
    p_latex_build.add_argument("--dry-run", action="store_true", help="print commands without executing them")
    p_latex_build.set_defaults(func=command_latex)
    p_quality=sub.add_parser("quality", help="run quality, regression, and release checks"); quality_sub=p_quality.add_subparsers(dest="quality_command", required=True)
    p_quality_manifest=quality_sub.add_parser("manifest", help="validate a project build manifest")
    p_quality_manifest.add_argument("input")
    p_quality_manifest.add_argument("--warnings-as-errors", action="store_true")
    p_quality_manifest.set_defaults(func=command_quality)
    p_quality_snapshot=quality_sub.add_parser("snapshot", help="write a SHA-256 snapshot for golden files")
    p_quality_snapshot.add_argument("files", nargs="+")
    p_quality_snapshot.add_argument("-o", "--output")
    p_quality_snapshot.add_argument("--base-dir", default=".")
    p_quality_snapshot.add_argument("--description")
    p_quality_snapshot.set_defaults(func=command_quality)
    p_quality_snapshot_check=quality_sub.add_parser("snapshot-check", help="verify files against a SHA-256 snapshot")
    p_quality_snapshot_check.add_argument("input")
    p_quality_snapshot_check.add_argument("--base-dir")
    p_quality_snapshot_check.add_argument("--warnings-as-errors", action="store_true")
    p_quality_snapshot_check.add_argument("--json", action="store_true")
    p_quality_snapshot_check.set_defaults(func=command_quality)
    p_quality_report=quality_sub.add_parser("report", help="generate a Markdown or JSON report from an sldl.release_manifest")
    p_quality_report.add_argument("input", help="input sldl.release_manifest JSON")
    p_quality_report.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p_quality_report.add_argument("--language", choices=["en", "ja"], default="en")
    p_quality_report.add_argument("-o", "--output")
    p_quality_report.add_argument("--check", help="compare generated report with an existing file")
    p_quality_report.set_defaults(func=command_quality)
    p_quality_release=quality_sub.add_parser("release", help="run release quality checks declared by a release-check JSON")
    p_quality_release.add_argument("--targets", required=True, help="sldl.release_check JSON target file")
    p_quality_release.add_argument("--manifest", help="write an sldl.release_manifest JSON")
    p_quality_release.add_argument("--warnings-as-errors", action="store_true")
    p_quality_release.add_argument("--fail-on-warning", action="store_true", help="treat release warnings as failures; CI-friendly alias for warning-sensitive release gates")
    p_quality_release.add_argument("--summary-json", help="write a compact sldl.release_summary JSON file for CI systems")
    p_quality_release.add_argument("--json", action="store_true")
    p_quality_release.set_defaults(func=command_quality)
    p_grammar=sub.add_parser("grammar", help="print implemented EBNF grammar"); p_grammar.add_argument("-o","--output"); p_grammar.set_defaults(func=command_grammar)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser=build_arg_parser(); args=parser.parse_args(argv); return args.func(args)

if(__name__=="__main__"):
    raise SystemExit(main())
