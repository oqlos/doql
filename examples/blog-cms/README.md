# Blog CMS

DOQL example — blog/CMS with posts, categories, comments, media management.

## Features

- Post management with draft/review/publish workflow
- Category hierarchy with nested categories
- Comment system with moderation
- Media file upload with S3 storage
- Email notifications for new posts and comments
- PWA-enabled React frontend
- Role-based access (admin, editor, writer, public)

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.sass` — format SASS z wcięciami i zmiennymi $variables

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/blog-cms my-blog
cd my-blog

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz DOMAIN, S3 credentials

# 3. Waliduj deklarację
doql validate

# 4. Zobacz plan generowania
doql plan

# 5. Wygeneruj cały kod
doql build
# → build/api/        FastAPI backend
# → build/web/        React SPA
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

### Docker Compose

```bash
cd build/infra
docker-compose up
```

**Uwaga:** `doql run` próbuje uruchomić pełny stack Docker — może się nie udać jeśli port 8000 jest już zajęty.
