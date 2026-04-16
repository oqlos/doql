# Changelog

Wszystkie istotne zmiany w projekcie `doql`. Format oparty na [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added (sesja 8 — full-stack examples + env manager)
- **Mobile PWA generator** (`doql/generators/mobile_gen.py`) — replaces the
  earlier stub. Now emits a self-contained installable PWA: `manifest.json`,
  `service-worker.js` (cache-first shell, network-first API), entity-aware
  CRUD `app.js`, mobile-first `style.css`, and SVG icons.
- **Tauri v2 desktop generator** — `desktop_gen.py` upgraded from Tauri 1.5
  (which required deprecated `webkit2gtk-4.0` + `libsoup-2.4`) to Tauri 2.x
  (uses `webkit2gtk-4.1` + `libsoup-3.0` available on Ubuntu 24.04+).
  Generates a placeholder RGBA `icons/icon.png` so `tauri dev` compiles
  out-of-the-box; bundling disabled by default.
- **New examples**:
  - `examples/notes-app/` — full-stack demo (API + web + mobile + desktop)
  - `examples/todo-pwa/` — minimal mobile-first PWA demo
- **Environment manager** (`tests/env_manager.py`) — discovers every
  `examples/*/app.doql`, runs `doql build`, and verifies all 5 generated
  layers per example: API (compile + uvicorn boot + `/health` + OpenAPI),
  web (package.json/vite/tsconfig/.tsx), mobile (manifest+SW+icons),
  desktop (tauri.conf.json v1/v2, Cargo.toml, optional `cargo check`),
  infra (compose+Dockerfile). Outputs both human-readable table and
  `--json`. CLI flags: `--skip-api`, `--cargo-check`, `--verbose`.
- **Playground**: `.env` tab showing seeded localhost defaults + spec
  references; URL hash sync (`#tab=ast` deep-links).

### Added (Faza 3 — Ecosystem, sesja 6)
- **`doql-plugin-iso17025`** — ISO/IEC 17025:2017: traceability chain, GUM
  uncertainty budgets (u_c = √Σ(cᵢ·uᵢ)²), calibration certificates, drift
  monitor (linear regression vs CMC).
- **`doql-plugin-fleet`** — multi-tenant fleet manager: `Tenant` model +
  `TenantMiddleware` (X-Tenant-Id / subdomain / JWT), device registry
  (`/enroll`, `/heartbeat`, `/health`), `MetricSample` time-series,
  OTA canary rollout with state machine.
- **`doql-plugin-erp`** — Odoo XML-RPC client, mapping DSL, bidirectional
  sync with conflict policies, inbound webhook handlers (HMAC-verified).
- **Marketplace scaffolds** — `saas-multi-tenant`, `calibration-lab`,
  `iot-fleet`; new CLI flag `doql init --list-templates`.

### Added (Faza 2 — sesja 7)
- **Test suite** — 38 pytest tests covering parser, generators, plugins,
  LSP + GUM numerics; `tests/runtime_deploy.sh` end-to-end runtime smoke;
  `tests/runtime_all_examples.sh` multi-example /health probe;
  `tests/playground_e2e.py` headless Playwright verification.
- **Packaging** — `pyproject.toml` `package-data` ships `scaffolds/**/*`
  with the wheel; 5 wheels build cleanly (doql + 4 plugins). Fresh-venv
  install verified.
- **CI** — `.github/workflows/ci.yml` with matrix unit-tests (3.10–3.13),
  runtime-smoke job (API + all examples + web build), packaging job
  (sdist + wheel + fresh-venv verification + artifact upload), and a
  playground deploy job (GitHub Pages, main-only).
- **Playground** — `playground/` static HTML+Pyodide app runs the real
  `doql` wheel client-side. Live editor → parser + validator + generator
  diagnostics + generated `models.py` / `schemas.py` preview. No backend,
  no telemetry, ~65 kB wheel served once per session. Deploys to
  GitHub Pages / Netlify / S3.

### Fixed (runtime bugs found during deploy verification, sesja 7)
- API generator: auto-inject `id` primary key when an entity has no `id`
  field (was: `sqlalchemy.exc.ArgumentError: could not assemble any
  primary key columns`).
- API generator: `_py_type` wraps all non-required / auto fields in
  `Optional[…]` (was: `ResponseValidationError: Input should be a valid
  string` for nullable columns under Pydantic v2 strict mode).
- API generator: CRUD routes auto-generate UUID `id` on POST.
- API generator: `id: Optional[str]` injected into response schema for
  auto-PK entities so clients see the generated id.
- API generator: drop FK constraint when the referenced entity is not in
  the spec (was: `NoReferencedTableError` at app startup).
- API generator: pin `bcrypt>=4.0,<4.1` in `requirements.txt` (passlib
  1.7.x is broken on bcrypt 4.1+ due to removed `__about__` attribute).
- Parser `ROLES`: match `^  name:` not `- word` (was: nested permission
  verbs like `read`, `execute` were extracted as role names).
- Auth generator: use `role.name` instead of stringifying the whole
  `Role` dataclass into the `ROLES = [...]` allowlist.
- Web generator: prepend `id: any` to the TS entity interface when the
  entity has no explicit id field (TSX was `TS2339: Property 'id' does
  not exist`).

### W toku (Faza 1 — MVP)
- Parser `.doql` v0.2 (pokrywający nowe sekcje DATA, DOCUMENT, TEMPLATE, kiosk)
- Generator dla `DOCUMENT` — Jinja2 + WeasyPrint pipeline
- Generator dla `INTERFACE kiosk` — Electron/Tauri + RPi image builder
- Pilot w realnej firmie
- LSP dla VS Code

## [0.2.0-alpha] — 2026-04-16

Rozszerzenie zakresu: dokumenty, dane, kiosk, jednoznaczna semantyka.

### Added

#### Język i specyfikacja
- Nowy dokument `GLOSSARY.md` — jednoznaczna semantyka OQL / DOQL / IQL
- SPEC v0.2 — 16 sekcji (z 11 w v0.1)
- Nowy typ sekcji `DATA` — źródła danych: JSON, SQLite, API, CSV, Excel, ENV
- Nowy typ sekcji `TEMPLATE` — reużywalne szablony
- Nowy typ sekcji `DOCUMENT` — generowanie PDF/HTML/DOCX/Markdown
- Nowy typ sekcji `REPORT` — okresowe raporty z agregacją
- Nowy typ sekcji `DATABASE` — jawne deklarowanie bazy
- Nowy typ sekcji `API_CLIENT` — klienty do zewnętrznych API
- Nowy typ sekcji `WEBHOOK` — handlery zdarzeń przychodzących
- Nowy typ interfejsu `INTERFACE kiosk` — stanowiska pełnoekranowe
- Nowy target deploy `kiosk-appliance` — Raspberry Pi / tablet

#### Przykłady
- `examples/document-generator/` — generator świadectw ISO 17025 (bez ciężkiego SaaS)
- `examples/kiosk-station/` — stanowisko operatora na tablecie

#### Dokumentacja
- Zaktualizowany `README.md` z rozszerzonym zakresem
- Zaktualizowany `OQLOS-REQUIREMENTS.md` — 3 nowe wymagania (webhook push, execution data, delta API)

### Changed
- `INTERFACE web/mobile/desktop` mogą teraz korzystać z `DATA` sources bezpośrednio
- `DEPLOY` wspiera 3 targety: `docker-compose`, `quadlet`, `kiosk-appliance`
- Quadlet generator produkuje też Traefik jako Quadlet (a nie zwykły docker-compose)

### Known Limitations
- Parser v0.2 jeszcze w trakcie implementacji
- Generator PDF przez WeasyPrint — pełne CSS3 grid jeszcze nie działa
- Kiosk appliance tylko dla Raspberry Pi OS (Windows IoT / Ubuntu Kiosk w v0.3)

## [0.1.0-alpha] — 2026-04-16

Pierwsza publiczna wersja — specyfikacja języka i przykłady SaaS.

### Added
- Specyfikacja języka `doql` v0.1 (SPEC.md)
- Trzy kompletne przykłady deklaracji:
  - `examples/asset-management/` — klon Drägerware
  - `examples/calibration-lab/` — lab ISO 17025
  - `examples/iot-fleet/` — flota urządzeń IoT
- Szkielet CLI (`doql init`, `validate`, `plan`, `build`, `run`, `deploy`, `sync`, `export`, `docs`)
- Dokument `OQLOS-REQUIREMENTS.md` z listą zmian wymaganych w oqlos
- Dokument `ROADMAP.md` z planem faz 0–3

---

## Przyszłe wersje

### [0.3.0] — planowane Lipiec 2026
- LSP dla VS Code + składnia
- Playground online (playground.doql.dev)
- Kubernetes target (Helm chart)
- Flutter mobile generator
- Windows IoT / Ubuntu Kiosk targets

### [0.5.0] — planowane Wrzesień 2026
- Pierwszy pilot w produkcji
- Marketplace szablonów `.doql`
- `doql sync` (merge-friendly)
- Import z Postmana / OpenAPI do `.doql`

### [1.0.0] — planowane Q4 2026
- Stabilne API, backwards compatibility guarantee
- Pełen zestaw szablonów domenowych
- Certyfikacja deweloperów
- Commercial plugins (gxp, iso17025, fleet)
