# doql Playground

100% client-side playground that runs the real `doql` parser + validator
in your browser via [Pyodide](https://pyodide.org/). No backend, no
telemetry — your `.doql` source never leaves the page.

## Files

- `index.html` — two-pane UI (editor + diagnostics/AST/generated files)
- `style.css` — minimal dark theme
- `app.js` — boots Pyodide, installs the `doql` wheel, wires live build
- `doql-*.whl` — the actual doql distribution that runs in the browser

## Running locally

```sh
# From the doql repo root:
cp dist/doql-*.whl playground/             # refresh the wheel
python3 -m http.server -d playground 8000  # any static server works

# → open http://127.0.0.1:8000/
```

## Refreshing the wheel

When you change `doql/` source, rebuild and copy:

```sh
python -m build --outdir dist
cp dist/doql-*.whl playground/
```

Then hard-reload the playground — Pyodide will pick up the new wheel.

## Deploying to playground.doql.dev

Any static host works. Upload the entire `playground/` directory (plus
the freshly built `.whl`). Examples:

- **GitHub Pages** — push `playground/` to the `gh-pages` branch.
- **Netlify / Vercel** — point the site at `playground/` as publish dir.
- **S3 + CloudFront** — `aws s3 sync playground/ s3://bucket/ --acl public-read`.

No server-side code is required.

## Architecture

```
browser
  │
  ▼
Pyodide (WASM Python 3.12)
  │
  ▼
micropip install ./doql-0.1.0a1-py3-none-any.whl
  │
  ▼
doql.parser.parse_text(source)
doql.parser.validate(spec, env_vars={})
doql.generators.api_gen._gen_models / _gen_schemas
  │
  ▼
JSON → window → DOM
```

The wheel is ~65 kB and loads once per session. Typed edits re-build
with a 350 ms debounce — parsing a medium spec takes ~5 ms.
