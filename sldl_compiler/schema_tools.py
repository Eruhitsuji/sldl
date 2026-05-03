from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .diagnostics import Diagnostic
from .schemas import SchemaRegistry, load_schema_registry

TOP_LEVEL_KEYS={"config_type", "description", "name", "$schema", "schema_version", "document_types", "node_field_types", "node_rules", "object_classes", "object_class_rules", "type_aliases", "enum_types", "enums", "function_signatures", "functions", "relation_rules", "logic_rules"}
DOC_LIST_STRING_KEYS={"required_meta", "recommended_meta", "allowed_meta", "required_nodes", "recommended_nodes", "allowed_nodes", "allowed_top_level_nodes", "forbidden_top_level_nodes"}
DOC_LIST_SECTION_KEYS={"required_sections", "recommended_sections", "allowed_sections", "section_order"}
RULE_LIST_STRING_KEYS={"required_fields", "recommended_fields", "allowed_fields", "forbidden_fields", "required_nodes", "recommended_nodes", "allowed_nodes", "forbidden_nodes"}
KNOWN_POLICY_VALUES={"allow", "warn", "warning", "error"}
KNOWN_SEVERITIES={"warning", "error"}


def check_schema_files(paths: list[Path]) -> list[Diagnostic]:
    diagnostics=[]
    for path in paths:
        diagnostics.extend(_check_schema_file(path))
    return diagnostics


def _check_schema_file(path: Path) -> list[Diagnostic]:
    diagnostics=[]
    try:
        source=path.read_text(encoding="utf-8")
    except OSError as exc:
        return [Diagnostic("error", "E_SCHEMA_FILE_READ", f"Cannot read schema file: {path} ({exc})")]
    try:
        data=json.loads(source)
    except json.JSONDecodeError as exc:
        return [Diagnostic("error", "E_SCHEMA_JSON", f"Invalid JSON in schema file: {path}: {exc.msg}", exc.lineno, exc.colno)]
    if(not isinstance(data, dict)):
        return [Diagnostic("error", "E_SCHEMA_ROOT", "Schema root must be a JSON object")]
    for key in data.keys():
        if(key not in TOP_LEVEL_KEYS):
            diagnostics.append(Diagnostic("warning", "W_SCHEMA_UNKNOWN_TOP_LEVEL_KEY", f"Unknown top-level schema key: {key}"))
    diagnostics.extend(_check_document_types(data.get("document_types", {})))
    diagnostics.extend(_check_node_rule_map(data.get("node_rules", {}), "node_rules"))
    diagnostics.extend(_check_node_field_types(data.get("node_field_types", {})))
    diagnostics.extend(_check_object_classes(data.get("object_classes", {}), "object_classes"))
    diagnostics.extend(_check_object_classes(data.get("object_class_rules", {}), "object_class_rules"))
    diagnostics.extend(_check_type_aliases(data.get("type_aliases", {})))
    diagnostics.extend(_check_enum_types(data.get("enum_types", data.get("enums", {}))))
    diagnostics.extend(_check_function_signatures(data.get("function_signatures", data.get("functions", {}))))
    diagnostics.extend(_check_relation_rules(data.get("relation_rules", {})))
    return diagnostics


