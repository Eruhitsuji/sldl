# SLDL language reference

SLDL documents are typed source files. They combine ordinary document structure with explicit logical relations such as claims, evidence, and conclusions.

## Document

```sldl
document "research_report_en" : ResearchReport {
    meta {
        title: "Title"@en;
        author: "Author"@en;
        date: Date("2026-05-02");
        lang: "en-US";
        version: "1.0.0";
    }

    section intro : Section {
        title: "Introduction"@en;
        paragraph { text: "Body text."@en; }
    }
}
```

A document has an identifier and a document type. The type must be accepted by the schema supplied through `--schema` or the project JSON.

## Metadata

The `meta` block commonly contains:

- `title`
- `author`
- `date`
- `lang`
- `version`
- `toc`
- LaTeX hints such as `latex_profile` and `latex_top_level`

## Literals

- Language-tagged text: `"Text"@en`, `"本文"@ja`
- Date: `Date("YYYY-MM-DD")`
- Boolean: `true`, `false`
- Number: integer or float
- List: `[a, b, c]`
- Object-like maps: `{ key: "value"; }`

## Sections and paragraphs

```sldl
section method : Section {
    title: "Method"@en;
    paragraph { text: "The method is described here."@en; }
}
```

## Logical nodes

Claims can be grounded in evidence and used by conclusions.

```sldl
claim c_goal : Claim {
    text: "The workflow is repeatable."@en;
    evidence: [e_manifest];
    strength: asserted;
}

evidence e_manifest : Evidence {
    text: "The build manifest records generated files."@en;
    source: ref_sldl;
}

conclusion con_main : Conclusion {
    text: "The workflow is suitable for release checks."@en;
    based_on: [c_goal, e_manifest];
}
```

## Tables and flowcharts

Tables and flowcharts are source-level objects and can be exported to Markdown, HTML, and LaTeX-oriented outputs.

```sldl
table t_checks : Table {
    caption: "Checks"@en;
    columns: [{ name: "item"; type: Text; }, { name: "status"; type: Text; }];
    rows: [["syntax", "checked"], ["config", "checked"]];
}
```

```sldl
flowchart fig_workflow : Flowchart {
    caption: "Workflow"@en;
    direction: "LR";
    nodes: { source: "SLDL"; build: "Build"; };
    edges: [["source", "build", "generate"]];
}
```

## Cross references

Inline text can refer to an object by using `{{ref:object_id}}`. Structured fields such as `xrefs`, `source`, and `supports` can also connect nodes.
