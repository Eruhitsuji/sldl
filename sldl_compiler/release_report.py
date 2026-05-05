from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

from .config_tools import load_config_json

VERSION="1.0.15"
IGNORED_REPORT_COMMAND_PREFIXES=("quality-report-",)
IGNORED_REPORT_COMMAND_NAMES={"config-explain-release-report"}


def _load_manifest(path: str | Path) -> dict[str, Any]:
    data,diagnostics=load_config_json(path)
    if(data is None):
        messages="; ".join(d.message for d in diagnostics)
        raise ValueError(messages or f"Cannot load release manifest: {path}")
    if(data.get("config_type")!="sldl.release_manifest"):
        raise ValueError(f"Expected config_type sldl.release_manifest: {path}")
    return data


def _is_report_check(item: dict[str, Any]) -> bool:
    if(item.get("category")!="command"):
        return False
    name=str(item.get("name", ""))
    if(name in IGNORED_REPORT_COMMAND_NAMES):
        return True
    return any(name.startswith(prefix) for prefix in IGNORED_REPORT_COMMAND_PREFIXES)


def _normalized_checks(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    checks=manifest.get("checks", [])
    if(not isinstance(checks, list)):
        return []
    return [item for item in checks if(isinstance(item, dict) and not _is_report_check(item))]


def _diagnostic_codes(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counter: Counter[str]=Counter()
    levels: dict[str, str]={}
    for item in checks:
        for diag in item.get("diagnostics", []):
            if(not isinstance(diag, dict)):
                continue
            code=str(diag.get("code") or "UNKNOWN")
            level=str(diag.get("level") or "error")
            counter[code]+=1
            levels.setdefault(code, level)
    return [{"code": code, "level": levels.get(code, "error"), "count": counter[code]} for code in sorted(counter)]


def _summary_rows(checks: list[dict[str, Any]], key: str) -> list[dict[str, Any]]:
    values=sorted({str(item.get(key, "unknown")) for item in checks})
    rows=[]
    for value in values:
        subset=[item for item in checks if(str(item.get(key, "unknown"))==value)]
        total=len(subset)
        failed=sum(1 for item in subset if(not item.get("ok")))
        warnings=sum(1 for item in subset for diag in item.get("diagnostics", []) if(isinstance(diag, dict) and diag.get("level")=="warning"))
        rows.append({key: value, "total": total, "passed": total-failed, "failed": failed, "warnings": warnings})
    return rows


def _category_summary(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _summary_rows(checks, "category")


def _failed_checks(checks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows=[]
    for item in checks:
        if(item.get("ok")):
            continue
        diagnostics=[]
        for diag in item.get("diagnostics", []):
            if(isinstance(diag, dict)):
                diagnostics.append({
                    "level": diag.get("level", "error"),
                    "code": diag.get("code", "UNKNOWN"),
                    "message": diag.get("message", ""),
                })
        rows.append({
            "category": item.get("category", "unknown"),
            "release_category": item.get("release_category", item.get("category", "unknown")),
            "severity": item.get("severity", "error"),
            "name": item.get("name", ""),
            "diagnostics": diagnostics,
        })
    return rows


def _stable_base_dir(value: Any) -> str:
    text=str(value or ".")
    if(Path(text).is_absolute()):
        return "."
    return text or "."


def build_release_report(manifest_path: str | Path, language: str = "en") -> dict[str, Any]:
    path=Path(manifest_path)
    manifest=_load_manifest(path)
    checks=_normalized_checks(manifest)
    total=len(checks)
    failed=sum(1 for item in checks if(not item.get("ok")))
    warning_count=sum(1 for item in checks for diag in item.get("diagnostics", []) if(isinstance(diag, dict) and diag.get("level")=="warning"))
    error_count=sum(1 for item in checks for diag in item.get("diagnostics", []) if(isinstance(diag, dict) and diag.get("level")=="error"))
    summary={"total": total, "passed": total-failed, "failed": failed, "warning_count": warning_count, "error_count": error_count}
    return {
        "config_type": "sldl.release_report",
        "description": "Generated SLDL release report" if(language=="en") else "生成されたSLDLリリースレポート",
        "version": VERSION,
        "language": language,
        "source_manifest": path.as_posix(),
        "target": manifest.get("target"),
        "base_dir": _stable_base_dir(manifest.get("base_dir")),
        "python": Path(str(manifest.get("python", "python"))).name,
        "summary": summary,
        "category_summary": _category_summary(checks),
        "release_category_summary": _summary_rows(checks, "release_category"),
        "severity_summary": _summary_rows(checks, "severity"),
        "diagnostic_codes": _diagnostic_codes(checks),
        "failed_checks": _failed_checks(checks),
        "ci_summary": {
            "status": "passed" if(failed==0) else "failed",
            "exit_code": 0 if(failed==0) else 1,
            "machine_readable": True,
            "warning_count": warning_count,
            "error_count": error_count,
        },
    }


def render_release_report_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2)+"\n"


def render_release_report_markdown(report: dict[str, Any], language: str = "en") -> str:
    summary=report.get("summary", {}) if(isinstance(report.get("summary"), dict)) else {}
    title="# SLDL Release Report（日本語）" if(language=="ja") else "# SLDL Release Report"
    intro="`quality release` の結果から生成した静的なリリースレポートです。レポート自身を検査するコマンドは循環差分を避けるため集計から除外されます。" if(language=="ja") else "This static release report is generated from a `quality release` manifest. Report-check commands are excluded from the aggregate to avoid circular drift."
    lines=[
        title,
        "",
        intro,
        "",
        f"- version: `{report.get('version', '')}`",
        f"- source_manifest: `{report.get('source_manifest', '')}`",
        f"- status: `{report.get('ci_summary', {}).get('status', '')}`",
        f"- checks: `{summary.get('passed', 0)}/{summary.get('total', 0)} passed, {summary.get('failed', 0)} failed, {summary.get('warning_count', 0)} warnings`",
        "",
        "## Category summary" if(language!="ja") else "## カテゴリ別サマリー",
        "",
        "| Category | Total | Passed | Failed | Warnings |" if(language!="ja") else "| カテゴリ | 合計 | 成功 | 失敗 | 警告 |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in report.get("category_summary", []):
        lines.append(f"| `{row.get('category', '')}` | {row.get('total', 0)} | {row.get('passed', 0)} | {row.get('failed', 0)} | {row.get('warnings', 0)} |")
    lines.extend(["", "## Release category summary" if(language!="ja") else "## リリース分類別サマリー", "", "| Release category | Total | Passed | Failed | Warnings |" if(language!="ja") else "| リリース分類 | 合計 | 成功 | 失敗 | 警告 |", "|---|---:|---:|---:|---:|"])
    for row in report.get("release_category_summary", []):
        lines.append(f"| `{row.get('release_category', '')}` | {row.get('total', 0)} | {row.get('passed', 0)} | {row.get('failed', 0)} | {row.get('warnings', 0)} |")
    lines.extend(["", "## Severity summary" if(language!="ja") else "## 重要度別サマリー", "", "| Severity | Total | Passed | Failed | Warnings |" if(language!="ja") else "| 重要度 | 合計 | 成功 | 失敗 | 警告 |", "|---|---:|---:|---:|---:|"])
    for row in report.get("severity_summary", []):
        lines.append(f"| `{row.get('severity', '')}` | {row.get('total', 0)} | {row.get('passed', 0)} | {row.get('failed', 0)} | {row.get('warnings', 0)} |")
    lines.extend(["", "## Diagnostic codes" if(language!="ja") else "## 診断コード", ""])
    codes=report.get("diagnostic_codes", [])
    if(codes):
        lines.extend(["| Code | Level | Count |", "|---|---|---:|"])
        for row in codes:
            lines.append(f"| `{row.get('code', '')}` | `{row.get('level', '')}` | {row.get('count', 0)} |")
    else:
        lines.append("No diagnostics were recorded." if(language!="ja") else "記録された診断はありません。")
    lines.extend(["", "## Failed checks" if(language!="ja") else "## 失敗した検査", ""])
    failed=report.get("failed_checks", [])
    if(failed):
        for item in failed:
            lines.append(f"- `{item.get('severity', 'error')}` / `{item.get('release_category', item.get('category', ''))}` / `{item.get('name', '')}`")
            for diag in item.get("diagnostics", []):
                lines.append(f"  - `{diag.get('code', '')}`: {diag.get('message', '')}")
    else:
        lines.append("None." if(language!="ja") else "なし。")
    lines.extend([
        "",
        "## Commands" if(language!="ja") else "## コマンド",
        "",
        "```bash",
        "python3 -S -m sldl_compiler.cli quality release \\",
        "  --targets examples/release_check.json \\",
        "  --manifest build/release_manifest.json",
        "python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format markdown --check docs/release_report.md",
        "python3 -S -m sldl_compiler.cli quality report build/release_manifest.json --format json --check docs/release_report.json",
        "python3 -S -m sldl_compiler.cli quality release --targets examples/release_summary_smoke_check.json --summary-json build/release_summary_smoke.json",
        "```",
    ])
    return "\n".join(lines)+"\n"
