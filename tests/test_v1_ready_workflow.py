from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.config_tools import check_config_file
from sldl_compiler.quality import run_release_check

ROOT=Path(__file__).resolve().parents[1]


def test_version_metadata():
    assert __version__=="1.0.14"


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
    manifest_path=ROOT/"build"/"test_release_manifest.json"
    proc=subprocess.run([
        sys.executable,
        "-S",
        "-m",
        "sldl_compiler.cli",
        "quality",
        "release",
        "--targets",
        str(ROOT/"examples"/"release_check.json"),
        "--manifest",
        str(manifest_path),
    ], cwd=ROOT, text=True, capture_output=True, timeout=120)
    assert proc.returncode==0, proc.stdout+proc.stderr
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["summary"]["failed"]==0


def test_v114_readme_and_getting_started_are_template_first():
    readme=(ROOT/"README.md").read_text(encoding="utf-8")
    getting_started=(ROOT/"docs"/"getting_started.md").read_text(encoding="utf-8")
    ja_getting_started=(ROOT/"docs"/"ja"/"getting_started.md").read_text(encoding="utf-8")
    for text in [readme, getting_started, ja_getting_started]:
        assert "template project research_report_en" in text
        assert "project check examples/my_report_project.json" in text
        assert "project build examples/my_report_project.json" in text
        assert "quality manifest build/my_report/sldl_build_manifest.json" in text


def test_v114_commands_reference_documents_template_docs_checks():
    commands=(ROOT/"docs"/"commands_reference.md").read_text(encoding="utf-8")
    ja_commands=(ROOT/"docs"/"ja"/"commands_reference.md").read_text(encoding="utf-8")
    for text in [commands, ja_commands]:
        assert "template explain research_report_en --format markdown" in text
        assert "template explain research_report_en --format json" in text
        assert "template docs --format markdown --check docs/generated_template_reference.md" in text
        assert "template docs --format markdown --language ja --check docs/ja/generated_template_reference.md" in text
        assert "template docs --format json --check docs/generated_template_reference.json" in text


def test_v114_project_workflow_and_examples_document_template_provenance():
    project_workflow=(ROOT/"docs"/"project_workflow.md").read_text(encoding="utf-8")
    ja_project_workflow=(ROOT/"docs"/"ja"/"project_workflow.md").read_text(encoding="utf-8")
    examples_readme=(ROOT/"examples"/"README.md").read_text(encoding="utf-8")
    for text in [project_workflow, ja_project_workflow, examples_readme]:
        assert "template_schema_binding_project.json" in text
        assert "template metadata" in text or "template metadata" in text.lower() or "template情報" in text
        assert "SHA-256" in text
