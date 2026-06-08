# uri2doql

Sterowanie manifestami DOQL przez schemat URI **`doql://`** — odczyt, zapis, edycja, patch.

Powiązane: [indeks paczek](../README.md) · [README główne doql](../../README.md) · [nlp2uri](src/uri2doql/nlp2uri.py)

## Do czego służy

- **query** — wyciąga blok jako JSON/YAML/LESS
- **materialize** — zapisuje fragment do pliku
- **patch / update** — podmienia blok w pliku źródłowym
- **append** — dopisuje bloki do manifestu
- **apply** — unified: materialize | patch | append
- **resolve / nlp2uri** — NL → sugerowany URI

## CLI

```bash
uri2doql query --uri 'doql://block/app?file=app.doql.less'
uri2doql patch --uri 'doql://block/entity/Contact?file=app.doql.less' --with contact.less
uri2doql append --file app.doql.less --with workflow.less
uri2doql apply --uri 'doql://block/workflow/install?file=app.doql.less' --mode materialize --dest /tmp/w.less
uri2doql resolve "pokaż workflow install" --file app.doql.less
```

## Python API

```python
from uri2doql import query_uri, patch_uri, nlp2uri, apply_uri
```

## Testy

```bash
pytest packages/uri2doql/tests -q
```
