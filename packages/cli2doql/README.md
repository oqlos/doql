# cli2doql

**Interaktywny shell CLI** do sterowania DOQL — wykonuje komendy DSL z `dsl2doql`.

Powiązane: [indeks paczek](../README.md) · [README główne doql](../../README.md) · [dsl2doql](../dsl2doql/README.md)

## Do czego służy

- REPL: `cli2doql shell`
- skrypt DSL: `cli2doql run script.dsl`
- pojedyncza komenda: `cli2doql exec 'QUERY doql://block/app'`
- skanowanie CLI w projekcie → `doql adopt` (logika w `doql/adopt/scanner/interfaces/cli.py`)

## Przykłady

```bash
pip install -e ../.. -e packages/dsl2doql -e .
cli2doql shell --file app.doql.less
# doql> QUERY doql://block/app?file=app.doql.less
# doql> VALIDATE app.doql.less
```

## Testy

```bash
pytest packages/cli2doql/tests -q
```
