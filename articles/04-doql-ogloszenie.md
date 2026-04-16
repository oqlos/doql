---
title: "doql — kiedy z jednego pliku rodzi się cała aplikacja"
slug: "doql-ogloszenie"
date: 2026-04-16
author: "Softreck"
categories: ["doql", "announcement", "vision"]
tags: ["doql", "oqlos", "code generation", "low-code", "saas", "asset management"]
excerpt: "Ogłaszamy doql — meta-warstwę nad oqlos, która z deklaracji .doql generuje kompletny stack: API, Web, Mobile, Desktop, Infra. Klon Drägerware w jednym pliku."
language: pl
status: draft
---

# doql — kiedy z jednego pliku rodzi się cała aplikacja

Jeśli spędziłeś kiedykolwiek dwa tygodnie na budowaniu CRUD-u z autoryzacją, wiesz, że zaczynasz od tego samego za każdym razem. Model danych. REST API. Formularz CRUD. Dashboard. Uwierzytelnianie. Role. Raporty PDF. Deploy. Dokumentacja. Strzelania z biodra w CSS o 2 w nocy.

Dla wąsko zdefiniowanego typu aplikacji — tych, które kręcą się wokół encji, workflow i (czasem) zdarzeń sprzętowych — powtarzanie tego ma coraz mniej sensu. Ogłaszam **doql**: warstwę deklaratywną nad oqlos, która generuje cały stack z jednego pliku.

## Problem, który rozwiązujemy

Nasz pilotowy klient — firma z pneumatyczno-hardwarową historią — chce ucywilizować zarządzanie parkiem urządzeń ochrony dróg oddechowych. Dräger ma na to produkt zamknięty pod nazwą Drägerware, znany każdemu gospodarzowi sprzętu w straży pożarnej. PSTrax, Collective Data — alternatywy, wszystkie komercyjne, wszystkie zamknięte.

Opcja open source też istnieje. Snipe-IT — generyczny asset management, można przystosować. Odoo z modułem fire & safety — ciężkie, ale działa. Atlas CMMS — otwarty, wymaga głębokiej konfiguracji.

Niezależnie od ścieżki, dla konkretnego wdrożenia trzeba: zaprojektować model (urządzenie, inspekcja, operator, kwalifikacja, stacja), zbudować UI (dashboard, skanowanie barcode, formularze inspekcji, raporty), spiąć z istniejącym stanowiskiem testowym (Modbus/MQTT/USB), zdeplojować na produkcji (Docker/Traefik/backup). Kilka tygodni, niezależnie od wyjściowego narzędzia.

doql chce ten koszt ścisnąć do godzin.

## Jak doql wygląda

Oto deklaracja kompletnej aplikacji typu Drägerware. Nie fragment, nie pseudo-kod — to ma być wystarczające do wygenerowania działającego SaaS.

```doql
APP: "Mask Inspection Manager"

ENTITY Device:
  serial: string! unique
  model: string!
  manufacturer: string!
  barcode: string unique
  status: enum[ready, failed, overdue]
  last_inspection: date
  next_inspection: date computed

ENTITY Inspection:
  device: Device ref
  operator: Operator ref
  scenario_id: oql
  result: enum[pass, fail]
  report_pdf: pdf computed

SCENARIOS:
  IMPORT: scenarios/*.oql

INTERFACE web:
  PAGE dashboard:
    widgets:
      - stat: Device WHERE status=overdue COLOR=red
      - table: Device WHERE status=overdue LIMIT 10
  PAGE devices: crud
  PAGE scan:
    features: [barcode_scanner]
    on_scan: lookup Device WHERE barcode=$scanned

INTERFACE mobile:
  type: pwa
  offline: true
  features: [barcode_scanner, camera]

INTERFACE api:
  type: rest
  auth: jwt

INTEGRATION notifications:
  - email: smtp from env.SMTP_*

DEPLOY docker-compose with traefik
```

Trzydzieści linii. Potem jedna komenda:

```bash
doql build && doql deploy
```

