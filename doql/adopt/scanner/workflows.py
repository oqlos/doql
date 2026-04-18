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


def _extract_makefile_workflows(path: Path, spec: DoqlSpec) -> None:
    """Parse a Makefile into :class:`Workflow` entries."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return

    # Match:  target: [deps]\n\t<cmds...>
    # ``[ \t]*`` — horizontal whitespace only. Using ``\s*`` here would
    # consume the newline + tab and slurp the first command into the ``deps``
    # capture group.
    # ``(?!=)`` — negative lookahead: reject ``VAR := value`` / ``VAR ?= value``
    # variable assignments, which otherwise match because ``:`` is part of the
    # operator. Plain ``VAR = value`` is already rejected (no colon).
    target_re = re.compile(
        r"^([a-zA-Z_][a-zA-Z0-9_-]*)[ \t]*:(?!=)[ \t]*([^\n]*)\n((?:\t[^\n]+\n?)*)",
        re.MULTILINE,
    )
    seen: set[str] = {w.name for w in spec.workflows}

    for match in target_re.finditer(content):
        name = match.group(1)
        deps_raw = match.group(2)
        body = match.group(3)
        if name.startswith(".") or name.lower() in _MAKEFILE_SKIP_TARGETS:
            continue
        if name in seen:
            continue

        # Second-line defence: reject any capture where the "deps" looks like
        # a variable value (contains ``=`` before whitespace). Covers the
        # odd ``VAR=value`` style some Makefiles use without a space.
        if deps_raw.lstrip().startswith("="):
            continue

        steps: list[WorkflowStep] = []
        for line in body.splitlines():
            cmd = line.strip()
            if cmd.startswith("@"):
                cmd = cmd[1:]
            if cmd:
                steps.append(WorkflowStep(action="run", params={"cmd": cmd}))

        # Promote prerequisites to explicit ``depend`` steps so a target like
        # ``install: install-backend install-frontend`` round-trips as a
        # meaningful workflow rather than an empty block.
        deps = _parse_makefile_deps(deps_raw)
        if deps and not steps:
            for dep in deps:
                steps.append(WorkflowStep(action="depend", params={"target": dep}))

        if not steps:
            # Truly empty target (no deps, no commands) — skip.
            continue

        spec.workflows.append(Workflow(
            name=name,
            trigger="manual",
            steps=steps,
        ))
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

        steps: list[WorkflowStep] = []
        for cmd in task.get("cmds") or []:
            if isinstance(cmd, str) and cmd.strip():
                steps.append(WorkflowStep(action="run", params={"cmd": cmd.strip()}))
        # Taskfile schedule (cron string) → workflow schedule
        schedule = task.get("schedule") if isinstance(task.get("schedule"), str) else None

        if not steps and not schedule:
            continue

        spec.workflows.append(Workflow(
            name=str(task_name),
            trigger="schedule" if schedule else "manual",
            schedule=schedule,
            steps=steps,
        ))
        seen.add(str(task_name))
