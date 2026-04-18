# Changelog

Wszystkie istotne zmiany w projekcie `doql`. Format oparty na [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

### Added (sesja 13 — doql adopt + environments)
- **`doql adopt`** command — reverse-engineer existing project into `app.doql.css`.
  Scans `pyproject.toml`, `package.json`, `.env`, `Dockerfile`, `docker-compose.yml`,
  SQL `CREATE TABLE`, Python model classes. Detects API (FastAPI/Flask/Django),
  CLI (click/argparse), Web (React/Vue/Svelte), Mobile, Desktop interfaces.
  Implementation: `doql/adopt/scanner.py` (~400 lines) + `doql/adopt/emitter.py`.
- **`Environment` model** — `environment[name="prod"] { runtime: quadlet; ssh_host: ...; }`
  New dataclass in `parsers/models.py`, CSS mapper `_map_environment`, CSS renderer
  `_render_environment`, full round-trip support across all formats.
- Generated manifests for 5 oqlos sibling projects: oql, oqlos, testql, weboql, www.

### Fixed (sesja 13)
- **Interface lookup** — changed from `i.type == itype` to `i.name == itype` in
  `_map_interface`, preventing duplicates when `type` declaration differs from selector.
- **Interface renderer** — now uses `interface[type="..."]` instead of `interface[name="..."]`.
- **Duplicate pages** — added deduplication in web frontend scanner.
- **SQL entity parser** — filtered REFERENCES/CASCADE/etc. from field names.

### Added (sesja 14 — doctor, publish, deploy directives)
- **`doql doctor`** — comprehensive 9-check health diagnostic: parse validation,
  env vars coverage, file references, database config, interface consistency,
  required tools on PATH, deploy config, environment definitions. Optional
  `--env <name>` runs remote SSH diagnostics (connectivity, runtime, disk space).
- **`doql build --no-overwrite`** — merge-friendly build that generates into temp
  directory and copies only new files to `build/`, skipping existing ones.
- **Deploy directives `@local`/`@push`/`@remote`** — CSS tokenizer updated to accept
  `@`-prefixed property names. New `Deploy.directives: dict[str, str]` field. Parsed
  in `_map_deploy`, rendered in `_render_deploy`. `doql deploy` executes them in
  order: local → push → remote, falling back to docker-compose if no directives.
- **`doql publish`** — publish artifacts to PyPI (twine), npm, Docker/Podman registries,
  GitHub Releases (gh CLI). Flags: `--target pypi,npm,docker,github`, `--dry-run`.
- **Test suite: 130 passed**, 3 skipped (pygls, 2× psycopg2).
- **CLI: 19 subcommands** (added: adopt, doctor, publish).

### Fixed (sesja 14)
- **Workflow generator** — `_step_fn_name()` sanitizes special characters (`+`, etc.)
  from step action names, preventing invalid Python function names like
  `step_hash_+_sign_certificate_pdf`.

#### Project metrics (sesja 14)
| Metric | Value |
|--------|-------|
| Source files | 92 |
| Lines of code | ~10,500 |
| Tests | 130 passed, 3 skipped |
| CLI subcommands | 19 |
| Examples | 10 |
| Plugins | 4 |
| Scaffold templates | 4 |

### W toku
- Parser tree-sitter (pełna gramatyka `.doql`, error recovery)
- Rozszerzenie VS Code o `.doql.css` / `.doql.less` / `.doql.sass`
- Pilot w realnej firmie

### Refactored (sesja 11 — static-analysis-driven refactoring)
- **css_exporter split** — 423-line monolith `css_exporter.py` → package
  `doql/exporters/css/` (`helpers.py`, `renderers.py`, `format_convert.py`,
  `__init__.py`). Old module kept as backward-compat re-export shim.
- **markdown_exporter split** — 225-line `markdown_exporter.py` → package
  `doql/exporters/markdown/` (`sections.py`, `writers.py`, `__init__.py`).
  Old module kept as backward-compat shim.
- **css_parser extract** — `_tokenise_css` and `_parse_declarations`
  extracted to `doql/parsers/css_tokenizer.py` (was inline in 213-line
  `css_parser.py`).
- **Shared `_clean`** — recursive dict cleaner extracted from
  `yaml_exporter.py` to `doql/utils/clean.py`.
- **`_createBuildFunction` split** — 110-line Python string template
  extracted from `playground/pyodide-bridge.js` to standalone
  `playground/doql_build.py` with 6 named helpers (`_collect_parse_errors`,
  `_build_env`, `_validate`, `_spec_summary`, `_try_generate`, `build`).
  JS now fetches the `.py` file at boot time.
- **yaml_importer docstrings** — added docstrings to all 17 builder
  functions in `doql/importers/yaml_importer.py`.

### Fixed (sesja 11)
- **`gen_auth` indentation bug** — multi-line `user_model_def` interpolated
  inside `textwrap.dedent(f'...')` broke line alignment; `auth.py` started
  with unexpected indent for specs without a `User` entity
  (e.g. calibration-lab). Fixed via `textwrap.indent` pre-alignment.

### Added (sesja 12 — full runtime testing)
- **`tests/test_runtime.py`** — 18 new pytest tests: 8 API boot+health
  tests (uvicorn launched per example, /health + /openapi.json verified)
  and 10 build-target artifact checks (web/mobile/desktop/infra per example).
- **`test_generators.py`** expanded from 5 → 10 examples (added blog-cms,
  crm-contacts, e-commerce-shop, notes-app, todo-pwa).
- **`runtime_all_examples.sh`** updated: all 10 examples, auto-skip
  postgres-dependent APIs, `auth.py` compile check, `python-multipart`
  auto-install in runtime venv.
- **Test suite: 120 tests** (99 → 120), 4 skipped
  (2 sqlalchemy plugin, 2 psycopg2/postgres).

### Fixed (sesja 12)
- **Runtime `python-multipart`** — generated `auth.py` uses
  `OAuth2PasswordRequestForm` (form data) which requires
  `python-multipart`; added to runtime venv deps.

#### Metrics (before → after)
| Metric | Before | After | Target |
|--------|--------|-------|--------|
| CC avg | 3.20 | 3.11 | < 2.5 |
| God modules (>300L) | 7 | 5 | 0 |
| Fan-out ≥ 8 | 20 | 9 | < 10 |
| Import cycles | 2 | 0 | 0 |

### Added (sesja 10 — CSS-like format + export/import + examples)
- **CSS-like parser** — full parser for `.doql.css`, `.doql.less`, `.doql.sass`
  formats (9 modules: `css_parser`, `css_utils`, `css_mappers`,
  `css_transformers`). All formats produce identical `DoqlSpec`.
- **LESS variables** (`@var`) and **SASS variables** (`$var`) are resolved
  during parsing; result is variable-free `DoqlSpec`.
- **Auto-detection** — `detect_doql_file()` priority:
  `.doql.less` > `.doql.sass` > `.doql.css` > `.doql`
- **Exporters** — `doql/exporters/`: `yaml_exporter.py`, `markdown_exporter.py`,
  `css_exporter.py` (supports CSS, LESS, SASS output).
- **Importer** — `doql/importers/yaml_importer.py`: YAML → `DoqlSpec`.
- **CLI `import` command** — `doql import spec.yaml -o app.doql`.
- **CLI `export` formats** expanded: `yaml`, `markdown`, `css`, `less`, `sass`
  (in addition to existing `openapi`, `postman`, `typescript-sdk`).
- **5 new examples**: `blog-cms` (SASS), `crm-contacts` (LESS),
  `e-commerce-shop` (CSS), `notes-app` (SASS), `todo-pwa` (CSS).
  Each example has both classic `.doql` and CSS-like format.
- **Test suite expanded** to **99 tests** (from 38): 13 CSS parser tests,
  28 exporter tests, plus parametrized example validation.

### Fixed (sesja 10)
- **Validator**: absolute DATA file paths (e.g. `/var/lib/kiosk/...`) now
  produce warnings instead of errors — they are deployment targets.
- **Validator**: env wildcard patterns (`env.SMTP_*`) no longer produce
  false-positive warnings. Prefix matching implemented for trailing `_` refs.
- **validate command**: now uses `detect_doql_file()` instead of hardcoded
  `"app.doql"` — correctly finds CSS-like format files.
- **asset-management example**: added missing `User` entity (referenced by
  `Station.manager`).
- **calibration-lab example**: added missing `Operator` entity (referenced by
  `Calibration.performed_by` / `reviewed_by`).
- **SPEC.md updated** to v0.2.1 — added sections 16 (CSS-like syntax),
  17 (Export/Import).

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
- **Test suite** — 99 pytest tests covering parser, CSS parser, exporters,
  generators, plugins, LSP + GUM numerics; `tests/runtime_deploy.sh` end-to-end runtime smoke;
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


## [0.1.2] - 2026-04-18

### Docs
- Update README.md

## [0.1.1] - 2026-04-18

### Other
- Update Taskfile.yml
- Update VERSION
- Update doql/__init__.py
- Update doql/parsers/css_transformers.py
- Update pyqual.yaml

## [0.0.3] - 2026-04-18

### Docs
- Update README.md

### Other
- Update doql/adopt/scanner/__init__.py
- Update doql/adopt/scanner/environments.py
- Update doql/generators/workflow_gen.py
- Update doql/parsers/css_mappers.py
- Update doql/parsers/css_transformers.py

## [0.0.2] - 2026-04-17

### Docs
- Update GLOSSARY.md
- Update README.md
- Update articles/01-oqlos-status-2026-q2.md
- Update articles/02-testql-status-2026-q2.md
- Update articles/05-wizja-ekosystemu-oqlos.md
- Update articles/06-doql-v02-dokumenty-kiosk.md

### Other
- Update doql/__init__.py
- Update examples/asset-management/app.doql.css

## [0.0.1] - 2026-04-17

### Docs
- Update README.md
- Update TODO/01-doql-format-migration-analysis.md
- Update TODO/02-doql-css-iot-fleet-example.md
- Update TODO/03-doql-less-calibration-lab-example.md
- Update TODO/04-doql-sass-notes-app-example.md
- Update TODO/05-doql-migration-guide.md
- Update TODO/README.md
- Update docs/README.md
- Update examples/notes-app/build/desktop/README.md
- Update project/README.md
- ... and 1 more files

### Test
- Update test_all_desktop.yml
- Update test_desktop_builds.yml
- Update test_playbook.yml

### Other
- Update .gitignore
- Update doql.sh
- Update doql/cli.py
- Update doql/cli/__init__.py
- Update doql/cli/build.py
- Update doql/cli/commands/__init__.py
- Update doql/cli/commands/deploy.py
- Update doql/cli/commands/docs.py
- Update doql/cli/commands/export.py
- Update doql/cli/commands/generate.py
- ... and 57 more files

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
