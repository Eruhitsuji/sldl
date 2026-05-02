from __future__ import annotations

from dataclasses import dataclass, field
import re
from typing import Iterable

from .ast_nodes import DocumentAst, Node, Value
from .export_config import ExportLabels, load_export_labels, DEFAULT_LABELS


CITATION_FIELDS={"cite", "source", "based_on"}
XREF_FIELD_NAMES={"xref", "xrefs", "ref", "refs"}


@dataclass
class ExportContext:
    doc: DocumentAst
    citation_numbers: dict[str, int] = field(default_factory=dict)
    table_numbers: dict[str, int] = field(default_factory=dict)
    figure_numbers: dict[str, int] = field(default_factory=dict)
    listing_numbers: dict[str, int] = field(default_factory=dict)
    section_numbers: dict[str, str] = field(default_factory=dict)
    section_titles: dict[str, str] = field(default_factory=dict)
    citation_style: str = "numeric"
    labels: ExportLabels = field(default_factory=lambda: load_export_labels())

    @classmethod
    def build(
        cls,
        doc: DocumentAst,
        citation_style: str | None = None,
        export_config_path: str | None = None,
        base_path: str | None = None,
    ) -> "ExportContext":
        if(citation_style is None):
            citation_style=_meta_string(doc, "citation_style") or _meta_string(doc, "cite_style") or "numeric"
        config_path=export_config_path or _meta_string(doc, "export_config") or _meta_string(doc, "export_labels")
        labels=load_export_labels(config_path, base_path=base_path)
        if(config_path is None):
            lang=_meta_string(doc, "lang") or _meta_string(doc, "language") or ""
            if(lang.lower().startswith("ja")):
                ja_labels=dict(DEFAULT_LABELS)
                ja_labels.update({
                    "author": "著者",
                    "date": "日付",
                    "version": "バージョン",
                    "references": "参考文献",
                    "figure": "図",
                    "table": "表",
                    "listing": "リスト",
                })
                labels=ExportLabels(labels=ja_labels, html_lang="ja")
        ctx=cls(doc=doc, citation_style=normalize_citation_style(citation_style), labels=labels)
        ctx._assign_numbers(doc.children)
        return ctx

    def label(self, key: str, default: str | None = None) -> str:
        return self.labels.get(key, default)

    def numbered_bibliography(self) -> bool:
        return self.citation_style in {"numeric", "ieee"}

    def _assign_numbers(self, nodes: list[Node]) -> None:
        self._assign_section_numbers(nodes, [])
        table_n=1
        figure_n=1
        listing_n=1
        for node in walk_nodes(nodes):
            if(node.kind=="Table" and node.id):
                self.table_numbers[node.id]=table_n
                table_n+=1
            elif(node.kind in {"Figure", "Chart", "Flowchart"} and node.id):
                self.figure_numbers[node.id]=figure_n
                figure_n+=1
            elif(node.kind=="CodeBlock" and node.id):
                self.listing_numbers[node.id]=listing_n
                listing_n+=1
        for node in walk_nodes(nodes):
            for ref_id in citation_ids(self, node):
                self.ensure_citation(ref_id)
        for node in nodes:
            if(node.kind=="Reference" and node.id):
                self.ensure_citation(node.id)

    def _assign_section_numbers(self, nodes: list[Node], prefix: list[int]) -> None:
        section_index=0
        for node in nodes:
            if(node.kind=="Section" and not is_reference_section(node)):
                section_index+=1
                number_parts=prefix+[section_index]
                if(node.id):
                    self.section_numbers[node.id]=".".join(str(part) for part in number_parts)
                    self.section_titles[node.id]=node_caption(node, node.id)
                self._assign_section_numbers(node.children, number_parts)
            else:
                self._assign_section_numbers(node.children, prefix)

    def ensure_citation(self, ref_id: str) -> int:
        if(ref_id not in self.citation_numbers):
            self.citation_numbers[ref_id]=len(self.citation_numbers)+1
        return self.citation_numbers[ref_id]

    def table_label(self, node: Node) -> str:
        number=self.table_numbers.get(node.id or "", 0)
        return f"{self.label('table', 'Table')}{number}" if(number) else self.label("table", "Table")

    def figure_label(self, node: Node) -> str:
        number=self.figure_numbers.get(node.id or "", 0)
        return f"{self.label('figure', 'Figure')}{number}" if(number) else self.label("figure", "Figure")

    def listing_label(self, node: Node) -> str:
        number=self.listing_numbers.get(node.id or "", 0)
        return f"{self.label('listing', 'Listing')}{number}" if(number) else self.label("listing", "Listing")

    def section_label(self, node: Node) -> str:
        number=self.section_numbers.get(node.id or "", "")
        return f"{self.label('section', 'Section')}{number}" if(number) else self.label("section", "Section")

    def target_label(self, target_id: str) -> str:
        node=self.doc.symbols.get(target_id)
        if(node is None):
            return target_id
        if(node.kind=="Section"):
            return self.section_label(node)
        if(node.kind in {"Figure", "Chart", "Flowchart"}):
            return self.figure_label(node)
        if(node.kind=="Table"):
            return self.table_label(node)
        if(node.kind=="CodeBlock"):
            return self.listing_label(node)
        return f"{self.label(node.kind.lower(), node.kind)} {target_id}"

    def target_anchor(self, target_id: str) -> str:
        return "sldl-"+safe_anchor_id(target_id)

    def section_toc_items(self) -> list[tuple[int, str, str, str]]:
        items=[]
        for node in walk_nodes(self.doc.children):
            if(node.kind=="Section" and node.id and not is_reference_section(node)):
                number=self.section_numbers.get(node.id, "")
                depth=number.count(".")+1 if(number) else 1
                title=self.section_titles.get(node.id, node_caption(node, node.id))
                items.append((depth, node.id, number, title))
        return items


