from __future__ import annotations

from .ast_nodes import DocumentAst, Node, Value


def format_document(doc: DocumentAst, indent: int = 4) -> str:
    unit=" "*indent
    lines=[f'document "{_escape_string(doc.id)}" : {doc.type_name} {{']
    if(doc.meta is not None):
        _format_node(doc.meta, lines, 1, unit)
        if(doc.children):
            lines.append("")
    for idx,node in enumerate(doc.children):
        _format_node(node, lines, 1, unit)
        if(idx!=len(doc.children)-1):
            lines.append("")
    lines.append("}")
    return "\n".join(lines).rstrip()+"\n"


def _format_node(node: Node, lines: list[str], depth: int, unit: str) -> None:
    pad=unit*depth
    if(node.kind=="Meta"):
        lines.append(f"{pad}meta {{")
    elif(node.kind=="Paragraph"):
        lines.append(f"{pad}paragraph {{")
    elif(node.kind=="Function"):
        params=node.fields.get("__params__")
        ret=node.fields.get("__return_type__")
        param_text=""
        if(params is not None and params.kind=="Raw"):
            param_text=", ".join(f"{p.get('name','')}: {p.get('type','')}" for p in params.value)
        lines.append(f"{pad}func {node.id or '_'}({param_text}) -> {_plain_string(ret) or 'Any'} {{")
    elif(node.kind=="Class"):
        lines.append(f"{pad}class {node.id or '_'} : {node.type_name or 'Object'} {{")
    else:
        keyword=_kind_to_keyword(node.kind)
        if(node.id is not None):
            lines.append(f"{pad}{keyword} {node.id} : {node.type_name or node.kind} {{")
        else:
            lines.append(f"{pad}{keyword} : {node.type_name or node.kind} {{")

    hidden={"__params__","__return_type__"}
    for key,value in node.fields.items():
        if(key in hidden):
            continue
        _format_field(key,value,lines,depth+1,unit)
    if(node.fields and node.children):
        lines.append("")
    for idx,child in enumerate(node.children):
        _format_node(child,lines,depth+1,unit)
        if(idx!=len(node.children)-1):
            lines.append("")
    lines.append(f"{pad}}}")


def _format_field(key: str, value: Value, lines: list[str], depth: int, unit: str) -> None:
    pad=unit*depth
    lines.append(f"{pad}{key}: {_format_value(value, depth, unit)};")


def _format_value(value: Value, depth: int, unit: str) -> str:
    if(value.kind=="TextLang"):
        return f'"{_escape_string(value.value["text"])}"@{value.value["lang"]}'
    if(value.kind=="String"):
        s=str(value.value)
        if("\n" in s):
            return '"""\n'+s.rstrip()+"\n"+unit*depth+'"""'
        return f'"{_escape_string(s)}"'
    if(value.kind=="Number"):
        return str(value.value)
    if(value.kind=="Bool"):
        return "true" if(value.value) else "false"
    if(value.kind=="Null"):
        return "null"
    if(value.kind=="Identifier"):
        return str(value.value)
    if(value.kind=="FunctionCall"):
        args=", ".join(_format_value(v, depth, unit) for v in value.value["args"])
        return f"{value.value['name']}({args})"
    if(value.kind=="List"):
        if(not value.value):
            return "[]"
        if(_is_simple_list(value)):
            return "["+", ".join(_format_value(v, depth, unit) for v in value.value)+"]"
        lines=["["]
        for idx,item in enumerate(value.value):
            comma="," if(idx!=len(value.value)-1) else ""
            lines.append(unit*(depth+1)+_format_value(item, depth+1, unit)+comma)
        lines.append(unit*depth+"]")
        return "\n".join(lines)
    if(value.kind=="Object"):
        if(not value.value):
            return "{}"
        lines=["{"]
        for k,v in value.value.items():
            lines.append(unit*(depth+1)+f"{k}: {_format_value(v, depth+1, unit)};")
        lines.append(unit*depth+"}")
        return "\n".join(lines)
    if(value.kind=="Raw"):
        return repr(value.value)
    return str(value.value)


def _is_simple_list(value: Value) -> bool:
    return value.kind=="List" and all(v.kind in {"TextLang","String","Number","Bool","Null","Identifier","FunctionCall"} for v in value.value)


def _kind_to_keyword(kind: str) -> str:
    return {
        "Section":"section",
        "Claim":"claim",
        "Evidence":"evidence",
        "Reason":"reason",
        "Counterargument":"counterargument",
        "Conclusion":"conclusion",
        "Definition":"definition",
        "Reference":"reference",
        "Figure":"figure",
        "Table":"table",
        "Chart":"chart",
        "Flowchart":"flowchart",
        "CodeBlock":"code",
        "Object":"object",
    }.get(kind, kind.lower())


def _plain_string(value: Value | None) -> str:
    if(value is None):
        return ""
    if(value.kind=="String"):
        return str(value.value)
    if(value.kind=="Identifier"):
        return str(value.value)
    if(value.kind=="TextLang"):
        return str(value.value["text"])
    return str(value.value)


def _escape_string(s: str) -> str:
    return str(s).replace("\\","\\\\").replace('"','\\"')
