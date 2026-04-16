# Rodzina OQL — paczka kompletna

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

**Pięć przykładów (gotowych `.doql`):**
- `examples/asset-management/` — klon Drägerware, pełen SaaS dla BHP
- `examples/calibration-lab/` — laboratorium ISO 17025 z 4-eyes i WORM
- `examples/iot-fleet/` — flota RPi z OTA canary i Prometheus
- `examples/document-generator/` — **nowy w v0.2** — tylko generator PDF bez backendu
- `examples/kiosk-station/` — **nowy w v0.2** — stanowisko operatora na tablecie

**Infrastruktura projektu:**
- `pyproject.toml` — pakowanie Python
- `doql/cli.py` — szkielet CLI z komendami init/validate/plan/build/run/deploy/sync/export/generate/render/query/kiosk/quadlet/docs
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

## Architektura — jak się to wszystko łączy

```
┌─────────────────────────────────────────────┐
│   doql file (.doql)                         │
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

**Tydzień 1 (najpilniejsze):**
- Naprawić 5 bugów P0 w www (szczegóły w artykule 03)
- Uzupełnić `en.json` i dodać `de.json` (targi w Niemczech)
- Dokończyć parser `.doql` v0.2

**Tydzień 2-4:**
- Publikować artykuły 01-06 w sekwencji
- Zaimplementować 3 krytyczne wymagania oqlos dla doql
- Pierwszy pilot klient dla doql (rozmowy wstępne toczą się)

**Miesiąc 2-3:**
- Faza 1 doql MVP — pełny generator
- Wdrożenie pilotażowe (lab kalibracyjny w Gdańsku)
- Przygotowanie prezentacji na targi w Niemczech

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
