from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any

from .ast_nodes import DocumentAst, Node, Value
from .diagnostics import Diagnostic
from .export_support import walk_nodes
from .type_system import type_matches, value_to_type_string


DEFAULT_NODE_FIELD_TYPES: dict[str, dict[str, str]]={
    "Meta": {"title": "Text", "subtitle": "Text", "author": "Text", "date": "Date|Text", "lang": "Text", "version": "Text", "bibliography": "Text|List<Text>", "bibliographies": "List<Text>", "bibtex": "Text|List<Text>", "bibtex_file": "Text", "bibtex_files": "List<Text>"},
    "Section": {"title": "Text"},
    "Paragraph": {"text": "Text", "cite": "List<Ref<Reference>>|Ref<Reference>"},
    "Claim": {"text": "Text", "evidence": "List<Union<Ref<Evidence>|Ref<Reference>|Ref<Table>|Ref<Figure>>>|Ref<Evidence>|Ref<Reference>|Ref<Table>|Ref<Figure>", "cite": "List<Ref<Reference>>|Ref<Reference>", "confidence": "Number|Text", "status": "Text", "contradicts": "List<Ref<Claim>>|Ref<Claim>", "depends_on": "List<Ref<Any>>|Ref<Any>"},
    "Evidence": {"text": "Text", "source": "List<Ref<Reference>>|Ref<Reference>", "supports": "List<Ref<Claim>>|Ref<Claim>", "method": "Ref<Object>|Text"},
    "Reason": {"text": "Text", "supports": "List<Ref<Claim>>|Ref<Claim>", "based_on": "List<Union<Ref<Evidence>|Ref<Reference>>>|Ref<Evidence>|Ref<Reference>"},
    "Counterargument": {"text": "Text", "against": "List<Union<Ref<Claim>|Ref<Reason>|Ref<Conclusion>|Ref<Counterargument>>>|Ref<Claim>|Ref<Reason>|Ref<Conclusion>|Ref<Counterargument>", "cite": "List<Ref<Reference>>|Ref<Reference>", "evidence": "List<Union<Ref<Evidence>|Ref<Reference>>>|Ref<Evidence>|Ref<Reference>", "based_on": "List<Union<Ref<Evidence>|Ref<Reference>|Ref<Reason>>>|Ref<Evidence>|Ref<Reference>|Ref<Reason>", "rebuts": "List<Union<Ref<Counterargument>|Ref<Claim>|Ref<Reason>|Ref<Conclusion>>>|Ref<Counterargument>|Ref<Claim>|Ref<Reason>|Ref<Conclusion>"},
    "Conclusion": {"text": "Text", "based_on": "List<Union<Ref<Claim>|Ref<Reason>|Ref<Evidence>>>|Ref<Claim>|Ref<Reason>|Ref<Evidence>"},
    "Definition": {"term": "Text", "text": "Text", "cite": "List<Ref<Reference>>|Ref<Reference>"},
    "Reference": {"title": "Text", "author": "Text", "year": "Int|Text", "journal": "Text", "booktitle": "Text", "publisher": "Text", "volume": "Text|Int", "number": "Text|Int", "pages": "Text", "doi": "Text", "url": "Text", "accessed": "Date|Text", "type": "Text", "bibkey": "Text", "imported_from": "Text", "note": "Text"},
    "Figure": {"src": "Text", "alt": "Text", "caption": "Text", "cite": "List<Ref<Reference>>|Ref<Reference>"},
    "Table": {"columns": "List<Object>", "rows": "List<List<Any>>", "caption": "Text", "cite": "List<Ref<Reference>>|Ref<Reference>"},
    "Chart": {"data": "Ref<Table>", "x": "Text", "y": "Text", "type": "Text", "caption": "Text"},
    "Flowchart": {"nodes": "Object", "edges": "List<List<Union<Text|Identifier>>>", "caption": "Text"},
    "CodeBlock": {"lang": "Text", "source": "Text", "caption": "Text"},
    "Object": {"name": "Text", "description": "Text", "type": "Text", "fields": "Object"},
    "Class": {"description": "Text", "fields": "Object"},
    "Function": {"description": "Text", "expression": "Text", "body": "Text", "abstract": "Bool", "precondition": "Text", "postcondition": "Text", "uses": "List<Ref<Any>>|Ref<Any>"},
}


