from __future__ import annotations

from dataclasses import dataclass
import re
from pathlib import Path
from typing import Any

from .ast_nodes import DocumentAst, Node, Value
from .export_support import (
    ExportContext,
    chart_mermaid,
    citation_ids,
    flowchart_mermaid,
    is_reference_section,
    node_caption,
    ordered_references,
    plain,
    reference_text,
    cross_reference_ids_for_display,
    meta_bool,
    replace_xref_markers,
)


_LATEX_REPLACEMENTS=[
    ("\\", r"\textbackslash{}"),
    ("&", r"\&"),
    ("%", r"\%"),
    ("$", r"\$"),
    ("#", r"\#"),
    ("_", r"\_"),
    ("{", r"\{"),
    ("}", r"\}"),
    ("~", r"\textasciitilde{}"),
    ("^", r"\textasciicircum{}"),
]


@dataclass(frozen=True)
class LatexProfile:
    name: str
    engine: str
    document_class: str
    class_options: str


_LATEX_PROFILES={
    "default": LatexProfile("default", "platex", "jsarticle", "12pt,a4paper,dvipdfmx"),
    "platex": LatexProfile("platex", "platex", "jsarticle", "12pt,a4paper,dvipdfmx"),
    "platex-jsarticle": LatexProfile("platex-jsarticle", "platex", "jsarticle", "12pt,a4paper,dvipdfmx"),
    "platex-jreport": LatexProfile("platex-jreport", "platex", "jreport", "12pt,a4j,dvipdfmx"),
    "uplatex": LatexProfile("uplatex", "uplatex", "jsarticle", "12pt,a4paper,dvipdfmx,uplatex"),
    "uplatex-jsarticle": LatexProfile("uplatex-jsarticle", "uplatex", "jsarticle", "12pt,a4paper,dvipdfmx,uplatex"),
    "uplatex-jreport": LatexProfile("uplatex-jreport", "uplatex", "jreport", "12pt,a4j,dvipdfmx,uplatex"),
    "lualatex": LatexProfile("lualatex", "lualatex", "ltjsarticle", "12pt,a4paper"),
    "lualatex-ltjsarticle": LatexProfile("lualatex-ltjsarticle", "lualatex", "ltjsarticle", "12pt,a4paper"),
    "xelatex": LatexProfile("xelatex", "xelatex", "bxjsarticle", "12pt,a4paper,xelatex"),
    "bxjsarticle": LatexProfile("bxjsarticle", "platex", "bxjsarticle", "12pt,a4paper,dvipdfmx"),
}


@dataclass
class LatexRenderOptions:
    profile_name: str
    engine: str
    document_class: str
    class_options: str
    geometry: str
    hyperref: bool
    sloppy: bool
    table_font: str
    top_level: str
    code_environment: str
    figure_width: str
    code_font_size: str
    toc: bool
    mermaid_mode: str


def export_latex(
    doc: DocumentAst,
    citation_style: str | None = None,
    export_config_path: str | None = None,
    base_path: str | None = None,
    latex_options: dict[str, Any] | None = None,
) -> str:
    ctx=ExportContext.build(doc, citation_style=citation_style, export_config_path=export_config_path, base_path=base_path)
    opts=_latex_render_options(doc, latex_options)
    title="Untitled"
    if(doc.meta and "title" in doc.meta.fields):
        title=plain(doc.meta.fields["title"])

    lines=[]
    lines.extend(_latex_preamble(ctx, doc, title, opts))
    lines.append(r"\begin{document}")
    lines.append(r"\maketitle")
    lines.append("")

    if(doc.meta):
        _meta_to_latex(ctx, doc, lines)

    if(opts.toc):
        lines.append(r"\tableofcontents")
        lines.append(r"\clearpage")
        lines.append("")

    for node in doc.children:
        _node_to_latex(ctx, node, lines, level=1, opts=opts)

    _references_to_latex(ctx, lines, opts)

    lines.append(r"\end{document}")
    return "\n".join(lines).rstrip()+"\n"


