from __future__ import annotations

from typing import Any

from .ast_nodes import DocumentAst, Node, Value
from .diagnostics import Diagnostic
from .type_system import type_matches


def install_schema_semantics(doc: DocumentAst, registry: Any | None) -> None:
    doc.type_aliases=dict(getattr(registry, "type_aliases", {}) or {}) if(registry is not None) else {}
    doc.enum_types={k:list(v) for k,v in (getattr(registry, "enum_types", {}) or {}).items()} if(registry is not None) else {}
    doc.function_signatures=_collect_function_signatures(doc, registry)
    doc.relation_rules=dict(getattr(registry, "relation_rules", {}) or {}) if(registry is not None) else {}
    doc.semantic_edges=[]


def check_semantics(doc: DocumentAst) -> None:
    _check_function_calls(doc)
    _check_relation_rules(doc)
    doc.schema_info.setdefault("v07_semantic_features", {
        "type_aliases": len(getattr(doc, "type_aliases", {})),
        "enum_types": len(getattr(doc, "enum_types", {})),
        "function_signatures": len(getattr(doc, "function_signatures", {})),
        "relation_rules": len(getattr(doc, "relation_rules", {})),
        "semantic_edges": len(getattr(doc, "semantic_edges", [])),
    })


def _collect_function_signatures(doc: DocumentAst, registry: Any | None) -> dict[str, dict[str, Any]]:
    signatures={}
    if(registry is not None):
        for name,sig in (getattr(registry, "function_signatures", {}) or {}).items():
            if(isinstance(sig, dict)):
                signatures[name]=_normalize_signature(name, sig)
    for node in _walk(doc.children):
        if(node.kind!="Function" or not node.id):
            continue
        params=[]
        raw_params=node.fields.get("__params__")
        if(raw_params is not None and raw_params.kind=="Raw" and isinstance(raw_params.value, list)):
            for p in raw_params.value:
                if(isinstance(p, dict)):
                    params.append({"name": str(p.get("name", "")), "type": str(p.get("type", "Any") or "Any")})
        ret=node.fields.get("__return_type__")
        signatures[node.id]={
            "name": node.id,
            "params": params,
            "return": _plain(ret) or "Any",
            "source": "document",
            "line": node.line,
            "column": node.column,
        }
    return signatures


def _normalize_signature(name: str, sig: dict[str, Any]) -> dict[str, Any]:
    params=[]
    raw_params=sig.get("params", sig.get("parameters", []))
    if(isinstance(raw_params, dict)):
        for param_name,param_type in raw_params.items():
            params.append({"name": str(param_name), "type": str(param_type)})
    elif(isinstance(raw_params, list)):
        for item in raw_params:
            if(isinstance(item, dict)):
                params.append({"name": str(item.get("name", "")), "type": str(item.get("type", "Any") or "Any")})
            else:
                params.append({"name": "", "type": str(item)})
    return {
        "name": name,
        "params": params,
        "return": str(sig.get("return", sig.get("return_type", "Any")) or "Any"),
        "source": str(sig.get("source", "schema")),
        "description": str(sig.get("description", "")),
    }


def _check_function_calls(doc: DocumentAst) -> None:
    signatures=getattr(doc, "function_signatures", {})
    for owner,value in _iter_values(doc.children):
        _check_function_call_value(doc, owner, value, signatures)


def _check_function_call_value(doc: DocumentAst, owner: Node, value: Value, signatures: dict[str, dict[str, Any]]) -> None:
    if(value.kind=="FunctionCall"):
        name=str(value.value.get("name"))
        args=list(value.value.get("args", []))
        if(name in {"Date", "Time", "DateTime"}):
            if(len(args)!=1):
                doc.diagnostics.append(Diagnostic("error", "E_FUNCTION_ARITY", f"{name} expects 1 argument(s), got {len(args)}", value.line, value.column))
            elif(args[0].kind not in {"String", "TextLang"}):
                doc.diagnostics.append(Diagnostic("error", "E_FUNCTION_ARG_TYPE", f"{name}.value: expected Text, got {args[0].kind}", args[0].line, args[0].column))
        else:
            sig=signatures.get(name)
            if(sig is None):
                doc.diagnostics.append(Diagnostic("warning", "W_UNKNOWN_FUNCTION_CALL", f"Function call has no signature: {name}", value.line, value.column))
            else:
                params=list(sig.get("params", []))
                if(len(args)!=len(params)):
                    doc.diagnostics.append(Diagnostic("error", "E_FUNCTION_ARITY", f"{name} expects {len(params)} argument(s), got {len(args)}", value.line, value.column))
                for idx,arg in enumerate(args[:len(params)]):
                    expected=str(params[idx].get("type", "Any") or "Any")
                    result=type_matches(arg, expected, doc)
                    if(not result.ok):
                        param_name=str(params[idx].get("name", idx+1))
                        doc.diagnostics.append(Diagnostic("error", "E_FUNCTION_ARG_TYPE", f"{name}.{param_name}: {result.reason}", arg.line, arg.column))
    for child in _children(value):
        _check_function_call_value(doc, owner, child, signatures)


