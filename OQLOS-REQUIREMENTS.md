# Wymagania dla oqlos aby doql był możliwy

> Lista zmian/dodatków w `oqlos` niezbędnych do implementacji `doql` w pełni. Kolejność — od krytycznych do nice-to-have.

---

## 1. KRYTYCZNE (bez tego `doql` nie ma jak działać)

### 1.1 Schema Introspection API

**Problem:** `doql build` musi wiedzieć, jakie peryferia, sensory, komendy i typy danych są dostępne w oqlos, żeby generator UI wiedział co narysować.

**Co dodać:** endpoint + CLI do eksportu pełnego schema:

```python
# oqlos/oqlos/api/introspection.py  (NOWY)
@router.get("/v1/schema")
def get_schema() -> Schema:
    return Schema(
        peripherals=list_peripherals(),     # pumps, valves, sensors
        commands=list_dsl_commands(),        # SET, GOAL, WAIT, ...
        types=list_peripheral_types(),
        plugins=list_loaded_plugins(),
    )

# CLI
$ oqlctl schema export --format=json > schema.json
```

**Dlaczego to krytyczne:** bez tego `doql` musi hardcodować listę peryferii.

**Ile pracy:** 4h (schema już istnieje rozproszone, trzeba tylko wystawić).

---

### 1.2 Event Bus / Webhooks

**Problem:** `doql` potrzebuje wiedzieć KIEDY scenariusz się skończył, JAKI był wynik, JAKIE błędy — żeby wywołać webhook, zaktualizować UI, zapisać raport.

**Co dodać:** pub/sub event stream + webhook dispatch.

```python
# oqlos/oqlos/core/events.py  (NOWY)
EVENTS = [
    "scenario.started",
    "scenario.goal.started",
    "scenario.goal.completed",
    "scenario.goal.failed",
    "scenario.completed",
    "scenario.failed",
    "hardware.connected",
    "hardware.disconnected",
    "peripheral.value_changed",
]

# Konfiguracja w oqlos.yaml
webhooks:
  - event: scenario.completed
    url: http://doql-backend/hook
    secret: ${WEBHOOK_SECRET}
    retry: 3
```

**Co już jest częściowo:** SSE stream w `/api/execution/stream` — trzeba to ucywilizować i udokumentować jako stabilne API.

**Ile pracy:** 1 dzień.

---

### 1.3 Multi-tenancy (organization_id)

**Problem:** Aplikacje generowane przez `doql` są często SaaS. Muszą izolować dane per klient.

**Co dodać:** `organization_id` we wszystkich modelach + middleware filtrujące:

```python
class Scenario(Base):
    id: int
    organization_id: str     # NOWE
    name: str
    content: str

class Execution(Base):
    id: str
    organization_id: str     # NOWE
    scenario_id: int
    # ...

# Middleware
@app.middleware("http")
async def inject_org(req: Request, call_next):
    req.state.org_id = resolve_org_from_jwt(req)
    return await call_next(req)
```

**Migracja:** dodać kolumnę `organization_id` (nullable w pierwszej wersji, NOT NULL po migracji).

**Ile pracy:** 2 dni (migracja DB + aktualizacja wszystkich query w API).

---

### 1.4 Auth / RBAC warstwa

**Problem:** `doql` deklaruje role (`operator`, `manager`, `auditor`) — oqlos musi je respektować przy uruchamianiu scenariuszy.

**Co dodać:** 

```python
# oqlos/oqlos/auth/models.py  (NOWY)
class User(Base):
    id: str
    email: str
    organization_id: str
    roles: list[str]

class Role(Base):
    name: str                       # 'operator', 'manager', ...
    permissions: list[str]          # ['scenario.execute', 'device.read', ...]

# W API:
@router.post("/scenarios/{id}/execute")
@require_permission("scenario.execute")
async def execute(id: int, user: User = Depends(current_user)):
    ...
```

Do rozważenia: integracja z Keycloak / Authentik zamiast własnego systemu.

**Ile pracy:** 3-5 dni (z migracją JWT).

---

### 1.5 Plugin Registry Discovery

