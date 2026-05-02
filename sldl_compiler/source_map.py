from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SourceContext:
    line: int
    column: int
    text: str
    caret: str


def get_source_context(source: str, line: int, column: int) -> SourceContext | None:
    if(line<=0 or column<=0):
        return None
    lines=source.splitlines()
    if(line>len(lines)):
        return None
    text=lines[line-1]
    caret=" "*(max(column-1,0))+"^"
    return SourceContext(line=line,column=column,text=text,caret=caret)
