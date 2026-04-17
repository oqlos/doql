"""Tenant module generator for doql-plugin-fleet."""
from __future__ import annotations

import textwrap


def _tenant_module() -> str:
    return textwrap.dedent('''\
        """Tenant model + row-level isolation middleware."""
        from __future__ import annotations

        import contextvars
        from datetime import datetime, timezone
        from typing import Optional

        from fastapi import Request
        from sqlalchemy import Column, String, DateTime, Boolean, Text, event
        from sqlalchemy.orm import Session, Query
        from starlette.middleware.base import BaseHTTPMiddleware

        try:
            from database import Base
        except ImportError:
            from sqlalchemy.orm import declarative_base
            Base = declarative_base()


        # Current tenant stored in context var (async-safe)
        current_tenant_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
            "current_tenant_id", default=None
        )


        class Tenant(Base):
            __tablename__ = "tenants"
            id = Column(String(36), primary_key=True)
            slug = Column(String(64), unique=True, nullable=False)    # URL-safe
            name = Column(String(255), nullable=False)
            plan = Column(String(32), nullable=False, default="free")   # free | pro | enterprise
            created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
            active = Column(Boolean, default=True)
            settings = Column(Text, nullable=True)   # JSON config per tenant


        class TenantMiddleware(BaseHTTPMiddleware):
            """Resolve tenant from subdomain / header / JWT and set context var."""

            async def dispatch(self, request: Request, call_next):
                tenant_id = self._resolve(request)
                token = current_tenant_id.set(tenant_id)
                try:
                    request.state.tenant_id = tenant_id
                    return await call_next(request)
                finally:
                    current_tenant_id.reset(token)

            def _resolve(self, request: Request) -> Optional[str]:
                # 1. Explicit header wins (for service-to-service)
                header = request.headers.get("X-Tenant-Id")
                if header:
                    return header
                # 2. Subdomain pattern: {slug}.app.example.com
                host = request.headers.get("host", "")
                parts = host.split(".")
                if len(parts) >= 3:
                    return parts[0]
                # 3. JWT claim — assumes auth ran earlier
                user = getattr(request.state, "user", None)
                if user is not None:
                    return getattr(user, "tenant_id", None)
                return None


        def apply_tenant_filter(query: Query, model: type) -> Query:
            """Apply row-level isolation to a query if the model has a tenant_id column."""
            if not hasattr(model, "tenant_id"):
                return query
            tid = current_tenant_id.get()
            if tid is None:
                # No tenant context = no data (defense in depth)
                return query.filter(False)
            return query.filter(model.tenant_id == tid)
    ''')
