# doql-plugin-gxp

Reference plugin adding **21 CFR Part 11** / **EU Annex 11** compliance primitives to any doql-generated application.

## What it generates

When `doql build` runs in a project with this plugin installed, the following files are emitted into `build/plugins/gxp/`:

- **`audit_log.py`** — Tamper-evident audit trail (`AuditEvent` model + `record()` + `verify_chain()`). Each record is SHA-256-hash-chained to the previous one (§11.10(e)).
- **`audit_middleware.py`** — Starlette/FastAPI middleware that automatically logs every POST/PATCH/PUT/DELETE.
- **`e_signature.py`** — `ESignature` model + `/gxp/signatures/sign` and `/gxp/signatures/verify/{id}` endpoints with password re-authentication (§11.200(a)).
- **`migration_audit.py`** — Alembic migration adding the `audit_events` and `e_signatures` tables, with indexes on `(entity, entity_id)` and `timestamp`.
- **`README.md`** — integration instructions for your project.

## Install

```bash
pip install doql-plugin-gxp
```

The plugin registers under the `doql_plugins` entry-point group and is **auto-discovered** by `doql build` — no config required.

## Verify it's picked up

```bash
$ doql build
🛠  Running 1 plugin(s)...
    → plugins/gxp/ (source: entry-point)
```

## Compliance disclaimer

This plugin provides **technical primitives** to help build a compliant system. Full compliance requires organizational SOPs, validation protocols (IQ/OQ/PQ), training records, and ongoing monitoring — none of which code alone can provide. Consult your QA/RA team.
