# nlp2doql

Natural language → DOQL (`.doql.less`) generator.

## CLI

```bash
pip install -e ../.. -e .
nlp2doql generate "CRM with contacts" --out app.doql.less --validate
nlp2doql validate app.doql.less
nlp2doql doctor
```

## Python API

```python
from nlp2doql import generate_spec

result = generate_spec("todo PWA", out_path="app.doql.less", validate=True)
print(result.doql)
```
