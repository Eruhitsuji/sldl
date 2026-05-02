from __future__ import annotations

import html

from .ast_nodes import DocumentAst, Node
from .export_support import (
    ExportContext,
    chart_mermaid,
    flowchart_mermaid,
    is_reference_section,
    html_citation_links,
    node_caption,
    ordered_references,
    plain,
    reference_text,
    cross_reference_ids_for_display,
    meta_bool,
    replace_xref_markers,
)


def export_html(
    doc: DocumentAst,
    citation_style: str | None = None,
    export_config_path: str | None = None,
    base_path: str | None = None,
    toc: bool | None = None,
) -> str:
    ctx=ExportContext.build(doc, citation_style=citation_style, export_config_path=export_config_path, base_path=base_path)
    title="Untitled"
    if(doc.meta and "title" in doc.meta.fields):
        title=plain(doc.meta.fields["title"])
    body=[]
    body.append(f"<h1>{html.escape(title)}</h1>")

    if(doc.meta):
        meta=[]
        if("author" in doc.meta.fields): meta.append(f"<li><strong>{html.escape(ctx.label('author', 'Author'))}:</strong> {html.escape(plain(doc.meta.fields['author']))}</li>")
        if("date" in doc.meta.fields): meta.append(f"<li><strong>{html.escape(ctx.label('date', 'Date'))}:</strong> {html.escape(plain(doc.meta.fields['date']))}</li>")
        if("version" in doc.meta.fields): meta.append(f"<li><strong>{html.escape(ctx.label('version', 'Version'))}:</strong> {html.escape(plain(doc.meta.fields['version']))}</li>")
        if(meta): body.append("<ul class=\"meta\">"+"".join(meta)+"</ul>")

    use_toc=meta_bool(doc, ("toc", "export_toc", "table_of_contents"), False) if(toc is None) else bool(toc)
    if(use_toc):
        _toc_to_html(ctx, body)

    for node in doc.children:
        _node_to_html(ctx, node, body, level=2)
    _references_to_html(ctx, body)

    return """<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<script type="module">import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs'; mermaid.initialize({{startOnLoad:true}});</script>
<style>
body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; line-height: 1.7; max-width: 980px; margin: 2rem auto; padding: 0 1rem; }}
.meta {{ color: #555; }}
.logic {{ border-left: 4px solid #ddd; padding-left: 1rem; margin: 1rem 0; }}
.caption {{ color: #555; font-size: 0.95rem; }}
.toc {{ border: 1px solid #ddd; padding: 1rem; margin: 1rem 0 2rem; background: #fafafa; }}
.toc ul {{ margin: 0.2rem 0 0.2rem 1.2rem; padding-left: 1rem; }}
table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; }}
th, td {{ border: 1px solid #ccc; padding: 0.4rem 0.6rem; }}
pre {{ background: #f6f6f6; padding: 1rem; overflow-x: auto; }}
.figure {{ margin: 1rem 0; }}
.references p {{ margin-bottom: 1rem; }}
</style>
</head>
<body>
{body}
</body>
</html>
""".format(lang=html.escape(ctx.labels.html_lang), title=html.escape(title), body="\n".join(body))


def _node_to_html(ctx: ExportContext, node: Node, body: list[str], level: int) -> None:
    if(node.kind=="Section"):
        if(is_reference_section(node)):
            return
        title=plain(node.fields.get("title")) if("title" in node.fields) else (node.id or ctx.label("section", "Section"))
        anchor=f' id="{html.escape(ctx.target_anchor(node.id))}"' if(node.id) else ""
        body.append(f"<h{level}{anchor}>{html.escape(title)}</h{level}>")
        for child in node.children:
            _node_to_html(ctx, child, body, min(level+1, 6))
        return

    if(node.kind=="Paragraph"):
        body.append(f"<p>{_text_with_xrefs_html(ctx, node, 'text')}{html_citation_links(ctx, node)}{_field_xrefs_html(ctx, node)}</p>")
        return

    if(node.kind=="Claim"):
        text=html.escape(plain(node.fields.get("text")))
        body.append(f"<div class=\"logic claim\"><strong>{html.escape(ctx.label('claim', 'Claim'))} {html.escape(node.id or '')}:</strong> {text}{html_citation_links(ctx, node)}</div>")
        return

    if(node.kind in {"Evidence", "Reason", "Counterargument", "Conclusion"}):
        text=_text_with_xrefs_html(ctx, node, "text")
        label=html.escape(ctx.label(node.kind.lower(), node.kind))
        link_text=html.escape(_logic_link_text(node))
        extra=f"<br><span class=\"caption\">{link_text}</span>" if(link_text) else ""
        body.append(f"<div class=\"logic\"><strong>{label} {html.escape(node.id or '')}:</strong> {text}{html_citation_links(ctx, node)}{extra}</div>")
        return

    if(node.kind=="Definition"):
        term=html.escape(plain(node.fields.get("term")))
        text=html.escape(plain(node.fields.get("text")))
        body.append(f"<div class=\"definition\"><strong>{html.escape(ctx.label('definition', 'Definition'))}: {term}</strong>{html_citation_links(ctx, node)}<p>{text}</p></div>")
        return

    if(node.kind in {"Object", "Class", "Function"}):
        label=ctx.label(node.kind.lower(), node.kind)
        title=f"{label} {node.id or ''}"
        body.append(f"<h{level}>{html.escape(title)}</h{level}>")
        body.append("<ul>")
        for key,value in node.fields.items():
            if(key.startswith("__")):
                continue
            body.append(f"<li><strong>{html.escape(key)}:</strong> {html.escape(plain(value))}</li>")
        body.append("</ul>")
        return

    if(node.kind=="Figure"):
        src=plain(node.fields.get("src"))
        alt=plain(node.fields.get("alt")) if("alt" in node.fields) else ""
        caption=node_caption(node)
        label=ctx.figure_label(node)
        body.append(f'<figure class="figure" id="{html.escape(ctx.target_anchor(node.id or ""))}">')
        body.append(f'<img src="{html.escape(src)}" alt="{html.escape(alt)}" style="max-width:100%;">')
        body.append(f'<figcaption>{html.escape(label)}: {html.escape(caption)}</figcaption>')
        body.append('</figure>')
        return

    if(node.kind=="Table"):
        _table_to_html(ctx, node, body)
        return

    if(node.kind=="Chart"):
        label=ctx.figure_label(node)
        caption=node_caption(node, node.id or "Chart")
        body.append(f"<p class=\"caption\" id=\"{html.escape(ctx.target_anchor(node.id or ''))}\"><strong>{html.escape(label)}: {html.escape(caption)}</strong></p>")
        body.append('<pre class="mermaid">'+html.escape(chart_mermaid(ctx, node))+'</pre>')
        return

    if(node.kind=="Flowchart"):
        label=ctx.figure_label(node)
        caption=node_caption(node, node.id or "Flowchart")
        body.append(f"<p class=\"caption\" id=\"{html.escape(ctx.target_anchor(node.id or ''))}\"><strong>{html.escape(label)}: {html.escape(caption)}</strong></p>")
        body.append('<pre class="mermaid">'+html.escape(flowchart_mermaid(node))+'</pre>')
        return

    if(node.kind=="CodeBlock"):
        lang=plain(node.fields.get("lang"))
        source=plain(node.fields.get("source"))
        caption=node_caption(node, node.id or "Code")
        label=ctx.listing_label(node)
        body.append(f"<p class=\"caption\" id=\"{html.escape(ctx.target_anchor(node.id or ''))}\"><strong>{html.escape(label)}: {html.escape(caption)}</strong></p>")
        body.append(f"<pre><code class=\"language-{html.escape(lang)}\">{html.escape(source)}</code></pre>")
        return

    if(node.kind=="Reference"):
        return

    for child in node.children:
        _node_to_html(ctx, child, body, level)




