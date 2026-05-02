from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


CONFIG_METADATA_KEYS={"config_type", "description", "name", "schema_version", "$schema"}

DEFAULT_LABELS={
    "author": "Author",
    "date": "Date",
    "version": "Version",
    "section": "Section",
    "toc": "Table of Contents",
    "claim": "Claim",
    "evidence": "Evidence",
    "reason": "Reason",
    "counterargument": "Counterargument",
    "conclusion": "Conclusion",
    "definition": "Definition",
    "object": "Object",
    "class": "Class",
    "function": "Function",
    "references": "References",
    "figure": "Figure",
    "table": "Table",
    "listing": "Listing",
}


@dataclass(frozen=True)
class ExportLabels:
    labels: dict[str, str] = field(default_factory=lambda: dict(DEFAULT_LABELS))
    html_lang: str = "en"

    def get(self, key: str, default: str | None = None) -> str:
        return self.labels.get(key, default or key)


def load_export_labels(config_path: str | None = None, base_path: str | None = None) -> ExportLabels:
    labels=dict(DEFAULT_LABELS)
    html_lang="en"
    if(config_path):
        data=_read_config(config_path, base_path)
        raw_labels=data.get("labels")
        if(raw_labels is None):
            raw_labels={key: value for key,value in data.items() if(key not in CONFIG_METADATA_KEYS and key != "html_lang")}
        if(not isinstance(raw_labels, dict)):
            raise ValueError("export label config must contain an object or a labels object")
        for key,value in raw_labels.items():
            if(isinstance(value, str)):
                labels[key]=value
        if(isinstance(data.get("html_lang"), str)):
            html_lang=data["html_lang"]
    return ExportLabels(labels=labels, html_lang=html_lang)


def _read_config(config_path: str, base_path: str | None = None) -> dict[str, Any]:
    path=Path(config_path)
    if((not path.is_absolute()) and not path.exists() and base_path is not None):
        path=Path(base_path)/path
    data=json.loads(path.read_text(encoding="utf-8"))
    if(not isinstance(data, dict)):
        raise ValueError("export label config root must be an object")
    return data
