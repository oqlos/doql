"""Lockfile operations for selective rebuild (sync command)."""
from __future__ import annotations

import hashlib
import json
import datetime
from collections.abc import Callable, Iterable
from typing import Any, cast

from .. import __version__
from ..parsers.models import DoqlSpec
from .context import BuildContext


def _simple_items_hash(
    items: Iterable[Any],
    key_prefix: str,
    val_fn: Callable[[Any], str],
    h_fn: Callable[[str], str],
) -> dict[str, str]:
    """Hash a flat list of spec items into {key_prefix:name -> hash} entries."""
    return {f"{key_prefix}:{item.name}": h_fn(val_fn(item)) for item in items}


def spec_section_hashes(spec: DoqlSpec, ctx: BuildContext) -> dict[str, str]:
    """Compute per-section hashes for diff detection."""
    def _h(data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    hashes = {
        "spec_file": hashlib.sha256(ctx.doql_file.read_bytes()).hexdigest(),
    }

    # Entity hashes
    for e in spec.entities:
        fields_str = "|".join(f"{f.name}:{f.type}:{f.required}:{f.unique}:{f.ref}" for f in e.fields)
        hashes[f"entity:{e.name}"] = _h(fields_str)

    # Interface hashes
    for i in spec.interfaces:
        pages_str = "|".join(p.name for p in i.pages)
        hashes[f"interface:{i.name}"] = _h(f"{i.type}:{pages_str}")

    hashes.update(_simple_items_hash(spec.documents, "document",
                                     lambda d: f"{d.type}:{d.template}:{d.output}", _h))
    hashes.update(_simple_items_hash(spec.reports, "report",
                                     lambda r: f"{r.schedule}:{r.output}:{r.template}", _h))
    hashes.update(_simple_items_hash(spec.integrations, "integration",
                                     lambda ig: ig.name, _h))

    if spec.roles:
        hashes["roles"] = _h("|".join(r.name if hasattr(r, 'name') else str(r) for r in spec.roles))
    if spec.languages:
        hashes["languages"] = _h("|".join(spec.languages))

    return hashes


def read_lockfile(ctx: BuildContext) -> dict[str, Any] | None:
    """Read and parse lockfile if it exists."""
    lockfile = ctx.root / "doql.lock"
    if not lockfile.exists():
        return None
    try:
        data = json.loads(lockfile.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or not all(isinstance(key, str) for key in data):
            return None
        return cast(dict[str, Any], data)
    except (json.JSONDecodeError, OSError):
        return None


def diff_sections(
    old_hashes: dict[str, str],
    new_hashes: dict[str, str],
) -> dict[str, dict[str, str]]:
    """Return dict of changed/added/removed section keys."""
    added = {k: new_hashes[k] for k in new_hashes if k not in old_hashes}
    removed = {k: old_hashes[k] for k in old_hashes if k not in new_hashes}
    changed = {k: new_hashes[k] for k in new_hashes if k in old_hashes and old_hashes[k] != new_hashes[k]}
    return {"added": added, "removed": removed, "changed": changed}


def write_lockfile(spec: DoqlSpec, ctx: BuildContext) -> None:
    """Write current spec hashes to lockfile."""
    lockfile = ctx.root / "doql.lock"
    hashes = spec_section_hashes(spec, ctx)
    content = {
        "version": "2",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00", "Z"),
        "doql_version": __version__,
        "sections": hashes,
    }
    lockfile.write_text(json.dumps(content, indent=2))
