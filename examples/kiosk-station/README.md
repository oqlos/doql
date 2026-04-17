# Example: Kiosk Station

Stanowisko operatora w trybie kiosk na tablecie / Raspberry Pi z 10-calowym ekranem dotykowym. Operator loguje się PIN-em, skanuje sprzęt kodem kreskowym, uruchamia scenariusz testowy, drukuje etykietę. Bez myszy, bez klawiatury, bez dostępu do systemu — jak terminal samoobsługowy w serwisie samochodowym, tylko dla stanowisk testowych PSA.

## Formaty

- `app.doql` — klasyczny format DOQL
- `app.doql.css` — wariant CSS-like (SSOT)

---

## Szybki start

```bash
# 1. Skopiuj ten katalog
cp -r doql/examples/kiosk-station my-kiosk
cd my-kiosk

# 2. Skonfiguruj sekrety
cp .env.example .env
$EDITOR .env    # wpisz OQLOS_URL, bazy danych

# 3. Waliduj deklarację
doql validate

# 4. Zobacz plan generowania
doql plan

# 5. Wygeneruj cały kod
doql build
# → build/api/        Backend FastAPI
# → build/infra/      Skrypty instalacyjne, systemd service
# → build/workflows/  Workflows offline sync i auto-logout

# 6. Zainstaluj na urządzeniu (patrz sekcja niżej)

# 7. Deploy na produkcję
doql deploy --env prod
```

---

## Uruchamianie aplikacji

### Lokalnie (dev mode)

```bash
cd build/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Dokumentacja API: http://localhost:8000/docs

### Na Raspberry Pi (kiosk mode)

```bash
# Skopiuj skrypty na urządzenie
scp -r build/infra pi@kiosk-01.local:/tmp/

# Zainstaluj kiosk
ssh pi@kiosk-01.local "sudo /tmp/infra/install-kiosk.sh"

# Reboot aby uruchomić kiosk
ssh pi@kiosk-01.local "sudo reboot"
```

Po rebootie urządzenie startuje prosto do aplikacji w trybie kiosk (Chromium).

### Docker Compose

```bash
cd build/infra
docker-compose up
```

---

## Dlaczego kiosk, a nie zwykła PWA

**PWA na tablecie** = operator może wyjść z aplikacji, otworzyć Facebooka, zablokować się w ustawieniach, zainstalować TikToka. W warsztacie z 15 operatorami zmianowymi — nie da się tego utrzymać.

**Kiosk appliance** = tablet startuje prosto do aplikacji, nie ma paska przeglądarki, nie ma dostępu do systemu, PIN obowiązuje przez 8h lub do zamknięcia zmiany. Krashuje — restartuje się. Pada internet — pracuje z lokalnego SQLite i synchronizuje po przywróceniu.

Różnica między "możesz korzystać z aplikacji" a "ta aplikacja to cały twój tablet".

---

## Co widzi operator

1. **Ekran powitalny** — "Stanowisko testowe WS-01 · Zeskanuj swój identyfikator lub wpisz PIN"
2. **PIN pad** — 4 cyfry, duże przyciski 120×120px (tak, żeby działały z rękawiczkami warsztatowymi)
3. **Menu główne** — 4 kafelki: Nowa inspekcja · Moje zadania · Zwrot sprzętu · Pomoc
4. **Skaner kodów** — pełnoekranowy widok kamery albo nasłuch na USB scanner
5. **Szczegóły urządzenia** — zdjęcie, numer seryjny, status, historia
6. **Guided flow inspekcji** — 4 kroki, każdy z wielkim przyciskiem "Dalej"
7. **Wynik** — PASS na całym ekranie zielono albo FAIL czerwono
8. **Wydruk etykiety** — automatycznie na Zebrze ZPL

Między etapami ładna animacja, żeby było wiadomo, że coś się dzieje.

---

## Co dostajesz z `doql build`

```
build/
├── kiosk-app/                    # Aplikacja w Electron/Tauri/webview
│   ├── src/
│   │   ├── pages/                # home, scan, device_detail, inspection
│   │   ├── components/           # PinPad, BarcodeScanner, GuidedFlow
│   │   ├── offline-queue.ts      # kolejka operacji offline
│   │   ├── sync.ts               # synchronizacja z oqlos
│   │   └── hardware/             # bindingi USB, printer, camera
│   └── main.ts
│
├── kiosk-os/                     # Konfiguracja systemowa
│   ├── install.sh                # instalator na Raspberry Pi
│   ├── openbox-autostart         # chromium --kiosk
│   ├── systemd/
│   │   ├── kiosk-app.service
│   │   ├── kiosk-sync.timer
│   │   └── kiosk-watchdog.service
│   └── image-builder.sh          # buduje obraz .img do sdcard
│
├── infra/
│   ├── quadlet/
│   │   └── kiosk-app.container
│   └── ota-server/               # backend do OTA updates (opcjonalnie)
│
└── data/
    ├── operators.db              # szablon
    └── devices.db                # szablon
```

---

## Deploy na fizyczne urządzenie

### Wariant A: Raspberry Pi 4 + ekran dotykowy 10"

```bash
# Zbuduj
doql build --target kiosk-appliance --os rpi-os-lite-64

# Opcja 1: instalacja na już zainstalowanym RPi OS
scp -r build/kiosk-os pi@kiosk-01.local:/tmp/
ssh pi@kiosk-01.local "sudo /tmp/kiosk-os/install.sh"

