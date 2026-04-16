# doql-plugin-gxp — Compliance Add-on

Generated for **Mask Inspection Manager** v1.0.0.

This plugin adds **21 CFR Part 11** / **EU Annex 11** compliance primitives:

## Components

| File | Purpose | Standard Reference |
|------|---------|--------------------|
| `audit_log.py` | Tamper-evident audit trail (SHA-256 chain) | §11.10(e) |
| `audit_middleware.py` | Auto-logs every mutation | §11.10(e) |
| `e_signature.py` | E-signatures + verification | §11.50, §11.70, §11.200 |
| `migration_audit.py` | Alembic migration for tables | — |

## Integration

1. Copy the generated files into your `api/plugins/gxp/` directory.
2. Apply the migration:
   ```bash
   cp migration_audit.py ../api/alembic/versions/
   alembic upgrade head
   ```
3. Wire the middleware in `main.py`:
   ```python
   from plugins.gxp.audit_middleware import AuditMiddleware
   from plugins.gxp.e_signature import router as gxp_router
   app.add_middleware(AuditMiddleware)
   app.include_router(gxp_router)
   ```
4. In any endpoint that mutates regulated data, call `record(db, ...)` manually for richer context (before/after states).

## Verify chain integrity

```python
from plugins.gxp.audit_log import verify_chain
valid, broken = verify_chain(db)
assert valid, f"Audit chain broken at event: {broken}"
```
