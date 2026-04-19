# doql TODO

## Vision Notes

- doql = deklaratywny język budowania usług, aplikacji, dokumentów, szablonów
- Nie tylko systemy — też dokumenty HTML/MD, pliki JSON, bazy SQLite, dostęp do API
- Łatwe reużycie danych z `.json`, `.env`
- Aplikacje w formacie Docker/Quadlet/Podman/Traefik z desktop/kiosk (mobilna jak w pactown)

## P0 — Stable release blockers

- [ ] `doql adopt` — end-to-end test with real project (oqlos itself)
- [ ] `doql doctor` — add `--fix` flag for auto-remediation of fixable issues
- [ ] pytest coverage: add `pytest-cov` + `.coveragerc`, target ≥ 50%

## P1 — Quality / CC hotspots

- [ ] `doql/adopt/scanner.py` (~400 lines) — split by interface detector type (FastAPI, Flask, CLI, Web)
- [ ] `doql/parsers/css_parser.py` — remaining CC hotspots after sesja 11 refactoring
- [ ] `doql/exporters/` — validate backward-compat shims are tested

## P2 — Features / Backlog

### Language features
- [ ] Tree-sitter parser (full `.doql` grammar, error recovery)
- [ ] `maskservice/workshop` — migrate device management from `maskservice/c2004`:
  - device inventory + location, scan device/barcode QR
  - associated files (PDFs, drivers, reports, certs, invoices)
  - tag/feature filtering + bulk actions
  - tag ID → SQLite ID remapping logic
- [ ] VS Code extension: `.doql.css` / `.doql.less` / `.doql.sass` syntax highlighting

### CLI improvements
- [ ] `doql build --watch` — file watcher for dev loop
- [ ] `doql deploy` — `@local`/`@push`/`@remote`: add rollback support
- [ ] `doql publish --target github` — automated GitHub Release notes from CHANGELOG

## Tests

- [ ] Run `testql run testql-scenarios/generated-api-smoke.testql.toon.yaml`
- [ ] Run `testql run testql-scenarios/generated-api-integration.testql.toon.yaml`
- [ ] Run `testql run testql-scenarios/generated-from-pytests.testql.toon.yaml`
- [ ] Pilot w realnej firmie — zidentyfikować projekt

## ✅ Done

- [x] `doql adopt` — reverse-engineer project into `app.doql.css` (sesja 13)
- [x] `Environment` model — `environment[name="prod"]` with runtime/ssh_host (sesja 13)
- [x] Generated manifests for 5 sibling projects (sesja 13)
- [x] `doql doctor` — 9-check health diagnostic with optional `--env` remote SSH (sesja 14)
- [x] `doql build --no-overwrite` — merge-friendly build (sesja 14)
- [x] Deploy directives `@local`/`@push`/`@remote` (sesja 14)
- [x] `doql publish` — PyPI, npm, Docker, GitHub targets (sesja 14)
- [x] 130 tests passing (sesja 14)
- [x] `css_exporter`, `markdown_exporter` split into packages (sesja 11)
- [x] `css_tokenizer.py` extracted from `css_parser.py` (sesja 11)
- [x] testql-scenarios generated (3 files)
- [x] README AI cost tracking removed; version badge updated to 0.1.3

