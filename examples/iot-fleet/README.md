# IoT Fleet Manager — Kubernetes doql example

Fleet management for 100–10 000 IoT nodes running oqlos-agent.

| Target | Tech | Start |
|--------|------|-------|
| API | FastAPI + InfluxDB + PostgreSQL | `cd build/api && uvicorn main:app --port 8103` |
| Web | React + Tailwind + Leaflet | `cd build/web && npm install && npm run dev` |

## Quick start

```bash
cp .env.example .env
doql validate
doql build --force

cd build/infra && docker compose -f docker-compose.localhost.yml up -d --build
# → http://iot-fleet.localhost/        (API)
# → http://iot-fleet.localhost/docs    (Swagger)
```

## Entities

- **Node** — IoT devices with geo location and computed status
- **Telemetry** — time-series data (cpu, memory, temperature)
- **Deployment** — scheduled scenario execution
- **FirmwareBuild** — signed firmware images
- **OTAUpdate** — canary OTA rollout

## Key features

- **Kubernetes deploy** — Helm chart with autoscale (2–10 API, 1–5 worker)
- **Real-time monitoring** — Prometheus + Grafana auto-provisioned dashboards
- **Canary OTA** — 5% → 25% → 100% with automatic rollback
- **WebSocket streaming** — bidirectional telemetry + commands
- **Leaflet map** — fleet map colored by node status

## Formats

- `app.doql` — original DOQL format
- `app.doql.less` — LESS variant with variables for multi-platform/multi-env
