"""Read a project's declared workflows and dependencies, with no device scan.

`doql.drift` answers "does this device match the declaration?" and needs op3 and
an SSH target to do it. A different question comes up whenever something else
runs a project on the project's behalf — a CI job, a scheduler, an agent:

    "I am about to run `python -m pytest -q` here. Is that what this project
    says it runs?"

Answering it needs nothing but the declaration file, so this module keeps that
path free of the device-scan dependencies:

``workflow_commands(source)``
    Map every declared workflow to the commands it runs, already split into
    argument vectors.
``declared_dependencies(source)``
    Map each dependency group (``runtime``, ``test``, …) to its entries.
``command_drift(configured, declared)``
    Report where an external caller's command disagrees with the declaration.
    Extra arguments are not drift: a caller may add to a declared command
    without contradicting it.
"""

from __future__ import annotations

from pathlib import Path
import shlex
from typing import Iterable, Mapping, Sequence

from .parsers import parse_file

__all__ = [
    "command_drift",
    "declared_dependencies",
    "find_declaration",
    "workflow_commands",
]

DECLARATION_NAMES = ("app.doql.less", "app.doql.css", "app.doql.sass")


def find_declaration(directory: Path | None = None) -> Path | None:
    """Locate a project's declaration file, or return None when it has none."""
    base = directory or Path.cwd()
    for name in DECLARATION_NAMES:
        candidate = base / name
        if candidate.is_file():
            return candidate
    return None


def _resolve(source: Path) -> Path | None:
    return find_declaration(source) if source.is_dir() else (source if source.is_file() else None)


def workflow_commands(source: Path) -> dict[str, tuple[tuple[str, ...], ...]]:
    """Map each declared workflow name to its commands as argument vectors.

    `source` may be a declaration file or the directory holding one. A project
    without a declaration yields an empty mapping rather than raising: callers
    routinely run against projects that have not adopted DOQL yet.
    """
    path = _resolve(source)
    if path is None:
        return {}
    spec = parse_file(path)
    commands: dict[str, tuple[tuple[str, ...], ...]] = {}
    for workflow in spec.workflows:
        vectors = []
        for step in workflow.steps:
            command = step.params.get("cmd")
            if not command:
                continue
            try:
                parsed = tuple(shlex.split(str(command)))
            except ValueError:
                continue
            if parsed:
                vectors.append(parsed)
        commands[workflow.name] = tuple(vectors)
    return commands


def declared_dependencies(source: Path) -> dict[str, tuple[str, ...]]:
    """Map each dependency group to its declared entries."""
    path = _resolve(source)
    if path is None:
        return {}
    spec = parse_file(path)
    groups: dict[str, tuple[str, ...]] = {}
    for group, value in spec.dependencies.items():
        entries = tuple(entry.strip() for entry in str(value).split(",") if entry.strip())
        if entries:
            groups[group] = entries
    return groups


def _extends(configured: Sequence[str], declared: Sequence[str]) -> bool:
    """True when `configured` is the declared command plus extra arguments."""
    remaining = iter(configured)
    return all(argument in remaining for argument in declared)


def command_drift(
    configured: Mapping[str, Iterable[Sequence[str]]],
    declared: Mapping[str, Iterable[Sequence[str]]],
) -> tuple[str, ...]:
    """Report where a caller's commands disagree with the declared workflows.

    Both sides map a workflow name to the commands run under it. A workflow the
    caller does not run, or one the project does not declare, is not drift —
    only a direct contradiction is.
    """
    findings = []
    for name, commands in sorted(configured.items()):
        declared_commands = [tuple(command) for command in declared.get(name, ())]
        if not declared_commands:
            continue
        for command in commands:
            vector = tuple(command)
            if not vector or any(_extends(vector, candidate) for candidate in declared_commands):
                continue
            readable = " | ".join(" ".join(candidate) for candidate in declared_commands)
            findings.append(f"{name}: caller runs {' '.join(vector)!r}, declaration says {readable!r}")
    return tuple(findings)
