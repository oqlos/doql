# doql TODO

## Vision Notes

- doql = deklaratywny język budowania usług, aplikacji, dokumentów, szablonów
- Nie tylko systemy — też dokumenty HTML/MD, pliki JSON, bazy SQLite, dostęp do API
- Łatwe reużycie danych z `.json`, `.env`
- Aplikacje w formacie Docker/Quadlet/Podman/Traefik z desktop/kiosk (mobilna jak w pactown)

## P0 — Stable release blockers

- [x] `doql adopt` — end-to-end test with real project (oqlos itself) ✅ sesja 15
- [x] `doql doctor` — add `--fix` flag for auto-remediation of fixable issues ✅ v1.0.3
- [x] pytest coverage: add `pytest-cov` + `.coveragerc`, target ≥ 45% ✅ v1.0.3

## P1 — Quality / CC hotspots

- [x] `doql/adopt/scanner.py` — split by interface detector type (FastAPI, Flask, CLI, Web) ✅ already done (scanner/ package)
- [x] `doql/parsers/css_parser.py` — remaining CC hotspots ✅ already clean (154 lines, routing map)
- [x] `doql/exporters/` — validate backward-compat shims are tested ✅ 7 tests added

## P2 — Features / Backlog

### Language features
- [ ] Tree-sitter parser (full `.doql` grammar, error recovery)
- [ ] `maskservice/workshop` — migrate device management from `maskservice/c2004`:
  - device inventory + location, scan device/barcode QR
  - associated files (PDFs, drivers, reports, certs, invoices)
  - tag/feature filtering + bulk actions
  - tag ID → SQLite ID remapping logic
- [ ] VS Code extension: `.doql.css` / `.doql.less` / `.doql.sass` syntax highlighting

### CLI improvements
- [ ] `doql build --watch` — file watcher for dev loop
- [ ] `doql deploy` — `@local`/`@push`/`@remote`: add rollback support
- [ ] `doql publish --target github` — automated GitHub Release notes from CHANGELOG

## Tests

- [ ] Run `testql run testql-scenarios/generated-api-smoke.testql.toon.yaml`
- [ ] Run `testql run testql-scenarios/generated-api-integration.testql.toon.yaml`
- [ ] Run `testql run testql-scenarios/generated-from-pytests.testql.toon.yaml`
- [ ] Pilot w realnej firmie — zidentyfikować projekt

## ✅ Done

- [x] `doql adopt` — reverse-engineer project into `app.doql.css` (sesja 13)
- [x] `Environment` model — `environment[name="prod"]` with runtime/ssh_host (sesja 13)
- [x] Generated manifests for 5 sibling projects (sesja 13)
- [x] `doql doctor` — 9-check health diagnostic with optional `--env` remote SSH (sesja 14)
- [x] `doql build --no-overwrite` — merge-friendly build (sesja 14)
- [x] Deploy directives `@local`/`@push`/`@remote` (sesja 14)
- [x] `doql publish` — PyPI, npm, Docker, GitHub targets (sesja 14)
- [x] 130 tests passing (sesja 14)
- [x] `css_exporter`, `markdown_exporter` split into packages (sesja 11)
- [x] `css_tokenizer.py` extracted from `css_parser.py` (sesja 11)
- [x] testql-scenarios generated (3 files)
- [x] README AI cost tracking removed; version badge updated to 0.1.3



## Szybka diagnoza obecnego stanuAha — ten `map_toon.yaml` to **doql**, nie redeploy. To bardzo zmienia sytuację. `critical:0`, `CC̄=3.5`, `cycles:0` — **doql jest czyste**. Natomiast `calls_toon.yaml` to stary skan redeploy sprzed rozbicia.

Porządkuję co mam:

| Źródło | Co pokazuje |
|---|---|
| `map_toon.yaml` | **doql** v?, 124 moduły, CC̄=3.5, **critical:0** — zdrowy projekt |
| `calls_toon.yaml` | stary **redeploy** call graph |
| README (dokument 24) | **redeploy v0.2.42** — produkcyjnie gotowy, dużo nowych feature'ów |
| `docker-infrastructure-sim.less` | przykład co doql generuje — pełny topology as data |

Widzę dwa osobne projekty, dwie osobne trajektorie refaktoru. Zróbmy to po kolei.

---

## doql — co tu refaktorować

**Metryki są zaskakująco dobre**. `critical:0` i malejący trend CC̄ (3.6→3.5) — to znaczy że masz tu dyscyplinę. Ale hotspoty pokazują ciekawy wzorzec: top 5 fan-out to wszystko funkcje **podkreślone** (prywatne pomocnicze), nie publiczne API. To klasyczny sygnał "dobre API, zagmatwane wnętrze".

### Top kandydaci (wszyscy z fan 15-17)