Po pięciu minutach pod `app.twojadomena.pl` działa: REST API z Swaggerem, React SPA z dashboardem, PWA do zainstalowania z telefonu, skanowanie kodów kreskowych uruchamiające scenariusze testowe, automatyczne raporty PDF, auth JWT z rolami, Docker Compose z Traefikiem i Let's Encrypt, backup i monitoring.

## Co doql generuje, warstwa po warstwie

**API** — FastAPI z SQLAlchemy, migracjami Alembic, OpenAPI 3.1, pełnym CRUD-em z respektem dla ról, automatycznym generowaniem TypeScript SDK dla frontu. Webhooki do oqlos dla zdarzeń sprzętowych.

**Web** — React + Vite + Material UI (default) lub Tailwind jako alternatywa. Strony dashboard, CRUD, scan, raporty. Formularze walidowane na podstawie definicji entity. Internationalization dla trzech języków (PL/EN/DE).

**Mobile** — PWA z service workerem, offline-first sync, background sync po odzyskaniu sieci, skanowanie kodów kreskowych przez Camera API. Instalowalna z przeglądarki mobilnej bez sklepu.

**Desktop** — Tauri (preferowany nad Electron — mniejszy, szybszy). System tray, auto-update, lokalny dostęp do portu szeregowego dla Modbus RTU.

**Infra** — `docker-compose.yml`, `docker-compose.prod.yml`, Quadlet container files dla rootless Podmana, konfiguracja Traefika z ACME, backup przez Restic z rotacją, health checki, Prometheus metrics.

**Docs** — mkdocs-material z automatycznie generowaną dokumentacją dla użytkownika końcowego, admina i developera.

## Dlaczego tylko teraz

Można zapytać: skoro pomysł jest oczywisty (low-code generatory istnieją od lat), dlaczego robimy to dopiero teraz. Trzy powody.

Po pierwsze, oqlos jako runtime wykonujący scenariusze sprzętowe jest gotowy. Bez tego podstawowego elementu — czyli bez warstwy, która naprawdę steruje pompą i sensorem — całe doql to tylko kolejny generator CRUD-u. Różnicą, która czyni to ciekawym, jest domena: zdarzenia sprzętowe wbudowane w model danych aplikacji.

Po drugie, Drägerware i pokrewne produkty mają od lat tę samą strukturę. Encje, inspekcje, kwalifikacje, workflow. Deklaratywne opisanie tego wzorca — tak, żeby małe niuanse (typy urządzeń, terminy inspekcji, compliance framework) były tuning'iem, a nie re-implementacją — stało się możliwe, gdy zobaczyliśmy ten wzorzec kilka razy z rzędu.

Po trzecie, ekosystem narzędziowy dojrzał. FastAPI dla API, React z Vite dla SPA, Tauri dla desktopu, Quadlet dla rootless Podmana — wszystko to są produkty mniej więcej stabilne. Pięć lat temu trzeba było by wybrać między Electron (ciężki) a niczym, Angularjs albo Reactem klasowym, Django albo Flaskiem bez typów. Dziś możemy oprzeć się na rozsądnym defaults i fokusować na własnej wartości dodanej.

## Co doql NIE jest

Uczciwie — żeby nie było rozczarowania.

**Nie jest no-code'owym narzędziem drag-and-drop.** To plik tekstowy, edytowany w IDE. Dla developera, nie dla biznesu. Dla biznesu może powstać wizualny edytor za rok, na razie — tekst.

**Nie zastępuje oqlos.** Nie steruje sprzętem. Delegate do oqlos, który to robi. Bez oqlos `doql` buduje aplikację CRUD z workflow, ale nie potrafi zmierzyć ciśnienia w pompie.

**Nie jest silver bullet.** Dla aplikacji, których model nie sprowadza się do encji i workflow, generator nie pomoże. Edycja wideo, gry, analityka big data — to nie jest doql.

**Nie jest sumiennym konkurentem Retoola czy Superblocks.** Tamte produkty rozwiązują problem „szybko wyklikać panel administracyjny". doql rozwiązuje problem „zbuduj kompletną aplikację SaaS do zarządzania sprzętem z integracją hardware". Punkt przecięcia — mały.

