"""Playground build function — executed inside Pyodide.

This file is fetched at runtime by pyodide-bridge.js and executed via
``pyodide.runPython()``.  The ``build`` name at module scope is picked up
as the callable entry point.
"""

import json
from doql import parser as _parser


_DEFAULT_ENV = {
    "DOMAIN": "app.localhost",
    "HOST": "localhost",
    "API_HOST": "api.localhost",
    "WEB_HOST": "web.localhost",
    "DB_HOST": "db.localhost",
    "REDIS_HOST": "redis.localhost",
    "SMTP_HOST": "smtp.localhost",
    "TRAEFIK_HOST": "traefik.localhost",
    "LE_EMAIL": "ops@localhost",
    "DATABASE_URL": "sqlite:///./data/app.db",
}


def _collect_parse_errors(spec, diags):
    """Append parse-recovery errors to *diags*."""
    for pe in spec.parse_errors or []:
        diags.append({
            "severity": "error",
            "path": getattr(pe, "path", ""),
            "message": getattr(pe, "message", str(pe)),
            "line": getattr(pe, "line", 0),
        })


def _build_env(spec):
    """Return (env_dict, env_refs_list) for the playground."""
    env = dict(_DEFAULT_ENV)
    for ref in spec.env_refs or []:
        env.setdefault(ref, "localhost")
    return env, list(spec.env_refs or [])


def _validate(spec, env, diags):
    """Run validation and append issues to *diags*."""
    for issue in _parser.validate(spec, env_vars=env):
        diags.append({
            "severity": issue.severity,
            "path": issue.path,
            "message": issue.message,
            "line": getattr(issue, "line", 0),
        })


def _spec_summary(spec):
    """Return a JSON-safe AST summary dict."""
    return {
        "app_name": spec.app_name,
        "version": spec.version,
        "domain": spec.domain,
        "entities": [
            {
                "name": e.name,
                "fields": [
                    {
                        "name": f.name,
                        "type": f.type,
                        "required": f.required,
                        "unique": f.unique,
                        "auto": f.auto,
                        "ref": f.ref,
                        "default": f.default,
                    }
                    for f in e.fields
                ],
            }
            for e in spec.entities
        ],
        "interfaces": [{"name": i.name, "type": i.type} for i in spec.interfaces],
        "workflows": [{"name": w.name, "trigger": w.trigger} for w in spec.workflows],
        "roles": [r.name for r in spec.roles],
        "languages": spec.languages,
    }


def _try_generate(spec, result):
    """Attempt code generation; populate *result* files/models on success."""
    try:
        from doql.generators.api_gen import _gen_models, _gen_schemas
        result["models_py"] = _gen_models(spec)
        result["schemas_py"] = _gen_schemas(spec)
        result["files"] = [
            {"path": "api/main.py", "size": 0},
            {"path": "api/models.py", "size": len(result["models_py"])},
            {"path": "api/schemas.py", "size": len(result["schemas_py"])},
            {"path": "api/routes.py", "size": 0},
            {"path": "api/database.py", "size": 0},
        ]
    except Exception as exc:
        result["diagnostics"].append({
            "severity": "warning",
            "path": "generator",
            "message": f"Could not generate API: {exc}",
            "line": 0,
        })


def build(source: str):
    """Parse + validate, return diagnostics + rendered files as JSON."""
    result = {
        "ok": False,
        "spec": None,
        "diagnostics": [],
        "files": [],
        "models_py": "",
        "schemas_py": "",
        "env_vars": {},
        "env_refs": [],
        "error": None,
    }

    try:
        spec = _parser.parse_text(source)
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {exc}"
        return json.dumps(result)

    _collect_parse_errors(spec, result["diagnostics"])

    env, refs = _build_env(spec)
    result["env_vars"] = env
    result["env_refs"] = refs

    _validate(spec, env, result["diagnostics"])
    result["spec"] = _spec_summary(spec)
    _try_generate(spec, result)

    result["ok"] = not any(d["severity"] == "error" for d in result["diagnostics"])
    return json.dumps(result)
