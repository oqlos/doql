# doql-plugin-fleet

Multi-tenant fleet manager — drop-in tenant isolation, device registry, metrics ingestion, and OTA campaigns.

## Install

```bash
pip install doql-plugin-fleet
```

Auto-discovered by `doql build` via `doql_plugins` entry-point.

## What you get

- **Tenant isolation** — `TenantMiddleware` resolves tenants from `X-Tenant-Id` header, subdomain (`{slug}.app.example.com`), or JWT claim. `apply_tenant_filter()` ensures queries never leak across tenants.
- **Device registry** — REST endpoints for enrollment (`POST /fleet/devices/enroll`), heartbeat (`/heartbeat`), and fleet health rollup (`/health`).
- **Metrics** — Simple time-series ingest (`POST /fleet/metrics/ingest`) + range query (`GET /fleet/metrics/query`).
- **OTA canary rollout** — `UpdateCampaign` model + `advance_campaign()` state machine: `draft → canary → rolling → completed|rolled_back` based on observed success rate.

## Combine with other plugins

| Plugin | Why combine |
|--------|-------------|
| `doql-plugin-gxp` | Audit every device action + signed firmware deployments |
| `doql-plugin-iso17025` | Attach calibration certificates to each fleet device |
