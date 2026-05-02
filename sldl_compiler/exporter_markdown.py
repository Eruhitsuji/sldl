from __future__ import annotations

from .ast_nodes import DocumentAst, Node, Value
from .export_support import (
    ExportContext,
    chart_mermaid,
    flowchart_mermaid,
    is_reference_section,
    markdown_citations,
    node_caption,
    ordered_references,
    plain,
    reference_text,
    cross_reference_ids_for_display,
    meta_bool,
    replace_xref_markers,
    safe_anchor_id,
)


def export_markdown(
    doc: DocumentAst,
    citation_style: str | None = None,
    export_config_path: str | None = None,
    base_path: str | None = None,
    toc: bool | None = None,
) -> str:
    ctx=ExportContext.build(doc, citation_style=citation_style, export_config_path=export_config_path, base_path=base_path)
    lines=[]

    title="Untitled"
    if(doc.meta and "title" in doc.meta.fields):
        title=plain(doc.meta.fields["title"])
    lines.append(f"# {title}")
    lines.append("")

    if(doc.meta):
        if("author" in doc.meta.fields):
            lines.append(f"- {ctx.label('author', 'Author')}: {plain(doc.meta.fields['author'])}")
        if("date" in doc.meta.fields):
            lines.append(f"- {ctx.label('date', 'Date')}: {plain(doc.meta.fields['date'])}")
        if("version" in doc.meta.fields):
            lines.append(f"- {ctx.label('version', 'Version')}: {plain(doc.meta.fields['version'])}")
        if(len(lines)>2):
            lines.append("")

    use_toc=meta_bool(doc, ("toc", "export_toc", "table_of_contents"), False) if(toc is None) else bool(toc)
    if(use_toc):
        _toc_to_markdown(ctx, lines)

    for node in doc.children:
        _node_to_markdown(ctx, node, lines, level=2)

    _references_to_markdown(ctx, lines)

    return "\n".join(lines).rstrip()+"\n"


def _node_to_markdown(ctx: ExportContext, node: Node, lines: list[str], level: int) -> None:
    if(node.kind=="Section"):
        if(is_reference_section(node)):
            return
        title=plain(node.fields.get("title")) if("title" in node.fields) else (node.id or ctx.label("section", "Section"))
        anchor=f" {{#{ctx.target_anchor(node.id)}}}" if(node.id) else ""
        lines.append(f"{'#'*level} {title}{anchor}")
        lines.append("")
        for child in node.children:
            _node_to_markdown(ctx, child, lines, min(level+1, 6))
        return

    if(node.kind=="Paragraph"):
        text=_text_with_xrefs_markdown(ctx, node, "text")
        lines.append(f"{text}{markdown_citations(ctx, node)}{_field_xrefs_markdown(ctx, node)}")
        lines.append("")
        return

    if(node.kind=="Claim"):
        text=_text_with_xrefs_markdown(ctx, node, "text")
        suffix=markdown_citations(ctx, node)
        lines.append(f"> **{ctx.label('claim', 'Claim')} {node.id or ''}:** {text}{suffix}{_field_xrefs_markdown(ctx, node)}")
        lines.append("")
        return

    if(node.kind in {"Evidence", "Reason", "Counterargument", "Conclusion"}):
        text=_text_with_xrefs_markdown(ctx, node, "text")
        suffix=markdown_citations(ctx, node)
        lines.append(f"> **{ctx.label(node.kind.lower(), node.kind)} {node.id or ''}:** {text}{suffix}{_field_xrefs_markdown(ctx, node)}")
        link_text=_logic_link_text(node)
        if(link_text):
            lines.append(f"> {link_text}")
        lines.append("")
        return

    if(node.kind=="Definition"):
        term=plain(node.fields.get("term"))
        text=_text_with_xrefs_markdown(ctx, node, "text")
        suffix=markdown_citations(ctx, node)
        lines.append(f"**{ctx.label('definition', 'Definition')}: {term}**{suffix}{_field_xrefs_markdown(ctx, node)}")
        lines.append("")
        lines.append(text)
        lines.append("")
        return

    if(node.kind=="Object"):
        name=plain(node.fields.get("name")) if("name" in node.fields) else (node.id or ctx.label("object", "Object"))
        type_name=f" : {node.type_name}" if(node.type_name) else ""
        lines.append(f"**{ctx.label('object', 'Object')} {node.id or name}{type_name}**")
        lines.append("")
        for key,value in node.fields.items():
            lines.append(f"- {key}: {plain(value)}")
        lines.append("")
        return

    if(node.kind=="Class"):
        lines.append(f"**{ctx.label('class', 'Class')} {node.id or ''}**")
        lines.append("")
        for key,value in node.fields.items():
            lines.append(f"- {key}: {plain(value)}")
        lines.append("")
        return

    if(node.kind=="Function"):
        return_type=plain(node.fields.get("__return_type__")) if("__return_type__" in node.fields) else "Any"
        params=plain(node.fields.get("__params__")) if("__params__" in node.fields) else ""
        lines.append(f"**{ctx.label('function', 'Function')} {node.id or ''}({params}) -> {return_type}**")
        lines.append("")
        for key,value in node.fields.items():
            if(key.startswith("__")):
                continue
            lines.append(f"- {key}: {plain(value)}")
        lines.append("")
        return

    if(node.kind=="Figure"):
        alt=plain(node.fields.get("alt")) if("alt" in node.fields) else ""
        src=plain(node.fields.get("src"))
        caption=node_caption(node)
        label=ctx.figure_label(node)
        lines.append(f"![{alt}]({src})")
        if(caption):
            lines.append(f'*<a id="{ctx.target_anchor(node.id or "")}"></a>{label}: {caption}*')
        else:
            lines.append(f'*<a id="{ctx.target_anchor(node.id or "")}"></a>{label}*')
        lines.append("")
        return

    if(node.kind=="Table"):
        _table_to_markdown(ctx, node, lines)
        return

    if(node.kind=="Chart"):
        label=ctx.figure_label(node)
        caption=node_caption(node, node.id or "Chart")
        lines.append(f'**<a id="{ctx.target_anchor(node.id or "")}"></a>{label}: {caption}**')
        lines.append("")
        lines.append("```mermaid")
        lines.append(chart_mermaid(ctx, node))
        lines.append("```")
        lines.append("")
        return

    if(node.kind=="Flowchart"):
        label=ctx.figure_label(node)
        caption=node_caption(node, node.id or "Flowchart")
        lines.append(f'**<a id="{ctx.target_anchor(node.id or "")}"></a>{label}: {caption}**')
        lines.append("")
        lines.append("```mermaid")
        lines.append(flowchart_mermaid(node))
        lines.append("```")
        lines.append("")
        return

    if(node.kind=="CodeBlock"):
        lang=plain(node.fields.get("lang"))
        source=plain(node.fields.get("source")).strip("\n")
        caption=node_caption(node, node.id or "Code")
        label=ctx.listing_label(node)
        lines.append(f'**<a id="{ctx.target_anchor(node.id or "")}"></a>{label}: {caption}**')
        lines.append("")
        lines.append(f"```{lang}")
        lines.append(source)
        lines.append("```")
        lines.append("")
        return

    if(node.kind=="Reference"):
        return

    for child in node.children:
        _node_to_markdown(ctx, child, lines, level)




