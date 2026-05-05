from __future__ import annotations

import json
from pathlib import Path

from sldl_compiler import __version__
from sldl_compiler.cli import main
from sldl_compiler.quality import _cli_args_support_warnings_as_errors

ROOT=Path(__file__).resolve().parents[1]


def test_version_metadata_v115():
    assert __version__=="1.0.15"


def test_github_actions_workflows_are_present_and_use_release_gate():
    test_workflow=(ROOT/".github"/"workflows"/"test.yml").read_text(encoding="utf-8")
    release_workflow=(ROOT/".github"/"workflows"/"release-check.yml").read_text(encoding="utf-8")
    assert "python -m pytest -q" in test_workflow
    assert "Install test dependencies" in test_workflow
    assert "python -m pip install -e" in test_workflow
    assert ".[test]" in test_workflow
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD" in test_workflow
    assert "python -S -m sldl_compiler.cli quality release" in release_workflow
    assert "--summary-json build/release_summary.json" in release_workflow
    assert "Check generated release report" in release_workflow
    assert "quality report build/release_manifest.json" in release_workflow
    assert "actions/upload-artifact@v4" in release_workflow
    assert "Prepare build directory" in release_workflow
    assert "mkdir -p build" in release_workflow


def test_ci_documentation_is_bilingual_and_linked_from_index():
    ci_doc=(ROOT/"docs"/"ci_workflow.md").read_text(encoding="utf-8")
    ja_ci_doc=(ROOT/"docs"/"ja"/"ci_workflow.md").read_text(encoding="utf-8")
    index=(ROOT/"docs"/"index.md").read_text(encoding="utf-8")
    ja_index=(ROOT/"docs"/"ja"/"index.md").read_text(encoding="utf-8")
    for text in [ci_doc, ja_ci_doc, index, ja_index]:
        assert "ci_workflow.md" in text or "CI workflow" in text
    assert ".github/workflows/release-check.yml" in ci_doc
    assert ".github/workflows/release-check.yml" in ja_ci_doc
    assert "build/release_summary.json" in ci_doc
    assert "build/release_summary.json" in ja_ci_doc
    assert "clean checkout" in ci_doc
    assert "clean checkout" in ja_ci_doc


def test_release_check_declares_ci_files_and_strict_smoke_command():
    data=json.loads((ROOT/"examples"/"release_check.json").read_text(encoding="utf-8"))
    required=set(data.get("required_files", []))
    for path in [
        ".github/workflows/test.yml",
        ".github/workflows/release-check.yml",
        "docs/ci_workflow.md",
        "docs/ja/ci_workflow.md",
        "docs/v1_0_13_release_notes.md",
        "docs/ja/v1_0_13_release_notes.md",
        "docs/v1_0_14_release_notes.md",
        "docs/ja/v1_0_14_release_notes.md",
        "docs/v1_0_15_release_notes.md",
        "docs/ja/v1_0_15_release_notes.md",
        "pyproject.toml",
    ]:
        assert path in required
    command_names={cmd.get("name") for cmd in data.get("commands", [])}
    assert "quality-release-summary-strict-smoke" in command_names
    assert not any(str(name).startswith("quality-report-") for name in command_names)


def test_warning_sensitive_release_gate_only_adds_supported_flags():
    assert _cli_args_support_warnings_as_errors(["config", "check", "examples/release_check.json"])
    assert not _cli_args_support_warnings_as_errors(["config", "list"])
    assert _cli_args_support_warnings_as_errors(["schema", "check", "examples/sldl_schema.json"])
    assert not _cli_args_support_warnings_as_errors(["schema", "list"])
    assert _cli_args_support_warnings_as_errors(["project", "build", "examples/project_official_examples.json"])


def test_release_summary_strict_smoke_command(tmp_path):
    manifest=tmp_path/"strict_manifest.json"
    summary=tmp_path/"strict_summary.json"
    assert main([
        "quality", "release",
        "--targets", str(ROOT/"examples"/"release_summary_smoke_check.json"),
        "--manifest", str(manifest),
        "--summary-json", str(summary),
        "--fail-on-warning",
    ])==0
    data=json.loads(summary.read_text(encoding="utf-8"))
    assert data["config_type"]=="sldl.release_summary"
    assert data["version"]=="1.0.15"
    assert data["ci_summary"]["status"]=="passed"


def test_pyproject_metadata_declares_v115_and_test_extra():
    pyproject=(ROOT/"pyproject.toml").read_text(encoding="utf-8")
    assert 'version = "1.0.15"' in pyproject
    assert '[project.optional-dependencies]' in pyproject
    assert 'pytest>=7.1' in pyproject
