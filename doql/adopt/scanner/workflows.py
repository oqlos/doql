"""Workflow scanning — Makefile and Taskfile.yml targets."""
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


def scan_workflows(root: Path, spec: DoqlSpec) -> None:
    """Promote Makefile / Taskfile.yml targets to ``WORKFLOW`` blocks.

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
