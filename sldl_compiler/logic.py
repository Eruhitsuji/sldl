from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .ast_nodes import DocumentAst, Node, Value
from .diagnostics import Diagnostic

DEFAULT_LOGIC_RULES={
    "enabled": True,
    "require_grounded_claims": "warning",
    "require_grounded_conclusions": "warning",
    "support_cycle_policy": "warning",
    "accepted_contradiction_policy": "warning",
    "rejected_support_policy": "warning",
    "counterargument_support_policy": "warning",
    "evidence_source_policy": "allow",
    "confidence_policy": "warning",
    "accepted_statuses": ["accepted", "supported", "validated", "confirmed", "採用", "支持", "確認済み"],
    "rejected_statuses": ["rejected", "unsupported", "refuted", "falsified", "棄却", "不支持", "反証"],
}

POSITIVE_FIELDS={"evidence", "based_on", "supports", "depends_on", "requires"}
NEGATIVE_FIELDS={"against", "contradicts"}
RESPONSE_FIELDS={"rebuts", "responds_to"}
SOURCE_FIELDS={"source", "cite", "cites"}
REVERSE_SUPPORT_FIELDS={"evidence", "based_on", "source", "cite", "cites", "depends_on", "requires"}
LOGIC_REFERENCE_FIELDS=POSITIVE_FIELDS | NEGATIVE_FIELDS | RESPONSE_FIELDS | SOURCE_FIELDS

FIELD_RELATION={
    "evidence": "evidence_for",
    "based_on": "basis_for",
    "supports": "supports",
    "depends_on": "depends_on",
    "requires": "requires",
    "against": "against",
    "contradicts": "contradicts",
    "rebuts": "rebuts",
    "responds_to": "responds_to",
    "source": "source",
    "cite": "cites",
    "cites": "cites",
}

SUPPORTED_TARGET_KINDS={
    "evidence": {"Evidence", "Reference"},
    "based_on": {"Claim", "Reason", "Evidence", "Reference", "Conclusion", "Definition", "Table", "Figure", "Chart"},
    "supports": {"Claim", "Conclusion", "Reason"},
    "depends_on": {"Claim", "Reason", "Evidence", "Conclusion", "Definition", "Object", "Function", "Table", "Figure", "Chart"},
    "requires": {"Claim", "Reason", "Evidence", "Conclusion", "Definition", "Object", "Function", "Table", "Figure", "Chart"},
    "against": {"Claim", "Reason", "Conclusion", "Counterargument"},
    "contradicts": {"Claim", "Reason", "Conclusion", "Counterargument"},
    "rebuts": {"Counterargument", "Claim", "Reason", "Conclusion"},
    "responds_to": {"Counterargument", "Claim", "Reason", "Conclusion"},
    "source": {"Reference"},
    "cite": {"Reference"},
    "cites": {"Reference"},
}

POLICY_LEVELS={"warn": "warning", "warning": "warning", "error": "error", "allow": "allow", "off": "allow", "none": "allow"}


@dataclass
class LogicEdge:
    source: str
    target: str
    relation: str
    polarity: str
    field: str
    source_kind: str
    target_kind: str

    def to_dict(self) -> dict[str, str]:
        return {
            "source": self.source,
            "target": self.target,
            "relation": self.relation,
            "polarity": self.polarity,
            "field": self.field,
            "source_kind": self.source_kind,
            "target_kind": self.target_kind,
        }


