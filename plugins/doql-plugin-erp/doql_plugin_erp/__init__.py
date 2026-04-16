"""doql-plugin-erp — Odoo (and generic ERP) integration.

Generates:
  build/plugins/erp/
  ├── odoo_client.py    — XML-RPC client (auth, read, search, create, write, unlink)
  ├── sync.py           — bidirectional entity sync with field mapping + conflict policy
  ├── mapping.py        — DSL for doql ENTITY ↔ Odoo model mapping
  ├── webhook.py        — inbound webhook receiver (Odoo → app) with HMAC verify
  └── README.md
"""
from __future__ import annotations

import pathlib
import textwrap


def _odoo_client_module() -> str:
    return textwrap.dedent('''\
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
    ''')


def _mapping_module() -> str:
    return textwrap.dedent('''\
        """Entity mapping DSL — describe how a doql ENTITY maps to an Odoo model."""
        from __future__ import annotations

        from dataclasses import dataclass, field
        from typing import Any, Callable, Optional


        @dataclass
        class FieldMapping:
            """One field's mapping — local column → Odoo column."""
            local: str
            remote: str
            to_odoo: Optional[Callable[[Any], Any]] = None
            from_odoo: Optional[Callable[[Any], Any]] = None

            def convert_out(self, value: Any) -> Any:
                return self.to_odoo(value) if self.to_odoo else value

            def convert_in(self, value: Any) -> Any:
                return self.from_odoo(value) if self.from_odoo else value


        @dataclass
        class EntityMapping:
            """Map one doql entity to one Odoo model."""
            entity: str                                   # e.g. "Customer"
            odoo_model: str                               # e.g. "res.partner"
            fields: list[FieldMapping] = field(default_factory=list)
            key_field: str = "id"                         # local primary key
            remote_key_field: str = "id"                  # odoo id field

            def to_odoo(self, record: dict) -> dict:
                out = {}
                for fm in self.fields:
                    if fm.local in record:
                        out[fm.remote] = fm.convert_out(record[fm.local])
                return out

            def from_odoo(self, record: dict) -> dict:
                out = {}
                for fm in self.fields:
                    if fm.remote in record:
                        out[fm.local] = fm.convert_in(record[fm.remote])
                return out


        # Example registry — extend in your project:
        #   CUSTOMER_MAPPING = EntityMapping(
        #       entity="Customer",
        #       odoo_model="res.partner",
        #       fields=[
        #           FieldMapping("name", "name"),
        #           FieldMapping("email", "email"),
        #           FieldMapping("phone", "phone"),
        #           FieldMapping("vat_id", "vat"),
        #       ],
        #   )
    ''')


def _sync_module() -> str:
    return textwrap.dedent('''\
        """Bidirectional sync between local ORM and Odoo."""
        from __future__ import annotations

        from enum import Enum
        from typing import Any


        class ConflictPolicy(str, Enum):
            LOCAL_WINS = "local_wins"
            REMOTE_WINS = "remote_wins"
            LATEST_WINS = "latest_wins"
            MANUAL = "manual"


        class OdooSync:
            """Push local records to Odoo and pull Odoo records locally."""

            def __init__(self, client, mapping, policy: ConflictPolicy = ConflictPolicy.LOCAL_WINS):
                self.client = client
                self.mapping = mapping
                self.policy = policy

            def push(self, local_records: list[dict]) -> dict:
                """Create/update Odoo records from local data. Returns stats."""
                created = 0
                updated = 0
                for rec in local_records:
                    remote_id = rec.get("odoo_id")
                    payload = self.mapping.to_odoo(rec)
                    if remote_id:
                        self.client.write(self.mapping.odoo_model, [remote_id], payload)
                        updated += 1
                    else:
                        new_id = self.client.create(self.mapping.odoo_model, payload)
                        rec["odoo_id"] = new_id   # caller should persist this
                        created += 1
                return {"created": created, "updated": updated}

            def pull(self, since_write_date: str | None = None, limit: int = 500) -> list[dict]:
                """Fetch Odoo records (optionally filtered by write_date >= since) mapped to local shape."""
                domain = []
                if since_write_date:
                    domain = [("write_date", ">=", since_write_date)]
                fields = [fm.remote for fm in self.mapping.fields] + ["id", "write_date"]
                remote_records = self.client.search_read(
                    self.mapping.odoo_model, domain, fields, limit=limit
                )
                return [
                    {**self.mapping.from_odoo(r), "odoo_id": r["id"], "odoo_write_date": r.get("write_date")}
                    for r in remote_records
                ]

            def resolve_conflict(self, local: dict, remote: dict) -> dict:
                """Apply the configured policy to pick a winner. Override for MANUAL."""
                if self.policy == ConflictPolicy.LOCAL_WINS:
                    return local
                if self.policy == ConflictPolicy.REMOTE_WINS:
                    return remote
                if self.policy == ConflictPolicy.LATEST_WINS:
                    l_ts = local.get("updated_at") or ""
                    r_ts = remote.get("odoo_write_date") or ""
                    return remote if r_ts > l_ts else local
                raise NotImplementedError("MANUAL policy requires override")
    ''')


