# Articles — WordPress-Ready

Repozytorium artykułów markdown gotowych do opublikowania na WordPress. Każdy plik to jeden artykuł o statusie konkretnego projektu w organizacji Softreck.

## Jak to działa

Każdy plik markdown zawiera front-matter YAML z metadanymi WordPress (tytuł, slug, kategorie, tagi, data) oraz treść w standardowym markdown/HTML. Można publikować przez:

- **Ręcznie:** kopiuj-wklej do edytora WordPress (tryb HTML/Markdown)
- **Automatycznie:** `wp-cli` + skrypt który parsuje front-matter
- **GitHub Action:** push do tego repo → publikacja na WP przez REST API

## Skrypt publikacji (sugerowany)

```bash
# Przykład — wp-cli
for file in *.md; do
  wp post create \
    --post_title="$(yq .title $file)" \
    --post_content="$(mdextract-body $file)" \
    --post_status=publish \
    --post_category="$(yq .categories $file)"
done
```

Lub używając WordPress REST API: zobacz `scripts/publish.py` (TODO).

## Indeks artykułów

| # | Plik | Projekt | Typ | Słowa | Status |
|---|------|---------|-----|-------|--------|
| 01 | [`01-oqlos-status-2026-q2.md`](./01-oqlos-status-2026-q2.md) | oqlos | status update | ~1400 | draft |
| 02 | [`02-testql-status-2026-q2.md`](./02-testql-status-2026-q2.md) | testql | status update | ~1500 | draft |
| 03 | [`03-saas-www-status-2026-q2.md`](./03-saas-www-status-2026-q2.md) | www / SaaS | status update | ~1600 | draft |
| 04 | [`04-doql-ogloszenie.md`](./04-doql-ogloszenie.md) | doql | announcement | ~1800 | draft |
| 05 | [`05-wizja-ekosystemu-oqlos.md`](./05-wizja-ekosystemu-oqlos.md) | cała rodzina | vision | ~1500 | draft |
| 06 | [`06-doql-v02-dokumenty-kiosk.md`](./06-doql-v02-dokumenty-kiosk.md) | doql | status/announcement | ~1700 | draft |

**Kolejność publikacji (sugerowana):**
1. Najpierw `01`, `02`, `03` (status każdego istniejącego projektu) — tydzień 1
2. Potem `05` (wizja — spina istniejące projekty w ekosystem) — tydzień 2
3. Potem `04` (ogłoszenie doql — nowy projekt, na fundamencie istniejących) — tydzień 3
4. Na koniec `06` (rozszerzenie doql o dokumenty + kiosk, wersja 0.2) — tydzień 4

Taka sekwencja buduje narrację: *mamy działające projekty → mamy spójną wizję → ogłaszamy nowy krok → rozszerzamy go o nowe zakresy.* Każdy kolejny artykuł odwołuje się do poprzednich, co z kolei buduje wewnętrzne linkowanie SEO.

## Konwencje

- Nazwa pliku: `NN-project-typ-[yyyy-qn].md` (zero-padded, lowercase, myślniki)
- Język: polski (ewentualnie dwujęzyczne sekcje PL/EN — front-matter `language: bilingual`)
- Długość: 800–2500 słów (artykuły statusowe), 1500–4000 słów (announcement, vision)
- Obrazki: ścieżki względne `./images/NN-nazwa.png` — wrzuć do Media Library WP przed publikacją
- Linki wewnętrzne: użyj `{{site_url}}` placeholder, zastąp przy publikacji

## Licencja

CC BY 4.0 — treść można dowolnie cytować i tłumaczyć z atrybucją.