DEFAULT_DOCUMENT_SCHEMAS: dict[str, dict[str, Any]]={
    "Document": {"required_meta": ["title"], "required_nodes": [], "recommended_nodes": [], "allowed_nodes": []},
    "Paper": {"required_meta": ["title", "author", "date"], "required_nodes": ["Section"], "recommended_nodes": ["Reference"], "allowed_nodes": []},
    "Minutes": {"required_meta": ["title", "date"], "required_nodes": ["Section"], "recommended_nodes": ["Object", "Table", "Conclusion"], "allowed_nodes": []},
    "Explainer": {"required_meta": ["title", "author"], "required_nodes": ["Section"], "recommended_nodes": ["Definition", "Figure"], "allowed_nodes": []},
    "Article": {"required_meta": ["title", "author", "date"], "required_nodes": ["Section"], "recommended_nodes": ["Reference"], "allowed_nodes": []},
}


DEFAULT_OBJECT_CLASSES: dict[str, Any]={
    "Person": {"name": "Text", "role": "Text", "email": "Text", "affiliation": "Text|Ref<Object>"},
    "Organization": {"name": "Text", "description": "Text", "url": "Text"},
    "Dataset": {"name": "Text", "description": "Text", "size": "Int|Text", "license": "Text", "url": "Text"},
    "Method": {"name": "Text", "description": "Text", "input": "Text", "output": "Text"},
    "Metric": {"name": "Text", "description": "Text", "unit": "Text", "formula": "Text"},
    "Concept": {"name": "Text", "description": "Text"},
}


DEFAULT_NODE_RULES: dict[str, dict[str, Any]]={}


class SchemaRegistry:
    def __init__(self) -> None:
        self.document_schemas=deepcopy(DEFAULT_DOCUMENT_SCHEMAS)
        self.node_field_types=deepcopy(DEFAULT_NODE_FIELD_TYPES)
        self.object_classes=deepcopy(DEFAULT_OBJECT_CLASSES)
        self.node_rules=deepcopy(DEFAULT_NODE_RULES)
        self.type_aliases={}
        self.enum_types={}
        self.function_signatures={}
        self.relation_rules={}
        self.logic_rules={}

    @classmethod
    def default(cls) -> "SchemaRegistry":
        return cls()

    def load_file(self, path: str | Path) -> None:
        p=Path(path)
        data=json.loads(p.read_text(encoding="utf-8"))
        self.merge(data)

    def merge(self, data: dict[str, Any]) -> None:
        for name,schema in data.get("document_types", {}).items():
            current=deepcopy(self.document_schemas.get(name, {}))
            current=_deep_merge_dict(current, schema)
            self.document_schemas[name]=current
        for kind,fields in data.get("node_field_types", {}).items():
            current=deepcopy(self.node_field_types.get(kind, {}))
            current.update(fields)
            self.node_field_types[kind]=current
        for kind,rule in data.get("node_rules", {}).items():
            current=deepcopy(self.node_rules.get(kind, {}))
            current=_deep_merge_dict(current, rule)
            self.node_rules[kind]=current
        for name,type_expr in data.get("type_aliases", {}).items():
            self.type_aliases[str(name)]=str(type_expr)
        for name,values in data.get("enum_types", data.get("enums", {})).items():
            self.enum_types[str(name)]=[str(v) for v in _as_list(values)]
        for name,signature in data.get("function_signatures", data.get("functions", {})).items():
            current=deepcopy(self.function_signatures.get(name, {}))
            if(isinstance(signature, dict)):
                current=_deep_merge_dict(current, signature)
            else:
                current={"return": str(signature), "params": []}
            self.function_signatures[str(name)]=current
        for key,rule in data.get("relation_rules", {}).items():
            current=deepcopy(self.relation_rules.get(key, {}))
            if(isinstance(rule, dict)):
                current=_deep_merge_dict(current, rule)
            else:
                current={"target": rule}
            self.relation_rules[str(key)]=current
        logic_rules=data.get("logic_rules", {})
        if(isinstance(logic_rules, dict)):
            self.logic_rules=_deep_merge_dict(deepcopy(self.logic_rules), logic_rules)
        for class_name,fields in data.get("object_classes", {}).items():
            current=deepcopy(self.object_classes.get(class_name, {}))
            if(_looks_like_object_class_rule(fields) or _looks_like_object_class_rule(current)):
                current=_deep_merge_dict(_normalize_object_class_schema(current), _normalize_object_class_schema(fields))
            else:
                current.update(fields)
            self.object_classes[class_name]=current
        for class_name,rule in data.get("object_class_rules", {}).items():
            current=deepcopy(self.object_classes.get(class_name, {}))
            current=_deep_merge_dict(_normalize_object_class_schema(current), _normalize_object_class_schema(rule))
            self.object_classes[class_name]=current


