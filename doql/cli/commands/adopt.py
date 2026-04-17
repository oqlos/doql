"""doql adopt — reverse-engineer an existing project into app.doql.css."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_adopt(args: argparse.Namespace) -> int:
    """Scan *target* directory, produce app.doql.css."""
    from doql.adopt.scanner import scan_project
    from doql.adopt.emitter import emit_css

    target = Path(args.target).resolve()
    if not target.is_dir():
        print(f"❌ Not a directory: {target}", file=sys.stderr)
        return 1

    output = target / (args.output or "app.doql.css")

    if output.exists() and not args.force:
        print(f"⚠️  {output.name} already exists. Use --force to overwrite.")
        return 1

    print(f"🔍 Scanning {target} …")
    spec = scan_project(target)

    # Summary
    ents = len(spec.entities)
    ifaces = len(spec.interfaces)
    dbs = len(spec.databases)
    integ = len(spec.integrations)
    roles = len(spec.roles)
    envs = len(spec.env_refs)
    environments = len(spec.environments)
    workflows = len(spec.workflows)
    deploy_target = spec.deploy.target if spec.deploy else "none"

    print(f"   app:          {spec.app_name} v{spec.version}")
    print(f"   entities:     {ents}")
    print(f"   interfaces:   {ifaces}  ({', '.join(i.name for i in spec.interfaces)})" if ifaces else "   interfaces:   0")
    print(f"   databases:    {dbs}  ({', '.join(d.name for d in spec.databases)})" if dbs else "   databases:    0")
    print(f"   integrations: {integ}  ({', '.join(i.name for i in spec.integrations)})" if integ else "   integrations: 0")
    print(f"   workflows:    {workflows}  ({', '.join(w.name for w in spec.workflows[:5])}{' ...' if workflows > 5 else ''})" if workflows else "   workflows:    0")
    print(f"   roles:        {roles}")
    print(f"   environments: {environments}  ({', '.join(e.name for e in spec.environments)})" if environments else "   environments: 0")
    print(f"   env vars:     {envs}")
    print(f"   deploy:       {deploy_target}")
    print()

    try:
        emit_css(spec, output)
    except Exception as exc:  # noqa: BLE001 — surface any render error
        print(f"❌ Failed to render {output.name}: {exc}", file=sys.stderr)
        # Remove empty/partial output to avoid misleading users
        try:
            if output.exists() and output.stat().st_size == 0:
                output.unlink()
        except OSError:
            pass
        return 1

    if not output.exists() or output.stat().st_size == 0:
        print(f"❌ {output.name} was not written (empty output).", file=sys.stderr)
        return 1

    print(f"✅ Written → {output}")
    return 0
