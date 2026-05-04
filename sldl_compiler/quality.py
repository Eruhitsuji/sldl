from __future__ import annotations

import ast
import contextlib
import tempfile
import hashlib
import json
from pathlib import Path
import sys
import time
from typing import Any

from .config_tools import check_config_file, load_config_json
from .diagnostics import Diagnostic


def sha256_file(path: str | Path) -> str:
    path=Path(path)
    digest=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024*1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_snapshot(files: list[str | Path], base_dir: str | Path = ".", description: str | None = None, version: str = "1.0.0") -> dict[str, Any]:
    base=Path(base_dir).resolve()
    entries=[]
    for file_name in files:
        path=Path(file_name)
        abs_path=path if(path.is_absolute()) else (base/path)
        abs_path=abs_path.resolve()
        rel_path=abs_path.relative_to(base).as_posix() if(_is_relative_to(abs_path, base)) else str(abs_path)
        entries.append({
            "path": rel_path,
            "bytes": abs_path.stat().st_size,
            "sha256": sha256_file(abs_path),
        })
    return {
        "config_type": "sldl.snapshot_manifest",
        "description": description or "SLDL golden file snapshot",
        "version": version,
        "files": entries,
    }


def check_snapshot(snapshot_path: str | Path, base_dir: str | Path | None = None) -> tuple[list[Diagnostic], dict[str, Any]]:
    snapshot_path=Path(snapshot_path)
    data,diagnostics=load_config_json(snapshot_path)
    details={"files": []}
    if(data is None):
        return diagnostics, details
    if(data.get("config_type") not in {"sldl.snapshot_manifest", None}):
        diagnostics.append(Diagnostic("error", "E_SNAPSHOT_TYPE", "snapshot config_type must be sldl.snapshot_manifest"))
    files=data.get("files")
    if(not isinstance(files, list)):
        diagnostics.append(Diagnostic("error", "E_SNAPSHOT_FILES", "snapshot files must be a list"))
        return diagnostics, details
    base=Path(base_dir).resolve() if(base_dir is not None) else snapshot_path.parent.resolve()
    for i,item in enumerate(files):
        loc=f"files[{i}]"
        if(not isinstance(item, dict)):
            diagnostics.append(Diagnostic("error", "E_SNAPSHOT_FILE", f"{loc} must be an object"))
            continue
        path_value=item.get("path")
        expected_hash=item.get("sha256")
        expected_bytes=item.get("bytes")
        if(not isinstance(path_value, str) or not path_value):
            diagnostics.append(Diagnostic("error", "E_SNAPSHOT_PATH", f"{loc}.path must be a non-empty string"))
            continue
        path=Path(path_value)
        abs_path=path if(path.is_absolute()) else base/path
        result={"path": str(abs_path), "expected_sha256": expected_hash, "expected_bytes": expected_bytes}
        if(not abs_path.exists()):
            diagnostics.append(Diagnostic("error", "E_SNAPSHOT_MISSING", f"snapshot file does not exist: {abs_path}"))
            result["status"]="missing"
            details["files"].append(result)
            continue
        actual_hash=sha256_file(abs_path)
        actual_bytes=abs_path.stat().st_size
        result.update({"actual_sha256": actual_hash, "actual_bytes": actual_bytes})
        if(expected_hash!=actual_hash):
            diagnostics.append(Diagnostic("error", "E_SNAPSHOT_HASH", f"sha256 mismatch for {path_value}"))
            result["status"]="hash-mismatch"
        elif(isinstance(expected_bytes, int) and expected_bytes!=actual_bytes):
            diagnostics.append(Diagnostic("error", "E_SNAPSHOT_BYTES", f"byte size mismatch for {path_value}"))
            result["status"]="byte-mismatch"
        else:
            result["status"]="ok"
        details["files"].append(result)
    return diagnostics, details


