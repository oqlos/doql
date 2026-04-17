"""Lockfile operations for selective rebuild (sync command)."""
from __future__ import annotations

import hashlib
import json
import datetime
import pathlib
from typing import Optional

from .. import __version__
from .context import BuildContext


def spec_section_hashes(spec, ctx: BuildContext) -> dict:
    """Compute per-section hashes for diff detection."""
    def _h(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    hashes = {
        "spec_file": hashlib.sha256(ctx.doql_file.read_bytes()).hexdigest(),
    }
    
    # Entity hashes
    for e in spec.entities:
        key = f"entity:{e.name}"
        fields_str = "|".join(f"{f.name}:{f.type}:{f.required}:{f.unique}:{f.ref}" for f in e.fields)
        hashes[key] = _h(fields_str)
    
    # Interface hashes
    for i in spec.interfaces:
        key = f"interface:{i.name}"
        pages_str = "|".join(p.name for p in i.pages)
        hashes[key] = _h(f"{i.type}:{pages_str}")
    
    # Document hashes
    for d in spec.documents:
        hashes[f"document:{d.name}"] = _h(f"{d.type}:{d.template}:{d.output}")
    
    # Report hashes
    for r in spec.reports:
        hashes[f"report:{r.name}"] = _h(f"{r.schedule}:{r.output}:{r.template}")
    
    # Integration hashes
    for ig in spec.integrations:
        hashes[f"integration:{ig.name}"] = _h(ig.name)
    
    # Roles
    if spec.roles:
        hashes["roles"] = _h("|".join(r.name if hasattr(r, 'name') else str(r) for r in spec.roles))
    
    # Languages
    if spec.languages:
        hashes["languages"] = _h("|".join(spec.languages))
    
    return hashes


def read_lockfile(ctx: BuildContext) -> Optional[dict]:
    """Read and parse lockfile if it exists."""
    lockfile = ctx.root / "doql.lock"
    if not lockfile.exists():
        return None
    try:
        return json.loads(lockfile.read_text())
    except (json.JSONDecodeError, OSError):
        return None


def diff_sections(old_hashes: dict, new_hashes: dict) -> dict:
    """Return dict of changed/added/removed section keys."""
    added = {k: new_hashes[k] for k in new_hashes if k not in old_hashes}
    removed = {k: old_hashes[k] for k in old_hashes if k not in new_hashes}
    changed = {k: new_hashes[k] for k in new_hashes if k in old_hashes and old_hashes[k] != new_hashes[k]}
    return {"added": added, "removed": removed, "changed": changed}


def write_lockfile(spec, ctx: BuildContext) -> None:
    """Write current spec hashes to lockfile."""
    from .lockfile import spec_section_hashes
    lockfile = ctx.root / "doql.lock"
    hashes = spec_section_hashes(spec, ctx)
    content = {
        "version": "2",
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
        "doql_version": __version__,
        "sections": hashes,
    }
    lockfile.write_text(json.dumps(content, indent=2))
