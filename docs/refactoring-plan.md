# doql — Szczegółowy Plan Refaktoryzacji

**Status:** W trakcie realizacji  
**Data:** 2026-04-20  
**Docelowa wersja:** 1.0.0

---

## TL;DR

Refaktoryzacja doql w pięciu fazach:

| Faza | Cel | Status | Czas |
|------|-----|--------|------|
| 1 | Domknięcie stubów przez delegację do redeploy | ✅ Zrobione | 1 tydzień |
| 2 | Generowanie `migration.yaml` jako artefaktu build | ✅ Zrobione | 1 tydzień |
| 3 | Unifikacja nazewnictwa strategii z redeploy | ✅ Zrobione | 2 dni |
| 4 | Eksperyment z DSL w składni LESS/SASS | ✅ **MVP Gotowe** | 2 tygodnie |
| 5 | Stabilizacja API i `doql[deploy]` optional dep | ✅ Zrobione | 1 tydzień |

**Razem:** 6–8 tygodni. Faza 4 eksperymentalna — może się rozszerzyć lub zostać odłożona.

---

## 1. Aktualny Stan

### Co doql robi dobrze

- Deklaracja aplikacji w jednym pliku (`app.doql`) — model danych, UI, role, deployment
- Generowanie kompletnych artefaktów — FastAPI backend, React frontend, docker-compose, Quadlet units, Traefik config
- CLI pokrywający cykl życia — `init`, `build`, `run`, `validate`, `status`, `deploy`, `quadlet`
- Przykłady pokrywające scenariusze biznesowe — kiosk-station, iot-fleet, asset-management, calibration-lab, crm-contacts

### Gdzie boli

| Problem | Objaw | Wpływ |
|---------|-------|-------|
| Stub `cmd_quadlet.install` | `print("⚠️ not yet implemented")` | Użytkownik musi ręcznie kopiować `.container` files |
| Stub `cmd_deploy` | `subprocess.call(["docker", "compose", "up"])` bez health checks | Deploy nie jest audytowalny |
| Brak `migration.yaml` | `doql build` nie produkuje spec dla deploy-runnera | Użytkownik duplikuje dane |
| Rozjazd nazewnictwa | `docker-compose` vs `docker_full`, `quadlet` vs `podman_quadlet` | Każda integracja wymaga mapowania |
| Składnia `.doql` | Własny język bez IDE support | Bariera wejścia |

---

## 2. Zidentyfikowane Kierunki Zmian

### Kierunek A: „doql zostaje build-time, redeploy przejmuje deploy-time"

Opcja zachowawcza. `doql` emituje `migration.yaml`, `doql deploy` jest cienkim wrapperem na `redeploy run`.

**Status:** ✅ Zaimplementowane w:
- `doql/cli/commands/deploy.py` — delegacja do redeploy API/CLI
- `doql/cli/commands/quadlet.py` — instalacja via redeploy lub systemctl
- `doql/generators/infra_gen.py` — `_gen_migration_spec()`

### Kierunek B: „DSL w składni LESS/SASS jako alternatywa dla .doql"

Eksperyment widoczny w `app.doql.less` i `app.doql.sass`.

```less
entity[name="Notebook"] {
  id: uuid! auto;
  name: string!;
  color: string default=sky;
}
```

**Plusy:**
- Składnia znana frontendowcom
- Istniejące parsery (tinycss2)
- IDE mają gotowy syntax highlight
- Mixins = naturalny model bibliotek

**Status:** 🔄 Parser działa, trwają testy regresji

### Kierunek C: „Hybryda" — rekomendacja

Zrobić A jako podstawę, B jako pluggable parser. Core używa IR (Python), parsery dla `.doql`, `.less`, `.sass` emitują ten sam IR.

---

## 3. Fazy Refaktoryzacji (Szczegóły)

### Faza 1 — Domknięcie Stubów przez Delegację do redeploy ✅

**Implementacja:**
```python
# doql/cli/commands/deploy.py
def cmd_deploy(args):
    migration_yaml = ctx.build_dir / "infra" / "migration.yaml"
    
    # 1. redeploy API
    rc = _deploy_via_redeploy_api(migration_yaml, dry_run, plan_only)
    if rc >= 0: return rc
    
    # 2. redeploy CLI fallback
    rc = _deploy_via_redeploy_cli(migration_yaml, dry_run, plan_only)
    if rc >= 0: return rc
    
    # 3. docker-compose fallback
    return deploy_gen.run(ctx, target_env)
```

**Akceptacja:**
- `doql deploy --dry-run` z redeploy pokazuje plan
- `doql quadlet --install` kopiuje `.container` files, robi `daemon-reload`

### Faza 2 — Generowanie migration.yaml ✅

