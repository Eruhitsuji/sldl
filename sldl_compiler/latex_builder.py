from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import re
import shlex
import subprocess
from typing import Any


DEFAULT_LATEX_BUILD_CONFIG={
    "config_type": "sldl.latex_build",
    "description": "Default LaTeX PDF build configuration: platex twice, then dvipdfmx.",
    "version": "0.12.1",
    "dry_run": False,
    "capture_output": False,
    "timeout_sec": 120,
    "work_dir": "{tex_dir}",
    "output_dir": "{tex_dir}",
    "job_name": "{tex_stem}",
    "stop_on_error": True,
    "show_output": False,
    "engine": {
        "command": "platex",
        "passes": 2,
        "args": [
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-output-directory", "{output_dir}",
            "{tex_path}",
        ],
    },
    "dvi_to_pdf": {
        "enabled": True,
        "command": "dvipdfmx",
        "args": ["-o", "{pdf_path}", "{dvi_path}"],
    },
    "cleanup": {
        "enabled": False,
        "on_success": False,
        "on_error": False,
        "extensions": [".aux", ".log", ".dvi", ".toc", ".out"],
        "files": [],
    },
}


@dataclass
class LatexBuildStepResult:
    name: str
    command: list[str]
    cwd: str
    returncode: int | None = None
    skipped: bool = False
    stdout_tail: str = ""
    stderr_tail: str = ""
    warnings: list[str] = field(default_factory=list)
    warning_count: int = 0
    error_summary: str = ""
    log_path: str = ""


@dataclass
class LatexBuildResult:
    tex_path: Path
    pdf_path: Path
    config_path: Path | None
    dry_run: bool
    success: bool
    steps: list[LatexBuildStepResult] = field(default_factory=list)
    cleanup_removed: list[str] = field(default_factory=list)
    error: str | None = None
    warnings: list[str] = field(default_factory=list)
    warning_count: int = 0

    def to_manifest(self) -> dict[str, Any]:
        data={
            "tex_path": str(self.tex_path),
            "pdf_path": str(self.pdf_path),
            "config_path": str(self.config_path) if(self.config_path) else None,
            "dry_run": self.dry_run,
            "success": self.success,
            "steps": [
                {
                    "name": step.name,
                    "command": step.command,
                    "cwd": step.cwd,
                    "returncode": step.returncode,
                    "skipped": step.skipped,
                    "stdout_tail": step.stdout_tail,
                    "stderr_tail": step.stderr_tail,
                    "warnings": step.warnings,
                    "warning_count": step.warning_count,
                    "error_summary": step.error_summary,
                    "log_path": step.log_path,
                }
                for step in self.steps
            ],
            "cleanup_removed": self.cleanup_removed,
            "warnings": self.warnings,
            "warning_count": self.warning_count,
        }
        if(self.error):
            data["error"]=self.error
        return data


def load_latex_build_config(config_path: str | Path | None = None) -> tuple[dict[str, Any], Path | None]:
    if(config_path is None):
        return _deepcopy_json(DEFAULT_LATEX_BUILD_CONFIG), None
    path=Path(config_path)
    data=json.loads(path.read_text(encoding="utf-8"))
    if(not isinstance(data, dict)):
        raise ValueError("LaTeX build config root must be a JSON object.")
    merged=_deepcopy_json(DEFAULT_LATEX_BUILD_CONFIG)
    _deep_update(merged, data)
    return merged, path