def _check_document_types(document_types: Any) -> list[Diagnostic]:
    diagnostics=[]
    if(document_types is None):
        return diagnostics
    if(not isinstance(document_types, dict)):
        return [Diagnostic("error", "E_SCHEMA_DOCUMENT_TYPES", "document_types must be an object")]
    for doc_type,schema in document_types.items():
        if(not isinstance(schema, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_DOCUMENT_TYPE", f"document_types.{doc_type} must be an object"))
            continue
        for key in DOC_LIST_STRING_KEYS:
            diagnostics.extend(_expect_string_list(schema, key, f"document_types.{doc_type}.{key}"))
        for key in DOC_LIST_SECTION_KEYS:
            diagnostics.extend(_expect_section_spec_list(schema, key, f"document_types.{doc_type}.{key}"))
        if(schema.get("strict_sections") and not schema.get("allowed_sections")):
            diagnostics.append(Diagnostic("warning", "W_SCHEMA_STRICT_WITHOUT_ALLOWED", f"document_types.{doc_type}.strict_sections is true but allowed_sections is empty"))
        if(schema.get("strict_section_order") and not schema.get("section_order")):
            diagnostics.append(Diagnostic("warning", "W_SCHEMA_ORDER_WITHOUT_ORDER", f"document_types.{doc_type}.strict_section_order is true but section_order is empty"))
        diagnostics.extend(_check_top_level_node_counts(schema.get("top_level_node_counts"), f"document_types.{doc_type}.top_level_node_counts"))
        diagnostics.extend(_check_section_rules(schema.get("section_rules", []), f"document_types.{doc_type}.section_rules"))
        diagnostics.extend(_check_node_rule_map(schema.get("node_rules", {}), f"document_types.{doc_type}.node_rules"))
        diagnostics.extend(_check_template_info(schema, f"document_types.{doc_type}"))
        for policy_key in ["unknown_meta_policy", "unknown_top_level_node_policy", "unknown_section_policy"]:
            diagnostics.extend(_check_policy(schema, policy_key, f"document_types.{doc_type}.{policy_key}"))
    return diagnostics



def _check_type_aliases(value: Any) -> list[Diagnostic]:
    if(value is None):
        return []
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_TYPE_ALIASES", "type_aliases must be an object")]
    diagnostics=[]
    for name,type_expr in value.items():
        if(not isinstance(type_expr, str)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_TYPE_ALIAS", f"type_aliases.{name} must be a type string"))
    return diagnostics


def _check_enum_types(value: Any) -> list[Diagnostic]:
    if(value is None):
        return []
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_ENUM_TYPES", "enum_types must be an object")]
    diagnostics=[]
    for name,items in value.items():
        if(not isinstance(items, list)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_ENUM", f"enum_types.{name} must be a list"))
            continue
        for index,item in enumerate(items):
            if(not isinstance(item, str)):
                diagnostics.append(Diagnostic("error", "E_SCHEMA_ENUM_ITEM", f"enum_types.{name}[{index}] must be a string"))
    return diagnostics


def _check_function_signatures(value: Any) -> list[Diagnostic]:
    if(value is None):
        return []
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_FUNCTION_SIGNATURES", "function_signatures must be an object")]
    diagnostics=[]
    for name,sig in value.items():
        if(not isinstance(sig, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_FUNCTION_SIGNATURE", f"function_signatures.{name} must be an object"))
            continue
        if("return" in sig and not isinstance(sig["return"], str)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_FUNCTION_RETURN", f"function_signatures.{name}.return must be a type string"))
        params=sig.get("params", sig.get("parameters", []))
        if(not isinstance(params, (list, dict))):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_FUNCTION_PARAMS", f"function_signatures.{name}.params must be a list or object"))
    return diagnostics


def _check_relation_rules(value: Any) -> list[Diagnostic]:
    if(value is None):
        return []
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_RELATION_RULES", "relation_rules must be an object")]
    diagnostics=[]
    for key,rule in value.items():
        if(not isinstance(rule, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_RELATION_RULE", f"relation_rules.{key} must be an object"))
            continue
        if("target" in rule and not isinstance(rule["target"], (str, list))):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_RELATION_TARGET", f"relation_rules.{key}.target must be a string or list"))
        if("targets" in rule and not isinstance(rule["targets"], (str, list))):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_RELATION_TARGET", f"relation_rules.{key}.targets must be a string or list"))
        if("level" in rule):
            diagnostics.extend(_check_severity(rule, "level", f"relation_rules.{key}.level"))
    return diagnostics

def _check_top_level_node_counts(value: Any, label: str) -> list[Diagnostic]:
    diagnostics=[]
    if(value is None):
        return diagnostics
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_NODE_COUNTS", f"{label} must be an object")]
    for kind,rule in value.items():
        if(not isinstance(rule, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_NODE_COUNT_RULE", f"{label}.{kind} must be an object"))
            continue
        for bound in ["min", "max"]:
            if(bound in rule and not isinstance(rule[bound], int)):
                diagnostics.append(Diagnostic("error", "E_SCHEMA_NODE_COUNT_BOUND", f"{label}.{kind}.{bound} must be an integer"))
        if(isinstance(rule.get("min"), int) and isinstance(rule.get("max"), int) and rule["min"]>rule["max"]):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_NODE_COUNT_RANGE", f"{label}.{kind}.min must be <= max"))
    return diagnostics


def _check_section_rules(value: Any, label: str) -> list[Diagnostic]:
    diagnostics=[]
    if(value is None):
        return diagnostics
    if(not isinstance(value, list)):
        return [Diagnostic("error", "E_SCHEMA_SECTION_RULES", f"{label} must be a list")]
    for index,rule in enumerate(value):
        rlabel=f"{label}[{index}]"
        if(not isinstance(rule, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_SECTION_RULE", f"{rlabel} must be an object"))
            continue
        if(not any(key in rule for key in ["id", "type", "type_name", "title", "title_pattern", "match"])):
            diagnostics.append(Diagnostic("warning", "W_SCHEMA_SECTION_RULE_MATCH", f"{rlabel} has no section match condition"))
        for key in ["min", "max"]:
            if(key in rule and not isinstance(rule[key], int)):
                diagnostics.append(Diagnostic("error", "E_SCHEMA_SECTION_RULE_BOUND", f"{rlabel}.{key} must be an integer"))
        if(isinstance(rule.get("min"), int) and isinstance(rule.get("max"), int) and rule["min"]>rule["max"]):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_SECTION_RULE_RANGE", f"{rlabel}.min must be <= max"))
        for key in ["required_nodes", "recommended_nodes", "allowed_nodes", "forbidden_nodes"]:
            diagnostics.extend(_expect_string_list(rule, key, f"{rlabel}.{key}"))
        for policy_key in ["unknown_node_policy"]:
            diagnostics.extend(_check_policy(rule, policy_key, f"{rlabel}.{policy_key}"))
    return diagnostics


def _check_node_rule_map(value: Any, label: str) -> list[Diagnostic]:
    diagnostics=[]
    if(value is None):
        return diagnostics
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_NODE_RULES", f"{label} must be an object")]
    for kind,rule in value.items():
        rlabel=f"{label}.{kind}"
        if(not isinstance(rule, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_NODE_RULE", f"{rlabel} must be an object"))
            continue
        for key in RULE_LIST_STRING_KEYS:
            diagnostics.extend(_expect_string_list(rule, key, f"{rlabel}.{key}"))
        if("fields" in rule and not isinstance(rule["fields"], dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_NODE_RULE_FIELDS", f"{rlabel}.fields must be an object"))
        diagnostics.extend(_check_policy(rule, "unknown_field_policy", f"{rlabel}.unknown_field_policy"))
        diagnostics.extend(_check_severity(rule, "unknown_field_level", f"{rlabel}.unknown_field_level"))
        diagnostics.extend(_check_severity(rule, "unknown_field_severity", f"{rlabel}.unknown_field_severity"))
    return diagnostics


def _check_node_field_types(value: Any) -> list[Diagnostic]:
    diagnostics=[]
    if(value is None):
        return diagnostics
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_NODE_FIELD_TYPES", "node_field_types must be an object")]
    for kind,fields in value.items():
        if(not isinstance(fields, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_NODE_FIELD_TYPE", f"node_field_types.{kind} must be an object"))
            continue
        for field_name,type_name in fields.items():
            if(not isinstance(type_name, str)):
                diagnostics.append(Diagnostic("error", "E_SCHEMA_TYPE_NAME", f"node_field_types.{kind}.{field_name} must be a type string"))
    return diagnostics


def _check_object_classes(value: Any, label: str) -> list[Diagnostic]:
    diagnostics=[]
    if(value is None):
        return diagnostics
    if(not isinstance(value, dict)):
        return [Diagnostic("error", "E_SCHEMA_OBJECT_CLASSES", f"{label} must be an object")]
    for class_name,fields in value.items():
        clabel=f"{label}.{class_name}"
        if(not isinstance(fields, dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_OBJECT_CLASS", f"{clabel} must be an object"))
            continue
        for key in ["required_fields", "recommended_fields", "allowed_fields", "forbidden_fields"]:
            diagnostics.extend(_expect_string_list(fields, key, f"{clabel}.{key}"))
        if("fields" in fields and not isinstance(fields["fields"], dict)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_OBJECT_CLASS_FIELDS", f"{clabel}.fields must be an object"))
    return diagnostics


def _check_template_info(schema: dict[str, Any], label: str) -> list[Diagnostic]:
    diagnostics=[]
    if("template" in schema and not isinstance(schema["template"], str)):
        diagnostics.append(Diagnostic("error", "E_SCHEMA_TEMPLATE", f"{label}.template must be a string"))
    if("template_name" in schema and not isinstance(schema["template_name"], str)):
        diagnostics.append(Diagnostic("error", "E_SCHEMA_TEMPLATE_NAME", f"{label}.template_name must be a string"))
    if("template_file" in schema and not isinstance(schema["template_file"], str)):
        diagnostics.append(Diagnostic("error", "E_SCHEMA_TEMPLATE_FILE", f"{label}.template_file must be a string path"))
    if("template_dir" in schema and not isinstance(schema["template_dir"], str)):
        diagnostics.append(Diagnostic("error", "E_SCHEMA_TEMPLATE_DIR", f"{label}.template_dir must be a string path"))
    if("strict_schema" in schema and not isinstance(schema["strict_schema"], bool)):
        diagnostics.append(Diagnostic("error", "E_SCHEMA_TEMPLATE_STRICT", f"{label}.strict_schema must be a boolean"))
    return diagnostics


def _check_policy(schema: dict[str, Any], key: str, label: str) -> list[Diagnostic]:
    if(key not in schema):
        return []
    if(str(schema[key]).lower() not in KNOWN_POLICY_VALUES):
        return [Diagnostic("warning", "W_SCHEMA_UNKNOWN_POLICY", f"{label} should be one of: allow, warn, warning, error")]
    return []


def _check_severity(schema: dict[str, Any], key: str, label: str) -> list[Diagnostic]:
    if(key not in schema):
        return []
    if(str(schema[key]).lower() not in KNOWN_SEVERITIES):
        return [Diagnostic("warning", "W_SCHEMA_UNKNOWN_SEVERITY", f"{label} should be warning or error")]
    return []


def _expect_string_list(obj: dict[str, Any], key: str, label: str) -> list[Diagnostic]:
    if(key not in obj):
        return []
    value=obj[key]
    if(not isinstance(value, list)):
        return [Diagnostic("error", "E_SCHEMA_LIST", f"{label} must be a list")]
    diagnostics=[]
    for index,item in enumerate(value):
        if(not isinstance(item, str)):
            diagnostics.append(Diagnostic("error", "E_SCHEMA_LIST_ITEM", f"{label}[{index}] must be a string"))
    return diagnostics


def _expect_section_spec_list(obj: dict[str, Any], key: str, label: str) -> list[Diagnostic]:
    if(key not in obj):
        return []
    value=obj[key]
    if(not isinstance(value, list)):
        return [Diagnostic("error", "E_SCHEMA_SECTION_SPEC_LIST", f"{label} must be a list")]
    diagnostics=[]
    for index,item in enumerate(value):
        if(isinstance(item, str)):
            continue
        if(isinstance(item, dict)):
            if(not any(match_key in item for match_key in ["id", "type", "type_name", "title", "title_pattern", "match"])):
                diagnostics.append(Diagnostic("warning", "W_SCHEMA_SECTION_SPEC_MATCH", f"{label}[{index}] has no match condition"))
            continue
        diagnostics.append(Diagnostic("error", "E_SCHEMA_SECTION_SPEC", f"{label}[{index}] must be a string or object"))
    return diagnostics


def schema_summary(registry: SchemaRegistry, sources: list[str] | None = None) -> dict[str, Any]:
    return {
        "sources": sources or [],
        "document_types": sorted(registry.document_schemas.keys()),
        "node_kinds": sorted(registry.node_field_types.keys()),
        "object_classes": sorted(registry.object_classes.keys()),
        "type_aliases": sorted(registry.type_aliases.keys()),
        "enum_types": sorted(registry.enum_types.keys()),
        "function_signatures": sorted(registry.function_signatures.keys()),
        "relation_rules": sorted(registry.relation_rules.keys()),
    }


def schema_explain(registry: SchemaRegistry, document_type: str | None = None) -> str:
    if(document_type is None):
        lines=["# SLDL schema summary", ""]
        lines.append("## Document types")
        for name in sorted(registry.document_schemas.keys()):
            lines.append(f"- {name}")
        lines.append("")
        lines.append("## Object classes")
        for name in sorted(registry.object_classes.keys()):
            lines.append(f"- {name}")
        return "\n".join(lines)+"\n"
    schema=registry.document_schemas.get(document_type)
    if(schema is None):
        return f"# {document_type}\n\nDocument type not found.\n"
    lines=[f"# {document_type}", ""]
    _append_list(lines, "Required meta", schema.get("required_meta"))
    _append_list(lines, "Recommended meta", schema.get("recommended_meta"))
    _append_list(lines, "Allowed meta", schema.get("allowed_meta"))
    _append_list(lines, "Required nodes", schema.get("required_nodes"))
    _append_list(lines, "Recommended nodes", schema.get("recommended_nodes"))
    _append_list(lines, "Allowed top-level nodes", schema.get("allowed_top_level_nodes") or schema.get("allowed_nodes"))
    _append_section_specs(lines, "Required sections", schema.get("required_sections"))
    _append_section_specs(lines, "Recommended sections", schema.get("recommended_sections"))
    _append_section_specs(lines, "Allowed sections", schema.get("allowed_sections"))
    section_rules=schema.get("section_rules")
    if(section_rules):
        lines.append("## Section rules")
        for rule in section_rules:
            if(not isinstance(rule, dict)):
                continue
            label=rule.get("id") or rule.get("type") or rule.get("title") or rule.get("match") or "<section>"
            lines.append(f"- {label}")
            for key in ["required_nodes", "recommended_nodes", "allowed_nodes", "forbidden_nodes"]:
                values=rule.get(key)
                if(values):
                    lines.append(f"  - {key}: "+", ".join(str(v) for v in values))
        lines.append("")
    node_rules=schema.get("node_rules")
    if(node_rules):
        lines.append("## Node rules")
        for kind,rule in sorted(node_rules.items()):
            if(not isinstance(rule, dict)):
                continue
            lines.append(f"- {kind}")
            for key in ["required_fields", "recommended_fields", "allowed_fields", "forbidden_fields"]:
                values=rule.get(key)
                if(values):
                    lines.append(f"  - {key}: "+", ".join(str(v) for v in values))
        lines.append("")
    return "\n".join(lines).rstrip()+"\n"


def _append_list(lines: list[str], title: str, value: Any) -> None:
    if(not value):
        return
    lines.append(f"## {title}")
    for item in value:
        lines.append(f"- {item}")
    lines.append("")


def _append_section_specs(lines: list[str], title: str, value: Any) -> None:
    if(not value):
        return
    lines.append(f"## {title}")
    for item in value:
        lines.append(f"- {_section_spec_label(item)}")
    lines.append("")


def _section_spec_label(value: Any) -> str:
    if(isinstance(value, str)):
        return value
    if(isinstance(value, dict)):
        for key in ["label", "id", "type", "type_name", "title", "title_pattern"]:
            if(key in value):
                return str(value[key])
        if("match" in value):
            return _section_spec_label(value["match"])
    return str(value)
