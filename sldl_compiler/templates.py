from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class Template:
    name: str
    description: str
    content: str
    source_path: Path | None = None
    document_type: str | None = None
    language: str | None = None


def default_template_dir() -> Path:
    return Path(__file__).resolve().parent.parent/"templates"


def _normalize_template_dir(template_dir: str | Path | None) -> Path:
    if(template_dir is None):
        return default_template_dir()
    return Path(template_dir)


def _load_manifest(template_dir: Path) -> dict:
    manifest_path=template_dir/"manifest.json"
    if(not manifest_path.exists()):
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
        }
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def load_templates(template_dir: str | Path | None = None) -> dict[str, Template]:
    directory=_normalize_template_dir(template_dir)
    if(not directory.exists()):
        raise FileNotFoundError(f"Template directory not found: {directory}")

    manifest=_load_manifest(directory)
    result: dict[str, Template]={}
    for item in manifest.get("templates", []):
        name=item["name"]
        rel_path=item.get("path")
        if(not rel_path):
            continue
        source_path=(directory/rel_path).resolve()
        if(not source_path.exists()):
            raise FileNotFoundError(f"Template file not found: {source_path}")
        result[name]=Template(
            name=name,
            description=item.get("description", name),
            content=source_path.read_text(encoding="utf-8"),
            source_path=source_path,
            document_type=item.get("document_type"),
            language=item.get("language"),
        )
    return result


def list_templates(template_dir: str | Path | None = None) -> list[dict]:
    templates=load_templates(template_dir)
    return [
        {
            "name": t.name,
            "description": t.description,
            "document_type": t.document_type or "",
            "language": t.language or "",
            "source_path": str(t.source_path) if(t.source_path is not None) else "",
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
        if(inline_template is not None and "\n" in str(inline_template)):
            return Template(
                name=candidate.get("name", candidate.get("document_type", "schema_template")),
                description=candidate.get("description", candidate.get("name", candidate.get("document_type", "schema_template"))),
                content=str(inline_template),
                source_path=None,
                document_type=candidate.get("document_type"),
                language=candidate.get("language"),
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
            )

        template_name=candidate.get("template_name")
        template_dir=candidate.get("template_dir")
        if(template_name):
            base_dir=(path.parent/template_dir).resolve() if(template_dir) else None
            return get_template(template_name, base_dir)

    raise KeyError(
        "Schema does not define a template. "
        "Use 'template', 'template_file', or 'template_name' in the schema JSON, "
        "either at the top level or under document_types.<TypeName>."
    )
