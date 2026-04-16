---
title: "oqlos.com — pierwsze sześć miesięcy platformy SaaS"
slug: "saas-www-status-2026-q2"
date: 2026-04-16
author: "Softreck"
categories: ["www", "status update", "saas", "marketing"]
tags: ["saas", "oqlos", "landing", "pricing", "i18n", "product"]
excerpt: "Sześć miesięcy po uruchomieniu strony SaaS mamy działającą aplikację, 309 linii strony Account, 34 testy e2e i bardzo jasne diagnozy co zostało do poprawy przed targami."
language: pl
status: draft
---

# oqlos.com — pierwsze sześć miesięcy platformy SaaS

Uruchomienie SaaS-owej warstwy produktu — oqlos.com — miało prosty cel: dać potencjalnemu klientowi miejsce, w którym bez instalacji niczego może obejrzeć język, zobaczyć demo, kupić plan. Sześć miesięcy później mamy front, mamy backend, mamy auth, mamy billing — i mamy bardzo konkretną listę tego, co trzeba zmienić, żeby to zaczęło sprzedawać.

## Stan warstwy webowej, miary

Monorepo `www/` — 180 plików, 20 100 linii, głównie React (53 plików) z niewielką ilością narzędziowego JS i konfiguracji. Średnia złożoność cyklomatyczna modułów `www/` spadła z 4,9 (w listopadzie) do 2,6 dzisiaj. Strona główna `Landing.jsx` ze złożoności 20 zeszła do 2. `Account.jsx` — nowa strona zarządzania kontem — ma 309 linii i pokrycie 34 testami end-to-end w Playwright.

Tyle statystyk. Przechodzę do tego, co to znaczy dla produktu.

## Co działa

**Autentykacja.** JWT z obsługą automatycznego logowania dla kont testowych (`test@test.com`, `demo@oqlos.com`) — pozwala pokazywać demo bez ceremonii rejestracji. Routowanie chronione przez `ProtectedRoute`, przekierowania z i do stron wymagających auth działają.

**Internacjonalizacja.** Plik `pl.json` — 92 klucze, polski pełny. `en.json` istnieje w drzewie, ale (ten punkt mnie uwiera) zawartość nie została uzupełniona do ostatniego stanu. Dla angielskiego użytkownika części interfejsu pokazują klucze zamiast tłumaczeń. To pierwszy priorytet tygodnia.

**Mock API w trybie dev.** Wszystkie strony — prawie wszystkie — używają `mockFetch` w trybie `VITE_FORCE_MOCK_API=true`, co pozwala pracować nad frontem bez stawiania backendu. Wyjątek: `NlpConsole.jsx` omija mockFetch i w trybie dev nie działa. Kolejny konkretny bug do naprawy, patrz niżej.

**Infrastruktura.** Quadlet (Podman systemd) dla produkcji jest gotowy — `infra/quadlet/*.container`. Dla developerki `docker-compose.test.yml` z seed data (`init-test-data.sql`) — chociaż tu walidator zgłasza trzy błędy parsowania w SQL. Do sprawdzenia.

## Co nie działa albo potknie się o własne nogi

Diagnoza uczciwa.

**Bug #1 — `lang` niezdefiniowane na Landingu.** W `Landing.jsx:48` odwołania do `lang === 'pl'` są bez destruktyryzacji z `useI18n()`. W runtime — `ReferenceError`, cała strona główna pada. To jest strona, którą zobaczy pierwszy odwiedzający. Naprawa: 15 minut. Dlaczego to nie zostało złapane? Bo w dev-mode z mocked i18n hook bywa wstrzykiwany inaczej; na produkcji — błąd. Test e2e na podstawowy rendering strony głównej powinien to wychwycić. Dodane do planu tygodnia.

**Bug #2 — `NlpConsole.jsx` używa `fetch` zamiast `mockFetch`.** W trybie mock NlpConsole nie działa w ogóle. Napraw przez jeden import, 15 minut.

**Bug #3 — `Scenarios.jsx` po usunięciu wbudowanego guard'u nie ma ochrony trasy.** Jeśli `<ProtectedRoute>` w `App.jsx` nie obejmuje `/scenarios`, niezalogowany użytkownik widzi pusty dashboard. Wymaga weryfikacji w App.jsx.

**Bug #4 — duplikat klucza `status` w `account` sekcji `pl.json`.** Parser JSON tego nie zgłosi, ale drugi klucz nadpisuje pierwszy. Może powodować cichą niezgodność tłumaczeń. Naprawa: 5 minut.

**Bug #5 — `en.json` niedopełnione.** Jak wyżej.

Plus jedno subtelne: `TerminalSim.jsx` ma CC=15 — to komponent symulujący terminal na Landingu, zbudowany imperatywnie. Działa, ale kolejna zmiana będzie bolała.

## Co mówi mi to o produkcie

Gdy piszesz stronę SaaS pierwszy raz, skupiasz się na tym, żeby wszystko się renderowało i klikało. Gdy wracasz po sześciu miesiącach, widzisz, że renderowanie i klikanie to minimum, nie produkt.

