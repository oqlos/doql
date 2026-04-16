---
title: "oqlos — stan projektu, kwiecień 2026"
slug: "oqlos-status-2026-q2"
date: 2026-04-16
author: "Softreck"
categories: ["oqlos", "status update"]
tags: ["oqlos", "dsl", "hardware testing", "open source", "pneumatyka", "aparaty oddechowe"]
excerpt: "Gdzie jest oqlos po refaktoryzacji fazy 2: CC̄ spada do 3,2, interpreter został rozbity na trzy moduły, 227 plików przechodzi walidację. Co dalej."
language: pl
status: draft
---

# oqlos — stan projektu, kwiecień 2026

**oqlos** to otwarty runtime interpretujący deklaratywny język `.oql` do opisu scenariuszy testowania sprzętu przemysłowego. Projekt istnieje od kilkunastu miesięcy i przeszedł właśnie drugą większą falę refaktoryzacji. Poniżej — gdzie jesteśmy, co działa, co zostało.

## Co to jest oqlos, jednym akapitem

Operator BHP, technik kalibracji albo inżynier QA pisze plik `.oql` opisujący co chce sprawdzić — w trzech liniach: „ustaw pompę na 5 l/min, poczekaj 2 sekundy, zmierz ciśnienie na AI01, jeśli poza [-15, 0] mbar zgłoś błąd". oqlos tłumaczy to na konkretne komendy do urządzeń podpiętych przez Modbus, MQTT, USB czy GPIO, wykonuje test, strumieniuje wyniki do UI i zapisuje protokół. Brak kodu, brak kompilacji, brak licencji — AGPL/Apache w zależności od modułu.

## Metryki, bez owijania

Ostatnia analiza (code2llm + redup + vallm) z 16 kwietnia 2026:

- **925 funkcji**, 26 643 linie kodu, 115 plików Python + 53 JavaScript + 12 shell
- **CC̄ = 3,2** (średnia złożoność cyklomatyczna) — spadek z 3,7 sprzed sprintu
- **2 funkcje krytyczne** pozostały (próg: 15), z 15 na początku roku
- **0 cykli** w grafie zależności modułów
- **13 grup duplikatów** w backend — znane, zaplanowane, głównie w warstwie pluginów hardware
- **227 plików** przechodzi walidację (43%), 38 ostrzeżeń, 2 błędy (jedno to brakujący paho.mqtt, drugie SQL w init-test-data)

Interpreter — największy moduł projektu — został rozbity z 576 linii (CC=10) na trzy mniejsze: `_value_normalizers.py`, `_sensor_evaluator.py`, `_firmware_executor.py`. Plik główny ma teraz 346 linii i CC=8. Dla każdego kto czytał ten kod rok temu — różnica jest odczuwalna.

## Co działa dziś

Pokazowy scenariusz *Dräger PSS 7000 — pełny test maski* (`drager-fps-7000-pelny-test-maski.oql`) wykonuje się end-to-end na stanowisku z pilotowego wdrożenia: od inicjalizacji peryferii, przez sekwencję nadciśnienia statycznego, test szczelności, pomiar ciśnienia otwarcia zaworu, aż po oględziny wizualne i zapis protokołu. Scenariuszy tego typu mamy w repozytorium trzy — w pełnej produkcji od kilku miesięcy, z częstotliwością kilkudziesięciu wykonań tygodniowo.

Stos komend obejmuje `SET`, `GOAL`, `SCENARIO`, `VAL`, `MIN`, `MAX`, `SAVE`, `WAIT`, `FUNC`, `IF`, `GOTO`, `SAMPLE`, `ERROR` plus drugi dialekt `.iql` do testów GUI/API — z komendami `NAVIGATE`, `CLICK`, `SELECT`, `STEP_COMPLETE`. Ten drugi powstał w odpowiedzi na konkretną potrzebę zapisywania i odtwarzania sesji testowych w aplikacji webowej.

## Co nie działa albo świeci na żółto

Uczciwość naukowa wymaga listy tego, co jeszcze boli.

**Alerty architektoniczne.** `FirmwareAdapter.set_peripheral` ma fan-out 20 (limit 10) — funkcja routująca komendy do pomp, zaworów i sensorów rośnie liniowo z każdym nowym typem peryferium. Pierwszy kandydat do wzorca strategy/registry. Podobnie `_handle_start` (fan-out 18) i parser XML (16). To nie są bugi, ale są to miejsca, w których następna zmiana będzie bolała, jeśli nic z tym nie zrobimy.

