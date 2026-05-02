from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re

from .ast_nodes import DocumentAst, Node, Value
from .diagnostics import Diagnostic


BIBLIOGRAPHY_META_FIELDS={
    "bibliography",
    "bibliographies",
    "bibtex",
    "bibtex_file",
    "bibtex_files",
    "references_file",
    "references_files",
}

BIBTEX_FIELD_ORDER=[
    "author",
    "title",
    "journal",
    "booktitle",
    "publisher",
    "year",
    "volume",
    "number",
    "pages",
    "doi",
    "url",
    "urldate",
    "note",
]


@dataclass
class BibEntry:
    entry_type: str
    key: str
    fields: dict[str, str]
    line: int = 0
    column: int = 0


class BibParser:
    def __init__(self, source: str):
        self.source=source
        self.pos=0
        self.line=1
        self.column=1
        self.diagnostics: list[Diagnostic]=[]

    def parse(self) -> tuple[list[BibEntry], list[Diagnostic]]:
        entries=[]
        while(not self._end()):
            self._skip_ws_and_comments()
            if(self._end()):
                break
            if(self._peek()!="@"):
                line,column=self.line,self.column
                self._advance()
                self.diagnostics.append(Diagnostic("warning", "W_BIBTEX_IGNORED_TEXT", "Ignored text outside BibTeX entry", line, column))
                continue
            entry=self._parse_entry()
            if(entry is not None):
                entries.append(entry)
        return entries,self.diagnostics

    def _parse_entry(self) -> BibEntry | None:
        start_line,start_col=self.line,self.column
        self._advance()
        entry_type=self._read_ident().lower()
        if(not entry_type):
            self.diagnostics.append(Diagnostic("error", "E_BIBTEX_PARSE", "BibTeX entry type is missing after @", start_line, start_col))
            return None
        self._skip_ws_and_comments()
        if(self._peek() not in "{("):
            self.diagnostics.append(Diagnostic("error", "E_BIBTEX_PARSE", f"BibTeX entry @{entry_type} must start with '{{' or '('", self.line, self.column))
            return None
        open_ch=self._advance()
        close_ch="}" if(open_ch=="{") else ")"

        if(entry_type in {"comment", "preamble"}):
            self._read_until_matching(close_ch)
            return None

        key=self._read_until_chars({",", close_ch}).strip()
        if(not key):
            self.diagnostics.append(Diagnostic("error", "E_BIBTEX_PARSE", f"BibTeX entry @{entry_type} has no key", start_line, start_col))
            self._read_until_matching(close_ch)
            return None
        if(self._peek()==close_ch):
            self._advance()
            return BibEntry(entry_type, key, {}, start_line, start_col)
        self._consume(",")

        if(entry_type=="string"):
            self._read_until_matching(close_ch)
            return None

        fields={}
        while(not self._end()):
            self._skip_ws_and_comments()
            if(self._peek()==close_ch):
                self._advance()
                break
            if(self._peek()==","):
                self._advance()
                continue

            field_line,field_col=self.line,self.column
            name=self._read_ident().lower()
            if(not name):
                self.diagnostics.append(Diagnostic("error", "E_BIBTEX_PARSE", "BibTeX field name is expected", field_line, field_col))
                self._recover_field(close_ch)
                continue
            self._skip_ws_and_comments()
            if(not self._consume("=")):
                self.diagnostics.append(Diagnostic("error", "E_BIBTEX_PARSE", f"BibTeX field {name} must use '='", self.line, self.column))
                self._recover_field(close_ch)
                continue
            value=self._read_value(close_ch)
            fields[name]=clean_bibtex_text(value)
            self._skip_ws_and_comments()
            if(self._peek()==","):
                self._advance()
                continue
            if(self._peek()==close_ch):
                self._advance()
                break
        return BibEntry(entry_type, key, fields, start_line, start_col)

    def _read_value(self, entry_close: str) -> str:
        parts=[]
        while(not self._end()):
            self._skip_ws_and_comments()
            ch=self._peek()
            if(ch=="{"):
                parts.append(self._read_braced())
            elif(ch=='"'):
                parts.append(self._read_quoted())
            else:
                parts.append(self._read_bare_value(entry_close))
            self._skip_ws_and_comments()
            if(self._peek()=="#"):
                self._advance()
                continue
            break
        return "".join(parts).strip()

    def _read_braced(self) -> str:
        start_line,start_col=self.line,self.column
        if(not self._consume("{")):
            return ""
        depth=1
        chars=[]
        while(not self._end()):
            ch=self._advance()
            if(ch=="\\"):
                if(not self._end()):
                    chars.append(ch)
                    chars.append(self._advance())
                else:
                    chars.append(ch)
                continue
            if(ch=="{"):
                depth+=1
                chars.append(ch)
                continue
            if(ch=="}"):
                depth-=1
                if(depth==0):
                    return "".join(chars)
                chars.append(ch)
                continue
            chars.append(ch)
        self.diagnostics.append(Diagnostic("error", "E_BIBTEX_PARSE", "Unterminated braced BibTeX value", start_line, start_col))
        return "".join(chars)

    def _read_quoted(self) -> str:
        start_line,start_col=self.line,self.column
        self._advance()
        chars=[]
        while(not self._end()):
            ch=self._advance()
            if(ch=="\\"):
                if(not self._end()):
                    esc=self._advance()
                    chars.append("\\"+esc)
                else:
                    chars.append("\\")
                continue
            if(ch=='"'):
                return "".join(chars)
            chars.append(ch)
        self.diagnostics.append(Diagnostic("error", "E_BIBTEX_PARSE", "Unterminated quoted BibTeX value", start_line, start_col))
        return "".join(chars)

    def _read_bare_value(self, entry_close: str) -> str:
        chars=[]
        while(not self._end()):
            ch=self._peek()
            if(ch in {",", "#", entry_close}):
                break
            chars.append(self._advance())
        return "".join(chars).strip()

    def _read_until_matching(self, close_ch: str) -> str:
        depth=1
        chars=[]
        while(not self._end()):
            ch=self._advance()
            if(ch=="\\" and not self._end()):
                chars.append(ch)
                chars.append(self._advance())
                continue
            if(ch=="{" and close_ch=="}"):
                depth+=1
                chars.append(ch)
                continue
            if(ch==close_ch):
                depth-=1
                if(depth==0):
                    return "".join(chars)
            chars.append(ch)
        return "".join(chars)

    def _recover_field(self, close_ch: str) -> None:
        while(not self._end() and self._peek() not in {",", close_ch}):
            self._advance()
        if(self._peek()==","):
            self._advance()

    def _read_until_chars(self, chars: set[str]) -> str:
        result=[]
        while(not self._end() and self._peek() not in chars):
            result.append(self._advance())
        return "".join(result)

    def _read_ident(self) -> str:
        result=[]
        while(not self._end()):
            ch=self._peek()
            if(ch.isalnum() or ch in "_-:./"):
                result.append(self._advance())
            else:
                break
        return "".join(result)

    def _skip_ws_and_comments(self) -> None:
        while(not self._end()):
            ch=self._peek()
            if(ch.isspace()):
                self._advance()
                continue
            if(ch=="%"):
                while(not self._end() and self._peek()!="\n"):
                    self._advance()
                continue
            break

    def _consume(self, ch: str) -> bool:
        if(self._peek()==ch):
            self._advance()
            return True
        return False

    def _peek(self) -> str:
        if(self._end()):
            return "\0"
        return self.source[self.pos]

    def _end(self) -> bool:
        return self.pos>=len(self.source)

    def _advance(self) -> str:
        ch=self.source[self.pos]
        self.pos+=1
        if(ch=="\n"):
            self.line+=1
            self.column=1
        else:
            self.column+=1
        return ch


