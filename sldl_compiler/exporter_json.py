from __future__ import annotations

import json

from .ast_nodes import DocumentAst


def export_json(doc: DocumentAst, indent: int = 2) -> str:
    return json.dumps(doc.to_dict(), ensure_ascii=False, indent=indent)