**Problem:** `doql` musi dynamicznie wiedzieć, jakie pluginy hardwarowe są zainstalowane (żeby UI wiedział, czy pokazywać opcję „skanuj barcode" albo „kamera termalna").

**Co dodać:** entry points w setup.py + katalog pluginów.

```python
# setup.py
entry_points={
    "oqlos.plugins": [
        "pss7000 = oqlos_plugin_pss7000:Plugin",
        "msa_g1 = oqlos_plugin_msa_g1:Plugin",
    ]
}

# Introspection
GET /api/v1/plugins
→ [
    {"name": "pss7000", "version": "1.2.0", "peripherals": [...]},
    {"name": "msa_g1", "version": "0.9.1", "peripherals": [...]},
  ]
```

**Co już jest:** `plugin_registry.py`, ale trzeba wystawić jako stabilne API.

**Ile pracy:** 1 dzień.

---

## 2. WAŻNE (bez tego doql ma ograniczoną funkcjonalność)

### 2.1 Job Queue / Async Execution

**Problem:** Niektóre scenariusze trwają 30 min — HTTP request nie może wisieć tak długo. Mobile/PWA potrzebuje odpytywać status.

**Co dodać:** kolejka zadań (Celery / RQ / Arq).

```python
POST /scenarios/42/execute → { "execution_id": "exec-abc", "status": "queued" }
GET  /executions/exec-abc   → { "status": "running", "progress": 0.45, "current_goal": "..." }
GET  /executions/exec-abc/stream  (SSE)  →  live events
```

**Ile pracy:** 2-3 dni.

---

### 2.2 Workflow Engine

**Problem:** `doql` deklaruje workflow wieloetapowe (notify → scan → run → report). Potrzebny silnik state-machine.

**Co dodać:** lekki engine lub integracja z Temporal / Prefect.

```python
class Workflow:
    states: list[str]
    transitions: dict[str, str]
    
    def advance(self, event: Event) -> State:
        ...
```

**Ile pracy:** 5-7 dni (lub 1 dzień na integrację z istniejącym).

---

### 2.3 File / Object Storage Abstraction

**Problem:** `doql` entity może mieć typ `image`, `file`, `pdf`. Oqlos musi te pliki gdzieś trzymać (lokalnie, S3, MinIO).

**Co dodać:** `storage` backend z interfejsem:

```python
class Storage(Protocol):
    def put(key: str, data: bytes) -> str: ...  # returns URL
    def get(key: str) -> bytes: ...
    def delete(key: str): ...
    def presigned_url(key: str, ttl: int) -> str: ...

# Implementacje: LocalStorage, S3Storage, MinIOStorage
```

**Ile pracy:** 2 dni.

---

### 2.4 OpenAPI Auto-generation z entity definitions

**Problem:** `doql build` generuje endpointy API na podstawie entity. Potrzebuje OpenAPI spec, żeby wygenerować TypeScript SDK dla frontu.

**Co już jest:** FastAPI automatycznie generuje OpenAPI. Wystarczy udostępnić `/openapi.json` i zadbać o porządne schematy Pydantic.

**Co dodać:** walidator, który przy `doql build` sprawdza, czy OpenAPI pokrywa wszystkie entity z `.doql`.

**Ile pracy:** 1 dzień.

---

### 2.5 Notification Service

**Problem:** `doql` deklaruje `INTEGRATION notifications` — oqlos powinien mieć wbudowany dispatcher.

**Co dodać:**

```python
# oqlos/oqlos/notifications/
class NotificationService:
    def send(channel: str, to: str, template: str, context: dict): ...

# Wbudowane kanały: email (SMTP), slack (webhook), sms (Twilio), push (FCM)
```

**Ile pracy:** 3 dni.

---

## 3. POŻĄDANE (podnoszą jakość doql)

### 3.1 Audit Log

**Problem:** Domeny GxP / ISO-17025 wymagają pełnej historii zmian. `doql` może to deklarować przez `AUDIT: full`.

**Co dodać:** tabela `audit_log` + middleware logujące CRUD + append-only storage.

