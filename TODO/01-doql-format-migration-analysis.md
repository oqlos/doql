---
title: "DOQL Format Migration: Czy CSS-like DSL to przyszłość konfiguracji aplikacji?"
date: 2026-04-17
categories: [doql, oqlos, dsl, architektura]
tags: [DOQL, DSL, CSS, LESS, SASS, OQL, Softreck]
status: publish
excerpt: "Analiza możliwej migracji formatu DOQL do składni CSS/LESS/SASS. Porównujemy podejście deklaratywne z istniejącym formatem i wskazujemy, dlaczego CSS-like jako format podstawowy ma strategiczne uzasadnienie."
---

# DOQL Format Migration: Czy CSS-like DSL to przyszłość konfiguracji aplikacji?

W ekosystemie **OqlOS / Softreck** format DOQL (Domain-Oriented Query Language) służy do deklaratywnego opisywania pełnych aplikacji — od modelu danych, przez interfejsy API i web, aż po konfigurację deploymentu. W miarę jak platforma rośnie, pojawia się naturalne pytanie: **czy obecna składnia jest optymalna, czy może warto zmigrować do czegoś bliższego powszechnym standardom?**

---

## Obecny format DOQL — mocne strony i ograniczenia

Aktualny DOQL wygląda tak:

```doql
APP: "IoT Fleet Manager"
VERSION: "0.5.0"
DOMAIN: "iot-fleet"

ENTITY Node:
  id: uuid! auto
  hostname: string! unique
  status: enum[online, offline, updating, error] computed

INTERFACE web:
  type: spa
  framework: react
  theme: tailwind

DEPLOY:
  target: kubernetes
  ingress: traefik
```

**Mocne strony:**
- Czytelny dla programistów
- Kompaktowy — mało szumu składniowego
- Dobrze opisuje intencję

**Ograniczenia:**
- Własna, niestandardowa gramatyka — brak narzędzi IDE z pudełka
- Trudniejszy do parsowania automatycznie niż YAML lub CSS-like
- Brak selektywności — nie można łatwo adresować "tylko web w środowisku prod"
- Nie obsługuje natywnie selektorów atrybutowych (`platform`, `env`, `method`)

---

## Dlaczego CSS-like jako format podstawowy?

CSS ma 30 lat produkcyjnego doświadczenia jako **deklaratywny język selektorów i deklaracji**. Jego model:

```
selektor [atrybut="wartość"] {
  właściwość: wartość;
}
```

...jest dokładnie tym, czego potrzebuje nowoczesny DSL do konfiguracji aplikacji wieloplatformowych.

### Kluczowe zalety podejścia CSS-like dla DOQL:

| Cecha | Obecny DOQL | CSS-like DOQL |
|---|---|---|
| Selektywność per platform/env | ❌ brak | ✅ `interface[platform="web"][env="prod"]` |
| Parsowanie maszynowe | średnie | ✅ tokenizacja jak CSS |
| Narzędzia IDE | ❌ tylko własne | ✅ możliwość reuse istniejących parserów |
| Rozszerzalność atrybutów | ograniczona | ✅ dowolne atrybuty selektorów |
| Warianty: LESS, SASS | ❌ | ✅ możliwe zmienne, zagnieżdżenia |

---

## Proponowana architektura formatów

Zamiast jednego formatu, proponujemy **trójwarstwowy ekosystem**:

```
app.config.css    ← PRIMARY (SSOT — Single Source of Truth)
      ↓
   Parser
      ↓ ↓ ↓
README.md (markpact)  Taskfile.yml  docker-compose.yml
```

### Warstwa 1 — CSS-like (format podstawowy)

Plik `[projekt].doql.css` — maszynowy, precyzyjny, pełna kontrola struktury.

### Warstwa 2 — LESS/SASS (dla zaawansowanych)

Pliki `[projekt].doql.less` i `[projekt].doql.sass` — dodają zmienne, zagnieżdżenia, mixiny. Dla dużych projektów z wieloma środowiskami.

### Warstwa 3 — Markdown / YAML (docelowe outputy)

Generowane automatycznie z warstwy 1. Nigdy edytowane ręcznie.

---

## Rekomendacja dla ekosystemu OqlOS

1. **CSS-like jako SSOT** — wszystkie nowe projekty tworzą `[name].doql.css`
2. **LESS dla dużych projektów** — wiele envów, wiele platform, wiele regionów
3. **SASS dla komponentów bibliotecznych** — mixiny dla powtarzalnych wzorców (np. `@mixin iso17025-plugin`)
4. **Markdown/YAML generowane** — z parsera DOQL, nigdy ręcznie edytowane

W kolejnych artykułach pokazujemy pełne przykłady dla każdego z tych formatów na bazie rzeczywistych projektów z organizacji Softreck.

---

*Artykuł jest częścią serii o ekosystemie OqlOS / DOQL. Następny: przykład formatu CSS-like dla projektu IoT Fleet Manager.*
