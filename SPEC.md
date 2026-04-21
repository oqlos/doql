# doql Language Specification v0.2.3

> **Status:** Draft · **Last updated:** 2026-04-21 · **Wersja poprzednia:** v0.2.2

`doql` (Declarative OQL) to język deklaratywny opisujący to, **co ma powstać** z danej deklaracji. Nie tylko aplikacje SaaS — także dokumenty, raporty PDF, szablony, bazy danych SQLite, klienty API, stanowiska kiosk.

**Zasada nadrzędna:** `doql` opisuje **artefakty** (rzeczy, które powstają). Generator je tworzy. `.env` dostarcza sekrety. `.json`/`.sqlite`/API dostarczają dane.

**Formaty plików:** `.doql` (classic), `.doql.css`, `.doql.less`, `.doql.sass` — wszystkie parsują się do tego samego `DoqlSpec`.

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
| `INFRASTRUCTURE` | Kubernetes, Terraform, Docker, systemd | `k8s`, `terraform` |
| `INGRESS` | Reverse proxy: Nginx, Traefik | `nginx`, `traefik` |
| `CI` | CI/CD pipeline: GitHub, GitLab, Jenkins | `github`, `gitlab` |

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
TESTS: IMPORT *.testql.toon.yaml

# — Interfejsy użytkownika
INTERFACE web | mobile | desktop | kiosk | api

# — Workflow
WORKFLOW ...

# — Uprawnienia
ROLES ...

# — Infrastruktura (Kubernetes, Terraform)
INFRASTRUCTURE ...

# — Ingress (Nginx, Traefik)
INGRESS ...

# — CI/CD (GitHub, GitLab, Jenkins)
CI ...

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

### 12.4 Deploy directives `@local` / `@push` / `@remote`

Blok `deploy` może zawierać dyrektywy `@local`, `@push`, `@remote` — komendy shell wykonywane przez `doql deploy` w kolejności:

```css
deploy {
  target: quadlet;
  @local: doql build && podman build -t myapp .;
  @push: podman push myapp registry.example.com/myapp;
  @remote: ssh prod systemctl --user restart myapp;
}
```

| Dyrektywa | Kiedy | Typowe użycie |
|-----------|-------|---------------|
| `@local` | Przed deployem | Build, testy, pakowanie |
| `@push` | Po local | Push image/artifact do registry |
| `@remote` | Po push | Restart usługi na serwerze |

Jeśli brak dyrektyw, `doql deploy` wykonuje fallback do docker-compose.

### 12.5 Environment — definicje środowisk

`ENVIRONMENT` definiuje nazwane środowisko docelowe (dev, staging, prod):

```css
environment[name="dev"] {
  runtime: docker-compose;
  env_file: ".env.dev";
}

environment[name="prod"] {
  runtime: podman-quadlet;
  ssh_host: env.PROD_HOST;
  replicas: 3;
}
```

| Pole | Typ | Opis |
|------|-----|------|
| `runtime` | string | `docker-compose`, `quadlet`, `podman` |
| `ssh_host` | string? | Host SSH do remote deploy |
| `env_file` | string? | Plik .env dla tego środowiska |
| `replicas` | int | Liczba replik (default: 1) |
| `config.*` | string | Dowolne key-value konfig |

Diagnostyka środowiska: `doql doctor --env prod` (sprawdza SSH, runtime, dysk).

### 12.6 Kiosk appliance

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

## 13. INFRASTRUCTURE — Kubernetes, Terraform, Docker

`INFRASTRUCTURE` definiuje platformę deploymentu niezależnie od `DEPLOY`. Dzięki temu jeden projekt może generować zarówno `docker-compose.yml`, jak i manifesty K8s lub pliki Terraform.

### 13.1 Kubernetes

```css
infrastructure[type="kubernetes"] {
  provider: k3s;
  namespace: doql;
  replicas: 3;
}
```

Generuje:
- `infra/deployment.yaml` — Deployment + Service
- `infra/configmap.yaml` — ConfigMap ze zmiennymi
- `infra/ingress.yaml` — Ingress (TLS opcjonalnie)
- `infra/kustomization.yaml` — Kustomize manifest

### 13.2 Terraform (Docker provider)

```css
infrastructure[type="terraform"] {
  provider: docker;
}
```

Generuje:
- `infra/main.tf` — Docker image + container resource
- `infra/variables.tf` — zmienne `domain`, `replicas`
- `infra/outputs.tf` — output `container_name`

### 13.3 Docker Compose (legacy fallback)

Jeśli brak bloku `INFRASTRUCTURE`, generator używa `DEPLOY.target` i emituje `docker-compose.yml` + `Dockerfile` (backward compatible).

