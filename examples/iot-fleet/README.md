# IoT Fleet Manager — Kubernetes doql example

Fleet management for 100–10 000 IoT nodes running oqlos-agent.

## Formaty

- `app.doql` — oryginalny format DOQL
- `app.doql.less` — wariant LESS ze zmiennymi dla multi-platform/multi-env

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/iot-fleet my-fleet
cd my-fleet

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz bazy danych

# 3. Waliduj deklarację
doql validate

# 4. Zobacz plan generowania
doql plan

# 5. Wygeneruj cały kod
doql build
# → build/api/        FastAPI backend
# → build/web/        React SPA + Leaflet map
# → build/infra/      docker-compose.yml

# 6. Uruchom wybrany target (patrz sekcja niżej)

# 7. Deploy na produkcję
doql deploy --env prod
```

---

## Uruchamianie aplikacji

### API (FastAPI)

```bash
cd build/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Dokumentacja API: http://localhost:8000/docs

### Web (React + Vite)

```bash
cd build/web
npm install
npm run dev  # dev mode na http://localhost:5173
# lub
npm run build && npm run preview  # production build
```

### Docker Compose

```bash
cd build/infra
docker-compose up
```

**Uwaga:** `doql run` próbuje uruchomić pełny stack Docker — może się nie udać jeśli port 8000 jest już zajęty.

---

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