def _toc_to_html(ctx: ExportContext, body: list[str]) -> None:
    items=ctx.section_toc_items()
    if(not items):
        return
    body.append(f'<nav class="toc" aria-label="{html.escape(ctx.label("toc", "Table of Contents"))}">')
    body.append(f'<strong>{html.escape(ctx.label("toc", "Table of Contents"))}</strong>')
    body.append('<ul>')
    for depth,node_id,number,title in items:
        prefix=(number+" ") if(number) else ""
        body.append(f'<li class="toc-level-{depth}"><a href="#{html.escape(ctx.target_anchor(node_id))}">{html.escape(prefix+title)}</a></li>')
    body.append('</ul></nav>')


def _format_xref_html(ctx: ExportContext, target_id: str) -> str:
    label=ctx.target_label(target_id)
    if(target_id not in ctx.doc.symbols):
        return html.escape(label)
    return f'<a href="#{html.escape(ctx.target_anchor(target_id))}">{html.escape(label)}</a>'


def _text_with_xrefs_html(ctx: ExportContext, node: Node, field_name: str) -> str:
    text=plain(node.fields.get(field_name))
    escaped=html.escape(text)
    return replace_xref_markers(escaped, lambda target_id: _format_xref_html(ctx, target_id))


def _field_xrefs_html(ctx: ExportContext, node: Node) -> str:
    ids=cross_reference_ids_for_display(node, "text")
    if(not ids):
        return ""
    return " ("+", ".join(_format_xref_html(ctx, target_id) for target_id in ids)+")"

def _logic_link_text(node: Node) -> str:
    parts=[]
    for key in ["supports", "against", "based_on", "source"]:
        if(key in node.fields):
            parts.append(f"{key}: {plain(node.fields[key])}")
    return "; ".join(parts)


def _table_to_html(ctx: ExportContext, node: Node, body: list[str]) -> None:
    caption=node_caption(node)
    label=ctx.table_label(node)
    body.append(f"<p class=\"caption\" id=\"{html.escape(ctx.target_anchor(node.id or ''))}\"><strong>{html.escape(label)}: {html.escape(caption)}</strong></p>")
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
    body.append("<table><thead><tr>"+"".join(f"<th>{html.escape(h)}</th>" for h in headers)+"</tr></thead><tbody>")
    for row in rows.value:
        if(row.kind=="List"):
            cells=[plain(v) for v in row.value]
            body.append("<tr>"+"".join(f"<td>{html.escape(c)}</td>" for c in cells)+"</tr>")
    body.append("</tbody></table>")


def _references_to_html(ctx: ExportContext, body: list[str]) -> None:
    refs=ordered_references(ctx)
    if(not refs):
        return
    body.append(f"<h2>{html.escape(ctx.label('references', 'References'))}</h2>")
    body.append('<div class="references">')
    if(ctx.numbered_bibliography()):
        for number, ref_id, ref in refs:
            body.append(f'<p id="ref-{number}">[{number}] {html.escape(reference_text(ref, ctx.citation_style))}</p>')
    else:
        body.append('<ul>')
        for number, ref_id, ref in refs:
            body.append(f'<li id="ref-{number}">{html.escape(reference_text(ref, ctx.citation_style))}</li>')
        body.append('</ul>')
    body.append('</div>')