def run_release_check(target_path: str | Path | None = None, manifest_path: str | Path | None = None, warnings_as_errors: bool = False) -> tuple[int, dict[str, Any]]:
    root=Path.cwd().resolve()
    target=None
    target_file=None
    if(target_path):
        target_file=Path(target_path)
    elif((root/"examples"/"release_check.json").exists()):
        target_file=Path("examples/release_check.json")
    if(target_file is not None):
        data,diagnostics=load_config_json(target_file)
        if(data is None):
            manifest=_new_release_manifest(target_file, root)
            for diag in diagnostics:
                _add_check(manifest, "target-config", str(target_file), False, [diag])
            _finish_manifest(manifest)
            _write_manifest_if_requested(manifest, manifest_path)
            return 1, manifest
        target=data
        base_dir_value=target.get("base_dir", ".")
        base_dir=Path(base_dir_value)
        base=(target_file.parent/base_dir).resolve() if(not base_dir.is_absolute()) else base_dir.resolve()
    else:
        target=_default_release_target()
        base=root

    manifest=_new_release_manifest(target_file, base)
    target_diags=_validate_release_target(target, target_file.parent if(target_file is not None) else base, check_paths=True)
    _add_check(manifest, "target-config", str(target_file or "<default>"), not _has_failures(target_diags, warnings_as_errors), target_diags)

    if(target.get("forbidden_paths") is not None or target.get("forbidden_globs") is not None):
        _run_forbidden_path_checks(manifest, base, target.get("forbidden_paths", []), target.get("forbidden_globs", []))

    if(target.get("required_files") is not None):
        _run_required_file_checks(manifest, base, target.get("required_files", []))

    for path in target.get("config_files", []):
        abs_path=_resolve(base, path)
        diagnostics=check_config_file(abs_path)
        ok=not _has_failures(diagnostics, warnings_as_errors)
        _add_check(manifest, "config-check", str(path), ok, diagnostics)

    if(target.get("compileall", True)):
        compile_targets=target.get("compile_paths", ["sldl_compiler", "tests"])
        for path in compile_targets:
            _run_compileall_check(manifest, base, path)

    for command in target.get("commands", []):
        _run_cli_command_check(manifest, base, command, warnings_as_errors)

    for path in target.get("project_files", []):
        _run_cli_args_check(manifest, base, f"project-check:{path}", ["project", "check", str(path)] + (["--warnings-as-errors"] if(warnings_as_errors) else []))

    build_projects=target.get("build_project_files")
    if(build_projects is None):
        build_projects=target.get("project_files", [])
    for path in build_projects:
        _run_cli_args_check(manifest, base, f"project-build:{path}", ["project", "build", str(path)] + (["--warnings-as-errors"] if(warnings_as_errors) else []))

    for manifest_file in target.get("build_manifest_files", []):
        diagnostics=_validate_build_manifest_file(_resolve(base, manifest_file))
        ok=not _has_failures(diagnostics, warnings_as_errors)
        _add_check(manifest, "build-manifest-check", str(manifest_file), ok, diagnostics)

    snapshot=target.get("golden_snapshot")
    if(snapshot):
        diagnostics,details=check_snapshot(_resolve(base, snapshot), base_dir=base)
        ok=not _has_failures(diagnostics, warnings_as_errors)
        _add_check(manifest, "snapshot-check", str(snapshot), ok, diagnostics, extra={"details": details})

    _finish_manifest(manifest)
    _write_manifest_if_requested(manifest, manifest_path)
    return (0 if(manifest["summary"]["failed"]==0) else 1), manifest


def validate_build_manifest(path: str | Path) -> list[Diagnostic]:
    return _validate_build_manifest_file(Path(path))


def _default_release_target() -> dict[str, Any]:
    return {
        "config_type": "sldl.release_check",
        "description": "Default SLDL release check target",
        "version": "1.0.0",
        "required_files": ["README.md", "CHANGELOG.md", "sldl_compiler/cli.py"],
        "forbidden_globs": ["examples/v0*", "docs/sldl_v0_*", "docs/v0_*"],
        "config_files": [
            "examples/export_labels_ja.json",
            "examples/latex_build_platex_dvipdfmx_dry_run.json",
            "examples/sldl_schema.json",
            "examples/project_official_examples.json",
        ],
        "project_files": ["examples/project_official_examples.json"],
        "build_project_files": ["examples/project_official_examples.json"],
        "compileall": True,
        "compile_paths": ["sldl_compiler"],
    }


def _new_release_manifest(target_file: Path | None, base: Path) -> dict[str, Any]:
    return {
        "config_type": "sldl.release_manifest",
        "description": "SLDL release quality check manifest",
        "version": "1.0.0",
        "target": str(target_file) if(target_file is not None) else None,
        "base_dir": str(base),
        "python": sys.executable,
        "checks": [],
        "summary": {"total": 0, "passed": 0, "failed": 0},
        "elapsed_sec": 0.0,
        "_start": time.monotonic(),
    }


