"""Audit middleware — automatically logs every mutating request."""
from __future__ import annotations

import json
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class AuditMiddleware(BaseHTTPMiddleware):
    """Log every POST/PATCH/DELETE to the audit_events table."""

    async def dispatch(self, request: Request, call_next):
        if request.method not in ("POST", "PATCH", "PUT", "DELETE"):
            return await call_next(request)

        # Read body for logging (non-destructive)
        body_bytes = await request.body()
        try:
            body = json.loads(body_bytes) if body_bytes else None
        except Exception:
            body = None

        response = await call_next(request)

        # Record post-response to capture success/failure
        try:
            from plugins.gxp.audit_log import record
            from database import SessionLocal
            db = SessionLocal()
            try:
                actor_id = getattr(request.state, "user_id", None)
                actor_role = getattr(request.state, "user_role", None)
                # Derive entity from path: /api/v1/devices/123 -> "devices"
                parts = [p for p in request.url.path.split("/") if p]
                entity = parts[2] if len(parts) >= 3 else "unknown"
                entity_id = parts[3] if len(parts) >= 4 else None
                action = {"POST": "create", "PATCH": "update", "PUT": "update", "DELETE": "delete"}[request.method]
                record(
                    db,
                    action=action,
                    entity=entity,
                    entity_id=entity_id,
                    actor_id=actor_id,
                    actor_role=actor_role,
                    after=body,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                )
            finally:
                db.close()
        except Exception as e:
            # Don't fail the request on audit failure — but log loudly
            import logging
            logging.error(f"[AUDIT] Failed to record: {e}")

        return response
