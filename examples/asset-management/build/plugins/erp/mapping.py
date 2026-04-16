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