def run_logic_checks(doc: DocumentAst, registry: Any | None = None) -> None:
    rules=_logic_rules(registry)
    if(not rules.get("enabled", True)):
        doc.logic={"enabled": False, "summary": {}, "graph": {"nodes": [], "edges": []}, "cycles": [], "grounded": {}}
        return
    nodes={node_id:node for node_id,node in doc.symbols.items()}
    edges=[]
    _collect_edges_from_semantic_edges(doc, nodes, edges)
    _collect_edges_from_fields(doc, nodes, edges)
    edges=_dedupe_edges(edges)
    grounded=_compute_grounded(nodes, edges, rules)
    cycles=_find_positive_cycles(edges)
    _check_logic_references(doc, nodes)
    _check_semantic_edges(doc, nodes)
    _check_target_kinds(doc, nodes, edges)
    _check_grounding(doc, nodes, grounded, rules)
    _check_cycles(doc, nodes, cycles, rules)
    _check_status_consistency(doc, nodes, edges, rules)
    _check_counterarguments(doc, nodes, grounded, rules)
    _check_evidence_sources(doc, nodes, edges, rules)
    _check_confidence_values(doc, nodes, rules)
    doc.logic={
        "enabled": True,
        "summary": _summary(nodes, edges, grounded, cycles),
        "graph": {
            "nodes": [
                {"id": node_id, "kind": node.kind, "type": node.type_name}
                for node_id,node in sorted(nodes.items())
                if(_is_logic_node(node))
            ],
            "edges": [edge.to_dict() for edge in edges],
        },
        "grounded": dict(sorted(grounded.items())),
        "cycles": cycles,
    }


def export_logic_report(doc: DocumentAst, source_edge_direction: str = "reference-to-evidence") -> str:
    logic=getattr(doc, "logic", {}) or {}
    summary=logic.get("summary", {})
    graph=logic.get("graph", {})
    edges=_display_edges(graph.get("edges", []), source_edge_direction)
    lines=[]
    lines.append(f"# SLDL Logic Report: {doc.id}")
    lines.append("")
    lines.append(f"- document_type: `{doc.type_name}`")
    lines.append(f"- logic_nodes: {summary.get('logic_nodes', 0)}")
    lines.append(f"- logic_edges: {summary.get('logic_edges', 0)}")
    lines.append(f"- claims: {summary.get('claims', 0)}")
    lines.append(f"- grounded_claims: {summary.get('grounded_claims', 0)}")
    lines.append(f"- conclusions: {summary.get('conclusions', 0)}")
    lines.append(f"- grounded_conclusions: {summary.get('grounded_conclusions', 0)}")
    lines.append(f"- cycles: {summary.get('cycles', 0)}")
    lines.append(f"- evidence: {summary.get('evidence', 0)}")
    lines.append(f"- sourced_evidence: {summary.get('sourced_evidence', 0)}")
    lines.append(f"- counterarguments: {summary.get('counterarguments', 0)}")
    lines.append(f"- negative_edges: {summary.get('negative_edges', 0)}")
    lines.append(f"- response_edges: {summary.get('response_edges', 0)}")
    lines.append("")
    lines.append("## Edges")
    lines.append("")
    if(edges):
        for edge in edges:
            lines.append(f"- `{edge['source']}` --{edge['relation']}--> `{edge['target']}` ({edge['polarity']})")
    else:
        lines.append("- No logic edges.")
    grounded=logic.get("grounded", {})
    lines.append("")
    lines.append("## Claims and Conclusions")
    lines.append("")
    claim_rows=[]
    for node_id,node in sorted(doc.symbols.items()):
        if(node.kind in {"Claim", "Conclusion"}):
            incoming_support=sum(1 for edge in graph.get("edges", []) if(edge.get("target")==node_id and edge.get("polarity") in {"positive", "source"}))
            incoming_negative=sum(1 for edge in graph.get("edges", []) if(edge.get("target")==node_id and edge.get("polarity")=="negative"))
            status=_node_status(node) or "-"
            confidence=_plain(node.fields.get("confidence")) or "-"
            claim_rows.append((node_id, node.kind, grounded.get(node_id, False), incoming_support, incoming_negative, status, confidence))
    if(claim_rows):
        lines.append("| id | kind | grounded | incoming_support | incoming_negative | status | confidence |")
        lines.append("| --- | --- | ---: | ---: | ---: | --- | ---: |")
        for row in claim_rows:
            lines.append(f"| `{row[0]}` | {row[1]} | {str(row[2]).lower()} | {row[3]} | {row[4]} | `{row[5]}` | {row[6]} |")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Contradictions and Responses")
    lines.append("")
    negative_edges=[edge for edge in edges if(edge.get("polarity")=="negative")]
    response_edges=[edge for edge in edges if(edge.get("polarity")=="response")]
    if(negative_edges):
        lines.append("### Negative edges")
        lines.append("")
        for edge in negative_edges:
            lines.append(f"- `{edge['source']}` --{edge['relation']}--> `{edge['target']}`")
    else:
        lines.append("- Negative edges: none.")
    lines.append("")
    if(response_edges):
        lines.append("### Response edges")
        lines.append("")
        for edge in response_edges:
            lines.append(f"- `{edge['source']}` --{edge['relation']}--> `{edge['target']}`")
    else:
        lines.append("- Response edges: none.")
    lines.append("")
    lines.append("## Diagnostics")
    lines.append("")
    if(doc.diagnostics):
        for diag in doc.diagnostics:
            lines.append(f"- `{diag.level}` `{diag.code}`: {diag.message}")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Ungrounded Claims and Conclusions")
    lines.append("")
    ungrounded=[]
    for node_id,node in sorted(doc.symbols.items()):
        if(node.kind in {"Claim", "Conclusion"} and not grounded.get(node_id, False)):
            ungrounded.append(node_id)
    if(ungrounded):
        for node_id in ungrounded:
            lines.append(f"- `{node_id}`")
    else:
        lines.append("- None.")
    lines.append("")
    lines.append("## Cycles")
    lines.append("")
    cycles=logic.get("cycles", [])
    if(cycles):
        for cycle in cycles:
            lines.append("- "+" -> ".join(f"`{x}`" for x in cycle))
    else:
        lines.append("- None.")
    lines.append("")
    return "\n".join(lines)


