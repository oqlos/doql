"""Role scanning — from env vars or SQL files."""
from __future__ import annotations

import re
from pathlib import Path

from ...parsers.models import DoqlSpec, Role


def scan_roles(root: Path, spec: DoqlSpec) -> None:
    """Detect roles from env vars or code patterns."""
    env_text = " ".join(spec.env_refs).upper()
    if "ADMIN" in env_text or "ROLE" in env_text:
        spec.roles.append(Role(name="admin", permissions=["*"]))

    # Check for role definitions in SQL
    for sql in root.rglob("*.sql"):
        if ".venv" in str(sql) or "venv" in str(sql):
            continue
        try:
            text = sql.read_text().lower()
        except Exception:
            continue
        if "role" in text:
            for m in re.finditer(r"'(admin|user|editor|manager|operator|viewer)'", text):
                role_name = m.group(1)
                if not any(r.name == role_name for r in spec.roles):
                    spec.roles.append(Role(name=role_name))
