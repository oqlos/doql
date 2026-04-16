---
title: "doql v0.2 — dokumenty, dane, kiosk. Kiedy jeden plik wystarczy"
slug: "doql-v02-dokumenty-kiosk"
date: 2026-04-16
author: "Softreck"
categories: ["doql", "status update", "announcement"]
tags: ["doql", "dokumenty", "pdf", "kiosk", "iso 17025", "quadlet", "raspberry pi"]
excerpt: "Wersja 0.2 doql rozszerza zakres z generatora SaaS na generator artefaktów — dokumentów, raportów, stanowisk kiosk. Z jasno ustaloną semantyką wobec oql i iql."
language: pl
status: draft
---

# doql v0.2 — dokumenty, dane, kiosk. Kiedy jeden plik wystarczy

Od ogłoszenia doql minęło kilka tygodni. Przez ten czas pojawiły się pytania, które powiedziały mi dwie rzeczy. Po pierwsze — zakres pierwszej wersji był za wąski. Po drugie — granica między `oql`, `doql` i `iql` była czytelna dla nas, ale rozmyta dla innych. Ta wersja, 0.2, rozwiązuje obie kwestie.

## Co się zmieniło w zakresie

W v0.1 doql mówił: „zbuduj aplikację SaaS z jednego pliku". Działało to dla asset management, labów ISO, flot IoT. Ale pojawiły się trzy typowe pytania, których wtedy nie obsługiwaliśmy.

Pierwsze: "Chcę wygenerować tylko PDF. Nie potrzebuję aplikacji, bazy, API." Klasyczne — laboratorium kalibracyjne, które chce w oparciu o deklarację wypluwać świadectwa w formacie ISO 17025, karmione danymi z JSON-ów i API oqlos. Ciężki SaaS to overengineering. W v0.2 mamy `DOCUMENT`, `TEMPLATE`, `REPORT` — można zadeklarować sam generator dokumentów bez backendu.

Drugie: "Mam dane w trzech miejscach — JSON dla konfiguracji, SQLite dla katalogu, API zewnętrzne dla świeżych liczb. Jak to połączyć?" W v0.1 entity zawsze trafiała do bazy relacyjnej. W v0.2 źródłem danych może być dowolny backend — `DATA source: json | sqlite | api | csv | excel | env`. To samo źródło może zasilić encję CRUD, dokument PDF, dashboard, workflow.

Trzecie: "Chcę zbudować stanowisko na tablecie w warsztacie. Pełnoekranowe, z PIN-em, skanerem kodów, wydrukiem etykiety. Nie chcę, żeby operator mógł wyjść z aplikacji." W v0.1 mieliśmy `INTERFACE web`, `mobile`, `desktop`, `api` — żaden nie pasował. Kiosk to nie to samo co PWA, bo PWA można zamknąć. W v0.2 mamy `INTERFACE kiosk` z całą stroną zablokowania systemu, hardware bindings dla USB scannera i ZPL printera, deploy target `kiosk-appliance` dla Raspberry Pi.

## Co ustaliliśmy o semantyce