def build_latex_pdf(
    tex_path: str | Path,
    pdf_path: str | Path | None = None,
    config_path: str | Path | None = None,
    dry_run: bool | None = None,
) -> LatexBuildResult:
    tex_abs=Path(tex_path).resolve()
    if(not tex_abs.exists()):
        return LatexBuildResult(tex_abs, Path(pdf_path).resolve() if(pdf_path) else tex_abs.with_suffix(".pdf"), Path(config_path).resolve() if(config_path) else None, bool(dry_run), False, error=f"TeX file does not exist: {tex_abs}")

    config,loaded_config_path=load_latex_build_config(config_path)
    loaded_config_path=loaded_config_path.resolve() if(loaded_config_path) else None
    base_dir=(loaded_config_path.parent if(loaded_config_path) else tex_abs.parent)

    first_vars=_initial_variables(tex_abs, tex_abs.parent, tex_abs.parent, None, config)
    work_dir=_resolve_template_path(_config_string(config, "work_dir", "{tex_dir}"), first_vars, base_dir)
    out_dir=_resolve_template_path(_config_string(config, "output_dir", "{tex_dir}"), first_vars, work_dir)
    job_name=_format_text(_config_string(config, "job_name", "{tex_stem}"), first_vars)
    default_pdf=out_dir/(job_name+".pdf")
    pdf_vars=dict(first_vars)
    pdf_vars.update({
        "work_dir": str(work_dir),
        "output_dir": str(out_dir),
        "out_dir": str(out_dir),
        "job_name": job_name,
    })
    if(pdf_path is not None):
        pdf_abs=Path(pdf_path).resolve()
    elif(isinstance(config.get("pdf_path"), str) and str(config.get("pdf_path")).strip()):
        pdf_abs=_resolve_template_path(str(config["pdf_path"]), pdf_vars, work_dir)
    else:
        pdf_abs=default_pdf

    variables=_initial_variables(tex_abs, work_dir, out_dir, pdf_abs, config)
    dvi_path=out_dir/(job_name+".dvi")
    variables.update({"dvi_path": str(dvi_path), "dvi_abs_path": str(dvi_path.resolve())})

    effective_dry_run=bool(config.get("dry_run", False)) if(dry_run is None) else dry_run
    stop_on_error=bool(config.get("stop_on_error", True))
    show_output=bool(config.get("show_output", False))

    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_abs.parent.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    result=LatexBuildResult(tex_abs, pdf_abs, loaded_config_path, effective_dry_run, success=True)
    steps=_build_steps(config)
    if(not steps):
        result.success=False
        result.error="No LaTeX build steps configured."
        return result

    for step in steps:
        name=str(step.get("name") or step.get("command") or "latex-step")
        command_text=step.get("command")
        if(not isinstance(command_text, str) or not command_text.strip()):
            result.success=False
            result.error=f"Invalid command in step: {name}"
            return result
        args=step.get("args", [])
        if(isinstance(args, str)):
            args=shlex.split(args)
        if(not isinstance(args, list)):
            result.success=False
            result.error=f"args must be a list or string in step: {name}"
            return result
        command=[_format_text(command_text, variables)]+[_format_text(str(arg), variables) for arg in args]
        step_cwd=work_dir
        if(isinstance(step.get("cwd"), str) and step.get("cwd").strip()):
            step_cwd=_resolve_template_path(str(step.get("cwd")), variables, work_dir)
            step_cwd.mkdir(parents=True, exist_ok=True)
        repeat=max(1, int(step.get("repeat", 1) or 1))
        for index in range(repeat):
            step_name=name if(repeat==1) else f"{name} ({index+1}/{repeat})"
            if(effective_dry_run):
                result.steps.append(LatexBuildStepResult(step_name, command, str(step_cwd), returncode=0, skipped=True))
                continue
            capture_output=bool(step.get("capture_output", config.get("capture_output", False)))
            timeout_sec=_timeout_value(step.get("timeout_sec", config.get("timeout_sec")))
            log_path=out_dir/(_safe_step_log_name(job_name, step_name)+".log")
            try:
                if(capture_output):
                    completed=subprocess.run(command, cwd=str(step_cwd), text=True, capture_output=True, timeout=timeout_sec)
                    stdout=completed.stdout or ""
                    stderr=completed.stderr or ""
                    combined=stdout+"\n"+stderr
                else:
                    with log_path.open("w", encoding="utf-8", errors="replace") as handle:
                        completed=subprocess.run(command, cwd=str(step_cwd), text=True, stdout=handle, stderr=subprocess.STDOUT, timeout=timeout_sec)
                    combined=log_path.read_text(encoding="utf-8", errors="replace") if(log_path.exists()) else ""
                    stdout=combined
                    stderr=""
            except subprocess.TimeoutExpired:
                step_result=LatexBuildStepResult(
                    step_name,
                    command,
                    str(step_cwd),
                    returncode=None,
                    stdout_tail="",
                    stderr_tail="",
                    warnings=[],
                    warning_count=0,
                    error_summary=f"step timed out after {timeout_sec} seconds" if(timeout_sec) else "step timed out",
                    log_path=str(log_path) if(log_path.exists()) else "",
                )
                result.steps.append(step_result)
                result.success=False
                result.error=f"LaTeX build step timed out: {step_name}"
                if(stop_on_error):
                    _cleanup(config, variables, result, success=False)
                    return result
                continue
            step_warnings=_extract_latex_warnings(combined)
            step_result=LatexBuildStepResult(
                step_name,
                command,
                str(step_cwd),
                returncode=completed.returncode,
                stdout_tail=_tail(stdout),
                stderr_tail=_tail(stderr),
                warnings=step_warnings,
                warning_count=len(step_warnings),
                error_summary=_extract_latex_error_summary(combined),
                log_path=str(log_path) if((not capture_output) and log_path.exists()) else "",
            )
            result.steps.append(step_result)
            # Aggregate only the last pass of a repeated LaTeX step.
            # Earlier passes often emit transient citation / rerun warnings
            # that are resolved by the final pass, while each step still keeps
            # its own warnings in the manifest for debugging.
            if(index==repeat-1):
                result.warnings.extend(step_warnings)
                result.warning_count+=len(step_warnings)
            if(show_output and stdout):
                print(stdout, end="")
            if(show_output and stderr):
                print(stderr, end="")
            if(completed.returncode!=0):
                result.success=False
                result.error=f"LaTeX build step failed: {step_name} (exit {completed.returncode})"
                if(step_result.error_summary):
                    result.error+=f": {step_result.error_summary}"
                if(stop_on_error):
                    _cleanup(config, variables, result, success=False)
                    return result
    if(not effective_dry_run and not pdf_abs.exists()):
        result.success=False
        result.error=f"PDF was not created: {pdf_abs}"
    _cleanup(config, variables, result, success=result.success)
    return result


