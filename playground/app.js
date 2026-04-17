// doql playground — client-side parser/validator via Pyodide.
//
// Loads the `doql` wheel (same build that ships to PyPI) into a Pyodide
// interpreter, exposes parse_text + validate, and wires the editor to
// render diagnostics live.
//
// Split into modules:
//   - renderers.js: UI output helpers
//   - pyodide-bridge.js: WebAssembly Python integration
//   - app.js: Main app logic (this file)

"use strict";

import { bootPyodide, debouncedBuild, executeBuild, initElements } from "./pyodide-bridge.js";

// ─── Examples ──────────────────────────────────────────────────────────

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
    debouncedBuild();
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
  debouncedBuild();
});
updateStats();

// ─── Wire up build button ──────────────────────────────────────────────

$btnBuild.addEventListener("click", executeBuild);

// ─── Initialize pyodide bridge ───────────────────────────────────────────

initElements({
  $editor,
  $btnBuild,
  $status,
  $doqlVersion,
  $diagnostics,
  $astView,
  $filesList,
  $envView,
  $modelsView,
  $schemasView,
});

bootPyodide();
