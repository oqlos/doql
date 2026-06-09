# rest2doql

REST API (FastAPI) — cienkie wrappery `dsl2doql.dispatch()`.

```bash
rest2doql serve --port 8210
curl http://127.0.0.1:8210/health
curl -X POST http://127.0.0.1:8210/v1/dsl -H 'Content-Type: text/plain' -d 'VALIDATE app.doql.less'
```

Powrót: [packages/README.md](../README.md)
