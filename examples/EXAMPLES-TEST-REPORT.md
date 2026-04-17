========================================
   RAPORT TESTÓW DOQL EXAMPLES
========================================

## Testowane przykłady (10 projektów)

### .doql.css format
1. asset-management     ✅ BUILD OK | ✅ API OK :8001 | ⚠️ 1 warning
2. e-commerce-shop      ✅ BUILD OK | ✅ API OK :8002 | ✅ Clean
3. kiosk-station        ✅ BUILD OK | ⚠️ No API (workflows only) | ⚠️ 2 warnings
4. todo-pwa            ✅ BUILD OK | ✅ API OK :8003 | ⚠️ 1 warning

### .doql / .doql.less / .doql.sass format
5. blog-cms            ✅ BUILD OK | ✅ API OK :8005 | ✅ Clean
6. crm-contacts        ✅ BUILD OK | ✅ API OK :8006 | ✅ Clean
7. iot-fleet           ✅ BUILD OK | ✅ API OK :8007 | ✅ Clean (fixed DB string)
8. calibration-lab     ✅ BUILD OK | ✅ API OK :8008 | ✅ Clean
9. document-generator  ✅ BUILD OK | ⚠️ No API (workflows only) | ✅ Clean
10. notes-app          ✅ BUILD OK | ✅ API OK :8010 | ⚠️ 2 warnings

## Uruchomione usługi API (FastAPI/Uvicorn)

| Port | Projekt             | Status | Endpoint dokumentacji   |
|------|---------------------|--------|-------------------------|
| 8001 | asset-management    | ✅     | http://localhost:8001/docs |
| 8002 | e-commerce-shop     | ✅     | http://localhost:8002/docs |
| 8003 | todo-pwa           | ✅     | http://localhost:8003/docs |
| 8005 | blog-cms           | ✅     | http://localhost:8005/docs |
| 8006 | crm-contacts       | ✅     | http://localhost:8006/docs |
| 8007 | iot-fleet          | ✅     | http://localhost:8007/docs |
| 8008 | calibration-lab    | ✅     | http://localhost:8008/docs |
| 8010 | notes-app          | ✅     | http://localhost:8010/docs |

## Usługi bez API (workflows only)

| Projekt             | Dlaczego bez API?                      |
|---------------------|----------------------------------------|
| kiosk-station       | Kiosk appliance - generuje workflows   |
| document-generator  | Doc gen service - generuje workflows   |

## Web frontend (Vite)

| Projekt             | Port | Status |
|---------------------|------|--------|
| asset-management    | 5173 | ✅ Running |
| e-commerce-shop     | 5173 | ✅ Running |

## Podsumowanie

✅ **Walidacja**: 10/10 projektów przeszło walidację
✅ **Build**: 10/10 projektów zbudowało się poprawnie
✅ **API**: 8/10 projektów z pełnym API działa (zmienione na SQLite)
⚠️  **Workflows only**: 2 projekty generują tylko workflows (expected)
✅ **Web**: 2 projekty z web frontend działają na Vite

## Problemy napotkane i rozwiązane

1. **PostgreSQL → SQLite**: Wszystkie projekty domyślnie używają PostgreSQL,
   zmienione na SQLite do testów lokalnych przez `sed`
   
2. **IoT-fleet syntax error**: Brak zamknięcia cudzysłowu w database.py
   po pierwszej próbie sed - naprawione ręcznie

3. **Kiosk-station brak main.py**: Ten projekt generuje tylko workflows,
   nie pełne API (zgodnie z designem - kiosk to appliance)

========================================

Testy wykonano: $(date)
