# E-Commerce Shop

DOQL example — full e-commerce shop with product catalog, cart, orders, payments.

## Features

- Product catalog with categories and search
- Shopping cart with session-based storage
- Order management with status tracking
- Stripe payment integration
- Email notifications for order confirmations
- Role-based access (admin, customer, guest)
- React SPA frontend with multiple pages
- JWT authentication

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.css` — format CSS-like

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/e-commerce-shop my-shop
cd my-shop

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz DOMAIN, Stripe keys

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
