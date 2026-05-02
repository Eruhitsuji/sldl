from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Value:
    kind: str
    value: Any = None
    line: int = 0
    column: int = 0

    def to_dict(self) -> Any:
        if(self.kind=="TextLang"):
            return {
                "kind": self.kind,
                "text": self.value["text"],
                "lang": self.value["lang"],
            }
        if(self.kind=="String"):
            return {"kind": self.kind, "value": self.value}
        if(self.kind=="Number"):
            return {"kind": self.kind, "value": self.value}
        if(self.kind=="Bool"):
            return {"kind": self.kind, "value": self.value}
        if(self.kind=="Null"):
            return {"kind": self.kind, "value": None}
        if(self.kind=="Identifier"):
            return {"kind": self.kind, "name": self.value}
        if(self.kind=="List"):
            return {"kind": self.kind, "items": [v.to_dict() for v in self.value]}
        if(self.kind=="Object"):
            return {"kind": self.kind, "fields": {k: v.to_dict() for k,v in self.value.items()}}
        if(self.kind=="FunctionCall"):
            return {
                "kind": self.kind,
                "name": self.value["name"],
                "args": [v.to_dict() for v in self.value["args"]],
            }
        if(self.kind=="Raw"):
            return {"kind": self.kind, "value": self.value}
        return {"kind": self.kind, "value": self.value}


@dataclass
class Node:
    kind: str
    id: str | None = None
    type_name: str | None = None
    fields: dict[str, Value] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    line: int = 0
    column: int = 0

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "id": self.id,
            "type": self.type_name,
            "fields": {k: v.to_dict() for k,v in self.fields.items()},
            "children": [c.to_dict() for c in self.children],
        }


@dataclass
class DocumentAst:
    id: str
    type_name: str
    meta: Node | None = None
    children: list[Node] = field(default_factory=list)
    symbols: dict[str, Node] = field(default_factory=dict)
    reference_aliases: dict[str, str] = field(default_factory=dict)
    diagnostics: list[Any] = field(default_factory=list)
    schema_info: dict[str, Any] = field(default_factory=dict)
    line: int = 0
    column: int = 0

    def to_dict(self) -> dict:
        return {
            "sldl_version": "0.9",
            "document": {
                "id": self.id,
                "type": self.type_name,
                "meta": self.meta.to_dict() if(self.meta is not None) else None,
                "nodes": [c.to_dict() for c in self.children],
                "symbols": sorted(list(self.symbols.keys())),
                "reference_aliases": dict(sorted(self.reference_aliases.items())),
                "bibliography": self.bibliography_map(),
                "schema": dict(self.schema_info),
                "type_aliases": dict(getattr(self, "type_aliases", {})),
                "enum_types": dict(getattr(self, "enum_types", {})),
                "function_signatures": dict(getattr(self, "function_signatures", {})),
                "semantic_edges": list(getattr(self, "semantic_edges", [])),
                "logic": getattr(self, "logic", {}),
            },
            "diagnostics": [
                d.to_dict() if(hasattr(d, "to_dict")) else d
                for d in self.diagnostics
            ],
        }

    def bibliography_map(self) -> dict[str, Any]:
        references=[]
        bibtex_key_to_sldl_id={}
        sldl_id_to_bibtex_key={}
        for node_id,node in sorted(self.symbols.items()):
            if(node.kind!="Reference"):
                continue
            bibtex_key=_value_plain(node.fields.get("bibkey")) or node_id
            aliases=sorted(alias for alias,target in self.reference_aliases.items() if(target==node_id))
            if(bibtex_key):
                bibtex_key_to_sldl_id[bibtex_key]=node_id
                sldl_id_to_bibtex_key[node_id]=bibtex_key
            references.append({
                "sldl_id": node_id,
                "bibtex_key": bibtex_key,
                "aliases": aliases,
            })
        return {
            "bibtex_key_to_sldl_id": bibtex_key_to_sldl_id,
            "sldl_id_to_bibtex_key": sldl_id_to_bibtex_key,
            "references": references,
        }


def _value_plain(value: Value | None) -> str:
    if(value is None):
        return ""
    if(value.kind=="TextLang"):
        return str(value.value["text"])
    if(value.kind in {"String", "Number", "Bool", "Identifier", "Raw"}):
        return str(value.value)
    if(value.kind=="List"):
        return ", ".join(_value_plain(v) for v in value.value)
    if(value.kind=="Object"):
        return ", ".join(f"{k}={_value_plain(v)}" for k,v in value.value.items())
    if(value.kind=="FunctionCall"):
        return f"{value.value['name']}("+", ".join(_value_plain(v) for v in value.value["args"])+")"
    return str(value.value)
