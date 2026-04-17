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
 * Load Pyodide runtime.
 * @returns {Promise<void>}
 */
async function _loadPyodide() {
  pyodide = await loadPyodide({
    indexURL: "https://cdn.jsdelivr.net/pyodide/v0.26.2/full/",
  });
}

/**
 * Install doql package.
 * @returns {Promise<string>} Version string
 */
async function _installDoql() {
  await pyodide.loadPackage(["micropip"]);
  
  await pyodide.runPythonAsync(`
    import micropip, sys
    try:
        await micropip.install("./doql-0.1.0a1-py3-none-any.whl")
        import doql
        version = getattr(doql, "__version__", "0.1.0a1")
    except Exception as e:
        print("Could not install doql wheel:", e)
        version = "not-installed"
  `);
  
  return pyodide.runPython(`version`);
}

/**
 * Fetch the Python build template and create the build function.
 * @returns {Promise<Function>} The build function
 */
async function _createBuildFunction() {
  const resp = await fetch("./doql_build.py");
  if (!resp.ok) throw new Error(`Failed to fetch doql_build.py: ${resp.status}`);
  const src = await resp.text();
  pyodide.runPython(src);
  return pyodide.globals.get("build");
}

/**
 * Boot Pyodide and install doql.
 * @returns {Promise<void>}
 */
export async function bootPyodide() {
  try {
    $status.textContent = "Loading Pyodide runtime…";
    await _loadPyodide();

    $status.textContent = "Installing doql…";
    const version = await _installDoql();
    $doqlVersion.textContent = `v${version}`;

    buildFn = await _createBuildFunction();

    $status.textContent = "Ready";
    $status.className = "status-ready";
    $btnBuild.disabled = false;

    executeBuild();
  } catch (err) {
    console.error(err);
    $status.textContent = `Load failed: ${err.message || err}`;
    $status.className = "status-err";
  }
}