def load_schema_registry(paths: list[str] | None = None) -> SchemaRegistry:
    registry=SchemaRegistry.default()
    for path in paths or []:
        registry.load_file(path)
    return registry


def check_with_schema(doc: DocumentAst, registry: SchemaRegistry) -> None:
    schema=_check_document_type(doc, registry)
    _check_field_types(doc, registry)
    _check_node_rules(doc, registry, schema)
    _check_object_classes(doc, registry)
    _check_logic_links(doc)


def _check_document_type(doc: DocumentAst, registry: SchemaRegistry) -> dict[str, Any] | None:
    schema=registry.document_schemas.get(doc.type_name)
    if(schema is None):
        doc.diagnostics.append(Diagnostic("warning", "W_UNKNOWN_DOCUMENT_TYPE", f"Unknown document type: {doc.type_name}", doc.line, doc.column))
        return None
    _check_schema_meta(doc, schema)
    _check_schema_nodes(doc, schema)
    _check_schema_sections(doc, schema)
    return schema


def _check_schema_meta(doc: DocumentAst, schema: dict[str, Any]) -> None:
    if(doc.meta is None):
        return
    for field in _as_list(schema.get("required_meta")):
        if(field not in doc.meta.fields):
            doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_REQUIRED_META", f"{doc.type_name}.meta.{field} is required by document schema", doc.meta.line, doc.meta.column))
    for field in _as_list(schema.get("recommended_meta")):
        if(field not in doc.meta.fields):
            doc.diagnostics.append(Diagnostic("warning", "W_SCHEMA_RECOMMENDED_META", f"{doc.type_name}.meta.{field} is recommended by document schema", doc.meta.line, doc.meta.column))
    allowed=_as_list(schema.get("allowed_meta"))
    if(allowed and _policy_enabled(schema, "strict_meta", "unknown_meta_policy")):
        level=_schema_level(schema, "unknown_meta", "error")
        for field_name,value in doc.meta.fields.items():
            normalized=field_name.rstrip("?")
            if(normalized.startswith("__")):
                continue
            if(normalized not in allowed):
                doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_UNKNOWN_META"), f"{doc.type_name}.meta.{normalized} is not declared in allowed_meta", value.line, value.column))


