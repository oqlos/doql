# doql-plugin-fleet — Multi-tenant Fleet Manager

Generated for **E-Commerce Shop** v0.1.0.

Tenant isolation + device registry + metrics + OTA in one drop-in plugin.

## Components

| File | Purpose |
|------|---------|
| `tenant.py` | `Tenant` model + `TenantMiddleware` (subdomain/header/JWT resolution) + `apply_tenant_filter()` for query isolation |
| `device_registry.py` | `/fleet/devices/enroll`, `/heartbeat`, `/health` — device lifecycle |
| `metrics.py` | `/fleet/metrics/ingest`, `/query` — time-series telemetry |
| `ota.py` | `UpdateCampaign` model + `advance_campaign()` canary gate logic |
| `migration.py` | Alembic migration for all tables |

## Wire it up

```python
from plugins.fleet.tenant import TenantMiddleware
from plugins.fleet.device_registry import router as devices_router
from plugins.fleet.metrics import router as metrics_router

app.add_middleware(TenantMiddleware)
app.include_router(devices_router)
app.include_router(metrics_router)
```

## Tenant resolution order

1. `X-Tenant-Id` header (for service-to-service)
2. Subdomain `{slug}.app.example.com`
3. JWT claim (`user.tenant_id`)

## Canary rollout

`advance_campaign(db, campaign_id, success_rate)` transitions status:
- `canary` → `rolling` (if failure_pct ≤ rollback threshold)
- `rolling` → `completed` (if success_rate ≥ 99%)
- any → `rolled_back` (if failure_pct > rollback threshold)