```python
class AuditEntry(Base):
    id: uuid
    organization_id: str
    user_id: str
    action: str            # create, update, delete, execute
    entity_type: str
    entity_id: str
    before: json
    after: json
    timestamp: datetime
    signature: str         # HMAC dla tamper-evidence
```

**Ile pracy:** 3 dni.

---

### 3.2 Mobile-first API features

- **Batching:** `POST /batch` z listą operacji (offline sync).
- **Delta sync:** `GET /devices?since=<timestamp>` — zwraca tylko zmiany.
- **Conflict resolution:** versioning + last-write-wins / manual merge.
- **Compressed responses:** gzip + brotli.
- **Partial fetch:** `?fields=id,serial,status`.

**Ile pracy:** 1 tydzień.

---

### 3.3 Report Generator

**Co dodać:** WeasyPrint / wkhtmltopdf + template engine dla PDF raportów.

```python
# oqlos/oqlos/reports/
@router.post("/executions/{id}/report")
def generate_report(id: str, template: str) -> bytes:
    ...
```

**Ile pracy:** 3-4 dni (z podpisami cyfrowymi).

---

### 3.4 Device Discovery / Provisioning API

**Problem:** `doql INTERFACE mobile` chce pokazywać „skanuj QR → urządzenie dodane do floty". Potrzebny provisioning flow.

**Co dodać:**

```python
POST /devices/provision
  { "qr_token": "...", "name": "...", "location": "..." }
→ { "device_id": "...", "agent_config": {...} }
```

**Ile pracy:** 3 dni.

---

### 3.5 Rate limiting + API keys

Standardowa higiena SaaS. `doql` deklaruje `rate_limit: 100/min` — oqlos musi to egzekwować.

**Ile pracy:** 1 dzień (z użyciem `slowapi` dla FastAPI).

---

## 4. SYMPATYCZNE (długoterminowo)

### 4.1 GraphQL Layer

Alternatywa dla REST dla frontendu. Szybszy development UI. Strawberry GraphQL + introspection z entity definitions.

### 4.2 Telemetry / OpenTelemetry

Traces + metrics + logs. Integracja z Grafana / Jaeger. Niezbędne dla Enterprise.

### 4.3 Feature Flags

`doql` może deklarować funkcje warunkowe na plan. Integracja z Unleash / OpenFeature.

### 4.4 i18n w core

Obecnie tłumaczenia tylko w `www`. oqlos powinien zwracać komunikaty błędów w locale użytkownika.

### 4.5 Scheduled Jobs

`WORKFLOW trigger: schedule: daily 08:00` — potrzebny wbudowany scheduler (APScheduler).

---

## 4B. Nowe wymagania od doql v0.2 (DOCUMENT / DATA / kiosk)

Wersja 0.2 doql rozszerzyła zakres o dokumenty, źródła danych i kiosk. Dodaje trzy nowe wymagania wobec oqlos.

### 4B.1 Webhook push (POST z HMAC) dla zdarzeń scenariusza

**Problem:** `WORKFLOW` w doql reaguje na `oqlos.scenario.completed`. W v0.1 requirements planowaliśmy SSE (pull), ale kiosk appliance i serverless deploy nie utrzymują aktywnej sesji SSE. Potrzebny jest push przez webhook.

**Co dodać:**

```python
# oqlos/oqlos/events/webhook_dispatcher.py
class WebhookDispatcher:
    def register(self, event: str, url: str, secret: str): ...
    def dispatch(self, event: str, payload: dict):
        sig = hmac.new(secret, body, sha256).hexdigest()
        httpx.post(url, json=payload, headers={"X-OQLOS-Signature": sig})
```

Konfiguracja webhooków w `oqlos.yaml` lub przez endpoint `POST /api/v1/webhooks`.

**Ile pracy:** 1 dzień (na bazie istniejącego event bus).

---

### 4B.2 Execution data dump endpoint

**Problem:** DOCUMENT kalibracyjny potrzebuje pełnych danych pomiarowych (wszystkie measurements, timings, uncertainty values) z wykonania scenariusza. W v0.1 executor trzymał je w pamięci i wysyłał tylko przez SSE.

**Co dodać:**