def _latex_render_options(doc: DocumentAst, overrides: dict[str, Any] | None = None) -> LatexRenderOptions:
    profile_name=(
        _option_string(doc, overrides, "profile", "latex_profile")
        or _option_string(doc, overrides, "engine", "latex_engine")
        or "default"
    )
    normalized_profile=profile_name.strip().lower()
    profile=_LATEX_PROFILES.get(normalized_profile, _LATEX_PROFILES["default"])

    engine=_option_string(doc, overrides, "engine", "latex_engine") or profile.engine
    document_class=_option_string(doc, overrides, "document_class", "latex_class") or profile.document_class
    class_options=_option_string(doc, overrides, "class_options", "latex_class_options") or profile.class_options
    geometry=_option_string(doc, overrides, "geometry", "latex_geometry") or ""
    hyperref=_option_bool(doc, overrides, "hyperref", "latex_hyperref", default=False)
    sloppy=_option_bool(doc, overrides, "sloppy", "latex_sloppy", default=True)
    table_font=_latex_font_size(_option_string(doc, overrides, "table_font", "latex_table_font") or "small")
    top_level=(_option_string(doc, overrides, "top_level", "latex_top_level") or "section").strip().lower()
    if(top_level not in {"section", "chapter"}):
        top_level="section"
    code_environment=(_option_string(doc, overrides, "code_environment", "latex_code_environment") or "lstlisting").strip().lower()
    if(code_environment not in {"lstlisting", "verbatim"}):
        code_environment="lstlisting"
    figure_width=_latex_dimension(_option_string(doc, overrides, "figure_width", "latex_figure_width") or r"0.9\linewidth", r"0.9\linewidth")
    code_font_size=_latex_font_size(_option_string(doc, overrides, "code_font_size", "latex_code_font_size") or "footnotesize")
    toc=_option_bool(doc, overrides, "toc", "toc", default=meta_bool(doc, ("export_toc", "table_of_contents"), False))
    mermaid_mode=_normalize_mermaid_mode(_option_string(doc, overrides, "mermaid_mode", "mermaid_mode") or _option_string(doc, overrides, "mermaid_mode", "latex_mermaid_mode") or "code")

    return LatexRenderOptions(
        profile_name=profile.name,
        engine=_latex_command_name(engine, profile.engine),
        document_class=document_class,
        class_options=class_options,
        geometry=geometry,
        hyperref=hyperref,
        sloppy=sloppy,
        table_font=table_font,
        top_level=top_level,
        code_environment=code_environment,
        figure_width=figure_width,
        code_font_size=code_font_size,
        toc=toc,
        mermaid_mode=mermaid_mode,
    )


def _option_string(doc: DocumentAst, overrides: dict[str, Any] | None, override_key: str, meta_key: str) -> str | None:
    if(overrides and override_key in overrides and overrides[override_key] is not None):
        value=str(overrides[override_key]).strip()
        return value or None
    if(doc.meta and meta_key in doc.meta.fields):
        value=plain(doc.meta.fields[meta_key]).strip()
        return value or None
    return None


def _option_bool(doc: DocumentAst, overrides: dict[str, Any] | None, override_key: str, meta_key: str, default: bool) -> bool:
    if(overrides and override_key in overrides and overrides[override_key] is not None):
        return _truthy(overrides[override_key], default)
    if(doc.meta and meta_key in doc.meta.fields):
        return _value_bool(doc.meta.fields[meta_key], default)
    return default


def _truthy(value: Any, default: bool = False) -> bool:
    if(isinstance(value, bool)):
        return value
    text=str(value).strip().lower()
    if(text in {"1", "true", "yes", "on", "enable", "enabled"}):
        return True
    if(text in {"0", "false", "no", "off", "disable", "disabled"}):
        return False
    return default


def _value_bool(value: Value, default: bool) -> bool:
    if(value.kind=="Bool"):
        return bool(value.value)
    return _truthy(plain(value), default)