def parse_bibtex(source: str) -> tuple[list[BibEntry], list[Diagnostic]]:
    return BibParser(source).parse()


def clean_bibtex_text(text: str) -> str:
    result=text.strip()
    replacements={
        r"\&": "&",
        r"\%": "%",
        r"\_": "_",
        r"\#": "#",
        r"\{": "{",
        r"\}": "}",
        r"~": " ",
    }
    for before,after in replacements.items():
        result=result.replace(before, after)
    # Keep the value readable for Markdown/HTML exports by removing BibTeX grouping braces.
    result=result.replace("{", "").replace("}", "")
    result=re.sub(r"\s+", " ", result)
    return result.strip()


def reference_id_from_bibkey(key: str) -> str:
    result=[]
    for ch in key:
        if(ch.isalnum() or ch in {"_", "-", "."}):
            result.append(ch)
        else:
            result.append("_")
    value="".join(result).strip("._-")
    if(not value):
        value="ref"
    if(not (value[0].isalpha() or value[0]=="_")):
        value="ref_"+value
    return value


def bib_entry_to_reference(entry: BibEntry, source_file: str | None = None, existing_ids: set[str] | None = None) -> Node:
    base_id=reference_id_from_bibkey(entry.key)
    ref_id=base_id
    if(existing_ids is not None):
        i=2
        while(ref_id in existing_ids):
            ref_id=f"{base_id}_{i}"
            i+=1
    fields: dict[str, Value]={}
    fields["type"]=Value("String", entry.entry_type, entry.line, entry.column)
    fields["bibkey"]=Value("String", entry.key, entry.line, entry.column)
    if(source_file):
        fields["imported_from"]=Value("String", source_file, entry.line, entry.column)

    mapped=dict(entry.fields)
    if("urldate" in mapped and "accessed" not in mapped):
        mapped["accessed"]=mapped["urldate"]

    for name in BIBTEX_FIELD_ORDER:
        if(name not in mapped):
            continue
        out_name="accessed" if(name=="urldate") else name
        raw=mapped[name]
        if(out_name=="year" and re.fullmatch(r"-?\d+", raw or "")):
            fields[out_name]=Value("Number", int(raw), entry.line, entry.column)
        else:
            fields[out_name]=Value("String", raw, entry.line, entry.column)

    for name,raw in mapped.items():
        if(name in BIBTEX_FIELD_ORDER or (name=="urldate" and "accessed" in fields)):
            continue
        safe_name=re.sub(r"[^A-Za-z0-9_.-]", "_", name)
        if(safe_name and safe_name not in fields):
            fields[safe_name]=Value("String", raw, entry.line, entry.column)

    return Node(kind="Reference", id=ref_id, type_name="Reference", fields=fields, children=[], line=entry.line, column=entry.column)


