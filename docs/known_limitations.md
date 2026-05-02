# Known limitations

- PDF generation depends on an external LaTeX environment. The canonical release check uses dry-run PDF generation so it can run without pLaTeX/dvipdfmx installed.
- Mermaid diagrams are exported as Mermaid code for Markdown/HTML. LaTeX-oriented rendering can use code, placeholder text, or external images.
- The schema system validates structure and selected logic rules, but it is not a complete formal proof system.
- Golden snapshots are byte-level checks. Any intentional exporter change requires regenerating the snapshot.
- The Japanese documentation is a companion guide. The English documentation is the primary reference for v1.0 public release.
- Old development examples are intentionally outside the active compatibility scope.