def _check_schema_nodes(doc: DocumentAst, schema: dict[str, Any]) -> None:
    all_nodes=list(walk_nodes(doc.children))
    top_nodes=list(doc.children)
    all_present={node.kind for node in all_nodes}
    top_present={node.kind for node in top_nodes}

    for kind in _as_list(schema.get("required_nodes")):
        if(kind not in all_present):
            doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_REQUIRED_NODE", f"{doc.type_name} requires at least one {kind}", doc.line, doc.column))
    for kind in _as_list(schema.get("recommended_nodes")):
        if(kind not in all_present):
            doc.diagnostics.append(Diagnostic("warning", "W_SCHEMA_RECOMMENDED_NODE", f"{doc.type_name} usually includes {kind}", doc.line, doc.column))
    for kind in _as_list(schema.get("required_top_level_nodes")):
        if(kind not in top_present):
            doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_REQUIRED_TOP_LEVEL_NODE", f"{doc.type_name} requires top-level {kind}", doc.line, doc.column))
    for kind in _as_list(schema.get("recommended_top_level_nodes")):
        if(kind not in top_present):
            doc.diagnostics.append(Diagnostic("warning", "W_SCHEMA_RECOMMENDED_TOP_LEVEL_NODE", f"{doc.type_name} usually includes top-level {kind}", doc.line, doc.column))

    allowed=_as_list(schema.get("allowed_nodes"))
    if(allowed):
        level=_schema_level(schema, "disallowed_node", "error")
        for node in all_nodes:
            if(node.kind not in allowed):
                doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_DISALLOWED_NODE"), f"{node.kind} is not allowed in {doc.type_name}", node.line, node.column))

    top_allowed=_as_list(schema.get("allowed_top_level_nodes"))
    if(top_allowed):
        level=_schema_level(schema, "disallowed_top_level_node", "error")
        for node in top_nodes:
            if(node.kind not in top_allowed):
                doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_DISALLOWED_TOP_LEVEL_NODE"), f"Top-level {node.kind} is not allowed in {doc.type_name}", node.line, node.column))

    for kind in _as_list(schema.get("forbidden_nodes")):
        for node in all_nodes:
            if(node.kind==kind):
                doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_FORBIDDEN_NODE", f"{kind} is forbidden in {doc.type_name}", node.line, node.column))
    for kind in _as_list(schema.get("forbidden_top_level_nodes")):
        for node in top_nodes:
            if(node.kind==kind):
                doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_FORBIDDEN_TOP_LEVEL_NODE", f"Top-level {kind} is forbidden in {doc.type_name}", node.line, node.column))

    _check_node_counts(doc, schema.get("node_counts", {}), all_nodes, doc.type_name, doc.line, doc.column)
    _check_node_counts(doc, schema.get("top_level_node_counts", {}), top_nodes, f"top-level {doc.type_name}", doc.line, doc.column)


def _check_schema_sections(doc: DocumentAst, schema: dict[str, Any]) -> None:
    sections=[node for node in walk_nodes(doc.children) if(node.kind=="Section")]
    top_sections=[node for node in doc.children if(node.kind=="Section")]

    for spec in _as_list(schema.get("required_sections")):
        if(not _find_sections(sections, spec)):
            label=_section_spec_label(spec)
            doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_REQUIRED_SECTION", f"{doc.type_name} requires section: {label}", doc.line, doc.column))
    for spec in _as_list(schema.get("recommended_sections")):
        if(not _find_sections(sections, spec)):
            label=_section_spec_label(spec)
            doc.diagnostics.append(Diagnostic("warning", "W_SCHEMA_RECOMMENDED_SECTION", f"{doc.type_name} usually includes section: {label}", doc.line, doc.column))

    allowed_specs=_as_list(schema.get("allowed_sections"))
    rules=_as_list(schema.get("section_rules"))+_as_list(schema.get("sections"))
    unknown_policy=str(schema.get("unknown_section_policy", "error" if(schema.get("strict_sections")) else "allow")).lower()
    if(allowed_specs and unknown_policy!="allow"):
        level="warning" if(unknown_policy in {"warn", "warning"}) else "error"
        for section in sections:
            if(not any(_section_matches_spec(section, spec) for spec in allowed_specs)):
                doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_UNKNOWN_SECTION"), f"Section is not declared in allowed_sections: {_section_label(section)}", section.line, section.column))

    _check_section_order(doc, schema, top_sections)

    for rule in rules:
        if(not isinstance(rule, dict)):
            continue
        matched=_find_sections(sections, rule)
        min_count=rule.get("min_count", rule.get("min", 1 if(rule.get("required")) else None))
        max_count=rule.get("max_count", rule.get("max"))
        if(min_count is not None and len(matched)<int(min_count)):
            level=_rule_level(rule, schema, "section_count", "error")
            doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_SECTION_COUNT"), f"Section rule '{_section_spec_label(rule)}' requires at least {min_count} section(s), found {len(matched)}", doc.line, doc.column))
        if(max_count is not None and len(matched)>int(max_count)):
            level=_rule_level(rule, schema, "section_count", "error")
            first=matched[int(max_count)] if(len(matched)>int(max_count)) else matched[-1]
            doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_SECTION_COUNT"), f"Section rule '{_section_spec_label(rule)}' allows at most {max_count} section(s), found {len(matched)}", first.line, first.column))
        if(rule.get("recommended") and not matched):
            doc.diagnostics.append(Diagnostic("warning", "W_SCHEMA_RECOMMENDED_SECTION", f"{doc.type_name} usually includes section: {_section_spec_label(rule)}", doc.line, doc.column))
        for section in matched:
            _check_single_section_rule(doc, section, rule, schema)