**Landing ma siedem sekcji i nie ma odpowiedzi na podstawowe pytanie.** Test pięciu sekund: w ciągu pięciu sekund na stronie głównej odwiedzający powinien wiedzieć (1) co to jest, (2) dla kogo, (3) jaki problem rozwiązuje, (4) co robić dalej. Obecna strona mówi „Open Source DSL" — odpowiada na (1). Na (2), (3), (4) — nie mówi. Hero subtitle: „Automatyzacja testów sprzętu przemysłowego w deklaratywnym DSL. Uruchom na Dockerze, Raspberry Pi lub w chmurze — od aparatów oddechowych po systemy IoT." To jest dla wszystkich, czyli dla nikogo w szczególności.

**Call-to-Action wszystkie tego samego typu.** „Docker Quick Start", „Wypróbuj OQL Live", „REST API" — wszystkie dla technicznego użytkownika. Decyzyjny manager? Inżynier oceniający? Handlowiec zbierający opinie w dziale QA swojej firmy? Nic. Segmentacja CTA — jedna z rzeczy do zrobienia w tym tygodniu.

**Brak case studies.** Metryki, które reklamujemy na landingu — „96 testów passing", „CC̄≤15", „3 scenariusze 12/12 goals" — to metryki kodu, nie metryki biznesowe. Przekonują developera. Nie przekonują CFO firmy testującej 200 masek miesięcznie. Przekonuje hipotetyczna historia: „Firma X z Gdańska testuje 200 aparatów miesięcznie. Przed: 3 operatorów, 15 min/test, Excel. Po: 1 operator, 4 min/test, automatyczny PDF. Oszczędność: 120 godzin miesięcznie, 6 000 euro rocznie." Taką historię trzeba napisać — na początku jako „przykładowe wdrożenie", potem z realnym klientem za zgodą.

**Brak wersji niemieckiej.** Plan zakłada walidację targową w Niemczech. `de.json` — nie istnieje. Tłumaczenie 92 kluczy to dwa-trzy dni pracy z tłumaczem, robimy natychmiast.

## Pricing — trzy plany to za mało

Obecny układ Free/Pro/Enterprise nie obsługuje:

- Studentów i makerów (chcą free edukacyjne, ale nie chcą ograniczenia na 1 urządzenie)
- Małych firm z 2-20 urządzeniami (Pro flat 49€ jest za dużo, Enterprise to inna rozmowa)
- Klientów regulowanych (pharma, medtech) — chcieliby dodatek compliance, nie pełny Enterprise

Planujemy rozszerzyć do pięciu poziomów: Starter (0€, edukacyjny) / SMB (9€ per device per month) / Pro (49€ flat) / Compliance Pack (+49€ dodatek) / Enterprise (custom). Argumentacja biznesowa — pokrycie szerszego rynku TAM bez rozwadniania głównej oferty. Implementacja — dwa dni modyfikacji w Billing.jsx i integracji Stripe.

## Co zrobimy w tym tygodniu

Bez upiekszania, konkretny plan pięciu dni:

Poniedziałek — bugi P0 (wszystkie pięć, łącznie około 2,5 godziny) plus uzupełnienie `en.json` i wypchnięcie do staging. To minimum, żeby strona działała dla nie-polskiego użytkownika.

Wtorek — warianty A/B dla hero subtitle (cztery wersje zorientowane na różne persony: industrial, QA, pharma, DevOps), przebudowa struktury Landingu z siedmiu sekcji do czterech głównych (hero → social proof → use cases → pricing), przepisanie feature cards z języka cech na język korzyści.

Środa — dwa-trzy case studies, ROI calculator jako prosta strona (cztery suwaki → szacunkowa oszczędność), osadzenie Cal.com dla „Umów prezentację (15 min)".

Czwartek — tłumaczenie DE, pierwsza strona Academy (free dla uczelni), integracja Slack (webhook do wyników testów), commit i deploy staging.

Piątek — pełny e2e na staging, deploy produkcji, ogłoszenie na LinkedIn i r/selfhosted, ustawienie analitycznego (Plausible), pierwszy retro.

To są rzeczy, które można zrobić bez nowych featuresów. Marketing i UX są tańsze niż kod, a efekt — większy.

## Czego nauczyliśmy się

Trzy rzeczy, które powtórzę sobie przy następnym produkcie.

**Nie dodawaj funkcji dopóki nie masz użytkownika.** Marketplace, Compliance Pack, Academy — wszystkie w backlogu, wszystkie kuszące do zbudowania „żeby było". Tylko jeden realny klient pilotowy; każda nowa funkcja bez ich potwierdzenia to potencjalny dług.

**Nie celuj we wszystkie segmenty naraz.** „Od aparatów oddechowych po IoT" — tak napisane, trafia w nikogo. Beachhead — polskie firmy BHP testujące SCBA. Zdominować ten segment, potem rozszerzać. To nie jest rozmycie ambicji, to dyscyplina.

**Nie inwestuj w marketing bez produktu.** Gdyby przed chwilą była masowa kampania reklamowa, prowadziłaby na stronę, która pada z ReferenceError. Najpierw naprawiać, potem zapraszać.

---

Produkt: [oqlos.com](https://oqlos.com)  
Staging: [staging.oqlos.com](https://staging.oqlos.com)  
Feedback — przycisk „thumbs down" pod dowolną stroną, albo issue w repo.
