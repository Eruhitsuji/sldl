from __future__ import annotations

import json
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.config_tools import check_config_file
from sldl_compiler.quality import run_release_check
from sldl_compiler.templates import get_template, list_templates

ROOT=Path(__file__).resolve().parents[1]


def test_version_metadata_v102():
    assert __version__=="1.0.2"


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
    assert project["version"]=="1.0.2"
    assert project["schemas"]
    assert project["export_config"].endswith("examples/export_labels_en.json")
    assert project["latex_build_config"].endswith("examples/latex_build_platex_dvipdfmx_dry_run.json")
    assert project["documents"][0]["template"]=="research_report_en"
    assert main(["project", "check", str(project_path), "--warnings-as-errors"])==0


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
