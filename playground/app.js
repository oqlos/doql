// doql playground — client-side parser/validator via Pyodide.
//
// Loads the `doql` wheel (same build that ships to PyPI) into a Pyodide
// interpreter, exposes parse_text + validate, and wires the editor to
// render diagnostics live.

"use strict";

const EXAMPLES = {
  minimal: `APP: "My App"
VERSION: "1.0.0"
DOMAIN: "demo.local"

ENTITY User:
  id: uuid! auto
  email: string! unique
  name: string!
  role: enum[admin, member]
  created: datetime auto

ENTITY Task:
  id: uuid! auto
  title: string!
  owner: User ref
  due_date: date
  done: bool default=false

INTERFACE api:
  type: rest
  auth: jwt

INTERFACE web:
  type: spa
  framework: react
`,
  saas: `APP: "My SaaS"
VERSION: "1.0.0"
DOMAIN: env.DOMAIN

ENTITY Tenant:
  id: uuid! auto
  name: string!
  plan: enum[free, pro, enterprise] default=free
  active: bool default=true

ENTITY User:
  id: uuid! auto
  tenant: Tenant ref
  email: string! unique
  role: enum[owner, admin, member]

ENTITY Project:
  id: uuid! auto
  tenant: Tenant ref
  name: string!
  created: datetime auto

INTERFACE api:
  type: rest
  auth: jwt
  middleware: [tenant_isolation]
`,
  calibration: `APP: "Calibration Lab"
VERSION: "0.9.0"

ENTITY Instrument:
  serial: string! unique
  manufacturer: string!
  category: enum[scale, pressure_gauge, thermometer]
  last_calibration: date
  next_calibration: date computed

ENTITY Calibration:
  id: uuid! auto
  instrument: Instrument ref
  performed_by: Operator ref     # dangling ref — validator will warn
  result: enum[pass, fail]
  certificate_number: string auto
`,
  iot: `APP: "IoT Fleet Manager"
VERSION: "1.0.0"

ENTITY Device:
  id: uuid! auto
  serial: string! unique
  model: string!
  firmware: string!
  status: enum[online, offline, updating] default=offline
  last_heartbeat: datetime

ENTITY MetricSample:
  id: uuid! auto
  device: Device ref
  metric: string!
  value: float!
  timestamp: datetime auto

INTERFACE api:
  type: rest
  auth: jwt
`,
};

// ─── DOM shortcuts ─────────────────────────────────────────────────────

const $editor = document.getElementById("editor");
const $btnBuild = document.getElementById("btn-build");
const $status = document.getElementById("status");
const $picker = document.getElementById("example-picker");
const $editorStats = document.getElementById("editor-stats");
const $diagnostics = document.getElementById("diagnostics");
const $astView = document.getElementById("ast-view");
const $filesList = document.getElementById("files-list");
const $modelsView = document.getElementById("models-view");
const $schemasView = document.getElementById("schemas-view");
const $envView = document.getElementById("env-view");
const $doqlVersion = document.getElementById("doql-version");
const $tabs = document.querySelectorAll(".pane-header.tabs button");

// ─── Tab switching (with URL hash sync) ────────────────────────────────

const TAB_NAMES = Array.from($tabs).map((b) => b.dataset.tab);

function activateTab(name, { pushHash = true } = {}) {
  if (!TAB_NAMES.includes(name)) return;
  $tabs.forEach((b) => b.classList.toggle("tab-active", b.dataset.tab === name));
  document.querySelectorAll(".tab-pane").forEach((p) => {
    p.classList.toggle("tab-active", p.id === `tab-${name}`);
  });
  if (pushHash) {
    const newHash = `#tab=${name}`;
    if (location.hash !== newHash) {
      history.replaceState(null, "", newHash);
    }
  }
}

