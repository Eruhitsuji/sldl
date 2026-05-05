from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Iterable

VERSION="1.0.14"


def _project_root(root: str | Path | None = None) -> Path:
    return Path(root).resolve() if(root is not None) else Path.cwd().resolve()


def _sha256_file(path: Path) -> str | None:
    if(not path.exists() or not path.is_file()):
        return None
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _file_record(root: Path, path: str, title_en: str, title_ja: str, kind: str, config_type: str | None = None) -> dict[str, Any]:
    file_path=root/path
    return {
        "path": path,
        "title": title_en,
        "title_ja": title_ja,
        "kind": kind,
        "config_type": config_type,
        "exists": file_path.exists(),
        "bytes": file_path.stat().st_size if(file_path.exists() and file_path.is_file()) else None,
        "sha256": _sha256_file(file_path),
    }


def build_reference_index(root: str | Path | None = None, language: str = "en") -> dict[str, Any]:
    base=_project_root(root)
    references=[
        _file_record(base, "docs/generated_template_reference.md", "Template reference", "テンプレートリファレンス", "markdown"),
        _file_record(base, "docs/ja/generated_template_reference.md", "Template reference (Japanese)", "テンプレートリファレンス（日本語）", "markdown"),
        _file_record(base, "docs/generated_template_reference.json", "Template reference JSON", "テンプレートリファレンスJSON", "json", "sldl.template_reference"),
        _file_record(base, "docs/diagnostics_reference.md", "Diagnostics reference", "診断コードリファレンス", "markdown"),
        _file_record(base, "docs/ja/diagnostics_reference.md", "Diagnostics reference (Japanese)", "診断コードリファレンス（日本語）", "markdown"),
        _file_record(base, "docs/diagnostics_reference.json", "Diagnostics reference JSON", "診断コードリファレンスJSON", "json", "sldl.diagnostics_reference"),
        _file_record(base, "docs/cli_help_reference.md", "CLI help reference", "CLI helpリファレンス", "markdown"),
        _file_record(base, "docs/ja/cli_help_reference.md", "CLI help reference (Japanese)", "CLI helpリファレンス（日本語）", "markdown"),
        _file_record(base, "docs/cli_help_reference.json", "CLI help reference JSON", "CLI helpリファレンスJSON", "json", "sldl.cli_help_reference"),
        _file_record(base, "docs/release_report.md", "Release report", "リリースレポート", "markdown"),
        _file_record(base, "docs/ja/release_report.md", "Release report (Japanese)", "リリースレポート（日本語）", "markdown"),
        _file_record(base, "docs/release_report.json", "Release report JSON", "リリースレポートJSON", "json", "sldl.release_report"),
        _file_record(base, "docs/release_summary.json", "Release summary JSON", "リリースサマリーJSON", "json", "sldl.release_summary"),
    ]
    return {
        "config_type": "sldl.reference_index",
        "description": "Generated SLDL reference index" if(language=="en") else "生成されたSLDLリファレンス索引",
        "version": VERSION,
        "language": language,
        "references": references,
    }


def render_reference_index_json(index: dict[str, Any]) -> str:
    return json.dumps(index, ensure_ascii=False, indent=2)+"\n"


def render_reference_index_markdown(index: dict[str, Any], language: str = "en") -> str:
    if(language=="ja"):
        lines=[
            "# SLDL Reference Index（日本語）",
            "",
            "生成済みリファレンス文書への入口です。v1.0.14では、template reference、diagnostics reference、CLI help reference、release report、CI向けrelease summaryをまとめて確認できます。",
            "",
            f"- version: `{index.get('version', '')}`",
            f"- references: `{len(index.get('references', []))}`",
            "",
            "| Title | Path | Kind | Config type | SHA-256 |",
            "|---|---|---|---|---|",
        ]
    else:
        lines=[
            "# SLDL Reference Index",
            "",
            "This page is the entry point for generated reference documents. In v1.0.14, the template reference, diagnostics reference, CLI help reference, release report, and CI release summary can be checked together.",
            "",
            f"- version: `{index.get('version', '')}`",
            f"- references: `{len(index.get('references', []))}`",
            "",
            "| Title | Path | Kind | Config type | SHA-256 |",
            "|---|---|---|---|---|",
        ]
    for ref in index.get("references", []):
        title=ref.get("title_ja") if(language=="ja") else ref.get("title")
        sha=ref.get("sha256") or "missing"
        sha_short=sha[:12] if(len(sha)>=12) else sha
        lines.append(f"| {title} | `{ref.get('path', '')}` | `{ref.get('kind', '')}` | `{ref.get('config_type') or ''}` | `{sha_short}` |")
    lines.extend([
        "",
        "## Commands" if(language!="ja") else "## コマンド",
        "",
        "```bash",
        "python3 -S -m sldl_compiler.cli reference index --format markdown --check docs/reference_index.md",
        "python3 -S -m sldl_compiler.cli reference cli-help --format markdown --check docs/cli_help_reference.md",
        "```",
    ])
    return "\n".join(lines)+"\n"


def _iter_command_parsers(parser: argparse.ArgumentParser, prefix: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], argparse.ArgumentParser]]:
    yield prefix, parser
    for action in parser._actions:
        if(isinstance(action, argparse._SubParsersAction)):
            for name,subparser in sorted(action.choices.items()):
                yield from _iter_command_parsers(subparser, prefix+(name,))


