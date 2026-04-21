# Parser Audit — doql vs. op3 (opstree)

**Scope:** dokumentuje asymetrię między parserami `.doql.less` w projekcie doql i op3.
**Purpose:** chroni kontrakt round-trip `doql build → op3 scan → doql drift`.
**Last updated:** 2026-04-21
**Versions:** doql 1.0.12, op3 0.1.14

## Executive Summary

| Kierunek | Co się dzieje | Ryzyko |
|----------|---------------|--------|
| op3 → doql | **Bezpieczny** — op3 emituje podzbiór który doql rozumie w całości | Zero |
| doql → op3 | **Wymaga downgrade** — doql parsuje więcej niż op3 rozumie | False positive w drift |

Decyzja architektoniczna: **asymetria świadoma** (opcja 3). doql jest źródłem prawdy dla deklaracji aplikacji; op3 jest źródłem prawdy dla snapshotu infrastruktury. Most `op3_bridge.py` tłumaczy między nimi, celowo gubiąc features które nie mają mapowania na warstwy op3.

---

## Feature Matrix

| Feature | doql parser | op3 LessAdapter | Round-trip |
|---------|-------------|-----------------|------------|
| **Flat CSS selectors** (`entity[name="X"]`) | ✅ Full | ✅ Full | ✅ |
| **Attribute selectors** (`[name="X"]`) | ✅ Full | ✅ (prosty regex) | ✅ |
| **Block types** — app | ✅ DoqlSpec.app_* | ✅ business.health | ✅ |
| **Block types** — interface | ✅ DoqlSpec.interfaces | ✅ physical.display | ✅ (subset) |
| **Block types** — service | ❌ N/A* | ✅ service.containers | ✅ |
| **Block types** — entity | ✅ DoqlSpec.entities | ❌ Nie parsuje | ⛔ |
| **Block types** — data | ✅ DoqlSpec.databases | ❌ Nie parsuje | ⛔ |
| **Block types** — template | ✅ DoqlSpec.templates | ❌ Nie parsuje | ⛔ |
| **Block types** — document | ✅ DoqlSpec.documents | ❌ Nie parsuje | ⛔ |
| **Block types** — report | ✅ DoqlSpec.reports | ❌ Nie parsuje | ⛔ |
| **Block types** — integration | ✅ DoqlSpec.integrations | ❌ Nie parsuje | ⛔ |
| **Block types** — workflow | ✅ DoqlSpec.workflows | ❌ Nie parsuje | ⛔ |
| **Block types** — role | ✅ DoqlSpec.roles | ❌ Nie parsuje | ⛔ |
| **Block types** — deploy | ✅ DoqlSpec.deploy | ✅ endpoint.http | ✅ (transformacja) |
| **Block types** — database | ✅ DoqlSpec.databases | ❌ Nie parsuje | ⛔ |
| **Block types** — environment | ✅ DoqlSpec.environments | ✅ runtime.container | ✅ (transformacja) |
| **Block types** — infrastructure | ✅ DoqlSpec.infrastructure | ❌ Nie parsuje | ⛔ |
| **Block types** — ingress | ✅ DoqlSpec.ingress | ❌ Nie parsuje | ⛔ |
| **Block types** — ci | ✅ DoqlSpec.ci | ❌ Nie parsuje | ⛔ |
| **Block types** — scenarios | Ignorowane (info) | ❌ Nie parsuje | ✅ |
| **Block types** — api-client | Ignorowane (info) | ❌ Nie parsuje | ✅ |
| **Block types** — tests | Ignorowane (info) | ❌ Nie parsuje | ✅ |
| **@variables (LESS)** | ✅ @var + 5-pass expansion | ❌ Ignorowane** | ⚠️ |
| **$variables (SASS)** | ✅ $var + 5-pass expansion | ❌ Ignorowane** | ⚠️ |
| **@mixin / @include (SASS)** | ✅ Definicja + expansion | ❌ Ignorowane** | ⚠️ |
| **Nesting (LESS)** | ✅ CSS-like nesting | ❌ Nie parsuje** | ⚠️ |
| **Chain selectors** (`A B C`) | ✅ Full chain | ❌ Tylko pierwszy element | ⚠️ |
| **@import** | ❌ Nie zaimplementowano | ❌ Nie parsuje | ✅ |
| **Inline comments `//`** | ✅ Strip before parse | ✅ Strip per-line | ✅ |
| **Multi-line values** | ✅ Unescaped `;` terminator | ✅ Unescaped `;` terminator | ✅ |
| **Escape sequences** (`\;`, `\\`, `\n`) | ✅ Full unescape | ✅ Full unescape | ✅ |
| **Number coercion** | ✅ string→int/float w mapperach | ❌ Tylko string | ✅ (lenient) |

