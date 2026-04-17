# Example: Asset Management (klon Drägerware)

Kompletna aplikacja do zarządzania sprzętem ochrony dróg oddechowych (SCBA, maski, butle), z:

- ✅ Inspekcjami okresowymi (import scenariuszy `.oql`)
- ✅ Skanowaniem kodów kreskowych z telefonu (PWA)
- ✅ Dashboardem z alertami o przeterminowanym sprzęcie
- ✅ Raportami PDF z podpisem cyfrowym
- ✅ Zarządzaniem operatorami + kwalifikacjami
- ✅ Historią napełnień butli
- ✅ Workflow'ami automatyzującymi przypomnienia
- ✅ Rolami (operator / manager stacji / auditor / admin)
- ✅ Desktopem (Tauri) do pracy offline przy stanowisku testowym
- ✅ Deploy: Docker Compose + Traefik + Let's Encrypt + backup

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.css` — wariant CSS-like (SSOT)

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/asset-management my-scba-manager
cd my-scba-manager

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz hasła, klucze, domeny

# 3. Waliduj deklarację
doql validate

# 4. Zobacz plan generowania
doql plan

# 5. Wygeneruj cały kod
doql build
# → build/api/        FastAPI app
# → build/web/        React SPA
# → build/mobile/     PWA
# → build/desktop/    Tauri project
# → build/infra/      docker-compose.yml + Traefik + Quadlet

# 6. Uruchom wybrany target (patrz sekcja niżej)

# 7. Deploy na produkcję
doql deploy --env prod
```

---

## Uruchamianie aplikacji

### Desktop (Tauri)

Do pracy offline przy stanowisku testowym:

```bash
cd build/desktop
npm install  # tylko przy pierwszym uruchomieniu
npm run dev
```

**Wymagania:**
- Rust toolchain: <https://rustup.rs>
- Node 20+
- System libraries (Linux):
  ```bash
  sudo apt install -y \
      libwebkit2gtk-4.1-dev libsoup-3.0-dev \
      libgtk-3-dev libayatana-appindicator3-dev \
      librsvg2-dev libssl-dev pkg-config build-essential
  ```

### Web (React + Vite)

```bash
cd build/web
npm install
npm run dev  # dev mode na http://localhost:5173
# lub
npm run build && npm run preview  # production build
```

### API (FastAPI)

```bash
cd build/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Dokumentacja API: http://localhost:8000/docs

### Pełny stack (Docker Compose)

```bash
cd build/infra
docker-compose up
```

**Uwaga:** `doql run` próbuje uruchomić pełny stack Docker — może się nie udać jeśli port 8000 jest już zajęty.

---

## Co zostaje wygenerowane

```
build/
├── api/                          FastAPI + SQLAlchemy + Alembic
│   ├── app/
│   │   ├── models/               Device, Inspection, Operator, ...
│   │   ├── routes/               /devices, /inspections, /operators, ...
│   │   ├── auth/                 JWT + RBAC
│   │   ├── webhooks/             integracja z oqlos
│   │   └── workflows/            APScheduler jobs
│   ├── migrations/               Alembic
│   ├── tests/                    pytest suite
│   ├── Dockerfile
│   └── openapi.json
│
├── web/                          React + Vite + MUI
│   ├── src/
│   │   ├── pages/                Dashboard, Devices, Scan, Inspections, ...
│   │   ├── components/           DeviceForm, BarcodeScanner, PdfViewer, ...
│   │   ├── api/                  auto-gen TS SDK z OpenAPI
│   │   └── i18n/                 pl.json, en.json, de.json
│   ├── public/
│   │   └── manifest.json         PWA manifest
│   ├── service-worker.ts         offline + background sync
│   └── Dockerfile
│
├── mobile/                       PWA (ten sam kod co web + PWA shell)
│   └── manifest.json
│
├── desktop/                      Tauri
│   ├── src-tauri/
│   ├── Cargo.toml
│   └── tauri.conf.json
│
├── infra/
│   ├── docker-compose.yml
│   ├── docker-compose.prod.yml
│   ├── quadlet/
│   │   ├── scba-api.container
│   │   ├── scba-web.container
│   │   └── scba-db.container
│   ├── traefik/
│   │   └── dynamic.yml
│   └── scripts/
│       ├── backup.sh
│       └── restore.sh
│
└── docs/                         mkdocs-material
    ├── user-guide/
    ├── admin-guide/
    └── api/
```

---

## Dodawanie nowego typu urządzenia

1. Dodaj scenariusz `.oql` do `scenarios/`:
   ```bash
   cat > scenarios/msa-g1-test.oql <<EOF
   SCENARIO: "MSA G1 Full Test"
   ...
   EOF
   ```

2. Zarejestruj go w `app.doql`:
   ```doql
   REGISTER scenario_msa_g1:
     file: scenarios/msa-g1-test.oql
     applies_to: Device WHERE manufacturer=MSA AND model=G1
     interval: 12 months
   ```

3. Wygeneruj zmiany:
   ```bash
   doql sync        # merge-friendly, nie nadpisuje custom kodu
   ```

UI automatycznie pokaże nową opcję w „Start Inspection" dla odpowiednich urządzeń.

---

## Customizacja

Jeśli chcesz nadpisać wygenerowany komponent:

```doql
INTERFACE web:
  template_override:
    pages/Dashboard: custom/MyDashboard.jsx
    components/DeviceCard: custom/MyDeviceCard.jsx
```

`doql sync` zachowa twoje overridy przy kolejnych buildach.

---

## Porównanie z Drägerware

| Funkcja | Drägerware | Ten przykład |
|---------|-----------|--------------|
| Licencja | Komercyjna, per seat | Apache 2.0 (twoja kopia) |
| Backend | Zamknięty | FastAPI (open) |
| Import wyników z stanowisk | ✅ | ✅ (przez oqlos) |
| Barcode scanner | ✅ (natywne) | ✅ (PWA camera API) |
| Mobilne | Natywne | PWA |
| Podpisy cyfrowe | ✅ | ✅ (addon) |
| Auth SSO | ❌ | ✅ |
| Multi-tenant | ❌ | ✅ |
| Modyfikacje | Tylko konfiguracja | Pełny kod (generowany) |
| Samohostowanie | Tak | Tak |
| Cena | $5k–15k / rok | Koszty infrastruktury |

---

## Znane ograniczenia

1. Generator zakłada że `oqlos` jest osiągalny pod `OQLOS_URL` — nie implementuje peryferii sam.
2. W pierwszej wersji desktop (Tauri) nie ma natywnego Modbus — łączy się przez oqlos agent na tej samej maszynie.
3. Workflow engine jest lightweight — dla złożonych procesów BPMN rozważ integrację z Camunda.
