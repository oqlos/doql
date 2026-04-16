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
