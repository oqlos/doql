# uri2doql

Address and materialize DOQL specifications via `doql://` URIs.

## URI scheme

| URI | Opis |
|-----|------|
| `doql://file/{path}` | Pełny plik DOQL |
| `doql://block/app?file=app.doql.less` | Metadane `app{}` |
| `doql://block/entity/Contact?file=...` | Blok encji |
| `doql://block/workflow/install?file=...` | Workflow |
| `doql://block/interface/cli/page/doql?file=...` | Zagnieżdżona strona CLI |
| `doql://generate?prompt=CRM+with+contacts` | Generacja przez nlp2doql |

## CLI

```bash
pip install -e ../.. -e .
uri2doql query --uri 'doql://block/app?file=app.doql.less'
uri2doql query --uri 'doql://block/workflow/test?file=app.doql.less' --format less
uri2doql materialize --uri 'doql://block/workflow/test?file=app.doql.less' --dest /tmp/test.less
uri2doql resolve "pokaż workflow install z app.doql" --file app.doql.less
```
