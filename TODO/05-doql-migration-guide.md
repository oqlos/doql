---
title: "DOQL CSS Migration Guide: Jak przeprowadzić migrację z DOQL na doql.css/.less/.sass"
date: 2026-04-17
categories: [doql, oqlos, migracja, dsl]
tags: [DOQL, CSS, LESS, SASS, OQL, migracja, Softreck]
status: publish
excerpt: "Praktyczny przewodnik migracji z obecnego formatu DOQL do nowych formatów doql.css, doql.less i doql.sass. Zawiera mapowanie składni, przykłady transformacji i strategię wdrożenia dla projektów w ekosystemie OqlOS."
---

# DOQL CSS Migration Guide: Praktyczna migracja krok po kroku

Ten artykuł to przewodnik dla deweloperów w ekosystemie Softreck/OqlOS, którzy chcą przenieść istniejące pliki `.doql` do nowych formatów CSS-like.

---

## Mapowanie składni — stary DOQL → doql.css

Poniżej tabela bezpośrednich odpowiedników:

| Stary DOQL | Nowy doql.css | Uwagi |
|---|---|---|
| `APP: "Name"` | `app { name: "Name"; }` | |
| `VERSION: "1.0"` | `app { version: "1.0"; }` | scalamy w blok `app` |
| `DOMAIN: env.X` | `app { domain: env.X; }` | |
| `ENTITY Foo:` | `entity[name="Foo"] { ... }` | |
| `  id: uuid! auto` | `  id: uuid!;` | `auto` → domyślne |
| `  field: type default=x` | `  field: type default=x;` | bez zmian |
| `  COMPUTED status:` | `entity[name="Foo"] computed[name="status"] { ... }` | wydzielony blok |
| `INTERFACE api:` | `interface[type="api"] { ... }` | |
| `  type: rest` | `  type: rest;` | |
| `  auth: jwt` | `  auth: jwt;` | |
| `INTERFACE web:` | `interface[type="web"] { ... }` | |
| `  PAGE name:` | `interface[type="web"] page[name="x"] { ... }` | zagnieżdżony selektor |
| `ROLES:` | *(sekcja `role[name="..."] { ... }`)* | |
| `  user:` | `role[name="user"] { ... }` | |
| `  can: [x, y]` | `  can: [x, y];` | |
| `DEPLOY:` | `deploy { ... }` | |
| `  target: docker-compose` | `  target: docker-compose;` | |
| `WORKFLOW name:` | `workflow[name="name"] { ... }` | |
| `  trigger: schedule "..."` | `  trigger: schedule "...";` | |
| `INTEGRATION name:` | `integration[name="name"] { ... }` | |

---

## Przykład transformacji — Notes App

**Przed (stary DOQL):**

```doql
APP: "Notes"
VERSION: "1.0.0"
DOMAIN: env.DOMAIN

ENTITY Notebook:
  id: uuid! auto
  name: string!
  color: string default=sky
  created: datetime auto

INTERFACE api:
  type: rest
  auth: jwt

INTERFACE mobile:
  type: pwa
  offline: true

ROLES:
  user:
    can: [read_own, write_own]
  admin:
    can: [*]

DEPLOY:
  target: docker-compose
  ingress: traefik
```

**Po (doql.css):**

```css
app {
  name:    "Notes";
  version: "1.0.0";
  domain:  env.DOMAIN;
}

entity[name="Notebook"] {
  id:      uuid!;
  name:    string!;
  color:   string default="sky";
  created: datetime auto;
}

interface[type="api"] {
  type: rest;
  auth: jwt;
}

interface[type="mobile"] {
  type:    pwa;
  offline: true;
}

role[name="user"] {
  can: [read_own, write_own];
}

role[name="admin"] {
  can: [*];
}

deploy {
  target:  docker-compose;
  ingress: traefik;
}
```

**Po (doql.less)** — z zmiennymi dla multi-env:

```less
@auth-method:    jwt;
@deploy-target:  docker-compose;
@ingress:        traefik;

app {
  name:    "Notes";
  version: "1.0.0";
  domain:  env.DOMAIN;
}

entity[name="Notebook"] {
  id:      uuid!;
  name:    string!;
  color:   string default="sky";
  created: datetime auto;
}

interface[type="api"] {
  type: rest;
  auth: @auth-method;

  endpoint[method="GET"][path="/notebooks"] {
    roles: [user, admin];
  }
}

interface[type="mobile"] {
  type:    pwa;
  offline: true;
}

role[name="user"] { can: [read_own, write_own]; }
role[name="admin"] { can: [*]; }

deploy {
  target:  @deploy-target;
  ingress: @ingress;
}
```