def _toc_to_markdown(ctx: ExportContext, lines: list[str]) -> None:
    items=ctx.section_toc_items()
    if(not items):
        return
    lines.append(f"## {ctx.label('toc', 'Table of Contents')}")
    lines.append("")
    for depth,node_id,number,title in items:
        indent="  "*(max(depth, 1)-1)
        prefix=(number+" ") if(number) else ""
        lines.append(f"{indent}- [{prefix}{title}](#{ctx.target_anchor(node_id)})")
    lines.append("")


def _format_xref_markdown(ctx: ExportContext, target_id: str) -> str:
    label=ctx.target_label(target_id)
    if(target_id not in ctx.doc.symbols):
        return label
    return f"[{label}](#{ctx.target_anchor(target_id)})"


def _text_with_xrefs_markdown(ctx: ExportContext, node: Node, field_name: str) -> str:
    text=plain(node.fields.get(field_name))
    return replace_xref_markers(text, lambda target_id: _format_xref_markdown(ctx, target_id))


def _field_xrefs_markdown(ctx: ExportContext, node: Node) -> str:
    ids=cross_reference_ids_for_display(node, "text")
    if(not ids):
        return ""
    return " ("+", ".join(_format_xref_markdown(ctx, target_id) for target_id in ids)+")"

def _logic_link_text(node: Node) -> str:
    parts=[]
    for key in ["supports", "against", "based_on", "source"]:
        if(key in node.fields):
            parts.append(f"{key}: {plain(node.fields[key])}")
    return "; ".join(parts)


def _table_to_markdown(ctx: ExportContext, node: Node, lines: list[str]) -> None:
    caption=node_caption(node)
    label=ctx.table_label(node)
    if(caption):
        lines.append(f'**<a id="{ctx.target_anchor(node.id or "")}"></a>{label}: {caption}**')
        lines.append("")
    else:
        lines.append(f'**<a id="{ctx.target_anchor(node.id or "")}"></a>{label}**')
        lines.append("")
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

    lines.append("| "+" | ".join(headers)+" |")
    lines.append("| "+" | ".join(["---"]*len(headers))+" |")
    for row in rows.value:
        if(row.kind=="List"):
            cells=[plain(v) for v in row.value]
            lines.append("| "+" | ".join(cells)+" |")
    lines.append("")


def _references_to_markdown(ctx: ExportContext, lines: list[str]) -> None:
    refs=ordered_references(ctx)
    if(not refs):
        return
    lines.append(f"## {ctx.label('references', 'References')}")
    lines.append("")
    for number, ref_id, ref in refs:
        if(ctx.numbered_bibliography()):
            lines.append(f"[{number}] {reference_text(ref, ctx.citation_style)}")
        else:
            lines.append(f"- {reference_text(ref, ctx.citation_style)}")
        lines.append("")


# Backward-compatible helper name used by older modules/tests.
def _plain(value: Value | None) -> str:
    return plain(value)
