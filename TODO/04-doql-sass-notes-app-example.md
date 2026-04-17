---
title: "Format doql.sass — minimalistyczna składnia whitespace-based dla bibliotek OqlOS"
date: 2026-04-17
categories: [doql, oqlos, sass, dsl]
tags: [DOQL, SASS, OQL, Notes, Softreck, multiplatform]
status: publish
excerpt: "Format .doql.sass inspirowany SASS (Syntactically Awesome Stylesheets) eliminuje nawiasy klamrowe i średniki. Idealny do definiowania bibliotek komponentów i mixinów wielokrotnego użytku w ekosystemie OqlOS."
---

# Format `.doql.sass` — minimalistyczna składnia dla bibliotek OqlOS

Format `[projekt].doql.sass` to **whitespace-based variant** DOQL — taki sam model semantyczny jak `doql.css` i `doql.less`, ale bez nawiasów klamrowych `{}` i średników `;`. Zamiast nich — **wcięcia** (jak Python lub YAML).

Dodaje też mechanizm **`@mixin` / `@include`** — kluczowy dla bibliotek komponentów w ekosystemie OqlOS, gdzie wiele projektów dzieli te same wzorce (ISO 17025 plugin, GxP audit, fleet management).

Plik: `notes-app.doql.sass`

---

## Zmienne i mixiny — bloki wielokrotnego użytku

```sass
// ─── Variables ───────────────────────────────────────────

$app-version: "1.0.0"
$auth-method: jwt
$deploy-target: docker-compose
$ingress: traefik
$offline-support: true

// ─── Mixins ──────────────────────────────────────────────

// Reusable: standard REST API config
@mixin rest-api($auth: jwt, $rate-limit: 1000/min)
  type: rest
  auth: $auth
  rate-limit: $rate-limit

// Reusable: standard web SPA config
@mixin web-spa($framework: react, $theme: tailwind)
  type: spa
  framework: $framework
  theme: $theme

// Reusable: standard docker-compose deploy
@mixin docker-deploy($ingress: traefik)
  target: docker-compose
  ingress: $ingress
  rootless: true

// Reusable: ISO 17025 audit fields
@mixin iso17025-fields
  performed_by: User ref
  reviewed_by: User ref
  certificate: Document ref nullable
  retention
    duration: 10years
    immutable: true

// Reusable: PWA offline config
@mixin pwa-offline
  type: pwa
  offline: $offline-support
  cache-strategy: stale-while-revalidate
  sync-on-reconnect: true
```

---

## Definicja aplikacji

```sass
// ─── App ─────────────────────────────────────────────────

app
  name: "Notes"
  version: $app-version
  domain: env.DOMAIN
  description: "Full-stack personal notes app — REST API + React SPA + PWA + Tauri"
```

---

## Model danych — zagnieżdżony bez nawiasów

```sass
// ─── Entities ────────────────────────────────────────────

entity[name="Notebook"]
  id: uuid! auto
  name: string!
  color: string default="sky"
  created: datetime auto

entity[name="Note"]
  id: uuid! auto
  notebook: Notebook ref
  title: string!
  body: text
  pinned: bool default=false
  tags: [string]
  created: datetime auto
  updated: datetime auto

  // Nested validation rule
  validation[name="title_not_empty"]
    rule: title.length > 0
    error: "Title cannot be empty"

entity[name="Tag"]
  id: uuid! auto
  name: string! unique
  color: string default="slate"
```

---

## Interfejsy z @include mixin