def _check_section_order(doc: DocumentAst, schema: dict[str, Any], top_sections: list[Node]) -> None:
    order=_as_list(schema.get("section_order"))
    if(not order):
        return
    level=_schema_level(schema, "section_order", "warning" if(not schema.get("strict_section_order")) else "error")
    last_index=-1
    last_label=""
    for section in top_sections:
        index=None
        for i,spec in enumerate(order):
            if(_section_matches_spec(section, spec)):
                index=i
                break
        if(index is None):
            continue
        if(index<last_index):
            doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_SECTION_ORDER"), f"Section order violation: {_section_label(section)} appears after {last_label}", section.line, section.column))
        else:
            last_index=index
            last_label=_section_label(section)


def _check_single_section_rule(doc: DocumentAst, section: Node, rule: dict[str, Any], doc_schema: dict[str, Any]) -> None:
    scope=str(rule.get("scope", "direct")).lower()
    nodes=list(walk_nodes(section.children)) if(scope in {"recursive", "descendant", "descendants", "all"}) else list(section.children)
    present={node.kind for node in nodes}

    for kind in _as_list(rule.get("required_nodes")):
        if(kind not in present):
            level=_rule_level(rule, doc_schema, "section_required_node", "error")
            doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_SECTION_REQUIRED_NODE"), f"Section {_section_label(section)} requires {kind}", section.line, section.column))
    for kind in _as_list(rule.get("recommended_nodes")):
        if(kind not in present):
            doc.diagnostics.append(Diagnostic("warning", "W_SCHEMA_SECTION_RECOMMENDED_NODE", f"Section {_section_label(section)} usually includes {kind}", section.line, section.column))
    allowed=_as_list(rule.get("allowed_nodes"))
    if(allowed):
        level=_rule_level(rule, doc_schema, "section_disallowed_node", "error")
        for node in nodes:
            if(node.kind not in allowed):
                doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_SECTION_DISALLOWED_NODE"), f"{node.kind} is not allowed in section {_section_label(section)}", node.line, node.column))
    for kind in _as_list(rule.get("forbidden_nodes")):
        for node in nodes:
            if(node.kind==kind):
                doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_SECTION_FORBIDDEN_NODE", f"{kind} is forbidden in section {_section_label(section)}", node.line, node.column))
    _check_node_counts(doc, rule.get("node_counts", {}), nodes, f"section {_section_label(section)}", section.line, section.column)


def _check_node_counts(doc: DocumentAst, counts_spec: Any, nodes: list[Node], owner: str, line: int, column: int) -> None:
    if(not isinstance(counts_spec, dict)):
        return
    counts: dict[str, int]={}
    for node in nodes:
        counts[node.kind]=counts.get(node.kind, 0)+1
    for kind,raw_rule in counts_spec.items():
        if(isinstance(raw_rule, int)):
            rule={"min": raw_rule}
        elif(isinstance(raw_rule, dict)):
            rule=raw_rule
        else:
            continue
        actual=counts.get(kind, 0)
        level=str(rule.get("level", rule.get("severity", "error"))).lower()
        if(actual<int(rule.get("min", 0))):
            doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_NODE_COUNT"), f"{owner} requires at least {rule.get('min')} {kind} node(s), found {actual}", line, column))
        if("max" in rule and actual>int(rule.get("max"))):
            first=next((n for n in nodes if(n.kind==kind)), None)
            doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_NODE_COUNT"), f"{owner} allows at most {rule.get('max')} {kind} node(s), found {actual}", first.line if(first) else line, first.column if(first) else column))


