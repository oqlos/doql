# doql-plugin-erp

Odoo / generic-ERP integration — thin XML-RPC client (stdlib only), mapping DSL, bidirectional sync, and inbound webhook receiver.

## Install

```bash
pip install doql-plugin-erp
```

Auto-registered under `doql_plugins` entry-point.

## Configure

Set env vars in your `.env`:

```
ODOO_URL=https://erp.example.com
ODOO_DB=production
ODOO_USERNAME=sync@example.com
ODOO_API_KEY=your-api-key
ERP_WEBHOOK_SECRET=shared-secret
```

## Status

Reference implementation. Extend for:

- Additional ERPs (SAP Business One, Microsoft Dynamics 365 via OData)
- Idempotency keys on push operations
- Batch + rate-limited pull for large datasets
