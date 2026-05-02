from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


DiagnosticLevel=Literal["error","warning"]


@dataclass
class Diagnostic:
    level: DiagnosticLevel
    code: str
    message: str
    line: int = 0
    column: int = 0

    def to_dict(self) -> dict:
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "line": self.line,
            "column": self.column,
        }

    def format(self, source: str | None = None, path: str | None = None) -> str:
        prefix="ERROR" if(self.level=="error") else "WARNING"
        location=f"{self.line}:{self.column}" if(self.line and self.column) else "-"
        if(path):
            location=f"{path}:{location}"
        head=f"{prefix} {self.code} at {location} {self.message}"
        if(source and self.line and self.column):
            lines=source.splitlines()
            if(1<=self.line<=len(lines)):
                src_line=lines[self.line-1]
                caret=" "*(max(self.column-1,0))+"^"
                return f"{head}\n  {src_line}\n  {caret}"
        return head
