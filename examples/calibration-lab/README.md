# Calibration Lab Manager — ISO 17025 doql example

ISO/IEC 17025 compliant calibration laboratory management system.

## Formaty

- `app.doql` — oryginalny format DOQL
- `app.doql.less` — wariant LESS ze zmiennymi dla multi-env (dev/staging/prod)

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/calibration-lab my-lab
cd my-lab

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz bazy danych

# 3. Waliduj deklarację
doql validate

# 4. Zobacz plan generowania
doql plan

# 5. Wygeneruj cały kod
doql build
# → build/api/        FastAPI backend
# → build/web/        React SPA
# → build/infra/      Quadlet containers

# 6. Uruchom wybrany target (patrz sekcja niżej)

# 7. Deploy na produkcję
doql deploy --env prod
```

---

## Uruchamianie aplikacji

### API (FastAPI)

```bash
cd build/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Dokumentacja API: http://localhost:8000/docs

### Web (React + Vite)

```bash
cd build/web
npm install
npm run dev  # dev mode na http://localhost:5173
# lub
npm run build && npm run preview  # production build
```

### Quadlet (Podman)

```bash
cd build/infra
podman-compose up
```

**Uwaga:** `doql run` próbuje uruchomić pełny stack — może się nie udać jeśli port 8000 jest już zajęty.

---

## Entities

- **Instrument** — calibrated devices with computed next_calibration
- **ReferenceStandard** — traceable reference standards (NIST/PTB/GUM)
- **Calibration** — 4-eyes principle, GUM-compliant uncertainty
- **Customer** — external clients
- **CalibrationOrder** — intake workflow with priority

## Key features

- **ISO 17025 compliance** — 4-eyes validation, audit trail, certificate signing
- **XAdES digital signatures** — EU-compliant certificate signing
- **WORM storage** — S3 with Object Lock for 10-year retention
- **Multi-language** — pl, en, de
