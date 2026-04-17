# doql Roadmap

> Żywy dokument. Aktualizowany z każdym releasem.

## Filozofia

- **Konwencja nad konfigurację** — minimalny `.doql` ma działać.
- **Merge-friendly** — `doql sync` nie niszczy ręcznych zmian.
- **Bring your own runtime** — oqlos jest wymagany, ale generator UI nie narzuca stacku.
- **Progressive disclosure** — domyślnie minimalne opcje, zaawansowane dostępne przez plugins.

---

## Faza 0 — Proof of Concept (2 tygodnie)

**Cel:** pokazać, że z `.doql` da się wygenerować coś działającego end-to-end.

- [x] Spec języka (v0.1)
- [x] Spec języka (v0.2) — DATA, DOCUMENT, TEMPLATE, REPORT, DATABASE, API_CLIENT, WEBHOOK, INTERFACE kiosk, DEPLOY quadlet/kiosk
- [x] Trzy przykładowe `.doql` (asset-management, calibration-lab, iot-fleet)
- [x] Dwa dodatkowe przykłady v0.2 (document-generator, kiosk-station)
- [x] Parser `.doql` (regex block-based, wszystkie 16 sekcji SPEC v0.2)
- [x] Parser `.env` + walidator referencji env.*, cross-ref entity/template/document/data
- [x] Generator API (FastAPI) — stub (generuje README + scaffold)
- [x] Generator Web (React) — stub (generuje README + scaffold)
- [x] Generator Infra (docker-compose + Quadlet + kiosk) — stub
- [x] CLI: `init`, `validate`, `plan`, `build`, `run`, `deploy`, `sync`, `export`, `generate`, `render`, `query`, `kiosk`, `quadlet`, `docs`
- [x] `pyproject.toml` + `pip install -e .` → `doql --version` działa
- [x] Scaffolds: `doql/scaffolds/minimal/` z `app.doql` + `.env.example`
- [x] Artykuły WordPress (6 szt.) w `articles/`
- [x] GLOSSARY.md — semantyka OQL/DOQL/IQL
- [ ] Parser tree-sitter (pełna gramatyka, LSP-ready) — odłożone do Faza 1
- [ ] Generatory produkujące prawdziwy kod (nie stuby) — odłożone do Faza 1

**Deliverable:** `doql init --template minimal demo && cd demo && doql build` → generuje scaffold. ✅
`doql plan` na każdym z 5 przykładów → poprawny plan. ✅
`doql validate` → sprawdza env.*, pliki DATA, szablony, cross-referencje. ✅

---

## Faza 1 — MVP (4 tygodnie)

**Cel:** jedna realna aplikacja wdrożona na produkcji.

- [x] Lockfile (`doql.lock`) — generowany przy `doql build`
- [x] Generator API — FastAPI routes + SQLAlchemy models + Pydantic schemas + CRUD endpoints (all ENTITY types, refs, computed, keyword escaping)
- [x] Generator DOCUMENT — Jinja2 render scripts + HTML preview per DOCUMENT + WeasyPrint PDF support
- [x] Generator Infra — real docker-compose.yml + Traefik + Dockerfile + .env.docker
- [x] Generator Infra — Podman Quadlet .container files + Traefik quadlet + .env
- [x] Generator Infra — Kiosk appliance installer (Openbox + Chromium --kiosk + systemd service)
- [x] Auth JWT + RBAC — auth.py z login/register/me, bcrypt+jose, role-based `require_role()`, auto-generated gdy ROLES zdefiniowane
- [x] Generator Web — React + Vite + TailwindCSS + React Router + Lucide icons, per-entity CRUD pages, Dashboard z licznikami, Layout z sidebar, api.ts client
- [x] Generator REPORT — standalone render scripts + crontab + WeasyPrint/PDF + JSON fallback + recipients
- [x] Parser: inline comment stripping, quoted value extraction w `_extract_val`
- [x] Alembic migrations — alembic.ini + env.py + initial migration z create_table/drop_table per entity
- [x] i18n — JSON translation files (pl/en/de) + React useTranslation hook + entity/field/page keys
- [x] Integracje: email (SMTP), Slack (webhook), S3 storage + unified notifications.py
- [x] Migration strategy — `doql sync` z lockfile v2 (per-section hashes), diff detection, selective regeneration
- [x] Generator PWA — service worker (cache-first static / network-first API), manifest.webmanifest, background sync stub, SW registration
- [x] Integracja z oqlos — API_CLIENT generator (typed REST client z retry/timeout), WEBHOOK dispatcher (HMAC signature verify, per-event handlers)
- [ ] Parser tree-sitter (pełna gramatyka `.doql`, error recovery)