def export_logic_mermaid(doc: DocumentAst, source_edge_direction: str = "reference-to-evidence") -> str:
    graph=(getattr(doc, "logic", {}) or {}).get("graph", {})
    lines=["flowchart TD"]
    nodes={n["id"]:n for n in graph.get("nodes", [])}
    for node_id,node in sorted(nodes.items()):
        label=_escape_mermaid_label(f"{node_id}\\n{node.get('kind','')}")
        lines.append(f"  {safe_mermaid_id(node_id)}[\"{label}\"]")
    for edge in _display_edges(graph.get("edges", []), source_edge_direction):
        src=safe_mermaid_id(edge["source"])
        dst=safe_mermaid_id(edge["target"])
        label=_escape_mermaid_label(edge["relation"])
        if(edge.get("polarity")=="negative"):
            lines.append(f"  {src} -. {label} .-> {dst}")
        else:
            lines.append(f"  {src} -- {label} --> {dst}")
    return "\n".join(lines)+"\n"


def _display_edges(edges: list[dict[str, str]], source_edge_direction: str = "reference-to-evidence") -> list[dict[str, str]]:
    direction=source_edge_direction or "reference-to-evidence"
    if(direction not in {"reference-to-evidence", "evidence-to-reference"}):
        raise ValueError("source_edge_direction must be 'reference-to-evidence' or 'evidence-to-reference'")
    out=[]
    for edge in edges:
        item=dict(edge)
        if(direction=="evidence-to-reference" and item.get("polarity")=="source"):
            item["source"],item["target"]=item["target"],item["source"]
            item["source_kind"],item["target_kind"]=item.get("target_kind", ""),item.get("source_kind", "")
        out.append(item)
    return out


def safe_mermaid_id(value: str) -> str:
    out=[]
    for ch in value:
        if(ch.isalnum() or ch=="_"):
            out.append(ch)
        else:
            out.append("_")
    result="".join(out)
    if(not result):
        return "node"
    if(result[0].isdigit()):
        return "n_"+result
    return result


def _escape_mermaid_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', "'")


def _logic_rules(registry: Any | None) -> dict[str, Any]:
    rules=dict(DEFAULT_LOGIC_RULES)
    if(registry is not None):
        custom=getattr(registry, "logic_rules", {}) or {}
        if(isinstance(custom, dict)):
            rules.update(custom)
    return rules


