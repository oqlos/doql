# doql Language Specification v0.2

> **Status:** Draft · **Last updated:** 2026-04-16 · **Wersja poprzednia:** v0.1

`doql` (Declarative OQL) to język deklaratywny opisujący to, **co ma powstać** z danej deklaracji. Nie tylko aplikacje SaaS — także dokumenty, raporty PDF, szablony, bazy danych SQLite, klienty API, stanowiska kiosk.

**Zasada nadrzędna:** `doql` opisuje **artefakty** (rzeczy, które powstają). Generator je tworzy. `.env` dostarcza sekrety. `.json`/`.sqlite`/API dostarczają dane.

---

## 1. Co może być artefaktem

Artefakt to wszystko, co generator `doql build` produkuje jako plik lub działającą usługę.

| Typ | Co powstaje | Przykład |
|-----|-------------|----------|
| `ENTITY` | Model danych + CRUD API + formularze | `Device`, `Inspection` |
| `DOCUMENT` | Plik HTML / PDF / Markdown / DOCX | Certyfikat, faktura, raport |
| `TEMPLATE` | Reużywalny szablon (partial) | Nagłówek listu, stopka PDF |
| `DATABASE` | Schemat + seed data | SQLite, PostgreSQL |
| `API_CLIENT` | Klient SDK do zewnętrznego API | Stripe, SendGrid, własny REST |
| `WEBHOOK` | Handler przychodzących zdarzeń | Slack, GitHub, oqlos |
| `WORKFLOW` | Sekwencja automatyzowana | "Gdy X, zrób Y i Z" |
| `INTERFACE` | UI (web/mobile/desktop/kiosk) | Dashboard, PWA, terminal |
| `INTEGRATION` | Łączenie z zewn. usługą | SMTP, Twilio, S3 |
| `REPORT` | Generator raportów (scheduled) | Miesięczny summary |

Każdy z nich ma własną gramatykę — poniżej.

---

## 2. Struktura pliku `.doql`

```doql
APP: "Nazwa"
VERSION: "1.0.0"

# — Źródła danych
DATA ...

# — Modele (trwałe)
ENTITY ...

# — Szablony i artefakty dokumentowe
TEMPLATE ...
DOCUMENT ...
REPORT ...

# — Bazy danych (jeśli nie default)
DATABASE ...

# — Integracje z zewn. usługami
API_CLIENT ...
INTEGRATION ...
WEBHOOK ...

# — Scenariusze i testy z rodziny oqlos
SCENARIOS: IMPORT *.oql
TESTS: IMPORT *.iql

# — Interfejsy użytkownika
INTERFACE web | mobile | desktop | kiosk | api

# — Workflow
WORKFLOW ...

# — Uprawnienia
ROLES ...

# — Wdrożenie
DEPLOY ...
```

Sekcje są **opcjonalne** — minimalny plik może mieć tylko `APP` + `DOCUMENT` (dla generatora PDF bez backendu).

---

## 3. DATA — źródła danych

`DATA` definiuje reużywalne źródło, z którego czerpią inne artefakty.

### 3.1 JSON

```doql
DATA devices:
  source: json
  file: data/devices.json
  schema: schemas/device.json   # opcjonalna walidacja

DATA config:
  source: json
  file: config.json
  env_overrides: true            # wartości z .env nadpisują
```

Użycie:
```doql
ENTITY Device:
  from: DATA devices             # seed z JSON

DOCUMENT spec_sheet:
  data: DATA config.product      # użyj sekcji product z config.json
```

### 3.2 SQLite

```doql
DATA catalog:
  source: sqlite
  file: data/catalog.db
  read_only: true

DATA inspections:
  source: sqlite
  file: data/inspections.db
  migrations: migrations/
  seed: seed/inspections.sql
```

### 3.3 REST API

```doql
DATA weather:
  source: api
  url: https://api.openweathermap.org/data/2.5/weather
  auth: apikey
  key: env.OPENWEATHER_KEY
  cache: 1h

DATA oqlos_scenarios:
  source: api
  url: env.OQLOS_URL + "/api/v1/scenarios"
  auth: bearer
  token: env.OQLOS_API_KEY
  refresh: 30s
```

### 3.4 CSV / Excel

```doql
DATA operators:
  source: csv
  file: data/operators.csv
  delimiter: ";"
  header: true

DATA inventory:
  source: excel
  file: data/inventory.xlsx
  sheet: "Sprzęt"
```

