// Pyodide bridge — WebAssembly Python runtime integration.
//
// This module handles loading Pyodide, installing the doql wheel,
// and exposing the build function for parsing/validation.

"use strict";

import { renderFatal, renderDiagnostics, renderAst, renderEnv, renderFiles } from "./renderers.js";

// DOM elements (passed from main app)
let $editor, $btnBuild, $status, $doqlVersion, $diagnostics, $astView, $filesList, $envView, $modelsView, $schemasView;

// State
let pyodide = null;
let buildFn = null;
let debounceTimer = null;

/**
 * Initialize DOM element references.
 * @param {object} elements - Object containing DOM element references
 */
export function initElements(elements) {
  $editor = elements.$editor;
  $btnBuild = elements.$btnBuild;
  $status = elements.$status;
  $doqlVersion = elements.$doqlVersion;
  $diagnostics = elements.$diagnostics;
  $astView = elements.$astView;
  $filesList = elements.$filesList;
  $envView = elements.$envView;
  $modelsView = elements.$modelsView;
  $schemasView = elements.$schemasView;
}

/**
 * Check if Pyodide is ready.
 * @returns {boolean}
 */
export function isReady() {
  return buildFn !== null;
}

/**
 * Schedule a debounced build.
 */
export function debouncedBuild() {
  if (!buildFn) return;
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(executeBuild, 350);
}

/**
 * Execute the build immediately.
 */
export function executeBuild() {
  if (!buildFn) return;
  const source = $editor.value;
  let resultJson;
  try {
    resultJson = buildFn(source);
  } catch (err) {
    renderFatal($diagnostics, err.message || String(err));
    return;
  }
  const r = JSON.parse(resultJson);
  if (r.error) {
    renderFatal($diagnostics, r.error);
    return;
  }
  renderDiagnostics($diagnostics, r.diagnostics);
  renderAst($astView, r.spec);
  renderFiles($filesList, r.files);
  renderEnv($envView, r.env_vars, r.env_refs);
  $modelsView.textContent = r.models_py || "(nothing to generate)";
  $schemasView.textContent = r.schemas_py || "(nothing to generate)";
}

/**
 * Boot Pyodide and install doql.
 * @returns {Promise<void>}
 */
export async function bootPyodide() {
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
    executeBuild();
  } catch (err) {
    console.error(err);
    $status.textContent = `Load failed: ${err.message || err}`;
    $status.className = "status-err";
  }
}