## Co musi się wydarzyć w oqlos, żeby doql zadziałał w pełni

To jest część, która najbardziej mnie uczciwie obchodzi. Obecnie oqlos nie ma wszystkiego, czego `doql` potrzebuje w pełnej wersji. Lista wymagań — w osobnym dokumencie, krótko:

Stabilne API introspection (żeby wiedzieć, jakie peryferia są dostępne). Event bus z webhook dispatch (żeby reagować na zdarzenia scenariusza). Multi-tenancy (organization_id w modelach). Auth/RBAC (role operatora, managera, audytora). Plugin registry discovery (żeby UI znał zainstalowane pluginy hardware).

Bez tych rzeczy — doql może działać w uproszczonej wersji, dla single-tenant aplikacji z polling zamiast push. Z nimi — może być prawdziwie production-ready.

Szacunkowa skala pracy nad oqlos: około ośmiu tygodni jednego inżyniera full-time na wszystkie wymagania. Połowa z tego to krytyczna ścieżka blokująca doql.

## Plan na Q2 i Q3

Faza 0 (dwa tygodnie): parser `.doql`, generator API dla prostego CRUD, CLI `init/validate/build/run`. Deliverable — uruchamiany przykład z minimalnego `.doql`.

Faza 1 (miesiąc): pełny generator dla wszystkich warstw, integracja z oqlos przez webhooki, pilot w firmie BHP. Deliverable — realna aplikacja, 10+ użytkowników.

Faza 2 (półtora miesiąca): Tauri dla desktopu, workflow engine, report generator, `doql sync` (merge-friendly), LSP dla VS Code. Deliverable — produkt, który ma sens pokazywać na targach w Niemczech.

Faza 3 (kwartał): plugins marketplace (doql-plugin-gxp dla 21 CFR Part 11, doql-plugin-iso17025, doql-plugin-fleet), certyfikacja, globalna oferta.

## Dlaczego to może się udać

Przez dwa lata budowaliśmy warstwowo: najpierw runtime (oqlos), potem test framework (testql), potem front SaaS (oqlos.com), teraz meta-generator (doql). Każda warstwa wyższa stoi na poprzedniej. Każda poprzednia odpowiada na realną potrzebę konkretnego wdrożenia. Żadna nie została zbudowana spekulacyjnie.

doql to krok, który pozwala nam skalować: zamiast pisać jedną aplikację na jednego klienta, piszemy deklarację, która obsługuje klasę aplikacji. Dla klienta BHP w Polsce — klon Drägerware. Dla lab kalibracyjnego — system ISO 17025. Dla flotowego IoT — multi-node orchestrator. Ta sama pętla generatora, trzy różne produkty.

Jeśli to działa — możemy otworzyć ten generator, pozwolić innym pisać swoje `.doql` dla własnych branż, i być katalizatorem zamiast jedynego dostawcy.

## Co możesz zrobić teraz

Jeśli jesteś zainteresowany — repozytorium `doql` jest publiczne, spec języka dostępny. Przykłady dla trzech domen (asset management, calibration lab, IoT fleet) — tam. Na ten moment stan to *alpha* — API może się zmieniać, generator jeszcze nie jest w pełni funkcjonalny — ale plik `.doql` już możesz napisać i zwalidować. Feedback, pull requesty, sugestie — najlepiej przez issue na GitHubie albo email bezpośredni.

Jeśli prowadzisz firmę, która pasuje do któregoś z przykładów — i chciałabyś być pilotowym klientem w fazie 1 — odzywaj się. Współpraca jest bezpłatna, wymaga tylko czasu i gotowości do feedbacku. W zamian — aplikacja zbudowana pod wasz use case, z kodem do modyfikacji, bez vendor lock-in.

---

Repo: [github.com/softreck/doql](https://github.com/softreck/doql)  
Specyfikacja: [doql/SPEC.md](https://github.com/softreck/doql/blob/main/SPEC.md)  
Wymagania wobec oqlos: [doql/OQLOS-REQUIREMENTS.md](https://github.com/softreck/doql/blob/main/OQLOS-REQUIREMENTS.md)  
Kontakt: hello@softreck.dev
