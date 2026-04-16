"""Example local plugin: generates project statistics."""
import pathlib


def generate(spec, env_vars, out: pathlib.Path, project_root: pathlib.Path):
    stats = {
        "app": spec.app_name,
        "version": spec.version,
        "entities": len(spec.entities),
        "fields_total": sum(len(e.fields) for e in spec.entities),
        "interfaces": len(spec.interfaces),
        "workflows": len(spec.workflows),
        "documents": len(spec.documents),
        "reports": len(spec.reports),
        "integrations": len(spec.integrations),
        "roles": len(spec.roles),
        "languages": spec.languages,
    }
    import json
    (out / "stats.json").write_text(json.dumps(stats, indent=2, ensure_ascii=False))
