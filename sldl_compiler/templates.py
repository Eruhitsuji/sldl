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
    manifest_path: Path | None = None
    manifest_version: str | None = None
    manifest_role: str | None = None


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
            "manifest_role": "adhoc",
            "templates": [
                {
                    "name": p.stem,
                    "description": p.stem,
                    "path": p.name,
                }
                for p in sorted(template_dir.glob("*.sldl"))
            ],
        }, template_dir
    return json.loads(manifest_path.read_text(encoding="utf-8")), manifest_path




def _template_info_from_template(t: Template) -> dict[str, Any]:
    return {
        "name": t.name,
        "description": t.description,
        "document_type": t.document_type,
        "language": t.language,
        "source_path": str(t.source_path) if(t.source_path is not None) else None,
        "schema": t.schema,
        "default_export_config": t.default_export_config,
        "default_latex_build_config": t.default_latex_build_config,
        "strict_schema": t.strict_schema,
        "manifest_path": str(t.manifest_path) if(t.manifest_path is not None) else None,
        "manifest_version": t.manifest_version,
        "manifest_role": t.manifest_role,
    }


def template_info(name: str, template_dir: str | Path | None = None) -> dict[str, Any]:
    return _template_info_from_template(get_template(name, template_dir))


def template_info_markdown(name: str, template_dir: str | Path | None = None) -> str:
    info=template_info(name, template_dir)
    lines=[f"# Template: {info['name']}", ""]
    rows=[
        ("description", info.get("description") or "-"),
        ("document_type", info.get("document_type") or "-"),
        ("language", info.get("language") or "-"),
        ("source_path", info.get("source_path") or "-"),
        ("schema", info.get("schema") or "-"),
        ("default_export_config", info.get("default_export_config") or "-"),
        ("default_latex_build_config", info.get("default_latex_build_config") or "-"),
        ("strict_schema", str(info.get("strict_schema"))),
        ("manifest_path", info.get("manifest_path") or "-"),
        ("manifest_version", info.get("manifest_version") or "-"),
        ("manifest_role", info.get("manifest_role") or "-"),
    ]
    lines.append("| Field | Value |")
    lines.append("|---|---|")
    for key,value in rows:
        escaped=str(value).replace("|", "\\|")
        lines.append(f"| `{key}` | `{escaped}` |")
    lines.append("")
    lines.append("## Typical commands")
    lines.append("")
    lines.append("```bash")
    lines.append(f"python3 -S -m sldl_compiler.cli template check {info['name']}")
    lines.append(f"python3 -S -m sldl_compiler.cli template project {info['name']} --document-output examples/generated_from_template.sldl -o examples/generated_from_template_project.json --force")
    lines.append("```")
    return "\n".join(lines)+"\n"

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

    manifest,manifest_path=_load_manifest(directory)
    manifest_base=manifest_path.parent if(manifest_path.is_file()) else manifest_path
    manifest_role=manifest.get("manifest_role") if(isinstance(manifest.get("manifest_role"), str)) else ("canonical" if(manifest_path.name=="template_manifest.json") else "legacy_compatibility")
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
            raise FileNotFoundError(
                f"Template file not found: template={name}; manifest={manifest_path}; declared_path={rel_path}; resolved_path={source_path}. "
                "Fix templates/template_manifest.json or add the missing template file."
            )
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
            manifest_path=manifest_path if(manifest_path.is_file()) else (_manifest_path(directory)),
            manifest_version=manifest.get("version") if(isinstance(manifest.get("version"), str)) else None,
            manifest_role=manifest_role,
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
            "manifest_path": str(t.manifest_path) if(t.manifest_path is not None) else "",
            "manifest_version": t.manifest_version or "",
            "manifest_role": t.manifest_role or "",
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
    if(not path.exists()):
        raise FileNotFoundError(f"Schema file not found: {path}. Provide a valid --schema path before deriving a template from schema metadata.")
    schema=json.loads(path.read_text(encoding="utf-8"))
    config_type=schema.get("config_type") if(isinstance(schema, dict)) else None
    if(config_type is not None and config_type!="sldl.schema"):
        raise ValueError(f"Schema template source must use config_type sldl.schema, but {path} declares {config_type!r}.")

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
                manifest_path=None,
                manifest_version=None,
                manifest_role=None,
            )
        if(template_file or inline_template):
            template_path=(path.parent/(template_file or inline_template)).resolve()
            if(not template_path.exists()):
                raise FileNotFoundError(
                    f"Template file declared by schema was not found: schema={path}; document_type={candidate.get('document_type') or '-'}; "
                    f"declared_template_file={template_file or inline_template}; resolved_path={template_path}."
                )
            return Template(
                name=candidate.get("name", template_path.stem),
                description=candidate.get("description", candidate.get("name", template_path.stem)),
                content=template_path.read_text(encoding="utf-8"),
                source_path=template_path,
                document_type=candidate.get("document_type"),
                language=candidate.get("language"),
                schema=str(path.resolve()),
                strict_schema=strict_schema,
                manifest_path=None,
                manifest_version=None,
                manifest_role=None,
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
