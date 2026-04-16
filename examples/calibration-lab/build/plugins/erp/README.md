# doql-plugin-erp — ERP Integration (Odoo)

Generated for **Calibration Lab Manager** v0.9.0.

## Components

| File | Purpose |
|------|---------|
| `odoo_client.py` | `OdooClient` — XML-RPC auth/search/read/create/write/unlink |
| `mapping.py` | `EntityMapping` DSL describing doql ENTITY ↔ Odoo model |
| `sync.py` | `OdooSync` push/pull with conflict policies |
| `webhook.py` | Inbound webhook (`POST /erp/webhook/{model}`) with HMAC verify |

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
stats = sync.push(local_customers)   # returns {"created": 5, "updated": 12}
```

## Receive Odoo events

```python
from plugins.erp.webhook import on_odoo, router as erp_webhook_router

app.include_router(erp_webhook_router)

@on_odoo("res.partner")
def handle_partner_change(payload):
    print("Odoo partner changed:", payload)
```
