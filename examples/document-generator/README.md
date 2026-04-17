# Example: Document Generator

Przykład doql pokazujący, że **z jednego pliku `.doql` można zbudować generator dokumentów PDF** — bez ciężkiego backendu, SaaS-owej oprawy, bez własnej bazy danych. Szablon HTML + dane z JSON/SQLite/API + `doql build` = gotowy generator.

**Use case:** laboratorium kalibracyjne wystawiające świadectwa ISO 17025.

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.less` — wariant LESS z zmiennymi dla multi-env

---

## Co ten przykład pokazuje

1. **Dane z wielu źródeł jednocześnie** — JSON (klienci, organizacja), SQLite (katalog przyrządów), API oqlos (pomiary live), ENV (sekrety i override'y).
2. **Reużywalne szablony HTML** — `letterhead`, `measurement_table`, `signature_block` użyte w certyfikacie głównym i raporcie niezgodności.
3. **Generowanie PDF z podpisem cyfrowym** — PAdES dla zgodności z regulacjami.
4. **Lekki web UI do manualnego generowania** — htmx, kilka formularzy, podgląd live PDF.
5. **Publiczna weryfikacja certyfikatu** — endpoint `/verify/{id}` bez logowania.
6. **Workflow auto-generowania** — webhook z oqlos → automatyczny certyfikat po kalibracji.
7. **Miesięczny raport scheduled** — `REPORT` z agregacją, e-mailem do quality managera.
8. **Deploy jako Quadlet + Traefik + Let's Encrypt** — rootless Podman, jeden kontener.

---

## Szybki start

```bash
cp -r doql/examples/document-generator my-lab
cd my-lab

# Uzupełnij dane
$EDITOR data/organization.json
$EDITOR data/customers.json
# (instruments.db możesz wygenerować przez seed SQL)

# Sekrety
cp .env.example .env
$EDITOR .env           # JWT_SECRET, SIGNING_KEY_PATH, OQLOS_URL, etc.

# Generuj
doql build

# Wywołaj generowanie pojedynczego certyfikatu (bez web UI)
doql generate calibration_certificate \
    --instrument-id "INST-001" \
    --execution-id "exec-abc" \
    --customer-id "cust-001" \
    --operator "Jan Kowalski" \
    --reviewer "Anna Nowak"

# → plik: certs/INST-001_2026-04-16.pdf

# Albo uruchom web UI
doql run
# → http://localhost:8080 — formularz + podgląd live
```

---

## Wygenerowane artefakty

```
build/
├── generator/                       # Python — silnik szablonów
│   ├── app.py                       # entry point
│   ├── data_sources.py              # loadery JSON/SQLite/API
│   ├── documents.py                 # definicje DOCUMENT
│   ├── templates/                   # skopiowane szablony
│   └── sign.py                      # PAdES signer
│
├── web/                             # htmx UI
│   ├── index.html                   # formularz
│   ├── verify.html                  # publiczna weryfikacja
│   └── static/
│
├── api/                             # FastAPI endpoint dla webhooks
│   ├── main.py
│   └── routes/
│       ├── certificates.py
│       └── webhooks.py
│
└── infra/
    ├── quadlet/
    │   ├── doqgen.container
    │   ├── doqgen-web.container
    │   └── traefik.container
    └── install.sh
```

---

## Co zostaje wygenerowane z `DOCUMENT calibration_certificate`

Generator bierze Twoją deklarację:

```doql
DOCUMENT calibration_certificate:
  type: pdf
  template: templates/cert_iso17025.html
  data:
    instrument: DATA instruments WHERE id = $args.instrument_id
    ...
```

I produkuje:

1. **Funkcję Python** `generate_calibration_certificate(instrument_id, ...)` — callable z innych miejsc
2. **Endpoint REST** `POST /certificates` — z walidacją inputu
3. **CLI** `doql generate calibration_certificate --...`
4. **Podpis cyfrowy** PAdES przez wywołanie lokalnego tool'a
5. **Hook po generowaniu** — audit log + email (jeśli klient ma email)

Wszystko w Twoim poddanym review kodzie — nie magii.

---

## Porównanie z alternatywami

| Sposób | Czas do działającego | Wymagania | Uwagi |
|--------|---------------------|-----------|-------|
| Własny Python + Jinja + WeasyPrint | 1-2 tygodnie | wiedza Python | pełna kontrola, trzeba obsłużyć wszystko |
| Python + Jinja + FastAPI + web UI | 3-4 tygodnie | wiedza Python + frontend | j.w. + web |
| **doql (ten przykład)** | **1 dzień** | tylko znajomość `.doql` | mniej kontroli, ale działa od razu |
| SaaS (DocuSeal, PandaDoc) | 30 min | account, monthly fee | vendor lock-in, koszty skalujące |
| Microsoft Power Automate | 1 tydzień | M365 license | ciężkie, zamknięte |

---

## Co jeszcze można dodać

W `app.doql` brakuje — bo to przykład minimalny, ale łatwo dorzucisz:

- **Wielojęzyczność** — `DOCUMENT calibration_certificate_en` z tym samym szablonem w EN
- **Batch generowanie** — `doql generate-batch --input data/batch.json` → 100 PDF-ów
- **Archiwizacja WORM** — `output.storage: s3` z Object Lock dla ISO retention
- **QR weryfikacyjny na każdym cert** — już zadeklarowane w `DOCUMENT qr_label`
- **Template override per customer** — różne layouty dla różnych klientów
- **Historia zmian** — jeśli certyfikat reissue'owany, poprzednia wersja zachowana

---

## Znane ograniczenia

1. **Podpis PAdES wymaga klucza w infrastrukturze** — w dev możesz self-signed, ale do produkcji kwalifikowany certyfikat od NCCert / Sigillum / EuroCert.
2. **Template HTML → PDF przez WeasyPrint** — nie wszystkie CSS3 działają (flexbox ok, grid częściowo, animacje nie).
3. **Weryfikacja podpisu** wymaga publicznego URL z klucza — sprawdź `VERIFY_BASE_URL` w .env.