def _finish_manifest(manifest: dict[str, Any]) -> None:
    total=len(manifest["checks"])
    failed=sum(1 for item in manifest["checks"] if(not item.get("ok")))
    manifest["summary"]={"total": total, "passed": total-failed, "failed": failed}
    manifest["elapsed_sec"]=round(time.monotonic()-manifest.get("_start", time.monotonic()), 3) if("_start" in manifest) else manifest.get("elapsed_sec", 0.0)
    manifest.pop("_start", None)


def _write_manifest_if_requested(manifest: dict[str, Any], manifest_path: str | Path | None) -> None:
    if(not manifest_path):
        return
    path=Path(manifest_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")


def _run_forbidden_path_checks(manifest: dict[str, Any], base: Path, paths: Any, globs: Any) -> None:
    diagnostics=[]
    checked=0
    if(paths is None):
        paths=[]
    if(globs is None):
        globs=[]
    if(not isinstance(paths, list) or not all(isinstance(item, str) for item in paths)):
        diagnostics.append(Diagnostic("error", "E_RELEASE_FORBIDDEN_PATHS", "forbidden_paths must be a list of strings"))
    else:
        for item in paths:
            checked+=1
            path=_resolve(base, item)
            if(path.exists()):
                diagnostics.append(Diagnostic("error", "E_RELEASE_FORBIDDEN_PATH_EXISTS", f"forbidden path exists: {item}"))
    matches=[]
    if(not isinstance(globs, list) or not all(isinstance(item, str) for item in globs)):
        diagnostics.append(Diagnostic("error", "E_RELEASE_FORBIDDEN_GLOBS", "forbidden_globs must be a list of strings"))
    else:
        for pattern in globs:
            checked+=1
            for match in sorted(base.glob(pattern)):
                matches.append(match.relative_to(base).as_posix() if(_is_relative_to(match, base)) else str(match))
        for match in matches:
            diagnostics.append(Diagnostic("error", "E_RELEASE_FORBIDDEN_GLOB_MATCH", f"forbidden glob matched: {match}"))
    _add_check(manifest, "forbidden-paths", "legacy-cleanup", not diagnostics, diagnostics, extra={"checked": checked, "matches": matches})


def _run_required_file_checks(manifest: dict[str, Any], base: Path, files: Any) -> None:
    if(not isinstance(files, list)):
        _add_check(manifest, "required-files", "required_files", False, [Diagnostic("error", "E_RELEASE_REQUIRED_FILES", "required_files must be a list")])
        return
    for file_name in files:
        if(not isinstance(file_name, str)):
            _add_check(manifest, "required-file", str(file_name), False, [Diagnostic("error", "E_RELEASE_REQUIRED_FILE", "required file entry must be a string")])
            continue
        path=_resolve(base, file_name)
        if(path.exists()):
            _add_check(manifest, "required-file", file_name, True, [])
        else:
            _add_check(manifest, "required-file", file_name, False, [Diagnostic("error", "E_RELEASE_FILE_MISSING", f"required file does not exist: {path}")])


def _run_compileall_check(manifest: dict[str, Any], base: Path, path_value: str) -> None:
    path=_resolve(base, path_value)
    if(not path.exists()):
        _add_check(manifest, "syntax-check", path_value, False, [Diagnostic("error", "E_RELEASE_COMPILE_PATH", f"compile path does not exist: {path}")])
        return
    files=sorted(path.rglob("*.py")) if(path.is_dir()) else [path]
    diagnostics=[]
    checked=0
    for py_file in files:
        try:
            ast.parse(py_file.read_text(encoding="utf-8"), filename=str(py_file))
            checked+=1
        except SyntaxError as exc:
            diagnostics.append(Diagnostic("error", "E_RELEASE_SYNTAX", f"syntax error in {py_file}: {exc.msg}", exc.lineno or 0, exc.offset or 0))
        except OSError as exc:
            diagnostics.append(Diagnostic("error", "E_RELEASE_FILE_READ", f"cannot read {py_file}: {exc}"))
    _add_check(manifest, "syntax-check", path_value, not diagnostics, diagnostics, extra={"checked_files": checked})


def _run_cli_command_check(manifest: dict[str, Any], base: Path, command: Any, warnings_as_errors: bool) -> None:
    if(not isinstance(command, dict)):
        _add_check(manifest, "command", str(command), False, [Diagnostic("error", "E_RELEASE_COMMAND", "command entry must be an object")])
        return
    name=str(command.get("name") or "command")
    args=command.get("args")
    if(not isinstance(args, list) or not all(isinstance(item, str) for item in args)):
        _add_check(manifest, "command", name, False, [Diagnostic("error", "E_RELEASE_COMMAND_ARGS", "command.args must be a list of strings")])
        return
    if(warnings_as_errors and "--warnings-as-errors" not in args and args and args[0] in {"check", "project", "schema", "config"}):
        args=args+["--warnings-as-errors"]
    expect_failure=bool(command.get("expect_failure", False))
    _run_cli_args_check(manifest, base, name, args, expect_failure=expect_failure)


def _run_cli_args_check(manifest: dict[str, Any], base: Path, name: str, args: list[str], expect_failure: bool = False) -> None:
    old_cwd=Path.cwd()
    stdout_text=""
    stderr_text=""
    try:
        import os
        cli_module=sys.modules.get("sldl_compiler.cli")
        if(cli_module is None or not hasattr(cli_module, "main")):
            main_module=sys.modules.get("__main__")
            if(main_module is not None and hasattr(main_module, "main")):
                cli_module=main_module
        if(cli_module is None or not hasattr(cli_module, "main")):
            from .cli import main as cli_main
        else:
            cli_main=cli_module.main
        os.chdir(base)
        with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stdout_file, tempfile.TemporaryFile(mode="w+", encoding="utf-8") as stderr_file:
            with contextlib.redirect_stdout(stdout_file), contextlib.redirect_stderr(stderr_file):
                try:
                    returncode=cli_main(args)
                except SystemExit as exc:
                    returncode=int(exc.code or 0) if(isinstance(exc.code, int)) else 1
            stdout_file.seek(0)
            stderr_file.seek(0)
            stdout_text=stdout_file.read()
            stderr_text=stderr_file.read()
        ok=(returncode!=0) if(expect_failure) else (returncode==0)
        if(ok):
            diagnostics=[]
        elif(expect_failure):
            diagnostics=[Diagnostic("error", "E_RELEASE_COMMAND_UNEXPECTED_SUCCESS", f"command was expected to fail but succeeded: {' '.join(args)}")]
        else:
            diagnostics=[Diagnostic("error", "E_RELEASE_COMMAND_FAILED", f"command failed with exit code {returncode}: {' '.join(args)}")]
        _add_check(manifest, "command", name, ok, diagnostics, extra={
            "args": args,
            "returncode": returncode,
            "expect_failure": expect_failure,
            "stdout_tail": _tail(stdout_text),
            "stderr_tail": _tail(stderr_text),
        })
    except Exception as exc:
        _add_check(manifest, "command", name, False, [Diagnostic("error", "E_RELEASE_COMMAND_EXCEPTION", f"command raised {type(exc).__name__}: {exc}")], extra={
            "args": args,
            "stdout_tail": _tail(stdout_text),
            "stderr_tail": _tail(stderr_text),
        })
    finally:
        import os
        os.chdir(old_cwd)




def _manifest_template_items(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw=data.get("templates")
    if(isinstance(raw, dict)):
        items=[]
        for name,value in raw.items():
            if(isinstance(value, dict)):
                item=dict(value)
                item.setdefault("name", str(name))
                items.append(item)
        return items
    if(isinstance(raw, list)):
        return [item for item in raw if(isinstance(item, dict))]
    return []


def _same_resolved_path(a: Path | None, b: Path | None) -> bool:
    if(a is None or b is None):
        return a is b
    try:
        return a.resolve()==b.resolve()
    except OSError:
        return str(a)==str(b)


def _validate_template_metadata_against_manifest(template: dict[str, Any], resolved_paths: dict[str, Path], doc_index: int) -> list[Diagnostic]:
    diagnostics=[]
    manifest_path=resolved_paths.get("manifest")
    if(manifest_path is None or not manifest_path.exists()):
        return diagnostics
    try:
        data=json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return [Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_MANIFEST_READ", f"documents[{doc_index}].template.manifest cannot be read: {exc}")]
    template_name=template.get("name")
    matches=[item for item in _manifest_template_items(data) if(item.get("name")==template_name)]
    if(not matches):
        diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_ENTRY", f"documents[{doc_index}].template.name is not declared by its template manifest: {template_name}"))
        return diagnostics
    item=matches[0]
    manifest_base=manifest_path.parent
    expected_paths={
        "source": manifest_base/str(item.get("path", item.get("template_file", ""))),
        "schema": manifest_base/str(item.get("schema", "")) if(item.get("schema")) else None,
        "export_config": manifest_base/str(item.get("default_export_config", "")) if(item.get("default_export_config")) else None,
        "latex_build_config": manifest_base/str(item.get("default_latex_build_config", "")) if(item.get("default_latex_build_config")) else None,
    }
    for key,expected in expected_paths.items():
        actual=resolved_paths.get(key)
        if(expected is not None and actual is not None and not _same_resolved_path(actual, expected)):
            diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_MANIFEST_MISMATCH", f"documents[{doc_index}].template.{key} does not match the canonical manifest entry for {template_name}"))
    declared_type=template.get("declared_document_type")
    manifest_type=item.get("document_type")
    if(isinstance(manifest_type, str) and manifest_type and declared_type!=manifest_type):
        diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_DOCUMENT_TYPE", f"documents[{doc_index}].template.declared_document_type must match manifest document_type {manifest_type}"))
    manifest_role=data.get("manifest_role")
    if(manifest_path.name=="template_manifest.json" and manifest_role not in {"canonical", None, ""}):
        diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_MANIFEST_ROLE", f"documents[{doc_index}].template.manifest points to template_manifest.json but source manifest is not canonical"))
    return diagnostics

def _validate_build_manifest_file(path: Path) -> list[Diagnostic]:
    diagnostics=check_config_file(path, expected_type="sldl.build_manifest", check_paths=False)
    data,load_diags=load_config_json(path)
    if(load_diags):
        return diagnostics
    if(data is None):
        return diagnostics
    documents=data.get("documents")
    project_dir=None
    project_value=data.get("project")
    if(isinstance(project_value, str) and project_value):
        project_path=Path(project_value)
        if(not project_path.is_absolute()):
            project_path=(Path.cwd()/project_path).resolve()
        project_dir=project_path.parent
    if(isinstance(documents, list)):
        for i,doc in enumerate(documents):
            if(not isinstance(doc, dict)):
                continue
            counts=doc.get("diagnostic_counts", {})
            if(isinstance(counts, dict) and counts.get("errors", 0)):
                diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_DOCUMENT_ERRORS", f"documents[{i}] has recorded errors"))
            template=doc.get("template")
            if(isinstance(template, dict) and any(template.get(k) for k in ("name", "source", "manifest"))):
                if(not isinstance(template.get("name"), str) or not template.get("name")):
                    diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_NAME", f"documents[{i}].template.name must be a non-empty string"))
                manifest_ref=template.get("manifest")
                source_ref=template.get("source")
                if(not isinstance(manifest_ref, str) or not manifest_ref):
                    diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_MANIFEST", f"documents[{i}].template.manifest must be recorded"))
                elif(Path(manifest_ref).name!="template_manifest.json"):
                    diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_CANONICAL", f"documents[{i}].template.manifest must point to template_manifest.json"))
                role=template.get("manifest_role")
                if(role not in {"canonical", "adhoc", None, ""}):
                    diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_ROLE", f"documents[{i}].template.manifest_role must be canonical for bundled templates"))
                resolved_template_paths={}
                if(project_dir is not None):
                    for key,ref in (("source", source_ref), ("manifest", manifest_ref), ("schema", template.get("schema")), ("export_config", template.get("export_config")), ("latex_build_config", template.get("latex_build_config"))):
                        if(isinstance(ref, str) and ref):
                            ref_path=Path(ref)
                            if(not ref_path.is_absolute()):
                                ref_path=(project_dir/ref_path).resolve()
                            resolved_template_paths[key]=ref_path
                            if(not ref_path.exists()):
                                diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_PATH", f"documents[{i}].template.{key} does not exist: {ref}"))
                                continue
                            expected_hash=template.get(f"{key}_sha256")
                            if(expected_hash is None):
                                diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_HASH_MISSING", f"documents[{i}].template.{key}_sha256 must be recorded"))
                            elif(not isinstance(expected_hash, str) or len(expected_hash)!=64):
                                diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_HASH", f"documents[{i}].template.{key}_sha256 must be a SHA-256 hex string"))
                            elif(sha256_file(ref_path)!=expected_hash):
                                diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_TEMPLATE_HASH_MISMATCH", f"documents[{i}].template.{key}_sha256 does not match {ref}"))
                    diagnostics.extend(_validate_template_metadata_against_manifest(template, resolved_template_paths, i))
            outputs=doc.get("outputs", [])
            if(isinstance(outputs, list)):
                for j,out in enumerate(outputs):
                    if(isinstance(out, dict) and out.get("error")):
                        diagnostics.append(Diagnostic("error", "E_BUILD_MANIFEST_OUTPUT_ERROR", f"documents[{i}].outputs[{j}] recorded an output error"))
    return diagnostics


def _validate_release_target(data: dict[str, Any], base: Path, check_paths: bool) -> list[Diagnostic]:
    diagnostics=[]
    if(data.get("config_type")!="sldl.release_check"):
        diagnostics.append(Diagnostic("error", "E_RELEASE_CONFIG_TYPE", "config_type must be sldl.release_check"))
    for key in ("required_files", "forbidden_paths", "forbidden_globs", "config_files", "project_files", "build_project_files", "build_manifest_files", "compile_paths"):
        value=data.get(key)
        if(value is None):
            continue
        if(not isinstance(value, list) or not all(isinstance(item, str) for item in value)):
            diagnostics.append(Diagnostic("error", "E_RELEASE_LIST", f"{key} must be a list of strings"))
    commands=data.get("commands")
    if(commands is not None and not isinstance(commands, list)):
        diagnostics.append(Diagnostic("error", "E_RELEASE_COMMANDS", "commands must be a list"))
    if("compileall" in data and not isinstance(data.get("compileall"), bool)):
        diagnostics.append(Diagnostic("error", "E_RELEASE_COMPILEALL", "compileall must be a boolean"))
    if(check_paths):
        base_dir_value=data.get("base_dir", ".")
        base_dir=Path(base_dir_value)
        actual_base=(base/base_dir).resolve() if(not base_dir.is_absolute()) else base_dir.resolve()
        for key in ("required_files", "forbidden_paths", "forbidden_globs", "config_files", "project_files", "build_project_files", "build_manifest_files", "compile_paths"):
            for item in data.get(key, []) if(isinstance(data.get(key), list)) else []:
                if(not _resolve(actual_base, item).exists() and key not in {"build_manifest_files", "forbidden_paths", "forbidden_globs"}):
                    diagnostics.append(Diagnostic("warning", "W_RELEASE_PATH_MISSING", f"Referenced path for {key} does not exist: {item}"))
        snapshot=data.get("golden_snapshot")
        if(snapshot and not _resolve(actual_base, str(snapshot)).exists()):
            diagnostics.append(Diagnostic("warning", "W_RELEASE_SNAPSHOT_MISSING", f"golden_snapshot does not exist yet: {snapshot}"))
    return diagnostics


def _add_check(manifest: dict[str, Any], category: str, name: str, ok: bool, diagnostics: list[Diagnostic], extra: dict[str, Any] | None = None) -> None:
    item={
        "category": category,
        "name": name,
        "ok": bool(ok),
        "diagnostics": [diag.to_dict() if(hasattr(diag, "to_dict")) else diag for diag in diagnostics],
    }
    if(extra):
        item.update(extra)
    manifest["checks"].append(item)


def _has_failures(diagnostics: list[Diagnostic], warnings_as_errors: bool) -> bool:
    if(any(d.level=="error" for d in diagnostics)):
        return True
    return warnings_as_errors and any(d.level=="warning" for d in diagnostics)


def _resolve(base: Path, value: str | Path) -> Path:
    path=Path(value)
    return path if(path.is_absolute()) else base/path


def _tail(text: str, lines: int = 20) -> str:
    parts=text.splitlines()
    return "\n".join(parts[-lines:])


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False
