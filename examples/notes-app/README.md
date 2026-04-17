# Notes — full-stack doql example

Generates **all four targets** from a single `app.doql`:

| Target | Tech | Start |
|--------|------|-------|
| API | FastAPI + SQLite | `cd build/api && uvicorn main:app --port 8100` |
| Web | React + Vite | `cd build/web && npm install && npm run dev` |
| Mobile | Installable PWA | `cd build/mobile && python3 -m http.server 8090` |
| Desktop | Tauri | `cd build/desktop && npm install && npm run dev` |

## Quick full-stack demo

```bash
cp .env.example .env
doql validate
doql build --force

# Start API + Traefik via docker (web + mobile auto-mounted)
cd build/infra && docker compose -f docker-compose.localhost.yml up -d --build
# → http://notes.localhost/        (API)
# → http://notes.localhost/docs    (Swagger)
# → http://notes.localhost/m/      (PWA, installable)
```

## Formats

- `app.doql` — classic DOQL format
- `app.doql.sass` — SASS variant with `$variables`, `@mixin`/`@include`, whitespace-based

## Entities

- **Notebook** — groups notes
- **Note** — title/body + tags + pin
- **Tag** — shared taxonomy

## What the PWA does

- Tap tabs to switch between `Notebook`, `Note`, `Tag`
- `+` FAB opens a quick-create form
- Works offline via service-worker cache
- Installable on Android/iOS via "Add to Home Screen"