| Pole | Typ | Opis |
|------|-----|------|
| `type` | string | `kubernetes`, `terraform`, `docker-compose` |
| `provider` | string? | `k3s`, `docker`, `aws`, `gcp` |
| `namespace` | string? | Namespace K8s lub projekt TF |
| `replicas` | int | Liczba replik (default: 1) |
| `config.*` | string | Dowolne key-value (np. `cluster: prod`) |

---

## 14. INGRESS — Nginx, Traefik

`INGRESS` definiuje reverse proxy i routing do usług.

### 14.1 Nginx

```css
ingress[type="nginx"] {
  tls: true;
  cert_manager: letsencrypt;
  rate_limit: 100r/m;
}
```

Generuje:
- `infra/nginx.conf` — konfiguracja upstream + server block
- `infra/Dockerfile.nginx` — obraz Nginx alpine z configiem

### 14.2 Traefik (K8s / Docker)

Traefik jest domyślnym ingress controllerem w K8s i obsługiwany przez `docker-compose.yml` (z etykietami).

| Pole | Typ | Opis |
|------|-----|------|
| `type` | string | `nginx`, `traefik` |
| `tls` | bool | Włącz HTTPS (default: false) |
| `cert_manager` | string? | `letsencrypt`, `selfsigned`, `custom` |
| `rate_limit` | string? | np. `100r/m` |
| `config.*` | string | Dodatkowe dyrektywy |

---

## 15. CI — GitHub, GitLab, Jenkins

`CI` definiuje pipeline CI/CD. Można zadeklarować wiele bloków CI (np. GitHub + Jenkins dla różnych branchy).

### 15.1 GitHub Actions (default)

```css
ci[type="github"] {
  runner: ubuntu-latest;
  stages: validate, build, test, deploy;
}
```

Generuje: `.github/workflows/doql-ci.yml`

### 15.2 GitLab CI

```css
ci[type="gitlab"] {
  runner: docker;
  stages: validate, build, test, deploy;
}
```

Generuje: `.gitlab-ci.yml`

### 15.3 Jenkins

```css
ci[type="jenkins"] {
  runner: any;
  stages: validate, build, test, deploy;
}
```

Generuje: `Jenkinsfile` (declarative pipeline)

| Pole | Typ | Opis |
|------|-----|------|
| `type` | string | `github`, `gitlab`, `jenkins` |
| `runner` | string? | Label runnera / agenta |
| `stages` | list[string] | Etapy pipeline (default: validate, build, test) |
| `config.*` | string | Dodatkowe zmienne |

---

## 16. Minimalny plik DOQL dla każdego scenariusza

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

## 17. Komendy CLI — rozszerzone

| Komenda | Co robi |
|---------|---------|
| `doql init` | Utwórz nowy projekt z szablonu |
| `doql validate` | Sprawdź poprawność `.doql` + `.env` |
| `doql plan` | Dry-run: pokaż co zostanie wygenerowane |
| `doql build` | Wygeneruj cały kod (`--no-overwrite` pomija istniejące pliki) |
| `doql run` | Uruchom lokalnie (dev mode) |
| `doql deploy` | Deploy na środowisko (wykonuje `@local/@push/@remote`) |
| `doql sync` | Re-generuj zmienione części (merge-friendly) |
| `doql export` | Eksportuj do OpenAPI / Postman / TS SDK / YAML / Markdown / CSS / LESS / SASS |
| `doql import` | Importuj YAML → DOQL |
| `doql generate <artifact>` | Wygeneruj pojedynczy artefakt (dokument, raport) |
| `doql render <template>` | Wyrenderuj szablon z danymi |
| `doql query <data>` | Zapytaj DATA source i zwróć JSON |
| `doql kiosk --install` | Zainstaluj wygenerowany kiosk na urządzeniu |
| `doql quadlet --install` | Zainstaluj Quadlet containers |
| `doql docs` | Wygeneruj stronę dokumentacji |
| `doql adopt <dir>` | Reverse-engineer istniejącego projektu → `app.doql.css` |
| `doql doctor` | Diagnostyka projektu (9 checks + `--env` remote SSH) |
| `doql drift` | Porównaj zadeklarowany stan z live device scan |
| `doql workspace` | Multi-project operations nad app.doql.css manifests |
| `doql publish` | Publikuj artefakty (PyPI, npm, Docker, GitHub) |

---

## 18. Konwencja katalogów

```
my-app/
├── app.doql                  # główna deklaracja (classic)
├── app.doql.css              # alternatywa: format CSS
├── app.doql.less             # alternatywa: format LESS (ze zmiennymi @)
├── app.doql.sass             # alternatywa: format SASS (ze zmiennymi $)
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
├── tests/                    # .testql.toon.yaml (testql)
├── schemas/                  # JSON Schema do walidacji DATA
├── assets/                   # logo, fonts, idle slideshow
├── build/                    # wygenerowane (gitignore)
└── doql.lock
```

