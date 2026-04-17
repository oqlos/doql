"""Odoo XML-RPC client.

Uses Odoo's external API (stdlib xmlrpc.client — no extra deps).
Configure via env vars:
  ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD (or ODOO_API_KEY)
"""
from __future__ import annotations

import os
import xmlrpc.client
from functools import cached_property
from typing import Any, Optional


class OdooClient:
    """Thin wrapper around Odoo's XML-RPC external API."""

    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ):
        self.url = url or os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = db or os.getenv("ODOO_DB", "odoo")
        self.username = username or os.getenv("ODOO_USERNAME", "")
        self.password = password or os.getenv("ODOO_API_KEY") or os.getenv("ODOO_PASSWORD", "")
        self._uid: Optional[int] = None

    @cached_property
    def _common(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", allow_none=True)

    @cached_property
    def _models(self):
        return xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", allow_none=True)

    def authenticate(self) -> int:
        """Authenticate and cache uid. Returns the uid."""
        if self._uid is not None:
            return self._uid
        uid = self._common.authenticate(self.db, self.username, self.password, {})
        if not uid:
            raise RuntimeError("Odoo authentication failed — check ODOO_USERNAME/ODOO_PASSWORD")
        self._uid = uid
        return uid

    def execute(self, model: str, method: str, args: list, kwargs: Optional[dict] = None) -> Any:
        uid = self.authenticate()
        return self._models.execute_kw(
            self.db, uid, self.password, model, method, args, kwargs or {}
        )

    # Convenience CRUD

    def search(self, model: str, domain: list, limit: int = 100) -> list[int]:
        return self.execute(model, "search", [domain], {"limit": limit})

    def read(self, model: str, ids: list[int], fields: Optional[list[str]] = None) -> list[dict]:
        kwargs = {"fields": fields} if fields else {}
        return self.execute(model, "read", [ids], kwargs)

    def search_read(self, model: str, domain: list, fields: list[str], limit: int = 100) -> list[dict]:
        return self.execute(model, "search_read", [domain], {"fields": fields, "limit": limit})

    def create(self, model: str, values: dict) -> int:
        return self.execute(model, "create", [values])

    def write(self, model: str, ids: list[int], values: dict) -> bool:
        return self.execute(model, "write", [ids, values])

    def unlink(self, model: str, ids: list[int]) -> bool:
        return self.execute(model, "unlink", [ids])

    def version(self) -> dict:
        return self._common.version()