Przez pierwsze tygodnie ktoś zapytał, czy można "napisać test w doql". Ktoś inny — czy "oql nadaje się do opisu aplikacji". Te pytania sygnalizowały, że granica między językami była u nas jasna, ale u innych nie. Dokument [`GLOSSARY.md`](https://github.com/softreck/doql/blob/main/GLOSSARY.md) w repozytorium doql próbuje to uporządkować raz a dobrze.

**OQL jest imperatywny.** Odpowiada na pytanie "jak wykonać zadanie krok po kroku". Pojedynczy plik `.oql` to skrypt — ustaw pompę, czekaj, zmierz, sprawdź, zapisz. Kolejność ma znaczenie. Mutuje stan (pompy, zaworu, czujnika). Interpretujemy linia po linii. Analogie: Bash, G-code, sekwencer CNC.

**DOQL jest deklaratywny.** Odpowiada na pytanie "co ma powstać". Plik `.doql` to opis celu — aplikacji, dokumentu, stanowiska. Kolejność sekcji nie ma znaczenia. Generator czyta całość, buduje plan, produkuje artefakty. Analogie: Terraform, Rails, CloudFormation.

**IQL jest deklaratywny, ale na innej osi.** Odpowiada na pytanie "jak wygląda interakcja". Plik `.iql` to zapis sekwencji zdarzeń — kliknij tu, wpisz to, sprawdź to. Używany do session recording, testów UI, dokumentacji przepływów, specyfikacji integracji przez webhooki. Analogie: Gherkin, OpenAPI z sekwencjami, Playwright trace.

Każdy z tych języków używa tego samego tokenizera (wspólny `_cql_tokenizer.py` w rodzinie oqlos), więc narzędzia (syntax highlighting, LSP) działają dla wszystkich. Ale semantyki są rozdzielne i nie konkurują.

## Przykład, który zamienia abstrakcję w konkret

Laboratorium kalibracyjne chce wypluwać świadectwa. Dane: JSON z organizacją, SQLite z katalogiem przyrządów, API oqlos z wynikami pomiarów. Output: PDF zgodny z ISO 17025, podpisany kwalifikowanym podpisem, wysłany mailem do klienta.

W wersji v0.1 doql musiałbyś zbudować całą aplikację SaaS, żeby wygenerować ten PDF. W v0.2 pełna deklaracja wygląda mniej więcej tak:

```doql
APP: "Cert Generator"

DATA organization:
  source: json
  file: data/organization.json

DATA instruments:
  source: sqlite
  file: data/instruments.db

DATA measurements:
  source: api
  url: env.OQLOS_URL + "/api/v1/executions"
  auth: bearer
  token: env.OQLOS_API_KEY

DOCUMENT calibration_certificate:
  type: pdf
  template: templates/cert_iso17025.html
  data:
    organization: DATA organization
    instrument: DATA instruments WHERE id = $args.instrument_id
    measurements: DATA measurements WHERE execution_id = $args.execution_id
  signature:
    enabled: true
    method: pades
    key: env.SIGNING_KEY_PATH
  hooks:
    on_generate:
      - email: $customer.email ATTACH $self

WORKFLOW auto_generate:
  trigger: webhook oqlos.scenario.completed
  steps:
    - GENERATE DOCUMENT calibration_certificate

DEPLOY quadlet with traefik
```

Trzydzieści linii. Generator produkuje kod Python z szablonem Jinja2, integracją WeasyPrint, bindingiem do oqlos API, podpisem PAdES, endpointem REST dla webhooka, kontenerami Quadlet. Gdy oqlos zakończy scenariusz kalibracyjny, doql automatycznie generuje PDF, podpisuje, wysyła klientowi.

To nie jest marketingowy mockup — pełny przykład w [`examples/document-generator/`](https://github.com/softreck/doql/tree/main/examples/document-generator) z szablonem HTML, seed JSON, deklaracją pełną.

## Przykład kiosk — bo tu skala złożoności skacze

Stanowisko operatora na tablecie w warsztacie testowym PSA. Operator loguje się PIN-em, skanuje kod urządzenia, wybiera scenariusz testowy, patrzy na live log wykonania, po zakończeniu — drukuje etykietę, wraca do menu głównego. Bez klawiatury, bez myszy, bez dostępu do systemu.

To pozornie prosta aplikacja, ale w praktyce wymaga:

- Integracji z USB barcode scannerem (emulującym klawiaturę) i Zebra ZPL drukarką po USB-serial
- Chromium w trybie `--kiosk` z wyłączonymi skrótami systemowymi (Alt+F4, Ctrl+Alt+Del), autostart na Openbox
- Lokalnego cache SQLite z operatorami i urządzeniami, bo warsztat pod ziemią nie ma LTE
- Kolejki offline dla operacji, gdy sieć pada, z retry exponential backoff po jej powrocie
- Auto-update OTA ze sprawdzaniem podpisu i rollbackiem przy nieudanym starcie
- Idle screen z slideshow BHP po 60 sekundach bezczynności
- Sesji PIN trwającej do końca zmiany (8h), bo operator nie ma czasu logować się co 10 minut
- High-contrast tematu z dużymi przyciskami 80×80px minimum — bo rękawiczki warsztatowe

Każdy z tych elementów jest *możliwy* w zwykłej aplikacji webowej albo PWA. Problem w tym, że jest ich dużo, i każdy wymaga konkretnej wiedzy operacyjnej (jak skonfigurować Openbox autostart, jaka komenda dla chromium --kiosk, jak ustawić udev regułę dla scanera).

W `.doql` to jest jedna sekcja [`INTERFACE kiosk`](https://github.com/softreck/doql/blob/main/examples/kiosk-station/app.doql) z ~150 liniami. Generator produkuje obraz Raspberry Pi, konfigurację systemd, aplikację w Electron/Tauri z lockdownem, bindingi hardware, cron do OTA updates. Plus uproszczony instalator — `doql kiosk --install --target rpi-os-lite`.

## Relacja do oqlos — co się zmieniło w wymaganiach

Pierwsza wersja [`OQLOS-REQUIREMENTS.md`](https://github.com/softreck/doql/blob/main/OQLOS-REQUIREMENTS.md) mówiła o pięciu krytycznych zmianach w oqlos, bez których doql nie zadziała w pełni. Po dodaniu dokumentów, źródeł danych i kiosk doszły trzy kolejne wymagania po stronie oqlos.

**Endpoint `/events` z webhook subscribe.** Żeby `WORKFLOW auto_generate` reagował na `scenario.completed`, oqlos musi pushnąć zdarzenie do doql backendu. W v0.1 planowaliśmy SSE; okazuje się, że webhook push (POST z HMAC signature) jest lepszy dla trybu kiosk (który nie utrzymuje aktywnej sesji SSE).

**API do zrzucenia execution data jako JSON.** Dokument kalibracyjny musi mieć dostęp do pełnych danych pomiarowych z wykonania scenariusza. W v0.1 executor oqlos trzymał te dane w pamięci; potrzebujemy endpointu `/executions/{id}/data` z kompletnym dumpem.

**Delta API dla offline sync.** Kiosk cache'uje listę urządzeń i operatorów; synchronizuje przyrostowo. Potrzebne `GET /devices?since=<timestamp>` zwracające tylko zmiany. W v0.1 było tylko pełne `/devices` — nie skaluje się dla kiosk z 10 000 urządzeń.

Łącznie oznacza to kolejne 3-5 dni pracy nad oqlos, ale wszystkie trzy to drobne dodatki do istniejących endpointów, nie przebudowa architektury.

## Deploy — co działa, co jest w planach

**Docker Compose + Traefik** — działa, testowane, docker-compose.yml + labels dla ingressu, Let's Encrypt automatycznie.

**Podman Quadlet (rootless)** — działa, generator produkuje `*.container` files gotowe do `~/.config/containers/systemd/`. Systemd ogarnia restart, dependencies, logi. Jeden container, jeden unit — czytelnie.

**Kiosk appliance na Raspberry Pi** — działa w pełni tylko dla RPi OS Lite 64-bit; inne platformy (Windows IoT, Ubuntu Kiosk) w planach na 0.3. Obraz .img do karty SD lub instalacja na już zainstalowanym RPi przez SSH.

**Kubernetes** — przekierowujemy do Docker Compose dla małych wdrożeń i Quadlet dla single-node. Dla k8s (1000+ nodes) generator będzie w fazie 3 — produkuje Helm chart, ale do tej wersji wolimy ograniczyć zakres.

## Co dalej

Plan na najbliższe sześć tygodni: dokończyć implementację parsera `.doql` pokrywającego pełną gramatykę v0.2, uruchomić pierwszego realnego klienta pilotowego (lab kalibracyjny w Gdańsku, wstępne rozmowy są), dodać LSP dla VS Code z podświetleniem składni i autocompletion, opublikować playground online gdzie ktoś może napisać `.doql` w przeglądarce i zobaczyć plan generowania.

Kolejna wersja — v0.3 — doda generatory dla Flutter mobile, pełen kubernetes target, marketplace szablonów `.doql`. Ale to wszystko dopiero gdy v0.2 będzie obsługiwana w produkcji przez co najmniej dwa zespoły zewnętrzne.

Jeśli prowadzisz laboratorium, warsztat, lub jakiekolwiek stanowisko operatorskie, które chciałbyś ustrukturyzować przez deklarację zamiast skomplikowanego kodu — odzywaj się. Fazy pilotażu są bezpłatne, wymagają czasu i feedbacku, w zamian — aplikacja zbudowana pod twój use case, kod otwarty, bez lock-inu.

---

Repo: [github.com/softreck/doql](https://github.com/softreck/doql)  
Słownik semantyki: [doql/GLOSSARY.md](https://github.com/softreck/doql/blob/main/GLOSSARY.md)  
Przykłady: [document-generator](https://github.com/softreck/doql/tree/main/examples/document-generator) · [kiosk-station](https://github.com/softreck/doql/tree/main/examples/kiosk-station)