# Opcja 2: pełny image .img do karty SD
doql kiosk image --output kiosk-ws-01.img
# → dd if=kiosk-ws-01.img of=/dev/sdX bs=4M
```

Po pierwszym bootze tablet startuje prosto do aplikacji. Logowanie przez PIN, scanner USB podpięty i skonfigurowany.

### Wariant B: Tablet Android z trybem kiosk (np. Samsung Knox)

Używa PWA zamiast Electrona. W Knox Configure ustawiasz URL aplikacji jako home screen, wyłączasz wszystko poza nią.

### Wariant C: Tablet Windows 10/11 IoT

Kiosk mode wbudowany w Windows. Aplikacja jako UWP lub PWA.

---

## Kluczowe cechy implementacji

### Offline-first

Każda operacja operatora (uruchomienie testu, zapis wyniku, wydruk etykiety) jest **najpierw zapisywana lokalnie**, potem wysyłana do oqlos. Jeśli sieć pada — operator nie zauważa różnicy, queue synchronizuje się po przywróceniu.

```
operator wciska "Start test"
  ↓
zapis do /var/lib/kiosk/queue/20260416-143022-start.json
  ↓
próba wysłania do oqlos
  ├── sukces → usuwamy z queue
  └── timeout → retry co 10s, 30s, 1m, 5m (exponential backoff)
```

### Sesja PIN

Po zalogowaniu PIN-em sesja trwa 8 godzin lub do wylogowania. Operatorzy na zmianę 8h nie muszą wpisywać PIN-a co 10 minut — to byłoby irytujące i w praktyce nigdy tak nie działa.

Po 3 minutach bezczynności aplikacja pokazuje idle screen (slideshow z BHP). Dotknięcie — wraca do menu, **bez** konieczności ponownego PIN-a (sesja aktywna). Po pełnym wylogowaniu albo timeoucie 8h — od nowa.

### Hardware bindings

- **USB Barcode Scanner** — zwykle emuluje klawiaturę, więc nasłuchujemy na `keydown` z końcówką `Enter`. Działa out of the box.
- **ZPL Printer** — Zebra ZPL przez USB-serial (/dev/ttyUSB0) albo TCP. Template etykiety w `templates/label.zpl`.
- **Camera** — do zdjęć usterek, używamy WebRTC `getUserMedia()`.

### Lockdown — co jest wyłączone

- Alt+F4, Alt+Tab, Ctrl+Alt+Del (na ile system pozwoli)
- Prawy klik → menu kontekstowe
- F12 / Ctrl+Shift+I (developer tools)
- Multi-touch gesty systemowe
- Pasek statusu, notyfikacje
- Instalacja aplikacji (bez roota nie da się)

### Auto-update OTA

Co noc o 3:00 kiosk sprawdza, czy na `env.OQLOS_URL/ota` jest nowsza wersja. Jeśli tak — pobiera, weryfikuje podpis, restartuje się. Jeśli nowa wersja nie wystartuje w ciągu 90s — rollback do poprzedniej.

---

## Czym to różni się od "Pactown" (jeśli znasz ten produkt)

Pactown, o ile znam, to konkretne wdrożenie kiosk-mode dla sieci serwisów samochodowych. Różnice architektoniczne w naszym podejściu:

- **DOQL jako źródło prawdy** — zmieniasz jedną deklarację, regenerujesz aplikację. Bez edycji XAML/kodu.
- **Wielowarstwowa integracja** — kiosk rozmawia z oqlos (scenariusze), testql (walidacja UI), weboql (zarządzanie). W tej samej rodzinie języków.
- **Offline-first domyślnie** — nie jako feature, jako podstawa. Stacja testowa w warsztacie pod ziemią, bez LTE? Działa.
- **Open core** — aplikacja jest Twoja, kod wygenerowany, wolno modyfikować.

---

## Testowanie

Ponieważ kiosk jest trudny do automatycznego testowania (touch, USB scanner, PIN pad), testujemy go na dwa sposoby.

**Testy jednostkowe** — komponenty React/Vue jak zwykle, Vitest / Jest.

**Testy UI** — `.iql` ze zdarzeniami semantycznymi:

```iql
SESSION: "Pełny flow inspekcji w kiosk"

NAVIGATE "/welcome"
CLICK ".btn-login"
PIN_ENTRY "1234"
ASSERT_VISIBLE ".menu-home"

CLICK "[data-action='scan']"
BARCODE_SCAN "PSS7000-A-001234"
ASSERT_TEXT ".device-model" "PSS 7000"

CLICK "[data-action='start-inspection']"
SELECT_SCENARIO "pss7000_full_test"
CLICK ".btn-next"
CLICK ".btn-device-connected"
WAIT_FOR_EXECUTION max=30m
ASSERT_RESULT "pass"

CLICK ".btn-end"
ASSERT_URL "/home"
```

Ten sam framework (testql) co do testów aplikacji webowej.

---

## Ograniczenia i planowany rozwój

1. **Pełny OTA nie jest jeszcze zaimplementowany** — obecnie tylko ręczny push przez ssh + systemctl restart.
2. **Podpis OTA pakietów** — docelowo przez signify lub GPG, obecnie checksumy SHA256.
3. **Multi-station management** — 50+ kiosków w sieci. Obecnie każdy zarządzany osobno; dashboard flotowy planowany.
4. **Integracja z Active Directory / LDAP dla operatorów** — obecnie PIN-y w lokalnym SQLite.
5. **Accessibility** — ekran dla operatora niedowidzącego, tryb wysokiego kontrastu OK, czytnik ekranu nie.