def _latex_preamble(ctx: ExportContext, doc: DocumentAst, title: str, opts: LatexRenderOptions) -> list[str]:
    author=plain(doc.meta.fields["author"]) if(doc.meta and "author" in doc.meta.fields) else ""
    if(doc.meta and "date" in doc.meta.fields):
        date_latex=escape_latex(plain(doc.meta.fields["date"]))
    else:
        date_latex=r"\today"

    lines=[
        f"% Generated by SLDL compiler LaTeX exporter",
        f"% LaTeX profile: {opts.profile_name}; engine: {opts.engine}",
        f"\\documentclass[{_latex_class_options(opts.class_options)}]{{{_latex_command_name(opts.document_class, 'jsarticle')}}}",
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage{booktabs}",
        r"\usepackage{longtable}",
        r"\usepackage{array}",
        r"\usepackage{graphicx}",
        r"\usepackage{listings}",
        r"\usepackage[hyphens]{url}",
        r"\providecommand{\phantomsection}{}",
    ]
    if(opts.engine in {"platex", "uplatex"}):
        lines.append(r"\usepackage[dvipdfmx]{xcolor}")
    else:
        lines.append(r"\usepackage{xcolor}")
    geometry=_latex_geometry_options(opts.geometry)
    if(geometry):
        lines.append(f"\\usepackage[{geometry}]{{geometry}}")
    lines.extend(_hyperref_lines(opts))
    if(opts.sloppy):
        lines.extend([
            r"\emergencystretch=3em",
            r"\Urlmuskip=0mu plus 1mu\relax",
            r"\AtBeginDocument{\sloppy}",
        ])
    lines.extend([
        r"\lstset{",
        f"  basicstyle=\\ttfamily{opts.code_font_size},",
        r"  breaklines=true,",
        r"  breakatwhitespace=false,",
        r"  breakindent=0pt,",
        r"  breakautoindent=false,",
        r"  columns=fullflexible,",
        r"  keepspaces=true,",
        r"  showstringspaces=false,",
        r"  postbreak=\mbox{\textcolor{black}{$\hookrightarrow$}\space}",
        r"}",
        f"\\renewcommand{{\\figurename}}{{{escape_latex(ctx.label('figure', 'Figure'))}}}",
        f"\\renewcommand{{\\tablename}}{{{escape_latex(ctx.label('table', 'Table'))}}}",
        f"\\renewcommand{{\\lstlistingname}}{{{escape_latex(ctx.label('listing', 'Listing'))}}}",
        f"\\title{{{escape_latex(title)}}}",
        f"\\author{{{escape_latex(author)}}}",
        f"\\date{{{date_latex}}}",
    ])
    if(doc.meta and "latex_preamble" in doc.meta.fields):
        lines.extend(_raw_preamble_lines(doc.meta.fields["latex_preamble"]))
    return lines


def _hyperref_lines(opts: LatexRenderOptions) -> list[str]:
    if(not opts.hyperref):
        return []
    engine=opts.engine.lower()
    class_options=opts.class_options.lower()
    if(engine=="platex"):
        # pxjahyper reports an error when hyperref's unicode mode is used on
        # the pTeX engine.  pLaTeX + dvipdfmx therefore intentionally omits
        # the unicode option; upLaTeX can still use it below.
        return [
            r"\usepackage[dvipdfmx]{hyperref}",
            r"\usepackage{pxjahyper}",
            r"\hypersetup{colorlinks=false,pdfborder={0 0 0}}",
        ]
    if(engine=="uplatex"):
        return [
            r"\usepackage[dvipdfmx,unicode]{hyperref}",
            r"\usepackage{pxjahyper}",
            r"\hypersetup{colorlinks=false,pdfborder={0 0 0}}",
        ]
    if("dvipdfmx" in class_options):
        return [
            r"\usepackage[dvipdfmx]{hyperref}",
            r"\hypersetup{colorlinks=false,pdfborder={0 0 0}}",
        ]
    return [
        r"\usepackage[unicode]{hyperref}",
        r"\hypersetup{colorlinks=false,pdfborder={0 0 0}}",
    ]


def _raw_preamble_lines(value: Value) -> list[str]:
    if(value.kind=="List"):
        return [plain(item) for item in value.value if(plain(item).strip())]
    text=plain(value)
    if(not text.strip()):
        return []
    return text.splitlines()


def _meta_to_latex(ctx: ExportContext, doc: DocumentAst, lines: list[str]) -> None:
    meta=[]
    if("version" in doc.meta.fields):
        meta.append((ctx.label("version", "Version"), plain(doc.meta.fields["version"])))
    if(not meta):
        return
    lines.append(r"\begin{description}")
    for key,value in meta:
        lines.append(f"\\item[{escape_latex(key)}] {escape_latex(value)}")
    lines.append(r"\end{description}")
    lines.append("")


