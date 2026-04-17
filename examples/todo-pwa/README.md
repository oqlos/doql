# Todo PWA — mobile-first doql example

Minimal example showcasing the mobile (PWA) generator.

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.css` — wariant CSS-like (SSOT)

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/todo-pwa my-todo-app
cd my-todo-app

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
# → build/mobile/     PWA (Progressive Web App)
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

### Mobile (PWA)

```bash
cd build/mobile
python3 -m http.server 8091
```

Otwórz http://localhost:8091/ w przeglądarce mobilnej Chrome i zainstaluj jako aplikację z menu adresu.

### Docker Compose

```bash
cd build/infra
docker-compose up
```

---

To test the full stack with Traefik see `tests/env_manager.py`.
