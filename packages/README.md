# doql tooling packages (`*2doql`)

Warstwy **sterowania DOQL** — MCP, DSL shell, URI i NL.

Powrót: [README główne doql](../README.md)

## Pakiety

| Pakiet | Rola | README |
|--------|------|--------|
| **mcp2doql** | Serwer MCP (stdio) — narzędzia DOQL | [mcp2doql/README.md](mcp2doql/README.md) |
| **cli2doql** | Shell CLI (REPL) na bazie DSL | [cli2doql/README.md](cli2doql/README.md) |
| **dsl2doql** | DSL sterowania DOQL (QUERY, PATCH, ADOPT, …) | [dsl2doql/README.md](dsl2doql/README.md) |
| **uri2doql** | `doql://` URI — query, patch, apply, nlp2uri | [uri2doql/README.md](uri2doql/README.md) |
| **nlp2doql** | NL — generate, validate, apply, edit | [nlp2doql/README.md](nlp2doql/README.md) |

## Logika w `doql/` (core)

| Funkcja | Lokalizacja |
|---------|-------------|
| Skan MCP (adopt) | `doql/adopt/scanner/interfaces/mcp.py` |
| Skan CLI (adopt) | `doql/adopt/scanner/interfaces/cli.py` |
| OQL/CQL → workflow | `doql/importers/oql_converter.py` |

## Przepływ

```text
NL ──► nlp2doql apply ──► nlp2uri ──► uri2doql patch/query
DSL ──► dsl2doql ──► uri2doql / nlp2doql / doql adopt
CLI ──► cli2doql shell ──► dsl2doql
MCP ──► mcp2doql serve ──► dsl2doql + uri2doql + nlp2doql
adopt ──► doql/adopt (skanery MCP/CLI in-core)
```

## Instalacja (dev)

```bash
uv sync --extra deploy
```

## Testy

```bash
pytest tests/ packages/ -q
```
