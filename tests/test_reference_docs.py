from __future__ import annotations

import json
import os
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.config_tools import check_config_file
from sldl_compiler.reference_docs import build_cli_help_reference, build_reference_index

ROOT=Path(__file__).resolve().parents[1]


def test_version_metadata_v110():
    assert __version__=="1.0.12"


def test_reference_index_json_is_valid_config():
    diagnostics=check_config_file(ROOT/"docs"/"reference_index.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_cli_help_reference_json_is_valid_config():
    diagnostics=check_config_file(ROOT/"docs"/"cli_help_reference.json")
    assert [d.to_dict() for d in diagnostics if d.level=="error"]==[]


def test_reference_index_contains_generated_references():
    index=build_reference_index(ROOT)
    paths={item["path"] for item in index["references"]}
    assert "docs/generated_template_reference.json" in paths
    assert "docs/diagnostics_reference.json" in paths
    assert "docs/cli_help_reference.json" in paths
    assert "docs/release_report.json" in paths


def test_reference_commands_and_drift_check(tmp_path):
    index_out=tmp_path/"reference_index.md"
    help_out=tmp_path/"cli_help_reference.md"
    assert main(["reference", "index", "--format", "markdown", "-o", str(index_out)])==0
    assert main(["reference", "index", "--format", "markdown", "--check", str(index_out)])==0
    index_out.write_text(index_out.read_text(encoding="utf-8")+"\nmanual drift\n", encoding="utf-8")
    assert main(["reference", "index", "--format", "markdown", "--check", str(index_out)])==1
    assert main(["reference", "cli-help", "--format", "markdown", "-o", str(help_out)])==0
    assert "template project" in help_out.read_text(encoding="utf-8")
    assert main(["reference", "cli-help", "--format", "markdown", "--check", str(help_out)])==0


def test_reference_json_outputs_are_valid_configs(tmp_path):
    index_json=tmp_path/"reference_index.json"
    help_json=tmp_path/"cli_help_reference.json"
    assert main(["reference", "cli-help", "--format", "json", "-o", str(help_json)])==0
    assert main(["reference", "index", "--format", "json", "-o", str(index_json)])==0
    help_data=json.loads(help_json.read_text(encoding="utf-8"))
    index_data=json.loads(index_json.read_text(encoding="utf-8"))
    assert help_data["config_type"]=="sldl.cli_help_reference"
    assert index_data["config_type"]=="sldl.reference_index"
    assert help_data["version"]=="1.0.12"
    assert index_data["version"]=="1.0.12"
    assert [d.to_dict() for d in check_config_file(help_json) if d.level=="error"]==[]
    assert [d.to_dict() for d in check_config_file(index_json) if d.level=="error"]==[]


def test_cli_help_reference_builder_covers_reference_command():
    from sldl_compiler.cli import build_arg_parser
    reference=build_cli_help_reference(build_arg_parser())
    commands={item["command"] for item in reference["commands"]}
    assert "reference" in commands
    assert "reference index" in commands
    assert "reference cli-help" in commands


def test_cli_help_reference_is_terminal_width_independent(monkeypatch):
    from sldl_compiler.cli import build_arg_parser
    monkeypatch.setenv("COLUMNS", "160")
    wide=build_cli_help_reference(build_arg_parser())
    monkeypatch.setenv("COLUMNS", "60")
    narrow=build_cli_help_reference(build_arg_parser())
    assert wide==narrow
    assert os.environ.get("COLUMNS")=="60"
