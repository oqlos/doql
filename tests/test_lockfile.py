"""Tests for typed selective-build lockfile boundaries."""
from __future__ import annotations

import json

from doql.cli.context import BuildContext
from doql.cli.lockfile import diff_sections, read_lockfile, spec_section_hashes, write_lockfile
from doql.parsers.models import DoqlSpec, Entity, EntityField


def _context(tmp_path) -> BuildContext:
    spec_file = tmp_path / "app.doql"
    spec_file.write_text('APP: "Lock Test"\n', encoding="utf-8")
    return BuildContext(
        root=tmp_path,
        doql_file=spec_file,
        env_file=tmp_path / ".env",
        build_dir=tmp_path / "build",
    )


def test_lockfile_round_trip_and_section_diff(tmp_path):
    context = _context(tmp_path)
    spec = DoqlSpec(
        app_name="Lock Test",
        entities=[Entity(name="Employee", fields=[EntityField(name="id", type="uuid")])],
        languages=["pl", "en"],
    )

    hashes = spec_section_hashes(spec, context)
    assert hashes["spec_file"]
    assert hashes["entity:Employee"]
    assert hashes["languages"]

    write_lockfile(spec, context)
    lock = read_lockfile(context)
    assert lock is not None
    assert lock["version"] == "2"
    assert lock["sections"] == hashes

    changed = diff_sections(hashes, {**hashes, "languages": "new", "role:admin": "added"})
    assert changed == {
        "added": {"role:admin": "added"},
        "removed": {},
        "changed": {"languages": "new"},
    }


def test_read_lockfile_rejects_non_mapping_root(tmp_path):
    context = _context(tmp_path)
    lockfile = tmp_path / "doql.lock"

    lockfile.write_text("[]", encoding="utf-8")
    assert read_lockfile(context) is None

    lockfile.write_text(json.dumps({"valid": True}), encoding="utf-8")
    assert read_lockfile(context) == {"valid": True}