**Milestone:** pilot w firmie BHP (Gdańsk) — realna instalacja, 10+ użytkowników.

---

## Faza 2 — Stabilność + DX (6 tygodni)

- [x] Generator Desktop (Tauri) — Cargo.toml, tauri.conf.json, main.rs z system tray + menu, package.json, generowane gdy INTERFACE.type=tauri
- [x] Workflow engine — `WorkflowEngine` + `WorkflowRun` + per-workflow `wf_<name>.py` + scheduler.py + REST routes
- [x] Report generator (WeasyPrint + signed PDFs) — zrealizowane w Fazie 1
- [x] `doql sync` (merge-friendly re-generation z lockfile v2 diff)
- [x] Plugin system — `.doql-plugins/*.py` + entry-point `doql_plugins` dyskover, run_plugins() w cmd_build
- [x] GitHub Action `doql-ci` — validate + build + API compile + npm build jobs
- [x] LSP / język server dla VS Code — `doql-lsp` (pygls 2.x), diagnostics/hover/goto-def/completions/symbols + VS Code extension scaffold (`vscode-doql/`)
- [x] Parser error recovery — `parse_text()` z per-block try/except, `spec.parse_errors`, line tracking w `ValidationIssue(line, column)`
- [x] Test suite (pytest) — 99 passing + 2 skipped: parser/generators/plugins/LSP/CSS-parser/exporters + runtime smoke (`tests/runtime_deploy.sh` + `tests/runtime_all_examples.sh`) + Playwright e2e (`tests/playground_e2e.py`)
- [x] Pakietowanie — doql + 4 plugins jako sdist + wheel (`dist/*.whl`, scaffolds included via package-data)
- [x] GitHub Actions CI — matrix 3.10–3.13 unit-tests + runtime-smoke + packaging + artifact upload (`.github/workflows/ci.yml`)
- [x] Playground online — `playground/` static HTML+Pyodide app, loads doql wheel in-browser, live parser+validator+generator diagnostics, deployable to GitHub Pages / Netlify / S3; Playwright e2e verified
- [x] Parser CSS-like — `.doql.css` / `.doql.less` / `.doql.sass` alternatywna składnia (9 modułów: css_parser, css_utils, css_mappers, css_transformers)
- [x] Eksportery — YAML, Markdown, CSS/LESS/SASS (`doql export --format yaml/markdown/css/less/sass`)
- [x] Importer YAML — `doql import spec.yaml` → `.doql`
- [x] Auto-detekcja formatu — `detect_doql_file()` preferuje `.doql.less` > `.doql.sass` > `.doql.css` > `.doql`
- [x] 10 przykładów — 5 nowych: notes-app, todo-pwa, blog-cms, crm-contacts, e-commerce-shop (każdy z wersją CSS-like)

---

## Faza 3 — Ecosystem (3 miesiące)

- [x] **doql-plugin-gxp** — 21 CFR Part 11 + audit log (SHA-256 chain) + e-signatures (`plugins/doql-plugin-gxp/`)
- [x] **doql-plugin-iso17025** — calibration certificates + traceability chain + GUM uncertainty budgets + drift monitor (`plugins/doql-plugin-iso17025/`)
- [x] **doql-plugin-fleet** — multi-tenant fleet manager: Tenant+TenantMiddleware, device registry, metrics ingest, OTA canary rollout (`plugins/doql-plugin-fleet/`)
- [x] **doql-plugin-erp** — Odoo XML-RPC client + mapping DSL + bidirectional sync + inbound webhooks (`plugins/doql-plugin-erp/`)
- [x] Marketplace `.doql` templates — `minimal`, `saas-multi-tenant`, `calibration-lab`, `iot-fleet` + `doql init --list-templates`
- [ ] Certyfikacja deweloperów (`Doql Certified Developer`)

---

## Odłożone / do dyskusji

| Pomysł | Status | Uwagi |
|--------|--------|-------|
| GraphQL layer | 🤔 | Może plugin |
| gRPC API | ❌ | Nisza, niepotrzebne w MVP |
| Flutter mobile | 🤔 | Po PWA, jeśli będzie popyt |
| Serverless target | 🤔 | AWS Lambda, Cloudflare Workers |
| AI-powered UI suggestions | 🌟 | „dodaj filtr po modelu" → modyfikacja `.doql` |
| Visual `.doql` editor | 🌟 | Drag-and-drop, dla non-tech |
| Reverse: introspect existing app → generate `.doql` | 💭 | bardzo ambitne |

---

## Dependencies

Zobacz [`OQLOS-REQUIREMENTS.md`](./OQLOS-REQUIREMENTS.md) — lista zmian wymaganych w oqlos, żeby fazy 1-3 były możliwe.
