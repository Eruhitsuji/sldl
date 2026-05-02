from __future__ import annotations

from datetime import date, datetime, time

from .ast_nodes import DocumentAst, Node, Value
from .diagnostics import Diagnostic


def check(doc: DocumentAst) -> None:
    _check_meta(doc)
    for node in doc.children:
        _check_node(doc, node)


def _check_meta(doc: DocumentAst) -> None:
    if(doc.meta is None):
        doc.diagnostics.append(Diagnostic("error", "E_MISSING_REQUIRED_FIELD", "meta block is required", doc.line, doc.column))
        return
    if("title" not in doc.meta.fields):
        doc.diagnostics.append(Diagnostic("error", "E_MISSING_REQUIRED_FIELD", "meta.title is required", doc.meta.line, doc.meta.column))
    _check_values_for_dates(doc, doc.meta)


def _check_node(doc: DocumentAst, node: Node) -> None:
    required={
        "Paragraph": ["text"],
        "Claim": ["text"],
        "Evidence": ["text"],
        "Reason": ["text", "supports"],
        "Counterargument": ["text", "against"],
        "Conclusion": ["text", "based_on"],
        "Definition": ["term", "text"],
        "Reference": ["title"],
        "Figure": ["src"],
        "CodeBlock": ["lang", "source"],
        "Chart": ["data", "x", "y"],
        "Flowchart": ["nodes", "edges"],
        "Table": ["columns", "rows"],
    }

    for field_name in required.get(node.kind, []):
        if(field_name not in node.fields):
            doc.diagnostics.append(Diagnostic("error", "E_MISSING_REQUIRED_FIELD", f"{node.kind}.{field_name} is required", node.line, node.column))

    if(node.kind=="Claim" and "evidence" not in node.fields):
        doc.diagnostics.append(Diagnostic("warning", "W_CLAIM_WITHOUT_EVIDENCE", f"Claim has no evidence: {node.id or '-'}", node.line, node.column))

    if(node.kind=="Figure" and "caption" not in node.fields):
        doc.diagnostics.append(Diagnostic("warning", "W_MISSING_CAPTION", f"Figure has no caption: {node.id or '-'}", node.line, node.column))

    if(node.kind=="Table"):
        _check_table(doc, node)

    if(node.kind=="Chart"):
        _check_chart(doc, node)

    if(node.kind=="Flowchart"):
        _check_flowchart(doc, node)

    _check_values_for_dates(doc, node)

    for child in node.children:
        _check_node(doc, child)


def _check_values_for_dates(doc: DocumentAst, node: Node) -> None:
    for value in node.fields.values():
        _check_date_value(doc, value)


def _check_date_value(doc: DocumentAst, value: Value) -> None:
    if(value.kind=="FunctionCall"):
        name=value.value["name"]
        args=value.value["args"]
        if(name in {"Date", "Time", "DateTime"}):
            if(len(args)!=1 or args[0].kind not in {"String", "TextLang"}):
                doc.diagnostics.append(Diagnostic("error", "E_INVALID_DATE", f"{name} requires one string argument", value.line, value.column))
            else:
                raw=args[0].value["text"] if(args[0].kind=="TextLang") else args[0].value
                try:
                    if(name=="Date"):
                        date.fromisoformat(raw)
                    elif(name=="Time"):
                        time.fromisoformat(raw)
                    elif(name=="DateTime"):
                        datetime.fromisoformat(raw.replace("Z", "+00:00"))
                except ValueError:
                    doc.diagnostics.append(Diagnostic("error", "E_INVALID_DATE", f"Invalid {name}: {raw}", value.line, value.column))
        for arg in args:
            _check_date_value(doc, arg)
    elif(value.kind=="List"):
        for item in value.value:
            _check_date_value(doc, item)
    elif(value.kind=="Object"):
        for item in value.value.values():
            _check_date_value(doc, item)


def _check_table(doc: DocumentAst, node: Node) -> None:
    columns=node.fields.get("columns")
    rows=node.fields.get("rows")
    if(columns is None or rows is None):
        return
    if(columns.kind!="List"):
        doc.diagnostics.append(Diagnostic("error", "E_INVALID_TABLE_ROW", "table.columns must be a list", columns.line, columns.column))
        return
    if(rows.kind!="List"):
        doc.diagnostics.append(Diagnostic("error", "E_INVALID_TABLE_ROW", "table.rows must be a list", rows.line, rows.column))
        return

    col_names=[]
    for col in columns.value:
        if(col.kind!="Object" or "name" not in col.value):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_TABLE_ROW", "Each column must be an object with name", col.line, col.column))
            continue
        col_name=_value_to_plain(col.value["name"])
        col_names.append(col_name)

    seen=set()
    for name in col_names:
        if(name in seen):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_TABLE_ROW", f"Duplicate column name: {name}", node.line, node.column))
        seen.add(name)

    for row in rows.value:
        if(row.kind!="List"):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_TABLE_ROW", "Each row must be a list", row.line, row.column))
            continue
        if(len(row.value)!=len(col_names)):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_TABLE_ROW", f"Row length {len(row.value)} does not match column length {len(col_names)}", row.line, row.column))


