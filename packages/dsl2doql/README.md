# dsl2doql

**DSL sterowania DOQL** — query, patch, validate, generate, adopt przez komendy tekstowe.

Powiązane: [indeks paczek](../README.md) · [README główne doql](../../README.md) · [uri2doql](../uri2doql/README.md)

## Do czego służy

- wykonuje komendy sterujące manifestem `.doql.less`
- integruje `uri2doql` (QUERY, MATERIALIZE, PATCH) i `nlp2doql` (GENERATE, VALIDATE)
- konwersja scenariuszy OQL → workflow: `CONVERT` (logika w `doql/importers/oql_converter.py`)

## Komendy DSL

| Komenda | Opis |
|---------|------|
| `QUERY doql://block/app?file=...` | odczyt bloku |
| `MATERIALIZE doql://... TO out.less` | zapis fragmentu |
| `PATCH doql://block/entity/X?file=... WITH frag.less` | podmiana bloku |
| `APPEND app.doql.less WITH extra.less` | dopisanie bloków |
| `VALIDATE app.doql.less` | walidacja |
| `GENERATE "CRM" OUT app.doql.less` | generacja NL |
| `RESOLVE "pokaż workflow install"` | nlp2uri |
| `CONVERT test.oql OUT workflow.less` | OQL → workflow |
| `ADOPT . OUT app.doql.less` | skan projektu |

## CLI

```bash
dsl2doql script.dsl --file app.doql.less
dsl2doql -c 'QUERY doql://block/app?file=app.doql.less'
```

## Testy

```bash
pytest packages/dsl2doql/tests -q
```
