from __future__ import annotations

from .ast_nodes import DocumentAst, Node, Value
from .diagnostics import Diagnostic

REFERENCE_FIELDS={"supports", "against", "evidence", "source", "based_on", "cite", "cites", "contradicts", "depends_on", "requires", "rebuts", "responds_to"}
CITATION_LIKE_FIELDS={"source", "cite", "cites"}
REFERENCE_USING_FIELDS={"source", "based_on", "cite", "cites", "evidence", "supports", "against", "contradicts", "depends_on", "requires", "rebuts", "responds_to"}


def resolve(doc: DocumentAst) -> DocumentAst:
    doc.symbols={}
    doc.reference_aliases={}
    for node in _walk(doc.children):
        if(node.id):
            if(node.id in doc.symbols):
                doc.diagnostics.append(Diagnostic("error", "E_DUPLICATE_ID", f"Duplicate id: {node.id}", node.line, node.column))
            else:
                doc.symbols[node.id]=node
        if(node.kind=="Reference"):
            _register_reference_aliases(doc, node)

    _check_references(doc)
    _warn_unused_references(doc)
    return doc


def _walk(nodes: list[Node]):
    for node in nodes:
        yield node
        yield from _walk(node.children)


def _register_reference_aliases(doc: DocumentAst, node: Node) -> None:
    if(not node.id):
        return
    doc.reference_aliases[node.id]=node.id
    for key in ["bibkey", "key", "doi"]:
        if(key in node.fields):
            value=_plain(node.fields[key]).strip()
            if(value):
                doc.reference_aliases[value]=node.id
    if("aliases" in node.fields):
        for alias in _iter_refs(node.fields["aliases"]):
            if(alias):
                doc.reference_aliases[alias]=node.id


def _check_references(doc: DocumentAst) -> None:
    available=_available_reference_keys(doc)
    for node in _walk(doc.children):
        for key,value in node.fields.items():
            normalized=key.rstrip("?")
            if(normalized not in REFERENCE_FIELDS):
                continue
            if(normalized=="source" and node.kind in {"CodeBlock", "Figure", "Table", "Flowchart"}):
                continue
            for ref_name in _iter_refs(value):
                if(ref_name in doc.reference_aliases):
                    continue
                if(ref_name in doc.symbols):
                    continue
                code="E_UNDEFINED_CITE_KEY" if(normalized in CITATION_LIKE_FIELDS) else "E_UNDEFINED_REFERENCE"
                doc.diagnostics.append(Diagnostic(
                    "error",
                    code,
                    _undefined_reference_message(code, normalized, ref_name, node, available),
                    value.line or node.line,
                    value.column or node.column,
                ))


def _warn_unused_references(doc: DocumentAst) -> None:
    used_reference_ids=set()
    for node in _walk(doc.children):
        if(node.kind=="Reference"):
            continue
        for key,value in node.fields.items():
            normalized=key.rstrip("?")
            if(normalized not in REFERENCE_USING_FIELDS):
                continue
            if(normalized=="source" and node.kind in {"CodeBlock", "Figure", "Table", "Flowchart"}):
                continue
            for raw in _iter_refs(value):
                ref_id=doc.reference_aliases.get(raw, raw)
                target=doc.symbols.get(ref_id)
                if(target is not None and target.kind=="Reference"):
                    used_reference_ids.add(ref_id)

    for node in _walk(doc.children):
        if(node.kind!="Reference" or not node.id):
            continue
        if(node.id not in used_reference_ids):
            bibkey=_plain(node.fields.get("bibkey")).strip() if("bibkey" in node.fields) else ""
            suffix=f" (BibTeX key: {bibkey})" if(bibkey and bibkey!=node.id) else ""
            doc.diagnostics.append(Diagnostic("warning", "W_UNUSED_REFERENCE", f"Reference is defined but not cited: {node.id}{suffix}", node.line, node.column))


def _undefined_reference_message(code: str, field_name: str, ref_name: str, node: Node, available: str) -> str:
    if(code=="E_UNDEFINED_CITE_KEY"):
        return (
            f"Undefined citation key in {node.kind}.{field_name}: {ref_name}. "
            f"Define a Reference node, import it from BibTeX, or use one of: {available}"
        )
    return f"Undefined reference in {node.kind}.{field_name}: {ref_name}"


def _available_reference_keys(doc: DocumentAst) -> str:
    keys=sorted(doc.reference_aliases.keys())
    if(not keys):
        return "<none>"
    if(len(keys)>20):
        return ", ".join(keys[:20])+", ..."
    return ", ".join(keys)


def _iter_refs(value: Value):
    if(value.kind=="Identifier"):
        yield str(value.value)
    elif(value.kind=="String"):
        yield str(value.value)
    elif(value.kind=="TextLang"):
        yield str(value.value["text"])
    elif(value.kind=="List"):
        for item in value.value:
            yield from _iter_refs(item)
    elif(value.kind=="FunctionCall"):
        for arg in value.value["args"]:
            yield from _iter_refs(arg)


def _plain(value: Value | None) -> str:
    if(value is None):
        return ""
    if(value.kind=="TextLang"):
        return str(value.value["text"])
    if(value.kind in {"String", "Number", "Bool", "Identifier"}):
        return str(value.value)
    if(value.kind=="List"):
        return ", ".join(_plain(v) for v in value.value)
    return str(value.value)