def _collect_edges_from_semantic_edges(doc: DocumentAst, nodes: dict[str, Node], out: list[LogicEdge]) -> None:
    for item in getattr(doc, "semantic_edges", []) or []:
        if(not isinstance(item, dict)):
            continue
        src=item.get("source", item.get("from"))
        dst=item.get("target", item.get("to"))
        field=item.get("field", item.get("relation", ""))
        if(src in nodes and dst in nodes and field in LOGIC_REFERENCE_FIELDS):
            out.append(_make_edge(src, dst, field, nodes))


def _collect_edges_from_fields(doc: DocumentAst, nodes: dict[str, Node], out: list[LogicEdge]) -> None:
    for node_id,node in nodes.items():
        if(not _is_logic_node(node)):
            continue
        for field,value in node.fields.items():
            if(field not in LOGIC_REFERENCE_FIELDS):
                continue
            for target_id in _targets_from_value(value, doc):
                if(target_id in nodes):
                    out.append(_make_edge(node_id, target_id, field, nodes))


def _make_edge(src: str, dst: str, field: str, nodes: dict[str, Node]) -> LogicEdge:
    if(field in NEGATIVE_FIELDS):
        polarity="negative"
    elif(field in RESPONSE_FIELDS):
        polarity="response"
    elif(field in SOURCE_FIELDS):
        polarity="source"
    else:
        polarity="positive"
    actual_src,actual_dst=(dst,src) if(field in REVERSE_SUPPORT_FIELDS) else (src,dst)
    return LogicEdge(actual_src, actual_dst, FIELD_RELATION.get(field, field), polarity, field, nodes[actual_src].kind, nodes[actual_dst].kind)


def _dedupe_edges(edges: list[LogicEdge]) -> list[LogicEdge]:
    seen=set()
    out=[]
    for edge in edges:
        key=(edge.source, edge.target, edge.field, edge.relation)
        if(key in seen):
            continue
        seen.add(key)
        out.append(edge)
    out.sort(key=lambda e:(e.source, e.relation, e.target))
    return out


def _targets_from_value(value: Value, doc: DocumentAst) -> list[str]:
    values=[]
    if(value.kind=="Identifier"):
        values.append(str(value.value))
    elif(value.kind=="String"):
        values.append(str(value.value))
    elif(value.kind=="List"):
        for item in value.value:
            values.extend(_targets_from_value(item, doc))
    elif(value.kind=="Object"):
        for item in value.value.values():
            values.extend(_targets_from_value(item, doc))
    resolved=[]
    for item in values:
        resolved.append(doc.reference_aliases.get(item, item))
    return resolved


def _check_logic_references(doc: DocumentAst, nodes: dict[str, Node]) -> None:
    for node_id,node in nodes.items():
        if(not _is_logic_node(node)):
            continue
        for field,value in node.fields.items():
            if(field not in LOGIC_REFERENCE_FIELDS):
                continue
            for raw_target in _raw_targets_from_value(value):
                target=doc.reference_aliases.get(raw_target, raw_target)
                if(target not in nodes):
                    doc.diagnostics.append(Diagnostic("error", "E_LOGIC_UNDEFINED_REFERENCE", f"{node.kind}.{field} refers to undefined logic/reference id: {raw_target}", value.line, value.column))


def _raw_targets_from_value(value: Value) -> list[str]:
    if(value.kind in {"Identifier", "String"}):
        return [str(value.value)]
    if(value.kind=="List"):
        out=[]
        for item in value.value:
            out.extend(_raw_targets_from_value(item))
        return out
    if(value.kind=="Object"):
        out=[]
        for item in value.value.values():
            out.extend(_raw_targets_from_value(item))
        return out
    return []