def _webhook_module() -> str:
    return textwrap.dedent('''\
        """Inbound webhook receiver — Odoo → this app.

        Add Odoo automated action → call outgoing webhook to /erp/webhook/{model}.
        HMAC signature verification uses ERP_WEBHOOK_SECRET env var.
        """
        from __future__ import annotations

        import hashlib
        import hmac
        import json
        import os
        from typing import Callable

        from fastapi import APIRouter, HTTPException, Request


        router = APIRouter(prefix="/erp/webhook", tags=["erp"])


        # Registry of per-model handlers
        HANDLERS: dict[str, list[Callable[[dict], None]]] = {}


        def on_odoo(model: str):
            """Decorator — register a handler for an Odoo model event."""
            def deco(fn: Callable[[dict], None]):
                HANDLERS.setdefault(model, []).append(fn)
                return fn
            return deco


        def _verify(body: bytes, signature: str, secret: str) -> bool:
            expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
            return hmac.compare_digest(expected, signature)


        @router.post("/{model}")
        async def receive(model: str, request: Request):
            body = await request.body()
            secret = os.getenv("ERP_WEBHOOK_SECRET", "")
            if secret:
                sig = request.headers.get("X-Signature", "")
                if not _verify(body, sig, secret):
                    raise HTTPException(401, "Invalid signature")
            payload = json.loads(body) if body else {}
            called = 0
            for handler in HANDLERS.get(model, []):
                handler(payload)
                called += 1
            return {"model": model, "handlers_called": called}
    ''')


def _readme(spec) -> str:
    return textwrap.dedent(f'''\
        # doql-plugin-erp — ERP Integration (Odoo)

        Generated for **{spec.app_name}** v{spec.version}.

        ## Components

        | File | Purpose |
        |------|---------|
        | `odoo_client.py` | `OdooClient` — XML-RPC auth/search/read/create/write/unlink |
        | `mapping.py` | `EntityMapping` DSL describing doql ENTITY ↔ Odoo model |
        | `sync.py` | `OdooSync` push/pull with conflict policies |
        | `webhook.py` | Inbound webhook (`POST /erp/webhook/{{model}}`) with HMAC verify |

        ## Configure

        ```bash
        export ODOO_URL=https://erp.example.com
        export ODOO_DB=production
        export ODOO_USERNAME=sync@example.com
        export ODOO_API_KEY=your-api-key   # or ODOO_PASSWORD
        export ERP_WEBHOOK_SECRET=shared-secret-for-odoo-automated-actions
        ```

        ## Push local customers to Odoo

        ```python
        from plugins.erp.odoo_client import OdooClient
        from plugins.erp.mapping import EntityMapping, FieldMapping
        from plugins.erp.sync import OdooSync, ConflictPolicy

        client = OdooClient()
        mapping = EntityMapping(
            entity="Customer",
            odoo_model="res.partner",
            fields=[
                FieldMapping("name", "name"),
                FieldMapping("email", "email"),
                FieldMapping("vat_id", "vat"),
            ],
        )
        sync = OdooSync(client, mapping, policy=ConflictPolicy.LATEST_WINS)
        stats = sync.push(local_customers)   # returns {{"created": 5, "updated": 12}}
        ```

        ## Receive Odoo events

        ```python
        from plugins.erp.webhook import on_odoo, router as erp_webhook_router

        app.include_router(erp_webhook_router)

        @on_odoo("res.partner")
        def handle_partner_change(payload):
            print("Odoo partner changed:", payload)
        ```
    ''')


def generate(spec, env_vars, out: pathlib.Path, project_root: pathlib.Path) -> None:
    """Entry point called by doql's plugin runner."""
    out.mkdir(parents=True, exist_ok=True)

    files = {
        "__init__.py": '"""doql-plugin-erp Odoo integration."""\n',
        "odoo_client.py": _odoo_client_module(),
        "mapping.py": _mapping_module(),
        "sync.py": _sync_module(),
        "webhook.py": _webhook_module(),
        "README.md": _readme(spec),
    }
    for name, content in files.items():
        (out / name).write_text(content, encoding="utf-8")
