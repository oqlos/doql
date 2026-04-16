"""Export Postman collection from DoqlSpec."""
from __future__ import annotations

import json
from typing import IO

from ..parser import DoqlSpec


def run(spec: DoqlSpec, out: IO[str]) -> None:
    """Write Postman collection JSON to the given stream."""
    collection = {
        "info": {"name": spec.app_name, "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"},
        "item": [
            {
                "name": e.name,
                "item": [
                    {"name": f"List {e.name}s", "request": {"method": "GET", "url": f"{{{{base_url}}}}/api/v1/{e.name.lower()}s"}},
                    {"name": f"Create {e.name}", "request": {"method": "POST", "url": f"{{{{base_url}}}}/api/v1/{e.name.lower()}s"}},
                ],
            }
            for e in spec.entities
        ],
    }
    json.dump(collection, out, indent=2)