def _node_to_latex(ctx: ExportContext, node: Node, lines: list[str], level: int, opts: LatexRenderOptions) -> None:
    if(node.kind=="Section"):
        if(is_reference_section(node)):
            return
        title=plain(node.fields.get("title")) if("title" in node.fields) else (node.id or ctx.label("section", "Section"))
        lines.append(_section_command(level, title, opts))
        if(node.id):
            lines.append(f"\\label{{{_latex_label('sec', node.id)}}}")
        lines.append("")
        for child in node.children:
            _node_to_latex(ctx, child, lines, min(level+1, 4), opts)
        return

    if(node.kind=="Paragraph"):
        lines.append(_text_with_citations(ctx, node, "text", opts)+_field_xrefs_latex(ctx, node, opts))
        lines.append("")
        return

    if(node.kind=="Claim"):
        _logic_node_to_latex(ctx, node, lines, opts)
        return

    if(node.kind in {"Evidence", "Reason", "Counterargument", "Conclusion"}):
        _logic_node_to_latex(ctx, node, lines, opts)
        return

    if(node.kind=="Definition"):
        term=escape_latex(plain(node.fields.get("term")))
        text=_text_with_citations(ctx, node, "text", opts)
        lines.append(f"\\paragraph{{{escape_latex(ctx.label('definition', 'Definition'))}: {term}}}")
        lines.append(text)
        lines.append("")
        return

    if(node.kind=="Object"):
        name=plain(node.fields.get("name")) if("name" in node.fields) else (node.id or ctx.label("object", "Object"))
        type_name=f" : {node.type_name}" if(node.type_name) else ""
        lines.append(f"\\paragraph{{{escape_latex(ctx.label('object', 'Object'))} {escape_latex(node.id or name)}{escape_latex(type_name)}}}")
        _field_list_to_latex(node, lines)
        return

    if(node.kind=="Class"):
        lines.append(f"\\paragraph{{{escape_latex(ctx.label('class', 'Class'))} {escape_latex(node.id or '')}}}")
        _field_list_to_latex(node, lines)
        return

    if(node.kind=="Function"):
        return_type=plain(node.fields.get("__return_type__")) if("__return_type__" in node.fields) else "Any"
        params=plain(node.fields.get("__params__")) if("__params__" in node.fields) else ""
        title=f"{ctx.label('function', 'Function')} {node.id or ''}({params}) -> {return_type}"
        lines.append(f"\\paragraph{{{escape_latex(title)}}}")
        _field_list_to_latex(node, lines, skip_internal=True)
        return

    if(node.kind=="Figure"):
        _figure_to_latex(ctx, node, lines, opts)
        return

    if(node.kind=="Table"):
        _table_to_latex(ctx, node, lines, opts)
        return

    if(node.kind=="Chart"):
        _mermaid_to_latex(ctx, node, lines, opts, chart_mermaid(ctx, node), node.id or "Chart")
        return

    if(node.kind=="Flowchart"):
        _mermaid_to_latex(ctx, node, lines, opts, flowchart_mermaid(node), node.id or "Flowchart")
        return

    if(node.kind=="CodeBlock"):
        label=ctx.listing_label(node)
        caption=node_caption(node, node.id or "Code")
        source=plain(node.fields.get("source")).strip("\n")
        lines.append(_target_label_line("lst", node.id))
        lines.append(_bold_caption(label, caption))
        lines.append(_listing_environment(source, opts))
        lines.append("")
        return

    if(node.kind=="Reference"):
        return

    for child in node.children:
        _node_to_latex(ctx, child, lines, level, opts)


def _logic_node_to_latex(ctx: ExportContext, node: Node, lines: list[str], opts: LatexRenderOptions | None = None) -> None:
    title=f"{ctx.label(node.kind.lower(), node.kind)} {node.id or ''}".strip()
    lines.append(_target_label_line(node.kind.lower(), node.id))
    lines.append(r"\begin{quote}\textbf{"+escape_latex(title)+r":} "+_text_with_citations(ctx, node, "text", opts)+_field_xrefs_latex(ctx, node, opts))
    link_text=_logic_link_text(node)
    if(link_text):
        lines.append(r"\\")
        lines.append(r"\footnotesize "+escape_latex(link_text))
    lines.append(r"\end{quote}")
    lines.append("")


def _field_list_to_latex(node: Node, lines: list[str], skip_internal: bool = False) -> None:
    visible=[]
    for key,value in node.fields.items():
        if(skip_internal and key.startswith("__")):
            continue
        visible.append((key, plain(value)))
    if(not visible):
        lines.append("")
        return
    lines.append(r"\begin{description}")
    for key,value in visible:
        lines.append(f"\\item[{escape_latex(key)}] {escape_latex(value)}")
    lines.append(r"\end{description}")
    lines.append("")