function tabFromHash() {
  const m = /(?:^|#|&)tab=([a-z0-9_-]+)/i.exec(location.hash || "");
  return m && TAB_NAMES.includes(m[1]) ? m[1] : null;
}

$tabs.forEach((btn) => {
  btn.addEventListener("click", () => activateTab(btn.dataset.tab));
});

window.addEventListener("hashchange", () => {
  const name = tabFromHash();
  if (name) activateTab(name, { pushHash: false });
});

// Apply initial tab from URL (if present)
{
  const initial = tabFromHash();
  if (initial) activateTab(initial, { pushHash: false });
}

// ─── Example picker ────────────────────────────────────────────────────

$picker.addEventListener("change", (e) => {
  const key = e.target.value;
  if (key && EXAMPLES[key]) {
    $editor.value = EXAMPLES[key];
    updateStats();
    scheduleBuild();
  }
  $picker.value = "";
});

// ─── Editor stats ──────────────────────────────────────────────────────

function updateStats() {
  const text = $editor.value;
  const lines = text.split("\n").length;
  const chars = text.length;
  $editorStats.textContent = `${lines} lines · ${chars} chars`;
}
$editor.addEventListener("input", () => {
  updateStats();
  scheduleBuild();
});
updateStats();

// ─── Pyodide bootstrap ─────────────────────────────────────────────────

let pyodide = null;
let buildFn = null;
let debounceTimer = null;

async function bootPyodide() {
  try {
    $status.textContent = "Loading Pyodide runtime…";
    pyodide = await loadPyodide({
      indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/",
    });

    $status.textContent = "Installing doql…";
    await pyodide.loadPackage(["micropip"]);

    // Try wheel first (relative), fall back to installing from source files
    await pyodide.runPythonAsync(`
      import micropip, sys
      # For the static playground we install doql from the locally-served
      # wheel if present, otherwise load the parser module inline.
      try:
          await micropip.install("./doql-0.1.0a1-py3-none-any.whl")
          import doql
          version = getattr(doql, "__version__", "0.1.0a1")
      except Exception as e:
          # Fallback: tell the user how to serve the wheel
          print("Could not install doql wheel:", e)
          version = "not-installed"
    `);

    const version = pyodide.runPython(`version`);
    $doqlVersion.textContent = `v${version}`;

    // Build the API surface we expose to JS
    buildFn = pyodide.runPython(`
      import json
      from doql import parser as _parser

      def build(source: str):
          """Parse + validate, return diagnostics + rendered files as JSON-safe dict."""
          result = {
              "ok": False,
              "spec": None,
              "diagnostics": [],
              "files": [],
              "models_py": "",
              "schemas_py": "",
              "env_vars": {},
              "env_refs": [],
              "error": None,
          }
          try:
              spec = _parser.parse_text(source)
          except Exception as e:
              result["error"] = f"{type(e).__name__}: {e}"
              return json.dumps(result)

          # Parse errors collected by recovery
          for pe in (spec.parse_errors or []):
              result["diagnostics"].append({
                  "severity": "error",
                  "path": getattr(pe, "path", ""),
                  "message": getattr(pe, "message", str(pe)),
                  "line": getattr(pe, "line", 0),
              })

          # Default playground env: seed common hosts with localhost and
          # auto-fill any referenced env var with 'localhost' so previews
          # don't emit "env var not found in .env" warnings.
          _default_env = {
              "DOMAIN": "app.localhost",
              "HOST": "localhost",
              "API_HOST": "api.localhost",
              "WEB_HOST": "web.localhost",
              "DB_HOST": "db.localhost",
              "REDIS_HOST": "redis.localhost",
              "SMTP_HOST": "smtp.localhost",
              "TRAEFIK_HOST": "traefik.localhost",
              "LE_EMAIL": "ops@localhost",
              "DATABASE_URL": "sqlite:///./data/app.db",
          }
          _env = dict(_default_env)
          for _ref in (spec.env_refs or []):
              _env.setdefault(_ref, "localhost")
          result["env_vars"] = _env
          result["env_refs"] = list(spec.env_refs or [])
          issues = _parser.validate(spec, env_vars=_env)
          for i in issues:
              result["diagnostics"].append({
                  "severity": i.severity,
                  "path": i.path,
                  "message": i.message,
                  "line": getattr(i, "line", 0),
              })

          # Spec summary (AST-ish)
          result["spec"] = {
              "app_name": spec.app_name,
              "version": spec.version,
              "domain": spec.domain,
              "entities": [
                  {
                      "name": e.name,
                      "fields": [
                          {
                              "name": f.name,
                              "type": f.type,
                              "required": f.required,
                              "unique": f.unique,
                              "auto": f.auto,
                              "ref": f.ref,
                              "default": f.default,
                          }
                          for f in e.fields
                      ],
                  }
                  for e in spec.entities
              ],
              "interfaces": [{"name": i.name, "type": i.type} for i in spec.interfaces],
              "workflows": [{"name": w.name, "trigger": w.trigger} for w in spec.workflows],
              "roles": [r.name for r in spec.roles],
              "languages": spec.languages,
          }

          # Try to generate models + schemas source
          try:
              from doql.generators.api_gen import _gen_models, _gen_schemas
              result["models_py"] = _gen_models(spec)
              result["schemas_py"] = _gen_schemas(spec)
              result["files"] = [
                  {"path": "api/main.py",    "size": 0},
                  {"path": "api/models.py",  "size": len(result["models_py"])},
                  {"path": "api/schemas.py", "size": len(result["schemas_py"])},
                  {"path": "api/routes.py",  "size": 0},
                  {"path": "api/database.py","size": 0},
              ]
          except Exception as e:
              result["diagnostics"].append({
                  "severity": "warning",
                  "path": "generator",
                  "message": f"Could not generate API: {e}",
                  "line": 0,
              })

          result["ok"] = not any(d["severity"] == "error" for d in result["diagnostics"])
          return json.dumps(result)

      build
    `);

    $status.textContent = "Ready";
    $status.className = "status-ready";
    $btnBuild.disabled = false;

    // Auto-build the initial example
    runBuild();
  } catch (err) {
    console.error(err);
    $status.textContent = `Load failed: ${err.message || err}`;
    $status.className = "status-err";
  }
}

// ─── Build pipeline ────────────────────────────────────────────────────

function scheduleBuild() {
  if (!buildFn) return;
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(runBuild, 350);
}

function runBuild() {
  if (!buildFn) return;
  const source = $editor.value;
  let resultJson;
  try {
    resultJson = buildFn(source);
  } catch (err) {
    renderFatal(err.message || String(err));
    return;
  }
  const r = JSON.parse(resultJson);
  if (r.error) {
    renderFatal(r.error);
    return;
  }
  renderDiagnostics(r.diagnostics);
  renderAst(r.spec);
  renderFiles(r.files);
  renderEnv(r.env_vars, r.env_refs);
  $modelsView.textContent = r.models_py || "(nothing to generate)";
  $schemasView.textContent = r.schemas_py || "(nothing to generate)";
}

$btnBuild.addEventListener("click", runBuild);

// ─── Renderers ─────────────────────────────────────────────────────────

function renderFatal(msg) {
  $diagnostics.innerHTML =
    `<div class="diagnostic sev-error"><span class="sev">fatal</span><span class="loc">parser</span><span class="msg">${escapeHtml(msg)}</span></div>`;
}

function renderDiagnostics(list) {
  if (!list.length) {
    $diagnostics.innerHTML = `<div class="no-diagnostics">✓ No issues detected.</div>`;
    return;
  }
  $diagnostics.innerHTML = list
    .map((d) => {
      const loc = d.line ? `${d.path} (line ${d.line})` : d.path;
      return `<div class="diagnostic sev-${d.severity}">` +
        `<span class="sev">${d.severity}</span>` +
        `<span class="loc">${escapeHtml(loc)}</span>` +
        `<span class="msg">${escapeHtml(d.message)}</span>` +
        `</div>`;
    })
    .join("");
}

function renderAst(spec) {
  if (!spec) { $astView.textContent = ""; return; }
  $astView.textContent = JSON.stringify(spec, null, 2);
}

function renderEnv(envVars, envRefs) {
  if (!envVars) { $envView.textContent = ""; return; }
  const refs = new Set(envRefs || []);
  const lines = [
    "# Playground .env (auto-seeded with localhost defaults)",
    "# Referenced by spec: " + (envRefs && envRefs.length ? envRefs.join(", ") : "(none)"),
    "",
  ];
  const keys = Object.keys(envVars).sort();
  for (const k of keys) {
    const marker = refs.has(k) ? "  # ← referenced via env." + k : "";
    lines.push(`${k}=${envVars[k]}${marker}`);
  }
  $envView.textContent = lines.join("\n");
}

function renderFiles(files) {
  if (!files.length) { $filesList.innerHTML = "<li><em>no files</em></li>"; return; }
  $filesList.innerHTML = files
    .map((f) => `<li><span class="path">${escapeHtml(f.path)}</span><span class="size">${f.size} B</span></li>`)
    .join("");
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) =>
    ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
  );
}

// ─── Go ────────────────────────────────────────────────────────────────

bootPyodide();
