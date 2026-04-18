"""Workflow scanning — Makefile, Taskfile.yml, and Python CLI commands."""
from __future__ import annotations

import re
from pathlib import Path

from ...parsers.models import DoqlSpec, Workflow, WorkflowStep
from .utils import load_yaml

# Targets that are *meta* scaffolding, not user-facing workflows. Excluding
# them keeps the generated ``workflow[...]`` section focused on meaningful
# automation (build/test/deploy/lint/...).
_MAKEFILE_SKIP_TARGETS = {
    "all", "default", ".phony", ".default", "help",
}

# CLI commands that should become workflows automatically
_CLI_WORKFLOW_COMMANDS = {
    "analyze": {"tools": "code2llm,redup,vallm", "desc": "Run project analysis tools"},
    "test": {"desc": "Run test suite"},
    "lint": {"desc": "Run linting"},
    "format": {"desc": "Format code"},
    "build": {"desc": "Build project"},
    "deploy": {"desc": "Deploy application"},
}


def scan_workflows(root: Path, spec: DoqlSpec) -> None:
    """Promote Makefile / Taskfile.yml targets and Python CLI commands to ``WORKFLOW`` blocks.

    Workflows detected here are *non-authoritative* — they mirror the shell
    automation the project already has so that a downstream ``doql build``
    can regenerate equivalent scripts. Each target becomes a ``Workflow``
    with the command lines captured as ``run cmd=...`` steps.
    """
    makefile = root / "Makefile"
    if makefile.exists():
        _extract_makefile_workflows(makefile, spec)

    for taskfile_name in ("Taskfile.yml", "Taskfile.yaml"):
        tf_path = root / taskfile_name
        if tf_path.exists():
            _extract_taskfile_workflows(tf_path, spec)
            break

    # Scan Python CLI commands for workflow candidates
    _extract_python_cli_workflows(root, spec)


# Makefile target regex - see _extract_makefile_workflows for details
_TARGET_RE = re.compile(
    r"^([a-zA-Z_][a-zA-Z0-9_-]*)[ \t]*:(?!=)[ \t]*([^\n]*)\n((?:\t[^\n]+\n?)*)",
    re.MULTILINE,
)


def _is_valid_target(name: str, deps_raw: str, seen: set[str]) -> bool:
    """Validate that a target name is acceptable (not skip target, not seen, not var)."""
    if name.startswith(".") or name.lower() in _MAKEFILE_SKIP_TARGETS:
        return False
    if name in seen:
        return False
    if deps_raw.lstrip().startswith("="):
        return False
    return True


def _build_steps_from_body(body: str, deps_raw: str) -> list[WorkflowStep]:
    """Build workflow steps from Makefile command body and dependencies."""
    steps: list[WorkflowStep] = []
    for line in body.splitlines():
        cmd = line.strip()
        if cmd.startswith("@"):
            cmd = cmd[1:]
        if cmd:
            steps.append(WorkflowStep(action="run", params={"cmd": cmd}))
    # Promote prerequisites to explicit depend steps
    deps = _parse_makefile_deps(deps_raw)
    if deps and not steps:
        for dep in deps:
            steps.append(WorkflowStep(action="depend", params={"target": dep}))
    return steps


def _create_workflow(name: str, steps: list[WorkflowStep]) -> Workflow | None:
    """Create a Workflow if steps exist, otherwise return None."""
    if not steps:
        return None
    return Workflow(name=name, trigger="manual", steps=steps)