**Po (doql.sass)** — whitespace, bez `{}` i `;`:

```sass
$auth-method: jwt
$deploy-target: docker-compose
$ingress: traefik

@mixin standard-deploy($target: docker-compose, $ingress: traefik)
  target: $target
  ingress: $ingress

app
  name: "Notes"
  version: "1.0.0"
  domain: env.DOMAIN

entity[name="Notebook"]
  id: uuid!
  name: string!
  color: string default="sky"
  created: datetime auto

interface[type="api"]
  type: rest
  auth: $auth-method

interface[type="mobile"]
  type: pwa
  offline: true

role[name="user"]
  can: [read_own, write_own]

role[name="admin"]
  can: [*]

deploy
  @include standard-deploy($target: $deploy-target, $ingress: $ingress)
```

---

## Strategia migracji dla organizacji Softreck

### Faza 1 — Narzędzia (tydzień 1–2)

1. Napisać **`doql-migrate` CLI** — automatyczna transformacja `*.doql` → `*.doql.css`
2. Napisać **parser `doql.css`** oparty na `tinycss2` (Python) lub `css-tree` (Node.js)
3. Dodać testy regresji: parser(old) → AST == parser(new) → AST

### Faza 2 — Pilotaż (tydzień 3–4)

1. Zmigrować dwa projekty pilotażowe: `notes-app` i `calibration-lab`
2. Wygenerować z nowych plików istniejące `docker-compose.yml` i `Taskfile.yml`
3. Zweryfikować zgodność z poprzednimi outputami

### Faza 3 — Biblioteka stdlib (tydzień 5–6)

1. Wydzielić `oqlos-stdlib.doql.sass` z mixinami:
   - `@mixin gxp-audit`
   - `@mixin iso17025-cert`
   - `@mixin fleet-ota`
   - `@mixin docker-deploy`
2. Zaktualizować wszystkie projekty do `@import "oqlos-stdlib"`

### Faza 4 — Deprecation (miesiąc 2)

1. Oznaczyć stary format `.doql` jako `@deprecated`
2. Parser nadal obsługuje stary format ale wyświetla warning
3. Oficjalne ogłoszenie w komunikacie targów (Niemcy Q2 2026)

---

## Wpływ na istniejące projekty w organizacji

| Projekt | Obecny format | Docelowy format | Priorytet |
|---|---|---|---|
| `notes-app` | `.doql` | `.doql.sass` (mixin stdlib) | 🟡 medium |
| `calibration-lab` | `.doql` | `.doql.less` (multi-env) | 🔴 high |
| `iot-fleet` | `.doql` | `.doql.less` (multi-platform) | 🔴 high |
| `asset-management` | `.doql` | `.doql.css` (prosty) | 🟢 low |
| `kiosk-station` | `.doql` | `.doql.css` (edge device) | 🟡 medium |
| `todo-pwa` | `.doql` | `.doql.css` (demo) | 🟢 low |
| `document-generator` | `.doql` | `.doql.less` (ISO compliance) | 🔴 high |

---

## Podsumowanie: dlaczego warto migrować?

1. **Standardowe narzędzia** — parsery CSS istnieją dla wszystkich języków programowania
2. **IDE support** — podświetlanie składni, autocompletion z istniejącymi pluginami CSS
3. **Selektywność** — `interface[type="web"][env="prod"]` zamiast płaskiej hierarchii
4. **Skalowalność** — zmienne LESS i mixiny SASS dla dużych projektów
5. **Ekosystem** — jeden `oqlos-stdlib.doql.sass` dla całej organizacji Softreck

Migracja jest **nieniszcząca** — parser może obsługiwać oba formaty jednocześnie przez okres przejściowy. Nowe projekty startują bezpośrednio w formacie CSS-like.

---

*Wszystkie przykłady kodu z tej serii dostępne w repozytorium `doql` w organizacji Softreck pod katalogiem `examples/`.*