> *`service` nie jest natywnym typem doql — pojawia się wyłącznie w output op3 → doql.
> **Features z `⚠️` mogą powodować false positive w drift: doql widzi inny AST niż op3.

---

## Szczegółowy Breakdown

### 1. Flat CSS selectors — SAFE

Oba parsery używają tej samej składni:

```less
app {
  name: "c2004";
  version: "1.0.33";
}

entity[name="Device"] {
  field: "serial_number string required";
}
```

doql: `_tokenise_css` + `_parse_selector` + `_apply_css_block`.
op3: regex `r'(
[
\w\-]+)(?:\[([^\]]+)\])?\s*\{'` + `_parse_block`.

**Kontrakt:** każdy blok który oba parsery rozpoznają produkuje semantycznie zgodne wyniki.

### 2. @variables / $variables — WARNING

doql rozwiązuje `@primary: #007bff;` przed tokenizacją, z 5-pasową rekurencją dla zagnieżdżonych zmiennych.

op3 **nie widzi zmiennych** — traktuje `@primary: #007bff;` jako nieznany blok lub ignoruje linię.

**Scenariusz drift:**

```less
// app.doql.less pisany ręcznie
@domain: "c2004.mask.services";

deploy {
  target: "pi@192.168.188.109";
  domain: @domain;
}
```

Po `doql build` → `op3 scan` → `doql drift`:
- doql parser widzi: `domain: "c2004.mask.services"` (po rozwinięciu)
- op3 parser widzi: `domain: "@domain"` (brak rozwinięcia)
- DriftDetector zgłasza: `domain: "c2004.mask.services"` → `"@domain"` — **false positive**

**Mitigation:** `spec_to_op3_compatible_less()` (TODO) musi rozwijać zmienne przed wysłaniem do op3, lub — prościej — zakazać zmiennych w plikach intendowane do drift.

### 3. Nesting / Chain selectors — WARNING

doql obsługuje łańcuchy selektorów:

```less
interface[type="cli"] page[name="doql"] {
  framework: "click";
}
```

op3 `LessAdapter.parse()` używa regex `r'interface\[type="([^"]+)"\]\s*\{([^}]+)\}'` — **nie widzi** `page[name="doql"]` jako osobnego bloku. Traktuje całość jako `interface[type="cli"]` z body zawierającym `page[name="doql"] { ... }` jako zwykłą deklarację (lub ignoruje jeśli body jest zbyt złożone).

**Mitigation:** w plikach `.doql.less` intendowanych do drift używaj tylko flat selectors.

### 4. Block type mapping — ASYMMETRIC by design

```
doql model          → op3 layer
─────────────────────────────────────────
app                 → business.health
interface           → physical.display
deploy              → endpoint.http
environment         → runtime.container
service (synthetic) → service.containers

entity, data, template, document, report,
integration, workflow, role, database,
infrastructure, ingress, ci
                    → ⛔ (no op3 layer)
```

