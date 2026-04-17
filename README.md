# Rodzina OQL — paczka kompletna


## AI Cost Tracking

![PyPI](https://img.shields.io/badge/pypi-costs-blue) ![Version](https://img.shields.io/badge/version-0.0.1-blue) ![Python](https://img.shields.io/badge/python-3.9+-blue) ![License](https://img.shields.io/badge/license-Apache--2.0-green)
![AI Cost](https://img.shields.io/badge/AI%20Cost-$0.75-orange) ![Human Time](https://img.shields.io/badge/Human%20Time-8.7h-blue) ![Model](https://img.shields.io/badge/Model-openrouter%2Fqwen%2Fqwen3--coder--next-lightgrey)

- 🤖 **LLM usage:** $0.7500 (5 commits)
- 👤 **Human dev:** ~$871 (8.7h @ $100/h, 30min dedup)

Generated on 2026-04-17 using [openrouter/qwen/qwen3-coder-next](https://openrouter.ai/qwen/qwen3-coder-next)

---

**Data wydania:** 2026-04-16  
**Zawartość:** repo `doql/` + repo `articles/` + ten README

---

## Co jest w tej paczce

### `doql/` — nowy projekt: generator deklaratywny
Kompletny projekt **doql** — warstwa deklaratywna nad `oqlos`, która z jednego pliku `.doql` generuje aplikacje, dokumenty, kioski, integracje API. Licencja Apache 2.0 (open core).

**Kluczowe dokumenty:**
- `README.md` — wprowadzenie, quick start, link do wszystkich sekcji
- `SPEC.md` — pełna specyfikacja języka v0.2 (16 sekcji, wszystkie typy artefaktów)
- `GLOSSARY.md` — **jednoznaczna semantyka OQL / DOQL / IQL** (niezbędne, jeśli komunikujesz projekt publicznie)
- `OQLOS-REQUIREMENTS.md` — lista zmian w oqlos (8 wymagań: 5 krytycznych, 3 dodane przy v0.2)
- `ROADMAP.md` — fazy 0-3 rozwoju, ~8 tygodni do produkcji
- `CHANGELOG.md` — historia wersji v0.1 i v0.2

**Dziesięć przykładów (gotowych `.doql` / `.doql.css` / `.doql.less` / `.doql.sass`):**
- `examples/asset-management/` — klon Drägerware, pełen SaaS dla BHP (`.doql` + `.doql.css`)
- `examples/calibration-lab/` — laboratorium ISO 17025 z 4-eyes i WORM (`.doql` + `.doql.less`)
- `examples/iot-fleet/` — flota RPi z OTA canary i Prometheus (`.doql` + `.doql.less`)
- `examples/document-generator/` — generator PDF bez backendu (`.doql` + `.doql.less`)
- `examples/kiosk-station/` — stanowisko operatora na tablecie (`.doql` + `.doql.css`)
- `examples/notes-app/` — full-stack demo: API + web + mobile + desktop (`.doql` + `.doql.sass`)
- `examples/todo-pwa/` — minimalna aplikacja PWA mobile-first (`.doql` + `.doql.css`)
- `examples/blog-cms/` — prosty blog CMS z tagami i komentarzami (`.doql.sass`)
- `examples/crm-contacts/` — kontakty CRM z pipeline sprzedaży (`.doql.less`)
- `examples/e-commerce-shop/` — sklep e-commerce z koszykiem i zamówieniami (`.doql.css`)

**Infrastruktura projektu:**
- `pyproject.toml` — pakowanie Python
- `doql/cli/` — CLI z 15 komendami: init/validate/plan/build/run/deploy/sync/export/import/generate/render/query/kiosk/quadlet/docs
- `doql/parsers/` — parser classic `.doql` + CSS-like parser (`.doql.css`, `.doql.less`, `.doql.sass`)
- `doql/exporters/` — eksport do YAML, Markdown, CSS/LESS/SASS
- `doql/importers/` — import z YAML do `.doql`
- `doql/generators/` — generatory: API, Web, Mobile, Desktop, Infra, Documents, Reports, i18n, Workflow, CI
- `doql/scaffolds/minimal/` — szablon dla `doql init` 
- `LICENSE` (Apache 2.0)
- `.gitignore` 

### `articles/` — artykuły WordPress
Sześć artykułów markdown z YAML front-matter gotowych do publikacji (kompatybilne z `wp-cli` i WordPress REST API). Każdy artykuł to jeden projekt / jedna nowość.

**Lista:**
1. `01-oqlos-status-2026-q2.md` — status oqlos po refaktorze (CC̄ 3,7→3,2)
2. `02-testql-status-2026-q2.md` — TestQL, porównanie z Playwright
3. `03-saas-www-status-2026-q2.md` — SaaS oqlos.com, 5 bugów P0, diagnoza landingu
4. `04-doql-ogloszenie.md` — ogłoszenie doql v0.1 (SaaS generator)
5. `05-wizja-ekosystemu-oqlos.md` — wizja całej rodziny (4 warstwy, strategia open-core)
6. `06-doql-v02-dokumenty-kiosk.md` — doql v0.2 (dokumenty, kiosk, semantyka)

Każdy 800-1800 słów, po polsku, gotowy do kopiuj-wklej do WordPressa.

---

## Jak to odpalić

### Instalacja doql (po sklonowaniu do repo)

```bash
cd doql/
pip install -e .
doql --version
```

### Szybki test — generator PDF

```bash
doql init --template document-generator my-lab
cd my-lab
cp .env.example .env
doql validate
doql plan
```

### Szybki start z CLI shell

Użyj skryptu `doql.sh` do generowania i uruchamiania aplikacji jedną komendą:

```bash
# Generuj i uruchom desktop app
./doql.sh examples/notes-app/app.doql desktop

# Generuj i uruchom web
./doql.sh examples/notes-app/app.doql web

# Generuj i uruchom API
./doql.sh examples/notes-app/app.doql api

# Generuj wszystko
./doql.sh examples/notes-app/app.doql all
```

CLI shell automatycznie:
- Waliduje specyfikację
- Planuje generację
- Generuje wszystkie artefakty
- Uruchamia aplikację (desktop/web/api)

### Publikacja artykułów

Opcja A — ręcznie do WP (najprostsze):
1. Skopiuj treść pliku `.md` bez front-matter
2. Wklej w edytorze WordPress (tryb Markdown jeśli masz plugin)
3. Tytuł, slug, kategorie, tagi z YAML front-matter

Opcja B — `wp-cli`:
```bash
for file in articles/*.md; do
  # yq wyciąga pola z front-matter, sed wycina YAML z body
  title=$(yq -r '.title' "$file")
  slug=$(yq -r '.slug' "$file")
  body=$(sed '/^---$/,/^---$/d' "$file")
  wp post create --post_title="$title" --post_name="$slug" \
    --post_content="$body" --post_status=publish
done
```

Opcja C — GitHub Action z WP REST API (plik `.github/workflows/publish.yml` — nie dołączony, łatwo dopisać).

---

## Formaty plików `.doql`

doql obsługuje cztery równoważne formaty specyfikacji:

| Format | Rozszerzenie | Styl |
|--------|-------------|------|
| Classic | `.doql` | indentacja YAML-like |
| CSS | `.doql.css` | `entity[name="X"] { ... }` |
| LESS | `.doql.less` | CSS + zmienne `@var` |
| SASS | `.doql.sass` | CSS + zmienne `$var`, indent-based |

Wszystkie formaty parsują się do tego samego `DoqlSpec` — można mieszać w projekcie i konwertować:

```bash
# Eksport do innego formatu
doql export --format less -o spec.doql.less

# Import z YAML
doql import spec.yaml -o app.doql
```

Każdy example zawiera zarówno wersję `.doql` jak i wersję CSS-like (`.doql.css` / `.doql.less` / `.doql.sass`).

---

## Architektura — jak się to wszystko łączy

```
┌─────────────────────────────────────────────┐
│   doql file (.doql / .doql.css / .less / …) │
│   deklaracja CO ma powstać                  │
└──────────────┬──────────────────────────────┘
               │  doql build
               ▼
   ┌───────────┴───────────┬──────────────┬─────────────┐
   ▼                       ▼              ▼             ▼
 ┌────┐   ┌────┐   ┌──────────┐   ┌────────┐   ┌──────────┐
 │API │   │Web │   │ Mobile/  │   │Kiosk   │   │Documents │
 │    │   │    │   │ Desktop  │   │        │   │PDF/HTML  │
 └─┬──┘   └────┘   └──────────┘   └────────┘   └──────────┘
   │
   │ wywołuje scenariusze .oql
   ▼
 ┌────────────────────────────────────┐
 │ oqlos runtime (interpretuje .oql)  │
 └──────────────┬─────────────────────┘
                │ Modbus / MQTT / USB / GPIO
                ▼
         ┌────────────┐
         │  Hardware  │
         └────────────┘
```

Testy aplikacji (`.iql`) → testql → Playwright-alternative z integracją hardware.

---

## Co dalej

**Zrealizowane (Fazy 0–3):**
- ✅ Parser `.doql` v0.2 (16 sekcji) + CSS-like parser (`.doql.css` / `.doql.less` / `.doql.sass`)
- ✅ 10 przykładów z walidacją i budowaniem
- ✅ Generatory: API (FastAPI), Web (React+Vite), Mobile (PWA), Desktop (Tauri v2), Infra, Documents, Reports
- ✅ Plugin system + 4 pluginy (GxP, ISO17025, Fleet, ERP)
- ✅ Eksport/Import: YAML, Markdown, CSS/LESS/SASS, OpenAPI, Postman, TypeScript SDK
- ✅ LSP server dla VS Code + playground online (Pyodide)
- ✅ 99 testów pytest, CI matrix 3.10–3.13

**Następne kroki:**
- Certyfikacja deweloperów (`Doql Certified Developer`)
- Parser tree-sitter (pełna gramatyka, error recovery)
- Rozszerzenie VS Code o wsparcie `.doql.css` / `.doql.less` / `.doql.sass`
- Pilot w realnej firmie (lab kalibracyjny w Gdańsku)

**Q3-Q4:**
- Marketplace szablonów `.doql` 
- Premium plugins (GxP, ISO 17025, Fleet)
- Walidacja drugiego segmentu ICP (pharma / medtech)

---

## Licencja

- **doql** i wszystkie jego przykłady — Apache 2.0
- **articles** — CC BY 4.0 (można cytować i tłumaczyć z atrybucją)

Premium plugins doql (komercyjne) — osobne warunki, patrz `doql/LICENSE`.

---

## Kontakt

- Repo główne: github.com/softreck/oqlos
- Repo doql: github.com/softreck/doql
- Email: hello@softreck.dev


## License

Licensed under Apache-2.0.
