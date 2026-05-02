from __future__ import annotations

from .ast_nodes import DocumentAst, Node


def export_mermaid(doc: DocumentAst) -> str:
    lines=["flowchart TD"]
    nodes={}
    for node in _walk(doc.children):
        if(node.id):
            nodes[node.id]=f"{node.kind}: {node.id}" if(node.kind) else node.id
    for node_id,label in sorted(nodes.items()):
        lines.append(f"    {_safe_id(node_id)}[\"{_escape(label)}\"]")
    edges=list(getattr(doc, "semantic_edges", []))
    if(not edges):
        lines.append("    empty[\"No semantic edges\"]")
    for edge in edges:
        src=str(edge.get("from", ""))
        dst=str(edge.get("to", ""))
        if(not src or not dst):
            continue
        field=str(edge.get("field", "ref"))
        if(src not in nodes):
            lines.append(f"    {_safe_id(src)}[\"{_escape(src)}\"]")
        if(dst not in nodes):
            lines.append(f"    {_safe_id(dst)}[\"{_escape(dst)}\"]")
        lines.append(f"    {_safe_id(src)} -- \"{_escape(field)}\" --> {_safe_id(dst)}")
    return "\n".join(lines)+"\n"


def _walk(nodes: list[Node]):
    for node in nodes:
        yield node
        yield from _walk(node.children)


def _safe_id(value: str) -> str:
    out=[]
    for ch in value:
        out.append(ch if(ch.isalnum()) else "_")
    text="".join(out).strip("_") or "node"
    if(text[0].isdigit()):
        text="n_"+text
    return text


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', "'")