```
GET /api/v1/executions/{id}/data
→ {
    "execution_id": "...",
    "scenario_id": ...,
    "started_at": "...",
    "completed_at": "...",
    "measurements": [
      { "timestamp": "...", "sensor": "AI01", "value": -12.4, "unit": "mbar" },
      ...
    ],
    "goals": [...],
    "errors": [...],
    "metadata": {...}
  }
```

**Ile pracy:** 1 dzień (zapis do event store już jest, trzeba tylko dodać endpoint z serializacją).

---

### 4B.3 Delta API dla offline sync

**Problem:** Kiosk cache'uje listę urządzeń/operatorów. Przy 10 000 urządzeń pełna synchronizacja co 5 minut jest nieakceptowalna. Potrzebny incremental sync.

**Co dodać:**

```
GET /api/v1/devices?since=2026-04-16T10:00:00Z
→ {
    "changes": [
      { "op": "upsert", "device": {...} },
      { "op": "delete", "id": "..." }
    ],
    "checkpoint": "2026-04-16T10:05:00Z"   # użyj jako ?since w następnym call
  }
```

Dotyczy `/devices`, `/operators`, `/scenarios` — wszystkie listingi z cache po stronie klienta.

**Wymaga:** updated_at i deleted_at w modelach (soft delete).

**Ile pracy:** 2-3 dni (migracja modeli + middleware + endpointy).

---

## 5. Roadmapa wdrożenia (proponowana)

```
SPRINT 1 (tydzień):   1.1 Schema introspection
                       1.2 Event bus (ustandaryzować SSE)
                       1.5 Plugin registry discovery

SPRINT 2 (tydzień):   1.3 Multi-tenancy (migracja DB)
                       1.4 Auth/RBAC

SPRINT 3 (tydzień):   2.1 Job queue (RQ lub Arq)
                       2.3 File storage abstraction
                       2.5 Notification service

SPRINT 4 (tydzień):   2.2 Workflow engine (minimum viable)
                       2.4 OpenAPI walidator
                       3.1 Audit log

────────────────────  doql v0.1 READY

SPRINT 5-6:            3.2 Mobile-first features
                       3.3 Report generator
                       3.4 Device provisioning

────────────────────  doql v0.5 (production pilot)

SPRINT 7+:             4.x (enterprise features)
```

**Całość: ~8 tygodni dla 1 inżyniera full-time**, aby dostać doql w stanie „można pokazać klientowi".

---

## 6. Breaking changes w oqlos (uwaga)

Niektóre zmiany wymuszą breaking changes:

| Zmiana | Impact |
|--------|--------|
| `organization_id` w modelach | SQL migration, wszystkie query musi dostać filtr |
| Auth middleware | Każdy endpoint wymaga tokenu (z wyjątkiem `/health`, `/openapi`) |
| Event schema stabilization | Obecne SSE events mają nieustrukturyzowany format — trzeba zmienić |

**Rekomendacja:** zrobić to jako `oqlos 2.0` z migration guide. Utrzymywać 1.x przez 6 miesięcy jako LTS.

---

## 7. Co MOŻNA zrobić bez zmian w oqlos (pierwsza wersja doql)

Ponieważ pełna migracja oqlos zajmie tygodnie, pierwsza wersja `doql` może działać z obecnym oqlos jeśli zrezygnuje z:

- ❌ Multi-tenancy (wszystkie aplikacje to jeden tenant)
- ❌ Zaawansowany RBAC (tylko JWT z rolą w claims)
- ❌ Workflow engine (tylko sekwencyjne scripty)
- ⚠️ Event webhooks (polling zamiast push)

Ale może mieć:

- ✅ Entity CRUD (bo generuje nowe FastAPI, nie używa oqlos do modeli)
- ✅ Wywoływanie scenariuszy przez istniejące REST API oqlos
- ✅ Generowanie web/mobile/desktop (niezależne od oqlos)
- ✅ Deploy z Traefik / Quadlet
- ✅ Integracja przez webhook z istniejącym SSE streamem

To pozwala na **MVP doql w 2-3 tygodnie** bez czekania na zmiany w oqlos.