def _figure_to_latex(ctx: ExportContext, node: Node, lines: list[str], opts: LatexRenderOptions) -> None:
    src=plain(node.fields.get("src"))
    caption=node_caption(node)
    label=_latex_label("fig", node.id)
    width=_latex_dimension(plain(node.fields.get("width")) if("width" in node.fields) else opts.figure_width, opts.figure_width)
    lines.append(r"\begin{figure}[htbp]")
    lines.append(r"\centering")
    if(src):
        lines.append(f"\\includegraphics[width={width}]{{{_latex_path(src)}}}")
    else:
        alt=plain(node.fields.get("alt")) if("alt" in node.fields) else ""
        lines.append(escape_latex(alt))
    if(caption):
        lines.append(f"\\caption{{{escape_latex(caption)}}}")
    if(label):
        lines.append(f"\\label{{{label}}}")
    lines.append(r"\end{figure}")
    lines.append("")


def _table_to_latex(ctx: ExportContext, node: Node, lines: list[str], opts: LatexRenderOptions) -> None:
    columns=node.fields.get("columns")
    rows=node.fields.get("rows")
    if(not columns or columns.kind!="List" or not rows or rows.kind!="List"):
        return

    headers=[]
    for col in columns.value:
        if(col.kind=="Object" and "name" in col.value):
            headers.append(plain(col.value["name"]))
    if(not headers):
        return

    caption=node_caption(node)
    label=_latex_label("tab", node.id)
    colspec=_table_colspec(len(headers))
    if(opts.table_font):
        lines.append("{"+opts.table_font)
    lines.append(f"\\begin{{longtable}}{{{colspec}}}")
    if(caption):
        cap=f"\\caption{{{escape_latex(caption)}}}"
        if(label):
            cap+=f"\\label{{{label}}}"
        cap+=r"\\"
        lines.append(cap)
    lines.append(r"\toprule")
    lines.append(" & ".join(_escape_table_cell(h) for h in headers)+r" \\")
    lines.append(r"\midrule")
    lines.append(r"\endfirsthead")
    lines.append(r"\toprule")
    lines.append(" & ".join(_escape_table_cell(h) for h in headers)+r" \\")
    lines.append(r"\midrule")
    lines.append(r"\endhead")
    for row in rows.value:
        if(row.kind=="List"):
            cells=[_escape_table_cell(plain(v)) for v in row.value]
            if(len(cells)<len(headers)):
                cells.extend([""]*(len(headers)-len(cells)))
            lines.append(" & ".join(cells[:len(headers)])+r" \\")
    lines.append(r"\bottomrule")
    lines.append(r"\end{longtable}")
    if(opts.table_font):
        lines.append("}")
    lines.append("")


def _references_to_latex(ctx: ExportContext, lines: list[str], opts: LatexRenderOptions | None = None) -> None:
    refs=ordered_references(ctx)
    if(not refs):
        return
    command="chapter" if(opts and opts.top_level=="chapter") else "section"
    lines.append(f"\\{command}*{{{escape_latex(ctx.label('references', 'References'))}}}")
    lines.append(r"\begin{thebibliography}{99}")
    for number, ref_id, ref in refs:
        lines.append(f"\\bibitem{{{_latex_cite_key(ref_id)}}} {escape_latex(reference_text(ref, ctx.citation_style))}")
    lines.append(r"\end{thebibliography}")
    lines.append("")


def _text_with_citations(ctx: ExportContext, node: Node, field_name: str, opts: LatexRenderOptions | None = None) -> str:
    text=_escape_text_with_xrefs_latex(ctx, plain(node.fields.get(field_name)), opts)
    cites=_latex_citations(ctx, node)
    return text+cites


def _escape_text_with_xrefs_latex(ctx: ExportContext, text: str, opts: LatexRenderOptions | None = None) -> str:
    pattern=re.compile(r"\{\{\s*(?:ref|xref)\s*:\s*([A-Za-z0-9_.:-]+)\s*\}\}")
    parts=[]
    last=0
    for match in pattern.finditer(text):
        parts.append(escape_latex(text[last:match.start()]))
        parts.append(_format_xref_latex(ctx, match.group(1), opts))
        last=match.end()
    parts.append(escape_latex(text[last:]))
    return "".join(parts)