### 3.5 Environment

```doql
DATA env:
  source: env
  prefix: APP_                   # tylko APP_*
```

Wszystkie `DATA` są dostępne wewnątrz szablonów, dokumentów, endpointów i workflow'ów przez składnię `DATA source.field`.

---

## 4. TEMPLATE — reużywalne szablony

```doql
TEMPLATE letterhead:
  type: html
  file: templates/letterhead.html
  vars: [org_name, org_address, logo_url]

TEMPLATE email_notification:
  type: mjml               # HTML emails
  file: templates/email/notification.mjml
  vars: [user_name, action, details]

TEMPLATE report_header:
  type: markdown
  content: |
    # ${title}
    _Wygenerowano: ${date}_
    _Operator: ${operator.name}_
```

Szablony używają Jinja2 domyślnie, można zmienić przez `engine: {jinja2|handlebars|mustache}`.

---

## 5. DOCUMENT — generowanie dokumentów

```doql
DOCUMENT calibration_certificate:
  type: pdf                      # pdf | html | docx | markdown
  template: templates/cert.html
  data:
    device: $device
    measurements: $measurements
    operator: $operator
    date: today

  styling:
    paper: A4
    margin: 2cm
    fonts: [Inter, "DejaVu Sans"]

  metadata:
    title: "Świadectwo kalibracji ${device.serial}"
    author: $operator.name
    subject: "ISO 17025 Calibration Certificate"

  signature:
    enabled: true
    method: xades               # xades | pades | visual
    key: env.SIGNING_KEY

  output:
    path: "certs/${device.serial}_${date}.pdf"
    storage: s3                 # local | s3 | ftp

  hooks:
    on_generate:
      - audit_log: "Certificate generated for ${device.serial}"
      - email: $customer.email TEMPLATE certificate_ready
```

### 5.1 Wywołanie generowania

Z endpointu API:
```doql
INTERFACE api:
  ENDPOINT POST /certificates:
    body: { device_id, measurements }
    action: GENERATE DOCUMENT calibration_certificate
    returns: { url: string, id: uuid }
```

Z workflow:
```doql
WORKFLOW monthly_report:
  trigger: schedule "0 0 1 * *"
  steps:
    - GENERATE DOCUMENT monthly_summary WITH month=last_month
    - EMAIL managers TEMPLATE monthly_report ATTACH $generated.pdf
```

Z CLI:
```bash
doql generate calibration_certificate --device d-001
```

---

## 6. REPORT — okresowe raporty

Specjalizacja `DOCUMENT` dla raportów:

```doql
REPORT monthly_summary:
  schedule: "0 0 1 * *"          # pierwszy dzień miesiąca
  template: templates/monthly.html
  output: pdf

  query:
    - from: Inspection
      where: started_at in last_month
      group_by: result
    - from: Device
      where: status = overdue

  recipients:
    to: [managers]
    cc: env.COMPLIANCE_EMAIL

  retention: 10 years            # ISO wymóg
```

---

## 7. DATABASE — jawne definiowanie bazy

Domyślnie `doql` używa SQLite w dev, PostgreSQL w prod. Można to skonfigurować jawnie:

```doql
DATABASE main:
  type: postgresql
  url: env.DATABASE_URL
  pool_size: 20

DATABASE analytics:
  type: sqlite
  file: data/analytics.db
  read_only: false
  backup: daily

DATABASE cache:
  type: redis
  url: env.REDIS_URL
```

---

## 8. API_CLIENT — klienty do zewnętrznych API

```doql
API_CLIENT stripe:
  base_url: https://api.stripe.com/v1
  auth: bearer
  token: env.STRIPE_SECRET
  rate_limit: 100/s
  retry: 3

  METHOD create_checkout:
    path: /checkout/sessions
    method: POST
    input: { amount, currency, customer }
    output: { id, url }

API_CLIENT oqlos:
  base_url: env.OQLOS_URL
  auth: bearer
  token: env.OQLOS_API_KEY
  openapi: env.OQLOS_URL + "/openapi.json"   # auto-gen z OpenAPI
```

Generator produkuje typed klient (Python + TypeScript SDK).

---

## 9. WEBHOOK — handlery zdarzeń

