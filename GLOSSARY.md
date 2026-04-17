# Rodzina OQL — Słownik i Semantyka

> Jeden z najczęstszych problemów rodzin języków — rozmyta granica między nimi.
> Ten dokument definiuje raz a jednoznacznie, czym jest każdy język rodziny OQL.

---

## Trzy języki, trzy role

| Język | Paradygmat | Odpowiada na pytanie | Analogia |
|-------|-----------|---------------------|----------|
| **OQL** (`.oql`) | imperatywny | **JAK wykonać zadanie?** (sekwencyjnie) | Bash / sekwencer CNC |
| **DOQL** (`.doql`) | deklaratywny | **CO ma powstać?** (aplikacja, dokument, artefakt) | Terraform / Rails |
| **TestQL** (`.testql.toon.yaml`) | deklaratywny | **JAK wygląda interakcja/komunikacja?** | Gherkin / OpenAPI + session |

---

## OQL — imperatywny, do wykonania zadań

`.oql` to skrypt wykonawczy. Mówi *co robić, krok po kroku*. Interpreter oqlos wykonuje linia po linii.

**Użycie:** sterowanie sprzętem, sekwencje testowe, procedury kalibracji, automatyzacja hardware.

**Przykład:**
```oql
SCENARIO: "Test szczelności maski"
DEVICE_TYPE: "BA"

GOAL: Podciśnienie
  SET 'pompa 1' '5 l/min'
  WAIT 2000
  IF AI01 < -15 mbar ELSE ERROR "Poza zakresem"
  SET 'pompa 1' '0'
  SAVE: wynik
```

Kluczowe cechy:
- **Kolejność ma znaczenie** — `SET` przed `WAIT` to coś innego niż `WAIT` przed `SET`
- **Stan mutowalny** — pompa włączona, ciśnienie rośnie, zawór zamknięty
- **Imperatywy** — `SET`, `WAIT`, `SAVE`, `GOTO`, `IF...ELSE`, `PUMP`

---

## DOQL — deklaratywny, do budowania artefaktów

`.doql` to deklaracja tego, *co ma powstać*. Generator doql czyta deklarację i produkuje artefakty: aplikacje, dokumenty, bazy danych, konfiguracje.

**Użycie:** generowanie kompletnych aplikacji (API + Web + Mobile + Desktop + Kiosk), dokumentów (HTML, PDF, Markdown), templatek, baz SQLite, integracji z API zewnętrznymi.

**Przykład:**
```doql
APP: "Manager inspekcji"

DATA devices:
  source: json
  file: data/devices.json

ENTITY Device:
  from: DATA devices

ARTIFACT certificate:
  type: pdf
  template: templates/cert.html
  data: { device: $device, date: today }

INTERFACE web:
  PAGE devices: crud FROM Device
  PAGE cert_generator:
    form: { device_id }
    on_submit: GENERATE certificate WITH device_id

INTERFACE kiosk:
  target: tablet
  fullscreen: true
  pages: [scan, inspect, print]

DEPLOY docker-compose with traefik quadlet
```

Kluczowe cechy:
- **Kolejność nie ma znaczenia** — `ENTITY` przed `DATA` to to samo co odwrotnie
- **Stan niemutowalny** — opisuje cel, nie kroki
- **Deklaracje** — `APP`, `ENTITY`, `ARTIFACT`, `TEMPLATE`, `DATA`, `INTERFACE`, `DEPLOY`

---

## TestQL — deklaratywny, do interakcji i testów interfejsów

`.testql.toon.yaml` to zapis sposobu *komunikacji z interfejsem* — webowym, API, mobilnym. Może być nagrany z sesji użytkownika, napisany ręcznie, albo wygenerowany z deklaracji testowej.

**Użycie:** session recording, testy UI, integracja z webhookami, dokumentacja przepływu API, onboarding (replay).

**Przykład:**
```testql
SESSION: "Periodyczny test urządzenia"

NAVIGATE "/connect-test-device"
WAIT 500

CLICK "[data-id='d-001'] .btn-test-item"
OPEN_INTERVAL_DIALOG "d-001"

SELECT "#interval-select" {"value": "36m"}
SELECT_INTERVAL "36m"

CLICK "#interval-start"
START_TEST "ts-c20" {"interval": "36m", "deviceId": "d-001"}

ASSERT_URL "/connect-test-protocol*"
STEP_COMPLETE "step-1" {"status": "passed"}

PROTOCOL_FINALIZE "pro-example123"
```

Kluczowe cechy:
- **Kolejność ma znaczenie** (to jest interakcja), ale każda linia to *deklaracja zdarzenia*
- **Semantyczne nie selektory** — `STEP_COMPLETE` zamiast `click(.button-123)`
- **Interakcja** — `NAVIGATE`, `CLICK`, `SELECT`, `ASSERT_*`, domain-specific jak `PROTOCOL_FINALIZE`

---

## Jak te trzy współpracują

Prosty scenariusz: aplikacja SaaS do zarządzania testami masek.

**Warstwa DOQL** (`app.doql`) deklaruje całą aplikację:
```doql
APP: "Mask Manager"
ENTITY Device: ...
INTERFACE web: ...
INTERFACE kiosk: ...
SCENARIOS: IMPORT scenarios/*.oql
TESTS: IMPORT tests/*.testql.toon.yaml
```

**Warstwa OQL** (`scenarios/pss7000.oql`) definiuje konkretne sekwencje hardware:
```oql
SCENARIO: "PSS 7000 full test"
GOAL: Podciśnienie
  SET 'pompa 1' '5 l/min'
  ...
```

**Warstwa TestQL** (`tests/acceptance.testql.toon.yaml`) definiuje jak aplikacja ma się zachowywać:
```testql
NAVIGATE "/devices/d-001"
CLICK ".btn-start-inspection"
ASSERT_TEXT ".status" "in_progress"
```

Generator `doql build` czyta DOQL, importuje referencje do OQL i IQL, i produkuje kompletny stack.

---

## Nie myl

| Myślisz o… | Używaj… |
|-----------|---------|
| „Uruchom pompę na 5 sekund" | **OQL** (to zadanie) |
| „Skonfiguruj API z endpointem /devices" | **DOQL** (to deklaracja artefaktu) |
| „Kliknij przycisk i sprawdź, czy strona się zmieniła” | **TestQL** (to interakcja) |
| „Zrób mi raport PDF z ostatniego testu" | **DOQL** (`ARTIFACT report`) |
| „Zaimportuj dane z JSON" | **DOQL** (`DATA source: json`) |
| „Wykonaj procedurę kalibracji" | **OQL** |
| „Opisz przepływ użytkownika do dokumentacji” | **TestQL** |
| „Zbuduj stanowisko operatora w trybie kiosk" | **DOQL** (`INTERFACE kiosk`) |

---

## Rozszerzalność

Każdy z trzech języków używa wspólnego tokenizera (`_cql_tokenizer.py` w oqlos), więc narzędzia (syntax highlighting, LSP, formatter) działają dla całej rodziny. Ale ich semantyki są rozdzielne — nie można pomylić `SCENARIO:` z `APP:` ani `NAVIGATE` z `SET`.

Ta rozdzielność to inwestycja na lata. Jedna rodzina, trzy narzędzia, jasne role.