def _check_semantic_edges(doc: DocumentAst, nodes: dict[str, Node]) -> None:
    for item in getattr(doc, "semantic_edges", []) or []:
        if(not isinstance(item, dict)):
            continue
        src=item.get("source", item.get("from"))
        dst=item.get("target", item.get("to"))
        field=item.get("field", item.get("relation", ""))
        line=int(item.get("line", 0) or 0) if(isinstance(item, dict)) else 0
        column=int(item.get("column", 0) or 0) if(isinstance(item, dict)) else 0
        if(field not in LOGIC_REFERENCE_FIELDS):
            continue
        src_node=nodes.get(src)
        if(src_node is not None and not _is_logic_node(src_node)):
            continue
        if(src not in nodes and isinstance(src, str) and "@" in src):
            continue
        if(src not in nodes):
            doc.diagnostics.append(Diagnostic("error", "E_LOGIC_UNDEFINED_ENDPOINT", f"logic edge source is undefined: {src}", line, column))
        if(dst not in nodes):
            doc.diagnostics.append(Diagnostic("error", "E_LOGIC_UNDEFINED_ENDPOINT", f"logic edge target is undefined: {dst}", line, column))


def _check_target_kinds(doc: DocumentAst, nodes: dict[str, Node], edges: list[LogicEdge]) -> None:
    for edge in edges:
        allowed=SUPPORTED_TARGET_KINDS.get(edge.field)
        if(allowed is None):
            continue
        if(edge.field in REVERSE_SUPPORT_FIELDS):
            target_kind=edge.source_kind
            target_id=edge.source
            owner_kind=edge.target_kind
            owner_id=edge.target
        else:
            target_kind=edge.target_kind
            target_id=edge.target
            owner_kind=edge.source_kind
            owner_id=edge.source
        if(target_kind not in allowed):
            doc.diagnostics.append(Diagnostic("error", "E_LOGIC_INVALID_TARGET_KIND", f"{owner_kind}.{edge.field} expects one of {sorted(allowed)}, but got {target_kind}: {target_id}", nodes[owner_id].line, nodes[owner_id].column))


def _compute_grounded(nodes: dict[str, Node], edges: list[LogicEdge], rules: dict[str, Any]) -> dict[str, bool]:
    grounded={node_id: node.kind in {"Evidence", "Reference", "Table", "Figure", "Chart"} for node_id,node in nodes.items()}
    if(_policy(rules.get("evidence_source_policy")) in {"warning", "error"}):
        sourced_evidence={edge.target for edge in edges if(edge.field in SOURCE_FIELDS and edge.source_kind=="Reference")}
        for node_id,node in nodes.items():
            if(node.kind=="Evidence"):
                grounded[node_id]=node_id in sourced_evidence
    changed=True
    while(changed):
        changed=False
        for edge in edges:
            if(edge.polarity in {"positive", "source"} and grounded.get(edge.target, False) is False and grounded.get(edge.source, False)):
                grounded[edge.target]=True
                changed=True
    return grounded


def _check_grounding(doc: DocumentAst, nodes: dict[str, Node], grounded: dict[str, bool], rules: dict[str, Any]) -> None:
    claim_level=_policy(rules.get("require_grounded_claims", "warning"))
    conclusion_level=_policy(rules.get("require_grounded_conclusions", "warning"))
    if(claim_level!="allow"):
        for node_id,node in nodes.items():
            if(node.kind=="Claim" and not grounded.get(node_id, False)):
                doc.diagnostics.append(Diagnostic(claim_level, "W_LOGIC_UNGROUNDED_CLAIM" if(claim_level=="warning") else "E_LOGIC_UNGROUNDED_CLAIM", f"Claim is not grounded by Evidence/Reference through the logic graph: {node_id}", node.line, node.column))
    if(conclusion_level!="allow"):
        for node_id,node in nodes.items():
            if(node.kind=="Conclusion" and not grounded.get(node_id, False)):
                doc.diagnostics.append(Diagnostic(conclusion_level, "W_LOGIC_UNGROUNDED_CONCLUSION" if(conclusion_level=="warning") else "E_LOGIC_UNGROUNDED_CONCLUSION", f"Conclusion is not grounded by Evidence/Reference through the logic graph: {node_id}", node.line, node.column))


