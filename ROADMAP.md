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
- [x] Trzy przykładowe `.doql` (asset-management, calibration-lab, iot-fleet)
- [ ] Parser `.doql` (tree-sitter grammar + Python binding)
- [ ] Parser `.env` + walidator referencji
- [ ] Generator API (FastAPI) — minimalny CRUD z 1-2 entity
- [ ] Generator Web (React + MUI) — dashboard + 1 strona CRUD
- [ ] Generator Infra (docker-compose + Traefik)
- [ ] CLI: `init`, `validate`, `plan`, `build`, `run`

**Deliverable:** `doql init --template asset-management demo && cd demo && doql build && doql run` → działająca aplikacja na `localhost:8080`.

---

## Faza 1 — MVP (4 tygodnie)

**Cel:** jedna realna aplikacja wdrożona na produkcji.

- [ ] Pełny generator API (wszystkie typy entity, relacje, COMPUTED, VALIDATE)
- [ ] Integracja z oqlos (REST + webhooks)
- [ ] Auth JWT + RBAC (podstawowe role)
- [ ] Generator Web: wszystkie widgety z spec (dashboard, crud, scan, workflow)
- [ ] Generator PWA (offline + background sync)
- [ ] Integracje: email, Slack, S3 storage
- [ ] i18n (pl, en, de)
- [ ] Deploy: docker-compose + Quadlet + Let's Encrypt
- [ ] Lockfile + migration strategy

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