def _check_field_types(doc: DocumentAst, registry: SchemaRegistry) -> None:
    if(doc.meta is not None):
        _check_node_field_types(doc, doc.meta, registry)
    for node in walk_nodes(doc.children):
        _check_node_field_types(doc, node, registry)


def _check_node_field_types(doc: DocumentAst, node: Node, registry: SchemaRegistry) -> None:
    field_types=registry.node_field_types.get(node.kind, {})
    for field_name,value in node.fields.items():
        normalized=field_name.rstrip("?")
        if(normalized.startswith("__")):
            continue
        expected=field_types.get(normalized)
        if(expected is None):
            continue
        result=type_matches(value, expected, doc)
        if(not result.ok):
            doc.diagnostics.append(Diagnostic("error", "E_TYPE_MISMATCH", f"{node.kind}.{normalized}: {result.reason}", value.line, value.column))


def _check_node_rules(doc: DocumentAst, registry: SchemaRegistry, doc_schema: dict[str, Any] | None) -> None:
    rules=deepcopy(registry.node_rules)
    if(doc_schema and isinstance(doc_schema.get("node_rules"), dict)):
        for kind,rule in doc_schema.get("node_rules", {}).items():
            current=deepcopy(rules.get(kind, {}))
            rules[kind]=_deep_merge_dict(current, rule)
    if(doc.meta is not None):
        _check_single_node_rule(doc, doc.meta, rules.get("Meta", {}), doc_schema)
    for node in walk_nodes(doc.children):
        _check_single_node_rule(doc, node, rules.get(node.kind, {}), doc_schema)


def _check_single_node_rule(doc: DocumentAst, node: Node, rule: dict[str, Any], doc_schema: dict[str, Any] | None) -> None:
    if(not rule):
        return
    field_types=rule.get("field_types", {}) if(isinstance(rule.get("field_types", {}), dict)) else {}
    for field_name,expected in field_types.items():
        if(field_name in node.fields):
            result=type_matches(node.fields[field_name], expected, doc)
            if(not result.ok):
                doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_FIELD_TYPE", f"{node.kind}.{field_name}: {result.reason}", node.fields[field_name].line, node.fields[field_name].column))
    for field_name in _as_list(rule.get("required_fields")):
        if(field_name not in node.fields):
            level=_rule_level(rule, doc_schema, "required_field", "error")
            doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_REQUIRED_FIELD"), f"{node.kind}.{field_name} is required by schema", node.line, node.column))
    for field_name in _as_list(rule.get("recommended_fields")):
        if(field_name not in node.fields):
            doc.diagnostics.append(Diagnostic("warning", "W_SCHEMA_RECOMMENDED_FIELD", f"{node.kind}.{field_name} is recommended by schema", node.line, node.column))
    for field_name in _as_list(rule.get("forbidden_fields")):
        if(field_name in node.fields):
            doc.diagnostics.append(Diagnostic("error", "E_SCHEMA_FORBIDDEN_FIELD", f"{node.kind}.{field_name} is forbidden by schema", node.fields[field_name].line, node.fields[field_name].column))
    allowed=_as_list(rule.get("allowed_fields"))
    if(allowed and _policy_enabled(rule, "strict_fields", "unknown_field_policy")):
        level=_rule_level(rule, doc_schema, "unknown_field", "error")
        for field_name,value in node.fields.items():
            normalized=field_name.rstrip("?")
            if(normalized.startswith("__")):
                continue
            if(normalized not in allowed):
                doc.diagnostics.append(Diagnostic(level, _code(level, "SCHEMA_UNKNOWN_FIELD"), f"{node.kind}.{normalized} is not declared in allowed_fields", value.line, value.column))


