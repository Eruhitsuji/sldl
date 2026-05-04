from __future__ import annotations

import json
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.config_tools import check_config_file
from sldl_compiler.quality import run_release_check
from sldl_compiler.templates import get_template, list_templates

ROOT=Path(__file__).resolve().parents[1]


def test_version_metadata_v105():
    assert __version__=="1.0.5"


def test_template_manifest_is_schema_bound():
    diagnostics=check_config_file(ROOT/"templates"/"template_manifest.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]
    entries=list_templates(ROOT/"templates")
    names={item["name"] for item in entries}
    assert "research_report_en" in names
    tmpl=get_template("research_report_en", ROOT/"templates")
    assert tmpl.schema is not None
    assert tmpl.default_export_config is not None
    assert tmpl.strict_schema is True


def test_template_explain_outputs_binding():
    assert main(["template", "explain", "research_report_en", "--template-dir", str(ROOT/"templates")])==0
    assert main(["template", "explain", "research_report_en", "--template-dir", str(ROOT/"templates"), "--json"])==0
    assert main(["template", "explain", "research_report_en", "--template-dir", str(ROOT/"templates"), "--format", "json"])==0
    assert main(["template", "explain", "research_report_en", "--template-dir", str(ROOT/"templates"), "--format", "markdown"])==0


def test_template_check_uses_bound_schema():
    assert main(["template", "check", "research_report_en", "--template-dir", str(ROOT/"templates")])==0
    assert main(["template", "check", "minutes", "--template-dir", str(ROOT/"templates")])==0


def test_template_schema_override_is_explicit(tmp_path):
    wrong_schema=tmp_path/"other_schema.json"
    wrong_schema.write_text(json.dumps({"config_type":"sldl.schema","document_types":{}}, ensure_ascii=False), encoding="utf-8")
    assert main([
        "template", "check", "research_report_en",
        "--template-dir", str(ROOT/"templates"),
        "--schema", str(wrong_schema),
    ])==2
    assert main([
        "template", "check", "research_report_en",
        "--template-dir", str(ROOT/"templates"),
        "--schema", str(wrong_schema),
        "--allow-schema-override",
    ])==1


def test_template_project_inherits_manifest_defaults(tmp_path):
    project_path=tmp_path/"generated_project.json"
    document_path=tmp_path/"generated_report.sldl"
    assert main([
        "template", "project", "research_report_en",
        "--template-dir", str(ROOT/"templates"),
        "-o", str(project_path),
        "--document-output", str(document_path),
        "--formats", "markdown,html,latex,pdf",
        "--build-dir", str(tmp_path/"build"),
    ])==0
    project=json.loads(project_path.read_text(encoding="utf-8"))
    assert project["version"]=="1.0.5"
    assert project["schemas"]
    assert project["export_config"].endswith("examples/export_labels_en.json")
    assert project["latex_build_config"].endswith("examples/latex_build_platex_dvipdfmx_dry_run.json")
    assert project["documents"][0]["template"]=="research_report_en"
    assert main(["project", "check", str(project_path), "--warnings-as-errors"])==0


def test_template_project_build_manifest_records_template_metadata(tmp_path):
    project_path=tmp_path/"generated_project.json"
    document_path=tmp_path/"generated_report.sldl"
    build_dir=tmp_path/"build"
    assert main([
        "template", "project", "research_report_en",
        "--template-dir", str(ROOT/"templates"),
        "-o", str(project_path),
        "--document-output", str(document_path),
        "--formats", "markdown",
        "--build-dir", str(build_dir),
    ])==0
    assert main(["project", "build", str(project_path)])==0
    manifest=json.loads((build_dir/"sldl_build_manifest.json").read_text(encoding="utf-8"))
    template_info=manifest["documents"][0].get("template")
    assert template_info["name"]=="research_report_en"
    assert template_info["declared_document_type"]=="ResearchReport"
    assert main(["quality", "manifest", str(build_dir/"sldl_build_manifest.json")])==0


def test_project_document_type_mismatch_negative_example_fails():
    assert main(["config", "check", str(ROOT/"examples"/"template_schema_binding_failure_project.json")])==0
    assert main(["project", "check", str(ROOT/"examples"/"template_schema_binding_failure_project.json")])==1


def test_template_manifest_rejects_unknown_document_type(tmp_path):
    manifest=tmp_path/"template_manifest.json"
    template=tmp_path/"sample.sldl"
    template.write_text('document "sample" : UnknownDoc { meta { title: "x"@en; } }\n', encoding="utf-8")
    manifest.write_text(json.dumps({
        "config_type":"sldl.template_manifest",
        "templates":[{
            "name":"sample",
            "description":"Sample",
            "document_type":"UnknownDoc",
            "language":"en-US",
            "path":"sample.sldl",
            "schema":str(ROOT/"examples"/"sldl_schema.json"),
            "default_export_config":str(ROOT/"examples"/"export_labels_en.json"),
            "default_latex_build_config":str(ROOT/"examples"/"latex_build_platex_dvipdfmx_dry_run.json"),
            "strict_schema":True
        }]
    }, ensure_ascii=False), encoding="utf-8")
    diagnostics=check_config_file(manifest)
    assert any(d.code=="E_TEMPLATE_SCHEMA_DOCUMENT_TYPE" for d in diagnostics)


def test_template_manifest_compatibility_copy_is_checked():
    diagnostics=check_config_file(ROOT/"templates"/"manifest.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_release_check_expected_failure_command_support(tmp_path):
    target=tmp_path/"release_check.json"
    target.write_text(json.dumps({
        "config_type":"sldl.release_check",
        "base_dir":str(ROOT),
        "commands":[{
            "name":"negative-project-check",
            "args":["project", "check", "examples/template_schema_binding_failure_project.json"],
            "expect_failure":True
        }],
        "compileall":False
    }, ensure_ascii=False), encoding="utf-8")
    code,manifest=run_release_check(target)
    assert code==0
    assert manifest["summary"]["failed"]==0


def test_template_docs_command_outputs_reference(tmp_path):
    out=tmp_path/"template_reference.md"
    assert main(["template", "docs", "--template-dir", str(ROOT/"templates"), "--format", "markdown", "-o", str(out)])==0
    text=out.read_text(encoding="utf-8")
    assert "research_report_en" in text
    assert "examples/sldl_schema.json" in text or "sldl_schema.json" in text
    assert main(["template", "docs", "--template-dir", str(ROOT/"templates"), "--format", "json"])==0


def test_legacy_manifest_warns_but_has_no_errors():
    diagnostics=check_config_file(ROOT/"templates"/"manifest.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]
    assert any(d.code=="W_TEMPLATE_MANIFEST_LEGACY" for d in diagnostics)


def test_build_manifest_template_metadata_is_canonical(tmp_path):
    project_path=tmp_path/"generated_project.json"
    document_path=tmp_path/"generated_report.sldl"
    build_dir=tmp_path/"build"
    assert main([
        "template", "project", "research_report_en",
        "--template-dir", str(ROOT/"templates"),
        "-o", str(project_path),
        "--document-output", str(document_path),
        "--formats", "markdown",
        "--build-dir", str(build_dir),
    ])==0
    project=json.loads(project_path.read_text(encoding="utf-8"))
    assert project["documents"][0]["template_manifest_role"]=="canonical"
    assert project["documents"][0]["template_manifest"].endswith("templates/template_manifest.json")
    assert main(["project", "build", str(project_path)])==0
    manifest=json.loads((build_dir/"sldl_build_manifest.json").read_text(encoding="utf-8"))
    template_info=manifest["documents"][0]["template"]
    assert template_info["manifest_role"]=="canonical"
    assert template_info["manifest"].endswith("templates/template_manifest.json")
    assert main(["quality", "manifest", str(build_dir/"sldl_build_manifest.json")])==0


def test_template_docs_check_detects_static_reference_drift(tmp_path):
    out=tmp_path/"template_reference.md"
    assert main(["template", "docs", "--template-dir", str(ROOT/"templates"), "--format", "markdown", "-o", str(out)])==0
    assert main(["template", "docs", "--template-dir", str(ROOT/"templates"), "--format", "markdown", "--check", str(out)])==0
    out.write_text(out.read_text(encoding="utf-8")+"\nmanual drift\n", encoding="utf-8")
    assert main(["template", "docs", "--template-dir", str(ROOT/"templates"), "--format", "markdown", "--check", str(out)])==1


def test_template_docs_japanese_and_json_reference_are_valid(tmp_path):
    ja_out=tmp_path/"template_reference_ja.md"
    json_out=tmp_path/"template_reference.json"
    assert main(["template", "docs", "--template-dir", str(ROOT/"templates"), "--format", "markdown", "--language", "ja", "-o", str(ja_out)])==0
    assert "日本語" in ja_out.read_text(encoding="utf-8")
    assert main(["template", "docs", "--template-dir", str(ROOT/"templates"), "--format", "json", "-o", str(json_out)])==0
    diagnostics=check_config_file(json_out)
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_build_manifest_template_hash_metadata_is_checked(tmp_path):
    project_path=tmp_path/"generated_project.json"
    document_path=tmp_path/"generated_report.sldl"
    build_dir=tmp_path/"build"
    assert main([
        "template", "project", "research_report_en",
        "--template-dir", str(ROOT/"templates"),
        "-o", str(project_path),
        "--document-output", str(document_path),
        "--formats", "markdown",
        "--build-dir", str(build_dir),
    ])==0
    assert main(["project", "build", str(project_path)])==0
    manifest_path=build_dir/"sldl_build_manifest.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8"))
    template_info=manifest["documents"][0]["template"]
    for key in ["source_sha256", "manifest_sha256", "schema_sha256", "export_config_sha256", "latex_build_config_sha256"]:
        assert isinstance(template_info.get(key), str)
        assert len(template_info[key])==64
    assert main(["quality", "manifest", str(manifest_path)])==0
    template_info["source_sha256"]="0"*64
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    assert main(["quality", "manifest", str(manifest_path)])==1