def normalize_citation_style(style: str | None) -> str:
    if(not style):
        return "numeric"
    s=str(style).strip().lower().replace("_", "-")
    aliases={
        "number": "numeric",
        "numbers": "numeric",
        "numeric": "numeric",
        "ieee": "ieee",
        "apa": "apa",
        "author-year": "author-year",
        "authoryear": "author-year",
        "year-author": "author-year",
        "著者年": "author-year",
        "著者-年": "author-year",
    }
    return aliases.get(s, "numeric")


def walk_nodes(nodes: Iterable[Node]):
    for node in nodes:
        yield node
        yield from walk_nodes(node.children)



def is_reference_section(node: Node) -> bool:
    """Return True when a Section is only a container for bibliography entries.

    Such sections exist in SLDL source so schemas can control where references
    are declared, but Markdown/HTML exporters render the bibliography once via
    the configured localized label. Rendering the Section heading as well would
    produce duplicate headings such as "references" and "参考文献".
    """
    if(node.kind!="Section"):
        return False
    if(not node.children):
        return False
    return all(child.kind=="Reference" for child in node.children)

def plain(value: Value | None) -> str:
    if(value is None):
        return ""
    if(value.kind=="TextLang"):
        return str(value.value["text"])
    if(value.kind in {"String", "Number", "Bool"}):
        return str(value.value)
    if(value.kind=="Identifier"):
        return str(value.value)
    if(value.kind=="List"):
        return ", ".join(plain(v) for v in value.value)
    if(value.kind=="Object"):
        return ", ".join(f"{k}={plain(v)}" for k,v in value.value.items())
    if(value.kind=="FunctionCall"):
        name=value.value["name"]
        args=value.value["args"]
        if(name in {"Date", "Time", "DateTime"} and len(args)==1):
            return plain(args[0])
        return f"{name}("+", ".join(plain(v) for v in args)+")"
    if(value.kind=="Raw"):
        return str(value.value)
    return str(value.value)


def _meta_string(doc: DocumentAst, key: str) -> str | None:
    if(doc.meta is None or key not in doc.meta.fields):
        return None
    result=plain(doc.meta.fields[key]).strip()
    return result or None


