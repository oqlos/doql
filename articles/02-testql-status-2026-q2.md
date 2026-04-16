---
title: "TestQL — kiedy testy aplikacji mówią w tym samym języku co testy sprzętu"
slug: "testql-status-2026-q2"
date: 2026-04-16
author: "Softreck"
categories: ["testql", "status update", "testing"]
tags: ["testql", "iql", "dsl", "testing", "qa", "session recording", "ui testing"]
excerpt: "TestQL to drugie oblicze rodziny oqlos — zamiast sterować pompą, steruje przeglądarką. Ten sam model umysłowy, ten sam format pliku, ta sama infrastruktura."
language: pl
status: draft
---

# TestQL — kiedy testy aplikacji mówią w tym samym języku co testy sprzętu

Rok temu staliśmy przed pytaniem, które zadają sobie wszyscy z rozwijających platformy testowe: czy testy GUI piszemy w Cypress, Playwright, Selenium, czy może w czymś domowym. Dla zespołu, który już ma DSL do testowania sprzętu (`.oql`), odpowiedź okazała się nieoczywista. Dlaczego operator, który rano pisze scenariusz testu aparatu oddechowego, ma po południu uczyć się zupełnie innego języka, żeby napisać test logowania do aplikacji?

Stąd **TestQL** i format `.iql` — Inspection Query Language.

## Co to jest TestQL w jednym zdaniu

To framework testowy, w którym scenariusze testów aplikacji (webowej, API, mobilnej) zapisywane są w pliku `.iql`, wyglądającym podejrzanie podobnie do `.oql` z oqlos — bo używa tej samej gramatyki i tego samego runtime'u, tylko z innym zestawem komend.

## Jak to wygląda w praktyce

Sesja testowa urządzenia MSA G1 — test okresowy 36-miesięczny — wyrażona w `.iql`:

```iql
LOG "Session start"

NAVIGATE "/connect-test-device"
WAIT 500

CLICK "[data-id='d-001'] .btn-test-item"

OPEN_INTERVAL_DIALOG "d-001"
WAIT 300

SELECT "#interval-select" {"value": "36m"}
SELECT_INTERVAL "36m"

CLICK "#interval-start"
START_TEST "ts-c20" {"interval": "36m", "deviceId": "d-001"}

NAVIGATE "/connect-test-protocol?protocol=pro-example123&step=1"
WAIT 500

CLICK ".btn.btn-primary"
STEP_COMPLETE "step-1" {"name": "Wytworzyć podciśnienie", "status": "passed"}

PROTOCOL_FINALIZE "pro-example123"

LOG "Session complete"
```

Czterdzieści sekund operacji operatora, przetłumaczone na dziewiętnaście linii `.iql`. Można je odtworzyć, zmodyfikować, wrzucić do CI.

## Co TestQL daje, czego nie daje Playwright

Zanim odpowiem — Playwright jest świetny i używamy go do głębokich testów integracyjnych. TestQL nie zastępuje Playwright; rozwiązuje inny problem.

**Session recording jako first-class citizen.** W TestQL `session-recording.iql` to zwykły plik. Nie jest to artefakt frameworka, nie jest to nagranie binarne — to czytelny tekst, który może edytować operator, wersjonować się w Git, komentować w code review. Różnica między „odtwórzmy nagranie Cypresa" a „otwórzmy plik, zmieńmy nazwę urządzenia z d-001 na d-047 i uruchommy ponownie" jest jakościowa.

**Jednolity model dla sprzętu i UI.** Operator, który przez rok pracował z `.oql`, rozumie `.iql` w pięć minut. Ta sama gramatyka deklaratywna, te same komendy strukturalne (`WAIT`, `LOG`, `IF`, `STEP_COMPLETE`), ta sama konsola wykonania, ten sam widok wyników. Koszt poznawczy — minimalny.

**Nagrywarka integruje się z aplikacją, nie z przeglądarką.** Recorder TestQL to modul, który aplikacja hostująca może wbudować — tak jak Stripe wbudowuje się przez SDK. Daje to zapisy znacznie wyższej jakości niż „kliknięcie w CSS selector, który może się zmienić" — zapisuje semantyczne zdarzenia domenowe (`STEP_COMPLETE`, `PROTOCOL_FINALIZE`) razem ze strukturalnym kontekstem (ID, metadane).

Czego nie robi: nie zastąpi pełnowartościowego Playwright do testów komponentowych z asercjami na DOM. Nie ma warstwy mockowania sieci na poziomie przeglądarki. Nie renderuje storyboardów. To nie jest narzędzie konkurencyjne — to jest inny poziom abstrakcji.

## Jak to się rozwinęło od stycznia

Cztery rzeczy konkretnie.

Po pierwsze, komendy `OPEN_INTERVAL_DIALOG`, `SELECT_INTERVAL`, `START_TEST`, `STEP_COMPLETE`, `PROTOCOL_FINALIZE` przestały być domenowymi rozszerzeniami — zostały ustandaryzowane jako część rdzenia TestQL. Każda z nich emituje zdarzenie (w tym samym event bus co `.oql`), które możemy przechwycić, logować, forwardować do webhooków.

