from __future__ import annotations

import json
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.config_tools import check_config_file
from sldl_compiler.quality import run_release_check

ROOT=Path(__file__).resolve().parents[1]


def test_version_metadata():
    assert __version__=="1.0.1"


def test_curated_config_files_are_valid():
    for rel in [
        "examples/export_labels_en.json",
        "examples/export_labels_ja.json",
        "examples/latex_build_platex_dvipdfmx_dry_run.json",
        "examples/sldl_schema.json",
        "examples/project_official_examples.json",
        "examples/release_check.json",
        "templates/template_manifest.json",
    ]:
        diagnostics=check_config_file(ROOT/rel)
        assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_bilingual_documents_check_and_markdown_export(tmp_path):
    cases=[
        ("official_project_overview_en.sldl", "SLDL official project overview"),
        ("official_project_overview_ja.sldl", "SLDL公式プロジェクト概要"),
        ("research_report_en.sldl", "Bilingual SLDL research report example"),
        ("research_report_ja.sldl", "二言語SLDL研究報告書サンプル"),
    ]
    for file_name,expected in cases:
        src=ROOT/"examples"/file_name
        md_path=tmp_path/(Path(file_name).stem+".md")
        assert main(["check", str(src), "--schema", str(ROOT/"examples"/"sldl_schema.json")])==0
        assert main([
            "export",
            str(src),
            "--schema",
            str(ROOT/"examples"/"sldl_schema.json"),
            "--format",
            "markdown",
            "-o",
            str(md_path),
        ])==0
        assert md_path.exists()
        assert expected in md_path.read_text(encoding="utf-8")


def test_project_build_and_manifest_validation():
    assert main(["project", "check", "examples/project_official_examples.json"])==0
    assert main(["project", "build", "examples/project_official_examples.json"])==0
    assert main(["quality", "manifest", "build/official_examples/sldl_build_manifest.json"])==0


def test_forbidden_glob_rejects_legacy_files(tmp_path):
    legacy=tmp_path/"examples"/"v012_old_sample.sldl"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("legacy", encoding="utf-8")
    target=tmp_path/"release_check.json"
    target.write_text(json.dumps({
        "config_type": "sldl.release_check",
        "version": "1.0.0",
        "base_dir": ".",
        "forbidden_globs": ["examples/v0*"],
        "compileall": False,
    }), encoding="utf-8")
    code,manifest=run_release_check(target)
    assert code==1
    assert manifest["summary"]["failed"]==1
    assert any(item["category"]=="forbidden-paths" and not item["ok"] for item in manifest["checks"])


def test_release_check_passes_after_project_build():
    code,manifest=run_release_check(ROOT/"examples"/"release_check.json", ROOT/"build"/"test_release_manifest.json")
    assert code==0
    assert manifest["summary"]["failed"]==0