def bibliography_paths_from_doc(doc: DocumentAst) -> list[tuple[str, int, int]]:
    if(doc.meta is None):
        return []
    results=[]
    for field_name,value in doc.meta.fields.items():
        if(field_name.rstrip("?") not in BIBLIOGRAPHY_META_FIELDS):
            continue
        results.extend(_paths_from_value(value))
    return results


def _paths_from_value(value: Value) -> list[tuple[str, int, int]]:
    if(value.kind=="String"):
        return [(str(value.value), value.line, value.column)]
    if(value.kind=="TextLang"):
        return [(str(value.value["text"]), value.line, value.column)]
    if(value.kind=="List"):
        result=[]
        for item in value.value:
            result.extend(_paths_from_value(item))
        return result
    return []


def attach_bibtex_references(doc: DocumentAst, sldl_path: Path) -> None:
    paths=bibliography_paths_from_doc(doc)
    if(not paths):
        return
    existing=_collect_ids(doc.children)
    base_dir=sldl_path.parent
    for raw_path,line,column in paths:
        bib_path=Path(raw_path)
        if(not bib_path.is_absolute()):
            bib_path=base_dir/bib_path
        try:
            source=bib_path.read_text(encoding="utf-8")
        except OSError as exc:
            doc.diagnostics.append(Diagnostic("error", "E_BIBTEX_FILE", f"Cannot read BibTeX file: {raw_path} ({exc})", line, column))
            continue
        entries,diagnostics=parse_bibtex(source)
        for diag in diagnostics:
            doc.diagnostics.append(Diagnostic(diag.level, diag.code, f"{raw_path}: {diag.message}", diag.line, diag.column))
        for entry in entries:
            ref=bib_entry_to_reference(entry, raw_path, existing)
            if(ref.id in existing):
                doc.diagnostics.append(Diagnostic("warning", "W_BIBTEX_DUPLICATE_REFERENCE", f"Duplicate imported reference id skipped: {ref.id}", entry.line, entry.column))
                continue
            doc.children.append(ref)
            existing.add(ref.id)


def _collect_ids(nodes: list[Node]) -> set[str]:
    result=set()
    def visit(node: Node) -> None:
        if(node.id):
            result.add(node.id)
        for child in node.children:
            visit(child)
    for node in nodes:
        visit(node)
    return result


def bibtex_to_sldl_fragment(entries: list[BibEntry], source_file: str | None = None) -> str:
    existing:set[str]=set()
    nodes=[]
    for entry in entries:
        node=bib_entry_to_reference(entry, source_file, existing)
        if(node.id):
            existing.add(node.id)
        nodes.append(node)
    return "\n\n".join(reference_to_sldl(node) for node in nodes).rstrip()+("\n" if(nodes) else "")


def reference_to_sldl(node: Node) -> str:
    lines=[f"reference {node.id} : Reference "+"{"]
    field_order=["type", "bibkey", "title", "author", "journal", "booktitle", "publisher", "year", "volume", "number", "pages", "doi", "url", "accessed", "note", "imported_from"]
    keys=[k for k in field_order if(k in node.fields)]
    keys.extend(k for k in node.fields if(k not in keys))
    for key in keys:
        lines.append(f"    {key}: {_value_to_sldl(node.fields[key])};")
    lines.append("}")
    return "\n".join(lines)


def _value_to_sldl(value: Value) -> str:
    if(value.kind=="Number"):
        return str(value.value)
    if(value.kind=="Bool"):
        return "true" if(value.value) else "false"
    if(value.kind=="Null"):
        return "null"
    return "\""+str(value.value).replace("\\", "\\\\").replace('"', '\\"')+"\""
