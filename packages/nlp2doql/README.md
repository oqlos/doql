# nlp2doql

Sterowanie manifestami DOQL przez **język naturalny** — generacja, walidacja, edycja (via nlp2uri → uri2doql).

Powiązane: [indeks paczek](../README.md) · [README główne doql](../../README.md) · [uri2doql](../uri2doql/README.md)

## Do czego służy

- **generate** — NL → pełny `.doql.less` (reguły lub LLM)
- **validate** — walidacja pliku DOQL
- **apply** — NL → intent (query/patch/materialize/generate) + wykonanie
- **edit** — NL + plik fragmentu → patch bloku

## CLI

```bash
nlp2doql generate "CRM z kontaktami" --out app.doql.less --validate
nlp2doql validate app.doql.less
nlp2doql apply "pokaż app metadata" --file app.doql.less
nlp2doql edit "update entity Contact" --file app.doql.less --with contact.patch.less
nlp2doql apply "validate app.doql.less"
```

## Testy

```bash
pytest packages/nlp2doql/tests -q
```