def _build_steps(config: dict[str, Any]) -> list[dict[str, Any]]:
    raw_steps=config.get("steps")
    if(isinstance(raw_steps, list) and raw_steps):
        return [step for step in raw_steps if(isinstance(step, dict))]
    steps=[]
    engine=config.get("engine", {})
    if(isinstance(engine, dict) and engine.get("enabled", True)):
        steps.append({
            "name": engine.get("name", "latex"),
            "command": engine.get("command", "platex"),
            "args": engine.get("args", []),
            "repeat": engine.get("passes", 1),
            "cwd": engine.get("cwd"),
        })
    dvi_to_pdf=config.get("dvi_to_pdf", {})
    if(isinstance(dvi_to_pdf, dict) and dvi_to_pdf.get("enabled", True)):
        steps.append({
            "name": dvi_to_pdf.get("name", "dvipdfmx"),
            "command": dvi_to_pdf.get("command", "dvipdfmx"),
            "args": dvi_to_pdf.get("args", ["-o", "{pdf_path}", "{dvi_path}"]),
            "repeat": dvi_to_pdf.get("passes", 1),
            "cwd": dvi_to_pdf.get("cwd"),
        })
    return steps


def _cleanup(config: dict[str, Any], variables: dict[str, str], result: LatexBuildResult, success: bool) -> None:
    cleanup=config.get("cleanup", {})
    if(not isinstance(cleanup, dict) or not cleanup.get("enabled", False)):
        return
    if(success and not cleanup.get("on_success", True)):
        return
    if((not success) and not cleanup.get("on_error", False)):
        return
    paths=[]
    extensions=cleanup.get("extensions", [])
    if(isinstance(extensions, list)):
        for ext in extensions:
            if(not isinstance(ext, str) or not ext.startswith(".")):
                continue
            paths.append(Path(variables["output_dir"])/(variables["job_name"]+ext))
    files=cleanup.get("files", [])
    if(isinstance(files, list)):
        for item in files:
            if(isinstance(item, str)):
                paths.append(Path(_format_text(item, variables)))
    for path in paths:
        try:
            if(path.exists() and path.is_file()):
                path.unlink()
                result.cleanup_removed.append(str(path))
        except OSError:
            pass


