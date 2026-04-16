# doql — Declarative OQL

> **Z jednego pliku `.doql` zbuduj: aplikację (API + Web + Mobile + Desktop), dokument (PDF/HTML), kiosk, integrację z API, bazę danych, workflow — albo wszystko naraz.**

`doql` to warstwa deklaratywna nad ekosystemem [oqlos](https://github.com/softreck/oqlos). Opisuje **co ma powstać**, nie *jak to zakodować*. Generator czyta deklarację, importuje dane z JSON/SQLite/API i produkuje kompletne artefakty.

---

## Rodzina OQL — jednoznaczna semantyka

Trzy języki, trzy role — zobacz pełny [`GLOSSARY.md`](./GLOSSARY.md).

| Język | Paradygmat | Pytanie | Przykład użycia |
|-------|-----------|---------|-----------------|
| **OQL** (`.oql`) | imperatywny | *jak wykonać zadanie?* | sekwencja testowa hardware, kalibracja |
| **DOQL** (`.doql`) | deklaratywny | *co ma powstać?* | SaaS, dokumenty, kiosk, integracja |
| **IQL** (`.iql`) | deklaratywny | *jak wygląda interakcja?* | session recording, testy UI, webhooks |

---

## Co doql potrafi zbudować

`doql` nie jest tylko generatorem aplikacji SaaS — jest generatorem artefaktów. Artefakt to wszystko, co `doql build` produkuje.

| Artefakt | Przykład z życia |
|----------|------------------|
| **Pełna aplikacja SaaS** | Klon Drägerware dla BHP — [`asset-management`](./examples/asset-management) |
| **Lab zgodny z ISO 17025** | Walidacja, audit trail, 4-eyes — [`calibration-lab`](./examples/calibration-lab) |
| **Flota urządzeń IoT** | 1000+ nodes z OTA canary — [`iot-fleet`](./examples/iot-fleet) |
| **Generator dokumentów PDF** | Świadectwa kalibracji ISO 17025 — [`document-generator`](./examples/document-generator) |
| **Stanowisko kiosk** | Terminal operatora na tablecie — [`kiosk-station`](./examples/kiosk-station) |

Każdy z tych przykładów to **jeden plik `.doql`** (~200-500 linii deklaracji) + `.env` + szablony. Nie tysiące linii boilerplate.

---

## Minimalne przykłady dla każdego scenariusza

### Tylko generator PDF (bez serwera)

```doql
APP: "CV Generator"

DATA me:
  source: json
  file: me.json

DOCUMENT cv:
  type: pdf
  template: templates/cv.html
  data: DATA me
  output: "cv_${date}.pdf"
```

```bash
doql generate cv
# → plik cv_2026-04-16.pdf
```

### Tylko kiosk

```doql
APP: "Lab Kiosk"

INTERFACE kiosk:
  target: tablet
  auth: { mode: pin }
  PAGES: [home, scan, inspect]
  hardware: { barcode_scanner: usb-hid }

DEPLOY: kiosk-appliance on raspberry-pi
```

### Tylko klient API z cron

```doql
APP: "Stripe Sync"

API_CLIENT stripe:
  base_url: https://api.stripe.com/v1
  auth: bearer
  token: env.STRIPE_SECRET

DATA customers:
  source: sqlite
  file: data/customers.db

WORKFLOW sync:
  schedule: hourly
  steps:
    - fetch: stripe.list_customers
    - upsert: DATA customers
```

### Pełen SaaS

(zobacz [`examples/asset-management/app.doql`](./examples/asset-management/app.doql) — 250 linii, kompletna aplikacja)

---

## Źródła danych — reuzywalne, wszędzie

`doql` traktuje dane jako first-class citizen. Zdefiniowane raz, używane w API, dokumentach, interfejsach, workflow.

```doql
DATA devices:
  source: json | sqlite | api | csv | excel | env
  file: data/devices.json
  schema: schemas/device.json
```

Potem używasz:

- W modelu: `ENTITY Device: from: DATA devices`
- W dokumencie: `DOCUMENT cert: data: { instrument: DATA devices WHERE id=$id }`
- W UI: `PAGE devices: layout: crud FROM DATA devices`
- W workflow: `WORKFLOW alert: query: DATA devices WHERE status=overdue`

Jedno źródło prawdy, wiele konsumentów.

---

## Deploy: Docker Compose, Quadlet, Kiosk Appliance

### Docker Compose + Traefik (domyślne)

```doql
DEPLOY:
  target: docker-compose
  traefik:
    tls: letsencrypt
    le_email: env.LE_EMAIL
```

### Podman Quadlet (rootless systemd)

```doql
DEPLOY:
  target: quadlet
  rootless: true
  containers:
    - name: api
      image: auto
      labels: ["traefik.http.routers.api.rule=Host(`api.${DOMAIN}`)"]
  traefik:
    as_quadlet: true    # Traefik też jako Quadlet container
```

Generator produkuje `*.container` files gotowe do `~/.config/containers/systemd/`.

### Kiosk Appliance

```doql
DEPLOY:
  target: kiosk-appliance
  os: raspberry-pi-os
  boot_to_app: true
  auto_login: kiosk_user
  watchdog: systemd
  ota_enabled: true
```

Generator produkuje obraz `.img` lub skrypt instalacyjny — tablet startuje prosto do aplikacji bez dostępu do systemu.

---

## Szybki start

```bash
# Instalacja
pip install doql

# Z szablonu
doql init --template document-generator my-lab
cd my-lab

# Sekrety
cp .env.example .env && $EDITOR .env

# Waliduj
doql validate

# Zbuduj
doql build

# Uruchom lokalnie
doql run

# Albo pojedynczy artefakt
doql generate calibration_certificate --instrument-id INST-001
```

---

## Polecenia CLI

| Komenda | Co robi |
|---------|---------|
| `doql init [--template X]` | Scaffold projektu |
| `doql validate` | Walidacja `.doql` + `.env` + referencji |
| `doql plan` | Dry-run: co zostanie wygenerowane |
| `doql build` | Generuje wszystko |
| `doql run` | Dev mode (hot reload) |
| `doql deploy [--env X]` | Produkcja (docker/quadlet/kiosk) |
| `doql generate <artifact>` | Pojedynczy dokument/raport |
| `doql render <template>` | Renderuje szablon z danymi |
| `doql query <data>` | Zapytanie do DATA source → JSON |
| `doql sync` | Re-generowanie (merge-friendly) |
| `doql export [--format X]` | OpenAPI / Postman / TS SDK |
| `doql docs` | Dokumentacja mkdocs |
| `doql kiosk --install` | Instalacja kiosk na urządzeniu |
| `doql quadlet --install` | Instalacja Quadlet do systemd |

---

## Dokumenty w projekcie

- **[`SPEC.md`](./SPEC.md)** — pełna specyfikacja języka v0.2
- **[`GLOSSARY.md`](./GLOSSARY.md)** — jednoznaczna semantyka OQL/DOQL/IQL
- **[`OQLOS-REQUIREMENTS.md`](./OQLOS-REQUIREMENTS.md)** — co dodać do oqlos, żeby to działało w pełni
- **[`ROADMAP.md`](./ROADMAP.md)** — fazy 0-3 rozwoju
- **[`CHANGELOG.md`](./CHANGELOG.md)** — historia wersji

---

## Status

**Alpha** — specyfikacja i przykłady są stabilne, generator w fazie implementacji. Śledź `CHANGELOG.md`.

---

## Licencja

Apache 2.0 (open core). Premium plugins (`doql-plugin-gxp`, `doql-plugin-iso17025`, `doql-plugin-fleet`) na licencji komercyjnej.