def _find_positive_cycles(edges: list[LogicEdge]) -> list[list[str]]:
    graph={}
    for edge in edges:
        if(edge.polarity=="positive"):
            graph.setdefault(edge.source, []).append(edge.target)
    cycles=[]
    cycle_keys=set()
    seen=set()
    stack=[]
    on_stack=set()

    def dfs(node: str) -> None:
        seen.add(node)
        stack.append(node)
        on_stack.add(node)
        for nxt in graph.get(node, []):
            if(nxt not in seen):
                dfs(nxt)
            elif(nxt in on_stack):
                idx=stack.index(nxt)
                cycle=stack[idx:]+[nxt]
                key=_cycle_key(cycle)
                if(key not in cycle_keys):
                    cycle_keys.add(key)
                    cycles.append(cycle)
        stack.pop()
        on_stack.remove(node)

    for node in list(graph.keys()):
        if(node not in seen):
            dfs(node)
    return cycles


def _cycle_key(cycle: list[str]) -> tuple[str, ...]:
    body=cycle[:-1] if(len(cycle)>1 and cycle[0]==cycle[-1]) else cycle[:]
    if(not body):
        return tuple()
    rotations=[tuple(body[i:]+body[:i]) for i in range(len(body))]
    rev=list(reversed(body))
    rotations.extend(tuple(rev[i:]+rev[:i]) for i in range(len(rev)))
    return min(rotations)


def _check_cycles(doc: DocumentAst, nodes: dict[str, Node], cycles: list[list[str]], rules: dict[str, Any]) -> None:
    level=_policy(rules.get("support_cycle_policy", "warning"))
    if(level=="allow"):
        return
    for cycle in cycles:
        first=cycle[0]
        node=nodes.get(first)
        doc.diagnostics.append(Diagnostic(level, "W_LOGIC_SUPPORT_CYCLE" if(level=="warning") else "E_LOGIC_SUPPORT_CYCLE", "Circular positive support/dependency path: "+" -> ".join(cycle), node.line if(node) else 0, node.column if(node) else 0))


def _check_status_consistency(doc: DocumentAst, nodes: dict[str, Node], edges: list[LogicEdge], rules: dict[str, Any]) -> None:
    accepted=set(str(x).lower() for x in rules.get("accepted_statuses", []))
    rejected=set(str(x).lower() for x in rules.get("rejected_statuses", []))
    contradiction_level=_policy(rules.get("accepted_contradiction_policy", "warning"))
    rejected_level=_policy(rules.get("rejected_support_policy", "warning"))
    for edge in edges:
        if(edge.polarity=="negative" and contradiction_level!="allow"):
            if(_node_status(nodes[edge.source]).lower() in accepted and _node_status(nodes[edge.target]).lower() in accepted):
                doc.diagnostics.append(Diagnostic(contradiction_level, "W_LOGIC_ACCEPTED_CONTRADICTION" if(contradiction_level=="warning") else "E_LOGIC_ACCEPTED_CONTRADICTION", f"Accepted/supported nodes contradict each other: {edge.source} -> {edge.target}", nodes[edge.source].line, nodes[edge.source].column))
        if(edge.polarity=="positive" and rejected_level!="allow"):
            if(_node_status(nodes[edge.source]).lower() in rejected):
                doc.diagnostics.append(Diagnostic(rejected_level, "W_LOGIC_REJECTED_SUPPORT" if(rejected_level=="warning") else "E_LOGIC_REJECTED_SUPPORT", f"Rejected/refuted node is used as positive support: {edge.source} -> {edge.target}", nodes[edge.source].line, nodes[edge.source].column))


def _check_counterarguments(doc: DocumentAst, nodes: dict[str, Node], grounded: dict[str, bool], rules: dict[str, Any]) -> None:
    level=_policy(rules.get("counterargument_support_policy", "warning"))
    if(level=="allow"):
        return
    for node_id,node in nodes.items():
        if(node.kind!="Counterargument"):
            continue
        if("against" not in node.fields and "contradicts" not in node.fields):
            doc.diagnostics.append(Diagnostic(level, "W_LOGIC_COUNTERARGUMENT_WITHOUT_TARGET" if(level=="warning") else "E_LOGIC_COUNTERARGUMENT_WITHOUT_TARGET", f"Counterargument has no target: {node_id}", node.line, node.column))
        if(not grounded.get(node_id, False) and not any(k in node.fields for k in ["evidence", "source", "cite", "based_on"])):
            doc.diagnostics.append(Diagnostic(level, "W_LOGIC_UNGROUNDED_COUNTERARGUMENT" if(level=="warning") else "E_LOGIC_UNGROUNDED_COUNTERARGUMENT", f"Counterargument is not grounded: {node_id}", node.line, node.column))


