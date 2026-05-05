from __future__ import annotations

import json
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.config_tools import check_config_file
from sldl_compiler.diagnostic_reference import build_diagnostics_reference

ROOT=Path(__file__).resolve().parents[1]


def test_version_metadata_v114():
    assert __version__=="1.0.14"


def test_diagnostics_reference_contains_schema_template_codes():
    reference=build_diagnostics_reference(ROOT)
    codes={item["code"] for item in reference["codes"]}
    assert "E_SCHEMA_FILE_MISSING" in codes
    assert "E_TEMPLATE_MANIFEST_SCHEMA_MISSING" in codes
    assert "W_TEMPLATE_MANIFEST_LEGACY" in codes
    assert reference["counts"]["total"]==len(codes)


def test_diagnostics_reference_json_is_valid_config():
    diagnostics=check_config_file(ROOT/"docs"/"diagnostics_reference.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_diagnostics_docs_commands_and_drift_check(tmp_path):
    out=tmp_path/"diagnostics_reference.md"
    assert main(["diagnostics", "list"])==0
    assert main(["diagnostics", "list", "--json"])==0
    assert main(["diagnostics", "docs", "--format", "markdown", "-o", str(out)])==0
    assert "E_SCHEMA_FILE_MISSING" in out.read_text(encoding="utf-8")
    assert main(["diagnostics", "docs", "--format", "markdown", "--check", str(out)])==0
    out.write_text(out.read_text(encoding="utf-8")+"\nmanual drift\n", encoding="utf-8")
    assert main(["diagnostics", "docs", "--format", "markdown", "--check", str(out)])==1


def test_diagnostics_docs_json_output_is_valid_config(tmp_path):
    out=tmp_path/"diagnostics_reference.json"
    assert main(["diagnostics", "docs", "--format", "json", "-o", str(out)])==0
    data=json.loads(out.read_text(encoding="utf-8"))
    assert data["config_type"]=="sldl.diagnostics_reference"
    assert data["version"]=="1.0.14"
    diagnostics=check_config_file(out)
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]
