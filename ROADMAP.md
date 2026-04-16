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
- [ ] Parser tree-sitter (pełna gramatyka `.doql`, error recovery)
- [ ] Alembic migrations (auto-generate from ENTITY diff)
- [ ] Integracja z oqlos (REST + webhooks)
- [ ] Generator PWA (offline + background sync)
- [ ] Integracje: email, Slack, S3 storage
- [ ] i18n (pl, en, de)
- [ ] Migration strategy (`doql sync` z lockfile diffem)

**Milestone:** pilot w firmie BHP (Gdańsk) — realna instalacja, 10+ użytkowników.

---

## Faza 2 — Stabilność + DX (6 tygodni)

- [ ] Generator Desktop (Tauri)
- [ ] Workflow engine (lightweight state-machine)
- [ ] Report generator (WeasyPrint + signed PDFs)
- [ ] `doql sync` (merge-friendly re-generation)
- [ ] Plugin system
- [ ] LSP / język server dla VS Code
- [ ] GitHub Action `doql-ci`
- [ ] Playground online (playground.doql.dev)

---

## Faza 3 — Ecosystem (3 miesiące)

- [ ] **doql-plugin-gxp** — 21 CFR Part 11 + audit log + e-signatures
- [ ] **doql-plugin-iso17025** — certyfikaty + traceability + uncertainty
- [ ] **doql-plugin-fleet** — multi-tenant fleet manager
- [ ] **doql-plugin-erp** — Odoo integration
- [ ] Marketplace `.doql` templates
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