**Implementacja:**
```python
# doql/generators/infra_gen.py
def _gen_migration_spec(spec, env_vars, out):
    migration = {
        "name": slug,
        "source": {"strategy": "docker_full", ...},
        "target": {"strategy": target_strategy, ...},
    }
    (out / "migration.yaml").write_text(yaml.dump(migration))
```

**Mapowanie strategii:**
| doql DEPLOY.target | redeploy strategy |
|-------------------|-------------------|
| `docker-compose` | `docker_full` |
| `quadlet` | `podman_quadlet` |
| `kubernetes` | `k3s` |
| `kiosk-appliance` | `podman_quadlet` |
| `systemd` | `systemd` |

### Faza 3 — Unifikacja Nazewnictwa ✅

**Decyzja:** Opcja 1 — doql przyjmuje nazwy redeploy jako kanoniczne.

```python
def _map_deploy_strategy(doql_target: str) -> str:
    return {
        "docker-compose": "docker_full",
        "quadlet":        "podman_quadlet",
        "kubernetes":     "k3s",
    }.get(doql_target, "docker_full")
```

### Faza 4 — Eksperyment LESS/SASS Parser ✅ MVP

**Architektura:**
```
app.doql ─┐
app.less ─┼─► parser[format] ─► DoqlIR (pydantic) ─► generators ─► build/
app.sass ─┘
```

**Lokalizacja kodu:**
- `doql/parsers/css_parser.py` — główny parser
- `doql/parsers/css_transformers.py` — LESS/SASS → CSS
- `doql/parsers/css_mappers.py` — CSS → DoqlSpec
- `tests/test_parser_benchmark.py` — wydajność

**Kryteria MVP spełnione:**
- [x] Parser przechodzi przez wszystkie przykłady (9 projektów)
- [x] Testy regresji: `.doql` vs `.doql.less` dla `calibration-lab`
- [x] Ostrzeżenia dla nieznanych selektorów (z sugestiami)
- [x] Benchmarki: cold start <100ms, real examples <200ms
- [x] Benchmarki: duże pliki (100 entities) <500ms

**Następne kroki (opcjonalnie):**
- [ ] Lepsze komunikaty błędów składni (linia/kolumna)
- [ ] Dalsza optymalizacja (cel: <1.5x classic parser)

**Testy regresji:**
```python
def test_doql_vs_less_regression():
    classic = parse_file("app.doql")
    less = parse_file("app.doql.less")
    assert classic.app_name == less.app_name
    assert classic.entity_names == less.entity_names
```

### Faza 5 — Stabilizacja API ✅

**Zmiany:**
```python
# doql/__init__.py
__version__ = "1.0.0"

__all__ = [
    "parse_file", "parse_text", "parse_env", "validate",
    "DoqlSpec", "Entity", "Interface", "Deploy", ...
]
```

**pyproject.toml:**
```toml
version = "1.0.0"
classifiers = ["Development Status :: 4 - Beta"]
deploy = ["redeploy>=0.2.0,<0.3.0"]
```

---

## 4. Ryzyka i Decyzje

| Ryzyko | Prawdopodobieństwo | Mitygacja |
|--------|-------------------|-----------|
| Faza 4 zajmuje >3 tygodnie | Średnie | Time-box — po 3 tyg. zatrzymaj |
| Breaking change psuje userów | Niskie–średnie | Aliasy + warning przez 2 minor |
| redeploy zmienia API | Średnie | Pin `>=0.2.0,<0.3.0` |
| migration.yaml wymaga więcej pól | Wysokie | Rozszerzyć DEPLOY block |

---

## 5. Kryteria Sukcesu (v1.0.0)

- [x] Użytkownik pisze `app.doql` (lub `.less`/`.sass`)
- [x] `doql build` generuje `build/` + `migration.yaml`
- [x] `doql deploy` wykonuje pipeline przez redeploy
- [x] Nazwy strategii spójne z redeploy
- [x] Dokumentacja „od app.doql do produkcji"
- [x] Przykłady działają bez stubów

---

## 6. Co NIE Jest w Tym Planie

- Przepisanie generatorów kodu (FastAPI, React) — obecne działają
- Wsparcie dla Go/Rust backendów — po 1.0
- LSP dla `.doql` — jeśli faza 4 się uda, SASS/LESS mają IDE support
- Hot reload w `doql run` — nice-to-have
- Marketplace stdlib — po stabilnej składni

---

## 7. Następne Kroki

1. ✅ Faza 1–3 i 5 zakończone
2. 🔄 Faza 4 — checkpoint po 2 tygodniach
3. ⏳ Faza 4 — deadline po 3 tygodniach (go/no-go)

---

*Powiązane dokumenty:*
- `CHANGELOG.md` — historia zmian
- `TODO/05-doql-migration-guide.md` — przewodnik migracji formatów
