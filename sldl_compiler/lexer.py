from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .diagnostics import Diagnostic


@dataclass
class Token:
    type: str
    value: Any
    line: int
    column: int

    def __repr__(self) -> str:
        return f"Token({self.type!r}, {self.value!r}, {self.line}:{self.column})"


class Lexer:
    def __init__(self, source: str):
        self.source=source
        self.pos=0
        self.line=1
        self.column=1
        self.tokens: list[Token]=[]
        self.diagnostics: list[Diagnostic]=[]

    def tokenize(self) -> tuple[list[Token], list[Diagnostic]]:
        while(not self._is_at_end()):
            ch=self._peek()

            if(ch in " \t\r"):
                self._advance()
                continue

            if(ch=="\n"):
                self._advance()
                continue

            if(ch=="/" and self._peek_next()=="/"):
                self._skip_line_comment()
                continue

            if(ch=="/" and self._peek_next()=="*"):
                self._skip_block_comment()
                continue

            if(ch=='"'):
                self._read_string()
                continue

            if(ch=="-" and self._peek_next()==">"):
                line,column=self.line,self.column
                self._advance()
                self._advance()
                self.tokens.append(Token("ARROW", "->", line, column))
                continue

            if(ch=="-" and self._peek_next().isdigit()):
                self._read_number()
                continue

            if(ch.isdigit()):
                self._read_number()
                continue

            if(self._is_identifier_start(ch)):
                self._read_identifier()
                continue

            if(ch in "{}[]():;,.@?<>|"):
                line,column=self.line,self.column
                self._advance()
                self.tokens.append(Token("SYMBOL", ch, line, column))
                continue

            self.diagnostics.append(Diagnostic("error", "E_SYNTAX", f"Unexpected character: {ch!r}", self.line, self.column))
            self._advance()

        self.tokens.append(Token("EOF", "", self.line, self.column))
        return self.tokens, self.diagnostics

    def _is_at_end(self) -> bool:
        return self.pos>=len(self.source)

    def _peek(self) -> str:
        if(self._is_at_end()):
            return "\0"
        return self.source[self.pos]

    def _peek_next(self) -> str:
        if(self.pos+1>=len(self.source)):
            return "\0"
        return self.source[self.pos+1]

    def _peek_at(self, offset: int) -> str:
        idx=self.pos+offset
        if(idx>=len(self.source)):
            return "\0"
        return self.source[idx]

    def _advance(self) -> str:
        ch=self.source[self.pos]
        self.pos+=1
        if(ch=="\n"):
            self.line+=1
            self.column=1
        else:
            self.column+=1
        return ch

    def _skip_line_comment(self) -> None:
        while(not self._is_at_end() and self._peek()!="\n"):
            self._advance()

    def _skip_block_comment(self) -> None:
        start_line,start_col=self.line,self.column
        self._advance()
        self._advance()
        while(not self._is_at_end()):
            if(self._peek()=="*" and self._peek_next()=="/"):
                self._advance()
                self._advance()
                return
            self._advance()
        self.diagnostics.append(Diagnostic("error", "E_SYNTAX", "Unterminated block comment", start_line, start_col))

    def _read_string(self) -> None:
        line,column=self.line,self.column

        if(self._peek()=='"' and self._peek_next()=='"' and self._peek_at(2)=='"'):
            self._advance()
            self._advance()
            self._advance()
            chars=[]
            while(not self._is_at_end()):
                if(self._peek()=='"' and self._peek_next()=='"' and self._peek_at(2)=='"'):
                    self._advance()
                    self._advance()
                    self._advance()
                    self.tokens.append(Token("STRING", "".join(chars), line, column))
                    return
                chars.append(self._advance())
            self.diagnostics.append(Diagnostic("error", "E_SYNTAX", "Unterminated triple-quoted string", line, column))
            self.tokens.append(Token("STRING", "".join(chars), line, column))
            return

        self._advance()
        chars=[]
        while(not self._is_at_end()):
            ch=self._advance()
            if(ch=='"'):
                self.tokens.append(Token("STRING", "".join(chars), line, column))
                return
            if(ch=="\\"):
                if(self._is_at_end()):
                    break
                esc=self._advance()
                mapping={
                    "n": "\n",
                    "t": "\t",
                    "r": "\r",
                    '"': '"',
                    "\\": "\\",
                }
                chars.append(mapping.get(esc, esc))
            else:
                chars.append(ch)

        self.diagnostics.append(Diagnostic("error", "E_SYNTAX", "Unterminated string", line, column))
        self.tokens.append(Token("STRING", "".join(chars), line, column))

    def _read_number(self) -> None:
        line,column=self.line,self.column
        chars=[]

        if(self._peek()=="-"):
            chars.append(self._advance())

        while(self._peek().isdigit()):
            chars.append(self._advance())

        if(self._peek()=="." and self._peek_next().isdigit()):
            chars.append(self._advance())
            while(self._peek().isdigit()):
                chars.append(self._advance())

        raw="".join(chars)
        value=float(raw) if("." in raw) else int(raw)
        self.tokens.append(Token("NUMBER", value, line, column))

    def _read_identifier(self) -> None:
        line,column=self.line,self.column
        chars=[]
        while(self._is_identifier_part(self._peek())):
            chars.append(self._advance())
        self.tokens.append(Token("IDENT", "".join(chars), line, column))

    def _is_identifier_start(self, ch: str) -> bool:
        return ch=="_" or ch.isalpha()

    def _is_identifier_part(self, ch: str) -> bool:
        return ch=="_" or ch=="-" or ch=="." or ch.isalpha() or ch.isdigit()