def _check_object_classes(doc: DocumentAst, registry: SchemaRegistry) -> None:
    class_schemas={name: _normalize_object_class_schema(schema) for name,schema in registry.object_classes.items()}
    for node in walk_nodes(doc.children):
        if(node.kind=="Class" and node.id and "fields" in node.fields):
            fields_value=node.fields["fields"]
            if(fields_value.kind=="Object"):
                field_types={k: value_to_type_string(v) for k,v in fields_value.value.items()}
                class_schemas[node.id]={"fields": field_types, "recommended_fields": list(field_types.keys())}
    for node in walk_nodes(doc.children):
        if(node.kind!="Object" or not node.type_name):
            continue
        if(node.type_name=="Object"):
            continue
        schema=class_schemas.get(node.type_name)
        if(schema is None):
            doc.diagnostics.append(Diagnostic("warning", "W_UNKNOWN_OBJECT_TYPE", f"Unknown object type: {node.type_name}", node.line, node.column))
            continue
        fields=schema.get("fields", {}) if(isinstance(schema.get("fields"), dict)) else {}
        for field_name in _as_list(schema.get("required_fields")):
            if(field_name not in node.fields):
                doc.diagnostics.append(Diagnostic("error", "E_OBJECT_MISSING_REQUIRED_FIELD", f"{node.type_name}.{field_name} is required", node.line, node.column))
        for field_name in _as_list(schema.get("recommended_fields")):
            if(field_name not in node.fields):
                doc.diagnostics.append(Diagnostic("warning", "W_OBJECT_MISSING_FIELD", f"{node.type_name}.{field_name} is recommended", node.line, node.column))
        for field_name in _as_list(schema.get("forbidden_fields")):
            if(field_name in node.fields):
                doc.diagnostics.append(Diagnostic("error", "E_OBJECT_FORBIDDEN_FIELD", f"{node.type_name}.{field_name} is forbidden", node.fields[field_name].line, node.fields[field_name].column))
        for field_name,expected in fields.items():
            if(field_name not in node.fields):
                continue
            result=type_matches(node.fields[field_name], expected, doc)
            if(not result.ok):
                doc.diagnostics.append(Diagnostic("error", "E_OBJECT_FIELD_TYPE", f"{node.type_name}.{field_name}: {result.reason}", node.fields[field_name].line, node.fields[field_name].column))
        allowed=_as_list(schema.get("allowed_fields"))
        if(allowed and _policy_enabled(schema, "strict_fields", "unknown_field_policy")):
            level=str(schema.get("unknown_field_level", schema.get("unknown_field_severity", "error"))).lower()
            for field_name,value in node.fields.items():
                normalized=field_name.rstrip("?")
                if(normalized not in allowed):
                    doc.diagnostics.append(Diagnostic(level, _code(level, "OBJECT_UNKNOWN_FIELD"), f"{node.type_name}.{normalized} is not declared in allowed_fields", value.line, value.column))


def _check_logic_links(doc: DocumentAst) -> None:
    for node in walk_nodes(doc.children):
        if(node.kind=="Reason" and "supports" not in node.fields):
            doc.diagnostics.append(Diagnostic("warning", "W_LOGIC_LINK_MISSING", f"Reason should declare supports: {node.id or '-'}", node.line, node.column))
        if(node.kind=="Counterargument" and "against" not in node.fields):
            doc.diagnostics.append(Diagnostic("warning", "W_LOGIC_LINK_MISSING", f"Counterargument should declare against: {node.id or '-'}", node.line, node.column))
        if(node.kind=="Conclusion" and "based_on" not in node.fields):
            doc.diagnostics.append(Diagnostic("warning", "W_LOGIC_LINK_MISSING", f"Conclusion should declare based_on: {node.id or '-'}", node.line, node.column))


def _find_sections(sections: list[Node], spec: Any) -> list[Node]:
    return [section for section in sections if(_section_matches_spec(section, spec))]