Po drugie, parser `.iql` dzieli teraz rdzeń z `.oql`. Jeden moduł `_cql_tokenizer.py` (377 linii, CC=5) obsługuje oba formaty. To było celem od początku; w praktyce wymagało przeprojektowania kilku helperów (`_try_task`, `_try_if_fail_block`, `_try_save_ws`) — duplikaty tego typu są w aktualnym raporcie dup.

Po trzecie, wynik sesji TestQL można przetwarzać programowo. `recorded-test-session.iql` w pilotowej instalacji generuje strukturalny JUnit XML, który wpada do CI. Scenariusz krytyczny (pełen przebieg testu urządzenia) jest uruchamiany przy każdym deploy www — jeśli pęknie, deploy się cofa. Przez ostatnie trzy miesiące — jedno automatyczne wycofanie, zapobiegło regresji w kroku „finalizacja protokołu".

Po czwarte, TestQL jest dostępny z tego samego REST API co oqlos. Endpoint `/executions/start` przyjmuje zarówno `scenario_id` z biblioteki `.oql` jak i `.iql`; runtime rozpoznaje dialekt i routuje do odpowiedniego executora.

## Co mnie dziś niepokoi

Trzy rzeczy.

**Recorder jest za ciasno związany z jedną aplikacją.** Nagrywarka była pisana dla konkretnej aplikacji do testów sprzętu. Generalizacja — tak, żeby można było wdrożyć ją jako npm-package do dowolnej aplikacji React/Vue — została odłożona trzy razy. To jest blocker dla TestQL jako standalone oferty.

**Brak asercji poza STEP_COMPLETE.** W obecnej wersji `.iql` mówi „wykonaj krok", ale nie mówi „sprawdź, czy na ekranie pojawiła się liczba 42". Asercje są wyrażane pośrednio — przez to, czy krok został oznaczony jako passed. Dla testów akceptacyjnych to wystarcza, dla głębszych — nie. Planujemy dodać `ASSERT`, `EXPECT_TEXT`, `EXPECT_VISIBLE` w kolejnej wersji.

**Playground.** Nie ma miejsca, w którym developer mógłby w przeglądarce napisać `.iql` i zobaczyć, co się dzieje. Cypress ma `cypress open`, Playwright ma `codegen`. My mamy „zainstaluj oqlos, załaduj aplikację, wywołaj API". Bariera wejścia jest zbyt wysoka dla potencjalnego użytkownika, który nie ma jeszcze problemu do rozwiązania.

## Gdzie to pasuje w strategii

TestQL to drugi filar, obok oqlos, tego co ostatecznie nazwiemy platformą EquipOS/InspectOS (nazwa w procesie decyzyjnym). oqlos odpowiada na pytanie „jak sterować sprzętem", TestQL — „jak testować aplikację, która sterowaniem zarządza". Razem tworzą pełen stack testowy, w którym test aparatu oddechowego i test interfejsu do raportowania tego testu wyrażone są w zgodnym formacie.

Dla segmentu QA — konkurujemy tu pośrednio z Cypress i Postman. Nie przez lepsze asercje (bo nie mamy), tylko przez integrację hardwarową. Jeśli zespół QA ma w zakresie aplikację + sprzęt, TestQL + oqlos to jest spójne rozwiązanie; jeśli tylko aplikację, niech zostanie przy Playwright.

Dla segmentu pharma/medtech (GxP) — TestQL ma jedną cichą zaletę, której nikt nie wypromował: każdy krok ma naturalną ścieżkę audytu, bo jest nazwanym zdarzeniem. Walidacja instalacyjna (IQ), operacyjna (OQ) i kwalifikacyjna (PQ) w `.iql` to pliki, nie kliknięcia. To powinno być w następnym one-pagerze dla pharmy.

## Plan na najbliższe dwa miesiące

Rozbicie recorderu na samodzielny pakiet npm, dodanie podstawowych asercji (`ASSERT_TEXT`, `ASSERT_VISIBLE`, `ASSERT_URL`), uruchomienie playgrounda w przeglądarce z mock-backendem, napisanie jednej migracji dla istniejących użytkowników Postmana (konwerter `.postman_collection.json` → `.iql`).

Jeśli rynek kupi tę historię — TestQL ma szansę stać się pierwszym punktem kontaktu z rodziną oqlos dla ludzi, którzy nie mają w zakresie żadnego sprzętu.

---

Repo: [github.com/softreck/testql](https://github.com/softreck/testql)  
Przykłady sesji: [`recorded-test-session.iql`](https://github.com/softreck/testql/blob/main/examples/recorded-test-session.iql)  
Zapraszamy do testowania — zwłaszcza tych, którzy używają Cypress/Postman i mają opinie.