def _extract_makefile_workflows(path: Path, spec: DoqlSpec) -> None:
    """Parse a Makefile into :class:`Workflow` entries."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return

    seen: set[str] = {w.name for w in spec.workflows}

    for match in _TARGET_RE.finditer(content):
        name = match.group(1)
        deps_raw = match.group(2)
        body = match.group(3)

        if not _is_valid_target(name, deps_raw, seen):
            continue

        steps = _build_steps_from_body(body, deps_raw)
        workflow = _create_workflow(name, steps)
        if workflow:
            spec.workflows.append(workflow)
            seen.add(name)


def _parse_makefile_deps(deps_raw: str) -> list[str]:
    """Split the ``deps`` portion of ``target: dep1 dep2 ## comment``.

    Strips trailing ``## help`` comments and filters out dot-targets.
    """
    text = deps_raw.split("#", 1)[0]
    return [
        tok for tok in text.split()
        if tok and not tok.startswith(".")
    ]


def _build_taskfile_steps(task: dict) -> list[WorkflowStep]:
    """Build workflow steps from Taskfile task commands."""
    steps: list[WorkflowStep] = []
    for cmd in task.get("cmds") or []:
        if isinstance(cmd, str) and cmd.strip():
            steps.append(WorkflowStep(action="run", params={"cmd": cmd.strip()}))
    return steps


def _extract_taskfile_schedule(task: dict) -> str | None:
    """Extract schedule from Taskfile task if present."""
    schedule = task.get("schedule")
    return schedule if isinstance(schedule, str) else None


def _extract_taskfile_workflows(path: Path, spec: DoqlSpec) -> None:
    """Parse a Taskfile.yml into :class:`Workflow` entries."""
    data = load_yaml(path)
    if not data:
        return
    tasks = data.get("tasks") or {}
    if not isinstance(tasks, dict):
        return

    seen: set[str] = {w.name for w in spec.workflows}
    for task_name, task in tasks.items():
        if not isinstance(task, dict):
            continue
        if task_name in seen:
            continue

        steps = _build_taskfile_steps(task)
        schedule = _extract_taskfile_schedule(task)

        if not steps and not schedule:
            continue

        spec.workflows.append(Workflow(
            name=str(task_name),
            trigger="schedule" if schedule else "manual",
            schedule=schedule,
            steps=steps,
        ))
        seen.add(str(task_name))


def _extract_python_cli_workflows(root: Path, spec: DoqlSpec) -> None:
    """Scan Python CLI source files for click commands and create workflows.

    Detects commands like 'analyze', 'test', 'build' from CLI modules and
    creates corresponding workflow definitions that run these commands.
    """
    seen: set[str] = {w.name for w in spec.workflows}
    
    # Find CLI Python files
    cli_candidates: list[Path] = []
    
    # Common CLI file patterns
    for pattern in ["cli.py", "cli/*.py", "commands/*.py", "cmd/*.py"]:
        if "*" in pattern:
            parent, _ = pattern.split("/*")
            if (root / parent).is_dir():
                cli_candidates.extend((root / parent).rglob("*.py"))
        else:
            if (root / pattern).exists():
                cli_candidates.append(root / pattern)
    
    # Also check inside package directories (e.g., sumd/cli.py)
    for pkg_dir in root.iterdir():
        if pkg_dir.is_dir() and not pkg_dir.name.startswith((".", "_")):
            cli_file = pkg_dir / "cli.py"
            if cli_file.exists():
                cli_candidates.append(cli_file)
    
    # Detect CLI command name from pyproject.toml scripts
    cli_command = None
    pyproj = root / "pyproject.toml"
    if pyproj.exists():
        try:
            import tomllib
        except ImportError:
            import tomli as tomllib  # type: ignore[no-redef]
        try:
            with open(pyproj, "rb") as f:
                data = tomllib.load(f)
            scripts = data.get("project", {}).get("scripts", {})
            for name in scripts.keys():
                if name not in ("api", "server"):
                    cli_command = name
                    break
        except Exception:
            pass
    
    if not cli_command:
        cli_command = root.name  # fallback to directory name
    
    # Scan each CLI file for click commands
    for cli_file in set(cli_candidates):  # deduplicate
        try:
            content = cli_file.read_text(encoding="utf-8")
        except OSError:
            continue
        
        # Check if this is a click-based CLI
        if "click" not in content.lower():
            continue
        
        # Find @click.command() decorated functions
        # Pattern matches: @cli.command() followed by other decorators then def
        command_pattern = re.compile(
            r'@\w+\.command(?:\([^)]*\))?[\r\n]+(?:[^\r\n]*[\r\n]+)*?def\s+([a-z_][a-z0-9_]*)',
            re.MULTILINE | re.IGNORECASE
        )
        
        for match in command_pattern.finditer(content):
            cmd_name = match.group(1)
            
            # Skip common internal commands
            if cmd_name in ("main", "cli", "run", "start"):
                continue
            
            # Skip if already have this workflow
            if cmd_name in seen:
                continue
            
            # Check if this command should become a workflow
            if cmd_name in _CLI_WORKFLOW_COMMANDS:
                wf_config = _CLI_WORKFLOW_COMMANDS[cmd_name]
                
                steps: list[WorkflowStep] = []
                tools = wf_config.get("tools", "")
                
                # Build command
                if cmd_name == "analyze":
                    cmd_str = f"echo \"🔬 Running project analysis...\""
                    steps.append(WorkflowStep(action="run", params={"cmd": cmd_str}))
                    cmd_str = f"{cli_command} analyze . --tools {tools}"
                    steps.append(WorkflowStep(action="run", params={"cmd": cmd_str}))
                else:
                    cmd_str = f"{cli_command} {cmd_name}"
                    steps.append(WorkflowStep(action="run", params={"cmd": cmd_str}))
                
                spec.workflows.append(Workflow(
                    name=cmd_name,
                    trigger="manual",
                    steps=steps,
                ))
                seen.add(cmd_name)
