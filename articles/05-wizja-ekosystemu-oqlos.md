---
title: "Rodzina oqlos — cztery warstwy, jeden cel"
slug: "wizja-ekosystemu-oqlos"
date: 2026-04-16
author: "Softreck"
categories: ["vision", "ecosystem"]
tags: ["oqlos", "testql", "doql", "weboql", "strategy", "architecture", "open core"]
excerpt: "oqlos, testql, weboql, doql — cztery projekty, cztery warstwy abstrakcji. Gdy widać je razem, strategia staje się czytelna."
language: pl
status: draft
---

# Rodzina oqlos — cztery warstwy, jeden cel

Gdy zaczynaliśmy od `.oql`, nie było planu ekosystemu. Był konkretny problem: jak opisać test aparatu oddechowego tak, żeby opis ten był czytelny dla operatora BHP, wykonywalny przez maszynę i wersjonowalny w Git. Z tego wyrosło `oqlos`.

Potem, pracując nad interfejsem do zarządzania scenariuszami, zobaczyliśmy, że możemy użyć tego samego formatu do testowania samej aplikacji — tak powstał `.iql` i `testql`. Strona SaaS-owa — `weboql` i `www`. A teraz `doql` — generator kompletnych aplikacji z deklaracji.

Cztery projekty. Gdy układam je warstwowo, pojawia się spójna struktura.

## Stratyfikacja

```
┌─────────────────────────────────────────────────────────┐
│  doql      — generator aplikacji z deklaracji            │
│              (analogia: Rails, Django, Retool)           │
├─────────────────────────────────────────────────────────┤
│  testql    — framework testowy nad oqlos (.iql)          │
│  weboql    — web layer + IDE                             │
│              (analogia: pytest, Jupyter)                 │
├─────────────────────────────────────────────────────────┤
│  oqlos     — runtime interpretujący .oql                 │
│              (analogia: CPython, Node.js)                │
├─────────────────────────────────────────────────────────┤
│  Hardware  — Modbus, MQTT, USB, GPIO, I²C                │
│              (Raspberry Pi, ADS1115, DRI0050, …)         │
└─────────────────────────────────────────────────────────┘
```

Każda warstwa stoi na niższej i nie przecieka do wyższej. Jeśli zrobimy to dobrze, zmiana sprzętu nie wymusi zmiany w `doql`. Zmiana generatora UI w `doql` nie wymusi przebudowy `oqlos`.

## Dla kogo co

**`oqlos`** — dla każdego, kto ma sprzęt do zautomatyzowania. Producent stanowisk testowych, integrator systemów przemysłowych, firma kalibracyjna, zespół HIL w firmowym R&D. Nie dla końcowego operatora, nie dla CFO.

**`testql`** — dla zespołu QA, który testuje aplikację dotykającą sprzętu. Alternatywą jest Playwright lub Cypress plus ręczne przełączanie kontekstu. Z `testql` — jeden DSL dla obu.

**`weboql`** — dla każdego, kto edytuje scenariusze. Operator BHP, inżynier serwisu, technik kalibracji. IDE w przeglądarce, składniowo podświetlanie, edytor wizualny (w roadmapie), live execution.

**`doql`** — dla producentów aplikacji, którzy chcą wdrażać systemy typu Drägerware, lab kalibracyjny ISO 17025, flotę IoT — bez pisania każdego od zera. Dla konsultantów i integratorów, którzy każdemu klientowi dostarczają customizację podobnej domeny.

Ten podział ról jest ważny dla marketingu. Każda warstwa ma inny ICP, inny poziom technicznego detalu, inną cenę, inną obietnicę.

## Model biznesowy — open core, warstwowo

Każda warstwa ma swoją strategię licencyjną.

**`oqlos`** — Apache 2.0 w rdzeniu. Premium pluginy (enterprise hardware, high-throughput drivers) na licencji komercyjnej. Powód — sprzęt premium niszowe rozwiązania nie konkurują z Apache, bo tamte rynki nie kupują bez wsparcia i SLA.

**`testql`** — Apache 2.0. To jest brama wejściowa — im więcej zespołów QA tego używa, tym więcej dociera do oqlos. Zarabianie na `testql` bezpośrednio — nie ma sensu.

**`weboql`** — Apache 2.0 dla podstawowej wersji (edytor pojedynczego użytkownika). Multi-tenant cloud hosting i enterprise features (SSO, audit, white-label) — komercyjne.

**`doql`** — Apache 2.0 dla generatora. Premium szablony domenowe (doql-plugin-gxp, doql-plugin-iso17025, doql-plugin-fleet) — komercyjne. To jest analogia do GitLab albo Sentry: rdzeń otwarty, enterprise pluginy zamknięte.

W sumie — rdzeń używalny za darmo w każdej warstwie. Pieniądze są w premium dodatkach dla regulowanych branż (pharma, medtech, lab), multi-tenant hostingu i wsparcia.

## Dlaczego warstwowość wygrywa

Dwa lata temu mieliśmy pokusę, żeby zrobić jeden duży produkt — „platformę do testowania sprzętu z interfejsem i workflow-em". Dobrze, że tego nie zrobiliśmy.

**Bo użytkownik oqlos nie musi widzieć doql.** Firma, która chce tylko sterować swoim stanowiskiem testowym, instaluje `oqlos`, pisze kilka `.oql`, jest szczęśliwa. Nie musi wiedzieć, że istnieje czterowarstwowy ekosystem. Nie musi się zastanawiać, czy potrzebuje SaaS, czy nie. Każda warstwa jest produktem osobno.