def _usage_for_command(prefix: tuple[str, ...], parser: argparse.ArgumentParser) -> str:
    command=" ".join(prefix) if(prefix) else "sldlc"
    subcommands=[]
    has_options=False
    positionals=[]
    for action in parser._actions:
        if(isinstance(action, argparse._SubParsersAction)):
            subcommands=sorted(action.choices.keys())
        elif(action.option_strings):
            if(action.dest!="help"):
                has_options=True
        elif(action.dest not in {"help"}):
            positionals.append(action.dest)
    parts=[command]
    if(subcommands):
        parts.append("<command>")
    for dest in positionals:
        parts.append(f"<{dest}>")
    if(has_options):
        parts.append("[options]")
    return " ".join(parts)


def _nargs_suffix(action: argparse.Action) -> str:
    if(action.__class__.__name__ in {"_StoreTrueAction", "_StoreFalseAction", "_HelpAction"}):
        return ""
    if(not action.option_strings):
        return ""
    if(isinstance(action.nargs, int)):
        return " " + " ".join([str(action.metavar or action.dest.upper()) for _ in range(action.nargs)])
    if(action.nargs in {None, "?", "*", "+"}):
        return " " + str(action.metavar or action.dest.upper())
    return ""


def _stable_option_rows(parser: argparse.ArgumentParser) -> list[dict[str, str]]:
    rows=[]
    for action in parser._actions:
        if(isinstance(action, argparse._SubParsersAction)):
            continue
        if(not action.option_strings):
            continue
        names=", ".join(action.option_strings)+_nargs_suffix(action)
        help_text=action.help or ""
        if(action.choices is not None):
            choices=", ".join(str(choice) for choice in action.choices)
            help_text=(help_text+" " if(help_text) else "")+f"Choices: {choices}."
        rows.append({"names": names, "help": help_text})
    return rows


def _stable_positional_rows(parser: argparse.ArgumentParser) -> list[dict[str, str]]:
    rows=[]
    for action in parser._actions:
        if(isinstance(action, argparse._SubParsersAction)):
            continue
        if(action.option_strings):
            continue
        if(action.dest=="help"):
            continue
        rows.append({"name": action.dest, "help": action.help or ""})
    return rows


def _stable_subcommand_rows(parser: argparse.ArgumentParser) -> list[dict[str, str]]:
    rows=[]
    for action in parser._actions:
        if(isinstance(action, argparse._SubParsersAction)):
            for name,subparser in sorted(action.choices.items()):
                rows.append({"name": name, "help": getattr(subparser, "description", None) or ""})
    return rows


def _stable_help_text(command: str, usage: str, description: str, subcommands: list[dict[str, str]], positionals: list[dict[str, str]], options: list[dict[str, str]]) -> str:
    lines=[f"Command: {command}", f"Usage: {usage}"]
    if(description):
        lines.extend(["", "Description:", description])
    if(subcommands):
        lines.extend(["", "Subcommands:"])
        for row in subcommands:
            suffix=f" - {row['help']}" if(row.get("help")) else ""
            lines.append(f"  {row['name']}{suffix}")
    if(positionals):
        lines.extend(["", "Arguments:"])
        for row in positionals:
            suffix=f" - {row['help']}" if(row.get("help")) else ""
            lines.append(f"  {row['name']}{suffix}")
    if(options):
        lines.extend(["", "Options:"])
        for row in options:
            suffix=f" - {row['help']}" if(row.get("help")) else ""
            lines.append(f"  {row['names']}{suffix}")
    return "\n".join(lines)+"\n"


def build_cli_help_reference(parser: argparse.ArgumentParser, language: str = "en") -> dict[str, Any]:
    commands=[]
    for prefix,subparser in _iter_command_parsers(parser):
        command=" ".join(prefix) if(prefix) else "sldlc"
        usage=_usage_for_command(prefix, subparser)
        description=subparser.description or ""
        subcommands=_stable_subcommand_rows(subparser)
        positionals=_stable_positional_rows(subparser)
        options=_stable_option_rows(subparser)
        help_text=_stable_help_text(command, usage, description, subcommands, positionals, options)
        commands.append({
            "command": command,
            "path": list(prefix),
            "usage": usage,
            "description": description,
            "subcommands": subcommands,
            "arguments": positionals,
            "options": options,
            "help": help_text,
        })
    return {
        "config_type": "sldl.cli_help_reference",
        "description": "Generated SLDL CLI help reference" if(language=="en") else "生成されたSLDL CLI helpリファレンス",
        "version": VERSION,
        "language": language,
        "command_count": len(commands),
        "commands": commands,
    }

def render_cli_help_reference_json(reference: dict[str, Any]) -> str:
    return json.dumps(reference, ensure_ascii=False, indent=2)+"\n"


def render_cli_help_reference_markdown(reference: dict[str, Any], language: str = "en") -> str:
    if(language=="ja"):
        lines=[
            "# SLDL CLI Help Reference（日本語）",
            "",
            "CLIの `--help` 出力を静的ドキュメントとしてまとめたリファレンスです。ヘルプ本文はCLI実装から生成されます。",
            "",
            f"- version: `{reference.get('version', '')}`",
            f"- commands: `{reference.get('command_count', 0)}`",
            "",
        ]
    else:
        lines=[
            "# SLDL CLI Help Reference",
            "",
            "This reference captures CLI `--help` output as static documentation generated from the implemented argument parser.",
            "",
            f"- version: `{reference.get('version', '')}`",
            f"- commands: `{reference.get('command_count', 0)}`",
            "",
        ]
    for item in reference.get("commands", []):
        title=item.get("command") or "sldlc"
        lines.extend([
            f"## `{title}`",
            "",
            "```text",
            str(item.get("help", "")).rstrip(),
            "```",
            "",
        ])
    return "\n".join(lines)