def _initial_variables(tex_path: Path, work_dir: Path, output_dir: Path, pdf_path: Path | None, config: dict[str, Any]) -> dict[str, str]:
    variables={
        "tex_path": str(tex_path),
        "tex_abs_path": str(tex_path.resolve()),
        "tex_dir": str(tex_path.parent),
        "tex_stem": tex_path.stem,
        "tex_name": tex_path.name,
        "work_dir": str(work_dir),
        "output_dir": str(output_dir),
        "out_dir": str(output_dir),
        "job_name": str(config.get("job_name", "{tex_stem}")) if(config.get("job_name")) else tex_path.stem,
        "pdf_path": str(pdf_path) if(pdf_path) else str(output_dir/(tex_path.stem+".pdf")),
    }
    custom=config.get("variables", {})
    if(isinstance(custom, dict)):
        for key,value in custom.items():
            if(isinstance(key, str)):
                variables[key]=str(value)
    for _ in range(3):
        for key,value in list(variables.items()):
            variables[key]=_format_text(value, variables)
    return variables


def _config_string(config: dict[str, Any], key: str, default: str) -> str:
    value=config.get(key, default)
    return value if(isinstance(value, str) and value.strip()) else default


def _format_text(text: str, variables: dict[str, str]) -> str:
    result=text
    for key,value in variables.items():
        result=result.replace("{"+key+"}", str(value))
    return result


def _resolve_template_path(text: str, variables: dict[str, str], base_dir: Path) -> Path:
    formatted=_format_text(text, variables)
    path=Path(formatted)
    if(path.is_absolute()):
        return path
    return (base_dir/path).resolve()




def _timeout_value(value: Any) -> float | None:
    if(value in {None, "", False}):
        return None
    try:
        numeric=float(value)
    except (TypeError, ValueError):
        return None
    return numeric if(numeric>0) else None


def _safe_step_log_name(job_name: str, step_name: str) -> str:
    safe=re.sub(r"[^A-Za-z0-9_.-]+", "-", f"{job_name}-{step_name}").strip("-")
    return safe or "latex-step"

def _tail(text: str, limit: int = 1600) -> str:
    if(not text):
        return ""
    return text[-limit:]


def _deep_update(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    for key,value in override.items():
        if(isinstance(value, dict) and isinstance(base.get(key), dict)):
            _deep_update(base[key], value)
        else:
            base[key]=value
    return base


def _deepcopy_json(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False))


def _extract_latex_warnings(text: str, limit: int = 20) -> list[str]:
    warnings=[]
    if(not text):
        return warnings
    for line in text.splitlines():
        stripped=line.strip()
        if(not stripped):
            continue
        is_warning=(
            "LaTeX Warning:" in stripped
            or ("Package " in stripped and " Warning:" in stripped)
            or "Overfull \\hbox" in stripped
            or "Underfull \\hbox" in stripped
        )
        if(is_warning):
            if(len(stripped)>300):
                stripped=stripped[:297]+"..."
            warnings.append(stripped)
            if(len(warnings)>=limit):
                break
    return warnings


def _extract_latex_error_summary(text: str) -> str:
    if(not text):
        return ""
    lines=text.splitlines()
    for index,line in enumerate(lines):
        stripped=line.strip()
        if(stripped.startswith("!")):
            context=[]
            for item in lines[index:index+4]:
                item=item.strip()
                if(item):
                    context.append(item)
            return " / ".join(context)[:800]
    for line in lines:
        stripped=line.strip()
        if(" Error:" in stripped or "Fatal error" in stripped or "Emergency stop" in stripped):
            return stripped[:800]
    return ""