def _latex_citations(ctx: ExportContext, node: Node) -> str:
    ids=citation_ids(ctx, node)
    if(not ids):
        return ""
    keys=",".join(_latex_cite_key(ref_id) for ref_id in ids)
    return r"\cite{"+keys+"}"




def _format_xref_latex(ctx: ExportContext, target_id: str, opts: LatexRenderOptions | None = None) -> str:
    label=escape_latex(ctx.target_label(target_id))
    node=ctx.doc.symbols.get(target_id)
    if(node is None):
        return label
    prefix={"Section":"sec", "Figure":"fig", "Chart":"fig", "Flowchart":"fig", "Table":"tab", "CodeBlock":"lst"}.get(node.kind, node.kind.lower())
    latex_label=_latex_label(prefix, target_id)
    if(opts and opts.hyperref and latex_label):
        return r"\hyperref["+latex_label+"]{"+label+r"}"
    return label


def _field_xrefs_latex(ctx: ExportContext, node: Node, opts: LatexRenderOptions | None = None) -> str:
    ids=cross_reference_ids_for_display(node, "text")
    if(not ids):
        return ""
    return " ("+", ".join(_format_xref_latex(ctx, target_id, opts) for target_id in ids)+")"


def _target_label_line(prefix: str, node_id: str | None) -> str:
    label=_latex_label(prefix, node_id)
    if(not label):
        return ""
    return r"\phantomsection"+"\n"+f"\\label{{{label}}}"

def _logic_link_text(node: Node) -> str:
    parts=[]
    for key in ["supports", "against", "based_on", "source"]:
        if(key in node.fields):
            parts.append(f"{key}: {plain(node.fields[key])}")
    return "; ".join(parts)


def _bold_caption(label: str, caption: str) -> str:
    text=label
    if(caption):
        text=f"{label}: {caption}"
    return r"\noindent\textbf{"+escape_latex(text)+r"}"


def _listing_environment(source: str, opts: LatexRenderOptions | None = None) -> str:
    env=(opts.code_environment if(opts is not None) else "lstlisting")
    if(env=="verbatim"):
        safe=_protect_verbatim_end(source, "verbatim")
        return "\\begin{verbatim}\n"+safe.rstrip("\n")+"\n\\end{verbatim}"
    safe=_protect_verbatim_end(source, "lstlisting")
    return "\\begin{lstlisting}\n"+safe.rstrip("\n")+"\n\\end{lstlisting}"


def _normalize_mermaid_mode(value: str) -> str:
    text=str(value).strip().lower().replace("_", "-")
    aliases={
        "source": "code",
        "listing": "code",
        "lstlisting": "code",
        "verbatim": "code",
        "code-block": "code",
        "figure-placeholder": "placeholder",
        "placeholder-figure": "placeholder",
        "image-placeholder": "placeholder",
        "external": "external-image",
        "image": "external-image",
        "external-image": "external-image",
        "external-image-ref": "external-image",
    }
    normalized=aliases.get(text, text)
    if(normalized not in {"code", "placeholder", "external-image"}):
        return "code"
    return normalized


def _mermaid_to_latex(ctx: ExportContext, node: Node, lines: list[str], opts: LatexRenderOptions, source: str, default_caption: str) -> None:
    label=ctx.figure_label(node)
    caption=node_caption(node, default_caption)
    if(opts.mermaid_mode=="code"):
        lines.append(_target_label_line("fig", node.id))
        lines.append(_bold_caption(label, caption))
        lines.append(_listing_environment(source, opts))
        lines.append("")
        return

    if(opts.mermaid_mode=="external-image"):
        image_path=_mermaid_external_image_path(node)
        if(image_path):
            lines.append(r"\begin{figure}[htbp]")
            lines.append(r"\centering")
            lines.append(f"\\includegraphics[width={opts.figure_width}]{{{_latex_path(image_path)}}}")
            if(caption):
                lines.append(f"\\caption{{{escape_latex(caption)}}}")
            latex_label=_latex_label("fig", node.id)
            if(latex_label):
                lines.append(f"\\label{{{latex_label}}}")
            lines.append(r"\end{figure}")
            lines.append("")
            return

    _mermaid_placeholder_to_latex(ctx, node, lines, opts, label, caption)


def _mermaid_external_image_path(node: Node) -> str:
    for key in ("image", "image_src", "mermaid_image", "src"):
        if(key in node.fields):
            value=plain(node.fields.get(key)).strip()
            if(value):
                return value
    return ""