```doql
WEBHOOK oqlos_scenario_completed:
  source: oqlos
  event: scenario.completed
  auth: hmac
  secret: env.WEBHOOK_SECRET

  handler:
    - find: Inspection WHERE execution_id = $payload.execution_id
    - update: Inspection SET result = $payload.result
    - IF $payload.result == fail:
      - notify: Device.station.manager TEMPLATE inspection_failed
      - GENERATE DOCUMENT failure_report
```

---

## 10. INTERFACE kiosk — stanowisko pełnoekranowe

Nowy typ interfejsu dla dedykowanych stanowisk (tablet na ścianie, terminal operatora, ekran w punkcie serwisowym).

```doql
INTERFACE kiosk:
  target: tablet                 # tablet | monitor | pos | raspberrypi
  fullscreen: true
  chrome: none                   # ukryj pasek przeglądarki
  orientation: landscape         # landscape | portrait | auto
  idle_timeout: 120s             # po 2 min bez aktywności → home

  auth:
    mode: pin                    # pin | nfc | barcode | rfid | none
    length: 4
    timeout: 8h

  hardware:
    barcode_scanner: usb-hid     # usb-hid | camera | serial
    card_reader: nfc
    printer: zebra-zpl
    camera: front

  input:
    keyboard: virtual-only       # virtual-only | physical | both
    touch: primary
    voice: disabled

  style:
    theme: high-contrast         # dla słabego oświetlenia warsztatu
    font_size: large             # duży tekst dla ochrony oczu
    button_size: xl              # duże przyciski dla rękawiczek

  PAGES:
    - home:
        layout: grid
        cards:
          - "Nowa inspekcja" → scan
          - "Moje zadania" → tasks
          - "Zwrot sprzętu" → return
          - "Pomoc" → help

    - scan:
        fullscreen_camera: true
        on_scan:
          - lookup Device WHERE barcode = $scanned
          - next_page: device_detail

    - device_detail:
        from: Device
        buttons:
          - "Start Inspection"
          - "Print Label"
          - "Back"

    - idle_screen:
        show_after: 30s
        content: slideshow from assets/idle/

  lockdown:
    prevent_exit: true           # brak Alt+F4 / ESC
    disable_system_keys: true    # brak Win, Ctrl+Alt+Del
    kiosk_user: kiosk_ro         # osobny user systemowy
    auto_restart_on_crash: true
```

### 10.1 Deploy trybu kiosk

```doql
DEPLOY:
  target: kiosk-appliance
  os: raspberry-pi-os | windows-iot | ubuntu-kiosk
  boot_to_app: true              # start aplikacji razem z systemem
  hide_desktop: true
  auto_login: kiosk_user
  watchdog: systemd              # restart przy crash
```

---

## 11. INTERFACE web/mobile/desktop/api

(Zobacz SPEC v0.1 — semantyka bez zmian, tu tylko uzupełnienia.)

```doql
INTERFACE web:
  pwa: true                      # każdy web może być PWA
  offline_strategy: cache-first

  PAGE document_generator:
    form: DOCUMENT calibration_certificate.inputs
    preview: live                # podgląd PDF przy edycji

INTERFACE desktop:
  type: tauri
  local_db: sqlite               # wbudowany SQLite
  local_files: true              # dostęp do FS
  hardware: usb-serial           # Modbus RTU bezpośrednio
```

---

## 12. DEPLOY — docker-compose, Quadlet, kiosk

### 12.1 Docker Compose + Traefik (default)

```doql
DEPLOY:
  target: docker-compose
  compose_version: "3.9"
  traefik:
    enabled: true
    dashboard: true
    dashboard_domain: traefik.${DOMAIN}
    tls: letsencrypt
    le_email: env.LE_EMAIL
  networks:
    external: [web]
    internal: [backend]
```

### 12.2 Podman Quadlet (rootless, systemd-native)

```doql
DEPLOY:
  target: quadlet
  rootless: true
  systemd_user: doql

  containers:
    - name: api
      image: auto                # build z wygenerowanego kodu
      network: backend
      volume: [data:/var/lib/doql]
      labels:
        - "traefik.enable=true"
        - "traefik.http.routers.api.rule=Host(`api.${DOMAIN}`)"

    - name: web
      image: auto
      network: web
      labels:
        - "traefik.http.routers.web.rule=Host(`${DOMAIN}`)"

  traefik:
    as_quadlet: true             # Traefik też jako Quadlet

  auto_update: systemd-timer     # sprawdzanie aktualizacji co noc
```