def _section_matches_spec(section: Node, spec: Any) -> bool:
    if(section.kind!="Section"):
        return False
    if(isinstance(spec, str)):
        return spec in {section.id or "", section.type_name or "", _section_title(section)}
    if(not isinstance(spec, dict)):
        return False
    match=spec.get("match")
    if(match is not None):
        return _section_matches_spec(section, match)
    if("id" in spec and section.id!=spec.get("id")):
        return False
    if("type" in spec and (section.type_name or "")!=spec.get("type")):
        return False
    if("type_name" in spec and (section.type_name or "")!=spec.get("type_name")):
        return False
    if("title" in spec and _section_title(section)!=spec.get("title")):
        return False
    if("title_pattern" in spec):
        try:
            if(not re.search(str(spec.get("title_pattern")), _section_title(section))):
                return False
        except re.error:
            return False
    return any(key in spec for key in ["id", "type", "type_name", "title", "title_pattern", "match"]) or True


def _section_title(section: Node) -> str:
    return _value_plain(section.fields.get("title"))


def _section_label(section: Node) -> str:
    title=_section_title(section)
    if(title):
        return title
    if(section.id):
        return section.id
    return section.type_name or "Section"


def _section_spec_label(spec: Any) -> str:
    if(isinstance(spec, str)):
        return spec
    if(isinstance(spec, dict)):
        if("label" in spec):
            return str(spec["label"])
        if("title" in spec):
            return str(spec["title"])
        if("id" in spec):
            return str(spec["id"])
        if("type" in spec):
            return str(spec["type"])
        if("match" in spec):
            return _section_spec_label(spec["match"])
    return str(spec)


def _normalize_object_class_schema(schema: Any) -> dict[str, Any]:
    if(not isinstance(schema, dict)):
        return {"fields": {}}
    if(_looks_like_object_class_rule(schema)):
        result=deepcopy(schema)
        result.setdefault("fields", {})
        if("required" in result and "required_fields" not in result):
            result["required_fields"]=result.pop("required")
        if("recommended" in result and "recommended_fields" not in result):
            result["recommended_fields"]=result.pop("recommended")
        return result
    return {"fields": deepcopy(schema), "recommended_fields": list(schema.keys())}


def _looks_like_object_class_rule(schema: Any) -> bool:
    if(not isinstance(schema, dict)):
        return False
    return any(key in schema for key in ["fields", "required_fields", "recommended_fields", "allowed_fields", "forbidden_fields", "strict_fields", "unknown_field_policy"])


def _deep_merge_dict(base: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    result=deepcopy(base)
    for key,value in extra.items():
        if(isinstance(value, dict) and isinstance(result.get(key), dict)):
            result[key]=_deep_merge_dict(result[key], value)
        else:
            result[key]=deepcopy(value)
    return result


def _policy_enabled(rule: dict[str, Any], strict_key: str, policy_key: str) -> bool:
    if(rule.get(strict_key)):
        return True
    policy=str(rule.get(policy_key, "allow")).lower()
    return policy in {"warn", "warning", "error"}


def _schema_level(schema: dict[str, Any], key: str, default: str) -> str:
    severity=schema.get("severity", {}) if(isinstance(schema.get("severity", {}), dict)) else {}
    value=schema.get(key+"_level", schema.get(key+"_severity", severity.get(key, default)))
    value=str(value).lower()
    if(value in {"warn", "warning"}):
        return "warning"
    return "error" if(value=="error") else default


def _rule_level(rule: dict[str, Any], schema: dict[str, Any] | None, key: str, default: str) -> str:
    severity=rule.get("severity", {}) if(isinstance(rule.get("severity", {}), dict)) else {}
    value=rule.get(key+"_level", rule.get(key+"_severity", severity.get(key)))
    if(value is None and schema is not None):
        return _schema_level(schema, key, default)
    if(value is None):
        return default
    value=str(value).lower()
    if(value in {"warn", "warning"}):
        return "warning"
    return "error" if(value=="error") else default


def _code(level: str, base: str) -> str:
    return ("E_" if(level=="error") else "W_")+base


def _as_list(value: Any) -> list[Any]:
    if(value is None):
        return []
    if(isinstance(value, list)):
        return value
    return [value]


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