**Duplikaty.** 13 grup, łącznie 111 linii do odzyskania. Większość to pliki pluginów hardware — `lung.py`, `motor.py`, `piadc.py` mają niemal identyczne `health_check`, `disconnect`, `__init__`. Powiedzieliśmy sobie w lutym, że wyodrębnimy te wzorce do `plugins/utils/`, nie zrobiliśmy. Kolejny sprint.

**Dwa `main`, oba z wysokim CC.** Jeden (CC=15, fan-out 26) to punkt wejścia orchestrujący skrypt startowy; drugi (CC=15, fan-out 18) — w pakiecie `__main__`. Refaktor `setup_hardware_and_run_oql.py` zlecony, ale nietkniety.

**Niski indeks maintainability** w `interpreter.py` (10,9), `generators.py` (13,3) i testach tokenizera (17,4). Powyżej progu 20 tylko dzięki obronie działań profilowanych — w praktyce to moduły, które warto przeczytać na zimno.

## Co zmieniło się w modelu biznesowym

Dwie rzeczy, obie wpływają na roadmapę oqlos.

**Pilotowy klient nie interesuje się oprogramowaniem.** Hardwarowy biznes, który sprzedaje stanowiska testowe, chce uspservisować — tzn. sprzedawać kontrakt serwisowy, nie licencję. Dla nas to czysta przestrzeń: model revenue-sharing SaaS, bez konfliktów non-compete. Oznacza to konkretnie, że możemy rozwijać oqlos jako platformę, nie jako produkt zamknięty w ekosystemie jednego dostawcy.

**Targi w Niemczech jako walidacja.** Plan obecności na targach w DE wymaga od strony technicznej stabilnego demo i jasnej oferty. Analiza konkurencji pokazała, że w naszej niszy (testy aparatów oddechowych + deklaratywny DSL + open core) nie ma bezpośrednich odpowiedników — Dräger Quaestor, PSTrax, Collective Data to zamknięte produkty, a Snipe-IT czy Atlas CMMS są zbyt ogólne. Obecność w przestrzeni, w której nie ma jeszcze konkurencji, to sygnał rynkowy sam w sobie.

## Co zrobimy w następnym sprincie

Pięć rzeczy, w kolejności priorytetu.

Po pierwsze, dokończyć refaktor dwóch ostatnich funkcji krytycznych: głównego `main` i `BACKEND_URL` (detekcja środowiska w `config.js`, CC=18). Oba mają już gotowe szkice — zostało wpiąć.

Po drugie, zamknąć 13 grup duplikatów. Plan jest prosty: `plugins/utils/health_check.py`, `plugins/utils/disconnect.py`, wspólny `__init__` dla pluginów. Szacunek: trzy godziny uczciwej roboty.

Po trzecie, opublikować stabilne API do introspekcji schematu (lista peryferii, komend, typów) — potrzebuje tego nowy projekt **doql** (o nim osobny artykuł). To plus event bus z webhook dispatch dla zdarzeń typu `scenario.completed`.

Po czwarte, multi-tenancy. Migracja modeli o `organization_id`, middleware filtrujące, breaking change w API. To zajmie dwa-trzy dni i zablokuje nas przed pozycjonowaniem oqlos jako backendu SaaS dopóki nie będzie gotowe.

Po piąte, plugin `paho.mqtt.client` — jeden z dwóch błędów walidacji. Trywialne, zostało.

## Jak używać oqlos dziś

Instalacja standardowa przez `pip install oqlos` lub przez kontener Docker. Scenariusze testowe w `scenarios/` pokazują pełen zakres składni — od minimalnego testu pompy po złożony test kaskadowy z przełączaniem zakresów czujników. Dokumentacja API pod `http://localhost:8000/docs`, edytor webowy pod `/editor`.

Dla pierwszej integracji rekomendujemy zacząć od pliku `hardware-diagnostics.oql` — to samokontrola stanowiska, która wykaże, czy wszystkie peryferia są dostępne i odpowiadają w oczekiwanym zakresie.

## Gdzie to idzie

oqlos to fundament. Nad nim budujemy **testql** (framework testowy nad `.iql`, zobacz osobny artykuł), **weboql** (warstwa webowa i IDE) oraz **doql** (generator kompletnych aplikacji). Każdy z tych projektów rozwiązuje inny poziom problemu — od „jak sterować sprzętem" po „jak zbudować wokół tego SaaS". oqlos, w tej stratyfikacji, jest warstwą najniższą i najważniejszą. Dlatego przez najbliższy kwartał priorytetem jest jego stabilność, nie rozszerzanie o nowe cechy.

---

Repo: [github.com/softreck/oqlos](https://github.com/softreck/oqlos)  
Spec OQL: [oqlos/docs/oql-spec.md](https://github.com/softreck/oqlos/blob/main/docs/oql-spec.md)  
Feedback, issue, PR — welcome.