def meta_bool(doc: DocumentAst, keys: tuple[str, ...], default: bool = False) -> bool:
    if(doc.meta is None):
        return default
    for key in keys:
        if(key in doc.meta.fields):
            value=doc.meta.fields[key]
            if(value.kind=="Bool"):
                return bool(value.value)
            text=plain(value).strip().lower()
            if(text in {"1", "true", "yes", "on", "enable", "enabled"}):
                return True
            if(text in {"0", "false", "no", "off", "disable", "disabled"}):
                return False
    return default


def safe_anchor_id(value: str) -> str:
    safe=re.sub(r"[^A-Za-z0-9_.:-]+", "-", str(value))
    return safe.strip("-") or "unnamed"


def cross_reference_ids(node: Node) -> list[str]:
    """Return unique ids from explicit cross-reference fields."""
    ids=[]
    for key,value in node.fields.items():
        normalized=key.rstrip("?")
        if(normalized in XREF_FIELD_NAMES):
            for raw in _iter_reference_names(value):
                if(raw not in ids):
                    ids.append(raw)
    return ids


def xref_marker_ids(text: str) -> list[str]:
    ids=[]
    pattern=re.compile(r"\{\{\s*(?:ref|xref)\s*:\s*([A-Za-z0-9_.:-]+)\s*\}\}")
    for match in pattern.finditer(text or ""):
        target_id=match.group(1)
        if(target_id not in ids):
            ids.append(target_id)
    return ids


def cross_reference_ids_for_display(node: Node, text_field: str | None = None) -> list[str]:
    """Return explicit cross-references, excluding already rendered inline markers.

    `xrefs` can be used as machine-readable metadata while `{{ref:id}}`
    renders the same reference inline. This helper prevents duplicate
    parenthesized references in human-readable exports.
    """
    ids=cross_reference_ids(node)
    if(text_field is None or text_field not in node.fields):
        return ids
    inline=set(xref_marker_ids(plain(node.fields.get(text_field))))
    return [target_id for target_id in ids if(target_id not in inline)]


def replace_xref_markers(text: str, formatter) -> str:
    pattern=re.compile(r"\{\{\s*(?:ref|xref)\s*:\s*([A-Za-z0-9_.:-]+)\s*\}\}")
    return pattern.sub(lambda m: formatter(m.group(1)), text)


def _iter_reference_names(value: Value):
    if(value.kind=="Identifier"):
        yield str(value.value)
    elif(value.kind=="String"):
        yield str(value.value)
    elif(value.kind=="TextLang"):
        yield str(value.value["text"])
    elif(value.kind=="List"):
        for item in value.value:
            yield from _iter_reference_names(item)
    elif(value.kind=="FunctionCall"):
        for arg in value.value["args"]:
            yield from _iter_reference_names(arg)


def citation_ids(ctx: ExportContext, node: Node) -> list[str]:
    ids=[]
    for key,value in node.fields.items():
        normalized=key.rstrip("?")
        if(normalized in CITATION_FIELDS):
            for raw in _iter_reference_names(value):
                ref_id=ctx.doc.reference_aliases.get(raw, raw)
                ref=ctx.doc.symbols.get(ref_id)
                if(ref is not None and ref.kind=="Reference" and ref_id not in ids):
                    ids.append(ref_id)
    return ids


def markdown_citations(ctx: ExportContext, node: Node) -> str:
    ids=citation_ids(ctx, node)
    if(not ids):
        return ""
    return " "+format_citation(ctx, ids, html=False)


def html_citation_links(ctx: ExportContext, node: Node) -> str:
    ids=citation_ids(ctx, node)
    if(not ids):
        return ""
    return " "+format_citation(ctx, ids, html=True)


def format_citation(ctx: ExportContext, ref_ids: list[str], html: bool = False) -> str:
    if(ctx.citation_style=="ieee"):
        labels=[]
        for ref_id in ref_ids:
            number=ctx.ensure_citation(ref_id)
            label=f"[{number}]"
            labels.append(_citation_link(label, number, html))
        return ", ".join(labels)

    if(ctx.citation_style=="numeric"):
        numbers=[ctx.ensure_citation(ref_id) for ref_id in ref_ids]
        if(html):
            return "["+", ".join(_citation_link(str(n), n, True) for n in numbers)+"]"
        return "["+", ".join(str(n) for n in numbers)+"]"

    parts=[]
    for ref_id in ref_ids:
        number=ctx.ensure_citation(ref_id)
        ref=ctx.doc.symbols.get(ref_id)
        if(ref is None):
            continue
        label=author_year_label(ref, comma=(ctx.citation_style=="apa"))
        parts.append(_citation_link(label, number, html))
    return "("+"; ".join(parts)+")"