**Bo każdą warstwę można testować osobno.** Zmiany w `doql` nie wymagają regresji `oqlos`. Usterka w `www` nie znaczy, że `oqlos` nie działa u klientów. To oznacza szybsze release'y i mniejsze ryzyko.

**Bo każdą warstwę można sprzedawać osobno.** Klient, który kupił `oqlos` (runtime + wsparcie), może za rok dokupić `doql` (generator + szablony). Klient, który zaczął od `testql` (framework QA), może odkryć, że potrzebuje też oqlos. Każdy ruch w górę po stosie jest naturalnym upsell-em.

## Spójność językowa

Jedna rzecz, która spina wszystkie warstwy: ta sama gramatyka deklaratywna. `.oql` i `.iql` mają wspólny parser, wspólny tokenizer (`_cql_tokenizer.py` w repo). Operator, który w poniedziałek pisze scenariusz hardwareowy, we wtorek potrafi napisać test UI bez zmiany modelu umysłowego.

`.doql` pójdzie o krok dalej — użyje tej samej estetyki składniowej (blokowa, wcięciami, frazy naturalno-językowe) do opisu aplikacji. Patrząc na trzy pliki:

```oql
# oqlos
SCENARIO: "Test maski"
GOAL: Podciśnienie
  SET pompa-1 "5 l/min"
  WAIT 2000
  IF AI01 < -15 mbar ELSE ERROR "Poza zakresem"
```

```iql
# testql
SCENARIO: "Logowanie użytkownika"
NAVIGATE "/login"
TYPE "#email" "user@example.com"
CLICK "#submit"
ASSERT_URL "/dashboard"
```

```doql
# doql
APP: "Manager inspekcji"
ENTITY Device:
  serial: string!
  status: enum[ready, failed]
INTERFACE web:
  PAGE devices: crud
```

Trzy różne domeny, jeden model umysłowy. To jest świadomy wybór projektowy — i, jak sądzę, nasz najmocniejszy długoterminowy wyróżnik wobec fragmentowanych konkurentów (Cypress + Postman + Retool + Snipe-IT + Ansible, każdy ze swoim DSL-em).

## Nazwy, problem otwarty

Do dziś używam w notatkach roboczo nazw `oqlos`, `testql`, `weboql`, `doql`. Ale rodzina-parasol nie ma zatwierdzonej nazwy. Eksplorowaliśmy `EquipOS` i `InspectOS` — oba wskazują na inspekcję/sprzęt, oba są wolne w Google i w IP. Argumenty za `EquipOS` — szersza domena (każdy sprzęt, nie tylko inspekcje). Argumenty za `InspectOS` — silniejsze pozycjonowanie, bo inspekcja jest konkretnym use case.

Nazwa samego języka jądrowego: `EQL (Equipment Query Language)` to obecny faworyt. `HQL` odpadło przez konflikt z Hibernate Query Language w ekosystemie Java — ludzie by szukali jednego, trafiali na drugie.

To nie jest decyzja kosmetyczna. Pierwszy klient, który wpisze `EquipOS` w Google, chce znaleźć nas; jeśli znajduje stronę innej firmy — strata bramy wejściowej. Ta decyzja powinna zapaść przed obecnością na targach w Niemczech.

## Co się musi zdarzyć, żeby to zadziałało

Trzy rzeczy, w kolejności ważności.

**Utrzymać dyscyplinę warstw.** Będzie pokusa, żeby w `doql` zrobić własny runtime pomijając oqlos, albo w `testql` zaimplementować własne wykonanie pomijając core. Każde takie pęknięcie to dług, który się zemści. Warstwa wyższa mówi przez API niższej, nie robi skrótu.

**Pozyskać drugi pilot klient poza hardware-BHP.** Cały ekosystem jest obecnie walidowany przez jeden segment. Drugi pilot — lab kalibracyjny albo pharma/medtech — będzie potwierdzeniem, że warstwowa architektura rzeczywiście przenosi się na inne domeny. Bez tego ryzykujemy, że budujemy coś dopasowanego tylko do jednego use case.

**Dostarczyć historii technicznej, której nie można zignorować.** Case studies, porównania konkurencyjne, roadmapy, statystyki. Prawie wszystko to mamy fragmentarycznie; nic nie jest uporządkowane w jeden dokument, który można wysłać inwestorowi, dziennikarzowi, albo analitykowi branżowemu. Strategiczna dokumentacja jako produkt.

---

## Podsumowanie w trzech zdaniach

Cztery projekty, cztery warstwy, jeden model umysłowy. Każda warstwa stoi na niższej, każda warstwa jest produktem, każda warstwa ma własny ICP i własną ścieżkę pieniężną. Jeśli przez następny kwartał nic nie popsuje tej stratyfikacji, mamy szansę być pierwszym spójnym ekosystemem testowo-aplikacyjnym w tej niszy.

---

Repozytoria: [oqlos](https://github.com/softreck/oqlos) · [testql](https://github.com/softreck/testql) · [weboql](https://github.com/softreck/weboql) · [doql](https://github.com/softreck/doql)  
Pojedyncze artykuły szczegółowe — zobacz kategorie *status update* na tym blogu.
