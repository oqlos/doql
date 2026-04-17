# CRM Contacts

DOQL example — CRM with contacts, companies, deals pipeline, and activity tracking.

## Features

- Contact management with tags and source tracking
- Company directory with industry classification
- Deal pipeline with kanban board (lead → won/lost)
- Activity tracking (calls, emails, meetings, tasks)
- Automated deal stage notifications
- Daily overdue activity reminders
- Role-based access (admin, sales, viewer)

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.less` — format LESS ze zmiennymi @variables

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/crm-contacts my-crm
cd my-crm

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz DOMAIN, bazy danych

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