def _check_relation_rules(doc: DocumentAst) -> None:
    rules=getattr(doc, "relation_rules", {}) or {}
    for node in _walk(doc.children):
        for field_name,value in node.fields.items():
            if(field_name.startswith("__")):
                continue
            rule=_find_relation_rule(rules, node, field_name)
            if(rule is None and not _looks_like_reference_value(value)):
                continue
            targets=_extract_references(value)
            for target_name in targets:
                target_id=getattr(doc, "reference_aliases", {}).get(target_name, target_name)
                target=doc.symbols.get(target_id)
                if(target is not None):
                    getattr(doc, "semantic_edges", []).append({"from": node.id or f"{node.kind}@{node.line}:{node.column}", "from_kind": node.kind, "field": field_name.rstrip("?"), "to": target_id, "to_kind": target.kind, "to_type": target.type_name})
                if(rule is None):
                    continue
                if(target is None):
                    level=_rule_level(rule, "error")
                    doc.diagnostics.append(Diagnostic(level, _code(level, "RELATION_UNDEFINED_TARGET"), f"{node.kind}.{field_name} refers to undefined id: {target_name}", value.line, value.column))
                    continue
                allowed=_as_list(rule.get("target", rule.get("targets", rule.get("target_kinds", []))))
                if(allowed and not any(_target_allowed(target, str(item), doc) for item in allowed)):
                    level=_rule_level(rule, "error")
                    doc.diagnostics.append(Diagnostic(level, _code(level, "RELATION_TARGET_TYPE"), f"{node.kind}.{field_name} expects target {allowed}, got {target.kind}/{target.type_name}: {target_id}", value.line, value.column))


def _find_relation_rule(rules: dict[str, Any], node: Node, field_name: str) -> dict[str, Any] | None:
    normalized=field_name.rstrip("?")
    for key in [f"{node.kind}.{normalized}", f"{node.type_name}.{normalized}" if(node.type_name) else "", normalized]:
        if(key and isinstance(rules.get(key), dict)):
            return rules[key]
    return None


def _extract_references(value: Value) -> list[str]:
    if(value.kind in {"Identifier", "String"}):
        return [str(value.value)]
    if(value.kind=="TextLang"):
        return [str(value.value["text"])]
    if(value.kind=="List"):
        result=[]
        for item in value.value:
            result.extend(_extract_references(item))
        return result
    return []



def _looks_like_reference_value(value: Value) -> bool:
    if(value.kind=="Identifier"):
        return True
    if(value.kind=="List"):
        return all(_looks_like_reference_value(item) for item in value.value) if(value.value) else False
    return False

def _target_allowed(target: Node, allowed: str, doc: DocumentAst) -> bool:
    allowed=allowed.strip()
    if(allowed in {"Any", ""}):
        return True
    if("|" in allowed and not allowed.startswith("Union<")):
        return any(_target_allowed(target, part, doc) for part in allowed.split("|"))
    return target.kind==allowed or (target.type_name or "")==allowed


def _iter_values(nodes: list[Node]):
    for node in _walk(nodes):
        for value in node.fields.values():
            yield node,value


def _walk(nodes: list[Node]):
    for node in nodes:
        yield node
        yield from _walk(node.children)


def _children(value: Value) -> list[Value]:
    if(value.kind=="List"):
        return list(value.value)
    if(value.kind=="Object"):
        return list(value.value.values())
    if(value.kind=="FunctionCall"):
        return list(value.value.get("args", []))
    return []


def _plain(value: Value | None) -> str:
    if(value is None):
        return ""
    if(value.kind=="TextLang"):
        return str(value.value["text"])
    if(value.kind in {"String", "Identifier", "Raw"}):
        return str(value.value)
    return str(value.value)


def _as_list(value: Any) -> list[Any]:
    if(value is None):
        return []
    if(isinstance(value, list)):
        return value
    return [value]


def _rule_level(rule: dict[str, Any], default: str) -> str:
    value=str(rule.get("level", rule.get("severity", default))).lower()
    if(value in {"warn", "warning"}):
        return "warning"
    return "error" if(value=="error") else default


def _code(level: str, base: str) -> str:
    return ("E_" if(level=="error") else "W_")+base
