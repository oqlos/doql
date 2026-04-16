# Changelog

Wszystkie istotne zmiany w projekcie `doql`. Format oparty na [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

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