def _citation_link(label: str, number: int, html: bool) -> str:
    if(not html):
        return label
    return f'<a href="#ref-{number}">{label}</a>'


def node_caption(node: Node, default: str = "") -> str:
    if("caption" in node.fields):
        return plain(node.fields["caption"])
    if("title" in node.fields):
        return plain(node.fields["title"])
    return default


def ordered_references(ctx: ExportContext) -> list[tuple[int, str, Node]]:
    refs=[]
    for ref_id,number in sorted(ctx.citation_numbers.items(), key=lambda x: x[1]):
        node=ctx.doc.symbols.get(ref_id)
        if(node is not None and node.kind=="Reference"):
            refs.append((number, ref_id, node))
    return refs


def reference_text(ref: Node, citation_style: str = "numeric") -> str:
    if(citation_style=="apa"):
        return reference_text_apa(ref)
    if(citation_style=="ieee"):
        return reference_text_ieee(ref)
    if(citation_style=="author-year"):
        return reference_text_author_year(ref)
    return reference_text_numeric(ref)


def reference_text_numeric(ref: Node) -> str:
    title=plain(ref.fields.get("title")) or (ref.id or "Reference")
    author=plain(ref.fields.get("author"))
    year=plain(ref.fields.get("year"))
    venue=plain(ref.fields.get("journal")) or plain(ref.fields.get("booktitle")) or plain(ref.fields.get("venue")) or plain(ref.fields.get("publisher"))
    doi=plain(ref.fields.get("doi"))
    url=plain(ref.fields.get("url"))
    parts=[]
    if(author): parts.append(author)
    if(year): parts.append(f"({year})")
    parts.append(title)
    if(venue): parts.append(venue)
    if(doi): parts.append(f"doi:{doi}")
    if(url): parts.append(url)
    return ". ".join(parts)


def reference_text_apa(ref: Node) -> str:
    author=plain(ref.fields.get("author"))
    year=plain(ref.fields.get("year")) or "n.d."
    title=plain(ref.fields.get("title")) or (ref.id or "Reference")
    venue=plain(ref.fields.get("journal")) or plain(ref.fields.get("booktitle")) or plain(ref.fields.get("venue")) or plain(ref.fields.get("publisher"))
    volume=plain(ref.fields.get("volume"))
    number=plain(ref.fields.get("number"))
    pages=plain(ref.fields.get("pages"))
    doi=plain(ref.fields.get("doi"))
    url=plain(ref.fields.get("url"))
    parts=[]
    if(author):
        formatted_author=format_author_list_apa(author)
        if(formatted_author and not formatted_author.endswith(".")):
            formatted_author=formatted_author+"."
        parts.append(formatted_author+f" ({year}).")
    else: parts.append(f"({year}).")
    parts.append(f"{title}.")
    if(venue):
        venue_text=venue
        if(volume):
            venue_text+=f", {volume}"
            if(number): venue_text+=f"({number})"
        if(pages): venue_text+=f", {pages}"
        parts.append(venue_text+".")
    if(doi): parts.append(f"https://doi.org/{doi}" if(not doi.startswith("http")) else doi)
    elif(url): parts.append(url)
    return " ".join(p for p in parts if(p)).strip()


def reference_text_ieee(ref: Node) -> str:
    author=plain(ref.fields.get("author"))
    title=plain(ref.fields.get("title")) or (ref.id or "Reference")
    venue=plain(ref.fields.get("journal")) or plain(ref.fields.get("booktitle")) or plain(ref.fields.get("venue")) or plain(ref.fields.get("publisher"))
    volume=plain(ref.fields.get("volume"))
    number=plain(ref.fields.get("number"))
    pages=plain(ref.fields.get("pages"))
    year=plain(ref.fields.get("year"))
    doi=plain(ref.fields.get("doi"))
    url=plain(ref.fields.get("url"))
    parts=[]
    if(author): parts.append(author)
    parts.append(f'"{title}"')
    if(venue): parts.append(venue)
    if(volume): parts.append(f"vol. {volume}")
    if(number): parts.append(f"no. {number}")
    if(pages): parts.append(f"pp. {pages}")
    if(year): parts.append(year)
    text=", ".join(parts)+"."
    if(doi): text+=f" doi: {doi}."
    elif(url): text+=f" {url}."
    return text


