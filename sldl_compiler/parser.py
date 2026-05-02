from __future__ import annotations

from .ast_nodes import DocumentAst, Node, Value
from .diagnostics import Diagnostic
from .lexer import Lexer, Token


DECLARATION_KEYWORDS={
    "section": "Section",
    "claim": "Claim",
    "evidence": "Evidence",
    "reason": "Reason",
    "counterargument": "Counterargument",
    "conclusion": "Conclusion",
    "definition": "Definition",
    "reference": "Reference",
    "figure": "Figure",
    "table": "Table",
    "chart": "Chart",
    "flowchart": "Flowchart",
    "code": "CodeBlock",
    "object": "Object",
}


class Parser:
    def __init__(self, source: str):
        lexer=Lexer(source)
        self.tokens,self.diagnostics=lexer.tokenize()
        self.pos=0

    def parse(self) -> DocumentAst:
        doc_line,doc_col=self._current().line,self._current().column
        self._expect_ident_value("document")
        doc_id_tok=self._expect("STRING")
        self._expect_symbol(":")
        type_tok=self._expect("IDENT")
        doc=DocumentAst(
            id=doc_id_tok.value if(doc_id_tok is not None) else "",
            type_name=type_tok.value if(type_tok is not None) else "Document",
            line=doc_line,
            column=doc_col,
        )

        if(not self._match_symbol("{")):
            self._error_current("E_SYNTAX", "Expected document block")
            doc.diagnostics=self.diagnostics
            return doc

        while(not self._check_symbol("}") and not self._check("EOF")):
            stmt=self._parse_statement()
            if(stmt is not None):
                if(stmt.kind=="Meta"):
                    doc.meta=stmt
                else:
                    doc.children.append(stmt)

        self._expect_symbol("}")
        doc.diagnostics=self.diagnostics
        return doc

    def _parse_statement(self) -> Node | None:
        tok=self._current()

        if(tok.type!="IDENT"):
            self._error_current("E_SYNTAX", f"Expected statement, got {tok.type}:{tok.value}")
            self._advance()
            return None

        keyword=tok.value

        if(keyword=="meta"):
            self._advance()
            return self._parse_named_block("Meta", None, "Meta", tok.line, tok.column)

        if(keyword=="paragraph"):
            self._advance()
            return self._parse_named_block("Paragraph", None, "Paragraph", tok.line, tok.column)

        if(keyword in DECLARATION_KEYWORDS):
            self._advance()
            id_tok=self._expect("IDENT")
            self._expect_symbol(":")
            type_tok=self._expect("IDENT")
            return self._parse_named_block(
                DECLARATION_KEYWORDS[keyword],
                id_tok.value if(id_tok is not None) else None,
                type_tok.value if(type_tok is not None) else DECLARATION_KEYWORDS[keyword],
                tok.line,
                tok.column,
            )

        if(keyword=="class"):
            self._advance()
            id_tok=self._expect("IDENT")
            type_name="Object"
            if(self._match_symbol(":")):
                type_tok=self._expect("IDENT")
                if(type_tok is not None):
                    type_name=type_tok.value
            return self._parse_named_block(
                "Class",
                id_tok.value if(id_tok is not None) else None,
                type_name,
                tok.line,
                tok.column,
            )

        if(keyword=="func"):
            return self._parse_function_decl()

        return self._parse_field_as_node()

    def _parse_named_block(self, kind: str, node_id: str | None, type_name: str | None, line: int, column: int) -> Node:
        node=Node(kind=kind, id=node_id, type_name=type_name, line=line, column=column)
        if(not self._match_symbol("{")):
            self._error_current("E_SYNTAX", f"Expected block for {kind}")
            return node

        while(not self._check_symbol("}") and not self._check("EOF")):
            if(self._is_field_start()):
                key,value=self._parse_field()
                if(key is not None and value is not None):
                    node.fields[key]=value
            else:
                child=self._parse_statement()
                if(child is not None):
                    node.children.append(child)

        self._expect_symbol("}")
        return node

    def _parse_function_decl(self) -> Node:
        tok=self._current()
        self._expect_ident_value("func")
        id_tok=self._expect("IDENT")
        node=Node(
            kind="Function",
            id=id_tok.value if(id_tok is not None) else None,
            type_name="Function",
            line=tok.line,
            column=tok.column,
        )

        params=[]
        self._expect_symbol("(")
        if(not self._check_symbol(")")):
            while(True):
                param_name=self._expect("IDENT")
                self._expect_symbol(":")
                param_type=self._parse_type_expr({",", ")"})
                params.append({
                    "name": param_name.value if(param_name is not None) else "",
                    "type": param_type,
                })
                if(not self._match_symbol(",")):
                    break
        self._expect_symbol(")")
        self._expect("ARROW")
        return_type=self._parse_type_expr({"{"})
        node.fields["__params__"]=Value("Raw", params, tok.line, tok.column)
        node.fields["__return_type__"]=Value("String", return_type, tok.line, tok.column)

        if(not self._match_symbol("{")):
            self._error_current("E_SYNTAX", "Expected function body")
            return node

        while(not self._check_symbol("}") and not self._check("EOF")):
            if(self._is_field_start()):
                key,value=self._parse_field()
                if(key is not None and value is not None):
                    node.fields[key]=value
            else:
                child=self._parse_statement()
                if(child is not None):
                    node.children.append(child)
        self._expect_symbol("}")
        return node

    def _parse_type_expr(self, stop_symbols: set[str]) -> str:
        parts=[]
        depth=0
        while(not self._check("EOF")):
            tok=self._current()
            if(tok.type=="SYMBOL"):
                if(tok.value=="<"):
                    depth+=1
                    parts.append(tok.value)
                    self._advance()
                    continue
                if(tok.value==">"):
                    depth=max(0, depth-1)
                    parts.append(tok.value)
                    self._advance()
                    continue
                if(depth==0 and tok.value in stop_symbols):
                    break
                if(tok.value in {"|", "."}):
                    parts.append(tok.value)
                    self._advance()
                    continue
                if(tok.value=="," and depth>0):
                    parts.append(tok.value)
                    self._advance()
                    continue
                break
            if(tok.type=="IDENT"):
                parts.append(str(tok.value))
                self._advance()
                continue
            self._error_current("E_SYNTAX", "Expected type expression")
            break
        return "".join(parts).strip()

    def _parse_field_as_node(self) -> Node | None:
        key,value=self._parse_field()
        if(key is None or value is None):
            return None
        return Node(kind="Field", id=None, type_name=None, fields={key: value}, line=value.line, column=value.column)

    def _parse_field(self) -> tuple[str | None, Value | None]:
        key_tok=self._expect("IDENT")
        if(key_tok is None):
            return None,None

        key=key_tok.value
        if(self._match_symbol("?")):
            key=key+"?"

        self._expect_symbol(":")
        value=self._parse_value()
        if(not self._match_symbol(";")):
            self._error_current("E_SYNTAX", "Expected symbol ';'")
            self._synchronize_field_end()
        return key,value

    def _parse_value(self) -> Value:
        tok=self._current()

        if(tok.type=="STRING"):
            self._advance()
            if(self._match_symbol("@")):
                lang_tok=self._expect("IDENT")
                lang=lang_tok.value if(lang_tok is not None) else ""
                return Value("TextLang", {"text": tok.value, "lang": lang}, tok.line, tok.column)
            return Value("String", tok.value, tok.line, tok.column)

        if(tok.type=="NUMBER"):
            self._advance()
            return Value("Number", tok.value, tok.line, tok.column)

        if(tok.type=="IDENT"):
            self._advance()
            if(tok.value=="true"):
                return Value("Bool", True, tok.line, tok.column)
            if(tok.value=="false"):
                return Value("Bool", False, tok.line, tok.column)
            if(tok.value=="null"):
                return Value("Null", None, tok.line, tok.column)

            if(self._match_symbol("(")):
                args=[]
                if(not self._check_symbol(")")):
                    while(True):
                        args.append(self._parse_value())
                        if(not self._match_symbol(",")):
                            break
                self._expect_symbol(")")
                return Value("FunctionCall", {"name": tok.value, "args": args}, tok.line, tok.column)

            return Value("Identifier", tok.value, tok.line, tok.column)

        if(self._match_symbol("[")):
            items=[]
            while(not self._check_symbol("]") and not self._check("EOF")):
                items.append(self._parse_value())
                if(not self._match_symbol(",")):
                    break
            self._expect_symbol("]")
            return Value("List", items, tok.line, tok.column)

        if(self._match_symbol("{")):
            fields={}
            while(not self._check_symbol("}") and not self._check("EOF")):
                key,value=self._parse_field()
                if(key is not None and value is not None):
                    fields[key]=value
            self._expect_symbol("}")
            return Value("Object", fields, tok.line, tok.column)

        self._error_current("E_SYNTAX", f"Expected value, got {tok.type}:{tok.value}")
        self._advance()
        return Value("Null", None, tok.line, tok.column)


    def _synchronize_field_end(self) -> None:
        while(not self._check("EOF") and not self._check_symbol(";") and not self._check_symbol("}") and not self._check_symbol("]")):
            self._advance()
        if(self._check_symbol(";")):
            self._advance()

    def _is_field_start(self) -> bool:
        return self._check("IDENT") and (
            self._peek_token(1).type=="SYMBOL" and self._peek_token(1).value in {":", "?"}
        )

    def _current(self) -> Token:
        return self.tokens[self.pos]

    def _peek_token(self, offset: int) -> Token:
        idx=self.pos+offset
        if(idx>=len(self.tokens)):
            return self.tokens[-1]
        return self.tokens[idx]

    def _advance(self) -> Token:
        tok=self._current()
        if(not self._check("EOF")):
            self.pos+=1
        return tok

    def _check(self, token_type: str) -> bool:
        return self._current().type==token_type

    def _check_symbol(self, value: str) -> bool:
        return self._current().type=="SYMBOL" and self._current().value==value

    def _match_symbol(self, value: str) -> bool:
        if(self._check_symbol(value)):
            self._advance()
            return True
        return False

    def _expect(self, token_type: str) -> Token | None:
        if(self._check(token_type)):
            return self._advance()
        self._error_current("E_SYNTAX", f"Expected {token_type}, got {self._current().type}:{self._current().value}")
        return None

    def _expect_symbol(self, value: str) -> Token | None:
        if(self._check_symbol(value)):
            return self._advance()
        self._error_current("E_SYNTAX", f"Expected symbol {value!r}")
        return None

    def _expect_ident_value(self, value: str) -> Token | None:
        if(self._current().type=="IDENT" and self._current().value==value):
            return self._advance()
        self._error_current("E_SYNTAX", f"Expected keyword {value!r}")
        return None

    def _error_current(self, code: str, message: str) -> None:
        tok=self._current()
        self.diagnostics.append(Diagnostic("error", code, message, tok.line, tok.column))


def parse_source(source: str) -> DocumentAst:
    parser=Parser(source)
    return parser.parse()