**`_diagnostics_for` fan=17** — prawdopodobnie `cmd doctor` który sprawdza 17 rzeczy w jednym lejku. Wzorzec: lista `Diagnostic` jako dane:

```python
# doql/doctor/checks.py
@dataclass(frozen=True)
class DiagnosticCheck:
    id: str
    description: str
    applies_to: Callable[[Context], bool]  # kiedy uruchamiać
    probe: Callable[[Context], CheckResult]
    fix_hint: str | None = None

CHECKS: list[DiagnosticCheck] = [
    DiagnosticCheck("python_version", "Python 3.10+ available", ...),
    DiagnosticCheck("redeploy_installed", "redeploy CLI on PATH", ...),
    DiagnosticCheck("less_parser", "Can parse .doql.less", ...),
    # 14 kolejnych — wcześniej w jednej funkcji
]

def _diagnostics_for(ctx: Context) -> list[CheckResult]:
    return [c.probe(ctx) for c in CHECKS if c.applies_to(ctx)]
```

Dokładnie ten sam pattern który proponowałem dla `detect/templates.py` w redeploy. U ciebie to już najlepsze ROI bo *doctor* to komenda, do której się dodaje nowe rzeczy — czyli ten plik będzie tylko rósł.

**`_convert_indent_to_braces` fan=16** — to w parserze LESS. Prawdopodobnie shared state (level counter, current block, pending braces). Tu refaktor inny: wyciąg do małej klasy `BraceConverter` z explicit state:

```python
class BraceConverter:
    def __init__(self, text: str):
        self.lines = text.splitlines()
        self.out: list[str] = []
        self.depth = 0
    
    def convert(self) -> str:
        for line in self.lines:
            self._handle_line(line)
        self._close_remaining()
        return "\n".join(self.out)
    
    def _handle_line(self, line: str) -> None: ...
    def _close_remaining(self) -> None: ...
```

CC spada bo state jest w fieldach, nie w args.

**`_extract_page_from_format2` fan=16** — domyślam się że masz kilka formatów (`format1`, `format2`...) i każdy ma własny extractor. To jest **Strategy pattern szukający domu**:

```python
# doql/formats/
├── __init__.py          # FORMATS registry
├── base.py              # FormatExtractor protocol
├── format1.py
├── format2.py
└── format3.py

class FormatExtractor(Protocol):
    format_id: str
    def detect(self, content: str) -> bool: ...
    def extract_page(self, content: str) -> Page: ...
    def extract_blocks(self, content: str) -> list[Block]: ...

def extract_page(content: str) -> Page:
    for fmt in FORMATS:
        if fmt.detect(content):
            return fmt.extract_page(content)
    raise UnknownFormatError(content[:100])
```

**`cmd_doctor` fan=16** — to sam CLI dispatcher doctora. Po refaktorze `_diagnostics_for` (krok 1) ten automatycznie się uprości, bo będzie tylko loop po wynikach + render.

### Nowy moduł który się prosi — `doql/hardware/`

Widzę że generujesz `docker-infrastructure-sim.less` z LESS-em opisującym `hardware[name="app-server-1"]`. Patrząc na to:

```less
hardware[name="app-server-1"] {
  type: application-server;
  ports: [8001];
  networks: [backend, database];
}
```

...i na twój nowy redeploy feature (scan hardware → YAML → edit → apply), **są dwa kierunki inżynieryjne które trzeba zdecydować**:

1. **LESS jako source of truth**: doql generuje `.less`, redeploy deployuje. Obecny stan.
2. **LESS ↔ YAML jako izomorficzna para**: doql generuje oba formaty, użytkownik wybiera, redeploy rozumie oba.

Jeśli idziesz w (2) — dodaj w doql moduł `doql/formats/adapters.py`:

```python
class LessYamlAdapter:
    def less_to_yaml(self, less_text: str) -> dict: ...
    def yaml_to_less(self, data: dict) -> str: ...
```

Plus round-trip test: `yaml_to_less(less_to_yaml(x)) == x` modulo whitespace. To odblokowuje scenariusz: `redeploy hardware --query` zwraca JSON, użytkownik edytuje jako YAML, doql konwertuje z powrotem do LESS, commit, rebuild.

### doql — propozycja na tydzień

| Dzień | Zadanie |
|---|---|
| Pn | `_diagnostics_for` → `doql/doctor/checks.py` jako lista danych |
| Wt | `_extract_page_from_format2` + rodzeństwo → `doql/formats/` (registry + strategy) |
| Śr | `_convert_indent_to_braces` → `BraceConverter` class |
| Cz | Decyzja: LESS-only vs LESS+YAML. Jeśli LESS+YAML → `formats/adapters.py` + round-trip testy |
| Pt | Scan + porównanie trendu. Cel: `CC̄ 3.5→3.2`, żaden fan-out > 12 |

---