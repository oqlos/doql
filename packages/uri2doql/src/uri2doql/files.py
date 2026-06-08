"""Resolve DOQL file path from URI params or cwd."""

from __future__ import annotations

from pathlib import Path

import doql


def resolve_doql_file(file_param: str | None = None, *, start: Path | None = None) -> Path:
    if file_param:
        path = Path(file_param).expanduser()
        if not path.is_absolute():
            base = start or Path.cwd()
            path = (base / path).resolve()
        else:
            path = path.resolve()
        if not path.is_file():
            raise FileNotFoundError(f"DOQL file not found: {path}")
        return path

    detected = doql.detect_doql_file(start or Path.cwd())
    if detected is None:
        raise FileNotFoundError("No app.doql.less/.css/.sass found in current directory")
    return detected