def _check_chart(doc: DocumentAst, node: Node) -> None:
    data=node.fields.get("data")
    x=node.fields.get("x")
    y=node.fields.get("y")
    if(data is None):
        return
    if(data.kind=="Identifier"):
        if(x is None or y is None):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_CHART_REF", "chart.data table reference requires x and y fields", data.line, data.column))
            return
        target=doc.symbols.get(data.value)
        if(target is None):
            return
        if(target.kind!="Table"):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_CHART_REF", f"chart.data must refer to Table: {data.value}", data.line, data.column))
            return
        col_names=_table_column_names(target)
        x_name=_value_to_plain(x)
        y_name=_value_to_plain(y)
        if(x_name not in col_names):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_CHART_REF", f"chart.x column not found: {x_name}", x.line, x.column))
        if(y_name not in col_names):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_CHART_REF", f"chart.y column not found: {y_name}", y.line, y.column))
        return
    if(data.kind=="List"):
        for item in data.value:
            if(item.kind!="Object"):
                doc.diagnostics.append(Diagnostic("error", "E_INVALID_CHART_REF", "Inline chart.data rows must be objects", item.line, item.column))
                continue
            x_found=("x" in item.value) or (x is not None and _value_to_plain(x) in item.value)
            y_found=("y" in item.value) or (y is not None and _value_to_plain(y) in item.value)
            if(not x_found or not y_found):
                doc.diagnostics.append(Diagnostic("error", "E_INVALID_CHART_REF", "Inline chart.data row must contain x/y values", item.line, item.column))
        return
    doc.diagnostics.append(Diagnostic("error", "E_INVALID_CHART_REF", "chart.data must be a table identifier or inline row list", data.line, data.column))


def _check_flowchart(doc: DocumentAst, node: Node) -> None:
    nodes=node.fields.get("nodes")
    edges=node.fields.get("edges")
    if(nodes is None or edges is None):
        return
    node_names=_flowchart_node_names(nodes)
    if(not node_names):
        doc.diagnostics.append(Diagnostic("error", "E_INVALID_FLOW_EDGE", "flowchart.nodes must define at least one node", nodes.line, nodes.column))
        return
    if(edges.kind!="List"):
        doc.diagnostics.append(Diagnostic("error", "E_INVALID_FLOW_EDGE", "flowchart.edges must be a list", edges.line, edges.column))
        return

    for edge in edges.value:
        left=""
        right=""
        if(edge.kind=="List" and len(edge.value) in {2,3}):
            left=_value_to_plain(edge.value[0])
            right=_value_to_plain(edge.value[1])
        elif(edge.kind=="Object"):
            left=_value_to_plain(edge.value.get("from"))
            right=_value_to_plain(edge.value.get("to"))
        else:
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_FLOW_EDGE", "Each flowchart edge must be [from, to] or {from,to,label?}", edge.line, edge.column))
            continue
        if(left not in node_names):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_FLOW_EDGE", f"Flowchart node not found: {left}", edge.line, edge.column))
        if(right not in node_names):
            doc.diagnostics.append(Diagnostic("error", "E_INVALID_FLOW_EDGE", f"Flowchart node not found: {right}", edge.line, edge.column))


def _flowchart_node_names(value: Value) -> set[str]:
    names=set()
    if(value.kind=="Object"):
        for name in value.value.keys():
            names.add(str(name))
    elif(value.kind=="List"):
        for item in value.value:
            if(item.kind=="Object"):
                nid=_value_to_plain(item.value.get("id"))
                if(nid):
                    names.add(nid)
            else:
                nid=_value_to_plain(item)
                if(nid):
                    names.add(nid)
    return names

def _table_column_names(table: Node) -> set[str]:
    columns=table.fields.get("columns")
    if(columns is None or columns.kind!="List"):
        return set()
    result=set()
    for col in columns.value:
        if(col.kind=="Object" and "name" in col.value):
            result.add(_value_to_plain(col.value["name"]))
    return result


def _value_to_plain(value: Value) -> str:
    if(value.kind=="TextLang"):
        return str(value.value["text"])
    if(value.kind=="String"):
        return str(value.value)
    if(value.kind=="Identifier"):
        return str(value.value)
    if(value.kind=="Number"):
        return str(value.value)
    if(value.kind=="Bool"):
        return str(value.value).lower()
    if(value.kind=="Null"):
        return "null"
    return str(value.value)
