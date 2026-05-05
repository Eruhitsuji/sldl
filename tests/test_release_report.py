from __future__ import annotations

import json
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.config_tools import check_config_file
from sldl_compiler.release_report import build_release_report

ROOT=Path(__file__).resolve().parents[1]


def _build_smoke_manifest(tmp_path: Path) -> Path:
    manifest=tmp_path/"release_manifest.json"
    summary=tmp_path/"release_summary.json"
    assert main([
        "quality", "release",
        "--targets", str(ROOT/"examples"/"release_summary_smoke_check.json"),
        "--manifest", str(manifest),
        "--summary-json", str(summary),
    ])==0
    return manifest


def test_version_metadata_v115():
    assert __version__=="1.0.15"


def test_release_report_json_is_valid_config():
    diagnostics=check_config_file(ROOT/"docs"/"release_report.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_release_report_builds_summary_from_manifest(tmp_path):
    report=build_release_report(_build_smoke_manifest(tmp_path))
    assert report["config_type"]=="sldl.release_report"
    assert report["summary"]["failed"]==0
    assert report["summary"]["total"]>0
    assert any(row["category"]=="command" for row in report["category_summary"])
    assert report["base_dir"]=="."


def test_release_report_commands_and_drift_check(tmp_path):
    md_out=tmp_path/"release_report.md"
    json_out=tmp_path/"release_report.json"
    manifest=_build_smoke_manifest(tmp_path)
    assert main(["quality", "report", str(manifest), "--format", "markdown", "-o", str(md_out)])==0
    assert "SLDL Release Report" in md_out.read_text(encoding="utf-8")
    assert main(["quality", "report", str(manifest), "--format", "markdown", "--check", str(md_out)])==0
    md_out.write_text(md_out.read_text(encoding="utf-8")+"\nmanual drift\n", encoding="utf-8")
    assert main(["quality", "report", str(manifest), "--format", "markdown", "--check", str(md_out)])==1
    assert main(["quality", "report", str(manifest), "--format", "json", "-o", str(json_out)])==0
    data=json.loads(json_out.read_text(encoding="utf-8"))
    assert data["config_type"]=="sldl.release_report"
    assert data["version"]=="1.0.15"


def test_release_report_ignores_own_drift_checks(tmp_path):
    report=build_release_report(_build_smoke_manifest(tmp_path))
    names={item["name"] for item in report.get("failed_checks", [])}
    assert not any(name.startswith("quality-report-") for name in names)


def test_release_summary_json_is_valid_config():
    diagnostics=check_config_file(ROOT/"docs"/"release_summary.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_release_summary_command(tmp_path):
    manifest_path=tmp_path/"summary_manifest.json"
    summary_path=tmp_path/"release_summary.json"
    assert main([
        "quality", "release",
        "--targets", str(ROOT/"examples"/"release_summary_smoke_check.json"),
        "--manifest", str(manifest_path),
        "--summary-json", str(summary_path),
    ])==0
    data=json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["config_type"]=="sldl.release_summary"
    assert data["version"]=="1.0.15"
    assert data["ci_summary"]["status"]=="passed"
    assert any(row["release_category"]=="release-summary" for row in data["release_category_summary"])