Generator produkuje:
```
build/infra/quadlet/
├── api.container
├── web.container
├── db.container
├── traefik.container
├── backup.timer
├── backup.service
└── install.sh
```

Instalacja:
```bash
cp build/infra/quadlet/*.container ~/.config/containers/systemd/
systemctl --user daemon-reload
systemctl --user start doql-api doql-web doql-db doql-traefik
```

### 12.3 Kiosk appliance

```doql
DEPLOY:
  target: kiosk-appliance
  os_image: rpi-os-lite
  install_script: scripts/kiosk-install.sh

  first_boot:
    - install: [chromium, unclutter, xserver-xorg]
    - configure: /etc/xdg/openbox/autostart
    - start: doql-kiosk.service

  update_channel: stable
  ota_enabled: true              # aktualizacje zdalne
```

---

## 13. Minimalny plik DOQL dla każdego scenariusza

### Tylko dokument (np. generator CV):
```doql
APP: "CV Generator"

DATA me:
  source: json
  file: me.json

DOCUMENT cv:
  type: pdf
  template: templates/cv.html
  data: DATA me
  output: cv_${date}.pdf
```
`doql build && doql generate cv` → gotowy PDF, bez serwera.

### Tylko kiosk:
```doql
APP: "Inspection Kiosk"

INTERFACE kiosk:
  target: tablet
  PAGES: [home, scan, inspect]
  hardware: { barcode_scanner: usb-hid }

DEPLOY kiosk-appliance
```

### Tylko klient API:
```doql
APP: "Stripe Sync"

API_CLIENT stripe: ...
API_CLIENT oqlos: ...

WORKFLOW sync:
  schedule: hourly
  steps:
    - fetch: stripe.list_customers
    - upsert: oqlos.customers
```

### Pełen SaaS:
(jak w `examples/asset-management/app.doql`)

---

## 14. Komendy CLI — rozszerzone

| Komenda | Co robi |
|---------|---------|
| `doql generate <artifact>` | Wygeneruj pojedynczy artefakt (dokument, raport) |
| `doql render <template>` | Wyrenderuj szablon z danymi |
| `doql query <data>` | Zapytaj DATA source i zwróć JSON |
| `doql kiosk --install` | Zainstaluj wygenerowany kiosk na urządzeniu |
| `doql quadlet --install` | Zainstaluj Quadlet containers |

---

## 15. Konwencja katalogów

```
my-app/
├── app.doql                  # główna deklaracja
├── .env                      # sekrety
├── .env.example
├── data/                     # źródła danych (JSON, SQLite, CSV)
│   ├── devices.json
│   ├── catalog.db
│   └── operators.csv
├── templates/                # szablony dokumentów i emaili
│   ├── cert.html
│   ├── report.mjml
│   └── email/
├── scenarios/                # .oql (oqlos)
├── tests/                    # .iql (testql)
├── schemas/                  # JSON Schema do walidacji DATA
├── assets/                   # logo, fonts, idle slideshow
├── build/                    # wygenerowane (gitignore)
└── doql.lock
```

---

## 16. Zmiany względem v0.1

**Dodane w v0.2:**
- Sekcja 1 (Artefakty) — jawny katalog typów artefaktów
- Sekcja 3 (DATA sources) — JSON, SQLite, API, CSV, Excel, ENV
- Sekcja 4 (TEMPLATE) — reużywalne szablony
- Sekcja 5 (DOCUMENT) — generowanie HTML/PDF/DOCX/Markdown
- Sekcja 6 (REPORT) — scheduled reports
- Sekcja 7 (DATABASE) — jawne deklarowanie bazy
- Sekcja 8 (API_CLIENT) — klienty do zewn. API
- Sekcja 9 (WEBHOOK) — handlery zdarzeń
- Sekcja 10 (INTERFACE kiosk) — tryb kiosk
- Sekcja 12.2 (Quadlet) — rozszerzony
- Sekcja 12.3 (kiosk-appliance) — nowy target deploy

**Bez zmian od v0.1:**
- Składnia `ENTITY`
- Sekcje `SCENARIOS`, `TESTS`, `ROLES`, `WORKFLOW`
- `INTERFACE web`, `mobile`, `desktop`, `api` (podstawowa semantyka)