def _check_evidence_sources(doc: DocumentAst, nodes: dict[str, Node], edges: list[LogicEdge], rules: dict[str, Any]) -> None:
    level=_policy(rules.get("evidence_source_policy", "allow"))
    if(level=="allow"):
        return
    sourced={edge.target for edge in edges if(edge.field in SOURCE_FIELDS and edge.source_kind=="Reference")}
    for node_id,node in nodes.items():
        if(node.kind=="Evidence" and node_id not in sourced):
            doc.diagnostics.append(Diagnostic(level, "W_LOGIC_EVIDENCE_WITHOUT_SOURCE" if(level=="warning") else "E_LOGIC_EVIDENCE_WITHOUT_SOURCE", f"Evidence has no Reference source/cite: {node_id}", node.line, node.column))


def _check_confidence_values(doc: DocumentAst, nodes: dict[str, Node], rules: dict[str, Any]) -> None:
    level=_policy(rules.get("confidence_policy", "warning"))
    if(level=="allow"):
        return
    for node_id,node in nodes.items():
        value=node.fields.get("confidence")
        if(value is None):
            continue
        try:
            v=float(value.value)
        except Exception:
            continue
        if(v<0 or v>1):
            doc.diagnostics.append(Diagnostic(level, "W_LOGIC_CONFIDENCE_RANGE" if(level=="warning") else "E_LOGIC_CONFIDENCE_RANGE", f"confidence should be in the range 0..1: {node_id} = {v}", value.line, value.column))


def _node_status(node: Node) -> str:
    return _plain(node.fields.get("status"))


def _plain(value: Value | None) -> str:
    if(value is None):
        return ""
    if(value.kind=="TextLang"):
        return str(value.value.get("text", ""))
    if(value.kind in {"String", "Identifier", "Number", "Bool", "Raw"}):
        return str(value.value)
    return ""


def _policy(value: Any) -> str:
    return POLICY_LEVELS.get(str(value).lower(), "warning")


def _is_logic_node(node: Node) -> bool:
    return node.kind in {"Claim", "Reason", "Evidence", "Conclusion", "Counterargument", "Reference", "Definition", "Table", "Figure", "Chart"}


def _summary(nodes: dict[str, Node], edges: list[LogicEdge], grounded: dict[str, bool], cycles: list[list[str]]) -> dict[str, int]:
    sourced_evidence={edge.target for edge in edges if(edge.polarity=="source" and edge.source_kind=="Reference" and edge.target_kind=="Evidence")}
    return {
        "logic_nodes": sum(1 for node in nodes.values() if(_is_logic_node(node))),
        "logic_edges": len(edges),
        "claims": sum(1 for node in nodes.values() if(node.kind=="Claim")),
        "grounded_claims": sum(1 for node_id,node in nodes.items() if(node.kind=="Claim" and grounded.get(node_id, False))),
        "conclusions": sum(1 for node in nodes.values() if(node.kind=="Conclusion")),
        "grounded_conclusions": sum(1 for node_id,node in nodes.items() if(node.kind=="Conclusion" and grounded.get(node_id, False))),
        "evidence": sum(1 for node in nodes.values() if(node.kind=="Evidence")),
        "sourced_evidence": len(sourced_evidence),
        "counterarguments": sum(1 for node in nodes.values() if(node.kind=="Counterargument")),
        "references": sum(1 for node in nodes.values() if(node.kind=="Reference")),
        "positive_edges": sum(1 for edge in edges if(edge.polarity=="positive")),
        "negative_edges": sum(1 for edge in edges if(edge.polarity=="negative")),
        "response_edges": sum(1 for edge in edges if(edge.polarity=="response")),
        "source_edges": sum(1 for edge in edges if(edge.polarity=="source")),
        "cycles": len(cycles),
    }
