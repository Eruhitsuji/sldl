from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ast_nodes import DocumentAst, Value


@dataclass(frozen=True)
class TypeCheckResult:
    ok: bool
    actual: str
    expected: str
    reason: str = ""


PRIMITIVE_ALIASES={
    "String": "Text",
    "URI": "Text",
    "URL": "Text",
    "FilePath": "Text",
    "MathExpr": "Text",
    "Percent": "Float",
    "Number": "Float",
}


def normalize_type(type_name: str, doc: DocumentAst | None = None, _seen: set[str] | None = None) -> str:
    raw=(type_name or "").strip()
    raw=PRIMITIVE_ALIASES.get(raw, raw)
    if(doc is None):
        return raw
    aliases=getattr(doc, "type_aliases", {})
    if(raw not in aliases):
        return raw
    if(_seen is None):
        _seen=set()
    if(raw in _seen):
        return raw
    _seen.add(raw)
    return normalize_type(str(aliases[raw]), doc, _seen)


def infer_value_type(value: Value, doc: DocumentAst | None = None) -> str:
    if(value.kind=="String"):
        return "Text"
    if(value.kind=="TextLang"):
        return "TextLang"
    if(value.kind=="Number"):
        return "Int" if(isinstance(value.value, int) and not isinstance(value.value, bool)) else "Float"
    if(value.kind=="Bool"):
        return "Bool"
    if(value.kind=="Null"):
        return "Null"
    if(value.kind=="Identifier"):
        return "Identifier"
    if(value.kind=="List"):
        if(not value.value):
            return "List<Any>"
        item_types=[]
        for item in value.value:
            t=infer_value_type(item, doc)
            if(t not in item_types):
                item_types.append(t)
        if(len(item_types)==1):
            return f"List<{item_types[0]}>"
        return "List<Union<"+"|".join(item_types)+">>"
    if(value.kind=="Object"):
        return "Object"
    if(value.kind=="FunctionCall"):
        name=value.value["name"]
        if(name in {"Date", "Time", "DateTime"}):
            return name
        if(doc is not None):
            sig=getattr(doc, "function_signatures", {}).get(name)
            if(isinstance(sig, dict) and sig.get("return")):
                return str(sig.get("return"))
        return f"Call<{name}>"
    if(value.kind=="Raw"):
        return "Raw"
    return value.kind


def type_matches(value: Value, expected: str, doc: DocumentAst | None = None) -> TypeCheckResult:
    expected=(expected or "").strip()
    actual=infer_value_type(value, doc)
    if(_matches(value, expected, doc)):
        return TypeCheckResult(True, actual, expected)
    return TypeCheckResult(False, actual, expected, f"expected {expected}, got {actual}")


def _matches(value: Value, expected: str, doc: DocumentAst | None) -> bool:
    expected=normalize_type(expected.strip(), doc)
    if(not expected or expected=="Any"):
        return True
    top_parts=_split_union(expected)
    if(len(top_parts)>1 and not expected.startswith("Union<") and not expected.startswith("Enum<")):
        return any(_matches(value, part, doc) for part in top_parts)
    if(expected.startswith("Union<") and expected.endswith(">")):
        inner=expected[len("Union<"):-1]
        return any(_matches(value, part, doc) for part in _split_union(inner))
    if(expected.startswith("List<") and expected.endswith(">")):
        if(value.kind!="List"):
            return False
        inner=expected[len("List<"):-1]
        return all(_matches(item, inner, doc) for item in value.value)
    if(expected.startswith("Ref<") and expected.endswith(">")):
        if(value.kind=="Identifier"):
            ref_name=str(value.value)
        elif(value.kind=="String"):
            ref_name=str(value.value)
        elif(value.kind=="TextLang"):
            ref_name=str(value.value["text"])
        else:
            return False
        if(doc is None):
            return True
        alias=getattr(doc, "reference_aliases", {}).get(ref_name, ref_name)
        target=doc.symbols.get(alias)
        if(target is None):
            return True
        allowed=expected[len("Ref<"):-1]
        if(allowed=="Any"):
            return True
        return _target_type_allowed(target.kind, target.type_name or "", allowed, doc)
    if(expected.startswith("Enum<") and expected.endswith(">")):
        return _plain_value(value) in set(_split_union(expected[len("Enum<"):-1]))
    if(doc is not None and expected in getattr(doc, "enum_types", {})):
        return _plain_value(value) in set(str(x) for x in getattr(doc, "enum_types", {}).get(expected, []))
    if(value.kind=="FunctionCall"):
        actual=infer_value_type(value, doc)
        if(actual==expected):
            return True
        if(doc is not None):
            return _type_name_matches(actual, expected, doc)
    if(expected=="Text"):
        return value.kind in {"String", "TextLang", "Identifier"}
    if(expected=="TextLang"):
        return value.kind=="TextLang"
    if(expected=="Int"):
        return value.kind=="Number" and isinstance(value.value, int) and not isinstance(value.value, bool)
    if(expected=="Float"):
        return value.kind=="Number" and isinstance(value.value, (int, float)) and not isinstance(value.value, bool)
    if(expected=="Bool"):
        return value.kind=="Bool"
    if(expected in {"Date", "Time", "DateTime"}):
        return value.kind=="FunctionCall" and value.value.get("name")==expected
    if(expected=="Object"):
        return value.kind=="Object"
    if(expected=="Identifier"):
        return value.kind=="Identifier"
    if(expected=="Raw"):
        return value.kind=="Raw"
    if(value.kind=="Identifier" and doc is not None and str(value.value) in doc.symbols):
        target=doc.symbols[str(value.value)]
        return _target_type_allowed(target.kind, target.type_name or "", expected, doc)
    return _type_name_matches(infer_value_type(value, doc), expected, doc)


def _target_type_allowed(kind: str, type_name: str, allowed: str, doc: DocumentAst | None) -> bool:
    allowed=normalize_type(allowed, doc)
    allowed_parts=_split_union(allowed)
    if(len(allowed_parts)>1):
        return any(_target_type_allowed(kind, type_name, part, doc) for part in allowed_parts)
    return kind==allowed or type_name==allowed


def _type_name_matches(actual: str, expected: str, doc: DocumentAst | None) -> bool:
    actual=normalize_type(actual, doc)
    expected=normalize_type(expected, doc)
    if(actual==expected):
        return True
    if(expected=="Float" and actual=="Int"):
        return True
    return False


def _split_union(text: str) -> list[str]:
    result=[]
    depth=0
    start=0
    for i,ch in enumerate(text):
        if(ch=="<"):
            depth+=1
        elif(ch==">"):
            depth=max(0, depth-1)
        elif(ch=="|" and depth==0):
            result.append(text[start:i].strip())
            start=i+1
    result.append(text[start:].strip())
    return [x for x in result if(x)]


def _plain_value(value: Value) -> str:
    if(value.kind=="TextLang"):
        return str(value.value["text"])
    if(value.kind in {"String", "Number", "Bool", "Identifier", "Raw"}):
        return str(value.value)
    return str(value.value)


def value_to_type_string(value: Value) -> str:
    """Compatibility helper for v0.6 schema diagnostics."""
    return infer_value_type(value)
