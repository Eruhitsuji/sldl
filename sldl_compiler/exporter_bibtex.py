from __future__ import annotations

from .ast_nodes import DocumentAst, Node
from .export_support import ExportContext, ordered_references, plain


BIBTEX_FIELD_ORDER=["author", "title", "journal", "booktitle", "publisher", "year", "volume", "number", "pages", "doi", "url", "accessed", "note"]


def export_bibtex(doc: DocumentAst) -> str:
    ctx=ExportContext.build(doc)
    entries=[]
    for _, ref_id, ref in ordered_references(ctx):
        entries.append(_reference_to_bibtex(ref_id, ref))
    return "\n\n".join(entries).rstrip()+("\n" if(entries) else "")


def _reference_to_bibtex(ref_id: str, ref: Node) -> str:
    entry_type=plain(ref.fields.get("type")).lower() if("type" in ref.fields) else ""
    if(entry_type not in {"article", "book", "inproceedings", "misc", "techreport", "phdthesis", "mastersthesis"}):
        entry_type="article" if("journal" in ref.fields) else "misc"
    key=plain(ref.fields.get("bibkey")) if("bibkey" in ref.fields) else ref_id
    lines=[f"@{entry_type}"+"{"+_safe_key(key)+","]
    for field in BIBTEX_FIELD_ORDER:
        if(field in ref.fields):
            bib_field="urldate" if(field=="accessed") else field
            lines.append(f"  {bib_field} = {{{_escape_bibtex(plain(ref.fields[field]))}}},")
    if(len(lines)>1):
        lines[-1]=lines[-1].rstrip(",")
    lines.append("}")
    return "\n".join(lines)


def _safe_key(text: str) -> str:
    return "".join(ch if(ch.isalnum() or ch in "_:-") else "_" for ch in text)


def _escape_bibtex(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "\\{").replace("}", "\\}")