```sass
// ─── Interfaces ──────────────────────────────────────────

interface[type="api"]
  @include rest-api($auth: $auth-method, $rate-limit: 2000/min)

  endpoint[method="GET"][path="/notes"]
    roles: [user, admin]
    filter-by: owner=current_user

  endpoint[method="POST"][path="/notes"]
    body: { title: string!, body: text, notebook_id: uuid, tags: [string] }
    returns: { id: uuid, created: datetime }
    roles: [user, admin]

  endpoint[method="PUT"][path="/notes/{id}"]
    roles: [owner, admin]

  endpoint[method="DELETE"][path="/notes/{id}"]
    roles: [owner, admin]
    soft-delete: true

interface[type="web"]
  @include web-spa($framework: react, $theme: tailwind)

  page[name="home"]
    layout: sidebar
    sidebar
      component: NotebookList
      actions: [create_notebook, select_notebook]
    main
      component: NoteList
      filters: [pinned, tag, search]
    fab[label="New Note"]
      action: open_note_editor

  page[name="note_editor"]
    layout: fullscreen
    editor: markdown
    autosave: true
    autosave-interval: 3s

interface[type="mobile"]
  @include pwa-offline
  install-prompt: true
  share-target: true

interface[type="desktop"]
  type: tauri
  platform: web
  features
    - system_tray
    - global_shortcut: "Ctrl+Shift+N"
    - window-title: "Notes — {current_notebook}"
```

---

## Role z dziedziczeniem

```sass
// ─── Roles ───────────────────────────────────────────────

role[name="user"]
  can: [read_own, write_own, delete_own]
  own-filter: owner = current_user

role[name="admin"]
  can: [*]
  bypass-ownership: true
```

---

## Deploy z mixin

```sass
// ─── Deploy ──────────────────────────────────────────────

deploy
  @include docker-deploy($ingress: $ingress)

  container[name="api"]
    port: 8000
    replicas: 1
    db: sqlite

  container[name="web"]
    port: 3000
    replicas: 1

  backup
    paths: [data/]
    schedule: daily
    retention: 1year
```

---

## Przykład bibliotecznego mixinu dla całego ekosystemu OqlOS

Jeden z kluczowych argumentów za `.doql.sass` w ekosystemie OqlOS to możliwość stworzenia **biblioteki wspólnych mixinów**:

```sass
// plik: oqlos-stdlib.doql.sass
// Można importować w każdym projekcie OqlOS

// GxP compliance mixin
@mixin gxp-audit
  audit-log
    enabled: true
    immutable: true
    retention: 10years
  e-signature
    required: true
    method: totp

// ISO 17025 compliance mixin
@mixin iso17025-cert
  certificate-generation
    method: pades
    standard: ISO/IEC 17025
  drift-monitor
    enabled: true
    threshold: 0.5%

// Fleet management mixin
@mixin fleet-ota
  ota
    strategy: canary
    rollback-on: failure_rate > 1%
    signed: true
  heartbeat
    interval: 60s
    timeout: 5min
```

Następnie w projekcie:

```sass
// calibration-lab.doql.sass

@import "oqlos-stdlib"

deploy
  @include gxp-audit
  @include iso17025-cert
  target: kubernetes
```

---

## Porównanie trzech formatów

| Cecha | `.doql.css` | `.doql.less` | `.doql.sass` |
|---|---|---|---|
| Składnia | `selector { prop: val; }` | jak CSS + zmienne `@` | whitespace, bez `{}` i `;` |
| Zmienne | ❌ | `@var: value` | `$var: value` |
| Mixiny | ❌ | ❌ | ✅ `@mixin` / `@include` |
| Zagnieżdżenia | płaskie atrybuty | bloki zagnieżdżone | wcięcia |
| Import | ❌ | `@import` | `@import` |
| Rekomendowany dla | prostych projektów | multi-env SaaS | biblioteki, stdlib |
| Parser | standardowy CSS | LESS preprocessor | SASS/indented parser |

---

## Kiedy wybrać który format?

- **`.doql.css`** — nowy projekt, jedno środowisko, szybki start
- **`.doql.less`** — projekt z dev/staging/prod, wiele konfiguracji
- **`.doql.sass`** — tworzysz bibliotekę komponentów OqlOS lub chcesz maksymalnej zwięzłości

Wszystkie trzy formaty kompilują się do tego samego **AST DOQL**, który generator przekształca w `docker-compose.yml`, `Taskfile.yml`, `k8s-manifest.yaml` i dokumentację Markdown.

---

*To ostatni artykuł z serii o formatach DOQL CSS-like. Pełna dokumentacja i parser dostępne w repozytorium `doql` w organizacji Softreck.*