def _mermaid_placeholder_to_latex(ctx: ExportContext, node: Node, lines: list[str], opts: LatexRenderOptions, label: str, caption: str) -> None:
    node_name=node.id or node.kind
    lines.append(r"\begin{figure}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\fbox{\begin{minipage}{0.86\linewidth}")
    lines.append(r"\centering")
    lines.append(r"\ttfamily\small Mermaid diagram placeholder\\")
    lines.append(escape_latex(f"{label}: {caption}" if(caption) else label)+r"\\")
    lines.append(escape_latex(f"node={node_name}; mode={opts.mermaid_mode}"))
    lines.append(r"\end{minipage}}")
    if(caption):
        lines.append(f"\\caption{{{escape_latex(caption)}}}")
    latex_label=_latex_label("fig", node.id)
    if(latex_label):
        lines.append(f"\\label{{{latex_label}}}")
    lines.append(r"\end{figure}")
    lines.append("")


def _protect_verbatim_end(source: str, env: str) -> str:
    pattern=rf"\\end\{{{re.escape(env)}\}}"
    return re.sub(pattern, lambda m: m.group(0).replace(r"\end", r"\string\end"), source)


def _section_command(level: int, title: str, opts: LatexRenderOptions | None = None) -> str:
    use_chapter=bool(opts and opts.top_level=="chapter")
    if(use_chapter):
        command={1:"chapter", 2:"section", 3:"subsection", 4:"subsubsection"}.get(level, "paragraph")
    else:
        command={1:"section", 2:"subsection", 3:"subsubsection"}.get(level, "paragraph")
    return f"\\{command}{{{escape_latex(title)}}}"


def _table_colspec(ncols: int) -> str:
    if(ncols<=0):
        return "l"
    width=max(0.12, min(0.46, 0.92/ncols))
    return "@{}"+"".join([f">{{\\raggedright\\arraybackslash}}p{{{width:.2f}\\linewidth}}" for _ in range(ncols)])+"@{}"


def _escape_table_cell(text: str) -> str:
    collapsed=" ".join(str(text).splitlines())
    return escape_latex(collapsed)


def _latex_label(prefix: str, node_id: str | None) -> str:
    if(not node_id):
        return ""
    return prefix+":"+_safe_latex_id(node_id)


def _latex_cite_key(ref_id: str) -> str:
    return "ref:"+_safe_latex_id(ref_id)


def _safe_latex_id(value: str) -> str:
    safe=re.sub(r"[^A-Za-z0-9:.-]+", "-", value)
    return safe.strip("-") or "unnamed"


def _latex_path(path: str) -> str:
    sanitized=str(path).replace("\n", " ").replace("}", "-").replace("{", "-")
    return r"\detokenize{"+sanitized+"}"


def _latex_class_options(value: str) -> str:
    allowed=set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,=-_ ")
    return "".join(ch for ch in value if(ch in allowed)).strip() or "12pt,a4paper,dvipdfmx"


def _latex_geometry_options(value: str) -> str:
    if(not value):
        return ""
    allowed=set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789,=-_. /")
    return "".join(ch for ch in value if(ch in allowed)).strip()


def _latex_command_name(value: str, default: str) -> str:
    safe=re.sub(r"[^A-Za-z0-9_-]", "", value)
    return safe or default


def _latex_font_size(value: str) -> str:
    text=value.strip().lstrip("\\").lower()
    allowed={"none":"", "normalsize":r"\normalsize", "small":r"\small", "footnotesize":r"\footnotesize", "scriptsize":r"\scriptsize"}
    return allowed.get(text, r"\small")


def _latex_dimension(value: str, default: str) -> str:
    text=value.strip()
    # Keep dimensions conservative: numeric TeX units, \linewidth, or fractions of \linewidth.
    if(re.fullmatch(r"[0-9]+(\.[0-9]+)?\\linewidth", text)):
        return text
    if(re.fullmatch(r"[0-9]+(\.[0-9]+)?(pt|mm|cm|in|em|ex)", text)):
        return text
    if(text in {r"\linewidth", r"\textwidth"}):
        return text
    return default


def escape_latex(text: str) -> str:
    mapping=dict(_LATEX_REPLACEMENTS)
    return "".join(mapping.get(ch, ch) for ch in str(text))


# Backward-compatible helper name for tests and external scripts.
def _escape_latex(text: str) -> str:
    return escape_latex(text)