def reference_text_author_year(ref: Node) -> str:
    author=plain(ref.fields.get("author"))
    year=plain(ref.fields.get("year")) or "n.d."
    title=plain(ref.fields.get("title")) or (ref.id or "Reference")
    venue=plain(ref.fields.get("journal")) or plain(ref.fields.get("booktitle")) or plain(ref.fields.get("venue")) or plain(ref.fields.get("publisher"))
    parts=[]
    if(author): parts.append(f"{author} ({year})")
    else: parts.append(f"({year})")
    parts.append(title)
    if(venue): parts.append(venue)
    doi=plain(ref.fields.get("doi"))
    url=plain(ref.fields.get("url"))
    if(doi): parts.append(f"doi:{doi}")
    if(url): parts.append(url)
    return ". ".join(parts)


def author_year_label(ref: Node, comma: bool = True) -> str:
    author=plain(ref.fields.get("author"))
    year=plain(ref.fields.get("year")) or "n.d."
    title=plain(ref.fields.get("title")) or (ref.id or "Reference")
    author_label=short_author_label(author) if(author) else title
    sep=", " if(comma) else " "
    return f"{author_label}{sep}{year}"


def short_author_label(author: str) -> str:
    names=_split_authors(author)
    surnames=[_surname(name) for name in names if(_surname(name))]
    if(not surnames):
        return author
    if(len(surnames)==1):
        return surnames[0]
    if(len(surnames)==2):
        return f"{surnames[0]} & {surnames[1]}"
    return f"{surnames[0]} et al."


def format_author_list_apa(author: str) -> str:
    names=_split_authors(author)
    formatted=[]
    for name in names:
        parts=name.split()
        if(len(parts)==2 and parts[0] in {"John"}):
            formatted.append(name)
            continue
        surname=_surname(name)
        initials=_initials(name)
        formatted.append(f"{surname}, {initials}" if(initials) else surname)
    if(not formatted):
        return author
    if(len(formatted)==1):
        return formatted[0]
    if(len(formatted)==2):
        return f"{formatted[0]}, & {formatted[1]}"
    return ", ".join(formatted[:-1])+f", & {formatted[-1]}"


def _split_authors(author: str) -> list[str]:
    if(" and " in author):
        return [p.strip() for p in re.split(r"\s+and\s+", author) if(p.strip())]
    if(";" in author):
        return [p.strip() for p in author.split(";") if(p.strip())]
    return [author.strip()] if(author.strip()) else []


def _surname(name: str) -> str:
    name=name.strip()
    if(not name):
        return ""
    if("," in name):
        return name.split(",", 1)[0].strip()
    parts=name.split()
    return parts[-1] if(parts) else name


def _initials(name: str) -> str:
    name=name.strip()
    if(not name):
        return ""
    if("," in name):
        rest=name.split(",", 1)[1].strip()
        parts=rest.split()
    else:
        parts=name.split()[:-1]
    initials=[]
    for part in parts:
        cleaned=re.sub(r"[^A-Za-zÀ-ÖØ-öø-ÿ]", "", part)
        if(cleaned):
            initials.append(cleaned[0].upper()+".")
    return " ".join(initials)


