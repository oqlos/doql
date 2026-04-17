# Calibration Lab Manager — ISO 17025 doql example

ISO/IEC 17025 compliant calibration laboratory management system.

| Target | Tech | Start |
|--------|------|-------|
| API | FastAPI + SQLite/PostgreSQL | `cd build/api && uvicorn main:app --port 8102` |
| Web | React + Material UI | `cd build/web && npm install && npm run dev` |

## Quick start

```bash
cp .env.example .env
doql validate
doql build --force

cd build/infra && docker compose -f docker-compose.localhost.yml up -d --build
# → http://calibration-lab.localhost/        (API)
# → http://calibration-lab.localhost/docs    (Swagger)
```

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

## Formats

- `app.doql` — original DOQL format
- `app.doql.less` — LESS variant with variables for multi-env (dev/staging/prod)
