# Notes — full-stack doql example

Generates **all four targets** from a single `app.doql`:

| Target | Tech | Start |
|--------|------|-------|
| API | FastAPI + SQLite | `cd build/api && uvicorn main:app --port 8100` |
| Web | React + Vite | `cd build/web && npm install && npm run dev` |
| Mobile | Installable PWA | `cd build/mobile && python3 -m http.server 8090` |
| Desktop | Tauri | `cd build/desktop && npm install && npm run dev` |

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.sass` — wariant SASS ze zmiennymi `$variables`, `@mixin`/`@include`, wcięciami

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/notes-app my-notes
cd my-notes

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz DOMAIN

# 3. Waliduj deklarację
doql validate

# 4. Zobacz plan generowania
doql plan

# 5. Wygeneruj cały kod
doql build
# → build/api/        FastAPI backend
# → build/web/        React SPA
# → build/mobile/     PWA
# → build/desktop/    Tauri desktop
# → build/infra/      docker-compose.yml

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

### Mobile (PWA)

```bash
cd build/mobile
python3 -m http.server 8091
```

Otwórz http://localhost:8091/ w przeglądarce mobilnej Chrome i zainstaluj jako aplikację.

### Desktop (Tauri)

```bash
cd build/desktop
npm install  # tylko przy pierwszym uruchomieniu
npm run dev
```

**Wymagania:**
- Rust toolchain: <https://rustup.rs>
- Node 20+
- System libraries (Linux):
  ```bash
  sudo apt install -y \
      libwebkit2gtk-4.1-dev libsoup-3.0-dev \
      libgtk-3-dev libayatana-appindicator3-dev \
      librsvg2-dev libssl-dev pkg-config build-essential
  ```

### Docker Compose

```bash
cd build/infra
docker-compose up
```

**Uwaga:** `doql run` próbuje uruchomić pełny stack Docker — może się nie udać jeśli port 8000 jest już zajęty.

---

## Entities

- **Notebook** — groups notes
- **Note** — title/body + tags + pin
- **Tag** — shared taxonomy

## What the PWA does

- Tap tabs to switch between `Notebook`, `Note`, `Tag`
- `+` FAB opens a quick-create form
- Works offline via service-worker cache
- Installable on Android/iOS via "Add to Home Screen"
