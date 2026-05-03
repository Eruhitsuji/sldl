from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import json


@dataclass
class Template:
    name: str
    description: str
    content: str
    source_path: Path | None = None
    document_type: str | None = None
    language: str | None = None
    schema: str | None = None
    default_export_config: str | None = None
    default_latex_build_config: str | None = None
    strict_schema: bool = False


def default_template_dir() -> Path:
    return Path(__file__).resolve().parent.parent/"templates"


def _normalize_template_dir(template_dir: str | Path | None) -> Path:
    if(template_dir is None):
        return default_template_dir()
    return Path(template_dir)


def _manifest_path(template_dir: Path) -> Path | None:
    for name in ("template_manifest.json", "manifest.json"):
        path=template_dir/name
        if(path.exists()):
            return path
    return None


def _load_manifest(template_dir: Path) -> tuple[dict[str, Any], Path]:
    manifest_path=_manifest_path(template_dir)
    if(manifest_path is None):
        return {
            "version": "adhoc",
            "templates": [
                {
                    "name": p.stem,
                    "description": p.stem,
                    "path": p.name,
                }
                for p in sorted(template_dir.glob("*.sldl"))
            ],
        }, template_dir
    return json.loads(manifest_path.read_text(encoding="utf-8")), manifest_path.parent


def _iter_template_items(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    raw=manifest.get("templates", [])
    if(isinstance(raw, dict)):
        items=[]
        for name,value in raw.items():
            if(isinstance(value, dict)):
                item=dict(value)
                item.setdefault("name", str(name))
                items.append(item)
        return items
    if(isinstance(raw, list)):
        return [item for item in raw if(isinstance(item, dict))]
    return []


def _resolve_optional(base_dir: Path, value: Any) -> str | None:
    if(value is None):
        return None
    if(not isinstance(value, str) or not value.strip()):
        return None
    path=Path(value)
    return str(path if(path.is_absolute()) else (base_dir/path).resolve())


def load_templates(template_dir: str | Path | None = None) -> dict[str, Template]:
    directory=_normalize_template_dir(template_dir)
    if(not directory.exists()):
        raise FileNotFoundError(f"Template directory not found: {directory}")

    manifest,manifest_base=_load_manifest(directory)
    result: dict[str, Template]={}
    for item in _iter_template_items(manifest):
        name=item.get("name")
        if(not isinstance(name, str) or not name):
            continue
        rel_path=item.get("path") or item.get("template_file")
        if(not rel_path):
            continue
        source_path=(manifest_base/rel_path).resolve()
        if(not source_path.exists()):
            raise FileNotFoundError(f"Template file not found: {source_path}")
        result[name]=Template(
            name=name,
            description=item.get("description", name),
            content=source_path.read_text(encoding="utf-8"),
            source_path=source_path,
            document_type=item.get("document_type"),
            language=item.get("language"),
            schema=_resolve_optional(manifest_base, item.get("schema")),
            default_export_config=_resolve_optional(manifest_base, item.get("default_export_config")),
            default_latex_build_config=_resolve_optional(manifest_base, item.get("default_latex_build_config")),
            strict_schema=bool(item.get("strict_schema", False)),
        )
    return result


def list_templates(template_dir: str | Path | None = None) -> list[dict[str, Any]]:
    templates=load_templates(template_dir)
    return [
        {
            "name": t.name,
            "description": t.description,
            "document_type": t.document_type or "",
            "language": t.language or "",
            "source_path": str(t.source_path) if(t.source_path is not None) else "",
            "schema": t.schema or "",
            "default_export_config": t.default_export_config or "",
            "default_latex_build_config": t.default_latex_build_config or "",
            "strict_schema": t.strict_schema,
        }
        for t in templates.values()
    ]


def get_template(name: str, template_dir: str | Path | None = None) -> Template:
    templates=load_templates(template_dir)
    if(name not in templates):
        available=", ".join(sorted(templates.keys()))
        raise KeyError(f"Unknown template: {name}. Available: {available}")
    return templates[name]


def get_template_from_schema(schema_path: str | Path, document_type: str | None=None) -> Template:
    path=Path(schema_path)
    schema=json.loads(path.read_text(encoding="utf-8"))

    candidates=[]
    if(document_type):
        doc_types=schema.get("document_types") or {}
        if(document_type not in doc_types):
            raise KeyError(f"Document type is not defined in schema: {document_type}")
        candidate=dict(doc_types[document_type])
        candidate.setdefault("document_type", document_type)
        candidates.append(candidate)
    candidates.append(schema)
    for name,definition in (schema.get("document_types") or {}).items():
        candidate=dict(definition)
        candidate.setdefault("document_type", name)
        candidates.append(candidate)

    for candidate in candidates:
        inline_template=candidate.get("template")
        template_file=candidate.get("template_file")
        strict_schema=bool(candidate.get("strict_schema", False))
        if(inline_template is not None and "\n" in str(inline_template)):
            return Template(
                name=candidate.get("name", candidate.get("document_type", "schema_template")),
                description=candidate.get("description", candidate.get("name", candidate.get("document_type", "schema_template"))),
                content=str(inline_template),
                source_path=None,
                document_type=candidate.get("document_type"),
                language=candidate.get("language"),
                schema=str(path.resolve()),
                strict_schema=strict_schema,
            )
        if(template_file or inline_template):
            template_path=(path.parent/(template_file or inline_template)).resolve()
            if(not template_path.exists()):
                raise FileNotFoundError(f"Template file declared by schema was not found: {template_path}")
            return Template(
                name=candidate.get("name", template_path.stem),
                description=candidate.get("description", candidate.get("name", template_path.stem)),
                content=template_path.read_text(encoding="utf-8"),
                source_path=template_path,
                document_type=candidate.get("document_type"),
                language=candidate.get("language"),
                schema=str(path.resolve()),
                strict_schema=strict_schema,
            )

        template_name=candidate.get("template_name")
        template_dir=candidate.get("template_dir")
        if(template_name):
            base_dir=(path.parent/template_dir).resolve() if(template_dir) else None
            tmpl=get_template(template_name, base_dir)
            if(tmpl.schema is None):
                tmpl.schema=str(path.resolve())
            return tmpl

    raise KeyError(
        "Schema does not define a template. "
        "Use 'template', 'template_file', or 'template_name' in the schema JSON, "
        "either at the top level or under document_types.<TypeName>."
    )