def flowchart_mermaid(node: Node) -> str:
    direction=plain(node.fields.get("direction")) or "TD"
    lines=[f"flowchart {direction}"]
    nodes=node.fields.get("nodes")
    edges=node.fields.get("edges")

    node_labels=_flowchart_node_labels(nodes)
    for nid,label in node_labels.items():
        lines.append(f"    {nid}[{_mermaid_escape(label or nid)}]")

    if(edges and edges.kind=="List"):
        for item in edges.value:
            src=""
            dst=""
            label=""
            if(item.kind=="Object"):
                src=plain(item.value.get("from"))
                dst=plain(item.value.get("to"))
                label=plain(item.value.get("label")) if("label" in item.value) else ""
            elif(item.kind=="List" and len(item.value) in {2,3}):
                src=plain(item.value[0])
                dst=plain(item.value[1])
                label=plain(item.value[2]) if(len(item.value)==3) else ""
            if(src and dst):
                if(label): lines.append(f"    {src} -- {_mermaid_escape(label)} --> {dst}")
                else: lines.append(f"    {src} --> {dst}")
    return "\n".join(lines)


def _flowchart_node_labels(value: Value | None) -> dict[str, str]:
    labels={}
    if(value is None):
        return labels
    if(value.kind=="Object"):
        for nid,label_value in value.value.items():
            labels[str(nid)]=plain(label_value)
    elif(value.kind=="List"):
        for item in value.value:
            if(item.kind=="Object"):
                nid=plain(item.value.get("id"))
                label=plain(item.value.get("label")) or nid
                if(nid):
                    labels[nid]=label
            elif(item.kind in {"Identifier", "String", "TextLang"}):
                nid=plain(item)
                if(nid):
                    labels[nid]=nid
    return labels


def chart_mermaid(ctx: ExportContext, node: Node) -> str:
    chart_type=plain(node.fields.get("chart_type")) or plain(node.fields.get("type")) or "bar"
    title=node_caption(node, node.id or "Chart")
    x_name=plain(node.fields.get("x"))
    y_name=plain(node.fields.get("y"))
    x_label=plain(node.fields.get("x_label")) or x_name or "x"
    y_label=plain(node.fields.get("y_label")) or y_name or "y"
    xs=[]
    ys=[]
    _collect_chart_points(ctx, node, x_name, y_name, xs, ys)
    lines=["xychart-beta", f"    title \"{_mermaid_escape(title)}\"", f"    x-axis \"{_mermaid_escape(x_label)}\" [{', '.join(xs)}]", f"    y-axis \"{_mermaid_escape(y_label)}\""]
    keyword="line" if(chart_type.lower()=="line") else "bar"
    lines.append(f"    {keyword} [{', '.join(ys)}]")
    return "\n".join(lines)


def _collect_chart_points(ctx: ExportContext, node: Node, x_name: str, y_name: str, xs: list[str], ys: list[str]) -> None:
    data=node.fields.get("data")
    if(data is None):
        return
    if(data.kind=="List"):
        for item in data.value:
            if(item.kind=="Object"):
                x=plain(item.value.get("x")) or plain(item.value.get(x_name))
                y=plain(item.value.get("y")) or plain(item.value.get(y_name))
                if(x and y):
                    xs.append(_format_mermaid_x_value(x))
                    ys.append(_format_mermaid_y_value(y))
        return
    if(data.kind=="Identifier"):
        target=ctx.doc.symbols.get(str(data.value))
        if(target is None or target.kind!="Table"):
            return
        columns=target.fields.get("columns")
        rows=target.fields.get("rows")
        if(columns is None or columns.kind!="List" or rows is None or rows.kind!="List"):
            return
        headers=[]
        for col in columns.value:
            if(col.kind=="Object" and "name" in col.value):
                headers.append(plain(col.value["name"]))
        try:
            x_idx=headers.index(x_name)
            y_idx=headers.index(y_name)
        except ValueError:
            return
        for row in rows.value:
            if(row.kind=="List" and len(row.value)>max(x_idx,y_idx)):
                x=plain(row.value[x_idx])
                y=plain(row.value[y_idx])
                if(x and y):
                    xs.append(_format_mermaid_x_value(x))
                    ys.append(_format_mermaid_y_value(y))


def _format_mermaid_x_value(value: str) -> str:
    compact=value.replace(".", "", 1).replace("-", "", 1)
    if(compact.isdigit()):
        return value
    return '"'+_mermaid_escape(value)+'"'


def _format_mermaid_y_value(value: str) -> str:
    return value.replace(",", "")

def _mermaid_escape(text: str) -> str:
    return text.replace('"', "'").replace("\n", " ")