Priorytet autodetekcji: `.doql.less` > `.doql.sass` > `.doql.css` > `.doql`

---

## 19. Alternatywna składnia CSS-like

Oprócz klasycznego formatu indentacyjnego, doql wspiera trzy formaty CSS-like. Wszystkie parsują się do identycznego `DoqlSpec`.

### 19.1 Format `.doql.css`

```css
app {
  name:    "My App";
  version: "1.0.0";
  domain:  "my-domain";
}

entity[name="Device"] {
  id:     uuid! auto;
  serial: string! unique;
  model:  string!;
  status: enum[active, retired] default=active;
}

interface[name="web"] {
  type:      spa;
  framework: react;
}

deploy {
  target: docker-compose;
}
```

### 19.2 Format `.doql.less` (ze zmiennymi `@`)

```less
@app-name:    "Calibration Lab";
@app-version: "0.9.0";
@db-backend:  postgresql;

app {
  name:    @app-name;
  version: @app-version;
}

entity[name="Instrument"] {
  serial:       string! unique;
  manufacturer: string!;
}
```

Zmienne `@var` są rozwijane w czasie parsowania — wynikowy `DoqlSpec` nie zawiera zmiennych.

### 19.3 Format `.doql.sass` (ze zmiennymi `$`, indent-based)

```sass
$primary: "#2563eb"
$app-name: "Notes App"

app
  name:    $app-name
  version: "1.0.0"

entity[name="Note"]
  id:      uuid! auto
  title:   string!
  content: text
```

### 19.4 Konwersja między formatami

```bash
# Classic → LESS
doql export --format less -o spec.doql.less

# LESS → YAML (exchange format)
doql export --format yaml -o spec.yaml

# YAML → Classic
doql import spec.yaml -o app.doql
```

### 19.5 Selektory CSS

| Selektor | Znaczenie |
|----------|-----------|
| `app` | Sekcja APP |
| `entity[name="X"]` | ENTITY X |
| `interface[name="web"]` | INTERFACE web |
| `data[name="X"]` | DATA X |
| `workflow[name="X"]` | WORKFLOW X |
| `deploy` | DEPLOY |
| `roles role[name="X"]` | ROLE X |
| `infrastructure[type="X"]` | INFRASTRUCTURE X |
| `ingress[type="X"]` | INGRESS X |
| `ci[type="X"]` | CI X |

---

## 20. Eksport i import

### Formaty eksportu (`doql export`)

| Format | Flaga | Opis |
|--------|-------|------|
| OpenAPI 3.1 | `--format openapi` | JSON schema z ENTITY + API endpoints |
| Postman | `--format postman` | Kolekcja Postman v2.1 |
| TypeScript SDK | `--format typescript-sdk` | Wygenerowany klient TS |
| YAML | `--format yaml` | Serializacja DoqlSpec do YAML |
| Markdown | `--format markdown` | Dokumentacja specyfikacji |
| CSS | `--format css` | Format `.doql.css` |
| LESS | `--format less` | Format `.doql.less` ze zmiennymi |
| SASS | `--format sass` | Format `.doql.sass` ze zmiennymi |

### Import (`doql import`)

```bash
doql import spec.yaml           # YAML → .doql (stdout)
doql import spec.yaml -o app.doql  # YAML → plik
```

---

## 21. Zmiany względem v0.1

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

**Dodane w v0.2.2:**
- Sekcja 13 (INFRASTRUCTURE) — Kubernetes, Terraform, Docker
- Sekcja 14 (INGRESS) — Nginx, Traefik reverse proxy
- Sekcja 15 (CI) — GitHub Actions, GitLab CI, Jenkins pipeline
- Generatory: `deployment.yaml`, `service.yaml`, `configmap.yaml`, `kustomization.yaml` (K8s)
- Generatory: `main.tf`, `variables.tf`, `outputs.tf` (Terraform)
- Generatory: `nginx.conf`, `Dockerfile.nginx` (Nginx)
- Generatory: `.gitlab-ci.yml`, `Jenkinsfile` (CI)
- Routing CI generatora po `spec.ci_configs` z fallback do GitHub Actions

**Dodane w v0.2.1:**
- Sekcja 19 (Alternatywna składnia CSS-like) — `.doql.css`, `.doql.less`, `.doql.sass`
- Sekcja 20 (Eksport i import) — 8 formatów eksportu, import z YAML
- Zaktualizowana konwencja katalogów — pliki CSS-like + priorytet autodetekcji

**Bez zmian od v0.1:**
- Składnia `ENTITY`
- Sekcje `SCENARIOS`, `TESTS`, `ROLES`, `WORKFLOW`
- `INTERFACE web`, `mobile`, `desktop`, `api` (podstawowa semantyka)