Oznacza to że **pełna deklaracja aplikacji doql (z entity, workflow, database) nie ma round-trip przez op3**. To jest świadoma granica — op3 opisuje infrastrukturę, nie architekturę aplikacji.

### 5. service[name="X"] — op3-only in this direction

```less
service[name="c2004-backend"] {
  image: "localhost/c2004-backend:latest";
  state: "running";
}
```

Ten blok **nie jest parsowany przez doql** (doql nie ma block typu `service` w `_apply_css_block`).
Pojawia się wyłącznie w output `op3 scan → snapshot_to_less()`.

doql parser go **ignoruje** z warningiem: `Unknown CSS block type 'service'. Did you mean one of: ...`.

**To jest OK** — pliki `.doql.less` generowane przez `adopt --from-device` są "read-only" dla doql (służą jako intended state dla drift, nie jako źródło do `doql build`).

---

## Testy chroniące kontrakt

| Test | Lokalizacja | Co chroni |
|------|-------------|-----------|
| `test_adopt_output_is_parsable_by_doql` | `tests/integration/test_adopt_from_device.py:185` | op3-generated LESS jest valid dla doql |
| `test_adopt_from_rpi5_output_is_parsable_by_doql` | `tests/integration/test_adopt_from_device.py:263` | Podman Quadlet output jest valid dla doql |
| `test_snapshot_to_less_produces_parsable_less` | `tests/integration/test_op3_bridge.py` | op3 render → doql parse round-trip |
| `test_detect_drift_no_changes` | `tests/integration/test_drift.py` | Zero drift gdy intended == actual |
| `test_detect_drift_service_state_mismatch` | `tests/integration/test_drift.py` | Drift wykrywa realne różnice |

**Brakujący test:** `test_drift_with_less_variables_no_false_positive` — sprawdza że `@var` w intended nie daje false positive. Wymaga implementacji `spec_to_op3_compatible_less()`.

---

## Recomendacje

### Dla autorów `.doql.less` intendowanych do drift

1. **Używaj tylko flat selectors** — bez nesting, bez chain selectors.
2. **Unikaj `@variables` i `$variables`** — używaj literal values.
3. **Ogranicz block types** do: `app`, `interface`, `deploy`, `environment`. `service` jest OK jeśli plik jest generowany przez op3 (read-only).
4. **Testuj round-trip:** `doql drift --from-device USER@HOST` po każdej zmianie.

### Dla deweloperów doql

1. **Implementuj `spec_to_op3_compatible_less()`** w `doql/integrations/op3_bridge.py` przed dalszym rozszerzaniem parsera.
2. **Dodaj `_warn_lost_features()`** — explicit warning gdy `@var` lub nesting jest dropowane.
3. **Nie dodawaj nowych block types do op3 bez uzasadnienia** — każdy nowy typ wymaga mapowania na warstwę op3.

### Dla deweloperów op3

1. **Rozważ `--user` flagę w `ServiceContainersProbe`** — Quadlet services żyją w user slice.
2. **Rozważ rozszerzenie `_parse_block`** o number coercion — obecnie wszystkie values są stringami.
3. **Freeze public API** — `LessAdapter.parse()`, `LessAdapter.render()`, `PartialSnapshot` to kontrakt.

---

## Decyzje architektoniczne

| Decyzja | Stan | Uzasadnienie |
|---------|------|--------------|
| Dwa parsery zamiast jednego | ✅ Zaakceptowane | doql parsuje aplikację, op3 parsuje infrastrukturę — różne modele mentalne |
| Asymetria doql ⊃ op3 | ✅ Zaakceptowane | doql rozumie superset; op3 wymusza discipline przez subset |
| spec_to_op3_compatible_less() | ⏳ TODO | Chroni przed false positive w drift przy @var |
| --user systemd support w op3 | ⏳ TODO | Quadlet services na RPi5 żyją w user slice |
| Unified parser v2.0 | ❌ Odrzucone | Zbyt duża praca, zbyt mały zysk — modele są różne by design |
