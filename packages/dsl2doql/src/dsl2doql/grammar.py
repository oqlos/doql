"""Text DSL → dict."""

from __future__ import annotations

import shlex
from typing import Any


def split_command(line: str) -> list[str]:
    line = line.strip()
    if not line or line.startswith("#"):
        return []
    try:
        return shlex.split(line, posix=True)
    except ValueError:
        return line.split()


def pick_flag(tokens: list[str], flag: str) -> str | None:
    if flag in tokens:
        idx = tokens.index(flag)
        if idx + 1 < len(tokens):
            return tokens[idx + 1]
    return None


def parse_line(line: str) -> dict[str, Any] | None:
    tokens = split_command(line)
    if not tokens:
        return None
    verb = tokens[0].upper()
    rest = tokens[1:]
    cmd: dict[str, Any] = {"verb": verb}

    if verb == "QUERY":
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
        if f := pick_flag(rest, "FORMAT"):
            cmd["format"] = f.lower()
    elif verb == "VALIDATE":
        cmd["path"] = rest[0] if rest else ""
    elif verb == "RESOLVE":
        cmd["text"] = " ".join(rest)
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb in {"PATCH", "UPDATE", "REPLACE"}:
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "WITH"):
            cmd["with_path"] = f
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb == "APPEND":
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "WITH"):
            cmd["with_path"] = f
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb == "MATERIALIZE":
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "TO") or pick_flag(rest, "DEST"):
            cmd["dest"] = f
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb == "APPLY":
        cmd["target"] = rest[0] if rest else ""
        if f := pick_flag(rest, "MODE"):
            cmd["mode"] = f.lower()
        if f := pick_flag(rest, "TO") or pick_flag(rest, "DEST"):
            cmd["dest"] = f
        if f := pick_flag(rest, "WITH"):
            cmd["with_path"] = f
        if f := pick_flag(rest, "FILE"):
            cmd["file"] = f
    elif verb == "GENERATE":
        cmd["text"] = rest[0].strip('"').strip("'") if rest else ""
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
    elif verb == "CONVERT":
        cmd["source"] = rest[0] if rest else ""
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
    elif verb == "ADOPT":
        cmd["root"] = rest[0] if rest else "."
        if f := pick_flag(rest, "OUT"):
            cmd["out"] = f
    else:
        cmd["args"] = rest
    return cmd


def to_text(cmd: dict[str, Any]) -> str:
    verb = str(cmd.get("verb", "")).upper()
    parts = [verb]
    for key, flag in (
        ("target", None),
        ("path", None),
        ("text", None),
        ("source", None),
        ("root", None),
    ):
        if val := cmd.get(key):
            parts.append(f'"{val}"' if " " in str(val) else str(val))
    for key, flag in (("file", "FILE"), ("format", "FORMAT"), ("with_path", "WITH"), ("dest", "TO"), ("out", "OUT"), ("mode", "MODE")):
        if val := cmd.get(key):
            parts.extend([flag or key.upper(), str(val)])
    return " ".join(parts)
